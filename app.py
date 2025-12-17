import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_wtf.csrf import CSRFProtect
from src.database import (init_database, seed_scenarios, seed_achievements, seed_items, 
                          seed_npcs, seed_quests, seed_random_events, seed_rivals, 
                          seed_milestones, seed_weekly_challenges, seed_avatar_options,
                          seed_fantasy_scenarios, seed_industrial_scenarios, 
                          seed_industrial_events, seed_industrial_rivals, seed_modern_restaurant_full,
                          seed_marketing_curriculum, seed_accounting_curriculum, seed_finance_curriculum,
                          seed_legal_curriculum, seed_operations_curriculum, seed_hr_curriculum,
                          seed_strategy_curriculum, seed_daily_login_rewards, seed_advisors,
                          seed_equipment, seed_daily_missions, seed_interactive_challenges,
                          seed_advanced_challenges, seed_scheduling_challenges)
from src.game_engine import GameEngine
from src.leveling import get_level_title, get_progress_bar, get_exp_to_next_level

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
csrf = CSRFProtect(app)

init_database()
seed_scenarios()
seed_achievements()
seed_items()
seed_npcs()
seed_quests()
seed_random_events()
seed_rivals()
seed_milestones()
seed_weekly_challenges()
seed_avatar_options()
seed_fantasy_scenarios()
seed_industrial_scenarios()
seed_industrial_events()
seed_industrial_rivals()
seed_modern_restaurant_full()
seed_marketing_curriculum()
seed_accounting_curriculum()
seed_finance_curriculum()
seed_legal_curriculum()
seed_operations_curriculum()
seed_hr_curriculum()
seed_strategy_curriculum()
seed_daily_login_rewards()
seed_advisors()
seed_equipment()
seed_daily_missions()
seed_interactive_challenges()
seed_advanced_challenges()
seed_scheduling_challenges()

engine = GameEngine()

@app.route('/')
def index():
    players = engine.get_all_players()
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
        
        if engine.player_name_exists(name):
            flash('That name is already taken. Please choose another.', 'error')
            return render_template('new_game.html')
        
        world = request.form.get('world', 'Modern')
        industry = request.form.get('industry', 'Restaurant')
        career_path = request.form.get('career_path', 'entrepreneur')
        
        player = engine.create_new_player(name, world, industry, career_path, password)
        session['player_id'] = player.player_id
        
        return redirect(url_for('hub'))
    
    return render_template('new_game.html')

@app.route('/load_game/<int:player_id>', methods=['GET', 'POST'])
def load_game(player_id):
    if request.method == 'POST':
        password = request.form.get('password', '')
        auth_result = engine.authenticate_player(player_id, password)
        
        if auth_result['success']:
            player = engine.load_player(player_id)
            session['player_id'] = player.player_id
            return redirect(url_for('hub'))
        else:
            flash(auth_result.get('error', 'Login failed'), 'error')
            return render_template('login.html', player_id=player_id, player_name=request.args.get('name', 'Player'))
    
    auth_check = engine.authenticate_player(player_id, None)
    
    if auth_check.get('needs_password'):
        players = engine.get_all_players()
        player_name = next((p['player_name'] for p in players if p['player_id'] == player_id), 'Player')
        return render_template('login.html', player_id=player_id, player_name=player_name)
    
    player = engine.load_player(player_id)
    session['player_id'] = player.player_id
    return redirect(url_for('hub'))

@app.route('/hub')
def hub():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    engine.load_player(player_id)
    stats = engine.get_player_stats()
    
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
    
    return render_template('hub.html', stats=stats, energy=energy, login_status=login_status, 
                          idle_income=idle_income, prestige_status=prestige_status, leaderboard=leaderboard)

@app.route('/scenarios/<discipline>')
def scenarios(discipline):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    engine.load_player(player_id)
    all_scenarios = engine.get_all_scenarios_with_status(discipline)
    stats = engine.get_player_stats()
    
    return render_template('scenarios.html', 
                         scenarios=all_scenarios, 
                         discipline=discipline,
                         stats=stats)

