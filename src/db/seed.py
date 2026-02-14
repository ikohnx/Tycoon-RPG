import json
from .connection import get_connection, return_connection
from .queries import get_default_chart_of_accounts


def seed_scenarios():
    """Seed the database with MVP scenarios: Modern World / Restaurant / Marketing (L1-L5)."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM scenario_master WHERE world_type = 'Modern' AND industry = 'Restaurant' AND discipline = 'Marketing'")
    result = cur.fetchone()
    if result['count'] > 0:
        print("Scenarios already seeded.")
        cur.close()
        return_connection(conn)
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
    return_connection(conn)


def seed_achievements():
    """Seed the database with initial achievements."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM achievements")
    result = cur.fetchone()
    if result['count'] > 0:
        print("Achievements already seeded.")
        cur.close()
        return_connection(conn)
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
    return_connection(conn)


def seed_items():
    """Seed the database with initial items."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM items")
    result = cur.fetchone()
    if result['count'] > 0:
        print("Items already seeded.")
        cur.close()
        return_connection(conn)
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
    return_connection(conn)


def seed_npcs():
    """Seed the database with initial NPCs."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM npcs")
    result = cur.fetchone()
    if result['count'] > 0:
        print("NPCs already seeded.")
        cur.close()
        return_connection(conn)
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
    return_connection(conn)


def seed_quests():
    """Seed the database with initial quests."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM quests")
    result = cur.fetchone()
    if result['count'] > 0:
        print("Quests already seeded.")
        cur.close()
        return_connection(conn)
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
    return_connection(conn)


def seed_random_events():
    """Seed the database with random business events."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM random_events")
    result = cur.fetchone()
    if result['count'] > 0:
        print("Random events already seeded.")
        cur.close()
        return_connection(conn)
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
    return_connection(conn)


def seed_rivals():
    """Seed the database with rival businesses."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM rivals")
    result = cur.fetchone()
    if result['count'] > 0:
        print("Rivals already seeded.")
        cur.close()
        return_connection(conn)
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
    return_connection(conn)


def seed_milestones():
    """Seed the database with business milestones."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM business_milestones")
    result = cur.fetchone()
    if result['count'] > 0:
        print("Milestones already seeded.")
        cur.close()
        return_connection(conn)
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
    return_connection(conn)


def seed_weekly_challenges():
    """Seed the database with weekly challenges."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM weekly_challenges")
    result = cur.fetchone()
    if result['count'] > 0:
        print("Weekly challenges already seeded.")
        cur.close()
        return_connection(conn)
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
    return_connection(conn)


def seed_avatar_options():
    """Seed the database with avatar customization options."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM avatar_options")
    result = cur.fetchone()
    if result['count'] > 0:
        print("Avatar options already seeded.")
        cur.close()
        return_connection(conn)
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
    return_connection(conn)


def seed_fantasy_scenarios():
    """Seed Fantasy World scenarios for tavern industry."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM scenario_master WHERE world_type = 'Fantasy'")
    result = cur.fetchone()
    if result['count'] > 0:
        print("Fantasy scenarios already seeded.")
        cur.close()
        return_connection(conn)
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
    return_connection(conn)


def seed_industrial_scenarios():
    """Seed Industrial Age scenarios for steel mill, textile factory, and railroad industries."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM scenario_master WHERE world_type = 'Industrial'")
    result = cur.fetchone()
    if result['count'] > 0:
        print("Industrial scenarios already seeded.")
        cur.close()
        return_connection(conn)
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
    return_connection(conn)


def seed_industrial_events():
    """Seed random events for Industrial Age world."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM random_events WHERE world_type = 'Industrial'")
    result = cur.fetchone()
    if result['count'] > 0:
        print("Industrial events already seeded.")
        cur.close()
        return_connection(conn)
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
    return_connection(conn)


def seed_industrial_rivals():
    """Seed rival businesses for Industrial Age world."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM rivals WHERE world_type = 'Industrial'")
    result = cur.fetchone()
    if result['count'] > 0:
        print("Industrial rivals already seeded.")
        cur.close()
        return_connection(conn)
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
    return_connection(conn)


def seed_modern_restaurant_full():
    """Seed complete scenarios for Modern/Restaurant covering all 6 disciplines."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM scenario_master WHERE world_type = 'Modern' AND industry = 'Restaurant' AND discipline = 'Finance'")
    result = cur.fetchone()
    if result['count'] > 0:
        print("Modern Restaurant full disciplines already seeded.")
        cur.close()
        return_connection(conn)
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
    return_connection(conn)


def seed_marketing_curriculum():
    """Seed the complete 10-level Marketing Curriculum for Modern/Restaurant."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM scenario_master WHERE discipline = 'Marketing' AND scenario_title LIKE '%L1:%'")
    result = cur.fetchone()
    if result['count'] > 0:
        print("Marketing curriculum already seeded.")
        cur.close()
        return_connection(conn)
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
    return_connection(conn)


def seed_accounting_curriculum():
    """Seed the complete 10-level Accounting/Finance Curriculum for Modern/Restaurant."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM scenario_master WHERE discipline = 'Finance' AND scenario_title LIKE 'L1:%'")
    result = cur.fetchone()
    if result['count'] > 0:
        print("Accounting curriculum already seeded.")
        cur.close()
        return_connection(conn)
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
    return_connection(conn)


def seed_finance_curriculum():
    """Seed the complete 10-level Strategic Finance Curriculum across all 3 worlds."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM scenario_master WHERE discipline = 'Finance' AND scenario_title LIKE '%Cash Flow Management%'")
    result = cur.fetchone()
    if result['count'] > 0:
        print("Finance curriculum already seeded.")
        cur.close()
        return_connection(conn)
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
    return_connection(conn)


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
        return_connection(conn)
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
    return_connection(conn)


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
        return_connection(conn)
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
    return_connection(conn)


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
        return_connection(conn)
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
    return_connection(conn)


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
        return_connection(conn)
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
    return_connection(conn)


def seed_daily_login_rewards():
    """Seed daily login rewards (7-day cycle)."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM daily_login_rewards")
    result = cur.fetchone()
    if result['count'] > 0:
        print("Daily login rewards already seeded.")
        cur.close()
        return_connection(conn)
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
            INSERT INTO daily_login_rewards (day_number, reward_type, reward_value, reward_description)
            VALUES (%s, %s, %s, %s)
        """, (day, reward_type, value, desc))
    
    conn.commit()
    print("Seeded 7 daily login rewards!")
    cur.close()
    return_connection(conn)


def seed_advisors():
    """Seed 12 recruitable advisors with unique bonuses."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM advisors")
    result = cur.fetchone()
    if result['count'] > 0:
        print("Advisors already seeded.")
        cur.close()
        return_connection(conn)
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
    return_connection(conn)


def seed_equipment():
    """Seed equipment items for Head, Body, and Accessory slots."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM equipment")
    result = cur.fetchone()
    if result['count'] > 0:
        print("Equipment already seeded.")
        cur.close()
        return_connection(conn)
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
    return_connection(conn)


