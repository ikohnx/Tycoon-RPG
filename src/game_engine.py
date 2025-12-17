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
    },
    'Steel Mill': {
        1: 'Furnace Stoker',
        2: 'Foundry Worker',
        3: 'Shift Supervisor',
        4: 'Foreman',
        5: 'Production Manager',
        6: 'Plant Superintendent',
        7: 'Operations Director',
        8: 'Vice President',
        9: 'Senior Vice President',
        10: 'Mill Baron'
    },
    'Textile Factory': {
        1: 'Loom Operator',
        2: 'Pattern Cutter',
        3: 'Floor Supervisor',
        4: 'Quality Inspector',
        5: 'Production Chief',
        6: 'Factory Manager',
        7: 'Regional Director',
        8: 'Vice President',
        9: 'Chief Operating Officer',
        10: 'Textile Magnate'
    },
    'Railroad': {
        1: 'Track Layer',
        2: 'Station Porter',
        3: 'Conductor',
        4: 'Station Master',
        5: 'District Manager',
        6: 'Division Superintendent',
        7: 'Regional Director',
        8: 'Vice President',
        9: 'Executive VP',
        10: 'Railroad Tycoon'
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
    
    def create_new_player(self, name: str, world: str = "Modern", industry: str = "Restaurant", career_path: str = "entrepreneur", password: str = None) -> Player:
        """Create a new player and initialize their progress."""
        import hashlib
        conn = get_connection()
        cur = conn.cursor()
        
        password_hash = None
        if password:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
        
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
        """Get list of all saved players (names only for login, no sensitive data)."""
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT player_id, player_name, chosen_world, chosen_industry, total_cash, password_hash IS NOT NULL as has_password FROM player_profiles ORDER BY last_played DESC")
        players = cur.fetchall()
        
        cur.close()
        conn.close()
        return players
    
    def authenticate_player(self, player_id: int, password: str = None) -> dict:
        """Authenticate a player by ID and password."""
        import hashlib
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT player_id, player_name, password_hash FROM player_profiles WHERE player_id = %s", (player_id,))
        player = cur.fetchone()
        
        cur.close()
        conn.close()
        
        if not player:
            return {"success": False, "error": "Player not found"}
        
        if player['password_hash']:
            if not password:
                return {"success": False, "error": "Password required", "needs_password": True}
            
            input_hash = hashlib.sha256(password.encode()).hexdigest()
            if input_hash != player['password_hash']:
                return {"success": False, "error": "Incorrect password"}
        
        return {"success": True, "player_id": player['player_id'], "player_name": player['player_name']}
    
    def player_name_exists(self, name: str) -> bool:
        """Check if a player name already exists."""
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(*) as count FROM player_profiles WHERE LOWER(player_name) = LOWER(%s)", (name,))
        result = cur.fetchone()
        
        cur.close()
        conn.close()
        return result['count'] > 0
    
    def get_scenario_by_id(self, scenario_id: int) -> dict:
        """Get a specific scenario by ID."""
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM scenario_master WHERE scenario_id = %s", (scenario_id,))
        scenario = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return dict(scenario) if scenario else None
    
    def get_training_content(self, scenario_id: int) -> dict:
        """Get training/tutorial content for a scenario."""
        import json
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT training_content, discipline, challenge_type FROM scenario_master WHERE scenario_id = %s", (scenario_id,))
        result = cur.fetchone()
        
        cur.close()
        conn.close()
        
        if result and result.get('training_content'):
            try:
                return json.loads(result['training_content'])
            except json.JSONDecodeError:
                pass
        
        discipline = result['discipline'] if result else 'Marketing'
        challenge_type = result.get('challenge_type', 'choice') if result else 'choice'
        
        default_training = {
            'budget_calculator': {
                'concept': '<p><strong>Profit</strong> is what remains after subtracting all expenses from revenue. It tells you if your business is making or losing money.</p>',
                'formula': 'Profit = Revenue - (Wages + Rent + Supplies + Marketing)',
                'example': '<p>If Revenue = $50,000 and total expenses = $40,000<br>Then Profit = $50,000 - $40,000 = <strong>$10,000</strong></p>',
                'tips': ['Add up all expenses first', 'Subtract total expenses from revenue', 'A negative number means a loss']
            },
            'pricing_strategy': {
                'concept': '<p><strong>Profit Margin</strong> is the percentage of the selling price that is profit. Setting prices correctly ensures you cover costs and make money.</p>',
                'formula': 'Selling Price = Cost ÷ (1 - Margin%)',
                'example': '<p>If item costs $10 and you want 40% margin:<br>$10 ÷ (1 - 0.40) = $10 ÷ 0.60 = <strong>$16.67</strong></p>',
                'tips': ['Convert margin percentage to decimal (40% = 0.40)', 'Subtract from 1, then divide', 'Check: at $16.67, profit is $6.67 which is 40%']
            },
            'staffing_decision': {
                'concept': '<p><strong>Staffing calculations</strong> help you hire the right number of employees. Too few = poor service. Too many = wasted money.</p>',
                'formula': 'Staff Needed = Customers ÷ Customers per Staff',
                'example': '<p>If you expect 200 customers and each staff can serve 25:<br>200 ÷ 25 = <strong>8 staff members</strong></p>',
                'tips': ['Always round UP to ensure coverage', 'Consider peak hours may need more staff', 'Factor in breaks and absences']
            },
            'break_even': {
                'concept': '<p><strong>Break-even point</strong> is the number of units you must sell to cover all costs. Below this = loss, above = profit.</p>',
                'formula': 'Break-Even Units = Fixed Costs ÷ (Price - Variable Cost)',
                'example': '<p>Fixed costs $10,000, sell at $50, costs $30 to make:<br>$10,000 ÷ ($50 - $30) = $10,000 ÷ $20 = <strong>500 units</strong></p>',
                'tips': ['Fixed costs stay the same regardless of sales', 'Price minus cost = contribution margin', 'Sell more than break-even to profit']
            },
            'roi_calculator': {
                'concept': '<p><strong>Return on Investment (ROI)</strong> measures the profitability of an investment as a percentage. Positive ROI = making money, negative ROI = losing money.</p>',
                'formula': 'ROI = ((Total Gain - Investment) ÷ Investment) × 100',
                'example': '<p>Investment of $10,000, total returns of $12,000:<br>(($12,000 - $10,000) ÷ $10,000) × 100 = <strong>20% ROI</strong></p>',
                'tips': ['Calculate total gains over the period first', 'Subtract original investment to get net gain', 'Negative ROI means you lost money on the investment']
            },
            'inventory_turnover': {
                'concept': '<p><strong>Inventory Turnover</strong> shows how many times you sell and replace inventory in a year. Higher = more efficient, lower = slow-moving stock.</p>',
                'formula': 'Inventory Turnover = Cost of Goods Sold ÷ Average Inventory',
                'example': '<p>COGS of $100,000 and average inventory of $20,000:<br>$100,000 ÷ $20,000 = <strong>5 times per year</strong></p>',
                'tips': ['Use COGS, not revenue', 'Higher turnover means less cash tied up in stock', 'Industry standards vary - restaurants should be high']
            },
            'ltv_calculator': {
                'concept': '<p><strong>Customer Lifetime Value (CLV/LTV)</strong> predicts the total profit from a customer relationship. Essential for knowing how much to spend on customer acquisition.</p>',
                'formula': 'LTV = (Avg Purchase × Frequency × 12 × Years) × Profit Margin',
                'example': '<p>$50 avg, 2 times/month, 3 years, 25% margin:<br>($50 × 2 × 12 × 3) × 0.25 = $3,600 × 0.25 = <strong>$900 LTV</strong></p>',
                'tips': ['Multiply by profit margin, not revenue', 'LTV should exceed customer acquisition cost', 'Loyal customers are worth investing in']
            },
            'payback_period': {
                'concept': '<p><strong>Payback Period</strong> is how long it takes to recover your initial investment. Shorter = less risky, faster return on capital.</p>',
                'formula': 'Payback Period = Initial Investment ÷ Annual Profit',
                'example': '<p>$50,000 investment generating $10,000 annual profit:<br>$50,000 ÷ $10,000 = <strong>5 years to pay back</strong></p>',
                'tips': ['Lower payback period = better investment', 'Compare multiple options by payback period', 'Consider risk - shorter payback = lower risk']
            },
            'compound_growth': {
                'concept': '<p><strong>Compound Growth</strong> shows how values grow exponentially over time. Money earns returns on returns, accelerating growth.</p>',
                'formula': 'Future Value = Present Value × (1 + Rate)^Years',
                'example': '<p>$100,000 growing at 10% for 3 years:<br>$100,000 × (1.10)³ = $100,000 × 1.331 = <strong>$133,100</strong></p>',
                'tips': ['Convert percentage to decimal (10% = 0.10)', 'Add 1 to the rate before raising to power', 'Compound growth accelerates over time']
            },
            'choice': {
                'concept': f'<p>This quest will test your <strong>{discipline}</strong> skills. Read the scenario carefully and choose the best option based on business principles.</p>',
                'formula': None,
                'example': None,
                'tips': ['Read all options before choosing', 'Consider short and long-term effects', 'Think about customer and employee impact']
            }
        }
        
        return default_training.get(challenge_type, default_training['choice'])
    
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
    
    def get_all_scenarios_with_status(self, discipline: str = None) -> list:
        """Get all scenarios for a discipline with completion status and stars."""
        if not self.current_player:
            return []
        
        conn = get_connection()
        cur = conn.cursor()
        
        query = """
            SELECT s.*, 
                   cs.scenario_id IS NOT NULL as is_completed,
                   COALESCE(cs.stars_earned, 0) as stars_earned
            FROM scenario_master s
            LEFT JOIN completed_scenarios cs ON s.scenario_id = cs.scenario_id AND cs.player_id = %s
            WHERE s.world_type = %s 
            AND s.industry = %s 
            AND s.is_active = TRUE
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
        scenarios = [dict(row) for row in cur.fetchall()]
        
        cur.close()
        conn.close()
        
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
        
        advisor_bonuses = self.get_advisor_bonuses(discipline)
        exp_bonus_pct = advisor_bonuses.get('exp_boost', 0) / 100
        gold_bonus_pct = advisor_bonuses.get('gold_boost', 0) / 100
        rep_bonus = advisor_bonuses.get('reputation_boost', 0)
        
        weighted_exp = calculate_weighted_exp(
            base_exp, 
            self.current_player.industry, 
            discipline
        )
        weighted_exp = int(weighted_exp * (1 + exp_bonus_pct))
        
        progress = self.current_player.discipline_progress[discipline]
        old_exp = progress['total_exp']
        new_exp = old_exp + weighted_exp
        
        leveled_up, old_level, new_level = check_level_up(old_exp, new_exp)
        
        progress['total_exp'] = new_exp
        progress['exp'] = new_exp
        progress['level'] = new_level
        
        boosted_cash = cash_change * (1 + gold_bonus_pct)
        boosted_rep = reputation_change + rep_bonus
        
        self.current_player.cash += boosted_cash
        self.current_player.reputation = max(0, min(100, self.current_player.reputation + boosted_rep))
        
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
        
        stars = self._calculate_stars(scenario, choice)
        
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO completed_scenarios (player_id, scenario_id, choice_made, stars_earned)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (player_id, scenario_id) DO NOTHING
        """, (self.current_player.player_id, scenario['scenario_id'], choice, stars))
        conn.commit()
        cur.close()
        conn.close()
        
        self.current_player.save_to_db()
        
        if boosted_cash != 0:
            if boosted_cash > 0:
                create_pending_transaction(
                    self.current_player.player_id,
                    'scenario_income',
                    f"Revenue from {scenario['scenario_title']}",
                    abs(boosted_cash),
                    '1000',
                    '4000',
                    'scenario',
                    scenario['scenario_id']
                )
            else:
                create_pending_transaction(
                    self.current_player.player_id,
                    'scenario_expense',
                    f"Expense from {scenario['scenario_title']}",
                    abs(boosted_cash),
                    '5950',
                    '1000',
                    'scenario',
                    scenario['scenario_id']
                )
        
        return {
            "success": True,
            "exp_gained": weighted_exp,
            "base_exp": base_exp,
            "cash_change": boosted_cash,
            "reputation_change": boosted_rep,
            "feedback": feedback,
            "leveled_up": leveled_up,
            "old_level": old_level,
            "new_level": new_level,
            "discipline": discipline,
            "new_total_exp": new_exp,
            "promotion": promotion,
            "stars_earned": stars,
            "advisor_bonuses": advisor_bonuses
        }
    
    def _calculate_stars(self, scenario: dict, choice: str) -> int:
        """Calculate stars earned based on choice quality (1-3 stars).
        Equipment luck bonus can upgrade stars."""
        exp_rewards = [
            scenario.get('choice_a_exp_reward', 0),
            scenario.get('choice_b_exp_reward', 0),
            scenario.get('choice_c_exp_reward', 0) if scenario.get('choice_c_text') else 0
        ]
        exp_rewards = [e for e in exp_rewards if e > 0]
        if not exp_rewards:
            return 1
        
        choice_prefix = f"choice_{choice.lower()}"
        chosen_exp = scenario.get(f'{choice_prefix}_exp_reward', 0)
        max_exp = max(exp_rewards)
        
        if chosen_exp >= max_exp:
            stars = 3
        elif chosen_exp >= max_exp * 0.7:
            stars = 2
        else:
            stars = 1
        
        equipment_bonuses = self.get_equipment_bonuses()
        luck_bonus = equipment_bonuses.get('luck', 0)
        import random
        if luck_bonus > 0 and stars < 3:
            luck_chance = luck_bonus * 0.02
            if random.random() < luck_chance:
                stars += 1
        
        return stars
    
    def get_challenge_by_id(self, scenario_id: int) -> dict:
        """Get a challenge scenario with parsed config."""
        import json
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM scenario_master WHERE scenario_id = %s", (scenario_id,))
        scenario = cur.fetchone()
        
        cur.close()
        conn.close()
        
        if not scenario:
            return None
        
        challenge_config = {}
        if scenario.get('challenge_config'):
            try:
                challenge_config = json.loads(scenario['challenge_config'])
            except json.JSONDecodeError:
                challenge_config = {}
        
        return {
            'scenario_id': scenario['scenario_id'],
            'title': scenario['scenario_title'],
            'narrative': scenario['scenario_narrative'],
            'discipline': scenario['discipline'],
            'level': scenario['required_level'],
            'type': scenario.get('challenge_type', 'choice'),
            'data': challenge_config,
            'base_exp': scenario['choice_a_exp_reward'],
            'cash_reward': float(scenario['choice_a_cash_change'] or 0),
            'reputation_reward': scenario['choice_a_reputation_change'] or 0
        }
    
    def evaluate_challenge(self, scenario_id: int, challenge_type: str, answer: float) -> dict:
        """
        Evaluate a player's answer to an interactive challenge.
        Returns result dict with EXP, stars, and feedback.
        """
        import json
        if not self.current_player:
            return {"error": "No player loaded"}
        
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM scenario_master WHERE scenario_id = %s", (scenario_id,))
        scenario = cur.fetchone()
        
        if not scenario:
            cur.close()
            conn.close()
            return {"error": "Scenario not found"}
        
        challenge_config = {}
        if scenario.get('challenge_config'):
            try:
                challenge_config = json.loads(scenario['challenge_config'])
            except json.JSONDecodeError:
                pass
        
        correct_answer = 0
        tolerance = 0.01
        
        if challenge_type == 'budget_calculator':
            revenue = challenge_config.get('revenue', 0)
            wages = challenge_config.get('wages', 0)
            rent = challenge_config.get('rent', 0)
            supplies = challenge_config.get('supplies', 0)
            marketing = challenge_config.get('marketing', 0)
            correct_answer = revenue - wages - rent - supplies - marketing
            tolerance = 1
            
        elif challenge_type == 'pricing_strategy':
            unit_cost = challenge_config.get('unit_cost', 0)
            target_margin = challenge_config.get('target_margin', 0) / 100
            correct_answer = round(unit_cost / (1 - target_margin), 2)
            tolerance = 0.50
            
        elif challenge_type == 'staffing_decision':
            daily_customers = challenge_config.get('daily_customers', 0)
            customers_per_staff = challenge_config.get('customers_per_staff', 1)
            import math
            correct_answer = math.ceil(daily_customers / customers_per_staff)
            tolerance = 0
            
        elif challenge_type == 'break_even':
            fixed_costs = challenge_config.get('fixed_costs', 0)
            unit_price = challenge_config.get('unit_price', 0)
            unit_cost = challenge_config.get('unit_cost', 0)
            if unit_price > unit_cost:
                correct_answer = fixed_costs / (unit_price - unit_cost)
            tolerance = 1
        
        elif challenge_type == 'roi_calculator':
            investment = challenge_config.get('investment', 0)
            monthly_gain = challenge_config.get('monthly_gain', 0)
            period_months = challenge_config.get('period_months', 12)
            total_gain = monthly_gain * period_months
            net_gain = total_gain - investment
            correct_answer = (net_gain / investment) * 100 if investment > 0 else 0
            tolerance = 2
        
        elif challenge_type == 'inventory_turnover':
            cogs = challenge_config.get('cost_of_goods_sold', 0)
            avg_inventory = challenge_config.get('average_inventory', 1)
            correct_answer = cogs / avg_inventory if avg_inventory > 0 else 0
            tolerance = 0.5
        
        elif challenge_type == 'ltv_calculator':
            avg_purchase = challenge_config.get('avg_purchase', 0)
            frequency = challenge_config.get('frequency_monthly', 1)
            years = challenge_config.get('retention_years', 1)
            margin = challenge_config.get('profit_margin', 100) / 100
            total_revenue = avg_purchase * frequency * 12 * years
            correct_answer = total_revenue * margin
            tolerance = 50
        
        elif challenge_type == 'payback_period':
            cost_a = challenge_config.get('option_a_cost', 0)
            profit_a = challenge_config.get('option_a_annual_profit', 1)
            cost_b = challenge_config.get('option_b_cost', 0)
            profit_b = challenge_config.get('option_b_annual_profit', 1)
            payback_a = cost_a / profit_a if profit_a > 0 else 999
            payback_b = cost_b / profit_b if profit_b > 0 else 999
            correct_answer = payback_a if payback_a <= payback_b else payback_b
            tolerance = 0.1
        
        elif challenge_type == 'compound_growth':
            initial = challenge_config.get('initial_value', 0)
            rate = challenge_config.get('growth_rate', 0) / 100
            years = challenge_config.get('years', 1)
            correct_answer = initial * ((1 + rate) ** years)
            tolerance = 500
        
        if challenge_type == 'pricing_strategy':
            answer = round(answer, 2)
        
        error = abs(answer - correct_answer)
        if tolerance == 0:
            accuracy = 1.0 if int(answer) == int(correct_answer) else 0.0
        elif correct_answer == 0:
            accuracy = 1.0 if error < tolerance else 0.0
        else:
            accuracy = max(0, 1 - (error / max(abs(correct_answer) * 0.15, 1)))
        
        if accuracy >= 0.95:
            stars = 3
            feedback = "Perfect! Your calculation was spot-on."
        elif accuracy >= 0.7:
            stars = 2
            feedback = f"Good job! The correct answer was ${correct_answer:,.2f}. You were close."
        elif accuracy >= 0.4:
            stars = 1
            feedback = f"Almost there. The correct answer was ${correct_answer:,.2f}. Keep practicing!"
        else:
            stars = 1
            feedback = f"Not quite right. The correct answer was ${correct_answer:,.2f}. Review the formulas."
        
        base_exp = scenario['choice_a_exp_reward']
        exp_multiplier = {3: 1.0, 2: 0.7, 1: 0.4}
        adjusted_exp = int(base_exp * exp_multiplier[stars])
        
        discipline = scenario['discipline']
        
        advisor_bonuses = self.get_advisor_bonuses(discipline)
        exp_bonus_pct = advisor_bonuses.get('exp_boost', 0) / 100
        gold_bonus_pct = advisor_bonuses.get('gold_boost', 0) / 100
        rep_bonus = advisor_bonuses.get('reputation_boost', 0)
        
        weighted_exp = calculate_weighted_exp(
            adjusted_exp,
            self.current_player.industry,
            discipline
        )
        weighted_exp = int(weighted_exp * (1 + exp_bonus_pct))
        
        progress = self.current_player.discipline_progress[discipline]
        old_exp = progress['total_exp']
        new_exp = old_exp + weighted_exp
        
        leveled_up, old_level, new_level = check_level_up(old_exp, new_exp)
        
        progress['total_exp'] = new_exp
        progress['exp'] = new_exp
        progress['level'] = new_level
        
        cash_change = float(scenario['choice_a_cash_change'] or 0) * exp_multiplier[stars] * (1 + gold_bonus_pct)
        reputation_change = int((scenario['choice_a_reputation_change'] or 0) * exp_multiplier[stars]) + rep_bonus
        
        self.current_player.cash += cash_change
        self.current_player.reputation = max(0, min(100, self.current_player.reputation + reputation_change))
        
        cur.execute("""
            INSERT INTO completed_scenarios (player_id, scenario_id, choice_made, stars_earned)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (player_id, scenario_id) DO NOTHING
        """, (self.current_player.player_id, scenario_id, 'X', stars))
        
        cur.execute("""
            UPDATE player_discipline_progress
            SET current_level = %s, current_exp = %s, total_exp_earned = %s
            WHERE player_id = %s AND discipline_name = %s
        """, (new_level, new_exp, new_exp, self.current_player.player_id, discipline))
        
        cur.execute("""
            UPDATE player_profiles
            SET total_cash = %s, business_reputation = %s, last_played = CURRENT_TIMESTAMP
            WHERE player_id = %s
        """, (self.current_player.cash, self.current_player.reputation, self.current_player.player_id))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return {
            "success": True,
            "feedback": feedback,
            "correct_answer": correct_answer,
            "player_answer": answer,
            "accuracy_pct": int(accuracy * 100),
            "exp_gained": weighted_exp,
            "base_exp": adjusted_exp,
            "cash_change": cash_change,
            "reputation_change": reputation_change,
            "leveled_up": leveled_up,
            "old_level": old_level,
            "new_level": new_level,
            "discipline": discipline,
            "new_total_exp": new_exp,
            "stars_earned": stars
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
    
    def get_player_energy(self) -> dict:
        """Get current player energy with auto-recharge calculation."""
        if not self.current_player:
            return {"error": "No player loaded"}
        
        import datetime
        
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
        conn.close()
        
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
        conn.close()
        
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
        conn.close()
        
        if result:
            return {"success": True, "new_energy": result['current_energy'], "max_energy": result['max_energy']}
        return {"error": "Failed to recharge energy"}
    
    def get_daily_login_status(self) -> dict:
        """Get daily login status and available rewards."""
        if not self.current_player:
            return {"error": "No player loaded"}
        
        import datetime
        
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
        conn.close()
        
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
        
        import datetime
        
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
        conn.close()
        
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
        
        import datetime
        
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
        conn.close()
        
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
        conn.close()
        
        base_rate = 0.5
        scenario_bonus = completed * 0.1
        level_bonus = total_levels * 0.05
        
        return round(base_rate + scenario_bonus + level_bonus, 2)
    
    def collect_idle_income(self) -> dict:
        """Collect accumulated idle income gold."""
        if not self.current_player:
            return {"error": "No player loaded"}
        
        import datetime
        
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
        conn.close()
        
        return {
            "success": True,
            "collected": round(collected, 2),
            "new_rate": new_rate,
            "new_cash": self.current_player.cash
        }
    
    def get_leaderboard(self, limit: int = 10) -> dict:
        """Get top players for leaderboard display."""
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT p.player_id, p.player_name, p.total_cash, p.business_reputation, p.chosen_world,
                   COALESCE(SUM(dp.current_level), 0) as total_levels,
                   COALESCE(SUM(cs.stars), 0) as total_stars
            FROM player_profiles p
            LEFT JOIN player_discipline_progress dp ON p.player_id = dp.player_id
            LEFT JOIN (SELECT player_id, SUM(stars_earned) as stars FROM completed_scenarios GROUP BY player_id) cs ON p.player_id = cs.player_id
            GROUP BY p.player_id, p.player_name, p.total_cash, p.business_reputation, p.chosen_world
            ORDER BY total_stars DESC, total_levels DESC, total_cash DESC
            LIMIT %s
        """, (limit,))
        by_stars = [dict(row) for row in cur.fetchall()]
        
        cur.execute("""
            SELECT p.player_id, p.player_name, p.total_cash, p.chosen_world
            FROM player_profiles p
            ORDER BY p.total_cash DESC
            LIMIT %s
        """, (limit,))
        by_wealth = [dict(row) for row in cur.fetchall()]
        
        cur.close()
        conn.close()
        
        return {
            "by_stars": by_stars,
            "by_wealth": by_wealth
        }
    
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
        conn.close()
        
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
        conn.close()
        
        bonuses = {"exp_boost": 0, "gold_boost": 0, "reputation_boost": 0}
        
        for advisor in active_advisors:
            applies = discipline is None or advisor['discipline_specialty'] == discipline
            if applies:
                bonus_type = advisor['bonus_type']
                bonus_value = advisor['bonus_value'] * advisor['level']
                if bonus_type in bonuses:
                    bonuses[bonus_type] += bonus_value
        
        return bonuses
    
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
        conn.close()
        
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
            conn.close()
            return {"error": "Advisor not found"}
        
        cur.execute("""
            SELECT * FROM player_advisors WHERE player_id = %s AND advisor_id = %s
        """, (self.current_player.player_id, advisor_id))
        if cur.fetchone():
            cur.close()
            conn.close()
            return {"error": "Already recruited this advisor"}
        
        cost = float(advisor['unlock_cost'])
        if self.current_player.cash < cost:
            cur.close()
            conn.close()
            return {"error": f"Not enough gold! Need ${cost:,.0f}"}
        
        self.current_player.cash -= cost
        self.current_player.save_to_db()
        
        cur.execute("""
            INSERT INTO player_advisors (player_id, advisor_id, level, is_active)
            VALUES (%s, %s, 1, TRUE)
        """, (self.current_player.player_id, advisor_id))
        
        conn.commit()
        cur.close()
        conn.close()
        
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
        conn.close()
        
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
            conn.close()
            return {"error": "Equipment not found"}
        
        cur.execute("""
            SELECT * FROM player_equipment WHERE player_id = %s AND equipment_id = %s
        """, (self.current_player.player_id, equipment_id))
        if cur.fetchone():
            cur.close()
            conn.close()
            return {"error": "Already own this equipment"}
        
        cost = float(equip['purchase_price'])
        if self.current_player.cash < cost:
            cur.close()
            conn.close()
            return {"error": f"Not enough gold! Need ${cost:,.0f}"}
        
        self.current_player.cash -= cost
        self.current_player.save_to_db()
        
        cur.execute("""
            INSERT INTO player_equipment (player_id, equipment_id, slot_type, is_equipped)
            VALUES (%s, %s, %s, FALSE)
        """, (self.current_player.player_id, equipment_id, equip['slot_type']))
        
        conn.commit()
        cur.close()
        conn.close()
        
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
            conn.close()
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
        conn.close()
        
        return {
            "success": True,
            "equipped": equip['equipment_name'],
            "slot": slot
        }
    
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
        conn.close()
        
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
        conn.close()
        
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
        
        import datetime
        
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
        conn.close()
        
        return {
            "missions": [dict(m) for m in missions],
            "date": str(today)
        }
    
    def claim_daily_mission(self, mission_id: int) -> dict:
        """Claim a completed daily mission reward."""
        if not self.current_player:
            return {"error": "No player loaded"}
        
        import datetime
        
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
            conn.close()
            return {"error": "Mission not found"}
        
        if not mission['is_completed']:
            cur.close()
            conn.close()
            return {"error": "Mission not completed yet"}
        
        if mission['is_claimed']:
            cur.close()
            conn.close()
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
        conn.close()
        
        return {
            "success": True,
            "mission_name": mission['mission_name'],
            "reward_type": reward_type,
            "reward_amount": reward_amount
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
            conn.close()
            return []
        
        results = cur.fetchall()
        cur.close()
        conn.close()
        
        return [dict(r) for r in results]
    
    def get_rival_battle_status(self) -> dict:
        """Get available rivals for battle."""
        if not self.current_player:
            return {"error": "No player loaded"}
        
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT * FROM rivals 
            WHERE world_type = %s
            ORDER BY rival_level
        """, (self.current_player.world,))
        rivals = cur.fetchall()
        
        player_power = self._calculate_player_power()
        
        cur.close()
        conn.close()
        
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
        conn.close()
        
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
            conn.close()
            return {"error": "Rival not found"}
        
        player_power = self._calculate_player_power()
        rival_power = rival['rival_level'] * 50 + 100
        
        import random
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
        conn.close()
        
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
        conn.close()
        
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
        conn.close()
        
        return boss_scenarios


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


