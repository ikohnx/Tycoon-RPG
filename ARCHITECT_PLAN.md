# Business Tycoon RPG - Architecture Audit & Blueprint

**Audit Date:** December 24, 2025  
**Auditor Role:** Senior Game Systems Architect & Lead QA Engineer  
**Codebase:** Flask-based educational RPG with 138 routes, 85 templates, 6 src modules

---

## Executive Summary

The Business Tycoon RPG has substantial feature scope but suffers from **incomplete system integration**. Many game mechanics exist as UI-only implementations without backend enforcement. The core "Business Mastery Simulation" resource system (Capital, Morale, Brand Equity) is displayed but not meaningfully enforced in gameplay loops.

**Critical Finding:** Feature gating is purely cosmetic - routes don't verify requirements or deduct costs.

---

## CRITICAL Issues (App-Breaking / Core Mechanics Broken)

### C1. Feature Gating Has No Server-Side Enforcement
**Location:** `app.py` (all gated routes), `src/company_resources.py`  
**Problem:** The `FEATURE_REQUIREMENTS` dictionary defines costs (e.g., Battle Arena costs 10 Morale) and the hub template shows "disabled" buttons, but:
- Routes like `/battle_arena`, `/negotiation`, `/random_event` have no verification
- Players can directly navigate to URLs and bypass all gating
- No resources are ever deducted when features are used
**Impact:** Core game economy is non-functional; resources are meaningless  
**Fix Required:** Add `check_and_deduct_feature_cost(player_id, 'feature_name')` guard at start of each gated route

### C2. Game Over Condition Not Enforced
**Location:** `src/company_resources.py:check_game_over()`, `app.py` routes  
**Problem:** The `check_game_over()` function exists and returns `game_over: True` when brand_equity <= 0, but:
- Only `process_choice()` in game_engine.py checks this
- 90% of gameplay routes don't check game-over status
- Players can continue playing indefinitely after "bankruptcy"
**Impact:** No meaningful consequence for poor decisions  
**Fix Required:** Add middleware or decorator that checks game-over status on all gameplay routes

### C3. Quarterly Events Don't Display to Player
**Location:** `src/company_resources.py:record_decision()`, `app.py:make_choice()`  
**Problem:** The quarterly event system triggers via `record_decision()` → `advance_quarter()` → `trigger_quarterly_event()`, and events properly update resources, but:
- Return value `quarterly_event` is not passed to templates
- Player never sees what event occurred or why resources changed
- No UI feedback for quarter advancement
**Impact:** Core fiscal quarter mechanic is invisible to players  
**Fix Required:** Store quarterly event in session/flash and display in result.html or dedicated modal

### C4. Energy System Exists But Is Never Used
**Location:** `src/game_engine.py:get_player_energy()`, `app.py:hub()`  
**Problem:** A complete energy system exists with:
- `player_energy` database table
- Auto-recharge logic (1 energy per 5 minutes)
- UI display in hub.html
- But NO route checks or deducts energy before actions
**Impact:** Energy is purely cosmetic; no action gating  
**Fix Required:** Add `consume_energy(player_id, amount)` checks to scenario/challenge/battle routes

---

## FUNCTIONAL Issues (Non-Working Features / Broken Links)

### F1. Skill Tree Abilities Unlock But Don't Apply Consistently
**Location:** `src/company_resources.py:apply_ability_modifiers()`, `src/game_engine.py:process_choice()`  
**Problem:** 
- Abilities are unlocked based on subskill levels
- `apply_ability_modifiers()` calculates bonuses (e.g., 1.5x revenue for Viral Campaign)
- Modifiers are applied in `process_choice()` but not in other systems
- Battle arena, negotiations, challenges don't use ability modifiers
**Impact:** Skill tree feels disconnected from most gameplay  
**Fix:** Apply ability modifiers consistently across all reward-granting routes

