from flask import Blueprint, session, jsonify, request, render_template
from flask_wtf.csrf import generate_csrf
from src.routes.helpers import login_required, get_engine

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/csrf')
def api_csrf():
    return jsonify({'token': generate_csrf()})


@api_bp.route('/players')
def api_players():
    engine = get_engine()
    players = engine.get_all_players()
    return jsonify({'players': players})


@api_bp.route('/create_player', methods=['POST'])
def api_create_player():
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    password = (data.get('password') or '').strip()
    world = data.get('world', 'Modern')
    industry = data.get('industry', 'Restaurant')
    career_path = data.get('career_path', 'entrepreneur')

    if not name:
        return jsonify({'success': False, 'error': 'Please enter a name'})
    if len(password) < 4:
        password = 'pass'

    engine = get_engine()
    if engine.player_name_exists(name):
        return jsonify({'success': False, 'error': 'That name is already taken'})

    player = engine.create_new_player(name, world, industry, career_path, password)
    session['player_id'] = player.player_id

    stats = engine.get_player_stats()
    energy = engine.get_player_energy()
    from src.company_resources import get_company_resources
    resources = get_company_resources(player.player_id)

    player_info = {**stats}
    if energy:
        player_info['energy'] = energy.get('current_energy', 100)
    if resources:
        player_info['morale'] = resources.get('morale', 80)
        player_info['brand_equity'] = resources.get('brand_equity', 100)
        player_info['fiscal_quarter'] = resources.get('fiscal_quarter', 1)

    return jsonify({'success': True, 'player': player_info})


@api_bp.route('/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    player_id = data.get('player_id')
    password = data.get('password')

    if not player_id:
        return jsonify({'success': False, 'error': 'No player selected'})

    engine = get_engine()
    auth_result = engine.authenticate_player(player_id, password)

    if auth_result.get('needs_password') and password is None:
        return jsonify({'success': False, 'needs_password': True})

    if not auth_result.get('success', False):
        return jsonify({'success': False, 'error': auth_result.get('error', 'Login failed')})

    player = engine.load_player(player_id)
    session['player_id'] = player.player_id

    stats = engine.get_player_stats()
    energy = engine.get_player_energy()
    from src.company_resources import get_company_resources
    resources = get_company_resources(player.player_id)

    player_info = {**stats}
    if energy:
        player_info['energy'] = energy.get('current_energy', 100)
    if resources:
        player_info['morale'] = resources.get('morale', 80)
        player_info['brand_equity'] = resources.get('brand_equity', 100)
        player_info['fiscal_quarter'] = resources.get('fiscal_quarter', 1)

    return jsonify({'success': True, 'player': player_info})


@api_bp.route('/dashboard')
@login_required
def api_dashboard():
    player_id = session.get('player_id')
    if not player_id:
        return jsonify({'error': 'Not logged in'}), 401
    engine = get_engine()
    engine.load_player(player_id)
    stats = engine.get_player_stats()
    energy = engine.get_player_energy()
    from src.company_resources import get_dashboard_data
    dashboard_data = get_dashboard_data(player_id)
    milestones = engine.get_milestones()
    rivals = engine.get_rivals()
    return jsonify({
        'stats': stats,
        'energy': energy,
        'dashboard': dashboard_data,
        'milestones': milestones,
        'rivals': rivals
    })


@api_bp.route('/stats')
@login_required
def api_stats():
    player_id = session.get('player_id')
    if not player_id:
        return jsonify({'error': 'Not logged in'}), 401
    engine = get_engine()
    engine.load_player(player_id)
    stats = engine.get_player_stats()
    energy = engine.get_player_energy()
    from src.company_resources import get_company_resources
    resources = get_company_resources(player_id)
    return jsonify({'stats': stats, 'energy': energy, 'resources': resources})


@api_bp.route('/scenarios/<discipline>')
@login_required
def api_scenarios(discipline):
    player_id = session.get('player_id')
    if not player_id:
        return jsonify({'error': 'Not logged in'}), 401
    engine = get_engine()
    engine.load_player(player_id)
    scenarios = engine.get_all_scenarios_with_status(discipline)
    stats = engine.get_player_stats()
    return jsonify({'scenarios': scenarios, 'stats': stats})


@api_bp.route('/shop')
@login_required
def api_shop():
    player_id = session.get('player_id')
    if not player_id:
        return jsonify({'error': 'Not logged in'}), 401
    engine = get_engine()
    engine.load_player(player_id)
    items = engine.get_shop_items()
    stats = engine.get_player_stats()
    return jsonify({'items': items, 'cash': stats.get('cash', 0)})


@api_bp.route('/buy/<int:item_id>', methods=['POST'])
@login_required
def api_buy(item_id):
    player_id = session.get('player_id')
    if not player_id:
        return jsonify({'error': 'Not logged in'}), 401
    engine = get_engine()
    engine.load_player(player_id)
    result = engine.purchase_item(item_id)
    return jsonify(result)


@api_bp.route('/play/<int:scenario_id>')
@login_required
def api_play(scenario_id):
    player_id = session.get('player_id')
    if not player_id:
        return jsonify({'error': 'Not logged in'}), 401
    engine = get_engine()
    engine.load_player(player_id)
    if engine.is_scenario_completed(scenario_id):
        return jsonify({'error': 'Already completed'})
    scenario = engine.get_scenario_by_id(scenario_id)
    if not scenario:
        return jsonify({'error': 'Scenario not found'})
    return jsonify({'scenario': scenario})


@api_bp.route('/choose/<int:scenario_id>/<choice>', methods=['POST'])
@login_required
def api_choose(scenario_id, choice):
    player_id = session.get('player_id')
    if not player_id:
        return jsonify({'error': 'Not logged in'}), 401
    engine = get_engine()
    engine.load_player(player_id)
    if engine.is_scenario_completed(scenario_id):
        return jsonify({'error': 'Already completed this quest'})
    energy_data = engine.get_player_energy()
    if energy_data and energy_data.get('current_energy', 0) < 10:
        return jsonify({'error': 'Not enough energy'})
    scenario = engine.get_scenario_by_id(scenario_id)
    if not scenario:
        return jsonify({'error': 'Scenario not found'})
    result = engine.process_choice(scenario, choice)
    stats = engine.get_player_stats()
    energy = engine.get_player_energy()
    from src.company_resources import get_company_resources
    resources = get_company_resources(player_id)
    return jsonify({'result': result, 'stats': stats, 'energy': energy, 'resources': resources})
