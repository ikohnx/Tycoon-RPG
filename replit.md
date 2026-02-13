# Business Tycoon RPG

## Overview
Business Tycoon RPG is a 2D educational role-playing game developed with Python/Flask. Its primary purpose is to impart practical business skills through engaging, scenario-based gameplay. The game covers six core business disciplines and eight transferable sub-skills, each with a 10-level progression system. The vision is to create an immersive learning experience across diverse themed worlds (Modern, Industrial, Fantasy, Sci-Fi), ultimately preparing players for real-world business challenges. The game aims to provide an immersive learning experience, combining educational content with engaging RPG mechanics to create a unique and effective platform for business skill development.

## User Preferences
I prefer iterative development, with a focus on delivering functional, well-tested features in logical steps. Please ask for clarification if there are ambiguities, and propose solutions before implementing major changes. I value clear, concise explanations and prefer a collaborative approach where we discuss design choices.

## System Architecture
The game is built as a Flask web application with a responsive, mobile-first UI, leveraging Jinja2 templates, CSS animations, and cartoon-style graphics.

**Core Components & Mechanics:**
-   **Game Engine:** Manages player progression, scenario processing, and core game logic.
-   **Leveling System:** 10-level EXP progression with dynamic calculations.
-   **Database:** PostgreSQL for player data, scenario information, and a comprehensive double-entry bookkeeping system.
-   **Content Structure:** Scenarios teach business concepts across Marketing, Finance, Operations, Human Resources, Legal, and Strategy.
-   **UI/UX:** RPG aesthetic with custom fonts, game-styled buttons, HUD navbar, SVG campaign map, and visual novel-style dialogue with NPC portraits.
-   **Core Game Mechanics:** Star rating, energy/stamina, daily rewards, idle income, advisor collection, equipment, prestige, boss challenges, daily missions, leaderboards, and rival battles.
-   **Educational Mechanics:** Interactive challenges with real-world calculations (e.g., ROI, Break-Even Analysis), and a training system with concept explanations.
-   **Financial Engine:** Robust accounting system supporting Chart of Accounts, Journal Entry, Trial Balance, Income Statement, Balance Sheet, and period close.
-   **Project Management System:** Scheduling subsystem with initiative/task management, critical path calculation, resource allocation, and weekly simulation. Includes 5 interactive scheduling challenges.
-   **Cash Flow Forecasting System:** 13-week rolling forecasts with challenges covering receivables, payables, seasonal planning, and emergency reserves.
-   **Business Plan Workshop:** Guided business plan creation with 8 sections and mentor feedback.
-   **Negotiation Simulator:** Interactive deal-making scenarios covering BATNA, anchoring, concessions, and win-win strategies across various negotiation types.
-   **Risk Management Dashboard:** Portfolio-style risk assessment for identification, scoring, and mitigation across 8 categories.
-   **Supply Chain Simulator:** Inventory management with reorder points, safety stock, lead times, and supplier relationships.
-   **Market Simulation:** Price-demand dynamics teaching elasticity, competitive responses, and promotion ROI through 5 challenge types.
-   **HR Performance Management:** Covers employee lifecycle, hiring, performance reviews, team dynamics, conflict resolution, and succession planning.
-   **Investor Pitch Simulator:** Guided pitch deck creation with 8 sections and mentor scoring for different investor profiles.
-   **Learning Analytics Dashboard:** Tracks skill progress, identifies weak areas, and provides personalized recommendations.
-   **Achievement System:** Educational badges, mastery rewards, streak tracking, and scenario unlocks.
-   **Competitive Features:** Business competitions with league rankings, weekly challenges, and leaderboards.
-   **Advanced Simulations:** Includes M&A, international expansion, crisis management, and full business lifecycle simulation.
-   **Tutorial/Onboarding:** Guided tutorial system with progress tracking.
-   **Storyline Quest System:** Multi-chapter narrative arcs with branching decisions across different world themes.
-   **Mentorship & Advisor Progression:** Deep relationships with NPC advisors, affinity system, mentor missions, and skill tree unlocking.
-   **Business Network & Partnerships:** Player networking, joint ventures, networking events, and partnership management.
-   **Industry Specialization Tracks:** Deep-dive career paths for 5 industries with specific challenges and certifications.
-   **Dynamic Market Events:** Real-time economic events, market cycles, breaking news, and global community challenges.
-   **Multiplayer & Social:** Guild/alliance system, co-op challenges, player-to-player trading, and mentoring system.
-   **Seasonal Content:** Rotating weekly/monthly events, battle pass, limited-time boss challenges, and holiday events.
-   **AI Personalization:** Adaptive difficulty, AI-powered learning path recommendations, personalized scenario generation, and virtual business coach.
-   **Content Expansion:** New world themes, real-world business case studies, guest mentor NPCs, and deeper industry specialization.
-   **Accessibility & Polish:** PWA optimization, screen reader support, color blind modes, high contrast, reduced motion, and customizable font sizes.

**Technical Implementations:**
-   **Business Mastery Simulation:** Implements Capital, Team Morale, and Brand Equity tracking. Fiscal quarters advance with decisions, triggering quarterly events. Features a skill tree with 6 discipline-specific abilities.
-   **Explorable 2D RPG Map System:** HTML5 Canvas-based 2D tile engine with camera scrolling, player movement (arrow keys/WASD, mobile D-pad), collision detection, and sprite rendering. Includes a dialogue system, NPC interactions, and map transitions.
-   **Resource Integration & Feature Gating:** Server-side `check_feature_requirements()` and `deduct_feature_cost()` enforce resource costs. Uses `@feature_gated`, `@game_over_check`, and `@energy_required` decorators for route protection.
-   **Security & Infrastructure:** Bcrypt for password hashing, `@login_required` for route protection, PostgreSQL connection pooling, and request-scoped `GameEngine` instances.
-   **Mobile & Cross-Platform Support:** Full Progressive Web App (PWA) implementation for offline caching and "Add to Home Screen" functionality. Capacitor configuration for native iOS and Android builds. Responsive design enhancements for touch interactions, safe areas, and accessibility modes.

## External Dependencies
-   **PostgreSQL:** Relational database for all game data persistence.
-   **Flask-WTF:** Used for CSRF protection in web forms.
-   **bcrypt:** Industry-standard password hashing library.