# ============================================================================
# ACCOUNTING SYSTEM FUNCTIONS
# ============================================================================

def get_player_chart_of_accounts(player_id: int) -> list:
    """Get the player's chart of accounts organized by type."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT account_id, account_code, account_name, account_type, normal_balance, description
        FROM chart_of_accounts
        WHERE player_id = %s AND is_active = TRUE
        ORDER BY account_code
    """, (player_id,))
    
    accounts = cur.fetchall()
    cur.close()
    conn.close()
    return accounts


def get_current_accounting_period(player_id: int) -> dict:
    """Get the player's current (open) accounting period."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT period_id, period_name, period_number, start_date, end_date, is_closed
        FROM accounting_periods
        WHERE player_id = %s AND is_closed = FALSE
        ORDER BY period_number DESC
        LIMIT 1
    """, (player_id,))
    
    period = cur.fetchone()
    cur.close()
    conn.close()
    return period


def get_pending_transactions(player_id: int) -> list:
    """Get all unprocessed transactions awaiting journal entry."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT transaction_id, transaction_type, description, amount, 
               suggested_debit_account, suggested_credit_account, source_type, created_at
        FROM pending_transactions
        WHERE player_id = %s AND is_processed = FALSE
        ORDER BY created_at
    """, (player_id,))
    
    transactions = cur.fetchall()
    cur.close()
    conn.close()
    return transactions


