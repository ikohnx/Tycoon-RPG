import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from src.database import init_database, seed_scenarios
from src.game_engine import GameEngine
from src.leveling import get_level_title, get_progress_bar, get_exp_to_next_level

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

init_database()
seed_scenarios()

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
        
        player = engine.create_new_player(name, world, industry)
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

@app.route('/logout')
def logout():
    session.pop('player_id', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
