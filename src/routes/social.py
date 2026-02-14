from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from src.routes.helpers import login_required, feature_gated, get_engine

social_bp = Blueprint('social', __name__)


@social_bp.route('/npcs')
@login_required
def npcs():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    npc_list = get_engine().get_npcs()

    return render_template('social/npcs.html', stats=stats, npcs=npc_list)


@social_bp.route('/talk/<int:npc_id>', methods=['POST'])
@login_required
def talk_to_npc(npc_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    result = get_engine().interact_with_npc(npc_id)
    stats = get_engine().get_player_stats()

    if result.get('error'):
        flash(result['error'])
        return redirect(url_for('social.npcs'))

    return render_template('social/npc_dialogue.html', stats=stats, npc=result['npc'], relationship=result['relationship_level'])


@social_bp.route('/quests')
@login_required
def quests():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    quest_data = get_engine().get_quests()

    return render_template('social/quests.html', stats=stats, quests=quest_data)


@social_bp.route('/start_quest/<int:quest_id>', methods=['POST'])
@login_required
def start_quest(quest_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    result = get_engine().start_quest(quest_id)

    if result.get('error'):
        flash(result['error'])
    else:
        flash(f"Started quest: {result['quest']['quest_name']}!")

    return redirect(url_for('social.quests'))


@social_bp.route('/rivals')
@login_required
@feature_gated('rivals')
def rivals():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    rival_list = get_engine().get_rivals()

    return render_template('social/rivals.html', stats=stats, rivals=rival_list)


@social_bp.route('/challenges')
@login_required
def challenges():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    challenge_data = get_engine().get_weekly_challenges()

    return render_template('social/challenges.html', stats=stats, challenges=challenge_data)


@social_bp.route('/battle_arena')
@login_required
@feature_gated('battle_arena')
def battle_arena():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    battle_data = get_engine().get_rival_battle_status()

    return render_template('social/battle_arena.html', stats=stats, battle_data=battle_data)


@social_bp.route('/battle_rival/<int:rival_id>', methods=['POST'])
@login_required
def battle_rival(rival_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    result = get_engine().battle_rival(rival_id)
    stats = get_engine().get_player_stats()

    if result.get('error'):
        flash(result['error'])
        return redirect(url_for('social.battle_arena'))

    return render_template('social/battle_result.html', stats=stats, result=result)


@social_bp.route('/leaderboard')
@login_required
def leaderboard():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    category = request.args.get('category', 'stars')
    rankings = get_engine().get_leaderboard(category)

    return render_template('social/leaderboard.html', stats=stats, rankings=rankings, category=category)


@social_bp.route('/advisors')
@login_required
def advisors():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    advisor_data = get_engine().get_advisors()

    return render_template('social/advisors.html', stats=stats, advisor_data=advisor_data)


@social_bp.route('/recruit_advisor/<int:advisor_id>', methods=['POST'])
@login_required
def recruit_advisor(advisor_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    result = get_engine().recruit_advisor(advisor_id)

    if result.get('error'):
        flash(result['error'])
    else:
        flash(f"Recruited {result['advisor_name']}!")

    return redirect(url_for('social.advisors'))


@social_bp.route('/avatar')
@login_required
def avatar():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    avatar_options = get_engine().get_avatar_options()
    current_avatar = get_engine().get_player_avatar()

    return render_template('social/avatar.html', stats=stats, options=avatar_options, current=current_avatar)


@social_bp.route('/update_avatar', methods=['POST'])
@login_required
def update_avatar():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

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

    return redirect(url_for('social.avatar'))


@social_bp.route('/daily_login')
@login_required
def daily_login():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    login_status = get_engine().get_daily_login_status()
    stats = get_engine().get_player_stats()

    return render_template('social/daily_login.html', stats=stats, login_status=login_status)


@social_bp.route('/claim_daily', methods=['POST'])
@login_required
def claim_daily():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    result = get_engine().claim_daily_login()

    if result.get('error'):
        flash(result['error'])
    else:
        rewards_str = ", ".join(result['rewards_given']) if result['rewards_given'] else "Reward claimed!"
        flash(f"Day {result['reward_day']} reward claimed! {rewards_str}")

    return redirect(url_for('core.hub'))


@social_bp.route('/collect_idle', methods=['POST'])
@login_required
def collect_idle():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    result = get_engine().collect_idle_income()

    if result.get('error'):
        flash(result['error'])
    else:
        flash(f"Collected ${result['collected']:,.0f} gold from passive income!")

    return redirect(url_for('core.hub'))


@social_bp.route('/daily_missions')
@login_required
def daily_missions():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    missions_data = get_engine().get_daily_missions()

    return render_template('social/daily_missions.html', stats=stats, missions_data=missions_data)


@social_bp.route('/claim_mission/<int:mission_id>', methods=['POST'])
@login_required
def claim_mission(mission_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    result = get_engine().claim_daily_mission(mission_id)

    if result.get('error'):
        flash(result['error'])
    else:
        flash(f"Claimed {result['mission_name']} reward: +{result['reward_amount']} {result['reward_type']}!")

    return redirect(url_for('social.daily_missions'))


@social_bp.route('/achievements')
@login_required
def achievements():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    from src.game_engine import get_player_achievements

    player_achievements = get_player_achievements(player_id)

    unlocked = [a for a in player_achievements if a['is_unlocked']]
    in_progress = [a for a in player_achievements if not a['is_unlocked'] and a['progress'] > 0]
    locked = [a for a in player_achievements if not a['is_unlocked'] and a['progress'] == 0]

    return render_template('social/achievements.html',
                          stats=stats,
                          unlocked=unlocked,
                          in_progress=in_progress,
                          locked=locked)


@social_bp.route('/stories')
@login_required
def stories():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    from src.game_engine import get_story_arcs
    level = stats.get('overall_level', 1) if isinstance(stats, dict) else 1
    arcs = get_story_arcs(player_id, level)

    return render_template('social/stories.html', stats=stats, arcs=arcs)


@social_bp.route('/stories/<int:arc_id>')
@login_required
def story_arc(arc_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    from src.game_engine import get_story_arcs, get_story_chapter
    arcs = get_story_arcs(player_id, 99)
    arc = next((a for a in arcs if a['arc_id'] == arc_id), None)

    if not arc:
        flash('Story not found')
        return redirect(url_for('social.stories'))

    chapter_num = arc['current_chapter'] or 1
    chapter = get_story_chapter(arc_id, chapter_num)

    return render_template('social/story_chapter.html', stats=stats, arc=arc, chapter=chapter)


@social_bp.route('/stories/<int:arc_id>/start', methods=['POST'])
@login_required
def start_story(arc_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    from src.game_engine import start_story_arc
    start_story_arc(player_id, arc_id)

    return redirect(url_for('social.story_arc', arc_id=arc_id))


@social_bp.route('/stories/<int:arc_id>/chapter/<int:chapter_num>/choice', methods=['POST'])
@login_required
def story_choice(arc_id, chapter_num):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    choice = request.form.get('choice', 'a')

    from src.game_engine import make_story_choice
    result = make_story_choice(player_id, arc_id, chapter_num, choice)

    if result.get('success'):
        flash(f"{result['outcome']} +{result['exp_earned']} EXP")
        if result.get('is_finale'):
            flash('Congratulations! You completed the story arc!')
            return redirect(url_for('social.stories'))

    return redirect(url_for('social.story_arc', arc_id=arc_id))


@social_bp.route('/mentorship')
@login_required
def mentorship():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    from src.game_engine import get_advisor_relationships, get_mentorship_missions

    advisors = get_advisor_relationships(player_id)
    missions = get_mentorship_missions(player_id)

    return render_template('social/mentorship.html', stats=stats, advisors=advisors, missions=missions)


@social_bp.route('/mentorship/advisor/<int:advisor_id>')
@login_required
def advisor_detail(advisor_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    from src.game_engine import get_advisor_relationships, get_advisor_skill_tree, get_mentorship_missions

    advisors = get_advisor_relationships(player_id)
    advisor = next((a for a in advisors if a['advisor_id'] == advisor_id), None)
    skills = get_advisor_skill_tree(advisor_id)
    missions = get_mentorship_missions(player_id, advisor_id)

    return render_template('social/advisor_detail.html', stats=stats, advisor=advisor, skills=skills, missions=missions)


@social_bp.route('/mentorship/lesson/<int:module_id>')
@login_required
def mentorship_lesson_redirect(module_id):
    path_id = request.args.get('path_id')
    if path_id:
        return redirect(url_for('social.mentorship_lesson', module_id=module_id, path_id=path_id))
    return redirect(url_for('social.mentorship_lesson', module_id=module_id))


@social_bp.route('/learn/<int:module_id>')
@login_required
def mentorship_lesson(module_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    from src.game_engine import get_mentorship_module, start_mentorship

    module = get_mentorship_module(module_id)
    if not module:
        flash('Lesson not found')
        return redirect(url_for('scenarios.scenarios'))

    start_mentorship(player_id, module_id)

    scenario_id = request.args.get('scenario_id')
    path_id = request.args.get('path_id', type=int)

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    return render_template('social/mentorship_lesson.html',
                          stats=stats,
                          module=module,
                          scenario_id=scenario_id,
                          path_id=path_id)


@social_bp.route('/learn/<int:module_id>/validate', methods=['POST'])
@login_required
def validate_practice_route(module_id):
    from src.game_engine import validate_practice_answer

    user_answer = request.form.get('answer', '') or request.json.get('answer', '') if request.is_json else request.form.get('answer', '')
    result = validate_practice_answer(module_id, user_answer)

    return jsonify(result)


@social_bp.route('/learn/<int:module_id>/complete', methods=['POST'])
@login_required
def complete_mentorship_route(module_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

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
        return redirect(url_for('finance.learning_path_detail', path_id=path_id))

    scenario_id = request.form.get('scenario_id')
    if scenario_id:
        flash('Lesson complete! Now you can apply what you learned.')
        return redirect(url_for('scenarios.play_scenario', scenario_id=scenario_id))

    flash('Lesson completed!')
    return redirect(url_for('core.hub'))


@social_bp.route('/learn/required/<int:scenario_id>')
@login_required
def mentorship_required(scenario_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    from src.game_engine import get_mentorship_for_scenario

    module = get_mentorship_for_scenario(scenario_id)
    if not module:
        return redirect(url_for('scenarios.play_scenario', scenario_id=scenario_id))

    return redirect(url_for('social.mentorship_lesson', module_id=module['module_id'], scenario_id=scenario_id))


@social_bp.route('/network')
@login_required
def network():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    from src.game_engine import get_business_partners, get_networking_events, get_player_network

    reputation = stats.get('reputation', 50) if isinstance(stats, dict) else 50
    partners = get_business_partners(player_id, reputation)
    events = get_networking_events(reputation)
    contacts = get_player_network(player_id)

    return render_template('social/network.html', stats=stats, partners=partners, events=events, contacts=contacts)


@social_bp.route('/network/event/<int:event_id>/attend', methods=['POST'])
@login_required
def attend_event(event_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    from src.game_engine import attend_networking_event
    result = attend_networking_event(player_id, event_id)

    if result.get('success'):
        flash(f"Great networking! You made {result['contacts_gained']} new contacts. +{result['exp_earned']} EXP")

    return redirect(url_for('social.network'))


@social_bp.route('/network/ventures')
@login_required
def ventures():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    from src.game_engine import get_joint_ventures
    ventures = get_joint_ventures(player_id)

    return render_template('social/ventures.html', stats=stats, ventures=ventures)


@social_bp.route('/guilds')
@login_required
def guilds():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    from src.game_engine import get_guilds, get_player_guild

    all_guilds = get_guilds(player_id)
    my_guild = get_player_guild(player_id)

    return render_template('social/guilds.html', stats=stats, guilds=all_guilds, my_guild=my_guild)


@social_bp.route('/guilds/create', methods=['POST'])
@login_required
def create_guild():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    from src.game_engine import create_guild as engine_create_guild

    name = request.form.get('guild_name', '').strip()
    tag = request.form.get('guild_tag', '').strip().upper()
    description = request.form.get('description', '').strip()

    if not name or not tag:
        flash('Guild name and tag are required', 'error')
        return redirect(url_for('social.guilds'))

    result = engine_create_guild(player_id, name, tag, description)

    if result.get('success'):
        flash(f"Guild '{name}' created successfully! You are now the Guild Master.")
    else:
        flash(result.get('error', 'Failed to create guild'), 'error')

    return redirect(url_for('social.guilds'))


@social_bp.route('/guilds/<int:guild_id>/join', methods=['POST'])
@login_required
def join_guild(guild_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    from src.game_engine import join_guild as engine_join_guild

    result = engine_join_guild(player_id, guild_id)

    if result.get('success'):
        flash(f"You have joined the guild!")
    else:
        flash(result.get('error', 'Failed to join guild'), 'error')

    return redirect(url_for('social.guilds'))


@social_bp.route('/guilds/leave', methods=['POST'])
@login_required
def leave_guild():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    from src.game_engine import leave_guild as engine_leave_guild

    result = engine_leave_guild(player_id)

    if result.get('success'):
        flash("You have left the guild.")
    else:
        flash(result.get('error', 'Failed to leave guild'), 'error')

    return redirect(url_for('social.guilds'))


@social_bp.route('/coop')
@login_required
def coop():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    from src.game_engine import get_coop_challenges
    challenges = get_coop_challenges()

    return render_template('social/coop.html', stats=stats, challenges=challenges)


@social_bp.route('/coop/<int:challenge_id>/join', methods=['POST'])
@login_required
def join_coop_challenge(challenge_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    from src.game_engine import join_coop_challenge as engine_join_coop

    result = engine_join_coop(player_id, challenge_id)

    if result.get('success'):
        flash(f"You've joined the co-op challenge! Find teammates to complete it.")
    else:
        flash(result.get('error', 'Failed to join challenge'), 'error')

    return redirect(url_for('social.coop'))


@social_bp.route('/trading')
@login_required
def trading():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    from src.game_engine import get_trade_listings, get_player_inventory
    listings = get_trade_listings(player_id)
    inventory = get_player_inventory(player_id)

    return render_template('social/trading.html', stats=stats, listings=listings, inventory=inventory)


@social_bp.route('/trading/create', methods=['POST'])
@login_required
def create_trade_listing():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    from src.game_engine import create_trade_listing as engine_create_listing

    try:
        item_id = int(request.form.get('item_id', 0))
        price = int(request.form.get('price', 0))
    except (ValueError, TypeError):
        flash('Invalid item or price', 'error')
        return redirect(url_for('social.trading'))

    if item_id <= 0 or price <= 0:
        flash('Invalid item or price', 'error')
        return redirect(url_for('social.trading'))

    result = engine_create_listing(player_id, item_id, price)

    if result.get('success'):
        flash(f"Item listed for ${price:,}!")
    else:
        flash(result.get('error', 'Failed to create listing'), 'error')

    return redirect(url_for('social.trading'))


@social_bp.route('/trading/<int:listing_id>/buy', methods=['POST'])
@login_required
def buy_trade_item(listing_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    from src.game_engine import buy_trade_item as engine_buy_item

    result = engine_buy_item(player_id, listing_id)

    if result.get('success'):
        flash(f"Item purchased for ${result.get('price', 0):,}!")
    else:
        flash(result.get('error', 'Failed to purchase item'), 'error')

    return redirect(url_for('social.trading'))


@social_bp.route('/trading/<int:listing_id>/cancel', methods=['POST'])
@login_required
def cancel_trade_listing(listing_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    from src.game_engine import cancel_trade_listing as engine_cancel_listing

    result = engine_cancel_listing(player_id, listing_id)

    if result.get('success'):
        flash("Listing cancelled. Item returned to inventory.")
    else:
        flash(result.get('error', 'Failed to cancel listing'), 'error')

    return redirect(url_for('social.trading'))


@social_bp.route('/seasons')
@login_required
def seasons():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    from src.game_engine import get_current_season, get_player_battle_pass, get_seasonal_events, get_limited_bosses

    season = get_current_season()
    battle_pass = get_player_battle_pass(player_id)
    events = get_seasonal_events()
    bosses = get_limited_bosses()

    return render_template('social/seasons.html', stats=stats, season=season, battle_pass=battle_pass, events=events, bosses=bosses)


@social_bp.route('/seasons/battle-pass/claim/<int:tier>', methods=['POST'])
@login_required
def claim_battle_pass_reward(tier):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    from src.game_engine import claim_battle_pass_tier

    result = claim_battle_pass_tier(player_id, tier)

    if result.get('success'):
        flash(f"Tier {tier} reward claimed: {result.get('reward', 'Unknown')}!")
    else:
        flash(result.get('error', 'Failed to claim reward'), 'error')

    return redirect(url_for('social.seasons'))


@social_bp.route('/seasons/boss/<int:boss_id>/attack', methods=['POST'])
@login_required
def attack_limited_boss(boss_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    from src.game_engine import attack_limited_boss as engine_attack_boss

    result = engine_attack_boss(player_id, boss_id)

    if result.get('success'):
        flash(f"You dealt {result.get('damage', 0):,} damage! +{result.get('exp_earned', 0)} EXP")
        if result.get('boss_defeated'):
            flash("BOSS DEFEATED! Bonus rewards earned!", 'success')
    else:
        flash(result.get('error', 'Failed to attack boss'), 'error')

    return redirect(url_for('social.seasons'))


@social_bp.route('/competitions')
@login_required
def competitions():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    from src.game_engine import get_active_competitions, get_player_league

    active_comps = get_active_competitions()
    league = get_player_league(player_id)

    return render_template('social/competitions.html',
                          stats=stats,
                          competitions=active_comps,
                          league=league)


@social_bp.route('/competitions/join/<int:active_id>', methods=['POST'])
@login_required
def join_competition(active_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    from src.game_engine import join_competition as do_join
    result = do_join(player_id, active_id)

    if result.get('success'):
        flash('You have joined the competition!')
    else:
        flash(result.get('error', 'Failed to join competition'))

    return redirect(url_for('social.competitions'))


@social_bp.route('/competitions/<int:active_id>/leaderboard')
@login_required
def competition_leaderboard(active_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    from src.game_engine import get_competition_leaderboard, get_active_competitions

    leaderboard = get_competition_leaderboard(active_id)
    comps = get_active_competitions()
    competition = next((c for c in comps if c['active_id'] == active_id), None)

    return render_template('social/leaderboard.html',
                          stats=stats,
                          leaderboard=leaderboard,
                          competition=competition)


@social_bp.route('/industries')
@login_required
def industries():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    from src.game_engine import get_industry_tracks
    tracks = get_industry_tracks(player_id)

    return render_template('social/industries.html', stats=stats, tracks=tracks)


@social_bp.route('/industries/<int:track_id>')
@login_required
def industry_detail(track_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    from src.game_engine import get_industry_tracks, get_industry_certifications, get_industry_challenges

    tracks = get_industry_tracks(player_id)
    track = next((t for t in tracks if t['track_id'] == track_id), None)

    if not track:
        flash('Industry track not found')
        return redirect(url_for('social.industries'))

    certs = get_industry_certifications(track_id, track['current_level'])
    challenges = get_industry_challenges(track_id, track['current_level'])

    return render_template('social/industry_detail.html', stats=stats, track=track, certifications=certs, challenges=challenges)


@social_bp.route('/market-events')
@login_required
def market_events():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    from src.game_engine import get_active_market_events, get_current_market_cycle, get_global_challenges, get_breaking_news

    events = get_active_market_events()
    cycle = get_current_market_cycle()
    challenges = get_global_challenges()
    news = get_breaking_news()

    return render_template('social/market_events.html', stats=stats, events=events, cycle=cycle, global_challenges=challenges, news=news)


@social_bp.route('/market-events/news/<int:news_id>/respond', methods=['POST'])
@login_required
def respond_news(news_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    response = request.form.get('response', 'standard')

    from src.game_engine import respond_to_news
    result = respond_to_news(player_id, news_id, response)

    if result.get('success'):
        flash(f"Response submitted! +{result['exp_earned']} EXP")

    return redirect(url_for('social.market_events'))