def seed_daily_missions():
    """Seed daily mission templates."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM daily_missions")
    result = cur.fetchone()
    if result['count'] > 0:
        print("Daily missions already seeded.")
        cur.close()
        return_connection(conn)
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
    return_connection(conn)


def seed_interactive_challenges():
    """Seed interactive calculation-based challenge scenarios."""
    import json
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM scenario_master WHERE challenge_type != 'choice'")
    result = cur.fetchone()
    if result['count'] > 0:
        print("Interactive challenges already seeded.")
        cur.close()
        return_connection(conn)
        return
    
    challenges = [
        {
            'world_type': 'Modern',
            'industry': 'Restaurant',
            'discipline': 'Finance',
            'required_level': 2,
            'scenario_title': 'Monthly Budget Review',
            'scenario_narrative': 'Your restaurant manager needs you to calculate this month\'s profit. Review the financial data and determine if you\'re making money or losing it.',
            'challenge_type': 'budget_calculator',
            'challenge_config': json.dumps({
                'revenue': 45000,
                'wages': 18000,
                'rent': 5500,
                'supplies': 12000,
                'marketing': 2500
            }),
            'choice_a_exp_reward': 150,
            'choice_a_cash_change': 500,
            'choice_a_reputation_change': 5,
            'choice_a_feedback': 'Understanding profit calculation is fundamental to running any business.'
        },
        {
            'world_type': 'Modern',
            'industry': 'Restaurant',
            'discipline': 'Marketing',
            'required_level': 2,
            'scenario_title': 'Menu Pricing Strategy',
            'scenario_narrative': 'You\'re launching a new signature dish. Your chef says ingredients cost $8.50 per plate. You want to hit a 35% profit margin to cover overhead and make money.',
            'challenge_type': 'pricing_strategy',
            'challenge_config': json.dumps({
                'unit_cost': 8.50,
                'competitor_price': 16.99,
                'target_margin': 35
            }),
            'choice_a_exp_reward': 175,
            'choice_a_cash_change': 400,
            'choice_a_reputation_change': 5,
            'choice_a_feedback': 'Pricing strategy balances cost coverage, profit goals, and competitive positioning.'
        },
        {
            'world_type': 'Modern',
            'industry': 'Restaurant',
            'discipline': 'Human Resources',
            'required_level': 2,
            'scenario_title': 'Weekend Staffing Plan',
            'scenario_narrative': 'Saturday is your busiest day with an estimated 240 customers. Each server can handle 20 customers per shift. How many servers do you need to schedule?',
            'challenge_type': 'staffing_decision',
            'challenge_config': json.dumps({
                'daily_customers': 240,
                'customers_per_staff': 20,
                'hourly_wage': 15
            }),
            'choice_a_exp_reward': 140,
            'choice_a_cash_change': 300,
            'choice_a_reputation_change': 5,
            'choice_a_feedback': 'Proper staffing ensures customer satisfaction without overspending on labor.'
        },
        {
            'world_type': 'Modern',
            'industry': 'Restaurant',
            'discipline': 'Operations',
            'required_level': 3,
            'scenario_title': 'Break-Even Analysis',
            'scenario_narrative': 'Your fixed monthly costs (rent, utilities, insurance) are $15,000. Each meal sells for $25 and costs $10 to prepare. How many meals must you sell to break even?',
            'challenge_type': 'break_even',
            'challenge_config': json.dumps({
                'fixed_costs': 15000,
                'unit_price': 25,
                'unit_cost': 10
            }),
            'choice_a_exp_reward': 200,
            'choice_a_cash_change': 600,
            'choice_a_reputation_change': 8,
            'choice_a_feedback': 'Break-even analysis helps you understand the minimum sales needed to avoid losses.'
        },
        {
            'world_type': 'Modern',
            'industry': 'Restaurant',
            'discipline': 'Finance',
            'required_level': 4,
            'scenario_title': 'Quarterly Profit Analysis',
            'scenario_narrative': 'The board wants your quarterly profit report. This quarter: Revenue $125,000, Wages $45,000, Rent $16,500, Supplies $35,000, Marketing $8,500.',
            'challenge_type': 'budget_calculator',
            'challenge_config': json.dumps({
                'revenue': 125000,
                'wages': 45000,
                'rent': 16500,
                'supplies': 35000,
                'marketing': 8500
            }),
            'choice_a_exp_reward': 250,
            'choice_a_cash_change': 800,
            'choice_a_reputation_change': 10,
            'choice_a_feedback': 'Regular profit analysis helps identify trends and opportunities for improvement.'
        },
        {
            'world_type': 'Modern',
            'industry': 'Restaurant',
            'discipline': 'Marketing',
            'required_level': 4,
            'scenario_title': 'Premium Wine Pricing',
            'scenario_narrative': 'Your sommelier wants to add a premium wine. The bottle costs $22 from your supplier. Industry standard is a 70% markup for wine. What should you charge?',
            'challenge_type': 'pricing_strategy',
            'challenge_config': json.dumps({
                'unit_cost': 22.00,
                'competitor_price': 75.00,
                'target_margin': 70
            }),
            'choice_a_exp_reward': 225,
            'choice_a_cash_change': 500,
            'choice_a_reputation_change': 7,
            'choice_a_feedback': 'High-margin items like wine can significantly boost restaurant profitability.'
        },
        {
            'world_type': 'Industrial',
            'industry': 'Steel Mill',
            'discipline': 'Finance',
            'required_level': 2,
            'scenario_title': 'Mill Profit Calculation',
            'scenario_narrative': 'The accountants need your help. This month\'s figures: Steel sales $78,000, Coal and ore $28,000, Worker wages $22,000, Furnace maintenance $8,000, Transport $5,000.',
            'challenge_type': 'budget_calculator',
            'challenge_config': json.dumps({
                'revenue': 78000,
                'wages': 22000,
                'rent': 8000,
                'supplies': 28000,
                'marketing': 5000
            }),
            'choice_a_exp_reward': 160,
            'choice_a_cash_change': 450,
            'choice_a_reputation_change': 6,
            'choice_a_feedback': 'Industrial profit margins depend heavily on raw material and labor costs.'
        },
        {
            'world_type': 'Industrial',
            'industry': 'Steel Mill',
            'discipline': 'Operations',
            'required_level': 3,
            'scenario_title': 'Steel Production Break-Even',
            'scenario_narrative': 'Your mill has monthly fixed costs of $25,000. Each ton of steel sells for $500 and costs $200 in materials and labor to produce. How many tons to break even?',
            'challenge_type': 'break_even',
            'challenge_config': json.dumps({
                'fixed_costs': 25000,
                'unit_price': 500,
                'unit_cost': 200
            }),
            'choice_a_exp_reward': 210,
            'choice_a_cash_change': 550,
            'choice_a_reputation_change': 8,
            'choice_a_feedback': 'Industrial break-even analysis guides production targets and capacity planning.'
        },
        {
            'world_type': 'Fantasy',
            'industry': 'Tavern',
            'discipline': 'Finance',
            'required_level': 2,
            'scenario_title': 'Tavern Coin Counting',
            'scenario_narrative': 'The bard wants to know if the tavern is profitable. Monthly income: 5000 gold coins. Expenses: Staff 1800g, Rent 800g, Ale & Food 1500g, Entertainment 400g.',
            'challenge_type': 'budget_calculator',
            'challenge_config': json.dumps({
                'revenue': 5000,
                'wages': 1800,
                'rent': 800,
                'supplies': 1500,
                'marketing': 400
            }),
            'choice_a_exp_reward': 140,
            'choice_a_cash_change': 350,
            'choice_a_reputation_change': 5,
            'choice_a_feedback': 'Even in a fantasy realm, profit equals revenue minus all expenses!'
        },
        {
            'world_type': 'Sci-Fi',
            'industry': 'Space Station',
            'discipline': 'Operations',
            'required_level': 3,
            'scenario_title': 'Cargo Bay Break-Even',
            'scenario_narrative': 'Your station has 50,000 credits in monthly fixed costs. Each cargo container processed earns 200 credits and costs 75 credits in fuel and labor. Break-even containers?',
            'challenge_type': 'break_even',
            'challenge_config': json.dumps({
                'fixed_costs': 50000,
                'unit_price': 200,
                'unit_cost': 75
            }),
            'choice_a_exp_reward': 190,
            'choice_a_cash_change': 500,
            'choice_a_reputation_change': 7,
            'choice_a_feedback': 'Space logistics require precise break-even analysis for profitable operations.'
        }
    ]
    
    for ch in challenges:
        cur.execute("""
            INSERT INTO scenario_master 
            (world_type, industry, discipline, required_level, scenario_title, scenario_narrative,
             choice_a_text, choice_a_exp_reward, choice_a_cash_change, choice_a_reputation_change, choice_a_feedback,
             choice_b_text, choice_b_exp_reward, choice_b_cash_change, choice_b_reputation_change, choice_b_feedback,
             challenge_type, challenge_config, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE)
        """, (
            ch['world_type'], ch['industry'], ch['discipline'], ch['required_level'],
            ch['scenario_title'], ch['scenario_narrative'],
            'Calculate Answer', ch['choice_a_exp_reward'], ch['choice_a_cash_change'], 
            ch['choice_a_reputation_change'], ch['choice_a_feedback'],
            'Skip Challenge', 0, 0, 0, 'You chose to skip this challenge.',
            ch['challenge_type'], ch['challenge_config']
        ))
    
    conn.commit()
    print(f"Seeded {len(challenges)} interactive challenges!")
    cur.close()
    return_connection(conn)


def seed_advanced_challenges():
    """Seed advanced calculation-based challenges for levels 5-10."""
    import json
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM scenario_master WHERE challenge_type = 'roi_calculator'")
    result = cur.fetchone()
    if result['count'] > 0:
        print("Advanced challenges already seeded.")
        cur.close()
        return_connection(conn)
        return
    
    challenges = [
        {
            'world_type': 'Modern',
            'industry': 'Restaurant',
            'discipline': 'Finance',
            'required_level': 5,
            'scenario_title': 'Kitchen Renovation ROI',
            'scenario_narrative': 'You\'re considering a $50,000 kitchen renovation. Your consultant estimates it will increase monthly profits by $2,500. Calculate the ROI percentage for the first year.',
            'challenge_type': 'roi_calculator',
            'challenge_config': json.dumps({
                'investment': 50000,
                'monthly_gain': 2500,
                'period_months': 12
            }),
            'choice_a_exp_reward': 350,
            'choice_a_cash_change': 1000,
            'choice_a_reputation_change': 12,
            'choice_a_feedback': 'ROI = (Net Gain / Investment) x 100. In this case: (30000-50000)/50000 = -40% first year, but positive long-term!'
        },
        {
            'world_type': 'Modern',
            'industry': 'Restaurant',
            'discipline': 'Operations',
            'required_level': 6,
            'scenario_title': 'Inventory Turnover Analysis',
            'scenario_narrative': 'Your annual cost of goods sold is $180,000. Average inventory value is $15,000. Calculate your inventory turnover ratio to assess supply chain efficiency.',
            'challenge_type': 'inventory_turnover',
            'challenge_config': json.dumps({
                'cost_of_goods_sold': 180000,
                'average_inventory': 15000
            }),
            'choice_a_exp_reward': 400,
            'choice_a_cash_change': 1200,
            'choice_a_reputation_change': 15,
            'choice_a_feedback': 'Inventory Turnover = COGS / Average Inventory. Higher ratios mean faster-moving inventory and better cash flow.'
        },
        {
            'world_type': 'Modern',
            'industry': 'Restaurant',
            'discipline': 'Marketing',
            'required_level': 7,
            'scenario_title': 'Customer Lifetime Value',
            'scenario_narrative': 'Your average customer spends $45 per visit, visits 3 times per month, and stays loyal for 2 years on average. With a 30% profit margin, what\'s the Customer Lifetime Value?',
            'challenge_type': 'ltv_calculator',
            'challenge_config': json.dumps({
                'avg_purchase': 45,
                'frequency_monthly': 3,
                'retention_years': 2,
                'profit_margin': 30
            }),
            'choice_a_exp_reward': 450,
            'choice_a_cash_change': 1500,
            'choice_a_reputation_change': 18,
            'choice_a_feedback': 'CLV = (Avg Purchase × Frequency × 12 × Years) × Profit Margin. This tells you how much you can spend to acquire customers.'
        },
        {
            'world_type': 'Modern',
            'industry': 'Restaurant',
            'discipline': 'Strategy',
            'required_level': 8,
            'scenario_title': 'Expansion Investment Decision',
            'scenario_narrative': 'Two franchise opportunities: Location A costs $200,000 and projects $80,000 annual profit. Location B costs $150,000 and projects $52,500 annual profit. Which has better payback period?',
            'challenge_type': 'payback_period',
            'challenge_config': json.dumps({
                'option_a_cost': 200000,
                'option_a_annual_profit': 80000,
                'option_b_cost': 150000,
                'option_b_annual_profit': 52500
            }),
            'choice_a_exp_reward': 500,
            'choice_a_cash_change': 2000,
            'choice_a_reputation_change': 20,
            'choice_a_feedback': 'Payback Period = Initial Investment / Annual Profit. Compare both options to find the faster return on investment.'
        },
        {
            'world_type': 'Modern',
            'industry': 'Restaurant',
            'discipline': 'Finance',
            'required_level': 9,
            'scenario_title': 'Compound Growth Forecast',
            'scenario_narrative': 'Your restaurant chain has $500,000 in annual revenue growing at 15% compound annually. Project the revenue after 3 years of sustained growth.',
            'challenge_type': 'compound_growth',
            'challenge_config': json.dumps({
                'initial_value': 500000,
                'growth_rate': 15,
                'years': 3
            }),
            'choice_a_exp_reward': 600,
            'choice_a_cash_change': 2500,
            'choice_a_reputation_change': 25,
            'choice_a_feedback': 'Compound Growth: Future Value = Present Value × (1 + rate)^years. Understanding compound growth is key to long-term planning.'
        }
    ]
    
    for ch in challenges:
        cur.execute("""
            INSERT INTO scenario_master 
            (world_type, industry, discipline, required_level, scenario_title, scenario_narrative,
             choice_a_text, choice_a_exp_reward, choice_a_cash_change, choice_a_reputation_change, choice_a_feedback,
             choice_b_text, choice_b_exp_reward, choice_b_cash_change, choice_b_reputation_change, choice_b_feedback,
             challenge_type, challenge_config, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE)
        """, (
            ch['world_type'], ch['industry'], ch['discipline'], ch['required_level'],
            ch['scenario_title'], ch['scenario_narrative'],
            'Calculate Answer', ch['choice_a_exp_reward'], ch['choice_a_cash_change'], 
            ch['choice_a_reputation_change'], ch['choice_a_feedback'],
            'Skip Challenge', 0, 0, 0, 'You chose to skip this challenge.',
            ch['challenge_type'], ch['challenge_config']
        ))
    
    conn.commit()
    print(f"Seeded {len(challenges)} advanced challenges!")
    cur.close()
    return_connection(conn)



def seed_scheduling_challenges():
    """Seed scheduling challenges for teaching project management concepts."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM scheduling_challenges")
    if cur.fetchone()['count'] > 0:
        print("Scheduling challenges already seeded.")
        cur.close()
        return_connection(conn)
        return
    
    import json
    
    challenges = [
        {
            'title': 'Critical Path Basics',
            'description': 'Order these restaurant renovation tasks to find the shortest project duration.',
            'challenge_type': 'critical_path',
            'difficulty': 1,
            'world_type': 'Modern',
            'required_level': 1,
            'task_data': json.dumps({
                'tasks': [
                    {'id': 'A', 'name': 'Plan Layout', 'duration': 1, 'predecessors': []},
                    {'id': 'B', 'name': 'Order Equipment', 'duration': 2, 'predecessors': ['A']},
                    {'id': 'C', 'name': 'Paint Walls', 'duration': 1, 'predecessors': ['A']},
                    {'id': 'D', 'name': 'Install Equipment', 'duration': 2, 'predecessors': ['B', 'C']},
                    {'id': 'E', 'name': 'Final Inspection', 'duration': 1, 'predecessors': ['D']}
                ]
            }),
            'correct_answer': json.dumps({'critical_path': ['A', 'B', 'D', 'E'], 'duration': 6}),
            'exp_reward': 50,
            'time_limit_seconds': 180,
            'hint_text': 'The critical path is the longest sequence of dependent tasks.'
        },
        {
            'title': 'Resource Allocation',
            'description': 'Assign your 3 staff members to tasks without over-allocating anyone.',
            'challenge_type': 'resource_leveling',
            'difficulty': 2,
            'world_type': 'Modern',
            'required_level': 2,
            'task_data': json.dumps({
                'resources': [
                    {'id': 'R1', 'name': 'Chef', 'capacity': 40},
                    {'id': 'R2', 'name': 'Manager', 'capacity': 40},
                    {'id': 'R3', 'name': 'Assistant', 'capacity': 40}
                ],
                'tasks': [
                    {'id': 'T1', 'name': 'Menu Planning', 'hours': 20, 'week': 1, 'skills': ['chef', 'manager']},
                    {'id': 'T2', 'name': 'Vendor Negotiation', 'hours': 30, 'week': 1, 'skills': ['manager']},
                    {'id': 'T3', 'name': 'Kitchen Prep', 'hours': 25, 'week': 1, 'skills': ['chef', 'assistant']}
                ]
            }),
            'correct_answer': json.dumps({'assignments': {'T1': 'R1', 'T2': 'R2', 'T3': 'R3'}}),
            'exp_reward': 75,
            'time_limit_seconds': 240,
            'hint_text': 'Check each resource capacity vs assigned hours to avoid overload.'
        },
        {
            'title': 'Time Estimation',
            'description': 'Use the three-point estimate method to calculate expected task duration.',
            'challenge_type': 'estimation',
            'difficulty': 2,
            'world_type': 'Modern',
            'required_level': 3,
            'task_data': json.dumps({
                'optimistic': 4,
                'most_likely': 6,
                'pessimistic': 14
            }),
            'correct_answer': json.dumps({'expected': 7, 'formula': '(O + 4M + P) / 6'}),
            'exp_reward': 60,
            'time_limit_seconds': 120,
            'hint_text': 'PERT formula: Expected = (Optimistic + 4×Most Likely + Pessimistic) / 6'
        },
        {
            'title': 'Dependency Chain',
            'description': 'Identify which tasks can run in parallel vs which must be sequential.',
            'challenge_type': 'dependencies',
            'difficulty': 1,
            'world_type': 'Modern',
            'required_level': 2,
            'task_data': json.dumps({
                'tasks': [
                    {'id': 'A', 'name': 'Design Logo', 'duration': 3},
                    {'id': 'B', 'name': 'Print Menus', 'duration': 2, 'needs_logo': True},
                    {'id': 'C', 'name': 'Train Staff', 'duration': 5},
                    {'id': 'D', 'name': 'Order Supplies', 'duration': 2},
                    {'id': 'E', 'name': 'Grand Opening', 'duration': 1, 'needs': ['B', 'C', 'D']}
                ]
            }),
            'correct_answer': json.dumps({'parallel': ['A', 'C', 'D'], 'sequential': [['A', 'B'], ['B', 'E'], ['C', 'E'], ['D', 'E']]}),
            'exp_reward': 55,
            'time_limit_seconds': 180,
            'hint_text': 'Tasks without dependencies can run in parallel.'
        },
        {
            'title': 'Schedule Compression',
            'description': 'Your project is 2 weeks behind. Decide which technique to use: crashing or fast-tracking.',
            'challenge_type': 'compression',
            'difficulty': 3,
            'world_type': 'Modern',
            'required_level': 4,
            'task_data': json.dumps({
                'current_duration': 12,
                'target_duration': 10,
                'options': [
                    {'type': 'crash', 'task': 'Kitchen Install', 'cost': 2000, 'time_saved': 2},
                    {'type': 'crash', 'task': 'Staff Training', 'cost': 1500, 'time_saved': 1},
                    {'type': 'fast_track', 'tasks': ['Permits', 'Equipment Order'], 'risk': 'medium', 'time_saved': 2}
                ]
            }),
            'correct_answer': json.dumps({'best_option': 'fast_track', 'reason': 'No additional cost, acceptable risk'}),
            'exp_reward': 80,
            'time_limit_seconds': 180,
            'hint_text': 'Crashing adds cost; fast-tracking adds risk by overlapping tasks.'
        }
    ]
    
    for ch in challenges:
        cur.execute("""
            INSERT INTO scheduling_challenges 
            (title, description, challenge_type, difficulty, world_type, required_level,
             task_data, correct_answer, exp_reward, time_limit_seconds, hint_text)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            ch['title'], ch['description'], ch['challenge_type'], ch['difficulty'],
            ch['world_type'], ch['required_level'], ch['task_data'], ch['correct_answer'],
            ch['exp_reward'], ch['time_limit_seconds'], ch['hint_text']
        ))
    
    conn.commit()
    print(f"Seeded {len(challenges)} scheduling challenges!")
    cur.close()
    return_connection(conn)



def seed_cash_flow_challenges():
    """Seed cash flow forecasting challenges."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM cash_flow_challenges")
    if cur.fetchone()['count'] > 0:
        print("Cash flow challenges already seeded.")
        cur.close()
        return_connection(conn)
        return
    
    import json
    
    challenges = [
        {
            'title': 'Receivables Timing',
            'description': 'Your catering business just landed a $10,000 contract. The client offers 3 payment options. Which maximizes your cash position?',
            'challenge_type': 'timing',
            'difficulty': 1,
            'scenario_data': json.dumps({
                'contract_value': 10000,
                'current_cash': 5000,
                'weekly_expenses': 3000,
                'options': [
                    {'id': 'A', 'name': '50% upfront, 50% on delivery', 'upfront': 5000, 'on_delivery': 5000, 'weeks_to_delivery': 4},
                    {'id': 'B', 'name': '100% on delivery', 'upfront': 0, 'on_delivery': 10000, 'weeks_to_delivery': 4},
                    {'id': 'C', 'name': '25% upfront, 75% Net 30', 'upfront': 2500, 'on_delivery': 0, 'net30': 7500, 'weeks_to_delivery': 4}
                ]
            }),
            'correct_answer': json.dumps({'best': 'A', 'reason': 'Prevents cash shortage in week 2-3 while still receiving full payment'}),
            'exp_reward': 60,
            'hint_text': 'Calculate your cash balance each week under each scenario to see which avoids going negative.'
        },
        {
            'title': 'Emergency Cash Reserve',
            'description': 'How many weeks of operating expenses should you keep as emergency cash reserve for a restaurant?',
            'challenge_type': 'planning',
            'difficulty': 1,
            'scenario_data': json.dumps({
                'weekly_fixed_costs': 5000,
                'weekly_variable_costs': 3000,
                'average_weekly_revenue': 12000,
                'industry': 'Restaurant'
            }),
            'correct_answer': json.dumps({'weeks': 8, 'range': [6, 12], 'reason': 'Restaurants need 6-12 weeks reserve due to seasonality and unpredictable events'}),
            'exp_reward': 50,
            'hint_text': 'Consider what would happen if revenue dropped suddenly for several weeks.'
        },
        {
            'title': '13-Week Forecast',
            'description': 'Complete this 13-week cash flow forecast. In which week will you first need a credit line?',
            'challenge_type': 'forecast',
            'difficulty': 2,
            'scenario_data': json.dumps({
                'starting_cash': 20000,
                'minimum_cash': 5000,
                'weeks': [
                    {'week': 1, 'inflows': 8000, 'outflows': 6000},
                    {'week': 2, 'inflows': 7500, 'outflows': 6000},
                    {'week': 3, 'inflows': 6000, 'outflows': 6000},
                    {'week': 4, 'inflows': 5000, 'outflows': 8000},
                    {'week': 5, 'inflows': 4500, 'outflows': 6000},
                    {'week': 6, 'inflows': 4000, 'outflows': 6000},
                    {'week': 7, 'inflows': 5000, 'outflows': 6000},
                    {'week': 8, 'inflows': 6000, 'outflows': 9000},
                    {'week': 9, 'inflows': 7000, 'outflows': 6000},
                    {'week': 10, 'inflows': 8000, 'outflows': 6000},
                    {'week': 11, 'inflows': 9000, 'outflows': 6000},
                    {'week': 12, 'inflows': 10000, 'outflows': 6000},
                    {'week': 13, 'inflows': 11000, 'outflows': 6000}
                ]
            }),
            'correct_answer': json.dumps({'credit_needed_week': 8, 'lowest_balance': 2500, 'amount_needed': 2500}),
            'exp_reward': 80,
            'hint_text': 'Track the running balance each week: Ending = Beginning + Inflows - Outflows'
        },
        {
            'title': 'Payables Strategy',
            'description': 'You have $8,000 cash and $15,000 in bills due. Prioritize which to pay first.',
            'challenge_type': 'prioritization',
            'difficulty': 2,
            'scenario_data': json.dumps({
                'available_cash': 8000,
                'bills': [
                    {'id': 1, 'vendor': 'Rent', 'amount': 3000, 'due': 'Now', 'penalty': 'Eviction', 'discount': 0},
                    {'id': 2, 'vendor': 'Food Supplier', 'amount': 4000, 'due': '5 days', 'penalty': 'Stop delivery', 'discount': 0.02},
                    {'id': 3, 'vendor': 'Utilities', 'amount': 800, 'due': '10 days', 'penalty': 'Shutoff', 'discount': 0},
                    {'id': 4, 'vendor': 'Equipment Lease', 'amount': 2000, 'due': '15 days', 'penalty': 'Late fee $50', 'discount': 0},
                    {'id': 5, 'vendor': 'Marketing Agency', 'amount': 2500, 'due': '30 days', 'penalty': 'None', 'discount': 0.05},
                    {'id': 6, 'vendor': 'Linen Service', 'amount': 700, 'due': '7 days', 'penalty': 'Service pause', 'discount': 0}
                ]
            }),
            'correct_answer': json.dumps({'priority_order': [1, 3, 2], 'reasoning': 'Pay essential operational bills first (rent, utilities), then supplies to keep operating'}),
            'exp_reward': 75,
            'hint_text': 'Consider which bills, if unpaid, would shut down your business vs just cost you fees.'
        },
        {
            'title': 'Seasonal Cash Planning',
            'description': 'Your ice cream shop revenue varies seasonally. Plan your cash needs for the slow winter months.',
            'challenge_type': 'seasonal',
            'difficulty': 3,
            'scenario_data': json.dumps({
                'monthly_revenue': {
                    'Jan': 8000, 'Feb': 9000, 'Mar': 15000, 'Apr': 22000, 'May': 30000, 'Jun': 40000,
                    'Jul': 45000, 'Aug': 42000, 'Sep': 28000, 'Oct': 18000, 'Nov': 10000, 'Dec': 12000
                },
                'fixed_costs_monthly': 12000,
                'variable_cost_pct': 0.35,
                'current_cash': 25000,
                'start_month': 'September'
            }),
            'correct_answer': json.dumps({
                'months_negative': ['Jan', 'Feb', 'Nov'],
                'max_shortfall': 6600,
                'savings_needed': 15000
            }),
            'exp_reward': 100,
            'hint_text': 'Calculate net cash flow each month (Revenue - Fixed Costs - Variable Costs) and track cumulative position.'
        }
    ]
    
    for ch in challenges:
        cur.execute("""
            INSERT INTO cash_flow_challenges 
            (title, description, challenge_type, difficulty, scenario_data, correct_answer, exp_reward, hint_text)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            ch['title'], ch['description'], ch['challenge_type'], ch['difficulty'],
            ch['scenario_data'], ch['correct_answer'], ch['exp_reward'], ch['hint_text']
        ))
    
    conn.commit()
    print(f"Seeded {len(challenges)} cash flow challenges!")
    cur.close()
    return_connection(conn)


def seed_negotiation_scenarios():
    """Seed negotiation simulation scenarios."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM negotiation_scenarios")
    if cur.fetchone()['count'] > 0:
        print("Negotiation scenarios already seeded.")
        cur.close()
        return_connection(conn)
        return
    
    import json
    
    scenarios = [
        {
            'title': 'Vendor Price Negotiation',
            'description': 'Your main food supplier wants to raise prices 15%. Negotiate a better deal.',
            'negotiation_type': 'vendor',
            'difficulty': 1,
            'counterparty_name': 'Marco, Sales Rep',
            'counterparty_style': 'collaborative',
            'your_batna': json.dumps({'alternative': 'Switch to competitor', 'switching_cost': 2000, 'time_to_switch': '4 weeks'}),
            'their_batna': json.dumps({'lose_account_impact': 'Moderate - you are 5% of their business'}),
            'issues': json.dumps([
                {'name': 'price_increase', 'your_ideal': 0, 'their_ideal': 15, 'importance_you': 10, 'importance_them': 8},
                {'name': 'payment_terms', 'your_ideal': 45, 'their_ideal': 15, 'importance_you': 6, 'importance_them': 9},
                {'name': 'delivery_frequency', 'your_ideal': 3, 'their_ideal': 1, 'importance_you': 4, 'importance_them': 5}
            ]),
            'opening_position': json.dumps({'price_increase': 15, 'payment_terms': 15, 'delivery_frequency': 1}),
            'optimal_outcome': json.dumps({'price_increase': 5, 'payment_terms': 30, 'delivery_frequency': 2}),
            'exp_reward': 100
        },
        {
            'title': 'Salary Negotiation',
            'description': 'Your star chef wants a raise or they will leave. Find a deal that works for both.',
            'negotiation_type': 'employment',
            'difficulty': 2,
            'counterparty_name': 'Chef Sarah',
            'counterparty_style': 'competitive',
            'your_batna': json.dumps({'alternative': 'Hire replacement', 'cost': 8000, 'time': '6 weeks', 'quality_drop': 'Significant'}),
            'their_batna': json.dumps({'other_offer': '$65,000 salary at competitor'}),
            'issues': json.dumps([
                {'name': 'base_salary', 'your_ideal': 55000, 'their_ideal': 70000, 'importance_you': 9, 'importance_them': 10},
                {'name': 'bonus_pct', 'your_ideal': 0, 'their_ideal': 15, 'importance_you': 5, 'importance_them': 7},
                {'name': 'schedule_flexibility', 'your_ideal': 0, 'their_ideal': 2, 'importance_you': 3, 'importance_them': 8},
                {'name': 'title', 'your_ideal': 0, 'their_ideal': 1, 'importance_you': 1, 'importance_them': 6}
            ]),
            'opening_position': json.dumps({'base_salary': 70000, 'bonus_pct': 15, 'schedule_flexibility': 2, 'title': 1}),
            'optimal_outcome': json.dumps({'base_salary': 60000, 'bonus_pct': 10, 'schedule_flexibility': 1, 'title': 1}),
            'exp_reward': 150
        },
        {
            'title': 'Lease Renewal',
            'description': 'Your restaurant lease is up for renewal. The landlord wants a 20% increase.',
            'negotiation_type': 'real_estate',
            'difficulty': 2,
            'counterparty_name': 'Property Manager Linda',
            'counterparty_style': 'analytical',
            'your_batna': json.dumps({'alternative': 'Move locations', 'cost': 50000, 'time': '3 months', 'customer_loss': '30%'}),
            'their_batna': json.dumps({'vacancy_cost': '$5000/month', 'time_to_relet': '4 months'}),
            'issues': json.dumps([
                {'name': 'rent_increase_pct', 'your_ideal': 0, 'their_ideal': 20, 'importance_you': 10, 'importance_them': 9},
                {'name': 'lease_term_years', 'your_ideal': 2, 'their_ideal': 5, 'importance_you': 7, 'importance_them': 8},
                {'name': 'improvement_allowance', 'your_ideal': 15000, 'their_ideal': 0, 'importance_you': 6, 'importance_them': 4},
                {'name': 'signage_rights', 'your_ideal': 1, 'their_ideal': 0, 'importance_you': 5, 'importance_them': 2}
            ]),
            'opening_position': json.dumps({'rent_increase_pct': 20, 'lease_term_years': 5, 'improvement_allowance': 0, 'signage_rights': 0}),
            'optimal_outcome': json.dumps({'rent_increase_pct': 8, 'lease_term_years': 3, 'improvement_allowance': 10000, 'signage_rights': 1}),
            'exp_reward': 175
        }
    ]
    
    for sc in scenarios:
        cur.execute("""
            INSERT INTO negotiation_scenarios 
            (title, description, negotiation_type, difficulty, counterparty_name, counterparty_style,
             your_batna, their_batna, issues, opening_position, optimal_outcome, exp_reward)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            sc['title'], sc['description'], sc['negotiation_type'], sc['difficulty'],
            sc['counterparty_name'], sc['counterparty_style'], sc['your_batna'], sc['their_batna'],
            sc['issues'], sc['opening_position'], sc['optimal_outcome'], sc['exp_reward']
        ))
    
    conn.commit()
    print(f"Seeded {len(scenarios)} negotiation scenarios!")
    cur.close()
    return_connection(conn)


def seed_risk_categories():
    """Seed risk categories for the risk management system."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM risk_categories")
    if cur.fetchone()['count'] > 0:
        print("Risk categories already seeded.")
        cur.close()
        return_connection(conn)
        return
    
    categories = [
        ('Operational', 'Risks related to day-to-day operations, equipment, and processes', 'bi-gear'),
        ('Financial', 'Risks related to cash flow, credit, and market conditions', 'bi-currency-dollar'),
        ('Legal/Compliance', 'Risks from regulations, contracts, and legal obligations', 'bi-shield-exclamation'),
        ('Reputational', 'Risks to brand image and customer perception', 'bi-star'),
        ('Strategic', 'Risks from competition, market changes, and business decisions', 'bi-compass'),
        ('Human Resources', 'Risks related to staffing, training, and workplace issues', 'bi-people'),
        ('Technology', 'Risks from IT systems, data security, and digital operations', 'bi-laptop'),
        ('External/Environmental', 'Risks from natural disasters, supply chain, and external events', 'bi-cloud-lightning')
    ]
    
    for cat in categories:
        cur.execute("""
            INSERT INTO risk_categories (category_name, description, icon)
            VALUES (%s, %s, %s)
        """, cat)
    
    conn.commit()
    print(f"Seeded {len(categories)} risk categories!")
    cur.close()
    return_connection(conn)


