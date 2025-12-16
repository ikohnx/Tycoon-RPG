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
