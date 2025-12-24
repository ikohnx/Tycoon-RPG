# Business Tycoon RPG

## Overview
Business Tycoon RPG is a 2D educational role-playing game developed with Python/Flask. Its primary purpose is to impart practical business skills through engaging, scenario-based gameplay. The game covers six core business disciplines and eight transferable sub-skills, each with a 10-level progression system. The vision is to create an immersive learning experience across diverse themed worlds (Modern, Industrial, Fantasy, Sci-Fi), ultimately preparing players for real-world business challenges.

## User Preferences
I prefer iterative development, with a focus on delivering functional, well-tested features in logical steps. Please ask for clarification if there are ambiguities, and propose solutions before implementing major changes. I value clear, concise explanations and prefer a collaborative approach where we discuss design choices.

## System Architecture
The game is built as a Flask web application with a responsive, mobile-first UI. The front-end leverages Jinja2 templates, CSS animations, and cartoon-style graphics with world-specific backdrops to create an engaging aesthetic. Core architectural components include:

-   **Game Engine:** Manages player progression, scenario processing, and core game logic.
-   **Leveling System:** Implements a 10-level EXP progression with dynamic calculations based on industry-specific weighting.
-   **Database:** A PostgreSQL database stores player data, scenario information, and financial metrics. The schema supports detailed tracking of player progress, completed scenarios, and a comprehensive double-entry bookkeeping system.
-   **Content Structure:** Scenarios are designed to teach specific business concepts across all 6 disciplines (Marketing, Finance, Operations, Human Resources, Legal, Strategy) with choices, feedback, and consequences.
-   **UI/UX:** Features an RPG game aesthetic with custom fonts (Cinzel, Staatliches), game-styled buttons, a HUD navbar, decorative panel borders, and an SVG-based campaign map. A visual novel-style dialogue system is used for scenarios, featuring NPC advisor portraits and typing animations.
-   **Core Game Mechanics:** Includes a star rating system for scenarios, energy/stamina, daily login rewards, idle income, advisor collection, equipment system, prestige system, boss challenges, daily missions, leaderboards, and a rival battle system.
-   **Educational Mechanics:** Incorporates interactive challenges with real-world calculations (e.g., Budget Calculator, ROI, Break-Even Analysis) and a dedicated training system that provides concept explanations, formulas, and examples before gameplay.
-   **Financial Engine:** A robust accounting system supports a Chart of Accounts, Journal Entry system with debit/credit validation, Trial Balance, Income Statement, Balance Sheet, and monthly period close.
-   **Project Management System:** A scheduling subsystem with initiative/task management, critical path calculation, resource allocation, and weekly tick-based simulation. Features 5 interactive scheduling challenges (Critical Path, PERT Estimation, Resource Leveling, Schedule Compression, Task Dependencies) to teach PM concepts before applying them in real projects.
-   **Cash Flow Forecasting System:** 13-week rolling cash flow forecasts with interactive challenges teaching receivables timing, payables prioritization, seasonal planning, and emergency reserves. Helps players understand the difference between profit and cash.
-   **Business Plan Workshop:** Guided business plan creation with 8 sections (Executive Summary, Market Analysis, Financial Projections, etc.) and mentor feedback scoring. Players build comprehensive plans and receive actionable guidance.
-   **Negotiation Simulator:** Interactive deal-making scenarios teaching BATNA, anchoring, concessions, and win-win strategies. Covers vendor, employment, and real estate negotiations with multi-round offer/counter-offer dynamics.
-   **Risk Management Dashboard:** Portfolio-style risk assessment where players identify, score (probability x impact), and mitigate business risks across 8 categories. Visual risk matrix and mitigation tracking.
-   **Supply Chain Simulator:** Inventory management with reorder points, safety stock, lead times, and supplier relationships. Players manage products, create purchase orders, and learn EOQ concepts.
-   **Market Simulation:** Price-demand dynamics teaching elasticity, competitive responses, seasonal trends, and promotion ROI. Features 5 challenge types (pricing, competition, marketing ROI, segmentation, positioning) across multiple market segments.
-   **HR Performance Management:** Complete employee lifecycle from recruitment through retention. Covers hiring decisions, performance reviews, team dynamics, conflict resolution, and succession planning with interactive challenges.
-   **Investor Pitch Simulator:** Guided pitch deck creation with 8 sections (Problem, Solution, Market, Financials, Team, Ask, etc.) and mentor scoring. Practice presentations with different investor profiles (angels, VCs, strategic) who ask targeted questions.
-   **Learning Analytics Dashboard:** Comprehensive skill progress tracking across all 8 educational systems, weak area identification, personalized learning recommendations, and skill development visualizations.
-   **Achievement System:** Educational badges tied to module completion, mastery rewards for each discipline, streak tracking for consistent learning, and special scenario unlocks.
-   **Competitive Features:** Business competitions between players with league rankings by discipline, weekly challenges with leaderboards, and reward multipliers.
-   **Advanced Simulations:** Complex business scenarios including M&A (mergers & acquisitions), international expansion, crisis management, and full business lifecycle simulation.
-   **Tutorial/Onboarding:** Guided tutorial system for new player onboarding with progress tracking across 6 core sections.
-   **Storyline Quest System:** Multi-chapter narrative arcs with branching decisions, 5 story arcs across different world themes (Modern, Industrial, Fantasy, Sci-Fi), player progress tracking, and experience rewards for story completion.
-   **Mentorship & Advisor Progression:** Deep relationships with NPC advisors, affinity system tracking interactions, mentor missions with specialized rewards, skill tree unlocking mechanics, and advisor-specific training paths.
-   **Business Network & Partnerships:** Player networking system with business partners, joint ventures with shared rewards/risks, networking events with contact gains, and partnership management across industries.
-   **Industry Specialization Tracks:** Deep-dive career paths for 5 industries (Tech Startups, Healthcare, Retail, Financial Services, Manufacturing), industry-specific challenges, professional certifications with exams, and mastery achievements.
-   **Dynamic Market Events:** Real-time economic events affecting gameplay, market cycles (expansion/recession/stable), breaking news with time-limited responses, global community challenges with shared reward pools, and industry-specific impact modifiers.
-   **Phase 5A - Multiplayer & Social:** Guild/alliance system with guild wars, co-op challenges requiring team coordination, player-to-player trading marketplace, and player mentoring system for knowledge sharing.
-   **Phase 5B - Seasonal Content:** Rotating weekly/monthly events with themed rewards, seasonal battle pass progression system, limited-time boss challenges, and holiday-themed special events.
-   **Phase 5C - AI Personalization:** Adaptive difficulty system, AI-powered learning path recommendations, personalized scenario generation, virtual business coach with weak area identification and learning style detection.
-   **Phase 5D - Content Expansion:** New world themes (Pirate for maritime trade, Space for futuristic commerce), real-world business case studies, guest mentor NPCs from famous companies, and deeper industry specialization tracks.
-   **Phase 5E - Accessibility & Polish:** PWA optimization, screen reader support, color blind modes (protanopia, deuteranopia, tritanopia), high contrast mode, reduced motion settings, and customizable font sizes.

