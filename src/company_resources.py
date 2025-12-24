"""
Company Resources Module for Business Mastery Simulation

Manages the core resource pool:
- Capital ($): Money for actions and growth
- Team Morale: Stamina - if zero, actions fail
- Brand Equity: Health (HP) - if zero, game over (bankruptcy)

Also handles:
- Fiscal Quarter timeline (3 decisions = 1 quarter)
- Quarterly events
- Skill Tree abilities
- News ticker system
"""

from src.database import get_connection, return_connection
import random

SKILL_TREE_ABILITIES = {
    'Marketing': {
        'subskill': 'Brand Identity',
        'ability_name': 'Viral Campaign',
        'ability_code': 'viral_campaign',
        'description': 'Launch a viral marketing campaign that boosts your next revenue gain by 50%',
        'effect_type': 'revenue_multiplier',
        'effect_value': 1.5,
        'unlock_level': 3,
        'icon': 'megaphone'
    },
    'Finance': {
        'subskill': 'Unit Economics',
        'ability_name': 'Burn Rate Optimization',
        'ability_code': 'burn_optimization',
        'description': 'Optimize spending to reduce capital losses by 30% for one quarter',
        'effect_type': 'cost_reduction',
        'effect_value': 0.7,
        'unlock_level': 3,
        'icon': 'calculator'
    },
    'Operations': {
        'subskill': 'Process Mapping',
        'ability_name': 'Automation Initiative',
        'ability_code': 'automation',
        'description': 'Implement process automation to boost team morale by 20 points',
        'effect_type': 'morale_boost',
        'effect_value': 20,
        'unlock_level': 3,
        'icon': 'gear'
    },
    'Human Resources': {
        'subskill': 'Talent Acquisition',
        'ability_name': 'Headhunter Network',
        'ability_code': 'headhunter',
        'description': 'Access elite talent network - reduces hiring costs by 40%',
        'effect_type': 'hiring_discount',
        'effect_value': 0.6,
        'unlock_level': 3,
        'icon': 'people'
    },
    'Legal': {
        'subskill': 'Compliance',
        'ability_name': 'Liability Shield',
        'ability_code': 'liability_shield',
        'description': 'Proactive legal protection prevents random lawsuit events for one quarter',
        'effect_type': 'event_prevention',
        'effect_value': 1.0,
        'unlock_level': 3,
        'icon': 'shield'
    },
    'Strategy': {
        'subskill': 'Pivot Logic',
        'ability_name': 'Blue Ocean Strategy',
        'ability_code': 'blue_ocean',
        'description': 'Find untapped market space - multiplies ALL XP gains by 2x for one quarter',
        'effect_type': 'exp_multiplier',
        'effect_value': 2.0,
        'unlock_level': 3,
        'icon': 'compass'
    }
}

