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
- **Single-Page Canvas Game**: `templates/game.html` serves as the sole entry point; all gameplay happens on one full-screen HTML5 Canvas page
- **Game State Machine**: `static/js/rpg/game.js` is the master controller managing states: TITLE, CHAR_SELECT, LOGIN, WORLD, BATTLE, PAUSE_MENU
- **External Loop Pattern**: game.js owns the game loop; RPGEngine provides `externalUpdate(dt)` and `externalRender()` for WORLD state delegation
- **JSON API Backend**: All game data flows through `/api/*` endpoints (CSRF, players, create_player, login, stats, scenarios, play, choose, shop, buy)
- **Flask Blueprints**: Routes split into 7 blueprints (auth, core, scenarios, inventory, social, api, finance)
- **Mixin Pattern**: GameEngine uses ScenariosMixin, ProgressionMixin, SocialMixin for method organization
- **Backward Compatibility Shims**: `src/database.py` and `src/game_engine.py` re-export from their respective packages
- **Request-scoped Engine**: `get_engine()` creates per-request GameEngine instances via Flask's `g` object
- **IIFE + Namespace Pattern (JS)**: RPGColors, RPGTiles, RPGSprites, RPGEngine, Game are window globals

### Key Technical Details
- **Database**: PostgreSQL with connection pooling (ThreadedConnectionPool, 2-20 connections)
- **Security**: bcrypt password hashing, CSRF via Flask-WTF, JSON API uses X-CSRFToken header
- **2D Engine**: HTML5 Canvas, 16px tiles at 2x scale (32px), FF-style grid movement (180ms steps)
- **Sprite System**: 8 modern archetypes + 4 industrial characters (ind_accountant, ind_foreman, ind_engineer, ind_inventor); world-specific hero sprites
- **Character Selection**: 6-step creation wizard: Name → World → Industry → Career → Character Appearance → Confirm
- **Battle System**: Prodigy-style turn-based combat where business scenarios ARE the battles (correct answer = attack, wrong = take damage)
- **Game Flow**: Title Screen → Character Creation (with appearance picker) → World Exploration → NPC Interaction → Battle (scenario questions) → Victory/Defeat
- **url_for references**: Use blueprint prefix (e.g., `url_for('auth.index')`, `url_for('core.hub')`)

## Recent Changes (Feb 2026)
- **Canvas Game Overhaul**: Transformed from multi-page HTML to single-page full-canvas Prodigy-style RPG
  - Created `templates/game.html` as sole entry point (no base.html dependency)
  - Created `static/js/rpg/game.js` master state machine (TITLE, CHAR_SELECT, LOGIN, WORLD, BATTLE, PAUSE_MENU)
  - Added JSON API endpoints: `/api/csrf`, `/api/players`, `/api/create_player`, `/api/login`
  - RPGEngine extended with `externalUpdate()`, `externalRender()`, `handleKeyDown()`, `handleKeyUp()`
  - Title screen with animated tile background, FF-style menu panels
  - Character creation wizard (name → world → industry → career → confirm)
  - Turn-based battle system with HP bars, particles, damage feedback
  - Pause menu with Status/Skills/Items/Resume/Save&Quit
  - `Cache-Control: no-cache` added to HTML responses
- **Major Refactoring**: Split 4 monolithic files (23,000+ lines total) into modular packages
- Modern HD pixel art overhaul (Chrono Trigger SNES quality): organic shapes, rich gradients, vegetation detail
- Character sprite archetype system with diverse appearances
- **Image-Based Tile System**: Replaced ~900 lines of procedural tile drawing with image-based renderer
  - 35 tile types total (29 original + 6 new: GRASS2, GRASS3, BRIDGE, COBBLE, STATUE, FENCE)
  - All tiles loaded as PNG images from `/static/images/tiles/`
  - Animated overlay effects for water, portal, fountain, lamp, fireplace, waterfall
  - Fallback colored rectangles if images fail to load
- **Expanded Maps**: Hub Town 80x65 tiles, Market District 60x50 tiles
  - Hub Town: winding river with bridges, tree clusters, gardens, lake, central fountain plaza, 16 NPCs
  - Market District: 4 market areas with stalls, central plaza, buildings, gardens, water features, 8 NPCs
  - Terrain variation system: grass variants, scattered flowers/rocks, deterministic seeding
- **No-Password Single Player**: Removed password authentication, players create/load without passwords
- **Industrial Age Expansion - The Iron Basin**:
  - 24 new procedural tile types (IDs 36-59): dirt, factory wall/roof/door/window, smokestack (animated smoke), railroad tracks (H/V/cross/curves), dock, pine tree, mountain/mountain base, gear (animated rotation), coal pile, iron fence, industrial lamp (animated flicker), warehouse, steam pipe, anvil, barrel, crane
  - Iron Basin map (80x70 tiles): mountains across top, pine forests flanking sides, factory district with 18+ factories, railway network with cross-junctions, harbor/docks along bottom, central town plaza with fountain
  - 16 industrial-era NPCs covering all business disciplines (Operations, Finance, Strategy, HR, Marketing, Legal)
  - World routing: players selecting "Industrial" world spawn in iron_basin map
  - Industrial Age asset spritesheets: `industrial_characters.png`, `industrial_npcs.png`, `iron_basin_map.png`

## External Dependencies
- **PostgreSQL:** Relational database for all game data persistence.
- **Flask-WTF:** Used for CSRF protection in web forms.
- **bcrypt:** Industry-standard password hashing library.
