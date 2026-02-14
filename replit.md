# Business Tycoon RPG

## Overview
Business Tycoon RPG is a 2D educational role-playing game developed with Python/Flask. Its primary purpose is to impart practical business skills through engaging, scenario-based gameplay. The game covers six core business disciplines and eight transferable sub-skills, each with a 10-level progression system. The vision is to create an immersive learning experience across diverse themed worlds (Modern, Industrial, Fantasy, Sci-Fi), ultimately preparing players for real-world business challenges.

## User Preferences
I prefer iterative development, with a focus on delivering functional, well-tested features in logical steps. Please ask for clarification if there are ambiguities, and propose solutions before implementing major changes. I value clear, concise explanations and prefer a collaborative approach where we discuss design choices.

## Project Architecture

### Directory Structure
```
├── app.py                     # Flask app factory (~60 lines) - creates app, registers blueprints
├── main.py                    # CLI game entry point
├── src/
│   ├── __init__.py
│   ├── database.py            # Backward-compat shim → imports from src.db
│   ├── game_engine.py         # Backward-compat shim → imports from src.engine
│   ├── ai_tutor.py            # AI-powered tutoring features
│   ├── company_resources.py   # Company resource management, skill trees, abilities
│   ├── leveling.py            # Level titles, progress bars, EXP calculations
│   ├── routes/                # Flask Blueprints (split from monolithic app.py)
│   │   ├── __init__.py
│   │   ├── helpers.py         # Shared decorators: login_required, feature_gated, game_over_check, energy_required, get_engine
│   │   ├── auth.py            # Blueprint 'auth': index, new_game, load_game, logout
│   │   ├── core.py            # Blueprint 'core': hub, explore, dashboard, progress, character, settings, campaign_map, etc.
│   │   ├── scenarios.py       # Blueprint 'scenarios': scenarios, play, training, challenges, events
│   │   ├── inventory.py       # Blueprint 'inventory': shop, buy, equipment, prestige
│   │   ├── social.py          # Blueprint 'social': npcs, quests, rivals, guilds, trading, seasons, etc.
│   │   ├── api.py             # Blueprint 'api' (url_prefix=/api): stats, scenarios, shop, buy, play, choose
│   │   └── finance.py         # Blueprint 'finance': accounting, scheduling, cashflow, negotiation, risks, etc.
│   ├── db/                    # Database package (split from monolithic database.py)
│   │   ├── __init__.py        # Re-exports all public functions for backward compat
│   │   ├── connection.py      # Connection pool, get_connection, return_connection, db_cursor
│   │   ├── schema.py          # init_database with all CREATE TABLE statements
│   │   ├── seed.py            # All seed_* functions and seed_all
│   │   └── queries.py         # Chart of accounts, accounting init, project templates
│   └── engine/                # Game engine package (split from monolithic game_engine.py)
│       ├── __init__.py        # Re-exports all classes/functions for backward compat
│       ├── player.py          # Player class, ADVISOR_QUOTES, get_random_advisor_quote
│       ├── core.py            # GameEngine class (inherits mixins), core methods
│       ├── scenarios.py       # ScenariosMixin: scenario loading, processing, challenges
│       ├── progression.py     # ProgressionMixin: daily login, idle income, prestige, battles
│       ├── social.py          # SocialMixin: shop, NPCs, quests, achievements, avatars
│       └── accounting.py      # Standalone functions: accounting, projects, scheduling, etc.
├── static/
│   ├── js/
│   │   ├── rpg/               # 2D RPG engine (split from monolithic engine.js)
│   │   │   ├── colors.js      # Color palette (C) and utilities (hexToHSL, hslHex, shade)
│   │   │   ├── tiles.js       # Tile rendering (drawTile, dither, ditherFast) - 29 tile types
│   │   │   ├── sprites.js     # Sprite system (drawSprite, archetypes, skin/hair/eye variety)
│   │   │   ├── engine.js      # Core engine (game loop, input, camera, dialogue, HUD, overlays)
│   │   │   └── maps.js        # Map definitions (hub town, market district)
│   │   └── game-effects.js    # UI effects for non-RPG pages
│   ├── icons/                 # PWA icons
│   ├── images/                # Game artwork
│   ├── manifest.json          # PWA manifest
│   └── sw.js                  # Service worker
└── templates/                 # Jinja2 templates organized by feature
    ├── auth/                  # Authentication: index, login, new_game (3 files)
    ├── core/                  # Core pages: base, hub, explore, dashboard, etc. (13 files)
    ├── scenarios/             # Gameplay: scenarios, play, training, result, etc. (7 files)
    ├── inventory/             # Items: shop, inventory, equipment, prestige (4 files)
    ├── social/                # Social: npcs, quests, guilds, trading, etc. (28 files)
    └── finance/               # Business tools: accounting, scheduling, etc. (30 files)
```

### Architecture Patterns
- **Flask Blueprints**: Routes split into 7 blueprints (auth, core, scenarios, inventory, social, api, finance)
- **Mixin Pattern**: GameEngine uses ScenariosMixin, ProgressionMixin, SocialMixin for method organization
- **Backward Compatibility Shims**: `src/database.py` and `src/game_engine.py` re-export from their respective packages
- **Request-scoped Engine**: `get_engine()` creates per-request GameEngine instances via Flask's `g` object
- **IIFE + Namespace Pattern (JS)**: RPGColors, RPGTiles, RPGSprites are window globals consumed by RPGEngine
- **Template Organization**: 85 templates in 6 feature subdirectories, all extending `core/base.html`

### Key Technical Details
- **Database**: PostgreSQL with connection pooling (ThreadedConnectionPool, 2-20 connections)
- **Security**: bcrypt password hashing, CSRF via Flask-WTF, @login_required decorator
- **2D Engine**: HTML5 Canvas, 16px tiles at 3x scale (48px), FF-style grid movement (180ms steps)
- **Sprite System**: 8 archetypes (merchant, scholar, elder, warrior, scout, noble, artisan, mystic), 6 skin tones, 8 hair colors/styles, modular rendering (drawHair, drawFace, drawOutfit, drawAcc, etc.)
- **url_for references**: Use blueprint prefix (e.g., `url_for('auth.index')`, `url_for('core.hub')`)

## Recent Changes (Feb 2026)
- **Major Refactoring**: Split 4 monolithic files (23,000+ lines total) into modular packages:
  - app.py (3,278→59 lines) → 7 Flask Blueprints in src/routes/
  - database.py (9,405→1 line shim) → src/db/ package (connection, schema, seed, queries)
  - game_engine.py (8,125→8 line shim) → src/engine/ package (player, core, scenarios, progression, social, accounting)
  - engine.js (2,992→754 lines) → 4 JS modules (colors, tiles, sprites, engine)
- **Template Organization**: 85 templates moved from flat directory into 6 feature subdirectories
- Modern HD pixel art overhaul (Sea of Stars quality): organic shapes, rich gradients, vegetation detail
- Character sprite archetype system with diverse appearances
- In-game overlay system replacing page redirects
- FF-style pause menu and HUD auto-updates

## External Dependencies
- **PostgreSQL:** Relational database for all game data persistence.
- **Flask-WTF:** Used for CSRF protection in web forms.
- **bcrypt:** Industry-standard password hashing library.
