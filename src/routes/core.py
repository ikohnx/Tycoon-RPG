from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from src.routes.helpers import login_required, feature_gated, get_engine
from src.leveling import get_level_title, get_progress_bar, get_exp_to_next_level

core_bp = Blueprint('core', __name__)


@core_bp.route('/hub')
@login_required
def hub():
    return redirect(url_for('core.explore'))


@core_bp.route('/explore')
@core_bp.route('/explore/<map_id>')
@login_required
def explore(map_id='hub'):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    engine = get_engine()
    engine.load_player(player_id)
    energy = engine.get_player_energy()

    from src.company_resources import get_company_resources
    resources = get_company_resources(player_id)

    return render_template('core/explore.html',
                          current_map=map_id,
                          resources=resources,
                          energy=energy)


@core_bp.route('/dashboard')
@login_required
def dashboard():
    return redirect(url_for('core.explore'))


@core_bp.route('/progress')
@login_required
def progress():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    for disc, data in stats['disciplines'].items():
        data['title'] = get_level_title(data['level'])
        data['progress_bar'] = get_progress_bar(data['total_exp'], data['level'])
        exp_needed, next_level = get_exp_to_next_level(data['total_exp'])
        data['exp_to_next'] = exp_needed
        data['next_level'] = next_level

    return render_template('core/progress.html', stats=stats)


@core_bp.route('/character')
@login_required
def character():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    achievements = get_engine().get_all_achievements()

    return render_template('core/character.html', stats=stats, achievements=achievements)


@core_bp.route('/allocate_stat/<stat_name>', methods=['POST'])
@login_required
def allocate_stat(stat_name):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    result = get_engine().allocate_stat(stat_name)

    if result.get('error'):
        flash(result['error'])
    else:
        flash(f"{stat_name.capitalize()} increased to {result['new_value']}!")

    return redirect(url_for('core.character'))


@core_bp.route('/settings')
@login_required
def settings():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    from src.game_engine import get_player_preferences
    preferences = get_player_preferences(player_id)

    return render_template('core/settings.html', stats=stats, preferences=preferences)


@core_bp.route('/settings/update', methods=['POST'])
@login_required
def update_settings():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

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

    return redirect(url_for('core.settings'))


@core_bp.route('/campaign_map')
@login_required
def campaign_map():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

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

    return render_template('core/campaign_map.html',
                          stats=stats,
                          campaign=campaign_data,
                          learning_paths=learning_by_discipline,
                          resources=resources,
                          skill_tree=skill_tree,
                          active_abilities=active_abilities,
                          news_ticker=news_ticker)


@core_bp.route('/boss_challenges')
@login_required
@feature_gated('boss_challenges')
def boss_challenges():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    bosses = get_engine().get_boss_scenarios()

    return render_template('core/boss_challenges.html', stats=stats, bosses=bosses)


@core_bp.route('/worlds')
@login_required
def worlds():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    from src.game_engine import get_expanded_worlds
    level = stats.get('overall_level', 1) if isinstance(stats, dict) else 1
    all_worlds = get_expanded_worlds(level)

    return render_template('core/worlds.html', stats=stats, worlds=all_worlds)


@core_bp.route('/coach')
@login_required
def coach():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    from src.game_engine import get_learning_profile, get_learning_recommendations

    profile = get_learning_profile(player_id)
    recommendations = get_learning_recommendations(player_id)

    return render_template('core/coach.html', stats=stats, profile=profile, recommendations=recommendations)


@core_bp.route('/case-studies')
@login_required
def case_studies():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    from src.game_engine import get_case_studies, get_guest_mentors

    cases = get_case_studies()
    mentors = get_guest_mentors()

    return render_template('core/case_studies.html', stats=stats, cases=cases, mentors=mentors)


@core_bp.route('/tutorial')
@login_required
def tutorial():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    from src.game_engine import get_tutorial_progress
    progress = get_tutorial_progress(player_id)

    return render_template('core/tutorial.html',
                          stats=stats,
                          sections=progress)


@core_bp.route('/tutorial/<section_id>/complete', methods=['POST'])
@login_required
def complete_tutorial(section_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    from src.game_engine import complete_tutorial_section
    complete_tutorial_section(player_id, section_id)

    flash('Tutorial section completed!')
    return redirect(url_for('core.tutorial'))


@core_bp.route('/dismiss_onboarding', methods=['POST'])
@login_required
def dismiss_onboarding():
    player_id = session.get('player_id')
    if player_id:
        from src.game_engine import mark_onboarding_seen
        mark_onboarding_seen(player_id)
    return jsonify({'success': True})


@core_bp.route('/activate_ability/<ability_code>', methods=['POST'])
@login_required
def activate_ability_route(ability_code):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    from src.company_resources import activate_ability
    result = activate_ability(player_id, ability_code)

    if result.get('success'):
        flash(f"Activated {result['ability_name']}! Effect: {result['effect_type'].replace('_', ' ').title()}", 'success')
    else:
        flash(result.get('error', 'Could not activate ability'), 'warning')

    return redirect(url_for('core.explore'))
