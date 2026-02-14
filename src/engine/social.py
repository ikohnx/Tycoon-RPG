"""
SocialMixin - Social/shop/NPC/quest-related GameEngine methods.
"""

import random
from src.database import get_connection, return_connection


class SocialMixin:
    """Mixin providing social interaction methods for GameEngine."""

    def get_shop_items(self) -> list:
        """Get all items available in the shop."""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM items ORDER BY purchase_price")
        items = [dict(row) for row in cur.fetchall()]
        cur.close()
        return_connection(conn)
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
            return_connection(conn)
            return {"error": "Item not found"}
        
        price = float(item['purchase_price'])
        if self.current_player.cash < price:
            cur.close()
            return_connection(conn)
            return {"error": "Not enough cash"}
        
        self.current_player.cash -= price
        
        cur.execute("""
            INSERT INTO player_inventory (player_id, item_id, quantity)
            VALUES (%s, %s, 1)
            ON CONFLICT (player_id, item_id) DO UPDATE SET quantity = player_inventory.quantity + 1
        """, (self.current_player.player_id, item_id))
        
        conn.commit()
        cur.close()
        return_connection(conn)
        
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
        return_connection(conn)
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
            return_connection(conn)
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
        return_connection(conn)
        
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
        return_connection(conn)
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
            return_connection(conn)
            return {"error": "Quest not found"}
        
        cur.execute("""
            INSERT INTO player_quests (player_id, quest_id, status, started_at)
            VALUES (%s, %s, 'active', CURRENT_TIMESTAMP)
            ON CONFLICT (player_id, quest_id) DO NOTHING
        """, (self.current_player.player_id, quest_id))
        
        conn.commit()
        cur.close()
        return_connection(conn)
        
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
        return_connection(conn)
        return achievements

    def get_random_event(self) -> dict:
        """Get a random event for the player based on their level and world."""
        if not self.current_player:
            return None
        
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
        return_connection(conn)
        
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
            return_connection(conn)
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
        return_connection(conn)
        
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
        return_connection(conn)
        
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
        return_connection(conn)
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
        return_connection(conn)
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
        return_connection(conn)
        
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
        return_connection(conn)
        
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
        return_connection(conn)
        
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
            return_connection(conn)
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
        return_connection(conn)
        
        return {"success": True}

    def get_advisors(self) -> dict:
        """Get all advisors and player's recruited advisors."""
        if not self.current_player:
            return {"error": "No player loaded"}
        
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM advisors ORDER BY rarity, discipline_specialty")
        all_advisors = cur.fetchall()
        
        cur.execute("""
            SELECT a.*, pa.level as recruited_level, pa.is_active
            FROM advisors a
            JOIN player_advisors pa ON a.advisor_id = pa.advisor_id
            WHERE pa.player_id = %s
        """, (self.current_player.player_id,))
        recruited = cur.fetchall()
        recruited_ids = {r['advisor_id'] for r in recruited}
        
        cur.close()
        return_connection(conn)
        
        return {
            "all_advisors": [dict(a) for a in all_advisors],
            "recruited": [dict(r) for r in recruited],
            "recruited_ids": recruited_ids
        }
    
    def recruit_advisor(self, advisor_id: int) -> dict:
        """Recruit an advisor for the player."""
        if not self.current_player:
            return {"error": "No player loaded"}
        
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM advisors WHERE advisor_id = %s", (advisor_id,))
        advisor = cur.fetchone()
        
        if not advisor:
            cur.close()
            return_connection(conn)
            return {"error": "Advisor not found"}
        
        cur.execute("""
            SELECT * FROM player_advisors WHERE player_id = %s AND advisor_id = %s
        """, (self.current_player.player_id, advisor_id))
        if cur.fetchone():
            cur.close()
            return_connection(conn)
            return {"error": "Already recruited this advisor"}
        
        cost = float(advisor['unlock_cost'])
        if self.current_player.cash < cost:
            cur.close()
            return_connection(conn)
            return {"error": f"Not enough gold! Need ${cost:,.0f}"}
        
        self.current_player.cash -= cost
        self.current_player.save_to_db()
        
        cur.execute("""
            INSERT INTO player_advisors (player_id, advisor_id, level, is_active)
            VALUES (%s, %s, 1, TRUE)
        """, (self.current_player.player_id, advisor_id))
        
        conn.commit()
        cur.close()
        return_connection(conn)
        
        return {
            "success": True,
            "advisor_name": advisor['advisor_name'],
            "cost": cost,
            "new_cash": self.current_player.cash
        }
    
    def get_equipment(self) -> dict:
        """Get all equipment and player's owned/equipped gear."""
        if not self.current_player:
            return {"error": "No player loaded"}
        
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM equipment ORDER BY slot_type, level_required")
        all_equipment = cur.fetchall()
        
        cur.execute("""
            SELECT e.*, pe.is_equipped
            FROM equipment e
            JOIN player_equipment pe ON e.equipment_id = pe.equipment_id
            WHERE pe.player_id = %s
        """, (self.current_player.player_id,))
        owned = cur.fetchall()
        owned_ids = {o['equipment_id'] for o in owned}
        
        cur.close()
        return_connection(conn)
        
        return {
            "all_equipment": [dict(e) for e in all_equipment],
            "owned": [dict(o) for o in owned],
            "owned_ids": owned_ids
        }
    
    def purchase_equipment(self, equipment_id: int) -> dict:
        """Purchase equipment for the player."""
        if not self.current_player:
            return {"error": "No player loaded"}
        
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM equipment WHERE equipment_id = %s", (equipment_id,))
        equip = cur.fetchone()
        
        if not equip:
            cur.close()
            return_connection(conn)
            return {"error": "Equipment not found"}
        
        cur.execute("""
            SELECT * FROM player_equipment WHERE player_id = %s AND equipment_id = %s
        """, (self.current_player.player_id, equipment_id))
        if cur.fetchone():
            cur.close()
            return_connection(conn)
            return {"error": "Already own this equipment"}
        
        cost = float(equip['purchase_price'])
        if self.current_player.cash < cost:
            cur.close()
            return_connection(conn)
            return {"error": f"Not enough gold! Need ${cost:,.0f}"}
        
        self.current_player.cash -= cost
        self.current_player.save_to_db()
        
        cur.execute("""
            INSERT INTO player_equipment (player_id, equipment_id, slot_type, is_equipped)
            VALUES (%s, %s, %s, FALSE)
        """, (self.current_player.player_id, equipment_id, equip['slot_type']))
        
        conn.commit()
        cur.close()
        return_connection(conn)
        
        return {
            "success": True,
            "equipment_name": equip['equipment_name'],
            "cost": cost,
            "new_cash": self.current_player.cash
        }
    
    def equip_item(self, equipment_id: int) -> dict:
        """Equip an item to the appropriate slot."""
        if not self.current_player:
            return {"error": "No player loaded"}
        
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT e.*, pe.id as player_equip_id 
            FROM equipment e
            JOIN player_equipment pe ON e.equipment_id = pe.equipment_id
            WHERE pe.player_id = %s AND e.equipment_id = %s
        """, (self.current_player.player_id, equipment_id))
        equip = cur.fetchone()
        
        if not equip:
            cur.close()
            return_connection(conn)
            return {"error": "You don't own this equipment"}
        
        slot = equip['slot_type']
        
        cur.execute("""
            UPDATE player_equipment SET is_equipped = FALSE
            WHERE player_id = %s AND slot_type = %s
        """, (self.current_player.player_id, slot))
        
        cur.execute("""
            UPDATE player_equipment SET is_equipped = TRUE
            WHERE player_id = %s AND equipment_id = %s
        """, (self.current_player.player_id, equipment_id))
        
        conn.commit()
        cur.close()
        return_connection(conn)
        
        return {
            "success": True,
            "equipped": equip['equipment_name'],
            "slot": slot
        }