### F2. Equipment Stats Don't Affect Gameplay
**Location:** `app.py:equipment()`, `src/game_engine.py:equip_item()`  
**Problem:**
- Equipment can be purchased and equipped to slots
- Items have stat bonuses (charisma, intelligence, luck, negotiation)
- Player stats exist and are tracked in `player_stats` table
- But stats are never used in any game calculations
**Impact:** Equipment system is cosmetic only  
**Fix:** Integrate stats into scenario outcomes, battle calculations, and challenge success rates

### F3. Inventory Items Have No Use
**Location:** `app.py:inventory()`, `src/game_engine.py:get_shop_items()`  
**Problem:**
- Shop sells items that go to inventory
- Inventory displays owned items
- No "use item" functionality exists
- No item effects are implemented
**Impact:** Shop purchases feel meaningless  
**Fix:** Implement item consumption system with actual effects

### F4. Prestige System Gating Only on UI Side
**Location:** `app.py:prestige()`, `templates/hub.html`  
**Problem:**
- Hub shows Prestige locked (requires 80% Brand HP)
- `/prestige` route has no server-side brand check
- `perform_prestige()` can be called regardless of brand level
**Impact:** Prestige requirement can be bypassed  
**Fix:** Add brand_equity >= 80 check in `perform_prestige()` route

### F5. disabled Class on Buttons Doesn't Prevent Navigation
**Location:** `templates/hub.html`  
**Problem:**
- Buttons use `class="disabled"` but are still `<a href>` links
- CSS makes them look disabled but clicking still navigates
- No `pointer-events: none` or `onclick="return false"`
**Impact:** UI gating is purely visual  
**Fix:** Add `onclick="return false"` or use JavaScript to prevent click when disabled

### F6. Missing Error Handling on Database Operations
**Location:** `app.py` (138 routes), `src/game_engine.py`  
**Problem:**
- Only 7 try/except blocks in entire app.py
- Database errors can crash the application
- Connection pool exhaustion not gracefully handled
**Impact:** Poor user experience on errors; potential data loss  
**Fix:** Add try/except with user-friendly error messages to critical routes

### F7. Rival Battle System Incomplete
**Location:** `app.py:battle_rival()`, `templates/battle_arena.html`  
**Problem:**
- Battle arena lists rivals
- Battle logic exists but outcome calculations are simplistic
- No integration with player stats or equipment bonuses
- Win/loss doesn't meaningfully affect resources
**Impact:** Combat feels random and disconnected  
**Fix:** Wire stats/equipment into battle formula; add meaningful rewards/penalties

### F8. Daily Missions Progress Not Tracked Automatically
**Location:** `app.py:daily_missions()`, `src/game_engine.py`  
**Problem:**
- Daily missions are seeded with requirements (e.g., "Complete 3 Marketing scenarios")
- Mission progress is not automatically updated when player completes scenarios
- Manual claim exists but progress tracking is missing
**Impact:** Missions don't reflect actual gameplay  
**Fix:** Hook scenario completion into mission progress tracking

---

## POLISH Issues (Gameplay Balance / UI Improvements / Technical Debt)

### P1. 392 LSP Diagnostics in Core Files
**Location:** `src/database.py` (251), `src/company_resources.py` (141)  
**Problem:** High volume of type/syntax warnings  
**Fix:** Run type checker, fix unused imports, add type hints

### P2. Connection Pool Return Consistency
**Location:** `src/database.py`, all modules using `get_connection()`  
**Problem:**
- 14 `get_connection()` calls found
- 6 `return_connection()` calls found
- Mismatch suggests potential connection leaks
**Fix:** Audit all database access patterns; prefer `with db_cursor()` context manager

### P3. Inconsistent Resource Key Naming
**Location:** `src/company_resources.py`  
**Problem:**
- Database column is `team_morale`
- Dictionary key is sometimes `morale`, sometimes `team_morale`
- Recently fixed in `get_feature_access()` but may exist elsewhere
**Fix:** Standardize on one naming convention throughout

### P4. Scenario Star Rating System Not Visible
**Location:** `src/game_engine.py`, `templates/result.html`  
**Problem:**
- Star ratings (1-3) are calculated and stored
- Result template doesn't display earned stars
- No star collection overview exists
**Fix:** Add star display to result page and collection view