def create_pending_transaction(player_id: int, transaction_type: str, description: str, 
                              amount: float, debit_account: str, credit_account: str,
                              source_type: str = None, source_id: int = None) -> int:
    """Create a pending transaction for the player to record in their books."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO pending_transactions 
        (player_id, transaction_type, description, amount, suggested_debit_account, 
         suggested_credit_account, source_type, source_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING transaction_id
    """, (player_id, transaction_type, description, amount, debit_account, credit_account, source_type, source_id))
    
    transaction_id = cur.fetchone()['transaction_id']
    conn.commit()
    cur.close()
    conn.close()
    return transaction_id


def create_journal_entry(player_id: int, description: str, lines: list, 
                        is_adjusting: bool = False) -> dict:
    """
    Create a journal entry with debit and credit lines.
    
    lines should be a list of dicts: [{'account_code': '1000', 'debit': 100, 'credit': 0}, ...]
    Returns success status and entry info.
    """
    if not lines or len(lines) < 2:
        return {'success': False, 'error': 'Journal entry requires at least 2 lines', 'exp_earned': 0}
    
    for line in lines:
        debit = line.get('debit')
        credit = line.get('credit')
        line['debit'] = float(debit) if debit is not None else 0.0
        line['credit'] = float(credit) if credit is not None else 0.0
        if not line.get('account_code'):
            return {'success': False, 'error': 'Missing account code in journal line', 'exp_earned': 0}
    
    conn = get_connection()
    cur = conn.cursor()
    
    account_codes = [line['account_code'] for line in lines]
    placeholders = ','.join(['%s'] * len(account_codes))
    cur.execute(f"""
        SELECT account_code FROM chart_of_accounts 
        WHERE player_id = %s AND account_code IN ({placeholders})
    """, (player_id, *account_codes))
    valid_codes = [row['account_code'] for row in cur.fetchall()]
    
    for code in account_codes:
        if code not in valid_codes:
            cur.close()
            conn.close()
            return {'success': False, 'error': f'Invalid account code: {code}', 'exp_earned': 0}
    
    total_debits = sum(line['debit'] for line in lines)
    total_credits = sum(line['credit'] for line in lines)
    
    if abs(total_debits - total_credits) > 0.01:
        cur.close()
        conn.close()
        return {
            'success': False,
            'error': f'Debits (${total_debits:,.2f}) must equal Credits (${total_credits:,.2f})',
            'exp_earned': 0
        }
    
    # Get current period
    cur.execute("""
        SELECT period_id FROM accounting_periods 
        WHERE player_id = %s AND is_closed = FALSE 
        ORDER BY period_number DESC LIMIT 1
    """, (player_id,))
    period_result = cur.fetchone()
    period_id = period_result['period_id'] if period_result else None
    
    # Create journal entry
    cur.execute("""
        INSERT INTO journal_entries 
        (player_id, period_id, description, is_adjusting, total_debits, total_credits, is_posted)
        VALUES (%s, %s, %s, %s, %s, %s, TRUE)
        RETURNING entry_id
    """, (player_id, period_id, description, is_adjusting, total_debits, total_credits))
    
    entry_id = cur.fetchone()['entry_id']
    
    # Create journal lines
    for line in lines:
        cur.execute("""
            SELECT account_id FROM chart_of_accounts 
            WHERE player_id = %s AND account_code = %s
        """, (player_id, line['account_code']))
        account_result = cur.fetchone()
        
        if account_result:
            cur.execute("""
                INSERT INTO journal_lines (entry_id, account_id, debit_amount, credit_amount)
                VALUES (%s, %s, %s, %s)
            """, (entry_id, account_result['account_id'], line.get('debit', 0), line.get('credit', 0)))
    
    # Award EXP for correct entry
    exp_earned = 25 if is_adjusting else 15
    
    conn.commit()
    cur.close()
    conn.close()
    
    return {
        'success': True,
        'entry_id': entry_id,
        'total_debits': total_debits,
        'total_credits': total_credits,
        'exp_earned': exp_earned
    }