def seed_market_simulation():
    """Seed market segments, challenges, and competitor data."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM market_segments")
    if cur.fetchone()['count'] > 0:
        print("Market simulation already seeded.")
        cur.close()
        return_connection(conn)
        return
    
    segments = [
        ('Budget Conscious', 25000, 90, 30, 20, 0.01, 'Price-sensitive customers who prioritize affordability over quality'),
        ('Value Seekers', 40000, 60, 60, 40, 0.03, 'Customers looking for the best balance of price and quality'),
        ('Premium Buyers', 15000, 20, 90, 60, 0.02, 'Quality-focused customers willing to pay more for excellence'),
        ('Brand Loyalists', 10000, 40, 70, 90, 0.01, 'Customers who stick with brands they trust regardless of alternatives'),
        ('Early Adopters', 5000, 30, 50, 25, 0.05, 'Trend-seekers who try new products and influence others')
    ]
    
    for seg in segments:
        cur.execute("""
            INSERT INTO market_segments 
            (segment_name, segment_size, price_sensitivity, quality_preference, brand_loyalty, growth_rate, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, seg)
    
    challenges = [
        {
            'title': 'Price Elasticity Challenge',
            'description': 'Your product currently sells at $50 with 1000 units/month. Research shows a 10% price increase would reduce demand by 15%. Calculate the new revenue.',
            'challenge_type': 'pricing',
            'difficulty': 1,
            'scenario_data': json.dumps({'current_price': 50, 'current_units': 1000, 'price_change_pct': 10, 'demand_change_pct': -15}),
            'correct_answer': json.dumps({'new_revenue': 46750}),
            'hint_text': 'New Revenue = New Price × New Quantity. New Price = $50 × 1.10. New Quantity = 1000 × 0.85',
            'exp_reward': 100
        },
        {
            'title': 'Market Share Battle',
            'description': 'Your competitor launched a 20% off sale. You have 15% market share, they have 25%. If you match their discount, you keep share. If not, you lose 3%. What should you do if your margin is 30%?',
            'challenge_type': 'competition',
            'difficulty': 2,
            'scenario_data': json.dumps({'your_share': 15, 'their_share': 25, 'your_margin': 30, 'their_discount': 20, 'share_loss_if_ignore': 3}),
            'correct_answer': json.dumps({'decision': 'ignore', 'reason': 'Losing 3% share costs less than 20% margin reduction'}),
            'hint_text': 'Compare the cost of losing 3% market share vs. giving 20% discount on all sales. Sometimes it\'s better to let competitors have the price-sensitive customers.',
            'exp_reward': 150
        },
        {
            'title': 'Marketing ROI Calculation',
            'description': 'You spent $5000 on a marketing campaign. It generated 200 new customers with an average order value of $75 and 40% profit margin. Calculate your ROI.',
            'challenge_type': 'marketing',
            'difficulty': 1,
            'scenario_data': json.dumps({'marketing_spend': 5000, 'new_customers': 200, 'avg_order': 75, 'margin_pct': 40}),
            'correct_answer': json.dumps({'roi': 20, 'profit': 6000, 'net_gain': 1000}),
            'hint_text': 'Profit = Customers × Order Value × Margin%. ROI = (Profit - Cost) / Cost × 100',
            'exp_reward': 100
        },
        {
            'title': 'Segment Targeting Decision',
            'description': 'You can only afford to target one market segment. Premium Buyers (15K customers, $120 avg purchase, 50% margin) or Value Seekers (40K customers, $50 avg purchase, 25% margin). Assume you can capture 5% of either segment.',
            'challenge_type': 'segmentation',
            'difficulty': 2,
            'scenario_data': json.dumps({
                'segments': [
                    {'name': 'Premium Buyers', 'size': 15000, 'avg_purchase': 120, 'margin': 50},
                    {'name': 'Value Seekers', 'size': 40000, 'avg_purchase': 50, 'margin': 25}
                ],
                'capture_rate': 5
            }),
            'correct_answer': json.dumps({'best_segment': 'Premium Buyers', 'profit': 45000}),
            'hint_text': 'Calculate expected profit for each: Size × Capture Rate × Avg Purchase × Margin',
            'exp_reward': 125
        },
        {
            'title': 'Competitive Positioning',
            'description': 'Map your position: You have Quality=70, Price=60. Competitor A: Quality=80, Price=90. Competitor B: Quality=50, Price=40. Which gap in the market should you target?',
            'challenge_type': 'positioning',
            'difficulty': 3,
            'scenario_data': json.dumps({
                'your_position': {'quality': 70, 'price': 60},
                'competitors': [
                    {'name': 'A', 'quality': 80, 'price': 90},
                    {'name': 'B', 'quality': 50, 'price': 40}
                ]
            }),
            'correct_answer': json.dumps({'strategy': 'value_leader', 'reason': 'High quality at moderate price fills gap between premium A and budget B'}),
            'hint_text': 'Look for gaps in the market where customer needs are unmet. You are positioned between a premium and budget competitor.',
            'exp_reward': 175
        }
    ]
    
    for ch in challenges:
        cur.execute("""
            INSERT INTO market_challenges 
            (title, description, challenge_type, difficulty, scenario_data, correct_answer, hint_text, exp_reward)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (ch['title'], ch['description'], ch['challenge_type'], ch['difficulty'],
              ch['scenario_data'], ch['correct_answer'], ch['hint_text'], ch['exp_reward']))
    
    conn.commit()
    print(f"Seeded {len(segments)} market segments and {len(challenges)} market challenges!")
    cur.close()
    return_connection(conn)


def seed_hr_management():
    """Seed employee roles and HR challenges."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM employee_roles")
    if cur.fetchone()['count'] > 0:
        print("HR management already seeded.")
        cur.close()
        return_connection(conn)
        return
    
    roles = [
        ('Sales Associate', 'Sales', 35000, json.dumps({'communication': 3, 'product_knowledge': 2}), 
         'Handle customer inquiries, process sales, meet quotas', 'Sales Associate → Senior Sales → Sales Manager'),
        ('Customer Service Rep', 'Support', 32000, json.dumps({'communication': 4, 'patience': 3, 'problem_solving': 2}),
         'Resolve customer issues, handle complaints, process returns', 'CSR → Senior CSR → Support Manager'),
        ('Marketing Coordinator', 'Marketing', 42000, json.dumps({'creativity': 3, 'analytics': 2, 'social_media': 3}),
         'Execute marketing campaigns, manage social media, track metrics', 'Coordinator → Specialist → Marketing Manager'),
        ('Operations Manager', 'Operations', 55000, json.dumps({'leadership': 4, 'organization': 4, 'analytics': 3}),
         'Oversee daily operations, manage staff, optimize processes', 'Ops Manager → Director → VP Operations'),
        ('Financial Analyst', 'Finance', 60000, json.dumps({'analytics': 5, 'excel': 4, 'attention_to_detail': 4}),
         'Analyze financial data, create reports, support decision-making', 'Analyst → Senior Analyst → Finance Manager'),
        ('HR Generalist', 'Human Resources', 48000, json.dumps({'communication': 4, 'empathy': 4, 'organization': 3}),
         'Handle recruiting, onboarding, employee relations, compliance', 'Generalist → Senior HR → HR Director'),
        ('Software Developer', 'Technology', 75000, json.dumps({'coding': 5, 'problem_solving': 4, 'teamwork': 3}),
         'Build and maintain software systems, collaborate with team', 'Developer → Senior Dev → Tech Lead → CTO'),
        ('Administrative Assistant', 'Administration', 30000, json.dumps({'organization': 4, 'communication': 3, 'multitasking': 4}),
         'Manage schedules, handle correspondence, support executives', 'Admin → Executive Assistant → Office Manager')
    ]
    
    for role in roles:
        cur.execute("""
            INSERT INTO employee_roles 
            (role_name, department, base_salary, skill_requirements, responsibilities, career_path)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, role)
    
    challenges = [
        {
            'title': 'The Hiring Decision',
            'description': 'You need to hire a Sales Associate. Candidate A has 5 years experience but asks for $45K. Candidate B is a recent graduate asking $32K with high potential. Your budget is $38K.',
            'challenge_type': 'hiring',
            'difficulty': 1,
            'scenario_data': json.dumps({
                'role': 'Sales Associate',
                'budget': 38000,
                'candidates': [
                    {'name': 'Candidate A', 'experience': 5, 'ask': 45000, 'potential': 70},
                    {'name': 'Candidate B', 'experience': 0, 'ask': 32000, 'potential': 90}
                ]
            }),
            'correct_answer': json.dumps({'choice': 'B', 'reason': 'Within budget with higher long-term potential and trainability'}),
            'hint_text': 'Consider both immediate fit and long-term potential. Budget constraints matter.',
            'exp_reward': 100
        },
        {
            'title': 'Performance Review Prep',
            'description': 'Employee has met 3 of 5 goals (60%), received positive customer feedback, but has attendance issues (late 6 times). What rating would you give: 1-5?',
            'challenge_type': 'performance',
            'difficulty': 1,
            'scenario_data': json.dumps({
                'goals_met': 3,
                'goals_total': 5,
                'customer_feedback': 'positive',
                'attendance_issues': 6,
                'peer_reviews': 'average'
            }),
            'correct_answer': json.dumps({'rating': 3, 'reason': 'Meets expectations with room for improvement'}),
            'hint_text': 'Balance the positives (goals met, good feedback) against negatives (attendance).',
            'exp_reward': 75
        },
        {
            'title': 'Conflict Resolution',
            'description': 'Two employees are in conflict. Employee A claims B takes credit for shared work. B claims A doesn\'t pull their weight. Both are valuable. How do you handle this?',
            'challenge_type': 'conflict',
            'difficulty': 2,
            'scenario_data': json.dumps({
                'employee_a': {'tenure': 3, 'performance': 85, 'complaint': 'credit_taking'},
                'employee_b': {'tenure': 2, 'performance': 80, 'complaint': 'lack_of_effort'}
            }),
            'correct_answer': json.dumps({'approach': 'mediate', 'actions': ['Meet separately', 'Meet together', 'Set clear expectations', 'Document']}),
            'hint_text': 'Avoid taking sides. Focus on understanding both perspectives and finding common ground.',
            'exp_reward': 125
        },
        {
            'title': 'Retention Challenge',
            'description': 'Your top performer got an outside offer for 20% more salary. They make $60K. You can offer 10% raise max. What else can you offer to retain them?',
            'challenge_type': 'retention',
            'difficulty': 2,
            'scenario_data': json.dumps({
                'current_salary': 60000,
                'outside_offer': 72000,
                'max_raise_pct': 10,
                'available_perks': ['flexible_schedule', 'remote_work', 'title_promotion', 'training_budget', 'bonus_plan']
            }),
            'correct_answer': json.dumps({'strategy': 'total_compensation', 'offer': {'raise_pct': 10, 'perks': ['flexible_schedule', 'title_promotion', 'bonus_plan']}}),
            'hint_text': 'Total compensation includes more than salary. Think about flexibility, growth, and recognition.',
            'exp_reward': 150
        },
        {
            'title': 'Team Building Budget',
            'description': 'You have $2000 for team building. Team of 10. Options: A) Team dinner ($50/person), B) Escape room ($30/person + transport), C) Volunteer day ($20/person). What maximizes engagement?',
            'challenge_type': 'culture',
            'difficulty': 1,
            'scenario_data': json.dumps({
                'budget': 2000,
                'team_size': 10,
                'options': [
                    {'name': 'Team Dinner', 'cost_per_person': 50, 'engagement_score': 6},
                    {'name': 'Escape Room', 'cost_per_person': 45, 'engagement_score': 9},
                    {'name': 'Volunteer Day', 'cost_per_person': 20, 'engagement_score': 8}
                ]
            }),
            'correct_answer': json.dumps({'choice': 'Escape Room', 'reason': 'Highest engagement within budget, promotes teamwork'}),
            'hint_text': 'Consider what builds collaboration and team bonds, not just fun.',
            'exp_reward': 75
        }
    ]
    
    for ch in challenges:
        cur.execute("""
            INSERT INTO hr_challenges 
            (title, description, challenge_type, difficulty, scenario_data, correct_answer, hint_text, exp_reward)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (ch['title'], ch['description'], ch['challenge_type'], ch['difficulty'],
              ch['scenario_data'], ch['correct_answer'], ch['hint_text'], ch['exp_reward']))
    
    conn.commit()
    print(f"Seeded {len(roles)} employee roles and {len(challenges)} HR challenges!")
    cur.close()
    return_connection(conn)


