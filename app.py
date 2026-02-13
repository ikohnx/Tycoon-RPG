import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, g
from flask_wtf.csrf import CSRFProtect


def login_required(f):
    """Decorator to require authentication for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'player_id' not in session:
            flash('Please select or create a character to continue.', 'warning')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def feature_gated(feature_name):
    """Decorator to check feature requirements and deduct costs before allowing access."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'player_id' not in session:
                flash('Please select or create a character to continue.', 'warning')
                return redirect(url_for('index'))
            
            from src.company_resources import check_feature_requirements, deduct_feature_cost
            
            check = check_feature_requirements(session['player_id'], feature_name)
            if not check['allowed']:
                flash(f"Access denied: {check['reason']}", 'error')
                return redirect(url_for('hub'))
            
            result = deduct_feature_cost(session['player_id'], feature_name)
            if not result['success']:
                flash(f"Cannot access: {result['message']}", 'error')
                return redirect(url_for('hub'))
            
            if result.get('game_over'):
                flash('Your company has gone bankrupt! Game Over.', 'error')
                return redirect(url_for('hub'))
            
            if result['message'] != 'No cost required':
                flash(result['message'], 'info')
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def game_over_check(f):
    """Decorator to check if the game is over (brand equity = 0) before allowing gameplay."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'player_id' not in session:
            flash('Please select or create a character to continue.', 'warning')
            return redirect(url_for('index'))
        
        from src.company_resources import check_game_over
        game_status = check_game_over(session['player_id'])
        
        if game_status.get('game_over'):
            flash('Your company has gone bankrupt! You cannot continue playing.', 'error')
            return redirect(url_for('hub'))
        
        return f(*args, **kwargs)
    return decorated_function


def energy_required(amount=10):
    """Decorator to check and consume energy before allowing gameplay actions."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'player_id' not in session:
                flash('Please select or create a character to continue.', 'warning')
                return redirect(url_for('index'))
            
            engine = get_engine()
            engine.load_player(session['player_id'])
            energy = engine.get_player_energy()
            
            if energy.get('current_energy', 0) < amount:
                flash(f'Not enough energy! Need {amount}, have {energy.get("current_energy", 0)}. Wait for recharge.', 'error')
                return redirect(url_for('hub'))
            
            result = engine.consume_energy(amount)
            if result.get('error'):
                flash(result['error'], 'error')
                return redirect(url_for('hub'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


from src.database import init_database, seed_all
from src.game_engine import GameEngine
from src.leveling import get_level_title, get_progress_bar, get_exp_to_next_level

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
csrf = CSRFProtect(app)

def initialize_database():
    """Safely initialize database with error handling."""
    try:
        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            print("WARNING: DATABASE_URL not set. Database features will be unavailable.")
            return False
        init_database()
        seed_all()
        return True
    except Exception as e:
        print(f"WARNING: Database initialization failed: {e}")
        return False

db_initialized = initialize_database()

@app.context_processor
def inject_company_resources():
    """Inject company resources into all templates for the HUD display."""
    if 'player_id' in session:
        try:
            from src.company_resources import get_company_resources
            resources = get_company_resources(session['player_id'])
            return {'company_resources': resources}
        except Exception:
            pass
    return {'company_resources': None}

def get_engine():
    """Get a request-scoped GameEngine instance to prevent cross-user data leakage."""
    if 'engine' not in g:
        g.engine = GameEngine()
    return g.engine

@app.route('/')
def index():
    players = get_engine().get_all_players()
    return render_template('index.html', players=players)

@app.route('/new_game', methods=['GET', 'POST'])
def new_game():
    if request.method == 'POST':
        name = request.form.get('name', 'Entrepreneur').strip()
        password = request.form.get('password', '').strip()
        
        if not name:
            flash('Please enter a name', 'error')
            return render_template('new_game.html')
        
        if len(password) < 4:
            flash('Password must be at least 4 characters', 'error')
            return render_template('new_game.html')
        
        if get_engine().player_name_exists(name):
            flash('That name is already taken. Please choose another.', 'error')
            return render_template('new_game.html')
        
        world = request.form.get('world', 'Modern')
        industry = request.form.get('industry', 'Restaurant')
        career_path = request.form.get('career_path', 'entrepreneur')
        
        player = get_engine().create_new_player(name, world, industry, career_path, password)
        session['player_id'] = player.player_id
        
        return redirect(url_for('hub'))
    
    return render_template('new_game.html')

@app.route('/load_game/<int:player_id>', methods=['GET', 'POST'])
def load_game(player_id):
    if request.method == 'POST':
        password = request.form.get('password', '')
        auth_result = get_engine().authenticate_player(player_id, password)
        
        if auth_result['success']:
            player = get_engine().load_player(player_id)
            session['player_id'] = player.player_id
            return redirect(url_for('hub'))
        else:
            flash(auth_result.get('error', 'Login failed'), 'error')
            return render_template('login.html', player_id=player_id, player_name=request.args.get('name', 'Player'))
    
    auth_check = get_engine().authenticate_player(player_id, None)
    
    if auth_check.get('needs_password'):
        players = get_engine().get_all_players()
        player_name = next((p['player_name'] for p in players if p['player_id'] == player_id), 'Player')
        return render_template('login.html', player_id=player_id, player_name=player_name)
    
    player = get_engine().load_player(player_id)
    session['player_id'] = player.player_id
    return redirect(url_for('hub'))

@app.route('/hub')
@login_required
def hub():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    engine = get_engine()
    engine.load_player(player_id)
    stats = engine.get_player_stats()
    
    # Check if player has seen onboarding (persisted in database)
    from src.game_engine import get_onboarding_seen
    is_new_player = not get_onboarding_seen(player_id)
    
    for disc, data in stats['disciplines'].items():
        data['title'] = get_level_title(data['level'])
        data['progress_bar'] = get_progress_bar(data['total_exp'], data['level'])
        exp_needed, next_level = get_exp_to_next_level(data['total_exp'])
        data['exp_to_next'] = exp_needed
        data['next_level'] = next_level
    
    energy = engine.get_player_energy()
    login_status = engine.get_daily_login_status()
    idle_income = engine.get_idle_income_status()
    prestige_status = engine.get_prestige_status()
    leaderboard = engine.get_leaderboard(5)
    
    from src.game_engine import get_player_next_step, get_random_advisor_quote
    next_step = get_player_next_step(player_id)
    advisor_quote = get_random_advisor_quote()
    
    from src.company_resources import (
        get_company_resources, get_skill_tree, get_active_abilities, get_news_ticker, get_feature_access
    )
    resources = get_company_resources(player_id)
    skill_tree = get_skill_tree(player_id)
    active_abilities = get_active_abilities(player_id)
    news_ticker = get_news_ticker(player_id, limit=5)
    feature_access = get_feature_access(player_id)
    
    return render_template('hub.html', stats=stats, energy=energy, login_status=login_status, 
                          idle_income=idle_income, prestige_status=prestige_status, leaderboard=leaderboard,
                          is_new_player=is_new_player, next_step=next_step, advisor_quote=advisor_quote,
                          resources=resources, skill_tree=skill_tree, active_abilities=active_abilities,
                          news_ticker=news_ticker, feature_access=feature_access)


@app.route('/explore')
@app.route('/explore/<map_id>')
@login_required
def explore(map_id='hub'):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    engine = get_engine()
    engine.load_player(player_id)
    energy = engine.get_player_energy()
    
    from src.company_resources import get_company_resources
    resources = get_company_resources(player_id)
    
    return render_template('explore.html', 
                          current_map=map_id,
                          resources=resources,
                          energy=energy)


@app.route('/dismiss_onboarding', methods=['POST'])
@login_required
def dismiss_onboarding():
    player_id = session.get('player_id')
    if player_id:
        from src.game_engine import mark_onboarding_seen
        mark_onboarding_seen(player_id)
    return jsonify({'success': True})

@app.route('/scenarios/<discipline>')
@login_required
@game_over_check
def scenarios(discipline):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    all_scenarios = get_engine().get_all_scenarios_with_status(discipline)
    stats = get_engine().get_player_stats()
    
    return render_template('scenarios.html', 
                         scenarios=all_scenarios, 
                         discipline=discipline,
                         stats=stats)

@app.route('/training/<int:scenario_id>')
@login_required
def training(scenario_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    if get_engine().is_scenario_completed(scenario_id):
        flash("You've already completed this quest!")
        return redirect(url_for('hub'))
    
    scenario = get_engine().get_scenario_by_id(scenario_id)
    
    if not scenario:
        flash("Scenario not found!")
        return redirect(url_for('hub'))
    
    training_data = get_engine().get_training_content(scenario_id)
    
    return render_template('training.html', scenario=scenario, training=training_data, stats=stats)

@app.route('/play/<int:scenario_id>')
@login_required
@game_over_check
def play_scenario(scenario_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    # Check if learning path is required before playing
    from src.game_engine import check_learning_path_gate
    path_gate = check_learning_path_gate(player_id, scenario_id)
    if path_gate.get('gated') and not path_gate.get('ready'):
        flash("Complete the learning path first to unlock this scenario!")
        return redirect(url_for('learning_path_detail', path_id=path_gate['path_id']))
    
    # Check if mentorship is required before playing
    from src.game_engine import check_scenario_mentorship_ready
    mentorship_check = check_scenario_mentorship_ready(player_id, scenario_id)
    if not mentorship_check['ready'] and mentorship_check['module']:
        flash("Complete the lesson first to learn the concepts!")
        return redirect(url_for('mentorship_lesson', 
                               module_id=mentorship_check['module']['module_id'], 
                               scenario_id=scenario_id))
    
    if get_engine().is_scenario_completed(scenario_id):
        flash("You've already completed this scenario!")
        return redirect(url_for('hub'))
    
    scenario = get_engine().get_scenario_by_id(scenario_id)
    
    if not scenario:
        flash("Scenario not found!")
        return redirect(url_for('hub'))
    
    return render_template('play.html', scenario=scenario, stats=stats)

@app.route('/choose/<int:scenario_id>/<choice>')
@login_required
@game_over_check
def make_choice(scenario_id, choice):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    
    if get_engine().is_scenario_completed(scenario_id):
        flash("You've already completed this scenario!")
        return redirect(url_for('hub'))
    
    energy_result = get_engine().consume_energy(10)
    if energy_result.get('error'):
        flash(energy_result['error'])
        return redirect(url_for('hub'))
    
    scenario = get_engine().get_scenario_by_id(scenario_id)
    
    if not scenario:
        flash("Scenario not found!")
        return redirect(url_for('hub'))
    
    result = get_engine().process_choice(scenario, choice)
    
    if result.get('error'):
        flash(result['error'])
        return redirect(url_for('hub'))
    
    result['level_title'] = get_level_title(result['new_level'])
    stats = get_engine().get_player_stats()
    
    return render_template('result.html', result=result, scenario=scenario, stats=stats)

@app.route('/challenge/<int:scenario_id>')
@login_required
@game_over_check
def play_challenge(scenario_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    if get_engine().is_scenario_completed(scenario_id):
        flash("You've already completed this challenge!")
        return redirect(url_for('hub'))
    
    challenge = get_engine().get_challenge_by_id(scenario_id)
    
    if not challenge:
        flash("Challenge not found!")
        return redirect(url_for('hub'))
    
    return render_template('challenge.html', challenge=challenge, stats=stats)

@app.route('/submit_challenge/<int:scenario_id>', methods=['POST'])
@login_required
@game_over_check
def submit_challenge(scenario_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    
    if get_engine().is_scenario_completed(scenario_id):
        flash("You've already completed this challenge!")
        return redirect(url_for('hub'))
    
    energy_result = get_engine().consume_energy(10)
    if energy_result.get('error'):
        flash(energy_result['error'])
        return redirect(url_for('hub'))
    
    challenge_type = request.form.get('challenge_type')
    answer = request.form.get('answer')
    
    try:
        answer = float(answer)
    except (ValueError, TypeError):
        flash("Invalid answer format!")
        return redirect(url_for('play_challenge', scenario_id=scenario_id))
    
    result = get_engine().evaluate_challenge(scenario_id, challenge_type, answer)
    
    if result.get('error'):
        flash(result['error'])
        return redirect(url_for('hub'))
    
    result['level_title'] = get_level_title(result['new_level'])
    stats = get_engine().get_player_stats()
    scenario = get_engine().get_scenario_by_id(scenario_id)
    
    return render_template('result.html', result=result, scenario=scenario, stats=stats)

@app.route('/progress')
@login_required
def progress():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    for disc, data in stats['disciplines'].items():
        data['title'] = get_level_title(data['level'])
        data['progress_bar'] = get_progress_bar(data['total_exp'], data['level'])
        exp_needed, next_level = get_exp_to_next_level(data['total_exp'])
        data['exp_to_next'] = exp_needed
        data['next_level'] = next_level
    
    return render_template('progress.html', stats=stats)

@app.route('/character')
@login_required
def character():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    achievements = get_engine().get_all_achievements()
    
    return render_template('character.html', stats=stats, achievements=achievements)

@app.route('/allocate_stat/<stat_name>', methods=['POST'])
@login_required
def allocate_stat(stat_name):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    result = get_engine().allocate_stat(stat_name)
    
    if result.get('error'):
        flash(result['error'])
    else:
        flash(f"{stat_name.capitalize()} increased to {result['new_value']}!")
    
    return redirect(url_for('character'))

@app.route('/shop')
@login_required
def shop():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    items = get_engine().get_shop_items()
    
    return render_template('shop.html', stats=stats, items=items)

@app.route('/buy/<int:item_id>', methods=['POST'])
@login_required
def buy_item(item_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    result = get_engine().purchase_item(item_id)
    
    if result.get('error'):
        flash(result['error'])
    else:
        flash(f"Purchased {result['item']['item_name']}!")
    
    return redirect(url_for('shop'))

@app.route('/inventory')
@login_required
def inventory():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    return render_template('inventory.html', stats=stats)

@app.route('/npcs')
@login_required
def npcs():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    npc_list = get_engine().get_npcs()
    
    return render_template('npcs.html', stats=stats, npcs=npc_list)

@app.route('/talk/<int:npc_id>', methods=['POST'])
@login_required
def talk_to_npc(npc_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    result = get_engine().interact_with_npc(npc_id)
    stats = get_engine().get_player_stats()
    
    if result.get('error'):
        flash(result['error'])
        return redirect(url_for('npcs'))
    
    return render_template('npc_dialogue.html', stats=stats, npc=result['npc'], relationship=result['relationship_level'])

@app.route('/quests')
@login_required
def quests():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    quest_data = get_engine().get_quests()
    
    return render_template('quests.html', stats=stats, quests=quest_data)

@app.route('/start_quest/<int:quest_id>', methods=['POST'])
@login_required
def start_quest(quest_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    result = get_engine().start_quest(quest_id)
    
    if result.get('error'):
        flash(result['error'])
    else:
        flash(f"Started quest: {result['quest']['quest_name']}!")
    
    return redirect(url_for('quests'))

@app.route('/logout')
def logout():
    session.pop('player_id', None)
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    milestones = get_engine().get_milestones()
    financial_history = get_engine().get_financial_history()
    rivals = get_engine().get_rivals()
    
    from src.company_resources import get_dashboard_data
    dashboard_data = get_dashboard_data(player_id)
    
    return render_template('dashboard.html', stats=stats, milestones=milestones, 
                          financial_history=financial_history, rivals=rivals,
                          dashboard=dashboard_data)


@app.route('/activate_ability/<ability_code>', methods=['POST'])
@login_required
def activate_ability_route(ability_code):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    from src.company_resources import activate_ability
    result = activate_ability(player_id, ability_code)
    
    if result.get('success'):
        flash(f"Activated {result['ability_name']}! Effect: {result['effect_type'].replace('_', ' ').title()}", 'success')
    else:
        flash(result.get('error', 'Could not activate ability'), 'warning')
    
    return redirect(url_for('dashboard'))


@app.route('/random_event')
@login_required
@feature_gated('random_event')
def random_event():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    event = get_engine().get_random_event()
    stats = get_engine().get_player_stats()
    
    if not event:
        flash("No events available right now. Keep playing!")
        return redirect(url_for('hub'))
    
    return render_template('random_event.html', event=event, stats=stats)

@app.route('/resolve_event/<int:event_id>/<choice>')
@login_required
def resolve_event(event_id, choice):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    result = get_engine().process_random_event(event_id, choice)
    stats = get_engine().get_player_stats()
    
    if result.get('error'):
        flash(result['error'])
        return redirect(url_for('hub'))
    
    return render_template('event_result.html', result=result, stats=stats)

@app.route('/rivals')
@login_required
@feature_gated('rivals')
def rivals():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    rival_list = get_engine().get_rivals()
    
    return render_template('rivals.html', stats=stats, rivals=rival_list)

@app.route('/challenges')
@login_required
def challenges():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    challenge_data = get_engine().get_weekly_challenges()
    
    return render_template('challenges.html', stats=stats, challenges=challenge_data)

@app.route('/avatar')
@login_required
def avatar():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    avatar_options = get_engine().get_avatar_options()
    current_avatar = get_engine().get_player_avatar()
    
    return render_template('avatar.html', stats=stats, options=avatar_options, current=current_avatar)

@app.route('/update_avatar', methods=['POST'])
@login_required
def update_avatar():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    
    hair = request.form.get('hair', 'default')
    outfit = request.form.get('outfit', 'default')
    accessory = request.form.get('accessory', 'none')
    color = request.form.get('color', 'blue')
    
    result = get_engine().update_avatar(hair, outfit, accessory, color)
    
    if result.get('error'):
        flash(result['error'])
    else:
        flash("Avatar updated successfully!")
    
    return redirect(url_for('avatar'))

@app.route('/daily_login')
@login_required
def daily_login():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    login_status = get_engine().get_daily_login_status()
    stats = get_engine().get_player_stats()
    
    return render_template('daily_login.html', stats=stats, login_status=login_status)

@app.route('/claim_daily', methods=['POST'])
@login_required
def claim_daily():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    result = get_engine().claim_daily_login()
    
    if result.get('error'):
        flash(result['error'])
    else:
        rewards_str = ", ".join(result['rewards_given']) if result['rewards_given'] else "Reward claimed!"
        flash(f"Day {result['reward_day']} reward claimed! {rewards_str}")
    
    return redirect(url_for('hub'))

@app.route('/collect_idle', methods=['POST'])
@login_required
def collect_idle():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    result = get_engine().collect_idle_income()
    
    if result.get('error'):
        flash(result['error'])
    else:
        flash(f"Collected ${result['collected']:,.0f} gold from passive income!")
    
    return redirect(url_for('hub'))

@app.route('/advisors')
@login_required
def advisors():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    advisor_data = get_engine().get_advisors()
    
    return render_template('advisors.html', stats=stats, advisor_data=advisor_data)

@app.route('/recruit_advisor/<int:advisor_id>', methods=['POST'])
@login_required
def recruit_advisor(advisor_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    result = get_engine().recruit_advisor(advisor_id)
    
    if result.get('error'):
        flash(result['error'])
    else:
        flash(f"Recruited {result['advisor_name']}!")
    
    return redirect(url_for('advisors'))

@app.route('/equipment')
@login_required
def equipment():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    equipment_data = get_engine().get_equipment()
    
    return render_template('equipment.html', stats=stats, equipment_data=equipment_data)

@app.route('/purchase_equipment/<int:equipment_id>', methods=['POST'])
@login_required
def purchase_equipment(equipment_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    result = get_engine().purchase_equipment(equipment_id)
    
    if result.get('error'):
        flash(result['error'])
    else:
        flash(f"Purchased {result['equipment_name']}!")
    
    return redirect(url_for('equipment'))

@app.route('/equip_item/<int:equipment_id>', methods=['POST'])
@login_required
def equip_item(equipment_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    result = get_engine().equip_item(equipment_id)
    
    if result.get('error'):
        flash(result['error'])
    else:
        flash(f"Equipped {result['equipped']} to {result['slot']} slot!")
    
    return redirect(url_for('equipment'))

@app.route('/prestige')
@login_required
@feature_gated('prestige')
def prestige():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    prestige_status = get_engine().get_prestige_status()
    
    return render_template('prestige.html', stats=stats, prestige_status=prestige_status)

@app.route('/perform_prestige', methods=['POST'])
@login_required
def perform_prestige():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    result = get_engine().perform_prestige()
    
    if result.get('error'):
        flash(result['error'])
    else:
        flash(f"Prestige complete! Now at Prestige Level {result['new_prestige_level']}. EXP x{result['new_exp_multiplier']:.1f}, Gold x{result['new_gold_multiplier']:.2f}")
    
    return redirect(url_for('hub'))

@app.route('/daily_missions')
@login_required
def daily_missions():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    missions_data = get_engine().get_daily_missions()
    
    return render_template('daily_missions.html', stats=stats, missions_data=missions_data)

@app.route('/claim_mission/<int:mission_id>', methods=['POST'])
@login_required
def claim_mission(mission_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    result = get_engine().claim_daily_mission(mission_id)
    
    if result.get('error'):
        flash(result['error'])
    else:
        flash(f"Claimed {result['mission_name']} reward: +{result['reward_amount']} {result['reward_type']}!")
    
    return redirect(url_for('daily_missions'))

@app.route('/leaderboard')
@login_required
def leaderboard():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    category = request.args.get('category', 'stars')
    rankings = get_engine().get_leaderboard(category)
    
    return render_template('leaderboard.html', stats=stats, rankings=rankings, category=category)

@app.route('/battle_arena')
@login_required
@feature_gated('battle_arena')
def battle_arena():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    battle_data = get_engine().get_rival_battle_status()
    
    return render_template('battle_arena.html', stats=stats, battle_data=battle_data)

@app.route('/battle_rival/<int:rival_id>', methods=['POST'])
@login_required
def battle_rival(rival_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    result = get_engine().battle_rival(rival_id)
    stats = get_engine().get_player_stats()
    
    if result.get('error'):
        flash(result['error'])
        return redirect(url_for('battle_arena'))
    
    return render_template('battle_result.html', stats=stats, result=result)

@app.route('/campaign_map')
@login_required
def campaign_map():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    campaign_data = get_engine().get_campaign_map()
    
    from src.game_engine import get_learning_paths
    learning_paths = get_learning_paths(player_id)
    learning_by_discipline = {}
    for path in learning_paths:
        disc = path.get('discipline')
        if disc and disc not in learning_by_discipline:
            learning_by_discipline[disc] = path
    
    from src.company_resources import (
        get_company_resources, get_skill_tree, get_active_abilities, get_news_ticker
    )
    resources = get_company_resources(player_id)
    skill_tree = get_skill_tree(player_id)
    active_abilities = get_active_abilities(player_id)
    news_ticker = get_news_ticker(player_id, limit=5)
    
    return render_template('campaign_map.html', 
                          stats=stats, 
                          campaign=campaign_data, 
                          learning_paths=learning_by_discipline,
                          resources=resources,
                          skill_tree=skill_tree,
                          active_abilities=active_abilities,
                          news_ticker=news_ticker)

@app.route('/boss_challenges')
@login_required
@feature_gated('boss_challenges')
def boss_challenges():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    bosses = get_engine().get_boss_scenarios()
    
    return render_template('boss_challenges.html', stats=stats, bosses=bosses)


@app.route('/accounting')
@login_required
def accounting():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    from src.database import initialize_player_accounting
    initialize_player_accounting(player_id)
    
    accounts = get_engine().get_player_chart_of_accounts(player_id)
    period = get_engine().get_current_accounting_period(player_id)
    pending_transactions = get_engine().get_pending_transactions(player_id)
    journal_entries = get_engine().get_journal_entries(player_id)
    trial_balance = get_engine().get_trial_balance(player_id)
    income_statement = get_engine().get_income_statement(player_id)
    balance_sheet = get_engine().get_balance_sheet(player_id)
    
    return render_template('accounting.html', 
                          stats=stats,
                          accounts=accounts,
                          period=period,
                          pending_transactions=pending_transactions,
                          journal_entries=journal_entries,
                          trial_balance=trial_balance,
                          income_statement=income_statement,
                          balance_sheet=balance_sheet)


@app.route('/accounting/process', methods=['POST'])
@login_required
def accounting_process():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    transaction_id = request.form.get('transaction_id', type=int)
    debit_account = request.form.get('debit_account')
    credit_account = request.form.get('credit_account')
    
    if transaction_id and debit_account and credit_account:
        result = get_engine().process_pending_transaction(player_id, transaction_id, debit_account, credit_account)
        if result.get('success'):
            flash(f"Transaction posted! +{result['exp_earned']} EXP earned.")
        else:
            flash(result.get('error', 'Failed to post transaction'))
    
    return redirect(url_for('accounting'))


@app.route('/accounting/entry', methods=['POST'])
@login_required
def accounting_entry():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    description = request.form.get('description', '').strip()
    debit_account = request.form.get('debit_account', '').strip()
    credit_account = request.form.get('credit_account', '').strip()
    is_adjusting = request.form.get('is_adjusting') == 'on'
    
    try:
        debit_amount = float(request.form.get('debit_amount', 0) or 0)
        credit_amount = float(request.form.get('credit_amount', 0) or 0)
    except (ValueError, TypeError):
        flash('Invalid amount values!')
        return redirect(url_for('accounting'))
    
    if debit_amount <= 0 or credit_amount <= 0:
        flash('Amounts must be greater than zero!')
        return redirect(url_for('accounting'))
    
    if abs(debit_amount - credit_amount) > 0.01:
        flash('Debits must equal Credits!')
        return redirect(url_for('accounting'))
    
    if not debit_account or not credit_account:
        flash('Please select valid accounts!')
        return redirect(url_for('accounting'))
    
    if not description:
        flash('Please provide a description!')
        return redirect(url_for('accounting'))
    
    lines = [
        {'account_code': debit_account, 'debit': debit_amount, 'credit': 0},
        {'account_code': credit_account, 'debit': 0, 'credit': credit_amount}
    ]
    
    result = get_engine().create_journal_entry(player_id, description, lines, is_adjusting)
    
    if result.get('success'):
        flash(f"Journal entry posted! +{result['exp_earned']} EXP earned.")
    else:
        flash(result.get('error', 'Failed to create entry'))
    
    return redirect(url_for('accounting'))


@app.route('/projects')
@login_required
def projects():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    from src.database import initialize_player_projects
    initialize_player_projects(player_id)
    
    from src.game_engine import (get_player_initiatives, get_active_initiative, 
                                  get_player_resources, get_scheduling_challenges,
                                  get_project_templates_list)
    
    active_project = get_active_initiative(player_id)
    all_initiatives = get_player_initiatives(player_id)
    resources = get_player_resources(player_id)
    templates = get_project_templates_list()
    
    player_level = stats.get('overall_level', 1) if isinstance(stats, dict) else 1
    challenges = get_scheduling_challenges(player_level)
    
    return render_template('projects.html',
                          stats=stats,
                          active_project=active_project,
                          all_initiatives=all_initiatives,
                          resources=resources,
                          templates=templates,
                          challenges=challenges)


@app.route('/projects/start', methods=['POST'])
@login_required
def start_project():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    template_index = request.form.get('template_index', 0, type=int)
    
    from src.game_engine import create_initiative_from_template
    result = create_initiative_from_template(player_id, template_index)
    
    if result.get('success'):
        flash(f"Started new project: {result['title']}")
    else:
        flash(result.get('error', 'Failed to start project'))
    
    return redirect(url_for('projects'))


@app.route('/projects/advance', methods=['POST'])
@login_required
def advance_project():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    initiative_id = request.form.get('initiative_id', type=int)
    
    from src.game_engine import advance_project_week
    result = advance_project_week(player_id, initiative_id)
    
    if result.get('success'):
        if result.get('project_completed'):
            bonus_type = "On-Time Bonus!" if result.get('on_time') else "Project Complete!"
            flash(f"{bonus_type} +{result['exp_earned']} EXP, +${result.get('bonus_earned', 0)} cash!")
        else:
            completed = ", ".join(result.get('completed_tasks', []))
            msg = f"Week {result['new_week']} complete!"
            if completed:
                msg += f" Finished: {completed}"
            if result['exp_earned'] > 0:
                msg += f" +{result['exp_earned']} EXP"
            flash(msg)
    else:
        flash(result.get('error', 'Failed to advance project'))
    
    return redirect(url_for('projects'))


@app.route('/projects/challenge/<int:challenge_id>')
@login_required
def scheduling_challenge(challenge_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    from src.game_engine import get_scheduling_challenge
    challenge = get_scheduling_challenge(challenge_id)
    
    if not challenge:
        flash('Challenge not found')
        return redirect(url_for('projects'))
    
    return render_template('scheduling_challenge.html',
                          stats=stats,
                          challenge=challenge)


@app.route('/projects/challenge/<int:challenge_id>/submit', methods=['POST'])
@login_required
def submit_scheduling_challenge(challenge_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    from src.game_engine import submit_scheduling_challenge as submit_challenge, get_scheduling_challenge
    
    challenge = get_scheduling_challenge(challenge_id)
    if not challenge:
        flash('Challenge not found')
        return redirect(url_for('projects'))
    
    answer = {}
    if challenge['challenge_type'] == 'critical_path':
        answer['duration'] = request.form.get('duration', 0, type=int)
    elif challenge['challenge_type'] == 'estimation':
        answer['expected'] = request.form.get('expected', 0, type=float)
    elif challenge['challenge_type'] == 'compression':
        answer['choice'] = request.form.get('choice', '')
    elif challenge['challenge_type'] == 'resource_leveling':
        answer['assignments'] = {}
        for key, value in request.form.items():
            if key.startswith('assign_'):
                task_id = key.replace('assign_', '')
                answer['assignments'][task_id] = value
    
    result = submit_challenge(player_id, challenge_id, answer)
    
    if result['is_correct']:
        flash(f"Correct! +{result['exp_earned']} EXP earned!")
    else:
        flash(f"Not quite right. {result['feedback']} (+{result['exp_earned']} EXP for effort)")
    
    return redirect(url_for('projects'))


# ============================================================================
# CASH FLOW FORECASTING ROUTES
# ============================================================================

@app.route('/cashflow')
@login_required
def cashflow():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    from src.game_engine import get_cash_flow_challenges, get_player_cash_flow_forecast
    
    challenges = get_cash_flow_challenges(stats.get('overall_level', 1) if isinstance(stats, dict) else 1)
    forecast = get_player_cash_flow_forecast(player_id)
    
    return render_template('cashflow.html',
                          stats=stats,
                          challenges=challenges,
                          forecast=forecast)


@app.route('/cashflow/challenge/<int:challenge_id>')
@login_required
def cashflow_challenge(challenge_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    from src.game_engine import get_cash_flow_challenge
    challenge = get_cash_flow_challenge(challenge_id)
    
    if not challenge:
        flash('Challenge not found')
        return redirect(url_for('cashflow'))
    
    return render_template('cashflow_challenge.html',
                          stats=stats,
                          challenge=challenge)


@app.route('/cashflow/challenge/<int:challenge_id>/submit', methods=['POST'])
@login_required
def submit_cashflow_challenge(challenge_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    from src.game_engine import submit_cash_flow_challenge, get_cash_flow_challenge
    
    challenge = get_cash_flow_challenge(challenge_id)
    if not challenge:
        flash('Challenge not found')
        return redirect(url_for('cashflow'))
    
    answer = {}
    if challenge['challenge_type'] == 'timing':
        answer['choice'] = request.form.get('choice', '')
    elif challenge['challenge_type'] == 'planning':
        answer['weeks'] = request.form.get('weeks', 0, type=int)
    elif challenge['challenge_type'] == 'forecast':
        answer['credit_needed_week'] = request.form.get('credit_needed_week', 0, type=int)
    elif challenge['challenge_type'] == 'prioritization':
        priority_str = request.form.get('priority', '')
        answer['priority'] = [int(x.strip()) for x in priority_str.split(',') if x.strip().isdigit()]
    elif challenge['challenge_type'] == 'seasonal':
        answer['savings_needed'] = request.form.get('savings_needed', 0, type=int)
    
    result = submit_cash_flow_challenge(player_id, challenge_id, answer)
    
    if result['is_correct']:
        flash(f"Correct! +{result['exp_earned']} EXP earned! {result['feedback']}")
    else:
        flash(f"Not quite right. {result['feedback']} (+{result['exp_earned']} EXP for effort)")
    
    return redirect(url_for('cashflow'))


# ============================================================================
# BUSINESS PLAN WORKSHOP ROUTES
# ============================================================================

@app.route('/businessplan')
@login_required
def businessplan():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    from src.game_engine import get_player_business_plans, BUSINESS_PLAN_SECTIONS
    
    plans = get_player_business_plans(player_id)
    
    return render_template('businessplan.html',
                          stats=stats,
                          plans=plans,
                          section_templates=BUSINESS_PLAN_SECTIONS)


@app.route('/businessplan/create', methods=['POST'])
@login_required
def create_businessplan():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    plan_name = request.form.get('plan_name', 'My Business Plan')
    business_type = request.form.get('business_type', '')
    
    from src.game_engine import create_business_plan
    result = create_business_plan(player_id, plan_name, business_type)
    
    if result.get('success'):
        flash(f"Created new business plan: {plan_name}")
        return redirect(url_for('edit_businessplan', plan_id=result['plan_id']))
    else:
        flash('Failed to create business plan')
        return redirect(url_for('businessplan'))


@app.route('/businessplan/<int:plan_id>')
@login_required
def edit_businessplan(plan_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    from src.game_engine import get_business_plan
    plan = get_business_plan(plan_id)
    
    if not plan or plan['player_id'] != player_id:
        flash('Business plan not found')
        return redirect(url_for('businessplan'))
    
    return render_template('businessplan_edit.html',
                          stats=stats,
                          plan=plan)


@app.route('/businessplan/section/<int:section_id>/save', methods=['POST'])
@login_required
def save_businessplan_section(section_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    content = request.form.get('content', '')
    
    from src.game_engine import update_business_plan_section
    result = update_business_plan_section(section_id, content)
    
    if result.get('success'):
        flash(f"Section saved! Score: {result['score']}/100. {result['feedback']}")
    else:
        flash('Failed to save section')
    
    return redirect(request.referrer or url_for('businessplan'))


# ============================================================================
# NEGOTIATION SIMULATOR ROUTES
# ============================================================================

@app.route('/negotiation')
@login_required
@feature_gated('negotiation')
def negotiation():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    from src.game_engine import get_negotiation_scenarios
    
    scenarios = get_negotiation_scenarios(stats.get('overall_level', 1) if isinstance(stats, dict) else 1)
    
    return render_template('negotiation.html',
                          stats=stats,
                          scenarios=scenarios)


@app.route('/negotiation/<int:scenario_id>')
@login_required
def negotiation_scenario(scenario_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    from src.game_engine import get_negotiation_scenario, start_negotiation
    
    scenario = get_negotiation_scenario(scenario_id)
    if not scenario:
        flash('Scenario not found')
        return redirect(url_for('negotiation'))
    
    result = start_negotiation(player_id, scenario_id)
    
    return render_template('negotiation_play.html',
                          stats=stats,
                          scenario=scenario,
                          negotiation_id=result.get('negotiation_id'))


@app.route('/negotiation/offer/<int:negotiation_id>', methods=['POST'])
@login_required
def submit_negotiation_offer(negotiation_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    from src.game_engine import submit_negotiation_offer as submit_offer
    
    offer = {}
    for key, value in request.form.items():
        if key.startswith('issue_'):
            issue_name = key.replace('issue_', '')
            try:
                offer[issue_name] = float(value)
            except ValueError:
                offer[issue_name] = value
    
    result = submit_offer(negotiation_id, offer)
    
    if result.get('deal_reached'):
        flash(f"{result['message']} +{result['exp_earned']} EXP earned!")
        return redirect(url_for('negotiation'))
    else:
        flash(result.get('message', 'Offer submitted'))
        return redirect(request.referrer or url_for('negotiation'))


# ============================================================================
# RISK MANAGEMENT ROUTES
# ============================================================================

@app.route('/risks')
@login_required
@feature_gated('risks')
def risks():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    from src.game_engine import get_risk_categories, get_player_risks
    
    categories = get_risk_categories()
    player_risks = get_player_risks(player_id)
    
    return render_template('risks.html',
                          stats=stats,
                          categories=categories,
                          risks=player_risks)


@app.route('/risks/add', methods=['POST'])
@login_required
def add_risk():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    from src.game_engine import add_player_risk
    
    category_id = request.form.get('category_id', type=int)
    risk_name = request.form.get('risk_name', '')
    description = request.form.get('description', '')
    probability = request.form.get('probability', 50, type=int)
    impact = request.form.get('impact', 50, type=int)
    mitigation = request.form.get('mitigation', '')
    
    result = add_player_risk(player_id, category_id, risk_name, description, probability, impact, mitigation)
    
    if result.get('success'):
        flash(f"Risk added! Risk Score: {result['risk_score']}")
    else:
        flash('Failed to add risk')
    
    return redirect(url_for('risks'))


# ============================================================================
# SUPPLY CHAIN ROUTES
# ============================================================================

@app.route('/supplychain')
@login_required
@feature_gated('supplychain')
def supplychain():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    from src.game_engine import initialize_player_supply_chain, get_player_inventory, get_player_suppliers
    
    initialize_player_supply_chain(player_id)
    
    inventory = get_player_inventory(player_id)
    suppliers = get_player_suppliers(player_id)
    
    return render_template('supplychain.html',
                          stats=stats,
                          inventory=inventory,
                          suppliers=suppliers)


@app.route('/supplychain/order', methods=['POST'])
@login_required
def create_order():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    from src.game_engine import create_purchase_order
    
    supplier_id = request.form.get('supplier_id', type=int)
    product_id = request.form.get('product_id', type=int)
    quantity = request.form.get('quantity', type=int)
    
    result = create_purchase_order(player_id, supplier_id, product_id, quantity)
    
    if result.get('success'):
        flash(f"Purchase order created! Total: ${result['total_cost']:.2f}")
    else:
        flash(result.get('error', 'Failed to create order'))
    
    return redirect(url_for('supplychain'))


# ============================================================================
# MARKET SIMULATION ROUTES
# ============================================================================

@app.route('/market')
@login_required
@feature_gated('market')
def market():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    from src.game_engine import get_market_segments, get_market_challenges, initialize_player_market, get_player_market_position
    
    initialize_player_market(player_id)
    
    segments = get_market_segments()
    challenges = get_market_challenges(stats.get('overall_level', 1) if isinstance(stats, dict) else 1)
    position = get_player_market_position(player_id)
    
    return render_template('market.html',
                          stats=stats,
                          segments=segments,
                          challenges=challenges,
                          position=position)


@app.route('/market/challenge/<int:challenge_id>')
@login_required
def market_challenge(challenge_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    from src.game_engine import get_market_challenge
    challenge = get_market_challenge(challenge_id)
    
    if not challenge:
        flash('Challenge not found')
        return redirect(url_for('market'))
    
    return render_template('market_challenge.html',
                          stats=stats,
                          challenge=challenge)


@app.route('/market/challenge/<int:challenge_id>/submit', methods=['POST'])
@login_required
def submit_market_challenge(challenge_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    from src.game_engine import submit_market_challenge as submit_challenge, get_market_challenge
    
    challenge = get_market_challenge(challenge_id)
    if not challenge:
        flash('Challenge not found')
        return redirect(url_for('market'))
    
    answer = {}
    if challenge['challenge_type'] == 'pricing':
        answer['new_revenue'] = request.form.get('new_revenue', 0, type=float)
    elif challenge['challenge_type'] == 'competition':
        answer['decision'] = request.form.get('decision', '')
    elif challenge['challenge_type'] == 'marketing':
        answer['roi'] = request.form.get('roi', 0, type=float)
    elif challenge['challenge_type'] == 'segmentation':
        answer['best_segment'] = request.form.get('best_segment', '')
    elif challenge['challenge_type'] == 'positioning':
        answer['strategy'] = request.form.get('strategy', '')
    
    result = submit_challenge(player_id, challenge_id, answer)
    
    if result['is_correct']:
        flash(f"Correct! +{result['exp_earned']} EXP earned! {result['feedback']}")
    else:
        flash(f"Not quite right. {result['feedback']} (+{result['exp_earned']} EXP for effort)")
    
    return redirect(url_for('market'))


# ============================================================================
# HR MANAGEMENT ROUTES
# ============================================================================

@app.route('/hrmanagement')
@login_required
@feature_gated('hrmanagement')
def hrmanagement():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    from src.game_engine import get_employee_roles, get_hr_challenges, get_player_employees
    
    roles = get_employee_roles()
    challenges = get_hr_challenges(stats.get('overall_level', 1) if isinstance(stats, dict) else 1)
    employees = get_player_employees(player_id)
    
    return render_template('hrmanagement.html',
                          stats=stats,
                          roles=roles,
                          challenges=challenges,
                          employees=employees)


@app.route('/hrmanagement/challenge/<int:challenge_id>')
@login_required
def hr_challenge(challenge_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    from src.game_engine import get_hr_challenge
    challenge = get_hr_challenge(challenge_id)
    
    if not challenge:
        flash('Challenge not found')
        return redirect(url_for('hrmanagement'))
    
    return render_template('hr_challenge.html',
                          stats=stats,
                          challenge=challenge)


@app.route('/hrmanagement/challenge/<int:challenge_id>/submit', methods=['POST'])
@login_required
def submit_hr_challenge(challenge_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    from src.game_engine import submit_hr_challenge as submit_challenge, get_hr_challenge
    
    challenge = get_hr_challenge(challenge_id)
    if not challenge:
        flash('Challenge not found')
        return redirect(url_for('hrmanagement'))
    
    answer = {}
    if challenge['challenge_type'] == 'hiring':
        answer['choice'] = request.form.get('choice', '')
    elif challenge['challenge_type'] == 'performance':
        answer['rating'] = request.form.get('rating', 0, type=int)
    elif challenge['challenge_type'] == 'conflict':
        answer['approach'] = request.form.get('approach', '')
    elif challenge['challenge_type'] == 'retention':
        perks_str = request.form.get('perks', '')
        answer['perks'] = [p.strip() for p in perks_str.split(',') if p.strip()]
    elif challenge['challenge_type'] == 'culture':
        answer['choice'] = request.form.get('choice', '')
    
    result = submit_challenge(player_id, challenge_id, answer)
    
    if result['is_correct']:
        flash(f"Correct! +{result['exp_earned']} EXP earned! {result['feedback']}")
    else:
        flash(f"Not quite right. {result['feedback']} (+{result['exp_earned']} EXP for effort)")
    
    return redirect(url_for('hrmanagement'))


@app.route('/hrmanagement/hire', methods=['POST'])
@login_required
def hire_employee():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    from src.game_engine import hire_employee as do_hire
    
    role_id = request.form.get('role_id', type=int)
    employee_name = request.form.get('employee_name', '')
    salary = request.form.get('salary', type=float)
    
    result = do_hire(player_id, role_id, employee_name, salary)
    
    if result.get('success'):
        flash(f"Hired {employee_name}!")
    else:
        flash('Failed to hire employee')
    
    return redirect(url_for('hrmanagement'))


# ============================================================================
# INVESTOR PITCH ROUTES
# ============================================================================

@app.route('/pitch')
@login_required
@feature_gated('pitch')
def pitch():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    from src.game_engine import get_player_pitch_decks, get_investor_profiles, PITCH_SECTIONS
    
    decks = get_player_pitch_decks(player_id)
    investors = get_investor_profiles()
    
    return render_template('pitch.html',
                          stats=stats,
                          decks=decks,
                          investors=investors,
                          section_templates=PITCH_SECTIONS)


@app.route('/pitch/create', methods=['POST'])
@login_required
def create_pitch():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    deck_name = request.form.get('deck_name', 'My Pitch Deck')
    funding_stage = request.form.get('funding_stage', 'seed')
    target_amount = request.form.get('target_amount', 100000, type=float)
    
    from src.game_engine import create_pitch_deck
    result = create_pitch_deck(player_id, deck_name, funding_stage, target_amount)
    
    if result.get('success'):
        flash(f"Created new pitch deck: {deck_name}")
        return redirect(url_for('edit_pitch', deck_id=result['deck_id']))
    else:
        flash('Failed to create pitch deck')
        return redirect(url_for('pitch'))


@app.route('/pitch/<int:deck_id>')
@login_required
def edit_pitch(deck_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    from src.game_engine import get_pitch_deck
    deck = get_pitch_deck(deck_id)
    
    if not deck or deck['player_id'] != player_id:
        flash('Pitch deck not found')
        return redirect(url_for('pitch'))
    
    return render_template('pitch_edit.html',
                          stats=stats,
                          deck=deck)


@app.route('/pitch/section/<int:section_id>/save', methods=['POST'])
@login_required
def save_pitch_section(section_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    content = request.form.get('content', '')
    
    from src.game_engine import update_pitch_section
    result = update_pitch_section(section_id, content)
    
    if result.get('success'):
        flash(f"Section saved! Score: {result['score']}/100. {result['feedback']}")
    else:
        flash('Failed to save section')
    
    return redirect(request.referrer or url_for('pitch'))


@app.route('/pitch/<int:deck_id>/present/<int:investor_id>')
@login_required
def present_pitch(deck_id, investor_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    from src.game_engine import start_pitch_session, get_pitch_deck
    
    deck = get_pitch_deck(deck_id)
    if not deck or deck['player_id'] != player_id:
        flash('Pitch deck not found')
        return redirect(url_for('pitch'))
    
    result = start_pitch_session(player_id, deck_id, investor_id)
    
    if not result.get('success'):
        flash(result.get('error', 'Failed to start pitch session'))
        return redirect(url_for('pitch'))
    
    return render_template('pitch_present.html',
                          stats=stats,
                          deck=deck,
                          investor=result['investor'],
                          questions=result['questions'],
                          session_id=result['session_id'])


@app.route('/pitch/session/<int:session_id>/submit', methods=['POST'])
@login_required
def submit_pitch(session_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    answers = []
    i = 0
    while True:
        answer = request.form.get(f'answer_{i}')
        if answer is None:
            break
        answers.append(answer)
        i += 1
    
    from src.game_engine import submit_pitch_answers
    result = submit_pitch_answers(session_id, answers)
    
    if result.get('success'):
        flash(f"{result['message']} +{result['exp_earned']} EXP earned!")
    else:
        flash(result.get('error', 'Pitch session failed'))
    
    return redirect(url_for('pitch'))


# ============================================================================
# LEARNING ANALYTICS ROUTES
# ============================================================================

@app.route('/analytics')
@login_required
def analytics():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    from src.game_engine import get_player_analytics, get_player_skill_chart_data
    
    analytics_data = get_player_analytics(player_id)
    chart_data = get_player_skill_chart_data(player_id)
    
    return render_template('analytics.html',
                          stats=stats,
                          analytics=analytics_data,
                          chart_data=chart_data)


# ============================================================================
# ACHIEVEMENTS ROUTES
# ============================================================================

@app.route('/achievements')
@login_required
def achievements():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    from src.game_engine import get_player_achievements
    
    player_achievements = get_player_achievements(player_id)
    
    unlocked = [a for a in player_achievements if a['is_unlocked']]
    in_progress = [a for a in player_achievements if not a['is_unlocked'] and a['progress'] > 0]
    locked = [a for a in player_achievements if not a['is_unlocked'] and a['progress'] == 0]
    
    return render_template('achievements.html',
                          stats=stats,
                          unlocked=unlocked,
                          in_progress=in_progress,
                          locked=locked)


# ============================================================================
# COMPETITIONS ROUTES
# ============================================================================

@app.route('/competitions')
@login_required
def competitions():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    from src.game_engine import get_active_competitions, get_player_league
    
    active_comps = get_active_competitions()
    league = get_player_league(player_id)
    
    return render_template('competitions.html',
                          stats=stats,
                          competitions=active_comps,
                          league=league)


@app.route('/competitions/join/<int:active_id>', methods=['POST'])
@login_required
def join_competition(active_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    from src.game_engine import join_competition as do_join
    result = do_join(player_id, active_id)
    
    if result.get('success'):
        flash('You have joined the competition!')
    else:
        flash(result.get('error', 'Failed to join competition'))
    
    return redirect(url_for('competitions'))


@app.route('/competitions/<int:active_id>/leaderboard')
@login_required
def competition_leaderboard(active_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    from src.game_engine import get_competition_leaderboard, get_active_competitions
    
    leaderboard = get_competition_leaderboard(active_id)
    comps = get_active_competitions()
    competition = next((c for c in comps if c['active_id'] == active_id), None)
    
    return render_template('leaderboard.html',
                          stats=stats,
                          leaderboard=leaderboard,
                          competition=competition)


# ============================================================================
# ADVANCED SIMULATIONS ROUTES
# ============================================================================

@app.route('/simulations')
@login_required
@feature_gated('simulations')
def simulations():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    from src.game_engine import get_advanced_simulations
    
    level = stats.get('overall_level', 1) if isinstance(stats, dict) else 1
    sims = get_advanced_simulations(level)
    
    ma_sims = [s for s in sims if s['simulation_type'] == 'ma']
    intl_sims = [s for s in sims if s['simulation_type'] == 'international']
    crisis_sims = [s for s in sims if s['simulation_type'] == 'crisis']
    
    return render_template('simulations.html',
                          stats=stats,
                          ma_simulations=ma_sims,
                          international_simulations=intl_sims,
                          crisis_simulations=crisis_sims)


@app.route('/simulations/<int:simulation_id>')
@login_required
def simulation_detail(simulation_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    from src.game_engine import get_simulation
    sim = get_simulation(simulation_id)
    
    if not sim:
        flash('Simulation not found')
        return redirect(url_for('simulations'))
    
    return render_template('simulation_detail.html',
                          stats=stats,
                          simulation=sim)


@app.route('/simulations/<int:simulation_id>/start', methods=['POST'])
@login_required
def start_simulation(simulation_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    from src.game_engine import start_simulation as do_start
    result = do_start(player_id, simulation_id)
    
    if result.get('success'):
        flash('Simulation started!')
        return redirect(url_for('simulation_play', progress_id=result['progress_id']))
    else:
        flash('Failed to start simulation')
        return redirect(url_for('simulations'))


@app.route('/simulations/play/<int:progress_id>')
@login_required
def simulation_play(progress_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    return render_template('simulation_play.html',
                          stats=stats,
                          progress_id=progress_id)


# ============================================================================
# TUTORIAL ROUTES
# ============================================================================

@app.route('/tutorial')
@login_required
def tutorial():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    from src.game_engine import get_tutorial_progress
    progress = get_tutorial_progress(player_id)
    
    return render_template('tutorial.html',
                          stats=stats,
                          sections=progress)


@app.route('/tutorial/<section_id>/complete', methods=['POST'])
@login_required
def complete_tutorial(section_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    from src.game_engine import complete_tutorial_section
    complete_tutorial_section(player_id, section_id)
    
    flash('Tutorial section completed!')
    return redirect(url_for('tutorial'))


# ============================================================================
# MENTORSHIP SYSTEM ROUTES - Learn before playing scenarios
# ============================================================================

@app.route('/mentorship/lesson/<int:module_id>')
@login_required
def mentorship_lesson_redirect(module_id):
    """Redirect old URL to new URL."""
    path_id = request.args.get('path_id')
    if path_id:
        return redirect(url_for('mentorship_lesson', module_id=module_id, path_id=path_id))
    return redirect(url_for('mentorship_lesson', module_id=module_id))


@app.route('/learn/<int:module_id>')
@login_required
def mentorship_lesson(module_id):
    """View a mentorship lesson."""
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    from src.game_engine import get_mentorship_module, start_mentorship
    
    module = get_mentorship_module(module_id)
    if not module:
        flash('Lesson not found')
        return redirect(url_for('scenarios'))
    
    start_mentorship(player_id, module_id)
    
    scenario_id = request.args.get('scenario_id')
    path_id = request.args.get('path_id', type=int)
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    return render_template('mentorship_lesson.html', 
                          stats=stats, 
                          module=module,
                          scenario_id=scenario_id,
                          path_id=path_id)


@app.route('/learn/<int:module_id>/validate', methods=['POST'])
@login_required
def validate_practice_route(module_id):
    """Server-side validation for practice question answers."""
    from src.game_engine import validate_practice_answer
    
    user_answer = request.form.get('answer', '') or request.json.get('answer', '') if request.is_json else request.form.get('answer', '')
    result = validate_practice_answer(module_id, user_answer)
    
    return jsonify(result)


@app.route('/learn/<int:module_id>/complete', methods=['POST'])
@login_required
def complete_mentorship_route(module_id):
    """Mark a mentorship lesson as complete with server-side validation."""
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    from src.game_engine import complete_mentorship, update_learning_path_progress, validate_practice_answer, get_mentorship_module
    
    module = get_mentorship_module(module_id)
    practice_score = 100
    
    if module and module.get('practice_question'):
        user_answer = request.form.get('practice_answer', '')
        validation = validate_practice_answer(module_id, user_answer)
        practice_score = validation.get('score', 50)
    
    complete_mentorship(player_id, module_id, practice_score)
    
    path_id = request.form.get('path_id', type=int)
    if path_id:
        update_learning_path_progress(player_id, path_id, 'lesson')
        flash('Lesson complete! Continue to the next step.')
        return redirect(url_for('learning_path_detail', path_id=path_id))
    
    scenario_id = request.form.get('scenario_id')
    if scenario_id:
        flash('Lesson complete! Now you can apply what you learned.')
        return redirect(url_for('play_scenario', scenario_id=scenario_id))
    
    flash('Lesson completed!')
    return redirect(url_for('hub'))


@app.route('/learn/required/<int:scenario_id>')
@login_required
def mentorship_required(scenario_id):
    """Show required mentorship before a scenario."""
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    from src.game_engine import get_mentorship_for_scenario
    
    module = get_mentorship_for_scenario(scenario_id)
    if not module:
        return redirect(url_for('play_scenario', scenario_id=scenario_id))
    
    return redirect(url_for('mentorship_lesson', module_id=module['module_id'], scenario_id=scenario_id))


# ============================================================================
# MENTOR TRIALS - RPG-THEMED KNOWLEDGE QUIZZES
# ============================================================================

@app.route('/trials')
@login_required
def mentor_trials_list():
    """Show all available mentor trials."""
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    from src.game_engine import get_all_mentor_trials
    trials = get_all_mentor_trials(player_id)
    
    return render_template('mentor_trials.html', stats=stats, trials=trials)


@app.route('/trials/<int:trial_id>')
@login_required
def mentor_trial(trial_id):
    """Start a mentor trial quiz."""
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    path_id = request.args.get('path_id', type=int)
    
    from src.game_engine import get_mentor_trial, start_mentor_trial
    trial = get_mentor_trial(trial_id)
    
    if not trial:
        flash('Trial not found!')
        return redirect(url_for('mentor_trials_list'))
    
    start_mentor_trial(player_id, trial_id)
    
    return render_template('mentor_trial_play.html', stats=stats, trial=trial, path_id=path_id)


@app.route('/trials/<int:trial_id>/submit', methods=['POST'])
@login_required
def submit_mentor_trial(trial_id):
    """Submit mentor trial answers and calculate results."""
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    from src.game_engine import get_mentor_trial, complete_mentor_trial
    
    path_id = request.form.get('path_id', type=int)
    
    trial = get_mentor_trial(trial_id)
    if not trial:
        flash('Trial not found!')
        return redirect(url_for('mentor_trials_list'))
    
    # Calculate score
    score = 0
    max_score = 0
    results = []
    
    for q in trial['questions']:
        answer = request.form.get(f'q_{q["question_id"]}')
        is_correct = answer and answer.upper() == q['correct_answer'].upper()
        points = q['points'] if is_correct else 0
        score += points
        max_score += q['points']
        results.append({
            'question': q['question_text'],
            'your_answer': answer,
            'correct_answer': q['correct_answer'],
            'is_correct': is_correct,
            'explanation': q['explanation'],
            'points': points
        })
    
    percentage = (score / max_score * 100) if max_score > 0 else 0
    is_passed = percentage >= trial['passing_score']
    
    rewards = complete_mentor_trial(player_id, trial_id, score, max_score, is_passed)
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    return render_template('mentor_trial_result.html', 
                          stats=stats, 
                          trial=trial, 
                          results=results,
                          score=score,
                          max_score=max_score,
                          percentage=percentage,
                          is_passed=is_passed,
                          rewards=rewards,
                          path_id=path_id)


# ============================================================================
# MERCHANT PUZZLES - INTERACTIVE BUSINESS CALCULATORS
# ============================================================================

@app.route('/puzzles')
@login_required
def merchant_puzzles_list():
    """Show all available merchant puzzles."""
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    from src.game_engine import get_all_merchant_puzzles
    puzzles = get_all_merchant_puzzles(player_id)
    
    return render_template('merchant_puzzles.html', stats=stats, puzzles=puzzles)


@app.route('/puzzles/<int:puzzle_id>')
@login_required
def merchant_puzzle(puzzle_id):
    """Play a merchant puzzle."""
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    path_id = request.args.get('path_id', type=int)
    
    from src.game_engine import get_merchant_puzzle, start_merchant_puzzle
    puzzle = get_merchant_puzzle(puzzle_id)
    
    if not puzzle:
        flash('Puzzle not found!')
        return redirect(url_for('merchant_puzzles_list'))
    
    start_merchant_puzzle(player_id, puzzle_id)
    
    return render_template('merchant_puzzle_play.html', stats=stats, puzzle=puzzle, path_id=path_id)


@app.route('/puzzles/<int:puzzle_id>/submit', methods=['POST'])
@login_required
def submit_merchant_puzzle(puzzle_id):
    """Submit merchant puzzle answer."""
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    from src.game_engine import get_merchant_puzzle, complete_merchant_puzzle
    
    path_id = request.form.get('path_id', type=int)
    
    puzzle = get_merchant_puzzle(puzzle_id)
    if not puzzle:
        flash('Puzzle not found!')
        return redirect(url_for('merchant_puzzles_list'))
    
    answer = request.form.get('answer', '')
    time_seconds = int(request.form.get('time_seconds', 0))
    
    try:
        player_answer = float(answer)
    except (ValueError, TypeError):
        player_answer = None
    
    challenge = puzzle.get('challenge_data', {})
    correct_answer = challenge.get('correct_margin') or challenge.get('correct_breakeven') or challenge.get('correct_roi') or challenge.get('correct_price') or challenge.get('correct_rate')
    tolerance = challenge.get('tolerance', 0)
    
    is_correct = player_answer is not None and abs(player_answer - correct_answer) <= tolerance
    
    rewards = complete_merchant_puzzle(player_id, puzzle_id, time_seconds, is_correct)
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    return render_template('merchant_puzzle_result.html',
                          stats=stats,
                          puzzle=puzzle,
                          player_answer=player_answer,
                          correct_answer=correct_answer,
                          is_correct=is_correct,
                          time_seconds=time_seconds,
                          rewards=rewards,
                          path_id=path_id)


# ============================================================================
# LEARNING PATHS SYSTEM ROUTES
# ============================================================================

@app.route('/learning-paths')
@login_required
def learning_paths_list():
    """Show all learning paths with player progress."""
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    discipline = request.args.get('discipline')
    
    from src.game_engine import get_learning_paths
    paths = get_learning_paths(player_id, discipline)
    
    return render_template('learning_paths.html', stats=stats, paths=paths, filter_discipline=discipline)


@app.route('/learning-paths/<int:path_id>')
@login_required
def learning_path_detail(path_id):
    """View a single learning path with detailed progress."""
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    from src.game_engine import get_learning_path_by_id
    path = get_learning_path_by_id(path_id, player_id)
    
    if not path:
        flash('Learning path not found!')
        return redirect(url_for('learning_paths_list'))
    
    return render_template('learning_path_detail.html', stats=stats, path=path)


@app.route('/learning-paths/<int:path_id>/claim-bonus', methods=['POST'])
@login_required
def claim_path_bonus(path_id):
    """Claim the completion bonus for a learning path."""
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    from src.game_engine import claim_learning_path_bonus
    result = claim_learning_path_bonus(player_id, path_id)
    
    if result.get('error'):
        flash(result['error'])
    else:
        flash(f"Claimed +{result['gold_earned']} gold and +{result['exp_earned']} XP!")
    
    return redirect(url_for('learning_path_detail', path_id=path_id))


# ============================================================================
# PHASE 4: STORYLINE QUEST SYSTEM ROUTES
# ============================================================================

@app.route('/stories')
@login_required
def stories():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    from src.game_engine import get_story_arcs
    level = stats.get('overall_level', 1) if isinstance(stats, dict) else 1
    arcs = get_story_arcs(player_id, level)
    
    return render_template('stories.html', stats=stats, arcs=arcs)


@app.route('/stories/<int:arc_id>')
@login_required
def story_arc(arc_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    from src.game_engine import get_story_arcs, get_story_chapter
    arcs = get_story_arcs(player_id, 99)
    arc = next((a for a in arcs if a['arc_id'] == arc_id), None)
    
    if not arc:
        flash('Story not found')
        return redirect(url_for('stories'))
    
    chapter_num = arc['current_chapter'] or 1
    chapter = get_story_chapter(arc_id, chapter_num)
    
    return render_template('story_chapter.html', stats=stats, arc=arc, chapter=chapter)


@app.route('/stories/<int:arc_id>/start', methods=['POST'])
@login_required
def start_story(arc_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    from src.game_engine import start_story_arc
    start_story_arc(player_id, arc_id)
    
    return redirect(url_for('story_arc', arc_id=arc_id))


@app.route('/stories/<int:arc_id>/chapter/<int:chapter_num>/choice', methods=['POST'])
@login_required
def story_choice(arc_id, chapter_num):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    choice = request.form.get('choice', 'a')
    
    from src.game_engine import make_story_choice
    result = make_story_choice(player_id, arc_id, chapter_num, choice)
    
    if result.get('success'):
        flash(f"{result['outcome']} +{result['exp_earned']} EXP")
        if result.get('is_finale'):
            flash('Congratulations! You completed the story arc!')
            return redirect(url_for('stories'))
    
    return redirect(url_for('story_arc', arc_id=arc_id))


# ============================================================================
# PHASE 4: MENTORSHIP ROUTES
# ============================================================================

@app.route('/mentorship')
@login_required
def mentorship():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    from src.game_engine import get_advisor_relationships, get_mentorship_missions
    
    advisors = get_advisor_relationships(player_id)
    missions = get_mentorship_missions(player_id)
    
    return render_template('mentorship.html', stats=stats, advisors=advisors, missions=missions)


@app.route('/mentorship/advisor/<int:advisor_id>')
@login_required
def advisor_detail(advisor_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    from src.game_engine import get_advisor_relationships, get_advisor_skill_tree, get_mentorship_missions
    
    advisors = get_advisor_relationships(player_id)
    advisor = next((a for a in advisors if a['advisor_id'] == advisor_id), None)
    skills = get_advisor_skill_tree(advisor_id)
    missions = get_mentorship_missions(player_id, advisor_id)
    
    return render_template('advisor_detail.html', stats=stats, advisor=advisor, skills=skills, missions=missions)


# ============================================================================
# PHASE 4: BUSINESS NETWORK ROUTES
# ============================================================================

@app.route('/network')
@login_required
def network():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    from src.game_engine import get_business_partners, get_networking_events, get_player_network
    
    reputation = stats.get('reputation', 50) if isinstance(stats, dict) else 50
    partners = get_business_partners(player_id, reputation)
    events = get_networking_events(reputation)
    contacts = get_player_network(player_id)
    
    return render_template('network.html', stats=stats, partners=partners, events=events, contacts=contacts)


@app.route('/network/event/<int:event_id>/attend', methods=['POST'])
@login_required
def attend_event(event_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    from src.game_engine import attend_networking_event
    result = attend_networking_event(player_id, event_id)
    
    if result.get('success'):
        flash(f"Great networking! You made {result['contacts_gained']} new contacts. +{result['exp_earned']} EXP")
    
    return redirect(url_for('network'))


@app.route('/network/ventures')
@login_required
def ventures():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    from src.game_engine import get_joint_ventures
    ventures = get_joint_ventures(player_id)
    
    return render_template('ventures.html', stats=stats, ventures=ventures)


# ============================================================================
# PHASE 4: INDUSTRY TRACKS ROUTES
# ============================================================================

@app.route('/industries')
@login_required
def industries():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    from src.game_engine import get_industry_tracks
    tracks = get_industry_tracks(player_id)
    
    return render_template('industries.html', stats=stats, tracks=tracks)


@app.route('/industries/<int:track_id>')
@login_required
def industry_detail(track_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    from src.game_engine import get_industry_tracks, get_industry_certifications, get_industry_challenges
    
    tracks = get_industry_tracks(player_id)
    track = next((t for t in tracks if t['track_id'] == track_id), None)
    
    if not track:
        flash('Industry track not found')
        return redirect(url_for('industries'))
    
    certs = get_industry_certifications(track_id, track['current_level'])
    challenges = get_industry_challenges(track_id, track['current_level'])
    
    return render_template('industry_detail.html', stats=stats, track=track, certifications=certs, challenges=challenges)


# ============================================================================
# PHASE 4: MARKET EVENTS ROUTES
# ============================================================================

@app.route('/market-events')
@login_required
def market_events():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    from src.game_engine import get_active_market_events, get_current_market_cycle, get_global_challenges, get_breaking_news
    
    events = get_active_market_events()
    cycle = get_current_market_cycle()
    challenges = get_global_challenges()
    news = get_breaking_news()
    
    return render_template('market_events.html', stats=stats, events=events, cycle=cycle, global_challenges=challenges, news=news)


@app.route('/market-events/news/<int:news_id>/respond', methods=['POST'])
@login_required
def respond_news(news_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    response = request.form.get('response', 'standard')
    
    from src.game_engine import respond_to_news
    result = respond_to_news(player_id, news_id, response)
    
    if result.get('success'):
        flash(f"Response submitted! +{result['exp_earned']} EXP")
    
    return redirect(url_for('market_events'))


# ============================================================================
# PHASE 5A: MULTIPLAYER & SOCIAL ROUTES
# ============================================================================

@app.route('/guilds')
@login_required
def guilds():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    from src.game_engine import get_guilds, get_player_guild
    
    all_guilds = get_guilds(player_id)
    my_guild = get_player_guild(player_id)
    
    return render_template('guilds.html', stats=stats, guilds=all_guilds, my_guild=my_guild)


@app.route('/guilds/create', methods=['POST'])
@login_required
def create_guild():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    from src.game_engine import create_guild as engine_create_guild
    
    name = request.form.get('guild_name', '').strip()
    tag = request.form.get('guild_tag', '').strip().upper()
    description = request.form.get('description', '').strip()
    
    if not name or not tag:
        flash('Guild name and tag are required', 'error')
        return redirect(url_for('guilds'))
    
    result = engine_create_guild(player_id, name, tag, description)
    
    if result.get('success'):
        flash(f"Guild '{name}' created successfully! You are now the Guild Master.")
    else:
        flash(result.get('error', 'Failed to create guild'), 'error')
    
    return redirect(url_for('guilds'))


@app.route('/guilds/<int:guild_id>/join', methods=['POST'])
@login_required
def join_guild(guild_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    from src.game_engine import join_guild as engine_join_guild
    
    result = engine_join_guild(player_id, guild_id)
    
    if result.get('success'):
        flash(f"You have joined the guild!")
    else:
        flash(result.get('error', 'Failed to join guild'), 'error')
    
    return redirect(url_for('guilds'))


@app.route('/guilds/leave', methods=['POST'])
@login_required
def leave_guild():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    from src.game_engine import leave_guild as engine_leave_guild
    
    result = engine_leave_guild(player_id)
    
    if result.get('success'):
        flash("You have left the guild.")
    else:
        flash(result.get('error', 'Failed to leave guild'), 'error')
    
    return redirect(url_for('guilds'))


@app.route('/coop')
@login_required
def coop():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    from src.game_engine import get_coop_challenges
    challenges = get_coop_challenges()
    
    return render_template('coop.html', stats=stats, challenges=challenges)


@app.route('/coop/<int:challenge_id>/join', methods=['POST'])
@login_required
def join_coop_challenge(challenge_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    from src.game_engine import join_coop_challenge as engine_join_coop
    
    result = engine_join_coop(player_id, challenge_id)
    
    if result.get('success'):
        flash(f"You've joined the co-op challenge! Find teammates to complete it.")
    else:
        flash(result.get('error', 'Failed to join challenge'), 'error')
    
    return redirect(url_for('coop'))


@app.route('/trading')
@login_required
def trading():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    from src.game_engine import get_trade_listings, get_player_inventory
    listings = get_trade_listings(player_id)
    inventory = get_player_inventory(player_id)
    
    return render_template('trading.html', stats=stats, listings=listings, inventory=inventory)


@app.route('/trading/create', methods=['POST'])
@login_required
def create_trade_listing():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    from src.game_engine import create_trade_listing as engine_create_listing
    
    try:
        item_id = int(request.form.get('item_id', 0))
        price = int(request.form.get('price', 0))
    except (ValueError, TypeError):
        flash('Invalid item or price', 'error')
        return redirect(url_for('trading'))
    
    if item_id <= 0 or price <= 0:
        flash('Invalid item or price', 'error')
        return redirect(url_for('trading'))
    
    result = engine_create_listing(player_id, item_id, price)
    
    if result.get('success'):
        flash(f"Item listed for ${price:,}!")
    else:
        flash(result.get('error', 'Failed to create listing'), 'error')
    
    return redirect(url_for('trading'))


@app.route('/trading/<int:listing_id>/buy', methods=['POST'])
@login_required
def buy_trade_item(listing_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    from src.game_engine import buy_trade_item as engine_buy_item
    
    result = engine_buy_item(player_id, listing_id)
    
    if result.get('success'):
        flash(f"Item purchased for ${result.get('price', 0):,}!")
    else:
        flash(result.get('error', 'Failed to purchase item'), 'error')
    
    return redirect(url_for('trading'))


@app.route('/trading/<int:listing_id>/cancel', methods=['POST'])
@login_required
def cancel_trade_listing(listing_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    from src.game_engine import cancel_trade_listing as engine_cancel_listing
    
    result = engine_cancel_listing(player_id, listing_id)
    
    if result.get('success'):
        flash("Listing cancelled. Item returned to inventory.")
    else:
        flash(result.get('error', 'Failed to cancel listing'), 'error')
    
    return redirect(url_for('trading'))


# ============================================================================
# PHASE 5B: SEASONAL CONTENT ROUTES
# ============================================================================

@app.route('/seasons')
@login_required
def seasons():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    from src.game_engine import get_current_season, get_player_battle_pass, get_seasonal_events, get_limited_bosses
    
    season = get_current_season()
    battle_pass = get_player_battle_pass(player_id)
    events = get_seasonal_events()
    bosses = get_limited_bosses()
    
    return render_template('seasons.html', stats=stats, season=season, battle_pass=battle_pass, events=events, bosses=bosses)


@app.route('/seasons/battle-pass/claim/<int:tier>', methods=['POST'])
@login_required
def claim_battle_pass_reward(tier):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    from src.game_engine import claim_battle_pass_tier
    
    result = claim_battle_pass_tier(player_id, tier)
    
    if result.get('success'):
        flash(f"Tier {tier} reward claimed: {result.get('reward', 'Unknown')}!")
    else:
        flash(result.get('error', 'Failed to claim reward'), 'error')
    
    return redirect(url_for('seasons'))


@app.route('/seasons/boss/<int:boss_id>/attack', methods=['POST'])
@login_required
def attack_limited_boss(boss_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    from src.game_engine import attack_limited_boss as engine_attack_boss
    
    result = engine_attack_boss(player_id, boss_id)
    
    if result.get('success'):
        flash(f"You dealt {result.get('damage', 0):,} damage! +{result.get('exp_earned', 0)} EXP")
        if result.get('boss_defeated'):
            flash("BOSS DEFEATED! Bonus rewards earned!", 'success')
    else:
        flash(result.get('error', 'Failed to attack boss'), 'error')
    
    return redirect(url_for('seasons'))


# ============================================================================
# PHASE 5C: AI PERSONALIZATION ROUTES
# ============================================================================

@app.route('/coach')
@login_required
def coach():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    from src.game_engine import get_learning_profile, get_learning_recommendations
    
    profile = get_learning_profile(player_id)
    recommendations = get_learning_recommendations(player_id)
    
    return render_template('coach.html', stats=stats, profile=profile, recommendations=recommendations)


# ============================================================================
# PHASE 5D: CONTENT EXPANSION ROUTES
# ============================================================================

@app.route('/worlds')
@login_required
def worlds():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    from src.game_engine import get_expanded_worlds
    level = stats.get('overall_level', 1) if isinstance(stats, dict) else 1
    all_worlds = get_expanded_worlds(level)
    
    return render_template('worlds.html', stats=stats, worlds=all_worlds)


@app.route('/case-studies')
@login_required
def case_studies():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    from src.game_engine import get_case_studies, get_guest_mentors
    
    cases = get_case_studies()
    mentors = get_guest_mentors()
    
    return render_template('case_studies.html', stats=stats, cases=cases, mentors=mentors)


# ============================================================================
# PHASE 5E: ACCESSIBILITY ROUTES
# ============================================================================

@app.route('/settings')
@login_required
def settings():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    
    from src.game_engine import get_player_preferences
    preferences = get_player_preferences(player_id)
    
    return render_template('settings.html', stats=stats, preferences=preferences)


@app.route('/settings/update', methods=['POST'])
@login_required
def update_settings():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    from src.game_engine import update_player_preferences
    
    preferences = {
        'theme': request.form.get('theme'),
        'font_size': request.form.get('font_size'),
        'high_contrast': request.form.get('high_contrast') == 'on',
        'reduced_motion': request.form.get('reduced_motion') == 'on',
        'screen_reader_mode': request.form.get('screen_reader_mode') == 'on',
        'color_blind_mode': request.form.get('color_blind_mode')
    }
    
    update_player_preferences(player_id, preferences)
    flash('Settings updated successfully!')
    
    return redirect(url_for('settings'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