def get_journal_entries(player_id: int, period_id: int = None, limit: int = 20) -> list:
    """Get player's journal entries, optionally filtered by period."""
    conn = get_connection()
    cur = conn.cursor()
    
    if period_id:
        cur.execute("""
            SELECT je.entry_id, je.entry_date, je.description, je.total_debits, 
                   je.total_credits, je.is_adjusting, je.is_closing
            FROM journal_entries je
            WHERE je.player_id = %s AND je.period_id = %s AND je.is_posted = TRUE
            ORDER BY je.entry_date DESC
            LIMIT %s
        """, (player_id, period_id, limit))
    else:
        cur.execute("""
            SELECT je.entry_id, je.entry_date, je.description, je.total_debits, 
                   je.total_credits, je.is_adjusting, je.is_closing
            FROM journal_entries je
            WHERE je.player_id = %s AND je.is_posted = TRUE
            ORDER BY je.entry_date DESC
            LIMIT %s
        """, (player_id, limit))
    
    entries = cur.fetchall()
    cur.close()
    conn.close()
    return entries


def get_journal_entry_lines(entry_id: int) -> list:
    """Get the lines for a specific journal entry."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT jl.line_id, jl.debit_amount, jl.credit_amount,
               ca.account_code, ca.account_name, ca.account_type
        FROM journal_lines jl
        JOIN chart_of_accounts ca ON jl.account_id = ca.account_id
        WHERE jl.entry_id = %s
        ORDER BY jl.debit_amount DESC, jl.credit_amount DESC
    """, (entry_id,))
    
    lines = cur.fetchall()
    cur.close()
    conn.close()
    return lines