## Business Mastery Simulation (December 2024)
-   **Company Resources System:** Tracks Capital ($), Team Morale (0-100 stamina), and Brand Equity (0-100 HP). Game over when Brand Equity reaches zero.
-   **Fiscal Quarter Timeline:** Every 3 decisions advances the quarter (Q1 → Q2 → Q3 → Q4). Quarterly events can trigger at quarter boundaries.
-   **Skill Tree Abilities:** 6 discipline-specific abilities unlock at subskill level 3:
    - Viral Campaign (Marketing): 1.5x revenue multiplier
    - Burn Rate Optimization (Finance): 30% cost reduction
    - Automation Initiative (Operations): 2x EXP multiplier
    - Headhunter Network (HR): +20 morale boost
    - Liability Shield (Legal): Prevents lawsuit quarterly events
    - Blue Ocean Strategy (Strategy): 2x EXP multiplier
-   **Command Center Dashboard:** Features radar chart for 6 pillars, resource ledger with progress bars, news ticker for recent events, skill tree grid, and active buffs display.
-   **HUD Resources Bar:** Navbar now displays Capital, Team Morale, Brand Equity, and Fiscal Quarter across all gameplay pages.
-   **Quarterly Events:** Probability-based events include Market Boom (+$5000), Competitor Crisis (+10 brand), Regulatory Changes (-$2000), Lawsuits (-15 brand, preventable with Liability Shield), and Talent Shortage (-15 morale).
-   **Modular Scenario Content:** Crisis and opportunity scenarios stored in content/scenarios.json with morale/brand impact trade-offs.

