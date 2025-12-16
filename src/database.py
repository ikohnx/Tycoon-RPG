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
            total_cash DECIMAL(15, 2) DEFAULT 10000.00,
            business_reputation INTEGER DEFAULT 50,
            current_month INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_played TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
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


if __name__ == "__main__":
    init_database()
    seed_scenarios()