def get_trial_balance(player_id: int) -> dict:
    """
    Generate a trial balance from all posted journal entries.
    Returns account balances and totals.
    """
    conn = get_connection()
    cur = conn.cursor()
    
    # Get all accounts with their debit/credit totals from journal lines
    cur.execute("""
        SELECT ca.account_code, ca.account_name, ca.account_type, ca.normal_balance,
               COALESCE(SUM(jl.debit_amount), 0) as total_debits,
               COALESCE(SUM(jl.credit_amount), 0) as total_credits
        FROM chart_of_accounts ca
        LEFT JOIN journal_lines jl ON ca.account_id = jl.account_id
        LEFT JOIN journal_entries je ON jl.entry_id = je.entry_id AND je.is_posted = TRUE
        WHERE ca.player_id = %s AND ca.is_active = TRUE
        GROUP BY ca.account_id, ca.account_code, ca.account_name, ca.account_type, ca.normal_balance
        ORDER BY ca.account_code
    """, (player_id,))
    
    accounts = cur.fetchall()
    
    # Calculate balances based on normal balance type
    trial_balance = []
    total_debit_balance = 0
    total_credit_balance = 0
    
    for acc in accounts:
        net = float(acc['total_debits']) - float(acc['total_credits'])
        
        if acc['normal_balance'] == 'Debit':
            debit_bal = net if net >= 0 else 0
            credit_bal = abs(net) if net < 0 else 0
        else:
            credit_bal = abs(net) if net <= 0 else 0
            debit_bal = net if net > 0 else 0
        
        if debit_bal != 0 or credit_bal != 0:
            trial_balance.append({
                'account_code': acc['account_code'],
                'account_name': acc['account_name'],
                'account_type': acc['account_type'],
                'debit_balance': debit_bal,
                'credit_balance': credit_bal
            })
            total_debit_balance += debit_bal
            total_credit_balance += credit_bal
    
    cur.close()
    conn.close()
    
    return {
        'accounts': trial_balance,
        'total_debits': total_debit_balance,
        'total_credits': total_credit_balance,
        'is_balanced': abs(total_debit_balance - total_credit_balance) < 0.01
    }