def seed_investor_pitch():
    """Seed pitch templates and investor profiles."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM pitch_templates")
    if cur.fetchone()['count'] > 0:
        print("Investor pitch already seeded.")
        cur.close()
        return_connection(conn)
        return
    
    templates = [
        ('Standard Pitch Deck', 'Title Slide', 1, 'Company name, tagline, your name and title',
         'Acme Corp - Making the World a Better Place, One Widget at a Time. Jane Doe, CEO & Founder',
         json.dumps({'has_company_name': 10, 'has_tagline': 10, 'memorable': 10})),
        ('Standard Pitch Deck', 'Problem', 2, 'The pain point you\'re solving - make it relatable and quantifiable',
         '70% of small businesses fail within 10 years, often due to poor financial management. Current solutions are expensive and complex.',
         json.dumps({'clear_problem': 15, 'quantified': 15, 'relatable': 10})),
        ('Standard Pitch Deck', 'Solution', 3, 'Your product/service and how it solves the problem',
         'FinanceEasy is an AI-powered CFO for small businesses. Automated bookkeeping, cash flow predictions, and actionable insights for $99/month.',
         json.dumps({'solves_problem': 15, 'unique_approach': 10, 'clear_value': 15})),
        ('Standard Pitch Deck', 'Market Opportunity', 4, 'TAM, SAM, SOM - the size of your opportunity',
         'TAM: $50B global SMB finance market. SAM: $8B US market. SOM: $400M (5% of US market in 5 years).',
         json.dumps({'tam_defined': 10, 'sam_defined': 10, 'som_realistic': 15, 'growing_market': 5})),
        ('Standard Pitch Deck', 'Business Model', 5, 'How you make money',
         'SaaS subscription: $99/month Basic, $249/month Pro, $599/month Enterprise. 85% gross margin. Upsell consulting services.',
         json.dumps({'clear_revenue': 15, 'pricing_justified': 10, 'margins_shown': 10, 'scalable': 5})),
        ('Standard Pitch Deck', 'Traction', 6, 'Proof that it\'s working - metrics, customers, revenue',
         '500 paying customers, $45K MRR, 15% month-over-month growth. Key customers: TechStart Inc, LocalBiz Co.',
         json.dumps({'revenue_shown': 20, 'growth_rate': 15, 'customer_names': 5})),
        ('Standard Pitch Deck', 'Team', 7, 'Why you\'re the right team to solve this',
         'Jane Doe (CEO) - 10 years at Goldman Sachs. John Smith (CTO) - Ex-Google engineer. Advisory board includes CFOs from Fortune 500.',
         json.dumps({'relevant_experience': 15, 'complete_team': 10, 'advisors': 5})),
        ('Standard Pitch Deck', 'The Ask', 8, 'How much you need and what you\'ll do with it',
         'Raising $2M seed round. Use of funds: 50% engineering (hire 3), 30% sales/marketing, 20% operations. 18-month runway to Series A milestones.',
         json.dumps({'amount_clear': 10, 'use_of_funds': 15, 'milestones': 10, 'runway': 5}))
    ]
    
    for t in templates:
        cur.execute("""
            INSERT INTO pitch_templates 
            (template_name, section_name, section_order, description, example_content, scoring_criteria)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, t)
    
    investors = [
        ('Sarah Chen', 'angel', json.dumps(['SaaS', 'FinTech', 'B2B']), 25000, 150000, 70,
         json.dumps({'team': 30, 'traction': 25, 'market': 25, 'product': 20}), 'collaborative'),
        ('Marcus Williams', 'vc_associate', json.dumps(['Enterprise', 'AI', 'Deep Tech']), 500000, 3000000, 40,
         json.dumps({'market': 35, 'traction': 30, 'team': 20, 'product': 15}), 'analytical'),
        ('Emily Rodriguez', 'angel_group', json.dumps(['Consumer', 'E-commerce', 'Marketplace']), 50000, 500000, 60,
         json.dumps({'traction': 35, 'product': 25, 'team': 25, 'market': 15}), 'skeptical'),
        ('David Kim', 'vc_partner', json.dumps(['HealthTech', 'EdTech', 'Impact']), 1000000, 10000000, 30,
         json.dumps({'market': 40, 'team': 30, 'traction': 20, 'product': 10}), 'strategic'),
        ('Lisa Thompson', 'family_office', json.dumps(['Real Estate Tech', 'Sustainability', 'Consumer']), 100000, 2000000, 50,
         json.dumps({'team': 35, 'product': 25, 'market': 20, 'traction': 20}), 'relationship_focused')
    ]
    
    for inv in investors:
        cur.execute("""
            INSERT INTO investor_profiles 
            (investor_name, investor_type, focus_areas, investment_range_min, investment_range_max, 
             risk_tolerance, priorities, personality)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, inv)
    
    conn.commit()
    print(f"Seeded {len(templates)} pitch templates and {len(investors)} investor profiles!")
    cur.close()
    return_connection(conn)


def seed_learning_analytics():
    """Seed learning analytics recommendations."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM learning_recommendations")
    if cur.fetchone()['count'] > 0:
        print("Learning analytics already seeded.")
        cur.close()
        return_connection(conn)
        return
    
    recommendations = [
        ('marketing', 1, 'Start with basic marketing concepts', 'Complete Marketing 101 scenarios to build your foundation.'),
        ('marketing', 3, 'Practice market segmentation', 'Try the Market Simulation challenges to sharpen your skills.'),
        ('marketing', 5, 'Master competitive positioning', 'Advanced marketing scenarios await - focus on differentiation.'),
        ('finance', 1, 'Learn basic accounting', 'Start with the Accounting Hub to understand debits and credits.'),
        ('finance', 3, 'Practice cash flow management', 'The Cash Flow Forecast system will help you master timing.'),
        ('finance', 5, 'Advanced financial analysis', 'Work on ROI calculations and break-even analysis.'),
        ('operations', 1, 'Understand supply chain basics', 'Begin with the Supply Chain Simulator.'),
        ('operations', 3, 'Optimize inventory management', 'Practice reorder points and safety stock calculations.'),
        ('operations', 5, 'Master project scheduling', 'Use the Scheduling Challenges to learn critical path.'),
        ('hr', 1, 'Learn hiring fundamentals', 'HR Management challenges teach recruitment basics.'),
        ('hr', 3, 'Practice performance reviews', 'Work on giving balanced, constructive feedback.'),
        ('hr', 5, 'Master conflict resolution', 'Advanced HR scenarios cover difficult conversations.'),
        ('legal', 1, 'Understand business contracts', 'Legal scenarios introduce contract fundamentals.'),
        ('legal', 3, 'Risk management basics', 'Use the Risk Dashboard to identify and mitigate risks.'),
        ('strategy', 1, 'Business planning fundamentals', 'Start with the Business Plan Workshop.'),
        ('strategy', 3, 'Practice negotiation', 'Negotiation Simulator teaches BATNA and anchoring.'),
        ('strategy', 5, 'Investor relations', 'Master pitch decks with the Investor Pitch Simulator.')
    ]
    
    for rec in recommendations:
        cur.execute("""
            INSERT INTO learning_recommendations 
            (discipline, min_level, title, description)
            VALUES (%s, %s, %s, %s)
        """, rec)
    
    conn.commit()
    print(f"Seeded {len(recommendations)} learning recommendations!")
    cur.close()
    return_connection(conn)


def seed_educational_achievements():
    """Seed educational achievement milestones."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM educational_achievements")
    if cur.fetchone()['count'] > 0:
        print("Educational achievements already seeded.")
        cur.close()
        return_connection(conn)
        return
    
    achievements = [
        ('Cash Flow Master', 'Complete all cash flow challenges', 'cash_flow', 5, 500, 'gold'),
        ('Business Planner', 'Create a complete business plan', 'business_plan', 1, 300, 'silver'),
        ('Negotiation Pro', 'Win 10 negotiations', 'negotiation', 10, 400, 'gold'),
        ('Risk Manager', 'Identify and mitigate 20 risks', 'risk', 20, 350, 'silver'),
        ('Supply Chain Expert', 'Manage 50 purchase orders', 'supply_chain', 50, 450, 'gold'),
        ('Market Strategist', 'Complete all market challenges', 'market', 5, 500, 'gold'),
        ('HR Leader', 'Hire and manage 10 employees', 'hr', 10, 400, 'silver'),
        ('Pitch Perfect', 'Successfully pitch to 5 investors', 'pitch', 5, 500, 'gold'),
        ('Accounting Ace', 'Close 12 monthly periods', 'accounting', 12, 600, 'platinum'),
        ('Project Manager', 'Complete 10 scheduling challenges', 'scheduling', 10, 400, 'silver'),
        ('Marketing Maven', 'Reach level 5 in Marketing', 'discipline_level', 5, 300, 'silver'),
        ('Finance Guru', 'Reach level 5 in Finance', 'discipline_level', 5, 300, 'silver'),
        ('Operations Expert', 'Reach level 5 in Operations', 'discipline_level', 5, 300, 'silver'),
        ('HR Specialist', 'Reach level 5 in HR', 'discipline_level', 5, 300, 'silver'),
        ('Legal Eagle', 'Reach level 5 in Legal', 'discipline_level', 5, 300, 'silver'),
        ('Strategy Master', 'Reach level 5 in Strategy', 'discipline_level', 5, 300, 'silver'),
        ('Business Tycoon', 'Reach level 10 in all disciplines', 'discipline_level', 60, 2000, 'diamond'),
        ('Weekly Warrior', 'Complete 10 weekly challenges', 'weekly', 10, 250, 'bronze'),
        ('Daily Dedication', 'Log in 30 consecutive days', 'streak', 30, 500, 'gold'),
        ('First Steps', 'Complete your first scenario', 'scenario', 1, 50, 'bronze')
    ]
    
    for ach in achievements:
        cur.execute("""
            INSERT INTO educational_achievements 
            (achievement_name, description, category, requirement_count, exp_reward, tier)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, ach)
    
    conn.commit()
    print(f"Seeded {len(achievements)} educational achievements!")
    cur.close()
    return_connection(conn)


def seed_competitions():
    """Seed competition types and leagues."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM competition_types")
    if cur.fetchone()['count'] > 0:
        print("Competitions already seeded.")
        cur.close()
        return_connection(conn)
        return
    
    comp_types = [
        ('Weekly Sprint', 'Complete the most challenges in a week', 'weekly', 7, 500, json.dumps(['scenarios_completed', 'exp_earned'])),
        ('Profit Masters', 'Highest profit in simulations', 'weekly', 7, 600, json.dumps(['simulation_profit', 'efficiency'])),
        ('Pitch Competition', 'Best investor pitch scores', 'event', 3, 1000, json.dumps(['pitch_score', 'investor_approval'])),
        ('Risk Assessment', 'Most comprehensive risk management', 'weekly', 7, 400, json.dumps(['risks_identified', 'risks_mitigated'])),
        ('Hiring Challenge', 'Build the best team', 'event', 5, 750, json.dumps(['team_performance', 'budget_efficiency'])),
        ('Market Domination', 'Highest market share gains', 'weekly', 7, 550, json.dumps(['market_share', 'revenue_growth']))
    ]
    
    for comp in comp_types:
        cur.execute("""
            INSERT INTO competition_types 
            (competition_name, description, competition_type, duration_days, exp_reward, scoring_criteria)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, comp)
    
    leagues = [
        ('Bronze League', 1, 0, 999, 1.0),
        ('Silver League', 2, 1000, 4999, 1.2),
        ('Gold League', 3, 5000, 14999, 1.5),
        ('Platinum League', 4, 15000, 49999, 2.0),
        ('Diamond League', 5, 50000, 999999999, 3.0)
    ]
    
    for league in leagues:
        cur.execute("""
            INSERT INTO leagues 
            (league_name, tier, min_exp, max_exp, reward_multiplier)
            VALUES (%s, %s, %s, %s, %s)
        """, league)
    
    conn.commit()
    print(f"Seeded {len(comp_types)} competition types and {len(leagues)} leagues!")
    cur.close()
    return_connection(conn)


def seed_advanced_simulations():
    """Seed M&A, international expansion, and crisis scenarios."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM advanced_simulations")
    if cur.fetchone()['count'] > 0:
        print("Advanced simulations already seeded.")
        cur.close()
        return_connection(conn)
        return
    
    simulations = [
        ('Startup Acquisition', 'ma', 'A tech startup is for sale. Evaluate the deal.', 3,
         json.dumps({'target_company': 'TechStart Inc', 'asking_price': 5000000, 'revenue': 1200000, 'growth_rate': 40, 'employees': 25, 'tech_assets': ['AI Platform', 'Customer Data'], 'synergies': 800000}),
         json.dumps({'steps': ['Due diligence', 'Valuation', 'Negotiation', 'Integration planning']}), 400),
        ('Hostile Takeover Defense', 'ma', 'A competitor is attempting a hostile takeover. Defend your company.', 4,
         json.dumps({'acquirer': 'MegaCorp', 'offer_premium': 30, 'your_market_cap': 50000000, 'defense_options': ['Poison pill', 'White knight', 'Pac-man', 'Crown jewel']}),
         json.dumps({'optimal_defense': 'white_knight', 'negotiation_points': ['Price', 'Culture', 'Jobs']}), 500),
        ('European Expansion', 'international', 'Expand your business to the European market.', 3,
         json.dumps({'markets': [{'country': 'UK', 'market_size': 10000000, 'competition': 'high', 'regulations': 'moderate'}, {'country': 'Germany', 'market_size': 15000000, 'competition': 'medium', 'regulations': 'strict'}, {'country': 'Spain', 'market_size': 8000000, 'competition': 'low', 'regulations': 'moderate'}], 'budget': 2000000}),
         json.dumps({'considerations': ['Market size', 'Competition', 'Regulations', 'Cultural fit', 'Language']}), 350),
        ('Asia Pacific Entry', 'international', 'Enter the rapidly growing Asia Pacific market.', 4,
         json.dumps({'markets': [{'country': 'Japan', 'market_size': 20000000, 'entry_barrier': 'high', 'partner_required': True}, {'country': 'Singapore', 'market_size': 5000000, 'entry_barrier': 'low', 'partner_required': False}, {'country': 'India', 'market_size': 50000000, 'entry_barrier': 'medium', 'partner_required': True}]}),
         json.dumps({'entry_modes': ['Joint venture', 'Subsidiary', 'Franchise', 'Export']}), 400),
        ('Product Recall Crisis', 'crisis', 'A major product defect has been discovered affecting 10,000 customers.', 5,
         json.dumps({'affected_units': 10000, 'injury_reports': 5, 'media_coverage': 'high', 'stock_drop': 15, 'options': ['Full recall', 'Partial recall', 'Fix on request', 'Deny issue']}),
         json.dumps({'best_response': 'full_recall', 'communication_plan': ['Press release', 'Customer notification', 'Social media', 'Regulatory filing']}), 500),
        ('Data Breach Response', 'crisis', 'Hackers have stolen customer data. How do you respond?', 5,
         json.dumps({'records_exposed': 50000, 'data_types': ['Names', 'Emails', 'Payment info'], 'discovered_by': 'security_team', 'time_since_breach': 48}),
         json.dumps({'response_steps': ['Contain', 'Investigate', 'Notify', 'Remediate', 'Review']}), 550),
        ('Supply Chain Disruption', 'crisis', 'Your main supplier has gone bankrupt. Production stops in 2 weeks.', 4,
         json.dumps({'supplier_dependency': 70, 'alternative_suppliers': 3, 'inventory_days': 14, 'customer_commitments': 50000}),
         json.dumps({'mitigation_options': ['Emergency sourcing', 'Production pause', 'Customer communication', 'Inventory rationing']}), 400),
        ('Executive Scandal', 'crisis', 'Your CEO has been accused of misconduct. The board must act.', 4,
         json.dumps({'allegation_severity': 'high', 'media_attention': 'viral', 'stock_impact': -20, 'employee_morale': 'low', 'board_options': ['Suspend pending investigation', 'Immediate termination', 'Public defense', 'Quiet resignation']}),
         json.dumps({'recommended_action': 'suspend_pending_investigation', 'communication_priority': ['Board', 'Employees', 'Investors', 'Media']}), 450)
    ]
    
    for sim in simulations:
        cur.execute("""
            INSERT INTO advanced_simulations 
            (simulation_name, simulation_type, description, difficulty, scenario_data, solution_guide, exp_reward)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, sim)
    
    conn.commit()
    print(f"Seeded {len(simulations)} advanced simulations!")
    cur.close()
    return_connection(conn)


