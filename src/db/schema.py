from .connection import get_connection, return_connection


def init_database():
    """Initialize all database tables for the Business Tycoon RPG."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_profiles (
            player_id SERIAL PRIMARY KEY,
            player_name VARCHAR(100) NOT NULL,
            password_hash VARCHAR(255),
            chosen_world VARCHAR(50) NOT NULL DEFAULT 'Modern',
            chosen_industry VARCHAR(100) NOT NULL DEFAULT 'Restaurant',
            career_path VARCHAR(50) NOT NULL DEFAULT 'entrepreneur',
            job_title VARCHAR(100) DEFAULT NULL,
            job_level INTEGER DEFAULT 1,
            total_cash DECIMAL(15, 2) DEFAULT 10000.00,
            business_reputation INTEGER DEFAULT 50,
            current_month INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_played TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cur.execute("""
        ALTER TABLE player_profiles 
        ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);
    """)
    
    cur.execute("""
        ALTER TABLE player_profiles 
        ADD COLUMN IF NOT EXISTS career_path VARCHAR(50) NOT NULL DEFAULT 'entrepreneur';
    """)
    
    cur.execute("""
        ALTER TABLE player_profiles 
        ADD COLUMN IF NOT EXISTS job_title VARCHAR(100) DEFAULT NULL;
    """)
    
    cur.execute("""
        ALTER TABLE player_profiles 
        ADD COLUMN IF NOT EXISTS job_level INTEGER DEFAULT 1;
    """)
    
    cur.execute("""
        ALTER TABLE player_profiles 
        ADD COLUMN IF NOT EXISTS onboarding_seen BOOLEAN DEFAULT FALSE;
    """)
    
    cur.execute("""
        ALTER TABLE player_profiles 
        ADD COLUMN IF NOT EXISTS team_morale INTEGER DEFAULT 100;
    """)
    
    cur.execute("""
        ALTER TABLE player_profiles 
        ADD COLUMN IF NOT EXISTS brand_equity INTEGER DEFAULT 100;
    """)
    
    cur.execute("""
        ALTER TABLE player_profiles 
        ADD COLUMN IF NOT EXISTS fiscal_quarter INTEGER DEFAULT 1;
    """)
    
    cur.execute("""
        ALTER TABLE player_profiles 
        ADD COLUMN IF NOT EXISTS decisions_this_quarter INTEGER DEFAULT 0;
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_discipline_progress (
            progress_id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            discipline_name VARCHAR(100) NOT NULL,
            current_level INTEGER DEFAULT 1,
            current_exp INTEGER DEFAULT 0,
            total_exp_earned INTEGER DEFAULT 0,
            UNIQUE(player_id, discipline_name)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_subskill_progress (
            subskill_id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            subskill_name VARCHAR(100) NOT NULL,
            parent_discipline VARCHAR(100) NOT NULL,
            current_level INTEGER DEFAULT 1,
            current_exp INTEGER DEFAULT 0,
            UNIQUE(player_id, subskill_name)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS skill_tree_abilities (
            ability_id SERIAL PRIMARY KEY,
            discipline VARCHAR(100) NOT NULL,
            prerequisite_subskill VARCHAR(100) NOT NULL,
            ability_name VARCHAR(100) NOT NULL,
            ability_code VARCHAR(50) UNIQUE NOT NULL,
            description TEXT NOT NULL,
            effect_type VARCHAR(50) NOT NULL,
            effect_value DECIMAL(10, 2) DEFAULT 1.0,
            unlock_level INTEGER DEFAULT 3,
            icon VARCHAR(50) DEFAULT 'star'
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_unlocked_abilities (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            ability_id INTEGER REFERENCES skill_tree_abilities(ability_id) ON DELETE CASCADE,
            unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            times_used INTEGER DEFAULT 0,
            last_used_quarter INTEGER,
            is_active BOOLEAN DEFAULT FALSE,
            UNIQUE(player_id, ability_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS quarterly_events (
            event_id SERIAL PRIMARY KEY,
            event_type VARCHAR(50) NOT NULL,
            event_title VARCHAR(200) NOT NULL,
            event_description TEXT NOT NULL,
            capital_impact DECIMAL(10, 2) DEFAULT 0,
            morale_impact INTEGER DEFAULT 0,
            brand_impact INTEGER DEFAULT 0,
            exp_multiplier DECIMAL(5, 2) DEFAULT 1.0,
            target_discipline VARCHAR(100),
            is_crisis BOOLEAN DEFAULT FALSE,
            probability DECIMAL(3, 2) DEFAULT 0.5
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_quarterly_history (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            quarter_number INTEGER NOT NULL,
            capital_start DECIMAL(15, 2),
            capital_end DECIMAL(15, 2),
            morale_start INTEGER,
            morale_end INTEGER,
            brand_start INTEGER,
            brand_end INTEGER,
            decisions_made INTEGER DEFAULT 0,
            events_triggered JSONB DEFAULT '[]',
            abilities_used JSONB DEFAULT '[]',
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(player_id, quarter_number)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS news_ticker (
            news_id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            news_text TEXT NOT NULL,
            news_type VARCHAR(50) DEFAULT 'info',
            related_discipline VARCHAR(100),
            capital_change DECIMAL(10, 2),
            morale_change INTEGER,
            brand_change INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS scenario_master (
            scenario_id SERIAL PRIMARY KEY,
            world_type VARCHAR(50) NOT NULL,
            industry VARCHAR(100) NOT NULL,
            discipline VARCHAR(100) NOT NULL,
            required_level INTEGER NOT NULL,
            scenario_title VARCHAR(255) NOT NULL,
            scenario_narrative TEXT NOT NULL,
            choice_a_text TEXT NOT NULL,
            choice_a_exp_reward INTEGER NOT NULL,
            choice_a_cash_change DECIMAL(10, 2) DEFAULT 0,
            choice_a_reputation_change INTEGER DEFAULT 0,
            choice_a_feedback TEXT NOT NULL,
            choice_b_text TEXT NOT NULL,
            choice_b_exp_reward INTEGER NOT NULL,
            choice_b_cash_change DECIMAL(10, 2) DEFAULT 0,
            choice_b_reputation_change INTEGER DEFAULT 0,
            choice_b_feedback TEXT NOT NULL,
            choice_c_text TEXT,
            choice_c_exp_reward INTEGER DEFAULT 0,
            choice_c_cash_change DECIMAL(10, 2) DEFAULT 0,
            choice_c_reputation_change INTEGER DEFAULT 0,
            choice_c_feedback TEXT,
            subskill_focus VARCHAR(100),
            storyline_arc VARCHAR(100),
            is_active BOOLEAN DEFAULT TRUE
        );
    """)
    
    cur.execute("""
        ALTER TABLE scenario_master ADD COLUMN IF NOT EXISTS choice_a_morale_change INTEGER DEFAULT 0;
    """)
    cur.execute("""
        ALTER TABLE scenario_master ADD COLUMN IF NOT EXISTS choice_a_brand_change INTEGER DEFAULT 0;
    """)
    cur.execute("""
        ALTER TABLE scenario_master ADD COLUMN IF NOT EXISTS choice_b_morale_change INTEGER DEFAULT 0;
    """)
    cur.execute("""
        ALTER TABLE scenario_master ADD COLUMN IF NOT EXISTS choice_b_brand_change INTEGER DEFAULT 0;
    """)
    cur.execute("""
        ALTER TABLE scenario_master ADD COLUMN IF NOT EXISTS choice_c_morale_change INTEGER DEFAULT 0;
    """)
    cur.execute("""
        ALTER TABLE scenario_master ADD COLUMN IF NOT EXISTS choice_c_brand_change INTEGER DEFAULT 0;
    """)
    cur.execute("""
        ALTER TABLE scenario_master ADD COLUMN IF NOT EXISTS scenario_type VARCHAR(50) DEFAULT 'opportunity';
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS financial_metrics (
            metric_id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            month_number INTEGER NOT NULL,
            revenue DECIMAL(15, 2) DEFAULT 0,
            wages_cost DECIMAL(15, 2) DEFAULT 0,
            rent_cost DECIMAL(15, 2) DEFAULT 0,
            taxes_cost DECIMAL(15, 2) DEFAULT 0,
            other_costs DECIMAL(15, 2) DEFAULT 0,
            net_profit DECIMAL(15, 2) DEFAULT 0,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(player_id, month_number)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS completed_scenarios (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            scenario_id INTEGER REFERENCES scenario_master(scenario_id) ON DELETE CASCADE,
            choice_made CHAR(1) NOT NULL,
            stars_earned INTEGER DEFAULT 1,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(player_id, scenario_id)
        );
    """)
    
    cur.execute("""
        ALTER TABLE completed_scenarios 
        ADD COLUMN IF NOT EXISTS stars_earned INTEGER DEFAULT 1;
    """)
    
    cur.execute("""
        ALTER TABLE scenario_master 
        ADD COLUMN IF NOT EXISTS challenge_type VARCHAR(50) DEFAULT 'choice';
    """)
    
    cur.execute("""
        ALTER TABLE scenario_master 
        ADD COLUMN IF NOT EXISTS challenge_config TEXT DEFAULT NULL;
    """)
    
    cur.execute("""
        ALTER TABLE scenario_master 
        ADD COLUMN IF NOT EXISTS training_content TEXT DEFAULT NULL;
    """)
    
    # Mentorship system tables - require learning before quests
    cur.execute("""
        CREATE TABLE IF NOT EXISTS mentorship_modules (
            module_id SERIAL PRIMARY KEY,
            module_code VARCHAR(100) UNIQUE NOT NULL,
            module_title VARCHAR(255) NOT NULL,
            discipline VARCHAR(100) NOT NULL,
            required_level INTEGER DEFAULT 1,
            theory_content TEXT NOT NULL,
            key_concepts TEXT,
            formulas TEXT,
            real_world_example TEXT,
            practice_question TEXT,
            practice_answer TEXT,
            practice_explanation TEXT,
            mentor_name VARCHAR(100) DEFAULT 'Business Mentor',
            mentor_avatar VARCHAR(100) DEFAULT 'mentor_default',
            estimated_minutes INTEGER DEFAULT 5,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS scenario_mentorship (
            id SERIAL PRIMARY KEY,
            scenario_id INTEGER REFERENCES scenario_master(scenario_id) ON DELETE CASCADE,
            module_id INTEGER REFERENCES mentorship_modules(module_id) ON DELETE CASCADE,
            is_required BOOLEAN DEFAULT TRUE,
            UNIQUE(scenario_id, module_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_mentorship_progress (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            module_id INTEGER REFERENCES mentorship_modules(module_id) ON DELETE CASCADE,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            practice_score INTEGER DEFAULT 0,
            is_completed BOOLEAN DEFAULT FALSE,
            UNIQUE(player_id, module_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_stats (
            stat_id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            charisma INTEGER DEFAULT 5,
            intelligence INTEGER DEFAULT 5,
            luck INTEGER DEFAULT 5,
            negotiation INTEGER DEFAULT 5,
            stat_points_available INTEGER DEFAULT 3,
            UNIQUE(player_id)
        );
    """)
    
    # Mentor Trials - RPG-themed knowledge quizzes
    cur.execute("""
        CREATE TABLE IF NOT EXISTS mentor_trials (
            trial_id SERIAL PRIMARY KEY,
            trial_code VARCHAR(50) UNIQUE NOT NULL,
            trial_name VARCHAR(150) NOT NULL,
            mentor_name VARCHAR(100) NOT NULL,
            mentor_title VARCHAR(150),
            mentor_avatar VARCHAR(100) DEFAULT 'mentor_sage',
            discipline VARCHAR(100) NOT NULL,
            difficulty INTEGER DEFAULT 1,
            story_intro TEXT,
            story_success TEXT,
            story_fail TEXT,
            time_limit_seconds INTEGER DEFAULT 300,
            passing_score INTEGER DEFAULT 70,
            exp_reward INTEGER DEFAULT 50,
            gold_reward INTEGER DEFAULT 100,
            badge_code VARCHAR(50),
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS trial_questions (
            question_id SERIAL PRIMARY KEY,
            trial_id INTEGER REFERENCES mentor_trials(trial_id) ON DELETE CASCADE,
            question_text TEXT NOT NULL,
            question_context TEXT,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT,
            option_d TEXT,
            correct_answer CHAR(1) NOT NULL,
            explanation TEXT,
            points INTEGER DEFAULT 10,
            question_order INTEGER DEFAULT 1
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_trial_progress (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            trial_id INTEGER REFERENCES mentor_trials(trial_id) ON DELETE CASCADE,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            score INTEGER DEFAULT 0,
            max_score INTEGER DEFAULT 0,
            is_passed BOOLEAN DEFAULT FALSE,
            attempts INTEGER DEFAULT 0,
            best_score INTEGER DEFAULT 0,
            UNIQUE(player_id, trial_id)
        );
    """)
    
    # Merchant Puzzles - Interactive business calculators as challenges
    cur.execute("""
        CREATE TABLE IF NOT EXISTS merchant_puzzles (
            puzzle_id SERIAL PRIMARY KEY,
            puzzle_code VARCHAR(50) UNIQUE NOT NULL,
            puzzle_name VARCHAR(150) NOT NULL,
            merchant_name VARCHAR(100) NOT NULL,
            merchant_title VARCHAR(150),
            merchant_avatar VARCHAR(100) DEFAULT 'merchant_trader',
            discipline VARCHAR(100) NOT NULL,
            puzzle_type VARCHAR(50) NOT NULL,
            difficulty INTEGER DEFAULT 1,
            story_intro TEXT,
            story_success TEXT,
            challenge_data JSONB,
            formula_hint TEXT,
            time_limit_seconds INTEGER DEFAULT 180,
            exp_reward INTEGER DEFAULT 40,
            gold_reward INTEGER DEFAULT 150,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_puzzle_progress (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            puzzle_id INTEGER REFERENCES merchant_puzzles(puzzle_id) ON DELETE CASCADE,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            attempts INTEGER DEFAULT 0,
            best_time_seconds INTEGER,
            is_solved BOOLEAN DEFAULT FALSE,
            UNIQUE(player_id, puzzle_id)
        );
    """)
    
    # Learning badges
    cur.execute("""
        CREATE TABLE IF NOT EXISTS learning_badges (
            badge_id SERIAL PRIMARY KEY,
            badge_code VARCHAR(50) UNIQUE NOT NULL,
            badge_name VARCHAR(100) NOT NULL,
            badge_description TEXT,
            badge_icon VARCHAR(100) DEFAULT 'badge_star',
            badge_tier VARCHAR(20) DEFAULT 'bronze',
            discipline VARCHAR(100),
            requirement_type VARCHAR(50),
            requirement_count INTEGER DEFAULT 1,
            exp_bonus INTEGER DEFAULT 0
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_learning_badges (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            badge_id INTEGER REFERENCES learning_badges(badge_id) ON DELETE CASCADE,
            earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(player_id, badge_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS learning_paths (
            path_id SERIAL PRIMARY KEY,
            path_code VARCHAR(50) UNIQUE NOT NULL,
            path_name VARCHAR(150) NOT NULL,
            path_description TEXT,
            discipline VARCHAR(100) NOT NULL,
            difficulty INTEGER DEFAULT 1,
            lesson_module_id INTEGER,
            trial_id INTEGER,
            puzzle_id INTEGER,
            scenario_id INTEGER,
            exp_bonus INTEGER DEFAULT 100,
            gold_bonus INTEGER DEFAULT 200,
            badge_code VARCHAR(50),
            is_active BOOLEAN DEFAULT TRUE,
            sort_order INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_learning_path_progress (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            path_id INTEGER REFERENCES learning_paths(path_id) ON DELETE CASCADE,
            lesson_completed BOOLEAN DEFAULT FALSE,
            lesson_completed_at TIMESTAMP,
            trial_completed BOOLEAN DEFAULT FALSE,
            trial_completed_at TIMESTAMP,
            trial_score INTEGER,
            puzzle_completed BOOLEAN DEFAULT FALSE,
            puzzle_completed_at TIMESTAMP,
            puzzle_time_seconds INTEGER,
            scenario_completed BOOLEAN DEFAULT FALSE,
            scenario_completed_at TIMESTAMP,
            scenario_stars INTEGER,
            path_completed BOOLEAN DEFAULT FALSE,
            path_completed_at TIMESTAMP,
            bonus_claimed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(player_id, path_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ai_tutor_interactions (
            interaction_id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            path_id INTEGER,
            interaction_type VARCHAR(50) NOT NULL,
            question_context TEXT,
            player_answer TEXT,
            correct_answer TEXT,
            is_correct BOOLEAN,
            knowledge_gap TEXT,
            ai_feedback TEXT,
            remediation_content TEXT,
            model_used VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_knowledge_gaps (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            discipline VARCHAR(100) NOT NULL,
            concept VARCHAR(150) NOT NULL,
            gap_description TEXT,
            times_struggled INTEGER DEFAULT 1,
            last_struggled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            remediated BOOLEAN DEFAULT FALSE,
            remediated_at TIMESTAMP,
            UNIQUE(player_id, discipline, concept)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS achievements (
            achievement_id SERIAL PRIMARY KEY,
            achievement_code VARCHAR(50) UNIQUE NOT NULL,
            achievement_name VARCHAR(100) NOT NULL,
            achievement_description TEXT NOT NULL,
            achievement_icon VARCHAR(50) DEFAULT 'trophy',
            exp_reward INTEGER DEFAULT 0,
            cash_reward DECIMAL(10, 2) DEFAULT 0
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_achievements (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            achievement_id INTEGER REFERENCES achievements(achievement_id) ON DELETE CASCADE,
            earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(player_id, achievement_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS items (
            item_id SERIAL PRIMARY KEY,
            item_code VARCHAR(50) UNIQUE NOT NULL,
            item_name VARCHAR(100) NOT NULL,
            item_description TEXT NOT NULL,
            item_type VARCHAR(50) NOT NULL,
            item_icon VARCHAR(50) DEFAULT 'box',
            purchase_price DECIMAL(10, 2) DEFAULT 0,
            effect_type VARCHAR(50),
            effect_value INTEGER DEFAULT 0,
            is_consumable BOOLEAN DEFAULT FALSE
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_inventory (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            item_id INTEGER REFERENCES items(item_id) ON DELETE CASCADE,
            quantity INTEGER DEFAULT 1,
            acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(player_id, item_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS npcs (
            npc_id SERIAL PRIMARY KEY,
            npc_code VARCHAR(50) UNIQUE NOT NULL,
            npc_name VARCHAR(100) NOT NULL,
            npc_title VARCHAR(100),
            npc_description TEXT,
            npc_type VARCHAR(50) NOT NULL,
            world_type VARCHAR(50) NOT NULL,
            dialogue_intro TEXT,
            avatar_image VARCHAR(255)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_npc_relationships (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            npc_id INTEGER REFERENCES npcs(npc_id) ON DELETE CASCADE,
            relationship_level INTEGER DEFAULT 0,
            times_interacted INTEGER DEFAULT 0,
            last_interaction TIMESTAMP,
            UNIQUE(player_id, npc_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS quests (
            quest_id SERIAL PRIMARY KEY,
            quest_code VARCHAR(50) UNIQUE NOT NULL,
            quest_name VARCHAR(100) NOT NULL,
            quest_description TEXT NOT NULL,
            quest_type VARCHAR(50) NOT NULL,
            world_type VARCHAR(50) NOT NULL,
            required_level INTEGER DEFAULT 1,
            exp_reward INTEGER DEFAULT 0,
            cash_reward DECIMAL(10, 2) DEFAULT 0,
            reputation_reward INTEGER DEFAULT 0,
            prerequisite_quest_id INTEGER REFERENCES quests(quest_id),
            npc_giver_id INTEGER REFERENCES npcs(npc_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_quests (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            quest_id INTEGER REFERENCES quests(quest_id) ON DELETE CASCADE,
            status VARCHAR(50) DEFAULT 'available',
            progress INTEGER DEFAULT 0,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            UNIQUE(player_id, quest_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS random_events (
            event_id SERIAL PRIMARY KEY,
            event_code VARCHAR(50) UNIQUE NOT NULL,
            event_name VARCHAR(100) NOT NULL,
            event_description TEXT NOT NULL,
            event_type VARCHAR(50) NOT NULL,
            world_type VARCHAR(50) NOT NULL,
            industry VARCHAR(100),
            choice_a_text TEXT NOT NULL,
            choice_a_cash_change DECIMAL(10, 2) DEFAULT 0,
            choice_a_reputation_change INTEGER DEFAULT 0,
            choice_a_feedback TEXT NOT NULL,
            choice_b_text TEXT NOT NULL,
            choice_b_cash_change DECIMAL(10, 2) DEFAULT 0,
            choice_b_reputation_change INTEGER DEFAULT 0,
            choice_b_feedback TEXT NOT NULL,
            rarity VARCHAR(20) DEFAULT 'common',
            min_level INTEGER DEFAULT 1
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_event_history (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            event_id INTEGER REFERENCES random_events(event_id) ON DELETE CASCADE,
            choice_made CHAR(1) NOT NULL,
            occurred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS weekly_challenges (
            challenge_id SERIAL PRIMARY KEY,
            challenge_code VARCHAR(50) UNIQUE NOT NULL,
            challenge_name VARCHAR(100) NOT NULL,
            challenge_description TEXT NOT NULL,
            challenge_type VARCHAR(50) NOT NULL,
            target_value INTEGER NOT NULL,
            exp_reward INTEGER DEFAULT 0,
            cash_reward DECIMAL(10, 2) DEFAULT 0,
            start_date DATE,
            end_date DATE,
            is_active BOOLEAN DEFAULT TRUE
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_challenge_progress (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            challenge_id INTEGER REFERENCES weekly_challenges(challenge_id) ON DELETE CASCADE,
            current_progress INTEGER DEFAULT 0,
            completed BOOLEAN DEFAULT FALSE,
            completed_at TIMESTAMP,
            UNIQUE(player_id, challenge_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS avatar_options (
            option_id SERIAL PRIMARY KEY,
            option_type VARCHAR(50) NOT NULL,
            option_code VARCHAR(50) UNIQUE NOT NULL,
            option_name VARCHAR(100) NOT NULL,
            option_image VARCHAR(255),
            unlock_cost DECIMAL(10, 2) DEFAULT 0,
            unlock_level INTEGER DEFAULT 1
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_avatar (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            hair_style VARCHAR(50) DEFAULT 'default',
            outfit VARCHAR(50) DEFAULT 'default',
            accessory VARCHAR(50) DEFAULT 'none',
            color_scheme VARCHAR(50) DEFAULT 'blue',
            UNIQUE(player_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS rivals (
            rival_id SERIAL PRIMARY KEY,
            rival_code VARCHAR(50) UNIQUE NOT NULL,
            rival_name VARCHAR(100) NOT NULL,
            rival_business VARCHAR(100) NOT NULL,
            rival_description TEXT,
            world_type VARCHAR(50) NOT NULL,
            industry VARCHAR(100) NOT NULL,
            difficulty_level INTEGER DEFAULT 1,
            avatar_image VARCHAR(255)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_rival_status (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            rival_id INTEGER REFERENCES rivals(rival_id) ON DELETE CASCADE,
            competition_score INTEGER DEFAULT 0,
            times_beaten INTEGER DEFAULT 0,
            times_lost INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT TRUE,
            UNIQUE(player_id, rival_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS business_milestones (
            milestone_id SERIAL PRIMARY KEY,
            milestone_code VARCHAR(50) UNIQUE NOT NULL,
            milestone_name VARCHAR(100) NOT NULL,
            milestone_description TEXT NOT NULL,
            milestone_type VARCHAR(50) NOT NULL,
            target_value DECIMAL(15, 2) NOT NULL,
            exp_reward INTEGER DEFAULT 0,
            cash_reward DECIMAL(10, 2) DEFAULT 0,
            badge_icon VARCHAR(50) DEFAULT 'award'
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_milestones (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            milestone_id INTEGER REFERENCES business_milestones(milestone_id) ON DELETE CASCADE,
            achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(player_id, milestone_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_energy (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            current_energy INTEGER DEFAULT 100,
            max_energy INTEGER DEFAULT 100,
            last_recharge_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(player_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_daily_login (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            current_streak INTEGER DEFAULT 0,
            longest_streak INTEGER DEFAULT 0,
            last_login_date DATE,
            last_claim_date DATE,
            UNIQUE(player_id)
        );
    """)
    
    cur.execute("""
        ALTER TABLE player_daily_login ADD COLUMN IF NOT EXISTS current_streak INTEGER DEFAULT 0;
    """)
    cur.execute("""
        ALTER TABLE player_daily_login ADD COLUMN IF NOT EXISTS longest_streak INTEGER DEFAULT 0;
    """)
    cur.execute("""
        ALTER TABLE player_daily_login ADD COLUMN IF NOT EXISTS last_claim_date DATE;
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_prestige (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            prestige_level INTEGER DEFAULT 0,
            exp_multiplier DECIMAL(5, 2) DEFAULT 1.0,
            gold_multiplier DECIMAL(5, 2) DEFAULT 1.0,
            total_prestiges INTEGER DEFAULT 0,
            UNIQUE(player_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS daily_login_rewards (
            day_number INTEGER PRIMARY KEY,
            reward_type VARCHAR(50) NOT NULL,
            reward_value INTEGER NOT NULL,
            reward_description TEXT NOT NULL
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_idle_income (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            gold_per_minute DECIMAL(10, 2) DEFAULT 0,
            last_collection_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            uncollected_gold DECIMAL(15, 2) DEFAULT 0,
            UNIQUE(player_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS advisors (
            advisor_id SERIAL PRIMARY KEY,
            advisor_code VARCHAR(50) UNIQUE NOT NULL,
            advisor_name VARCHAR(100) NOT NULL,
            advisor_title VARCHAR(100) NOT NULL,
            advisor_description TEXT,
            discipline_specialty VARCHAR(100) NOT NULL,
            bonus_type VARCHAR(50) NOT NULL,
            bonus_value INTEGER DEFAULT 10,
            rarity VARCHAR(20) DEFAULT 'common',
            unlock_cost DECIMAL(10, 2) DEFAULT 0,
            avatar_image VARCHAR(255)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_advisors (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            advisor_id INTEGER REFERENCES advisors(advisor_id) ON DELETE CASCADE,
            level INTEGER DEFAULT 1,
            recruited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            UNIQUE(player_id, advisor_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS equipment (
            equipment_id SERIAL PRIMARY KEY,
            equipment_code VARCHAR(50) UNIQUE NOT NULL,
            equipment_name VARCHAR(100) NOT NULL,
            equipment_description TEXT,
            slot_type VARCHAR(50) NOT NULL,
            stat_bonus_type VARCHAR(50) NOT NULL,
            stat_bonus_value INTEGER DEFAULT 0,
            rarity VARCHAR(20) DEFAULT 'common',
            purchase_price DECIMAL(10, 2) DEFAULT 0,
            level_required INTEGER DEFAULT 1,
            icon_image VARCHAR(255)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_equipment (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            equipment_id INTEGER REFERENCES equipment(equipment_id) ON DELETE CASCADE,
            slot_type VARCHAR(50) NOT NULL,
            is_equipped BOOLEAN DEFAULT FALSE,
            acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(player_id, equipment_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_prestige (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            prestige_level INTEGER DEFAULT 0,
            exp_multiplier DECIMAL(5, 2) DEFAULT 1.0,
            gold_multiplier DECIMAL(5, 2) DEFAULT 1.0,
            total_prestiges INTEGER DEFAULT 0,
            last_prestige_at TIMESTAMP,
            UNIQUE(player_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS daily_missions (
            mission_id SERIAL PRIMARY KEY,
            mission_code VARCHAR(50) UNIQUE NOT NULL,
            mission_name VARCHAR(100) NOT NULL,
            mission_description TEXT NOT NULL,
            mission_type VARCHAR(50) NOT NULL,
            target_value INTEGER NOT NULL,
            exp_reward INTEGER DEFAULT 0,
            cash_reward DECIMAL(10, 2) DEFAULT 0,
            energy_reward INTEGER DEFAULT 0
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_daily_missions (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            mission_id INTEGER REFERENCES daily_missions(mission_id) ON DELETE CASCADE,
            current_progress INTEGER DEFAULT 0,
            completed BOOLEAN DEFAULT FALSE,
            assigned_date DATE DEFAULT CURRENT_DATE,
            completed_at TIMESTAMP,
            UNIQUE(player_id, mission_id, assigned_date)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS boss_scenarios (
            boss_id SERIAL PRIMARY KEY,
            scenario_id INTEGER REFERENCES scenario_master(scenario_id) ON DELETE CASCADE,
            boss_name VARCHAR(100) NOT NULL,
            boss_description TEXT,
            difficulty_rating INTEGER DEFAULT 5,
            bonus_exp_multiplier DECIMAL(3, 1) DEFAULT 2.0,
            bonus_cash_reward DECIMAL(10, 2) DEFAULT 0,
            world_type VARCHAR(50) NOT NULL,
            discipline VARCHAR(100) NOT NULL,
            required_level INTEGER NOT NULL,
            UNIQUE(scenario_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS leaderboard_cache (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            total_stars INTEGER DEFAULT 0,
            total_wealth DECIMAL(15, 2) DEFAULT 0,
            highest_discipline_level INTEGER DEFAULT 1,
            total_scenarios_completed INTEGER DEFAULT 0,
            rank_stars INTEGER,
            rank_wealth INTEGER,
            rank_level INTEGER,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(player_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS rival_battles (
            battle_id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            rival_id INTEGER REFERENCES rivals(rival_id) ON DELETE CASCADE,
            player_score INTEGER DEFAULT 0,
            rival_score INTEGER DEFAULT 0,
            winner VARCHAR(20),
            rewards_earned DECIMAL(10, 2) DEFAULT 0,
            battle_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Accounting System Tables
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chart_of_accounts (
            account_id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            account_code VARCHAR(20) NOT NULL,
            account_name VARCHAR(100) NOT NULL,
            account_type VARCHAR(20) NOT NULL CHECK (account_type IN ('Asset', 'Liability', 'Equity', 'Revenue', 'Expense')),
            normal_balance VARCHAR(10) NOT NULL CHECK (normal_balance IN ('Debit', 'Credit')),
            description TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(player_id, account_code)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS accounting_periods (
            period_id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            period_name VARCHAR(50) NOT NULL,
            period_number INTEGER NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            is_closed BOOLEAN DEFAULT FALSE,
            closed_at TIMESTAMP,
            closing_exp_earned INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(player_id, period_number)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS journal_entries (
            entry_id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            period_id INTEGER REFERENCES accounting_periods(period_id) ON DELETE SET NULL,
            entry_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            description TEXT NOT NULL,
            source_type VARCHAR(50),
            source_id INTEGER,
            is_posted BOOLEAN DEFAULT FALSE,
            is_adjusting BOOLEAN DEFAULT FALSE,
            is_closing BOOLEAN DEFAULT FALSE,
            total_debits DECIMAL(15, 2) DEFAULT 0,
            total_credits DECIMAL(15, 2) DEFAULT 0,
            exp_earned INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS journal_lines (
            line_id SERIAL PRIMARY KEY,
            entry_id INTEGER REFERENCES journal_entries(entry_id) ON DELETE CASCADE,
            account_id INTEGER REFERENCES chart_of_accounts(account_id) ON DELETE CASCADE,
            debit_amount DECIMAL(15, 2) DEFAULT 0,
            credit_amount DECIMAL(15, 2) DEFAULT 0,
            memo TEXT
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS account_balances (
            balance_id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            account_id INTEGER REFERENCES chart_of_accounts(account_id) ON DELETE CASCADE,
            period_id INTEGER REFERENCES accounting_periods(period_id) ON DELETE CASCADE,
            opening_balance DECIMAL(15, 2) DEFAULT 0,
            closing_balance DECIMAL(15, 2) DEFAULT 0,
            UNIQUE(account_id, period_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pending_transactions (
            transaction_id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            transaction_type VARCHAR(50) NOT NULL,
            description TEXT NOT NULL,
            amount DECIMAL(15, 2) NOT NULL,
            suggested_debit_account VARCHAR(20),
            suggested_credit_account VARCHAR(20),
            source_type VARCHAR(50),
            source_id INTEGER,
            is_processed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS project_initiatives (
            initiative_id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            world_type VARCHAR(50) DEFAULT 'Modern',
            industry VARCHAR(100),
            planned_duration_weeks INTEGER DEFAULT 4,
            actual_duration_weeks INTEGER DEFAULT 0,
            start_week INTEGER DEFAULT 1,
            current_week INTEGER DEFAULT 1,
            status VARCHAR(50) DEFAULT 'planning',
            budget DECIMAL(15, 2) DEFAULT 0,
            spent DECIMAL(15, 2) DEFAULT 0,
            completion_bonus_exp INTEGER DEFAULT 100,
            completion_bonus_cash DECIMAL(15, 2) DEFAULT 0,
            on_time_multiplier DECIMAL(3, 2) DEFAULT 1.5,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS project_tasks (
            task_id SERIAL PRIMARY KEY,
            initiative_id INTEGER REFERENCES project_initiatives(initiative_id) ON DELETE CASCADE,
            task_name VARCHAR(200) NOT NULL,
            description TEXT,
            estimated_effort_hours INTEGER DEFAULT 8,
            actual_effort_hours INTEGER DEFAULT 0,
            planned_start_week INTEGER DEFAULT 1,
            planned_end_week INTEGER DEFAULT 1,
            actual_start_week INTEGER,
            actual_end_week INTEGER,
            status VARCHAR(50) DEFAULT 'not_started',
            priority VARCHAR(20) DEFAULT 'medium',
            is_critical_path BOOLEAN DEFAULT FALSE,
            task_order INTEGER DEFAULT 0,
            exp_reward INTEGER DEFAULT 20,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS task_dependencies (
            dependency_id SERIAL PRIMARY KEY,
            task_id INTEGER REFERENCES project_tasks(task_id) ON DELETE CASCADE,
            depends_on_task_id INTEGER REFERENCES project_tasks(task_id) ON DELETE CASCADE,
            dependency_type VARCHAR(10) DEFAULT 'FS',
            lag_weeks INTEGER DEFAULT 0,
            UNIQUE(task_id, depends_on_task_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS project_resources (
            resource_id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            resource_name VARCHAR(100) NOT NULL,
            resource_type VARCHAR(50) DEFAULT 'staff',
            capacity_hours_per_week INTEGER DEFAULT 40,
            hourly_cost DECIMAL(10, 2) DEFAULT 25,
            skill_bonus INTEGER DEFAULT 0,
            is_available BOOLEAN DEFAULT TRUE
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS task_resource_assignments (
            assignment_id SERIAL PRIMARY KEY,
            task_id INTEGER REFERENCES project_tasks(task_id) ON DELETE CASCADE,
            resource_id INTEGER REFERENCES project_resources(resource_id) ON DELETE CASCADE,
            hours_allocated INTEGER DEFAULT 8,
            hours_worked INTEGER DEFAULT 0,
            UNIQUE(task_id, resource_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS project_history (
            history_id SERIAL PRIMARY KEY,
            initiative_id INTEGER REFERENCES project_initiatives(initiative_id) ON DELETE CASCADE,
            week_number INTEGER NOT NULL,
            planned_completion_pct DECIMAL(5, 2) DEFAULT 0,
            actual_completion_pct DECIMAL(5, 2) DEFAULT 0,
            variance_pct DECIMAL(5, 2) DEFAULT 0,
            notes TEXT,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS scheduling_challenges (
            challenge_id SERIAL PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            challenge_type VARCHAR(50) NOT NULL,
            difficulty INTEGER DEFAULT 1,
            world_type VARCHAR(50) DEFAULT 'Modern',
            required_level INTEGER DEFAULT 1,
            task_data JSONB,
            correct_answer JSONB,
            exp_reward INTEGER DEFAULT 50,
            time_limit_seconds INTEGER DEFAULT 300,
            hint_text TEXT,
            is_active BOOLEAN DEFAULT TRUE
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cash_flow_forecasts (
            forecast_id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            forecast_name VARCHAR(200) NOT NULL,
            start_week INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cash_flow_periods (
            period_id SERIAL PRIMARY KEY,
            forecast_id INTEGER REFERENCES cash_flow_forecasts(forecast_id) ON DELETE CASCADE,
            week_number INTEGER NOT NULL,
            beginning_cash DECIMAL(15, 2) DEFAULT 0,
            projected_inflows DECIMAL(15, 2) DEFAULT 0,
            projected_outflows DECIMAL(15, 2) DEFAULT 0,
            ending_cash DECIMAL(15, 2) DEFAULT 0,
            actual_inflows DECIMAL(15, 2),
            actual_outflows DECIMAL(15, 2),
            actual_ending DECIMAL(15, 2),
            variance DECIMAL(15, 2),
            notes TEXT,
            UNIQUE(forecast_id, week_number)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cash_flow_line_items (
            item_id SERIAL PRIMARY KEY,
            period_id INTEGER REFERENCES cash_flow_periods(period_id) ON DELETE CASCADE,
            item_type VARCHAR(20) NOT NULL,
            category VARCHAR(100) NOT NULL,
            description VARCHAR(255),
            projected_amount DECIMAL(15, 2) DEFAULT 0,
            actual_amount DECIMAL(15, 2),
            is_recurring BOOLEAN DEFAULT FALSE,
            recurrence_weeks INTEGER
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cash_flow_challenges (
            challenge_id SERIAL PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            challenge_type VARCHAR(50) NOT NULL,
            difficulty INTEGER DEFAULT 1,
            scenario_data JSONB,
            correct_answer JSONB,
            exp_reward INTEGER DEFAULT 50,
            hint_text TEXT,
            is_active BOOLEAN DEFAULT TRUE
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS business_plans (
            plan_id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            plan_name VARCHAR(200) NOT NULL,
            business_type VARCHAR(100),
            target_market VARCHAR(200),
            overall_score INTEGER DEFAULT 0,
            mentor_feedback TEXT,
            status VARCHAR(50) DEFAULT 'draft',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS business_plan_sections (
            section_id SERIAL PRIMARY KEY,
            plan_id INTEGER REFERENCES business_plans(plan_id) ON DELETE CASCADE,
            section_type VARCHAR(50) NOT NULL,
            section_order INTEGER NOT NULL,
            content TEXT,
            score INTEGER DEFAULT 0,
            feedback TEXT,
            is_complete BOOLEAN DEFAULT FALSE,
            UNIQUE(plan_id, section_type)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS negotiation_scenarios (
            scenario_id SERIAL PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            negotiation_type VARCHAR(50) NOT NULL,
            difficulty INTEGER DEFAULT 1,
            counterparty_name VARCHAR(100),
            counterparty_style VARCHAR(50),
            your_batna JSONB,
            their_batna JSONB,
            issues JSONB,
            opening_position JSONB,
            optimal_outcome JSONB,
            exp_reward INTEGER DEFAULT 100,
            is_active BOOLEAN DEFAULT TRUE
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_negotiations (
            negotiation_id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            scenario_id INTEGER REFERENCES negotiation_scenarios(scenario_id),
            current_round INTEGER DEFAULT 1,
            player_offers JSONB,
            counterparty_offers JSONB,
            final_deal JSONB,
            deal_value DECIMAL(15, 2),
            relationship_impact INTEGER DEFAULT 0,
            status VARCHAR(50) DEFAULT 'in_progress',
            exp_earned INTEGER DEFAULT 0,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS risk_categories (
            category_id SERIAL PRIMARY KEY,
            category_name VARCHAR(100) NOT NULL,
            description TEXT,
            icon VARCHAR(50)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_risks (
            risk_id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            category_id INTEGER REFERENCES risk_categories(category_id),
            risk_name VARCHAR(200) NOT NULL,
            description TEXT,
            probability INTEGER DEFAULT 50,
            impact INTEGER DEFAULT 50,
            risk_score INTEGER GENERATED ALWAYS AS (probability * impact / 100) STORED,
            mitigation_strategy TEXT,
            status VARCHAR(50) DEFAULT 'identified',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS supply_chain_products (
            product_id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            product_name VARCHAR(200) NOT NULL,
            sku VARCHAR(50),
            unit_cost DECIMAL(10, 2) DEFAULT 0,
            selling_price DECIMAL(10, 2) DEFAULT 0,
            reorder_point INTEGER DEFAULT 10,
            reorder_quantity INTEGER DEFAULT 50,
            lead_time_days INTEGER DEFAULT 7,
            current_stock INTEGER DEFAULT 0,
            safety_stock INTEGER DEFAULT 5
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            supplier_id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            supplier_name VARCHAR(200) NOT NULL,
            reliability_score INTEGER DEFAULT 80,
            price_competitiveness INTEGER DEFAULT 50,
            lead_time_days INTEGER DEFAULT 7,
            minimum_order DECIMAL(10, 2) DEFAULT 100,
            payment_terms VARCHAR(50) DEFAULT 'Net 30',
            relationship_level INTEGER DEFAULT 1
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS purchase_orders (
            order_id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            supplier_id INTEGER REFERENCES suppliers(supplier_id),
            product_id INTEGER REFERENCES supply_chain_products(product_id),
            quantity INTEGER NOT NULL,
            unit_cost DECIMAL(10, 2) NOT NULL,
            total_cost DECIMAL(15, 2) NOT NULL,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expected_delivery TIMESTAMP,
            actual_delivery TIMESTAMP,
            status VARCHAR(50) DEFAULT 'pending'
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS market_segments (
            segment_id SERIAL PRIMARY KEY,
            segment_name VARCHAR(100) NOT NULL,
            segment_size INTEGER DEFAULT 10000,
            price_sensitivity INTEGER DEFAULT 50,
            quality_preference INTEGER DEFAULT 50,
            brand_loyalty INTEGER DEFAULT 30,
            growth_rate DECIMAL(5, 2) DEFAULT 0.02,
            description TEXT
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS market_competitors (
            competitor_id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            competitor_name VARCHAR(100) NOT NULL,
            market_share DECIMAL(5, 2) DEFAULT 0.10,
            price_level INTEGER DEFAULT 50,
            quality_level INTEGER DEFAULT 50,
            marketing_spend INTEGER DEFAULT 1000,
            strategy VARCHAR(50) DEFAULT 'balanced',
            is_active BOOLEAN DEFAULT TRUE
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_market_position (
            position_id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            segment_id INTEGER REFERENCES market_segments(segment_id),
            market_share DECIMAL(5, 4) DEFAULT 0.0100,
            price_point INTEGER DEFAULT 50,
            quality_rating INTEGER DEFAULT 50,
            brand_awareness INTEGER DEFAULT 10,
            customer_satisfaction INTEGER DEFAULT 70,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS market_simulation_rounds (
            round_id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            round_number INTEGER NOT NULL,
            price_decision INTEGER,
            marketing_spend INTEGER,
            quality_investment INTEGER,
            revenue DECIMAL(15, 2),
            profit DECIMAL(15, 2),
            market_share_change DECIMAL(5, 4),
            round_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS market_challenges (
            challenge_id SERIAL PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            challenge_type VARCHAR(50) NOT NULL,
            difficulty INTEGER DEFAULT 1,
            scenario_data JSONB DEFAULT '{}',
            correct_answer JSONB DEFAULT '{}',
            hint_text TEXT,
            exp_reward INTEGER DEFAULT 100,
            discipline VARCHAR(50) DEFAULT 'Marketing'
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS employee_roles (
            role_id SERIAL PRIMARY KEY,
            role_name VARCHAR(100) NOT NULL,
            department VARCHAR(50) NOT NULL,
            base_salary DECIMAL(10, 2) NOT NULL,
            skill_requirements JSONB DEFAULT '{}',
            responsibilities TEXT,
            career_path TEXT
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_employees (
            employee_id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            employee_name VARCHAR(100) NOT NULL,
            role_id INTEGER REFERENCES employee_roles(role_id),
            hire_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            salary DECIMAL(10, 2) NOT NULL,
            performance_score INTEGER DEFAULT 70,
            satisfaction INTEGER DEFAULT 75,
            skills JSONB DEFAULT '{}',
            tenure_months INTEGER DEFAULT 0,
            status VARCHAR(50) DEFAULT 'active'
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS performance_reviews (
            review_id SERIAL PRIMARY KEY,
            employee_id INTEGER REFERENCES player_employees(employee_id) ON DELETE CASCADE,
            review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reviewer_notes TEXT,
            goals_met INTEGER DEFAULT 0,
            goals_total INTEGER DEFAULT 5,
            rating INTEGER DEFAULT 3,
            feedback_given TEXT,
            development_plan TEXT,
            salary_adjustment DECIMAL(5, 2) DEFAULT 0,
            exp_earned INTEGER DEFAULT 0
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS hr_challenges (
            challenge_id SERIAL PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            challenge_type VARCHAR(50) NOT NULL,
            difficulty INTEGER DEFAULT 1,
            scenario_data JSONB DEFAULT '{}',
            correct_answer JSONB DEFAULT '{}',
            hint_text TEXT,
            exp_reward INTEGER DEFAULT 100
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pitch_templates (
            template_id SERIAL PRIMARY KEY,
            template_name VARCHAR(100) NOT NULL,
            section_name VARCHAR(100) NOT NULL,
            section_order INTEGER NOT NULL,
            description TEXT,
            example_content TEXT,
            scoring_criteria JSONB DEFAULT '{}'
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_pitch_decks (
            deck_id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            deck_name VARCHAR(200) NOT NULL,
            funding_stage VARCHAR(50) DEFAULT 'seed',
            target_amount DECIMAL(15, 2) DEFAULT 100000,
            valuation DECIMAL(15, 2) DEFAULT 500000,
            overall_score INTEGER DEFAULT 0,
            status VARCHAR(50) DEFAULT 'draft',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pitch_deck_sections (
            section_id SERIAL PRIMARY KEY,
            deck_id INTEGER REFERENCES player_pitch_decks(deck_id) ON DELETE CASCADE,
            section_name VARCHAR(100) NOT NULL,
            section_order INTEGER NOT NULL,
            content TEXT,
            score INTEGER DEFAULT 0,
            feedback TEXT,
            is_complete BOOLEAN DEFAULT FALSE
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS investor_profiles (
            investor_id SERIAL PRIMARY KEY,
            investor_name VARCHAR(100) NOT NULL,
            investor_type VARCHAR(50) NOT NULL,
            focus_areas JSONB DEFAULT '[]',
            investment_range_min DECIMAL(15, 2) DEFAULT 25000,
            investment_range_max DECIMAL(15, 2) DEFAULT 500000,
            risk_tolerance INTEGER DEFAULT 50,
            priorities JSONB DEFAULT '{}',
            personality VARCHAR(50) DEFAULT 'analytical'
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pitch_sessions (
            session_id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            deck_id INTEGER REFERENCES player_pitch_decks(deck_id),
            investor_id INTEGER REFERENCES investor_profiles(investor_id),
            session_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            questions_asked JSONB DEFAULT '[]',
            answers_given JSONB DEFAULT '[]',
            investor_interest INTEGER DEFAULT 50,
            funding_offered DECIMAL(15, 2),
            equity_requested DECIMAL(5, 2),
            outcome VARCHAR(50) DEFAULT 'pending',
            exp_earned INTEGER DEFAULT 0
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS learning_recommendations (
            recommendation_id SERIAL PRIMARY KEY,
            discipline VARCHAR(50) NOT NULL,
            min_level INTEGER DEFAULT 1,
            title VARCHAR(200) NOT NULL,
            description TEXT
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_learning_progress (
            progress_id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            discipline VARCHAR(50) NOT NULL,
            scenarios_completed INTEGER DEFAULT 0,
            challenges_completed INTEGER DEFAULT 0,
            correct_answers INTEGER DEFAULT 0,
            total_attempts INTEGER DEFAULT 0,
            time_spent_minutes INTEGER DEFAULT 0,
            last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            strengths JSONB DEFAULT '[]',
            weaknesses JSONB DEFAULT '[]'
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS educational_achievements (
            achievement_id SERIAL PRIMARY KEY,
            achievement_name VARCHAR(200) NOT NULL,
            description TEXT,
            category VARCHAR(50) NOT NULL,
            requirement_count INTEGER DEFAULT 1,
            exp_reward INTEGER DEFAULT 100,
            tier VARCHAR(20) DEFAULT 'bronze'
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_educational_achievements (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            achievement_id INTEGER REFERENCES educational_achievements(achievement_id),
            progress_count INTEGER DEFAULT 0,
            is_unlocked BOOLEAN DEFAULT FALSE,
            unlocked_at TIMESTAMP,
            UNIQUE(player_id, achievement_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS competition_types (
            competition_id SERIAL PRIMARY KEY,
            competition_name VARCHAR(200) NOT NULL,
            description TEXT,
            competition_type VARCHAR(50) NOT NULL,
            duration_days INTEGER DEFAULT 7,
            exp_reward INTEGER DEFAULT 500,
            scoring_criteria JSONB DEFAULT '[]'
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS leagues (
            league_id SERIAL PRIMARY KEY,
            league_name VARCHAR(100) NOT NULL,
            tier INTEGER NOT NULL,
            min_exp INTEGER DEFAULT 0,
            max_exp INTEGER DEFAULT 999999,
            reward_multiplier DECIMAL(3, 2) DEFAULT 1.0
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS active_competitions (
            active_id SERIAL PRIMARY KEY,
            competition_id INTEGER REFERENCES competition_types(competition_id),
            start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_date TIMESTAMP,
            status VARCHAR(50) DEFAULT 'active'
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS competition_entries (
            entry_id SERIAL PRIMARY KEY,
            active_id INTEGER REFERENCES active_competitions(active_id) ON DELETE CASCADE,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            score INTEGER DEFAULT 0,
            rank INTEGER,
            metrics JSONB DEFAULT '{}',
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(active_id, player_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_league_status (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            league_id INTEGER REFERENCES leagues(league_id),
            season INTEGER DEFAULT 1,
            season_exp INTEGER DEFAULT 0,
            rank_in_league INTEGER,
            promoted BOOLEAN DEFAULT FALSE,
            relegated BOOLEAN DEFAULT FALSE,
            UNIQUE(player_id, season)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS advanced_simulations (
            simulation_id SERIAL PRIMARY KEY,
            simulation_name VARCHAR(200) NOT NULL,
            simulation_type VARCHAR(50) NOT NULL,
            description TEXT,
            difficulty INTEGER DEFAULT 3,
            scenario_data JSONB DEFAULT '{}',
            solution_guide JSONB DEFAULT '{}',
            exp_reward INTEGER DEFAULT 300
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_simulation_progress (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            simulation_id INTEGER REFERENCES advanced_simulations(simulation_id),
            current_step INTEGER DEFAULT 0,
            decisions JSONB DEFAULT '[]',
            outcome_score INTEGER DEFAULT 0,
            status VARCHAR(50) DEFAULT 'in_progress',
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tutorial_progress (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            tutorial_section VARCHAR(100) NOT NULL,
            is_completed BOOLEAN DEFAULT FALSE,
            completed_at TIMESTAMP,
            UNIQUE(player_id, tutorial_section)
        );
    """)
    
    # Phase 4: Storyline Quest System
    cur.execute("""
        CREATE TABLE IF NOT EXISTS story_arcs (
            arc_id SERIAL PRIMARY KEY,
            arc_name VARCHAR(200) NOT NULL,
            arc_description TEXT,
            world_type VARCHAR(50),
            total_chapters INTEGER DEFAULT 5,
            unlock_level INTEGER DEFAULT 1,
            exp_reward INTEGER DEFAULT 500,
            is_active BOOLEAN DEFAULT TRUE
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS story_chapters (
            chapter_id SERIAL PRIMARY KEY,
            arc_id INTEGER REFERENCES story_arcs(arc_id) ON DELETE CASCADE,
            chapter_number INTEGER NOT NULL,
            chapter_title VARCHAR(200) NOT NULL,
            chapter_narrative TEXT,
            choice_a_text TEXT,
            choice_a_outcome TEXT,
            choice_a_next_chapter INTEGER,
            choice_b_text TEXT,
            choice_b_outcome TEXT,
            choice_b_next_chapter INTEGER,
            choice_c_text TEXT,
            choice_c_outcome TEXT,
            choice_c_next_chapter INTEGER,
            exp_reward INTEGER DEFAULT 100,
            is_finale BOOLEAN DEFAULT FALSE
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_story_progress (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            arc_id INTEGER REFERENCES story_arcs(arc_id) ON DELETE CASCADE,
            current_chapter INTEGER DEFAULT 1,
            choices_made JSONB DEFAULT '[]',
            status VARCHAR(50) DEFAULT 'in_progress',
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            UNIQUE(player_id, arc_id)
        );
    """)
    
    # Phase 4: Mentorship & Advisor Progression
    cur.execute("""
        CREATE TABLE IF NOT EXISTS advisor_skill_trees (
            skill_id SERIAL PRIMARY KEY,
            advisor_id INTEGER REFERENCES advisors(advisor_id) ON DELETE CASCADE,
            skill_name VARCHAR(100) NOT NULL,
            skill_description TEXT,
            skill_tier INTEGER DEFAULT 1,
            parent_skill_id INTEGER,
            bonus_type VARCHAR(50),
            bonus_value DECIMAL(5, 2) DEFAULT 0,
            unlock_cost INTEGER DEFAULT 100
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_advisor_relationships (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            advisor_id INTEGER REFERENCES advisors(advisor_id) ON DELETE CASCADE,
            affinity_level INTEGER DEFAULT 0,
            total_interactions INTEGER DEFAULT 0,
            unlocked_skills JSONB DEFAULT '[]',
            is_mentor BOOLEAN DEFAULT FALSE,
            mentorship_started TIMESTAMP,
            UNIQUE(player_id, advisor_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS mentorship_missions (
            mission_id SERIAL PRIMARY KEY,
            advisor_id INTEGER REFERENCES advisors(advisor_id) ON DELETE CASCADE,
            mission_name VARCHAR(200) NOT NULL,
            mission_description TEXT,
            required_affinity INTEGER DEFAULT 10,
            mission_type VARCHAR(50),
            objectives JSONB DEFAULT '[]',
            rewards JSONB DEFAULT '{}',
            exp_reward INTEGER DEFAULT 200
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_mentor_missions (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            mission_id INTEGER REFERENCES mentorship_missions(mission_id) ON DELETE CASCADE,
            progress JSONB DEFAULT '{}',
            status VARCHAR(50) DEFAULT 'active',
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        );
    """)
    
    # Phase 4: Business Network & Partnerships
    cur.execute("""
        CREATE TABLE IF NOT EXISTS business_partners (
            partner_id SERIAL PRIMARY KEY,
            partner_name VARCHAR(200) NOT NULL,
            partner_type VARCHAR(50),
            industry VARCHAR(100),
            description TEXT,
            reputation_required INTEGER DEFAULT 0,
            partnership_bonus JSONB DEFAULT '{}'
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_partnerships (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            partner_id INTEGER REFERENCES business_partners(partner_id) ON DELETE CASCADE,
            partnership_level INTEGER DEFAULT 1,
            trust_score INTEGER DEFAULT 50,
            joint_ventures_completed INTEGER DEFAULT 0,
            total_shared_profit DECIMAL(15, 2) DEFAULT 0,
            established_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(player_id, partner_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS joint_ventures (
            venture_id SERIAL PRIMARY KEY,
            venture_name VARCHAR(200) NOT NULL,
            venture_description TEXT,
            partner_id INTEGER REFERENCES business_partners(partner_id),
            investment_required DECIMAL(15, 2) DEFAULT 5000,
            duration_weeks INTEGER DEFAULT 4,
            risk_level INTEGER DEFAULT 3,
            potential_return DECIMAL(5, 2) DEFAULT 1.5,
            exp_reward INTEGER DEFAULT 150
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_joint_ventures (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            venture_id INTEGER REFERENCES joint_ventures(venture_id) ON DELETE CASCADE,
            investment_amount DECIMAL(15, 2),
            start_week INTEGER,
            end_week INTEGER,
            status VARCHAR(50) DEFAULT 'active',
            outcome JSONB DEFAULT '{}',
            profit_loss DECIMAL(15, 2) DEFAULT 0
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS networking_events (
            event_id SERIAL PRIMARY KEY,
            event_name VARCHAR(200) NOT NULL,
            event_type VARCHAR(50),
            description TEXT,
            entry_cost DECIMAL(10, 2) DEFAULT 0,
            reputation_required INTEGER DEFAULT 0,
            contacts_gained INTEGER DEFAULT 1,
            exp_reward INTEGER DEFAULT 100
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_network (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            contact_name VARCHAR(200) NOT NULL,
            contact_type VARCHAR(50),
            industry VARCHAR(100),
            relationship_strength INTEGER DEFAULT 1,
            met_at_event INTEGER REFERENCES networking_events(event_id),
            referrals_given INTEGER DEFAULT 0,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Phase 4: Industry Specialization Tracks
    cur.execute("""
        CREATE TABLE IF NOT EXISTS industry_tracks (
            track_id SERIAL PRIMARY KEY,
            track_name VARCHAR(100) NOT NULL,
            industry VARCHAR(100) NOT NULL,
            description TEXT,
            total_levels INTEGER DEFAULT 5,
            base_exp_required INTEGER DEFAULT 500
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS industry_certifications (
            cert_id SERIAL PRIMARY KEY,
            track_id INTEGER REFERENCES industry_tracks(track_id) ON DELETE CASCADE,
            cert_name VARCHAR(200) NOT NULL,
            cert_description TEXT,
            required_level INTEGER DEFAULT 1,
            exam_questions JSONB DEFAULT '[]',
            passing_score INTEGER DEFAULT 70,
            exp_reward INTEGER DEFAULT 300,
            badge_icon VARCHAR(100)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_industry_progress (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            track_id INTEGER REFERENCES industry_tracks(track_id) ON DELETE CASCADE,
            current_level INTEGER DEFAULT 1,
            current_exp INTEGER DEFAULT 0,
            certifications_earned JSONB DEFAULT '[]',
            specialization_bonuses JSONB DEFAULT '{}',
            UNIQUE(player_id, track_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS industry_challenges (
            challenge_id SERIAL PRIMARY KEY,
            track_id INTEGER REFERENCES industry_tracks(track_id) ON DELETE CASCADE,
            challenge_name VARCHAR(200) NOT NULL,
            challenge_description TEXT,
            required_level INTEGER DEFAULT 1,
            challenge_data JSONB DEFAULT '{}',
            exp_reward INTEGER DEFAULT 150
        );
    """)
    
    # Phase 4: Dynamic Market Events
    cur.execute("""
        CREATE TABLE IF NOT EXISTS market_events (
            event_id SERIAL PRIMARY KEY,
            event_name VARCHAR(200) NOT NULL,
            event_type VARCHAR(50),
            description TEXT,
            affected_industries JSONB DEFAULT '[]',
            market_modifier DECIMAL(4, 2) DEFAULT 1.0,
            duration_days INTEGER DEFAULT 7,
            is_global BOOLEAN DEFAULT FALSE
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS active_market_events (
            id SERIAL PRIMARY KEY,
            event_id INTEGER REFERENCES market_events(event_id) ON DELETE CASCADE,
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_time TIMESTAMP,
            current_phase INTEGER DEFAULT 1,
            total_phases INTEGER DEFAULT 3,
            status VARCHAR(50) DEFAULT 'active'
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS market_cycles (
            cycle_id SERIAL PRIMARY KEY,
            cycle_name VARCHAR(100) NOT NULL,
            cycle_type VARCHAR(50),
            description TEXT,
            revenue_modifier DECIMAL(4, 2) DEFAULT 1.0,
            cost_modifier DECIMAL(4, 2) DEFAULT 1.0,
            opportunity_modifier DECIMAL(4, 2) DEFAULT 1.0,
            duration_weeks INTEGER DEFAULT 12
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS global_challenges (
            challenge_id SERIAL PRIMARY KEY,
            challenge_name VARCHAR(200) NOT NULL,
            challenge_description TEXT,
            target_type VARCHAR(50),
            target_value INTEGER DEFAULT 10000,
            current_progress INTEGER DEFAULT 0,
            participants INTEGER DEFAULT 0,
            reward_pool INTEGER DEFAULT 5000,
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            status VARCHAR(50) DEFAULT 'pending'
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_global_contributions (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            challenge_id INTEGER REFERENCES global_challenges(challenge_id) ON DELETE CASCADE,
            contribution INTEGER DEFAULT 0,
            reward_claimed BOOLEAN DEFAULT FALSE,
            contributed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(player_id, challenge_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS breaking_news (
            news_id SERIAL PRIMARY KEY,
            headline VARCHAR(300) NOT NULL,
            news_content TEXT,
            news_type VARCHAR(50),
            affected_discipline VARCHAR(100),
            response_deadline TIMESTAMP,
            optimal_response TEXT,
            exp_reward INTEGER DEFAULT 100,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_news_responses (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            news_id INTEGER REFERENCES breaking_news(news_id) ON DELETE CASCADE,
            response_choice VARCHAR(50),
            response_quality INTEGER DEFAULT 0,
            exp_earned INTEGER DEFAULT 0,
            responded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(player_id, news_id)
        );
    """)
    
    # ============================================================================
    # PHASE 5A: MULTIPLAYER & SOCIAL FEATURES
    # ============================================================================
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS guilds (
            guild_id SERIAL PRIMARY KEY,
            guild_name VARCHAR(100) UNIQUE NOT NULL,
            guild_tag VARCHAR(10) NOT NULL,
            guild_description TEXT,
            leader_id INTEGER REFERENCES player_profiles(player_id) ON DELETE SET NULL,
            guild_level INTEGER DEFAULT 1,
            guild_exp INTEGER DEFAULT 0,
            guild_treasury INTEGER DEFAULT 0,
            max_members INTEGER DEFAULT 20,
            guild_banner VARCHAR(100),
            is_public BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS guild_members (
            id SERIAL PRIMARY KEY,
            guild_id INTEGER REFERENCES guilds(guild_id) ON DELETE CASCADE,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            member_role VARCHAR(50) DEFAULT 'member',
            contribution_exp INTEGER DEFAULT 0,
            contribution_gold INTEGER DEFAULT 0,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(player_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS guild_wars (
            war_id SERIAL PRIMARY KEY,
            guild_a_id INTEGER REFERENCES guilds(guild_id) ON DELETE CASCADE,
            guild_b_id INTEGER REFERENCES guilds(guild_id) ON DELETE CASCADE,
            war_type VARCHAR(50) DEFAULT 'challenge',
            guild_a_score INTEGER DEFAULT 0,
            guild_b_score INTEGER DEFAULT 0,
            winner_id INTEGER REFERENCES guilds(guild_id),
            reward_pool INTEGER DEFAULT 1000,
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_time TIMESTAMP,
            status VARCHAR(50) DEFAULT 'active'
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS coop_challenges (
            challenge_id SERIAL PRIMARY KEY,
            challenge_name VARCHAR(200) NOT NULL,
            challenge_description TEXT,
            challenge_type VARCHAR(50) DEFAULT 'duo',
            min_players INTEGER DEFAULT 2,
            max_players INTEGER DEFAULT 4,
            difficulty INTEGER DEFAULT 1,
            scenario_data JSONB,
            exp_reward INTEGER DEFAULT 200,
            bonus_reward INTEGER DEFAULT 50,
            time_limit_minutes INTEGER DEFAULT 30,
            is_active BOOLEAN DEFAULT TRUE
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS coop_sessions (
            session_id SERIAL PRIMARY KEY,
            challenge_id INTEGER REFERENCES coop_challenges(challenge_id) ON DELETE CASCADE,
            host_player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            session_code VARCHAR(10) UNIQUE,
            status VARCHAR(50) DEFAULT 'waiting',
            current_phase INTEGER DEFAULT 1,
            total_score INTEGER DEFAULT 0,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS coop_participants (
            id SERIAL PRIMARY KEY,
            session_id INTEGER REFERENCES coop_sessions(session_id) ON DELETE CASCADE,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            contribution_score INTEGER DEFAULT 0,
            is_ready BOOLEAN DEFAULT FALSE,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(session_id, player_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS trade_listings (
            listing_id SERIAL PRIMARY KEY,
            seller_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            item_type VARCHAR(50) NOT NULL,
            item_id INTEGER,
            item_name VARCHAR(200),
            item_data JSONB,
            asking_price INTEGER NOT NULL,
            quantity INTEGER DEFAULT 1,
            status VARCHAR(50) DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS trade_transactions (
            transaction_id SERIAL PRIMARY KEY,
            listing_id INTEGER REFERENCES trade_listings(listing_id) ON DELETE CASCADE,
            seller_id INTEGER REFERENCES player_profiles(player_id) ON DELETE SET NULL,
            buyer_id INTEGER REFERENCES player_profiles(player_id) ON DELETE SET NULL,
            item_type VARCHAR(50),
            item_name VARCHAR(200),
            price INTEGER,
            quantity INTEGER DEFAULT 1,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_mentoring (
            mentoring_id SERIAL PRIMARY KEY,
            mentor_player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            mentee_player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            discipline_focus VARCHAR(100),
            sessions_completed INTEGER DEFAULT 0,
            mentor_rating DECIMAL(3, 2) DEFAULT 0,
            status VARCHAR(50) DEFAULT 'active',
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(mentor_player_id, mentee_player_id)
        );
    """)
    
    # ============================================================================
    # PHASE 5B: SEASONAL CONTENT & LIVE EVENTS
    # ============================================================================
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS seasons (
            season_id SERIAL PRIMARY KEY,
            season_name VARCHAR(100) NOT NULL,
            season_theme VARCHAR(100),
            description TEXT,
            start_date TIMESTAMP,
            end_date TIMESTAMP,
            is_active BOOLEAN DEFAULT FALSE
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS battle_passes (
            pass_id SERIAL PRIMARY KEY,
            season_id INTEGER REFERENCES seasons(season_id) ON DELETE CASCADE,
            pass_name VARCHAR(100) NOT NULL,
            max_tier INTEGER DEFAULT 50,
            premium_price INTEGER DEFAULT 500,
            free_rewards JSONB,
            premium_rewards JSONB
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_battle_pass (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            pass_id INTEGER REFERENCES battle_passes(pass_id) ON DELETE CASCADE,
            current_tier INTEGER DEFAULT 1,
            current_exp INTEGER DEFAULT 0,
            is_premium BOOLEAN DEFAULT FALSE,
            rewards_claimed JSONB DEFAULT '[]',
            UNIQUE(player_id, pass_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS seasonal_events (
            event_id SERIAL PRIMARY KEY,
            event_name VARCHAR(200) NOT NULL,
            event_type VARCHAR(50),
            event_theme VARCHAR(100),
            description TEXT,
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            bonus_multiplier DECIMAL(3, 2) DEFAULT 1.5,
            special_rewards JSONB,
            is_active BOOLEAN DEFAULT FALSE
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS limited_time_bosses (
            boss_id SERIAL PRIMARY KEY,
            boss_name VARCHAR(200) NOT NULL,
            boss_title VARCHAR(200),
            description TEXT,
            difficulty INTEGER DEFAULT 5,
            health_points INTEGER DEFAULT 10000,
            current_hp INTEGER DEFAULT 10000,
            scenario_data JSONB,
            exp_reward INTEGER DEFAULT 500,
            exclusive_rewards JSONB,
            available_from TIMESTAMP,
            available_until TIMESTAMP,
            is_defeated BOOLEAN DEFAULT FALSE
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS weekly_rotations (
            rotation_id SERIAL PRIMARY KEY,
            rotation_type VARCHAR(50) NOT NULL,
            content_ids JSONB,
            bonus_discipline VARCHAR(100),
            bonus_multiplier DECIMAL(3, 2) DEFAULT 1.25,
            week_start TIMESTAMP,
            week_end TIMESTAMP
        );
    """)
    
    # ============================================================================
    # PHASE 5C: AI-POWERED PERSONALIZATION
    # ============================================================================
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_learning_profiles (
            profile_id SERIAL PRIMARY KEY,
            player_id INTEGER UNIQUE REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            learning_style VARCHAR(50) DEFAULT 'balanced',
            preferred_difficulty DECIMAL(3, 2) DEFAULT 1.0,
            weak_areas JSONB DEFAULT '[]',
            strong_areas JSONB DEFAULT '[]',
            recommended_path JSONB,
            last_analysis TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS adaptive_difficulty (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            discipline VARCHAR(100),
            current_difficulty DECIMAL(3, 2) DEFAULT 1.0,
            success_streak INTEGER DEFAULT 0,
            failure_streak INTEGER DEFAULT 0,
            total_attempts INTEGER DEFAULT 0,
            average_score DECIMAL(5, 2) DEFAULT 0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(player_id, discipline)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS learning_recommendations (
            recommendation_id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            recommendation_type VARCHAR(50),
            content_type VARCHAR(50),
            content_id INTEGER,
            content_name VARCHAR(200),
            reason TEXT,
            priority INTEGER DEFAULT 1,
            is_completed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS coach_messages (
            message_id SERIAL PRIMARY KEY,
            trigger_type VARCHAR(50),
            trigger_condition JSONB,
            message_text TEXT NOT NULL,
            message_category VARCHAR(50),
            priority INTEGER DEFAULT 1,
            is_active BOOLEAN DEFAULT TRUE
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_coach_history (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            message_id INTEGER REFERENCES coach_messages(message_id) ON DELETE CASCADE,
            shown_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            was_helpful BOOLEAN
        );
    """)
    
    # ============================================================================
    # PHASE 5D: CONTENT EXPANSION
    # ============================================================================
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS expanded_worlds (
            world_id SERIAL PRIMARY KEY,
            world_name VARCHAR(100) UNIQUE NOT NULL,
            world_type VARCHAR(50),
            description TEXT,
            unlock_level INTEGER DEFAULT 1,
            theme_color VARCHAR(20),
            backdrop_image VARCHAR(200),
            special_mechanics TEXT,
            is_active BOOLEAN DEFAULT TRUE
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS case_studies (
            case_id SERIAL PRIMARY KEY,
            case_title VARCHAR(200) NOT NULL,
            company_name VARCHAR(100),
            industry VARCHAR(100),
            discipline VARCHAR(100),
            difficulty INTEGER DEFAULT 3,
            case_background TEXT,
            case_challenge TEXT,
            learning_objectives JSONB,
            solution_analysis TEXT,
            key_takeaways JSONB,
            exp_reward INTEGER DEFAULT 300,
            is_premium BOOLEAN DEFAULT FALSE
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_case_progress (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            case_id INTEGER REFERENCES case_studies(case_id) ON DELETE CASCADE,
            status VARCHAR(50) DEFAULT 'not_started',
            player_analysis TEXT,
            score INTEGER DEFAULT 0,
            completed_at TIMESTAMP,
            UNIQUE(player_id, case_id)
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS guest_mentors (
            mentor_id SERIAL PRIMARY KEY,
            mentor_name VARCHAR(100) NOT NULL,
            mentor_title VARCHAR(200),
            company VARCHAR(100),
            bio TEXT,
            expertise_areas JSONB,
            avatar_image VARCHAR(200),
            special_scenarios JSONB,
            unlock_requirement TEXT,
            is_available BOOLEAN DEFAULT TRUE
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS advanced_disciplines (
            discipline_id SERIAL PRIMARY KEY,
            base_discipline VARCHAR(100),
            advanced_name VARCHAR(100) NOT NULL,
            description TEXT,
            unlock_level INTEGER DEFAULT 10,
            max_level INTEGER DEFAULT 15,
            special_skills JSONB,
            is_active BOOLEAN DEFAULT TRUE
        );
    """)
    
    # ============================================================================
    # PHASE 5E: POLISH & ACCESSIBILITY
    # ============================================================================
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_preferences (
            id SERIAL PRIMARY KEY,
            player_id INTEGER UNIQUE REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            theme VARCHAR(50) DEFAULT 'dark',
            font_size VARCHAR(20) DEFAULT 'medium',
            high_contrast BOOLEAN DEFAULT FALSE,
            reduced_motion BOOLEAN DEFAULT FALSE,
            screen_reader_mode BOOLEAN DEFAULT FALSE,
            color_blind_mode VARCHAR(50),
            notification_settings JSONB DEFAULT '{}',
            offline_content JSONB DEFAULT '[]',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS offline_progress (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES player_profiles(player_id) ON DELETE CASCADE,
            content_type VARCHAR(50),
            content_id INTEGER,
            progress_data JSONB,
            synced BOOLEAN DEFAULT FALSE,
            created_offline_at TIMESTAMP,
            synced_at TIMESTAMP
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS performance_metrics (
            id SERIAL PRIMARY KEY,
            metric_type VARCHAR(50),
            metric_name VARCHAR(100),
            metric_value DECIMAL(10, 2),
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    conn.commit()
    cur.close()
    return_connection(conn)
    print("Database initialized successfully!")

