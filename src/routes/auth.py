from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from src.routes.helpers import get_engine

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
def index():
    return render_template('game.html')


@auth_bp.route('/old')
def index_old():
    players = get_engine().get_all_players()
    return render_template('auth/index.html', players=players)


@auth_bp.route('/new_game', methods=['GET', 'POST'])
def new_game():
    if request.method == 'POST':
        name = request.form.get('name', 'Entrepreneur').strip()
        password = request.form.get('password', '').strip()

        if not name:
            flash('Please enter a name', 'error')
            return render_template('auth/new_game.html')

        if len(password) < 4:
            flash('Password must be at least 4 characters', 'error')
            return render_template('auth/new_game.html')

        if get_engine().player_name_exists(name):
            flash('That name is already taken. Please choose another.', 'error')
            return render_template('auth/new_game.html')

        world = request.form.get('world', 'Modern')
        industry = request.form.get('industry', 'Restaurant')
        career_path = request.form.get('career_path', 'entrepreneur')

        player = get_engine().create_new_player(name, world, industry, career_path, password)
        session['player_id'] = player.player_id

        return redirect(url_for('core.hub'))

    return render_template('auth/new_game.html')


@auth_bp.route('/load_game/<int:player_id>', methods=['GET', 'POST'])
def load_game(player_id):
    if request.method == 'POST':
        password = request.form.get('password', '')
        auth_result = get_engine().authenticate_player(player_id, password)

        if auth_result['success']:
            player = get_engine().load_player(player_id)
            session['player_id'] = player.player_id
            return redirect(url_for('core.hub'))
        else:
            flash(auth_result.get('error', 'Login failed'), 'error')
            return render_template('auth/login.html', player_id=player_id, player_name=request.args.get('name', 'Player'))

    auth_check = get_engine().authenticate_player(player_id, None)

    if auth_check.get('needs_password'):
        players = get_engine().get_all_players()
        player_name = next((p['player_name'] for p in players if p['player_id'] == player_id), 'Player')
        return render_template('auth/login.html', player_id=player_id, player_name=player_name)

    player = get_engine().load_player(player_id)
    session['player_id'] = player.player_id
    return redirect(url_for('core.hub'))


@auth_bp.route('/logout')
def logout():
    session.pop('player_id', None)
    return redirect(url_for('auth.index'))
