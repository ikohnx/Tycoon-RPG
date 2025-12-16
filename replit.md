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

## 4 Worlds
1. Modern - Contemporary business (offices, digital marketing)
2. Industrial - Late 1800s industrial age (steel mills, textile factories, railroads)
3. Fantasy - Medieval magical realm (taverns, dragon trade)
4. Sci-Fi - Futuristic galactic economy (starships, rare-earth mining)

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
- 2025-12: Added Random Events system with 8 surprise business events
- 2025-12: Created Business Dashboard with milestones and rival tracking
- 2025-12: Implemented Rival NPC system with 5 competing businesses
- 2025-12: Added Weekly Challenges with reward tracking
- 2025-12: Built Avatar Customization system (hair, outfit, accessories, colors)
- 2025-12: Complete mobile-first UI redesign for all key pages
- 2025-12: Built visual SVG-based Campaign Map with snake-path node layout
- 2025-12: Added mobile bottom navigation bar with quick access buttons
- 2025-12: Implemented touch-friendly controls throughout the game
- 2025-12: Expanded Fantasy World with 3 tavern-themed scenarios
- 2025-12: Added Industrial Age world with Steel Mill, Textile Factory, and Railroad industries
- 2025-12: Created 10 Industrial scenarios covering Operations, HR, Finance, Strategy, Marketing, Legal
- 2025-12: Added 5 Industrial random events and 5 Industrial rivals (Carnegie, Vanderbilt, etc.)
- 2025-12: Implemented Industrial job progression (Furnace Stoker to Mill Baron, Track Layer to Railroad Tycoon)
- 2025-12: Major UI overhaul - transformed from business app to RPG game aesthetic
- 2025-12: Added Cinzel and Staatliches game fonts with golden gradient titles
- 2025-12: Created game-styled buttons (gold, crimson, emerald, purple variants with glow effects)
- 2025-12: Implemented game HUD navbar, decorative panel borders, and custom scrollbar
- 2025-12: Added avatar frame glow, level badge pulse animations, and stat card accents
- 2025-12: Generated illustrated game graphics (Kingshot-style visual assets):
  - Hero character portrait and rival villain portrait
  - 6 discipline building icons (Marketing, Finance, Operations, HR, Legal, Strategy)
  - Resource icons (gold coin, reputation star)
  - Scenario illustration cards for each discipline
  - Victory and defeat splash screens
