"""
Leveling System for Business Tycoon RPG

Implements:
- 10-Level EXP progression (150,000 total EXP to reach L10)
- Industry weighting formula for dynamic EXP calculation
- Level-up checking and progression
"""

EXP_TABLE = {
    1: 0,
    2: 500,
    3: 1500,
    4: 3500,
    5: 7000,
    6: 12500,
    7: 22000,
    8: 40000,
    9: 75000,
    10: 150000
}

INDUSTRY_WEIGHTS = {
    "Restaurant": {
        "Marketing": 1.2,
        "Finance": 0.9,
        "Operations": 1.1,
        "Human Resources": 1.0,
        "Legal": 0.8,
        "Strategy": 1.0
    },
    "SaaS": {
        "Marketing": 1.3,
        "Finance": 1.1,
        "Operations": 0.9,
        "Human Resources": 1.0,
        "Legal": 1.1,
        "Strategy": 1.2
    },
    "Retail": {
        "Marketing": 1.1,
        "Finance": 1.0,
        "Operations": 1.2,
        "Human Resources": 1.0,
        "Legal": 0.9,
        "Strategy": 1.0
    },
    "Construction": {
        "Marketing": 0.8,
        "Finance": 1.0,
        "Operations": 1.3,
        "Human Resources": 1.1,
        "Legal": 1.2,
        "Strategy": 0.9
    },
    "Oil & Gas": {
        "Marketing": 0.7,
        "Finance": 1.2,
        "Operations": 1.1,
        "Human Resources": 0.9,
        "Legal": 1.3,
        "Strategy": 1.1
    },
    "Healthcare": {
        "Marketing": 0.9,
        "Finance": 1.1,
        "Operations": 1.0,
        "Human Resources": 1.2,
        "Legal": 1.3,
        "Strategy": 1.0
    },
    "Steel Mill": {
        "Marketing": 0.7,
        "Finance": 1.2,
        "Operations": 1.4,
        "Human Resources": 1.1,
        "Legal": 0.9,
        "Strategy": 1.0
    },
    "Textile Factory": {
        "Marketing": 1.0,
        "Finance": 1.0,
        "Operations": 1.3,
        "Human Resources": 1.2,
        "Legal": 0.8,
        "Strategy": 0.9
    },
    "Railroad": {
        "Marketing": 0.8,
        "Finance": 1.3,
        "Operations": 1.2,
        "Human Resources": 1.0,
        "Legal": 1.1,
        "Strategy": 1.3
    }
}

DISCIPLINES = [
    "Marketing",
    "Finance", 
    "Operations",
    "Human Resources",
    "Legal",
    "Strategy"
]

SUB_SKILLS = {
    "Marketing": ["Brand Identity", "Digital Marketing", "Campaign Planning", "Customer Retention", "Analytics"],
    "Finance": ["Budgeting", "Investment Analysis", "Cash Flow Management", "Financial Reporting"],
    "Operations": ["Supply Chain", "Quality Control", "Process Optimization", "Inventory Management"],
    "Human Resources": ["Recruitment", "Team Building", "Conflict Resolution", "Performance Management"],
    "Legal": ["Contract Law", "Compliance", "Intellectual Property", "Risk Assessment"],
    "Strategy": ["Market Analysis", "Competitive Intelligence", "Long-term Planning", "Innovation"]
}


def get_exp_for_level(level: int) -> int:
    """Get the cumulative EXP required to reach a specific level."""
    return EXP_TABLE.get(level, 150000)


def get_current_level(total_exp: int) -> int:
    """Calculate the current level based on total EXP earned."""
    current_level = 1
    for level, required_exp in sorted(EXP_TABLE.items()):
        if total_exp >= required_exp:
            current_level = level
        else:
            break
    return current_level


def get_exp_to_next_level(total_exp: int) -> tuple:
    """
    Returns (exp_needed, next_level) tuple.
    Returns (0, 10) if already at max level.
    """
    current_level = get_current_level(total_exp)
    if current_level >= 10:
        return (0, 10)
    
    next_level = current_level + 1
    exp_needed = EXP_TABLE[next_level] - total_exp
    return (exp_needed, next_level)


def calculate_weighted_exp(base_exp: int, industry: str, discipline: str) -> int:
    """
    Apply industry weighting to base EXP reward.
    
    Example: Marketing EXP is higher in Restaurant (1.2x) than Oil & Gas (0.7x)
    """
    weights = INDUSTRY_WEIGHTS.get(industry, {})
    weight = weights.get(discipline, 1.0)
    return int(base_exp * weight)


def check_level_up(old_exp: int, new_exp: int) -> tuple:
    """
    Check if adding exp results in a level up.
    Returns (leveled_up: bool, old_level: int, new_level: int)
    """
    old_level = get_current_level(old_exp)
    new_level = get_current_level(new_exp)
    return (new_level > old_level, old_level, new_level)


def get_level_title(level: int) -> str:
    """Get the title associated with a level."""
    titles = {
        1: "Novice",
        2: "Apprentice", 
        3: "Junior Associate",
        4: "Associate",
        5: "Senior Associate",
        6: "Manager",
        7: "Senior Manager",
        8: "Director",
        9: "Vice President",
        10: "Master Tycoon"
    }
    return titles.get(level, "Unknown")


def get_progress_bar(current_exp: int, current_level: int, bar_length: int = 20) -> str:
    """Generate a text-based progress bar for EXP."""
    if current_level >= 10:
        return "[" + "=" * bar_length + "] MAX"
    
    level_start = EXP_TABLE[current_level]
    level_end = EXP_TABLE[current_level + 1]
    progress = current_exp - level_start
    total_needed = level_end - level_start
    
    filled = int((progress / total_needed) * bar_length)
    empty = bar_length - filled
    
    percentage = int((progress / total_needed) * 100)
    return f"[{'=' * filled}{'-' * empty}] {percentage}%"


if __name__ == "__main__":
    print("=== Leveling System Test ===\n")
    
    print("EXP Table:")
    for level, exp in EXP_TABLE.items():
        print(f"  Level {level}: {exp:,} EXP - {get_level_title(level)}")
    
    print("\n--- Testing Level Calculations ---")
    test_exp_values = [0, 250, 500, 1000, 3500, 12500, 75000, 150000]
    for exp in test_exp_values:
        level = get_current_level(exp)
        exp_needed, next_level = get_exp_to_next_level(exp)
        print(f"  {exp:,} EXP = Level {level} ({get_level_title(level)}), {exp_needed:,} EXP to Level {next_level}")
    
    print("\n--- Testing Industry Weighting ---")
    base_exp = 100
    for industry in ["Restaurant", "SaaS", "Oil & Gas"]:
        weighted = calculate_weighted_exp(base_exp, industry, "Marketing")
        print(f"  {base_exp} base Marketing EXP in {industry}: {weighted} EXP")
