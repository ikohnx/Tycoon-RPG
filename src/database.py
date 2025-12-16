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
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(player_id, scenario_id)
        );
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