QUARTERLY_EVENTS = [
    {
        'event_type': 'market_boom',
        'event_title': 'Market Expansion',
        'event_description': 'Economic conditions are favorable! Customer demand is surging.',
        'capital_impact': 2000,
        'morale_impact': 10,
        'brand_impact': 5,
        'exp_multiplier': 1.2,
        'is_crisis': False,
        'probability': 0.15
    },
    {
        'event_type': 'competitor_crisis',
        'event_title': 'Competitor Stumbles',
        'event_description': 'A major competitor faces a PR disaster. Opportunity to gain market share.',
        'capital_impact': 1000,
        'morale_impact': 5,
        'brand_impact': 10,
        'exp_multiplier': 1.0,
        'target_discipline': 'Marketing',
        'is_crisis': False,
        'probability': 0.10
    },
    {
        'event_type': 'supply_disruption',
        'event_title': 'Supply Chain Crisis',
        'event_description': 'Key supplier bankruptcy threatens your operations.',
        'capital_impact': -1500,
        'morale_impact': -15,
        'brand_impact': -10,
        'exp_multiplier': 1.0,
        'target_discipline': 'Operations',
        'is_crisis': True,
        'probability': 0.12
    },
    {
        'event_type': 'talent_drain',
        'event_title': 'Talent War',
        'event_description': 'Competitors are poaching your best employees with higher salaries.',
        'capital_impact': -500,
        'morale_impact': -20,
        'brand_impact': -5,
        'exp_multiplier': 1.0,
        'target_discipline': 'Human Resources',
        'is_crisis': True,
        'probability': 0.10
    },
    {
        'event_type': 'regulatory_change',
        'event_title': 'New Regulations',
        'event_description': 'Government announces new compliance requirements for your industry.',
        'capital_impact': -800,
        'morale_impact': -5,
        'brand_impact': 0,
        'exp_multiplier': 1.0,
        'target_discipline': 'Legal',
        'is_crisis': True,
        'probability': 0.08
    },
    {
        'event_type': 'investor_interest',
        'event_title': 'Investor Attention',
        'event_description': 'A venture capital firm has expressed interest in your company.',
        'capital_impact': 0,
        'morale_impact': 15,
        'brand_impact': 15,
        'exp_multiplier': 1.3,
        'target_discipline': 'Finance',
        'is_crisis': False,
        'probability': 0.08
    },
    {
        'event_type': 'viral_moment',
        'event_title': 'Viral Success',
        'event_description': 'Your brand goes viral on social media for all the right reasons!',
        'capital_impact': 1500,
        'morale_impact': 20,
        'brand_impact': 25,
        'exp_multiplier': 1.0,
        'target_discipline': 'Marketing',
        'is_crisis': False,
        'probability': 0.05
    },
    {
        'event_type': 'lawsuit',
        'event_title': 'Lawsuit Filed',
        'event_description': 'A former employee has filed a lawsuit against your company.',
        'capital_impact': -2000,
        'morale_impact': -10,
        'brand_impact': -15,
        'exp_multiplier': 1.0,
        'target_discipline': 'Legal',
        'is_crisis': True,
        'probability': 0.06
    }
]


def seed_skill_tree_abilities():
    """Seed the skill tree abilities into the database."""
    conn = get_connection()
    cur = conn.cursor()
    
    for discipline, ability in SKILL_TREE_ABILITIES.items():
        cur.execute("""
            INSERT INTO skill_tree_abilities 
            (discipline, prerequisite_subskill, ability_name, ability_code, description, 
             effect_type, effect_value, unlock_level, icon)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (ability_code) DO NOTHING
        """, (
            discipline,
            ability['subskill'],
            ability['ability_name'],
            ability['ability_code'],
            ability['description'],
            ability['effect_type'],
            ability['effect_value'],
            ability['unlock_level'],
            ability['icon']
        ))
    
    conn.commit()
    cur.close()
    return_connection(conn)


