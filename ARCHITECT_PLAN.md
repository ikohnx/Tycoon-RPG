# Business Tycoon RPG - Architecture Audit & Remediation Plan

**Audit Date:** December 24, 2025  
**Auditor Role:** Senior Game Systems Architect & Lead QA Engineer

---

## Executive Summary

This audit identified **3 Critical**, **6 Functional**, and **5 Polish** issues across the codebase. The game has a solid foundation but suffers from:
- Database connection fragility
- Partially implemented features exposed in UI
- Progression data not persisting correctly
- Several dead-end navigation paths

---

## CRITICAL Issues (App-Breaking)

### C1: Database Initialization Crash on Missing DATABASE_URL
**Location:** `src/database.py`, module-level initialization  
**Issue:** `init_database()` and `seed_all()` run at module import without guarding for missing environment variables or connection failures. If DATABASE_URL is unset, the entire app crashes on import.  
**Impact:** Application cannot start  
**Fix:** Add lazy initialization with try/except and fallback messaging

### C2: GameEngine Database Connections Not Properly Released
**Location:** `src/game_engine.py`, multiple methods  
**Issue:** DB interactions lack proper error handling. Any database hiccup bubbles up and leaves pooled connections open, risking connection exhaustion and crashes.  
**Impact:** Connection pool exhaustion, app becomes unresponsive  
**Fix:** Wrap all DB calls with context managers/finally blocks to guarantee `return_connection()` is called

### C3: Missing Flask Routes for UI Elements (404 Errors)
**Location:** `app.py`, `templates/hub.html`, `templates/campaign_map.html`  
**Issue:** Several hub/campaign links point to templates without corresponding Flask routes:
- Boss challenges button on campaign map
- Some advisor interaction routes
- Inventory management routes
- Combat arena links  
**Impact:** Players encounter 404 errors, breaking progression flow  
**Fix:** Either implement missing routes or hide/disable buttons until implemented

---

## FUNCTIONAL Issues (Non-Working Features)

### F1: Learning Path Server-Side Validation Missing
**Location:** `templates/mentorship_lesson.html`, `app.py`  
**Issue:** Learning flow unlock logic is entirely client-side. The practice answer check enables "Continue" even on failure. No server validation means players can bypass lessons, and path completion can desync with database.  
**Impact:** Players can skip learning content; progress tracking unreliable  
**Fix:** Add server-side validation for practice answers before marking lessons complete

### F2: Non-Marketing Disciplines Have Dead-End Campaign Maps
**Location:** `app.py` campaign route, database seeding  
**Issue:** Campaign map node unlock state depends on data not properly seeded for all disciplines. Marketing is the only fully wired path—other disciplines (Finance, Operations, HR, Legal, Strategy) render as locked forever.  
**Impact:** Players cannot progress in 5 of 6 disciplines  
**Fix:** Ensure all disciplines have proper learning paths, scenarios, and unlock conditions seeded

### F3: EXP/Leveling Stats Don't Persist After Level-Up
**Location:** `src/game_engine.py`, level-up methods  
**Issue:** EXP grants ignore discipline weighting for some scenarios. Stat allocations from level-ups don't persist back to DB (missing UPDATE queries). Players lose earned progress on page refresh.  
**Impact:** Player progression resets; frustrating UX  
**Fix:** Add proper UPDATE queries after level calculations

### F4: Learning Path Progress Not Synced Across Tables
**Location:** `src/database.py`, progress tracking  
**Issue:** Progress is tracked in both `player_learning_path_progress` and `completed_scenarios` tables, but queries don't consistently check both, leading to status display mismatches.  
**Impact:** Confusing UI showing different completion states  
**Fix:** Consolidate progress queries to use COALESCE across both tables consistently

### F5: Energy/Stamina System Not Enforced
**Location:** `src/game_engine.py`, scenario routes  
**Issue:** Energy/stamina values exist in player stats but aren't deducted or checked when playing scenarios. Players have unlimited actions.  
**Impact:** Game balance broken; no pacing mechanism  
**Fix:** Implement energy checks before scenario play and regeneration over time

### F6: Daily Login Rewards Not Triggering
**Location:** `app.py`, `src/game_engine.py`  
**Issue:** Daily login reward logic exists but isn't wired to any route or triggered on login. The feature is invisible to players.  
**Impact:** Missing engagement feature  
**Fix:** Wire daily rewards to login flow or hub display

---

## POLISH Issues (Balance & UX)

### P1: Economy System Inactive
**Location:** `src/game_engine.py`, financial methods  
**Issue:** Starting cash never changes because income/expense events aren't wired to gameplay. Business simulation feels static.  
**Impact:** Core gameplay loop feels hollow  
**Fix:** Wire financial transactions to scenario outcomes

### P2: Inventory/Equipment System Empty
**Location:** `templates/inventory.html` (if exists), hub links  
**Issue:** Inventory menu exists but item list is always empty. No loot drops or equipment acquisition is implemented.  
**Impact:** Dead feature visible in UI  
**Fix:** Either implement loot system or hide inventory button until ready

### P3: Boss Challenge Button Without Implementation
**Location:** `templates/campaign_map.html`  
**Issue:** Boss challenge skull button is visible but has no route/logic. Clicking it errors.  
**Impact:** Broken UI element  
**Fix:** Conditionally hide button until feature is implemented

### P4: Advisor Affinity System Not Progressing
**Location:** `src/game_engine.py`, advisor methods  
**Issue:** Advisor affinity values exist but don't increase from player interactions. Mentor relationships feel static.  
**Impact:** Missing progression loop  
**Fix:** Add affinity gains to lesson completions and scenario choices

### P5: Tutorial/Onboarding Incomplete
**Location:** `templates/tutorial.html`, onboarding tracking  
**Issue:** Tutorial system tracks 6 sections but some sections have no content or lead to 404s.  
**Impact:** New player confusion  
**Fix:** Complete tutorial content or simplify to working sections only

---

## Recommended Fix Priority

### Phase 1: Stabilization (Critical)
1. Add guarded database initialization with lazy connect
2. Implement proper connection pooling hygiene (try/finally/return_connection)
3. Map all exposed UI endpoints to actual routes OR hide/disable buttons

### Phase 2: Core Loop (Functional)
1. Fix learning path progression persistence
2. Seed all 6 disciplines with proper content
3. Implement EXP/stat persistence on level-up
4. Add server-side validation for practice questions

### Phase 3: Polish
1. Wire economy to gameplay
2. Hide unimplemented features (inventory, boss battles)
3. Complete advisor affinity system

---

## Files Requiring Changes

| File | Priority | Changes Needed |
|------|----------|----------------|
| `src/database.py` | CRITICAL | Lazy init, error handling |
| `src/game_engine.py` | CRITICAL | Connection handling, stat persistence |
| `app.py` | CRITICAL/FUNCTIONAL | Missing routes, validation |
| `templates/hub.html` | FUNCTIONAL | Hide dead-end buttons |
| `templates/campaign_map.html` | FUNCTIONAL | Conditional rendering |
| `templates/mentorship_lesson.html` | FUNCTIONAL | Server validation |

---

**Awaiting approval to proceed with implementation.**
