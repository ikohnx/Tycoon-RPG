import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    """Get a database connection using DATABASE_URL environment variable."""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    return psycopg2.connect(database_url, cursor_factory=RealDictCursor)


def init_database():
    """Initialize all database tables for the Business Tycoon RPG."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_profiles (
            player_id SERIAL PRIMARY KEY,
            player_name VARCHAR(100) NOT NULL,
            chosen_world VARCHAR(50) NOT NULL DEFAULT 'Modern',
            chosen_industry VARCHAR(100) NOT NULL DEFAULT 'Restaurant',
            career_path VARCHAR(50) NOT NULL DEFAULT 'entrepreneur',
            job_title VARCHAR(100) DEFAULT NULL,
            job_level INTEGER DEFAULT 1,
            total_cash DECIMAL(15, 2) DEFAULT 10000.00,
            business_reputation INTEGER DEFAULT 50,
            current_month INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_played TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cur.execute("""
        ALTER TABLE player_profiles 
        ADD COLUMN IF NOT EXISTS career_path VARCHAR(50) NOT NULL DEFAULT 'entrepreneur';
    """)
    
    cur.execute("""
        ALTER TABLE player_profiles 
        ADD COLUMN IF NOT EXISTS job_title VARCHAR(100) DEFAULT NULL;
    """)
    
    cur.execute("""
        ALTER TABLE player_profiles 
        ADD COLUMN IF NOT EXISTS job_level INTEGER DEFAULT 1;
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_discipline_progress (
            progress_id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            discipline_name VARCHAR(100) NOT NULL,
            current_level INTEGER DEFAULT 1,
            current_exp INTEGER DEFAULT 0,
            total_exp_earned INTEGER DEFAULT 0,
            UNIQUE(player_id, discipline_name)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_subskill_progress (
            subskill_id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            subskill_name VARCHAR(100) NOT NULL,
            parent_discipline VARCHAR(100) NOT NULL,
            current_level INTEGER DEFAULT 1,
            current_exp INTEGER DEFAULT 0,
            UNIQUE(player_id, subskill_name)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS scenario_master (
            scenario_id SERIAL PRIMARY KEY,
            world_type VARCHAR(50) NOT NULL,
            industry VARCHAR(100) NOT NULL,
            discipline VARCHAR(100) NOT NULL,
            required_level INTEGER NOT NULL,
            scenario_title VARCHAR(255) NOT NULL,
            scenario_narrative TEXT NOT NULL,
            choice_a_text TEXT NOT NULL,
            choice_a_exp_reward INTEGER NOT NULL,
            choice_a_cash_change DECIMAL(10, 2) DEFAULT 0,
            choice_a_reputation_change INTEGER DEFAULT 0,
            choice_a_feedback TEXT NOT NULL,
            choice_b_text TEXT NOT NULL,
            choice_b_exp_reward INTEGER NOT NULL,
            choice_b_cash_change DECIMAL(10, 2) DEFAULT 0,
            choice_b_reputation_change INTEGER DEFAULT 0,
            choice_b_feedback TEXT NOT NULL,
            choice_c_text TEXT,
            choice_c_exp_reward INTEGER DEFAULT 0,
            choice_c_cash_change DECIMAL(10, 2) DEFAULT 0,
            choice_c_reputation_change INTEGER DEFAULT 0,
            choice_c_feedback TEXT,
            subskill_focus VARCHAR(100),
            storyline_arc VARCHAR(100),
            is_active BOOLEAN DEFAULT TRUE
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS financial_metrics (
            metric_id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            month_number INTEGER NOT NULL,
            revenue DECIMAL(15, 2) DEFAULT 0,
            wages_cost DECIMAL(15, 2) DEFAULT 0,
            rent_cost DECIMAL(15, 2) DEFAULT 0,
            taxes_cost DECIMAL(15, 2) DEFAULT 0,
            other_costs DECIMAL(15, 2) DEFAULT 0,
            net_profit DECIMAL(15, 2) DEFAULT 0,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(player_id, month_number)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS completed_scenarios (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            scenario_id INTEGER REFERENCES scenario_master(scenario_id) ON DELETE CASCADE,
            choice_made CHAR(1) NOT NULL,
            stars_earned INTEGER DEFAULT 1,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(player_id, scenario_id)
        );
    """)
    
    cur.execute("""
        ALTER TABLE completed_scenarios 
        ADD COLUMN IF NOT EXISTS stars_earned INTEGER DEFAULT 1;
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_stats (
            stat_id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            charisma INTEGER DEFAULT 5,
            intelligence INTEGER DEFAULT 5,
            luck INTEGER DEFAULT 5,
            negotiation INTEGER DEFAULT 5,
            stat_points_available INTEGER DEFAULT 3,
            UNIQUE(player_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS achievements (
            achievement_id SERIAL PRIMARY KEY,
            achievement_code VARCHAR(50) UNIQUE NOT NULL,
            achievement_name VARCHAR(100) NOT NULL,
            achievement_description TEXT NOT NULL,
            achievement_icon VARCHAR(50) DEFAULT 'trophy',
            exp_reward INTEGER DEFAULT 0,
            cash_reward DECIMAL(10, 2) DEFAULT 0
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_achievements (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            achievement_id INTEGER REFERENCES achievements(achievement_id) ON DELETE CASCADE,
            earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(player_id, achievement_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS items (
            item_id SERIAL PRIMARY KEY,
            item_code VARCHAR(50) UNIQUE NOT NULL,
            item_name VARCHAR(100) NOT NULL,
            item_description TEXT NOT NULL,
            item_type VARCHAR(50) NOT NULL,
            item_icon VARCHAR(50) DEFAULT 'box',
            purchase_price DECIMAL(10, 2) DEFAULT 0,
            effect_type VARCHAR(50),
            effect_value INTEGER DEFAULT 0,
            is_consumable BOOLEAN DEFAULT FALSE
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_inventory (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            item_id INTEGER REFERENCES items(item_id) ON DELETE CASCADE,
            quantity INTEGER DEFAULT 1,
            acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(player_id, item_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS npcs (
            npc_id SERIAL PRIMARY KEY,
            npc_code VARCHAR(50) UNIQUE NOT NULL,
            npc_name VARCHAR(100) NOT NULL,
            npc_title VARCHAR(100),
            npc_description TEXT,
            npc_type VARCHAR(50) NOT NULL,
            world_type VARCHAR(50) NOT NULL,
            dialogue_intro TEXT,
            avatar_image VARCHAR(255)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_npc_relationships (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            npc_id INTEGER REFERENCES npcs(npc_id) ON DELETE CASCADE,
            relationship_level INTEGER DEFAULT 0,
            times_interacted INTEGER DEFAULT 0,
            last_interaction TIMESTAMP,
            UNIQUE(player_id, npc_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS quests (
            quest_id SERIAL PRIMARY KEY,
            quest_code VARCHAR(50) UNIQUE NOT NULL,
            quest_name VARCHAR(100) NOT NULL,
            quest_description TEXT NOT NULL,
            quest_type VARCHAR(50) NOT NULL,
            world_type VARCHAR(50) NOT NULL,
            required_level INTEGER DEFAULT 1,
            exp_reward INTEGER DEFAULT 0,
            cash_reward DECIMAL(10, 2) DEFAULT 0,
            reputation_reward INTEGER DEFAULT 0,
            prerequisite_quest_id INTEGER REFERENCES quests(quest_id),
            npc_giver_id INTEGER REFERENCES npcs(npc_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_quests (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            quest_id INTEGER REFERENCES quests(quest_id) ON DELETE CASCADE,
            status VARCHAR(50) DEFAULT 'available',
            progress INTEGER DEFAULT 0,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            UNIQUE(player_id, quest_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS random_events (
            event_id SERIAL PRIMARY KEY,
            event_code VARCHAR(50) UNIQUE NOT NULL,
            event_name VARCHAR(100) NOT NULL,
            event_description TEXT NOT NULL,
            event_type VARCHAR(50) NOT NULL,
            world_type VARCHAR(50) NOT NULL,
            industry VARCHAR(100),
            choice_a_text TEXT NOT NULL,
            choice_a_cash_change DECIMAL(10, 2) DEFAULT 0,
            choice_a_reputation_change INTEGER DEFAULT 0,
            choice_a_feedback TEXT NOT NULL,
            choice_b_text TEXT NOT NULL,
            choice_b_cash_change DECIMAL(10, 2) DEFAULT 0,
            choice_b_reputation_change INTEGER DEFAULT 0,
            choice_b_feedback TEXT NOT NULL,
            rarity VARCHAR(20) DEFAULT 'common',
            min_level INTEGER DEFAULT 1
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_event_history (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            event_id INTEGER REFERENCES random_events(event_id) ON DELETE CASCADE,
            choice_made CHAR(1) NOT NULL,
            occurred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS weekly_challenges (
            challenge_id SERIAL PRIMARY KEY,
            challenge_code VARCHAR(50) UNIQUE NOT NULL,
            challenge_name VARCHAR(100) NOT NULL,
            challenge_description TEXT NOT NULL,
            challenge_type VARCHAR(50) NOT NULL,
            target_value INTEGER NOT NULL,
            exp_reward INTEGER DEFAULT 0,
            cash_reward DECIMAL(10, 2) DEFAULT 0,
            start_date DATE,
            end_date DATE,
            is_active BOOLEAN DEFAULT TRUE
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_challenge_progress (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            challenge_id INTEGER REFERENCES weekly_challenges(challenge_id) ON DELETE CASCADE,
            current_progress INTEGER DEFAULT 0,
            completed BOOLEAN DEFAULT FALSE,
            completed_at TIMESTAMP,
            UNIQUE(player_id, challenge_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS avatar_options (
            option_id SERIAL PRIMARY KEY,
            option_type VARCHAR(50) NOT NULL,
            option_code VARCHAR(50) UNIQUE NOT NULL,
            option_name VARCHAR(100) NOT NULL,
            option_image VARCHAR(255),
            unlock_cost DECIMAL(10, 2) DEFAULT 0,
            unlock_level INTEGER DEFAULT 1
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_avatar (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            hair_style VARCHAR(50) DEFAULT 'default',
            outfit VARCHAR(50) DEFAULT 'default',
            accessory VARCHAR(50) DEFAULT 'none',
            color_scheme VARCHAR(50) DEFAULT 'blue',
            UNIQUE(player_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS rivals (
            rival_id SERIAL PRIMARY KEY,
            rival_code VARCHAR(50) UNIQUE NOT NULL,
            rival_name VARCHAR(100) NOT NULL,
            rival_business VARCHAR(100) NOT NULL,
            rival_description TEXT,
            world_type VARCHAR(50) NOT NULL,
            industry VARCHAR(100) NOT NULL,
            difficulty_level INTEGER DEFAULT 1,
            avatar_image VARCHAR(255)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_rival_status (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            rival_id INTEGER REFERENCES rivals(rival_id) ON DELETE CASCADE,
            competition_score INTEGER DEFAULT 0,
            times_beaten INTEGER DEFAULT 0,
            times_lost INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT TRUE,
            UNIQUE(player_id, rival_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS business_milestones (
            milestone_id SERIAL PRIMARY KEY,
            milestone_code VARCHAR(50) UNIQUE NOT NULL,
            milestone_name VARCHAR(100) NOT NULL,
            milestone_description TEXT NOT NULL,
            milestone_type VARCHAR(50) NOT NULL,
            target_value DECIMAL(15, 2) NOT NULL,
            exp_reward INTEGER DEFAULT 0,
            cash_reward DECIMAL(10, 2) DEFAULT 0,
            badge_icon VARCHAR(50) DEFAULT 'award'
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_milestones (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            milestone_id INTEGER REFERENCES business_milestones(milestone_id) ON DELETE CASCADE,
            achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(player_id, milestone_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_energy (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            current_energy INTEGER DEFAULT 100,
            max_energy INTEGER DEFAULT 100,
            last_recharge_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(player_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_daily_login (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            current_streak INTEGER DEFAULT 0,
            longest_streak INTEGER DEFAULT 0,
            last_login_date DATE,
            last_claim_date DATE,
            UNIQUE(player_id)
        );
    """)
    
    cur.execute("""
        ALTER TABLE player_daily_login ADD COLUMN IF NOT EXISTS current_streak INTEGER DEFAULT 0;
    """)
    cur.execute("""
        ALTER TABLE player_daily_login ADD COLUMN IF NOT EXISTS longest_streak INTEGER DEFAULT 0;
    """)
    cur.execute("""
        ALTER TABLE player_daily_login ADD COLUMN IF NOT EXISTS last_claim_date DATE;
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_prestige (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            prestige_level INTEGER DEFAULT 0,
            exp_multiplier DECIMAL(5, 2) DEFAULT 1.0,
            gold_multiplier DECIMAL(5, 2) DEFAULT 1.0,
            total_prestiges INTEGER DEFAULT 0,
            UNIQUE(player_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS daily_login_rewards (
            day_number INTEGER PRIMARY KEY,
            reward_type VARCHAR(50) NOT NULL,
            reward_amount INTEGER NOT NULL,
            reward_description TEXT NOT NULL
        );
    """)
    
    cur.execute("""
        ALTER TABLE daily_login_rewards ADD COLUMN IF NOT EXISTS reward_amount INTEGER DEFAULT 0;
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_idle_income (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            gold_per_minute DECIMAL(10, 2) DEFAULT 0,
            last_collection_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            uncollected_gold DECIMAL(15, 2) DEFAULT 0,
            UNIQUE(player_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS advisors (
            advisor_id SERIAL PRIMARY KEY,
            advisor_code VARCHAR(50) UNIQUE NOT NULL,
            advisor_name VARCHAR(100) NOT NULL,
            advisor_title VARCHAR(100) NOT NULL,
            advisor_description TEXT,
            discipline_specialty VARCHAR(100) NOT NULL,
            bonus_type VARCHAR(50) NOT NULL,
            bonus_value INTEGER DEFAULT 10,
            rarity VARCHAR(20) DEFAULT 'common',
            unlock_cost DECIMAL(10, 2) DEFAULT 0,
            avatar_image VARCHAR(255)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_advisors (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            advisor_id INTEGER REFERENCES advisors(advisor_id) ON DELETE CASCADE,
            level INTEGER DEFAULT 1,
            recruited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            UNIQUE(player_id, advisor_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS equipment (
            equipment_id SERIAL PRIMARY KEY,
            equipment_code VARCHAR(50) UNIQUE NOT NULL,
            equipment_name VARCHAR(100) NOT NULL,
            equipment_description TEXT,
            slot_type VARCHAR(50) NOT NULL,
            stat_bonus_type VARCHAR(50) NOT NULL,
            stat_bonus_value INTEGER DEFAULT 0,
            rarity VARCHAR(20) DEFAULT 'common',
            purchase_price DECIMAL(10, 2) DEFAULT 0,
            level_required INTEGER DEFAULT 1,
            icon_image VARCHAR(255)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_equipment (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            equipment_id INTEGER REFERENCES equipment(equipment_id) ON DELETE CASCADE,
            slot_type VARCHAR(50) NOT NULL,
            is_equipped BOOLEAN DEFAULT FALSE,
            acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(player_id, equipment_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_prestige (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            prestige_level INTEGER DEFAULT 0,
            exp_multiplier DECIMAL(5, 2) DEFAULT 1.0,
            gold_multiplier DECIMAL(5, 2) DEFAULT 1.0,
            total_prestiges INTEGER DEFAULT 0,
            last_prestige_at TIMESTAMP,
            UNIQUE(player_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS daily_missions (
            mission_id SERIAL PRIMARY KEY,
            mission_code VARCHAR(50) UNIQUE NOT NULL,
            mission_name VARCHAR(100) NOT NULL,
            mission_description TEXT NOT NULL,
            mission_type VARCHAR(50) NOT NULL,
            target_value INTEGER NOT NULL,
            exp_reward INTEGER DEFAULT 0,
            cash_reward DECIMAL(10, 2) DEFAULT 0,
            energy_reward INTEGER DEFAULT 0
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_daily_missions (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            mission_id INTEGER REFERENCES daily_missions(mission_id) ON DELETE CASCADE,
            current_progress INTEGER DEFAULT 0,
            completed BOOLEAN DEFAULT FALSE,
            assigned_date DATE DEFAULT CURRENT_DATE,
            completed_at TIMESTAMP,
            UNIQUE(player_id, mission_id, assigned_date)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS boss_scenarios (
            boss_id SERIAL PRIMARY KEY,
            scenario_id INTEGER REFERENCES scenario_master(scenario_id) ON DELETE CASCADE,
            boss_name VARCHAR(100) NOT NULL,
            boss_description TEXT,
            difficulty_rating INTEGER DEFAULT 5,
            bonus_exp_multiplier DECIMAL(3, 1) DEFAULT 2.0,
            bonus_cash_reward DECIMAL(10, 2) DEFAULT 0,
            world_type VARCHAR(50) NOT NULL,
            discipline VARCHAR(100) NOT NULL,
            required_level INTEGER NOT NULL,
            UNIQUE(scenario_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS leaderboard_cache (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            total_stars INTEGER DEFAULT 0,
            total_wealth DECIMAL(15, 2) DEFAULT 0,
            highest_discipline_level INTEGER DEFAULT 1,
            total_scenarios_completed INTEGER DEFAULT 0,
            rank_stars INTEGER,
            rank_wealth INTEGER,
            rank_level INTEGER,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(player_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS rival_battles (
            battle_id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            rival_id INTEGER REFERENCES rivals(rival_id) ON DELETE CASCADE,
            player_score INTEGER DEFAULT 0,
            rival_score INTEGER DEFAULT 0,
            winner VARCHAR(20),
            rewards_earned DECIMAL(10, 2) DEFAULT 0,
            battle_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    conn.commit()
    cur.close()
    conn.close()
    print("Database initialized successfully!")


def seed_scenarios():
    """Seed the database with MVP scenarios: Modern World / Restaurant / Marketing (L1-L5)."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM scenario_master WHERE world_type = 'Modern' AND industry = 'Restaurant' AND discipline = 'Marketing'")
    result = cur.fetchone()
    if result['count'] > 0:
        print("Scenarios already seeded.")
        cur.close()
        conn.close()
        return
    
    scenarios = [
        {
            "world_type": "Modern",
            "industry": "Restaurant",
            "discipline": "Marketing",
            "required_level": 1,
            "scenario_title": "Your First Menu Design",
            "scenario_narrative": "You've just opened your restaurant and need to create your first menu. A local designer offers two approaches: a simple text-based menu that's cheap to print, or a colorful photo menu that costs more but showcases your dishes.",
            "choice_a_text": "Go with the simple text menu to save costs ($50)",
            "choice_a_exp_reward": 75,
            "choice_a_cash_change": -50,
            "choice_a_reputation_change": 0,
            "choice_a_feedback": "You saved money, but customers struggle to visualize dishes. You learned that sometimes presentation matters in marketing.",
            "choice_b_text": "Invest in the photo menu ($200)",
            "choice_b_exp_reward": 100,
            "choice_b_cash_change": -200,
            "choice_b_reputation_change": 5,
            "choice_b_feedback": "Excellent choice! Customers order more when they see appetizing photos. You've learned the power of visual marketing.",
            "choice_c_text": "Create a QR code menu that links to an online gallery ($100)",
            "choice_c_exp_reward": 125,
            "choice_c_cash_change": -100,
            "choice_c_reputation_change": 3,
            "choice_c_feedback": "Innovative! You've embraced digital marketing while saving paper costs. Younger customers especially appreciate this approach.",
            "subskill_focus": "Brand Identity"
        },
        {
            "world_type": "Modern",
            "industry": "Restaurant",
            "discipline": "Marketing",
            "required_level": 1,
            "scenario_title": "Social Media Presence",
            "scenario_narrative": "A customer asks if you're on social media. You realize you haven't set up any accounts yet. Your competitor across the street has 5,000 followers on Instagram.",
            "choice_a_text": "Create accounts on all major platforms immediately",
            "choice_a_exp_reward": 80,
            "choice_a_cash_change": 0,
            "choice_a_reputation_change": 2,
            "choice_a_feedback": "Good initiative, but spreading thin across platforms means inconsistent posting. Focus is key in social media marketing.",
            "choice_b_text": "Focus on one platform (Instagram) and do it well",
            "choice_b_exp_reward": 110,
            "choice_b_cash_change": 0,
            "choice_b_reputation_change": 4,
            "choice_b_feedback": "Smart strategy! Concentrated effort on one platform builds a stronger following. You've learned about focused marketing.",
            "choice_c_text": "Hire a social media manager for $500/month",
            "choice_c_exp_reward": 90,
            "choice_c_cash_change": -500,
            "choice_c_reputation_change": 3,
            "choice_c_feedback": "Professional help is valuable, but at your current stage, learning the basics yourself builds important marketing skills.",
            "subskill_focus": "Digital Marketing"
        },
        {
            "world_type": "Modern",
            "industry": "Restaurant",
            "discipline": "Marketing",
            "required_level": 2,
            "scenario_title": "The Grand Opening Event",
            "scenario_narrative": "It's time for your grand opening! You have a budget of $1,000. A local radio station offers advertising, while a food blogger with 20,000 followers wants to feature you.",
            "choice_a_text": "Spend it all on radio advertising",
            "choice_a_exp_reward": 150,
            "choice_a_cash_change": -1000,
            "choice_a_reputation_change": 3,
            "choice_a_feedback": "Radio reaches broad audiences but lacks targeting. ROI is hard to measure. Traditional marketing still has its place though.",
            "choice_b_text": "Invite the food blogger for a free tasting experience",
            "choice_b_exp_reward": 200,
            "choice_b_cash_change": -150,
            "choice_b_reputation_change": 8,
            "choice_b_feedback": "Brilliant! Influencer marketing gives authentic exposure to engaged food lovers. Your cost per impression was excellent!",
            "choice_c_text": "Split the budget between both options",
            "choice_c_exp_reward": 175,
            "choice_c_cash_change": -600,
            "choice_c_reputation_change": 5,
            "choice_c_feedback": "Diversifying marketing channels reduces risk. You've learned about multi-channel marketing strategy.",
            "subskill_focus": "Campaign Planning"
        },
        {
            "world_type": "Modern",
            "industry": "Restaurant",
            "discipline": "Marketing",
            "required_level": 2,
            "scenario_title": "Customer Reviews Crisis",
            "scenario_narrative": "You receive your first 1-star review online. The customer claims the service was slow. You know it was an unusually busy night. How do you respond?",
            "choice_a_text": "Ignore it - one bad review won't hurt",
            "choice_a_exp_reward": 50,
            "choice_a_cash_change": 0,
            "choice_a_reputation_change": -5,
            "choice_a_feedback": "Ignoring negative reviews is a missed opportunity. Potential customers see unaddressed complaints as red flags.",
            "choice_b_text": "Respond publicly with an apology and offer a free meal",
            "choice_b_exp_reward": 200,
            "choice_b_cash_change": -30,
            "choice_b_reputation_change": 6,
            "choice_b_feedback": "Excellent reputation management! Public responses show you care. Many customers trust businesses more after seeing problems handled well.",
            "choice_c_text": "Respond defensively explaining it was a busy night",
            "choice_c_exp_reward": 75,
            "choice_c_cash_change": 0,
            "choice_c_reputation_change": -3,
            "choice_c_feedback": "Being defensive rarely helps. Customers want acknowledgment, not excuses. This is a key lesson in brand management.",
            "subskill_focus": "Brand Identity"
        },
        {
            "world_type": "Modern",
            "industry": "Restaurant",
            "discipline": "Marketing",
            "required_level": 3,
            "scenario_title": "Loyalty Program Design",
            "scenario_narrative": "Regular customers are asking about rewards. You need to design a loyalty program. Options range from simple punch cards to a digital app.",
            "choice_a_text": "Classic punch card: Buy 10, get 1 free",
            "choice_a_exp_reward": 200,
            "choice_a_cash_change": -100,
            "choice_a_reputation_change": 4,
            "choice_a_feedback": "Simple and effective! Low-tech solutions work well for casual dining. You understand that complexity isn't always better.",
            "choice_b_text": "Digital app with points and tiered rewards ($2,000 development)",
            "choice_b_exp_reward": 300,
            "choice_b_cash_change": -2000,
            "choice_b_reputation_change": 7,
            "choice_b_feedback": "High investment but you gain valuable customer data for future marketing. Digital loyalty programs enable personalization.",
            "choice_c_text": "Partner with an existing loyalty platform ($200/month)",
            "choice_c_exp_reward": 275,
            "choice_c_cash_change": -200,
            "choice_c_reputation_change": 5,
            "choice_c_feedback": "Smart outsourcing! You get professional features without development costs. Understanding when to build vs buy is crucial.",
            "subskill_focus": "Customer Retention"
        },
        {
            "world_type": "Modern",
            "industry": "Restaurant",
            "discipline": "Marketing",
            "required_level": 3,
            "scenario_title": "Calculating Marketing ROI",
            "scenario_narrative": "You spent $500 on Facebook ads last month. Your analytics show 50 new customers came from these ads, with an average spend of $25 each. Was this campaign successful?",
            "choice_a_text": "Yes! We got 50 new customers",
            "choice_a_exp_reward": 175,
            "choice_a_cash_change": 0,
            "choice_a_reputation_change": 0,
            "choice_a_feedback": "New customers are good, but look deeper! $500 spent / 50 customers = $10 cost per acquisition. With $25 average spend and ~30% profit margin, you made ~$7.50 profit per customer. ROI is $375 return on $500 = 75% loss initially, but lifetime value matters!",
            "choice_b_text": "Calculate the Customer Acquisition Cost (CAC) first",
            "choice_b_exp_reward": 325,
            "choice_b_cash_change": 0,
            "choice_b_reputation_change": 2,
            "choice_b_feedback": "Excellent analytical thinking! CAC = $500/50 = $10 per customer. If these customers return 3+ times, you'll profit. Understanding CAC and Customer Lifetime Value (CLV) is essential marketing knowledge.",
            "choice_c_text": "No, we spent $500 and only got $1,250 in sales",
            "choice_c_exp_reward": 150,
            "choice_c_cash_change": 0,
            "choice_c_reputation_change": 0,
            "choice_c_feedback": "You're thinking about profit, which is good! But marketing ROI isn't just immediate sales. Consider repeat customers and referrals - the lifetime value equation.",
            "subskill_focus": "Analytics"
        },
        {
            "world_type": "Modern",
            "industry": "Restaurant",
            "discipline": "Marketing",
            "required_level": 4,
            "scenario_title": "Seasonal Campaign Strategy",
            "scenario_narrative": "Valentine's Day is approaching. Last year's revenue was $3,000 for that day. How will you maximize this opportunity?",
            "choice_a_text": "Create a special prix-fixe menu at $75 per couple",
            "choice_a_exp_reward": 350,
            "choice_a_cash_change": 1500,
            "choice_a_reputation_change": 6,
            "choice_a_feedback": "Smart premium positioning! Limited-time offers create urgency. You've applied scarcity marketing principles effectively.",
            "choice_b_text": "Run a 'Galentine's Day' promotion for friend groups",
            "choice_b_exp_reward": 400,
            "choice_b_cash_change": 2000,
            "choice_b_reputation_change": 8,
            "choice_b_feedback": "Innovative market segmentation! You identified an underserved audience. Thinking beyond traditional markets is advanced marketing.",
            "choice_c_text": "Offer 20% discount to attract more volume",
            "choice_c_exp_reward": 225,
            "choice_c_cash_change": 500,
            "choice_c_reputation_change": 2,
            "choice_c_feedback": "Discounting on a high-demand day leaves money on the table. Price strategy should consider demand elasticity.",
            "subskill_focus": "Campaign Planning"
        },
        {
            "world_type": "Modern",
            "industry": "Restaurant",
            "discipline": "Marketing",
            "required_level": 4,
            "scenario_title": "Local Business Partnership",
            "scenario_narrative": "The movie theater next door proposes a partnership: they'll promote your restaurant if you offer discounts to their ticket holders. How do you negotiate?",
            "choice_a_text": "Accept their terms immediately - any exposure is good",
            "choice_a_exp_reward": 275,
            "choice_a_cash_change": -200,
            "choice_a_reputation_change": 3,
            "choice_a_feedback": "Enthusiasm is good, but you may have gotten a better deal. Always negotiate in business partnerships.",
            "choice_b_text": "Counter-propose: 10% discount for ticket holders, they feature you in their pre-movie ads",
            "choice_b_exp_reward": 425,
            "choice_b_cash_change": 300,
            "choice_b_reputation_change": 7,
            "choice_b_feedback": "Masterful negotiation! You created mutual value. Cross-promotion partnerships work best when both parties contribute equally.",
            "choice_c_text": "Decline - you don't want to give discounts",
            "choice_c_exp_reward": 100,
            "choice_c_cash_change": 0,
            "choice_c_reputation_change": -2,
            "choice_c_feedback": "You missed a strategic opportunity. Partnerships expand your reach to new customers at low cost.",
            "subskill_focus": "Negotiation"
        },
        {
            "world_type": "Modern",
            "industry": "Restaurant",
            "discipline": "Marketing",
            "required_level": 5,
            "scenario_title": "Market Research Investment",
            "scenario_narrative": "A market research firm offers a comprehensive study of your target demographic for $5,000. It includes competitor analysis, customer surveys, and trend forecasting.",
            "choice_a_text": "Too expensive - rely on your intuition instead",
            "choice_a_exp_reward": 200,
            "choice_a_cash_change": 0,
            "choice_a_reputation_change": 0,
            "choice_a_feedback": "Intuition has limits. Data-driven decisions reduce risk. At scale, $5,000 for actionable insights can prevent costly mistakes.",
            "choice_b_text": "Invest in the full research package",
            "choice_b_exp_reward": 500,
            "choice_b_cash_change": -5000,
            "choice_b_reputation_change": 5,
            "choice_b_feedback": "Strategic investment in knowledge! The insights reveal an underserved late-night market segment worth $50,000+ annually.",
            "choice_c_text": "Negotiate a smaller, focused study for $2,000",
            "choice_c_exp_reward": 450,
            "choice_c_cash_change": -2000,
            "choice_c_reputation_change": 3,
            "choice_c_feedback": "Good negotiation and resource management! You got core insights while preserving capital. Balancing information needs with budget is wise.",
            "subskill_focus": "Analytics"
        },
        {
            "world_type": "Modern",
            "industry": "Restaurant",
            "discipline": "Marketing",
            "required_level": 5,
            "scenario_title": "Brand Expansion Decision",
            "scenario_narrative": "Your restaurant is thriving. A franchise consultant suggests you could franchise your concept. A real estate agent shows you a second location. A venture capitalist offers $500,000 for 40% equity to scale quickly.",
            "choice_a_text": "Open a second location yourself ($150,000 investment)",
            "choice_a_exp_reward": 475,
            "choice_a_cash_change": -150000,
            "choice_a_reputation_change": 8,
            "choice_a_feedback": "Controlled expansion! You maintain full ownership and quality control. Growth with retained equity builds long-term wealth.",
            "choice_b_text": "Develop a franchise model ($50,000 in legal and branding)",
            "choice_b_exp_reward": 550,
            "choice_b_cash_change": -50000,
            "choice_b_reputation_change": 10,
            "choice_b_feedback": "Scalable thinking! Franchising multiplies your brand with others' capital. You've entered strategic brand marketing territory.",
            "choice_c_text": "Accept the VC investment for rapid scaling",
            "choice_c_exp_reward": 425,
            "choice_c_cash_change": 500000,
            "choice_c_reputation_change": 6,
            "choice_c_feedback": "Fast capital, but you gave up 40% ownership. Understand the trade-off between speed and equity dilution in growth financing.",
            "subskill_focus": "Brand Identity"
        }
    ]
    
    for scenario in scenarios:
        cur.execute("""
            INSERT INTO scenario_master (
                world_type, industry, discipline, required_level, scenario_title, scenario_narrative,
                choice_a_text, choice_a_exp_reward, choice_a_cash_change, choice_a_reputation_change, choice_a_feedback,
                choice_b_text, choice_b_exp_reward, choice_b_cash_change, choice_b_reputation_change, choice_b_feedback,
                choice_c_text, choice_c_exp_reward, choice_c_cash_change, choice_c_reputation_change, choice_c_feedback,
                subskill_focus
            ) VALUES (
                %(world_type)s, %(industry)s, %(discipline)s, %(required_level)s, %(scenario_title)s, %(scenario_narrative)s,
                %(choice_a_text)s, %(choice_a_exp_reward)s, %(choice_a_cash_change)s, %(choice_a_reputation_change)s, %(choice_a_feedback)s,
                %(choice_b_text)s, %(choice_b_exp_reward)s, %(choice_b_cash_change)s, %(choice_b_reputation_change)s, %(choice_b_feedback)s,
                %(choice_c_text)s, %(choice_c_exp_reward)s, %(choice_c_cash_change)s, %(choice_c_reputation_change)s, %(choice_c_feedback)s,
                %(subskill_focus)s
            )
        """, scenario)
    
    conn.commit()
    print(f"Seeded {len(scenarios)} Marketing scenarios successfully!")
    cur.close()
    conn.close()


def seed_achievements():
    """Seed the database with initial achievements."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM achievements")
    result = cur.fetchone()
    if result['count'] > 0:
        print("Achievements already seeded.")
        cur.close()
        conn.close()
        return
    
    achievements = [
        {"code": "first_scenario", "name": "First Steps", "description": "Complete your first scenario", "icon": "star", "exp_reward": 50},
        {"code": "marketing_novice", "name": "Marketing Novice", "description": "Reach Level 2 in Marketing", "icon": "megaphone", "exp_reward": 100},
        {"code": "marketing_pro", "name": "Marketing Professional", "description": "Reach Level 5 in Marketing", "icon": "bullseye", "exp_reward": 500},
        {"code": "first_1000", "name": "First Thousand", "description": "Earn your first $1,000 in profit", "icon": "cash", "exp_reward": 75},
        {"code": "reputation_builder", "name": "Reputation Builder", "description": "Reach 75 reputation", "icon": "star-fill", "exp_reward": 150},
        {"code": "perfect_choice", "name": "Perfect Choice", "description": "Make the optimal choice in a scenario", "icon": "check-circle", "exp_reward": 50},
        {"code": "five_scenarios", "name": "Getting Started", "description": "Complete 5 scenarios", "icon": "list-check", "exp_reward": 100},
        {"code": "ten_scenarios", "name": "Business Veteran", "description": "Complete 10 scenarios", "icon": "award", "exp_reward": 250},
        {"code": "stat_master", "name": "Self-Improvement", "description": "Allocate all your initial stat points", "icon": "person-up", "exp_reward": 50},
        {"code": "first_item", "name": "Collector", "description": "Purchase your first item", "icon": "bag", "exp_reward": 25},
    ]
    
    for ach in achievements:
        cur.execute("""
            INSERT INTO achievements (achievement_code, achievement_name, achievement_description, achievement_icon, exp_reward)
            VALUES (%(code)s, %(name)s, %(description)s, %(icon)s, %(exp_reward)s)
        """, ach)
    
    conn.commit()
    print(f"Seeded {len(achievements)} achievements successfully!")
    cur.close()
    conn.close()


def seed_items():
    """Seed the database with initial items."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM items")
    result = cur.fetchone()
    if result['count'] > 0:
        print("Items already seeded.")
        cur.close()
        conn.close()
        return
    
    items = [
        {"code": "coffee_boost", "name": "Premium Coffee", "description": "Boosts your focus. +10% EXP on next scenario.", "type": "consumable", "icon": "cup-hot", "price": 50, "effect_type": "exp_boost", "effect_value": 10, "consumable": True},
        {"code": "consultant_advice", "name": "Consultant Advice", "description": "Expert guidance. Reveals the best choice in a scenario.", "type": "consumable", "icon": "lightbulb", "price": 200, "effect_type": "reveal_best", "effect_value": 1, "consumable": True},
        {"code": "lucky_coin", "name": "Lucky Coin", "description": "Increases luck by 2 for the next scenario.", "type": "consumable", "icon": "coin", "price": 75, "effect_type": "luck_boost", "effect_value": 2, "consumable": True},
        {"code": "business_suit", "name": "Professional Suit", "description": "Look sharp! Permanent +1 Charisma.", "type": "equipment", "icon": "suit-club", "price": 500, "effect_type": "charisma", "effect_value": 1, "consumable": False},
        {"code": "calculator", "name": "Financial Calculator", "description": "Crunch numbers faster. Permanent +1 Intelligence.", "type": "equipment", "icon": "calculator", "price": 500, "effect_type": "intelligence", "effect_value": 1, "consumable": False},
        {"code": "negotiation_book", "name": "Art of the Deal", "description": "Master negotiation tactics. Permanent +1 Negotiation.", "type": "equipment", "icon": "book", "price": 500, "effect_type": "negotiation", "effect_value": 1, "consumable": False},
        {"code": "energy_drink", "name": "Energy Drink", "description": "Quick energy boost. +5% EXP on next scenario.", "type": "consumable", "icon": "lightning", "price": 25, "effect_type": "exp_boost", "effect_value": 5, "consumable": True},
        {"code": "market_report", "name": "Market Report", "description": "Industry insights. +15% EXP on Marketing scenarios.", "type": "consumable", "icon": "graph-up", "price": 150, "effect_type": "discipline_boost", "effect_value": 15, "consumable": True},
    ]
    
    for item in items:
        cur.execute("""
            INSERT INTO items (item_code, item_name, item_description, item_type, item_icon, purchase_price, effect_type, effect_value, is_consumable)
            VALUES (%(code)s, %(name)s, %(description)s, %(type)s, %(icon)s, %(price)s, %(effect_type)s, %(effect_value)s, %(consumable)s)
        """, item)
    
    conn.commit()
    print(f"Seeded {len(items)} items successfully!")
    cur.close()
    conn.close()


def seed_npcs():
    """Seed the database with initial NPCs."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM npcs")
    result = cur.fetchone()
    if result['count'] > 0:
        print("NPCs already seeded.")
        cur.close()
        conn.close()
        return
    
    npcs = [
        {"code": "mentor_marcus", "name": "Marcus Chen", "title": "Business Mentor", "description": "A seasoned entrepreneur who's built and sold multiple companies. Always willing to share wisdom.", "type": "mentor", "world": "Modern", "dialogue": "Ah, another aspiring business mogul! I've seen many come and go. Let me share some hard-earned wisdom with you."},
        {"code": "rival_victoria", "name": "Victoria Sterling", "title": "Rival CEO", "description": "Your main competitor. Ruthless, brilliant, and always one step ahead.", "type": "rival", "world": "Modern", "dialogue": "So, you're the new player in town. Don't get too comfortable - this market isn't big enough for both of us."},
        {"code": "partner_alex", "name": "Alex Rivera", "title": "Potential Partner", "description": "A talented operations manager looking for the right venture to join.", "type": "partner", "world": "Modern", "dialogue": "I've been watching your business grow. Maybe we could help each other out?"},
        {"code": "investor_james", "name": "James Wellington", "title": "Angel Investor", "description": "Old money with an eye for new opportunities. Has funded dozens of successful startups.", "type": "investor", "world": "Modern", "dialogue": "I'm always looking for the next big thing. Impress me with your numbers and vision."},
        {"code": "supplier_maria", "name": "Maria Santos", "title": "Premium Supplier", "description": "Runs the best supply chain in the industry. Her products are top-notch but exclusive.", "type": "vendor", "world": "Modern", "dialogue": "Quality has a price, my friend. But I assure you, it's worth every penny."},
    ]
    
    for npc in npcs:
        cur.execute("""
            INSERT INTO npcs (npc_code, npc_name, npc_title, npc_description, npc_type, world_type, dialogue_intro)
            VALUES (%(code)s, %(name)s, %(title)s, %(description)s, %(type)s, %(world)s, %(dialogue)s)
        """, npc)
    
    conn.commit()
    print(f"Seeded {len(npcs)} NPCs successfully!")
    cur.close()
    conn.close()


def seed_quests():
    """Seed the database with initial quests."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM quests")
    result = cur.fetchone()
    if result['count'] > 0:
        print("Quests already seeded.")
        cur.close()
        conn.close()
        return
    
    quests = [
        {"code": "tutorial_1", "name": "First Day on the Job", "description": "Complete your first marketing scenario to prove you have what it takes.", "type": "main", "world": "Modern", "level": 1, "exp": 100, "cash": 100, "rep": 5},
        {"code": "tutorial_2", "name": "Building Your Brand", "description": "Complete 3 marketing scenarios to establish your presence.", "type": "main", "world": "Modern", "level": 1, "exp": 250, "cash": 500, "rep": 10},
        {"code": "mentor_intro", "name": "Meet Your Mentor", "description": "Visit Marcus Chen at the Business Center and introduce yourself.", "type": "main", "world": "Modern", "level": 1, "exp": 50, "cash": 0, "rep": 5},
        {"code": "rival_encounter", "name": "Know Your Enemy", "description": "Your rival Victoria has opened a restaurant nearby. Scout the competition.", "type": "main", "world": "Modern", "level": 2, "exp": 150, "cash": 0, "rep": 5},
        {"code": "side_social", "name": "Social Butterfly", "description": "Build your social media presence to 1000 followers.", "type": "side", "world": "Modern", "level": 1, "exp": 200, "cash": 250, "rep": 8},
    ]
    
    for quest in quests:
        cur.execute("""
            INSERT INTO quests (quest_code, quest_name, quest_description, quest_type, world_type, required_level, exp_reward, cash_reward, reputation_reward)
            VALUES (%(code)s, %(name)s, %(description)s, %(type)s, %(world)s, %(level)s, %(exp)s, %(cash)s, %(rep)s)
        """, quest)
    
    conn.commit()
    print(f"Seeded {len(quests)} quests successfully!")
    cur.close()
    conn.close()


def seed_random_events():
    """Seed the database with random business events."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM random_events")
    result = cur.fetchone()
    if result['count'] > 0:
        print("Random events already seeded.")
        cur.close()
        conn.close()
        return
    
    events = [
        {"code": "health_inspection", "name": "Surprise Health Inspection", "description": "The health inspector just walked in unannounced! Your kitchen is 80% up to code, but there are a few issues.", "type": "challenge", "world": "Modern", "industry": "Restaurant",
         "choice_a_text": "Be honest about the issues and promise immediate fixes", "choice_a_cash": -500, "choice_a_rep": 5, "choice_a_feedback": "The inspector appreciates your honesty and gives you a week to fix issues.",
         "choice_b_text": "Try to distract them and hide the problems", "choice_b_cash": 0, "choice_b_rep": -10, "choice_b_feedback": "They noticed your evasiveness. You got a warning and a return visit scheduled.", "rarity": "common", "min_level": 1},
        {"code": "viral_review", "name": "Your Restaurant Goes Viral!", "description": "A famous food blogger just posted a glowing review of your restaurant. Customers are flooding in!", "type": "opportunity", "world": "Modern", "industry": "Restaurant",
         "choice_a_text": "Raise prices slightly to capitalize", "choice_a_cash": 2000, "choice_a_rep": -3, "choice_a_feedback": "Smart business move, but some regulars complained about the increase.",
         "choice_b_text": "Keep prices stable and handle the rush", "choice_b_cash": 1000, "choice_b_rep": 10, "choice_b_feedback": "Customers loved your consistency! Many became regulars.", "rarity": "rare", "min_level": 2},
        {"code": "equipment_failure", "name": "Kitchen Equipment Breakdown", "description": "Your main oven just broke down during lunch rush! You need to act fast.", "type": "crisis", "world": "Modern", "industry": "Restaurant",
         "choice_a_text": "Pay for emergency same-day repair ($800)", "choice_a_cash": -800, "choice_a_rep": 0, "choice_a_feedback": "Expensive, but you kept the kitchen running smoothly.",
         "choice_b_text": "Close the kitchen temporarily and offer discounts", "choice_b_cash": -200, "choice_b_rep": -5, "choice_b_feedback": "You saved money but lost some customer trust.", "rarity": "common", "min_level": 1},
        {"code": "celebrity_visit", "name": "Celebrity Sighting!", "description": "A local celebrity just walked into your restaurant with their entourage. All eyes are on you!", "type": "opportunity", "world": "Modern", "industry": "Restaurant",
         "choice_a_text": "Offer a complimentary meal and VIP treatment", "choice_a_cash": -300, "choice_a_rep": 15, "choice_a_feedback": "They posted about it! Free publicity worth thousands.",
         "choice_b_text": "Treat them like any other customer", "choice_b_cash": 200, "choice_b_rep": 2, "choice_b_feedback": "Professional approach. They paid and left a decent tip.", "rarity": "rare", "min_level": 3},
        {"code": "supplier_deal", "name": "Bulk Discount Opportunity", "description": "Your supplier offers a 40% discount if you buy 3 months of inventory upfront.", "type": "decision", "world": "Modern", "industry": "Restaurant",
         "choice_a_text": "Take the deal and stock up ($5,000)", "choice_a_cash": -5000, "choice_a_rep": 0, "choice_a_feedback": "You'll save money long-term if you can use it all before it expires.",
         "choice_b_text": "Decline and maintain flexible ordering", "choice_b_cash": 0, "choice_b_rep": 0, "choice_b_feedback": "Staying agile. You can adapt to menu changes more easily.", "rarity": "common", "min_level": 2},
        {"code": "staff_dispute", "name": "Employee Conflict", "description": "Two of your best employees are having a heated argument in the kitchen. Other staff are taking sides.", "type": "crisis", "world": "Modern", "industry": "Restaurant",
         "choice_a_text": "Pull them aside immediately for mediation", "choice_a_cash": 0, "choice_a_rep": 3, "choice_a_feedback": "Good leadership! You resolved it professionally.",
         "choice_b_text": "Let them work it out themselves", "choice_b_cash": 0, "choice_b_rep": -5, "choice_b_feedback": "The tension escalated. One of them called in sick the next day.", "rarity": "common", "min_level": 1},
        {"code": "weather_event", "name": "Severe Weather Warning", "description": "A major storm is predicted for tonight. You have reservations booked and staff scheduled.", "type": "decision", "world": "Modern", "industry": "Restaurant",
         "choice_a_text": "Close early and send staff home safely", "choice_a_cash": -500, "choice_a_rep": 5, "choice_a_feedback": "Your staff appreciated the concern. Loyalty increased.",
         "choice_b_text": "Stay open - customers might still come", "choice_b_cash": 300, "choice_b_rep": -2, "choice_b_feedback": "A few customers braved the storm. Staff were grumpy though.", "rarity": "common", "min_level": 1},
        {"code": "competitor_closes", "name": "Competitor Shutting Down", "description": "The restaurant across the street is closing! Their chef and equipment are available.", "type": "opportunity", "world": "Modern", "industry": "Restaurant",
         "choice_a_text": "Hire their head chef ($2,000 signing bonus)", "choice_a_cash": -2000, "choice_a_rep": 5, "choice_a_feedback": "Great acquisition! Their regulars might follow.",
         "choice_b_text": "Buy their kitchen equipment at auction ($3,000)", "choice_b_cash": -3000, "choice_b_rep": 0, "choice_b_feedback": "Quality equipment at a discount. Your kitchen just got an upgrade.", "rarity": "rare", "min_level": 3},
    ]
    
    for event in events:
        cur.execute("""
            INSERT INTO random_events (event_code, event_name, event_description, event_type, world_type, industry,
                choice_a_text, choice_a_cash_change, choice_a_reputation_change, choice_a_feedback,
                choice_b_text, choice_b_cash_change, choice_b_reputation_change, choice_b_feedback,
                rarity, min_level)
            VALUES (%(code)s, %(name)s, %(description)s, %(type)s, %(world)s, %(industry)s,
                %(choice_a_text)s, %(choice_a_cash)s, %(choice_a_rep)s, %(choice_a_feedback)s,
                %(choice_b_text)s, %(choice_b_cash)s, %(choice_b_rep)s, %(choice_b_feedback)s,
                %(rarity)s, %(min_level)s)
        """, event)
    
    conn.commit()
    print(f"Seeded {len(events)} random events successfully!")
    cur.close()
    conn.close()


def seed_rivals():
    """Seed the database with rival businesses."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM rivals")
    result = cur.fetchone()
    if result['count'] > 0:
        print("Rivals already seeded.")
        cur.close()
        conn.close()
        return
    
    rivals = [
        {"code": "bistro_bella", "name": "Marco Bellini", "business": "Bistro Bella", "description": "A charming Italian bistro known for its authentic pasta. Marco trained in Rome and has a loyal following.", "world": "Modern", "industry": "Restaurant", "difficulty": 2},
        {"code": "fusion_kings", "name": "Chef Kim", "business": "Fusion Kings", "description": "An innovative fusion restaurant that's always on the cutting edge. Chef Kim has been featured in food magazines.", "world": "Modern", "industry": "Restaurant", "difficulty": 3},
        {"code": "quick_bites", "name": "Tommy Thompson", "business": "Quick Bites Express", "description": "A fast-casual chain that competes on speed and price. Tommy's backed by investors.", "world": "Modern", "industry": "Restaurant", "difficulty": 1},
        {"code": "farm_table", "name": "Sarah Greenfield", "business": "Farm to Table Fresh", "description": "An organic restaurant focused on locally-sourced ingredients. Sarah has strong community ties.", "world": "Modern", "industry": "Restaurant", "difficulty": 2},
        {"code": "gourmet_palace", "name": "Chef Alexandre", "business": "Le Gourmet Palace", "description": "A fine dining establishment with a Michelin-star chef. The biggest competitor in the upscale market.", "world": "Modern", "industry": "Restaurant", "difficulty": 5},
    ]
    
    for rival in rivals:
        cur.execute("""
            INSERT INTO rivals (rival_code, rival_name, rival_business, rival_description, world_type, industry, difficulty_level)
            VALUES (%(code)s, %(name)s, %(business)s, %(description)s, %(world)s, %(industry)s, %(difficulty)s)
        """, rival)
    
    conn.commit()
    print(f"Seeded {len(rivals)} rivals successfully!")
    cur.close()
    conn.close()


def seed_milestones():
    """Seed the database with business milestones."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM business_milestones")
    result = cur.fetchone()
    if result['count'] > 0:
        print("Milestones already seeded.")
        cur.close()
        conn.close()
        return
    
    milestones = [
        {"code": "first_profit", "name": "In the Black", "description": "Earn your first $1,000 in profit", "type": "cash", "target": 1000, "exp": 100, "cash": 100, "icon": "piggy-bank"},
        {"code": "five_k_club", "name": "5K Club", "description": "Accumulate $5,000 in cash", "type": "cash", "target": 5000, "exp": 250, "cash": 250, "icon": "cash-stack"},
        {"code": "ten_k_milestone", "name": "Five Figures", "description": "Reach $10,000 in total cash", "type": "cash", "target": 10000, "exp": 500, "cash": 500, "icon": "wallet2"},
        {"code": "fifty_k_empire", "name": "Growing Empire", "description": "Amass $50,000 in cash", "type": "cash", "target": 50000, "exp": 1000, "cash": 1000, "icon": "building"},
        {"code": "hundred_k_mogul", "name": "Business Mogul", "description": "Achieve $100,000 in total wealth", "type": "cash", "target": 100000, "exp": 2500, "cash": 2500, "icon": "gem"},
        {"code": "rep_50", "name": "Getting Known", "description": "Reach 50 reputation", "type": "reputation", "target": 50, "exp": 100, "cash": 0, "icon": "star"},
        {"code": "rep_75", "name": "Local Legend", "description": "Achieve 75 reputation", "type": "reputation", "target": 75, "exp": 250, "cash": 250, "icon": "star-fill"},
        {"code": "rep_100", "name": "Industry Icon", "description": "Max out your reputation at 100", "type": "reputation", "target": 100, "exp": 1000, "cash": 1000, "icon": "trophy"},
        {"code": "scenario_10", "name": "Decision Maker", "description": "Complete 10 business scenarios", "type": "scenarios", "target": 10, "exp": 200, "cash": 100, "icon": "check-circle"},
        {"code": "scenario_25", "name": "Seasoned Veteran", "description": "Complete 25 business scenarios", "type": "scenarios", "target": 25, "exp": 500, "cash": 250, "icon": "check-all"},
        {"code": "level_5", "name": "Skilled Professional", "description": "Reach Level 5 in any discipline", "type": "level", "target": 5, "exp": 500, "cash": 250, "icon": "graph-up"},
        {"code": "level_10", "name": "Master of the Trade", "description": "Reach Level 10 in any discipline", "type": "level", "target": 10, "exp": 2000, "cash": 1000, "icon": "mortarboard"},
    ]
    
    for milestone in milestones:
        cur.execute("""
            INSERT INTO business_milestones (milestone_code, milestone_name, milestone_description, milestone_type, target_value, exp_reward, cash_reward, badge_icon)
            VALUES (%(code)s, %(name)s, %(description)s, %(type)s, %(target)s, %(exp)s, %(cash)s, %(icon)s)
        """, milestone)
    
    conn.commit()
    print(f"Seeded {len(milestones)} milestones successfully!")
    cur.close()
    conn.close()


def seed_weekly_challenges():
    """Seed the database with weekly challenges."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM weekly_challenges")
    result = cur.fetchone()
    if result['count'] > 0:
        print("Weekly challenges already seeded.")
        cur.close()
        conn.close()
        return
    
    from datetime import date, timedelta
    today = date.today()
    week_end = today + timedelta(days=7)
    
    challenges = [
        {"code": "weekly_scenarios", "name": "Weekly Warrior", "description": "Complete 5 scenarios this week", "type": "scenarios_completed", "target": 5, "exp": 300, "cash": 500},
        {"code": "weekly_exp", "name": "Knowledge Seeker", "description": "Earn 500 EXP this week", "type": "exp_earned", "target": 500, "exp": 200, "cash": 300},
        {"code": "weekly_profit", "name": "Profit Hunter", "description": "Earn $2,000 in profit this week", "type": "cash_earned", "target": 2000, "exp": 250, "cash": 400},
    ]
    
    for challenge in challenges:
        challenge['start'] = today
        challenge['end'] = week_end
        cur.execute("""
            INSERT INTO weekly_challenges (challenge_code, challenge_name, challenge_description, challenge_type, target_value, exp_reward, cash_reward, start_date, end_date)
            VALUES (%(code)s, %(name)s, %(description)s, %(type)s, %(target)s, %(exp)s, %(cash)s, %(start)s, %(end)s)
        """, challenge)
    
    conn.commit()
    print(f"Seeded {len(challenges)} weekly challenges successfully!")
    cur.close()
    conn.close()


def seed_avatar_options():
    """Seed the database with avatar customization options."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM avatar_options")
    result = cur.fetchone()
    if result['count'] > 0:
        print("Avatar options already seeded.")
        cur.close()
        conn.close()
        return
    
    options = [
        {"type": "hair", "code": "hair_default", "name": "Classic", "cost": 0, "level": 1},
        {"type": "hair", "code": "hair_slick", "name": "Slick Back", "cost": 100, "level": 1},
        {"type": "hair", "code": "hair_curly", "name": "Curly", "cost": 100, "level": 1},
        {"type": "hair", "code": "hair_mohawk", "name": "Mohawk", "cost": 250, "level": 3},
        {"type": "hair", "code": "hair_bald", "name": "Clean Shaven", "cost": 50, "level": 1},
        {"type": "outfit", "code": "outfit_default", "name": "Business Casual", "cost": 0, "level": 1},
        {"type": "outfit", "code": "outfit_suit", "name": "Power Suit", "cost": 500, "level": 2},
        {"type": "outfit", "code": "outfit_chef", "name": "Chef's Whites", "cost": 300, "level": 2},
        {"type": "outfit", "code": "outfit_casual", "name": "Startup Casual", "cost": 200, "level": 1},
        {"type": "outfit", "code": "outfit_luxury", "name": "Designer Luxury", "cost": 2000, "level": 5},
        {"type": "accessory", "code": "acc_none", "name": "None", "cost": 0, "level": 1},
        {"type": "accessory", "code": "acc_glasses", "name": "Reading Glasses", "cost": 100, "level": 1},
        {"type": "accessory", "code": "acc_sunglasses", "name": "Sunglasses", "cost": 200, "level": 2},
        {"type": "accessory", "code": "acc_watch", "name": "Luxury Watch", "cost": 1000, "level": 4},
        {"type": "accessory", "code": "acc_hat", "name": "Chef's Hat", "cost": 150, "level": 2},
        {"type": "color", "code": "color_blue", "name": "Professional Blue", "cost": 0, "level": 1},
        {"type": "color", "code": "color_red", "name": "Power Red", "cost": 100, "level": 1},
        {"type": "color", "code": "color_green", "name": "Money Green", "cost": 100, "level": 1},
        {"type": "color", "code": "color_purple", "name": "Royal Purple", "cost": 250, "level": 3},
        {"type": "color", "code": "color_gold", "name": "Golden Success", "cost": 500, "level": 5},
    ]
    
    for opt in options:
        cur.execute("""
            INSERT INTO avatar_options (option_type, option_code, option_name, unlock_cost, unlock_level)
            VALUES (%(type)s, %(code)s, %(name)s, %(cost)s, %(level)s)
        """, opt)
    
    conn.commit()
    print(f"Seeded {len(options)} avatar options successfully!")
    cur.close()
    conn.close()


def seed_fantasy_scenarios():
    """Seed Fantasy World scenarios for tavern industry."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM scenario_master WHERE world_type = 'Fantasy'")
    result = cur.fetchone()
    if result['count'] > 0:
        print("Fantasy scenarios already seeded.")
        cur.close()
        conn.close()
        return
    
    scenarios = [
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Marketing", "required_level": 1,
         "scenario_title": "The Tavern Sign", "scenario_narrative": "Your tavern needs a sign to attract adventurers. A dwarf craftsman offers an iron sign, while an elf artist proposes a magical glowing sign.",
         "choice_a_text": "Commission the iron sign (50 gold)", "choice_a_exp_reward": 75, "choice_a_cash_change": -50, "choice_a_reputation_change": 2,
         "choice_a_feedback": "Sturdy and reliable! Dwarven craftsmanship never disappoints.",
         "choice_b_text": "Order the magical glowing sign (150 gold)", "choice_b_exp_reward": 110, "choice_b_cash_change": -150, "choice_b_reputation_change": 8,
         "choice_b_feedback": "Brilliant! Adventurers from leagues away can spot your tavern now.",
         "choice_c_text": "Paint your own sign (10 gold for supplies)", "choice_c_exp_reward": 60, "choice_c_cash_change": -10, "choice_c_reputation_change": 0,
         "choice_c_feedback": "Budget-friendly, but it shows. Maybe invest in better marketing later.", "subskill_focus": "Brand Identity"},
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Marketing", "required_level": 1,
         "scenario_title": "Bard for Hire", "scenario_narrative": "A traveling bard offers to perform at your tavern. Entertainment could draw crowds, but bards require payment and lodging.",
         "choice_a_text": "Hire the bard for a week (100 gold + room)", "choice_a_exp_reward": 100, "choice_a_cash_change": -100, "choice_a_reputation_change": 10,
         "choice_a_feedback": "The bard's tales of heroes brought adventurers seeking glory!",
         "choice_b_text": "Offer performance for tips only", "choice_b_exp_reward": 80, "choice_b_cash_change": 0, "choice_b_reputation_change": 5,
         "choice_b_feedback": "The bard agreed but put in minimal effort. Still better than silence.",
         "choice_c_text": "Decline - focus on food and drink", "choice_c_exp_reward": 50, "choice_c_cash_change": 0, "choice_c_reputation_change": 0,
         "choice_c_feedback": "Your tavern remains quiet. Some patrons prefer the peace.", "subskill_focus": "Campaign Planning"},
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Marketing", "required_level": 2,
         "scenario_title": "The Adventurer's Guild", "scenario_narrative": "The local Adventurer's Guild is looking for an official tavern partner. Competition is fierce with two other taverns bidding.",
         "choice_a_text": "Offer a 20% discount to guild members", "choice_a_exp_reward": 150, "choice_a_cash_change": 0, "choice_a_reputation_change": 15,
         "choice_a_feedback": "Deal secured! Guild members flood in, and word spreads quickly.",
         "choice_b_text": "Promise to host guild meetings with free mead", "choice_b_exp_reward": 175, "choice_b_cash_change": -200, "choice_b_reputation_change": 12,
         "choice_b_feedback": "The guild loves the hospitality! This could be a long-term partnership.",
         "choice_c_text": "Decline - don't want to be tied to one faction", "choice_c_exp_reward": 75, "choice_c_cash_change": 0, "choice_c_reputation_change": -5,
         "choice_c_feedback": "The guild chose a competitor. Some adventurers avoid your tavern now.", "subskill_focus": "Partnership Marketing"},
    ]
    
    for scenario in scenarios:
        cur.execute("""
            INSERT INTO scenario_master (world_type, industry, discipline, required_level, scenario_title, scenario_narrative,
                choice_a_text, choice_a_exp_reward, choice_a_cash_change, choice_a_reputation_change, choice_a_feedback,
                choice_b_text, choice_b_exp_reward, choice_b_cash_change, choice_b_reputation_change, choice_b_feedback,
                choice_c_text, choice_c_exp_reward, choice_c_cash_change, choice_c_reputation_change, choice_c_feedback,
                subskill_focus)
            VALUES (%(world_type)s, %(industry)s, %(discipline)s, %(required_level)s, %(scenario_title)s, %(scenario_narrative)s,
                %(choice_a_text)s, %(choice_a_exp_reward)s, %(choice_a_cash_change)s, %(choice_a_reputation_change)s, %(choice_a_feedback)s,
                %(choice_b_text)s, %(choice_b_exp_reward)s, %(choice_b_cash_change)s, %(choice_b_reputation_change)s, %(choice_b_feedback)s,
                %(choice_c_text)s, %(choice_c_exp_reward)s, %(choice_c_cash_change)s, %(choice_c_reputation_change)s, %(choice_c_feedback)s,
                %(subskill_focus)s)
        """, scenario)
    
    conn.commit()
    print(f"Seeded {len(scenarios)} Fantasy scenarios successfully!")
    cur.close()
    conn.close()


def seed_industrial_scenarios():
    """Seed Industrial Age scenarios for steel mill, textile factory, and railroad industries."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM scenario_master WHERE world_type = 'Industrial'")
    result = cur.fetchone()
    if result['count'] > 0:
        print("Industrial scenarios already seeded.")
        cur.close()
        conn.close()
        return
    
    scenarios = [
        {"world_type": "Industrial", "industry": "Steel Mill", "discipline": "Operations", "required_level": 1,
         "scenario_title": "The Bessemer Decision", "scenario_narrative": "A salesman offers the revolutionary Bessemer process equipment. It promises faster steel production but requires significant capital and worker retraining.",
         "choice_a_text": "Invest in the Bessemer converter ($5,000)", "choice_a_exp_reward": 120, "choice_a_cash_change": -5000, "choice_a_reputation_change": 15,
         "choice_a_feedback": "Brilliant! Your mill now produces steel 10x faster than competitors using traditional methods.",
         "choice_b_text": "Wait and observe competitors first", "choice_b_exp_reward": 60, "choice_b_cash_change": 0, "choice_b_reputation_change": 0,
         "choice_b_feedback": "Cautious, but competitors are racing ahead. You'll need to decide soon.",
         "choice_c_text": "Stick with puddling furnaces (traditional)", "choice_c_exp_reward": 40, "choice_c_cash_change": 0, "choice_c_reputation_change": -5,
         "choice_c_feedback": "Your workers know the old ways, but the industry is changing rapidly.", "subskill_focus": "Process Optimization"},
        
        {"world_type": "Industrial", "industry": "Steel Mill", "discipline": "Human Resources", "required_level": 1,
         "scenario_title": "The Labor Dispute", "scenario_narrative": "Furnace workers demand shorter 10-hour shifts instead of the current 12 hours. They threaten to strike during peak production season.",
         "choice_a_text": "Negotiate 11-hour shifts with meal breaks", "choice_a_exp_reward": 100, "choice_a_cash_change": -200, "choice_a_reputation_change": 10,
         "choice_a_feedback": "A reasonable compromise! Workers are satisfied and productivity remains strong.",
         "choice_b_text": "Refuse and prepare to hire replacements", "choice_b_exp_reward": 50, "choice_b_cash_change": 500, "choice_b_reputation_change": -15,
         "choice_b_feedback": "The strike lasted two weeks. Production suffered but you maintained control.",
         "choice_c_text": "Grant 10-hour shifts with slight wage reduction", "choice_c_exp_reward": 85, "choice_c_cash_change": 100, "choice_c_reputation_change": 5,
         "choice_c_feedback": "Workers accepted the trade-off. Morale improved somewhat.", "subskill_focus": "Conflict Resolution"},
        
        {"world_type": "Industrial", "industry": "Steel Mill", "discipline": "Finance", "required_level": 2,
         "scenario_title": "Railroad Contract Bid", "scenario_narrative": "The Pennsylvania Railroad needs 10,000 tons of rail steel. Winning this contract would establish your mill, but you'll need to secure capital to expand capacity.",
         "choice_a_text": "Bid aggressively and seek bank financing", "choice_a_exp_reward": 150, "choice_a_cash_change": 8000, "choice_a_reputation_change": 20,
         "choice_a_feedback": "Contract secured! Your mill is now a major supplier to the railroad industry.",
         "choice_b_text": "Bid conservatively within current capacity", "choice_b_exp_reward": 90, "choice_b_cash_change": 2000, "choice_b_reputation_change": 5,
         "choice_b_feedback": "You won a smaller portion of the contract. Safe but limited growth.",
         "choice_c_text": "Partner with a larger mill to share the contract", "choice_c_exp_reward": 110, "choice_c_cash_change": 4000, "choice_c_reputation_change": 12,
         "choice_c_feedback": "The partnership worked well. You gained experience and contacts.", "subskill_focus": "Investment Analysis"},
        
        {"world_type": "Industrial", "industry": "Textile Factory", "discipline": "Operations", "required_level": 1,
         "scenario_title": "The Power Loom Upgrade", "scenario_narrative": "Your hand looms are reliable but slow. Power looms could triple output, but they require steam engine installation and new worker training.",
         "choice_a_text": "Install power looms throughout ($3,000)", "choice_a_exp_reward": 110, "choice_a_cash_change": -3000, "choice_a_reputation_change": 10,
         "choice_a_feedback": "Production soared! You can now compete with the largest mills in New England.",
         "choice_b_text": "Upgrade half the factory first", "choice_b_exp_reward": 80, "choice_b_cash_change": -1500, "choice_b_reputation_change": 5,
         "choice_b_feedback": "A measured approach. You can observe results before full commitment.",
         "choice_c_text": "Invest in faster hand looms instead", "choice_c_exp_reward": 50, "choice_c_cash_change": -500, "choice_c_reputation_change": 0,
         "choice_c_feedback": "Marginal improvement. Your competitors are pulling ahead.", "subskill_focus": "Process Optimization"},
        
        {"world_type": "Industrial", "industry": "Textile Factory", "discipline": "Human Resources", "required_level": 1,
         "scenario_title": "The Child Labor Question", "scenario_narrative": "Many mills employ children for their small fingers and low wages. A reformer is publicizing conditions. Your factory currently employs workers of all ages.",
         "choice_a_text": "Transition to adult workers only, offer fair wages", "choice_a_exp_reward": 130, "choice_a_cash_change": -800, "choice_a_reputation_change": 25,
         "choice_a_feedback": "Your reputation as a fair employer attracts skilled workers from competitors.",
         "choice_b_text": "Establish a factory school for young workers", "choice_b_exp_reward": 100, "choice_b_cash_change": -400, "choice_b_reputation_change": 15,
         "choice_b_feedback": "A progressive compromise that garners public approval.",
         "choice_c_text": "Continue current practices quietly", "choice_c_exp_reward": 40, "choice_c_cash_change": 200, "choice_c_reputation_change": -10,
         "choice_c_feedback": "Profits remain high, but the reformer's article damaged your reputation.", "subskill_focus": "Team Building"},
        
        {"world_type": "Industrial", "industry": "Textile Factory", "discipline": "Marketing", "required_level": 2,
         "scenario_title": "The Department Store Opportunity", "scenario_narrative": "A new department store in Philadelphia wants exclusive textile patterns. This could establish your brand but requires design investment.",
         "choice_a_text": "Create exclusive patterns and brand partnership", "choice_a_exp_reward": 140, "choice_a_cash_change": 1500, "choice_a_reputation_change": 18,
         "choice_a_feedback": "Your patterns are the talk of high society! Orders are flooding in.",
         "choice_b_text": "Offer standard patterns at discount", "choice_b_exp_reward": 70, "choice_b_cash_change": 600, "choice_b_reputation_change": 3,
         "choice_b_feedback": "They accepted, but you're one of many suppliers.",
         "choice_c_text": "Decline - focus on wholesale markets", "choice_c_exp_reward": 50, "choice_c_cash_change": 0, "choice_c_reputation_change": 0,
         "choice_c_feedback": "Wholesale is reliable but the retail opportunity passed you by.", "subskill_focus": "Brand Identity"},
        
        {"world_type": "Industrial", "industry": "Railroad", "discipline": "Strategy", "required_level": 1,
         "scenario_title": "The Route Survey", "scenario_narrative": "Your railroad needs to connect two cities. The mountain route is shorter but requires expensive tunneling. The valley route is longer but easier to build.",
         "choice_a_text": "Take the mountain route (tunnel investment)", "choice_a_exp_reward": 130, "choice_a_cash_change": -6000, "choice_a_reputation_change": 20,
         "choice_a_feedback": "The shorter route attracts more passengers and freight. Competitors are envious!",
         "choice_b_text": "Build the valley route (longer but cheaper)", "choice_b_exp_reward": 80, "choice_b_cash_change": -2000, "choice_b_reputation_change": 5,
         "choice_b_feedback": "The route works but the longer journey time limits your competitive advantage.",
         "choice_c_text": "Survey both options further (delay)", "choice_c_exp_reward": 50, "choice_c_cash_change": -500, "choice_c_reputation_change": -5,
         "choice_c_feedback": "A competitor started building while you deliberated. Time is money!", "subskill_focus": "Long-term Planning"},
        
        {"world_type": "Industrial", "industry": "Railroad", "discipline": "Finance", "required_level": 1,
         "scenario_title": "The Stock Offering", "scenario_narrative": "To fund expansion, you need capital. You can issue stock, seek bank loans, or find wealthy investors. Each has different implications for control and cost.",
         "choice_a_text": "Issue public stock (dilute ownership)", "choice_a_exp_reward": 100, "choice_a_cash_change": 10000, "choice_a_reputation_change": 15,
         "choice_a_feedback": "Capital secured! You now have a board of directors to answer to.",
         "choice_b_text": "Secure bank loans (keep full control)", "choice_b_exp_reward": 90, "choice_b_cash_change": 5000, "choice_b_reputation_change": 8,
         "choice_b_feedback": "Full control maintained, but the interest payments are significant.",
         "choice_c_text": "Find a wealthy partner (share control, share risk)", "choice_c_exp_reward": 110, "choice_c_cash_change": 7000, "choice_c_reputation_change": 12,
         "choice_c_feedback": "Your new partner brings both capital and valuable political connections.", "subskill_focus": "Investment Analysis"},
        
        {"world_type": "Industrial", "industry": "Railroad", "discipline": "Operations", "required_level": 2,
         "scenario_title": "The Gauge Question", "scenario_narrative": "Your railroad uses a different track gauge than connecting lines. Passengers and freight must transfer at junctions, causing delays and costs.",
         "choice_a_text": "Convert to standard gauge (major expense)", "choice_a_exp_reward": 150, "choice_a_cash_change": -8000, "choice_a_reputation_change": 25,
         "choice_a_feedback": "Seamless connections! Shippers and passengers flock to your efficient line.",
         "choice_b_text": "Build transfer facilities at junctions", "choice_b_exp_reward": 80, "choice_b_cash_change": -2000, "choice_b_reputation_change": 5,
         "choice_b_feedback": "Workable but inefficient. The transfer delays remain a complaint.",
         "choice_c_text": "Lobby for your gauge as the new standard", "choice_c_exp_reward": 60, "choice_c_cash_change": -1000, "choice_c_reputation_change": -5,
         "choice_c_feedback": "The lobbying failed. Congress chose the other gauge as standard.", "subskill_focus": "Supply Chain"},
        
        {"world_type": "Industrial", "industry": "Railroad", "discipline": "Legal", "required_level": 2,
         "scenario_title": "The Land Grant Proposal", "scenario_narrative": "The federal government offers land grants for railroads expanding westward. The terms are complex and require navigating political relationships.",
         "choice_a_text": "Pursue the land grant aggressively", "choice_a_exp_reward": 160, "choice_a_cash_change": 15000, "choice_a_reputation_change": 20,
         "choice_a_feedback": "Success! Thousands of acres of valuable land are now yours to develop or sell.",
         "choice_b_text": "Apply cautiously with proper legal review", "choice_b_exp_reward": 120, "choice_b_cash_change": 8000, "choice_b_reputation_change": 15,
         "choice_b_feedback": "A smaller grant, but with clear title and no legal complications.",
         "choice_c_text": "Avoid government entanglements", "choice_c_exp_reward": 50, "choice_c_cash_change": 0, "choice_c_reputation_change": 0,
         "choice_c_feedback": "Your competitors are now major landowners. You missed an opportunity.", "subskill_focus": "Contract Law"},
    ]
    
    for scenario in scenarios:
        cur.execute("""
            INSERT INTO scenario_master (world_type, industry, discipline, required_level, scenario_title, scenario_narrative,
                choice_a_text, choice_a_exp_reward, choice_a_cash_change, choice_a_reputation_change, choice_a_feedback,
                choice_b_text, choice_b_exp_reward, choice_b_cash_change, choice_b_reputation_change, choice_b_feedback,
                choice_c_text, choice_c_exp_reward, choice_c_cash_change, choice_c_reputation_change, choice_c_feedback,
                subskill_focus)
            VALUES (%(world_type)s, %(industry)s, %(discipline)s, %(required_level)s, %(scenario_title)s, %(scenario_narrative)s,
                %(choice_a_text)s, %(choice_a_exp_reward)s, %(choice_a_cash_change)s, %(choice_a_reputation_change)s, %(choice_a_feedback)s,
                %(choice_b_text)s, %(choice_b_exp_reward)s, %(choice_b_cash_change)s, %(choice_b_reputation_change)s, %(choice_b_feedback)s,
                %(choice_c_text)s, %(choice_c_exp_reward)s, %(choice_c_cash_change)s, %(choice_c_reputation_change)s, %(choice_c_feedback)s,
                %(subskill_focus)s)
        """, scenario)
    
    conn.commit()
    print(f"Seeded {len(scenarios)} Industrial scenarios successfully!")
    cur.close()
    conn.close()


def seed_industrial_events():
    """Seed random events for Industrial Age world."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM random_events WHERE world_type = 'Industrial'")
    result = cur.fetchone()
    if result['count'] > 0:
        print("Industrial events already seeded.")
        cur.close()
        conn.close()
        return
    
    events = [
        {"code": "machinery_breakdown", "name": "Machinery Breakdown", "type": "crisis", "world": "Industrial", "industry": None,
         "description": "A critical piece of machinery has broken down! Production is halted until repairs are made.",
         "choice_a_text": "Rush repair with overtime pay", "choice_a_cash": -500, "choice_a_rep": 5, 
         "choice_a_feedback": "Expensive but production resumed quickly. Workers appreciate the quick action.",
         "choice_b_text": "Wait for regular repair schedule", "choice_b_cash": 0, "choice_b_rep": -10,
         "choice_b_feedback": "Production delays hurt your reputation with clients.", "rarity": "common", "min_level": 1},
        {"code": "coal_shortage", "name": "Coal Shortage", "type": "crisis", "world": "Industrial", "industry": None,
         "description": "A mine collapse has caused a regional coal shortage. Your operations depend on a steady supply.",
         "choice_a_text": "Secure emergency coal at premium prices", "choice_a_cash": -800, "choice_a_rep": 5,
         "choice_a_feedback": "Operations continue smoothly. Your reliability is noted by customers.",
         "choice_b_text": "Reduce operations until supply normalizes", "choice_b_cash": -300, "choice_b_rep": -5,
         "choice_b_feedback": "Slower production, but you weathered the shortage.", "rarity": "uncommon", "min_level": 1},
        {"code": "inventors_proposal", "name": "Inventor's Proposal", "type": "opportunity", "world": "Industrial", "industry": None,
         "description": "A young inventor presents a patent for improved efficiency. He wants capital in exchange for exclusive rights.",
         "choice_a_text": "Invest in the patent ($1000)", "choice_a_cash": -1000, "choice_a_rep": 15,
         "choice_a_feedback": "The invention works! Your factory becomes more efficient.",
         "choice_b_text": "Politely decline", "choice_b_cash": 0, "choice_b_rep": 0,
         "choice_b_feedback": "A competitor bought the patent instead. Their loss is your caution.", "rarity": "rare", "min_level": 2},
        {"code": "workers_parade", "name": "Workers' Parade", "type": "decision", "world": "Industrial", "industry": None,
         "description": "Workers are organizing a parade for the new Labor Day holiday. They want you to close the factory for the day.",
         "choice_a_text": "Close for the day with pay", "choice_a_cash": -200, "choice_a_rep": 20,
         "choice_a_feedback": "Worker morale soars! You're seen as a fair employer.",
         "choice_b_text": "Keep factory open (voluntary attendance)", "choice_b_cash": 100, "choice_b_rep": -5,
         "choice_b_feedback": "Production continued but workers grumbled.", "rarity": "common", "min_level": 1},
        {"code": "govt_inspection", "name": "Government Inspection", "type": "crisis", "world": "Industrial", "industry": None,
         "description": "A government inspector has arrived unannounced to examine working conditions and safety measures.",
         "choice_a_text": "Cooperate fully and make improvements", "choice_a_cash": -600, "choice_a_rep": 15,
         "choice_a_feedback": "The inspector was impressed with your cooperation and improvements.",
         "choice_b_text": "Show only the best areas of the facility", "choice_b_cash": -100, "choice_b_rep": -10,
         "choice_b_feedback": "The inspector noticed your evasiveness and scheduled a return visit.", "rarity": "uncommon", "min_level": 1},
    ]
    
    for event in events:
        cur.execute("""
            INSERT INTO random_events (event_code, event_name, event_description, event_type, world_type, industry,
                choice_a_text, choice_a_cash_change, choice_a_reputation_change, choice_a_feedback,
                choice_b_text, choice_b_cash_change, choice_b_reputation_change, choice_b_feedback,
                rarity, min_level)
            VALUES (%(code)s, %(name)s, %(description)s, %(type)s, %(world)s, %(industry)s,
                %(choice_a_text)s, %(choice_a_cash)s, %(choice_a_rep)s, %(choice_a_feedback)s,
                %(choice_b_text)s, %(choice_b_cash)s, %(choice_b_rep)s, %(choice_b_feedback)s,
                %(rarity)s, %(min_level)s)
        """, event)
    
    conn.commit()
    print(f"Seeded {len(events)} Industrial random events successfully!")
    cur.close()
    conn.close()


def seed_industrial_rivals():
    """Seed rival businesses for Industrial Age world."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM rivals WHERE world_type = 'Industrial'")
    result = cur.fetchone()
    if result['count'] > 0:
        print("Industrial rivals already seeded.")
        cur.close()
        conn.close()
        return
    
    rivals = [
        {"code": "carnegie_steel", "name": "Andrew Carnegie", "business": "Carnegie Steel Works", "world": "Industrial", "industry": "Steel Mill",
         "description": "The largest and most efficient steel operation in the region.", "difficulty": 5},
        {"code": "allegheny_iron", "name": "Henry Frick", "business": "Allegheny Iron & Coke", "world": "Industrial", "industry": "Steel Mill",
         "description": "A vertically integrated competitor controlling ore and fuel sources.", "difficulty": 4},
        {"code": "lowell_mills", "name": "Francis Lowell Jr.", "business": "Lowell Textile Mills", "world": "Industrial", "industry": "Textile Factory",
         "description": "Pioneering factory with the famous 'Lowell System' of worker management.", "difficulty": 4},
        {"code": "manchester_cotton", "name": "Lord Manchester", "business": "Manchester Cotton Works", "world": "Industrial", "industry": "Textile Factory",
         "description": "British-backed operation with access to imported cotton and machinery.", "difficulty": 3},
        {"code": "vanderbilt_rail", "name": "Cornelius Vanderbilt", "business": "Vanderbilt Railways", "world": "Industrial", "industry": "Railroad",
         "description": "The commodore's expanding railroad empire threatens all competitors.", "difficulty": 5},
    ]
    
    for rival in rivals:
        cur.execute("""
            INSERT INTO rivals (rival_code, rival_name, rival_business, rival_description, world_type, industry, difficulty_level)
            VALUES (%(code)s, %(name)s, %(business)s, %(description)s, %(world)s, %(industry)s, %(difficulty)s)
        """, rival)
    
    conn.commit()
    print(f"Seeded {len(rivals)} Industrial rivals successfully!")
    cur.close()
    conn.close()


def seed_modern_restaurant_full():
    """Seed complete scenarios for Modern/Restaurant covering all 6 disciplines."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM scenario_master WHERE world_type = 'Modern' AND industry = 'Restaurant' AND discipline = 'Finance'")
    result = cur.fetchone()
    if result['count'] > 0:
        print("Modern Restaurant full disciplines already seeded.")
        cur.close()
        conn.close()
        return
    
    scenarios = [
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Finance", "required_level": 1,
         "scenario_title": "Your First Budget", "scenario_narrative": "You need to create a monthly budget for your restaurant. Your accountant suggests tracking food costs, labor, rent, and utilities separately.",
         "choice_a_text": "Use a simple spreadsheet to track everything", "choice_a_exp_reward": 75, "choice_a_cash_change": 0, "choice_a_reputation_change": 0,
         "choice_a_feedback": "Spreadsheets work for starting out, but they're prone to errors. Consider upgrading as you grow.",
         "choice_b_text": "Invest in restaurant accounting software ($50/month)", "choice_b_exp_reward": 100, "choice_b_cash_change": -50, "choice_b_reputation_change": 2,
         "choice_b_feedback": "Smart investment! Proper tools save time and reduce costly errors. You've learned the value of financial systems.",
         "choice_c_text": "Hire a part-time bookkeeper ($500/month)", "choice_c_exp_reward": 90, "choice_c_cash_change": -500, "choice_c_reputation_change": 3,
         "choice_c_feedback": "Professional help is valuable but expensive at this stage. Learn the basics yourself first.", "subskill_focus": "Budgeting"},
        
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Finance", "required_level": 1,
         "scenario_title": "The Food Cost Challenge", "scenario_narrative": "Your food cost percentage is running at 38%. Industry standard is 28-32%. You're losing money on every plate served.",
         "choice_a_text": "Reduce portion sizes by 15%", "choice_a_exp_reward": 70, "choice_a_cash_change": 200, "choice_a_reputation_change": -5,
         "choice_a_feedback": "Customers noticed smaller portions. Some left negative reviews. Cost cutting has limits.",
         "choice_b_text": "Renegotiate with suppliers and reduce waste", "choice_b_exp_reward": 120, "choice_b_cash_change": 300, "choice_b_reputation_change": 3,
         "choice_b_feedback": "Excellent! Addressing root causes is better than cutting quality. You've learned cost optimization.",
         "choice_c_text": "Raise menu prices by 10%", "choice_c_exp_reward": 85, "choice_c_cash_change": 150, "choice_c_reputation_change": -2,
         "choice_c_feedback": "Prices went up but so did expectations. Balance is key in pricing strategy.", "subskill_focus": "Cost Analysis"},
        
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Finance", "required_level": 2,
         "scenario_title": "The Equipment Loan Decision", "scenario_narrative": "Your kitchen equipment needs upgrading. A bank offers a $20,000 loan at 8% for 5 years. Monthly payments would be $405.",
         "choice_a_text": "Take the full loan amount", "choice_a_exp_reward": 100, "choice_a_cash_change": 20000, "choice_a_reputation_change": 5,
         "choice_a_feedback": "New equipment improved efficiency and food quality. Good investment if managed well.",
         "choice_b_text": "Lease equipment instead ($600/month)", "choice_b_exp_reward": 110, "choice_b_cash_change": 0, "choice_b_reputation_change": 3,
         "choice_b_feedback": "Leasing preserves capital and includes maintenance. Smart cash flow management!",
         "choice_c_text": "Buy used equipment with cash savings", "choice_c_exp_reward": 80, "choice_c_cash_change": -5000, "choice_c_reputation_change": 0,
         "choice_c_feedback": "Avoided debt but older equipment may need repairs soon. Consider total cost of ownership.", "subskill_focus": "Investment Analysis"},
        
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Operations", "required_level": 1,
         "scenario_title": "Kitchen Flow Setup", "scenario_narrative": "Your kitchen layout is causing bottlenecks. Chefs are bumping into each other during rush hour, slowing down orders.",
         "choice_a_text": "Reorganize to create designated stations", "choice_a_exp_reward": 110, "choice_a_cash_change": -200, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Station-based workflow reduced ticket times by 30%! You've learned about process optimization.",
         "choice_b_text": "Add another prep table ($800)", "choice_b_exp_reward": 75, "choice_b_cash_change": -800, "choice_b_reputation_change": 2,
         "choice_b_feedback": "More space helps but doesn't address the core flow issue. Think systems, not just equipment.",
         "choice_c_text": "Stagger cooking start times", "choice_c_exp_reward": 90, "choice_c_cash_change": 0, "choice_c_reputation_change": 3,
         "choice_c_feedback": "Good temporary solution! Process timing is a key operations concept.", "subskill_focus": "Process Optimization"},
        
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Operations", "required_level": 1,
         "scenario_title": "Inventory Management Crisis", "scenario_narrative": "You're throwing away $300 of spoiled produce weekly. Your walk-in refrigerator organization is chaotic.",
         "choice_a_text": "Implement FIFO (First In, First Out) system", "choice_a_exp_reward": 120, "choice_a_cash_change": 200, "choice_a_reputation_change": 3,
         "choice_a_feedback": "FIFO reduced waste by 60%! This inventory principle applies across all industries.",
         "choice_b_text": "Order smaller quantities more frequently", "choice_b_exp_reward": 90, "choice_b_cash_change": 100, "choice_b_reputation_change": 2,
         "choice_b_feedback": "Less waste but higher ordering costs. Consider the full supply chain equation.",
         "choice_c_text": "Create a daily prep checklist with par levels", "choice_c_exp_reward": 100, "choice_c_cash_change": 150, "choice_c_reputation_change": 3,
         "choice_c_feedback": "Systematic approach to inventory! Par levels are fundamental to operations management.", "subskill_focus": "Supply Chain"},
        
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Operations", "required_level": 2,
         "scenario_title": "The Supplier Dilemma", "scenario_narrative": "Your main produce supplier raised prices 15%. A new supplier offers lower prices but you haven't worked with them before.",
         "choice_a_text": "Switch to the new supplier immediately", "choice_a_exp_reward": 70, "choice_a_cash_change": 400, "choice_a_reputation_change": -3,
         "choice_a_feedback": "Quality issues emerged. Vetting suppliers before switching is crucial in operations.",
         "choice_b_text": "Test the new supplier with a small order first", "choice_b_exp_reward": 130, "choice_b_cash_change": 200, "choice_b_reputation_change": 3,
         "choice_b_feedback": "Smart risk management! Pilot testing before full commitment is a best practice.",
         "choice_c_text": "Negotiate with current supplier using the competing quote", "choice_c_exp_reward": 110, "choice_c_cash_change": 250, "choice_c_reputation_change": 4,
         "choice_c_feedback": "Excellent negotiation! Competitive quotes are powerful leverage in supplier relationships.", "subskill_focus": "Supply Chain"},
        
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Human Resources", "required_level": 1,
         "scenario_title": "Your First Hire", "scenario_narrative": "You need to hire a line cook. Three candidates applied: one with experience but higher salary demands, one new but eager, and one with mixed reviews from previous jobs.",
         "choice_a_text": "Hire the experienced cook at higher pay", "choice_a_exp_reward": 90, "choice_a_cash_change": -500, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Experience speeds up training but costs more. Consider ROI when hiring.",
         "choice_b_text": "Hire the eager newcomer and train them yourself", "choice_b_exp_reward": 110, "choice_b_cash_change": -100, "choice_b_reputation_change": 3,
         "choice_b_feedback": "Training takes time but builds loyalty. Investing in people pays long-term dividends.",
         "choice_c_text": "Call references on the third candidate first", "choice_c_exp_reward": 120, "choice_c_cash_change": 0, "choice_c_reputation_change": 2,
         "choice_c_feedback": "Due diligence before hiring is essential! Reference checks reveal important information.", "subskill_focus": "Recruitment"},
        
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Human Resources", "required_level": 1,
         "scenario_title": "Staff Scheduling Nightmare", "scenario_narrative": "Your servers are complaining about unfair scheduling. Some always get weekend shifts (better tips), while others are stuck with slow weekdays.",
         "choice_a_text": "Create a rotating schedule system", "choice_a_exp_reward": 120, "choice_a_cash_change": 0, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Fair rotation improved morale significantly! Equitable treatment is a core HR principle.",
         "choice_b_text": "Assign shifts based on seniority", "choice_b_exp_reward": 80, "choice_b_cash_change": 0, "choice_b_reputation_change": 2,
         "choice_b_feedback": "Veterans appreciate the perk but newer staff feel undervalued. Consider retention of all employees.",
         "choice_c_text": "Let staff trade shifts among themselves", "choice_c_exp_reward": 90, "choice_c_cash_change": 0, "choice_c_reputation_change": 3,
         "choice_c_feedback": "Autonomy is appreciated but chaos can result. Some structure is usually needed.", "subskill_focus": "Team Building"},
        
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Human Resources", "required_level": 2,
         "scenario_title": "The Training Program", "scenario_narrative": "New hires are making too many mistakes. Orders are wrong, customers are frustrated. You need better onboarding.",
         "choice_a_text": "Create a formal training manual and checklist", "choice_a_exp_reward": 130, "choice_a_cash_change": -100, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Documented processes ensure consistency. This is a foundation of professional HR management.",
         "choice_b_text": "Pair new hires with experienced staff for shadowing", "choice_b_exp_reward": 100, "choice_b_cash_change": 0, "choice_b_reputation_change": 3,
         "choice_b_feedback": "Mentorship works well but quality varies by mentor. Consider combining approaches.",
         "choice_c_text": "Extend the probation period from 2 weeks to 4 weeks", "choice_c_exp_reward": 70, "choice_c_cash_change": 0, "choice_c_reputation_change": 0,
         "choice_c_feedback": "More time doesn't help without better training structure. Focus on the process, not just duration.", "subskill_focus": "Training"},
        
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Legal", "required_level": 1,
         "scenario_title": "The Health Inspection", "scenario_narrative": "The health inspector is coming next week. Your kitchen has some minor issues - a faulty hand sink and some questionable food storage practices.",
         "choice_a_text": "Fix everything immediately before the inspection", "choice_a_exp_reward": 120, "choice_a_cash_change": -300, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Proactive compliance is always the right choice. You passed with flying colors!",
         "choice_b_text": "Fix the major issues, hope they miss the minor ones", "choice_b_exp_reward": 60, "choice_b_cash_change": -100, "choice_b_reputation_change": -3,
         "choice_b_feedback": "You got cited for the issues they found. Cutting corners on compliance is risky.",
         "choice_c_text": "Consult with a food safety expert ($200)", "choice_c_exp_reward": 100, "choice_c_cash_change": -400, "choice_c_reputation_change": 6,
         "choice_c_feedback": "Expert guidance identified issues you hadn't noticed. Professional advice on compliance is valuable.", "subskill_focus": "Regulatory Compliance"},
        
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Legal", "required_level": 1,
         "scenario_title": "The Slip and Fall", "scenario_narrative": "A customer slipped on a wet floor in your restaurant. They're not seriously injured but are threatening to sue. Your insurance has a $5,000 deductible.",
         "choice_a_text": "Offer to pay their medical bills directly", "choice_a_exp_reward": 100, "choice_a_cash_change": -500, "choice_a_reputation_change": 4,
         "choice_a_feedback": "Goodwill gesture diffused the situation. Sometimes direct resolution is cheaper than legal battles.",
         "choice_b_text": "Let your insurance handle it completely", "choice_b_exp_reward": 80, "choice_b_cash_change": -5000, "choice_b_reputation_change": -2,
         "choice_b_feedback": "Insurance covered it but you paid the deductible. Prevention is cheaper than claims.",
         "choice_c_text": "Document everything and implement better floor safety", "choice_c_exp_reward": 130, "choice_c_cash_change": -800, "choice_c_reputation_change": 5,
         "choice_c_feedback": "Smart risk management! Documentation protects you legally while prevention reduces future incidents.", "subskill_focus": "Risk Management"},
        
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Legal", "required_level": 2,
         "scenario_title": "The Employment Contract", "scenario_narrative": "Your head chef wants a formal employment contract with non-compete and confidentiality clauses. This is your first experience with such agreements.",
         "choice_a_text": "Write a simple contract yourself", "choice_a_exp_reward": 60, "choice_a_cash_change": 0, "choice_a_reputation_change": 0,
         "choice_a_feedback": "DIY contracts often have unenforceable clauses. Legal expertise matters for important documents.",
         "choice_b_text": "Have a lawyer draft a proper contract ($500)", "choice_b_exp_reward": 130, "choice_b_cash_change": -500, "choice_b_reputation_change": 5,
         "choice_b_feedback": "Professional contracts protect both parties. This investment in legal infrastructure is wise.",
         "choice_c_text": "Use a standard template from the internet", "choice_c_exp_reward": 75, "choice_c_cash_change": -50, "choice_c_reputation_change": 2,
         "choice_c_feedback": "Templates work as a starting point but may not fit your specific needs. Consider customization.", "subskill_focus": "Contract Law"},
        
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Strategy", "required_level": 1,
         "scenario_title": "The Competition Opens", "scenario_narrative": "A new restaurant just opened across the street with lower prices and a similar menu. Your first week after their opening, sales dropped 20%.",
         "choice_a_text": "Match their prices immediately", "choice_a_exp_reward": 60, "choice_a_cash_change": -500, "choice_a_reputation_change": -2,
         "choice_a_feedback": "Price wars erode profits for everyone. Competing on price alone is rarely sustainable.",
         "choice_b_text": "Differentiate with unique dishes and better service", "choice_b_exp_reward": 130, "choice_b_cash_change": -200, "choice_b_reputation_change": 8,
         "choice_b_feedback": "Excellent strategic thinking! Differentiation creates sustainable competitive advantage.",
         "choice_c_text": "Focus on your loyal customers with exclusive offers", "choice_c_exp_reward": 110, "choice_c_cash_change": -100, "choice_c_reputation_change": 5,
         "choice_c_feedback": "Retention is cheaper than acquisition. Strong strategy to protect your core customer base.", "subskill_focus": "Competitive Analysis"},
        
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Strategy", "required_level": 1,
         "scenario_title": "The Expansion Question", "scenario_narrative": "After 6 months, your restaurant is profitable. A friend suggests opening a second location. Your banker says you could qualify for a loan.",
         "choice_a_text": "Start looking for a second location immediately", "choice_a_exp_reward": 70, "choice_a_cash_change": 0, "choice_a_reputation_change": 3,
         "choice_a_feedback": "Enthusiasm is good but 6 months may be too early. Make sure your first location runs smoothly first.",
         "choice_b_text": "Wait until the first location runs without you there", "choice_b_exp_reward": 130, "choice_b_cash_change": 0, "choice_b_reputation_change": 5,
         "choice_b_feedback": "Wise strategic patience! Scaling before having systems in place is a common failure point.",
         "choice_c_text": "Expand the current location's capacity instead", "choice_c_exp_reward": 100, "choice_c_cash_change": -2000, "choice_c_reputation_change": 4,
         "choice_c_feedback": "Maximizing existing assets before expansion is smart. Less risky than new locations.", "subskill_focus": "Long-term Planning"},
        
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Strategy", "required_level": 2,
         "scenario_title": "The Franchise Offer", "scenario_narrative": "A business consultant approaches you about franchising your concept. They claim you could have 10 locations in 5 years with their help (for 10% of franchise fees).",
         "choice_a_text": "Explore the franchise opportunity in detail", "choice_a_exp_reward": 100, "choice_a_cash_change": -1000, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Due diligence is appropriate. Franchising requires systems, training, and legal infrastructure.",
         "choice_b_text": "Focus on perfecting the current business first", "choice_b_exp_reward": 120, "choice_b_cash_change": 0, "choice_b_reputation_change": 3,
         "choice_b_feedback": "Strategic patience. Franchising a flawed concept just spreads problems. Perfect the model first.",
         "choice_c_text": "Reject franchising - you want to own all locations", "choice_c_exp_reward": 80, "choice_c_cash_change": 0, "choice_c_reputation_change": 2,
         "choice_c_feedback": "Full ownership means more control but slower growth. Both approaches can work.", "subskill_focus": "Business Planning"},
    ]
    
    for scenario in scenarios:
        cur.execute("""
            INSERT INTO scenario_master (world_type, industry, discipline, required_level, scenario_title, scenario_narrative,
                choice_a_text, choice_a_exp_reward, choice_a_cash_change, choice_a_reputation_change, choice_a_feedback,
                choice_b_text, choice_b_exp_reward, choice_b_cash_change, choice_b_reputation_change, choice_b_feedback,
                choice_c_text, choice_c_exp_reward, choice_c_cash_change, choice_c_reputation_change, choice_c_feedback,
                subskill_focus)
            VALUES (%(world_type)s, %(industry)s, %(discipline)s, %(required_level)s, %(scenario_title)s, %(scenario_narrative)s,
                %(choice_a_text)s, %(choice_a_exp_reward)s, %(choice_a_cash_change)s, %(choice_a_reputation_change)s, %(choice_a_feedback)s,
                %(choice_b_text)s, %(choice_b_exp_reward)s, %(choice_b_cash_change)s, %(choice_b_reputation_change)s, %(choice_b_feedback)s,
                %(choice_c_text)s, %(choice_c_exp_reward)s, %(choice_c_cash_change)s, %(choice_c_reputation_change)s, %(choice_c_feedback)s,
                %(subskill_focus)s)
        """, scenario)
    
    conn.commit()
    print(f"Seeded {len(scenarios)} Modern Restaurant scenarios for all disciplines!")
    cur.close()
    conn.close()


def seed_marketing_curriculum():
    """Seed the complete 10-level Marketing Curriculum for Modern/Restaurant."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM scenario_master WHERE discipline = 'Marketing' AND scenario_title LIKE '%L1:%'")
    result = cur.fetchone()
    if result['count'] > 0:
        print("Marketing curriculum already seeded.")
        cur.close()
        conn.close()
        return
    
    scenarios = [
        # LEVEL 1: What is Marketing? (Need vs. Want)
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Marketing", "required_level": 1,
         "scenario_title": "L1: Understanding Customer Needs", 
         "scenario_narrative": "A customer walks in looking tired and mentions they skipped breakfast. Your Marketing Manager explains: 'Marketing is about matching what we offer to what customers need or want. This person has a NEED (hunger) but we can shape their WANT.' How do you respond?",
         "choice_a_text": "Offer a quick, affordable breakfast combo (addresses the NEED)", 
         "choice_a_exp_reward": 80, "choice_a_cash_change": 50, "choice_a_reputation_change": 3,
         "choice_a_feedback": "You addressed the customer's basic need. In marketing, identifying needs is step one - but remember, wants can lead to higher-value sales.",
         "choice_b_text": "Suggest the premium brunch special with fresh-squeezed juice (creates a WANT)", 
         "choice_b_exp_reward": 100, "choice_b_cash_change": 120, "choice_b_reputation_change": 5,
         "choice_b_feedback": "Excellent! You transformed a basic need into a premium want. Marketing's power is shaping desires beyond basic needs.",
         "choice_c_text": "Just take their order without any suggestion", 
         "choice_c_exp_reward": 40, "choice_c_cash_change": 30, "choice_c_reputation_change": 0,
         "choice_c_feedback": "You missed a marketing opportunity. Great marketers proactively guide customers from needs to wants.", 
         "subskill_focus": "Customer Psychology"},
        
        # LEVEL 2: The 4 Ps - Product
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Marketing", "required_level": 2,
         "scenario_title": "L2: Defining Your Product Strategy", 
         "scenario_narrative": "You're designing a new menu item. The Finance Director says 'Product is the first of the 4 Ps of marketing.' You must decide the product's features, benefits, and positioning. What approach do you take?",
         "choice_a_text": "Create a premium gourmet burger with high-quality ingredients and unique presentation", 
         "choice_a_exp_reward": 100, "choice_a_cash_change": -200, "choice_a_reputation_change": 8,
         "choice_a_feedback": "Premium products have higher margins but smaller markets. Your product now signals quality and exclusivity - a key marketing decision.",
         "choice_b_text": "Create a budget-friendly everyday burger that's affordable and consistent", 
         "choice_b_exp_reward": 90, "choice_b_cash_change": 150, "choice_b_reputation_change": 3,
         "choice_b_feedback": "Budget products target volume over margin. This product strategy focuses on accessibility and repeat purchases.",
         "choice_c_text": "Create a mid-range burger that tries to appeal to everyone", 
         "choice_c_exp_reward": 60, "choice_c_cash_change": 50, "choice_c_reputation_change": 2,
         "choice_c_feedback": "The 'stuck in the middle' trap! Products that try to be everything often appeal to no one. Choose a clear position.", 
         "subskill_focus": "Product Strategy"},
        
        # LEVEL 3: Customer Segmentation & Target Audience
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Marketing", "required_level": 3,
         "scenario_title": "L3: Finding Your Target Market", 
         "scenario_narrative": "Your Marketing Manager presents data: 'We can't advertise to everyone. We need to segment the market.' She shows two potential segments: College students (limited budget, high volume, social media users) or Business professionals (expense accounts, weekday lunches, value convenience). Who do you target?",
         "choice_a_text": "Target college students with social media campaigns and student discounts", 
         "choice_a_exp_reward": 90, "choice_a_cash_change": 100, "choice_a_reputation_change": 4,
         "choice_a_feedback": "Good segmentation! Students are price-sensitive but bring volume and word-of-mouth. Demographics (age, income) and psychographics (lifestyle) drove this choice.",
         "choice_b_text": "Target business professionals with lunch specials and quick service", 
         "choice_b_exp_reward": 100, "choice_b_cash_change": 200, "choice_b_reputation_change": 5,
         "choice_b_feedback": "Smart choice! Business customers have higher spending power. You used demographics (income) and behavior (weekday patterns) to segment.",
         "choice_c_text": "Target both segments with different campaigns for each", 
         "choice_c_exp_reward": 80, "choice_c_cash_change": -100, "choice_c_reputation_change": 3,
         "choice_c_feedback": "Multi-segment strategies require more resources. Possible, but expensive - most startups focus on one segment first.", 
         "subskill_focus": "Market Segmentation"},
        
        # LEVEL 4: The 4 Ps - Price
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Marketing", "required_level": 4,
         "scenario_title": "L4: Setting the Right Price", 
         "scenario_narrative": "Time to price your new signature dish. Your Finance Director explains pricing strategies: Cost-plus (production cost + margin), competitive (match competitors), or value-based (what customers perceive it's worth). Your dish costs $8 to make, competitors charge $18, and customers in focus groups said they'd pay up to $25. What's your price?",
         "choice_a_text": "Price at $16 (cost-plus: $8 cost + 100% margin)", 
         "choice_a_exp_reward": 70, "choice_a_cash_change": 100, "choice_a_reputation_change": 2,
         "choice_a_feedback": "Cost-plus is simple and ensures profit, but you left money on the table. Customers would pay more!",
         "choice_b_text": "Price at $18 (competitive: match the market)", 
         "choice_b_exp_reward": 85, "choice_b_cash_change": 150, "choice_b_reputation_change": 3,
         "choice_b_feedback": "Competitive pricing reduces risk but doesn't differentiate you. Good for commodities, less so for unique products.",
         "choice_c_text": "Price at $22 (value-based: below max willingness to pay)", 
         "choice_c_exp_reward": 110, "choice_c_cash_change": 250, "choice_c_reputation_change": 5,
         "choice_c_feedback": "Value-based pricing captures customer perception! You priced below their $25 max to leave room for satisfaction. This is premium marketing.", 
         "subskill_focus": "Pricing Strategy"},
        
        # LEVEL 5: The 4 Ps - Place (Distribution)
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Marketing", "required_level": 5,
         "scenario_title": "L5: Choosing Your Distribution Channels", 
         "scenario_narrative": "Your Operations Chief asks about expansion. 'Place is the third P - how customers access your product.' Options: Open a second physical location downtown ($50K investment), partner with delivery apps (15% commission per order), or build your own online ordering system ($10K investment). Which channel strategy do you pursue?",
         "choice_a_text": "Open the second physical location downtown", 
         "choice_a_exp_reward": 90, "choice_a_cash_change": -500, "choice_a_reputation_change": 8,
         "choice_a_feedback": "Physical expansion increases reach but requires capital and management attention. Great for building brand presence in high-traffic areas.",
         "choice_b_text": "Partner with delivery apps for instant reach", 
         "choice_b_exp_reward": 100, "choice_b_cash_change": 200, "choice_b_reputation_change": 4,
         "choice_b_feedback": "Smart channel leverage! Delivery apps provide instant distribution to thousands of customers. The 15% commission is the cost of that reach.",
         "choice_c_text": "Build your own online ordering system", 
         "choice_c_exp_reward": 85, "choice_c_cash_change": -100, "choice_c_reputation_change": 3,
         "choice_c_feedback": "Own channels mean no commissions and customer data ownership. Higher upfront cost but better long-term margins.", 
         "subskill_focus": "Distribution Channels"},
        
        # LEVEL 6: The 4 Ps - Promotion & CPA
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Marketing", "required_level": 6,
         "scenario_title": "L6: Measuring Promotion Effectiveness (CPA)", 
         "scenario_narrative": "Your Marketing Manager presents two ad campaigns: Social Media Ads cost $500 and brought 50 new customers. Local Newspaper Ads cost $800 and brought 40 new customers. She asks: 'Which has the better Cost Per Acquisition?' Which campaign wins and should get more budget?",
         "choice_a_text": "Social Media - CPA is $10 per customer ($500÷50)", 
         "choice_a_exp_reward": 120, "choice_a_cash_change": 300, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Correct! CPA = Total Cost ÷ Customers Acquired. Social media's $10 CPA beats newspaper's $20 CPA. Always measure promotion effectiveness!",
         "choice_b_text": "Newspaper - it reaches a more established audience", 
         "choice_b_exp_reward": 60, "choice_b_cash_change": -100, "choice_b_reputation_change": 2,
         "choice_b_feedback": "Audience quality matters, but you ignored the math. Newspaper's CPA is $20 ($800÷40) - twice as expensive per customer. Data beats intuition.",
         "choice_c_text": "Split budget equally between both channels", 
         "choice_c_exp_reward": 80, "choice_c_cash_change": 50, "choice_c_reputation_change": 3,
         "choice_c_feedback": "Diversification has value, but ignoring CPA data wastes money. Optimize based on metrics, then diversify.", 
         "subskill_focus": "Cost Per Acquisition"},
        
        # LEVEL 7: A/B Testing & Conversion
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Marketing", "required_level": 7,
         "scenario_title": "L7: Running Your First A/B Test", 
         "scenario_narrative": "You want to improve online orders. Your Marketing Manager suggests an A/B test: 'Show half of visitors Version A (photo-focused menu) and half Version B (description-focused menu). After 1000 visitors each, Version A converted 8% and Version B converted 5%.' What do you conclude?",
         "choice_a_text": "Version A wins - immediately switch all traffic to it", 
         "choice_a_exp_reward": 100, "choice_a_cash_change": 200, "choice_a_reputation_change": 5,
         "choice_a_feedback": "You applied A/B testing correctly! Version A has 60% higher conversion (8% vs 5%). A/B testing removes guesswork from marketing decisions.",
         "choice_b_text": "Keep testing longer - the sample size might be too small", 
         "choice_b_exp_reward": 110, "choice_b_cash_change": 150, "choice_b_reputation_change": 6,
         "choice_b_feedback": "Statistical rigor! 1000 visitors each is decent, but you're right to consider significance. In practice, this 3% difference is likely significant.",
         "choice_c_text": "The difference is too small to matter", 
         "choice_c_exp_reward": 50, "choice_c_cash_change": 0, "choice_c_reputation_change": 1,
         "choice_c_feedback": "3 percentage points is huge! That's 60% more conversions. In marketing, small percentage improvements compound into major revenue.", 
         "subskill_focus": "Conversion Optimization"},
        
        # LEVEL 8: Customer Retention & LTV
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Marketing", "required_level": 8,
         "scenario_title": "L8: Understanding Customer Lifetime Value", 
         "scenario_narrative": "Your Finance Director presents data: 'Average customer visits 2x/month, spends $30/visit, and stays loyal for 2 years. That's an LTV of $1,440 ($30 × 2 × 24 months).' She asks whether to spend $5,000 on a loyalty program (improves retention by 6 months) or $5,000 on new customer ads (brings 200 new customers). What's smarter?",
         "choice_a_text": "Invest in the loyalty program - retention extends LTV", 
         "choice_a_exp_reward": 120, "choice_a_cash_change": 400, "choice_a_reputation_change": 7,
         "choice_a_feedback": "Brilliant LTV thinking! If 100 loyal customers stay 6 months longer, that's $36,000 additional revenue (100 × $30 × 2 × 6). Retention often beats acquisition.",
         "choice_b_text": "Invest in new customer ads - growth requires new customers", 
         "choice_b_exp_reward": 80, "choice_b_cash_change": 200, "choice_b_reputation_change": 4,
         "choice_b_feedback": "200 new customers × $1,440 LTV = $288,000 potential. But what's their retention rate? New customers often churn faster than loyal ones.",
         "choice_c_text": "Do both with $2,500 each", 
         "choice_c_exp_reward": 90, "choice_c_cash_change": 250, "choice_c_reputation_change": 5,
         "choice_c_feedback": "Balanced approach! But the math favored retention here. Always calculate LTV impact before splitting budgets.", 
         "subskill_focus": "Customer Lifetime Value"},
        
        # LEVEL 9: Competitive Strategy & Positioning (SWOT)
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Marketing", "required_level": 9,
         "scenario_title": "L9: Competitive Positioning with SWOT", 
         "scenario_narrative": "A rival just opened across the street with identical menu and lower prices! Your Strategy Advisor runs a SWOT analysis: Strengths (loyal customer base, unique recipes), Weaknesses (higher costs), Opportunities (delivery expansion), Threats (price war). How do you position against them?",
         "choice_a_text": "Emphasize quality and unique recipes - 'You can't copy our secret sauce'", 
         "choice_a_exp_reward": 130, "choice_a_cash_change": 300, "choice_a_reputation_change": 8,
         "choice_a_feedback": "Perfect positioning! You leveraged strengths (unique recipes) to differentiate. Positioning means owning a distinct place in customers' minds.",
         "choice_b_text": "Match their prices to prevent customer loss", 
         "choice_b_exp_reward": 60, "choice_b_cash_change": -200, "choice_b_reputation_change": 2,
         "choice_b_feedback": "Price wars destroy margins and rarely have winners. Your weakness (higher costs) makes this especially dangerous.",
         "choice_c_text": "Accelerate delivery expansion to capture new territory", 
         "choice_c_exp_reward": 100, "choice_c_cash_change": 100, "choice_c_reputation_change": 5,
         "choice_c_feedback": "Using opportunities from SWOT! Expanding where they aren't reduces direct competition. Strategic but requires execution.", 
         "subskill_focus": "Competitive Positioning"},
        
        # LEVEL 10: Brand Architecture & Crisis Management
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Marketing", "required_level": 10,
         "scenario_title": "L10: Managing a Brand Crisis", 
         "scenario_narrative": "CRISIS! A customer found a foreign object in their food and posted it on social media. It's going viral - 50,000 views and climbing. News outlets are calling. Your Legal Counsel warns about liability, but your Marketing Manager says 'This is a brand moment.' How do you respond?",
         "choice_a_text": "Issue immediate public apology, offer full refund, invite customer back for VIP treatment", 
         "choice_a_exp_reward": 150, "choice_a_cash_change": -500, "choice_a_reputation_change": 10,
         "choice_a_feedback": "Masterful crisis management! Transparency, accountability, and generosity turn critics into advocates. This is executive-level brand leadership.",
         "choice_b_text": "Stay silent and let legal handle it - don't admit fault publicly", 
         "choice_b_exp_reward": 40, "choice_b_cash_change": 0, "choice_b_reputation_change": -15,
         "choice_b_feedback": "Silence in a crisis is catastrophic. Social media amplifies every hour you don't respond. You've lost control of the narrative.",
         "choice_c_text": "Post a general statement about food safety standards without addressing the specific incident", 
         "choice_c_exp_reward": 70, "choice_c_cash_change": -100, "choice_c_reputation_change": -5,
         "choice_c_feedback": "Generic responses feel evasive. Customers want to see you take personal responsibility, not hide behind corporate speak.", 
         "subskill_focus": "Crisis Management"},
    ]
    
    for scenario in scenarios:
        cur.execute("""
            INSERT INTO scenario_master (world_type, industry, discipline, required_level, scenario_title, scenario_narrative,
                choice_a_text, choice_a_exp_reward, choice_a_cash_change, choice_a_reputation_change, choice_a_feedback,
                choice_b_text, choice_b_exp_reward, choice_b_cash_change, choice_b_reputation_change, choice_b_feedback,
                choice_c_text, choice_c_exp_reward, choice_c_cash_change, choice_c_reputation_change, choice_c_feedback,
                subskill_focus)
            VALUES (%(world_type)s, %(industry)s, %(discipline)s, %(required_level)s, %(scenario_title)s, %(scenario_narrative)s,
                %(choice_a_text)s, %(choice_a_exp_reward)s, %(choice_a_cash_change)s, %(choice_a_reputation_change)s, %(choice_a_feedback)s,
                %(choice_b_text)s, %(choice_b_exp_reward)s, %(choice_b_cash_change)s, %(choice_b_reputation_change)s, %(choice_b_feedback)s,
                %(choice_c_text)s, %(choice_c_exp_reward)s, %(choice_c_cash_change)s, %(choice_c_reputation_change)s, %(choice_c_feedback)s,
                %(subskill_focus)s)
        """, scenario)
    
    conn.commit()
    print(f"Seeded {len(scenarios)} Marketing Curriculum scenarios (Levels 1-10)!")
    cur.close()
    conn.close()


def seed_accounting_curriculum():
    """Seed the complete 10-level Accounting/Finance Curriculum for Modern/Restaurant."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM scenario_master WHERE discipline = 'Finance' AND scenario_title LIKE 'L1:%'")
    result = cur.fetchone()
    if result['count'] > 0:
        print("Accounting curriculum already seeded.")
        cur.close()
        conn.close()
        return
    
    scenarios = [
        # LEVEL 1: The Accounting Equation (Assets = Liabilities + Equity)
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Finance", "required_level": 1,
         "scenario_title": "L1: The Accounting Equation", 
         "scenario_narrative": "Your Finance Director draws on a whiteboard: 'Every business transaction follows one rule - Assets = Liabilities + Equity. If your restaurant has $50,000 in assets, a $20,000 bank loan (liability), what's your equity?' She tests your understanding.",
         "choice_a_text": "$30,000 - because Assets ($50K) minus Liabilities ($20K) equals Equity", 
         "choice_a_exp_reward": 100, "choice_a_cash_change": 0, "choice_a_reputation_change": 3,
         "choice_a_feedback": "Correct! The accounting equation always balances: $50,000 = $20,000 + $30,000. Equity represents what you actually OWN after paying debts.",
         "choice_b_text": "$70,000 - I add assets and liabilities together", 
         "choice_b_exp_reward": 40, "choice_b_cash_change": 0, "choice_b_reputation_change": 0,
         "choice_b_feedback": "Not quite. Liabilities are what you OWE, not own. Equity = Assets - Liabilities. You'd have $30,000 in equity.",
         "choice_c_text": "$50,000 - the equity equals the assets", 
         "choice_c_exp_reward": 50, "choice_c_cash_change": 0, "choice_c_reputation_change": 1,
         "choice_c_feedback": "That would only be true if you had no debt. With a $20K loan, your equity is $30K. Always subtract what you owe!", 
         "subskill_focus": "Accounting Fundamentals"},
        
        # LEVEL 2: Revenue vs Expense (Key Terms)
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Finance", "required_level": 2,
         "scenario_title": "L2: Revenue vs Expense", 
         "scenario_narrative": "Your accountant reviews last month: 'You sold $40,000 worth of food (revenue), but spent $15,000 on ingredients, $8,000 on wages, and $5,000 on rent (expenses).' She asks you to calculate the profit.",
         "choice_a_text": "$12,000 profit - Revenue ($40K) minus all Expenses ($28K)", 
         "choice_a_exp_reward": 100, "choice_a_cash_change": 120, "choice_a_reputation_change": 4,
         "choice_a_feedback": "Excellent! Profit = Revenue - Expenses. $40,000 - ($15,000 + $8,000 + $5,000) = $12,000. You understand the fundamental profit calculation!",
         "choice_b_text": "$25,000 profit - I only subtracted ingredients", 
         "choice_b_exp_reward": 50, "choice_b_cash_change": 0, "choice_b_reputation_change": 1,
         "choice_b_feedback": "You forgot wages and rent! All operating expenses must be subtracted. Real profit is $12,000.",
         "choice_c_text": "$40,000 profit - that's what we made in sales", 
         "choice_c_exp_reward": 30, "choice_c_cash_change": 0, "choice_c_reputation_change": 0,
         "choice_c_feedback": "Revenue is NOT profit! You must subtract expenses. Many businesses fail because owners confuse revenue with profit.", 
         "subskill_focus": "Profit Calculation"},
        
        # LEVEL 3: Cash vs Accrual Accounting
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Finance", "required_level": 3,
         "scenario_title": "L3: Cash vs Accrual Accounting", 
         "scenario_narrative": "A corporate client orders $5,000 worth of catering but won't pay for 30 days. Your accountant asks: 'Under CASH accounting, we record revenue when paid. Under ACCRUAL accounting, we record when earned. Which should we use, and when do we record this sale?'",
         "choice_a_text": "Accrual - record the $5,000 now when service is delivered", 
         "choice_a_exp_reward": 110, "choice_a_cash_change": 0, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Correct! Accrual accounting matches revenue to when it's EARNED, not received. Most larger businesses use accrual for accurate financial pictures.",
         "choice_b_text": "Cash - record the $5,000 in 30 days when we receive payment", 
         "choice_b_exp_reward": 80, "choice_b_cash_change": 0, "choice_b_reputation_change": 3,
         "choice_b_feedback": "Cash accounting is simpler and shows actual cash flow, but can misrepresent your business's real activity. Small businesses often start with cash basis.",
         "choice_c_text": "Record half now and half when paid", 
         "choice_c_exp_reward": 40, "choice_c_cash_change": 0, "choice_c_reputation_change": 1,
         "choice_c_feedback": "You can't mix methods! Choose one system and apply it consistently. GAAP requires accrual for larger businesses.", 
         "subskill_focus": "Accounting Methods"},
        
        # LEVEL 4: Income Statement (P&L)
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Finance", "required_level": 4,
         "scenario_title": "L4: Reading the Income Statement", 
         "scenario_narrative": "Your Finance Director presents the P&L: Revenue $100,000, Cost of Goods Sold $35,000, Operating Expenses $40,000, Interest $5,000, Taxes $5,000. She asks: 'What's our Gross Profit and Net Income?'",
         "choice_a_text": "Gross Profit: $65,000 (Revenue - COGS), Net Income: $15,000 (after all expenses)", 
         "choice_a_exp_reward": 120, "choice_a_cash_change": 150, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Perfect! Gross Profit = Revenue - COGS = $65,000. Net Income = Gross Profit - Operating Expenses - Interest - Taxes = $15,000. You read a P&L like a pro!",
         "choice_b_text": "Gross Profit: $25,000, Net Income: $15,000", 
         "choice_b_exp_reward": 60, "choice_b_cash_change": 0, "choice_b_reputation_change": 2,
         "choice_b_feedback": "Your Net Income is right, but Gross Profit only subtracts COGS from Revenue. Gross Profit = $100K - $35K = $65,000.",
         "choice_c_text": "Both are $15,000 - that's what's left after all expenses", 
         "choice_c_exp_reward": 50, "choice_c_cash_change": 0, "choice_c_reputation_change": 1,
         "choice_c_feedback": "Net Income is $15K, but Gross Profit is higher ($65K). Gross Profit shows profitability before overhead - a key metric for restaurants!", 
         "subskill_focus": "Income Statement"},
        
        # LEVEL 5: Balance Sheet
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Finance", "required_level": 5,
         "scenario_title": "L5: Understanding the Balance Sheet", 
         "scenario_narrative": "An investor asks to see your Balance Sheet. Your accountant shows: Current Assets $30,000 (cash, inventory), Fixed Assets $70,000 (equipment), Current Liabilities $20,000 (payables), Long-term Debt $40,000 (loan), Owner's Equity $40,000. The investor asks: 'Is this business healthy?'",
         "choice_a_text": "Yes - Assets ($100K) equal Liabilities + Equity ($100K), and we have positive equity", 
         "choice_a_exp_reward": 110, "choice_a_cash_change": 500, "choice_a_reputation_change": 6,
         "choice_a_feedback": "Great analysis! The balance sheet balances, equity is positive at $40K, and current ratio (30K/20K = 1.5) shows short-term health. You impressed the investor!",
         "choice_b_text": "No - we have $60,000 in total debt, that's too much", 
         "choice_b_exp_reward": 70, "choice_b_cash_change": 0, "choice_b_reputation_change": 2,
         "choice_b_feedback": "Debt isn't inherently bad! Your debt-to-equity ratio is 1.5 ($60K/$40K), which is reasonable for a restaurant. Focus on ability to pay, not total debt.",
         "choice_c_text": "I need more information to assess health", 
         "choice_c_exp_reward": 90, "choice_c_cash_change": 200, "choice_c_reputation_change": 4,
         "choice_c_feedback": "Smart answer! Balance sheets show a snapshot, but trends, cash flow, and industry context matter too. The investor appreciates your caution.", 
         "subskill_focus": "Balance Sheet"},
        
        # LEVEL 6: Cash Flow Statement
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Finance", "required_level": 6,
         "scenario_title": "L6: The Three Types of Cash Flow", 
         "scenario_narrative": "Your Finance Director explains: 'Cash Flow has 3 sections: Operating (daily business), Investing (buying/selling assets), Financing (loans, equity).' This month: customers paid $50K (Operating +), bought $20K equipment (Investing -), took $10K loan (Financing +). What's net cash flow?",
         "choice_a_text": "+$40,000 net cash flow ($50K - $20K + $10K)", 
         "choice_a_exp_reward": 120, "choice_a_cash_change": 400, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Correct! Operating +$50K, Investing -$20K, Financing +$10K = Net +$40K. You understand how cash moves through the three channels!",
         "choice_b_text": "+$60,000 - I added all the numbers", 
         "choice_b_exp_reward": 50, "choice_b_cash_change": 0, "choice_b_reputation_change": 1,
         "choice_b_feedback": "Equipment purchase is a cash OUTFLOW (negative). Investing activities that buy assets reduce cash. Net is +$40K.",
         "choice_c_text": "+$30,000 - I subtracted the loan since it's debt", 
         "choice_c_exp_reward": 60, "choice_c_cash_change": 0, "choice_c_reputation_change": 2,
         "choice_c_feedback": "Loans INCREASE cash when received (even though they're debt). Repaying loans decreases cash. This inflow gives you +$40K net.", 
         "subskill_focus": "Cash Flow Statement"},
        
        # LEVEL 7: Financial Ratios (Quick and Current Ratios)
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Finance", "required_level": 7,
         "scenario_title": "L7: Analyzing Financial Ratios", 
         "scenario_narrative": "A bank is considering a loan. They examine your ratios: Current Assets $30,000, Inventory $10,000, Current Liabilities $20,000. The banker asks: 'What's your Current Ratio and Quick Ratio? We need Current Ratio above 1.5 and Quick Ratio above 1.0.'",
         "choice_a_text": "Current Ratio: 1.5 (30K/20K), Quick Ratio: 1.0 ((30K-10K)/20K) - We qualify!", 
         "choice_a_exp_reward": 130, "choice_a_cash_change": 1000, "choice_a_reputation_change": 7,
         "choice_a_feedback": "Perfect calculations! Current Ratio = Current Assets / Current Liabilities. Quick Ratio excludes inventory (harder to liquidate). You secured the loan!",
         "choice_b_text": "Both ratios are 1.5 - we divide assets by liabilities", 
         "choice_b_exp_reward": 70, "choice_b_cash_change": 0, "choice_b_reputation_change": 2,
         "choice_b_feedback": "Current Ratio is 1.5, but Quick Ratio EXCLUDES inventory: (30K-10K)/20K = 1.0. Inventory isn't as liquid as cash!",
         "choice_c_text": "Current Ratio: 0.67, Quick Ratio: 0.5 - we're in trouble", 
         "choice_c_exp_reward": 40, "choice_c_cash_change": 0, "choice_c_reputation_change": 0,
         "choice_c_feedback": "You inverted the formula! Assets go on TOP: Current Ratio = Assets/Liabilities = 30K/20K = 1.5, not 20K/30K.", 
         "subskill_focus": "Financial Ratios"},
        
        # LEVEL 8: Inventory Valuation (FIFO/LIFO)
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Finance", "required_level": 8,
         "scenario_title": "L8: FIFO vs LIFO Inventory Valuation", 
         "scenario_narrative": "Ingredient prices are rising. You bought flour at $10/bag (January, 100 bags) and $15/bag (February, 100 bags). You used 120 bags this month. Your accountant asks: 'FIFO (First-In-First-Out) or LIFO (Last-In-First-Out)? This affects your reported profit and taxes.'",
         "choice_a_text": "FIFO - Report $1,300 COGS (100×$10 + 20×$15), higher profit, higher taxes", 
         "choice_a_exp_reward": 120, "choice_a_cash_change": -100, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Correct FIFO calculation! Using older $10 bags first shows lower COGS, higher profit, but higher taxes. FIFO is standard for restaurants (matches actual usage).",
         "choice_b_text": "LIFO - Report $1,700 COGS (100×$15 + 20×$10), lower profit, lower taxes", 
         "choice_b_exp_reward": 110, "choice_b_cash_change": 100, "choice_b_reputation_change": 5,
         "choice_b_feedback": "Correct LIFO math! Using newer $15 bags first shows higher COGS, lower profit, lower taxes. LIFO saves taxes when prices rise, but isn't allowed under IFRS.",
         "choice_c_text": "Average cost - $12.50 per bag for $1,500 COGS", 
         "choice_c_exp_reward": 100, "choice_c_cash_change": 0, "choice_c_reputation_change": 4,
         "choice_c_feedback": "Weighted average is a third valid method! Simple and smooths out price fluctuations. Good choice for volatile ingredients.", 
         "subskill_focus": "Inventory Valuation"},
        
        # LEVEL 9: Budgeting and Variance Analysis
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Finance", "required_level": 9,
         "scenario_title": "L9: Budget Variance Analysis", 
         "scenario_narrative": "You budgeted $10,000 for food costs but actually spent $12,000. Your Finance Director asks: 'That's a $2,000 unfavorable variance (20% over budget). Should we investigate price variance (costs went up) or quantity variance (we used more)?'",
         "choice_a_text": "Investigate both - break down variance into price and quantity components", 
         "choice_a_exp_reward": 140, "choice_a_cash_change": 200, "choice_a_reputation_change": 7,
         "choice_a_feedback": "Excellent variance analysis! Total Variance = Price Variance + Quantity Variance. Maybe suppliers raised prices (price) AND we wasted ingredients (quantity). Root cause analysis prevents future overruns.",
         "choice_b_text": "Focus on quantity - we probably over-ordered or wasted food", 
         "choice_b_exp_reward": 100, "choice_b_cash_change": 100, "choice_b_reputation_change": 4,
         "choice_b_feedback": "Quantity variance is often controllable, but don't ignore price! If suppliers raised rates, renegotiating saves more than reducing waste.",
         "choice_c_text": "It's only 20% over - acceptable variance, don't investigate", 
         "choice_c_exp_reward": 60, "choice_c_cash_change": -200, "choice_c_reputation_change": 1,
         "choice_c_feedback": "20% is significant! $2,000 monthly = $24,000 yearly. Small variances compound. Always investigate material deviations from budget.", 
         "subskill_focus": "Budgeting"},
        
        # LEVEL 10: Tax Strategy and Compliance (GAAP/IFRS)
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Finance", "required_level": 10,
         "scenario_title": "L10: Tax Strategy and Accounting Standards", 
         "scenario_narrative": "Your accountant explains: 'GAAP (US) and IFRS (International) are accounting frameworks that determine how we report finances. We can also legally reduce taxes through depreciation methods, timing of expenses, and entity structure.' An investor from Europe asks about your compliance. What's your strategy?",
         "choice_a_text": "Follow GAAP with aggressive depreciation and strategic expense timing to minimize taxes legally", 
         "choice_a_exp_reward": 150, "choice_a_cash_change": 500, "choice_a_reputation_change": 8,
         "choice_a_feedback": "Masterful! Accelerated depreciation front-loads deductions, reducing early-year taxes. Combined with proper expense timing, this maximizes cash flow while staying compliant. CFO-level thinking!",
         "choice_b_text": "Follow GAAP strictly with conservative accounting - less risk of audit issues", 
         "choice_b_exp_reward": 110, "choice_b_cash_change": 0, "choice_b_reputation_change": 6,
         "choice_b_feedback": "Conservative accounting is defensible and builds credibility with investors. You pay more taxes now but have cleaner books for future funding rounds.",
         "choice_c_text": "Use whatever methods show the highest profit to impress investors", 
         "choice_c_exp_reward": 50, "choice_c_cash_change": -500, "choice_c_reputation_change": -5,
         "choice_c_feedback": "Dangerous! Aggressive accounting to inflate profits can lead to fraud charges. Enron collapsed this way. Always prioritize compliance over appearance.", 
         "subskill_focus": "Tax Strategy"},
    ]
    
    for scenario in scenarios:
        cur.execute("""
            INSERT INTO scenario_master (world_type, industry, discipline, required_level, scenario_title, scenario_narrative,
                choice_a_text, choice_a_exp_reward, choice_a_cash_change, choice_a_reputation_change, choice_a_feedback,
                choice_b_text, choice_b_exp_reward, choice_b_cash_change, choice_b_reputation_change, choice_b_feedback,
                choice_c_text, choice_c_exp_reward, choice_c_cash_change, choice_c_reputation_change, choice_c_feedback,
                subskill_focus)
            VALUES (%(world_type)s, %(industry)s, %(discipline)s, %(required_level)s, %(scenario_title)s, %(scenario_narrative)s,
                %(choice_a_text)s, %(choice_a_exp_reward)s, %(choice_a_cash_change)s, %(choice_a_reputation_change)s, %(choice_a_feedback)s,
                %(choice_b_text)s, %(choice_b_exp_reward)s, %(choice_b_cash_change)s, %(choice_b_reputation_change)s, %(choice_b_feedback)s,
                %(choice_c_text)s, %(choice_c_exp_reward)s, %(choice_c_cash_change)s, %(choice_c_reputation_change)s, %(choice_c_feedback)s,
                %(subskill_focus)s)
        """, scenario)
    
    conn.commit()
    print(f"Seeded {len(scenarios)} Accounting Curriculum scenarios (Levels 1-10)!")
    cur.close()
    conn.close()


def seed_finance_curriculum():
    """Seed the complete 10-level Strategic Finance Curriculum across all 3 worlds."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM scenario_master WHERE discipline = 'Finance' AND scenario_title LIKE '%Cash Flow Management%'")
    result = cur.fetchone()
    if result['count'] > 0:
        print("Finance curriculum already seeded.")
        cur.close()
        conn.close()
        return
    
    scenarios = [
        # ========== LEVEL 1: Cash Flow Management (Working Capital) ==========
        # Modern World
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Finance", "required_level": 1,
         "scenario_title": "L1: Cash Flow Management", 
         "scenario_narrative": "Your Finance Director looks worried: 'We have $15,000 in the bank. This month's bills are $12,000, but our biggest customer owes us $20,000 and won't pay for 45 days. A supplier is offering a 10% discount if we pay $8,000 today.' How do you manage your working capital?",
         "choice_a_text": "Pay bills first ($12K), skip the discount - we need to stay solvent", 
         "choice_a_exp_reward": 90, "choice_a_cash_change": -120, "choice_a_reputation_change": 3,
         "choice_a_feedback": "Safe choice! Rule #1 of cash flow: solvency first. You can't benefit from discounts if you can't pay employees. Cash management is about surviving to tomorrow.",
         "choice_b_text": "Take the discount ($8K), pay partial bills - negotiate payment plans for the rest", 
         "choice_b_exp_reward": 110, "choice_b_cash_change": 200, "choice_b_reputation_change": 5,
         "choice_b_feedback": "Strategic cash management! The $800 discount savings plus negotiated terms maximizes your working capital. This is how CFOs think.",
         "choice_c_text": "Call the customer demanding early payment - it's their fault we're tight", 
         "choice_c_exp_reward": 50, "choice_c_cash_change": 0, "choice_c_reputation_change": -3,
         "choice_c_feedback": "Damaging a customer relationship rarely solves cash flow. Working capital management means planning ahead, not reacting with panic.", 
         "subskill_focus": "Working Capital"},
        
        # Fantasy World
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Finance", "required_level": 1,
         "scenario_title": "L1: Cash Flow Management", 
         "scenario_narrative": "Your tavern has 200 gold coins in the vault. The ale merchant demands 150 gold today, but the Adventurer's Guild owes you 300 gold for last month's feast - payable at the next full moon (3 weeks away). A traveling spice merchant offers rare ingredients at 80 gold, but only today.",
         "choice_a_text": "Pay the ale merchant (150g) - we need stock to serve customers", 
         "choice_a_exp_reward": 90, "choice_a_cash_change": -100, "choice_a_reputation_change": 3,
         "choice_a_feedback": "Keeping your core supplies flowing is essential. Without ale, you have no business. But you missed the rare spice opportunity.",
         "choice_b_text": "Pay ale (150g) AND buy spices (80g) - use our buffer for opportunity", 
         "choice_b_exp_reward": 60, "choice_b_cash_change": -230, "choice_b_reputation_change": 2,
         "choice_b_feedback": "Risky! You're left with only 20 gold. If the Guild delays payment or an emergency arises, you're insolvent. Never drain your cash buffer.",
         "choice_c_text": "Negotiate 100g partial payment to ale merchant, buy spices with remainder", 
         "choice_c_exp_reward": 110, "choice_c_cash_change": 180, "choice_c_reputation_change": 5,
         "choice_c_feedback": "Masterful working capital management! Partial payments, relationship leverage, and seizing opportunities - you balance all three.", 
         "subskill_focus": "Working Capital"},
        
        # Sci-Fi World  
        {"world_type": "Sci-Fi", "industry": "Mining Corp", "discipline": "Finance", "required_level": 1,
         "scenario_title": "L1: Cash Flow Management", 
         "scenario_narrative": "Your asteroid mining operation has 50,000 credits. The refueling depot demands 35,000 credits by end of cycle. The Galactic Trade Federation owes you 80,000 credits for last quarter's ore shipment - processing takes 60 days. A rival offers to buy your secondary drill for 25,000 credits today.",
         "choice_a_text": "Pay the depot (35K), wait for the Federation payment", 
         "choice_a_exp_reward": 80, "choice_a_cash_change": -200, "choice_a_reputation_change": 2,
         "choice_a_feedback": "Conservative approach keeps you operational but you're tight on reserves. What if ore prices drop or Federation delays?",
         "choice_b_text": "Sell the drill (25K), pay depot - maintain equipment flexibility", 
         "choice_b_exp_reward": 100, "choice_b_cash_change": 100, "choice_b_reputation_change": 4,
         "choice_b_feedback": "Smart liquidity move! Converting idle assets to cash improves your working capital position. You've gained breathing room.",
         "choice_c_text": "Request early payment from Federation at a 5% discount", 
         "choice_c_exp_reward": 110, "choice_c_cash_change": 150, "choice_c_reputation_change": 5,
         "choice_c_feedback": "Factoring receivables! Giving up 5% to get cash 60 days early is often worthwhile. Time value of money in action.", 
         "subskill_focus": "Working Capital"},

        # ========== LEVEL 2: Return on Investment (ROI) ==========
        # Modern World
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Finance", "required_level": 2,
         "scenario_title": "L2: Return on Investment (ROI)", 
         "scenario_narrative": "You have $10,000 to invest. Option A: New espresso machine costs $10,000 and will generate $3,000 extra profit per year. Option B: Marketing campaign costs $10,000 and will generate $5,000 extra profit, but only this year. Which has better ROI?",
         "choice_a_text": "Espresso machine - 30% ROI annually ($3K/$10K), compounds over years", 
         "choice_a_exp_reward": 110, "choice_a_cash_change": 300, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Excellent long-term thinking! 30% annual ROI that repeats beats a one-time 50%. Over 3 years: machine = $9K profit vs marketing = $5K. Time matters!",
         "choice_b_text": "Marketing campaign - 50% ROI ($5K/$10K) is higher than 30%", 
         "choice_b_exp_reward": 80, "choice_b_cash_change": 500, "choice_b_reputation_change": 3,
         "choice_b_feedback": "Higher immediate ROI, but it's one-time. For recurring investments, consider lifetime returns. The machine earns more by year 2.",
         "choice_c_text": "Split $5,000 into each option", 
         "choice_c_exp_reward": 90, "choice_c_cash_change": 250, "choice_c_reputation_change": 4,
         "choice_c_feedback": "Diversification has merit! Half-machine generates $1,500/year ongoing, half-marketing generates $2,500 once. Good balanced approach.", 
         "subskill_focus": "ROI Analysis"},
        
        # Fantasy World
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Finance", "required_level": 2,
         "scenario_title": "L2: Return on Investment (ROI)", 
         "scenario_narrative": "You have 500 gold to invest. Option A: Commission a rare Enchanted Artifact from a master craftsman for 500 gold - sells for 700 gold (40% ROI). Option B: Buy brewing supplies for 500 gold that will produce ale worth 600 gold monthly, forever. Which investment wins?",
         "choice_a_text": "Brewing supplies - 20% monthly ROI ($100/$500) recurring is infinite returns", 
         "choice_a_exp_reward": 120, "choice_a_cash_change": 100, "choice_a_reputation_change": 6,
         "choice_a_feedback": "Brilliant! 20% monthly = 240% annually, recurring forever. The artifact's 40% one-time return pales in comparison. Recurring ROI beats one-time.",
         "choice_b_text": "Enchanted Artifact - 40% ROI in one transaction is higher", 
         "choice_b_exp_reward": 70, "choice_b_cash_change": 200, "choice_b_reputation_change": 2,
         "choice_b_feedback": "One-time 40% is good, but brewing supplies at 20% MONTHLY means 240% ROI in a year. Always annualize returns for fair comparison!",
         "choice_c_text": "Wait for a better opportunity - both seem risky", 
         "choice_c_exp_reward": 40, "choice_c_cash_change": 0, "choice_c_reputation_change": 0,
         "choice_c_feedback": "Inaction is its own risk! Your gold earns 0% sitting in the vault. Even a modest ROI beats inflation and opportunity cost.", 
         "subskill_focus": "ROI Analysis"},
        
        # Sci-Fi World
        {"world_type": "Sci-Fi", "industry": "Mining Corp", "discipline": "Finance", "required_level": 2,
         "scenario_title": "L2: Return on Investment (ROI)", 
         "scenario_narrative": "You have 100,000 credits. Option A: New Mining Drill costs 100,000 and extracts 25,000 credits of exotic metals per quarter. Option B: Automation upgrade costs 100,000 and saves 15,000 credits in labor costs per quarter, forever. Calculate the ROI.",
         "choice_a_text": "Mining Drill - 25% quarterly ROI (25K/100K) = 100% annual return", 
         "choice_a_exp_reward": 100, "choice_a_cash_change": 250, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Revenue-generating assets have clear ROI. 25K quarterly = 100K annually = 100% ROI. Payback in 1 year, then pure profit!",
         "choice_b_text": "Automation - 15% quarterly savings = 60% annual ROI, plus reduces risk", 
         "choice_b_exp_reward": 110, "choice_b_cash_change": 150, "choice_b_reputation_change": 6,
         "choice_b_feedback": "Smart risk-adjusted thinking! Cost savings are guaranteed; revenue depends on market prices. 60% safe ROI may beat 100% risky ROI.",
         "choice_c_text": "Both investments have the same long-term value", 
         "choice_c_exp_reward": 50, "choice_c_cash_change": 0, "choice_c_reputation_change": 1,
         "choice_c_feedback": "Not quite! The drill's 100% beats automation's 60% in pure ROI terms. But risk matters too - calculate both.", 
         "subskill_focus": "ROI Analysis"},

        # ========== LEVEL 3: Time Value of Money (TVM) ==========
        # Modern World
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Finance", "required_level": 3,
         "scenario_title": "L3: Time Value of Money", 
         "scenario_narrative": "A supplier offers you a choice: receive a $10,000 rebate today OR a $11,000 rebate in one year. Your Finance Director asks: 'If we invest $10,000 today at 8% annual interest, what's it worth in a year?' What should you choose?",
         "choice_a_text": "$10,000 today - it becomes $10,800 in a year (10K × 1.08), which is less than $11K", 
         "choice_a_exp_reward": 80, "choice_a_cash_change": 100, "choice_a_reputation_change": 3,
         "choice_a_feedback": "Good TVM calculation! $10K × 1.08 = $10,800 < $11,000. Mathematically, waiting IS better here. But cash flow needs might override theory.",
         "choice_b_text": "$11,000 in one year - it's $200 more in future value terms", 
         "choice_b_exp_reward": 110, "choice_b_cash_change": 0, "choice_b_reputation_change": 5,
         "choice_b_feedback": "Correct TVM analysis! $11K > $10,800 (the future value of $10K at 8%). You earned the equivalent of 10% return by waiting - better than 8%!",
         "choice_c_text": "Always take money today - a bird in hand is worth two in the bush", 
         "choice_c_exp_reward": 60, "choice_c_cash_change": 100, "choice_c_reputation_change": 2,
         "choice_c_feedback": "The intuition is often right, but not always! When the future amount exceeds your investment returns, waiting can be mathematically superior.", 
         "subskill_focus": "Time Value of Money"},
        
        # Fantasy World
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Finance", "required_level": 3,
         "scenario_title": "L3: Time Value of Money", 
         "scenario_narrative": "A noble offers you a choice: 1,000 gold coins today OR 1,200 gold coins after the harvest festival (6 months). The Dwarven Banking Guild pays 5% interest per 6 months. What is the smarter financial decision?",
         "choice_a_text": "Take 1,000 gold today - at 5% it becomes 1,050 gold, still less than 1,200", 
         "choice_a_exp_reward": 80, "choice_a_cash_change": 0, "choice_a_reputation_change": 3,
         "choice_a_feedback": "Good math! 1,000 × 1.05 = 1,050 < 1,200. The noble's offer beats the bank rate. TVM says wait for 1,200 gold.",
         "choice_b_text": "Wait for 1,200 gold - that's a 20% return, far exceeding the 5% bank rate", 
         "choice_b_exp_reward": 120, "choice_b_cash_change": 200, "choice_b_reputation_change": 6,
         "choice_b_feedback": "Perfect! 20% in 6 months (200 gold profit) vs 5% from the bank. Always compare offered returns against your opportunity cost!",
         "choice_c_text": "The noble might not pay - take the guaranteed gold now", 
         "choice_c_exp_reward": 70, "choice_c_cash_change": 100, "choice_c_reputation_change": 3,
         "choice_c_feedback": "Risk consideration is valid! In TVM, we often add a 'risk premium' for uncertain future payments. Noble's credit matters.", 
         "subskill_focus": "Time Value of Money"},
        
        # Sci-Fi World
        {"world_type": "Sci-Fi", "industry": "Mining Corp", "discipline": "Finance", "required_level": 3,
         "scenario_title": "L3: Time Value of Money", 
         "scenario_narrative": "The Galactic Trade Federation offers a contract: receive 50,000 credits today as upfront payment OR 60,000 credits in 2 years upon project completion. Current Federation Bond rates yield 8% annually. Which is worth more?",
         "choice_a_text": "50K today grows to 58,320 credits in 2 years (50K × 1.08²) - take the upfront", 
         "choice_a_exp_reward": 100, "choice_a_cash_change": 500, "choice_a_reputation_change": 4,
         "choice_a_feedback": "Solid compound interest calculation! FV = 50,000 × (1.08)² = 58,320. But 60K > 58,320, so waiting actually wins!",
         "choice_b_text": "60K in 2 years - its present value is 51,440 (60K ÷ 1.08²), exceeds 50K", 
         "choice_b_exp_reward": 120, "choice_b_cash_change": 0, "choice_b_reputation_change": 6,
         "choice_b_feedback": "Master-level TVM! You correctly discounted future value to present value. PV = 60,000 / 1.1664 = 51,440 > 50,000. Waiting wins!",
         "choice_c_text": "They're equivalent - 10K more over 2 years is about 10% annual return", 
         "choice_c_exp_reward": 70, "choice_c_cash_change": 0, "choice_c_reputation_change": 2,
         "choice_c_feedback": "Close thinking but imprecise! The implied return is (60K/50K)^0.5 - 1 = 9.5% annually, slightly above the 8% bond rate. Math matters!", 
         "subskill_focus": "Time Value of Money"},

        # ========== LEVEL 4: Capital Budgeting (Payback Period) ==========
        # Modern World
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Finance", "required_level": 4,
         "scenario_title": "L4: Capital Budgeting - Payback Period", 
         "scenario_narrative": "Two expansion opportunities: Location A costs $100,000 and generates $25,000 annual profit. Location B costs $150,000 and generates $50,000 annual profit. Your bank requires investments to 'pay back' within 4 years. Which do you choose?",
         "choice_a_text": "Location B - payback is 3 years ($150K ÷ $50K), faster than A's 4 years", 
         "choice_a_exp_reward": 120, "choice_a_cash_change": 500, "choice_a_reputation_change": 6,
         "choice_a_feedback": "Correct payback analysis! B: 150K/50K = 3 years. A: 100K/25K = 4 years. Both meet the 4-year threshold, but B recovers capital faster!",
         "choice_b_text": "Location A - it costs less and still meets the 4-year payback requirement", 
         "choice_b_exp_reward": 80, "choice_b_cash_change": 250, "choice_b_reputation_change": 3,
         "choice_b_feedback": "A meets requirements, but B pays back faster (3 vs 4 years) AND generates more profit after payback ($50K vs $25K annually). Think bigger!",
         "choice_c_text": "Neither - 3-4 years is too long to wait for returns", 
         "choice_c_exp_reward": 50, "choice_c_cash_change": 0, "choice_c_reputation_change": 1,
         "choice_c_feedback": "3-4 year payback is standard for real estate! After payback, you own income-generating assets. Short-term thinking costs opportunities.", 
         "subskill_focus": "Capital Budgeting"},
        
        # Fantasy World
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Finance", "required_level": 4,
         "scenario_title": "L4: Capital Budgeting - Payback Period", 
         "scenario_narrative": "Two expansion options: The Cellar expansion costs 2,000 gold and generates 500 gold annual profit. The Garden Terrace costs 3,000 gold and generates 1,200 gold annual profit (but only in warm seasons - 600 gold effective). Which pays back faster?",
         "choice_a_text": "Cellar - payback is 4 years (2,000 ÷ 500), the terrace is 5 years (3,000 ÷ 600)", 
         "choice_a_exp_reward": 110, "choice_a_cash_change": 250, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Excellent adjustment for seasonality! Terrace's 1,200 gold is only half-effective (600 avg), making payback 5 years vs Cellar's 4. Real-world factors matter!",
         "choice_b_text": "Terrace - 1,200 gold annual beats 500 gold, faster payback overall", 
         "choice_b_exp_reward": 60, "choice_b_cash_change": 0, "choice_b_reputation_change": 2,
         "choice_b_feedback": "You forgot seasonal adjustment! 1,200 gold 'only in warm seasons' means ~600 gold annualized. Always normalize to annual figures!",
         "choice_c_text": "Terrace - higher profit after payback, even if slower initially", 
         "choice_c_exp_reward": 90, "choice_c_cash_change": 200, "choice_c_reputation_change": 4,
         "choice_c_feedback": "Valid long-term thinking! After payback, Terrace earns more. Payback period ignores post-payback profits - a known limitation.", 
         "subskill_focus": "Capital Budgeting"},
        
        # Sci-Fi World
        {"world_type": "Sci-Fi", "industry": "Mining Corp", "discipline": "Finance", "required_level": 4,
         "scenario_title": "L4: Capital Budgeting - Payback Period", 
         "scenario_narrative": "Two asteroid mining claims: Claim Alpha costs 500,000 credits and yields 100,000 credits annually. Claim Beta costs 800,000 credits and yields 250,000 credits annually. The Federation requires 5-year payback for licensing. Which qualifies?",
         "choice_a_text": "Both qualify - Alpha (5 years exactly) and Beta (3.2 years)", 
         "choice_a_exp_reward": 100, "choice_a_cash_change": 200, "choice_a_reputation_change": 4,
         "choice_a_feedback": "Correct! Alpha: 500K/100K = 5 years (barely qualifies). Beta: 800K/250K = 3.2 years (comfortably qualifies). Both work, but Beta is safer.",
         "choice_b_text": "Only Beta qualifies - 3.2 years beats Alpha's 5 years, which doesn't meet 'within' 5 years", 
         "choice_b_exp_reward": 80, "choice_b_cash_change": 100, "choice_b_reputation_change": 3,
         "choice_b_feedback": "Strict interpretation! 'Within 5 years' could mean <5 or ≤5. Beta definitely qualifies at 3.2 years. Always clarify contract terms!",
         "choice_c_text": "Choose Beta - faster payback AND higher annual returns after payback", 
         "choice_c_exp_reward": 120, "choice_c_cash_change": 300, "choice_c_reputation_change": 6,
         "choice_c_feedback": "Strategic thinking! Beta recovers faster AND generates 2.5× more annually afterward. This is how capital budgeting drives real decisions.", 
         "subskill_focus": "Capital Budgeting"},

        # ========== LEVEL 5: Debt Financing & Interest ==========
        # Modern World
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Finance", "required_level": 5,
         "scenario_title": "L5: Debt Financing & Interest", 
         "scenario_narrative": "You need $100,000 for expansion. Three loan options: Bank A: 8% interest, 5-year term, $20,280/year payments. Bank B: 6% interest, 10-year term, $13,590/year payments. Bank C: 10% interest, 3-year term, $40,210/year payments. Which minimizes total interest paid?",
         "choice_a_text": "Bank C (3 years) - $40,210 × 3 = $120,630 total, only $20,630 interest", 
         "choice_a_exp_reward": 120, "choice_a_cash_change": -200, "choice_a_reputation_change": 6,
         "choice_a_feedback": "Mathematically optimal! Despite highest rate, shortest term = least interest. A: $101,400 paid, B: $135,900 paid, C: $120,630 paid. Time is money!",
         "choice_b_text": "Bank B (6%) - lowest rate means lowest total cost", 
         "choice_b_exp_reward": 60, "choice_b_cash_change": 0, "choice_b_reputation_change": 2,
         "choice_b_feedback": "Common mistake! B's low rate over 10 years = $35,900 total interest. C's high rate over 3 years = only $20,630 interest. Duration matters more!",
         "choice_c_text": "Bank A - middle ground balances rate and term", 
         "choice_c_exp_reward": 80, "choice_c_cash_change": -100, "choice_c_reputation_change": 3,
         "choice_c_feedback": "A pays $101,400 total ($1,400 interest), better than B but not optimal. Sometimes the middle option isn't the best financial choice.", 
         "subskill_focus": "Debt Financing"},
        
        # Fantasy World
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Finance", "required_level": 5,
         "scenario_title": "L5: Debt Financing & Interest", 
         "scenario_narrative": "You need 5,000 gold for a tavern upgrade. The Dwarven Banking Guild offers: Secured loan (artifact collateral) at 4% for 5 years OR Unsecured loan at 8% for 5 years. You have a 3,000 gold family heirloom artifact. What's the smarter choice?",
         "choice_a_text": "Secured loan (4%) - 5,000 × 0.04 × 5 = 1,000 gold interest total", 
         "choice_a_exp_reward": 110, "choice_a_cash_change": 200, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Smart leverage! Using collateral saves 1,000 gold in interest (2,000 vs 1,000). As long as you make payments, the artifact stays safe.",
         "choice_b_text": "Unsecured loan (8%) - never risk the family heirloom", 
         "choice_b_exp_reward": 80, "choice_b_cash_change": -200, "choice_b_reputation_change": 3,
         "choice_b_feedback": "Emotional decision, not financial. 8% = 2,000 gold interest. The extra 1,000 gold 'buys' peace of mind. Valid if you doubt repayment ability.",
         "choice_c_text": "Take the secured loan but hide the artifact's true value", 
         "choice_c_exp_reward": 40, "choice_c_cash_change": -500, "choice_c_reputation_change": -5,
         "choice_c_feedback": "Fraud! Misrepresenting collateral is a serious offense. The Dwarven Guild will blacklist you. Honesty is the best policy in finance.", 
         "subskill_focus": "Debt Financing"},
        
        # Sci-Fi World
        {"world_type": "Sci-Fi", "industry": "Mining Corp", "discipline": "Finance", "required_level": 5,
         "scenario_title": "L5: Debt Financing & Interest", 
         "scenario_narrative": "You need 1,000,000 credits for a new mining vessel. The Galactic Trade Federation offers: Fixed rate 7% for 10 years OR Variable rate starting at 5% (could rise to 12%). Your economists predict rates will rise. Which structure protects you?",
         "choice_a_text": "Fixed 7% - lock in the rate to protect against predicted increases", 
         "choice_a_exp_reward": 120, "choice_a_cash_change": 300, "choice_a_reputation_change": 6,
         "choice_a_feedback": "Correct hedging strategy! If rates rise to 12%, variable costs explode. Fixed at 7% provides certainty. In rising rate environments, lock in!",
         "choice_b_text": "Variable starting at 5% - we save 2% initially and can refinance later", 
         "choice_b_exp_reward": 70, "choice_b_cash_change": -200, "choice_b_reputation_change": 2,
         "choice_b_feedback": "Gambling against your own prediction! If rates rise to 12%, you'll wish for 7%. Refinancing isn't guaranteed in high-rate environments.",
         "choice_c_text": "Take variable but hedge with interest rate derivatives", 
         "choice_c_exp_reward": 100, "choice_c_cash_change": 100, "choice_c_reputation_change": 5,
         "choice_c_feedback": "Sophisticated! Interest rate swaps can cap your exposure. This is how large corporations manage variable rate risk. Advanced finance!", 
         "subskill_focus": "Debt Financing"},

        # ========== LEVEL 6: Risk and Return ==========
        # Modern World
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Finance", "required_level": 6,
         "scenario_title": "L6: Risk and Return Tradeoff", 
         "scenario_narrative": "You have $50,000 to invest. Option A: Expand current location - 80% chance of 15% return, 20% chance of -5% return. Option B: Open new location - 50% chance of 40% return, 50% chance of -20% return. Calculate the expected return.",
         "choice_a_text": "Option A: Expected return = (0.8 × 15%) + (0.2 × -5%) = 11% with lower risk", 
         "choice_a_exp_reward": 120, "choice_a_cash_change": 550, "choice_a_reputation_change": 6,
         "choice_a_feedback": "Perfect expected value calculation! A = 12% - 1% = 11%. B = 20% - 10% = 10%. A has BOTH higher expected return AND lower risk. Clear winner!",
         "choice_b_text": "Option B: 40% potential upside is too attractive to pass up", 
         "choice_b_exp_reward": 70, "choice_b_cash_change": -100, "choice_b_reputation_change": 2,
         "choice_b_feedback": "Chasing upside ignores expected value! B's expected return (10%) is actually lower than A (11%), with MORE risk. Do the math first.",
         "choice_c_text": "Split 50/50 between both options for diversification", 
         "choice_c_exp_reward": 90, "choice_c_cash_change": 200, "choice_c_reputation_change": 4,
         "choice_c_feedback": "Diversification reduces risk but blends expected returns. You get ~10.5% expected return with moderate risk. Not optimal here, but valid strategy.", 
         "subskill_focus": "Risk Management"},
        
        # Fantasy World
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Finance", "required_level": 6,
         "scenario_title": "L6: Risk and Return Tradeoff", 
         "scenario_narrative": "A merchant offers investments: Dragon Trade Route - 30% chance of 100% return, 70% chance of total loss. Safe Kingdom Bonds - guaranteed 8% return. How much of your 1,000 gold should you risk on dragons?",
         "choice_a_text": "Zero on dragons - expected return is (0.3 × 100%) + (0.7 × -100%) = -40%, negative!", 
         "choice_a_exp_reward": 110, "choice_a_cash_change": 80, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Excellent expected value analysis! Dragon route EV = 30% - 70% = -40%. Never invest in negative expected value propositions, regardless of upside!",
         "choice_b_text": "100 gold on dragons - small bet, big potential payoff", 
         "choice_b_exp_reward": 60, "choice_b_cash_change": -100, "choice_b_reputation_change": 2,
         "choice_b_feedback": "Even small bets on -40% EV are mathematically foolish. 10% of capital in negative EV = -40 gold expected loss. Only the Kingdom Bonds make sense.",
         "choice_c_text": "Calculate the Kelly Criterion for optimal bet sizing", 
         "choice_c_exp_reward": 100, "choice_c_cash_change": 0, "choice_c_reputation_change": 5,
         "choice_c_feedback": "Advanced thinking! Kelly Criterion says bet zero when edge is negative. For positive EV bets, Kelly = (probability × payout - loss probability) / payout.", 
         "subskill_focus": "Risk Management"},
        
        # Sci-Fi World
        {"world_type": "Sci-Fi", "industry": "Mining Corp", "discipline": "Finance", "required_level": 6,
         "scenario_title": "L6: Risk and Return Tradeoff", 
         "scenario_narrative": "Board allocation decision: Safe Asteroid (proven deposits) - guaranteed 12% annual return. Speculative Asteroid (unproven) - 40% chance of 50% return, 40% chance of 10% return, 20% chance of total loss. What's the risk-adjusted recommendation?",
         "choice_a_text": "Safe Asteroid - 12% guaranteed beats Speculative's 14% expected return given the 20% loss risk", 
         "choice_a_exp_reward": 100, "choice_a_cash_change": 120, "choice_a_reputation_change": 4,
         "choice_a_feedback": "Risk-averse choice! Speculative EV = (0.4×50) + (0.4×10) + (0.2×-100) = 20% + 4% - 20% = 4%. Safe at 12% is definitely better than risky 4%!",
         "choice_b_text": "Speculative - EV = (0.4 × 50%) + (0.4 × 10%) + (0.2 × -100%) = 4%, but upside matters", 
         "choice_b_exp_reward": 70, "choice_b_cash_change": -200, "choice_b_reputation_change": 2,
         "choice_b_feedback": "You calculated correctly (4% EV) but chose poorly! 4% expected return with loss risk vs 12% guaranteed. Sharpe ratio strongly favors Safe.",
         "choice_c_text": "Speculative EV is 24% (20% + 4% + 0%), triple the Safe return", 
         "choice_c_exp_reward": 50, "choice_c_cash_change": 0, "choice_c_reputation_change": 1,
         "choice_c_feedback": "Calculation error! Loss probability means NEGATIVE contribution: 0.2 × -100% = -20%. Correct EV = 20% + 4% - 20% = 4%. Always account for losses!", 
         "subskill_focus": "Risk Management"},

        # ========== LEVEL 7: Discounted Cash Flow (DCF) & NPV ==========
        # Modern World
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Finance", "required_level": 7,
         "scenario_title": "L7: Discounted Cash Flow & NPV", 
         "scenario_narrative": "A 5-year catering contract offers $20,000 annual payments. At a 10% discount rate, what's the Net Present Value? Use: NPV = CF/(1+r)¹ + CF/(1+r)² + ... Your Finance Director needs this for the board.",
         "choice_a_text": "NPV = $75,816 (sum of $18,182 + $16,529 + $15,026 + $13,660 + $12,419)", 
         "choice_a_exp_reward": 130, "choice_a_cash_change": 758, "choice_a_reputation_change": 7,
         "choice_a_feedback": "Perfect DCF calculation! Each year's $20K is discounted: Y1=18,182, Y2=16,529, Y3=15,026, Y4=13,660, Y5=12,419. Total PV = $75,816. CFO-level skill!",
         "choice_b_text": "NPV = $100,000 - just multiply $20,000 × 5 years", 
         "choice_b_exp_reward": 50, "choice_b_cash_change": 0, "choice_b_reputation_change": 1,
         "choice_b_feedback": "That ignores time value! $20K in year 5 is worth less than $20K today. At 10% discount, future dollars are worth progressively less.",
         "choice_c_text": "NPV = $90,000 - discount the total by 10%", 
         "choice_c_exp_reward": 60, "choice_c_cash_change": 0, "choice_c_reputation_change": 2,
         "choice_c_feedback": "Discount applies year-by-year, not to the total! Year 1 is divided by 1.1, Year 2 by 1.21, etc. The correct NPV is $75,816.", 
         "subskill_focus": "DCF Valuation"},
        
        # Fantasy World
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Finance", "required_level": 7,
         "scenario_title": "L7: Discounted Cash Flow & NPV", 
         "scenario_narrative": "The Royal Court offers a 3-year exclusive supply contract: 500 gold per year. A rival offers 1,400 gold upfront today. At 8% discount rate, which deal has higher present value?",
         "choice_a_text": "Contract NPV = 500/1.08 + 500/1.1664 + 500/1.2597 = 463 + 429 + 397 = 1,289 gold. Take the 1,400 upfront!", 
         "choice_a_exp_reward": 130, "choice_a_cash_change": 140, "choice_a_reputation_change": 7,
         "choice_a_feedback": "Masterful DCF! Contract PV = 1,289 gold < 1,400 upfront. The rival's offer is worth 111 gold more in present value terms. Excellent analysis!",
         "choice_b_text": "Contract total is 1,500 gold vs 1,400 upfront - take the contract", 
         "choice_b_exp_reward": 60, "choice_b_cash_change": -110, "choice_b_reputation_change": 2,
         "choice_b_feedback": "You ignored discounting! 1,500 nominal > 1,400, but 1,289 present value < 1,400. Time value matters. The upfront offer is genuinely better.",
         "choice_c_text": "They're roughly equal - take whichever has less risk", 
         "choice_c_exp_reward": 80, "choice_c_cash_change": 0, "choice_c_reputation_change": 3,
         "choice_c_feedback": "Risk adjustment is valid! Contract has counterparty risk over 3 years. Upfront eliminates that. But mathematically, upfront is still better by 111 gold PV.", 
         "subskill_focus": "DCF Valuation"},
        
        # Sci-Fi World
        {"world_type": "Sci-Fi", "industry": "Mining Corp", "discipline": "Finance", "required_level": 7,
         "scenario_title": "L7: Discounted Cash Flow & NPV", 
         "scenario_narrative": "Evaluate an asteroid mining project: Initial investment 500,000 credits. Expected cash flows: Year 1: 150K, Year 2: 200K, Year 3: 250K, Year 4: 200K. At 12% discount rate, what's the NPV? Should we invest?",
         "choice_a_text": "NPV = -500K + 134K + 159K + 178K + 127K = +98K. Positive NPV = invest!", 
         "choice_a_exp_reward": 130, "choice_a_cash_change": 980, "choice_a_reputation_change": 7,
         "choice_a_feedback": "Excellent! Y1: 150/1.12=134K, Y2: 200/1.2544=159K, Y3: 250/1.4049=178K, Y4: 200/1.5735=127K. Total PV=598K. NPV=598K-500K=+98K. Invest!",
         "choice_b_text": "Total cash flows are 800K vs 500K investment = 300K profit. Easy yes!", 
         "choice_b_exp_reward": 60, "choice_b_cash_change": 0, "choice_b_reputation_change": 2,
         "choice_b_feedback": "Nominal profit ignores time value! The real present value of those cash flows is 598K, giving only 98K NPV. Still positive, but less than you thought.",
         "choice_c_text": "NPV is negative after discounting - don't invest", 
         "choice_c_exp_reward": 40, "choice_c_cash_change": -200, "choice_c_reputation_change": 0,
         "choice_c_feedback": "Calculation error! NPV = +98K, which is positive. Always double-check your discounting. Positive NPV projects create shareholder value.", 
         "subskill_focus": "DCF Valuation"},

        # ========== LEVEL 8: Cost of Capital (WACC) ==========
        # Modern World
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Finance", "required_level": 8,
         "scenario_title": "L8: Weighted Average Cost of Capital (WACC)", 
         "scenario_narrative": "Your capital structure: 60% equity (investors expect 15% return) and 40% debt (6% interest rate, 25% tax rate). Calculate WACC to determine the minimum return any project must earn.",
         "choice_a_text": "WACC = (0.6 × 15%) + (0.4 × 6% × 0.75) = 9% + 1.8% = 10.8%", 
         "choice_a_exp_reward": 140, "choice_a_cash_change": 500, "choice_a_reputation_change": 8,
         "choice_a_feedback": "Perfect WACC calculation! Equity cost: 9%, After-tax debt cost: 1.8%, WACC: 10.8%. Any project returning less than 10.8% destroys shareholder value!",
         "choice_b_text": "WACC = (0.6 × 15%) + (0.4 × 6%) = 9% + 2.4% = 11.4%", 
         "choice_b_exp_reward": 80, "choice_b_cash_change": 0, "choice_b_reputation_change": 3,
         "choice_b_feedback": "Close! You forgot the tax shield. Interest is tax-deductible, so after-tax debt cost = 6% × (1 - 0.25) = 4.5%, not 6%. WACC = 10.8%.",
         "choice_c_text": "Just average 15% and 6% = 10.5% is good enough", 
         "choice_c_exp_reward": 50, "choice_c_cash_change": 0, "choice_c_reputation_change": 1,
         "choice_c_feedback": "Weighted average requires weights! 50/50 would give 10.5%, but your actual mix is 60/40. Also, tax shield matters. Precision matters in finance!", 
         "subskill_focus": "Cost of Capital"},
        
        # Fantasy World
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Finance", "required_level": 8,
         "scenario_title": "L8: Weighted Average Cost of Capital (WACC)", 
         "scenario_narrative": "Your tavern's funding: 70% from a Noble Patron (expects 20% return on investment) and 30% from Dwarven Bank (8% interest, no tax benefit in the kingdom). What's your WACC?",
         "choice_a_text": "WACC = (0.7 × 20%) + (0.3 × 8%) = 14% + 2.4% = 16.4%", 
         "choice_a_exp_reward": 130, "choice_a_cash_change": 300, "choice_a_reputation_change": 7,
         "choice_a_feedback": "Correct! Without tax benefits, debt cost stays at 8%. Your 16.4% WACC means any expansion must return at least 16.4% to satisfy all capital providers.",
         "choice_b_text": "Just use the 20% equity return - that's what matters to the Noble", 
         "choice_b_exp_reward": 60, "choice_b_cash_change": -100, "choice_b_reputation_change": 2,
         "choice_b_feedback": "WACC blends all capital costs! Using only equity cost ignores the cheaper debt financing. Your true hurdle rate is 16.4%, not 20%.",
         "choice_c_text": "Use the 8% debt rate - it's the cheapest option", 
         "choice_c_exp_reward": 50, "choice_c_cash_change": -100, "choice_c_reputation_change": 1,
         "choice_c_feedback": "Debt is cheaper but you can't fund everything with debt! WACC reflects your actual capital mix. Projects must return 16.4% overall.", 
         "subskill_focus": "Cost of Capital"},
        
        # Sci-Fi World
        {"world_type": "Sci-Fi", "industry": "Mining Corp", "discipline": "Finance", "required_level": 8,
         "scenario_title": "L8: Weighted Average Cost of Capital (WACC)", 
         "scenario_narrative": "Your mining corp: 50% equity (shareholders want 18% return), 30% senior debt (5% rate), 20% junior debt (10% rate). Corporate tax is 20%. Calculate WACC.",
         "choice_a_text": "WACC = (0.5 × 18%) + (0.3 × 5% × 0.8) + (0.2 × 10% × 0.8) = 9% + 1.2% + 1.6% = 11.8%", 
         "choice_a_exp_reward": 140, "choice_a_cash_change": 400, "choice_a_reputation_change": 8,
         "choice_a_feedback": "Expert-level WACC! Multiple debt tranches each get tax-adjusted: Senior after-tax: 4%, Junior after-tax: 8%. Total WACC: 11.8%. Minimum acceptable project return!",
         "choice_b_text": "Average all rates: (18% + 5% + 10%) / 3 = 11%", 
         "choice_b_exp_reward": 50, "choice_b_cash_change": 0, "choice_b_reputation_change": 1,
         "choice_b_feedback": "Simple average ignores weights and tax benefits! Your capital structure weights are 50/30/20, not equal. Precision in WACC = precision in decisions.",
         "choice_c_text": "WACC = 9% + 1.5% + 2% = 12.5%", 
         "choice_c_exp_reward": 70, "choice_c_cash_change": 0, "choice_c_reputation_change": 2,
         "choice_c_feedback": "Close but check your tax adjustment! After-tax debt = rate × (1 - tax rate) = rate × 0.8, not rate × 0.9. Correct WACC is 11.8%.", 
         "subskill_focus": "Cost of Capital"},

        # ========== LEVEL 9: Equity Financing & Dilution ==========
        # Modern World
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Finance", "required_level": 9,
         "scenario_title": "L9: Equity Financing & Dilution", 
         "scenario_narrative": "An Angel Investor offers $500,000 for 20% of your company. You currently own 100% of 1,000,000 shares. After investment, what's the post-money valuation, and how many shares does the investor get?",
         "choice_a_text": "Post-money: $2.5M ($500K ÷ 20%). Investor gets 250,000 new shares (25% of 1M = 20% of 1.25M)", 
         "choice_a_exp_reward": 140, "choice_a_cash_change": 5000, "choice_a_reputation_change": 8,
         "choice_a_feedback": "Perfect! Post-money = Investment ÷ Ownership = $2.5M. Issue 250K new shares so investor has 250K/1.25M = 20%. Your 1M shares = 80%. Dilution math mastered!",
         "choice_b_text": "Give investor 200,000 of my existing shares (20% of 1,000,000)", 
         "choice_b_exp_reward": 60, "choice_b_cash_change": 0, "choice_b_reputation_change": 2,
         "choice_b_feedback": "Selling YOUR shares means the money goes to you, not the company! For company funding, issue NEW shares. This is a crucial distinction.",
         "choice_c_text": "Post-money: $2M pre-money + $500K = $2.5M, but investor gets 500K shares for 50%", 
         "choice_c_exp_reward": 50, "choice_c_cash_change": 0, "choice_c_reputation_change": 1,
         "choice_c_feedback": "Math error! 500K shares out of 1.5M total = 33%, not 50% or 20%. To get exactly 20%, investor needs 250K shares (20% of 1.25M total).", 
         "subskill_focus": "Equity Financing"},
        
        # Fantasy World
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Finance", "required_level": 9,
         "scenario_title": "L9: Equity Financing & Dilution", 
         "scenario_narrative": "A Royal Patron offers 10,000 gold for 25% ownership of future tax revenues (equity equivalent). Your tavern currently generates 2,000 gold annual profit. What implicit valuation is the Patron offering, and should you accept?",
         "choice_a_text": "Implied valuation: 40,000 gold (10,000 ÷ 25%). At 2,000/year profit, that's 20x earnings - generous!", 
         "choice_a_exp_reward": 130, "choice_a_cash_change": 1000, "choice_a_reputation_change": 7,
         "choice_a_feedback": "Excellent valuation analysis! 10K/25% = 40K post-money value. 40K ÷ 2K profit = 20x P/E ratio. For a tavern, that's premium. Accept if you need growth capital!",
         "choice_b_text": "Bad deal - you're giving up 25% forever for just 5 years of profit", 
         "choice_b_exp_reward": 80, "choice_b_cash_change": 0, "choice_b_reputation_change": 3,
         "choice_b_feedback": "Valid concern! But if the 10K capital grows profits to 5K/year, you keep 75% of 5K = 3,750 vs 100% of 2K = 2K. Growth potential matters!",
         "choice_c_text": "Counter-offer: 10,000 gold for 15% instead of 25%", 
         "choice_c_exp_reward": 110, "choice_c_cash_change": 500, "choice_c_reputation_change": 6,
         "choice_c_feedback": "Negotiation! 15% implies 67K valuation (10K ÷ 15% = 66.7K), or 33x earnings. Ambitious but shows financial sophistication. The Patron may counter-offer.", 
         "subskill_focus": "Equity Financing"},
        
        # Sci-Fi World
        {"world_type": "Sci-Fi", "industry": "Mining Corp", "discipline": "Finance", "required_level": 9,
         "scenario_title": "L9: Equity Financing & Dilution", 
         "scenario_narrative": "A Venture Capital firm offers 5,000,000 credits for 30% equity. They want 2x liquidation preference and anti-dilution protection. You currently own 100%. What do these terms mean for your exit scenarios?",
         "choice_a_text": "2x preference means in a sale, VC gets 10M credits (2 × 5M) before you get anything", 
         "choice_a_exp_reward": 140, "choice_a_cash_change": 0, "choice_a_reputation_change": 8,
         "choice_a_feedback": "Correct! Liquidation preference protects downside. If company sells for 15M: VC takes 10M first, you split remaining 5M (70% = 3.5M). Preferences matter more than percentages!",
         "choice_b_text": "With 30% ownership, in a 20M sale, VC gets 6M (30%) and you get 14M (70%)", 
         "choice_b_exp_reward": 60, "choice_b_cash_change": 0, "choice_b_reputation_change": 2,
         "choice_b_feedback": "That ignores liquidation preference! VC takes 10M first, then 30% of remaining 10M = 3M more. VC total: 13M, You: 7M. Preferences > percentages!",
         "choice_c_text": "Anti-dilution protects you from future investor dilution", 
         "choice_c_exp_reward": 50, "choice_c_cash_change": -500, "choice_c_reputation_change": 1,
         "choice_c_feedback": "Backwards! Anti-dilution protects the VC. If future rounds are at lower valuations, VC gets extra shares to maintain value. Founders get diluted more.", 
         "subskill_focus": "Equity Financing"},

        # ========== LEVEL 10: Mergers & Acquisitions (M&A) ==========
        # Modern World
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Finance", "required_level": 10,
         "scenario_title": "L10: Mergers & Acquisitions", 
         "scenario_narrative": "A restaurant chain offers to acquire you. They propose: $2M cash + $1M in their stock + $500K earnout based on 2-year performance. Your last valuation was $3M. Your advisor asks: 'How do you evaluate this offer?'",
         "choice_a_text": "Total value ~$3.5M but quality varies: $2M certain, $1M stock risky, $500K earnout uncertain", 
         "choice_a_exp_reward": 150, "choice_a_cash_change": 2000, "choice_a_reputation_change": 10,
         "choice_a_feedback": "Masterful deal analysis! Cash is certain, stock depends on acquirer performance, earnout requires hitting targets. Risk-adjusted value is closer to $3M. Sophisticated M&A thinking!",
         "choice_b_text": "$3.5M total exceeds $3M valuation - accept immediately", 
         "choice_b_exp_reward": 70, "choice_b_cash_change": 0, "choice_b_reputation_change": 3,
         "choice_b_feedback": "Headline value vs real value! Stock can decline, earnouts often go unpaid (40% industry failure rate). Always discount non-cash components.",
         "choice_c_text": "Counter with $3M all-cash to eliminate uncertainty", 
         "choice_c_exp_reward": 120, "choice_c_cash_change": 1500, "choice_c_reputation_change": 8,
         "choice_c_feedback": "Strong negotiating position! Trading $500K nominal for certainty is often worthwhile. All-cash deals close faster and eliminate integration risk.", 
         "subskill_focus": "M&A Valuation"},
        
        # Fantasy World
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Finance", "required_level": 10,
         "scenario_title": "L10: Mergers & Acquisitions", 
         "scenario_narrative": "The Grand Innkeepers Guild wants to acquire your successful tavern. They offer: 50,000 gold upfront + 10% of combined profits for 5 years + a seat on their Council. Your tavern profits 5,000 gold yearly. Is this a good deal?",
         "choice_a_text": "Analyze: 50K upfront (10x current profit) + future share of larger pie + strategic value of Council seat", 
         "choice_a_exp_reward": 150, "choice_a_cash_change": 500, "choice_a_reputation_change": 10,
         "choice_a_feedback": "Executive-level thinking! 10x profit multiple is fair. 10% of Guild profits could exceed your current 5K. Council seat provides strategic influence. Synergies matter in M&A!",
         "choice_b_text": "Reject - I built this tavern and won't sell my legacy", 
         "choice_b_exp_reward": 70, "choice_b_cash_change": 0, "choice_b_reputation_change": 5,
         "choice_b_feedback": "Emotional decisions aren't always wrong. But consider: with 50K capital and Guild resources, you could build something bigger. Legacy can evolve.",
         "choice_c_text": "Counter: 60K upfront + 15% profit share + two Council seats", 
         "choice_c_exp_reward": 130, "choice_c_cash_change": 600, "choice_c_reputation_change": 8,
         "choice_c_feedback": "Negotiation in action! 20% premium on cash, increased profit share, more governance power. They'll counter-offer, but you've established your value.", 
         "subskill_focus": "M&A Valuation"},
        
        # Sci-Fi World
        {"world_type": "Sci-Fi", "industry": "Mining Corp", "discipline": "Finance", "required_level": 10,
         "scenario_title": "L10: Mergers & Acquisitions", 
         "scenario_narrative": "The Galactic Mining Consortium offers to acquire your company. Terms: 20,000,000 credits in Consortium stock (currently trading at 100 credits/share) OR 15,000,000 credits cash. Your DCF valuation shows 18,000,000 credits. How do you evaluate?",
         "choice_a_text": "Stock offer is nominally higher but risky. Cash at 15M is 83% of intrinsic value - negotiate for 17M cash.", 
         "choice_a_exp_reward": 150, "choice_a_cash_change": 1700, "choice_a_reputation_change": 10,
         "choice_a_feedback": "CEO-level analysis! Stock can decline post-merger. 15M certain > 20M uncertain for risk-averse sellers. Negotiating to 17M (94% of DCF) is realistic. M&A mastery achieved!",
         "choice_b_text": "Take the 20M in stock - it's worth more than the 18M DCF valuation", 
         "choice_b_exp_reward": 80, "choice_b_cash_change": 0, "choice_b_reputation_change": 4,
         "choice_b_feedback": "Stock value isn't guaranteed! Acquisition stocks often drop 10-20% post-deal. 20M could become 16M. Always discount stock offers for execution risk.",
         "choice_c_text": "Walk away - neither offer meets the 18M DCF valuation", 
         "choice_c_exp_reward": 90, "choice_c_cash_change": 0, "choice_c_reputation_change": 5,
         "choice_c_feedback": "DCF is one estimate, not absolute truth. 15M cash represents 83% of DCF - many sellers accept that for certainty. Sometimes good-enough deals beat perfect ones.", 
         "subskill_focus": "M&A Valuation"},
    ]
    
    for scenario in scenarios:
        cur.execute("""
            INSERT INTO scenario_master (world_type, industry, discipline, required_level, scenario_title, scenario_narrative,
                choice_a_text, choice_a_exp_reward, choice_a_cash_change, choice_a_reputation_change, choice_a_feedback,
                choice_b_text, choice_b_exp_reward, choice_b_cash_change, choice_b_reputation_change, choice_b_feedback,
                choice_c_text, choice_c_exp_reward, choice_c_cash_change, choice_c_reputation_change, choice_c_feedback,
                subskill_focus)
            VALUES (%(world_type)s, %(industry)s, %(discipline)s, %(required_level)s, %(scenario_title)s, %(scenario_narrative)s,
                %(choice_a_text)s, %(choice_a_exp_reward)s, %(choice_a_cash_change)s, %(choice_a_reputation_change)s, %(choice_a_feedback)s,
                %(choice_b_text)s, %(choice_b_exp_reward)s, %(choice_b_cash_change)s, %(choice_b_reputation_change)s, %(choice_b_feedback)s,
                %(choice_c_text)s, %(choice_c_exp_reward)s, %(choice_c_cash_change)s, %(choice_c_reputation_change)s, %(choice_c_feedback)s,
                %(subskill_focus)s)
        """, scenario)
    
    conn.commit()
    print(f"Seeded {len(scenarios)} Finance Curriculum scenarios (Levels 1-10, 3 worlds)!")
    cur.close()
    conn.close()


def seed_legal_curriculum():
    """Seed the complete 10-level Legal Curriculum across 3 worlds (30 scenarios total).
    
    Curriculum Structure:
    - L1-L3: Foundational Structure & Contracts (Entity Structure, Contract Essentials, Employee Agreements)
    - L4-L6: Real Estate & Compliance (Leases, Licensing/Permits, Torts/Negligence)
    - L7-L8: Intellectual Property (Trademarks, Patents/Trade Secrets)
    - L9-L10: Strategy & Mastery (Litigation, International Law)
    """
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM scenario_master WHERE discipline = 'Legal' AND scenario_title LIKE 'L%:%'")
    result = cur.fetchone()
    if result['count'] >= 30:
        print("Legal curriculum already seeded.")
        cur.close()
        conn.close()
        return
    
    scenarios = [
        # ========== LEVEL 1: Business Entity Structure ==========
        # Modern World
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Legal", "required_level": 1,
         "scenario_title": "L1: Business Entity Structure", 
         "scenario_narrative": "You're opening your first restaurant. A lawyer asks: 'How do you want to structure the business?' As a Sole Proprietor, the business is simple but you're personally liable for all debts. As a Corporation (LLC), there's more paperwork but your personal assets are protected.",
         "choice_a_text": "Form an LLC - I want liability protection for my personal assets", 
         "choice_a_exp_reward": 50, "choice_a_cash_change": -500, "choice_a_reputation_change": 3,
         "choice_a_feedback": "Smart choice! An LLC creates a 'corporate veil' separating business debts from personal assets. If the restaurant is sued, your house and savings are protected. The filing fee is worth the peace of mind.",
         "choice_b_text": "Sole Proprietorship - simpler and cheaper to start", 
         "choice_b_exp_reward": 30, "choice_b_cash_change": 0, "choice_b_reputation_change": 1,
         "choice_b_feedback": "Simpler, yes, but risky! If a customer sues and wins $500,000, they can take your personal savings, car, even your home. For any business with liability risk, incorporation is essential.",
         "choice_c_text": "I'll decide later once the business is profitable", 
         "choice_c_exp_reward": 20, "choice_c_cash_change": 0, "choice_c_reputation_change": 0,
         "choice_c_feedback": "Dangerous delay! Liability exists from day one. If someone slips on opening day and you're a sole proprietor, your personal assets are immediately at risk. Structure first, operate second.", 
         "subskill_focus": "Business Formation"},
        
        # Fantasy World
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Legal", "required_level": 1,
         "scenario_title": "L1: Business Entity Structure", 
         "scenario_narrative": "The Guild Registrar asks how you wish to establish your tavern. A 'Personal Charter' means you own everything but bear all risks personally. A 'Guild-Protected Charter' costs 200 gold but shields your personal holdings from business debts.",
         "choice_a_text": "Guild-Protected Charter - shield my family estate from tavern debts", 
         "choice_a_exp_reward": 50, "choice_a_cash_change": -200, "choice_a_reputation_change": 3,
         "choice_a_feedback": "Wise decision! The Guild Charter creates legal separation. If a dragon destroys your tavern and you owe suppliers, they cannot claim your family home. This is the medieval equivalent of incorporation!",
         "choice_b_text": "Personal Charter - I trust my tavern will succeed without extra cost", 
         "choice_b_exp_reward": 30, "choice_b_cash_change": 0, "choice_b_reputation_change": 1,
         "choice_b_feedback": "Optimism isn't a legal strategy! One bad barrel of ale that sickens nobles could result in claims exceeding your tavern's worth. Without protection, they'll seize your family lands.",
         "choice_c_text": "Ask the Registrar which other successful taverns chose", 
         "choice_c_exp_reward": 40, "choice_c_cash_change": 0, "choice_c_reputation_change": 2,
         "choice_c_feedback": "Research is good! You learn that 9 of 10 successful taverns chose Guild-Protected Charters. The 200 gold is standard insurance for any business serving the public.", 
         "subskill_focus": "Business Formation"},
        
        # Sci-Fi World
        {"world_type": "Sci-Fi", "industry": "Mining Corp", "discipline": "Legal", "required_level": 1,
         "scenario_title": "L1: Business Entity Structure", 
         "scenario_narrative": "Galactic Commerce Authority requires you to register your mining operation. Option A: 'Individual Operator License' - simple, but you're personally liable for mining accidents. Option B: 'Limited Liability Corporation' - more complex, but corporate structure limits personal exposure.",
         "choice_a_text": "LLC registration - mining is dangerous, I need liability shields", 
         "choice_a_exp_reward": 50, "choice_a_cash_change": -1000, "choice_a_reputation_change": 3,
         "choice_a_feedback": "Essential for mining! Space mining accidents can cause millions in damages. LLC structure means creditors can only claim corporate assets, not your personal spacecraft or colony residence.",
         "choice_b_text": "Individual License - fewer regulations and reporting requirements", 
         "choice_b_exp_reward": 25, "choice_b_cash_change": 0, "choice_b_reputation_change": 0,
         "choice_b_feedback": "Catastrophic risk! One asteroid drilling accident that damages a neighboring operation could result in claims of 10 million credits. As an individual, you'd face personal bankruptcy.",
         "choice_c_text": "Consult with a Galactic Commerce attorney before deciding", 
         "choice_c_exp_reward": 45, "choice_c_cash_change": -200, "choice_c_reputation_change": 2,
         "choice_c_feedback": "Professional advice is valuable! The attorney confirms: 'Any operation with injury or property damage potential needs LLC protection.' Mining definitely qualifies.", 
         "subskill_focus": "Business Formation"},

        # ========== LEVEL 2: Contract Essentials ==========
        # Modern World
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Legal", "required_level": 2,
         "scenario_title": "L2: Contract Essentials", 
         "scenario_narrative": "Your produce supplier sends a contract. Your lawyer explains a valid contract needs three elements: Offer (supplier promises weekly deliveries), Acceptance (you agree to the terms), and Consideration (you pay $2,000/month, they deliver produce). The contract is missing a signature line for you.",
         "choice_a_text": "Don't sign until they add proper acceptance provisions - contracts need all 3 elements", 
         "choice_a_exp_reward": 60, "choice_a_cash_change": 0, "choice_a_reputation_change": 3,
         "choice_a_feedback": "Excellent legal awareness! A contract without clear acceptance mechanism isn't properly formed. The signature line creates documented proof of acceptance. Never sign incomplete contracts.",
         "choice_b_text": "Sign it anyway - the offer and price are there, that's enough", 
         "choice_b_exp_reward": 30, "choice_b_cash_change": 0, "choice_b_reputation_change": 1,
         "choice_b_feedback": "Risky! While verbal acceptance can sometimes form contracts, you want written proof. If they fail to deliver and claim 'you never formally accepted,' you'll struggle in court.",
         "choice_c_text": "Email them your acceptance and keep the email as proof", 
         "choice_c_exp_reward": 50, "choice_c_cash_change": 0, "choice_c_reputation_change": 2,
         "choice_c_feedback": "Creative solution! Emails can constitute acceptance in many jurisdictions. However, a formal signed contract is cleaner. Request they update the document for professional completeness.", 
         "subskill_focus": "Contract Law"},
        
        # Fantasy World
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Legal", "required_level": 2,
         "scenario_title": "L2: Contract Essentials", 
         "scenario_narrative": "A merchant offers to supply your tavern with rare elven wine. He hands you a scroll stating: 'I will deliver 10 barrels monthly for 50 gold each.' For this to be a binding contract under Guild Law, what must you add?",
         "choice_a_text": "Add my written acceptance and what I'm providing in exchange (the 500 gold payment)", 
         "choice_a_exp_reward": 60, "choice_a_cash_change": 0, "choice_a_reputation_change": 3,
         "choice_a_feedback": "Perfect! You've identified all three elements: his Offer (wine delivery), your Acceptance (written agreement), and Consideration (500 gold monthly). This contract will be enforceable before the Guild Court.",
         "choice_b_text": "A handshake should be sufficient - we're honorable merchants", 
         "choice_b_exp_reward": 25, "choice_b_cash_change": 0, "choice_b_reputation_change": 0,
         "choice_b_feedback": "Honor doesn't replace documentation! If the merchant claims you agreed to 75 gold per barrel, how will you prove otherwise? Written contracts protect both parties.",
         "choice_c_text": "Just pay him the 500 gold - money proves there's an agreement", 
         "choice_c_exp_reward": 40, "choice_c_cash_change": -500, "choice_c_reputation_change": 1,
         "choice_c_feedback": "Payment shows consideration, but without documented terms, disputes become difficult. What if he delivers 8 barrels and claims that was the agreement? Always document terms.", 
         "subskill_focus": "Contract Law"},
        
        # Sci-Fi World
        {"world_type": "Sci-Fi", "industry": "Mining Corp", "discipline": "Legal", "required_level": 2,
         "scenario_title": "L2: Contract Essentials", 
         "scenario_narrative": "A fuel supplier transmits a digital contract for 100,000 credits of reactor fuel monthly. Your legal AI flags an issue: the contract contains an offer and price, but no acceptance mechanism and no specification of what happens if you don't pay (no consideration clause).",
         "choice_a_text": "Request amendments adding acceptance signature block and payment terms before proceeding", 
         "choice_a_exp_reward": 60, "choice_a_cash_change": 0, "choice_a_reputation_change": 3,
         "choice_a_feedback": "Correct! Interstellar commerce law requires all three elements: Offer (fuel terms), Acceptance (your agreement), Consideration (payment obligations). Incomplete contracts aren't enforceable in Galactic Court.",
         "choice_b_text": "The digital transmission itself counts as acceptance - proceed with operations", 
         "choice_b_exp_reward": 30, "choice_b_cash_change": 0, "choice_b_reputation_change": 1,
         "choice_b_feedback": "Receiving a contract isn't accepting it! You need affirmative acceptance. Also, without consideration terms, if they fail to deliver, you can't prove what they owed you.",
         "choice_c_text": "Have your legal AI draft a counter-proposal with all required elements", 
         "choice_c_exp_reward": 55, "choice_c_cash_change": -100, "choice_c_reputation_change": 3,
         "choice_c_feedback": "Proactive approach! A counter-proposal that includes all elements (Offer, Acceptance, Consideration) shifts the negotiation to proper legal ground. AI legal assistants are invaluable.", 
         "subskill_focus": "Contract Law"},

        # ========== LEVEL 3: Employee Agreements ==========
        # Modern World
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Legal", "required_level": 3,
         "scenario_title": "L3: Employee Agreements", 
         "scenario_narrative": "You're hiring a head chef who will learn your secret recipes. Your lawyer recommends an employment contract with an NDA (Non-Disclosure Agreement) preventing them from sharing recipes, and a non-compete clause. The chef hesitates at signing.",
         "choice_a_text": "Explain the NDA protects business secrets - it's standard practice for key employees", 
         "choice_a_exp_reward": 70, "choice_a_cash_change": 0, "choice_a_reputation_change": 4,
         "choice_a_feedback": "Professional approach! NDAs are standard for employees with access to trade secrets. Explain that it protects both parties - they can't be accused of theft if they follow the agreement. Most quality candidates understand this.",
         "choice_b_text": "Drop the NDA to make the chef more comfortable joining", 
         "choice_b_exp_reward": 30, "choice_b_cash_change": 0, "choice_b_reputation_change": 1,
         "choice_b_feedback": "Risky! Without an NDA, if the chef leaves and opens a competing restaurant using your secret recipes, you have no legal recourse. Protect your intellectual property.",
         "choice_c_text": "Offer a signing bonus in exchange for accepting the NDA terms", 
         "choice_c_exp_reward": 60, "choice_c_cash_change": -1000, "choice_c_reputation_change": 3,
         "choice_c_feedback": "Negotiation works! A signing bonus compensates for the restrictions. The chef feels valued, and you get the legal protection you need. Win-win when both parties gain something.", 
         "subskill_focus": "Employment Law"},
        
        # Fantasy World
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Legal", "required_level": 3,
         "scenario_title": "L3: Employee Agreements", 
         "scenario_narrative": "You're hiring a master brewer who knows your secret ale recipe. The Guild recommends a 'Secrecy Oath' (equivalent to an NDA) and a 'Non-Competition Covenant' preventing them from working at rival taverns for 2 years after leaving. The brewer wants to negotiate.",
         "choice_a_text": "Agree to reduce non-compete to 1 year but keep the full Secrecy Oath", 
         "choice_a_exp_reward": 70, "choice_a_cash_change": 0, "choice_a_reputation_change": 4,
         "choice_a_feedback": "Smart negotiation! The Secrecy Oath (protecting your recipe) is essential and non-negotiable. The non-compete duration can flex. 1 year is still meaningful protection while being fair to the brewer's career.",
         "choice_b_text": "Remove all restrictions - a good brewer will stay loyal without contracts", 
         "choice_b_exp_reward": 25, "choice_b_cash_change": 0, "choice_b_reputation_change": 0,
         "choice_b_feedback": "Naive! Loyalty is wonderful but not legally enforceable. If a rival offers triple wages, even honest people may be tempted. Contracts set clear boundaries everyone understands.",
         "choice_c_text": "Insist on all terms exactly as written - they can accept or leave", 
         "choice_c_exp_reward": 40, "choice_c_cash_change": 0, "choice_c_reputation_change": 1,
         "choice_c_feedback": "Inflexibility can cost you talent! Good employees expect reasonable negotiation. A 2-year non-compete may be excessive and could be unenforceable in some jurisdictions anyway.", 
         "subskill_focus": "Employment Law"},
        
        # Sci-Fi World
        {"world_type": "Sci-Fi", "industry": "Mining Corp", "discipline": "Legal", "required_level": 3,
         "scenario_title": "L3: Employee Agreements", 
         "scenario_narrative": "You're hiring a chief engineer who will have access to your proprietary asteroid scanning algorithms. Your legal team prepares a contract with an NDA, invention assignment clause (company owns any work-related inventions), and termination provisions. The engineer requests changes.",
         "choice_a_text": "Keep NDA and invention assignment, but negotiate fair termination terms", 
         "choice_a_exp_reward": 70, "choice_a_cash_change": 0, "choice_a_reputation_change": 4,
         "choice_a_feedback": "Balanced approach! The NDA and invention assignment protect core IP and are standard in tech. Termination terms (severance, notice period) are appropriate negotiation points. Protect IP, be fair on employment terms.",
         "choice_b_text": "Accept all their changes to secure this talented engineer quickly", 
         "choice_b_exp_reward": 30, "choice_b_cash_change": 0, "choice_b_reputation_change": 1,
         "choice_b_feedback": "Hasty! If you waive invention assignment and they develop a breakthrough using company resources, they could leave and patent it personally. Key IP protections aren't negotiable.",
         "choice_c_text": "Have legal AI analyze which clauses are essential vs. nice-to-have", 
         "choice_c_exp_reward": 65, "choice_c_cash_change": -100, "choice_c_reputation_change": 3,
         "choice_c_feedback": "Data-driven negotiation! The AI confirms: NDA and invention assignment are essential; specific termination terms are flexible. Now you know exactly what to protect and where to give.", 
         "subskill_focus": "Employment Law"},

        # ========== LEVEL 4: Leases and Property Law ==========
        # Modern World
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Legal", "required_level": 4,
         "scenario_title": "L4: Leases and Property Law", 
         "scenario_narrative": "Your 5-year restaurant lease is expiring. The landlord offers renewal at 20% higher rent. Your lawyer points out the lease contains a 'Tenant Improvement' clause - you invested $50,000 in kitchen upgrades that stay with the property if you leave.",
         "choice_a_text": "Negotiate: my improvements increased property value, so rent increase should be offset", 
         "choice_a_exp_reward": 80, "choice_a_cash_change": 200, "choice_a_reputation_change": 4,
         "choice_a_feedback": "Strong negotiating position! Your improvements benefit future tenants. A skilled negotiator would argue for reduced increase or tenant improvement credits. The landlord profits from your investment.",
         "choice_b_text": "Accept the 20% increase - moving costs would exceed the rent difference", 
         "choice_b_exp_reward": 50, "choice_b_cash_change": -200, "choice_b_reputation_change": 2,
         "choice_b_feedback": "You may be right about moving costs, but you left money on the table! Always negotiate before accepting. Even getting 15% instead of 20% saves significant money over 5 years.",
         "choice_c_text": "Threaten to remove all improvements before leaving if they don't negotiate", 
         "choice_c_exp_reward": 40, "choice_c_cash_change": 0, "choice_c_reputation_change": 0,
         "choice_c_feedback": "Check your lease! Most tenant improvement clauses specify improvements become landlord property. Threatening to remove them could breach your contract and create legal liability.", 
         "subskill_focus": "Property Law"},
        
        # Fantasy World
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Legal", "required_level": 4,
         "scenario_title": "L4: Leases and Property Law", 
         "scenario_narrative": "Your Royal Land Grant for the tavern expires next season. The Crown offers renewal but demands you allow Royal Inspectors access anytime, and you must use only 'approved' building materials (more expensive). Your current structure uses traditional timber.",
         "choice_a_text": "Negotiate inspector notice requirements and grandfather existing timber construction", 
         "choice_a_exp_reward": 80, "choice_a_cash_change": 0, "choice_a_reputation_change": 4,
         "choice_a_feedback": "Skilled negotiation! 'Grandfather clauses' exempt existing structures from new requirements. Reasonable notice for inspections (24 hours) balances Crown oversight with business operations.",
         "choice_b_text": "Accept all terms - arguing with the Crown is unwise", 
         "choice_b_exp_reward": 40, "choice_b_cash_change": -300, "choice_b_reputation_change": 1,
         "choice_b_feedback": "The Crown expects negotiation! Even royal grants have standard negotiation. Accepting everything signals you don't understand your rights. The approved materials clause alone costs you significantly.",
         "choice_c_text": "Seek alternative location outside Crown lands to avoid restrictions", 
         "choice_c_exp_reward": 50, "choice_c_cash_change": 0, "choice_c_reputation_change": 2,
         "choice_c_feedback": "Exploring alternatives is wise research! However, Crown lands have better trade routes and customer traffic. Sometimes constraints are worth the location benefits.", 
         "subskill_focus": "Property Law"},
        
        # Sci-Fi World
        {"world_type": "Sci-Fi", "industry": "Mining Corp", "discipline": "Legal", "required_level": 4,
         "scenario_title": "L4: Leases and Property Law", 
         "scenario_narrative": "Your orbital station lease requires renewal. The Station Authority demands you assume responsibility for gravity generator maintenance (previously their duty) and pay 30% more rent. Your operations depend on stable gravity.",
         "choice_a_text": "Counter-offer: accept maintenance responsibility in exchange for flat rent renewal", 
         "choice_a_exp_reward": 80, "choice_a_cash_change": 100, "choice_a_reputation_change": 4,
         "choice_a_feedback": "Excellent trade-off analysis! Taking maintenance responsibility gives you control over critical systems. Trading that for eliminating the 30% rent increase is good value if you have competent engineers.",
         "choice_b_text": "Reject maintenance transfer - too much liability if generators fail", 
         "choice_b_exp_reward": 50, "choice_b_cash_change": -300, "choice_b_reputation_change": 2,
         "choice_b_feedback": "Valid concern about liability! But you're still paying 30% more AND depending on the Authority's maintenance quality. Consider: would your engineers do better?",
         "choice_c_text": "Accept both changes - we need this location for asteroid proximity", 
         "choice_c_exp_reward": 35, "choice_c_cash_change": -400, "choice_c_reputation_change": 1,
         "choice_c_feedback": "Poor negotiation! You accepted extra responsibility AND extra cost. Location value doesn't mean accepting all terms. Counter-offers are expected in commercial negotiations.", 
         "subskill_focus": "Property Law"},

        # ========== LEVEL 5: Licensing and Permits ==========
        # Modern World
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Legal", "required_level": 5,
         "scenario_title": "L5: Licensing and Permits", 
         "scenario_narrative": "Grand opening is in 2 weeks! Your manager reports that the health permit is approved, but the liquor license is still processing (takes 4-6 weeks). Serving alcohol without a license is a criminal offense that could permanently bar you from getting one.",
         "choice_a_text": "Open without alcohol service until license arrives - compliance first", 
         "choice_a_exp_reward": 90, "choice_a_cash_change": -500, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Correct decision! Serving alcohol without a license risks criminal charges, fines, and permanent license denial. A few weeks of reduced revenue beats a destroyed business. Legal compliance isn't optional.",
         "choice_b_text": "Delay grand opening until all licenses are secured", 
         "choice_b_exp_reward": 70, "choice_b_cash_change": -1000, "choice_b_reputation_change": 3,
         "choice_b_feedback": "Conservative but costly! You're paying rent, staff, and marketing for a closed restaurant. Opening without alcohol is legal and generates revenue while you wait. Balance caution with business reality.",
         "choice_c_text": "Open fully and serve alcohol - we'll have the license soon anyway", 
         "choice_c_exp_reward": 20, "choice_c_cash_change": 500, "choice_c_reputation_change": -5,
         "choice_c_feedback": "Criminal risk! If inspected, you face fines up to $50,000, criminal charges, and permanent license denial. One undercover inspector ruins everything. Never gamble on regulatory compliance.", 
         "subskill_focus": "Regulatory Compliance"},
        
        # Fantasy World
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Legal", "required_level": 5,
         "scenario_title": "L5: Licensing and Permits", 
         "scenario_narrative": "The Guild Inspector arrives and finds you lack a 'Fire Safety Seal' - your hearth doesn't meet new fire prevention standards. Operating without it risks a 500 gold fine and closure. Upgrading costs 300 gold and takes one week.",
         "choice_a_text": "Close for one week, upgrade hearth, obtain proper Fire Safety Seal", 
         "choice_a_exp_reward": 90, "choice_a_cash_change": -300, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Compliance protects your business! One week closure and 300 gold is far better than 500 gold fine plus forced closure plus reputation damage. Proactive compliance shows professional management.",
         "choice_b_text": "Pay the 500 gold fine and continue operating while upgrading", 
         "choice_b_exp_reward": 50, "choice_b_cash_change": -500, "choice_b_reputation_change": 1,
         "choice_b_feedback": "Expensive choice! You pay the fine AND still need the 300 gold upgrade. Total: 800 gold vs 300 gold for immediate compliance. Plus, repeat violations bring harsher penalties.",
         "choice_c_text": "Offer the Inspector a 'consideration' to overlook the violation", 
         "choice_c_exp_reward": 20, "choice_c_cash_change": -200, "choice_c_reputation_change": -10,
         "choice_c_feedback": "Bribery is a serious crime! If discovered, you lose your license permanently, face criminal charges, and destroy your reputation. The short-term savings aren't worth the catastrophic risk.", 
         "subskill_focus": "Regulatory Compliance"},
        
        # Sci-Fi World
        {"world_type": "Sci-Fi", "industry": "Mining Corp", "discipline": "Legal", "required_level": 5,
         "scenario_title": "L5: Licensing and Permits", 
         "scenario_narrative": "Galactic Mining Commission notifies you that your Environmental Impact Permit expires in 30 days. Renewal requires updated asteroid debris dispersion analysis (costs 50,000 credits, takes 45 days). Operating without permit: 1 million credit fine per day.",
         "choice_a_text": "Immediately commission the analysis and plan for 15-day operations pause", 
         "choice_a_exp_reward": 90, "choice_a_cash_change": -50000, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Correct response! 15 days pause costs perhaps 200,000 credits in lost revenue. Operating one day without permit: 1 million fine. The math is clear. Start analysis immediately.",
         "choice_b_text": "Apply for a 60-day extension while completing the analysis", 
         "choice_b_exp_reward": 85, "choice_b_cash_change": -60000, "choice_b_reputation_change": 4,
         "choice_b_feedback": "Smart! Many regulators grant extensions for proactive applicants. Extension fee is typically 10,000 credits - far cheaper than operational pause. Always explore administrative solutions.",
         "choice_c_text": "Continue operations and pay fines as cost of doing business", 
         "choice_c_exp_reward": 20, "choice_c_cash_change": -1000000, "choice_c_reputation_change": -10,
         "choice_c_feedback": "Catastrophic! At 1 million per day, even 3 days of violation exceeds your analysis cost 60 times over. Plus, repeat violations lead to license revocation. Never treat compliance as optional.", 
         "subskill_focus": "Regulatory Compliance"},

        # ========== LEVEL 6: Torts and Negligence ==========
        # Modern World
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Legal", "required_level": 6,
         "scenario_title": "L6: Torts and Negligence", 
         "scenario_narrative": "A customer slips on a wet floor near the restroom and breaks their wrist. There was no 'Wet Floor' sign displayed. They're threatening to sue for medical bills ($15,000) plus pain and suffering ($50,000). Your insurance deductible is $10,000.",
         "choice_a_text": "Acknowledge the missing sign was our negligence, offer to cover medical bills directly", 
         "choice_a_exp_reward": 100, "choice_a_cash_change": -15000, "choice_a_reputation_change": 3,
         "choice_a_feedback": "Smart settlement! You were negligent (no sign = breach of duty of care). $15,000 direct payment is better than $65,000 lawsuit plus legal fees. Acknowledging fault and settling fairly prevents escalation.",
         "choice_b_text": "Deny liability - the customer should watch where they walk", 
         "choice_b_exp_reward": 40, "choice_b_cash_change": 0, "choice_b_reputation_change": -3,
         "choice_b_feedback": "Legally weak! Business owners have a 'duty of care' to maintain safe premises. No warning sign is clear negligence. Fighting this wastes money on lawyers and likely loses anyway.",
         "choice_c_text": "Report to insurance and let them handle everything", 
         "choice_c_exp_reward": 70, "choice_c_cash_change": -10000, "choice_c_reputation_change": 1,
         "choice_c_feedback": "Standard approach, but consider: insurance fights claims to minimize payouts, which can anger injured parties and escalate demands. Sometimes direct settlement is faster and cheaper.", 
         "subskill_focus": "Liability Management"},
        
        # Fantasy World
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Legal", "required_level": 6,
         "scenario_title": "L6: Torts and Negligence", 
         "scenario_narrative": "A patron claims your enchanted warming stones caused burns when they malfunctioned. The stones were installed by a licensed enchanter, but you hadn't had them inspected in 3 years. The patron demands 1,000 gold for healer's fees and suffering.",
         "choice_a_text": "Admit the inspection lapse was negligent, negotiate fair compensation", 
         "choice_a_exp_reward": 100, "choice_a_cash_change": -800, "choice_a_reputation_change": 3,
         "choice_a_feedback": "Responsible approach! Regular maintenance is part of duty of care. 3 years without inspection shows negligence. Negotiating to 800 gold (healer fees plus modest suffering) is reasonable settlement.",
         "choice_b_text": "Blame the enchanter - they installed faulty stones", 
         "choice_b_exp_reward": 50, "choice_b_cash_change": 0, "choice_b_reputation_change": 0,
         "choice_b_feedback": "Partial defense! You may have a claim against the enchanter, but the patron was injured in YOUR establishment. You're liable to them first, then can seek reimbursement from the enchanter.",
         "choice_c_text": "Deny everything - the patron probably caused the malfunction themselves", 
         "choice_c_exp_reward": 30, "choice_c_cash_change": 0, "choice_c_reputation_change": -5,
         "choice_c_feedback": "Weak defense! Without evidence of patron tampering, Guild Courts will find your 3-year inspection gap as clear negligence. Fighting obvious liability wastes gold and reputation.", 
         "subskill_focus": "Liability Management"},
        
        # Sci-Fi World
        {"world_type": "Sci-Fi", "industry": "Mining Corp", "discipline": "Legal", "required_level": 6,
         "scenario_title": "L6: Torts and Negligence", 
         "scenario_narrative": "A habitat module fails due to a structural flaw, causing temporary life support loss. Three workers require medical treatment (200,000 credits). Investigation shows you delayed mandatory structural inspections by 2 months to meet production targets.",
         "choice_a_text": "Accept responsibility, cover all medical costs, implement immediate safety review", 
         "choice_a_exp_reward": 100, "choice_a_cash_change": -200000, "choice_a_reputation_change": 5,
         "choice_a_feedback": "The only ethical choice! Delayed safety inspections to meet production is textbook negligence. Full compensation plus systemic reform shows genuine accountability. This protects against punitive damages.",
         "choice_b_text": "Blame the inspection company for not flagging the issue sooner", 
         "choice_b_exp_reward": 40, "choice_b_cash_change": 0, "choice_b_reputation_change": -3,
         "choice_b_feedback": "YOU delayed THEIR inspection. Blaming them invites evidence of your delay orders. Courts will find you primarily liable for preventing the inspection that would have caught the flaw.",
         "choice_c_text": "Offer partial compensation and dispute the connection to inspection delay", 
         "choice_c_exp_reward": 60, "choice_c_cash_change": -100000, "choice_c_reputation_change": -1,
         "choice_c_feedback": "Risky strategy! If workers can prove the delay caused the failure (and documentation likely exists), disputing connection looks like bad faith. Juries punish companies that minimize negligence.", 
         "subskill_focus": "Liability Management"},

        # ========== LEVEL 7: Trademarks and Branding ==========
        # Modern World
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Legal", "required_level": 7,
         "scenario_title": "L7: Trademarks and Branding", 
         "scenario_narrative": "A new restaurant opens across town with a name and logo remarkably similar to yours. Customers are confused, and some report bad experiences there thinking it was your location. Your lawyer says trademark infringement is likely, but litigation costs $50,000+.",
         "choice_a_text": "Send a cease and desist letter first - many infringers stop when confronted legally", 
         "choice_a_exp_reward": 110, "choice_a_cash_change": -2000, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Smart escalation! A cease and desist letter ($2,000 in legal fees) stops 70% of infringers without litigation. It also establishes your willingness to defend your trademark, which is legally important.",
         "choice_b_text": "Immediately file a trademark infringement lawsuit", 
         "choice_b_exp_reward": 70, "choice_b_cash_change": -50000, "choice_b_reputation_change": 3,
         "choice_b_feedback": "Aggressive but expensive! Litigation should be a last resort. Many judges expect parties to attempt resolution first. A cease and desist achieves the same goal at 4% of the cost.",
         "choice_c_text": "Ignore it - they'll probably fail anyway and it's not worth the hassle", 
         "choice_c_exp_reward": 30, "choice_c_cash_change": 0, "choice_c_reputation_change": -5,
         "choice_c_feedback": "Dangerous! Failure to defend trademarks can weaken your legal rights. Courts may find you 'abandoned' protection. Plus, their bad reviews harm your reputation. Trademarks require active defense.", 
         "subskill_focus": "Intellectual Property"},
        
        # Fantasy World
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Legal", "required_level": 7,
         "scenario_title": "L7: Trademarks and Branding", 
         "scenario_narrative": "Your tavern's famous 'Golden Dragon' name and sign are being copied by a rival in the next town. Travelers are confused about which is the original. The Guild offers trademark registration for 200 gold, which gives you exclusive rights throughout the kingdom.",
         "choice_a_text": "Register the trademark immediately, then send formal notice to the rival", 
         "choice_a_exp_reward": 110, "choice_a_cash_change": -200, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Perfect strategy! Registration creates legal proof of ownership. The formal notice backed by registration usually forces compliance. If they refuse, you have clear grounds for Guild Court action.",
         "choice_b_text": "Confront the rival directly and demand they change their name", 
         "choice_b_exp_reward": 50, "choice_b_cash_change": 0, "choice_b_reputation_change": 1,
         "choice_b_feedback": "Without registration, you have weaker legal standing. They might claim they thought of the name independently. Register first, then your demand has legal teeth.",
         "choice_c_text": "Change my own name to something more distinctive and unique", 
         "choice_c_exp_reward": 40, "choice_c_cash_change": -500, "choice_c_reputation_change": -3,
         "choice_c_feedback": "Surrender! You built the Golden Dragon reputation. Changing your name means losing that brand value while the copycat benefits from your original work. Defend what you created.", 
         "subskill_focus": "Intellectual Property"},
        
        # Sci-Fi World
        {"world_type": "Sci-Fi", "industry": "Mining Corp", "discipline": "Legal", "required_level": 7,
         "scenario_title": "L7: Trademarks and Branding", 
         "scenario_narrative": "Your 'NovaCore Mining' brand is well-known for quality asteroid surveys. A competitor launches 'NovaCorp Mining' with nearly identical branding. Industry analysts report customer confusion is costing you contracts worth 500,000 credits annually.",
         "choice_a_text": "File for expedited trademark review, then pursue injunction to stop their use", 
         "choice_a_exp_reward": 110, "choice_a_cash_change": -30000, "choice_a_reputation_change": 6,
         "choice_a_feedback": "Aggressive defense! Expedited review (10,000 credits) plus injunction filing (20,000 credits) can stop them within 90 days. 500,000 annual losses justify this investment. Brand protection is business protection.",
         "choice_b_text": "Negotiate a licensing deal where they pay us for brand association", 
         "choice_b_exp_reward": 80, "choice_b_cash_change": 50000, "choice_b_reputation_change": 2,
         "choice_b_feedback": "Creative monetization! If they're willing to pay for legitimacy, licensing converts a threat into revenue. However, this only works if their quality matches yours. Bad licensed work hurts your brand.",
         "choice_c_text": "Rebrand ourselves with something completely distinct to avoid confusion", 
         "choice_c_exp_reward": 40, "choice_c_cash_change": -100000, "choice_c_reputation_change": -3,
         "choice_c_feedback": "Expensive retreat! You're paying 100,000 credits to abandon brand equity you built while letting the copier benefit. Defending is almost always cheaper than abandoning established brands.", 
         "subskill_focus": "Intellectual Property"},

        # ========== LEVEL 8: Patents and Trade Secrets ==========
        # Modern World
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Legal", "required_level": 8,
         "scenario_title": "L8: Patents and Trade Secrets", 
         "scenario_narrative": "Your chef invented a unique food preparation process that dramatically improves flavor. You could patent it (20-year protection, but process becomes public) or keep it as a trade secret (indefinite protection, but if discovered or reverse-engineered, no legal protection).",
         "choice_a_text": "Trade secret - our process is hard to reverse-engineer and patents expire", 
         "choice_a_exp_reward": 120, "choice_a_cash_change": 0, "choice_a_reputation_change": 6,
         "choice_a_feedback": "Strategic choice! Coca-Cola's formula has been a trade secret for 130+ years. If your process can't be easily discovered through analysis, trade secret provides longer protection. Just ensure robust NDAs and security.",
         "choice_b_text": "Patent it - we want enforceable legal protection against copycats", 
         "choice_b_exp_reward": 100, "choice_b_cash_change": -15000, "choice_b_reputation_change": 5,
         "choice_b_feedback": "Valid approach! Patents give you the right to sue infringers. But remember: once filed, the process is public. Competitors can study it and design around it. And protection ends after 20 years.",
         "choice_c_text": "Do both - patent the broad concept, keep specific details as trade secrets", 
         "choice_c_exp_reward": 110, "choice_c_cash_change": -15000, "choice_c_reputation_change": 5,
         "choice_c_feedback": "Sophisticated strategy! Patent the general method for legal protection while keeping exact specifications secret. This layered approach is used by many successful companies. Consult a patent attorney for best structure.", 
         "subskill_focus": "Intellectual Property"},
        
        # Fantasy World
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Legal", "required_level": 8,
         "scenario_title": "L8: Patents and Trade Secrets", 
         "scenario_narrative": "Your alchemist developed a new stable healing potion formula. The Mages' Guild offers to register it as a 'Protected Invention' (like a patent - 15 year monopoly, but formula becomes public after) or you can keep it as a closely guarded 'Guild Secret.'",
         "choice_a_text": "Guild Secret - we can protect it indefinitely with proper precautions", 
         "choice_a_exp_reward": 120, "choice_a_cash_change": 0, "choice_a_reputation_change": 6,
         "choice_a_feedback": "Long-term thinking! If you can control access through careful employee agreements and secure storage, indefinite protection beats 15 years. Many master alchemists keep formulas as trade secrets for generations.",
         "choice_b_text": "Protected Invention - we need legal recourse if someone steals the formula", 
         "choice_b_exp_reward": 100, "choice_b_cash_change": -500, "choice_b_reputation_change": 5,
         "choice_b_feedback": "Defensive choice! If you fear theft or lack strong security, registration provides clear legal standing. Trade secrets offer no protection if independently discovered. Consider your vulnerability.",
         "choice_c_text": "Register only the stabilization process, keep the base formula secret", 
         "choice_c_exp_reward": 115, "choice_c_cash_change": -300, "choice_c_reputation_change": 5,
         "choice_c_feedback": "Layered protection! The registered process protects against that specific innovation while the core formula remains secret. Competitors would need both pieces. Excellent IP strategy.", 
         "subskill_focus": "Intellectual Property"},
        
        # Sci-Fi World
        {"world_type": "Sci-Fi", "industry": "Mining Corp", "discipline": "Legal", "required_level": 8,
         "scenario_title": "L8: Patents and Trade Secrets", 
         "scenario_narrative": "Your engineers designed a revolutionary Zero-G robotic welder. Galactic Patent Office offers 25-year protection (but full technical specs become public). Alternatively, keep it as a trade secret and rely on contracts and security.",
         "choice_a_text": "Patent it - in 25 years our technology will be obsolete anyway", 
         "choice_a_exp_reward": 120, "choice_a_cash_change": -100000, "choice_a_reputation_change": 6,
         "choice_a_feedback": "Practical analysis! Technology often advances faster than patent terms. 25 years of protection for a design that might be outdated in 10 is still valuable. Patent also enables licensing revenue.",
         "choice_b_text": "Trade secret - competitors can't reverse-engineer what they can't access", 
         "choice_b_exp_reward": 100, "choice_b_cash_change": 0, "choice_b_reputation_change": 4,
         "choice_b_feedback": "Viable if you have strong security! But space stations leak information. One disgruntled engineer with specs could destroy your advantage. Trade secrets require constant vigilance.",
         "choice_c_text": "Patent core innovations, keep manufacturing processes as trade secrets", 
         "choice_c_exp_reward": 115, "choice_c_cash_change": -75000, "choice_c_reputation_change": 5,
         "choice_c_feedback": "Optimal hybrid! Patent protects the inventive concept while trade secrets cover production efficiency. Competitors can legally build similar robots but can't match your manufacturing cost.", 
         "subskill_focus": "Intellectual Property"},

        # ========== LEVEL 9: Litigation and Dispute Resolution ==========
        # Modern World
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Legal", "required_level": 9,
         "scenario_title": "L9: Litigation and Dispute Resolution", 
         "scenario_narrative": "Your primary food supplier breaches their contract, failing to deliver for 2 weeks and costing you $80,000 in lost revenue. Options: Arbitration (faster, private, but limited damages) vs. Lawsuit (slower, public, but full damages possible). Contract has an arbitration clause.",
         "choice_a_text": "Pursue arbitration - the contract requires it and it's faster and cheaper", 
         "choice_a_exp_reward": 130, "choice_a_cash_change": -10000, "choice_a_reputation_change": 6,
         "choice_a_feedback": "Correct! The arbitration clause likely makes it mandatory anyway. Arbitration typically resolves in 3-6 months vs. 2-3 years for litigation. Costs ~$10,000 vs. $100,000+. Privacy also protects your business reputation.",
         "choice_b_text": "File lawsuit anyway - arbitration clauses can be challenged", 
         "choice_b_exp_reward": 60, "choice_b_cash_change": -50000, "choice_b_reputation_change": 2,
         "choice_b_feedback": "Uphill battle! Courts generally enforce arbitration clauses. You'll spend money fighting to litigate before even addressing the breach. Follow the contract terms you agreed to.",
         "choice_c_text": "Negotiate directly with the supplier for compensation before legal action", 
         "choice_c_exp_reward": 110, "choice_c_cash_change": -5000, "choice_c_reputation_change": 5,
         "choice_c_feedback": "Best first step! Direct negotiation preserves business relationships and is cheapest. Many disputes settle for 60-70% of damages without formal proceedings. Only escalate to arbitration if negotiation fails.", 
         "subskill_focus": "Dispute Resolution"},
        
        # Fantasy World
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Legal", "required_level": 9,
         "scenario_title": "L9: Litigation and Dispute Resolution", 
         "scenario_narrative": "A major supplier breaches your ale contract during festival season, costing you 5,000 gold in lost sales. Options: Guild Arbitration (quick, private, but maximum award is 3,000 gold) vs. Crown Court (slow, public, full damages possible but expensive and reputation-damaging).",
         "choice_a_text": "Guild Arbitration - recover 3,000 gold quickly rather than risk prolonged battle", 
         "choice_a_exp_reward": 130, "choice_a_cash_change": 2500, "choice_a_reputation_change": 6,
         "choice_a_feedback": "Pragmatic! 3,000 gold in 30 days beats maybe 5,000 gold in 18 months. Time has value. You can use the quick resolution to find a new supplier and move forward with your business.",
         "choice_b_text": "Crown Court - I want full compensation for their breach", 
         "choice_b_exp_reward": 70, "choice_b_cash_change": 0, "choice_b_reputation_change": 2,
         "choice_b_feedback": "Emotionally satisfying but economically questionable. Crown Court costs 1,000+ gold in fees, takes over a year, and the public attention may hurt your reputation. Is extra 2,000 gold worth all that?",
         "choice_c_text": "Threaten Crown Court but offer to settle for 4,000 gold to avoid proceedings", 
         "choice_c_exp_reward": 120, "choice_c_cash_change": 3500, "choice_c_reputation_change": 5,
         "choice_c_feedback": "Skilled negotiation! The threat of expensive Crown Court litigation incentivizes settlement. 4,000 gold is a reasonable middle ground that saves both parties time and money.", 
         "subskill_focus": "Dispute Resolution"},
        
        # Sci-Fi World
        {"world_type": "Sci-Fi", "industry": "Mining Corp", "discipline": "Legal", "required_level": 9,
         "scenario_title": "L9: Litigation and Dispute Resolution", 
         "scenario_narrative": "A critical equipment supplier breached contract, costing you 2,000,000 credits in downtime. Options: Interstellar Commercial Arbitration (binding, fast, private) vs. Galactic Trade Court (expensive, slow, but precedent-setting and full damages). Your contract specifies arbitration.",
         "choice_a_text": "Follow contract arbitration clause - it's binding and most efficient", 
         "choice_a_exp_reward": 130, "choice_a_cash_change": -50000, "choice_a_reputation_change": 6,
         "choice_a_feedback": "Correct approach! Arbitration clauses are typically enforceable. 50,000 credits for a 6-month resolution beats 500,000 credits for a 3-year court battle. Recover damages faster and return to operations.",
         "choice_b_text": "Galactic Trade Court - I want this precedent to protect future contracts", 
         "choice_b_exp_reward": 80, "choice_b_cash_change": -500000, "choice_b_reputation_change": 3,
         "choice_b_feedback": "Idealistic but costly! Precedent-setting cases require massive legal investment. Unless you're planning industry-wide advocacy, use arbitration for this dispute and save resources for your business.",
         "choice_c_text": "Propose mediation before any formal proceedings to preserve the relationship", 
         "choice_c_exp_reward": 100, "choice_c_cash_change": -20000, "choice_c_reputation_change": 5,
         "choice_c_feedback": "Excellent escalation strategy! Mediation is even cheaper than arbitration. If the supplier values your business, they may offer fair compensation to maintain the relationship. Only escalate if mediation fails.", 
         "subskill_focus": "Dispute Resolution"},

        # ========== LEVEL 10: International Law & Governance ==========
        # Modern World
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Legal", "required_level": 10,
         "scenario_title": "L10: International Law & Governance", 
         "scenario_narrative": "You're signing a major supply contract with an overseas manufacturer. Your lawyer asks: Which country's laws govern the contract? Where will disputes be resolved? The manufacturer wants their home country; you want yours. This could determine a lawsuit's outcome.",
         "choice_a_text": "Insist on neutral third country (Singapore/Switzerland) for both governing law and arbitration", 
         "choice_a_exp_reward": 150, "choice_a_cash_change": 0, "choice_a_reputation_change": 8,
         "choice_a_feedback": "Expert-level negotiation! Neutral jurisdictions like Singapore or Switzerland have well-developed commercial law and no home-court advantage for either party. This is standard practice in major international contracts.",
         "choice_b_text": "Accept their governing law but require arbitration in a neutral location", 
         "choice_b_exp_reward": 110, "choice_b_cash_change": 0, "choice_b_reputation_change": 5,
         "choice_b_feedback": "Reasonable compromise! Governing law determines contract interpretation, but neutral arbitration ensures fair proceedings. Make sure you understand their commercial law before agreeing.",
         "choice_c_text": "Insist on your home country for everything - this is non-negotiable", 
         "choice_c_exp_reward": 60, "choice_c_cash_change": 0, "choice_c_reputation_change": 2,
         "choice_c_feedback": "Inflexible position! The manufacturer may walk away or demand unfavorable trade-offs. International contracts require mutual compromise on jurisdiction. Hard-line positions often kill deals.", 
         "subskill_focus": "International Law"},
        
        # Fantasy World
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Legal", "required_level": 10,
         "scenario_title": "L10: International Law & Governance", 
         "scenario_narrative": "You're negotiating a major contract with an Elven Kingdom merchant for rare wines. They insist on Elven Law governing the contract and disputes resolved in Elven Courts. You want Human Kingdom law. The Merchant Guild suggests neutral Dwarven Commercial Law.",
         "choice_a_text": "Accept Dwarven Commercial Law - they're known for fair, predictable rulings", 
         "choice_a_exp_reward": 150, "choice_a_cash_change": -100, "choice_a_reputation_change": 8,
         "choice_a_feedback": "Diplomatic excellence! Dwarven Commercial Courts are renowned across all kingdoms for impartiality. Neither party has advantage, and their precedents are clear. This protects both sides equally.",
         "choice_b_text": "Agree to Elven Law but with Human Kingdom arbitrators", 
         "choice_b_exp_reward": 100, "choice_b_cash_change": 0, "choice_b_reputation_change": 4,
         "choice_b_feedback": "Creative split! This can work if arbitrators are skilled in Elven Law. However, mixing systems creates complexity. Consider whether simpler neutral framework would be cleaner.",
         "choice_c_text": "Walk away - I won't risk being subject to foreign courts", 
         "choice_c_exp_reward": 50, "choice_c_cash_change": 0, "choice_c_reputation_change": 0,
         "choice_c_feedback": "Lost opportunity! International trade requires compromise on jurisdiction. Refusing all foreign law means limiting yourself to domestic suppliers. Neutral third-party law is the solution.", 
         "subskill_focus": "International Law"},
        
        # Sci-Fi World
        {"world_type": "Sci-Fi", "industry": "Mining Corp", "discipline": "Legal", "required_level": 10,
         "scenario_title": "L10: International Law & Governance", 
         "scenario_narrative": "You're finalizing a major contract with an alien civilization's mining consortium for rare element trade. They operate under completely different legal concepts. Your legal AI suggests three options: your Federation law, their law, or newly-developed Interspecies Commercial Code.",
         "choice_a_text": "Interspecies Commercial Code - it's designed specifically for cross-species transactions", 
         "choice_a_exp_reward": 150, "choice_a_cash_change": -50000, "choice_a_reputation_change": 8,
         "choice_a_feedback": "Forward-thinking choice! The Interspecies Commercial Code reconciles different legal traditions into neutral standards both species can understand. This is the future of galactic commerce law.",
         "choice_b_text": "Federation law with an alien legal liaison to explain concepts", 
         "choice_b_exp_reward": 90, "choice_b_cash_change": -30000, "choice_b_reputation_change": 4,
         "choice_b_feedback": "Risky approach! Even with a liaison, your laws may contain concepts that don't translate. The alien consortium might agree to terms they interpret very differently. Misunderstandings cause disputes.",
         "choice_c_text": "Create a custom legal framework for just this contract", 
         "choice_c_exp_reward": 110, "choice_c_cash_change": -100000, "choice_c_reputation_change": 6,
         "choice_c_feedback": "Thorough but expensive! Custom frameworks can address unique situations but cost significant legal fees to develop. The Interspecies Code already solved most issues you'd have to reinvent.", 
         "subskill_focus": "International Law"},
    ]
    
    for scenario in scenarios:
        cur.execute("""
            INSERT INTO scenario_master (world_type, industry, discipline, required_level, scenario_title, scenario_narrative,
                choice_a_text, choice_a_exp_reward, choice_a_cash_change, choice_a_reputation_change, choice_a_feedback,
                choice_b_text, choice_b_exp_reward, choice_b_cash_change, choice_b_reputation_change, choice_b_feedback,
                choice_c_text, choice_c_exp_reward, choice_c_cash_change, choice_c_reputation_change, choice_c_feedback,
                subskill_focus)
            VALUES (%(world_type)s, %(industry)s, %(discipline)s, %(required_level)s, %(scenario_title)s, %(scenario_narrative)s,
                %(choice_a_text)s, %(choice_a_exp_reward)s, %(choice_a_cash_change)s, %(choice_a_reputation_change)s, %(choice_a_feedback)s,
                %(choice_b_text)s, %(choice_b_exp_reward)s, %(choice_b_cash_change)s, %(choice_b_reputation_change)s, %(choice_b_feedback)s,
                %(choice_c_text)s, %(choice_c_exp_reward)s, %(choice_c_cash_change)s, %(choice_c_reputation_change)s, %(choice_c_feedback)s,
                %(subskill_focus)s)
        """, scenario)
    
    conn.commit()
    print(f"Seeded {len(scenarios)} Legal Curriculum scenarios (Levels 1-10, 3 worlds)!")
    cur.close()
    conn.close()


def seed_operations_curriculum():
    """Seed the complete 10-level Operations Curriculum across 3 worlds (30 scenarios total).
    
    Curriculum Structure:
    - L1-L3: Fundamentals & Workflow (Transformation Process, Inventory Management, Workflow Optimization)
    - L4-L6: Efficiency & Quality (Capacity Utilization, Quality Assurance, Production Scheduling)
    - L7-L8: Advanced Logistics (Just-In-Time, Supply Chain Risk)
    - L9-L10: Strategy & Mastery (Outsourcing/Offshoring, Process Innovation/Automation)
    """
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM scenario_master WHERE discipline = 'Operations' AND scenario_title LIKE 'L%:%'")
    result = cur.fetchone()
    if result['count'] >= 30:
        print("Operations curriculum already seeded.")
        cur.close()
        conn.close()
        return
    
    scenarios = [
        # ========== LEVEL 1: The Transformation Process ==========
        # Modern World
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Operations", "required_level": 1,
         "scenario_title": "L1: The Transformation Process", 
         "scenario_narrative": "Your restaurant manager asks you to map the complete transformation process: from raw ingredients arriving at the back door to a finished meal reaching the customer's table. Understanding Input → Process → Output is fundamental to operations.",
         "choice_a_text": "Map it: Inputs (ingredients, labor) → Process (prep, cooking, plating) → Output (finished meal, service)", 
         "choice_a_exp_reward": 50, "choice_a_cash_change": 0, "choice_a_reputation_change": 3,
         "choice_a_feedback": "Perfect operations thinking! Every business transforms inputs into outputs. By mapping this flow, you can identify bottlenecks, waste, and opportunities for improvement. This is the foundation of operations management.",
         "choice_b_text": "Focus only on the cooking - that's where the real work happens", 
         "choice_b_exp_reward": 25, "choice_b_cash_change": 0, "choice_b_reputation_change": 1,
         "choice_b_feedback": "Too narrow! Cooking is just one process step. If ingredients arrive late (input problem) or service is slow (output problem), great cooking doesn't matter. Operations views the entire system.",
         "choice_c_text": "Hire a consultant to figure this out - it's too complex", 
         "choice_c_exp_reward": 30, "choice_c_cash_change": -500, "choice_c_reputation_change": 1,
         "choice_c_feedback": "Consultants can help, but you should understand your own transformation process! This is basic operations knowledge every business owner needs. Start with a simple flowchart yourself.", 
         "subskill_focus": "Process Mapping"},
        
        # Fantasy World
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Operations", "required_level": 1,
         "scenario_title": "L1: The Transformation Process", 
         "scenario_narrative": "The Guild Master asks you to explain how your tavern creates value. He wants to understand the transformation from raw materials to satisfied customers. This will determine your Guild certification level.",
         "choice_a_text": "Explain: Inputs (grain, hops, meat) → Process (brewing, cooking, serving) → Output (ale, meals, entertainment)", 
         "choice_a_exp_reward": 50, "choice_a_cash_change": 0, "choice_a_reputation_change": 3,
         "choice_a_feedback": "Excellent understanding! The Guild recognizes you understand value creation. Raw materials alone have limited value; your transformation processes create something customers will pay premium prices for.",
         "choice_b_text": "We buy things and sell them - it's simple trading", 
         "choice_b_exp_reward": 20, "choice_b_cash_change": 0, "choice_b_reputation_change": 0,
         "choice_b_feedback": "That's merchant thinking, not operations thinking! A tavern doesn't just resell - it transforms grain into ale, raw meat into feasts. Your processes ADD value beyond the raw materials.",
         "choice_c_text": "Show him the account books - money in, money out", 
         "choice_c_exp_reward": 30, "choice_c_cash_change": 0, "choice_c_reputation_change": 1,
         "choice_c_feedback": "Financial view is important but doesn't explain HOW value is created. Operations focuses on the physical transformation, not just the monetary result. The Guild wants to see your process understanding.", 
         "subskill_focus": "Process Mapping"},
        
        # Sci-Fi World
        {"world_type": "Sci-Fi", "industry": "Mining Corp", "discipline": "Operations", "required_level": 1,
         "scenario_title": "L1: The Transformation Process", 
         "scenario_narrative": "The Galactic Operations Board requires all mining corps to document their transformation process for efficiency audits. You must map how raw asteroid ore becomes refined, sellable minerals.",
         "choice_a_text": "Document: Inputs (ore, energy, labor) → Process (extraction, refining, quality testing) → Output (refined minerals, waste byproducts)", 
         "choice_a_exp_reward": 50, "choice_a_cash_change": 0, "choice_a_reputation_change": 3,
         "choice_a_feedback": "Comprehensive mapping! The Board is impressed. By documenting each step, you can measure efficiency, identify energy waste, and optimize the refining process. This is operations excellence.",
         "choice_b_text": "We dig rocks and sell them - what's there to map?", 
         "choice_b_exp_reward": 20, "choice_b_cash_change": 0, "choice_b_reputation_change": -1,
         "choice_b_feedback": "Oversimplification fails the audit! Between 'dig' and 'sell' are dozens of transformation steps. Extraction methods, ore sorting, refining techniques - each affects quality and cost. Map the details.",
         "choice_c_text": "Submit last year's documentation with updated dates", 
         "choice_c_exp_reward": 25, "choice_c_cash_change": 0, "choice_c_reputation_change": 0,
         "choice_c_feedback": "If your processes haven't changed, reusing documentation is efficient. But has nothing improved in a year? The audit is also an opportunity to review and optimize your transformation process.", 
         "subskill_focus": "Process Mapping"},

        # ========== LEVEL 2: Inventory Management Basics ==========
        # Modern World
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Operations", "required_level": 2,
         "scenario_title": "L2: Inventory Management Basics", 
         "scenario_narrative": "Your head chef complains about running out of key ingredients during dinner rush, while your accountant shows you $3,000 worth of spoiled food thrown away last month. You need a proper inventory management system.",
         "choice_a_text": "Implement FIFO (First In, First Out) rotation and set minimum stock levels for key items", 
         "choice_a_exp_reward": 60, "choice_a_cash_change": 500, "choice_a_reputation_change": 3,
         "choice_a_feedback": "Classic inventory management! FIFO ensures older stock is used first (reducing spoilage), while minimum stock levels prevent stockouts. This balances carrying costs against availability.",
         "choice_b_text": "Just order more of everything to avoid running out", 
         "choice_b_exp_reward": 25, "choice_b_cash_change": -1000, "choice_b_reputation_change": 1,
         "choice_b_feedback": "More inventory means more spoilage! Perishables have limited shelf life. You'll solve stockouts but triple your waste. Inventory management balances having enough without having too much.",
         "choice_c_text": "Let each station manage their own supplies independently", 
         "choice_c_exp_reward": 30, "choice_c_cash_change": -300, "choice_c_reputation_change": 1,
         "choice_c_feedback": "Decentralization causes duplication and inconsistency. One station hoards while another runs out. Centralized inventory tracking with clear reorder points is more efficient.", 
         "subskill_focus": "Inventory Control"},
        
        # Fantasy World
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Operations", "required_level": 2,
         "scenario_title": "L2: Inventory Management Basics", 
         "scenario_narrative": "Your cellar contains valuable ale barrels, rare spell components, and dried provisions. Some items are spoiling before use while others run out during festivals. The chaos is costing you gold.",
         "choice_a_text": "Create an inventory ledger tracking all items with dates received and use oldest stock first", 
         "choice_a_exp_reward": 60, "choice_a_cash_change": 300, "choice_a_reputation_change": 3,
         "choice_a_feedback": "Proper stock management! Recording receipt dates and using oldest first (FIFO) minimizes spoilage. Setting reorder points for each item prevents stockouts. Your cellar is now professionally managed.",
         "choice_b_text": "Hire a cellar keeper to memorize everything", 
         "choice_b_exp_reward": 35, "choice_b_cash_change": -200, "choice_b_reputation_change": 1,
         "choice_b_feedback": "Human memory is unreliable and doesn't scale! What happens when the cellar keeper is sick or leaves? Written records create a system that survives personnel changes.",
         "choice_c_text": "Check inventory only when something runs out", 
         "choice_c_exp_reward": 20, "choice_c_cash_change": -400, "choice_c_reputation_change": 0,
         "choice_c_feedback": "Reactive management causes stockouts during peak demand! By the time you notice something's gone, it's too late for the dinner rush. Proactive inventory checks prevent problems.", 
         "subskill_focus": "Inventory Control"},
        
        # Sci-Fi World
        {"world_type": "Sci-Fi", "industry": "Mining Corp", "discipline": "Operations", "required_level": 2,
         "scenario_title": "L2: Inventory Management Basics", 
         "scenario_narrative": "Your orbital station stores exotic metals, life support components, and radiation-sensitive materials. Some materials are degrading in storage while critical parts run out during emergencies. The CFO demands better inventory control.",
         "choice_a_text": "Implement automated tracking with sensors monitoring stock levels, expiration, and environmental conditions", 
         "choice_a_exp_reward": 60, "choice_a_cash_change": -5000, "choice_a_reputation_change": 4,
         "choice_a_feedback": "State-of-the-art inventory management! Sensors track quantity, detect degradation, and auto-trigger reorders. For radiation-sensitive materials, this prevents both waste and safety hazards.",
         "choice_b_text": "Maintain larger buffer stocks of everything critical", 
         "choice_b_exp_reward": 40, "choice_b_cash_change": -20000, "choice_b_reputation_change": 2,
         "choice_b_feedback": "Expensive solution! Buffer stock ties up capital and some materials degrade over time regardless of quantity. Smart tracking is more cost-effective than brute-force inventory increases.",
         "choice_c_text": "Accept occasional stockouts as normal in remote operations", 
         "choice_c_exp_reward": 20, "choice_c_cash_change": 0, "choice_c_reputation_change": -2,
         "choice_c_feedback": "In space, stockouts can be life-threatening! Life support component shortages aren't acceptable. Remote operations require BETTER inventory management, not lower standards.", 
         "subskill_focus": "Inventory Control"},

        # ========== LEVEL 3: Workflow Optimization ==========
        # Modern World
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Operations", "required_level": 3,
         "scenario_title": "L3: Workflow Optimization", 
         "scenario_narrative": "Dinner service is chaotic. Cooks bump into each other, orders get lost, and food sits under heat lamps too long. You need to create Standard Operating Procedures (SOPs) and optimize the kitchen layout.",
         "choice_a_text": "Redesign layout for logical flow and create step-by-step SOPs for each station", 
         "choice_a_exp_reward": 70, "choice_a_cash_change": 800, "choice_a_reputation_change": 4,
         "choice_a_feedback": "Operations excellence! Logical layout reduces movement waste, and SOPs ensure consistency. The new workflow means faster service, fewer errors, and less staff stress. Efficiency gains compound.",
         "choice_b_text": "Just tell everyone to work faster and pay attention", 
         "choice_b_exp_reward": 25, "choice_b_cash_change": 0, "choice_b_reputation_change": 0,
         "choice_b_feedback": "Blaming workers ignores system problems! If the layout causes collisions and the process creates confusion, working faster just makes more mistakes. Fix the system, not the people.",
         "choice_c_text": "Hire more staff to handle the chaos", 
         "choice_c_exp_reward": 35, "choice_c_cash_change": -1500, "choice_c_reputation_change": 1,
         "choice_c_feedback": "More people in a bad system creates more chaos! Before adding labor, optimize the workflow. Often, better processes let fewer people do more work with less stress.", 
         "subskill_focus": "Process Optimization"},
        
        # Fantasy World
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Operations", "required_level": 3,
         "scenario_title": "L3: Workflow Optimization", 
         "scenario_narrative": "Your brewing area is disorganized. Apprentices constantly search for tools, batches are inconsistent, and accidents happen when people cross paths. The Master Brewer demands you fix the workspace.",
         "choice_a_text": "Reorganize for logical flow: ingredients → mixing → brewing → aging, with tools at each station", 
         "choice_a_exp_reward": 70, "choice_a_cash_change": 400, "choice_a_reputation_change": 4,
         "choice_a_feedback": "Workflow mastery! Organizing by process sequence eliminates wasted movement. Tools at each station means no searching. Written procedures ensure every apprentice brews consistently. Production doubles!",
         "choice_b_text": "Put the most experienced brewer in charge to direct traffic", 
         "choice_b_exp_reward": 40, "choice_b_cash_change": 0, "choice_b_reputation_change": 2,
         "choice_b_feedback": "Supervision helps but doesn't fix the underlying chaos! A well-designed workspace shouldn't need constant direction. Good systems work smoothly even when the expert isn't watching.",
         "choice_c_text": "Restrict access so only one person works at a time", 
         "choice_c_exp_reward": 30, "choice_c_cash_change": -200, "choice_c_reputation_change": 1,
         "choice_c_feedback": "Eliminates collisions but destroys throughput! Sequential access means massive delays. The goal is parallel work without interference. Redesign the space, don't restrict it.", 
         "subskill_focus": "Process Optimization"},
        
        # Sci-Fi World
        {"world_type": "Sci-Fi", "industry": "Mining Corp", "discipline": "Operations", "required_level": 3,
         "scenario_title": "L3: Workflow Optimization", 
         "scenario_narrative": "Your ore processing facility has inefficient material flow. Ore moves back and forth between stations, workers wait for equipment, and shift handovers cause delays. Engineering requests SOPs and layout optimization.",
         "choice_a_text": "Redesign for linear flow and create detailed SOPs with automated handover protocols", 
         "choice_a_exp_reward": 70, "choice_a_cash_change": 5000, "choice_a_reputation_change": 4,
         "choice_a_feedback": "Industrial engineering excellence! Linear flow eliminates backtracking. SOPs ensure consistency across shifts. Automated handover protocols mean zero information loss at shift changes. Throughput increases 30%.",
         "choice_b_text": "Add more equipment to reduce waiting times", 
         "choice_b_exp_reward": 40, "choice_b_cash_change": -10000, "choice_b_reputation_change": 2,
         "choice_b_feedback": "Capital-intensive solution to a workflow problem! Before buying equipment, optimize the process. Often the bottleneck is layout or procedure, not equipment capacity.",
         "choice_c_text": "Run three independent shifts with no handover requirements", 
         "choice_c_exp_reward": 30, "choice_c_cash_change": -5000, "choice_c_reputation_change": 0,
         "choice_c_feedback": "Independent shifts means triplicating everything! And in-progress work can't be abandoned between shifts. Proper handover protocols are more efficient than complete independence.", 
         "subskill_focus": "Process Optimization"},

        # ========== LEVEL 4: Capacity Utilization ==========
        # Modern World
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Operations", "required_level": 4,
         "scenario_title": "L4: Capacity Utilization", 
         "scenario_narrative": "Your kitchen can produce 200 meals per night at maximum capacity. You're currently serving 120 meals. A new oven costs $30,000 and would increase capacity to 280 meals. But should you buy it?",
         "choice_a_text": "No - current utilization is 60%. Focus on filling existing capacity before expanding", 
         "choice_a_exp_reward": 80, "choice_a_cash_change": 0, "choice_a_reputation_change": 4,
         "choice_a_feedback": "Excellent capacity analysis! At 60% utilization, you have 80 unused meals of capacity. Marketing to fill existing capacity is far cheaper than $30,000 for equipment you don't need yet.",
         "choice_b_text": "Yes - more capacity means more potential revenue", 
         "choice_b_exp_reward": 35, "choice_b_cash_change": -30000, "choice_b_reputation_change": 1,
         "choice_b_feedback": "Capacity without demand is waste! The oven cost $30,000 but won't generate revenue unless you have customers to fill it. First, achieve higher utilization of current equipment.",
         "choice_c_text": "Wait until we're at 100% capacity, then expand", 
         "choice_c_exp_reward": 60, "choice_c_cash_change": 0, "choice_c_reputation_change": 2,
         "choice_c_feedback": "Waiting for 100% is risky - you'll turn away customers while waiting for the oven. Industry standard is to expand around 80-85% utilization. Plan ahead, but don't overbuild.", 
         "subskill_focus": "Capacity Planning"},
        
        # Fantasy World
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Operations", "required_level": 4,
         "scenario_title": "L4: Capacity Utilization", 
         "scenario_narrative": "Your brewing capacity is 100 barrels per month. You're currently selling 70 barrels. A dwarven expansion would cost 5,000 gold and double your capacity to 200 barrels. The Master Brewer is eager. Is it wise?",
         "choice_a_text": "Not yet - at 70% utilization, optimize demand before doubling capacity", 
         "choice_a_exp_reward": 80, "choice_a_cash_change": 0, "choice_a_reputation_change": 4,
         "choice_a_feedback": "Strategic thinking! 30 unsold barrels represent unused current capacity. Growing demand to 85-90 barrels through better distribution or marketing costs far less than 5,000 gold for capacity you can't fill.",
         "choice_b_text": "Expand now - the upcoming festival season will need extra capacity", 
         "choice_b_exp_reward": 60, "choice_b_cash_change": -5000, "choice_b_reputation_change": 3,
         "choice_b_feedback": "Seasonal planning is valid! If festival demand exceeds 100 barrels, expansion makes sense. But verify the demand forecast before committing 5,000 gold. Temporary solutions might bridge seasonal peaks.",
         "choice_c_text": "Double capacity immediately - bigger is always better for breweries", 
         "choice_c_exp_reward": 30, "choice_c_cash_change": -5000, "choice_c_reputation_change": 1,
         "choice_c_feedback": "Bigger isn't better without demand! 200 barrels capacity selling only 70 means 65% waste of investment. Capacity should lead demand slightly, not massively exceed it.", 
         "subskill_focus": "Capacity Planning"},
        
        # Sci-Fi World
        {"world_type": "Sci-Fi", "industry": "Mining Corp", "discipline": "Operations", "required_level": 4,
         "scenario_title": "L4: Capacity Utilization", 
         "scenario_narrative": "Your refinery processes 10,000 tons of ore monthly at maximum capacity. Current throughput is 7,500 tons. A 2,000,000 credit expansion would add another 10,000 tons capacity. The Operations VP pushes for approval.",
         "choice_a_text": "Reject - at 75% utilization, we should maximize current capacity first", 
         "choice_a_exp_reward": 80, "choice_a_cash_change": 0, "choice_a_reputation_change": 4,
         "choice_a_feedback": "Sound capacity management! 2.5 million credits of unused capacity exists. Improving extraction rates or extending operating hours might reach 9,000+ tons without capital investment.",
         "choice_b_text": "Approve if ore supply contracts support 15,000+ tons demand", 
         "choice_b_exp_reward": 75, "choice_b_cash_change": 0, "choice_b_reputation_change": 4,
         "choice_b_feedback": "Conditional approval is smart! Expansion should match contracted demand. If you have signed agreements for 15,000 tons monthly, expansion is justified. Capacity follows demand commitments.",
         "choice_c_text": "Approve to position for market growth opportunities", 
         "choice_c_exp_reward": 40, "choice_c_cash_change": -2000000, "choice_c_reputation_change": 2,
         "choice_c_feedback": "Speculative capacity is risky! 'Market growth' isn't a contract. If growth doesn't materialize, you've committed 2 million credits to idle equipment. Expand based on commitments, not hopes.", 
         "subskill_focus": "Capacity Planning"},

        # ========== LEVEL 5: Quality Assurance ==========
        # Modern World
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Operations", "required_level": 5,
         "scenario_title": "L5: Quality Assurance", 
         "scenario_narrative": "Customer complaints about inconsistent food quality are increasing. Some dishes are excellent, others are subpar. You need to implement quality controls that ensure every plate meets standards before leaving the kitchen.",
         "choice_a_text": "Implement mandatory quality checkpoint: every dish inspected by expeditor before serving", 
         "choice_a_exp_reward": 90, "choice_a_cash_change": 500, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Quality gate implementation! The expeditor checkpoint catches problems before they reach customers. Rejecting subpar dishes costs less than losing customers. This is classic QA: inspect before delivery.",
         "choice_b_text": "Trust the cooks - they know when food is ready", 
         "choice_b_exp_reward": 30, "choice_b_cash_change": 0, "choice_b_reputation_change": -2,
         "choice_b_feedback": "Self-inspection has known limitations! People miss their own errors. Independent quality checks catch what creators overlook. Professional kitchens always have expeditor oversight.",
         "choice_c_text": "Fire the cooks whose dishes get complaints", 
         "choice_c_exp_reward": 40, "choice_c_cash_change": -500, "choice_c_reputation_change": 0,
         "choice_c_feedback": "Reactive punishment doesn't prevent problems! By the time you identify bad cooks, customers are already unhappy. Systematic quality checks catch issues before they reach customers.", 
         "subskill_focus": "Quality Control"},
        
        # Fantasy World
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Operations", "required_level": 5,
         "scenario_title": "L5: Quality Assurance", 
         "scenario_narrative": "Some batches of your ale are excellent, others are barely drinkable. The inconsistency is hurting your reputation. Customers don't know what they'll get when they order. The Guild suggests quality standards.",
         "choice_a_text": "Create written quality standards and taste-test every batch before selling", 
         "choice_a_exp_reward": 90, "choice_a_cash_change": 300, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Quality assurance mastery! Written standards define 'acceptable.' Taste testing catches bad batches before customers do. Rejecting subpar batches costs less than reputation damage. Consistency builds loyalty.",
         "choice_b_text": "Blend good and bad batches together to average out quality", 
         "choice_b_exp_reward": 40, "choice_b_cash_change": 0, "choice_b_reputation_change": 1,
         "choice_b_feedback": "Dilution doesn't solve the problem! You're now selling mediocre ale instead of some great and some bad. Better to fix the process that creates bad batches in the first place.",
         "choice_c_text": "Sell bad batches at discount rather than waste them", 
         "choice_c_exp_reward": 50, "choice_c_cash_change": 100, "choice_c_reputation_change": 0,
         "choice_c_feedback": "Salvage recovery is valid but incomplete! You recover some value from bad batches, but still have reputation risk. The real solution is preventing bad batches through process improvement.", 
         "subskill_focus": "Quality Control"},
        
        # Sci-Fi World
        {"world_type": "Sci-Fi", "industry": "Mining Corp", "discipline": "Operations", "required_level": 5,
         "scenario_title": "L5: Quality Assurance", 
         "scenario_narrative": "Refined minerals are reaching customers with inconsistent purity levels. Some shipments meet specs, others are rejected. Quality failures cost 500,000 credits last quarter in returns and penalties. Engineering proposes automated quality testing.",
         "choice_a_text": "Implement inline sensors testing 100% of output with automatic rejection of subspec material", 
         "choice_a_exp_reward": 90, "choice_a_cash_change": -50000, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Zero-defect quality system! Automated 100% inspection with automatic rejection ensures nothing substandard ships. The 50,000 credit investment saves 500,000+ in returns. Quality pays for itself.",
         "choice_b_text": "Test samples from each batch - 100% testing is overkill", 
         "choice_b_exp_reward": 60, "choice_b_cash_change": -20000, "choice_b_reputation_change": 3,
         "choice_b_feedback": "Statistical sampling can work but has risks. If contamination is localized, sampling might miss it. For high-value materials with severe rejection penalties, 100% testing is often justified.",
         "choice_c_text": "Negotiate with customers to accept wider purity tolerances", 
         "choice_c_exp_reward": 40, "choice_c_cash_change": 0, "choice_c_reputation_change": -2,
         "choice_c_feedback": "Lowering standards instead of raising quality? Customers chose you for specifications you promised. Asking them to accept less damages your reputation and competitive position.", 
         "subskill_focus": "Quality Control"},

        # ========== LEVEL 6: Production Scheduling ==========
        # Modern World
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Operations", "required_level": 6,
         "scenario_title": "L6: Production Scheduling", 
         "scenario_narrative": "You're opening three new franchise locations simultaneously. Each requires permits (2 weeks), construction (8 weeks), equipment (delivered in 6 weeks), and staff training (3 weeks). How do you schedule this complex project?",
         "choice_a_text": "Create a Gantt chart showing parallel tasks and dependencies - permits first, then construction alongside equipment ordering", 
         "choice_a_exp_reward": 100, "choice_a_cash_change": 1000, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Project management excellence! Gantt charts visualize dependencies. Permits must complete before construction, but equipment can be ordered simultaneously. Critical path analysis shows minimum timeline: 13 weeks total.",
         "choice_b_text": "Start everything at once to move as fast as possible", 
         "choice_b_exp_reward": 40, "choice_b_cash_change": -2000, "choice_b_reputation_change": 1,
         "choice_b_feedback": "Ignoring dependencies wastes resources! You can't construct without permits. Equipment arriving before the building is ready means storage costs. Sequencing based on dependencies is essential.",
         "choice_c_text": "Open them one at a time to reduce complexity", 
         "choice_c_exp_reward": 60, "choice_c_cash_change": 0, "choice_c_reputation_change": 2,
         "choice_c_feedback": "Sequential execution is slower and misses economies of scale! With proper project management, parallel work on three locations shares resources efficiently. Complexity is manageable with good scheduling.", 
         "subskill_focus": "Project Scheduling"},
        
        # Fantasy World
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Operations", "required_level": 6,
         "scenario_title": "L6: Production Scheduling", 
         "scenario_narrative": "You've been contracted to build a wizard's tower. The project requires stone masonry (10 weeks), then enchantment binding (4 weeks), then protective warding (2 weeks). Masonry can't start until foundation stones arrive (3 weeks lead time).",
         "choice_a_text": "Schedule: Order stones immediately, masonry weeks 3-13, enchantment weeks 13-17, warding weeks 17-19", 
         "choice_a_exp_reward": 100, "choice_a_cash_change": 500, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Critical path identified! You correctly sequenced dependent tasks. Ordering stones immediately minimizes wait time. Total project: 19 weeks, with each phase starting only when prerequisites complete.",
         "choice_b_text": "Start enchantment preparation while masonry proceeds to save time", 
         "choice_b_exp_reward": 70, "choice_b_cash_change": 200, "choice_b_reputation_change": 3,
         "choice_b_feedback": "Partial overlap possible! Enchanters can prepare materials while masonry proceeds, but actual binding requires finished stone. This might save 1-2 weeks. Good optimization thinking!",
         "choice_c_text": "Hire more masons to compress the 10-week masonry phase", 
         "choice_c_exp_reward": 60, "choice_c_cash_change": -300, "choice_c_reputation_change": 2,
         "choice_c_feedback": "Crashing the schedule has costs! Additional masons mean higher wages and potential quality issues from crowding. Only accelerate critical path if the timeline savings justify the cost.", 
         "subskill_focus": "Project Scheduling"},
        
        # Sci-Fi World
        {"world_type": "Sci-Fi", "industry": "Mining Corp", "discipline": "Operations", "required_level": 6,
         "scenario_title": "L6: Production Scheduling", 
         "scenario_narrative": "You're deploying an orbital habitat structure. Components arrive over 8 weeks, assembly requires zero-G conditions (next window: weeks 6-10), and system testing takes 4 weeks after assembly. How do you schedule to meet the window?",
         "choice_a_text": "Rush component delivery to complete by week 5, assembly during window weeks 6-10, testing weeks 10-14", 
         "choice_a_exp_reward": 100, "choice_a_cash_change": -10000, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Critical constraint management! The zero-G window is immovable. Compressing component delivery (expensive but possible) enables assembly during the window. Missing the window delays everything by months.",
         "choice_b_text": "Wait for the next zero-G window rather than rush delivery", 
         "choice_b_exp_reward": 50, "choice_b_cash_change": 0, "choice_b_reputation_change": 2,
         "choice_b_feedback": "Delay has costs too! If the next window is months away, you're paying for stored components, delayed revenue, and contract penalties. Sometimes rush fees are cheaper than waiting.",
         "choice_c_text": "Attempt assembly during suboptimal conditions to avoid rush fees", 
         "choice_c_exp_reward": 30, "choice_c_cash_change": -50000, "choice_c_reputation_change": -3,
         "choice_c_feedback": "Safety constraints exist for reasons! Assembly outside proper zero-G conditions risks catastrophic failure. The rush fee is 10,000 credits; failure costs lives and millions. Never compromise safety constraints.", 
         "subskill_focus": "Project Scheduling"},

        # ========== LEVEL 7: Just-In-Time Inventory ==========
        # Modern World
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Operations", "required_level": 7,
         "scenario_title": "L7: Just-In-Time Inventory", 
         "scenario_narrative": "Your walk-in cooler is stuffed with ingredients. Inventory carrying costs (spoilage, space, tied-up cash) total $2,000 monthly. Your supplier offers daily deliveries for a $300/month fee. Should you adopt Just-In-Time inventory?",
         "choice_a_text": "Yes - daily deliveries save $1,700/month ($2,000 costs minus $300 fee) and ensure fresher ingredients", 
         "choice_a_exp_reward": 110, "choice_a_cash_change": 1700, "choice_a_reputation_change": 5,
         "choice_a_feedback": "JIT implementation! Smaller, more frequent deliveries reduce inventory carrying costs. Fresher ingredients improve quality. The math is clear: $300 fee saves $2,000 in costs. Classic operations optimization.",
         "choice_b_text": "No - we need buffer stock in case the supplier fails to deliver", 
         "choice_b_exp_reward": 60, "choice_b_cash_change": 0, "choice_b_reputation_change": 2,
         "choice_b_feedback": "Valid risk concern! JIT requires reliable suppliers. But you can mitigate by keeping minimal safety stock of critical items while reducing bulk inventory. Partial JIT captures most savings.",
         "choice_c_text": "Negotiate: daily delivery with no fee in exchange for exclusivity", 
         "choice_c_exp_reward": 90, "choice_c_cash_change": 2000, "choice_c_reputation_change": 4,
         "choice_c_feedback": "Strategic negotiation! Exclusivity has value to suppliers. If they eliminate competition, they might waive delivery fees. You save the full $2,000. Just ensure exclusivity doesn't lock you into bad pricing.", 
         "subskill_focus": "JIT Operations"},
        
        # Fantasy World
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Operations", "required_level": 7,
         "scenario_title": "L7: Just-In-Time Inventory", 
         "scenario_narrative": "Your cellar holds 3 months of supplies. Storage costs (spoilage, guarding, space) run 200 gold monthly. A merchant offers weekly deliveries for 50 gold/month. The cellar space could be converted to additional seating worth 100 gold/month revenue.",
         "choice_a_text": "Switch to weekly deliveries: save 200 gold storage, pay 50 gold fee, gain 100 gold from new seating = 250 gold/month benefit", 
         "choice_a_exp_reward": 110, "choice_a_cash_change": 250, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Multi-factor JIT analysis! You correctly calculated: storage savings (200) - delivery fee (50) + space conversion (100) = 250 gold monthly benefit. Converting freed space to revenue amplifies JIT benefits.",
         "choice_b_text": "Keep large inventory - what if war blocks the trade routes?", 
         "choice_b_exp_reward": 60, "choice_b_cash_change": 0, "choice_b_reputation_change": 2,
         "choice_b_feedback": "Strategic reserves have value in uncertain times! Perhaps keep 2 weeks buffer instead of 3 months. Balance JIT efficiency against genuine disruption risks. Partial implementation is reasonable.",
         "choice_c_text": "Convert to weekly delivery but keep cellar empty as backup storage", 
         "choice_c_exp_reward": 70, "choice_c_cash_change": 150, "choice_c_reputation_change": 3,
         "choice_c_feedback": "Conservative transition! You save 150 gold (200 storage - 50 fee) while keeping optionality. But empty space earning nothing is still a cost. Consider at least partial conversion.", 
         "subskill_focus": "JIT Operations"},
        
        # Sci-Fi World
        {"world_type": "Sci-Fi", "industry": "Mining Corp", "discipline": "Operations", "required_level": 7,
         "scenario_title": "L7: Just-In-Time Inventory", 
         "scenario_narrative": "Your orbital station maintains 6 months of spare parts. Inventory carrying costs (storage modules, inventory management, capital) total 500,000 credits annually. A supply ship could make monthly runs for 100,000 credits/year. Is JIT feasible in space?",
         "choice_a_text": "Implement JIT for non-critical parts, maintain safety stock for life-critical systems", 
         "choice_a_exp_reward": 110, "choice_a_cash_change": 300000, "choice_a_reputation_change": 6,
         "choice_a_feedback": "Risk-stratified JIT! Non-critical parts (85% of inventory) can go JIT, saving ~400,000 in carrying costs. Life-critical systems keep safety stock because delay cost is infinite. Hybrid approach optimizes both efficiency and safety.",
         "choice_b_text": "Full JIT - monthly supply runs are reliable enough", 
         "choice_b_exp_reward": 60, "choice_b_cash_change": 400000, "choice_b_reputation_change": 2,
         "choice_b_feedback": "Risky in space! One delayed supply run when life support fails is catastrophic. The carrying cost of safety stock for critical items is insurance you can't skip. Pure JIT doesn't fit all environments.",
         "choice_c_text": "No changes - space is too risky for JIT inventory", 
         "choice_c_exp_reward": 40, "choice_c_cash_change": 0, "choice_c_reputation_change": 1,
         "choice_c_feedback": "Overly conservative! While full JIT is dangerous in space, hybrid approaches capture most savings while maintaining critical safety stocks. Analyze item by item rather than blanket rejection.", 
         "subskill_focus": "JIT Operations"},

        # ========== LEVEL 8: Supply Chain Risk Management ==========
        # Modern World
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Operations", "required_level": 8,
         "scenario_title": "L8: Supply Chain Risk Management", 
         "scenario_narrative": "Your restaurant depends on a single supplier for premium coffee beans - 40% of your beverage revenue. That supplier just announced they're being acquired by a competitor. Your supply chain is at risk. What's your mitigation strategy?",
         "choice_a_text": "Immediately qualify a backup supplier and split orders 70/30 to reduce single-source dependency", 
         "choice_a_exp_reward": 120, "choice_a_cash_change": -500, "choice_a_reputation_change": 6,
         "choice_a_feedback": "Supply chain resilience! Dual-sourcing eliminates single points of failure. The backup supplier might cost slightly more, but supply continuity is worth the premium. Never let one supplier control a critical input.",
         "choice_b_text": "Negotiate a long-term contract with the current supplier before the acquisition closes", 
         "choice_b_exp_reward": 80, "choice_b_cash_change": 0, "choice_b_reputation_change": 3,
         "choice_b_feedback": "Contractual protection helps but doesn't eliminate risk! The new owner might honor contracts grudgingly with worse service. Or find legal ways to exit. Contracts plus backup suppliers provide real security.",
         "choice_c_text": "Wait and see - the acquisition might not change anything", 
         "choice_c_exp_reward": 30, "choice_c_cash_change": 0, "choice_c_reputation_change": 0,
         "choice_c_feedback": "Passive risk acceptance! If the new owner raises prices or drops you, you'll scramble for alternatives under pressure. Proactive qualification of alternatives costs little and provides insurance.", 
         "subskill_focus": "Risk Management"},
        
        # Fantasy World
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Operations", "required_level": 8,
         "scenario_title": "L8: Supply Chain Risk Management", 
         "scenario_narrative": "Your most valuable brew requires Moonstone from a single mine in the Elvish lands. Border tensions are rising between the kingdoms. If trade routes close, you lose your signature product. How do you manage this supply chain risk?",
         "choice_a_text": "Find an alternative Moonstone source (even if more expensive) and stockpile 6 months supply as buffer", 
         "choice_a_exp_reward": 120, "choice_a_cash_change": -1000, "choice_a_reputation_change": 6,
         "choice_a_feedback": "Comprehensive risk mitigation! Alternative sourcing eliminates single-point dependency. Strategic stockpile provides time buffer if war actually closes routes. The cost is insurance against business interruption.",
         "choice_b_text": "Develop a substitute recipe that doesn't require Moonstone", 
         "choice_b_exp_reward": 90, "choice_b_cash_change": -300, "choice_b_reputation_change": 4,
         "choice_b_feedback": "Product adaptation! If you can create an alternative that customers accept, you eliminate the supply risk entirely. But test market acceptance before the crisis - you need this ready in advance.",
         "choice_c_text": "Hope tensions ease - wars are bad for everyone's business", 
         "choice_c_exp_reward": 25, "choice_c_cash_change": 0, "choice_c_reputation_change": 0,
         "choice_c_feedback": "Hope isn't a strategy! Even if war is unlikely, the cost of preparation is low compared to business interruption. Risk management means preparing for bad outcomes, not hoping they won't happen.", 
         "subskill_focus": "Risk Management"},
        
        # Sci-Fi World
        {"world_type": "Sci-Fi", "industry": "Mining Corp", "discipline": "Operations", "required_level": 8,
         "scenario_title": "L8: Supply Chain Risk Management", 
         "scenario_narrative": "Your primary supply route passes through an asteroid field now contested in a trade war. Alternative routes add 40% to shipping costs. Your supply chain analysis shows this route handles 80% of your incoming materials.",
         "choice_a_text": "Immediately diversify: 50% primary route, 30% expensive alternative, 20% local sourcing development", 
         "choice_a_exp_reward": 120, "choice_a_cash_change": -100000, "choice_a_reputation_change": 6,
         "choice_a_feedback": "Strategic diversification! Higher costs now prevent catastrophic disruption later. Local sourcing development builds long-term independence. Supply chain resilience is a competitive advantage in unstable regions.",
         "choice_b_text": "Stockpile 12 months of critical materials while the route is still open", 
         "choice_b_exp_reward": 80, "choice_b_cash_change": -500000, "choice_b_reputation_change": 4,
         "choice_b_feedback": "Buffer strategy! Stockpiling buys time but doesn't solve the underlying problem. If the blockade lasts longer than your stockpile, you're back to the same crisis. Combine stockpiling with route diversification.",
         "choice_c_text": "Lobby both sides of the trade war for neutral passage rights", 
         "choice_c_exp_reward": 60, "choice_c_cash_change": -50000, "choice_c_reputation_change": 3,
         "choice_c_feedback": "Diplomatic approach can work! Neutral status in trade conflicts is valuable. But political solutions aren't guaranteed. Continue physical diversification while pursuing diplomatic options.", 
         "subskill_focus": "Risk Management"},

        # ========== LEVEL 9: Outsourcing and Offshoring ==========
        # Modern World
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Operations", "required_level": 9,
         "scenario_title": "L9: Outsourcing and Offshoring", 
         "scenario_narrative": "A commissary kitchen offers to prepare your sauces, doughs, and prep work at 30% lower cost than in-house. This would free your kitchen for cooking only. But you'd lose direct control over these foundation elements.",
         "choice_a_text": "Outsource commodity prep (doughs, basic stocks) but keep signature sauces in-house for quality control", 
         "choice_a_exp_reward": 130, "choice_a_cash_change": 2000, "choice_a_reputation_change": 6,
         "choice_a_feedback": "Strategic outsourcing! Commodity items where quality is standardized benefit from outsourcing. Signature items that define your brand stay in-house. This captures cost savings while protecting differentiation.",
         "choice_b_text": "Keep everything in-house - quality and consistency are worth the extra cost", 
         "choice_b_exp_reward": 70, "choice_b_cash_change": 0, "choice_b_reputation_change": 3,
         "choice_b_feedback": "Valid for premium positioning! If your brand depends on 'everything made fresh in-house,' outsourcing undermines your story. But verify customers actually value and notice the difference for commodity items.",
         "choice_c_text": "Outsource everything prep-related to maximize cost savings", 
         "choice_c_exp_reward": 50, "choice_c_cash_change": 3000, "choice_c_reputation_change": 0,
         "choice_c_feedback": "Risk of commoditization! If your sauces taste like every other restaurant using the same commissary, what's your differentiation? Outsourcing core elements can save money but erode competitive advantage.", 
         "subskill_focus": "Make vs Buy"},
        
        # Fantasy World
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Operations", "required_level": 9,
         "scenario_title": "L9: Outsourcing and Offshoring", 
         "scenario_narrative": "A dwarven brewing guild offers to produce your standard ales at 40% lower cost, freeing your brewmasters to focus on premium specialty brews. Your standard ales are 60% of volume but only 30% of profit.",
         "choice_a_text": "Outsource standard ales, refocus in-house on high-margin specialty brews that differentiate us", 
         "choice_a_exp_reward": 130, "choice_a_cash_change": 1500, "choice_a_reputation_change": 6,
         "choice_a_feedback": "Strategic focus! Outsourcing low-margin commodity production frees expert resources for high-value specialty work. You capture cost savings on 60% of volume while improving the 30% that drives profit.",
         "choice_b_text": "Keep all brewing in-house - our reputation depends on craftsmanship", 
         "choice_b_exp_reward": 70, "choice_b_cash_change": 0, "choice_b_reputation_change": 4,
         "choice_b_feedback": "Brand protection strategy! If customers associate your tavern with artisanal everything, outsourcing changes that perception. Verify whether standard ale customers actually distinguish your brew from dwarven mass production.",
         "choice_c_text": "Outsource specialty brews too - focus on running the tavern, not brewing", 
         "choice_c_exp_reward": 40, "choice_c_cash_change": 2000, "choice_c_reputation_change": -2,
         "choice_c_feedback": "Dangerous commoditization! If you outsource everything distinctive, you become a generic tavern. Your specialty brews are your competitive advantage - outsourcing them surrenders differentiation.", 
         "subskill_focus": "Make vs Buy"},
        
        # Sci-Fi World
        {"world_type": "Sci-Fi", "industry": "Mining Corp", "discipline": "Operations", "required_level": 9,
         "scenario_title": "L9: Outsourcing and Offshoring", 
         "scenario_narrative": "A manufacturing consortium on a low-cost planet offers to build your mining drones at 50% savings. Currently you manufacture in-house, giving you quality control and fast customization. The consortium's quality is 'acceptable' but not premium.",
         "choice_a_text": "Outsource standard drones, keep specialized/custom drone manufacturing in-house", 
         "choice_a_exp_reward": 130, "choice_a_cash_change": 500000, "choice_a_reputation_change": 6,
         "choice_a_feedback": "Tiered manufacturing strategy! Standard drones are commodity - acceptable quality at 50% savings makes sense. Custom/specialized drones are competitive advantage - keep control. Classic make vs. buy optimization.",
         "choice_b_text": "Maintain in-house manufacturing for full quality control and customization speed", 
         "choice_b_exp_reward": 80, "choice_b_cash_change": 0, "choice_b_reputation_change": 4,
         "choice_b_feedback": "Vertical integration has value! If drone reliability is critical to operations or quick customization provides competitive advantage, the premium may be justified. Quantify the value before deciding.",
         "choice_c_text": "Full outsourcing to the consortium for maximum cost reduction", 
         "choice_c_exp_reward": 50, "choice_c_cash_change": 800000, "choice_c_reputation_change": -1,
         "choice_c_feedback": "Cost focus ignores capability loss! 'Acceptable' quality may mean more failures. Lost customization speed may cost contracts. And you've transferred your manufacturing capability to a potential future competitor.", 
         "subskill_focus": "Make vs Buy"},

        # ========== LEVEL 10: Process Innovation & Automation ==========
        # Modern World
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Operations", "required_level": 10,
         "scenario_title": "L10: Process Innovation & Automation", 
         "scenario_narrative": "A robotics company offers automated prep stations that can handle 80% of kitchen prep work, reducing staff needs by 50% and improving consistency. Investment: $200,000. Payback period: 18 months. Your staff are concerned about job losses.",
         "choice_a_text": "Implement automation for prep, retrain displaced workers for customer service and quality oversight roles", 
         "choice_a_exp_reward": 150, "choice_a_cash_change": -200000, "choice_a_reputation_change": 8,
         "choice_a_feedback": "Responsible automation! You capture efficiency gains while creating new roles for existing staff. Customer service and quality oversight can't be automated. This approach builds loyalty and captures innovation benefits.",
         "choice_b_text": "Full automation with workforce reduction - business survival requires efficiency", 
         "choice_b_exp_reward": 100, "choice_b_cash_change": -200000, "choice_b_reputation_change": 2,
         "choice_b_feedback": "Efficiency gains achieved but at reputation cost. Layoffs create negative publicity and lose institutional knowledge. The financial math works, but community relationships and employee morale suffer.",
         "choice_c_text": "Reject automation - our people are our competitive advantage", 
         "choice_c_exp_reward": 60, "choice_c_cash_change": 0, "choice_c_reputation_change": 3,
         "choice_c_feedback": "Competitor risk! If rivals automate and achieve 50% lower costs, they can undercut your prices. Rejecting all automation may preserve culture short-term but risks long-term competitiveness.", 
         "subskill_focus": "Automation Strategy"},
        
        # Fantasy World
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Operations", "required_level": 10,
         "scenario_title": "L10: Process Innovation & Automation", 
         "scenario_narrative": "A gnomish artificer offers enchanted brewing equipment that automates temperature control, timing, and mixing - tripling output while reducing labor by 60%. Cost: 10,000 gold. Your master brewer calls it 'soulless mechanical ale.'",
         "choice_a_text": "Implement for standard production, keep master brewer focused on premium artisanal batches", 
         "choice_a_exp_reward": 150, "choice_a_cash_change": -10000, "choice_a_reputation_change": 8,
         "choice_a_feedback": "Hybrid approach! Automation handles volume efficiently while craftsmanship creates premium products. The master brewer's skills now focus where they add most value. You get scale AND quality differentiation.",
         "choice_b_text": "Full automation to compete with larger breweries on price", 
         "choice_b_exp_reward": 90, "choice_b_cash_change": -10000, "choice_b_reputation_change": 3,
         "choice_b_feedback": "Volume strategy! If your market is price-sensitive, automation enables competition. But verify you can actually match large brewery distribution. Automation without scale may not achieve price competitiveness.",
         "choice_c_text": "Reject the machinery - our hand-crafted ale is what makes us special", 
         "choice_c_exp_reward": 60, "choice_c_cash_change": 0, "choice_c_reputation_change": 4,
         "choice_c_feedback": "Artisanal positioning is valid! If customers pay premium for 'hand-crafted,' automation undermines your value proposition. But monitor competitors - if everyone automates, hand-crafted becomes expensive niche.", 
         "subskill_focus": "Automation Strategy"},
        
        # Sci-Fi World
        {"world_type": "Sci-Fi", "industry": "Mining Corp", "discipline": "Operations", "required_level": 10,
         "scenario_title": "L10: Process Innovation & Automation", 
         "scenario_narrative": "An AI company offers fully autonomous mining drones with neural network optimization. They promise 200% productivity increase and 80% reduction in human operators. Investment: 5,000,000 credits. Human operators' union threatens strike.",
         "choice_a_text": "Implement with transition program: redeploy operators to drone supervision, maintenance, and remote exploration", 
         "choice_a_exp_reward": 150, "choice_a_cash_change": -5000000, "choice_a_reputation_change": 8,
         "choice_a_feedback": "Strategic transformation! Autonomous drones need human oversight, maintenance, and problem-solving for edge cases. Redeployment captures productivity gains while honoring workforce commitments. Industry leadership position achieved.",
         "choice_b_text": "Full automation with workforce reduction - shareholders demand efficiency", 
         "choice_b_exp_reward": 100, "choice_b_cash_change": -5000000, "choice_b_reputation_change": 1,
         "choice_b_feedback": "Maximum efficiency, maximum disruption. Strike likely delays implementation. Laid-off workers become competitors or critics. The math works but social license to operate is damaged. Consider long-term reputation costs.",
         "choice_c_text": "Delay until union concerns are fully resolved - technology can wait", 
         "choice_c_exp_reward": 50, "choice_c_cash_change": 0, "choice_c_reputation_change": 2,
         "choice_c_feedback": "Competitors won't wait! If rivals implement autonomous mining, your cost structure becomes uncompetitive. Negotiated transition is better than indefinite delay. Find a path forward that addresses concerns while capturing benefits.", 
         "subskill_focus": "Automation Strategy"},
    ]
    
    for scenario in scenarios:
        cur.execute("""
            INSERT INTO scenario_master (world_type, industry, discipline, required_level, scenario_title, scenario_narrative,
                choice_a_text, choice_a_exp_reward, choice_a_cash_change, choice_a_reputation_change, choice_a_feedback,
                choice_b_text, choice_b_exp_reward, choice_b_cash_change, choice_b_reputation_change, choice_b_feedback,
                choice_c_text, choice_c_exp_reward, choice_c_cash_change, choice_c_reputation_change, choice_c_feedback,
                subskill_focus)
            VALUES (%(world_type)s, %(industry)s, %(discipline)s, %(required_level)s, %(scenario_title)s, %(scenario_narrative)s,
                %(choice_a_text)s, %(choice_a_exp_reward)s, %(choice_a_cash_change)s, %(choice_a_reputation_change)s, %(choice_a_feedback)s,
                %(choice_b_text)s, %(choice_b_exp_reward)s, %(choice_b_cash_change)s, %(choice_b_reputation_change)s, %(choice_b_feedback)s,
                %(choice_c_text)s, %(choice_c_exp_reward)s, %(choice_c_cash_change)s, %(choice_c_reputation_change)s, %(choice_c_feedback)s,
                %(subskill_focus)s)
        """, scenario)
    
    conn.commit()
    print(f"Seeded {len(scenarios)} Operations Curriculum scenarios (Levels 1-10, 3 worlds)!")
    cur.close()
    conn.close()


def seed_hr_curriculum():
    """Seed the complete 10-level Human Resources Curriculum across 3 worlds (30 scenarios total).
    
    Curriculum Structure:
    - L1-L3: Acquisition & Compliance (Job Description, Legal Hiring, Onboarding)
    - L4-L6: Performance & Engagement (Performance Management, Compensation, Employee Morale)
    - L7-L8: Conflict & Legal Risk (Conflict Resolution, Termination)
    - L9-L10: Strategy & Mastery (Succession Planning, Labor Relations)
    """
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM scenario_master WHERE discipline = 'Human Resources' AND scenario_title LIKE 'L%:%'")
    result = cur.fetchone()
    if result['count'] >= 30:
        print("HR curriculum already seeded.")
        cur.close()
        conn.close()
        return
    
    scenarios = [
        # ========== LEVEL 1: Job Description & Needs Analysis ==========
        # Modern World
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Human Resources", "required_level": 1,
         "scenario_title": "L1: Job Description & Needs Analysis", 
         "scenario_narrative": "Your head chef just quit unexpectedly. Before posting the job, you need to clearly define what skills and responsibilities are needed. A vague job description will attract the wrong candidates.",
         "choice_a_text": "Write a detailed job description listing required skills, experience levels, daily duties, and reporting structure", 
         "choice_a_exp_reward": 50, "choice_a_cash_change": 0, "choice_a_reputation_change": 3,
         "choice_a_feedback": "Excellent talent identification! A clear job description attracts qualified candidates who understand the role. Defining exact skills (knife work, menu development) and responsibilities (inventory, staff scheduling) filters out poor fits before interviews begin.",
         "choice_b_text": "Post 'Head Chef Wanted - Great Pay!' and see who applies", 
         "choice_b_exp_reward": 20, "choice_b_cash_change": -500, "choice_b_reputation_change": 0,
         "choice_b_feedback": "Vague postings attract vague candidates! You'll waste time interviewing unqualified applicants. Talent identification requires defining needs BEFORE searching. What cuisine experience? What management skills?",
         "choice_c_text": "Promote the sous chef immediately - they already know the kitchen", 
         "choice_c_exp_reward": 35, "choice_c_cash_change": 0, "choice_c_reputation_change": 2,
         "choice_c_feedback": "Internal promotion can work, but did you analyze if the sous chef has HEAD chef skills? Managing a team is different from assisting. Always conduct a needs analysis even for internal candidates.", 
         "subskill_focus": "Talent Identification"},
        
        # Fantasy World
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Human Resources", "required_level": 1,
         "scenario_title": "L1: Job Description & Needs Analysis", 
         "scenario_narrative": "Your tavern needs a new Brewmaster after the previous one departed to join an adventuring party. The Guild requires you to register the position with specific skill requirements before recruiting.",
         "choice_a_text": "Document requirements: brewing expertise, ingredient knowledge, quality testing, apprentice training responsibilities", 
         "choice_a_exp_reward": 50, "choice_a_cash_change": 0, "choice_a_reputation_change": 3,
         "choice_a_feedback": "Proper talent identification! The Guild approves your detailed posting. By specifying that candidates need experience with both common ales AND exotic magical brews, you'll attract masters, not novices.",
         "choice_b_text": "Ask the Guild to send anyone who can brew - we're desperate", 
         "choice_b_exp_reward": 20, "choice_b_cash_change": -200, "choice_b_reputation_change": 0,
         "choice_b_feedback": "Desperation leads to poor hires! The Guild sends an apprentice who can make basic mead but not your signature Dragon Fire Ale. Define requirements clearly to find the right talent.",
         "choice_c_text": "Offer the position to a regular customer who claims to know brewing", 
         "choice_c_exp_reward": 25, "choice_c_cash_change": -300, "choice_c_reputation_change": -1,
         "choice_c_feedback": "Drinking ale doesn't mean one can brew it! Without a proper needs analysis, you hired based on claims, not verified skills. First batch ruins your reputation.", 
         "subskill_focus": "Talent Identification"},
        
        # Sci-Fi World
        {"world_type": "Sci-Fi", "industry": "Mining Corp", "discipline": "Human Resources", "required_level": 1,
         "scenario_title": "L1: Job Description & Needs Analysis", 
         "scenario_narrative": "Your Chief Mining Engineer is transferring to a competitor. The Galactic HR Registry requires all positions be defined with specific competency matrices before recruitment can begin.",
         "choice_a_text": "Create detailed competency matrix: zero-G mining experience, exotic materials certification, drone fleet management, safety protocols", 
         "choice_a_exp_reward": 50, "choice_a_cash_change": 0, "choice_a_reputation_change": 3,
         "choice_a_feedback": "Comprehensive talent identification! The Registry approves immediately. Your competency matrix clearly distinguishes between planetary and asteroid mining experience - critical for this role.",
         "choice_b_text": "Copy the job description from when we hired the previous engineer 10 years ago", 
         "choice_b_exp_reward": 30, "choice_b_cash_change": 0, "choice_b_reputation_change": 1,
         "choice_b_feedback": "Technology has changed! That old description doesn't mention drone fleet management or quantum extraction techniques. Needs analysis must reflect CURRENT requirements, not historical ones.",
         "choice_c_text": "Let the algorithm auto-generate requirements based on industry averages", 
         "choice_c_exp_reward": 35, "choice_c_cash_change": 0, "choice_c_reputation_change": 1,
         "choice_c_feedback": "Algorithms provide baselines but miss your unique needs! Your operation mines rare isotopes requiring specialized certifications. Generic requirements attract generic candidates.", 
         "subskill_focus": "Talent Identification"},

        # ========== LEVEL 2: Legal & Ethical Hiring ==========
        # Modern World
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Human Resources", "required_level": 2,
         "scenario_title": "L2: Legal & Ethical Hiring", 
         "scenario_narrative": "You're interviewing candidates for a server position. During the interview, you're tempted to ask about family plans, age, and religious observances that might affect scheduling. These questions seem practical but could violate Equal Employment Opportunity (EEO) laws.",
         "choice_a_text": "Stick to job-related questions only: availability, experience, skills - never ask about protected characteristics", 
         "choice_a_exp_reward": 60, "choice_a_cash_change": 0, "choice_a_reputation_change": 4,
         "choice_a_feedback": "EEO compliance achieved! Anti-discrimination law prohibits questions about age, religion, family status, pregnancy, and other protected characteristics. Ask about availability directly without probing reasons. 'Can you work weekends?' is legal; 'Do you go to church on Sundays?' is not.",
         "choice_b_text": "Ask about family plans to ensure they can commit long-term", 
         "choice_b_exp_reward": 15, "choice_b_cash_change": -2000, "choice_b_reputation_change": -3,
         "choice_b_feedback": "EEO violation! Asking about family plans is illegal because it can discriminate against women and parents. Even if you don't intend discrimination, the question itself creates legal liability. Small fine issued.",
         "choice_c_text": "Have a manager casually ask these questions 'off the record'", 
         "choice_c_exp_reward": 10, "choice_c_cash_change": -3000, "choice_c_reputation_change": -4,
         "choice_c_feedback": "Attempting to circumvent the law makes it worse! 'Off the record' questions are still illegal and show intentional violation. Larger fine and possible lawsuit from rejected candidate.", 
         "subskill_focus": "Employment Law"},
        
        # Fantasy World
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Human Resources", "required_level": 2,
         "scenario_title": "L2: Legal & Ethical Hiring", 
         "scenario_narrative": "The Guild enforces fair hiring practices across all races and magical alignments. A highly qualified elf applies for your bouncer position, but some customers prefer human-only staff. An equally qualified dwarf also applies.",
         "choice_a_text": "Evaluate all candidates purely on job-relevant qualifications: strength, conflict resolution skills, experience", 
         "choice_a_exp_reward": 60, "choice_a_cash_change": 0, "choice_a_reputation_change": 4,
         "choice_a_feedback": "Guild-compliant hiring! Discrimination based on race (human, elf, dwarf) or magical alignment violates Guild law. The elf with superior conflict resolution skills gets the job. Some customers grumble but most respect fair treatment.",
         "choice_b_text": "Hire the human to avoid customer complaints", 
         "choice_b_exp_reward": 20, "choice_b_cash_change": -500, "choice_b_reputation_change": -2,
         "choice_b_feedback": "Guild violation! Customer preference doesn't justify discrimination. The Guild fines you and word spreads that your tavern discriminates. You lose more customers than you kept.",
         "choice_c_text": "Create separate 'human nights' and 'all-races nights' to satisfy everyone", 
         "choice_c_exp_reward": 15, "choice_c_cash_change": -800, "choice_c_reputation_change": -3,
         "choice_c_feedback": "Segregation violates Guild principles! Separate is not equal. Heavy fine and required diversity training for all staff.", 
         "subskill_focus": "Employment Law"},
        
        # Sci-Fi World
        {"world_type": "Sci-Fi", "industry": "Mining Corp", "discipline": "Human Resources", "required_level": 2,
         "scenario_title": "L2: Legal & Ethical Hiring", 
         "scenario_narrative": "You're hiring for a hazardous asteroid extraction role. Two candidates apply: a Terran human and a Synthetic (android) worker. The Galactic Employment Act prohibits discrimination based on species or origin, including artificial beings.",
         "choice_a_text": "Evaluate both on job qualifications: safety record, technical skills, team compatibility - regardless of origin", 
         "choice_a_exp_reward": 60, "choice_a_cash_change": 0, "choice_a_reputation_change": 4,
         "choice_a_feedback": "Full compliance with Galactic Employment Act! The Synthetic has a superior safety record and doesn't require life support, making them ideal for vacuum work. Merit-based hiring wins.",
         "choice_b_text": "Hire the human - organics work better with the current crew", 
         "choice_b_exp_reward": 20, "choice_b_cash_change": -5000, "choice_b_reputation_change": -2,
         "choice_b_feedback": "Species discrimination! The Galactic Employment Board investigates and issues a citation. 'Cultural fit' cannot mask discrimination. If crews don't work well with Synthetics, train the crew.",
         "choice_c_text": "Ask the Synthetic about their 'creation date' to assess experience", 
         "choice_c_exp_reward": 25, "choice_c_cash_change": -2000, "choice_c_reputation_change": -1,
         "choice_c_feedback": "Creation date questions are equivalent to asking a human's age - discriminatory! Ask about years of experience in the field, not existence. Citation issued.", 
         "subskill_focus": "Employment Law"},

        # ========== LEVEL 3: Onboarding & Training ==========
        # Modern World
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Human Resources", "required_level": 3,
         "scenario_title": "L3: Onboarding & Training", 
         "scenario_narrative": "Your new line cook starts Monday. Without proper onboarding, new hires often feel lost, make mistakes, and quit within weeks. You need a structured integration process covering systems, culture, and safety.",
         "choice_a_text": "Create a 3-day training program: Day 1 orientation/safety, Day 2 systems training, Day 3 shadowing experienced staff", 
         "choice_a_exp_reward": 70, "choice_a_cash_change": 300, "choice_a_reputation_change": 4,
         "choice_a_feedback": "Excellent onboarding structure! New hires who receive proper training become productive faster and stay longer. Your program covers safety protocols (preventing injuries), POS systems (preventing errors), and culture (building team connection).",
         "choice_b_text": "Just have them watch and learn - cooking is hands-on", 
         "choice_b_exp_reward": 25, "choice_b_cash_change": -200, "choice_b_reputation_change": 0,
         "choice_b_feedback": "Sink-or-swim causes drowning! Without structured training, new hires don't learn safety protocols, make avoidable mistakes, and feel unsupported. Many quit within the first month.",
         "choice_c_text": "Give them the employee handbook and have them start immediately", 
         "choice_c_exp_reward": 30, "choice_c_cash_change": 0, "choice_c_reputation_change": 1,
         "choice_c_feedback": "Reading isn't doing! Handbooks provide reference but don't replace hands-on training. New cook makes errors because reading about the kitchen isn't the same as learning it.", 
         "subskill_focus": "Employee Integration"},
        
        # Fantasy World
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Human Resources", "required_level": 3,
         "scenario_title": "L3: Onboarding & Training", 
         "scenario_narrative": "A new apprentice joins your tavern. The Guild requires all establishments to provide proper craft training, but many tavern owners just throw apprentices into service unprepared.",
         "choice_a_text": "Design a week-long apprenticeship program: Guild traditions, brewing basics, customer service, safety around magical ingredients", 
         "choice_a_exp_reward": 70, "choice_a_cash_change": -100, "choice_a_reputation_change": 4,
         "choice_a_feedback": "Exemplary onboarding! The Guild commends your training program. Apprentices learn proper handling of enchanted ingredients (preventing accidents), brewing fundamentals (ensuring quality), and customer customs (avoiding conflicts).",
         "choice_b_text": "Assign them to follow the senior barmaid - they'll learn by watching", 
         "choice_b_exp_reward": 35, "choice_b_cash_change": 0, "choice_b_reputation_change": 1,
         "choice_b_feedback": "Observation has limits. The barmaid is busy serving, not teaching. Apprentice learns bad habits alongside good ones. No structured progression means inconsistent skills.",
         "choice_c_text": "Send them to the Guild training center - let them handle it", 
         "choice_c_exp_reward": 40, "choice_c_cash_change": -200, "choice_c_reputation_change": 2,
         "choice_c_feedback": "Guild training covers fundamentals but not YOUR specific methods! They return knowing generic skills but not your special recipes or customer base. Internal onboarding is still essential.", 
         "subskill_focus": "Employee Integration"},
        
        # Sci-Fi World
        {"world_type": "Sci-Fi", "industry": "Mining Corp", "discipline": "Human Resources", "required_level": 3,
         "scenario_title": "L3: Onboarding & Training", 
         "scenario_narrative": "New zero-gravity extraction technicians arrive at your orbital station. The Galactic Safety Authority requires documented training before they can operate equipment. Proper onboarding prevents accidents and regulatory violations.",
         "choice_a_text": "Implement comprehensive program: safety certification, equipment simulation, emergency protocols, cultural integration with existing crew", 
         "choice_a_exp_reward": 70, "choice_a_cash_change": -2000, "choice_a_reputation_change": 4,
         "choice_a_feedback": "Industry-leading onboarding! Safety Authority approves your training documentation. Simulation prevents costly real-equipment mistakes. Emergency protocol training could save lives. Well-integrated crews work better together.",
         "choice_b_text": "Fast-track them through safety videos so they can start producing immediately", 
         "choice_b_exp_reward": 25, "choice_b_cash_change": -5000, "choice_b_reputation_change": -2,
         "choice_b_feedback": "Videos aren't verification! First week, undertrained tech causes equipment damage. Safety Authority audit finds inadequate documentation. Fines exceed what you saved by rushing.",
         "choice_c_text": "Partner them with experienced operators for on-the-job training only", 
         "choice_c_exp_reward": 40, "choice_c_cash_change": 0, "choice_c_reputation_change": 2,
         "choice_c_feedback": "OJT is valuable but insufficient for documentation. Safety Authority requires CERTIFIED training, not just experience. You'll need to supplement with formal certification anyway.", 
         "subskill_focus": "Employee Integration"},

        # ========== LEVEL 4: Performance Management ==========
        # Modern World
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Human Resources", "required_level": 4,
         "scenario_title": "L4: Performance Management", 
         "scenario_narrative": "Quarterly reviews are approaching. Some servers have no clear goals to measure against, making evaluations subjective and contentious. You need to implement SMART goals (Specific, Measurable, Achievable, Relevant, Time-bound).",
         "choice_a_text": "Set SMART goals for each position: 'Achieve 95% customer satisfaction scores this quarter' instead of 'be friendly'", 
         "choice_a_exp_reward": 80, "choice_a_cash_change": 500, "choice_a_reputation_change": 4,
         "choice_a_feedback": "Performance management excellence! SMART goals remove subjectivity. '95% satisfaction' is measurable; 'be friendly' is opinion. Staff know exactly what success looks like and can track their progress.",
         "choice_b_text": "Use general ratings: Excellent/Good/Needs Improvement based on manager opinion", 
         "choice_b_exp_reward": 35, "choice_b_cash_change": 0, "choice_b_reputation_change": 1,
         "choice_b_feedback": "Subjective ratings cause disputes! What's 'Excellent' to one manager is 'Good' to another. Without specific metrics, employees feel unfairly judged and reviews become arguments.",
         "choice_c_text": "Skip formal goals - just address problems when they arise", 
         "choice_c_exp_reward": 20, "choice_c_cash_change": -300, "choice_c_reputation_change": 0,
         "choice_c_feedback": "Reactive management fails! Without goals, staff don't know expectations until they're already failing. Proactive goal-setting prevents problems rather than just punishing them.", 
         "subskill_focus": "Goal Setting"},
        
        # Fantasy World
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Human Resources", "required_level": 4,
         "scenario_title": "L4: Performance Management", 
         "scenario_narrative": "The Guild requires annual performance assessments for all journeymen. Your staff have been working without clear objectives, making evaluations arbitrary. You need measurable criteria.",
         "choice_a_text": "Establish clear guild-standard metrics: drinks served per shift, customer complaints, recipe mastery demonstrations", 
         "choice_a_exp_reward": 80, "choice_a_cash_change": 200, "choice_a_reputation_change": 4,
         "choice_a_feedback": "Proper performance management! Measurable standards let journeymen track their own progress toward master status. 'Brew 50 barrels with less than 2% waste' is a clear target to hit.",
         "choice_b_text": "Base evaluations on seniority - longer service means better performance", 
         "choice_b_exp_reward": 30, "choice_b_cash_change": 0, "choice_b_reputation_change": 0,
         "choice_b_feedback": "Seniority isn't skill! A 10-year employee coasting produces less than an ambitious 2-year journeyman. Performance management must measure actual performance, not just time served.",
         "choice_c_text": "Let each staff member set their own goals however they wish", 
         "choice_c_exp_reward": 40, "choice_c_cash_change": 0, "choice_c_reputation_change": 1,
         "choice_c_feedback": "Self-set goals vary wildly! One sets 'work harder' while another sets 'maintain current level.' Goals must align with tavern objectives and be comparable across staff.", 
         "subskill_focus": "Goal Setting"},
        
        # Sci-Fi World
        {"world_type": "Sci-Fi", "industry": "Mining Corp", "discipline": "Human Resources", "required_level": 4,
         "scenario_title": "L4: Performance Management", 
         "scenario_narrative": "Your extraction teams have no standardized performance metrics. Some supervisors reward ore quantity while others prioritize safety. The inconsistency causes confusion and resentment among workers.",
         "choice_a_text": "Implement balanced scorecard: extraction volume, safety incidents, equipment maintenance, team collaboration scores", 
         "choice_a_exp_reward": 80, "choice_a_cash_change": 1000, "choice_a_reputation_change": 4,
         "choice_a_feedback": "Comprehensive performance management! Balanced scorecards prevent gaming single metrics. Teams can't sacrifice safety for volume or neglect equipment for short-term gains. All objectives matter.",
         "choice_b_text": "Focus purely on ore extracted - that's what generates revenue", 
         "choice_b_exp_reward": 40, "choice_b_cash_change": 2000, "choice_b_reputation_change": -1,
         "choice_b_feedback": "Single-metric focus backfires! Teams cut corners on safety and maintenance to maximize volume. Equipment failures and injuries soon exceed productivity gains. Balance matters.",
         "choice_c_text": "Let each team lead define their own performance standards", 
         "choice_c_exp_reward": 35, "choice_c_cash_change": 0, "choice_c_reputation_change": 1,
         "choice_c_feedback": "Inconsistent standards cause unfairness! Workers transferring between teams face different expectations. Corporation-wide standards ensure equity and clarity.", 
         "subskill_focus": "Goal Setting"},

        # ========== LEVEL 5: Compensation & Benefits ==========
        # Modern World
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Human Resources", "required_level": 5,
         "scenario_title": "L5: Compensation & Benefits", 
         "scenario_narrative": "Your mid-level kitchen staff are receiving offers from competitors. To retain talent, you need to design a competitive total rewards package balancing salary, bonuses, and benefits like health insurance and paid time off.",
         "choice_a_text": "Create tiered benefits package: health insurance, performance bonuses, PTO, and meal allowances - analyze competitor offerings first", 
         "choice_a_exp_reward": 90, "choice_a_cash_change": -1000, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Total rewards strategy! Compensation isn't just salary. Health insurance, bonuses, and PTO have real value to employees. Your competitive analysis ensures you match market without overspending.",
         "choice_b_text": "Just increase base salary - that's what people really care about", 
         "choice_b_exp_reward": 50, "choice_b_cash_change": -2000, "choice_b_reputation_change": 2,
         "choice_b_feedback": "Salary alone is expensive! A $3/hour raise costs more than equivalent health benefits. Many employees value stability (insurance) over marginal cash. Understand total compensation value.",
         "choice_c_text": "Offer minimal benefits and hire replacements when people leave", 
         "choice_c_exp_reward": 25, "choice_c_cash_change": -500, "choice_c_reputation_change": -2,
         "choice_c_feedback": "Turnover is expensive! Recruiting, hiring, and training replacements costs more than retention benefits. High turnover also hurts service quality and team morale.", 
         "subskill_focus": "Total Rewards"},
        
        # Fantasy World
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Human Resources", "required_level": 5,
         "scenario_title": "L5: Compensation & Benefits", 
         "scenario_narrative": "Other taverns are luring away your trained staff with better compensation. You need to design a rewards package that competes while controlling costs. Gold isn't the only currency of value.",
         "choice_a_text": "Offer combination: competitive wages, profit sharing on busy nights, room and board, and Guild certification sponsorship", 
         "choice_a_exp_reward": 90, "choice_a_cash_change": -300, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Creative total rewards! Room and board has real value without cash outlay. Guild sponsorship invests in their future. Profit sharing aligns their success with yours. Staff stay for the whole package.",
         "choice_b_text": "Match competitor wages exactly - gold for gold", 
         "choice_b_exp_reward": 50, "choice_b_cash_change": -600, "choice_b_reputation_change": 2,
         "choice_b_feedback": "Wage wars drain gold! If competitors raise wages again, you must match again. Non-cash benefits create differentiation that pure salary can't. Think beyond gold.",
         "choice_c_text": "Remind staff of their loyalty obligations under Guild apprenticeship oaths", 
         "choice_c_exp_reward": 20, "choice_c_cash_change": 0, "choice_c_reputation_change": -2,
         "choice_c_feedback": "Guilt doesn't retain talent! Oaths cover basic obligations, not enthusiasm. Resentful staff who feel trapped provide poor service. Earn loyalty through fair treatment.", 
         "subskill_focus": "Total Rewards"},
        
        # Sci-Fi World
        {"world_type": "Sci-Fi", "industry": "Mining Corp", "discipline": "Human Resources", "required_level": 5,
         "scenario_title": "L5: Compensation & Benefits", 
         "scenario_narrative": "Your skilled technicians receive offers from competing corps. In space, benefits packages must address unique needs: hazard pay, family communication allowances, return-to-Earth leave, and medical coverage.",
         "choice_a_text": "Design comprehensive space-worker package: hazard differentials, quarterly Earth leave, family video credits, full medical with evacuation coverage", 
         "choice_a_exp_reward": 90, "choice_a_cash_change": -5000, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Industry-leading total rewards! Space workers value different things than planet-based staff. Family connection and evacuation insurance address psychological and safety needs that pure salary can't buy.",
         "choice_b_text": "Maximize cash compensation - let workers buy what they need", 
         "choice_b_exp_reward": 50, "choice_b_cash_change": -8000, "choice_b_reputation_change": 2,
         "choice_b_feedback": "Cash can't buy everything in space! Individual workers can't negotiate evacuation insurance or family communication satellites. Corporate benefits have collective purchasing power.",
         "choice_c_text": "Remind them how few opportunities exist for their specialized skills", 
         "choice_c_exp_reward": 20, "choice_c_cash_change": 0, "choice_c_reputation_change": -3,
         "choice_c_feedback": "Threats breed resentment! Yes, space mining skills are specialized, but that cuts both ways - you need them too. Competitors will gladly take disgruntled experts.", 
         "subskill_focus": "Total Rewards"},

        # ========== LEVEL 6: Employee Relations & Morale ==========
        # Modern World
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Human Resources", "required_level": 6,
         "scenario_title": "L6: Employee Relations & Morale", 
         "scenario_narrative": "Staff turnover has increased and shift-swap requests are constant. Anonymous feedback suggests burnout and low morale, especially during rush hours. You need to measure and improve engagement.",
         "choice_a_text": "Conduct formal engagement survey, analyze results, implement top 3 requested changes, and follow up with staff", 
         "choice_a_exp_reward": 100, "choice_a_cash_change": 800, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Engagement excellence! Surveys measure sentiment scientifically. Acting on feedback shows you listen. Staff requested flexible scheduling, break room improvements, and recognition programs - all implemented. Turnover drops.",
         "choice_b_text": "Host a team party to boost morale", 
         "choice_b_exp_reward": 45, "choice_b_cash_change": -500, "choice_b_reputation_change": 2,
         "choice_b_feedback": "Parties are nice but don't address root causes! Staff enjoy the pizza but still face the same scheduling stress Monday morning. Engagement requires systemic changes, not just events.",
         "choice_c_text": "Tell managers to be more positive and encouraging", 
         "choice_c_exp_reward": 35, "choice_c_cash_change": 0, "choice_c_reputation_change": 1,
         "choice_c_feedback": "Surface positivity without action feels hollow. 'Great job!' rings false when real concerns go unaddressed. Listen first, then respond with genuine changes.", 
         "subskill_focus": "Engagement"},
        
        # Fantasy World
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Human Resources", "required_level": 6,
         "scenario_title": "L6: Employee Relations & Morale", 
         "scenario_narrative": "After a challenging quest resulted in a team injury, staff morale is low. Workers are anxious about dangers and question whether the risks are worth it. You need to restore confidence and engagement.",
         "choice_a_text": "Host a Guild Feast to honor the injured, review safety protocols together, and implement staff-suggested improvements", 
         "choice_a_exp_reward": 100, "choice_a_cash_change": -200, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Masterful engagement! The feast honors sacrifice while creating community. Collaborative safety review shows you take concerns seriously. Staff-suggested improvements give them ownership. Morale rebounds.",
         "choice_b_text": "Increase danger pay to compensate for the risks", 
         "choice_b_exp_reward": 50, "choice_b_cash_change": -400, "choice_b_reputation_change": 2,
         "choice_b_feedback": "Gold doesn't heal fear! Extra pay acknowledges risk but doesn't address the underlying safety concerns. Staff remain anxious even with fatter purses. Address the root issue.",
         "choice_c_text": "Replace anxious staff with adventurers who don't mind danger", 
         "choice_c_exp_reward": 30, "choice_c_cash_change": -300, "choice_c_reputation_change": -1,
         "choice_c_feedback": "Replacement isn't leadership! Loyal staff dismissed for legitimate concerns tells everyone their feelings don't matter. Adventurers may accept danger but lack your trained skills.", 
         "subskill_focus": "Engagement"},
        
        # Sci-Fi World
        {"world_type": "Sci-Fi", "industry": "Mining Corp", "discipline": "Human Resources", "required_level": 6,
         "scenario_title": "L6: Employee Relations & Morale", 
         "scenario_narrative": "Crew morale is deteriorating after 8 months of deep space operations. Psychological reports show isolation effects, interpersonal conflicts, and declining productivity. You must address engagement before the mission extends.",
         "choice_a_text": "Implement holistic engagement program: virtual reality Earth experiences, conflict mediation, rotation of duties, enhanced communication bandwidth home", 
         "choice_a_exp_reward": 100, "choice_a_cash_change": -10000, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Comprehensive engagement strategy! Space psychology requires addressing isolation, variety, and connection. VR Earth experiences combat homesickness. Mediation resolves conflicts before they escalate. Productivity and morale recover.",
         "choice_b_text": "Promise large bonuses upon mission completion", 
         "choice_b_exp_reward": 45, "choice_b_cash_change": 0, "choice_b_reputation_change": 2,
         "choice_b_feedback": "Future bonuses don't fix present misery! Crew need support now, not promises later. Someone experiencing psychological distress isn't motivated by distant rewards.",
         "choice_c_text": "Remind crew of contractual obligations and mission importance", 
         "choice_c_exp_reward": 30, "choice_c_cash_change": 0, "choice_c_reputation_change": -1,
         "choice_c_feedback": "Contractual reminders increase resentment! Crew know their obligations. What they need is support, not lectures. Psychological health requires proactive engagement, not legal threats.", 
         "subskill_focus": "Engagement"},

        # ========== LEVEL 7: Conflict Resolution ==========
        # Modern World
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Human Resources", "required_level": 7,
         "scenario_title": "L7: Conflict Resolution", 
         "scenario_narrative": "A heated dispute erupts between your production manager and quality control manager. Production accuses QC of slowing output with excessive inspections; QC accuses Production of cutting corners on food safety. Both threaten to resign.",
         "choice_a_text": "Facilitate structured mediation: hear both sides separately, identify shared goals, negotiate agreed standards with documented resolution", 
         "choice_a_exp_reward": 110, "choice_a_cash_change": 500, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Mediation mastery! Separating emotions from issues reveals both want restaurant success. Agreed inspection standards balance speed and safety. Documented resolution prevents future disputes. Both managers stay.",
         "choice_b_text": "Side with Production - speed is essential for profitability", 
         "choice_b_exp_reward": 40, "choice_b_cash_change": 300, "choice_b_reputation_change": -2,
         "choice_b_feedback": "Taking sides escalates conflict! QC manager resigns, feeling undermined. Without proper oversight, food safety incident follows. Short-term speed gain causes long-term damage.",
         "choice_c_text": "Fire both and start fresh with new managers who can get along", 
         "choice_c_exp_reward": 30, "choice_c_cash_change": -2000, "choice_c_reputation_change": -1,
         "choice_c_feedback": "Avoidance isn't resolution! You lose institutional knowledge and trained staff. New managers face the same structural tension. Fix the system, not just the people.", 
         "subskill_focus": "Mediation"},
        
        # Fantasy World
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Human Resources", "required_level": 7,
         "scenario_title": "L7: Conflict Resolution", 
         "scenario_narrative": "Your head brewer and head cook are in bitter dispute over cellar space. The brewer needs temperature-controlled storage for aging ales; the cook needs it for meat curing. Both claim seniority rights.",
         "choice_a_text": "Mediate: assess actual space needs, propose shared schedule or partitioning, have both sign formal agreement", 
         "choice_a_exp_reward": 110, "choice_a_cash_change": 200, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Wise mediation! Careful analysis shows the brewer needs constant temperature; the cook needs circulation. Different zones within the cellar serve both needs. Formal agreement prevents future conflict.",
         "choice_b_text": "Award the space to whoever has worked here longer", 
         "choice_b_exp_reward": 40, "choice_b_cash_change": 0, "choice_b_reputation_change": -1,
         "choice_b_feedback": "Seniority doesn't solve resource conflicts! The 'loser' feels unfairly treated regardless of tenure. Business needs, not arrival dates, should drive decisions.",
         "choice_c_text": "Let them fight it out between themselves", 
         "choice_c_exp_reward": 25, "choice_c_cash_change": -300, "choice_c_reputation_change": -2,
         "choice_c_feedback": "Unmediated conflicts escalate! Without intervention, the dispute spreads to their teams. Kitchen and brewery staff take sides. Service suffers as cooperation collapses.", 
         "subskill_focus": "Mediation"},
        
        # Sci-Fi World
        {"world_type": "Sci-Fi", "industry": "Mining Corp", "discipline": "Human Resources", "required_level": 7,
         "scenario_title": "L7: Conflict Resolution", 
         "scenario_narrative": "Tension explodes between the human extraction team and the Synthetic maintenance crew. Humans accuse Synthetics of prioritizing equipment over worker safety; Synthetics counter that humans damage equipment through careless operation.",
         "choice_a_text": "Conduct joint investigation, establish cross-team safety committee, create integrated protocols that address both equipment and personnel", 
         "choice_a_exp_reward": 110, "choice_a_cash_change": 0, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Cross-cultural mediation success! Investigation shows both groups have valid points. Joint committee builds understanding between species. Integrated protocols align incentives. Cooperation replaces blame.",
         "choice_b_text": "Separate the teams completely to prevent further conflict", 
         "choice_b_exp_reward": 45, "choice_b_cash_change": -5000, "choice_b_reputation_change": 1,
         "choice_b_feedback": "Separation breeds division! Teams that don't interact develop worse stereotypes. Equipment handoffs become tense. The underlying conflict remains unresolved, just hidden.",
         "choice_c_text": "Mandate that Synthetics defer to human judgment on all safety matters", 
         "choice_c_exp_reward": 30, "choice_c_cash_change": -2000, "choice_c_reputation_change": -2,
         "choice_c_feedback": "Species preference violates Galactic Employment Act! Synthetics file grievance. Equipment damage increases as their expertise is ignored. Favoritism solves nothing.", 
         "subskill_focus": "Mediation"},

        # ========== LEVEL 8: Termination & Severance ==========
        # Modern World
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Human Resources", "required_level": 8,
         "scenario_title": "L8: Termination & Severance", 
         "scenario_narrative": "After multiple documented performance issues, you must terminate a long-tenured employee who has threatened 'legal action' if fired. You need to handle this properly to minimize wrongful termination lawsuit risk.",
         "choice_a_text": "Review documentation, conduct formal exit meeting with witness, offer severance in exchange for release, provide written termination letter with appeal process", 
         "choice_a_exp_reward": 120, "choice_a_cash_change": -2000, "choice_a_reputation_change": 4,
         "choice_a_feedback": "Legally sound termination! Documentation proves cause, witness prevents he-said-she-said, severance with release protects against lawsuit, appeal process shows fairness. Clean separation protects the business.",
         "choice_b_text": "Fire them immediately before they cause more problems", 
         "choice_b_exp_reward": 40, "choice_b_cash_change": -8000, "choice_b_reputation_change": -3,
         "choice_b_feedback": "Hasty termination invites litigation! Without proper process, their lawyer argues wrongful termination. Settlement costs far exceed what proper severance would have cost.",
         "choice_c_text": "Make their job so unpleasant they quit voluntarily", 
         "choice_c_exp_reward": 25, "choice_c_cash_change": -5000, "choice_c_reputation_change": -4,
         "choice_c_feedback": "Constructive dismissal is illegal! Creating hostile conditions to force resignation is recognized by courts as wrongful termination. Lawsuit is stronger because you showed deliberate misconduct.", 
         "subskill_focus": "Separation Law"},
        
        # Fantasy World
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Human Resources", "required_level": 8,
         "scenario_title": "L8: Termination & Severance", 
         "scenario_narrative": "A senior guild member must be dismissed for stealing from the till. However, improper expulsion violates Guild law and could result in sanctions against your establishment. The employee knows powerful people.",
         "choice_a_text": "Document evidence thoroughly, notify the Guild, conduct formal hearing per Guild procedures, offer fair separation terms", 
         "choice_a_exp_reward": 120, "choice_a_cash_change": -500, "choice_a_reputation_change": 4,
         "choice_a_feedback": "Guild-compliant termination! Evidence proves theft beyond dispute. Guild procedures protect you from retaliation by their connections. Fair separation terms show you're just, not vindictive.",
         "choice_b_text": "Quietly dismiss them and avoid Guild involvement to prevent embarrassment", 
         "choice_b_exp_reward": 45, "choice_b_cash_change": -1000, "choice_b_reputation_change": -1,
         "choice_b_feedback": "Secrecy backfires! Without Guild documentation, they claim wrongful dismissal to their powerful friends. You're accused of framing a respected member. Proper procedures protect everyone.",
         "choice_c_text": "Confront them publicly to shame them into leaving", 
         "choice_c_exp_reward": 30, "choice_c_cash_change": -800, "choice_c_reputation_change": -3,
         "choice_c_feedback": "Public shaming violates dignity requirements! Even thieves have procedural rights. The Guild sanctions you for improper conduct. Handle separations privately and formally.", 
         "subskill_focus": "Separation Law"},
        
        # Sci-Fi World
        {"world_type": "Sci-Fi", "industry": "Mining Corp", "discipline": "Human Resources", "required_level": 8,
         "scenario_title": "L8: Termination & Severance", 
         "scenario_narrative": "A high-risk employee with access to proprietary extraction algorithms must be terminated for breach of conduct. They've hinted at selling information to competitors. Improper handling could compromise trade secrets.",
         "choice_a_text": "Coordinate with Legal and Security: immediate access revocation, exit interview with NDA reinforcement, competitive severance contingent on confidentiality", 
         "choice_a_exp_reward": 120, "choice_a_cash_change": -20000, "choice_a_reputation_change": 4,
         "choice_a_feedback": "High-stakes termination excellence! Access revocation prevents data theft. Competitive severance incentivizes honoring confidentiality. Legal documentation strengthens any future enforcement. Clean, professional separation.",
         "choice_b_text": "Terminate immediately and have security escort them off-station", 
         "choice_b_exp_reward": 50, "choice_b_cash_change": -5000, "choice_b_reputation_change": -1,
         "choice_b_feedback": "Aggressive termination creates enemies! Humiliated employee has every incentive to sell secrets for revenge. Without negotiated severance, they owe you nothing. Handle exits professionally.",
         "choice_c_text": "Keep them employed but reassigned until the threat passes", 
         "choice_c_exp_reward": 40, "choice_c_cash_change": -10000, "choice_c_reputation_change": 0,
         "choice_c_feedback": "Delay increases risk! Every day they remain employed, they can access more information. If conduct breach justifies termination, act decisively with proper protections.", 
         "subskill_focus": "Separation Law"},

        # ========== LEVEL 9: Succession Planning & Development ==========
        # Modern World
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Human Resources", "required_level": 9,
         "scenario_title": "L9: Succession Planning & Development", 
         "scenario_narrative": "Your executive chef is retiring in 18 months. Without a succession plan, you'll face a leadership vacuum. You need to identify high-potential employees and create development pathways to prepare them for leadership.",
         "choice_a_text": "Identify 2-3 high-potential candidates, create individualized development plans, rotate them through leadership experiences, have chef mentor the top candidate", 
         "choice_a_exp_reward": 130, "choice_a_cash_change": 0, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Talent pipeline established! Multiple candidates ensure backup options. Individualized development addresses each person's gaps. Leadership rotation builds practical skills. Mentorship transfers institutional knowledge. Smooth transition assured.",
         "choice_b_text": "Assume the sous chef will naturally step up when the time comes", 
         "choice_b_exp_reward": 45, "choice_b_cash_change": 0, "choice_b_reputation_change": 1,
         "choice_b_feedback": "Assumptions aren't planning! The sous chef may not want leadership or may lack key skills. What if they leave before transition? Succession requires deliberate development, not hope.",
         "choice_c_text": "Start external recruitment now to find the best replacement", 
         "choice_c_exp_reward": 55, "choice_c_cash_change": -3000, "choice_c_reputation_change": 2,
         "choice_c_feedback": "External hires have downsides! They don't know your systems, culture, or recipes. Internal candidates who were passed over may resign. External search PLUS internal development is ideal.", 
         "subskill_focus": "Talent Pipeline"},
        
        # Fantasy World
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Human Resources", "required_level": 9,
         "scenario_title": "L9: Succession Planning & Development", 
         "scenario_narrative": "Your Guild Master approaches retirement. Guild tradition requires a trained successor, but your journeymen lack leadership experience. You must design a management training program to prepare future leaders.",
         "choice_a_text": "Create structured apprenticeship to mastery pathway: rotating guild responsibilities, mentorship pairs, leadership challenges, formal certification", 
         "choice_a_exp_reward": 130, "choice_a_cash_change": -500, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Guild-worthy succession planning! Rotating responsibilities exposes apprentices to all aspects of leadership. Mentorship transfers wisdom. Leadership challenges test decision-making under pressure. Multiple prepared successors.",
         "choice_b_text": "Simply promote the most senior journeyman when the time comes", 
         "choice_b_exp_reward": 40, "choice_b_cash_change": 0, "choice_b_reputation_change": 0,
         "choice_b_feedback": "Seniority doesn't guarantee leadership ability! The most senior may be excellent at craft but terrible at management. Develop leaders deliberately, don't assume experience equals capability.",
         "choice_c_text": "Request the Guild send a trained Master from another tavern", 
         "choice_c_exp_reward": 50, "choice_c_cash_change": -300, "choice_c_reputation_change": 1,
         "choice_c_feedback": "Outside Masters don't know your traditions! Every tavern has unique recipes and customs. External placement also demoralizes your journeymen who see no advancement path.", 
         "subskill_focus": "Talent Pipeline"},
        
        # Sci-Fi World
        {"world_type": "Sci-Fi", "industry": "Mining Corp", "discipline": "Human Resources", "required_level": 9,
         "scenario_title": "L9: Succession Planning & Development", 
         "scenario_narrative": "Your Station Commander is being promoted to corporate. The role requires rare expertise combining technical knowledge, crisis management, and diplomatic skills. You have 12 months to develop a successor from your officer corps.",
         "choice_a_text": "Implement leadership accelerator: cross-functional rotations, crisis simulation training, diplomatic missions, executive coaching, board shadowing", 
         "choice_a_exp_reward": 130, "choice_a_cash_change": -15000, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Executive development excellence! Accelerated program compresses years of learning into months. Crisis simulations build confidence without real risk. Board shadowing provides strategic perspective. Ready successor identified.",
         "choice_b_text": "Let officers compete for the role through normal performance reviews", 
         "choice_b_exp_reward": 45, "choice_b_cash_change": 0, "choice_b_reputation_change": 1,
         "choice_b_feedback": "Reviews measure past performance, not future potential! Commander role requires skills not tested in current positions. Without targeted development, even top performers may lack key capabilities.",
         "choice_c_text": "Recruit an experienced commander from a competitor", 
         "choice_c_exp_reward": 55, "choice_c_cash_change": -30000, "choice_c_reputation_change": 1,
         "choice_c_feedback": "External recruitment is expensive and risky! Competitor commanders bring different cultures. Your officers may resent being passed over. Internal development plus external benchmarking is better.", 
         "subskill_focus": "Talent Pipeline"},

        # ========== LEVEL 10: Organizational Structure & Labor Relations ==========
        # Modern World
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Human Resources", "required_level": 10,
         "scenario_title": "L10: Organizational Structure & Labor Relations", 
         "scenario_narrative": "The Kitchen Workers Union is demanding wage increases and better scheduling practices. A strike would shut down your restaurant during peak season. You must negotiate a complex labor agreement that satisfies workers while maintaining profitability.",
         "choice_a_text": "Engage in good-faith negotiation: review their demands objectively, propose counter-offers with data, find creative solutions like profit-sharing, reach documented agreement", 
         "choice_a_exp_reward": 150, "choice_a_cash_change": -2000, "choice_a_reputation_change": 6,
         "choice_a_feedback": "Labor relations mastery! Good-faith bargaining builds long-term trust. Data-based proposals are harder to reject. Creative solutions like profit-sharing align interests. Documented agreement provides stability for years.",
         "choice_b_text": "Refuse all demands and prepare to replace striking workers", 
         "choice_b_exp_reward": 50, "choice_b_cash_change": -20000, "choice_b_reputation_change": -5,
         "choice_b_feedback": "Hardball backfires! Strike shuts you down during peak season. Replacement workers lack training. Community supports strikers. Legal costs mount. You eventually settle for worse terms than initial demands.",
         "choice_c_text": "Accept all union demands immediately to avoid conflict", 
         "choice_c_exp_reward": 60, "choice_c_cash_change": -15000, "choice_c_reputation_change": 3,
         "choice_c_feedback": "Total capitulation isn't sustainable! Accepting unrealistic demands strains finances. Next negotiation, union expects same easy victory. Negotiate fairly - both sides should feel they achieved something.", 
         "subskill_focus": "Union Negotiation"},
        
        # Fantasy World
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Human Resources", "required_level": 10,
         "scenario_title": "L10: Organizational Structure & Labor Relations", 
         "scenario_narrative": "The Local Craftsmen's Guild is demanding collective bargaining terms that would standardize wages and working conditions across all taverns. Resistance could mean work stoppages; acceptance means less flexibility.",
         "choice_a_text": "Negotiate collaboratively: acknowledge legitimate concerns, propose tiered standards based on establishment size, agree to joint oversight committee, sign binding compact", 
         "choice_a_exp_reward": 150, "choice_a_cash_change": -1000, "choice_a_reputation_change": 6,
         "choice_a_feedback": "Guild relations mastery! Tiered standards recognize that small taverns can't match large inn wages. Joint oversight builds trust. Binding compact provides predictability. Your leadership role in negotiations raises reputation.",
         "choice_b_text": "Organize other tavern owners to reject Guild demands collectively", 
         "choice_b_exp_reward": 50, "choice_b_cash_change": -5000, "choice_b_reputation_change": -4,
         "choice_b_feedback": "Owner coalition triggers worker coalition! Full Guild work stoppage affects all food service. Kingdom officials intervene, imposing terms worse than negotiated settlement would have been.",
         "choice_c_text": "Secretly hire non-Guild workers to reduce dependence", 
         "choice_c_exp_reward": 40, "choice_c_cash_change": -2000, "choice_c_reputation_change": -5,
         "choice_c_feedback": "Guild discovers your betrayal! All Guild workers walk out. Non-Guild replacements lack training. Your tavern is blacklisted. Underhanded tactics destroy reputation for years.", 
         "subskill_focus": "Union Negotiation"},
        
        # Sci-Fi World
        {"world_type": "Sci-Fi", "industry": "Mining Corp", "discipline": "Human Resources", "required_level": 10,
         "scenario_title": "L10: Organizational Structure & Labor Relations", 
         "scenario_narrative": "The Autonomous Drone Workers Collective (representing Synthetic workers) and the Human Crew Union are both demanding representation in operational decisions. Their interests sometimes conflict, and you must structure an organization that gives voice to both.",
         "choice_a_text": "Design dual-representation structure: joint labor council with equal voice, binding arbitration for conflicts, transparent decision processes, documented charter", 
         "choice_a_exp_reward": 150, "choice_a_cash_change": -8000, "choice_a_reputation_change": 6,
         "choice_a_feedback": "Organizational design excellence! Equal representation prevents species hierarchy. Binding arbitration resolves conflicts before they escalate. Transparent processes build trust. Your station becomes a model for interspecies labor relations.",
         "choice_b_text": "Favor human workers since they're the majority of the workforce", 
         "choice_b_exp_reward": 50, "choice_b_cash_change": 0, "choice_b_reputation_change": -4,
         "choice_b_feedback": "Species discrimination! Synthetics file Galactic Employment Board complaint. Even if humans outnumber Synthetics, minority rights must be protected. Heavy fines and mandated restructuring.",
         "choice_c_text": "Keep labor groups separate and negotiate with each independently", 
         "choice_c_exp_reward": 65, "choice_c_cash_change": -3000, "choice_c_reputation_change": 1,
         "choice_c_feedback": "Divide-and-conquer breeds resentment! Groups eventually realize you're playing them against each other. United front forms. Joint representation was inevitable - better to structure it yourself.", 
         "subskill_focus": "Union Negotiation"},
    ]
    
    for scenario in scenarios:
        cur.execute("""
            INSERT INTO scenario_master (world_type, industry, discipline, required_level, scenario_title, scenario_narrative,
                choice_a_text, choice_a_exp_reward, choice_a_cash_change, choice_a_reputation_change, choice_a_feedback,
                choice_b_text, choice_b_exp_reward, choice_b_cash_change, choice_b_reputation_change, choice_b_feedback,
                choice_c_text, choice_c_exp_reward, choice_c_cash_change, choice_c_reputation_change, choice_c_feedback,
                subskill_focus)
            VALUES (%(world_type)s, %(industry)s, %(discipline)s, %(required_level)s, %(scenario_title)s, %(scenario_narrative)s,
                %(choice_a_text)s, %(choice_a_exp_reward)s, %(choice_a_cash_change)s, %(choice_a_reputation_change)s, %(choice_a_feedback)s,
                %(choice_b_text)s, %(choice_b_exp_reward)s, %(choice_b_cash_change)s, %(choice_b_reputation_change)s, %(choice_b_feedback)s,
                %(choice_c_text)s, %(choice_c_exp_reward)s, %(choice_c_cash_change)s, %(choice_c_reputation_change)s, %(choice_c_feedback)s,
                %(subskill_focus)s)
        """, scenario)
    
    conn.commit()
    print(f"Seeded {len(scenarios)} HR Curriculum scenarios (Levels 1-10, 3 worlds)!")
    cur.close()
    conn.close()


def seed_strategy_curriculum():
    """Seed the complete 10-level Strategy Curriculum across 3 worlds (30 scenarios total).
    
    This is the CAPSTONE discipline synthesizing Marketing, Accounting, Finance, Legal, and HR.
    
    Curriculum Structure:
    - L1-L3: Fundamentals & Vision (Mission/Vision, Competitive Advantage, PESTLE)
    - L4-L6: Internal Analysis & Formulation (VRIO, Porter's Generic, Balanced Scorecard)
    - L7-L8: Market Expansion & Defense (Ansoff Matrix, Porter's Five Forces)
    - L9-L10: Organizational Design & Mastery (Org Structure, Strategic Resource Allocation)
    """
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM scenario_master WHERE discipline = 'Strategy' AND scenario_title LIKE 'L%:%'")
    result = cur.fetchone()
    if result['count'] >= 30:
        print("Strategy curriculum already seeded.")
        cur.close()
        conn.close()
        return
    
    scenarios = [
        # ========== LEVEL 1: Mission and Vision ==========
        # Modern World
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Strategy", "required_level": 1,
         "scenario_title": "L1: Mission and Vision", 
         "scenario_narrative": "Your restaurant has grown from a single location to three, but your team seems confused about the company's direction. Investors and new employees ask 'What does this company stand for?' You need to articulate a clear Mission (current purpose) and Vision (long-term goal).",
         "choice_a_text": "Draft comprehensive statements: Vision - 'Become the region's most beloved farm-to-table dining destination' / Mission - 'Serve fresh, locally-sourced meals that connect community with cuisine'", 
         "choice_a_exp_reward": 50, "choice_a_cash_change": 0, "choice_a_reputation_change": 4,
         "choice_a_feedback": "Strategic clarity achieved! A clear Vision gives everyone a North Star to aim for. The Mission explains HOW you'll get there daily. Employees now understand why local sourcing matters - it's core to identity, not just a marketing gimmick.",
         "choice_b_text": "Keep it simple: 'Make money and serve good food'", 
         "choice_b_exp_reward": 20, "choice_b_cash_change": 0, "choice_b_reputation_change": 0,
         "choice_b_feedback": "Too generic! Every restaurant wants to make money and serve good food. A Mission must differentiate - what makes YOUR approach unique? Without specificity, it provides no strategic guidance.",
         "choice_c_text": "Focus only on financial targets - 'Achieve $5M revenue by 2027'", 
         "choice_c_exp_reward": 30, "choice_c_cash_change": 0, "choice_c_reputation_change": 1,
         "choice_c_feedback": "Financial goals are important but aren't Mission statements! Mission answers WHY you exist, not just WHAT you want to achieve. Revenue targets belong in strategic plans, not foundational identity.", 
         "subskill_focus": "Defining Purpose"},
        
        # Fantasy World
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Strategy", "required_level": 1,
         "scenario_title": "L1: Mission and Vision", 
         "scenario_narrative": "The Guild Council asks you to submit your establishment's Charter of Purpose. This document will guide all future decisions and define your tavern's identity within the Guild registry for generations.",
         "choice_a_text": "Craft a meaningful charter: Vision - 'Become the realm's legendary gathering place where heroes find fellowship' / Mission - 'Provide finest ales, warmest hearth, and safe haven to all who seek adventure'", 
         "choice_a_exp_reward": 50, "choice_a_cash_change": 0, "choice_a_reputation_change": 4,
         "choice_a_feedback": "A charter worthy of the Guild archives! Your Vision inspires - legendary status is aspirational. Your Mission is actionable - ales, warmth, and haven are daily deliverables. New staff understand their higher purpose.",
         "choice_b_text": "Write: 'Sell drinks, make gold'", 
         "choice_b_exp_reward": 20, "choice_b_cash_change": 0, "choice_b_reputation_change": -1,
         "choice_b_feedback": "The Guild rejects this charter as beneath their standards! Any merchant can sell drinks. A charter must capture what makes your establishment special. Revision required.",
         "choice_c_text": "Copy another successful tavern's charter with minor changes", 
         "choice_c_exp_reward": 25, "choice_c_cash_change": 0, "choice_c_reputation_change": 0,
         "choice_c_feedback": "Borrowed identity is no identity! The Guild notices the similarities. Your charter should reflect YOUR unique strengths and aspirations, not imitate others.", 
         "subskill_focus": "Defining Purpose"},
        
        # Sci-Fi World
        {"world_type": "Sci-Fi", "industry": "Mining Corp", "discipline": "Strategy", "required_level": 1,
         "scenario_title": "L1: Mission and Vision", 
         "scenario_narrative": "The Galactic Commerce Board requires all corporations to file a Statement of Purpose explaining their contribution to interstellar society. This document will be publicly available and shapes stakeholder expectations.",
         "choice_a_text": "File comprehensive statement: Vision - 'Pioneer sustainable resource extraction that enables humanity's expansion to the stars' / Mission - 'Responsibly harvest rare minerals while protecting crew welfare and cosmic environments'", 
         "choice_a_exp_reward": 50, "choice_a_cash_change": 0, "choice_a_reputation_change": 4,
         "choice_a_feedback": "The Board commends your statement! Your Vision connects mining to humanity's greater purpose. Your Mission balances profit (resource extraction) with responsibility (welfare, environment). Investors appreciate the long-term thinking.",
         "choice_b_text": "File: 'Extract maximum resources at minimum cost for shareholder value'", 
         "choice_b_exp_reward": 25, "choice_b_cash_change": 500, "choice_b_reputation_change": -2,
         "choice_b_feedback": "Functionally accurate but reputationally damaging! The public sees a corporation that cares only about profit. Talent chooses competitors with more inspiring missions. Short-term focus, long-term cost.",
         "choice_c_text": "Hire consultants to craft something that sounds good without commitment", 
         "choice_c_exp_reward": 30, "choice_c_cash_change": -1000, "choice_c_reputation_change": 1,
         "choice_c_feedback": "Empty words are eventually exposed! Consultant-speak sounds impressive but means nothing actionable. When actions don't match the statement, stakeholders lose trust. Authenticity beats eloquence.", 
         "subskill_focus": "Defining Purpose"},

        # ========== LEVEL 2: Competitive Advantage ==========
        # Modern World
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Strategy", "required_level": 2,
         "scenario_title": "L2: Competitive Advantage", 
         "scenario_narrative": "Three new restaurants opened nearby, creating intense competition. You must identify what your restaurant does better than rivals. The choice: compete on lowest prices (Cost Leadership) or compete on unique quality (Differentiation).",
         "choice_a_text": "Pursue Differentiation: Focus on unique fusion cuisine, premium ingredients, and exceptional dining experience that commands higher prices", 
         "choice_a_exp_reward": 60, "choice_a_cash_change": 500, "choice_a_reputation_change": 4,
         "choice_a_feedback": "Differentiation strategy chosen! You can't be the cheapest AND the best - pick one. By focusing on unique quality, customers pay premium for experiences they can't get elsewhere. Competitors can't easily copy your chef's creativity.",
         "choice_b_text": "Pursue Cost Leadership: Streamline operations, buy in bulk, offer the lowest prices in the area", 
         "choice_b_exp_reward": 55, "choice_b_cash_change": 800, "choice_b_reputation_change": 2,
         "choice_b_feedback": "Cost Leadership strategy chosen! Valid approach, but requires ruthless efficiency. You must have the LOWEST costs to sustain lowest prices. If competitors match prices, you'll need even better operations to survive.",
         "choice_c_text": "Try both: Offer cheap prices AND premium quality", 
         "choice_c_exp_reward": 25, "choice_c_cash_change": -500, "choice_c_reputation_change": -1,
         "choice_c_feedback": "Stuck in the middle! Premium ingredients at cheap prices means losing money on every plate. Customers get confused - are you fast food or fine dining? Pick a lane and commit.", 
         "subskill_focus": "Competitive Positioning"},
        
        # Fantasy World
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Strategy", "required_level": 2,
         "scenario_title": "L2: Competitive Advantage", 
         "scenario_narrative": "New taverns and inns flood the district. The Guild Assessor asks: 'What makes YOUR establishment worth visiting?' You must define your competitive advantage - the best enchanted ales (Differentiation) or the cheapest drinks (Cost Leadership).",
         "choice_a_text": "Differentiation: Invest in master-crafted enchanted beverages, rare ingredients, and legendary atmosphere that no competitor can replicate", 
         "choice_a_exp_reward": 60, "choice_a_cash_change": 300, "choice_a_reputation_change": 4,
         "choice_a_feedback": "Differentiation mastery! Your Dragon Fire Ale and phoenix-feather decor create experiences money alone can't buy. Wealthy adventurers pay premium prices. Competitors would need decades to match your reputation.",
         "choice_b_text": "Cost Leadership: Efficient brewing, simple fare, the lowest prices for working-class patrons", 
         "choice_b_exp_reward": 55, "choice_b_cash_change": 400, "choice_b_reputation_change": 2,
         "choice_b_feedback": "Cost Leadership engaged! You serve the masses with honest, affordable refreshment. Volume compensates for lower margins. Just ensure your costs stay below competitors - or they'll undercut you.",
         "choice_c_text": "Serve premium products at budget prices to attract everyone", 
         "choice_c_exp_reward": 25, "choice_c_cash_change": -400, "choice_c_reputation_change": 0,
         "choice_c_feedback": "Economically impossible! Rare enchanted ingredients at tavern prices means you're subsidizing every customer. Either raise prices to match quality, or lower quality to match prices.", 
         "subskill_focus": "Competitive Positioning"},
        
        # Sci-Fi World
        {"world_type": "Sci-Fi", "industry": "Mining Corp", "discipline": "Strategy", "required_level": 2,
         "scenario_title": "L2: Competitive Advantage", 
         "scenario_narrative": "Dozens of mining corps compete for contracts. The Galactic Mining Authority asks what distinguishes your operation. Will you be the lowest-cost extractor (Cost Leadership) or the specialist in rare exotic materials (Differentiation)?",
         "choice_a_text": "Differentiation: Specialize in extracting ultra-rare isotopes requiring custom equipment and expert crews that competitors can't match", 
         "choice_a_exp_reward": 60, "choice_a_cash_change": 2000, "choice_a_reputation_change": 4,
         "choice_a_feedback": "Niche differentiation! Rare isotopes command massive premiums. Your specialized equipment and trained crews create barriers to entry. Competitors can't easily replicate your expertise.",
         "choice_b_text": "Cost Leadership: Maximum automation, minimal crew, lowest extraction cost per ton for commodity minerals", 
         "choice_b_exp_reward": 55, "choice_b_cash_change": 3000, "choice_b_reputation_change": 2,
         "choice_b_feedback": "Scale efficiency! Commodity minerals have thin margins but enormous volume. Your automated operations achieve costs 20% below competitors. Win on price when quality is standardized.",
         "choice_c_text": "Offer specialty extraction at commodity prices to dominate both markets", 
         "choice_c_exp_reward": 25, "choice_c_cash_change": -5000, "choice_c_reputation_change": 0,
         "choice_c_feedback": "Impossible economics! Specialty equipment costs don't scale down to commodity prices. You're losing money on every rare extraction contract. Strategic clarity requires choosing your battlefield.", 
         "subskill_focus": "Competitive Positioning"},

        # ========== LEVEL 3: Environmental Scanning (PESTLE) ==========
        # Modern World
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Strategy", "required_level": 3,
         "scenario_title": "L3: Environmental Scanning (PESTLE)", 
         "scenario_narrative": "Before expanding to a second city, you must analyze the external environment using PESTLE: Political, Economic, Social, Technological, Legal, Environmental factors. Recent news mentions new health regulations (L), rising inflation (E), and changing food trends (S).",
         "choice_a_text": "Conduct full PESTLE analysis: Map how each factor (Political, Economic, Social, Technological, Legal, Environmental) affects your expansion plans before committing", 
         "choice_a_exp_reward": 70, "choice_a_cash_change": 0, "choice_a_reputation_change": 4,
         "choice_a_feedback": "Strategic foresight! Your PESTLE analysis reveals: new health regs (L) require kitchen upgrades; inflation (E) increases ingredient costs; plant-based trend (S) opens opportunity. Now you can plan accordingly rather than react surprised.",
         "choice_b_text": "Focus only on local competitors - that's the real threat", 
         "choice_b_exp_reward": 35, "choice_b_cash_change": 0, "choice_b_reputation_change": 1,
         "choice_b_feedback": "Competitor analysis is important but incomplete! You missed that new environmental regulations (E) ban your preferred packaging. PESTLE captures macro forces beyond direct competition.",
         "choice_c_text": "Expand quickly before overanalyzing - speed is advantage", 
         "choice_c_exp_reward": 30, "choice_c_cash_change": -2000, "choice_c_reputation_change": -1,
         "choice_c_feedback": "Speed without foresight is reckless! You opened during a recession (E) with regulatory changes (L) you didn't anticipate. Losses exceed what analysis would have cost.", 
         "subskill_focus": "External Analysis"},
        
        # Fantasy World
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Strategy", "required_level": 3,
         "scenario_title": "L3: Environmental Scanning (PESTLE)", 
         "scenario_narrative": "Before opening a tavern in a new kingdom, you consult the Guild's Strategic Council. They advise using the ancient PESTLE wisdom: Political (kingdom stability), Economic (trade routes), Social (local customs), Technological (magical innovations), Legal (guild laws), Environmental (harvest conditions).",
         "choice_a_text": "Commission comprehensive realm analysis: Political tensions with neighboring kingdoms, economic toll road changes, social attitudes toward outsiders, available enchantments, local guild regulations, crop forecasts", 
         "choice_a_exp_reward": 70, "choice_a_cash_change": -200, "choice_a_reputation_change": 4,
         "choice_a_feedback": "Strategic wisdom! Analysis reveals: Political tensions (P) mean soldier customers; toll changes (E) affect supplier costs; locals distrust outsiders (S) requiring community integration; new preservation enchantments (T) available. Informed expansion succeeds.",
         "choice_b_text": "Ask a local merchant if the area seems profitable", 
         "choice_b_exp_reward": 35, "choice_b_cash_change": 0, "choice_b_reputation_change": 1,
         "choice_b_feedback": "Single perspective is limited! The merchant doesn't know upcoming Legal changes banning certain brews. PESTLE examines ALL external factors systematically.",
         "choice_c_text": "Trust intuition - you've succeeded before without analysis", 
         "choice_c_exp_reward": 25, "choice_c_cash_change": -500, "choice_c_reputation_change": -1,
         "choice_c_feedback": "Past success doesn't predict new environments! Different kingdoms have different forces. Your intuition missed an upcoming harvest failure (E) that spikes ingredient costs. Analysis prevents surprises.", 
         "subskill_focus": "External Analysis"},
        
        # Sci-Fi World
        {"world_type": "Sci-Fi", "industry": "Mining Corp", "discipline": "Strategy", "required_level": 3,
         "scenario_title": "L3: Environmental Scanning (PESTLE)", 
         "scenario_narrative": "Before establishing operations in a new star system, your Strategic Intelligence division recommends PESTLE analysis: Political (system governance), Economic (mineral prices), Social (colony attitudes), Technological (extraction advances), Legal (Galactic regulations), Environmental (asteroid stability).",
         "choice_a_text": "Deploy full intelligence gathering: Political faction analysis, commodity price forecasts, colony labor attitudes, emerging extraction tech, new Galactic Mining Act provisions, geological surveys", 
         "choice_a_exp_reward": 70, "choice_a_cash_change": -5000, "choice_a_reputation_change": 4,
         "choice_a_feedback": "Strategic intelligence mastery! Analysis reveals: Political instability (P) poses security risks; price forecasts (E) show declining returns; colony opposes corporate mining (S) requiring local partnerships; new extraction tech (T) could halve costs. Plan adjusted for success.",
         "choice_b_text": "Check mineral surveys - if there's ore, we can mine it", 
         "choice_b_exp_reward": 35, "choice_b_cash_change": 0, "choice_b_reputation_change": 1,
         "choice_b_feedback": "Technical feasibility isn't strategic viability! Yes, ore exists, but new Legal restrictions (L) limit extraction rates. Political unrest (P) requires expensive security. PESTLE sees the whole picture.",
         "choice_c_text": "Competitors are moving in - we must act before analysis is complete", 
         "choice_c_exp_reward": 30, "choice_c_cash_change": -10000, "choice_c_reputation_change": -1,
         "choice_c_feedback": "Speed without intelligence is costly! Competitors who analyzed first knew about upcoming Environmental regulations (E) requiring expensive containment. They waited strategically while you committed prematurely.", 
         "subskill_focus": "External Analysis"},

        # ========== LEVEL 4: Resource Analysis (VRIO) ==========
        # Modern World
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Strategy", "required_level": 4,
         "scenario_title": "L4: Resource Analysis (VRIO)", 
         "scenario_narrative": "An investor asks what makes your restaurant defensible long-term. You need to analyze your resources using VRIO: Is each resource Valuable, Rare, hard to Imitate, and is your Organization set up to exploit it? Your chef's recipes, location, and brand all need evaluation.",
         "choice_a_text": "Conduct VRIO assessment: Chef's secret recipes (V-yes, R-yes, I-hard, O-yes = sustainable advantage), Location (V-yes, R-no = temporary), Brand (V-yes, R-developing, I-medium, O-building)", 
         "choice_a_exp_reward": 80, "choice_a_cash_change": 0, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Resource-based strategy! VRIO reveals your true competitive moat. The chef's recipes are your sustainable advantage - valuable, rare, hard to copy, and you're organized to leverage them. Protect this asset; invest in brand-building as secondary advantage.",
         "choice_b_text": "List all resources as equally important competitive advantages", 
         "choice_b_exp_reward": 35, "choice_b_cash_change": 0, "choice_b_reputation_change": 1,
         "choice_b_feedback": "Not all resources are equal! Your tables are valuable but not rare - anyone can buy tables. VRIO distinguishes temporary advantages from sustainable ones. Focus resources on what competitors CAN'T easily copy.",
         "choice_c_text": "Tell investor competitive advantage comes from hard work and determination", 
         "choice_c_exp_reward": 25, "choice_c_cash_change": 0, "choice_c_reputation_change": 0,
         "choice_c_feedback": "Platitudes don't satisfy investors! Everyone works hard. VRIO identifies SPECIFIC, DEFENSIBLE resources that create sustained above-average returns. Strategy requires analytical precision.", 
         "subskill_focus": "Internal Strength"},
        
        # Fantasy World
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Strategy", "required_level": 4,
         "scenario_title": "L4: Resource Analysis (VRIO)", 
         "scenario_narrative": "The Guild Master asks what resources make your tavern truly special. You must evaluate using the ancient VRIO framework: Valuable, Rare, Inimitable, Organized. Your enchanted brewing equipment, legendary recipes, and trained staff all warrant examination.",
         "choice_a_text": "Analyze each resource: Enchanted brewing vats (V-yes, R-yes, I-very hard, O-yes = sustainable advantage), Recipes passed down 5 generations (V-yes, R-yes, I-impossible to copy, O-yes = core advantage)", 
         "choice_a_exp_reward": 80, "choice_a_cash_change": 0, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Resource mastery! Your enchanted vats ARE rare - custom-forged by a now-deceased master. Your ancestral recipes are truly inimitable - they literally cannot be replicated. These are your defensive moats. Protect them absolutely.",
         "choice_b_text": "Our competitive advantage is excellent customer service", 
         "choice_b_exp_reward": 40, "choice_b_cash_change": 0, "choice_b_reputation_change": 2,
         "choice_b_feedback": "Service is valuable but easily imitated! Competitors can train staff to be friendly too. VRIO asks what can't be copied. Your unique enchanted equipment passes that test; generic 'service' doesn't.",
         "choice_c_text": "We don't need frameworks - we just know we're the best", 
         "choice_c_exp_reward": 25, "choice_c_cash_change": -200, "choice_c_reputation_change": 0,
         "choice_c_feedback": "Confidence without analysis is arrogance! The Guild has seen many 'best' taverns fail when competitors copied their non-protected advantages. VRIO identifies what truly cannot be replicated.", 
         "subskill_focus": "Internal Strength"},
        
        # Sci-Fi World
        {"world_type": "Sci-Fi", "industry": "Mining Corp", "discipline": "Strategy", "required_level": 4,
         "scenario_title": "L4: Resource Analysis (VRIO)", 
         "scenario_narrative": "The board demands a Resource Audit to identify sustainable competitive advantages. Using VRIO framework: Is your proprietary extraction algorithm, specialized fleet, and experienced crew Valuable, Rare, hard to Imitate, and properly Organized?",
         "choice_a_text": "Present rigorous VRIO analysis: Proprietary algorithm (V-yes, R-yes, I-patented, O-yes = core advantage), Fleet (V-yes, R-no = parity), Crew expertise (V-yes, R-somewhat, I-takes years, O-developing)", 
         "choice_a_exp_reward": 80, "choice_a_cash_change": 0, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Strategic resource clarity! Your algorithm is the crown jewel - valuable, rare, legally protected, and fully exploited. The fleet provides no advantage (competitors have similar ships). Crew expertise is developing but not yet a moat. Focus investment accordingly.",
         "choice_b_text": "Our advantage is having the best technology in the sector", 
         "choice_b_exp_reward": 40, "choice_b_cash_change": 0, "choice_b_reputation_change": 1,
         "choice_b_feedback": "Which technology specifically? 'Best technology' is vague. VRIO demands precision. Your extraction algorithm is truly rare; your ships are standard models. Know exactly where your advantage lies.",
         "choice_c_text": "Competitive advantage is overrated - just execute better than rivals", 
         "choice_c_exp_reward": 25, "choice_c_cash_change": 0, "choice_c_reputation_change": 0,
         "choice_c_feedback": "Execution matters but isn't strategy! If competitors can copy everything you do, 'better execution' becomes an exhausting arms race. VRIO identifies resources that provide lasting advantage regardless of execution.", 
         "subskill_focus": "Internal Strength"},

        # ========== LEVEL 5: Business Strategy (Porter's Generic) ==========
        # Modern World
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Strategy", "required_level": 5,
         "scenario_title": "L5: Business Strategy (Porter's Generic)", 
         "scenario_narrative": "A strategic consultant reviews your positioning and warns you're 'stuck in the middle' - not the cheapest option (Cost Leadership), not clearly premium (Differentiation), and not focused on a specific niche (Focus). Porter's Generic Strategies demand a clear choice.",
         "choice_a_text": "Commit fully to Differentiation: Elevate to premium positioning with unique chef creations, upscale ambiance, and premium pricing that clearly separates us from competitors", 
         "choice_a_exp_reward": 90, "choice_a_cash_change": 1000, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Strategic clarity achieved! Differentiation means customers choose you for unique value, not price. Your focus on chef creativity and ambiance creates experiences competitors can't match. Premium pricing reflects premium value.",
         "choice_b_text": "Pursue Cost Leadership: Strip away extras, maximize efficiency, become the value leader in the neighborhood", 
         "choice_b_exp_reward": 85, "choice_b_cash_change": 1500, "choice_b_reputation_change": 3,
         "choice_b_feedback": "Cost Leadership commitment! Valid strategy if you can truly achieve lowest costs. This means ruthless efficiency, standardized processes, and volume-based purchasing. Compete on price only if you have cost advantage.",
         "choice_c_text": "Stay flexible - sometimes compete on price, sometimes on quality, depending on the situation", 
         "choice_c_exp_reward": 35, "choice_c_cash_change": -500, "choice_c_reputation_change": -1,
         "choice_c_feedback": "This IS being stuck in the middle! Customers don't know what you stand for. Price-shoppers find cheaper options; quality-seekers find more prestigious ones. Porter proved: strategic ambiguity underperforms clear positioning.", 
         "subskill_focus": "Competitive Stance"},
        
        # Fantasy World
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Strategy", "required_level": 5,
         "scenario_title": "L5: Business Strategy (Porter's Generic)", 
         "scenario_narrative": "The Grand Strategist of the Guild warns your tavern lacks clear positioning. Are you the cheapest drinks in town (Cost Leadership), the most prestigious establishment (Differentiation), or specialized for a specific clientele (Focus)? 'All things to all people' fails.",
         "choice_a_text": "Declare Differentiation Focus: Become THE destination for adventurers seeking legendary brews, rare lore, and quest connections - premium pricing for premium experiences", 
         "choice_a_exp_reward": 90, "choice_a_cash_change": 500, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Focused Differentiation mastery! By targeting adventurers specifically with unique offerings they can't find elsewhere, you become irreplaceable to that segment. They'll travel across kingdoms for your legendary Dragon Fire Ale.",
         "choice_b_text": "Pursue Cost Leadership: Simple ales, efficient service, the working person's tavern with unbeatable prices", 
         "choice_b_exp_reward": 85, "choice_b_cash_change": 700, "choice_b_reputation_change": 3,
         "choice_b_feedback": "Cost Leadership commitment! Serve the masses with honest value. This requires operational efficiency - large batches, minimal waste, standardized recipes. Volume compensates for thinner margins.",
         "choice_c_text": "Adapt our positioning based on who walks through the door that day", 
         "choice_c_exp_reward": 30, "choice_c_cash_change": -300, "choice_c_reputation_change": -1,
         "choice_c_feedback": "Strategic confusion! Adventurers seeking legendary experiences find peasant prices suspicious. Workers seeking affordable drinks resent premium markups. Without consistent positioning, no one knows what to expect.", 
         "subskill_focus": "Competitive Stance"},
        
        # Sci-Fi World
        {"world_type": "Sci-Fi", "industry": "Mining Corp", "discipline": "Strategy", "required_level": 5,
         "scenario_title": "L5: Business Strategy (Porter's Generic)", 
         "scenario_narrative": "The Strategic Planning Committee demands you clarify your market position. Are you the lowest-cost extractor (Cost Leadership), the specialist in complex rare-mineral extraction (Differentiation), or focused on a specific sector like medical-grade isotopes (Focus)?",
         "choice_a_text": "Commit to Focused Differentiation: Specialize exclusively in ultra-rare medical-grade isotopes, becoming the premium provider for pharmaceutical and biotech clients who demand absolute purity", 
         "choice_a_exp_reward": 90, "choice_a_cash_change": 5000, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Focused Differentiation excellence! Medical-grade clients pay massive premiums for certified purity. Your specialized equipment, trained crews, and quality certifications create barriers competitors would need years to overcome.",
         "choice_b_text": "Pursue broad Cost Leadership: Maximize automation across all mineral types, achieve lowest cost-per-ton in the sector", 
         "choice_b_exp_reward": 85, "choice_b_cash_change": 8000, "choice_b_reputation_change": 3,
         "choice_b_feedback": "Scale efficiency! Broad Cost Leadership means being the sector's low-cost producer across commodity minerals. Heavy automation, optimal routes, minimal crew. When quality is standardized, lowest cost wins contracts.",
         "choice_c_text": "Remain flexible - bid on whatever contracts seem profitable at the moment", 
         "choice_c_exp_reward": 35, "choice_c_cash_change": -3000, "choice_c_reputation_change": -1,
         "choice_c_feedback": "Opportunistic bidding isn't strategy! Without clear positioning, you lack advantages in any segment. Specialists beat you on quality; cost leaders beat you on price. The middle is where profits die.", 
         "subskill_focus": "Competitive Stance"},

        # ========== LEVEL 6: Strategic Goal Setting (Balanced Scorecard) ==========
        # Modern World
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Strategy", "required_level": 6,
         "scenario_title": "L6: Strategic Goal Setting", 
         "scenario_narrative": "Annual planning begins. Last year focused only on revenue, but the Balanced Scorecard framework demands four perspectives: Financial (profits), Customer (satisfaction), Internal Process (efficiency), Learning & Growth (employee development). What KPIs will you set?",
         "choice_a_text": "Develop balanced KPIs: Financial (15% profit growth), Customer (4.5+ Yelp rating, 40% repeat visits), Internal Process (table turnover time, food waste %), Learning & Growth (chef certifications, cross-training hours)", 
         "choice_a_exp_reward": 100, "choice_a_cash_change": 0, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Balanced Scorecard mastery! Financial results are lagging indicators - they tell you what already happened. Customer, Process, and Learning metrics are leading indicators - they predict future financial success. Your balanced approach drives sustainable performance.",
         "choice_b_text": "Focus on financial metrics only - revenue, profit margin, and cash flow are what matter", 
         "choice_b_exp_reward": 50, "choice_b_cash_change": 500, "choice_b_reputation_change": 1,
         "choice_b_feedback": "Financial focus misses root causes! By the time you see declining revenue, customer satisfaction and internal processes already deteriorated. Balanced Scorecard catches problems before they hit the bottom line.",
         "choice_c_text": "Set vague goals like 'improve customer experience' without specific metrics", 
         "choice_c_exp_reward": 30, "choice_c_cash_change": 0, "choice_c_reputation_change": 0,
         "choice_c_feedback": "Unmeasurable goals are meaningless! 'Improve customer experience' - by how much? Compared to what baseline? KPIs must be specific and measurable to drive action and accountability.", 
         "subskill_focus": "Balanced Scorecard"},
        
        # Fantasy World
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Strategy", "required_level": 6,
         "scenario_title": "L6: Strategic Goal Setting", 
         "scenario_narrative": "The Guild requires annual goal registration using the Four Pillars framework: Treasury (gold), Patrons (customer loyalty), Craft (internal quality), Growth (apprentice development). You must set balanced targets across all four.",
         "choice_a_text": "Register balanced goals: Treasury (increase reserves 20%), Patrons (5+ Guild rating, track repeat visitors), Craft (legendary artifacts forged, waste reduction), Growth (apprentice completion rate, master certifications)", 
         "choice_a_exp_reward": 100, "choice_a_cash_change": 0, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Four Pillars excellence! The Guild commends your balanced approach. Strong Treasury comes FROM satisfied Patrons, efficient Craft, and skilled staff. By tracking all four, you identify problems before they drain your gold.",
         "choice_b_text": "Focus on Treasury alone - gold is the ultimate measure of success", 
         "choice_b_exp_reward": 50, "choice_b_cash_change": 300, "choice_b_reputation_change": 1,
         "choice_b_feedback": "Gold worship blinds you to its sources! When gold declines, you won't know if it's Patron dissatisfaction, Craft problems, or untrained staff. Balanced goals reveal root causes.",
         "choice_c_text": "Set inspiring but unmeasurable goals like 'become legendary'", 
         "choice_c_exp_reward": 30, "choice_c_cash_change": 0, "choice_c_reputation_change": 0,
         "choice_c_feedback": "The Guild rejects vague aspirations! 'Become legendary' - what does that mean specifically? How will you know when achieved? Goals must be measurable to be meaningful.", 
         "subskill_focus": "Balanced Scorecard"},
        
        # Sci-Fi World
        {"world_type": "Sci-Fi", "industry": "Mining Corp", "discipline": "Strategy", "required_level": 6,
         "scenario_title": "L6: Strategic Goal Setting", 
         "scenario_narrative": "The Strategic Planning System requires Balanced Scorecard KPIs across four dimensions: Financial (returns), Customer (client satisfaction), Internal Process (operational efficiency), Innovation & Growth (technology development). What metrics will you track?",
         "choice_a_text": "Program balanced metrics: Financial (ROI, margin), Customer (delivery reliability, quality scores), Internal Process (extraction efficiency, safety incidents), Innovation (R&D spend, patents filed, training hours)", 
         "choice_a_exp_reward": 100, "choice_a_cash_change": 0, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Balanced performance management! Financial metrics tell you how you DID. Customer, Process, and Innovation metrics predict how you WILL DO. Safety incidents predict future lawsuits; R&D predicts future competitive position. Lead and lag indicators together.",
         "choice_b_text": "Prioritize financial metrics - shareholder returns are the ultimate scorecard", 
         "choice_b_exp_reward": 50, "choice_b_cash_change": 2000, "choice_b_reputation_change": 1,
         "choice_b_feedback": "Short-term focus! This quarter's returns look great, but declining innovation investment and safety shortcuts will destroy future value. Balanced Scorecard forces long-term thinking.",
         "choice_c_text": "Track everything possible - data is power", 
         "choice_c_exp_reward": 35, "choice_c_cash_change": -1000, "choice_c_reputation_change": 0,
         "choice_c_feedback": "Data overload paralyzes decision-making! Hundreds of metrics mean nothing gets focus. Balanced Scorecard selects KEY performance indicators - the vital few that truly drive strategic success.", 
         "subskill_focus": "Balanced Scorecard"},

        # ========== LEVEL 7: Growth Strategy (Ansoff Matrix) ==========
        # Modern World
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Strategy", "required_level": 7,
         "scenario_title": "L7: Growth Strategy (Ansoff Matrix)", 
         "scenario_narrative": "Your restaurant is profitable but growth has stalled. The Ansoff Matrix presents four growth paths: Market Penetration (more sales to current customers), Market Development (new locations), Product Development (new menu items), or Diversification (new products for new markets). Which path?",
         "choice_a_text": "Start with Market Penetration (lowest risk): Increase visit frequency through loyalty programs and expanded hours before attempting riskier strategies", 
         "choice_a_exp_reward": 110, "choice_a_cash_change": 800, "choice_a_reputation_change": 4,
         "choice_a_feedback": "Strategic growth sequencing! Ansoff shows penetration is lowest-risk because you know both your product AND your customers. Extract maximum value from current position before taking risks. Loyalty programs increase average visits from 2 to 3 per month - significant growth without new investment.",
         "choice_b_text": "Pursue Diversification immediately: Open a completely different business (food truck, catering, meal kits) in new markets", 
         "choice_b_exp_reward": 60, "choice_b_cash_change": -2000, "choice_b_reputation_change": 2,
         "choice_b_feedback": "Diversification is highest risk! New products for new markets means you're learning everything from scratch. Ansoff suggests exhausting lower-risk options first. Why diversify when penetration opportunities remain?",
         "choice_c_text": "Pursue all four strategies simultaneously to maximize growth", 
         "choice_c_exp_reward": 40, "choice_c_cash_change": -3000, "choice_c_reputation_change": 0,
         "choice_c_feedback": "Resource dispersion kills execution! Each strategy requires focused investment. Doing four at once means doing none well. Ansoff helps CHOOSE - sequence strategies based on risk tolerance and resources.", 
         "subskill_focus": "Growth Planning"},
        
        # Fantasy World
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Strategy", "required_level": 7,
         "scenario_title": "L7: Growth Strategy (Ansoff Matrix)", 
         "scenario_narrative": "Your tavern's gold reserves are growing but the Guild challenges you to expand influence. The Four Paths of Growth: More sales to current patrons (Penetration), new territories (Market Development), new offerings (Product Development), or entirely new ventures (Diversification). Which path calls to you?",
         "choice_a_text": "Begin with Penetration: Maximize current tavern before expansion - loyalty rewards, exclusive memberships, extended hours to serve current patrons more frequently", 
         "choice_a_exp_reward": 110, "choice_a_cash_change": 400, "choice_a_reputation_change": 4,
         "choice_a_feedback": "Wisdom in sequence! You already know your patrons and your ales. Extracting more value from this known territory is safest. Guild Members who visited monthly now visit weekly with the new membership program. Growth without gambling.",
         "choice_b_text": "Diversify immediately: Open an adventuring supply shop attached to the tavern", 
         "choice_b_exp_reward": 60, "choice_b_cash_change": -800, "choice_b_reputation_change": 2,
         "choice_b_feedback": "New product for new market is maximum risk! You know tavern-keeping, not equipment supply. The shop struggles while taking focus from your core business. Exhaust lower-risk paths first.",
         "choice_c_text": "Pursue all growth paths simultaneously to grow as fast as possible", 
         "choice_c_exp_reward": 40, "choice_c_cash_change": -1000, "choice_c_reputation_change": 0,
         "choice_c_feedback": "Scattered resources achieve scattered results! Each path requires dedicated gold and attention. The Four Paths are OPTIONS to sequence, not simultaneous mandates.", 
         "subskill_focus": "Growth Planning"},
        
        # Sci-Fi World
        {"world_type": "Sci-Fi", "industry": "Mining Corp", "discipline": "Strategy", "required_level": 7,
         "scenario_title": "L7: Growth Strategy (Ansoff Matrix)", 
         "scenario_narrative": "Shareholder pressure demands growth plans. The Ansoff Matrix offers four vectors: Penetration (more extraction from current asteroids), Market Development (new star systems), Product Development (new mineral processing), Diversification (new industries). Strategic choice required.",
         "choice_a_text": "Prioritize Market Penetration: Optimize current asteroid yields with improved technology and extended mining schedules before expanding to new systems", 
         "choice_a_exp_reward": 110, "choice_a_cash_change": 5000, "choice_a_reputation_change": 4,
         "choice_a_feedback": "Capital-efficient growth! New technology increases yield from known asteroids by 30% - growth without the risk and cost of new system exploration. Ansoff prioritizes low-risk growth until opportunities exhaust.",
         "choice_b_text": "Pursue Diversification: Enter refining and manufacturing - move up the value chain entirely", 
         "choice_b_exp_reward": 60, "choice_b_cash_change": -20000, "choice_b_reputation_change": 2,
         "choice_b_feedback": "Highest risk, highest capital requirement! New industry, new customers, new competitors. Diversification makes sense AFTER exhausting lower-risk options. Why gamble when penetration opportunities remain?",
         "choice_c_text": "Spread investment across all four growth vectors for portfolio diversification", 
         "choice_c_exp_reward": 45, "choice_c_cash_change": -8000, "choice_c_reputation_change": 0,
         "choice_c_feedback": "Strategic diversification isn't the same as scattered investment! Ansoff helps you CHOOSE and SEQUENCE, not spread thin. Focus resources on the most attractive risk-adjusted opportunity.", 
         "subskill_focus": "Growth Planning"},

        # ========== LEVEL 8: Industry Analysis (Porter's Five Forces) ==========
        # Modern World
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Strategy", "required_level": 8,
         "scenario_title": "L8: Industry Analysis (Porter's Five Forces)", 
         "scenario_narrative": "Before major investment, you must analyze industry profit potential using Porter's Five Forces: Buyer Power, Supplier Power, Threat of Substitutes, Threat of New Entrants, and Competitive Rivalry. A consultant presents concerning findings about delivery app power (Buyers) and food supplier consolidation (Suppliers).",
         "choice_a_text": "Conduct full Five Forces analysis and develop strategies to counter each threat: Reduce delivery app dependence, diversify suppliers, strengthen barriers to entry, differentiate from substitutes", 
         "choice_a_exp_reward": 120, "choice_a_cash_change": 500, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Industry structure mastery! Your analysis reveals: delivery apps extract 30% commissions (high Buyer power) - counter with direct ordering incentives. Two suppliers control 80% of produce (high Supplier power) - develop local farm relationships. Understanding these forces lets you shape them.",
         "choice_b_text": "Focus only on direct competitors - they're the real threat", 
         "choice_b_exp_reward": 50, "choice_b_cash_change": 0, "choice_b_reputation_change": 2,
         "choice_b_feedback": "Rivalry is just ONE of five forces! You beat competitors but delivery apps still take 30% of revenue. Supplier consolidation raises your costs. Porter teaches that profitability depends on ALL five forces, not just direct competition.",
         "choice_c_text": "Industry analysis is academic - just focus on running a great restaurant", 
         "choice_c_exp_reward": 35, "choice_c_cash_change": -1000, "choice_c_reputation_change": 0,
         "choice_c_feedback": "Great restaurants can fail in bad industries! If suppliers have power, they take your margins. If substitutes are attractive, customers leave. Porter's Five Forces explains why some industries are structurally more profitable than others.", 
         "subskill_focus": "Industry Structure"},
        
        # Fantasy World
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Strategy", "required_level": 8,
         "scenario_title": "L8: Industry Analysis (Porter's Five Forces)", 
         "scenario_narrative": "The Grand Strategist teaches the Five Forces that shape any trade: Power of Patrons (Buyers), Power of Suppliers, Threat of Magical Alternatives (Substitutes), Threat of New Taverns (Entrants), and Rivalry among existing establishments. She warns of troubling trends.",
         "choice_a_text": "Analyze all Five Forces: Counter Patron power with unique offerings, diversify from the Brewers Guild monopoly (Supplier power), defend against wild magic beverages (Substitutes), build reputation barriers against new entrants", 
         "choice_a_exp_reward": 120, "choice_a_cash_change": 300, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Strategic force mastery! The Brewers Guild's monopoly (Supplier power) was extracting excessive margins - your new partnership with independent brewers breaks their hold. Understanding forces lets you reshape them to your advantage.",
         "choice_b_text": "Focus on defeating rival taverns - they're the clear enemy", 
         "choice_b_exp_reward": 50, "choice_b_cash_change": 0, "choice_b_reputation_change": 2,
         "choice_b_feedback": "Rivalry is visible but not always dominant! You crush rivals but wild magic potions (Substitutes) steal your younger patrons. The Royal Court's exclusive tax power (Buyer power) squeezes margins. See all five forces.",
         "choice_c_text": "These forces are beyond our control - just brew good ale", 
         "choice_c_exp_reward": 35, "choice_c_cash_change": -500, "choice_c_reputation_change": 0,
         "choice_c_feedback": "Forces can be shaped! Good ale matters, but if the Brewers Guild controls all ingredients, they capture the value of your good ale. The Five Forces aren't destiny - they're strategic targets to influence.", 
         "subskill_focus": "Industry Structure"},
        
        # Sci-Fi World
        {"world_type": "Sci-Fi", "industry": "Mining Corp", "discipline": "Strategy", "required_level": 8,
         "scenario_title": "L8: Industry Analysis (Porter's Five Forces)", 
         "scenario_narrative": "The Strategic Intelligence division presents Porter's Five Forces analysis of the mining sector: Buyer Power (major corps dictate prices), Supplier Power (Interstellar Bank controls financing), Threat of Substitutes (nanobots, asteroid reclamation), Threat of Entrants (low barriers), and intense Rivalry.",
         "choice_a_text": "Address each force strategically: Lock in long-term buyer contracts, secure alternative financing sources, differentiate from nanobot extraction, build scale barriers, find non-rival niches", 
         "choice_a_exp_reward": 120, "choice_a_cash_change": 2000, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Industry structure optimization! The Interstellar Bank's financing monopoly (Supplier power) was your biggest vulnerability - you secured alternative credit sources, reducing their leverage. Each force addressed improves structural profitability.",
         "choice_b_text": "Focus on beating rival mining corps - outcompete them and the rest follows", 
         "choice_b_exp_reward": 50, "choice_b_cash_change": 0, "choice_b_reputation_change": 2,
         "choice_b_feedback": "You win market share but profitability declines! Why? The Interstellar Bank (Supplier power) raised financing costs for the whole sector. Nanobot technology (Substitutes) made traditional extraction less valuable. All five forces matter.",
         "choice_c_text": "If industry forces are unfavorable, exit to a better industry", 
         "choice_c_exp_reward": 60, "choice_c_cash_change": -5000, "choice_c_reputation_change": 1,
         "choice_c_feedback": "Exit is an option, but forces can be reshaped! Your specialized position in rare isotopes faces different forces than commodity mining. Five Forces analysis identifies WHERE in the industry to compete, not just whether to compete.", 
         "subskill_focus": "Industry Structure"},

        # ========== LEVEL 9: Organizational Structure ==========
        # Modern World
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Strategy", "required_level": 9,
         "scenario_title": "L9: Organizational Structure", 
         "scenario_narrative": "Your restaurant group has grown to six locations, but the original functional structure (all chefs report to head chef, all servers to floor manager) is causing coordination problems. You're considering Divisional (each location self-contained) or Matrix (functional AND location reporting) structures.",
         "choice_a_text": "Restructure to Divisional: Each location becomes a self-contained unit with its own chef, manager, and P&L responsibility, with corporate providing shared services and standards", 
         "choice_a_exp_reward": 130, "choice_a_cash_change": 0, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Structure follows strategy! Divisional design empowers each location to adapt to local markets while maintaining brand standards. General Managers own results. Corporate focuses on strategy, not micromanagement. Accountability is clear.",
         "choice_b_text": "Maintain Functional structure: Central control ensures consistency across all locations", 
         "choice_b_exp_reward": 60, "choice_b_cash_change": -1000, "choice_b_reputation_change": 2,
         "choice_b_feedback": "Functional structure doesn't scale! With six locations, the head chef can't effectively oversee all kitchens. Decisions bottleneck at the top. What worked at one location creates chaos at six.",
         "choice_c_text": "Implement Matrix: Staff report to both functional heads and location managers", 
         "choice_c_exp_reward": 70, "choice_c_cash_change": -500, "choice_c_reputation_change": 3,
         "choice_c_feedback": "Matrix creates complexity! Chefs with two bosses face conflicting priorities. Matrix works for project-based organizations, but restaurants need clear operational authority. Divisional is cleaner for your situation.", 
         "subskill_focus": "Adaptive Design"},
        
        # Fantasy World
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Strategy", "required_level": 9,
         "scenario_title": "L9: Organizational Structure", 
         "scenario_narrative": "Your tavern empire spans three kingdoms. The original Guild structure (all brewers under Master Brewer, all servers under Hospitality Guild) creates conflicts between Guild loyalties and location needs. The Grand Council offers alternative structures.",
         "choice_a_text": "Adopt Regional Baronies (Divisional): Each kingdom's taverns become a self-governing barony with local Guildmasters, while the central House maintains standards and shared knowledge", 
         "choice_a_exp_reward": 130, "choice_a_cash_change": 0, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Wise restructuring! Each Barony can adapt to local customs, laws, and tastes while the central House ensures quality standards and knowledge sharing. Regional Barons own results and can respond quickly to local conditions.",
         "choice_b_text": "Strengthen central Guild control: All masters report directly to you regardless of location", 
         "choice_b_exp_reward": 55, "choice_b_cash_change": -400, "choice_b_reputation_change": 1,
         "choice_b_feedback": "Centralized control breaks at distance! Decisions for the distant eastern kingdom take weeks. Local opportunities pass while awaiting approval. Structure must match scale.",
         "choice_c_text": "Create Dual Loyalty (Matrix): Staff serve both their Guild and their location equally", 
         "choice_c_exp_reward": 65, "choice_c_cash_change": -200, "choice_c_reputation_change": 2,
         "choice_c_feedback": "Two masters create confusion! When the Brewers Guild demands recipe standardization but the local Barony needs adaptation, who wins? Clean authority lines outperform elegant but complex matrices.", 
         "subskill_focus": "Adaptive Design"},
        
        # Sci-Fi World
        {"world_type": "Sci-Fi", "industry": "Mining Corp", "discipline": "Strategy", "required_level": 9,
         "scenario_title": "L9: Organizational Structure", 
         "scenario_narrative": "Your corporation operates across twelve star systems, but the original Functional structure (Engineering division, Operations division, Sales division) causes coordination failures. Product decisions require alignment across all functions, slowing response time.",
         "choice_a_text": "Restructure to Product-Based Divisions: Create separate divisions for Commodity Minerals, Rare Isotopes, and Specialty Extraction - each with integrated engineering, operations, and sales", 
         "choice_a_exp_reward": 130, "choice_a_cash_change": -10000, "choice_a_reputation_change": 5,
         "choice_a_feedback": "Organizational alignment achieved! Each division now has the resources to move quickly on product-specific opportunities. Rare Isotopes division can invest in specialized equipment without Commodity Minerals budget politics. Structure matches strategy.",
         "choice_b_text": "Maintain Functional structure: Specialized expertise in each function is our competitive advantage", 
         "choice_b_exp_reward": 60, "choice_b_cash_change": -5000, "choice_b_reputation_change": 2,
         "choice_b_feedback": "Functional silos create handoff problems! Engineers optimize for technical elegance; Sales promises features Operations can't deliver. Cross-functional coordination meetings multiply. At your scale, functional structure creates more friction than expertise.",
         "choice_c_text": "Implement Matrix: Everyone reports to both Function and Product leaders", 
         "choice_c_exp_reward": 75, "choice_c_cash_change": -3000, "choice_c_reputation_change": 3,
         "choice_c_feedback": "Matrix can work but adds complexity. Your situation (clearly distinct product lines with different success factors) favors cleaner divisional structure. Matrix fits when products share so much capability that divisions would duplicate.", 
         "subskill_focus": "Adaptive Design"},

        # ========== LEVEL 10: Strategic Resource Allocation ==========
        # Modern World
        {"world_type": "Modern", "industry": "Restaurant", "discipline": "Strategy", "required_level": 10,
         "scenario_title": "L10: Strategic Resource Allocation", 
         "scenario_narrative": "As CEO, you must allocate the company's $500,000 annual surplus. Options: invest in R&D (test kitchen for new concepts), pursue M&A (acquire a competitor), or expand internal capacity (renovate existing locations). Each path has different risk/return profiles and strategic implications.",
         "choice_a_text": "Balanced allocation based on strategic priorities: 40% R&D for future concepts ($200K), 35% capacity expansion for proven locations ($175K), 25% M&A reserve for opportunistic acquisitions ($125K)", 
         "choice_a_exp_reward": 150, "choice_a_cash_change": 2000, "choice_a_reputation_change": 6,
         "choice_a_feedback": "Strategic capital deployment mastery! Your allocation reflects strategic thinking: R&D builds future advantages, capacity expansion harvests current success, M&A reserve enables opportunistic moves. The board commends your balanced, long-term perspective that doesn't sacrifice today for tomorrow or vice versa.",
         "choice_b_text": "All-in on M&A: Acquire the struggling competitor while they're weak", 
         "choice_b_exp_reward": 80, "choice_b_cash_change": 5000, "choice_b_reputation_change": 3,
         "choice_b_feedback": "High concentration risk! Acquisition succeeds but integration consumes all management attention. R&D stalls, existing locations deteriorate. Strategic resource allocation means balanced investment across time horizons.",
         "choice_c_text": "Return surplus to shareholders - let them decide where to invest", 
         "choice_c_exp_reward": 60, "choice_c_cash_change": 0, "choice_c_reputation_change": 2,
         "choice_c_feedback": "Abdication of strategic responsibility! As CEO, you have information shareholders lack about strategic opportunities. Returning capital signals you see no good internal investments - often untrue for growth companies.", 
         "subskill_focus": "Capital Deployment"},
        
        # Fantasy World
        {"world_type": "Fantasy", "industry": "Tavern", "discipline": "Strategy", "required_level": 10,
         "scenario_title": "L10: Strategic Resource Allocation", 
         "scenario_narrative": "The Grand Treasury holds 10,000 gold pieces in surplus. The Council demands your allocation decision: Invest in the Alchemical Research Guild (new brews for the future), acquire the failing Dragon's Rest tavern (M&A), or renovate the Great Hall (capacity expansion). Each choice shapes the empire's future.",
         "choice_a_text": "Strategic allocation across time horizons: 4,000 gold to Alchemical Research (future), 3,500 gold to Great Hall renovation (present), 2,500 gold reserved for opportunistic acquisitions", 
         "choice_a_exp_reward": 150, "choice_a_cash_change": 1000, "choice_a_reputation_change": 6,
         "choice_a_feedback": "Resource allocation wisdom! The Council celebrates your balanced vision. Alchemical research secures future advantages; renovation harvests current success; the acquisition reserve enables swift action when opportunities arise. All time horizons are served.",
         "choice_b_text": "Acquire Dragon's Rest immediately - they're desperate and it's a bargain", 
         "choice_b_exp_reward": 80, "choice_b_cash_change": 2000, "choice_b_reputation_change": 3,
         "choice_b_feedback": "Opportunistic but unbalanced! Dragon's Rest revives but your research stalls. Competitors develop new brews while you manage an integration. Strategic allocation balances present opportunities with future preparation.",
         "choice_c_text": "Distribute the gold to Guild Members as bonus - they earned it", 
         "choice_c_exp_reward": 55, "choice_c_cash_change": 0, "choice_c_reputation_change": 3,
         "choice_c_feedback": "Popular but strategically weak! Guild Members celebrate, but the empire builds no future advantage. Leaders must balance immediate rewards with long-term investment. Where will next decade's growth come from?", 
         "subskill_focus": "Capital Deployment"},
        
        # Sci-Fi World
        {"world_type": "Sci-Fi", "industry": "Mining Corp", "discipline": "Strategy", "required_level": 10,
         "scenario_title": "L10: Strategic Resource Allocation", 
         "scenario_narrative": "The board expects your capital allocation decision. The $50 million surplus could fund: R&D for quantum extraction technology (30% of profits for risky future tech), M&A to acquire a struggling competitor, or capacity expansion at proven asteroids. Shareholders demand justification.",
         "choice_a_text": "Present strategic allocation framework: 35% R&D for quantum extraction ($17.5M), 40% capacity expansion ($20M), 25% M&A opportunistic reserve ($12.5M), with clear metrics and stage gates for each", 
         "choice_a_exp_reward": 150, "choice_a_cash_change": 10000, "choice_a_reputation_change": 6,
         "choice_a_feedback": "Capital allocation excellence! Your presentation demonstrates mastery: R&D addresses technological disruption, capacity expansion harvests proven assets, M&A reserve enables strategic opportunism. Clear metrics ensure accountability. The board unanimously approves - this is what strategic leadership looks like.",
         "choice_b_text": "Commit 100% to quantum extraction R&D - technology is the future", 
         "choice_b_exp_reward": 70, "choice_b_cash_change": -5000, "choice_b_reputation_change": 2,
         "choice_b_feedback": "Bold but unbalanced! Quantum research may take 10 years. Meanwhile, current operations starve for capital while competitors expand. Strategic allocation serves multiple time horizons simultaneously.",
         "choice_c_text": "Maximize shareholder dividends - return 80% of surplus", 
         "choice_c_exp_reward": 55, "choice_c_cash_change": 0, "choice_c_reputation_change": 1,
         "choice_c_feedback": "Short-term shareholder appeasement! Dividends boost this quarter's stock price but signal no growth vision. Institutional investors question long-term trajectory. CEOs allocate capital; they don't just return it.", 
         "subskill_focus": "Capital Deployment"},
    ]
    
    for scenario in scenarios:
        cur.execute("""
            INSERT INTO scenario_master (world_type, industry, discipline, required_level, scenario_title, scenario_narrative,
                choice_a_text, choice_a_exp_reward, choice_a_cash_change, choice_a_reputation_change, choice_a_feedback,
                choice_b_text, choice_b_exp_reward, choice_b_cash_change, choice_b_reputation_change, choice_b_feedback,
                choice_c_text, choice_c_exp_reward, choice_c_cash_change, choice_c_reputation_change, choice_c_feedback,
                subskill_focus)
            VALUES (%(world_type)s, %(industry)s, %(discipline)s, %(required_level)s, %(scenario_title)s, %(scenario_narrative)s,
                %(choice_a_text)s, %(choice_a_exp_reward)s, %(choice_a_cash_change)s, %(choice_a_reputation_change)s, %(choice_a_feedback)s,
                %(choice_b_text)s, %(choice_b_exp_reward)s, %(choice_b_cash_change)s, %(choice_b_reputation_change)s, %(choice_b_feedback)s,
                %(choice_c_text)s, %(choice_c_exp_reward)s, %(choice_c_cash_change)s, %(choice_c_reputation_change)s, %(choice_c_feedback)s,
                %(subskill_focus)s)
        """, scenario)
    
    conn.commit()
    print(f"Seeded {len(scenarios)} Strategy Curriculum scenarios (Levels 1-10, 3 worlds)!")
    cur.close()
    conn.close()


def seed_daily_login_rewards():
    """Seed daily login rewards (7-day cycle)."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM daily_login_rewards")
    result = cur.fetchone()
    if result['count'] > 0:
        print("Daily login rewards already seeded.")
        cur.close()
        conn.close()
        return
    
    rewards = [
        (1, 'gold', 100, 'Day 1: 100 Gold'),
        (2, 'energy', 25, 'Day 2: 25 Energy'),
        (3, 'gold', 200, 'Day 3: 200 Gold'),
        (4, 'exp', 500, 'Day 4: 500 EXP Boost'),
        (5, 'gold', 300, 'Day 5: 300 Gold'),
        (6, 'energy', 50, 'Day 6: 50 Energy'),
        (7, 'gold', 500, 'Day 7: 500 Gold Jackpot!'),
    ]
    
    for day, reward_type, value, desc in rewards:
        cur.execute("""
            INSERT INTO daily_login_rewards (day_number, reward_type, reward_amount, reward_description)
            VALUES (%s, %s, %s, %s)
        """, (day, reward_type, value, desc))
    
    conn.commit()
    print("Seeded 7 daily login rewards!")
    cur.close()
    conn.close()


def seed_advisors():
    """Seed 12 recruitable advisors with unique bonuses."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM advisors")
    result = cur.fetchone()
    if result['count'] > 0:
        print("Advisors already seeded.")
        cur.close()
        conn.close()
        return
    
    advisors = [
        ('advisor_marketing_1', 'Maya Sterling', 'Brand Consultant', 'Former CMO who built iconic brands.', 'Marketing', 'exp_boost', 10, 'common', 500),
        ('advisor_marketing_2', 'Derek Viral', 'Social Media Guru', 'Influencer turned business strategist.', 'Marketing', 'exp_boost', 20, 'rare', 2000),
        ('advisor_finance_1', 'Charles Ledger', 'Senior Accountant', 'Decades of financial expertise.', 'Finance', 'gold_boost', 10, 'common', 500),
        ('advisor_finance_2', 'Victoria Vault', 'Investment Banker', 'Wall Street veteran.', 'Finance', 'gold_boost', 25, 'epic', 5000),
        ('advisor_operations_1', 'Marcus Flow', 'Process Engineer', 'Efficiency optimization expert.', 'Operations', 'exp_boost', 10, 'common', 500),
        ('advisor_operations_2', 'Linda Logistics', 'Supply Chain Director', 'Global logistics mastermind.', 'Operations', 'exp_boost', 20, 'rare', 2000),
        ('advisor_hr_1', 'Patricia People', 'HR Manager', 'Employee engagement specialist.', 'Human Resources', 'reputation_boost', 5, 'common', 500),
        ('advisor_hr_2', 'Robert Relations', 'Chief People Officer', 'Transformed company cultures.', 'Human Resources', 'reputation_boost', 10, 'rare', 2000),
        ('advisor_legal_1', 'James Justice', 'Corporate Attorney', 'Contract law specialist.', 'Legal', 'exp_boost', 10, 'common', 500),
        ('advisor_legal_2', 'Diana Defense', 'Litigation Expert', 'Undefeated in court.', 'Legal', 'exp_boost', 20, 'rare', 2000),
        ('advisor_strategy_1', 'Alexander Vision', 'Strategy Consultant', 'McKinsey trained strategist.', 'Strategy', 'exp_boost', 15, 'rare', 2000),
        ('advisor_strategy_2', 'Sophia Empire', 'CEO Coach', 'Advisor to Fortune 500 leaders.', 'Strategy', 'exp_boost', 30, 'legendary', 10000),
    ]
    
    for code, name, title, desc, specialty, bonus_type, bonus_val, rarity, cost in advisors:
        cur.execute("""
            INSERT INTO advisors (advisor_code, advisor_name, advisor_title, advisor_description, 
                                  discipline_specialty, bonus_type, bonus_value, rarity, unlock_cost)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (code, name, title, desc, specialty, bonus_type, bonus_val, rarity, cost))
    
    conn.commit()
    print("Seeded 12 advisors!")
    cur.close()
    conn.close()


def seed_equipment():
    """Seed equipment items for Head, Body, and Accessory slots."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM equipment")
    result = cur.fetchone()
    if result['count'] > 0:
        print("Equipment already seeded.")
        cur.close()
        conn.close()
        return
    
    equipment = [
        ('head_glasses', 'Reading Glasses', 'Sharp focus for analysis.', 'Head', 'intelligence', 2, 'common', 200, 1),
        ('head_headset', 'Premium Headset', 'Stay connected in style.', 'Head', 'charisma', 3, 'common', 300, 2),
        ('head_crown', 'Golden Crown', 'Symbol of business royalty.', 'Head', 'reputation', 5, 'epic', 5000, 5),
        ('body_suit', 'Business Suit', 'Professional appearance matters.', 'Body', 'charisma', 3, 'common', 500, 1),
        ('body_armor', 'Power Armor', 'Corporate warrior attire.', 'Body', 'negotiation', 4, 'rare', 2000, 3),
        ('body_cloak', 'Executive Cloak', 'Commanding presence.', 'Body', 'reputation', 5, 'epic', 5000, 5),
        ('acc_watch', 'Luxury Watch', 'Time is money.', 'Accessory', 'luck', 2, 'common', 300, 1),
        ('acc_ring', 'Signet Ring', 'Mark of success.', 'Accessory', 'negotiation', 3, 'rare', 1500, 3),
        ('acc_briefcase', 'Diamond Briefcase', 'Ultimate status symbol.', 'Accessory', 'intelligence', 5, 'legendary', 10000, 7),
    ]
    
    for code, name, desc, slot, stat, val, rarity, price, lvl in equipment:
        cur.execute("""
            INSERT INTO equipment (equipment_code, equipment_name, equipment_description, slot_type,
                                   stat_bonus_type, stat_bonus_value, rarity, purchase_price, level_required)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (code, name, desc, slot, stat, val, rarity, price, lvl))
    
    conn.commit()
    print("Seeded 9 equipment items!")
    cur.close()
    conn.close()


def seed_daily_missions():
    """Seed daily mission templates."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM daily_missions")
    result = cur.fetchone()
    if result['count'] > 0:
        print("Daily missions already seeded.")
        cur.close()
        conn.close()
        return
    
    missions = [
        ('daily_complete_3', 'Busy Day', 'Complete 3 scenarios', 'complete_scenarios', 3, 300, 100, 10),
        ('daily_complete_5', 'Workaholic', 'Complete 5 scenarios', 'complete_scenarios', 5, 500, 200, 20),
        ('daily_earn_1000', 'Money Maker', 'Earn 1000 gold', 'earn_gold', 1000, 200, 150, 15),
        ('daily_perfect_3', 'Perfectionist', 'Get 3-star rating 3 times', 'perfect_stars', 3, 400, 250, 25),
        ('daily_login_streak', 'Dedicated', 'Maintain 7-day login streak', 'login_streak', 7, 1000, 500, 50),
        ('daily_discipline', 'Well-Rounded', 'Complete scenarios in 3 different disciplines', 'varied_disciplines', 3, 350, 175, 15),
    ]
    
    for code, name, desc, mission_type, target, exp, cash, energy in missions:
        cur.execute("""
            INSERT INTO daily_missions (mission_code, mission_name, mission_description, mission_type,
                                        target_value, exp_reward, cash_reward, energy_reward)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (code, name, desc, mission_type, target, exp, cash, energy))
    
    conn.commit()
    print("Seeded 6 daily missions!")
    cur.close()
    conn.close()


if __name__ == "__main__":
    init_database()
    seed_scenarios()
    seed_achievements()
    seed_items()
    seed_npcs()
    seed_quests()
    seed_random_events()
    seed_rivals()
    seed_milestones()
    seed_weekly_challenges()
    seed_avatar_options()
    seed_fantasy_scenarios()
    seed_industrial_scenarios()
    seed_industrial_events()
    seed_industrial_rivals()
    seed_modern_restaurant_full()
    seed_marketing_curriculum()
    seed_accounting_curriculum()
    seed_finance_curriculum()
    seed_legal_curriculum()
    seed_operations_curriculum()
    seed_hr_curriculum()
    seed_strategy_curriculum()
    seed_daily_login_rewards()
    seed_advisors()
    seed_equipment()
    seed_daily_missions()
