from functools import wraps
from flask import session, g, redirect, flash
from src.game_engine import GameEngine


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'player_id' not in session:
            flash('Please select or create a character to continue.', 'warning')
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function


def feature_gated(feature_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'player_id' not in session:
                flash('Please select or create a character to continue.', 'warning')
                return redirect('/')

            from src.company_resources import check_feature_requirements, deduct_feature_cost

            check = check_feature_requirements(session['player_id'], feature_name)
            if not check['allowed']:
                flash(f"Access denied: {check['reason']}", 'error')
                return redirect('/hub')

            result = deduct_feature_cost(session['player_id'], feature_name)
            if not result['success']:
                flash(f"Cannot access: {result['message']}", 'error')
                return redirect('/hub')

            if result.get('game_over'):
                flash('Your company has gone bankrupt! Game Over.', 'error')
                return redirect('/hub')

            if result['message'] != 'No cost required':
                flash(result['message'], 'info')

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def game_over_check(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'player_id' not in session:
            flash('Please select or create a character to continue.', 'warning')
            return redirect('/')

        from src.company_resources import check_game_over
        game_status = check_game_over(session['player_id'])

        if game_status.get('game_over'):
            flash('Your company has gone bankrupt! You cannot continue playing.', 'error')
            return redirect('/hub')

        return f(*args, **kwargs)
    return decorated_function


def energy_required(amount=10):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'player_id' not in session:
                flash('Please select or create a character to continue.', 'warning')
                return redirect('/')

            engine = get_engine()
            engine.load_player(session['player_id'])
            energy = engine.get_player_energy()

            if energy.get('current_energy', 0) < amount:
                flash(f'Not enough energy! Need {amount}, have {energy.get("current_energy", 0)}. Wait for recharge.', 'error')
                return redirect('/hub')

            result = engine.consume_energy(amount)
            if result.get('error'):
                flash(result['error'], 'error')
                return redirect('/hub')

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def get_engine():
    if 'engine' not in g:
        g.engine = GameEngine()
    return g.engine