def seed_story_arcs():
    """Seed storyline quest system with narrative arcs and chapters."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM story_arcs")
    if cur.fetchone()['count'] > 0:
        print("Story arcs already seeded.")
        cur.close()
        return_connection(conn)
        return
    
    arcs = [
        ('The Restaurant Revival', 'A struggling restaurant needs your expertise to survive and thrive.', 'Modern', 5, 1, 500),
        ('The Factory Turnaround', 'An old factory faces closure. Can you modernize it?', 'Industrial', 5, 3, 600),
        ('The Startup Journey', 'From garage to IPO - build the next unicorn.', 'Modern', 7, 5, 800),
        ('The Franchise Empire', 'Expand a successful concept across the nation.', 'Modern', 6, 7, 750),
        ('The Crisis Commander', 'Multiple crises threaten your business empire.', 'Modern', 5, 10, 1000)
    ]
    
    for arc in arcs:
        cur.execute("""
            INSERT INTO story_arcs (arc_name, arc_description, world_type, total_chapters, unlock_level, exp_reward)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING arc_id
        """, arc)
        arc_id = cur.fetchone()['arc_id']
        
        if arc[0] == 'The Restaurant Revival':
            chapters = [
                (arc_id, 1, 'First Day Blues', 'You arrive at the restaurant to find it in worse shape than expected. The kitchen is outdated, staff morale is low, and customers are sparse.',
                 'Focus on quick wins - fix the menu', 'You streamline the menu, reducing costs. Staff appreciate the clarity.', 2,
                 'Invest in staff training first', 'The team feels valued. Service improves immediately.', 2,
                 'Launch a marketing blitz', 'Customers start coming, but the kitchen struggles with demand.', 3, 100, False),
                (arc_id, 2, 'The Competition Strikes', 'A new trendy restaurant opens across the street, stealing your customers.',
                 'Match their pricing aggressively', 'You retain customers but margins suffer. Need a new strategy.', 3,
                 'Differentiate with unique offerings', 'Your specialty dishes become local favorites.', 4,
                 'Form a partnership with them', 'Surprisingly, they agree. You share customers for events.', 4, 120, False),
                (arc_id, 3, 'Staff Rebellion', 'Your best chef threatens to quit, taking the kitchen team with them.',
                 'Offer a significant raise', 'The chef stays, but other staff expect the same treatment.', 4,
                 'Negotiate profit-sharing', 'The chef becomes invested in success. Innovation follows.', 5,
                 'Let them go and rebuild', 'Painful short-term, but you find passionate new talent.', 4, 140, False),
                (arc_id, 4, 'The Health Inspection', 'A surprise health inspection finds several violations.',
                 'Fix issues quickly and quietly', 'Problems solved, but at a cost. You pass the re-inspection.', 5,
                 'Use this as a catalyst for complete renovation', 'Expensive but you emerge with a modern, safe kitchen.', 5,
                 'Contest the findings', 'You win some battles but the negative press hurts business.', 5, 160, False),
                (arc_id, 5, 'The Grand Reopening', 'After all your efforts, its time for the grand reopening.',
                 'Host a celebrity chef event', 'The publicity is massive. You become a destination restaurant.', None,
                 'Focus on community appreciation night', 'Locals love you. Sustainable, loyal customer base.', None,
                 'Launch delivery and catering services', 'Multiple revenue streams secure your future.', None, 200, True)
            ]
            for ch in chapters:
                cur.execute("""
                    INSERT INTO story_chapters 
                    (arc_id, chapter_number, chapter_title, chapter_narrative, 
                     choice_a_text, choice_a_outcome, choice_a_next_chapter,
                     choice_b_text, choice_b_outcome, choice_b_next_chapter,
                     choice_c_text, choice_c_outcome, choice_c_next_chapter, exp_reward, is_finale)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, ch)
    
    conn.commit()
    print(f"Seeded {len(arcs)} story arcs with chapters!")
    cur.close()
    return_connection(conn)


def seed_mentorship_system():
    """Seed advisor skill trees and mentorship missions."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM advisor_skill_trees")
    if cur.fetchone()['count'] > 0:
        print("Mentorship system already seeded.")
        cur.close()
        return_connection(conn)
        return
    
    cur.execute("SELECT advisor_id, advisor_name, discipline_specialty FROM advisors LIMIT 5")
    advisors = cur.fetchall()
    
    for advisor in advisors:
        specialty = advisor['discipline_specialty'] or 'Business'
        skills = [
            (advisor['advisor_id'], f"{specialty} Basics", f"Learn the fundamentals of {specialty}", 1, None, 'exp_bonus', 5.0, 50),
            (advisor['advisor_id'], f"{specialty} Insights", f"Gain deeper insights into {specialty}", 2, None, 'exp_bonus', 10.0, 100),
            (advisor['advisor_id'], f"{specialty} Mastery", f"Master advanced {specialty} techniques", 3, None, 'exp_bonus', 15.0, 200),
            (advisor['advisor_id'], f"Network Access", f"Access {advisor['advisor_name']}'s professional network", 2, None, 'reputation_bonus', 5.0, 150),
            (advisor['advisor_id'], f"Secret Strategy", f"Learn {advisor['advisor_name']}'s secret success strategy", 3, None, 'cash_bonus', 10.0, 250)
        ]
        
        for skill in skills:
            cur.execute("""
                INSERT INTO advisor_skill_trees 
                (advisor_id, skill_name, skill_description, skill_tier, parent_skill_id, bonus_type, bonus_value, unlock_cost)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, skill)
        
        missions = [
            (advisor['advisor_id'], f"{advisor['advisor_name']}'s First Lesson", f"Complete your first challenge in {specialty}", 5, 'training',
             json.dumps(['Complete 1 scenario', 'Score at least 2 stars']), json.dumps({'exp': 100, 'affinity': 5}), 150),
            (advisor['advisor_id'], f"Prove Your Worth", f"Show {advisor['advisor_name']} you're serious about learning", 15, 'challenge',
             json.dumps(['Complete 5 scenarios', 'Maintain 3-star average']), json.dumps({'exp': 250, 'affinity': 10, 'skill_unlock': True}), 300),
            (advisor['advisor_id'], f"The Master Test", f"{advisor['advisor_name']} challenges you to demonstrate mastery", 30, 'mastery',
             json.dumps(['Complete all discipline scenarios', 'No failures']), json.dumps({'exp': 500, 'affinity': 20, 'title': 'Mentee of ' + advisor['advisor_name']}), 500)
        ]
        
        for mission in missions:
            cur.execute("""
                INSERT INTO mentorship_missions 
                (advisor_id, mission_name, mission_description, required_affinity, mission_type, objectives, rewards, exp_reward)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, mission)
    
    conn.commit()
    print("Mentorship system seeded!")
    cur.close()
    return_connection(conn)


def seed_business_network():
    """Seed business partners, joint ventures, and networking events."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM business_partners")
    if cur.fetchone()['count'] > 0:
        print("Business network already seeded.")
        cur.close()
        return_connection(conn)
        return
    
    partners = [
        ('TechVentures Capital', 'investor', 'Technology', 'A venture capital firm focused on tech startups.', 30, json.dumps({'investment_access': True, 'valuation_bonus': 10})),
        ('GlobalSupply Co', 'supplier', 'Manufacturing', 'International supply chain solutions provider.', 20, json.dumps({'cost_reduction': 5, 'reliability': 95})),
        ('MarketPro Agency', 'service', 'Marketing', 'Full-service digital marketing agency.', 15, json.dumps({'marketing_boost': 15, 'brand_awareness': 10})),
        ('LegalEagle LLP', 'service', 'Legal', 'Business law specialists with startup experience.', 25, json.dumps({'legal_protection': True, 'contract_review': True})),
        ('CloudScale Solutions', 'technology', 'Technology', 'Cloud infrastructure and scaling expertise.', 35, json.dumps({'tech_efficiency': 20, 'scalability': True})),
        ('EcoFriendly Packaging', 'supplier', 'Manufacturing', 'Sustainable packaging solutions.', 40, json.dumps({'sustainability_score': 25, 'cost_premium': 10})),
        ('TalentBridge HR', 'service', 'Human Resources', 'Executive search and HR consulting.', 30, json.dumps({'hiring_speed': 30, 'quality_bonus': 15})),
        ('FinanceFirst Consulting', 'service', 'Finance', 'CFO services and financial planning.', 45, json.dumps({'financial_accuracy': 20, 'tax_optimization': 10}))
    ]
    
    for p in partners:
        cur.execute("""
            INSERT INTO business_partners (partner_name, partner_type, industry, description, reputation_required, partnership_bonus)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING partner_id
        """, p)
        partner_id = cur.fetchone()['partner_id']
        
        ventures = [
            (f"Joint Project with {p[0]}", f"Collaborate with {p[0]} on a strategic initiative.", partner_id, 5000, 4, 3, 1.5, 150),
            (f"Expansion Deal", f"Partner with {p[0]} to expand into new markets.", partner_id, 15000, 8, 4, 2.0, 300)
        ]
        
        for v in ventures:
            cur.execute("""
                INSERT INTO joint_ventures (venture_name, venture_description, partner_id, investment_required, duration_weeks, risk_level, potential_return, exp_reward)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, v)
    
    events = [
        ('Industry Mixer', 'casual', 'Casual networking with local business professionals.', 50, 10, 2, 75),
        ('Startup Conference', 'conference', 'Annual gathering of entrepreneurs and investors.', 200, 30, 5, 150),
        ('Chamber of Commerce Dinner', 'formal', 'Formal networking with established business leaders.', 150, 40, 3, 125),
        ('Tech Meetup', 'casual', 'Monthly gathering of tech enthusiasts and founders.', 25, 15, 2, 60),
        ('Investor Demo Day', 'pitch', 'Present to a room full of potential investors.', 0, 50, 4, 200),
        ('Business Awards Gala', 'formal', 'Annual celebration of business excellence.', 500, 60, 6, 300),
        ('Mastermind Retreat', 'workshop', 'Intensive weekend with successful entrepreneurs.', 1000, 70, 8, 400)
    ]
    
    for e in events:
        cur.execute("""
            INSERT INTO networking_events (event_name, event_type, description, entry_cost, reputation_required, contacts_gained, exp_reward)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, e)
    
    conn.commit()
    print("Business network seeded!")
    cur.close()
    return_connection(conn)


def seed_industry_tracks():
    """Seed industry specialization tracks and certifications."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM industry_tracks")
    if cur.fetchone()['count'] > 0:
        print("Industry tracks already seeded.")
        cur.close()
        return_connection(conn)
        return
    
    tracks = [
        ('Technology Specialist', 'Technology', 'Master the tech industry from startups to enterprise.', 5, 500),
        ('Healthcare Expert', 'Healthcare', 'Navigate the complex healthcare business landscape.', 5, 600),
        ('Retail Strategist', 'Retail', 'Excel in retail from e-commerce to brick-and-mortar.', 5, 450),
        ('Manufacturing Pro', 'Manufacturing', 'Optimize production and supply chain operations.', 5, 550),
        ('Financial Services', 'Finance', 'Understand banking, insurance, and investment.', 5, 650),
        ('Hospitality Master', 'Hospitality', 'Lead in hotels, restaurants, and tourism.', 5, 500),
        ('Real Estate Developer', 'Real Estate', 'Build expertise in property development and management.', 5, 600),
        ('Media & Entertainment', 'Media', 'Create and manage content businesses.', 5, 500)
    ]
    
    for t in tracks:
        cur.execute("""
            INSERT INTO industry_tracks (track_name, industry, description, total_levels, base_exp_required)
            VALUES (%s, %s, %s, %s, %s) RETURNING track_id
        """, t)
        track_id = cur.fetchone()['track_id']
        
        certs = [
            (track_id, f"{t[1]} Fundamentals", f"Demonstrate basic {t[1].lower()} knowledge.", 1,
             json.dumps([{'q': f'What is the primary driver of success in {t[1].lower()}?', 'options': ['Innovation', 'Cost control', 'Customer focus', 'All of the above'], 'correct': 3}]),
             70, 200, 'cert_basic'),
            (track_id, f"{t[1]} Professional", f"Prove professional-level {t[1].lower()} competency.", 3,
             json.dumps([{'q': f'How do you measure ROI in {t[1].lower()} projects?', 'options': ['Revenue only', 'Profit/Investment', 'Customer growth', 'Market share'], 'correct': 1}]),
             75, 400, 'cert_pro'),
            (track_id, f"{t[1]} Expert", f"Achieve expert status in {t[1].lower()}.", 5,
             json.dumps([{'q': f'What advanced strategy works best for {t[1].lower()} growth?', 'options': ['Diversification', 'Focus', 'Innovation', 'Depends on context'], 'correct': 3}]),
             80, 600, 'cert_expert')
        ]
        
        for c in certs:
            cur.execute("""
                INSERT INTO industry_certifications (track_id, cert_name, cert_description, required_level, exam_questions, passing_score, exp_reward, badge_icon)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, c)
        
        challenges = [
            (track_id, f"{t[1]} Case Study", f"Analyze a real {t[1].lower()} business case.", 1, json.dumps({'type': 'case_study', 'time_limit': 30}), 100),
            (track_id, f"{t[1]} Strategy Challenge", f"Develop a strategy for a {t[1].lower()} company.", 3, json.dumps({'type': 'strategy', 'complexity': 'medium'}), 200),
            (track_id, f"{t[1]} Crisis Simulation", f"Handle a crisis in the {t[1].lower()} sector.", 5, json.dumps({'type': 'crisis', 'difficulty': 'hard'}), 350)
        ]
        
        for ch in challenges:
            cur.execute("""
                INSERT INTO industry_challenges (track_id, challenge_name, challenge_description, required_level, challenge_data, exp_reward)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, ch)
    
    conn.commit()
    print("Industry tracks seeded!")
    cur.close()
    return_connection(conn)


def seed_market_events():
    """Seed dynamic market events and global challenges."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM market_events")
    if cur.fetchone()['count'] > 0:
        print("Market events already seeded.")
        cur.close()
        return_connection(conn)
        return
    
    events = [
        ('Economic Boom', 'boom', 'The economy is thriving! Increased consumer spending.', json.dumps(['Retail', 'Hospitality', 'Technology']), 1.25, 14, True),
        ('Recession Warning', 'recession', 'Economic indicators suggest a slowdown ahead.', json.dumps(['All']), 0.80, 21, True),
        ('Tech Innovation Wave', 'opportunity', 'New technologies create business opportunities.', json.dumps(['Technology', 'Manufacturing']), 1.15, 10, False),
        ('Supply Chain Crisis', 'crisis', 'Global supply chains are disrupted.', json.dumps(['Manufacturing', 'Retail']), 0.85, 14, True),
        ('Consumer Confidence Surge', 'boom', 'Consumers are optimistic and spending more.', json.dumps(['Retail', 'Hospitality']), 1.20, 7, False),
        ('Regulatory Changes', 'neutral', 'New regulations affect business operations.', json.dumps(['Finance', 'Healthcare']), 0.95, 30, True),
        ('Talent War', 'challenge', 'Competition for skilled workers intensifies.', json.dumps(['Technology', 'Finance']), 1.10, 14, False),
        ('Sustainability Push', 'opportunity', 'Growing demand for eco-friendly businesses.', json.dumps(['Manufacturing', 'Retail']), 1.15, 21, True)
    ]
    
    for e in events:
        cur.execute("""
            INSERT INTO market_events (event_name, event_type, description, affected_industries, market_modifier, duration_days, is_global)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, e)
    
    cycles = [
        ('Growth Phase', 'expansion', 'Economic expansion with rising opportunities.', 1.15, 0.95, 1.25, 16),
        ('Peak Period', 'peak', 'Economy at its highest point. Competition intense.', 1.10, 1.10, 1.00, 8),
        ('Contraction', 'contraction', 'Economic slowdown begins. Caution advised.', 0.90, 1.05, 0.85, 12),
        ('Trough', 'recession', 'Economic bottom. Opportunities for prepared businesses.', 0.80, 1.15, 0.70, 8),
        ('Recovery', 'recovery', 'Economy begins to rebound. Early movers benefit.', 1.05, 1.00, 1.15, 12)
    ]
    
    for c in cycles:
        cur.execute("""
            INSERT INTO market_cycles (cycle_name, cycle_type, description, revenue_modifier, cost_modifier, opportunity_modifier, duration_weeks)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, c)
    
    global_challenges = [
        ('Community Business Week', 'Complete 1000 scenarios as a community.', 'scenarios', 1000, 0, 0, 5000),
        ('Innovation Marathon', 'Earn 50000 EXP collectively in Technology.', 'exp', 50000, 0, 0, 7500),
        ('Sustainability Initiative', 'Make 500 eco-friendly business decisions.', 'decisions', 500, 0, 0, 4000),
        ('Mentorship Movement', 'Complete 200 mentorship missions globally.', 'missions', 200, 0, 0, 6000)
    ]
    
    for gc in global_challenges:
        cur.execute("""
            INSERT INTO global_challenges (challenge_name, challenge_description, target_type, target_value, current_progress, participants, reward_pool)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, gc)
    
    news = [
        ('Tech Giant Announces Major Acquisition', 'Industry shakeup as leading tech company acquires competitor.', 'acquisition', 'Strategy', None, 'Analyze implications for your business strategy', 100),
        ('New Trade Tariffs Announced', 'Government implements new import tariffs affecting multiple industries.', 'regulation', 'Operations', None, 'Evaluate supply chain alternatives', 120),
        ('Consumer Spending Hits Record High', 'Holiday season sees unprecedented consumer spending.', 'market', 'Marketing', None, 'Capitalize on increased demand', 80),
        ('Labor Shortage Reaches Critical Level', 'Industries struggle to find qualified workers.', 'hr', 'Human Resources', None, 'Implement retention strategies', 110),
        ('Interest Rates Rise Again', 'Central bank raises interest rates for third consecutive time.', 'finance', 'Finance', None, 'Review debt and investment strategy', 130)
    ]
    
    for n in news:
        cur.execute("""
            INSERT INTO breaking_news (headline, news_content, news_type, affected_discipline, response_deadline, optimal_response, exp_reward)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, n)
    
    conn.commit()
    print("Market events seeded!")
    cur.close()
    return_connection(conn)


# ============================================================================
# PHASE 5 SEEDING FUNCTIONS
# ============================================================================