def get_income_statement(player_id: int) -> dict:
    """Generate an income statement (P&L) from Revenue and Expense accounts."""
    conn = get_connection()
    cur = conn.cursor()
    
    # Get Revenue accounts (4xxx)
    cur.execute("""
        SELECT ca.account_code, ca.account_name,
               COALESCE(SUM(jl.credit_amount), 0) - COALESCE(SUM(jl.debit_amount), 0) as balance
        FROM chart_of_accounts ca
        LEFT JOIN journal_lines jl ON ca.account_id = jl.account_id
        LEFT JOIN journal_entries je ON jl.entry_id = je.entry_id AND je.is_posted = TRUE
        WHERE ca.player_id = %s AND ca.account_type = 'Revenue'
        GROUP BY ca.account_id, ca.account_code, ca.account_name
        HAVING COALESCE(SUM(jl.credit_amount), 0) - COALESCE(SUM(jl.debit_amount), 0) != 0
        ORDER BY ca.account_code
    """, (player_id,))
    revenues = cur.fetchall()
    
    # Get Expense accounts (5xxx)
    cur.execute("""
        SELECT ca.account_code, ca.account_name,
               COALESCE(SUM(jl.debit_amount), 0) - COALESCE(SUM(jl.credit_amount), 0) as balance
        FROM chart_of_accounts ca
        LEFT JOIN journal_lines jl ON ca.account_id = jl.account_id
        LEFT JOIN journal_entries je ON jl.entry_id = je.entry_id AND je.is_posted = TRUE
        WHERE ca.player_id = %s AND ca.account_type = 'Expense'
        GROUP BY ca.account_id, ca.account_code, ca.account_name
        HAVING COALESCE(SUM(jl.debit_amount), 0) - COALESCE(SUM(jl.credit_amount), 0) != 0
        ORDER BY ca.account_code
    """, (player_id,))
    expenses = cur.fetchall()
    
    cur.close()
    conn.close()
    
    total_revenue = sum(float(r['balance']) for r in revenues)
    total_expenses = sum(float(e['balance']) for e in expenses)
    net_income = total_revenue - total_expenses
    
    return {
        'revenues': revenues,
        'expenses': expenses,
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'net_income': net_income
    }


def get_balance_sheet(player_id: int) -> dict:
    """Generate a balance sheet from Asset, Liability, and Equity accounts."""
    conn = get_connection()
    cur = conn.cursor()
    
    # Get Assets
    cur.execute("""
        SELECT ca.account_code, ca.account_name, ca.normal_balance,
               COALESCE(SUM(jl.debit_amount), 0) - COALESCE(SUM(jl.credit_amount), 0) as balance
        FROM chart_of_accounts ca
        LEFT JOIN journal_lines jl ON ca.account_id = jl.account_id
        LEFT JOIN journal_entries je ON jl.entry_id = je.entry_id AND je.is_posted = TRUE
        WHERE ca.player_id = %s AND ca.account_type = 'Asset'
        GROUP BY ca.account_id, ca.account_code, ca.account_name, ca.normal_balance
        ORDER BY ca.account_code
    """, (player_id,))
    assets = [a for a in cur.fetchall() if float(a['balance']) != 0]
    
    # Get Liabilities
    cur.execute("""
        SELECT ca.account_code, ca.account_name,
               COALESCE(SUM(jl.credit_amount), 0) - COALESCE(SUM(jl.debit_amount), 0) as balance
        FROM chart_of_accounts ca
        LEFT JOIN journal_lines jl ON ca.account_id = jl.account_id
        LEFT JOIN journal_entries je ON jl.entry_id = je.entry_id AND je.is_posted = TRUE
        WHERE ca.player_id = %s AND ca.account_type = 'Liability'
        GROUP BY ca.account_id, ca.account_code, ca.account_name
        ORDER BY ca.account_code
    """, (player_id,))
    liabilities = [l for l in cur.fetchall() if float(l['balance']) != 0]
    
    # Get Equity
    cur.execute("""
        SELECT ca.account_code, ca.account_name, ca.normal_balance,
               CASE WHEN ca.normal_balance = 'Credit' 
                    THEN COALESCE(SUM(jl.credit_amount), 0) - COALESCE(SUM(jl.debit_amount), 0)
                    ELSE COALESCE(SUM(jl.debit_amount), 0) - COALESCE(SUM(jl.credit_amount), 0)
               END as balance
        FROM chart_of_accounts ca
        LEFT JOIN journal_lines jl ON ca.account_id = jl.account_id
        LEFT JOIN journal_entries je ON jl.entry_id = je.entry_id AND je.is_posted = TRUE
        WHERE ca.player_id = %s AND ca.account_type = 'Equity'
        GROUP BY ca.account_id, ca.account_code, ca.account_name, ca.normal_balance
        ORDER BY ca.account_code
    """, (player_id,))
    equity = [e for e in cur.fetchall() if float(e['balance']) != 0]
    
    cur.close()
    conn.close()
    
    total_assets = sum(float(a['balance']) for a in assets)
    total_liabilities = sum(float(l['balance']) for l in liabilities)
    total_equity = sum(float(e['balance']) for e in equity)
    
    return {
        'assets': assets,
        'liabilities': liabilities,
        'equity': equity,
        'total_assets': total_assets,
        'total_liabilities': total_liabilities,
        'total_equity': total_equity,
        'is_balanced': abs(total_assets - (total_liabilities + total_equity)) < 0.01
    }


