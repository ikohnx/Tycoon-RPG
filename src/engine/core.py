"""
GameEngine core class - inherits from all mixins.
"""

import datetime
from src.database import get_connection, return_connection
from src.leveling import (
    calculate_weighted_exp,
    check_level_up,
    get_current_level,
    get_exp_to_next_level,
    get_level_title,
    get_progress_bar,
    DISCIPLINES
)
from src.engine.player import Player, JOB_TITLES
from src.engine.scenarios import ScenariosMixin
from src.engine.progression import ProgressionMixin
from src.engine.social import SocialMixin


class GameEngine(ScenariosMixin, ProgressionMixin, SocialMixin):
    """Main game engine handling all game logic."""

    def __init__(self):
        self.current_player = None
        self.available_scenarios = []

    def create_new_player(self, name: str, world: str = "Modern", industry: str = "Restaurant", career_path: str = "entrepreneur", password: str = None) -> Player:
        """Create a new player and initialize their progress."""
        import bcrypt
        conn = get_connection()
        cur = conn.cursor()

        password_hash = None
        if password:
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

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
            INSERT INTO player_profiles (player_name, password_hash, chosen_world, chosen_industry, career_path, job_title, job_level, total_cash, business_reputation)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING player_id
        """, (name, password_hash, world, industry, career_path, job_title, job_level, starting_cash, starting_reputation))

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
        return_connection(conn)

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
        """Get list of all saved players (names only for login, no sensitive data)."""
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT player_id, player_name, chosen_world, chosen_industry, total_cash, password_hash IS NOT NULL as has_password FROM player_profiles ORDER BY last_played DESC")
        players = cur.fetchall()

        cur.close()
        return_connection(conn)
        return players

    def authenticate_player(self, player_id: int, password: str = None) -> dict:
        """Authenticate a player by ID and password using bcrypt."""
        import bcrypt
        import hashlib
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT player_id, player_name, password_hash FROM player_profiles WHERE player_id = %s", (player_id,))
        player = cur.fetchone()

        cur.close()
        return_connection(conn)

        if not player:
            return {"success": False, "error": "Player not found"}

        if player['password_hash']:
            if not password:
                return {"success": False, "error": "Password required", "needs_password": True}

            stored_hash = player['password_hash']

            if stored_hash.startswith('$2'):
                if not bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                    return {"success": False, "error": "Incorrect password"}
            else:
                legacy_hash = hashlib.sha256(password.encode()).hexdigest()
                if legacy_hash != stored_hash:
                    return {"success": False, "error": "Incorrect password"}

                new_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                upgrade_conn = get_connection()
                try:
                    upgrade_cur = upgrade_conn.cursor()
                    upgrade_cur.execute("UPDATE player_profiles SET password_hash = %s WHERE player_id = %s",
                                       (new_hash, player_id))
                    upgrade_conn.commit()
                    upgrade_cur.close()
                finally:
                    return_connection(upgrade_conn)

        return {"success": True, "player_id": player['player_id'], "player_name": player['player_name']}

    def player_name_exists(self, name: str) -> bool:
        """Check if a player name already exists."""
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) as count FROM player_profiles WHERE LOWER(player_name) = LOWER(%s)", (name,))
        result = cur.fetchone()

        cur.close()
        return_connection(conn)
        return result['count'] > 0

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

    def get_hub_data(self) -> dict:
        """Get all hub data in a single efficient batch. Reduces database queries from 6+ to 1."""
        if not self.current_player:
            return {"error": "No player loaded"}

        conn = get_connection()
        cur = conn.cursor()
        player_id = self.current_player.player_id

        cur.execute("""
            SELECT * FROM player_energy WHERE player_id = %s
        """, (player_id,))
        energy_row = cur.fetchone()

        if not energy_row:
            cur.execute("""
                INSERT INTO player_energy (player_id, current_energy, max_energy, last_recharge_at)
                VALUES (%s, 100, 100, CURRENT_TIMESTAMP)
                RETURNING *
            """, (player_id,))
            energy_row = cur.fetchone()
            conn.commit()

        now = datetime.datetime.now(datetime.timezone.utc)
        last_recharge = energy_row['last_recharge_at']
        if last_recharge.tzinfo is None:
            last_recharge = last_recharge.replace(tzinfo=datetime.timezone.utc)

        minutes_elapsed = (now - last_recharge).total_seconds() / 60
        energy_to_add = int(minutes_elapsed / 5)
        current_energy = energy_row['current_energy']
        max_energy = energy_row['max_energy']

        if energy_to_add > 0 and current_energy < max_energy:
            current_energy = min(max_energy, current_energy + energy_to_add)
            cur.execute("""
                UPDATE player_energy 
                SET current_energy = %s, last_recharge_at = CURRENT_TIMESTAMP
                WHERE player_id = %s
            """, (current_energy, player_id))
            conn.commit()

        next_recharge_seconds = (5 - (minutes_elapsed % 5)) * 60 if current_energy < max_energy else 0
        energy = {
            "current_energy": current_energy,
            "max_energy": max_energy,
            "next_recharge_in": int(next_recharge_seconds)
        }

        cur.execute("""
            SELECT * FROM player_daily_login WHERE player_id = %s
        """, (player_id,))
        login_row = cur.fetchone()
        today = datetime.date.today()

        if not login_row:
            cur.execute("""
                INSERT INTO player_daily_login (player_id, current_streak, longest_streak, last_login_date, last_claim_date)
                VALUES (%s, 0, 0, NULL, NULL)
                RETURNING *
            """, (player_id,))
            login_row = cur.fetchone()
            conn.commit()

        current_streak = login_row['current_streak']
        longest_streak = login_row['longest_streak']
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

        login_status = {
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "can_claim": can_claim,
            "streak_broken": streak_broken,
            "reward_day": reward_day,
            "reward": dict(reward) if reward else None
        }

        cur.execute("""
            SELECT * FROM player_idle_income WHERE player_id = %s
        """, (player_id,))
        idle_row = cur.fetchone()
        now_dt = datetime.datetime.now()

        if not idle_row:
            cur.execute("""
                INSERT INTO player_idle_income (player_id, gold_per_hour, last_collect_at)
                VALUES (%s, 10, CURRENT_TIMESTAMP)
                RETURNING *
            """, (player_id,))
            idle_row = cur.fetchone()
            conn.commit()

        gold_per_hour = idle_row.get('gold_per_hour', 10) or 10
        last_collect = idle_row['last_collect_at']
        hours_elapsed = (now_dt - last_collect).total_seconds() / 3600
        max_hours = 24
        hours_counted = min(hours_elapsed, max_hours)
        accumulated_gold = int(hours_counted * gold_per_hour)

        idle_income = {
            "gold_per_hour": gold_per_hour,
            "accumulated_gold": accumulated_gold,
            "hours_elapsed": round(hours_counted, 1),
            "max_hours": max_hours,
            "can_collect": accumulated_gold > 0
        }

        cur.execute("""
            SELECT * FROM player_prestige WHERE player_id = %s
        """, (player_id,))
        prestige_row = cur.fetchone()

        if not prestige_row:
            cur.execute("""
                INSERT INTO player_prestige (player_id, prestige_level, exp_multiplier, gold_multiplier)
                VALUES (%s, 0, 1.0, 1.0)
                RETURNING *
            """, (player_id,))
            prestige_row = cur.fetchone()
            conn.commit()

        avg_level = sum(d['level'] for d in self.current_player.discipline_progress.values()) / 6 if self.current_player.discipline_progress else 1
        can_prestige = avg_level >= 5 and prestige_row['prestige_level'] < 10

        prestige_status = {
            "prestige_level": prestige_row['prestige_level'],
            "exp_multiplier": float(prestige_row['exp_multiplier']),
            "gold_multiplier": float(prestige_row['gold_multiplier']),
            "can_prestige": can_prestige,
            "avg_level": round(avg_level, 1)
        }

        cur.execute("""
            SELECT pp.player_name, COALESCE(SUM(psc.stars_earned), 0) as total_stars
            FROM player_profiles pp
            LEFT JOIN player_scenario_completions psc ON pp.player_id = psc.player_id
            GROUP BY pp.player_id, pp.player_name
            ORDER BY total_stars DESC
            LIMIT 5
        """)
        leaderboard = [{"name": r['player_name'], "stars": int(r['total_stars'])} for r in cur.fetchall()]

        cur.close()
        return_connection(conn)

        return {
            "energy": energy,
            "login_status": login_status,
            "idle_income": idle_income,
            "prestige_status": prestige_status,
            "leaderboard": leaderboard
        }

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