def seed_phase5_social():
    """Seed Phase 5A: Multiplayer & Social Features."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM coop_challenges")
    if cur.fetchone()['count'] > 0:
        print("Phase 5 social features already seeded.")
        cur.close()
        return_connection(conn)
        return
    
    coop_challenges = [
        ('Startup Sprint', 'Work together to launch a startup in 30 minutes.', 'duo', 2, 2, 2,
         json.dumps({'phases': 3, 'scenario_type': 'startup'}), 300, 100, 30),
        ('Crisis Management Team', 'Handle a company crisis as a team.', 'team', 3, 4, 3,
         json.dumps({'phases': 4, 'scenario_type': 'crisis'}), 400, 150, 45),
        ('Merger Negotiation', 'Negotiate a merger between two companies.', 'duo', 2, 2, 4,
         json.dumps({'phases': 5, 'scenario_type': 'negotiation'}), 500, 200, 60),
        ('Product Launch Party', 'Coordinate a successful product launch.', 'team', 2, 4, 2,
         json.dumps({'phases': 3, 'scenario_type': 'marketing'}), 350, 125, 40),
        ('Budget Battle', 'Compete to create the best budget proposal.', 'competitive', 2, 4, 3,
         json.dumps({'phases': 4, 'scenario_type': 'finance'}), 450, 175, 50)
    ]
    
    for c in coop_challenges:
        cur.execute("""
            INSERT INTO coop_challenges (challenge_name, challenge_description, challenge_type, min_players, max_players, difficulty, scenario_data, exp_reward, bonus_reward, time_limit_minutes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, c)
    
    coach_messages = [
        ('login', json.dumps({'days_inactive': 3}), "Welcome back! Ready to continue your business journey?", 'greeting', 1),
        ('achievement', json.dumps({'type': 'first_scenario'}), "Great job completing your first scenario! Keep going!", 'encouragement', 1),
        ('streak', json.dumps({'days': 7}), "Amazing 7-day streak! Your dedication is paying off.", 'milestone', 2),
        ('failure', json.dumps({'consecutive': 3}), "Don't give up! Try reviewing the training materials for this topic.", 'support', 3),
        ('level_up', json.dumps({'level': 5}), "Level 5! You're becoming a true business tycoon.", 'celebration', 2),
        ('weak_area', json.dumps({'discipline': 'any'}), "I noticed you could use some practice in this area. Want me to recommend some scenarios?", 'guidance', 2)
    ]
    
    for m in coach_messages:
        cur.execute("""
            INSERT INTO coach_messages (trigger_type, trigger_condition, message_text, message_category, priority)
            VALUES (%s, %s, %s, %s, %s)
        """, m)
    
    conn.commit()
    print("Phase 5 social features seeded!")
    cur.close()
    return_connection(conn)


def seed_phase5_seasons():
    """Seed Phase 5B: Seasonal Content & Live Events."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM seasons")
    if cur.fetchone()['count'] > 0:
        print("Phase 5 seasons already seeded.")
        cur.close()
        return_connection(conn)
        return
    
    from datetime import datetime, timedelta
    now = datetime.now()
    
    seasons = [
        ('Season 1: The Founders', 'startup', 'Build your empire from the ground up.', now, now + timedelta(days=90), True),
        ('Season 2: Global Expansion', 'international', 'Take your business worldwide.', now + timedelta(days=90), now + timedelta(days=180), False),
        ('Season 3: Innovation Era', 'technology', 'Lead the next tech revolution.', now + timedelta(days=180), now + timedelta(days=270), False)
    ]
    
    for s in seasons:
        cur.execute("""
            INSERT INTO seasons (season_name, season_theme, description, start_date, end_date, is_active)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING season_id
        """, s)
        season_id = cur.fetchone()['season_id']
        
        free_rewards = json.dumps([
            {'tier': 1, 'reward': 'exp', 'amount': 100},
            {'tier': 5, 'reward': 'gold', 'amount': 500},
            {'tier': 10, 'reward': 'title', 'name': 'Newcomer'},
            {'tier': 25, 'reward': 'avatar_frame', 'id': 1},
            {'tier': 50, 'reward': 'exclusive_scenario', 'id': 1}
        ])
        premium_rewards = json.dumps([
            {'tier': 1, 'reward': 'exp', 'amount': 200},
            {'tier': 5, 'reward': 'gold', 'amount': 1000},
            {'tier': 10, 'reward': 'exclusive_advisor', 'id': 1},
            {'tier': 25, 'reward': 'premium_equipment', 'id': 1},
            {'tier': 50, 'reward': 'legendary_title', 'name': 'Season Master'}
        ])
        
        cur.execute("""
            INSERT INTO battle_passes (season_id, pass_name, max_tier, premium_price, free_rewards, premium_rewards)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (season_id, f"{s[0]} Battle Pass", 50, 500, free_rewards, premium_rewards))
    
    seasonal_events = [
        ('Black Friday Bonanza', 'sales', 'Black Friday', 'Double rewards on all retail scenarios!', 
         now + timedelta(days=30), now + timedelta(days=32), 2.0, json.dumps({'bonus_disciplines': ['Marketing', 'Operations']})),
        ('Tax Season Challenge', 'challenge', 'Tax Season', 'Master accounting before the deadline!',
         now + timedelta(days=60), now + timedelta(days=75), 1.5, json.dumps({'bonus_disciplines': ['Finance']})),
        ('Summer Startup Sprint', 'competition', 'Summer', 'Launch the hottest new startup!',
         now + timedelta(days=120), now + timedelta(days=135), 1.75, json.dumps({'bonus_disciplines': ['Strategy']}))
    ]
    
    for e in seasonal_events:
        cur.execute("""
            INSERT INTO seasonal_events (event_name, event_type, event_theme, description, start_time, end_time, bonus_multiplier, special_rewards)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, e)
    
    limited_bosses = [
        ('The Corporate Raider', 'Legendary Business Tycoon', 'A ruthless corporate raider threatens to take over your company.',
         5, 10000, 10000, json.dumps({'phases': 5, 'attack_pattern': 'aggressive'}), 1000, 
         json.dumps({'title': 'Raider Slayer', 'equipment_id': 1}), now, now + timedelta(days=7)),
        ('The Regulatory Nightmare', 'Government Inspector', 'Navigate impossible compliance requirements.',
         4, 8000, 8000, json.dumps({'phases': 4, 'attack_pattern': 'tricky'}), 800,
         json.dumps({'title': 'Compliance Master', 'exp_bonus': 500}), now + timedelta(days=14), now + timedelta(days=21))
    ]
    
    for b in limited_bosses:
        cur.execute("""
            INSERT INTO limited_time_bosses (boss_name, boss_title, description, difficulty, health_points, current_hp, scenario_data, exp_reward, exclusive_rewards, available_from, available_until)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, b)
    
    conn.commit()
    print("Phase 5 seasons seeded!")
    cur.close()
    return_connection(conn)


