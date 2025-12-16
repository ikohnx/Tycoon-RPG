import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_wtf.csrf import CSRFProtect
from src.database import (init_database, seed_scenarios, seed_achievements, seed_items, 
                          seed_npcs, seed_quests, seed_random_events, seed_rivals, 
                          seed_milestones, seed_weekly_challenges, seed_avatar_options,
                          seed_fantasy_scenarios, seed_industrial_scenarios, 
                          seed_industrial_events, seed_industrial_rivals, seed_modern_restaurant_full,
                          seed_marketing_curriculum, seed_accounting_curriculum, seed_finance_curriculum,
                          seed_legal_curriculum, seed_operations_curriculum, seed_hr_curriculum)
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

engine = GameEngine()

@app.route('/')
def index():
    players = engine.get_all_players()
    return render_template('index.html', players=players)

@app.route('/new_game', methods=['GET', 'POST'])
def new_game():
    if request.method == 'POST':
        name = request.form.get('name', 'Entrepreneur').strip()
        if not name:
            name = 'Entrepreneur'
        world = request.form.get('world', 'Modern')
        industry = request.form.get('industry', 'Restaurant')
        career_path = request.form.get('career_path', 'entrepreneur')
        
        player = engine.create_new_player(name, world, industry, career_path)
        session['player_id'] = player.player_id
        
        return redirect(url_for('hub'))
    
    return render_template('new_game.html')

@app.route('/load_game/<int:player_id>')
def load_game(player_id):
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
    
    return render_template('hub.html', stats=stats)

@app.route('/scenarios/<discipline>')
def scenarios(discipline):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('index'))
    
    engine.load_player(player_id)
    available = engine.get_available_scenarios(discipline)
    stats = engine.get_player_stats()
    
    return render_template('scenarios.html', 
                         scenarios=available, 
                         discipline=discipline,
                         stats=stats)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