def seed_quarterly_events():
    """Seed quarterly events into the database."""
    conn = get_connection()
    cur = conn.cursor()
    
    for event in QUARTERLY_EVENTS:
        cur.execute("""
            INSERT INTO quarterly_events 
            (event_type, event_title, event_description, capital_impact, morale_impact, 
             brand_impact, exp_multiplier, target_discipline, is_crisis, probability)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (
            event['event_type'],
            event['event_title'],
            event['event_description'],
            event['capital_impact'],
            event['morale_impact'],
            event['brand_impact'],
            event['exp_multiplier'],
            event.get('target_discipline'),
            event['is_crisis'],
            event['probability']
        ))
    
    conn.commit()
    cur.close()
    return_connection(conn)


def get_company_resources(player_id: int) -> dict:
    """Get the current company resource levels."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT total_cash, team_morale, brand_equity, fiscal_quarter, decisions_this_quarter
        FROM player_profiles
        WHERE player_id = %s
    """, (player_id,))
    
    result = cur.fetchone()
    cur.close()
    return_connection(conn)
    
    if result:
        return {
            'capital': float(result['total_cash'] or 10000),
            'morale': result['team_morale'] or 100,
            'brand_equity': result['brand_equity'] or 100,
            'fiscal_quarter': result['fiscal_quarter'] or 1,
            'decisions_this_quarter': result['decisions_this_quarter'] or 0,
            'is_bankrupt': (result['brand_equity'] or 100) <= 0,
            'is_demoralized': (result['team_morale'] or 100) <= 0
        }
    
    return {
        'capital': 10000,
        'morale': 100,
        'brand_equity': 100,
        'fiscal_quarter': 1,
        'decisions_this_quarter': 0,
        'is_bankrupt': False,
        'is_demoralized': False
    }


def update_company_resources(player_id: int, capital_change: float = 0, 
                             morale_change: int = 0, brand_change: int = 0) -> dict:
    """Update company resources and check for game-over conditions."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        UPDATE player_profiles
        SET total_cash = GREATEST(0, total_cash + %s),
            team_morale = LEAST(100, GREATEST(0, team_morale + %s)),
            brand_equity = LEAST(100, GREATEST(0, brand_equity + %s))
        WHERE player_id = %s
        RETURNING total_cash, team_morale, brand_equity
    """, (capital_change, morale_change, brand_change, player_id))
    
    result = cur.fetchone()
    conn.commit()
    cur.close()
    return_connection(conn)
    
    if result:
        is_bankrupt = result['brand_equity'] <= 0
        is_demoralized = result['team_morale'] <= 0
        
        if capital_change != 0 or morale_change != 0 or brand_change != 0:
            add_news_ticker(player_id, capital_change, morale_change, brand_change)
        
        return {
            'capital': float(result['total_cash']),
            'morale': result['team_morale'],
            'brand_equity': result['brand_equity'],
            'is_bankrupt': is_bankrupt,
            'is_demoralized': is_demoralized,
            'game_over': is_bankrupt
        }
    
    return {'error': 'Player not found'}


def record_decision(player_id: int) -> dict:
    """Record a decision and check if quarter should advance."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        UPDATE player_profiles
        SET decisions_this_quarter = decisions_this_quarter + 1
        WHERE player_id = %s
        RETURNING fiscal_quarter, decisions_this_quarter
    """, (player_id,))
    
    result = cur.fetchone()
    conn.commit()
    
    quarter_result = {
        'current_quarter': result['fiscal_quarter'],
        'decisions_made': result['decisions_this_quarter'],
        'quarter_complete': False,
        'new_quarter': None,
        'quarterly_event': None
    }
    
    if result['decisions_this_quarter'] >= 3:
        quarter_result = advance_quarter(player_id, cur, conn, result['fiscal_quarter'])
    
    cur.close()
    return_connection(conn)
    
    return quarter_result


def advance_quarter(player_id: int, cur, conn, current_quarter: int) -> dict:
    """Advance to the next fiscal quarter and trigger quarterly events."""
    resources_before = get_company_resources(player_id)
    
    cur.execute("""
        INSERT INTO player_quarterly_history 
        (player_id, quarter_number, capital_start, capital_end, morale_start, morale_end, 
         brand_start, brand_end, decisions_made)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 3)
        ON CONFLICT (player_id, quarter_number) DO UPDATE
        SET capital_end = %s, morale_end = %s, brand_end = %s, decisions_made = 3
    """, (
        player_id, current_quarter,
        resources_before['capital'], resources_before['capital'],
        resources_before['morale'], resources_before['morale'],
        resources_before['brand_equity'], resources_before['brand_equity'],
        resources_before['capital'], resources_before['morale'], resources_before['brand_equity']
    ))
    
    cur.execute("""
        UPDATE player_profiles
        SET fiscal_quarter = fiscal_quarter + 1,
            decisions_this_quarter = 0
        WHERE player_id = %s
        RETURNING fiscal_quarter
    """, (player_id,))
    
    new_quarter = cur.fetchone()['fiscal_quarter']
    conn.commit()
    
    quarterly_event = trigger_quarterly_event(player_id)
    
    return {
        'current_quarter': new_quarter,
        'decisions_made': 0,
        'quarter_complete': True,
        'new_quarter': new_quarter,
        'quarterly_event': quarterly_event
    }


def trigger_quarterly_event(player_id: int) -> dict:
    """Randomly trigger a quarterly event based on probability."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT ability_code FROM player_unlocked_abilities pua
        JOIN skill_tree_abilities sta ON pua.ability_id = sta.ability_id
        WHERE pua.player_id = %s AND pua.is_active = TRUE
    """, (player_id,))
    active_abilities = [r['ability_code'] for r in cur.fetchall()]
    
    cur.execute("SELECT * FROM quarterly_events")
    events = cur.fetchall()
    cur.close()
    return_connection(conn)
    
    for event in events:
        if 'liability_shield' in active_abilities and event['event_type'] == 'lawsuit':
            continue
        
        if random.random() < float(event['probability']):
            update_company_resources(
                player_id,
                capital_change=float(event['capital_impact'] or 0),
                morale_change=event['morale_impact'] or 0,
                brand_change=event['brand_impact'] or 0
            )
            
            add_news_ticker(
                player_id,
                float(event['capital_impact'] or 0),
                event['morale_impact'] or 0,
                event['brand_impact'] or 0,
                event['event_title'],
                'crisis' if event['is_crisis'] else 'opportunity'
            )
            
            return {
                'event_type': event['event_type'],
                'title': event['event_title'],
                'description': event['event_description'],
                'is_crisis': event['is_crisis'],
                'impacts': {
                    'capital': float(event['capital_impact'] or 0),
                    'morale': event['morale_impact'] or 0,
                    'brand': event['brand_impact'] or 0
                }
            }
    
    return None


def add_news_ticker(player_id: int, capital_change: float = 0, morale_change: int = 0, 
                    brand_change: int = 0, headline: str = None, news_type: str = 'info'):
    """Add an entry to the player's news ticker."""
    if not headline:
        parts = []
        if capital_change > 0:
            headline = f"Revenue Up! +${capital_change:,.0f}"
            news_type = 'success'
        elif capital_change < 0:
            headline = f"Expense Alert: ${abs(capital_change):,.0f}"
            news_type = 'warning'
        elif morale_change > 0:
            headline = f"Team Spirit Rising! +{morale_change} Morale"
            news_type = 'success'
        elif morale_change < 0:
            headline = f"Morale Dip: {morale_change} points"
            news_type = 'warning'
        elif brand_change > 0:
            headline = f"Brand Boost! +{brand_change} Equity"
            news_type = 'success'
        elif brand_change < 0:
            headline = f"Brand Concern: {brand_change} Equity"
            news_type = 'warning'
        else:
            return
    
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO news_ticker (player_id, news_text, news_type, capital_change, morale_change, brand_change)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (player_id, headline, news_type, capital_change, morale_change, brand_change))
    
    cur.execute("""
        DELETE FROM news_ticker 
        WHERE player_id = %s 
        AND news_id NOT IN (
            SELECT news_id FROM news_ticker 
            WHERE player_id = %s 
            ORDER BY created_at DESC 
            LIMIT 20
        )
    """, (player_id, player_id))
    
    conn.commit()
    cur.close()
    return_connection(conn)