def seed_phase5_content():
    """Seed Phase 5D: Content Expansion."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM expanded_worlds")
    if cur.fetchone()['count'] > 0:
        print("Phase 5 content already seeded.")
        cur.close()
        return_connection(conn)
        return
    
    worlds = [
        ('Pirate Trade Routes', 'adventure', 'Navigate treacherous seas of commerce in the Age of Sail.', 10, '#8B4513', 'pirate_backdrop.png', 'Trade negotiations, risk calculation, crew management'),
        ('Space Commerce', 'scifi', 'Build an interstellar trading empire across the galaxy.', 15, '#0F0F3F', 'space_backdrop.png', 'Resource mining, alien diplomacy, tech research'),
        ('Wild West Business', 'western', 'Strike it rich in the frontier towns of the Old West.', 8, '#DAA520', 'western_backdrop.png', 'Gold rush economics, railroad investment, saloon management'),
        ('Ancient Empire', 'historical', 'Manage trade in ancient civilizations.', 12, '#CD853F', 'ancient_backdrop.png', 'Caravan routes, temple economics, conquest funding')
    ]
    
    for w in worlds:
        cur.execute("""
            INSERT INTO expanded_worlds (world_name, world_type, description, unlock_level, theme_color, backdrop_image, special_mechanics)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, w)
    
    case_studies = [
        ('The Fall of BlockBuster', 'BlockBuster', 'Entertainment', 'Strategy', 4,
         'BlockBuster was once the undisputed king of video rental, with over 9,000 stores worldwide...',
         'Analyze why BlockBuster failed to adapt to streaming technology and how Netflix succeeded.',
         json.dumps(['Understand disruption', 'Recognize pivot opportunities', 'Value innovation']),
         'BlockBuster had multiple opportunities to acquire Netflix but declined. Their failure to embrace digital...',
         json.dumps(['Adapt or die', 'Customer convenience wins', 'Legacy assets can be liabilities']), 400, False),
        ('Apple Store Revolution', 'Apple', 'Retail', 'Marketing', 3,
         'When Apple announced its retail stores in 2001, critics predicted failure...',
         'Examine how Apple created a revolutionary retail experience that defied conventional wisdom.',
         json.dumps(['Customer experience design', 'Brand building', 'Premium positioning']),
         'Apple focused on experience over sales metrics, using stores as brand temples...',
         json.dumps(['Experience sells', 'Train for service not sales', 'Location matters']), 350, False),
        ('Toyota Production System', 'Toyota', 'Manufacturing', 'Operations', 4,
         'Toyota transformed manufacturing with its innovative production system...',
         'Learn how lean manufacturing principles created one of the most efficient companies in the world.',
         json.dumps(['Just-in-time inventory', 'Continuous improvement', 'Employee empowerment']),
         'The Toyota Production System eliminated waste through kaizen and kanban...',
         json.dumps(['Small improvements compound', 'Respect workers', 'Quality at source']), 400, False),
        ('Zappos Culture', 'Zappos', 'Retail', 'Human Resources', 3,
         'Zappos built a billion-dollar company on an unusual foundation: employee happiness...',
         'Discover how Zappos prioritized culture to create exceptional customer service.',
         json.dumps(['Culture building', 'Employee engagement', 'Service excellence']),
         'Zappos offered new employees $2000 to quit, ensuring only committed people stayed...',
         json.dumps(['Culture is strategy', 'Happy employees = happy customers', 'Values over profits']), 350, False)
    ]
    
    for c in case_studies:
        cur.execute("""
            INSERT INTO case_studies (case_title, company_name, industry, discipline, difficulty, case_background, case_challenge, learning_objectives, solution_analysis, key_takeaways, exp_reward, is_premium)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, c)
    
    guest_mentors = [
        ('Sarah Chen', 'Serial Entrepreneur & Investor', 'TechVentures Capital', 
         'Founded 3 successful startups before age 35. Now helps the next generation of founders.',
         json.dumps(['Startup Strategy', 'Fundraising', 'Product-Market Fit']), 'sarah_chen.png',
         json.dumps([{'id': 1, 'name': 'The Pivot Decision'}]), 'Complete 10 Strategy scenarios'),
        ('Marcus Williams', 'Former Fortune 500 CFO', 'Williams Consulting',
         'Led finance at three Fortune 500 companies. Expert in turnarounds and growth financing.',
         json.dumps(['Financial Strategy', 'M&A', 'Capital Markets']), 'marcus_williams.png',
         json.dumps([{'id': 2, 'name': 'The Acquisition'}]), 'Complete all Finance training'),
        ('Elena Rodriguez', 'Marketing Maven', 'Global Brands Inc.',
         'Built iconic brands across 50 countries. Pioneer in digital and experiential marketing.',
         json.dumps(['Brand Building', 'Global Marketing', 'Digital Strategy']), 'elena_rodriguez.png',
         json.dumps([{'id': 3, 'name': 'Going Viral'}]), 'Reach Marketing Level 8')
    ]
    
    for m in guest_mentors:
        cur.execute("""
            INSERT INTO guest_mentors (mentor_name, mentor_title, company, bio, expertise_areas, avatar_image, special_scenarios, unlock_requirement)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, m)
    
    advanced_disciplines = [
        ('Marketing', 'Growth Hacking', 'Master viral growth and unconventional marketing tactics.', 10, 15, 
         json.dumps(['Viral loops', 'A/B testing', 'Conversion optimization', 'Referral systems'])),
        ('Finance', 'Private Equity', 'Lead leveraged buyouts and portfolio company turnarounds.', 10, 15,
         json.dumps(['LBO modeling', 'Due diligence', 'Value creation', 'Exit strategies'])),
        ('Operations', 'Supply Chain Mastery', 'Optimize global supply chains and logistics.', 10, 15,
         json.dumps(['Global logistics', 'Supplier networks', 'Inventory optimization', 'Risk mitigation'])),
        ('Strategy', 'Corporate Development', 'Lead M&A, partnerships, and corporate strategy.', 10, 15,
         json.dumps(['M&A strategy', 'Integration planning', 'Synergy realization', 'Strategic alliances'])),
        ('Human Resources', 'Organizational Design', 'Shape culture and structure for high performance.', 10, 15,
         json.dumps(['Culture engineering', 'Change management', 'Talent systems', 'Leadership development'])),
        ('Legal', 'Corporate Governance', 'Master boardroom dynamics and regulatory strategy.', 10, 15,
         json.dumps(['Board relations', 'Compliance strategy', 'Risk governance', 'Shareholder activism']))
    ]
    
    for d in advanced_disciplines:
        cur.execute("""
            INSERT INTO advanced_disciplines (base_discipline, advanced_name, description, unlock_level, max_level, special_skills)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, d)
    
    conn.commit()
    print("Phase 5 content seeded!")
    cur.close()
    return_connection(conn)


def seed_mentorship_modules():
    """Seed mentorship learning modules that teach concepts before scenarios."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM mentorship_modules")
    if cur.fetchone()['count'] > 0:
        print("Mentorship modules already seeded.")
        cur.close()
        return_connection(conn)
        return
    
    modules = [
        {
            'module_code': 'FINANCE_L1_ACCOUNTING_EQ',
            'module_title': 'The Accounting Equation',
            'discipline': 'Finance',
            'required_level': 1,
            'theory_content': '''<p>Every business transaction follows one fundamental rule: <strong>Assets = Liabilities + Equity</strong></p>
<p>This is the foundation of all accounting. Let's break it down:</p>
<ul>
<li><strong>Assets</strong> - Everything your business OWNS (cash, equipment, inventory, buildings)</li>
<li><strong>Liabilities</strong> - Everything your business OWES (loans, accounts payable, mortgages)</li>
<li><strong>Equity</strong> - What's left over for the owners (Assets minus Liabilities)</li>
</ul>
<p>Think of it like your personal finances: If you have a $300,000 house (asset) with a $200,000 mortgage (liability), your equity is $100,000.</p>''',
            'key_concepts': '''<strong>The equation must ALWAYS balance.</strong> Every transaction affects at least two accounts. If you buy equipment with cash, assets stay the same (equipment up, cash down). If you take a loan to buy equipment, both assets AND liabilities increase.''',
            'formulas': '''<strong>Assets = Liabilities + Equity</strong><br><br>
Rearranged: <strong>Equity = Assets - Liabilities</strong><br><br>
Example: $50,000 Assets - $20,000 Loan = $30,000 Equity''',
            'real_world_example': '''A restaurant has: $50,000 in cash and equipment (assets), a $20,000 bank loan (liability). Using the equation: Equity = $50,000 - $20,000 = <strong>$30,000</strong>. This means the owner truly "owns" $30,000 worth of the business.''',
            'practice_question': 'A business has $80,000 in assets and $30,000 in liabilities. What is the equity?',
            'practice_answer': '$50,000',
            'practice_explanation': 'Equity = Assets - Liabilities = $80,000 - $30,000 = $50,000. The owners have $50,000 stake in the business.',
            'estimated_minutes': 5
        },
        {
            'module_code': 'FINANCE_L2_REVENUE_EXPENSE',
            'module_title': 'Revenue vs Expenses',
            'discipline': 'Finance',
            'required_level': 2,
            'theory_content': '''<p><strong>Revenue</strong> is money coming IN from selling goods or services.</p>
<p><strong>Expenses</strong> are costs going OUT to operate your business.</p>
<p><strong>Profit = Revenue - Expenses</strong></p>
<p>Understanding this difference is crucial for business success. High revenue means nothing if expenses eat it all up!</p>''',
            'key_concepts': '''<strong>Revenue</strong> includes: sales, service fees, interest income, rent received<br><br>
<strong>Expenses</strong> include: wages, rent paid, utilities, supplies, marketing costs, insurance''',
            'formulas': '''<strong>Net Profit = Total Revenue - Total Expenses</strong><br><br>
<strong>Profit Margin = (Net Profit / Revenue) x 100%</strong>''',
            'real_world_example': '''A restaurant earns $40,000 in monthly sales. Expenses: $15,000 ingredients, $8,000 wages, $5,000 rent. Profit = $40,000 - $28,000 = <strong>$12,000</strong>. Profit margin = 30%.''',
            'practice_question': 'Revenue is $60,000, expenses are $45,000. What is the profit?',
            'practice_answer': '$15,000',
            'practice_explanation': 'Profit = Revenue - Expenses = $60,000 - $45,000 = $15,000',
            'estimated_minutes': 5
        },
        {
            'module_code': 'MARKETING_L1_FOUR_PS',
            'module_title': 'The 4 Ps of Marketing',
            'discipline': 'Marketing',
            'required_level': 1,
            'theory_content': '''<p>The <strong>Marketing Mix</strong> consists of 4 key elements:</p>
<ul>
<li><strong>Product</strong> - What you're selling (features, quality, design)</li>
<li><strong>Price</strong> - How much you charge (strategy, discounts)</li>
<li><strong>Place</strong> - Where customers can buy it (channels, locations)</li>
<li><strong>Promotion</strong> - How you communicate (advertising, PR, social media)</li>
</ul>
<p>All four must work together for marketing success!</p>''',
            'key_concepts': '''Each P must align with your target customer. A luxury product needs premium pricing, upscale locations, and sophisticated promotion. A budget product needs low prices, convenient access, and value-focused messaging.''',
            'formulas': None,
            'real_world_example': '''Apple iPhone: Premium <strong>Product</strong> (innovative design), Premium <strong>Price</strong> ($999+), Selective <strong>Place</strong> (Apple Stores, carriers), Aspirational <strong>Promotion</strong> (lifestyle advertising).''',
            'practice_question': 'Which of the 4 Ps refers to where and how customers buy your product?',
            'practice_answer': 'Place',
            'practice_explanation': 'Place refers to distribution channels and locations where customers can access your product.',
            'estimated_minutes': 4
        },
        {
            'module_code': 'OPERATIONS_L1_SUPPLY_CHAIN',
            'module_title': 'Supply Chain Basics',
            'discipline': 'Operations',
            'required_level': 1,
            'theory_content': '''<p>A <strong>supply chain</strong> is the network of activities to deliver a product from raw materials to the customer.</p>
<p>Key stages:</p>
<ul>
<li><strong>Sourcing</strong> - Finding and selecting suppliers</li>
<li><strong>Manufacturing</strong> - Creating the product</li>
<li><strong>Distribution</strong> - Moving products to where they're sold</li>
<li><strong>Delivery</strong> - Getting products to customers</li>
</ul>''',
            'key_concepts': '''<strong>Lead time</strong> is how long it takes from ordering to receiving goods. <strong>Safety stock</strong> is extra inventory to prevent stockouts. Managing both is crucial for smooth operations.''',
            'formulas': '''<strong>Reorder Point = (Daily Usage x Lead Time) + Safety Stock</strong><br><br>
Example: Use 10 units/day, 5-day lead time, 20 safety stock = Reorder at 70 units''',
            'real_world_example': '''A coffee shop uses 50 lbs of beans weekly, supplier takes 3 days to deliver, keeps 20 lbs safety stock. Reorder point = (50/7 x 3) + 20 = about <strong>41 lbs</strong>''',
            'practice_question': 'Daily usage is 20 units, lead time is 4 days, safety stock is 30 units. What is the reorder point?',
            'practice_answer': '110',
            'practice_explanation': 'Reorder Point = (20 x 4) + 30 = 80 + 30 = 110 units',
            'estimated_minutes': 5
        },
        {
            'module_code': 'HR_L1_HIRING',
            'module_title': 'Hiring the Right People',
            'discipline': 'Human Resources',
            'required_level': 1,
            'theory_content': '''<p>Hiring is one of the most important business decisions. The wrong hire can cost 2-3x their salary!</p>
<p>Key steps in the hiring process:</p>
<ul>
<li><strong>Job Analysis</strong> - Define what the role needs</li>
<li><strong>Sourcing</strong> - Find candidates (job boards, referrals, recruiters)</li>
<li><strong>Screening</strong> - Review resumes and applications</li>
<li><strong>Interviewing</strong> - Assess skills, culture fit, potential</li>
<li><strong>Selection</strong> - Make an offer to the best candidate</li>
</ul>''',
            'key_concepts': '''<strong>Skills</strong> can be taught, but <strong>attitude</strong> and <strong>culture fit</strong> are harder to change. Look for both technical abilities and soft skills like communication and teamwork.''',
            'formulas': None,
            'real_world_example': '''A startup hiring a developer: They need coding skills (technical), but also creativity and willingness to wear multiple hats (soft skills). They prioritize a growth mindset over years of experience.''',
            'practice_question': 'What is typically harder to change in an employee - skills or attitude?',
            'practice_answer': 'attitude',
            'practice_explanation': 'Skills can be trained, but attitude and personality are more ingrained. This is why many companies "hire for attitude, train for skills."',
            'estimated_minutes': 4
        },
        {
            'module_code': 'STRATEGY_L1_SWOT',
            'module_title': 'SWOT Analysis',
            'discipline': 'Strategy',
            'required_level': 1,
            'theory_content': '''<p><strong>SWOT Analysis</strong> helps you understand your competitive position:</p>
<ul>
<li><strong>S</strong>trengths - What you do well (internal)</li>
<li><strong>W</strong>eaknesses - Where you struggle (internal)</li>
<li><strong>O</strong>pportunities - External factors you can exploit</li>
<li><strong>T</strong>hreats - External risks to your business</li>
</ul>
<p>Strengths and Weaknesses are INTERNAL (you can control). Opportunities and Threats are EXTERNAL (you must respond to).</p>''',
            'key_concepts': '''Use strengths to capitalize on opportunities. Address weaknesses that could be exploited by threats. A good strategy aligns internal capabilities with external conditions.''',
            'formulas': None,
            'real_world_example': '''A local bakery: <strong>Strength</strong> - unique recipes. <strong>Weakness</strong> - limited parking. <strong>Opportunity</strong> - growing demand for artisan bread. <strong>Threat</strong> - new grocery store bakery opening nearby.''',
            'practice_question': 'Are "Opportunities" internal or external factors?',
            'practice_answer': 'external',
            'practice_explanation': 'Opportunities and Threats are external factors in the environment. Strengths and Weaknesses are internal to your organization.',
            'estimated_minutes': 4
        },
        {
            'module_code': 'LEGAL_L1_CONTRACTS',
            'module_title': 'Contract Basics',
            'discipline': 'Legal',
            'required_level': 1,
            'theory_content': '''<p>A <strong>contract</strong> is a legally binding agreement. For a contract to be valid, it needs:</p>
<ul>
<li><strong>Offer</strong> - One party proposes terms</li>
<li><strong>Acceptance</strong> - Other party agrees to the terms</li>
<li><strong>Consideration</strong> - Something of value exchanged (money, services)</li>
<li><strong>Capacity</strong> - Both parties can legally enter the contract</li>
<li><strong>Legality</strong> - The contract is for legal purposes</li>
</ul>''',
            'key_concepts': '''<strong>Always get it in writing!</strong> Verbal contracts are hard to enforce. Key contract terms include: payment terms, delivery dates, warranties, termination clauses, and dispute resolution.''',
            'formulas': None,
            'real_world_example': '''A freelancer agrees to build a website for $5,000. The contract specifies: deliverables, timeline, payment schedule, revision limits, and what happens if either party wants to cancel.''',
            'practice_question': 'What is "consideration" in a contract?',
            'practice_answer': 'something of value exchanged',
            'practice_explanation': 'Consideration means each party gives something of value - typically money for goods/services. Without consideration, there is no contract.',
            'estimated_minutes': 5
        }
    ]
    
    for m in modules:
        cur.execute("""
            INSERT INTO mentorship_modules 
            (module_code, module_title, discipline, required_level, theory_content, key_concepts, 
             formulas, real_world_example, practice_question, practice_answer, practice_explanation, estimated_minutes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (m['module_code'], m['module_title'], m['discipline'], m['required_level'],
              m['theory_content'], m['key_concepts'], m['formulas'], m['real_world_example'],
              m['practice_question'], m['practice_answer'], m['practice_explanation'], m['estimated_minutes']))
    
    conn.commit()
    
    # Link mentorship modules to scenarios
    # Get module IDs we just created
    cur.execute("SELECT module_id, module_code FROM mentorship_modules")
    modules_map = {row['module_code']: row['module_id'] for row in cur.fetchall()}
    
    # Link Finance Level 1 scenarios to the Accounting Equation module
    if 'FINANCE_L1_ACCOUNTING_EQ' in modules_map:
        cur.execute("""
            SELECT scenario_id FROM scenario_master 
            WHERE discipline = 'Finance' AND required_level = 1 
            AND scenario_title LIKE 'L1:%'
            LIMIT 3
        """)
        finance_scenarios = cur.fetchall()
        for row in finance_scenarios:
            cur.execute("""
                INSERT INTO scenario_mentorship (scenario_id, module_id, is_required)
                VALUES (%s, %s, TRUE)
                ON CONFLICT (scenario_id, module_id) DO NOTHING
            """, (row['scenario_id'], modules_map['FINANCE_L1_ACCOUNTING_EQ']))
    
    # Link Marketing Level 1 scenarios to 4 Ps module
    if 'MARKETING_L1_FOUR_PS' in modules_map:
        cur.execute("""
            SELECT scenario_id FROM scenario_master 
            WHERE discipline = 'Marketing' AND required_level = 1
            LIMIT 3
        """)
        marketing_scenarios = cur.fetchall()
        for row in marketing_scenarios:
            cur.execute("""
                INSERT INTO scenario_mentorship (scenario_id, module_id, is_required)
                VALUES (%s, %s, TRUE)
                ON CONFLICT (scenario_id, module_id) DO NOTHING
            """, (row['scenario_id'], modules_map['MARKETING_L1_FOUR_PS']))
    
    conn.commit()
    cur.close()
    return_connection(conn)
    print("Mentorship modules seeded.")


def seed_mentor_trials():
    """Seed RPG-themed knowledge quizzes with mentor characters."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM mentor_trials")
    if cur.fetchone()['count'] > 0:
        print("Mentor trials already seeded.")
        cur.close()
        return_connection(conn)
        return
    
    trials = [
        {
            'trial_code': 'FINANCE_LEDGER_TRIAL',
            'trial_name': 'The Ledger Master\'s Challenge',
            'mentor_name': 'Eldric the Accountant',
            'mentor_title': 'Keeper of the Golden Ledger',
            'mentor_avatar': 'mentor_sage',
            'discipline': 'Finance',
            'difficulty': 1,
            'story_intro': 'You enter the dusty halls of the Treasury Guild. An elderly man with spectacles peers at you from behind towering stacks of ledgers. "Ah, a young merchant seeking wisdom! Before I share the secrets of gold, you must prove your understanding of the sacred balance sheets..."',
            'story_success': '"Magnificent!" Eldric stamps your merchant license with a golden seal. "You have mastered the fundamentals. The Guild recognizes you as a true keeper of accounts. May your ledgers always balance!"',
            'story_fail': 'Eldric shakes his head slowly. "The numbers... they do not add up. Return when you have studied the ancient texts more carefully. The Treasury Guild demands precision!"',
            'time_limit_seconds': 300,
            'passing_score': 70,
            'exp_reward': 75,
            'gold_reward': 150,
            'badge_code': 'BADGE_LEDGER_APPRENTICE'
        },
        {
            'trial_code': 'MARKETING_BAZAAR_TRIAL',
            'trial_name': 'The Bazaar Merchant\'s Test',
            'mentor_name': 'Zara the Merchant Queen',
            'mentor_title': 'Master of the Four Markets',
            'mentor_avatar': 'mentor_merchant',
            'discipline': 'Marketing',
            'difficulty': 1,
            'story_intro': 'The Grand Bazaar bustles with activity. A woman draped in silk and gold gestures you to her ornate tent. "I am Zara, and I have sold everything from dragon scales to enchanted bread. To earn your place in my trade network, prove you understand the Four Pillars of Commerce!"',
            'story_success': 'Zara applauds and hands you a merchant\'s ring. "Brilliant! You understand Product, Price, Place, and Promotion. Welcome to the Merchant\'s Guild - may your sales be legendary!"',
            'story_fail': '"Hmm, your understanding is incomplete," Zara says with a knowing smile. "Return to the market stalls and observe. Watch how the masters sell - then come back and try again."',
            'time_limit_seconds': 300,
            'passing_score': 70,
            'exp_reward': 75,
            'gold_reward': 150,
            'badge_code': 'BADGE_BAZAAR_TRADER'
        },
        {
            'trial_code': 'OPERATIONS_FORGE_TRIAL',
            'trial_name': 'The Forge Master\'s Exam',
            'mentor_name': 'Grimlock the Smith',
            'mentor_title': 'Grand Master of the Iron Guild',
            'mentor_avatar': 'mentor_craftsman',
            'discipline': 'Operations',
            'difficulty': 1,
            'story_intro': 'Heat radiates from the massive forge. A mountain of a man, arms like tree trunks, sets down his hammer. "You want to run a business? First, you must understand HOW things are made. Efficiency is survival. Waste is death. Show me you grasp the ways of the forge!"',
            'story_success': 'Grimlock grins beneath his soot-covered beard. "HAH! You think like a true craftsman! Take this badge - you\'ve earned the respect of the Iron Guild. Now go build something worthy!"',
            'story_fail': 'Grimlock sighs and returns to his anvil. "Your thinking is sloppy, like cheap iron. Come back when you understand that every second wasted is gold lost."',
            'time_limit_seconds': 300,
            'passing_score': 70,
            'exp_reward': 75,
            'gold_reward': 150,
            'badge_code': 'BADGE_FORGE_APPRENTICE'
        }
    ]
    
    for t in trials:
        cur.execute("""
            INSERT INTO mentor_trials (trial_code, trial_name, mentor_name, mentor_title, mentor_avatar,
                discipline, difficulty, story_intro, story_success, story_fail, time_limit_seconds,
                passing_score, exp_reward, gold_reward, badge_code)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (trial_code) DO NOTHING
            RETURNING trial_id
        """, (t['trial_code'], t['trial_name'], t['mentor_name'], t['mentor_title'], t['mentor_avatar'],
              t['discipline'], t['difficulty'], t['story_intro'], t['story_success'], t['story_fail'],
              t['time_limit_seconds'], t['passing_score'], t['exp_reward'], t['gold_reward'], t['badge_code']))
    
    conn.commit()
    
    # Add questions for each trial
    questions_data = {
        'FINANCE_LEDGER_TRIAL': [
            {'text': 'In the ancient art of bookkeeping, what must always remain equal?', 'context': 'Eldric points to a massive balance scale on his desk.', 'a': 'Revenue and Expenses', 'b': 'Assets and Liabilities + Equity', 'c': 'Cash and Inventory', 'd': 'Profit and Loss', 'correct': 'b', 'explanation': 'The fundamental accounting equation: Assets = Liabilities + Owner\'s Equity. This sacred balance must always hold true!'},
            {'text': 'A merchant buys goods for 100 gold and sells them for 150 gold. What is their gross profit?', 'context': 'Eldric slides an abacus towards you.', 'a': '100 gold', 'b': '150 gold', 'c': '50 gold', 'd': '250 gold', 'correct': 'c', 'explanation': 'Gross Profit = Revenue - Cost of Goods Sold = 150 - 100 = 50 gold'},
            {'text': 'Which scroll records ALL transactions as they happen, in order of occurrence?', 'context': 'Eldric gestures to shelves of leather-bound books.', 'a': 'The General Ledger', 'b': 'The Trial Balance', 'c': 'The Journal', 'd': 'The Balance Sheet', 'correct': 'c', 'explanation': 'The Journal (or Book of Original Entry) records all transactions chronologically before posting to ledger accounts.'},
            {'text': 'When a merchant receives payment from a customer, which account INCREASES?', 'context': 'Coins clink as they hit the counting table.', 'a': 'Accounts Payable', 'b': 'Cash', 'c': 'Expenses', 'd': 'Liabilities', 'correct': 'b', 'explanation': 'When receiving payment, Cash (an asset) increases. Accounts Receivable would decrease if the payment was for a previous sale on credit.'},
            {'text': 'What document shows a business\'s financial position at a specific moment in time?', 'context': 'Eldric pulls out an official-looking parchment.', 'a': 'Income Statement', 'b': 'Cash Flow Statement', 'c': 'Balance Sheet', 'd': 'Budget Report', 'correct': 'c', 'explanation': 'The Balance Sheet (Statement of Financial Position) shows assets, liabilities, and equity at a specific date - a "snapshot" of the business.'}
        ],
        'MARKETING_BAZAAR_TRIAL': [
            {'text': 'What are the Four Pillars of Commerce that every merchant must master?', 'context': 'Zara holds up four golden tokens.', 'a': 'People, Profit, Planet, Purpose', 'b': 'Product, Price, Place, Promotion', 'c': 'Quality, Speed, Cost, Service', 'd': 'Buy, Sell, Trade, Barter', 'correct': 'b', 'explanation': 'The 4 Ps of Marketing: Product (what you sell), Price (how much), Place (where), and Promotion (how you tell people).'},
            {'text': 'A merchant lowers prices to attract more customers. What strategy is this?', 'context': 'A rival stall slashes their prices dramatically.', 'a': 'Premium pricing', 'b': 'Penetration pricing', 'c': 'Price skimming', 'd': 'Bundle pricing', 'correct': 'b', 'explanation': 'Penetration pricing sets low initial prices to rapidly gain market share and attract price-sensitive customers.'},
            {'text': 'Understanding WHO will buy your goods is called identifying your...?', 'context': 'Zara gestures to different groups of shoppers in the bazaar.', 'a': 'Competition', 'b': 'Target market', 'c': 'Supply chain', 'd': 'Inventory', 'correct': 'b', 'explanation': 'Your target market is the specific group of customers you aim to serve with your products or services.'},
            {'text': 'What makes your goods different and better than your competitors\'?', 'context': 'Two identical-looking stalls sit side by side, but one has a crowd.', 'a': 'Market share', 'b': 'Unique selling proposition', 'c': 'Break-even point', 'd': 'Operating costs', 'correct': 'b', 'explanation': 'Your USP (Unique Selling Proposition) is what sets you apart and gives customers a reason to choose you over competitors.'},
            {'text': 'Word spreads about your excellent goods through satisfied customers. This is...?', 'context': 'You overhear shoppers recommending your stall to friends.', 'a': 'Paid advertising', 'b': 'Word-of-mouth marketing', 'c': 'Direct sales', 'd': 'Wholesale', 'correct': 'b', 'explanation': 'Word-of-mouth marketing happens when customers voluntarily share positive experiences, often the most trusted form of promotion.'}
        ],
        'OPERATIONS_FORGE_TRIAL': [
            {'text': 'When a craftsman produces more items per hour, what has improved?', 'context': 'Grimlock forges three swords in the time it used to take for one.', 'a': 'Quality', 'b': 'Productivity', 'c': 'Inventory', 'd': 'Revenue', 'correct': 'b', 'explanation': 'Productivity measures output per unit of input (labor, time, resources). Higher productivity = more efficient operations.'},
            {'text': 'Keeping extra materials "just in case" represents what type of inventory?', 'context': 'Grimlock points to a shelf of backup iron ingots.', 'a': 'Work-in-progress', 'b': 'Finished goods', 'c': 'Safety stock', 'd': 'Raw waste', 'correct': 'c', 'explanation': 'Safety stock is extra inventory kept as a buffer against unexpected demand or supply disruptions.'},
            {'text': 'The path through production that takes the LONGEST time is called the...?', 'context': 'Grimlock draws a diagram showing interconnected forge stations.', 'a': 'Supply chain', 'b': 'Critical path', 'c': 'Assembly line', 'd': 'Quality control', 'correct': 'b', 'explanation': 'The critical path is the longest sequence of dependent tasks - it determines the minimum project completion time.'},
            {'text': 'Reducing waste and continuously improving processes is known as...?', 'context': 'Grimlock shows you how he reuses metal scraps.', 'a': 'Mass production', 'b': 'Outsourcing', 'c': 'Lean manufacturing', 'd': 'Vertical integration', 'correct': 'c', 'explanation': 'Lean manufacturing focuses on eliminating waste, improving efficiency, and creating more value with fewer resources.'},
            {'text': 'When demand exceeds what you can produce, you have a...?', 'context': 'Orders pile up faster than Grimlock can forge.', 'a': 'Surplus', 'b': 'Bottleneck', 'c': 'Profit margin', 'd': 'Market share', 'correct': 'b', 'explanation': 'A bottleneck is a constraint that limits output capacity, creating a backup in the production process.'}
        ]
    }
    
    for trial_code, questions in questions_data.items():
        cur.execute("SELECT trial_id FROM mentor_trials WHERE trial_code = %s", (trial_code,))
        result = cur.fetchone()
        if result:
            trial_id = result['trial_id']
            for i, q in enumerate(questions):
                cur.execute("""
                    INSERT INTO trial_questions (trial_id, question_text, question_context, option_a, option_b,
                        option_c, option_d, correct_answer, explanation, points, question_order)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 20, %s)
                """, (trial_id, q['text'], q['context'], q['a'], q['b'], q['c'], q.get('d'), q['correct'], q['explanation'], i+1))
    
    conn.commit()
    cur.close()
    return_connection(conn)
    print("Mentor trials seeded.")