### P5. No Visual Feedback for Resource Changes
**Location:** `templates/base.html` (HUD navbar)  
**Problem:**
- Resources update in database but HUD shows static values
- No animation or notification when resources change
- Players don't understand cause/effect of decisions
**Fix:** Add JavaScript for resource change animations; show delta values

### P6. Tutorial/Onboarding Incomplete
**Location:** `app.py:tutorial()`, `templates/tutorial.html`  
**Problem:**
- Tutorial route exists with 6 sections
- Only basic completion tracking
- No guided walkthrough of new resource system
**Fix:** Update tutorial to cover Command HUD, feature gating, skill tree

### P7. Leaderboard Shows Outdated Metrics
**Location:** `app.py:leaderboard()`, `src/game_engine.py:get_leaderboard()`  
**Problem:**
- Leaderboard ranks by total_cash
- Doesn't factor in Brand Equity, Quarter progress, or Prestige level
- Misleading ranking for "Business Mastery Simulation"
**Fix:** Create composite score factoring all three resources + prestige

### P8. World Theme Differences Are Cosmetic Only
**Location:** `templates/hub.html`, `content/scenarios.json`  
**Problem:**
- Four worlds exist (Modern, Industrial, Fantasy, Sci-Fi)
- Same mechanics and scenarios across all worlds
- Only background images differ
**Fix:** Add world-specific events, scenario variations, or resource modifiers

### P9. Advisor Affinity System Underutilized
**Location:** `src/database.py:player_advisor_relationships`  
**Problem:**
- Affinity tracking table exists
- No meaningful gameplay impact from affinity levels
- Advisor bonuses not applied to relevant disciplines
**Fix:** Implement affinity-based bonuses and unlock special advisor missions

### P10. Missing Rate Limiting on Sensitive Routes
**Location:** `app.py:new_game()`, `app.py:load_game()`  
**Problem:**
- No rate limiting on authentication attempts
- Potential for brute force attacks on passwords
**Fix:** Add rate limiting decorator or integrate Flask-Limiter

---

## Recommended Priority Order

### Phase 1: Critical Fixes (Required for Core Gameplay)
1. **C1** - Add server-side feature cost verification and deduction
2. **C2** - Enforce game-over checks on all gameplay routes
3. **F5** - Fix disabled buttons to actually prevent navigation
4. **C4** - Implement energy consumption on actions

### Phase 2: System Integration (Makes Features Meaningful)
1. **C3** - Display quarterly events to players
2. **F1** - Apply skill tree abilities across all systems
3. **F2** - Wire equipment stats into gameplay calculations
4. **F4** - Add server-side prestige requirements

### Phase 3: Polish & Balance (Enhances Experience)
1. **P5** - Add resource change animations
2. **P1** - Fix LSP diagnostics
3. **P2** - Standardize connection pool usage
4. **F6** - Add error handling throughout

---

## Technical Debt Summary

| Category | Count | Severity |
|----------|-------|----------|
| Server-side validation missing | 12+ routes | Critical |
| Database connection handling | ~8 potential leaks | Medium |
| Error handling gaps | 130+ routes | Medium |
| Type/lint issues | 392 diagnostics | Low |
| Incomplete feature integration | 8 systems | Medium |

---

## Files Requiring Changes

| File | Priority | Changes Needed |
|------|----------|----------------|
| `app.py` | CRITICAL | Add server-side guards to gated routes |
| `src/company_resources.py` | CRITICAL | Add `check_and_deduct_cost()` function |
| `src/game_engine.py` | CRITICAL | Add `consume_energy()`, game-over checks |
| `templates/hub.html` | FUNCTIONAL | Fix disabled button click prevention |
| `templates/result.html` | FUNCTIONAL | Display quarterly events |
| `src/database.py` | POLISH | Standardize connection handling |

---

## Next Steps

**DO NOT MODIFY CODE** until user approves this plan.

Upon approval:
1. Start with C1 (feature gating enforcement) as it touches the most systems
2. Create reusable decorators/helpers for common checks
3. Test each fix in isolation before moving to next
4. Update replit.md with architectural changes

---

*This audit represents the current state as of December 24, 2025.*
