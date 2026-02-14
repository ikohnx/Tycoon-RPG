"""
ProgressionMixin - Progression-related GameEngine methods.
"""

import random
import datetime
from src.database import get_connection, return_connection
from src.leveling import DISCIPLINES


class ProgressionMixin:
    """Mixin providing progression-related methods for GameEngine."""

    def get_player_energy(self) -> dict:
        """Get current player energy with auto-recharge calculation."""
        if not self.current_player:
            return {"error": "No player loaded"}
        
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT * FROM player_energy WHERE player_id = %s
        """, (self.current_player.player_id,))
        energy_row = cur.fetchone()
        
        if not energy_row:
            cur.execute("""
                INSERT INTO player_energy (player_id, current_energy, max_energy, last_recharge_at)
                VALUES (%s, 100, 100, CURRENT_TIMESTAMP)
                RETURNING *
            """, (self.current_player.player_id,))
            energy_row = cur.fetchone()
            conn.commit()
        
        current_energy = energy_row['current_energy']
        max_energy = energy_row['max_energy']
        last_recharge = energy_row['last_recharge_at']
        
        now = datetime.datetime.now(datetime.timezone.utc)
        if last_recharge.tzinfo is None:
            last_recharge = last_recharge.replace(tzinfo=datetime.timezone.utc)
        
        minutes_elapsed = (now - last_recharge).total_seconds() / 60
        energy_to_add = int(minutes_elapsed / 5)
        
        if energy_to_add > 0 and current_energy < max_energy:
            new_energy = min(max_energy, current_energy + energy_to_add)
            cur.execute("""
                UPDATE player_energy 
                SET current_energy = %s, last_recharge_at = CURRENT_TIMESTAMP
                WHERE player_id = %s
            """, (new_energy, self.current_player.player_id))
            conn.commit()
            current_energy = new_energy
        
        next_recharge_seconds = (5 - (minutes_elapsed % 5)) * 60 if current_energy < max_energy else 0
        
        cur.close()
        return_connection(conn)
        
        return {
            "current_energy": current_energy,
            "max_energy": max_energy,
            "next_recharge_in": int(next_recharge_seconds)
        }
    
    def consume_energy(self, amount: int = 10) -> dict:
        """Consume energy when playing a scenario."""
        if not self.current_player:
            return {"error": "No player loaded"}
        
        energy_info = self.get_player_energy()
        if "error" in energy_info:
            return energy_info
        
        if energy_info['current_energy'] < amount:
            return {"error": f"Not enough energy! Need {amount}, have {energy_info['current_energy']}"}
        
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            UPDATE player_energy 
            SET current_energy = current_energy - %s
            WHERE player_id = %s
            RETURNING current_energy
        """, (amount, self.current_player.player_id))
        result = cur.fetchone()
        conn.commit()
        cur.close()
        return_connection(conn)
        
        return {"success": True, "new_energy": result['current_energy']}
    
    def recharge_energy(self, amount: int) -> dict:
        """Add energy from rewards or items."""
        if not self.current_player:
            return {"error": "No player loaded"}
        
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            UPDATE player_energy 
            SET current_energy = LEAST(max_energy, current_energy + %s)
            WHERE player_id = %s
            RETURNING current_energy, max_energy
        """, (amount, self.current_player.player_id))
        result = cur.fetchone()
        conn.commit()
        cur.close()
        return_connection(conn)
        
        if result:
            return {"success": True, "new_energy": result['current_energy'], "max_energy": result['max_energy']}
        return {"error": "Failed to recharge energy"}
    
    def get_daily_login_status(self) -> dict:
        """Get daily login status and available rewards."""
        if not self.current_player:
            return {"error": "No player loaded"}
        
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT * FROM player_daily_login WHERE player_id = %s
        """, (self.current_player.player_id,))
        login_row = cur.fetchone()
        
        today = datetime.date.today()
        
        if not login_row:
            cur.execute("""
                INSERT INTO player_daily_login (player_id, current_streak, longest_streak, last_login_date, last_claim_date)
                VALUES (%s, 0, 0, NULL, NULL)
                RETURNING *
            """, (self.current_player.player_id,))
            login_row = cur.fetchone()
            conn.commit()
        
        current_streak = login_row['current_streak']
        longest_streak = login_row['longest_streak']
        last_login = login_row['last_login_date']
        last_claim = login_row['last_claim_date']
        
        can_claim = False
        streak_broken = False
        
        if last_claim is None:
            can_claim = True
        elif isinstance(last_claim, datetime.datetime):
            last_claim = last_claim.date()
        
        if last_claim and last_claim < today:
            can_claim = True
            if last_claim < today - datetime.timedelta(days=1):
                streak_broken = True
        
        reward_day = (current_streak % 7) + 1 if not streak_broken else 1
        
        cur.execute("""
            SELECT * FROM daily_login_rewards WHERE day_number = %s
        """, (reward_day,))
        reward = cur.fetchone()
        
        cur.close()
        return_connection(conn)
        
        return {
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "can_claim": can_claim,
            "streak_broken": streak_broken,
            "reward_day": reward_day,
            "reward": dict(reward) if reward else None
        }
    
    def claim_daily_login(self) -> dict:
        """Claim daily login reward."""
        if not self.current_player:
            return {"error": "No player loaded"}
        
        status = self.get_daily_login_status()
        if status.get("error"):
            return status
        
        if not status['can_claim']:
            return {"error": "Already claimed today!"}
        
        conn = get_connection()
        cur = conn.cursor()
        
        today = datetime.date.today()
        new_streak = 1 if status['streak_broken'] else status['current_streak'] + 1
        longest = max(status['longest_streak'], new_streak)
        
        cur.execute("""
            UPDATE player_daily_login 
            SET current_streak = %s, longest_streak = %s, last_login_date = %s, last_claim_date = %s
            WHERE player_id = %s
        """, (new_streak, longest, today, today, self.current_player.player_id))
        
        reward = status['reward']
        rewards_given = []
        
        if reward:
            if reward['reward_type'] == 'gold' and reward['reward_value']:
                self.current_player.cash += float(reward['reward_value'])
                rewards_given.append(f"+${reward['reward_value']:,.0f} Gold")
            elif reward['reward_type'] == 'energy' and reward['reward_value']:
                self.recharge_energy(int(reward['reward_value']))
                rewards_given.append(f"+{reward['reward_value']} Energy")
            elif reward['reward_type'] == 'exp' and reward['reward_value']:
                rewards_given.append(f"+{reward['reward_value']} EXP Bonus")
        
        self.current_player.save_to_db()
        conn.commit()
        cur.close()
        return_connection(conn)
        
        return {
            "success": True,
            "new_streak": new_streak,
            "longest_streak": longest,
            "rewards_given": rewards_given,
            "reward_day": status['reward_day']
        }
    
    def get_idle_income_status(self) -> dict:
        """Get current idle income status with accumulated gold."""
        if not self.current_player:
            return {"error": "No player loaded"}
        
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT * FROM player_idle_income WHERE player_id = %s
        """, (self.current_player.player_id,))
        row = cur.fetchone()
        
        now = datetime.datetime.now()
        
        if not row:
            base_rate = self._calculate_base_idle_rate()
            cur.execute("""
                INSERT INTO player_idle_income (player_id, gold_per_minute, last_collection_at, uncollected_gold)
                VALUES (%s, %s, %s, 0)
                RETURNING *
            """, (self.current_player.player_id, base_rate, now))
            row = cur.fetchone()
            conn.commit()
        
        last_collection = row['last_collection_at']
        gold_per_minute = float(row['gold_per_minute'])
        
        if last_collection:
            minutes_elapsed = (now - last_collection).total_seconds() / 60
            minutes_elapsed = min(minutes_elapsed, 480)
            accumulated = minutes_elapsed * gold_per_minute
        else:
            accumulated = 0
        
        cur.close()
        return_connection(conn)
        
        return {
            "gold_per_minute": gold_per_minute,
            "gold_per_hour": gold_per_minute * 60,
            "accumulated_gold": round(accumulated, 2),
            "max_accumulation_hours": 8,
            "last_collection": last_collection
        }
    
    def _calculate_base_idle_rate(self) -> float:
        """Calculate base idle income rate based on completed scenarios and levels."""
        if not self.current_player:
            return 0.5
        
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT COUNT(*) as completed FROM completed_scenarios WHERE player_id = %s
        """, (self.current_player.player_id,))
        completed = cur.fetchone()['completed']
        
        cur.execute("""
            SELECT SUM(current_level) as total_levels FROM player_discipline_progress WHERE player_id = %s
        """, (self.current_player.player_id,))
        result = cur.fetchone()
        total_levels = result['total_levels'] if result['total_levels'] else 6
        
        cur.close()
        return_connection(conn)
        
        base_rate = 0.5
        scenario_bonus = completed * 0.1
        level_bonus = total_levels * 0.05
        
        return round(base_rate + scenario_bonus + level_bonus, 2)
    
    def collect_idle_income(self) -> dict:
        """Collect accumulated idle income gold."""
        if not self.current_player:
            return {"error": "No player loaded"}
        
        status = self.get_idle_income_status()
        if status.get("error"):
            return status
        
        collected = status['accumulated_gold']
        if collected < 1:
            return {"error": "Not enough gold to collect (minimum 1 gold)"}
        
        conn = get_connection()
        cur = conn.cursor()
        
        now = datetime.datetime.now()
        new_rate = self._calculate_base_idle_rate()
        
        cur.execute("""
            UPDATE player_idle_income 
            SET last_collection_at = %s, gold_per_minute = %s
            WHERE player_id = %s
        """, (now, new_rate, self.current_player.player_id))
        
        self.current_player.cash += collected
        self.current_player.save_to_db()
        
        conn.commit()
        cur.close()
        return_connection(conn)
        
        return {
            "success": True,
            "collected": round(collected, 2),
            "new_rate": new_rate,
            "new_cash": self.current_player.cash
        }
    
    def get_leaderboard(self, category: str = "stars") -> list:
        """Get leaderboard rankings for various categories."""
        conn = get_connection()
        cur = conn.cursor()
        
        if category == "stars":
            cur.execute("""
                SELECT pp.player_name, pp.chosen_world, COUNT(cs.id) as total_scenarios,
                       COALESCE(SUM(cs.stars_earned), 0) as total_stars
                FROM player_profiles pp
                LEFT JOIN completed_scenarios cs ON pp.player_id = cs.player_id
                GROUP BY pp.player_id, pp.player_name, pp.chosen_world
                ORDER BY total_stars DESC
                LIMIT 10
            """)
        elif category == "wealth":
            cur.execute("""
                SELECT player_name, chosen_world, total_cash as score
                FROM player_profiles
                ORDER BY total_cash DESC
                LIMIT 10
            """)
        elif category == "levels":
            cur.execute("""
                SELECT pp.player_name, pp.chosen_world, 
                       COALESCE(SUM(pdp.current_level), 6) as total_levels
                FROM player_profiles pp
                LEFT JOIN player_discipline_progress pdp ON pp.player_id = pdp.player_id
                GROUP BY pp.player_id, pp.player_name, pp.chosen_world
                ORDER BY total_levels DESC
                LIMIT 10
            """)
        else:
            cur.close()
            return_connection(conn)
            return []
        
        results = cur.fetchall()
        cur.close()
        return_connection(conn)
        
        return [dict(r) for r in results]
    
    def get_equipment_bonuses(self) -> dict:
        """Get stat bonuses from equipped items."""
        if not self.current_player:
            return {"charisma": 0, "intelligence": 0, "luck": 0, "negotiation": 0}
        
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT e.stat_bonus_type, e.stat_bonus_value
            FROM equipment e
            JOIN player_equipment pe ON e.equipment_id = pe.equipment_id
            WHERE pe.player_id = %s AND pe.is_equipped = TRUE
        """, (self.current_player.player_id,))
        equipped = cur.fetchall()
        
        cur.close()
        return_connection(conn)
        
        bonuses = {"charisma": 0, "intelligence": 0, "luck": 0, "negotiation": 0}
        for item in equipped:
            stat_type = item['stat_bonus_type']
            if stat_type in bonuses:
                bonuses[stat_type] += item['stat_bonus_value']
        
        return bonuses
    
    def get_advisor_bonuses(self, discipline: str = None) -> dict:
        """Get active advisor bonuses that apply to scenarios.
        
        Returns bonuses like:
        - exp_boost: percentage to add to EXP (e.g., 10 = +10%)
        - gold_boost: percentage to add to gold rewards
        - reputation_boost: flat bonus to reputation gains
        """
        if not self.current_player:
            return {"exp_boost": 0, "gold_boost": 0, "reputation_boost": 0}
        
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT a.discipline_specialty, a.bonus_type, a.bonus_value, pa.level
            FROM advisors a
            JOIN player_advisors pa ON a.advisor_id = pa.advisor_id
            WHERE pa.player_id = %s AND pa.is_active = TRUE
        """, (self.current_player.player_id,))
        active_advisors = cur.fetchall()
        
        cur.close()
        return_connection(conn)
        
        bonuses = {"exp_boost": 0, "gold_boost": 0, "reputation_boost": 0}
        
        for advisor in active_advisors:
            applies = discipline is None or advisor['discipline_specialty'] == discipline
            if applies:
                bonus_type = advisor['bonus_type']
                bonus_value = advisor['bonus_value'] * advisor['level']
                if bonus_type in bonuses:
                    bonuses[bonus_type] += bonus_value
        
        return bonuses
    
    def get_prestige_status(self) -> dict:
        """Get player's prestige status and available bonuses."""
        if not self.current_player:
            return {"error": "No player loaded"}
        
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT * FROM player_prestige WHERE player_id = %s
        """, (self.current_player.player_id,))
        row = cur.fetchone()
        
        if not row:
            cur.execute("""
                INSERT INTO player_prestige (player_id, prestige_level, exp_multiplier, gold_multiplier, total_prestiges)
                VALUES (%s, 0, 1.0, 1.0, 0)
                RETURNING *
            """, (self.current_player.player_id,))
            row = cur.fetchone()
            conn.commit()
        
        cur.execute("""
            SELECT SUM(current_level) as total FROM player_discipline_progress WHERE player_id = %s
        """, (self.current_player.player_id,))
        total_levels = cur.fetchone()['total'] or 6
        
        can_prestige = total_levels >= 30
        next_exp_bonus = 0.1
        next_gold_bonus = 0.15
        
        cur.close()
        return_connection(conn)
        
        return {
            "prestige_level": row['prestige_level'],
            "exp_multiplier": float(row['exp_multiplier']),
            "gold_multiplier": float(row['gold_multiplier']),
            "total_prestiges": row['total_prestiges'],
            "can_prestige": can_prestige,
            "total_levels": total_levels,
            "levels_needed": 30,
            "next_exp_bonus": next_exp_bonus,
            "next_gold_bonus": next_gold_bonus
        }
    
    def perform_prestige(self) -> dict:
        """Perform prestige reset for permanent bonuses."""
        if not self.current_player:
            return {"error": "No player loaded"}
        
        status = self.get_prestige_status()
        if status.get("error"):
            return status
        
        if not status['can_prestige']:
            return {"error": f"Need {status['levels_needed']} total discipline levels. You have {status['total_levels']}."}
        
        conn = get_connection()
        cur = conn.cursor()
        
        new_prestige = status['prestige_level'] + 1
        new_exp_mult = status['exp_multiplier'] + 0.1
        new_gold_mult = status['gold_multiplier'] + 0.15
        
        cur.execute("""
            UPDATE player_prestige 
            SET prestige_level = %s, exp_multiplier = %s, gold_multiplier = %s, total_prestiges = total_prestiges + 1
            WHERE player_id = %s
        """, (new_prestige, new_exp_mult, new_gold_mult, self.current_player.player_id))
        
        cur.execute("""
            UPDATE player_discipline_progress 
            SET current_level = 1, current_exp = 0, total_exp_earned = 0
            WHERE player_id = %s
        """, (self.current_player.player_id,))
        
        cur.execute("""
            DELETE FROM completed_scenarios WHERE player_id = %s
        """, (self.current_player.player_id,))
        
        self.current_player.cash = 10000.0
        self.current_player.reputation = 50
        self.current_player.save_to_db()
        
        conn.commit()
        cur.close()
        return_connection(conn)
        
        return {
            "success": True,
            "new_prestige_level": new_prestige,
            "new_exp_multiplier": new_exp_mult,
            "new_gold_multiplier": new_gold_mult
        }
    
    def get_daily_missions(self) -> dict:
        """Get player's current daily missions."""
        if not self.current_player:
            return {"error": "No player loaded"}
        
        conn = get_connection()
        cur = conn.cursor()
        
        today = datetime.date.today()
        
        cur.execute("""
            SELECT pdm.*, dm.mission_name, dm.mission_description, dm.target_value, 
                   dm.reward_type, dm.reward_amount, dm.mission_type
            FROM player_daily_missions pdm
            JOIN daily_missions dm ON pdm.mission_id = dm.mission_id
            WHERE pdm.player_id = %s AND pdm.mission_date = %s
        """, (self.current_player.player_id, today))
        missions = cur.fetchall()
        
        if len(missions) < 3:
            cur.execute("""
                DELETE FROM player_daily_missions WHERE player_id = %s AND mission_date = %s
            """, (self.current_player.player_id, today))
            
            cur.execute("SELECT mission_id FROM daily_missions ORDER BY RANDOM() LIMIT 3")
            new_missions = cur.fetchall()
            
            for m in new_missions:
                cur.execute("""
                    INSERT INTO player_daily_missions (player_id, mission_id, mission_date, current_progress, is_completed, is_claimed)
                    VALUES (%s, %s, %s, 0, FALSE, FALSE)
                """, (self.current_player.player_id, m['mission_id'], today))
            
            conn.commit()
            
            cur.execute("""
                SELECT pdm.*, dm.mission_name, dm.mission_description, dm.target_value, 
                       dm.reward_type, dm.reward_amount, dm.mission_type
                FROM player_daily_missions pdm
                JOIN daily_missions dm ON pdm.mission_id = dm.mission_id
                WHERE pdm.player_id = %s AND pdm.mission_date = %s
            """, (self.current_player.player_id, today))
            missions = cur.fetchall()
        
        cur.close()
        return_connection(conn)
        
        return {
            "missions": [dict(m) for m in missions],
            "date": str(today)
        }
    
    def claim_daily_mission(self, mission_id: int) -> dict:
        """Claim a completed daily mission reward."""
        if not self.current_player:
            return {"error": "No player loaded"}
        
        conn = get_connection()
        cur = conn.cursor()
        
        today = datetime.date.today()
        
        cur.execute("""
            SELECT pdm.*, dm.reward_type, dm.reward_amount, dm.mission_name
            FROM player_daily_missions pdm
            JOIN daily_missions dm ON pdm.mission_id = dm.mission_id
            WHERE pdm.player_id = %s AND pdm.mission_id = %s AND pdm.mission_date = %s
        """, (self.current_player.player_id, mission_id, today))
        mission = cur.fetchone()
        
        if not mission:
            cur.close()
            return_connection(conn)
            return {"error": "Mission not found"}
        
        if not mission['is_completed']:
            cur.close()
            return_connection(conn)
            return {"error": "Mission not completed yet"}
        
        if mission['is_claimed']:
            cur.close()
            return_connection(conn)
            return {"error": "Already claimed this reward"}
        
        reward_type = mission['reward_type']
        reward_amount = mission['reward_amount']
        
        if reward_type == 'gold':
            self.current_player.cash += reward_amount
        elif reward_type == 'energy':
            self.recharge_energy(reward_amount)
        
        cur.execute("""
            UPDATE player_daily_missions SET is_claimed = TRUE
            WHERE player_id = %s AND mission_id = %s AND mission_date = %s
        """, (self.current_player.player_id, mission_id, today))
        
        self.current_player.save_to_db()
        conn.commit()
        cur.close()
        return_connection(conn)
        
        return {
            "success": True,
            "mission_name": mission['mission_name'],
            "reward_type": reward_type,
            "reward_amount": reward_amount
        }
    
    def get_rival_battle_status(self) -> dict:
        """Get available rivals for battle."""
        if not self.current_player:
            return {"error": "No player loaded"}
        
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT * FROM rivals 
            WHERE world_type = %s
            ORDER BY difficulty_level
        """, (self.current_player.world,))
        rivals = cur.fetchall()
        
        player_power = self._calculate_player_power()
        
        cur.close()
        return_connection(conn)
        
        return {
            "rivals": [dict(r) for r in rivals],
            "player_power": player_power
        }
    
    def _calculate_player_power(self) -> int:
        """Calculate player's combat power based on stats and equipment."""
        if not self.current_player:
            return 0
        
        base_power = 100
        
        stats = self.current_player.stats
        stat_power = (stats.get('charisma', 5) + stats.get('intelligence', 5) + 
                      stats.get('luck', 5) + stats.get('negotiation', 5)) * 5
        
        equipment_data = self.get_equipment()
        equipment_power = 0
        if not equipment_data.get("error"):
            for item in equipment_data.get('owned', []):
                if item.get('is_equipped'):
                    equipment_power += item.get('stat_bonus_value', 0) * 2
        
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT SUM(current_level) as total FROM player_discipline_progress WHERE player_id = %s
        """, (self.current_player.player_id,))
        result = cur.fetchone()
        level_power = (result['total'] or 6) * 10
        cur.close()
        return_connection(conn)
        
        return base_power + stat_power + equipment_power + level_power
    
    def battle_rival(self, rival_id: int) -> dict:
        """Battle a rival using stat comparison."""
        if not self.current_player:
            return {"error": "No player loaded"}
        
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM rivals WHERE rival_id = %s", (rival_id,))
        rival = cur.fetchone()
        
        if not rival:
            cur.close()
            return_connection(conn)
            return {"error": "Rival not found"}
        
        player_power = self._calculate_player_power()
        rival_power = rival['rival_level'] * 50 + 100
        
        luck_modifier = random.randint(-20, 20)
        final_player = player_power + luck_modifier
        
        victory = final_player > rival_power
        
        rewards = {}
        if victory:
            gold_reward = rival['rival_level'] * 500
            exp_reward = rival['rival_level'] * 100
            self.current_player.cash += gold_reward
            self.current_player.reputation = min(100, self.current_player.reputation + 2)
            rewards = {"gold": gold_reward, "exp": exp_reward, "reputation": 2}
            self.current_player.save_to_db()
        else:
            rep_loss = 1
            self.current_player.reputation = max(0, self.current_player.reputation - rep_loss)
            rewards = {"reputation_lost": rep_loss}
            self.current_player.save_to_db()
        
        conn.commit()
        cur.close()
        return_connection(conn)
        
        return {
            "success": True,
            "victory": victory,
            "player_power": player_power,
            "rival_power": rival_power,
            "luck_modifier": luck_modifier,
            "final_score": final_player,
            "rival_name": rival['rival_name'],
            "rewards": rewards
        }


    def get_campaign_map(self):
        """Get campaign map data showing scenario progression for all disciplines."""
        if not self.current_player:
            return {"error": "No player loaded"}
        
        conn = get_connection()
        cur = conn.cursor()
        
        player_world = self.current_player.world
        player_industry = self.current_player.industry
        
        cur.execute("""
            SELECT scenario_id FROM completed_scenarios 
            WHERE player_id = %s
        """, (self.current_player.player_id,))
        completed_ids = {row['scenario_id'] for row in cur.fetchall()}
        
        cur.execute("""
            SELECT scenario_id, stars_earned FROM completed_scenarios 
            WHERE player_id = %s
        """, (self.current_player.player_id,))
        stars_by_scenario = {row['scenario_id']: row['stars_earned'] for row in cur.fetchall()}
        
        campaign_data = {}
        for discipline in DISCIPLINES:
            cur.execute("""
                SELECT scenario_id, scenario_title, required_level
                FROM scenario_master
                WHERE world_type = %s AND industry = %s AND discipline = %s AND is_active = TRUE
                ORDER BY required_level ASC
                LIMIT 10
            """, (player_world, player_industry, discipline))
            scenarios = cur.fetchall()
            
            nodes = []
            for idx, s in enumerate(scenarios):
                is_completed = s['scenario_id'] in completed_ids
                stars = stars_by_scenario.get(s['scenario_id'], 0)
                
                prev_completed = True
                if idx > 0:
                    prev_scenario = scenarios[idx - 1]
                    prev_completed = prev_scenario['scenario_id'] in completed_ids
                
                is_unlocked = (idx == 0) or prev_completed
                is_current = is_unlocked and not is_completed
                
                nodes.append({
                    'scenario_id': s['scenario_id'],
                    'title': s['scenario_title'],
                    'level': s['required_level'],
                    'completed': is_completed,
                    'stars': stars,
                    'unlocked': is_unlocked,
                    'current': is_current,
                    'node_index': idx + 1
                })
            
            total_stars = sum(n['stars'] for n in nodes)
            max_stars = len(nodes) * 3
            completed_count = sum(1 for n in nodes if n['completed'])
            
            campaign_data[discipline] = {
                'nodes': nodes,
                'total_stars': total_stars,
                'max_stars': max_stars,
                'completed_count': completed_count,
                'total_count': len(nodes)
            }
        
        cur.close()
        return_connection(conn)
        
        return campaign_data
    
    def get_boss_scenarios(self):
        """Get all boss scenarios for the current player."""
        if not self.current_player:
            return {"error": "No player loaded"}
        
        conn = get_connection()
        cur = conn.cursor()
        
        player_world = self.current_player.world
        player_industry = self.current_player.industry
        
        cur.execute("""
            SELECT scenario_id FROM completed_scenarios 
            WHERE player_id = %s
        """, (self.current_player.player_id,))
        completed_ids = {row['scenario_id'] for row in cur.fetchall()}
        
        cur.execute("""
            SELECT scenario_id, stars_earned FROM completed_scenarios 
            WHERE player_id = %s
        """, (self.current_player.player_id,))
        stars_by_scenario = {row['scenario_id']: row['stars_earned'] for row in cur.fetchall()}
        
        cur.execute("""
            SELECT discipline_name, current_level 
            FROM player_discipline_progress
            WHERE player_id = %s
        """, (self.current_player.player_id,))
        player_levels = {row['discipline_name']: row['current_level'] for row in cur.fetchall()}
        
        cur.execute("""
            SELECT * FROM scenario_master
            WHERE world_type = %s AND industry = %s 
            AND required_level IN (5, 10) AND is_active = TRUE
            ORDER BY discipline, required_level
        """, (player_world, player_industry))
        
        boss_scenarios = []
        for s in cur.fetchall():
            disc = s['discipline']
            player_level = player_levels.get(disc, 1)
            is_completed = s['scenario_id'] in completed_ids
            stars = stars_by_scenario.get(s['scenario_id'], 0)
            is_unlocked = player_level >= s['required_level']
            
            boss_type = "Elite" if s['required_level'] == 5 else "Boss"
            
            boss_scenarios.append({
                'scenario_id': s['scenario_id'],
                'title': s['scenario_title'],
                'discipline': disc,
                'level': s['required_level'],
                'boss_type': boss_type,
                'completed': is_completed,
                'stars': stars,
                'unlocked': is_unlocked,
                'narrative': s['scenario_narrative'][:150] + '...' if len(s['scenario_narrative']) > 150 else s['scenario_narrative']
            })
        
        cur.close()
        return_connection(conn)
        
        return boss_scenarios
