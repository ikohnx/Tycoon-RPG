"""
Player class, ADVISOR_QUOTES, and related constants for Business Tycoon RPG.
"""

import random
from src.database import get_connection, return_connection

ADVISOR_QUOTES = {
    'Marketing': [
        "A customer told is nice. A customer who SHOWS others? That's gold.",
        "Your brand isn't what you say it is. It's what they say it is.",
        "Marketing is telling the story. Sales is asking for the ending.",
        "The best marketing doesn't feel like marketing.",
        "Half the money I spend on advertising is wasted. The trouble is I don't know which half.",
        "People don't buy products. They buy better versions of themselves.",
        "Content is fire. Social media is gasoline.",
        "Make the customer the hero of your story.",
        "Good marketing makes the company look smart. Great marketing makes the customer feel smart.",
        "The aim of marketing is to know the customer so well the product sells itself."
    ],
    'Finance': [
        "Revenue is vanity, profit is sanity, but cash is king.",
        "Profit isn't real until it's in the bank.",
        "Never confuse a healthy income statement with a healthy bank account.",
        "In business, the rear-view mirror is always clearer than the windshield.",
        "The first rule of compounding: Never interrupt it unnecessarily.",
        "Risk comes from not knowing what you're doing.",
        "Price is what you pay. Value is what you get.",
        "It's not about timing the market. It's about time IN the market.",
        "A budget tells your money where to go instead of wondering where it went.",
        "Beware of little expenses. A small leak will sink a great ship."
    ],
    'Operations': [
        "You can't manage what you can't measure.",
        "Efficiency is doing things right. Effectiveness is doing the right things.",
        "The bottleneck is the ceiling of your output.",
        "Inventory is money sitting around in another form.",
        "Quality is not an act, it's a habit.",
        "Simplify, then add lightness.",
        "The best process is the one that gets used.",
        "Speed without direction is just chaos.",
        "Every system is perfectly designed to get the results it gets.",
        "Fix the process, not the blame."
    ],
    'Human Resources': [
        "Train people well enough so they can leave. Treat them well enough so they don't want to.",
        "Culture eats strategy for breakfast.",
        "Hire character. Train skill.",
        "Your first hire sets your culture. Choose wisely.",
        "The strength of the team is each individual member. The strength of each member is the team.",
        "Great vision without great people is irrelevant.",
        "People don't leave bad jobs. They leave bad managers.",
        "Feedback is a gift. Even when it's wrapped poorly.",
        "Diversity is being invited to the party. Inclusion is being asked to dance.",
        "An employee's motivation is a direct result of the sum of interactions with their manager."
    ],
    'Legal': [
        "The best contract is the one you never have to enforce.",
        "An ounce of prevention is worth a pound of litigation.",
        "In law, nothing is certain except the expense.",
        "A verbal agreement isn't worth the paper it's written on.",
        "The devil is in the details. So is the lawyer.",
        "Assume everything you write will be read aloud in court.",
        "Compliance isn't a burden. It's a shield.",
        "Document everything. Memory fades, but paper doesn't.",
        "The law is a profession of words. Choose them carefully.",
        "Better to ask permission than to beg forgiveness. Legally speaking."
    ],
    'Strategy': [
        "Strategy without tactics is the slowest route to victory. Tactics without strategy is the noise before defeat.",
        "The essence of strategy is choosing what NOT to do.",
        "Culture is strategy's breakfast, lunch, and dinner.",
        "In the middle of difficulty lies opportunity.",
        "If you don't know where you're going, any road will get you there.",
        "The competitor to be feared is one who never bothers about you at all.",
        "Good strategy means saying no to a lot of good ideas.",
        "The only sustainable competitive advantage is the ability to learn faster than your competition.",
        "Vision without execution is hallucination.",
        "A goal without a plan is just a wish."
    ]
}


def get_random_advisor_quote(discipline=None):
    """Get a random advisor quote, optionally filtered by discipline."""
    if discipline and discipline in ADVISOR_QUOTES:
        quotes = ADVISOR_QUOTES[discipline]
    else:
        all_quotes = []
        for disc_quotes in ADVISOR_QUOTES.values():
            all_quotes.extend(disc_quotes)
        quotes = all_quotes
    return random.choice(quotes) if quotes else ""


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
        return_connection(conn)
        
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
        return_connection(conn)
    
    def get_discipline_level(self, discipline: str) -> int:
        """Get the current level for a discipline."""
        if discipline in self.discipline_progress:
            return self.discipline_progress[discipline]['level']
        return 1
