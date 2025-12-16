"""
Core Game Engine for Business Tycoon RPG

Handles:
- Player creation and management
- Scenario loading and progression
- Decision processing and EXP rewards
- Game state management
"""

from src.database import get_connection
from src.leveling import (
    calculate_weighted_exp, 
    check_level_up, 
    get_current_level,
    get_exp_to_next_level,
    get_level_title,
    get_progress_bar,
    DISCIPLINES
)


JOB_TITLES = {
    'Restaurant': {
        1: 'Dishwasher',
        2: 'Line Cook',
        3: 'Sous Chef',
        4: 'Head Chef',
        5: 'Kitchen Manager',
        6: 'Assistant General Manager',
        7: 'General Manager',
        8: 'Regional Manager',
        9: 'Director of Operations',
        10: 'VP of Operations'
    },
    'SaaS': {
        1: 'Customer Support Rep',
        2: 'Technical Support Specialist',
        3: 'Account Manager',
        4: 'Sales Representative',
        5: 'Senior Sales Rep',
        6: 'Sales Manager',
        7: 'Director of Sales',
        8: 'VP of Sales',
        9: 'Chief Revenue Officer',
        10: 'CEO'
    }
}

class Player:
    """Represents a player in the game."""
    
    def __init__(self, player_id: int = None):
        self.player_id = player_id
        self.name = ""
        self.world = "Modern"
        self.industry = "Restaurant"
        self.career_path = "entrepreneur"
        self.job_title = None
        self.job_level = 1
        self.cash = 10000.0
        self.reputation = 50
        self.current_month = 1
        self.discipline_progress = {}
        self.stats = {
            'charisma': 5,
            'intelligence': 5,
            'luck': 5,
            'negotiation': 5,
            'stat_points': 3
        }
        self.inventory = []
        self.achievements = []
        self.active_quests = []
        
    def load_from_db(self):
        """Load player data from database."""
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM player_profiles WHERE player_id = %s", (self.player_id,))
        profile = cur.fetchone()
        
        if profile:
            self.name = profile['player_name']
            self.world = profile['chosen_world']
            self.industry = profile['chosen_industry']
            self.career_path = profile.get('career_path', 'entrepreneur')
            self.job_title = profile.get('job_title')
            self.job_level = profile.get('job_level', 1)
            self.cash = float(profile['total_cash'])
            self.reputation = profile['business_reputation']
            self.current_month = profile['current_month']
        
        cur.execute("SELECT * FROM player_discipline_progress WHERE player_id = %s", (self.player_id,))
        progress_rows = cur.fetchall()
        
        for row in progress_rows:
            self.discipline_progress[row['discipline_name']] = {
                'level': row['current_level'],
                'exp': row['current_exp'],
                'total_exp': row['total_exp_earned']
            }
        
        cur.execute("SELECT * FROM player_stats WHERE player_id = %s", (self.player_id,))
        stats_row = cur.fetchone()
        if stats_row:
            self.stats = {
                'charisma': stats_row['charisma'],
                'intelligence': stats_row['intelligence'],
                'luck': stats_row['luck'],
                'negotiation': stats_row['negotiation'],
                'stat_points': stats_row['stat_points_available']
            }
        
        cur.execute("""
            SELECT i.*, pi.quantity FROM player_inventory pi
            JOIN items i ON pi.item_id = i.item_id
            WHERE pi.player_id = %s
        """, (self.player_id,))
        self.inventory = [dict(row) for row in cur.fetchall()]
        
        cur.execute("""
            SELECT a.* FROM player_achievements pa
            JOIN achievements a ON pa.achievement_id = a.achievement_id
            WHERE pa.player_id = %s
        """, (self.player_id,))
        self.achievements = [dict(row) for row in cur.fetchall()]
        
        cur.close()
        conn.close()
        
    def save_to_db(self):
        """Save player data to database."""
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            UPDATE player_profiles 
            SET total_cash = %s, business_reputation = %s, current_month = %s, 
                career_path = %s, job_title = %s, job_level = %s, last_played = CURRENT_TIMESTAMP
            WHERE player_id = %s
        """, (self.cash, self.reputation, self.current_month, 
              self.career_path, self.job_title, self.job_level, self.player_id))
        
        for discipline, progress in self.discipline_progress.items():
            cur.execute("""
                UPDATE player_discipline_progress
                SET current_level = %s, current_exp = %s, total_exp_earned = %s
                WHERE player_id = %s AND discipline_name = %s
            """, (progress['level'], progress['exp'], progress['total_exp'], self.player_id, discipline))
        
        cur.execute("""
            UPDATE player_stats
            SET charisma = %s, intelligence = %s, luck = %s, negotiation = %s, stat_points_available = %s
            WHERE player_id = %s
        """, (self.stats['charisma'], self.stats['intelligence'], self.stats['luck'], 
              self.stats['negotiation'], self.stats['stat_points'], self.player_id))
        
        conn.commit()
        cur.close()
        conn.close()
    
    def get_discipline_level(self, discipline: str) -> int:
        """Get the current level for a discipline."""
        if discipline in self.discipline_progress:
            return self.discipline_progress[discipline]['level']
        return 1


class GameEngine:
    """Main game engine handling all game logic."""
    
    def __init__(self):
        self.current_player = None
        self.available_scenarios = []
    
    def create_new_player(self, name: str, world: str = "Modern", industry: str = "Restaurant", career_path: str = "entrepreneur") -> Player:
        """Create a new player and initialize their progress."""
        conn = get_connection()
        cur = conn.cursor()
        
        if career_path == "employee":
            starting_cash = 500.0
            starting_reputation = 25
            job_title = JOB_TITLES.get(industry, JOB_TITLES['Restaurant']).get(1, 'Entry Level')
            job_level = 1
        else:
            starting_cash = 10000.0
            starting_reputation = 50
            job_title = None
            job_level = 0
        
        cur.execute("""
            INSERT INTO player_profiles (player_name, chosen_world, chosen_industry, career_path, job_title, job_level, total_cash, business_reputation)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING player_id
        """, (name, world, industry, career_path, job_title, job_level, starting_cash, starting_reputation))
        
        player_id = cur.fetchone()['player_id']
        
        for discipline in DISCIPLINES:
            cur.execute("""
                INSERT INTO player_discipline_progress (player_id, discipline_name, current_level, current_exp, total_exp_earned)
                VALUES (%s, %s, 1, 0, 0)
            """, (player_id, discipline))
        
        cur.execute("""
            INSERT INTO player_stats (player_id, charisma, intelligence, luck, negotiation, stat_points_available)
            VALUES (%s, 5, 5, 5, 5, 3)
        """, (player_id,))
        
        cur.execute("""
            INSERT INTO player_avatar (player_id, hair_style, outfit, accessory, color_scheme)
            VALUES (%s, 'default', 'default', 'none', 'blue')
        """, (player_id,))
        
        conn.commit()
        cur.close()
        conn.close()
        
        player = Player(player_id)
        player.name = name
        player.world = world
        player.career_path = career_path
        player.job_title = job_title
        player.job_level = job_level
        player.cash = starting_cash
        player.reputation = starting_reputation
        player.industry = industry
        player.discipline_progress = {d: {'level': 1, 'exp': 0, 'total_exp': 0} for d in DISCIPLINES}
        player.stats = {'charisma': 5, 'intelligence': 5, 'luck': 5, 'negotiation': 5, 'stat_points': 3}
        
        self.current_player = player
        return player
    
    def load_player(self, player_id: int) -> Player:
        """Load an existing player."""
        player = Player(player_id)
        player.load_from_db()
        self.current_player = player
        return player
    
    def get_all_players(self) -> list:
        """Get list of all saved players."""
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT player_id, player_name, chosen_world, chosen_industry, total_cash FROM player_profiles ORDER BY last_played DESC")
        players = cur.fetchall()
        
        cur.close()
        conn.close()
        return players
    
    def get_scenario_by_id(self, scenario_id: int) -> dict:
        """Get a specific scenario by ID."""
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM scenario_master WHERE scenario_id = %s", (scenario_id,))
        scenario = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return dict(scenario) if scenario else None
    
    def is_scenario_completed(self, scenario_id: int) -> bool:
        """Check if a scenario has been completed by the current player."""
        if not self.current_player:
            return False
        
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT 1 FROM completed_scenarios 
            WHERE player_id = %s AND scenario_id = %s
        """, (self.current_player.player_id, scenario_id))
        result = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return result is not None
    
    def get_available_scenarios(self, discipline: str = None) -> list:
        """Get scenarios available for the current player based on their level."""
        if not self.current_player:
            return []
        
        conn = get_connection()
        cur = conn.cursor()
        
        query = """
            SELECT s.* FROM scenario_master s
            LEFT JOIN completed_scenarios cs ON s.scenario_id = cs.scenario_id AND cs.player_id = %s
            WHERE s.world_type = %s 
            AND s.industry = %s 
            AND s.is_active = TRUE
            AND cs.scenario_id IS NULL
        """
        params = [self.current_player.player_id, self.current_player.world, self.current_player.industry]
        
        if discipline:
            query += " AND s.discipline = %s"
            params.append(discipline)
            
            player_level = self.current_player.get_discipline_level(discipline)
            query += " AND s.required_level <= %s"
            params.append(player_level)
        
        query += " ORDER BY s.required_level, s.scenario_id"
        
        cur.execute(query, params)
        scenarios = cur.fetchall()
        
        cur.close()
        conn.close()
        
        self.available_scenarios = scenarios
        return scenarios
    
    def process_choice(self, scenario: dict, choice: str) -> dict:
        """
        Process a player's choice for a scenario.
        Returns result dict with EXP gained, cash change, reputation change, and feedback.
        """
        if not self.current_player:
            return {"error": "No player loaded"}
        
        choice = choice.upper()
        if choice not in ['A', 'B', 'C']:
            return {"error": "Invalid choice"}
        
        if choice == 'C' and not scenario.get('choice_c_text'):
            return {"error": "Choice C not available for this scenario"}
        
        choice_prefix = f"choice_{choice.lower()}"
        base_exp = scenario[f'{choice_prefix}_exp_reward']
        cash_change = float(scenario[f'{choice_prefix}_cash_change'] or 0)
        reputation_change = scenario[f'{choice_prefix}_reputation_change'] or 0
        feedback = scenario[f'{choice_prefix}_feedback']
        
        discipline = scenario['discipline']
        weighted_exp = calculate_weighted_exp(
            base_exp, 
            self.current_player.industry, 
            discipline
        )
        
        progress = self.current_player.discipline_progress[discipline]
        old_exp = progress['total_exp']
        new_exp = old_exp + weighted_exp
        
        leveled_up, old_level, new_level = check_level_up(old_exp, new_exp)
        
        progress['total_exp'] = new_exp
        progress['exp'] = new_exp
        progress['level'] = new_level
        
        self.current_player.cash += cash_change
        self.current_player.reputation = max(0, min(100, self.current_player.reputation + reputation_change))
        
        promotion = None
        if self.current_player.career_path == 'employee' and leveled_up:
            if new_level > self.current_player.job_level:
                self.current_player.job_level = new_level
                job_titles = JOB_TITLES.get(self.current_player.industry, JOB_TITLES['Restaurant'])
                new_title = job_titles.get(new_level, job_titles.get(10, 'Senior Executive'))
                self.current_player.job_title = new_title
                promotion = {
                    'old_level': old_level,
                    'new_level': new_level,
                    'new_title': new_title
                }
        
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO completed_scenarios (player_id, scenario_id, choice_made)
            VALUES (%s, %s, %s)
            ON CONFLICT (player_id, scenario_id) DO NOTHING
        """, (self.current_player.player_id, scenario['scenario_id'], choice))
        conn.commit()
        cur.close()
        conn.close()
        
        self.current_player.save_to_db()
        
        return {
            "success": True,
            "exp_gained": weighted_exp,
            "base_exp": base_exp,
            "cash_change": cash_change,
            "reputation_change": reputation_change,
            "feedback": feedback,
            "leveled_up": leveled_up,
            "old_level": old_level,
            "new_level": new_level,
            "discipline": discipline,
            "new_total_exp": new_exp,
            "promotion": promotion
        }
    
    def get_player_stats(self) -> dict:
        """Get comprehensive player statistics."""
        if not self.current_player:
            return {}
        
        p = self.current_player
        stats = {
            "name": p.name,
            "world": p.world,
            "industry": p.industry,
            "career_path": p.career_path,
            "job_title": p.job_title,
            "job_level": p.job_level,
            "cash": p.cash,
            "reputation": p.reputation,
            "month": p.current_month,
            "disciplines": {},
            "character_stats": p.stats,
            "inventory": p.inventory,
            "achievements": p.achievements
        }
        
        for discipline, progress in p.discipline_progress.items():
            level = progress['level']
            total_exp = progress['total_exp']
            exp_needed, next_level = get_exp_to_next_level(total_exp)
            
            stats["disciplines"][discipline] = {
                "level": level,
                "title": get_level_title(level),
                "total_exp": total_exp,
                "exp_to_next": exp_needed,
                "next_level": next_level,
                "progress_bar": get_progress_bar(total_exp, level)
            }
        
        return stats
    
    def allocate_stat(self, stat_name: str) -> dict:
        """Allocate a stat point to a specific stat."""
        if not self.current_player:
            return {"error": "No player loaded"}
        
        valid_stats = ['charisma', 'intelligence', 'luck', 'negotiation']
        if stat_name not in valid_stats:
            return {"error": "Invalid stat name"}
        
        if self.current_player.stats['stat_points'] <= 0:
            return {"error": "No stat points available"}
        
        self.current_player.stats[stat_name] += 1
        self.current_player.stats['stat_points'] -= 1
        self.current_player.save_to_db()
        
        return {"success": True, "stat": stat_name, "new_value": self.current_player.stats[stat_name]}
    
    def get_shop_items(self) -> list:
        """Get all items available in the shop."""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM items ORDER BY purchase_price")
        items = [dict(row) for row in cur.fetchall()]
        cur.close()
        conn.close()
        return items
    
    def purchase_item(self, item_id: int) -> dict:
        """Purchase an item from the shop."""
        if not self.current_player:
            return {"error": "No player loaded"}
        
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM items WHERE item_id = %s", (item_id,))
        item = cur.fetchone()
        
        if not item:
            cur.close()
            conn.close()
            return {"error": "Item not found"}
        
        price = float(item['purchase_price'])
        if self.current_player.cash < price:
            cur.close()
            conn.close()
            return {"error": "Not enough cash"}
        
        self.current_player.cash -= price
        
        cur.execute("""
            INSERT INTO player_inventory (player_id, item_id, quantity)
            VALUES (%s, %s, 1)
            ON CONFLICT (player_id, item_id) DO UPDATE SET quantity = player_inventory.quantity + 1
        """, (self.current_player.player_id, item_id))
        
        conn.commit()
        cur.close()
        conn.close()
        
        self.current_player.save_to_db()
        self.current_player.load_from_db()
        
        return {"success": True, "item": dict(item), "new_cash": self.current_player.cash}
    
    def get_npcs(self) -> list:
        """Get NPCs available in the current world."""
        if not self.current_player:
            return []
        
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT n.*, COALESCE(pnr.relationship_level, 0) as relationship
            FROM npcs n
            LEFT JOIN player_npc_relationships pnr ON n.npc_id = pnr.npc_id AND pnr.player_id = %s
            WHERE n.world_type = %s
            ORDER BY n.npc_name
        """, (self.current_player.player_id, self.current_player.world))
        npcs = [dict(row) for row in cur.fetchall()]
        cur.close()
        conn.close()
        return npcs
    
    def interact_with_npc(self, npc_id: int) -> dict:
        """Interact with an NPC."""
        if not self.current_player:
            return {"error": "No player loaded"}
        
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM npcs WHERE npc_id = %s", (npc_id,))
        npc = cur.fetchone()
        
        if not npc:
            cur.close()
            conn.close()
            return {"error": "NPC not found"}
        
        cur.execute("""
            INSERT INTO player_npc_relationships (player_id, npc_id, relationship_level, times_interacted, last_interaction)
            VALUES (%s, %s, 1, 1, CURRENT_TIMESTAMP)
            ON CONFLICT (player_id, npc_id) DO UPDATE 
            SET relationship_level = player_npc_relationships.relationship_level + 1,
                times_interacted = player_npc_relationships.times_interacted + 1,
                last_interaction = CURRENT_TIMESTAMP
            RETURNING relationship_level
        """, (self.current_player.player_id, npc_id))
        
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        return {"success": True, "npc": dict(npc), "relationship_level": result['relationship_level']}
    
    def get_quests(self) -> dict:
        """Get available and active quests."""
        if not self.current_player:
            return {"available": [], "active": [], "completed": []}
        
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT q.*, pq.status, pq.progress
            FROM quests q
            LEFT JOIN player_quests pq ON q.quest_id = pq.quest_id AND pq.player_id = %s
            WHERE q.world_type = %s
            ORDER BY q.required_level, q.quest_id
        """, (self.current_player.player_id, self.current_player.world))
        
        quests = {"available": [], "active": [], "completed": []}
        for row in cur.fetchall():
            quest = dict(row)
            status = quest.get('status')
            if status == 'completed':
                quests['completed'].append(quest)
            elif status == 'active':
                quests['active'].append(quest)
            else:
                quests['available'].append(quest)
        
        cur.close()
        conn.close()
        return quests
    
    def start_quest(self, quest_id: int) -> dict:
        """Start a quest."""
        if not self.current_player:
            return {"error": "No player loaded"}
        
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM quests WHERE quest_id = %s", (quest_id,))
        quest = cur.fetchone()
        
        if not quest:
            cur.close()
            conn.close()
            return {"error": "Quest not found"}
        
        cur.execute("""
            INSERT INTO player_quests (player_id, quest_id, status, started_at)
            VALUES (%s, %s, 'active', CURRENT_TIMESTAMP)
            ON CONFLICT (player_id, quest_id) DO NOTHING
        """, (self.current_player.player_id, quest_id))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return {"success": True, "quest": dict(quest)}
    
    def get_all_achievements(self) -> list:
        """Get all achievements with earned status."""
        if not self.current_player:
            return []
        
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT a.*, 
                   CASE WHEN pa.player_id IS NOT NULL THEN TRUE ELSE FALSE END as earned
            FROM achievements a
            LEFT JOIN player_achievements pa ON a.achievement_id = pa.achievement_id AND pa.player_id = %s
            ORDER BY a.achievement_id
        """, (self.current_player.player_id,))
        achievements = [dict(row) for row in cur.fetchall()]
        cur.close()
        conn.close()
        return achievements

    def get_random_event(self) -> dict:
        """Get a random event for the player based on their level and world."""
        if not self.current_player:
            return None
        
        import random
        conn = get_connection()
        cur = conn.cursor()
        
        max_level = max([d['level'] for d in self.current_player.discipline_progress.values()], default=1)
        
        cur.execute("""
            SELECT * FROM random_events 
            WHERE world_type = %s 
            AND (industry = %s OR industry IS NULL)
            AND min_level <= %s
            ORDER BY RANDOM() LIMIT 1
        """, (self.current_player.world, self.current_player.industry, max_level))
        
        event = cur.fetchone()
        cur.close()
        conn.close()
        
        return dict(event) if event else None

    def process_random_event(self, event_id: int, choice: str) -> dict:
        """Process a random event choice."""
        if not self.current_player:
            return {"error": "No player loaded"}
        
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM random_events WHERE event_id = %s", (event_id,))
        event = cur.fetchone()
        
        if not event:
            cur.close()
            conn.close()
            return {"error": "Event not found"}
        
        if choice.upper() == 'A':
            cash_change = float(event['choice_a_cash_change'])
            rep_change = event['choice_a_reputation_change']
            feedback = event['choice_a_feedback']
        else:
            cash_change = float(event['choice_b_cash_change'])
            rep_change = event['choice_b_reputation_change']
            feedback = event['choice_b_feedback']
        
        self.current_player.cash += cash_change
        self.current_player.reputation = max(0, min(100, self.current_player.reputation + rep_change))
        self.current_player.save_to_db()
        
        cur.execute("""
            INSERT INTO player_event_history (player_id, event_id, choice_made)
            VALUES (%s, %s, %s)
        """, (self.current_player.player_id, event_id, choice.upper()))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return {
            "event_name": event['event_name'],
            "feedback": feedback,
            "cash_change": cash_change,
            "reputation_change": rep_change
        }

    def get_milestones(self) -> dict:
        """Get all milestones with earned status."""
        if not self.current_player:
            return {"earned": [], "available": []}
        
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT m.*, 
                   CASE WHEN pm.player_id IS NOT NULL THEN TRUE ELSE FALSE END as earned
            FROM business_milestones m
            LEFT JOIN player_milestones pm ON m.milestone_id = pm.milestone_id AND pm.player_id = %s
            ORDER BY m.target_value
        """, (self.current_player.player_id,))
        
        all_milestones = [dict(row) for row in cur.fetchall()]
        cur.close()
        conn.close()
        
        earned = [m for m in all_milestones if m['earned']]
        available = [m for m in all_milestones if not m['earned']]
        
        return {"earned": earned, "available": available}

    def get_financial_history(self) -> list:
        """Get financial history for dashboard charts."""
        if not self.current_player:
            return []
        
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT * FROM financial_metrics 
            WHERE player_id = %s 
            ORDER BY month_number DESC LIMIT 12
        """, (self.current_player.player_id,))
        history = [dict(row) for row in cur.fetchall()]
        cur.close()
        conn.close()
        return history

    def get_rivals(self) -> list:
        """Get all rivals with competition status."""
        if not self.current_player:
            return []
        
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT r.*, 
                   COALESCE(prs.competition_score, 0) as score,
                   COALESCE(prs.times_beaten, 0) as wins,
                   COALESCE(prs.times_lost, 0) as losses
            FROM rivals r
            LEFT JOIN player_rival_status prs ON r.rival_id = prs.rival_id AND prs.player_id = %s
            WHERE r.world_type = %s AND r.industry = %s
            ORDER BY r.difficulty_level
        """, (self.current_player.player_id, self.current_player.world, self.current_player.industry))
        
        rivals = [dict(row) for row in cur.fetchall()]
        cur.close()
        conn.close()
        return rivals

    def get_weekly_challenges(self) -> dict:
        """Get weekly challenges with progress."""
        if not self.current_player:
            return {"active": [], "completed": []}
        
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT wc.*, 
                   COALESCE(pcp.current_progress, 0) as progress,
                   COALESCE(pcp.completed, FALSE) as is_completed
            FROM weekly_challenges wc
            LEFT JOIN player_challenge_progress pcp ON wc.challenge_id = pcp.challenge_id AND pcp.player_id = %s
            WHERE wc.is_active = TRUE
            ORDER BY wc.challenge_id
        """, (self.current_player.player_id,))
        
        all_challenges = [dict(row) for row in cur.fetchall()]
        cur.close()
        conn.close()
        
        active = [c for c in all_challenges if not c['is_completed']]
        completed = [c for c in all_challenges if c['is_completed']]
        
        return {"active": active, "completed": completed}

    def get_avatar_options(self) -> dict:
        """Get all avatar customization options."""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM avatar_options ORDER BY option_type, unlock_level, unlock_cost")
        options = [dict(row) for row in cur.fetchall()]
        cur.close()
        conn.close()
        
        categorized = {"hair": [], "outfit": [], "accessory": [], "color": []}
        for opt in options:
            opt_type = opt['option_type']
            if opt_type in categorized:
                categorized[opt_type].append(opt)
        
        return categorized

    def get_player_avatar(self) -> dict:
        """Get current player avatar settings."""
        if not self.current_player:
            return {"hair_style": "default", "outfit": "default", "accessory": "none", "color_scheme": "blue"}
        
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM player_avatar WHERE player_id = %s", (self.current_player.player_id,))
        avatar = cur.fetchone()
        cur.close()
        conn.close()
        
        if avatar:
            return dict(avatar)
        return {"hair_style": "default", "outfit": "default", "accessory": "none", "color_scheme": "blue"}

    def update_avatar(self, hair: str, outfit: str, accessory: str, color: str) -> dict:
        """Update player avatar settings."""
        if not self.current_player:
            return {"error": "No player loaded"}
        
        conn = get_connection()
        cur = conn.cursor()
        
        current_avatar = self.get_player_avatar()
        total_cost = 0.0
        
        option_codes = [hair, outfit, accessory, color]
        for code in option_codes:
            cur.execute("SELECT unlock_cost FROM avatar_options WHERE option_code = %s", (code,))
            opt = cur.fetchone()
            if opt:
                total_cost += float(opt['unlock_cost'])
        
        if total_cost > self.current_player.cash:
            cur.close()
            conn.close()
            return {"error": f"Not enough cash! Need ${total_cost:.2f}"}
        
        cur.execute("""
            INSERT INTO player_avatar (player_id, hair_style, outfit, accessory, color_scheme)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (player_id) DO UPDATE SET
                hair_style = EXCLUDED.hair_style,
                outfit = EXCLUDED.outfit,
                accessory = EXCLUDED.accessory,
                color_scheme = EXCLUDED.color_scheme
        """, (self.current_player.player_id, hair, outfit, accessory, color))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return {"success": True}