def seed_merchant_puzzles():
    """Seed interactive business calculator challenges."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM merchant_puzzles")
    if cur.fetchone()['count'] > 0:
        print("Merchant puzzles already seeded.")
        cur.close()
        return_connection(conn)
        return
    
    puzzles = [
        {
            'puzzle_code': 'PROFIT_MARGIN_POTION',
            'puzzle_name': 'The Potion Seller\'s Profit',
            'merchant_name': 'Alchemist Vera',
            'merchant_title': 'Master of Potions & Profits',
            'merchant_avatar': 'merchant_alchemist',
            'discipline': 'Finance',
            'puzzle_type': 'profit_margin',
            'difficulty': 1,
            'story_intro': 'Vera the Alchemist sighs over her bubbling cauldrons. "Young entrepreneur! I sell healing potions for 25 gold each, but ingredients cost me 15 gold per potion. The guild masters demand I know my profit margins before expanding. Can you calculate them for me?"',
            'story_success': '"By the ancient formulae! You\'ve mastered the calculation!" Vera hands you a glowing vial. "Take this bonus gold - you\'ve earned it with your sharp mind!"',
            'challenge_data': '{"cost": 15, "price": 25, "correct_margin": 40, "tolerance": 1, "hint": "Profit Margin = ((Price - Cost) / Price) x 100"}',
            'formula_hint': 'Profit Margin (%) = ((Selling Price - Cost) / Selling Price) × 100',
            'time_limit_seconds': 120,
            'exp_reward': 50,
            'gold_reward': 100
        },
        {
            'puzzle_code': 'BREAKEVEN_BAKERY',
            'puzzle_name': 'The Baker\'s Break-Even',
            'merchant_name': 'Chef Magnus',
            'merchant_title': 'Royal Baker of the Crown',
            'merchant_avatar': 'merchant_chef',
            'discipline': 'Finance',
            'puzzle_type': 'breakeven',
            'difficulty': 1,
            'story_intro': 'Chef Magnus dusts flour from his apron. "I want to open a new pastry shop! Fixed costs are 500 gold per month, each pastry costs 2 gold to make, and I sell them for 7 gold each. How many pastries must I sell to break even?"',
            'story_success': '"Excellent calculation!" Magnus beams. "Now I know exactly what I need to sell. Here\'s some gold for your trouble, young business advisor!"',
            'challenge_data': '{"fixed_costs": 500, "variable_cost": 2, "selling_price": 7, "correct_breakeven": 100, "tolerance": 0, "hint": "Break-Even = Fixed Costs / (Price - Variable Cost)"}',
            'formula_hint': 'Break-Even Units = Fixed Costs / (Selling Price - Variable Cost per Unit)',
            'time_limit_seconds': 120,
            'exp_reward': 50,
            'gold_reward': 120
        },
        {
            'puzzle_code': 'ROI_INVESTMENT',
            'puzzle_name': 'The Investor\'s Return',
            'merchant_name': 'Lord Westbrook',
            'merchant_title': 'Master of the Merchant Bank',
            'merchant_avatar': 'merchant_noble',
            'discipline': 'Finance',
            'puzzle_type': 'roi',
            'difficulty': 2,
            'story_intro': 'Lord Westbrook adjusts his monocle. "I invested 1,000 gold in a trading expedition. After expenses, the voyage returned 1,350 gold. Calculate my Return on Investment percentage, and I shall reward your financial acumen."',
            'story_success': '"Precisely correct!" Westbrook nods approvingly. "You have a banker\'s mind. Take this reward - consider it your first commission."',
            'challenge_data': '{"investment": 1000, "return_value": 1350, "correct_roi": 35, "tolerance": 1, "hint": "ROI = ((Return - Investment) / Investment) x 100"}',
            'formula_hint': 'ROI (%) = ((Net Return - Investment) / Investment) × 100',
            'time_limit_seconds': 120,
            'exp_reward': 60,
            'gold_reward': 150
        },
        {
            'puzzle_code': 'MARKUP_MARKET',
            'puzzle_name': 'The Market Markup Mystery',
            'merchant_name': 'Trader Jameson',
            'merchant_title': 'The Price Wizard',
            'merchant_avatar': 'merchant_trader',
            'discipline': 'Marketing',
            'puzzle_type': 'markup',
            'difficulty': 1,
            'story_intro': 'Jameson rubs his hands together. "I buy silks from the East for 40 gold. I want to apply a 75% markup. What should my selling price be? Get it right and I\'ll share a bit of my profits!"',
            'story_success': '"Sharp as a tack!" Jameson laughs. "You\'ll go far in this business, mark my words. Here\'s your cut!"',
            'challenge_data': '{"cost": 40, "markup_percent": 75, "correct_price": 70, "tolerance": 0, "hint": "Selling Price = Cost x (1 + Markup%)"}',
            'formula_hint': 'Selling Price = Cost × (1 + Markup Percentage / 100)',
            'time_limit_seconds': 90,
            'exp_reward': 45,
            'gold_reward': 90
        },
        {
            'puzzle_code': 'CONVERSION_CAMPAIGN',
            'puzzle_name': 'The Campaign Conversion',
            'merchant_name': 'Town Crier Helena',
            'merchant_title': 'Voice of the Market Square',
            'merchant_avatar': 'merchant_herald',
            'discipline': 'Marketing',
            'puzzle_type': 'conversion_rate',
            'difficulty': 1,
            'story_intro': 'Helena rings her bell. "I announced a special sale - 200 people visited the stall! But only 30 actually bought something. The guild wants to know the conversion rate. Can you help?"',
            'story_success': '"Numbers don\'t lie!" Helena proclaims. "Now I can report to the guild. Take this reward for your quick thinking!"',
            'challenge_data': '{"visitors": 200, "buyers": 30, "correct_rate": 15, "tolerance": 1, "hint": "Conversion Rate = (Buyers / Visitors) x 100"}',
            'formula_hint': 'Conversion Rate (%) = (Number of Buyers / Total Visitors) × 100',
            'time_limit_seconds': 90,
            'exp_reward': 45,
            'gold_reward': 85
        }
    ]
    
    for p in puzzles:
        cur.execute("""
            INSERT INTO merchant_puzzles (puzzle_code, puzzle_name, merchant_name, merchant_title, merchant_avatar,
                discipline, puzzle_type, difficulty, story_intro, story_success, challenge_data, formula_hint,
                time_limit_seconds, exp_reward, gold_reward)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (puzzle_code) DO NOTHING
        """, (p['puzzle_code'], p['puzzle_name'], p['merchant_name'], p['merchant_title'], p['merchant_avatar'],
              p['discipline'], p['puzzle_type'], p['difficulty'], p['story_intro'], p['story_success'],
              p['challenge_data'], p['formula_hint'], p['time_limit_seconds'], p['exp_reward'], p['gold_reward']))
    
    conn.commit()
    cur.close()
    return_connection(conn)
    print("Merchant puzzles seeded.")


def seed_learning_badges():
    """Seed learning achievement badges."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM learning_badges")
    if cur.fetchone()['count'] > 0:
        print("Learning badges already seeded.")
        cur.close()
        return_connection(conn)
        return
    
    badges = [
        {'code': 'BADGE_LEDGER_APPRENTICE', 'name': 'Ledger Apprentice', 'desc': 'Passed the Finance Mentor Trial', 'icon': 'badge_ledger', 'tier': 'bronze', 'discipline': 'Finance', 'type': 'trial_complete', 'count': 1, 'exp': 25},
        {'code': 'BADGE_BAZAAR_TRADER', 'name': 'Bazaar Trader', 'desc': 'Passed the Marketing Mentor Trial', 'icon': 'badge_bazaar', 'tier': 'bronze', 'discipline': 'Marketing', 'type': 'trial_complete', 'count': 1, 'exp': 25},
        {'code': 'BADGE_FORGE_APPRENTICE', 'name': 'Forge Apprentice', 'desc': 'Passed the Operations Mentor Trial', 'icon': 'badge_forge', 'tier': 'bronze', 'discipline': 'Operations', 'type': 'trial_complete', 'count': 1, 'exp': 25},
        {'code': 'BADGE_PUZZLE_SOLVER', 'name': 'Puzzle Solver', 'desc': 'Completed your first Merchant Puzzle', 'icon': 'badge_puzzle', 'tier': 'bronze', 'discipline': None, 'type': 'puzzle_complete', 'count': 1, 'exp': 20},
        {'code': 'BADGE_CALCULATION_MASTER', 'name': 'Calculation Master', 'desc': 'Completed 5 Merchant Puzzles', 'icon': 'badge_calculator', 'tier': 'silver', 'discipline': None, 'type': 'puzzle_complete', 'count': 5, 'exp': 75},
        {'code': 'BADGE_TRIAL_CHAMPION', 'name': 'Trial Champion', 'desc': 'Passed 3 Mentor Trials', 'icon': 'badge_champion', 'tier': 'silver', 'discipline': None, 'type': 'trial_complete', 'count': 3, 'exp': 100},
        {'code': 'BADGE_FINANCE_SCHOLAR', 'name': 'Finance Scholar', 'desc': 'Completed all Finance learning activities', 'icon': 'badge_finance', 'tier': 'gold', 'discipline': 'Finance', 'type': 'discipline_mastery', 'count': 1, 'exp': 150},
        {'code': 'BADGE_MARKETING_MAVEN', 'name': 'Marketing Maven', 'desc': 'Completed all Marketing learning activities', 'icon': 'badge_marketing', 'tier': 'gold', 'discipline': 'Marketing', 'type': 'discipline_mastery', 'count': 1, 'exp': 150},
    ]
    
    for b in badges:
        cur.execute("""
            INSERT INTO learning_badges (badge_code, badge_name, badge_description, badge_icon, badge_tier,
                discipline, requirement_type, requirement_count, exp_bonus)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (badge_code) DO NOTHING
        """, (b['code'], b['name'], b['desc'], b['icon'], b['tier'], b['discipline'], b['type'], b['count'], b['exp']))
    
    conn.commit()
    cur.close()
    return_connection(conn)
    print("Learning badges seeded.")


def seed_learning_paths():
    """Seed learning paths that link lessons, trials, puzzles, and scenarios."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM learning_paths")
    if cur.fetchone()['count'] > 0:
        print("Learning paths already seeded.")
        cur.close()
        return_connection(conn)
        return
    
    cur.execute("SELECT module_id FROM mentorship_modules WHERE module_code = 'MKTG_L1_INTRO' LIMIT 1")
    mktg_module = cur.fetchone()
    mktg_module_id = mktg_module['module_id'] if mktg_module else None
    
    cur.execute("SELECT trial_id FROM mentor_trials WHERE trial_code = 'TRIAL_MARKETING_L1' LIMIT 1")
    mktg_trial = cur.fetchone()
    mktg_trial_id = mktg_trial['trial_id'] if mktg_trial else None
    
    cur.execute("SELECT puzzle_id FROM merchant_puzzles WHERE puzzle_code = 'PUZZLE_CONVERSION_RATE' LIMIT 1")
    mktg_puzzle = cur.fetchone()
    mktg_puzzle_id = mktg_puzzle['puzzle_id'] if mktg_puzzle else None
    
    cur.execute("SELECT scenario_id FROM scenario_master WHERE discipline = 'Marketing' AND required_level = 1 LIMIT 1")
    mktg_scenario = cur.fetchone()
    mktg_scenario_id = mktg_scenario['scenario_id'] if mktg_scenario else None
    
    cur.execute("SELECT module_id FROM mentorship_modules WHERE module_code = 'FIN_L1_INTRO' LIMIT 1")
    fin_module = cur.fetchone()
    fin_module_id = fin_module['module_id'] if fin_module else None
    
    cur.execute("SELECT trial_id FROM mentor_trials WHERE trial_code = 'TRIAL_FINANCE_L1' LIMIT 1")
    fin_trial = cur.fetchone()
    fin_trial_id = fin_trial['trial_id'] if fin_trial else None
    
    cur.execute("SELECT puzzle_id FROM merchant_puzzles WHERE puzzle_code = 'PUZZLE_PROFIT_MARGIN' LIMIT 1")
    fin_puzzle = cur.fetchone()
    fin_puzzle_id = fin_puzzle['puzzle_id'] if fin_puzzle else None
    
    cur.execute("SELECT scenario_id FROM scenario_master WHERE discipline = 'Finance' AND required_level = 1 LIMIT 1")
    fin_scenario = cur.fetchone()
    fin_scenario_id = fin_scenario['scenario_id'] if fin_scenario else None
    
    cur.execute("SELECT module_id FROM mentorship_modules WHERE module_code = 'OPS_L1_INTRO' LIMIT 1")
    ops_module = cur.fetchone()
    ops_module_id = ops_module['module_id'] if ops_module else None
    
    cur.execute("SELECT trial_id FROM mentor_trials WHERE trial_code = 'TRIAL_OPERATIONS_L1' LIMIT 1")
    ops_trial = cur.fetchone()
    ops_trial_id = ops_trial['trial_id'] if ops_trial else None
    
    cur.execute("SELECT puzzle_id FROM merchant_puzzles WHERE puzzle_code = 'PUZZLE_BREAKEVEN' LIMIT 1")
    ops_puzzle = cur.fetchone()
    ops_puzzle_id = ops_puzzle['puzzle_id'] if ops_puzzle else None
    
    cur.execute("SELECT scenario_id FROM scenario_master WHERE discipline = 'Operations' AND required_level = 1 LIMIT 1")
    ops_scenario = cur.fetchone()
    ops_scenario_id = ops_scenario['scenario_id'] if ops_scenario else None
    
    paths = [
        {
            'code': 'PATH_MKTG_INTRO',
            'name': 'Marketing Foundations',
            'description': 'Learn the basics of marketing: understanding customers, creating value, and building brand awareness.',
            'discipline': 'Marketing',
            'difficulty': 1,
            'lesson_id': mktg_module_id,
            'trial_id': mktg_trial_id,
            'puzzle_id': mktg_puzzle_id,
            'scenario_id': mktg_scenario_id,
            'exp_bonus': 150,
            'gold_bonus': 300,
            'badge_code': 'BADGE_MARKETING_MAVEN',
            'sort_order': 1
        },
        {
            'code': 'PATH_FIN_INTRO',
            'name': 'Finance Fundamentals',
            'description': 'Master essential finance concepts: profit margins, break-even analysis, and financial decision-making.',
            'discipline': 'Finance',
            'difficulty': 1,
            'lesson_id': fin_module_id,
            'trial_id': fin_trial_id,
            'puzzle_id': fin_puzzle_id,
            'scenario_id': fin_scenario_id,
            'exp_bonus': 150,
            'gold_bonus': 300,
            'badge_code': 'BADGE_FINANCE_SCHOLAR',
            'sort_order': 1
        },
        {
            'code': 'PATH_OPS_INTRO',
            'name': 'Operations Excellence',
            'description': 'Learn operational efficiency: process optimization, resource management, and quality control.',
            'discipline': 'Operations',
            'difficulty': 1,
            'lesson_id': ops_module_id,
            'trial_id': ops_trial_id,
            'puzzle_id': ops_puzzle_id,
            'scenario_id': ops_scenario_id,
            'exp_bonus': 150,
            'gold_bonus': 300,
            'badge_code': 'BADGE_FORGE_APPRENTICE',
            'sort_order': 1
        }
    ]
    
    for p in paths:
        cur.execute("""
            INSERT INTO learning_paths (path_code, path_name, path_description, discipline, difficulty,
                lesson_module_id, trial_id, puzzle_id, scenario_id, exp_bonus, gold_bonus, badge_code, sort_order)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (path_code) DO NOTHING
        """, (p['code'], p['name'], p['description'], p['discipline'], p['difficulty'],
              p['lesson_id'], p['trial_id'], p['puzzle_id'], p['scenario_id'],
              p['exp_bonus'], p['gold_bonus'], p['badge_code'], p['sort_order']))
    
    conn.commit()
    cur.close()
    return_connection(conn)
    print("Learning paths seeded.")


def seed_all():
    """Run all seed functions. Each function checks if data already exists."""
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
    seed_interactive_challenges()
    seed_advanced_challenges()
    seed_scheduling_challenges()
    seed_cash_flow_challenges()
    seed_negotiation_scenarios()
    seed_risk_categories()
    seed_market_simulation()
    seed_hr_management()
    seed_investor_pitch()
    seed_learning_analytics()
    seed_educational_achievements()
    seed_competitions()
    seed_advanced_simulations()
    seed_story_arcs()
    seed_mentorship_system()
    seed_business_network()
    seed_industry_tracks()
    seed_market_events()
    seed_phase5_social()
    seed_phase5_seasons()
    seed_phase5_content()
    seed_mentorship_modules()
    seed_mentor_trials()
    seed_merchant_puzzles()
    seed_learning_badges()
    seed_learning_paths()
    seed_company_resources()


def seed_company_resources():
    """Seed skill tree abilities and quarterly events."""
    from src.company_resources import seed_skill_tree_abilities, seed_quarterly_events
    seed_skill_tree_abilities()
    seed_quarterly_events()
    print("Company resources seeded.")



if __name__ == "__main__":
    seed_all()
