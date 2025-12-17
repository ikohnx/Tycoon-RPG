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

## External Dependencies
-   **PostgreSQL:** Relational database for all game data persistence.
-   **Flask-WTF:** Used for CSRF protection in web forms.