def display_scenario(scenario: dict) -> None:
    """Display a scenario in the console."""
    print("\n" + "=" * 60)
    print(f"📋 {scenario['scenario_title']}")
    print(f"   [{scenario['discipline']} - Level {scenario['required_level']}]")
    print("=" * 60)
    print(f"\n{scenario['scenario_narrative']}\n")
    print("-" * 40)
    print(f"  A) {scenario['choice_a_text']}")
    print(f"  B) {scenario['choice_b_text']}")
    if scenario.get('choice_c_text'):
        print(f"  C) {scenario['choice_c_text']}")
    print("-" * 40)


def display_result(result: dict) -> None:
    """Display the result of a choice."""
    print("\n" + "=" * 60)
    print("📊 RESULT")
    print("=" * 60)
    print(f"\n{result['feedback']}\n")
    print(f"  💡 EXP Gained: +{result['exp_gained']} (base: {result['base_exp']})")
    
    if result['cash_change'] != 0:
        sign = "+" if result['cash_change'] > 0 else ""
        print(f"  💰 Cash: {sign}${result['cash_change']:,.2f}")
    
    if result['reputation_change'] != 0:
        sign = "+" if result['reputation_change'] > 0 else ""
        print(f"  ⭐ Reputation: {sign}{result['reputation_change']}")
    
    if result['leveled_up']:
        print(f"\n  🎉 LEVEL UP! {result['discipline']}: Level {result['old_level']} → Level {result['new_level']}!")
        print(f"     New Title: {get_level_title(result['new_level'])}")
    
    print()


def display_player_stats(stats: dict) -> None:
    """Display player statistics."""
    print("\n" + "=" * 60)
    print(f"👤 {stats['name']} | {stats['world']} World | {stats['industry']} Industry")
    print("=" * 60)
    print(f"  💰 Cash: ${stats['cash']:,.2f}")
    print(f"  ⭐ Reputation: {stats['reputation']}/100")
    print(f"  📅 Month: {stats['month']}")
    print("\n📈 DISCIPLINE PROGRESS:")
    print("-" * 40)
    
    for discipline, data in stats['disciplines'].items():
        print(f"  {discipline}: Level {data['level']} - {data['title']}")
        print(f"    {data['progress_bar']} ({data['total_exp']:,} EXP)")
        if data['exp_to_next'] > 0:
            print(f"    {data['exp_to_next']:,} EXP to Level {data['next_level']}")
        print()