## Resource Integration & Feature Gating (December 2024)
-   **Server-Side Feature Gating:** `check_feature_requirements()` and `deduct_feature_cost()` enforce resource costs before allowing feature access
-   **Enforcement Decorators:** Three decorators control gameplay access:
    - `@feature_gated()`: Checks capital/morale requirements for specific features
    - `@game_over_check`: Prevents gameplay when brand_equity = 0 (bankruptcy)
    - `@energy_required(amount)`: Checks and consumes energy before actions
-   **Protected Routes:** 12+ gameplay routes protected with decorators (battle_arena, random_event, rivals, negotiation, supplychain, hrmanagement, risks, pitch, simulations, prestige, boss_challenges, market)
-   **Energy Consumption:** 10 energy consumed per scenario completion via `engine.consume_energy(10)` in make_choice route
-   **Quarterly Event Display:** result.html template shows quarterly events with color-coded styling (green=positive, red=negative, blue=neutral)
-   **Disabled Button Prevention:** JavaScript prevents clicks on disabled feature buttons in hub.html

## Security & Infrastructure (December 2024)
-   **Password Security:** Bcrypt password hashing with automatic SHA256 migration for existing users
-   **Route Protection:** @login_required decorator applied to 90+ gameplay routes
-   **Database Pooling:** ThreadedConnectionPool (2-20 connections) with proper connection return via `return_connection(conn)` throughout codebase
-   **Request-Scoped GameEngine:** Each HTTP request gets its own GameEngine instance via Flask's `g` context, preventing cross-user session data leakage
-   **Onboarding Persistence:** Welcome modal dismissal persists via `onboarding_seen` database flag - players only see it once
-   **Consolidated Seeding:** All 47 seed functions consolidated into `seed_all()` for cleaner startup code

## External Dependencies
-   **PostgreSQL:** Relational database for all game data persistence.
-   **Flask-WTF:** Used for CSRF protection in web forms.
-   **bcrypt:** Industry-standard password hashing library.

## Mobile & Cross-Platform Support (December 2024)
The game now works seamlessly across mobile and desktop platforms:

-   **Progressive Web App (PWA):** Full PWA implementation with:
    -   Web app manifest (`static/manifest.json`) with app icons and shortcuts
    -   Service worker (`static/sw.js`) for offline caching and network-first strategies
    -   Install prompt banner for "Add to Home Screen" functionality
    -   Offline fallback page for network-less gameplay

-   **Native Mobile (Capacitor):** Configuration for iOS and Android builds:
    -   `capacitor.config.json` ready for native compilation
    -   Splash screen and status bar configurations
    -   Safe area inset support for notched devices

-   **Responsive Design Enhancements:**
    -   Touch-friendly interactions (44px minimum touch targets)
    -   Safe area padding for iOS notch and Android gesture nav
    -   Landscape orientation optimization
    -   Reduced motion and high contrast accessibility modes

-   **App Icons:** Generated icon set from 72x72 to 512x512 pixels in `static/icons/`