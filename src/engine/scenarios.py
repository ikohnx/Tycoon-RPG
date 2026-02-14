"""
ScenariosMixin - Scenario-related GameEngine methods.
"""

import random
import json
import math
from src.database import get_connection, return_connection
from src.leveling import calculate_weighted_exp, check_level_up
from src.engine.player import JOB_TITLES


class ScenariosMixin:
    """Mixin providing scenario-related methods for GameEngine."""

    def get_scenario_by_id(self, scenario_id: int) -> dict:
        """Get a specific scenario by ID."""
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM scenario_master WHERE scenario_id = %s", (scenario_id,))
        scenario = cur.fetchone()
        
        cur.close()
        return_connection(conn)
        
        return dict(scenario) if scenario else None
    
    def get_training_content(self, scenario_id: int) -> dict:
        """Get training/tutorial content for a scenario."""
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT training_content, discipline, challenge_type FROM scenario_master WHERE scenario_id = %s", (scenario_id,))
        result = cur.fetchone()
        
        cur.close()
        return_connection(conn)
        
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
        return_connection(conn)
        
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
        return_connection(conn)
        
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
        return_connection(conn)
        
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
        
        if leveled_up:
            levels_gained = new_level - old_level
            stat_points_earned = levels_gained * 2
            self.current_player.stats['stat_points'] += stat_points_earned
        
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
        return_connection(conn)
        
        self.current_player.save_to_db()
        
        from src.engine.accounting import create_pending_transaction
        
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
        
        from src.company_resources import (
            update_company_resources, record_decision, apply_ability_modifiers, 
            check_game_over, add_news_ticker
        )
        
        morale_change = scenario.get(f'{choice_prefix}_morale_change', 0) or 0
        brand_change = scenario.get(f'{choice_prefix}_brand_change', 0) or 0
        
        modifiers = apply_ability_modifiers(
            self.current_player.player_id, 
            base_exp=weighted_exp, 
            base_cash=boosted_cash if boosted_cash > 0 else 0,
            base_cost=abs(boosted_cash) if boosted_cash < 0 else 0
        )
        
        if boosted_cash > 0:
            modified_cash = modifiers.get('final_cash', boosted_cash)
        elif boosted_cash < 0:
            modified_cash = -modifiers.get('final_cost', abs(boosted_cash))
        else:
            modified_cash = 0
        
        resource_update = update_company_resources(
            self.current_player.player_id,
            capital_change=modified_cash,
            morale_change=morale_change,
            brand_change=brand_change
        )
        
        decision_result = record_decision(self.current_player.player_id)
        
        game_status = check_game_over(self.current_player.player_id)
        
        add_news_ticker(
            self.current_player.player_id,
            capital_change=modified_cash,
            morale_change=morale_change,
            brand_change=brand_change,
            headline=f"Decision made: {scenario['scenario_title']}",
            news_type='success' if modified_cash >= 0 else 'warning'
        )
        
        return {
            "success": True,
            "exp_gained": weighted_exp,
            "base_exp": base_exp,
            "cash_change": boosted_cash,
            "reputation_change": boosted_rep,
            "morale_change": morale_change,
            "brand_change": brand_change,
            "feedback": feedback,
            "leveled_up": leveled_up,
            "old_level": old_level,
            "new_level": new_level,
            "discipline": discipline,
            "new_total_exp": new_exp,
            "promotion": promotion,
            "stars_earned": stars,
            "advisor_bonuses": advisor_bonuses,
            "quarter_info": decision_result,
            "resource_update": resource_update,
            "game_status": game_status,
            "ability_modifiers": modifiers
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
        if luck_bonus > 0 and stars < 3:
            luck_chance = luck_bonus * 0.02
            if random.random() < luck_chance:
                stars += 1
        
        return stars
    
    def get_challenge_by_id(self, scenario_id: int) -> dict:
        """Get a challenge scenario with parsed config."""
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM scenario_master WHERE scenario_id = %s", (scenario_id,))
        scenario = cur.fetchone()
        
        cur.close()
        return_connection(conn)
        
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
        if not self.current_player:
            return {"error": "No player loaded"}
        
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM scenario_master WHERE scenario_id = %s", (scenario_id,))
        scenario = cur.fetchone()
        
        if not scenario:
            cur.close()
            return_connection(conn)
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
        
        stat_points_earned = 0
        if leveled_up:
            levels_gained = new_level - old_level
            stat_points_earned = levels_gained * 2
            self.current_player.stats['stat_points'] += stat_points_earned
        
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
        
        if stat_points_earned > 0:
            cur.execute("""
                UPDATE player_stats
                SET stat_points_available = stat_points_available + %s
                WHERE player_id = %s
            """, (stat_points_earned, self.current_player.player_id))
        
        conn.commit()
        cur.close()
        return_connection(conn)
        
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