- 2025-12: Redesigned hub with visual building grid layout showing illustrated icons
- 2025-12: Added "SELECTED" badge indicators on new game selection cards
- 2025-12: Fixed core gameplay - added 15 new scenarios for Modern/Restaurant covering all 6 disciplines
- 2025-12: Each discipline now has real business education content with choices, feedback, and consequences
- 2025-12: Implemented illustrated backdrop graphics (Kingshot-style) for all pages
- 2025-12: Added world-specific background images: Modern office, Industrial factory, Fantasy tavern, Sci-Fi starship
- 2025-12: Created epic RPG title screen backdrop with fantasy kingdom cityscape
- 2025-12: Redesigned scenario play screen with visual novel style dialogue system
- 2025-12: Added 6 NPC discipline advisor portraits (Marketing Manager, Finance Director, Operations Chief, HR Manager, Legal Counsel, Strategy Advisor)
- 2025-12: Implemented dialogue typing animation and staggered choice card animations
- 2025-12: Created discipline-specific scene backdrops for all 6 business disciplines
- 2025-12: Implemented complete 10-level Marketing Curriculum with structured learning progression
- 2025-12: Marketing curriculum covers: Need vs Want, 4 Ps (Product, Price, Place, Promotion), Segmentation, CPA, A/B Testing, LTV, SWOT, Crisis Management
- 2025-12: Implemented complete 10-level Accounting/Finance Curriculum with structured learning progression
- 2025-12: Accounting curriculum covers: Accounting Equation, Revenue vs Expense, Cash vs Accrual, Income Statement (P&L), Balance Sheet, Cash Flow Statement, Financial Ratios (Quick/Current), FIFO/LIFO Inventory, Budget Variance Analysis, Tax Strategy (GAAP/IFRS)
- 2025-12: Implemented complete 10-level Strategic Finance Curriculum (30 scenarios across 3 worlds)
- 2025-12: Finance curriculum covers: Cash Flow Management, ROI, Time Value of Money, Capital Budgeting (Payback Period), Debt Financing, Risk/Return Tradeoff, DCF & NPV, WACC, Equity Financing & Dilution, Mergers & Acquisitions
- 2025-12: Implemented complete 10-level Legal Curriculum (30 scenarios across 3 worlds)
- 2025-12: Legal curriculum covers: Business Entity Structure, Contract Essentials, Employee Agreements/NDAs, Leases & Property Law, Licensing & Permits, Torts & Negligence, Trademarks, Patents & Trade Secrets, Litigation & Dispute Resolution, International Law & Governance
- 2025-12: Implemented complete 10-level Operations Curriculum (30 scenarios across 3 worlds)
- 2025-12: Operations curriculum covers: Transformation Process (I/O), Inventory Management, Workflow Optimization, Capacity Utilization, Quality Assurance, Production Scheduling, Just-In-Time Inventory, Supply Chain Risk Management, Outsourcing/Offshoring, Process Innovation & Automation
- 2025-12: Implemented complete 10-level Human Resources Curriculum (30 scenarios across 3 worlds)
- 2025-12: HR curriculum covers: Job Description & Needs Analysis, Legal & Ethical Hiring (EEO), Onboarding & Training, Performance Management (SMART Goals), Compensation & Benefits, Employee Relations & Morale, Conflict Resolution & Mediation, Termination & Severance, Succession Planning, Organizational Structure & Labor Relations
- 2025-12: Implemented complete 10-level Strategy Curriculum (30 scenarios across 3 worlds)
- 2025-12: Strategy curriculum covers: Mission & Vision, Competitive Advantage (Cost Leadership vs Differentiation), PESTLE Analysis, VRIO Framework, Porter's Generic Strategies, Balanced Scorecard, Ansoff Matrix, Porter's Five Forces, Organizational Structure (Functional/Divisional/Matrix), Strategic Resource Allocation
- 2025-12: **ALL 6 CORE DISCIPLINES COMPLETE** - Total of 210 educational business scenarios across all curricula
- 2025-12: Implemented 12 Kingshot-style mobile RPG game mechanics:
  - Star Rating System: 1-3 stars per scenario based on choice quality
  - Energy/Stamina System: 100 max energy, 10 cost per scenario, 1 per 5 min recharge
  - Daily Login Rewards: Streak tracking with escalating gold/item/energy rewards (7-day cycle)
  - Idle Income System: Passive gold generation based on completed scenarios and level (max 8 hour accumulation)
  - Advisor Collection System: 12 recruitable advisors with unique discipline bonuses
  - Equipment System: 9 items across 3 slots (Head, Body, Accessory) with stat bonuses
  - Prestige/Ascension System: Reset progress for permanent +10% EXP and +15% gold multipliers
  - Visual Campaign Map: Node-based stage progression showing all 6 disciplines with stars
  - Boss Challenges: Level 5 (Elite) and Level 10 (Boss) milestone scenarios per discipline
  - Daily Missions System: 3 refreshing daily tasks with gold rewards
  - Leaderboard System: Rankings by total stars, wealth, and combined discipline levels
  - Rival Battle System: Stat comparison combat with luck modifier and rewards
- 2025-12: Implemented Interactive Challenge System for "real learning" with calculations:
  - Budget Calculator: Calculate profit from revenue and expenses
  - Pricing Strategy: Set selling prices based on cost and target margin
  - Staffing Decision: Calculate staff needed for customer volume
  - Break-Even Analysis: Calculate break-even point in units
  - 10 interactive challenges seeded across Modern, Industrial, Fantasy, and Sci-Fi worlds
  - Star rating based on accuracy (95%+ = 3 stars, 70%+ = 2 stars, otherwise 1 star)
  - Challenge scenarios visually distinguished with purple "Math" badge in scenario list
- 2025-12: Implemented Training System for pre-quest learning:
  - Training page shows concept explanation, formula, worked example, and pro tips
  - All quests now route through /training first before gameplay
  - Default training content for each challenge type (budget, pricing, staffing, break-even)
  - Choice-based quests also get discipline-specific training intro
  - Buttons changed to "Learn & Play" / "Learn & Solve" to indicate training step
