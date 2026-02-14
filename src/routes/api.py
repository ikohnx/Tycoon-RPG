from flask import Blueprint, session, jsonify
from src.routes.helpers import login_required, get_engine

api_bp = Blueprint('api', __name__, url_prefix='/api')


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
