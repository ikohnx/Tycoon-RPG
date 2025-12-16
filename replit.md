# Business Tycoon RPG

## Overview
A 2D educational RPG built with Python/Pygame designed to teach real-world business skills across 6 Core Disciplines and 8 Transferable Sub-Skills, each with a 10-Level progression curve.

### Project Goal
Develop a 2D Graphical RPG set across three distinct worlds (Modern, Fantasy, Sci-Fi), teaching practical business acumen through scenario-based gameplay.

### Current State
**Phase 1 - MVP (In Progress)**
- Core database schema implemented (5 tables)
- 10-level EXP progression system (150,000 EXP to L10)
- Industry weighting formula for dynamic EXP calculation
- MVP content path: Modern World / Restaurant Industry / Marketing (10 scenarios L1-L5)
- Command-line interface for gameplay

## Project Structure
```
/
├── main.py                 # Main game entry point
├── src/
│   ├── __init__.py
│   ├── database.py         # PostgreSQL database initialization and seeding
│   ├── game_engine.py      # Core game logic, player management, scenario processing
│   └── leveling.py         # EXP tables, industry weights, level calculations
├── assets/                 # (Future) Sprite and image assets
│   ├── Modern/
│   ├── Fantasy/
│   └── SciFi/
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
python main.py
```

## Development Phases
- **Phase 1** (Current): MVP with command-line interface
- **Phase 2**: Pygame graphical integration, world reskinning
- **Phase 3**: Financial engine, reputation system, L6-L10 content
- **Phase 4**: Modular content framework, storyline arcs

## Recent Changes
- 2024-12: Initial project setup
- 2024-12: Database schema created with 5 core tables
- 2024-12: Leveling system implemented
- 2024-12: 10 Marketing scenarios seeded (L1-L5)
- 2024-12: Main game loop and CLI implemented
