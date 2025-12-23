import os
import json
from openai import OpenAI

client = OpenAI()

def analyze_answer(player_answer: str, correct_answer: str, question_text: str, 
                   concept: str, discipline: str) -> dict:
    """Analyze a player's answer and identify knowledge gaps."""
    
    prompt = f"""You are an expert business tutor analyzing a student's answer.

Question: {question_text}
Correct Answer: {correct_answer}
Student's Answer: {player_answer}
Business Concept: {concept}
Discipline: {discipline}

Analyze the student's answer and respond in JSON format:
{{
    "is_correct": true/false,
    "feedback": "Brief, encouraging feedback (2-3 sentences)",
    "knowledge_gap": "Specific concept they misunderstood, or null if correct",
    "gap_explanation": "Why this gap matters in business, or null if correct",
    "hint_for_next_time": "A helpful tip for similar questions"
}}

Be encouraging but honest. Focus on the learning opportunity."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a friendly business mentor helping students learn. Respond only with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        result = json.loads(response.choices[0].message.content)
        result['model_used'] = 'gpt-4o-mini'
        return result
        
    except Exception as e:
        return {
            "is_correct": str(player_answer).lower().strip() == str(correct_answer).lower().strip(),
            "feedback": "Let's review this concept together.",
            "knowledge_gap": None,
            "gap_explanation": None,
            "hint_for_next_time": "Take your time to consider all options.",
            "model_used": "fallback",
            "error": str(e)
        }


def generate_remediation_lesson(knowledge_gap: str, discipline: str, 
                                 original_question: str) -> dict:
    """Generate a targeted mini-lesson to address a specific knowledge gap."""
    
    prompt = f"""Create a short, focused business lesson to address this knowledge gap:

Knowledge Gap: {knowledge_gap}
Discipline: {discipline}
Context: Student struggled with a question about this topic.
Original Question: {original_question}

Create a mini-lesson in JSON format:
{{
    "lesson_title": "Short, clear title",
    "key_concept": "One sentence explaining the core idea",
    "explanation": "2-3 paragraph explanation in simple terms",
    "real_world_example": "A concrete business example",
    "formula_or_rule": "The key formula or rule to remember, if applicable",
    "practice_question": "A new question to test understanding",
    "practice_answer": "The correct answer with brief explanation"
}}

Keep it concise and practical. Use everyday language."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert business educator creating targeted lessons. Respond only with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        result = json.loads(response.choices[0].message.content)
        result['model_used'] = 'gpt-4o'
        return result
        
    except Exception as e:
        return {
            "lesson_title": f"Understanding {knowledge_gap}",
            "key_concept": "Let's review this important business concept.",
            "explanation": "This concept is fundamental to business success. Take time to study the materials and ask questions.",
            "real_world_example": "Consider how successful businesses apply this principle daily.",
            "formula_or_rule": None,
            "practice_question": None,
            "practice_answer": None,
            "model_used": "fallback",
            "error": str(e)
        }


def get_mentor_feedback(player_performance: dict, discipline: str) -> dict:
    """Generate personalized mentor feedback based on overall performance."""
    
    correct_count = player_performance.get('correct', 0)
    total_count = player_performance.get('total', 1)
    percentage = (correct_count / total_count) * 100 if total_count > 0 else 0
    weak_areas = player_performance.get('weak_areas', [])
    
    prompt = f"""You are a wise business mentor giving feedback to a student.

Performance Summary:
- Score: {correct_count}/{total_count} ({percentage:.0f}%)
- Discipline: {discipline}
- Areas needing work: {', '.join(weak_areas) if weak_areas else 'None identified'}

Generate encouraging mentor feedback in JSON format:
{{
    "greeting": "A warm, personalized greeting",
    "performance_summary": "Assessment of their performance (2 sentences)",
    "strengths": "What they did well",
    "improvement_areas": "Specific areas to focus on",
    "next_steps": "Concrete recommendations for what to study next",
    "motivational_close": "An encouraging closing message"
}}

Be warm, encouraging, and specific. This is an RPG game, so add a bit of adventure flavor."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a wise mentor in a business RPG game. Be encouraging and helpful. Respond only with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=500
        )
        
        result = json.loads(response.choices[0].message.content)
        result['model_used'] = 'gpt-4o-mini'
        return result
        
    except Exception as e:
        return {
            "greeting": "Well done, young entrepreneur!",
            "performance_summary": f"You scored {percentage:.0f}% on this challenge.",
            "strengths": "You showed determination in tackling these questions.",
            "improvement_areas": "Continue practicing to strengthen your understanding.",
            "next_steps": "Review the lesson materials and try again.",
            "motivational_close": "Every master was once a beginner. Keep going!",
            "model_used": "fallback",
            "error": str(e)
        }


def save_ai_interaction(player_id: int, path_id: int, interaction_type: str,
                        question_context: str, player_answer: str, correct_answer: str,
                        is_correct: bool, knowledge_gap: str, ai_feedback: str,
                        remediation_content: str, model_used: str):
    """Save an AI tutor interaction to the database."""
    from src.database import get_connection, return_connection
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO ai_tutor_interactions 
            (player_id, path_id, interaction_type, question_context, player_answer,
             correct_answer, is_correct, knowledge_gap, ai_feedback, remediation_content, model_used)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (player_id, path_id, interaction_type, question_context, player_answer,
              correct_answer, is_correct, knowledge_gap, ai_feedback, remediation_content, model_used))
        conn.commit()
    finally:
        cur.close()
        return_connection(conn)


def track_knowledge_gap(player_id: int, discipline: str, concept: str, gap_description: str):
    """Track or update a player's knowledge gap."""
    from src.database import get_connection, return_connection
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO player_knowledge_gaps (player_id, discipline, concept, gap_description)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (player_id, discipline, concept)
            DO UPDATE SET 
                times_struggled = player_knowledge_gaps.times_struggled + 1,
                last_struggled_at = CURRENT_TIMESTAMP,
                gap_description = EXCLUDED.gap_description
        """, (player_id, discipline, concept, gap_description))
        conn.commit()
    finally:
        cur.close()
        return_connection(conn)


def mark_gap_remediated(player_id: int, discipline: str, concept: str):
    """Mark a knowledge gap as remediated after successful practice."""
    from src.database import get_connection, return_connection
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            UPDATE player_knowledge_gaps 
            SET remediated = TRUE, remediated_at = CURRENT_TIMESTAMP
            WHERE player_id = %s AND discipline = %s AND concept = %s
        """, (player_id, discipline, concept))
        conn.commit()
    finally:
        cur.close()
        return_connection(conn)


def get_player_knowledge_gaps(player_id: int, discipline: str = None) -> list:
    """Get all knowledge gaps for a player, optionally filtered by discipline."""
    from src.database import get_connection, return_connection
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        if discipline:
            cur.execute("""
                SELECT * FROM player_knowledge_gaps 
                WHERE player_id = %s AND discipline = %s AND remediated = FALSE
                ORDER BY times_struggled DESC, last_struggled_at DESC
            """, (player_id, discipline))
        else:
            cur.execute("""
                SELECT * FROM player_knowledge_gaps 
                WHERE player_id = %s AND remediated = FALSE
                ORDER BY times_struggled DESC, last_struggled_at DESC
            """, (player_id,))
        
        return cur.fetchall()
    finally:
        cur.close()
        return_connection(conn)