def get_news_ticker(player_id: int, limit: int = 10) -> list:
    """Get recent news ticker entries for a player."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT news_text, news_type, capital_change, morale_change, brand_change, created_at
        FROM news_ticker
        WHERE player_id = %s
        ORDER BY created_at DESC
        LIMIT %s
    """, (player_id, limit))
    
    results = cur.fetchall()
    cur.close()
    return_connection(conn)
    
    return [dict(r) for r in results]


def get_skill_tree(player_id: int) -> dict:
    """Get the player's skill tree with unlocked abilities."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT sta.*, pua.unlocked_at, pua.times_used, pua.is_active
        FROM skill_tree_abilities sta
        LEFT JOIN player_unlocked_abilities pua ON sta.ability_id = pua.ability_id AND pua.player_id = %s
    """, (player_id,))
    
    abilities = cur.fetchall()
    
    cur.execute("""
        SELECT discipline_name, current_level
        FROM player_discipline_progress
        WHERE player_id = %s
    """, (player_id,))
    
    discipline_levels = {r['discipline_name']: r['current_level'] for r in cur.fetchall()}
    
    cur.execute("""
        SELECT subskill_name, current_level
        FROM player_subskill_progress
        WHERE player_id = %s
    """, (player_id,))
    
    subskill_levels = {r['subskill_name']: r['current_level'] for r in cur.fetchall()}
    
    cur.close()
    return_connection(conn)
    
    skill_tree = {}
    for ability in abilities:
        discipline = ability['discipline']
        subskill = ability['prerequisite_subskill']
        subskill_level = subskill_levels.get(subskill, 0)
        can_unlock = subskill_level >= ability['unlock_level']
        
        skill_tree[discipline] = {
            'ability_id': ability['ability_id'],
            'ability_name': ability['ability_name'],
            'ability_code': ability['ability_code'],
            'description': ability['description'],
            'icon': ability['icon'],
            'effect_type': ability['effect_type'],
            'effect_value': float(ability['effect_value']),
            'prerequisite': subskill,
            'unlock_level': ability['unlock_level'],
            'current_subskill_level': subskill_level,
            'can_unlock': can_unlock,
            'is_unlocked': ability['unlocked_at'] is not None,
            'is_active': ability['is_active'] or False,
            'times_used': ability['times_used'] or 0
        }
    
    return skill_tree