def process_pending_transaction(player_id: int, transaction_id: int, 
                                debit_account: str, credit_account: str) -> dict:
    """Process a pending transaction by creating a journal entry."""
    if not debit_account or not credit_account:
        return {'success': False, 'error': 'Invalid account codes provided', 'exp_earned': 0}
    
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT account_code FROM chart_of_accounts 
        WHERE player_id = %s AND account_code IN (%s, %s)
    """, (player_id, debit_account, credit_account))
    valid_accounts = [row['account_code'] for row in cur.fetchall()]
    
    if debit_account not in valid_accounts or credit_account not in valid_accounts:
        cur.close()
        conn.close()
        return {'success': False, 'error': 'Invalid account codes - account not found', 'exp_earned': 0}
    
    cur.execute("""
        SELECT transaction_id, description, amount 
        FROM pending_transactions 
        WHERE transaction_id = %s AND player_id = %s AND is_processed = FALSE
    """, (transaction_id, player_id))
    
    txn = cur.fetchone()
    if not txn:
        cur.close()
        conn.close()
        return {'success': False, 'error': 'Transaction not found or already processed', 'exp_earned': 0}
    
    amount = float(txn['amount']) if txn['amount'] is not None else 0
    if amount <= 0:
        cur.close()
        conn.close()
        return {'success': False, 'error': 'Invalid transaction amount', 'exp_earned': 0}
    
    cur.close()
    conn.close()
    
    lines = [
        {'account_code': debit_account, 'debit': amount, 'credit': 0},
        {'account_code': credit_account, 'debit': 0, 'credit': amount}
    ]
    
    result = create_journal_entry(player_id, txn['description'], lines)
    
    if result['success']:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE pending_transactions SET is_processed = TRUE WHERE transaction_id = %s", (transaction_id,))
        conn.commit()
        cur.close()
        conn.close()
    
    return result


def get_player_initiatives(player_id: int) -> list:
    """Get all project initiatives for a player."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT initiative_id, title, description, world_type, industry,
               planned_duration_weeks, actual_duration_weeks, start_week, current_week,
               status, budget, spent, completion_bonus_exp, completion_bonus_cash,
               on_time_multiplier, created_at, completed_at
        FROM project_initiatives
        WHERE player_id = %s
        ORDER BY created_at DESC
    """, (player_id,))
    
    initiatives = [dict(row) for row in cur.fetchall()]
    
    for initiative in initiatives:
        cur.execute("""
            SELECT task_id, task_name, status, planned_start_week, planned_end_week,
                   actual_start_week, actual_end_week, is_critical_path, priority
            FROM project_tasks
            WHERE initiative_id = %s
            ORDER BY task_order
        """, (initiative['initiative_id'],))
        initiative['tasks'] = [dict(row) for row in cur.fetchall()]
        
        total_tasks = len(initiative['tasks'])
        completed_tasks = sum(1 for t in initiative['tasks'] if t['status'] == 'completed')
        initiative['progress_pct'] = int((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0)
    
    cur.close()
    conn.close()
    return initiatives


def get_active_initiative(player_id: int) -> dict:
    """Get the player's currently active project initiative."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT initiative_id, title, description, planned_duration_weeks,
               current_week, status, budget, spent
        FROM project_initiatives
        WHERE player_id = %s AND status IN ('planning', 'in_progress')
        ORDER BY created_at DESC LIMIT 1
    """, (player_id,))
    
    result = cur.fetchone()
    if not result:
        cur.close()
        conn.close()
        return None
    
    initiative = dict(result)
    
    cur.execute("""
        SELECT t.task_id, t.task_name, t.description, t.estimated_effort_hours,
               t.actual_effort_hours, t.planned_start_week, t.planned_end_week,
               t.actual_start_week, t.actual_end_week, t.status, t.priority,
               t.is_critical_path, t.task_order, t.exp_reward
        FROM project_tasks t
        WHERE t.initiative_id = %s
        ORDER BY t.task_order
    """, (initiative['initiative_id'],))
    initiative['tasks'] = [dict(row) for row in cur.fetchall()]
    
    for task in initiative['tasks']:
        cur.execute("""
            SELECT d.depends_on_task_id, pt.task_name
            FROM task_dependencies d
            JOIN project_tasks pt ON d.depends_on_task_id = pt.task_id
            WHERE d.task_id = %s
        """, (task['task_id'],))
        task['dependencies'] = [dict(row) for row in cur.fetchall()]
    
    cur.close()
    conn.close()
    return initiative


def create_initiative_from_template(player_id: int, template_index: int = 0) -> dict:
    """Create a new project initiative from a template."""
    from src.database import get_project_templates
    
    templates = get_project_templates()
    if template_index >= len(templates):
        return {'success': False, 'error': 'Invalid template'}
    
    template = templates[template_index]
    
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM project_initiatives WHERE player_id = %s AND status IN ('planning', 'in_progress')", (player_id,))
    if cur.fetchone()['count'] > 0:
        cur.close()
        conn.close()
        return {'success': False, 'error': 'Complete your current project first'}
    
    cur.execute("""
        INSERT INTO project_initiatives 
        (player_id, title, description, world_type, industry, planned_duration_weeks,
         budget, completion_bonus_exp, completion_bonus_cash, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'planning')
        RETURNING initiative_id
    """, (
        player_id, template['title'], template['description'],
        template['world_type'], template['industry'], template['planned_duration_weeks'],
        template['budget'], template['completion_bonus_exp'], template['completion_bonus_cash']
    ))
    
    initiative_id = cur.fetchone()['initiative_id']
    
    task_name_to_id = {}
    for i, task in enumerate(template['tasks']):
        cur.execute("""
            INSERT INTO project_tasks 
            (initiative_id, task_name, estimated_effort_hours, planned_start_week,
             planned_end_week, priority, task_order)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING task_id
        """, (
            initiative_id, task['name'], task['effort'],
            task['week_start'], task['week_end'], task['priority'], i
        ))
        task_name_to_id[task['name']] = cur.fetchone()['task_id']
    
    for task in template['tasks']:
        if 'depends_on' in task:
            task_id = task_name_to_id[task['name']]
            for dep_name in task['depends_on']:
                if dep_name in task_name_to_id:
                    cur.execute("""
                        INSERT INTO task_dependencies (task_id, depends_on_task_id, dependency_type)
                        VALUES (%s, %s, 'FS')
                    """, (task_id, task_name_to_id[dep_name]))
    
    calculate_critical_path(initiative_id)
    
    conn.commit()
    cur.close()
    conn.close()
    
    return {'success': True, 'initiative_id': initiative_id, 'title': template['title']}


def calculate_critical_path(initiative_id: int):
    """Calculate and mark the critical path for a project."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT task_id, task_name, planned_start_week, planned_end_week
        FROM project_tasks WHERE initiative_id = %s
        ORDER BY planned_end_week DESC, planned_start_week DESC
    """, (initiative_id,))
    tasks = [dict(row) for row in cur.fetchall()]
    
    if not tasks:
        cur.close()
        conn.close()
        return
    
    cur.execute("UPDATE project_tasks SET is_critical_path = FALSE WHERE initiative_id = %s", (initiative_id,))
    
    last_task = tasks[0]
    cur.execute("UPDATE project_tasks SET is_critical_path = TRUE WHERE task_id = %s", (last_task['task_id'],))
    
    critical_tasks = {last_task['task_id']}
    
    for _ in range(len(tasks)):
        for task_id in list(critical_tasks):
            cur.execute("""
                SELECT d.depends_on_task_id
                FROM task_dependencies d
                WHERE d.task_id = %s
            """, (task_id,))
            for row in cur.fetchall():
                dep_id = row['depends_on_task_id']
                if dep_id not in critical_tasks:
                    critical_tasks.add(dep_id)
                    cur.execute("UPDATE project_tasks SET is_critical_path = TRUE WHERE task_id = %s", (dep_id,))
    
    conn.commit()
    cur.close()
    conn.close()


def advance_project_week(player_id: int, initiative_id: int) -> dict:
    """Advance the project by one week, updating task progress."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT initiative_id, current_week, planned_duration_weeks, status, budget, spent
        FROM project_initiatives
        WHERE initiative_id = %s AND player_id = %s
    """, (initiative_id, player_id))
    
    initiative = cur.fetchone()
    if not initiative:
        cur.close()
        conn.close()
        return {'success': False, 'error': 'Project not found'}
    
    if initiative['status'] == 'completed':
        cur.close()
        conn.close()
        return {'success': False, 'error': 'Project already completed'}
    
    current_week = initiative['current_week']
    new_week = current_week + 1
    
    cur.execute("""
        SELECT task_id, task_name, status, planned_start_week, planned_end_week,
               estimated_effort_hours, actual_effort_hours
        FROM project_tasks
        WHERE initiative_id = %s
    """, (initiative_id,))
    tasks = [dict(row) for row in cur.fetchall()]
    
    exp_earned = 0
    completed_this_week = []
    
    for task in tasks:
        if task['status'] == 'not_started' and task['planned_start_week'] <= current_week:
            cur.execute("""
                SELECT COUNT(*) as count FROM task_dependencies d
                JOIN project_tasks pt ON d.depends_on_task_id = pt.task_id
                WHERE d.task_id = %s AND pt.status != 'completed'
            """, (task['task_id'],))
            
            if cur.fetchone()['count'] == 0:
                cur.execute("""
                    UPDATE project_tasks SET status = 'in_progress', actual_start_week = %s
                    WHERE task_id = %s
                """, (current_week, task['task_id']))
        
        if task['status'] == 'in_progress':
            progress_hours = min(40, task['estimated_effort_hours'] - task['actual_effort_hours'])
            new_actual = task['actual_effort_hours'] + progress_hours
            
            if new_actual >= task['estimated_effort_hours']:
                cur.execute("""
                    UPDATE project_tasks 
                    SET status = 'completed', actual_effort_hours = %s, actual_end_week = %s
                    WHERE task_id = %s
                """, (task['estimated_effort_hours'], current_week, task['task_id']))
                completed_this_week.append(task['task_name'])
                exp_earned += 20
            else:
                cur.execute("UPDATE project_tasks SET actual_effort_hours = %s WHERE task_id = %s", 
                           (new_actual, task['task_id']))
    
    cur.execute("""
        SELECT COUNT(*) as total, SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as done
        FROM project_tasks WHERE initiative_id = %s
    """, (initiative_id,))
    progress = cur.fetchone()
    all_done = progress['total'] == progress['done']
    
    project_completed = False
    bonus_earned = 0
    
    if all_done:
        on_time = new_week <= initiative['planned_duration_weeks']
        multiplier = float(initiative['on_time_multiplier']) if on_time else 1.0
        
        cur.execute("""
            SELECT completion_bonus_exp, completion_bonus_cash
            FROM project_initiatives WHERE initiative_id = %s
        """, (initiative_id,))
        bonuses = cur.fetchone()
        
        bonus_earned = int(bonuses['completion_bonus_exp'] * multiplier)
        cash_bonus = float(bonuses['completion_bonus_cash']) * multiplier
        
        cur.execute("""
            UPDATE project_initiatives 
            SET status = 'completed', actual_duration_weeks = %s, current_week = %s,
                completed_at = CURRENT_TIMESTAMP
            WHERE initiative_id = %s
        """, (new_week, new_week, initiative_id))
        
        cur.execute("UPDATE player_profiles SET cash = cash + %s WHERE player_id = %s", (cash_bonus, player_id))
        
        project_completed = True
        exp_earned += bonus_earned
    else:
        cur.execute("UPDATE project_initiatives SET current_week = %s, status = 'in_progress' WHERE initiative_id = %s", 
                   (new_week, initiative_id))
    
    planned_pct = min(100, (current_week / initiative['planned_duration_weeks']) * 100)
    actual_pct = (progress['done'] / progress['total'] * 100) if progress['total'] > 0 else 0
    variance = actual_pct - planned_pct
    
    cur.execute("""
        INSERT INTO project_history (initiative_id, week_number, planned_completion_pct, actual_completion_pct, variance_pct)
        VALUES (%s, %s, %s, %s, %s)
    """, (initiative_id, current_week, planned_pct, actual_pct, variance))
    
    conn.commit()
    cur.close()
    conn.close()
    
    return {
        'success': True,
        'new_week': new_week,
        'completed_tasks': completed_this_week,
        'exp_earned': exp_earned,
        'project_completed': project_completed,
        'bonus_earned': bonus_earned if project_completed else 0,
        'on_time': new_week <= initiative['planned_duration_weeks'] if project_completed else None
    }


def get_player_resources(player_id: int) -> list:
    """Get all resources available to a player."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT resource_id, resource_name, resource_type, capacity_hours_per_week,
               hourly_cost, skill_bonus, is_available
        FROM project_resources
        WHERE player_id = %s
        ORDER BY resource_id
    """, (player_id,))
    
    resources = [dict(row) for row in cur.fetchall()]
    cur.close()
    conn.close()
    return resources


def get_scheduling_challenges(player_level: int = 1) -> list:
    """Get scheduling challenges available for a player's level."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT challenge_id, title, description, challenge_type, difficulty,
               required_level, exp_reward, time_limit_seconds, hint_text
        FROM scheduling_challenges
        WHERE required_level <= %s AND is_active = TRUE
        ORDER BY required_level, difficulty
    """, (player_level,))
    
    challenges = [dict(row) for row in cur.fetchall()]
    cur.close()
    conn.close()
    return challenges


def get_scheduling_challenge(challenge_id: int) -> dict:
    """Get a specific scheduling challenge with full data."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT challenge_id, title, description, challenge_type, difficulty,
               task_data, correct_answer, exp_reward, time_limit_seconds, hint_text
        FROM scheduling_challenges
        WHERE challenge_id = %s AND is_active = TRUE
    """, (challenge_id,))
    
    result = cur.fetchone()
    cur.close()
    conn.close()
    
    if result:
        import json
        challenge = dict(result)
        challenge['task_data'] = json.loads(challenge['task_data']) if challenge['task_data'] else {}
        challenge['correct_answer'] = json.loads(challenge['correct_answer']) if challenge['correct_answer'] else {}
        return challenge
    return None


def submit_scheduling_challenge(player_id: int, challenge_id: int, answer: dict) -> dict:
    """Submit an answer for a scheduling challenge."""
    challenge = get_scheduling_challenge(challenge_id)
    if not challenge:
        return {'success': False, 'error': 'Challenge not found', 'exp_earned': 0}
    
    correct = challenge['correct_answer']
    is_correct = False
    
    if challenge['challenge_type'] == 'critical_path':
        user_duration = answer.get('duration', 0)
        correct_duration = correct.get('duration', 0)
        is_correct = abs(user_duration - correct_duration) <= 1
    
    elif challenge['challenge_type'] == 'estimation':
        user_expected = answer.get('expected', 0)
        correct_expected = correct.get('expected', 0)
        is_correct = abs(user_expected - correct_expected) <= 0.5
    
    elif challenge['challenge_type'] == 'resource_leveling':
        is_correct = True
        user_assignments = answer.get('assignments', {})
        for task_id, resource_id in user_assignments.items():
            if not resource_id:
                is_correct = False
                break
    
    elif challenge['challenge_type'] == 'compression':
        is_correct = answer.get('choice') == correct.get('best_option')
    
    else:
        is_correct = answer == correct
    
    exp_earned = challenge['exp_reward'] if is_correct else int(challenge['exp_reward'] * 0.25)
    
    return {
        'success': True,
        'is_correct': is_correct,
        'exp_earned': exp_earned,
        'correct_answer': correct,
        'feedback': 'Correct! Great scheduling skills!' if is_correct else 'Not quite right. Review the hint and try again.'
    }


def get_project_templates_list() -> list:
    """Get list of available project templates."""
    from src.database import get_project_templates
    templates = get_project_templates()
    return [
        {
            'index': i,
            'title': t['title'],
            'description': t['description'],
            'duration': t['planned_duration_weeks'],
            'budget': t['budget'],
            'reward_exp': t['completion_bonus_exp'],
            'reward_cash': t['completion_bonus_cash'],
            'task_count': len(t['tasks'])
        }
        for i, t in enumerate(templates)
    ]