@app.route('/training/<int:scenario_id>')
def training(scenario_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    engine.load_player(player_id)
    stats = engine.get_player_stats()
    
    if engine.is_scenario_completed(scenario_id):
        flash("You've already completed this quest!")
        return redirect(url_for('hub'))
    
    scenario = engine.get_scenario_by_id(scenario_id)
    
    if not scenario:
        flash("Scenario not found!")
        return redirect(url_for('hub'))
    
    training_data = engine.get_training_content(scenario_id)
    
    return render_template('training.html', scenario=scenario, training=training_data, stats=stats)

@app.route('/play/<int:scenario_id>')
def play_scenario(scenario_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    engine.load_player(player_id)
    stats = engine.get_player_stats()
    
    if engine.is_scenario_completed(scenario_id):
        flash("You've already completed this scenario!")
        return redirect(url_for('hub'))
    
    scenario = engine.get_scenario_by_id(scenario_id)
    
    if not scenario:
        flash("Scenario not found!")
        return redirect(url_for('hub'))
    
    return render_template('play.html', scenario=scenario, stats=stats)

@app.route('/choose/<int:scenario_id>/<choice>')
def make_choice(scenario_id, choice):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    engine.load_player(player_id)
    
    if engine.is_scenario_completed(scenario_id):
        flash("You've already completed this scenario!")
        return redirect(url_for('hub'))
    
    energy_result = engine.consume_energy(10)
    if energy_result.get('error'):
        flash(energy_result['error'])
        return redirect(url_for('hub'))
    
    scenario = engine.get_scenario_by_id(scenario_id)
    
    if not scenario:
        flash("Scenario not found!")
        return redirect(url_for('hub'))
    
    result = engine.process_choice(scenario, choice)
    
    if result.get('error'):
        flash(result['error'])
        return redirect(url_for('hub'))
    
    result['level_title'] = get_level_title(result['new_level'])
    stats = engine.get_player_stats()
    
    return render_template('result.html', result=result, scenario=scenario, stats=stats)

@app.route('/challenge/<int:scenario_id>')
def play_challenge(scenario_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    engine.load_player(player_id)
    stats = engine.get_player_stats()
    
    if engine.is_scenario_completed(scenario_id):
        flash("You've already completed this challenge!")
        return redirect(url_for('hub'))
    
    challenge = engine.get_challenge_by_id(scenario_id)
    
    if not challenge:
        flash("Challenge not found!")
        return redirect(url_for('hub'))
    
    return render_template('challenge.html', challenge=challenge, stats=stats)

@app.route('/submit_challenge/<int:scenario_id>', methods=['POST'])
def submit_challenge(scenario_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    engine.load_player(player_id)
    
    if engine.is_scenario_completed(scenario_id):
        flash("You've already completed this challenge!")
        return redirect(url_for('hub'))
    
    energy_result = engine.consume_energy(10)
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
    
    result = engine.evaluate_challenge(scenario_id, challenge_type, answer)
    
    if result.get('error'):
        flash(result['error'])
        return redirect(url_for('hub'))
    
    result['level_title'] = get_level_title(result['new_level'])
    stats = engine.get_player_stats()
    scenario = engine.get_scenario_by_id(scenario_id)
    
    return render_template('result.html', result=result, scenario=scenario, stats=stats)

@app.route('/progress')
def progress():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    engine.load_player(player_id)
    stats = engine.get_player_stats()
    
    for disc, data in stats['disciplines'].items():
        data['title'] = get_level_title(data['level'])
        data['progress_bar'] = get_progress_bar(data['total_exp'], data['level'])
        exp_needed, next_level = get_exp_to_next_level(data['total_exp'])
        data['exp_to_next'] = exp_needed
        data['next_level'] = next_level
    
    return render_template('progress.html', stats=stats)

@app.route('/character')
def character():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    engine.load_player(player_id)
    stats = engine.get_player_stats()
    achievements = engine.get_all_achievements()
    
    return render_template('character.html', stats=stats, achievements=achievements)

@app.route('/allocate_stat/<stat_name>', methods=['POST'])
def allocate_stat(stat_name):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    engine.load_player(player_id)
    result = engine.allocate_stat(stat_name)
    
    if result.get('error'):
        flash(result['error'])
    else:
        flash(f"{stat_name.capitalize()} increased to {result['new_value']}!")
    
    return redirect(url_for('character'))

@app.route('/shop')
def shop():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    engine.load_player(player_id)
    stats = engine.get_player_stats()
    items = engine.get_shop_items()
    
    return render_template('shop.html', stats=stats, items=items)

@app.route('/buy/<int:item_id>', methods=['POST'])
def buy_item(item_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    engine.load_player(player_id)
    result = engine.purchase_item(item_id)
    
    if result.get('error'):
        flash(result['error'])
    else:
        flash(f"Purchased {result['item']['item_name']}!")
    
    return redirect(url_for('shop'))

@app.route('/inventory')
def inventory():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    engine.load_player(player_id)
    stats = engine.get_player_stats()
    
    return render_template('inventory.html', stats=stats)

@app.route('/npcs')
def npcs():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    engine.load_player(player_id)
    stats = engine.get_player_stats()
    npc_list = engine.get_npcs()
    
    return render_template('npcs.html', stats=stats, npcs=npc_list)

@app.route('/talk/<int:npc_id>', methods=['POST'])
def talk_to_npc(npc_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    engine.load_player(player_id)
    result = engine.interact_with_npc(npc_id)
    stats = engine.get_player_stats()
    
    if result.get('error'):
        flash(result['error'])
        return redirect(url_for('npcs'))
    
    return render_template('npc_dialogue.html', stats=stats, npc=result['npc'], relationship=result['relationship_level'])

@app.route('/quests')
def quests():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    engine.load_player(player_id)
    stats = engine.get_player_stats()
    quest_data = engine.get_quests()
    
    return render_template('quests.html', stats=stats, quests=quest_data)

@app.route('/start_quest/<int:quest_id>', methods=['POST'])
def start_quest(quest_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    engine.load_player(player_id)
    result = engine.start_quest(quest_id)
    
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
def dashboard():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    engine.load_player(player_id)
    stats = engine.get_player_stats()
    milestones = engine.get_milestones()
    financial_history = engine.get_financial_history()
    rivals = engine.get_rivals()
    
    return render_template('dashboard.html', stats=stats, milestones=milestones, 
                          financial_history=financial_history, rivals=rivals)

@app.route('/random_event')
def random_event():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    engine.load_player(player_id)
    event = engine.get_random_event()
    stats = engine.get_player_stats()
    
    if not event:
        flash("No events available right now. Keep playing!")
        return redirect(url_for('hub'))
    
    return render_template('random_event.html', event=event, stats=stats)

@app.route('/resolve_event/<int:event_id>/<choice>')
def resolve_event(event_id, choice):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    engine.load_player(player_id)
    result = engine.process_random_event(event_id, choice)
    stats = engine.get_player_stats()
    
    if result.get('error'):
        flash(result['error'])
        return redirect(url_for('hub'))
    
    return render_template('event_result.html', result=result, stats=stats)

@app.route('/rivals')
def rivals():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    engine.load_player(player_id)
    stats = engine.get_player_stats()
    rival_list = engine.get_rivals()
    
    return render_template('rivals.html', stats=stats, rivals=rival_list)

@app.route('/challenges')
def challenges():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    engine.load_player(player_id)
    stats = engine.get_player_stats()
    challenge_data = engine.get_weekly_challenges()
    
    return render_template('challenges.html', stats=stats, challenges=challenge_data)

@app.route('/avatar')
def avatar():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    engine.load_player(player_id)
    stats = engine.get_player_stats()
    avatar_options = engine.get_avatar_options()
    current_avatar = engine.get_player_avatar()
    
    return render_template('avatar.html', stats=stats, options=avatar_options, current=current_avatar)

@app.route('/update_avatar', methods=['POST'])
def update_avatar():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    engine.load_player(player_id)
    
    hair = request.form.get('hair', 'default')
    outfit = request.form.get('outfit', 'default')
    accessory = request.form.get('accessory', 'none')
    color = request.form.get('color', 'blue')
    
    result = engine.update_avatar(hair, outfit, accessory, color)
    
    if result.get('error'):
        flash(result['error'])
    else:
        flash("Avatar updated successfully!")
    
    return redirect(url_for('avatar'))

@app.route('/daily_login')
def daily_login():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    engine.load_player(player_id)
    login_status = engine.get_daily_login_status()
    stats = engine.get_player_stats()
    
    return render_template('daily_login.html', stats=stats, login_status=login_status)

@app.route('/claim_daily', methods=['POST'])
def claim_daily():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    engine.load_player(player_id)
    result = engine.claim_daily_login()
    
    if result.get('error'):
        flash(result['error'])
    else:
        rewards_str = ", ".join(result['rewards_given']) if result['rewards_given'] else "Reward claimed!"
        flash(f"Day {result['reward_day']} reward claimed! {rewards_str}")
    
    return redirect(url_for('hub'))

@app.route('/collect_idle', methods=['POST'])
def collect_idle():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    engine.load_player(player_id)
    result = engine.collect_idle_income()
    
    if result.get('error'):
        flash(result['error'])
    else:
        flash(f"Collected ${result['collected']:,.0f} gold from passive income!")
    
    return redirect(url_for('hub'))

@app.route('/advisors')
def advisors():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    engine.load_player(player_id)
    stats = engine.get_player_stats()
    advisor_data = engine.get_advisors()
    
    return render_template('advisors.html', stats=stats, advisor_data=advisor_data)

@app.route('/recruit_advisor/<int:advisor_id>', methods=['POST'])
def recruit_advisor(advisor_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    engine.load_player(player_id)
    result = engine.recruit_advisor(advisor_id)
    
    if result.get('error'):
        flash(result['error'])
    else:
        flash(f"Recruited {result['advisor_name']}!")
    
    return redirect(url_for('advisors'))

@app.route('/equipment')
def equipment():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    engine.load_player(player_id)
    stats = engine.get_player_stats()
    equipment_data = engine.get_equipment()
    
    return render_template('equipment.html', stats=stats, equipment_data=equipment_data)

@app.route('/purchase_equipment/<int:equipment_id>', methods=['POST'])
def purchase_equipment(equipment_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    engine.load_player(player_id)
    result = engine.purchase_equipment(equipment_id)
    
    if result.get('error'):
        flash(result['error'])
    else:
        flash(f"Purchased {result['equipment_name']}!")
    
    return redirect(url_for('equipment'))

@app.route('/equip_item/<int:equipment_id>', methods=['POST'])
def equip_item(equipment_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    engine.load_player(player_id)
    result = engine.equip_item(equipment_id)
    
    if result.get('error'):
        flash(result['error'])
    else:
        flash(f"Equipped {result['equipped']} to {result['slot']} slot!")
    
    return redirect(url_for('equipment'))

@app.route('/prestige')
def prestige():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    engine.load_player(player_id)
    stats = engine.get_player_stats()
    prestige_status = engine.get_prestige_status()
    
    return render_template('prestige.html', stats=stats, prestige_status=prestige_status)

@app.route('/perform_prestige', methods=['POST'])
def perform_prestige():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    engine.load_player(player_id)
    result = engine.perform_prestige()
    
    if result.get('error'):
        flash(result['error'])
    else:
        flash(f"Prestige complete! Now at Prestige Level {result['new_prestige_level']}. EXP x{result['new_exp_multiplier']:.1f}, Gold x{result['new_gold_multiplier']:.2f}")
    
    return redirect(url_for('hub'))

@app.route('/daily_missions')
def daily_missions():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    engine.load_player(player_id)
    stats = engine.get_player_stats()
    missions_data = engine.get_daily_missions()
    
    return render_template('daily_missions.html', stats=stats, missions_data=missions_data)

@app.route('/claim_mission/<int:mission_id>', methods=['POST'])
def claim_mission(mission_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    engine.load_player(player_id)
    result = engine.claim_daily_mission(mission_id)
    
    if result.get('error'):
        flash(result['error'])
    else:
        flash(f"Claimed {result['mission_name']} reward: +{result['reward_amount']} {result['reward_type']}!")
    
    return redirect(url_for('daily_missions'))

@app.route('/leaderboard')
def leaderboard():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    engine.load_player(player_id)
    stats = engine.get_player_stats()
    
    category = request.args.get('category', 'stars')
    rankings = engine.get_leaderboard(category)
    
    return render_template('leaderboard.html', stats=stats, rankings=rankings, category=category)

@app.route('/battle_arena')
def battle_arena():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    engine.load_player(player_id)
    stats = engine.get_player_stats()
    battle_data = engine.get_rival_battle_status()
    
    return render_template('battle_arena.html', stats=stats, battle_data=battle_data)

@app.route('/battle_rival/<int:rival_id>', methods=['POST'])
def battle_rival(rival_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    engine.load_player(player_id)
    result = engine.battle_rival(rival_id)
    stats = engine.get_player_stats()
    
    if result.get('error'):
        flash(result['error'])
        return redirect(url_for('battle_arena'))
    
    return render_template('battle_result.html', stats=stats, result=result)

@app.route('/campaign_map')
def campaign_map():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    engine.load_player(player_id)
    stats = engine.get_player_stats()
    campaign_data = engine.get_campaign_map()
    
    return render_template('campaign_map.html', stats=stats, campaign=campaign_data)

@app.route('/boss_challenges')
def boss_challenges():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    engine.load_player(player_id)
    stats = engine.get_player_stats()
    bosses = engine.get_boss_scenarios()
    
    return render_template('boss_challenges.html', stats=stats, bosses=bosses)


@app.route('/accounting')
def accounting():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    engine.load_player(player_id)
    stats = engine.get_player_stats()
    
    from src.database import initialize_player_accounting
    initialize_player_accounting(player_id)
    
    accounts = engine.get_player_chart_of_accounts(player_id)
    period = engine.get_current_accounting_period(player_id)
    pending_transactions = engine.get_pending_transactions(player_id)
    journal_entries = engine.get_journal_entries(player_id)
    trial_balance = engine.get_trial_balance(player_id)
    income_statement = engine.get_income_statement(player_id)
    balance_sheet = engine.get_balance_sheet(player_id)
    
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
def accounting_process():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    transaction_id = request.form.get('transaction_id', type=int)
    debit_account = request.form.get('debit_account')
    credit_account = request.form.get('credit_account')
    
    if transaction_id and debit_account and credit_account:
        result = engine.process_pending_transaction(player_id, transaction_id, debit_account, credit_account)
        if result.get('success'):
            flash(f"Transaction posted! +{result['exp_earned']} EXP earned.")
        else:
            flash(result.get('error', 'Failed to post transaction'))
    
    return redirect(url_for('accounting'))


@app.route('/accounting/entry', methods=['POST'])
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
    
    result = engine.create_journal_entry(player_id, description, lines, is_adjusting)
    
    if result.get('success'):
        flash(f"Journal entry posted! +{result['exp_earned']} EXP earned.")
    else:
        flash(result.get('error', 'Failed to create entry'))
    
    return redirect(url_for('accounting'))


@app.route('/projects')
def projects():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    engine.load_player(player_id)
    stats = engine.get_player_stats()
    
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
def scheduling_challenge(challenge_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    engine.load_player(player_id)
    stats = engine.get_player_stats()
    
    from src.game_engine import get_scheduling_challenge
    challenge = get_scheduling_challenge(challenge_id)
    
    if not challenge:
        flash('Challenge not found')
        return redirect(url_for('projects'))
    
    return render_template('scheduling_challenge.html',
                          stats=stats,
                          challenge=challenge)


@app.route('/projects/challenge/<int:challenge_id>/submit', methods=['POST'])
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