def unlock_ability(player_id: int, ability_code: str) -> dict:
    """Unlock a skill tree ability for the player."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT ability_id, discipline, prerequisite_subskill, unlock_level
        FROM skill_tree_abilities
        WHERE ability_code = %s
    """, (ability_code,))
    
    ability = cur.fetchone()
    if not ability:
        cur.close()
        return_connection(conn)
        return {'error': 'Ability not found'}
    
    cur.execute("""
        SELECT current_level FROM player_subskill_progress
        WHERE player_id = %s AND subskill_name = %s
    """, (player_id, ability['prerequisite_subskill']))
    
    subskill = cur.fetchone()
    if not subskill or subskill['current_level'] < ability['unlock_level']:
        cur.close()
        return_connection(conn)
        return {'error': f"Need level {ability['unlock_level']} in {ability['prerequisite_subskill']} to unlock"}
    
    cur.execute("""
        INSERT INTO player_unlocked_abilities (player_id, ability_id)
        VALUES (%s, %s)
        ON CONFLICT (player_id, ability_id) DO NOTHING
        RETURNING id
    """, (player_id, ability['ability_id']))
    
    result = cur.fetchone()
    conn.commit()
    cur.close()
    return_connection(conn)
    
    if result:
        return {'success': True, 'ability_code': ability_code}
    return {'error': 'Ability already unlocked'}


def activate_ability(player_id: int, ability_code: str) -> dict:
    """Activate a skill tree ability for use this quarter."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT fiscal_quarter FROM player_profiles WHERE player_id = %s
    """, (player_id,))
    current_quarter = cur.fetchone()['fiscal_quarter']
    
    cur.execute("""
        UPDATE player_unlocked_abilities pua
        SET is_active = TRUE, last_used_quarter = %s, times_used = times_used + 1
        FROM skill_tree_abilities sta
        WHERE pua.ability_id = sta.ability_id
        AND pua.player_id = %s
        AND sta.ability_code = %s
        RETURNING sta.ability_name, sta.effect_type, sta.effect_value
    """, (current_quarter, player_id, ability_code))
    
    result = cur.fetchone()
    conn.commit()
    cur.close()
    return_connection(conn)
    
    if result:
        if result['effect_type'] == 'morale_boost':
            update_company_resources(player_id, morale_change=int(result['effect_value']))
        
        return {
            'success': True,
            'ability_name': result['ability_name'],
            'effect_type': result['effect_type'],
            'effect_value': float(result['effect_value'])
        }
    
    return {'error': 'Could not activate ability'}


