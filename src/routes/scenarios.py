from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from src.routes.helpers import login_required, feature_gated, game_over_check, get_engine
from src.leveling import get_level_title

scenarios_bp = Blueprint('scenarios', __name__)


@scenarios_bp.route('/scenarios/<discipline>')
@login_required
@game_over_check
def scenarios(discipline):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    all_scenarios = get_engine().get_all_scenarios_with_status(discipline)
    stats = get_engine().get_player_stats()

    return render_template('scenarios/scenarios.html',
                         scenarios=all_scenarios,
                         discipline=discipline,
                         stats=stats)


@scenarios_bp.route('/training/<int:scenario_id>')
@login_required
def training(scenario_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    if get_engine().is_scenario_completed(scenario_id):
        flash("You've already completed this quest!")
        return redirect(url_for('core.hub'))

    scenario = get_engine().get_scenario_by_id(scenario_id)

    if not scenario:
        flash("Scenario not found!")
        return redirect(url_for('core.hub'))

    training_data = get_engine().get_training_content(scenario_id)

    return render_template('scenarios/training.html', scenario=scenario, training=training_data, stats=stats)


@scenarios_bp.route('/play/<int:scenario_id>')
@login_required
@game_over_check
def play_scenario(scenario_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    from src.game_engine import check_learning_path_gate
    path_gate = check_learning_path_gate(player_id, scenario_id)
    if path_gate.get('gated') and not path_gate.get('ready'):
        flash("Complete the learning path first to unlock this scenario!")
        return redirect(url_for('finance.learning_path_detail', path_id=path_gate['path_id']))

    from src.game_engine import check_scenario_mentorship_ready
    mentorship_check = check_scenario_mentorship_ready(player_id, scenario_id)
    if not mentorship_check['ready'] and mentorship_check['module']:
        flash("Complete the lesson first to learn the concepts!")
        return redirect(url_for('social.mentorship_lesson',
                               module_id=mentorship_check['module']['module_id'],
                               scenario_id=scenario_id))

    if get_engine().is_scenario_completed(scenario_id):
        flash("You've already completed this scenario!")
        return redirect(url_for('core.hub'))

    scenario = get_engine().get_scenario_by_id(scenario_id)

    if not scenario:
        flash("Scenario not found!")
        return redirect(url_for('core.hub'))

    return render_template('scenarios/play.html', scenario=scenario, stats=stats)


@scenarios_bp.route('/choose/<int:scenario_id>/<choice>')
@login_required
@game_over_check
def make_choice(scenario_id, choice):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)

    if get_engine().is_scenario_completed(scenario_id):
        flash("You've already completed this scenario!")
        return redirect(url_for('core.hub'))

    energy_result = get_engine().consume_energy(10)
    if energy_result.get('error'):
        flash(energy_result['error'])
        return redirect(url_for('core.hub'))

    scenario = get_engine().get_scenario_by_id(scenario_id)

    if not scenario:
        flash("Scenario not found!")
        return redirect(url_for('core.hub'))

    result = get_engine().process_choice(scenario, choice)

    if result.get('error'):
        flash(result['error'])
        return redirect(url_for('core.hub'))

    result['level_title'] = get_level_title(result['new_level'])
    stats = get_engine().get_player_stats()

    return render_template('scenarios/result.html', result=result, scenario=scenario, stats=stats)


@scenarios_bp.route('/challenge/<int:scenario_id>')
@login_required
@game_over_check
def play_challenge(scenario_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    if get_engine().is_scenario_completed(scenario_id):
        flash("You've already completed this challenge!")
        return redirect(url_for('core.hub'))

    challenge = get_engine().get_challenge_by_id(scenario_id)

    if not challenge:
        flash("Challenge not found!")
        return redirect(url_for('core.hub'))

    return render_template('scenarios/challenge.html', challenge=challenge, stats=stats)


@scenarios_bp.route('/submit_challenge/<int:scenario_id>', methods=['POST'])
@login_required
@game_over_check
def submit_challenge(scenario_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)

    if get_engine().is_scenario_completed(scenario_id):
        flash("You've already completed this challenge!")
        return redirect(url_for('core.hub'))

    energy_result = get_engine().consume_energy(10)
    if energy_result.get('error'):
        flash(energy_result['error'])
        return redirect(url_for('core.hub'))

    challenge_type = request.form.get('challenge_type')
    answer = request.form.get('answer')

    try:
        answer = float(answer)
    except (ValueError, TypeError):
        flash("Invalid answer format!")
        return redirect(url_for('scenarios.play_challenge', scenario_id=scenario_id))

    result = get_engine().evaluate_challenge(scenario_id, challenge_type, answer)

    if result.get('error'):
        flash(result['error'])
        return redirect(url_for('core.hub'))

    result['level_title'] = get_level_title(result['new_level'])
    stats = get_engine().get_player_stats()
    scenario = get_engine().get_scenario_by_id(scenario_id)

    return render_template('scenarios/result.html', result=result, scenario=scenario, stats=stats)


@scenarios_bp.route('/random_event')
@login_required
@feature_gated('random_event')
def random_event():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    event = get_engine().get_random_event()
    stats = get_engine().get_player_stats()

    if not event:
        flash("No events available right now. Keep playing!")
        return redirect(url_for('core.hub'))

    return render_template('scenarios/random_event.html', event=event, stats=stats)


@scenarios_bp.route('/resolve_event/<int:event_id>/<choice>')
@login_required
def resolve_event(event_id, choice):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    result = get_engine().process_random_event(event_id, choice)
    stats = get_engine().get_player_stats()

    if result.get('error'):
        flash(result['error'])
        return redirect(url_for('core.hub'))

    return render_template('scenarios/event_result.html', result=result, stats=stats)
