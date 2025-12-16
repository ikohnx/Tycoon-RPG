# Business Tycoon RPG

## Overview
A 2D educational RPG built with Python/Flask designed to teach real-world business skills across 6 Core Disciplines and 8 Transferable Sub-Skills, each with a 10-Level progression curve.

### Project Goal
Develop a 2D Graphical RPG set across three distinct worlds (Modern, Fantasy, Sci-Fi), teaching practical business acumen through scenario-based gameplay.

### Current State
**Phase 1 - MVP (Complete)**
- Core database schema implemented (6 tables)
- 10-level EXP progression system (150,000 EXP to L10)
- Industry weighting formula for dynamic EXP calculation
- MVP content path: Modern World / Restaurant Industry / Marketing (10 scenarios L1-L5)
- Flask web application with responsive UI
- Cartoon-style graphics with world-specific backgrounds
- Character avatars and scenario illustrations
- CSS animations for visual polish

## Project Structure
```
/
├── app.py                  # Flask web application entry point
├── src/
│   ├── __init__.py
│   ├── database.py         # PostgreSQL database initialization and seeding
│   ├── game_engine.py      # Core game logic, player management, scenario processing
│   └── leveling.py         # EXP tables, industry weights, level calculations
├── templates/              # Jinja2 HTML templates
│   ├── base.html           # Base template with CSS/JS
│   ├── index.html          # Login/registration page
│   ├── hub.html            # Main game hub
│   ├── scenarios.html      # Scenario list by discipline
│   ├── play.html           # Active scenario gameplay
│   ├── result.html         # Scenario outcome display
│   └── progress.html       # Player progress dashboard
├── static/images/          # Cartoon graphics assets
│   ├── modern_office_hub.png
│   ├── fantasy_tavern_hub.png
│   ├── scifi_starship_hub.png
│   ├── business_tycoon_avatar.png
│   └── [scenario illustrations]
└── replit.md              # This file
```

## Database Schema
- **player_profiles**: Player identity, world/industry choice, cash, reputation
- **player_discipline_progress**: 6 disciplines with level/EXP tracking
- **player_subskill_progress**: 8 sub-skills linked to parent disciplines
- **scenario_master**: All game scenarios with choices and rewards
- **financial_metrics**: Monthly revenue/cost tracking
- **completed_scenarios**: Tracks which scenarios each player has completed

## 6 Core Disciplines
1. Marketing
2. Finance
3. Operations
4. Human Resources
5. Legal
6. Strategy

## 3 Worlds
1. Modern - Contemporary business (offices, digital marketing)
2. Fantasy - Medieval magical realm (taverns, dragon trade)
3. Sci-Fi - Futuristic galactic economy (starships, rare-earth mining)

## Level Progression (Cumulative EXP)
- L1: 0 | L2: 500 | L3: 1,500 | L4: 3,500 | L5: 7,000
- L6: 12,500 | L7: 22,000 | L8: 40,000 | L9: 75,000 | L10: 150,000

## Industry Weights (EXP Modifiers)
Each industry provides bonuses/penalties to different disciplines:
- Restaurant: Marketing 1.2x, Operations 1.1x, Legal 0.8x
- SaaS: Marketing 1.3x, Strategy 1.2x
- Construction: Operations 1.3x, Legal 1.2x

## Running the Game
```bash
python app.py
```
The game runs as a web application on port 5000.

## Development Phases
- **Phase 1** (Complete): MVP with Flask web interface and cartoon graphics
- **Phase 2**: Additional worlds and industries content
- **Phase 3**: Financial engine, reputation system, L6-L10 content
- **Phase 4**: Modular content framework, storyline arcs

## Recent Changes
- 2024-12: Initial project setup
- 2024-12: Database schema created with 6 core tables
- 2024-12: Leveling system implemented
- 2024-12: 10 Marketing scenarios seeded (L1-L5)
- 2024-12: Converted to Flask web application
- 2024-12: Added cartoon-style graphics (world backgrounds, avatars, scenario illustrations)
- 2024-12: Implemented world-specific theming across all pages
- 2024-12: Added CSS animations and visual polish
- 2025-12: Added RPG character stats system (Charisma, Intelligence, Luck, Negotiation)
- 2025-12: Implemented achievement/badge system with 6 unlockable achievements
- 2025-12: Created inventory system with item shop (8 items: consumables and equipment)
- 2025-12: Built NPC relationship system with 5 characters and dialogue interactions
- 2025-12: Added quest system with Main and Side quest tracking
- 2025-12: Implemented CSRF protection via Flask-WTF for security
- 2025-12: Added dual career path system (Entrepreneur vs Employee)
- 2025-12: Implemented job title progression for employee path (10 job levels per industry)