def get_active_abilities(player_id: int) -> list:
    """Get all currently active abilities for a player."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT sta.ability_code, sta.ability_name, sta.effect_type, sta.effect_value, sta.icon
        FROM player_unlocked_abilities pua
        JOIN skill_tree_abilities sta ON pua.ability_id = sta.ability_id
        WHERE pua.player_id = %s AND pua.is_active = TRUE
    """, (player_id,))
    
    results = cur.fetchall()
    cur.close()
    return_connection(conn)
    
    return [dict(r) for r in results]


def apply_ability_modifiers(player_id: int, base_exp: int = 0, base_cash: float = 0, 
                            base_cost: float = 0) -> dict:
    """Apply active ability modifiers to rewards/costs."""
    active = get_active_abilities(player_id)
    
    exp_multiplier = 1.0
    revenue_multiplier = 1.0
    cost_multiplier = 1.0
    
    for ability in active:
        if ability['effect_type'] == 'exp_multiplier':
            exp_multiplier *= float(ability['effect_value'])
        elif ability['effect_type'] == 'revenue_multiplier':
            revenue_multiplier *= float(ability['effect_value'])
        elif ability['effect_type'] == 'cost_reduction':
            cost_multiplier *= float(ability['effect_value'])
    
    return {
        'final_exp': int(base_exp * exp_multiplier),
        'final_cash': base_cash * revenue_multiplier,
        'final_cost': base_cost * cost_multiplier,
        'exp_multiplier': exp_multiplier,
        'revenue_multiplier': revenue_multiplier,
        'cost_multiplier': cost_multiplier,
        'active_abilities': [a['ability_name'] for a in active]
    }


def reset_quarterly_abilities(player_id: int):
    """Reset all active abilities at the start of a new quarter."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        UPDATE player_unlocked_abilities
        SET is_active = FALSE
        WHERE player_id = %s
    """, (player_id,))
    
    conn.commit()
    cur.close()
    return_connection(conn)


def check_game_over(player_id: int) -> dict:
    """Check if the game is over due to bankruptcy or other conditions."""
    resources = get_company_resources(player_id)
    
    if resources['brand_equity'] <= 0:
        return {
            'game_over': True,
            'reason': 'bankruptcy',
            'message': 'Your brand equity has dropped to zero. The company has gone bankrupt.',
            'final_quarter': resources['fiscal_quarter']
        }
    
    if resources['morale'] <= 0:
        return {
            'game_over': False,
            'warning': True,
            'reason': 'demoralized',
            'message': 'Team morale is critically low. Actions may fail until morale recovers.',
            'morale': 0
        }
    
    return {'game_over': False, 'warning': False}


def get_dashboard_data(player_id: int) -> dict:
    """Get all data needed for the dashboard display."""
    resources = get_company_resources(player_id)
    news = get_news_ticker(player_id, limit=5)
    skill_tree = get_skill_tree(player_id)
    active_abilities = get_active_abilities(player_id)
    game_status = check_game_over(player_id)
    
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT discipline_name, current_level, current_exp
        FROM player_discipline_progress
        WHERE player_id = %s
    """, (player_id,))
    
    disciplines = {}
    for row in cur.fetchall():
        disciplines[row['discipline_name']] = {
            'level': row['current_level'],
            'exp': row['current_exp']
        }
    
    cur.close()
    return_connection(conn)
    
    radar_data = {
        'Marketing': disciplines.get('Marketing', {}).get('level', 1),
        'Finance': disciplines.get('Finance', {}).get('level', 1),
        'Operations': disciplines.get('Operations', {}).get('level', 1),
        'Human Resources': disciplines.get('Human Resources', {}).get('level', 1),
        'Legal': disciplines.get('Legal', {}).get('level', 1),
        'Strategy': disciplines.get('Strategy', {}).get('level', 1)
    }
    
    return {
        'resources': resources,
        'radar_data': radar_data,
        'disciplines': disciplines,
        'news_ticker': news,
        'skill_tree': skill_tree,
        'active_abilities': active_abilities,
        'game_status': game_status
    }
