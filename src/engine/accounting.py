"""
Standalone functions for Business Tycoon RPG - accounting, projects, scheduling,
cashflow, negotiation, risk, display helpers, and all other standalone functions.
"""

import json
import random
import datetime
import math
from src.database import get_connection, return_connection
from src.leveling import get_current_level, get_level_title


def display_scenario(scenario: dict) -> None:
    """Display a scenario in the console."""
    print("\n" + "=" * 60)
    print(f"📋 {scenario['scenario_title']}")
    print(f"   [{scenario['discipline']} - Level {scenario['required_level']}]")
    print("=" * 60)
    print(f"\n{scenario['scenario_narrative']}\n")
    print("-" * 40)
    print(f"  A) {scenario['choice_a_text']}")
    print(f"  B) {scenario['choice_b_text']}")
    if scenario.get('choice_c_text'):
        print(f"  C) {scenario['choice_c_text']}")
    print("-" * 40)


def display_result(result: dict) -> None:
    """Display the result of a choice."""
    print("\n" + "=" * 60)
    print("📊 RESULT")
    print("=" * 60)
    print(f"\n{result['feedback']}\n")
    print(f"  💡 EXP Gained: +{result['exp_gained']} (base: {result['base_exp']})")
    
    if result['cash_change'] != 0:
        sign = "+" if result['cash_change'] > 0 else ""
        print(f"  💰 Cash: {sign}${result['cash_change']:,.2f}")
    
    if result['reputation_change'] != 0:
        sign = "+" if result['reputation_change'] > 0 else ""
        print(f"  ⭐ Reputation: {sign}{result['reputation_change']}")
    
    if result['leveled_up']:
        print(f"\n  🎉 LEVEL UP! {result['discipline']}: Level {result['old_level']} → Level {result['new_level']}!")
        print(f"     New Title: {get_level_title(result['new_level'])}")
    
    print()


def display_player_stats(stats: dict) -> None:
    """Display player statistics."""
    print("\n" + "=" * 60)
    print(f"👤 {stats['name']} | {stats['world']} World | {stats['industry']} Industry")
    print("=" * 60)
    print(f"  💰 Cash: ${stats['cash']:,.2f}")
    print(f"  ⭐ Reputation: {stats['reputation']}/100")
    print(f"  📅 Month: {stats['month']}")
    print("\n📈 DISCIPLINE PROGRESS:")
    print("-" * 40)
    
    for discipline, data in stats['disciplines'].items():
        print(f"  {discipline}: Level {data['level']} - {data['title']}")
        print(f"    {data['progress_bar']} ({data['total_exp']:,} EXP)")
        if data['exp_to_next'] > 0:
            print(f"    {data['exp_to_next']:,} EXP to Level {data['next_level']}")
        print()


# ============================================================================
# ACCOUNTING SYSTEM FUNCTIONS
# ============================================================================

def get_player_chart_of_accounts(player_id: int) -> list:
    """Get the player's chart of accounts organized by type."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT account_id, account_code, account_name, account_type, normal_balance, description
        FROM chart_of_accounts
        WHERE player_id = %s AND is_active = TRUE
        ORDER BY account_code
    """, (player_id,))
    
    accounts = cur.fetchall()
    cur.close()
    return_connection(conn)
    return accounts


def get_current_accounting_period(player_id: int) -> dict:
    """Get the player's current (open) accounting period."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT period_id, period_name, period_number, start_date, end_date, is_closed
        FROM accounting_periods
        WHERE player_id = %s AND is_closed = FALSE
        ORDER BY period_number DESC
        LIMIT 1
    """, (player_id,))
    
    period = cur.fetchone()
    cur.close()
    return_connection(conn)
    return period


def get_pending_transactions(player_id: int) -> list:
    """Get all unprocessed transactions awaiting journal entry."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT transaction_id, transaction_type, description, amount, 
               suggested_debit_account, suggested_credit_account, source_type, created_at
        FROM pending_transactions
        WHERE player_id = %s AND is_processed = FALSE
        ORDER BY created_at
    """, (player_id,))
    
    transactions = cur.fetchall()
    cur.close()
    return_connection(conn)
    return transactions


def create_pending_transaction(player_id: int, transaction_type: str, description: str, 
                              amount: float, debit_account: str, credit_account: str,
                              source_type: str = None, source_id: int = None) -> int:
    """Create a pending transaction for the player to record in their books."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO pending_transactions 
        (player_id, transaction_type, description, amount, suggested_debit_account, 
         suggested_credit_account, source_type, source_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING transaction_id
    """, (player_id, transaction_type, description, amount, debit_account, credit_account, source_type, source_id))
    
    transaction_id = cur.fetchone()['transaction_id']
    conn.commit()
    cur.close()
    return_connection(conn)
    return transaction_id


def create_journal_entry(player_id: int, description: str, lines: list, 
                        is_adjusting: bool = False) -> dict:
    """
    Create a journal entry with debit and credit lines.
    
    lines should be a list of dicts: [{'account_code': '1000', 'debit': 100, 'credit': 0}, ...]
    Returns success status and entry info.
    """
    if not lines or len(lines) < 2:
        return {'success': False, 'error': 'Journal entry requires at least 2 lines', 'exp_earned': 0}
    
    for line in lines:
        debit = line.get('debit')
        credit = line.get('credit')
        line['debit'] = float(debit) if debit is not None else 0.0
        line['credit'] = float(credit) if credit is not None else 0.0
        if not line.get('account_code'):
            return {'success': False, 'error': 'Missing account code in journal line', 'exp_earned': 0}
    
    conn = get_connection()
    cur = conn.cursor()
    
    account_codes = [line['account_code'] for line in lines]
    placeholders = ','.join(['%s'] * len(account_codes))
    cur.execute(f"""
        SELECT account_code FROM chart_of_accounts 
        WHERE player_id = %s AND account_code IN ({placeholders})
    """, (player_id, *account_codes))
    valid_codes = [row['account_code'] for row in cur.fetchall()]
    
    for code in account_codes:
        if code not in valid_codes:
            cur.close()
            return_connection(conn)
            return {'success': False, 'error': f'Invalid account code: {code}', 'exp_earned': 0}
    
    total_debits = sum(line['debit'] for line in lines)
    total_credits = sum(line['credit'] for line in lines)
    
    if abs(total_debits - total_credits) > 0.01:
        cur.close()
        return_connection(conn)
        return {
            'success': False,
            'error': f'Debits (${total_debits:,.2f}) must equal Credits (${total_credits:,.2f})',
            'exp_earned': 0
        }
    
    # Get current period
    cur.execute("""
        SELECT period_id FROM accounting_periods 
        WHERE player_id = %s AND is_closed = FALSE 
        ORDER BY period_number DESC LIMIT 1
    """, (player_id,))
    period_result = cur.fetchone()
    period_id = period_result['period_id'] if period_result else None
    
    # Create journal entry
    cur.execute("""
        INSERT INTO journal_entries 
        (player_id, period_id, description, is_adjusting, total_debits, total_credits, is_posted)
        VALUES (%s, %s, %s, %s, %s, %s, TRUE)
        RETURNING entry_id
    """, (player_id, period_id, description, is_adjusting, total_debits, total_credits))
    
    entry_id = cur.fetchone()['entry_id']
    
    # Create journal lines
    for line in lines:
        cur.execute("""
            SELECT account_id FROM chart_of_accounts 
            WHERE player_id = %s AND account_code = %s
        """, (player_id, line['account_code']))
        account_result = cur.fetchone()
        
        if account_result:
            cur.execute("""
                INSERT INTO journal_lines (entry_id, account_id, debit_amount, credit_amount)
                VALUES (%s, %s, %s, %s)
            """, (entry_id, account_result['account_id'], line.get('debit', 0), line.get('credit', 0)))
    
    # Award EXP for correct entry
    exp_earned = 25 if is_adjusting else 15
    
    conn.commit()
    cur.close()
    return_connection(conn)
    
    return {
        'success': True,
        'entry_id': entry_id,
        'total_debits': total_debits,
        'total_credits': total_credits,
        'exp_earned': exp_earned
    }


def get_journal_entries(player_id: int, period_id: int = None, limit: int = 20) -> list:
    """Get player's journal entries, optionally filtered by period."""
    conn = get_connection()
    cur = conn.cursor()
    
    if period_id:
        cur.execute("""
            SELECT je.entry_id, je.entry_date, je.description, je.total_debits, 
                   je.total_credits, je.is_adjusting, je.is_closing
            FROM journal_entries je
            WHERE je.player_id = %s AND je.period_id = %s AND je.is_posted = TRUE
            ORDER BY je.entry_date DESC
            LIMIT %s
        """, (player_id, period_id, limit))
    else:
        cur.execute("""
            SELECT je.entry_id, je.entry_date, je.description, je.total_debits, 
                   je.total_credits, je.is_adjusting, je.is_closing
            FROM journal_entries je
            WHERE je.player_id = %s AND je.is_posted = TRUE
            ORDER BY je.entry_date DESC
            LIMIT %s
        """, (player_id, limit))
    
    entries = cur.fetchall()
    cur.close()
    return_connection(conn)
    return entries


def get_journal_entry_lines(entry_id: int) -> list:
    """Get the lines for a specific journal entry."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT jl.line_id, jl.debit_amount, jl.credit_amount,
               ca.account_code, ca.account_name, ca.account_type
        FROM journal_lines jl
        JOIN chart_of_accounts ca ON jl.account_id = ca.account_id
        WHERE jl.entry_id = %s
        ORDER BY jl.debit_amount DESC, jl.credit_amount DESC
    """, (entry_id,))
    
    lines = cur.fetchall()
    cur.close()
    return_connection(conn)
    return lines


def get_trial_balance(player_id: int) -> dict:
    """
    Generate a trial balance from all posted journal entries.
    Returns account balances and totals.
    """
    conn = get_connection()
    cur = conn.cursor()
    
    # Get all accounts with their debit/credit totals from journal lines
    cur.execute("""
        SELECT ca.account_code, ca.account_name, ca.account_type, ca.normal_balance,
               COALESCE(SUM(jl.debit_amount), 0) as total_debits,
               COALESCE(SUM(jl.credit_amount), 0) as total_credits
        FROM chart_of_accounts ca
        LEFT JOIN journal_lines jl ON ca.account_id = jl.account_id
        LEFT JOIN journal_entries je ON jl.entry_id = je.entry_id AND je.is_posted = TRUE
        WHERE ca.player_id = %s AND ca.is_active = TRUE
        GROUP BY ca.account_id, ca.account_code, ca.account_name, ca.account_type, ca.normal_balance
        ORDER BY ca.account_code
    """, (player_id,))
    
    accounts = cur.fetchall()
    
    # Calculate balances based on normal balance type
    trial_balance = []
    total_debit_balance = 0
    total_credit_balance = 0
    
    for acc in accounts:
        net = float(acc['total_debits']) - float(acc['total_credits'])
        
        if acc['normal_balance'] == 'Debit':
            debit_bal = net if net >= 0 else 0
            credit_bal = abs(net) if net < 0 else 0
        else:
            credit_bal = abs(net) if net <= 0 else 0
            debit_bal = net if net > 0 else 0
        
        if debit_bal != 0 or credit_bal != 0:
            trial_balance.append({
                'account_code': acc['account_code'],
                'account_name': acc['account_name'],
                'account_type': acc['account_type'],
                'debit_balance': debit_bal,
                'credit_balance': credit_bal
            })
            total_debit_balance += debit_bal
            total_credit_balance += credit_bal
    
    cur.close()
    return_connection(conn)
    
    return {
        'accounts': trial_balance,
        'total_debits': total_debit_balance,
        'total_credits': total_credit_balance,
        'is_balanced': abs(total_debit_balance - total_credit_balance) < 0.01
    }


def get_income_statement(player_id: int) -> dict:
    """Generate an income statement (P&L) from Revenue and Expense accounts."""
    conn = get_connection()
    cur = conn.cursor()
    
    # Get Revenue accounts (4xxx)
    cur.execute("""
        SELECT ca.account_code, ca.account_name,
               COALESCE(SUM(jl.credit_amount), 0) - COALESCE(SUM(jl.debit_amount), 0) as balance
        FROM chart_of_accounts ca
        LEFT JOIN journal_lines jl ON ca.account_id = jl.account_id
        LEFT JOIN journal_entries je ON jl.entry_id = je.entry_id AND je.is_posted = TRUE
        WHERE ca.player_id = %s AND ca.account_type = 'Revenue'
        GROUP BY ca.account_id, ca.account_code, ca.account_name
        HAVING COALESCE(SUM(jl.credit_amount), 0) - COALESCE(SUM(jl.debit_amount), 0) != 0
        ORDER BY ca.account_code
    """, (player_id,))
    revenues = cur.fetchall()
    
    # Get Expense accounts (5xxx)
    cur.execute("""
        SELECT ca.account_code, ca.account_name,
               COALESCE(SUM(jl.debit_amount), 0) - COALESCE(SUM(jl.credit_amount), 0) as balance
        FROM chart_of_accounts ca
        LEFT JOIN journal_lines jl ON ca.account_id = jl.account_id
        LEFT JOIN journal_entries je ON jl.entry_id = je.entry_id AND je.is_posted = TRUE
        WHERE ca.player_id = %s AND ca.account_type = 'Expense'
        GROUP BY ca.account_id, ca.account_code, ca.account_name
        HAVING COALESCE(SUM(jl.debit_amount), 0) - COALESCE(SUM(jl.credit_amount), 0) != 0
        ORDER BY ca.account_code
    """, (player_id,))
    expenses = cur.fetchall()
    
    cur.close()
    return_connection(conn)
    
    total_revenue = sum(float(r['balance']) for r in revenues)
    total_expenses = sum(float(e['balance']) for e in expenses)
    net_income = total_revenue - total_expenses
    
    return {
        'revenues': revenues,
        'expenses': expenses,
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'net_income': net_income
    }


def get_balance_sheet(player_id: int) -> dict:
    """Generate a balance sheet from Asset, Liability, and Equity accounts."""
    conn = get_connection()
    cur = conn.cursor()
    
    # Get Assets
    cur.execute("""
        SELECT ca.account_code, ca.account_name, ca.normal_balance,
               COALESCE(SUM(jl.debit_amount), 0) - COALESCE(SUM(jl.credit_amount), 0) as balance
        FROM chart_of_accounts ca
        LEFT JOIN journal_lines jl ON ca.account_id = jl.account_id
        LEFT JOIN journal_entries je ON jl.entry_id = je.entry_id AND je.is_posted = TRUE
        WHERE ca.player_id = %s AND ca.account_type = 'Asset'
        GROUP BY ca.account_id, ca.account_code, ca.account_name, ca.normal_balance
        ORDER BY ca.account_code
    """, (player_id,))
    assets = [a for a in cur.fetchall() if float(a['balance']) != 0]
    
    # Get Liabilities
    cur.execute("""
        SELECT ca.account_code, ca.account_name,
               COALESCE(SUM(jl.credit_amount), 0) - COALESCE(SUM(jl.debit_amount), 0) as balance
        FROM chart_of_accounts ca
        LEFT JOIN journal_lines jl ON ca.account_id = jl.account_id
        LEFT JOIN journal_entries je ON jl.entry_id = je.entry_id AND je.is_posted = TRUE
        WHERE ca.player_id = %s AND ca.account_type = 'Liability'
        GROUP BY ca.account_id, ca.account_code, ca.account_name
        ORDER BY ca.account_code
    """, (player_id,))
    liabilities = [l for l in cur.fetchall() if float(l['balance']) != 0]
    
    # Get Equity
    cur.execute("""
        SELECT ca.account_code, ca.account_name, ca.normal_balance,
               CASE WHEN ca.normal_balance = 'Credit' 
                    THEN COALESCE(SUM(jl.credit_amount), 0) - COALESCE(SUM(jl.debit_amount), 0)
                    ELSE COALESCE(SUM(jl.debit_amount), 0) - COALESCE(SUM(jl.credit_amount), 0)
               END as balance
        FROM chart_of_accounts ca
        LEFT JOIN journal_lines jl ON ca.account_id = jl.account_id
        LEFT JOIN journal_entries je ON jl.entry_id = je.entry_id AND je.is_posted = TRUE
        WHERE ca.player_id = %s AND ca.account_type = 'Equity'
        GROUP BY ca.account_id, ca.account_code, ca.account_name, ca.normal_balance
        ORDER BY ca.account_code
    """, (player_id,))
    equity = [e for e in cur.fetchall() if float(e['balance']) != 0]
    
    cur.close()
    return_connection(conn)
    
    total_assets = sum(float(a['balance']) for a in assets)
    total_liabilities = sum(float(l['balance']) for l in liabilities)
    total_equity = sum(float(e['balance']) for e in equity)
    
    return {
        'assets': assets,
        'liabilities': liabilities,
        'equity': equity,
        'total_assets': total_assets,
        'total_liabilities': total_liabilities,
        'total_equity': total_equity,
        'is_balanced': abs(total_assets - (total_liabilities + total_equity)) < 0.01
    }


def process_pending_transaction(player_id: int, transaction_id: int, 
                                debit_account: str, credit_account: str) -> dict:
    """Process a pending transaction by creating a journal entry."""
    if not debit_account or not credit_account:
        return {'success': False, 'error': 'Invalid account codes provided', 'exp_earned': 0}
    
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT account_code FROM chart_of_accounts 
        WHERE player_id = %s AND account_code IN (%s, %s)
    """, (player_id, debit_account, credit_account))
    valid_accounts = [row['account_code'] for row in cur.fetchall()]
    
    if debit_account not in valid_accounts or credit_account not in valid_accounts:
        cur.close()
        return_connection(conn)
        return {'success': False, 'error': 'Invalid account codes - account not found', 'exp_earned': 0}
    
    cur.execute("""
        SELECT transaction_id, description, amount 
        FROM pending_transactions 
        WHERE transaction_id = %s AND player_id = %s AND is_processed = FALSE
    """, (transaction_id, player_id))
    
    txn = cur.fetchone()
    if not txn:
        cur.close()
        return_connection(conn)
        return {'success': False, 'error': 'Transaction not found or already processed', 'exp_earned': 0}
    
    amount = float(txn['amount']) if txn['amount'] is not None else 0
    if amount <= 0:
        cur.close()
        return_connection(conn)
        return {'success': False, 'error': 'Invalid transaction amount', 'exp_earned': 0}
    
    cur.close()
    return_connection(conn)
    
    lines = [
        {'account_code': debit_account, 'debit': amount, 'credit': 0},
        {'account_code': credit_account, 'debit': 0, 'credit': amount}
    ]
    
    result = create_journal_entry(player_id, txn['description'], lines)
    
    if result['success']:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE pending_transactions SET is_processed = TRUE WHERE transaction_id = %s", (transaction_id,))
        conn.commit()
        cur.close()
        return_connection(conn)
    
    return result


def get_player_initiatives(player_id: int) -> list:
    """Get all project initiatives for a player."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT initiative_id, title, description, world_type, industry,
               planned_duration_weeks, actual_duration_weeks, start_week, current_week,
               status, budget, spent, completion_bonus_exp, completion_bonus_cash,
               on_time_multiplier, created_at, completed_at
        FROM project_initiatives
        WHERE player_id = %s
        ORDER BY created_at DESC
    """, (player_id,))
    
    initiatives = [dict(row) for row in cur.fetchall()]
    
    for initiative in initiatives:
        cur.execute("""
            SELECT task_id, task_name, status, planned_start_week, planned_end_week,
                   actual_start_week, actual_end_week, is_critical_path, priority
            FROM project_tasks
            WHERE initiative_id = %s
            ORDER BY task_order
        """, (initiative['initiative_id'],))
        initiative['tasks'] = [dict(row) for row in cur.fetchall()]
        
        total_tasks = len(initiative['tasks'])
        completed_tasks = sum(1 for t in initiative['tasks'] if t['status'] == 'completed')
        initiative['progress_pct'] = int((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0)
    
    cur.close()
    return_connection(conn)
    return initiatives


def get_active_initiative(player_id: int) -> dict:
    """Get the player's currently active project initiative."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT initiative_id, title, description, planned_duration_weeks,
               current_week, status, budget, spent
        FROM project_initiatives
        WHERE player_id = %s AND status IN ('planning', 'in_progress')
        ORDER BY created_at DESC LIMIT 1
    """, (player_id,))
    
    result = cur.fetchone()
    if not result:
        cur.close()
        return_connection(conn)
        return None
    
    initiative = dict(result)
    
    cur.execute("""
        SELECT t.task_id, t.task_name, t.description, t.estimated_effort_hours,
               t.actual_effort_hours, t.planned_start_week, t.planned_end_week,
               t.actual_start_week, t.actual_end_week, t.status, t.priority,
               t.is_critical_path, t.task_order, t.exp_reward
        FROM project_tasks t
        WHERE t.initiative_id = %s
        ORDER BY t.task_order
    """, (initiative['initiative_id'],))
    initiative['tasks'] = [dict(row) for row in cur.fetchall()]
    
    for task in initiative['tasks']:
        cur.execute("""
            SELECT d.depends_on_task_id, pt.task_name
            FROM task_dependencies d
            JOIN project_tasks pt ON d.depends_on_task_id = pt.task_id
            WHERE d.task_id = %s
        """, (task['task_id'],))
        task['dependencies'] = [dict(row) for row in cur.fetchall()]
    
    cur.close()
    return_connection(conn)
    return initiative


def create_initiative_from_template(player_id: int, template_index: int = 0) -> dict:
    """Create a new project initiative from a template."""
    from src.database import get_project_templates
    
    templates = get_project_templates()
    if template_index >= len(templates):
        return {'success': False, 'error': 'Invalid template'}
    
    template = templates[template_index]
    
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM project_initiatives WHERE player_id = %s AND status IN ('planning', 'in_progress')", (player_id,))
    if cur.fetchone()['count'] > 0:
        cur.close()
        return_connection(conn)
        return {'success': False, 'error': 'Complete your current project first'}
    
    cur.execute("""
        INSERT INTO project_initiatives 
        (player_id, title, description, world_type, industry, planned_duration_weeks,
         budget, completion_bonus_exp, completion_bonus_cash, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'planning')
        RETURNING initiative_id
    """, (
        player_id, template['title'], template['description'],
        template['world_type'], template['industry'], template['planned_duration_weeks'],
        template['budget'], template['completion_bonus_exp'], template['completion_bonus_cash']
    ))
    
    initiative_id = cur.fetchone()['initiative_id']
    
    task_name_to_id = {}
    for i, task in enumerate(template['tasks']):
        cur.execute("""
            INSERT INTO project_tasks 
            (initiative_id, task_name, estimated_effort_hours, planned_start_week,
             planned_end_week, priority, task_order)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING task_id
        """, (
            initiative_id, task['name'], task['effort'],
            task['week_start'], task['week_end'], task['priority'], i
        ))
        task_name_to_id[task['name']] = cur.fetchone()['task_id']
    
    for task in template['tasks']:
        if 'depends_on' in task:
            task_id = task_name_to_id[task['name']]
            for dep_name in task['depends_on']:
                if dep_name in task_name_to_id:
                    cur.execute("""
                        INSERT INTO task_dependencies (task_id, depends_on_task_id, dependency_type)
                        VALUES (%s, %s, 'FS')
                    """, (task_id, task_name_to_id[dep_name]))
    
    calculate_critical_path(initiative_id)
    
    conn.commit()
    cur.close()
    return_connection(conn)
    
    return {'success': True, 'initiative_id': initiative_id, 'title': template['title']}


def calculate_critical_path(initiative_id: int):
    """Calculate and mark the critical path for a project."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT task_id, task_name, planned_start_week, planned_end_week
        FROM project_tasks WHERE initiative_id = %s
        ORDER BY planned_end_week DESC, planned_start_week DESC
    """, (initiative_id,))
    tasks = [dict(row) for row in cur.fetchall()]
    
    if not tasks:
        cur.close()
        return_connection(conn)
        return
    
    cur.execute("UPDATE project_tasks SET is_critical_path = FALSE WHERE initiative_id = %s", (initiative_id,))
    
    last_task = tasks[0]
    cur.execute("UPDATE project_tasks SET is_critical_path = TRUE WHERE task_id = %s", (last_task['task_id'],))
    
    critical_tasks = {last_task['task_id']}
    
    for _ in range(len(tasks)):
        for task_id in list(critical_tasks):
            cur.execute("""
                SELECT d.depends_on_task_id
                FROM task_dependencies d
                WHERE d.task_id = %s
            """, (task_id,))
            for row in cur.fetchall():
                dep_id = row['depends_on_task_id']
                if dep_id not in critical_tasks:
                    critical_tasks.add(dep_id)
                    cur.execute("UPDATE project_tasks SET is_critical_path = TRUE WHERE task_id = %s", (dep_id,))
    
    conn.commit()
    cur.close()
    return_connection(conn)


def advance_project_week(player_id: int, initiative_id: int) -> dict:
    """Advance the project by one week, updating task progress."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT initiative_id, current_week, planned_duration_weeks, status, budget, spent
        FROM project_initiatives
        WHERE initiative_id = %s AND player_id = %s
    """, (initiative_id, player_id))
    
    initiative = cur.fetchone()
    if not initiative:
        cur.close()
        return_connection(conn)
        return {'success': False, 'error': 'Project not found'}
    
    if initiative['status'] == 'completed':
        cur.close()
        return_connection(conn)
        return {'success': False, 'error': 'Project already completed'}
    
    current_week = initiative['current_week']
    new_week = current_week + 1
    
    cur.execute("""
        SELECT task_id, task_name, status, planned_start_week, planned_end_week,
               estimated_effort_hours, actual_effort_hours
        FROM project_tasks
        WHERE initiative_id = %s
    """, (initiative_id,))
    tasks = [dict(row) for row in cur.fetchall()]
    
    exp_earned = 0
    completed_this_week = []
    
    for task in tasks:
        if task['status'] == 'not_started' and task['planned_start_week'] <= current_week:
            cur.execute("""
                SELECT COUNT(*) as count FROM task_dependencies d
                JOIN project_tasks pt ON d.depends_on_task_id = pt.task_id
                WHERE d.task_id = %s AND pt.status != 'completed'
            """, (task['task_id'],))
            
            if cur.fetchone()['count'] == 0:
                cur.execute("""
                    UPDATE project_tasks SET status = 'in_progress', actual_start_week = %s
                    WHERE task_id = %s
                """, (current_week, task['task_id']))
        
        if task['status'] == 'in_progress':
            progress_hours = min(40, task['estimated_effort_hours'] - task['actual_effort_hours'])
            new_actual = task['actual_effort_hours'] + progress_hours
            
            if new_actual >= task['estimated_effort_hours']:
                cur.execute("""
                    UPDATE project_tasks 
                    SET status = 'completed', actual_effort_hours = %s, actual_end_week = %s
                    WHERE task_id = %s
                """, (task['estimated_effort_hours'], current_week, task['task_id']))
                completed_this_week.append(task['task_name'])
                exp_earned += 20
            else:
                cur.execute("UPDATE project_tasks SET actual_effort_hours = %s WHERE task_id = %s", 
                           (new_actual, task['task_id']))
    
    cur.execute("""
        SELECT COUNT(*) as total, SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as done
        FROM project_tasks WHERE initiative_id = %s
    """, (initiative_id,))
    progress = cur.fetchone()
    all_done = progress['total'] == progress['done']
    
    project_completed = False
    bonus_earned = 0
    
    if all_done:
        on_time = new_week <= initiative['planned_duration_weeks']
        multiplier = float(initiative['on_time_multiplier']) if on_time else 1.0
        
        cur.execute("""
            SELECT completion_bonus_exp, completion_bonus_cash
            FROM project_initiatives WHERE initiative_id = %s
        """, (initiative_id,))
        bonuses = cur.fetchone()
        
        bonus_earned = int(bonuses['completion_bonus_exp'] * multiplier)
        cash_bonus = float(bonuses['completion_bonus_cash']) * multiplier
        
        cur.execute("""
            UPDATE project_initiatives 
            SET status = 'completed', actual_duration_weeks = %s, current_week = %s,
                completed_at = CURRENT_TIMESTAMP
            WHERE initiative_id = %s
        """, (new_week, new_week, initiative_id))
        
        cur.execute("UPDATE player_profiles SET cash = cash + %s WHERE player_id = %s", (cash_bonus, player_id))
        
        project_completed = True
        exp_earned += bonus_earned
    else:
        cur.execute("UPDATE project_initiatives SET current_week = %s, status = 'in_progress' WHERE initiative_id = %s", 
                   (new_week, initiative_id))
    
    planned_pct = min(100, (current_week / initiative['planned_duration_weeks']) * 100)
    actual_pct = (progress['done'] / progress['total'] * 100) if progress['total'] > 0 else 0
    variance = actual_pct - planned_pct
    
    cur.execute("""
        INSERT INTO project_history (initiative_id, week_number, planned_completion_pct, actual_completion_pct, variance_pct)
        VALUES (%s, %s, %s, %s, %s)
    """, (initiative_id, current_week, planned_pct, actual_pct, variance))
    
    conn.commit()
    cur.close()
    return_connection(conn)
    
    return {
        'success': True,
        'new_week': new_week,
        'completed_tasks': completed_this_week,
        'exp_earned': exp_earned,
        'project_completed': project_completed,
        'bonus_earned': bonus_earned if project_completed else 0,
        'on_time': new_week <= initiative['planned_duration_weeks'] if project_completed else None
    }


def get_player_resources(player_id: int) -> list:
    """Get all resources available to a player."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT resource_id, resource_name, resource_type, capacity_hours_per_week,
               hourly_cost, skill_bonus, is_available
        FROM project_resources
        WHERE player_id = %s
        ORDER BY resource_id
    """, (player_id,))
    
    resources = [dict(row) for row in cur.fetchall()]
    cur.close()
    return_connection(conn)
    return resources


def get_scheduling_challenges(player_level: int = 1) -> list:
    """Get scheduling challenges available for a player's level."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT challenge_id, title, description, challenge_type, difficulty,
               required_level, exp_reward, time_limit_seconds, hint_text
        FROM scheduling_challenges
        WHERE required_level <= %s AND is_active = TRUE
        ORDER BY required_level, difficulty
    """, (player_level,))
    
    challenges = [dict(row) for row in cur.fetchall()]
    cur.close()
    return_connection(conn)
    return challenges


def get_scheduling_challenge(challenge_id: int) -> dict:
    """Get a specific scheduling challenge with full data."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT challenge_id, title, description, challenge_type, difficulty,
               task_data, correct_answer, exp_reward, time_limit_seconds, hint_text
        FROM scheduling_challenges
        WHERE challenge_id = %s AND is_active = TRUE
    """, (challenge_id,))
    
    result = cur.fetchone()
    cur.close()
    return_connection(conn)
    
    if result:
        import json
        challenge = dict(result)
        challenge['task_data'] = json.loads(challenge['task_data']) if challenge['task_data'] else {}
        challenge['correct_answer'] = json.loads(challenge['correct_answer']) if challenge['correct_answer'] else {}
        return challenge
    return None


def submit_scheduling_challenge(player_id: int, challenge_id: int, answer: dict) -> dict:
    """Submit an answer for a scheduling challenge."""
    challenge = get_scheduling_challenge(challenge_id)
    if not challenge:
        return {'success': False, 'error': 'Challenge not found', 'exp_earned': 0}
    
    correct = challenge['correct_answer']
    is_correct = False
    
    if challenge['challenge_type'] == 'critical_path':
        user_duration = answer.get('duration', 0)
        correct_duration = correct.get('duration', 0)
        is_correct = abs(user_duration - correct_duration) <= 1
    
    elif challenge['challenge_type'] == 'estimation':
        user_expected = answer.get('expected', 0)
        correct_expected = correct.get('expected', 0)
        is_correct = abs(user_expected - correct_expected) <= 0.5
    
    elif challenge['challenge_type'] == 'resource_leveling':
        is_correct = True
        user_assignments = answer.get('assignments', {})
        for task_id, resource_id in user_assignments.items():
            if not resource_id:
                is_correct = False
                break
    
    elif challenge['challenge_type'] == 'compression':
        is_correct = answer.get('choice') == correct.get('best_option')
    
    else:
        is_correct = answer == correct
    
    exp_earned = challenge['exp_reward'] if is_correct else int(challenge['exp_reward'] * 0.25)
    
    return {
        'success': True,
        'is_correct': is_correct,
        'exp_earned': exp_earned,
        'correct_answer': correct,
        'feedback': 'Correct! Great scheduling skills!' if is_correct else 'Not quite right. Review the hint and try again.'
    }


def get_project_templates_list() -> list:
    """Get list of available project templates."""
    from src.database import get_project_templates
    templates = get_project_templates()
    return [
        {
            'index': i,
            'title': t['title'],
            'description': t['description'],
            'duration': t['planned_duration_weeks'],
            'budget': t['budget'],
            'reward_exp': t['completion_bonus_exp'],
            'reward_cash': t['completion_bonus_cash'],
            'task_count': len(t['tasks'])
        }
        for i, t in enumerate(templates)
    ]


# ============================================================================
# CASH FLOW FORECASTING SYSTEM
# ============================================================================

def get_cash_flow_challenges(player_level: int = 1) -> list:
    """Get cash flow challenges available for the player."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT challenge_id, title, description, challenge_type, difficulty, exp_reward, hint_text
        FROM cash_flow_challenges
        WHERE difficulty <= %s AND is_active = TRUE
        ORDER BY difficulty
    """, (max(3, player_level),))
    
    challenges = [dict(row) for row in cur.fetchall()]
    cur.close()
    return_connection(conn)
    return challenges


def get_cash_flow_challenge(challenge_id: int) -> dict:
    """Get a specific cash flow challenge with full data."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT challenge_id, title, description, challenge_type, difficulty,
               scenario_data, correct_answer, exp_reward, hint_text
        FROM cash_flow_challenges
        WHERE challenge_id = %s AND is_active = TRUE
    """, (challenge_id,))
    
    result = cur.fetchone()
    cur.close()
    return_connection(conn)
    
    if result:
        import json
        challenge = dict(result)
        challenge['scenario_data'] = json.loads(challenge['scenario_data']) if challenge['scenario_data'] else {}
        challenge['correct_answer'] = json.loads(challenge['correct_answer']) if challenge['correct_answer'] else {}
        return challenge
    return None


def submit_cash_flow_challenge(player_id: int, challenge_id: int, answer: dict) -> dict:
    """Submit an answer for a cash flow challenge."""
    challenge = get_cash_flow_challenge(challenge_id)
    if not challenge:
        return {'success': False, 'error': 'Challenge not found', 'exp_earned': 0}
    
    correct = challenge['correct_answer']
    is_correct = False
    feedback = ''
    
    if challenge['challenge_type'] == 'timing':
        is_correct = answer.get('choice') == correct.get('best')
        feedback = correct.get('reason', '') if is_correct else 'Consider the weekly cash balance under each option.'
    
    elif challenge['challenge_type'] == 'planning':
        user_weeks = answer.get('weeks', 0)
        valid_range = correct.get('range', [8, 8])
        is_correct = valid_range[0] <= user_weeks <= valid_range[1]
        feedback = correct.get('reason', '') if is_correct else f'Recommended range is {valid_range[0]}-{valid_range[1]} weeks.'
    
    elif challenge['challenge_type'] == 'forecast':
        user_week = answer.get('credit_needed_week', 0)
        correct_week = correct.get('credit_needed_week', 0)
        is_correct = user_week == correct_week
        feedback = f'The cash dips below minimum in week {correct_week}.' if not is_correct else 'Excellent forecasting!'
    
    elif challenge['challenge_type'] == 'prioritization':
        is_correct = answer.get('priority', [])[:3] == correct.get('priority_order', [])[:3]
        feedback = correct.get('reasoning', '')
    
    elif challenge['challenge_type'] == 'seasonal':
        user_savings = answer.get('savings_needed', 0)
        correct_savings = correct.get('savings_needed', 0)
        is_correct = abs(user_savings - correct_savings) <= 2000
        feedback = f'You need about ${correct_savings:,} to cover the slow months.'
    
    exp_earned = challenge['exp_reward'] if is_correct else int(challenge['exp_reward'] * 0.25)
    
    return {
        'success': True,
        'is_correct': is_correct,
        'exp_earned': exp_earned,
        'correct_answer': correct,
        'feedback': feedback or ('Correct! Great cash flow thinking!' if is_correct else 'Not quite. Review the hint.')
    }


def create_cash_flow_forecast(player_id: int, forecast_name: str, starting_cash: float) -> dict:
    """Create a new 13-week cash flow forecast for a player."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT current_month FROM player_profiles WHERE player_id = %s", (player_id,))
    result = cur.fetchone()
    start_week = (result['current_month'] - 1) * 4 + 1 if result else 1
    
    cur.execute("""
        INSERT INTO cash_flow_forecasts (player_id, forecast_name, start_week)
        VALUES (%s, %s, %s)
        RETURNING forecast_id
    """, (player_id, forecast_name, start_week))
    
    forecast_id = cur.fetchone()['forecast_id']
    
    current_balance = starting_cash
    for week in range(1, 14):
        cur.execute("""
            INSERT INTO cash_flow_periods (forecast_id, week_number, beginning_cash, ending_cash)
            VALUES (%s, %s, %s, %s)
        """, (forecast_id, week, current_balance, current_balance))
    
    conn.commit()
    cur.close()
    return_connection(conn)
    
    return {'success': True, 'forecast_id': forecast_id}


def get_player_cash_flow_forecast(player_id: int) -> dict:
    """Get the player's active cash flow forecast with all periods."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT forecast_id, forecast_name, start_week, created_at
        FROM cash_flow_forecasts
        WHERE player_id = %s AND is_active = TRUE
        ORDER BY created_at DESC
        LIMIT 1
    """, (player_id,))
    
    forecast = cur.fetchone()
    if not forecast:
        cur.close()
        return_connection(conn)
        return None
    
    forecast = dict(forecast)
    
    cur.execute("""
        SELECT period_id, week_number, beginning_cash, projected_inflows, projected_outflows,
               ending_cash, actual_inflows, actual_outflows, actual_ending, variance, notes
        FROM cash_flow_periods
        WHERE forecast_id = %s
        ORDER BY week_number
    """, (forecast['forecast_id'],))
    
    forecast['periods'] = [dict(row) for row in cur.fetchall()]
    
    cur.close()
    return_connection(conn)
    return forecast


# ============================================================================
# BUSINESS PLAN WORKSHOP SYSTEM
# ============================================================================

BUSINESS_PLAN_SECTIONS = [
    {'type': 'executive_summary', 'name': 'Executive Summary', 'order': 1, 'description': 'A concise overview of your business concept, goals, and key metrics.'},
    {'type': 'company_description', 'name': 'Company Description', 'order': 2, 'description': 'What your business does, its mission, and what makes it unique.'},
    {'type': 'market_analysis', 'name': 'Market Analysis', 'order': 3, 'description': 'Your target market, competition, and industry trends.'},
    {'type': 'products_services', 'name': 'Products & Services', 'order': 4, 'description': 'What you sell, pricing strategy, and competitive advantages.'},
    {'type': 'marketing_plan', 'name': 'Marketing Plan', 'order': 5, 'description': 'How you will reach customers and build your brand.'},
    {'type': 'operations_plan', 'name': 'Operations Plan', 'order': 6, 'description': 'Day-to-day operations, suppliers, and key processes.'},
    {'type': 'financial_projections', 'name': 'Financial Projections', 'order': 7, 'description': 'Revenue forecasts, expense estimates, and break-even analysis.'},
    {'type': 'funding_request', 'name': 'Funding Request', 'order': 8, 'description': 'How much funding you need and how you will use it.'}
]


def create_business_plan(player_id: int, plan_name: str, business_type: str = None) -> dict:
    """Create a new business plan for a player."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO business_plans (player_id, plan_name, business_type)
        VALUES (%s, %s, %s)
        RETURNING plan_id
    """, (player_id, plan_name, business_type))
    
    plan_id = cur.fetchone()['plan_id']
    
    for section in BUSINESS_PLAN_SECTIONS:
        cur.execute("""
            INSERT INTO business_plan_sections (plan_id, section_type, section_order)
            VALUES (%s, %s, %s)
        """, (plan_id, section['type'], section['order']))
    
    conn.commit()
    cur.close()
    return_connection(conn)
    
    return {'success': True, 'plan_id': plan_id}


def get_player_business_plans(player_id: int) -> list:
    """Get all business plans for a player."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT plan_id, plan_name, business_type, overall_score, status, created_at, updated_at
        FROM business_plans
        WHERE player_id = %s
        ORDER BY updated_at DESC
    """, (player_id,))
    
    plans = [dict(row) for row in cur.fetchall()]
    cur.close()
    return_connection(conn)
    return plans


def get_business_plan(plan_id: int) -> dict:
    """Get a specific business plan with all sections."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT plan_id, player_id, plan_name, business_type, target_market,
               overall_score, mentor_feedback, status, created_at
        FROM business_plans
        WHERE plan_id = %s
    """, (plan_id,))
    
    plan = cur.fetchone()
    if not plan:
        cur.close()
        return_connection(conn)
        return None
    
    plan = dict(plan)
    
    cur.execute("""
        SELECT section_id, section_type, section_order, content, score, feedback, is_complete
        FROM business_plan_sections
        WHERE plan_id = %s
        ORDER BY section_order
    """, (plan_id,))
    
    sections = [dict(row) for row in cur.fetchall()]
    
    for section in sections:
        section_info = next((s for s in BUSINESS_PLAN_SECTIONS if s['type'] == section['section_type']), None)
        if section_info:
            section['name'] = section_info['name']
            section['description'] = section_info['description']
    
    plan['sections'] = sections
    plan['completion_pct'] = sum(1 for s in sections if s['is_complete']) / len(sections) * 100 if sections else 0
    
    cur.close()
    return_connection(conn)
    return plan


def update_business_plan_section(section_id: int, content: str) -> dict:
    """Update a business plan section and generate mentor feedback."""
    conn = get_connection()
    cur = conn.cursor()
    
    score = min(100, len(content.split()) * 2)
    feedback = generate_section_feedback(content, score)
    is_complete = len(content.strip()) >= 50
    
    cur.execute("""
        UPDATE business_plan_sections
        SET content = %s, score = %s, feedback = %s, is_complete = %s
        WHERE section_id = %s
    """, (content, score, feedback, is_complete, section_id))
    
    cur.execute("SELECT plan_id FROM business_plan_sections WHERE section_id = %s", (section_id,))
    plan_id = cur.fetchone()['plan_id']
    
    cur.execute("""
        SELECT AVG(score)::int as avg_score FROM business_plan_sections WHERE plan_id = %s AND is_complete = TRUE
    """, (plan_id,))
    avg_score = cur.fetchone()['avg_score'] or 0
    
    cur.execute("UPDATE business_plans SET overall_score = %s, updated_at = CURRENT_TIMESTAMP WHERE plan_id = %s", (avg_score, plan_id))
    
    conn.commit()
    cur.close()
    return_connection(conn)
    
    return {'success': True, 'score': score, 'feedback': feedback, 'is_complete': is_complete}


def generate_section_feedback(content: str, score: int) -> str:
    """Generate mentor feedback for a business plan section."""
    word_count = len(content.split())
    
    if word_count < 25:
        return "This section needs more detail. Try to expand on your key points."
    elif word_count < 50:
        return "Good start! Consider adding specific numbers, examples, or market data."
    elif word_count < 100:
        return "Solid content. Make sure you've addressed all key aspects of this section."
    elif score >= 80:
        return "Excellent work! This section is comprehensive and well-thought-out."
    else:
        return "Good effort. Consider adding more specific details and actionable insights."


# ============================================================================
# NEGOTIATION SIMULATOR SYSTEM
# ============================================================================

def get_negotiation_scenarios(player_level: int = 1) -> list:
    """Get available negotiation scenarios for a player."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT scenario_id, title, description, negotiation_type, difficulty,
               counterparty_name, exp_reward
        FROM negotiation_scenarios
        WHERE difficulty <= %s AND is_active = TRUE
        ORDER BY difficulty
    """, (max(3, player_level),))
    
    scenarios = [dict(row) for row in cur.fetchall()]
    cur.close()
    return_connection(conn)
    return scenarios


def get_negotiation_scenario(scenario_id: int) -> dict:
    """Get a specific negotiation scenario with full data."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT scenario_id, title, description, negotiation_type, difficulty,
               counterparty_name, counterparty_style, your_batna, their_batna,
               issues, opening_position, optimal_outcome, exp_reward
        FROM negotiation_scenarios
        WHERE scenario_id = %s AND is_active = TRUE
    """, (scenario_id,))
    
    result = cur.fetchone()
    cur.close()
    return_connection(conn)
    
    if result:
        import json
        scenario = dict(result)
        for field in ['your_batna', 'their_batna', 'issues', 'opening_position', 'optimal_outcome']:
            scenario[field] = json.loads(scenario[field]) if scenario[field] else {}
        return scenario
    return None


def start_negotiation(player_id: int, scenario_id: int) -> dict:
    """Start a new negotiation session for a player."""
    conn = get_connection()
    cur = conn.cursor()
    
    import json
    
    cur.execute("""
        INSERT INTO player_negotiations (player_id, scenario_id, player_offers, counterparty_offers)
        VALUES (%s, %s, %s, %s)
        RETURNING negotiation_id
    """, (player_id, scenario_id, json.dumps([]), json.dumps([])))
    
    negotiation_id = cur.fetchone()['negotiation_id']
    conn.commit()
    cur.close()
    return_connection(conn)
    
    return {'success': True, 'negotiation_id': negotiation_id}


def submit_negotiation_offer(negotiation_id: int, offer: dict) -> dict:
    """Submit a negotiation offer and get counterparty response."""
    conn = get_connection()
    cur = conn.cursor()
    
    import json
    
    cur.execute("""
        SELECT n.*, s.issues, s.optimal_outcome, s.counterparty_style, s.exp_reward
        FROM player_negotiations n
        JOIN negotiation_scenarios s ON n.scenario_id = s.scenario_id
        WHERE n.negotiation_id = %s
    """, (negotiation_id,))
    
    result = cur.fetchone()
    if not result:
        cur.close()
        return_connection(conn)
        return {'success': False, 'error': 'Negotiation not found'}
    
    neg = dict(result)
    issues = json.loads(neg['issues']) if neg['issues'] else []
    optimal = json.loads(neg['optimal_outcome']) if neg['optimal_outcome'] else {}
    player_offers = json.loads(neg['player_offers']) if neg['player_offers'] else []
    counterparty_offers = json.loads(neg['counterparty_offers']) if neg['counterparty_offers'] else []
    
    player_offers.append(offer)
    
    counter_offer = {}
    for issue in issues:
        issue_name = issue['name']
        player_value = offer.get(issue_name, issue['their_ideal'])
        their_ideal = issue['their_ideal']
        your_ideal = issue['your_ideal']
        
        movement = (player_value - their_ideal) * 0.3
        counter_offer[issue_name] = round(their_ideal + movement, 2)
    
    counterparty_offers.append(counter_offer)
    new_round = neg['current_round'] + 1
    
    deal_reached = new_round >= 4
    
    if deal_reached:
        final_deal = {}
        for issue in issues:
            issue_name = issue['name']
            final_deal[issue_name] = (offer.get(issue_name, 0) + counter_offer.get(issue_name, 0)) / 2
        
        deal_value = calculate_deal_value(final_deal, optimal, issues)
        exp_earned = int(neg['exp_reward'] * (deal_value / 100))
        
        cur.execute("""
            UPDATE player_negotiations
            SET player_offers = %s, counterparty_offers = %s, current_round = %s,
                status = 'completed', final_deal = %s, deal_value = %s, exp_earned = %s,
                completed_at = CURRENT_TIMESTAMP
            WHERE negotiation_id = %s
        """, (json.dumps(player_offers), json.dumps(counterparty_offers), new_round,
              json.dumps(final_deal), deal_value, exp_earned, negotiation_id))
        
        conn.commit()
        cur.close()
        return_connection(conn)
        
        return {
            'success': True,
            'deal_reached': True,
            'final_deal': final_deal,
            'deal_value': deal_value,
            'exp_earned': exp_earned,
            'message': f'Deal reached! You scored {deal_value}% of optimal value.'
        }
    
    cur.execute("""
        UPDATE player_negotiations
        SET player_offers = %s, counterparty_offers = %s, current_round = %s
        WHERE negotiation_id = %s
    """, (json.dumps(player_offers), json.dumps(counterparty_offers), new_round, negotiation_id))
    
    conn.commit()
    cur.close()
    return_connection(conn)
    
    return {
        'success': True,
        'deal_reached': False,
        'counter_offer': counter_offer,
        'current_round': new_round,
        'message': f'Round {new_round}: Counterparty made a counter-offer.'
    }


def calculate_deal_value(final_deal: dict, optimal: dict, issues: list) -> float:
    """Calculate how close the deal is to the optimal outcome as a percentage."""
    if not issues:
        return 50.0
    
    total_score = 0
    total_weight = 0
    
    for issue in issues:
        issue_name = issue['name']
        importance = issue.get('importance_you', 5)
        your_ideal = issue.get('your_ideal', 0)
        their_ideal = issue.get('their_ideal', 0)
        final_value = final_deal.get(issue_name, their_ideal)
        
        if their_ideal != your_ideal:
            score = 100 * (1 - abs(final_value - your_ideal) / abs(their_ideal - your_ideal))
        else:
            score = 100
        
        total_score += max(0, min(100, score)) * importance
        total_weight += importance
    
    return round(total_score / total_weight, 1) if total_weight > 0 else 50.0


# ============================================================================
# RISK MANAGEMENT DASHBOARD SYSTEM
# ============================================================================

def get_risk_categories() -> list:
    """Get all risk categories."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT category_id, category_name, description, icon FROM risk_categories ORDER BY category_id")
    categories = [dict(row) for row in cur.fetchall()]
    
    cur.close()
    return_connection(conn)
    return categories


def get_player_risks(player_id: int) -> list:
    """Get all risks identified by a player."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT r.risk_id, r.risk_name, r.description, r.probability, r.impact, r.risk_score,
               r.mitigation_strategy, r.status, c.category_name, c.icon
        FROM player_risks r
        JOIN risk_categories c ON r.category_id = c.category_id
        WHERE r.player_id = %s
        ORDER BY r.risk_score DESC
    """, (player_id,))
    
    risks = [dict(row) for row in cur.fetchall()]
    cur.close()
    return_connection(conn)
    return risks


def add_player_risk(player_id: int, category_id: int, risk_name: str, description: str,
                   probability: int, impact: int, mitigation: str = None) -> dict:
    """Add a new risk to a player's risk register."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO player_risks (player_id, category_id, risk_name, description, probability, impact, mitigation_strategy)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING risk_id, risk_score
    """, (player_id, category_id, risk_name, description, probability, impact, mitigation))
    
    result = cur.fetchone()
    conn.commit()
    cur.close()
    return_connection(conn)
    
    return {'success': True, 'risk_id': result['risk_id'], 'risk_score': result['risk_score']}


def update_risk_mitigation(risk_id: int, mitigation: str) -> dict:
    """Update the mitigation strategy for a risk."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        UPDATE player_risks SET mitigation_strategy = %s, status = 'mitigated'
        WHERE risk_id = %s
    """, (mitigation, risk_id))
    
    conn.commit()
    cur.close()
    return_connection(conn)
    
    return {'success': True}


# ============================================================================
# SUPPLY CHAIN SIMULATOR SYSTEM  
# ============================================================================

def initialize_player_supply_chain(player_id: int) -> bool:
    """Initialize supply chain with default products and suppliers."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM supply_chain_products WHERE player_id = %s", (player_id,))
    if cur.fetchone()['count'] > 0:
        cur.close()
        return_connection(conn)
        return False
    
    default_products = [
        ('Fresh Produce', 'PROD-001', 2.50, 8.00, 20, 50, 3, 100, 10),
        ('Meat & Poultry', 'PROD-002', 8.00, 25.00, 15, 30, 2, 50, 5),
        ('Dry Goods', 'PROD-003', 1.00, 4.00, 50, 100, 7, 200, 25),
        ('Beverages', 'PROD-004', 0.75, 3.00, 30, 60, 5, 150, 15),
        ('Cleaning Supplies', 'PROD-005', 3.00, 0, 10, 25, 7, 50, 5)
    ]
    
    for prod in default_products:
        cur.execute("""
            INSERT INTO supply_chain_products 
            (player_id, product_name, sku, unit_cost, selling_price, reorder_point, reorder_quantity, lead_time_days, current_stock, safety_stock)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (player_id, *prod))
    
    default_suppliers = [
        ('Local Farm Co-op', 90, 70, 2, 100, 'Net 15', 1),
        ('Regional Distributor', 80, 60, 5, 250, 'Net 30', 1),
        ('National Wholesaler', 70, 85, 7, 500, 'Net 45', 1),
        ('Specialty Importer', 75, 40, 14, 1000, 'Net 30', 1)
    ]
    
    for sup in default_suppliers:
        cur.execute("""
            INSERT INTO suppliers 
            (player_id, supplier_name, reliability_score, price_competitiveness, lead_time_days, minimum_order, payment_terms, relationship_level)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (player_id, *sup))
    
    conn.commit()
    cur.close()
    return_connection(conn)
    return True


def get_player_inventory(player_id: int) -> list:
    """Get all products in player's inventory."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT product_id, product_name, sku, unit_cost, selling_price, reorder_point,
               reorder_quantity, lead_time_days, current_stock, safety_stock
        FROM supply_chain_products
        WHERE player_id = %s
        ORDER BY product_name
    """, (player_id,))
    
    products = [dict(row) for row in cur.fetchall()]
    
    for prod in products:
        prod['status'] = 'ok'
        if prod['current_stock'] <= prod['safety_stock']:
            prod['status'] = 'critical'
        elif prod['current_stock'] <= prod['reorder_point']:
            prod['status'] = 'reorder'
    
    cur.close()
    return_connection(conn)
    return products


def get_player_suppliers(player_id: int) -> list:
    """Get all suppliers for a player."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT supplier_id, supplier_name, reliability_score, price_competitiveness,
               lead_time_days, minimum_order, payment_terms, relationship_level
        FROM suppliers
        WHERE player_id = %s
        ORDER BY reliability_score DESC
    """, (player_id,))
    
    suppliers = [dict(row) for row in cur.fetchall()]
    cur.close()
    return_connection(conn)
    return suppliers


def create_purchase_order(player_id: int, supplier_id: int, product_id: int, quantity: int) -> dict:
    """Create a new purchase order."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT unit_cost FROM supply_chain_products WHERE product_id = %s", (product_id,))
    product = cur.fetchone()
    if not product:
        cur.close()
        return_connection(conn)
        return {'success': False, 'error': 'Product not found'}
    
    cur.execute("SELECT lead_time_days, minimum_order FROM suppliers WHERE supplier_id = %s", (supplier_id,))
    supplier = cur.fetchone()
    if not supplier:
        cur.close()
        return_connection(conn)
        return {'success': False, 'error': 'Supplier not found'}
    
    total_cost = float(product['unit_cost']) * quantity
    
    cur.execute("""
        INSERT INTO purchase_orders (player_id, supplier_id, product_id, quantity, unit_cost, total_cost, expected_delivery)
        VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP + INTERVAL '%s days')
        RETURNING order_id
    """, (player_id, supplier_id, product_id, quantity, product['unit_cost'], total_cost, supplier['lead_time_days']))
    
    order_id = cur.fetchone()['order_id']
    conn.commit()
    cur.close()
    return_connection(conn)
    
    return {'success': True, 'order_id': order_id, 'total_cost': total_cost}


# ============================================================================
# MARKET SIMULATION FUNCTIONS
# ============================================================================

def get_market_segments() -> list:
    """Get all market segments."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM market_segments ORDER BY segment_size DESC")
    segments = cur.fetchall()
    cur.close()
    return_connection(conn)
    return [dict(s) for s in segments]


def get_market_challenges(player_level: int = 1) -> list:
    """Get market challenges appropriate for player level."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM market_challenges 
        WHERE difficulty <= %s
        ORDER BY difficulty, challenge_id
    """, (player_level,))
    challenges = cur.fetchall()
    cur.close()
    return_connection(conn)
    
    result = []
    for ch in challenges:
        challenge = dict(ch)
        if challenge.get('scenario_data'):
            challenge['scenario_data'] = json.loads(challenge['scenario_data']) if isinstance(challenge['scenario_data'], str) else challenge['scenario_data']
        if challenge.get('correct_answer'):
            challenge['correct_answer'] = json.loads(challenge['correct_answer']) if isinstance(challenge['correct_answer'], str) else challenge['correct_answer']
        result.append(challenge)
    return result


def get_market_challenge(challenge_id: int) -> dict:
    """Get a specific market challenge."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM market_challenges WHERE challenge_id = %s", (challenge_id,))
    ch = cur.fetchone()
    cur.close()
    return_connection(conn)
    
    if not ch:
        return None
    
    challenge = dict(ch)
    if challenge.get('scenario_data'):
        challenge['scenario_data'] = json.loads(challenge['scenario_data']) if isinstance(challenge['scenario_data'], str) else challenge['scenario_data']
    if challenge.get('correct_answer'):
        challenge['correct_answer'] = json.loads(challenge['correct_answer']) if isinstance(challenge['correct_answer'], str) else challenge['correct_answer']
    return challenge


def submit_market_challenge(player_id: int, challenge_id: int, answer: dict) -> dict:
    """Submit an answer to a market challenge."""
    challenge = get_market_challenge(challenge_id)
    if not challenge:
        return {'is_correct': False, 'feedback': 'Challenge not found', 'exp_earned': 0}
    
    correct = challenge['correct_answer']
    is_correct = False
    feedback = ''
    
    if challenge['challenge_type'] == 'pricing':
        user_revenue = answer.get('new_revenue', 0)
        correct_revenue = correct.get('new_revenue', 0)
        is_correct = abs(user_revenue - correct_revenue) <= 100
        feedback = f"Correct answer: ${correct_revenue}. New Price × New Quantity = Revenue"
        
    elif challenge['challenge_type'] == 'competition':
        is_correct = answer.get('decision', '').lower() == correct.get('decision', '').lower()
        feedback = correct.get('reason', 'Consider the long-term cost of each option.')
        
    elif challenge['challenge_type'] == 'marketing':
        user_roi = answer.get('roi', 0)
        correct_roi = correct.get('roi', 0)
        is_correct = abs(user_roi - correct_roi) <= 5
        feedback = f"ROI = (Profit - Cost) / Cost × 100 = {correct_roi}%"
        
    elif challenge['challenge_type'] == 'segmentation':
        is_correct = answer.get('best_segment', '').lower() == correct.get('best_segment', '').lower()
        feedback = f"Best segment: {correct.get('best_segment')} with expected profit of ${correct.get('profit', 0)}"
        
    elif challenge['challenge_type'] == 'positioning':
        is_correct = 'value' in answer.get('strategy', '').lower()
        feedback = correct.get('reason', 'Position yourself where competition is weak.')
    
    exp_earned = challenge['exp_reward'] if is_correct else challenge['exp_reward'] // 4
    
    if is_correct:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE player_discipline_progress 
            SET current_exp = current_exp + %s, total_exp_earned = total_exp_earned + %s
            WHERE player_id = %s AND discipline_name = 'Marketing'
        """, (exp_earned, exp_earned, player_id))
        conn.commit()
        cur.close()
        return_connection(conn)
    
    return {
        'is_correct': is_correct,
        'feedback': feedback,
        'exp_earned': exp_earned
    }


def initialize_player_market(player_id: int) -> bool:
    """Initialize player's market position."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM player_market_position WHERE player_id = %s", (player_id,))
    if cur.fetchone()['count'] > 0:
        cur.close()
        return_connection(conn)
        return True
    
    cur.execute("SELECT segment_id FROM market_segments")
    segments = cur.fetchall()
    
    for seg in segments:
        cur.execute("""
            INSERT INTO player_market_position 
            (player_id, segment_id, market_share, price_point, quality_rating, brand_awareness)
            VALUES (%s, %s, 0.01, 50, 50, 10)
        """, (player_id, seg['segment_id']))
    
    conn.commit()
    cur.close()
    return_connection(conn)
    return True


def get_player_market_position(player_id: int) -> list:
    """Get player's market position across all segments."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT pmp.*, ms.segment_name, ms.segment_size, ms.price_sensitivity, ms.quality_preference
        FROM player_market_position pmp
        JOIN market_segments ms ON pmp.segment_id = ms.segment_id
        WHERE pmp.player_id = %s
    """, (player_id,))
    positions = cur.fetchall()
    cur.close()
    return_connection(conn)
    return [dict(p) for p in positions]


# ============================================================================
# HR MANAGEMENT FUNCTIONS
# ============================================================================

def get_employee_roles() -> list:
    """Get all available employee roles."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM employee_roles ORDER BY department, base_salary")
    roles = cur.fetchall()
    cur.close()
    return_connection(conn)
    
    result = []
    for r in roles:
        role = dict(r)
        if role.get('skill_requirements'):
            role['skill_requirements'] = json.loads(role['skill_requirements']) if isinstance(role['skill_requirements'], str) else role['skill_requirements']
        result.append(role)
    return result


def get_hr_challenges(player_level: int = 1) -> list:
    """Get HR challenges appropriate for player level."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM hr_challenges 
        WHERE difficulty <= %s
        ORDER BY difficulty, challenge_id
    """, (player_level,))
    challenges = cur.fetchall()
    cur.close()
    return_connection(conn)
    
    result = []
    for ch in challenges:
        challenge = dict(ch)
        if challenge.get('scenario_data'):
            challenge['scenario_data'] = json.loads(challenge['scenario_data']) if isinstance(challenge['scenario_data'], str) else challenge['scenario_data']
        if challenge.get('correct_answer'):
            challenge['correct_answer'] = json.loads(challenge['correct_answer']) if isinstance(challenge['correct_answer'], str) else challenge['correct_answer']
        result.append(challenge)
    return result


def get_hr_challenge(challenge_id: int) -> dict:
    """Get a specific HR challenge."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM hr_challenges WHERE challenge_id = %s", (challenge_id,))
    ch = cur.fetchone()
    cur.close()
    return_connection(conn)
    
    if not ch:
        return None
    
    challenge = dict(ch)
    if challenge.get('scenario_data'):
        challenge['scenario_data'] = json.loads(challenge['scenario_data']) if isinstance(challenge['scenario_data'], str) else challenge['scenario_data']
    if challenge.get('correct_answer'):
        challenge['correct_answer'] = json.loads(challenge['correct_answer']) if isinstance(challenge['correct_answer'], str) else challenge['correct_answer']
    return challenge


def submit_hr_challenge(player_id: int, challenge_id: int, answer: dict) -> dict:
    """Submit an answer to an HR challenge."""
    challenge = get_hr_challenge(challenge_id)
    if not challenge:
        return {'is_correct': False, 'feedback': 'Challenge not found', 'exp_earned': 0}
    
    correct = challenge['correct_answer']
    is_correct = False
    feedback = ''
    
    if challenge['challenge_type'] == 'hiring':
        is_correct = answer.get('choice', '').upper() == correct.get('choice', '').upper()
        feedback = correct.get('reason', 'Consider budget and long-term potential.')
        
    elif challenge['challenge_type'] == 'performance':
        user_rating = answer.get('rating', 0)
        correct_rating = correct.get('rating', 0)
        is_correct = abs(user_rating - correct_rating) <= 1
        feedback = correct.get('reason', 'Balance all factors in your assessment.')
        
    elif challenge['challenge_type'] == 'conflict':
        is_correct = 'mediate' in answer.get('approach', '').lower()
        feedback = 'Best approach: ' + ', '.join(correct.get('actions', []))
        
    elif challenge['challenge_type'] == 'retention':
        has_creative_solution = len(answer.get('perks', [])) >= 2
        is_correct = has_creative_solution
        feedback = 'Total compensation includes salary, flexibility, growth opportunities, and recognition.'
        
    elif challenge['challenge_type'] == 'culture':
        is_correct = answer.get('choice', '').lower() == correct.get('choice', '').lower()
        feedback = correct.get('reason', 'Consider what builds team bonds.')
    
    exp_earned = challenge['exp_reward'] if is_correct else challenge['exp_reward'] // 4
    
    if is_correct:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE player_discipline_progress 
            SET current_exp = current_exp + %s, total_exp_earned = total_exp_earned + %s
            WHERE player_id = %s AND discipline_name = 'Human Resources'
        """, (exp_earned, exp_earned, player_id))
        conn.commit()
        cur.close()
        return_connection(conn)
    
    return {
        'is_correct': is_correct,
        'feedback': feedback,
        'exp_earned': exp_earned
    }


def get_player_employees(player_id: int) -> list:
    """Get all employees for a player."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT pe.*, er.role_name, er.department, er.base_salary
        FROM player_employees pe
        JOIN employee_roles er ON pe.role_id = er.role_id
        WHERE pe.player_id = %s AND pe.status = 'active'
        ORDER BY er.department, pe.employee_name
    """, (player_id,))
    employees = cur.fetchall()
    cur.close()
    return_connection(conn)
    return [dict(e) for e in employees]


def hire_employee(player_id: int, role_id: int, employee_name: str, salary: float) -> dict:
    """Hire a new employee."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO player_employees (player_id, employee_name, role_id, salary)
        VALUES (%s, %s, %s, %s)
        RETURNING employee_id
    """, (player_id, employee_name, role_id, salary))
    
    employee_id = cur.fetchone()['employee_id']
    conn.commit()
    cur.close()
    return_connection(conn)
    
    return {'success': True, 'employee_id': employee_id}


def conduct_performance_review(employee_id: int, rating: int, feedback: str, development_plan: str) -> dict:
    """Conduct a performance review for an employee."""
    conn = get_connection()
    cur = conn.cursor()
    
    salary_adjustment = (rating - 3) * 2.0
    exp_earned = rating * 25
    
    cur.execute("""
        INSERT INTO performance_reviews 
        (employee_id, rating, feedback_given, development_plan, salary_adjustment, exp_earned)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING review_id
    """, (employee_id, rating, feedback, development_plan, salary_adjustment, exp_earned))
    
    review_id = cur.fetchone()['review_id']
    
    cur.execute("""
        UPDATE player_employees 
        SET performance_score = %s, 
            salary = salary * (1 + %s / 100)
        WHERE employee_id = %s
    """, (rating * 20, salary_adjustment, employee_id))
    
    conn.commit()
    cur.close()
    return_connection(conn)
    
    return {'success': True, 'review_id': review_id, 'salary_adjustment_pct': salary_adjustment, 'exp_earned': exp_earned}


# ============================================================================
# INVESTOR PITCH FUNCTIONS
# ============================================================================

PITCH_SECTIONS = [
    {'order': 1, 'name': 'Title Slide', 'description': 'Company name, tagline, your name and title'},
    {'order': 2, 'name': 'Problem', 'description': 'The pain point you\'re solving - make it relatable and quantifiable'},
    {'order': 3, 'name': 'Solution', 'description': 'Your product/service and how it solves the problem'},
    {'order': 4, 'name': 'Market Opportunity', 'description': 'TAM, SAM, SOM - the size of your opportunity'},
    {'order': 5, 'name': 'Business Model', 'description': 'How you make money'},
    {'order': 6, 'name': 'Traction', 'description': 'Proof that it\'s working - metrics, customers, revenue'},
    {'order': 7, 'name': 'Team', 'description': 'Why you\'re the right team to solve this'},
    {'order': 8, 'name': 'The Ask', 'description': 'How much you need and what you\'ll do with it'}
]


def get_investor_profiles() -> list:
    """Get all investor profiles."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM investor_profiles ORDER BY investor_name")
    investors = cur.fetchall()
    cur.close()
    return_connection(conn)
    
    result = []
    for inv in investors:
        investor = dict(inv)
        if investor.get('focus_areas'):
            investor['focus_areas'] = json.loads(investor['focus_areas']) if isinstance(investor['focus_areas'], str) else investor['focus_areas']
        if investor.get('priorities'):
            investor['priorities'] = json.loads(investor['priorities']) if isinstance(investor['priorities'], str) else investor['priorities']
        result.append(investor)
    return result


def create_pitch_deck(player_id: int, deck_name: str, funding_stage: str = 'seed', target_amount: float = 100000) -> dict:
    """Create a new pitch deck."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO player_pitch_decks (player_id, deck_name, funding_stage, target_amount)
        VALUES (%s, %s, %s, %s)
        RETURNING deck_id
    """, (player_id, deck_name, funding_stage, target_amount))
    
    deck_id = cur.fetchone()['deck_id']
    
    for section in PITCH_SECTIONS:
        cur.execute("""
            INSERT INTO pitch_deck_sections (deck_id, section_name, section_order)
            VALUES (%s, %s, %s)
        """, (deck_id, section['name'], section['order']))
    
    conn.commit()
    cur.close()
    return_connection(conn)
    
    return {'success': True, 'deck_id': deck_id}


def get_player_pitch_decks(player_id: int) -> list:
    """Get all pitch decks for a player."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM player_pitch_decks 
        WHERE player_id = %s 
        ORDER BY created_at DESC
    """, (player_id,))
    decks = cur.fetchall()
    cur.close()
    return_connection(conn)
    return [dict(d) for d in decks]


def get_pitch_deck(deck_id: int) -> dict:
    """Get a pitch deck with all its sections."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM player_pitch_decks WHERE deck_id = %s", (deck_id,))
    deck = cur.fetchone()
    if not deck:
        cur.close()
        return_connection(conn)
        return None
    
    deck = dict(deck)
    
    cur.execute("""
        SELECT * FROM pitch_deck_sections 
        WHERE deck_id = %s 
        ORDER BY section_order
    """, (deck_id,))
    sections = cur.fetchall()
    
    deck['sections'] = []
    completed_count = 0
    total_score = 0
    
    for s in sections:
        section = dict(s)
        section['description'] = next((ps['description'] for ps in PITCH_SECTIONS if ps['name'] == section['section_name']), '')
        deck['sections'].append(section)
        if section['is_complete']:
            completed_count += 1
        total_score += section['score']
    
    deck['completion_pct'] = (completed_count / len(sections) * 100) if sections else 0
    deck['overall_score'] = total_score // len(sections) if sections else 0
    
    cur.close()
    return_connection(conn)
    return deck


def update_pitch_section(section_id: int, content: str) -> dict:
    """Update a pitch deck section and score it."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT section_name FROM pitch_deck_sections WHERE section_id = %s", (section_id,))
    section = cur.fetchone()
    if not section:
        cur.close()
        return_connection(conn)
        return {'success': False}
    
    score = 0
    feedback = ''
    word_count = len(content.split())
    
    if word_count < 10:
        score = 20
        feedback = 'Too brief. Add more detail to make your point compelling.'
    elif word_count < 30:
        score = 50
        feedback = 'Good start. Consider adding specific examples or data.'
    elif word_count < 75:
        score = 75
        feedback = 'Solid content. Make sure it answers investor questions.'
    else:
        score = 90
        feedback = 'Comprehensive. Ensure every word earns its place.'
    
    if any(char.isdigit() for char in content):
        score = min(100, score + 10)
        feedback += ' Good use of specific numbers!'
    
    is_complete = score >= 50
    
    cur.execute("""
        UPDATE pitch_deck_sections 
        SET content = %s, score = %s, feedback = %s, is_complete = %s
        WHERE section_id = %s
    """, (content, score, feedback, is_complete, section_id))
    
    conn.commit()
    cur.close()
    return_connection(conn)
    
    return {'success': True, 'score': score, 'feedback': feedback}


def start_pitch_session(player_id: int, deck_id: int, investor_id: int) -> dict:
    """Start a pitch session with an investor."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM investor_profiles WHERE investor_id = %s", (investor_id,))
    investor = cur.fetchone()
    if not investor:
        cur.close()
        return_connection(conn)
        return {'success': False, 'error': 'Investor not found'}
    
    investor = dict(investor)
    if investor.get('priorities'):
        investor['priorities'] = json.loads(investor['priorities']) if isinstance(investor['priorities'], str) else investor['priorities']
    
    questions = []
    priorities = investor.get('priorities', {})
    
    if priorities.get('team', 0) > 25:
        questions.append("Tell me about your team's background and why you're the right people to build this.")
    if priorities.get('traction', 0) > 25:
        questions.append("What traction do you have? Walk me through your key metrics.")
    if priorities.get('market', 0) > 25:
        questions.append("How did you arrive at your market size estimates? What's your path to capturing it?")
    if priorities.get('product', 0) > 20:
        questions.append("What's your competitive advantage? Why can't a bigger player just copy this?")
    
    questions.append("What's your biggest risk and how are you addressing it?")
    
    cur.execute("""
        INSERT INTO pitch_sessions (player_id, deck_id, investor_id, questions_asked)
        VALUES (%s, %s, %s, %s)
        RETURNING session_id
    """, (player_id, deck_id, investor_id, json.dumps(questions)))
    
    session_id = cur.fetchone()['session_id']
    conn.commit()
    cur.close()
    return_connection(conn)
    
    return {
        'success': True,
        'session_id': session_id,
        'investor': investor,
        'questions': questions
    }


def submit_pitch_answers(session_id: int, answers: list) -> dict:
    """Submit answers to investor questions and get outcome."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT ps.*, ip.priorities, ip.risk_tolerance, ip.investment_range_min, ip.investment_range_max,
               ppd.target_amount
        FROM pitch_sessions ps
        JOIN investor_profiles ip ON ps.investor_id = ip.investor_id
        JOIN player_pitch_decks ppd ON ps.deck_id = ppd.deck_id
        WHERE ps.session_id = %s
    """, (session_id,))
    session = cur.fetchone()
    
    if not session:
        cur.close()
        return_connection(conn)
        return {'success': False, 'error': 'Session not found'}
    
    session = dict(session)
    
    answer_quality = 0
    for answer in answers:
        words = len(answer.split()) if answer else 0
        if words > 50:
            answer_quality += 25
        elif words > 20:
            answer_quality += 15
        else:
            answer_quality += 5
    
    answer_quality = min(100, answer_quality)
    
    base_interest = 30 + (answer_quality // 2)
    investor_interest = min(100, base_interest)
    
    outcome = 'rejected'
    funding_offered = None
    equity_requested = None
    exp_earned = 50
    
    if investor_interest >= 70:
        outcome = 'term_sheet'
        target = float(session['target_amount'])
        funding_offered = min(target, float(session['investment_range_max']))
        equity_requested = (funding_offered / target) * 15
        exp_earned = 200
    elif investor_interest >= 50:
        outcome = 'follow_up'
        exp_earned = 100
    
    cur.execute("""
        UPDATE pitch_sessions 
        SET answers_given = %s, investor_interest = %s, 
            funding_offered = %s, equity_requested = %s, outcome = %s, exp_earned = %s
        WHERE session_id = %s
    """, (json.dumps(answers), investor_interest, funding_offered, equity_requested, outcome, exp_earned, session_id))
    
    conn.commit()
    cur.close()
    return_connection(conn)
    
    messages = {
        'rejected': "The investor passed on this opportunity. Keep refining your pitch!",
        'follow_up': "The investor wants to schedule a follow-up meeting. Good progress!",
        'term_sheet': f"Congratulations! You received a term sheet for ${funding_offered:,.0f} at {equity_requested:.1f}% equity!"
    }
    
    return {
        'success': True,
        'outcome': outcome,
        'message': messages[outcome],
        'investor_interest': investor_interest,
        'funding_offered': funding_offered,
        'equity_requested': equity_requested,
        'exp_earned': exp_earned
    }


# ============================================================================
# LEARNING ANALYTICS FUNCTIONS
# ============================================================================

def get_player_analytics(player_id):
    """Get comprehensive learning analytics for a player."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT marketing_exp, finance_exp, operations_exp, 
               human_resources_exp, legal_exp, strategy_exp,
               scenarios_completed, login_streak, total_playtime_minutes
        FROM player_profiles WHERE player_id = %s
    """, (player_id,))
    player = cur.fetchone()
    
    if not player:
        cur.close()
        return_connection(conn)
        return None
    
    disciplines = {
        'Marketing': {'exp': player['marketing_exp'], 'level': get_current_level(player['marketing_exp'])},
        'Finance': {'exp': player['finance_exp'], 'level': get_current_level(player['finance_exp'])},
        'Operations': {'exp': player['operations_exp'], 'level': get_current_level(player['operations_exp'])},
        'HR': {'exp': player['human_resources_exp'], 'level': get_current_level(player['human_resources_exp'])},
        'Legal': {'exp': player['legal_exp'], 'level': get_current_level(player['legal_exp'])},
        'Strategy': {'exp': player['strategy_exp'], 'level': get_current_level(player['strategy_exp'])}
    }
    
    total_exp = sum(d['exp'] for d in disciplines.values())
    avg_level = sum(d['level'] for d in disciplines.values()) / 6
    
    strengths = sorted(disciplines.items(), key=lambda x: x[1]['exp'], reverse=True)[:2]
    weaknesses = sorted(disciplines.items(), key=lambda x: x[1]['exp'])[:2]
    
    cur.execute("""
        SELECT discipline, min_level, title, description 
        FROM learning_recommendations 
        ORDER BY discipline, min_level
    """)
    all_recs = cur.fetchall()
    
    recommendations = []
    for disc_name, disc_data in weaknesses:
        disc_key = disc_name.lower()
        for rec in all_recs:
            if rec['discipline'] == disc_key and rec['min_level'] <= disc_data['level'] + 1:
                recommendations.append({
                    'discipline': disc_name,
                    'title': rec['title'],
                    'description': rec['description']
                })
                break
    
    cur.close()
    return_connection(conn)
    
    return {
        'disciplines': disciplines,
        'total_exp': total_exp,
        'avg_level': round(avg_level, 1),
        'scenarios_completed': player['scenarios_completed'],
        'login_streak': player['login_streak'],
        'playtime_hours': round(player['total_playtime_minutes'] / 60, 1),
        'strengths': [(s[0], s[1]['level']) for s in strengths],
        'weaknesses': [(w[0], w[1]['level']) for w in weaknesses],
        'recommendations': recommendations[:3]
    }


def get_player_skill_chart_data(player_id):
    """Get data formatted for radar chart visualization."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT marketing_exp, finance_exp, operations_exp, 
               human_resources_exp, legal_exp, strategy_exp
        FROM player_profiles WHERE player_id = %s
    """, (player_id,))
    player = cur.fetchone()
    
    cur.close()
    return_connection(conn)
    
    if not player:
        return None
    
    max_exp = max(
        player['marketing_exp'], player['finance_exp'], player['operations_exp'],
        player['human_resources_exp'], player['legal_exp'], player['strategy_exp'], 1000
    )
    
    return {
        'labels': ['Marketing', 'Finance', 'Operations', 'HR', 'Legal', 'Strategy'],
        'values': [
            round(player['marketing_exp'] / max_exp * 100),
            round(player['finance_exp'] / max_exp * 100),
            round(player['operations_exp'] / max_exp * 100),
            round(player['human_resources_exp'] / max_exp * 100),
            round(player['legal_exp'] / max_exp * 100),
            round(player['strategy_exp'] / max_exp * 100)
        ]
    }


# ============================================================================
# ACHIEVEMENT FUNCTIONS
# ============================================================================

def get_player_achievements(player_id):
    """Get all achievements and player progress."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT ea.*, pea.progress_count, pea.is_unlocked, pea.unlocked_at
        FROM educational_achievements ea
        LEFT JOIN player_educational_achievements pea 
            ON ea.achievement_id = pea.achievement_id AND pea.player_id = %s
        ORDER BY ea.tier, ea.achievement_name
    """, (player_id,))
    achievements = cur.fetchall()
    
    cur.close()
    return_connection(conn)
    
    result = []
    for ach in achievements:
        progress = ach['progress_count'] or 0
        result.append({
            'achievement_id': ach['achievement_id'],
            'name': ach['achievement_name'],
            'description': ach['description'],
            'category': ach['category'],
            'requirement': ach['requirement_count'],
            'progress': progress,
            'progress_pct': min(100, round(progress / ach['requirement_count'] * 100)),
            'exp_reward': ach['exp_reward'],
            'tier': ach['tier'],
            'is_unlocked': ach['is_unlocked'] or False,
            'unlocked_at': ach['unlocked_at']
        })
    
    return result


def update_achievement_progress(player_id, category, increment=1):
    """Update progress on achievements for a category."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT achievement_id, requirement_count, exp_reward
        FROM educational_achievements WHERE category = %s
    """, (category,))
    achievements = cur.fetchall()
    
    unlocked = []
    
    for ach in achievements:
        cur.execute("""
            INSERT INTO player_educational_achievements (player_id, achievement_id, progress_count)
            VALUES (%s, %s, %s)
            ON CONFLICT (player_id, achievement_id) 
            DO UPDATE SET progress_count = player_educational_achievements.progress_count + %s
            RETURNING progress_count, is_unlocked
        """, (player_id, ach['achievement_id'], increment, increment))
        result = cur.fetchone()
        
        if result and not result['is_unlocked'] and result['progress_count'] >= ach['requirement_count']:
            cur.execute("""
                UPDATE player_educational_achievements 
                SET is_unlocked = TRUE, unlocked_at = CURRENT_TIMESTAMP
                WHERE player_id = %s AND achievement_id = %s
            """, (player_id, ach['achievement_id']))
            unlocked.append({
                'achievement_id': ach['achievement_id'],
                'exp_reward': ach['exp_reward']
            })
    
    conn.commit()
    cur.close()
    return_connection(conn)
    
    return unlocked


# ============================================================================
# COMPETITION FUNCTIONS
# ============================================================================

def get_active_competitions():
    """Get all active competitions."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT ac.*, ct.competition_name, ct.description, ct.competition_type, 
               ct.duration_days, ct.exp_reward, ct.scoring_criteria
        FROM active_competitions ac
        JOIN competition_types ct ON ac.competition_id = ct.competition_id
        WHERE ac.status = 'active' AND ac.end_date > CURRENT_TIMESTAMP
        ORDER BY ac.end_date
    """)
    competitions = cur.fetchall()
    
    cur.close()
    return_connection(conn)
    
    return [dict(c) for c in competitions]


def get_competition_leaderboard(active_id, limit=10):
    """Get leaderboard for a competition."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT ce.*, pp.name
        FROM competition_entries ce
        JOIN player_profiles pp ON ce.player_id = pp.player_id
        WHERE ce.active_id = %s
        ORDER BY ce.score DESC
        LIMIT %s
    """, (active_id, limit))
    entries = cur.fetchall()
    
    cur.close()
    return_connection(conn)
    
    return [dict(e) for e in entries]


def join_competition(player_id, active_id):
    """Join a competition."""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO competition_entries (active_id, player_id)
            VALUES (%s, %s)
            ON CONFLICT (active_id, player_id) DO NOTHING
            RETURNING entry_id
        """, (active_id, player_id))
        result = cur.fetchone()
        conn.commit()
        cur.close()
        return_connection(conn)
        return {'success': True, 'joined': result is not None}
    except Exception as e:
        conn.rollback()
        cur.close()
        return_connection(conn)
        return {'success': False, 'error': str(e)}


def get_player_league(player_id):
    """Get player's current league status."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT SUM(marketing_exp + finance_exp + operations_exp + 
                   human_resources_exp + legal_exp + strategy_exp) as total_exp
        FROM player_profiles WHERE player_id = %s
    """, (player_id,))
    player = cur.fetchone()
    
    if not player:
        cur.close()
        return_connection(conn)
        return None
    
    total_exp = player['total_exp'] or 0
    
    cur.execute("""
        SELECT * FROM leagues 
        WHERE min_exp <= %s AND max_exp >= %s
        ORDER BY tier DESC LIMIT 1
    """, (total_exp, total_exp))
    league = cur.fetchone()
    
    cur.close()
    return_connection(conn)
    
    if league:
        return {
            'league_id': league['league_id'],
            'league_name': league['league_name'],
            'tier': league['tier'],
            'player_exp': total_exp,
            'next_tier_exp': league['max_exp'] + 1,
            'reward_multiplier': float(league['reward_multiplier'])
        }
    
    return None


# ============================================================================
# ADVANCED SIMULATION FUNCTIONS
# ============================================================================

def get_advanced_simulations(player_level=1):
    """Get available advanced simulations."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT * FROM advanced_simulations 
        WHERE difficulty <= %s + 2
        ORDER BY difficulty, simulation_name
    """, (player_level,))
    simulations = cur.fetchall()
    
    cur.close()
    return_connection(conn)
    
    return [dict(s) for s in simulations]


def get_simulation(simulation_id):
    """Get a specific simulation."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM advanced_simulations WHERE simulation_id = %s", (simulation_id,))
    sim = cur.fetchone()
    
    cur.close()
    return_connection(conn)
    
    if sim:
        result = dict(sim)
        if isinstance(result['scenario_data'], str):
            result['scenario_data'] = json.loads(result['scenario_data'])
        if isinstance(result['solution_guide'], str):
            result['solution_guide'] = json.loads(result['solution_guide'])
        return result
    return None


def start_simulation(player_id, simulation_id):
    """Start an advanced simulation."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO player_simulation_progress (player_id, simulation_id)
        VALUES (%s, %s)
        RETURNING id
    """, (player_id, simulation_id))
    result = cur.fetchone()
    
    conn.commit()
    cur.close()
    return_connection(conn)
    
    return {'success': True, 'progress_id': result['id']}


def submit_simulation_decision(progress_id, decision):
    """Submit a decision in a simulation."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT psp.*, asm.solution_guide, asm.exp_reward
        FROM player_simulation_progress psp
        JOIN advanced_simulations asm ON psp.simulation_id = asm.simulation_id
        WHERE psp.id = %s
    """, (progress_id,))
    progress = cur.fetchone()
    
    if not progress:
        cur.close()
        return_connection(conn)
        return {'success': False, 'error': 'Progress not found'}
    
    decisions = progress['decisions'] if progress['decisions'] else []
    if isinstance(decisions, str):
        decisions = json.loads(decisions)
    decisions.append(decision)
    
    new_step = progress['current_step'] + 1
    
    cur.execute("""
        UPDATE player_simulation_progress 
        SET current_step = %s, decisions = %s
        WHERE id = %s
    """, (new_step, json.dumps(decisions), progress_id))
    
    conn.commit()
    cur.close()
    return_connection(conn)
    
    return {'success': True, 'step': new_step}


def complete_simulation(progress_id, final_score):
    """Complete an advanced simulation."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        UPDATE player_simulation_progress 
        SET status = 'completed', outcome_score = %s, completed_at = CURRENT_TIMESTAMP
        WHERE id = %s
        RETURNING player_id, simulation_id
    """, (final_score, progress_id))
    result = cur.fetchone()
    
    if result:
        cur.execute("SELECT exp_reward FROM advanced_simulations WHERE simulation_id = %s", (result['simulation_id'],))
        sim = cur.fetchone()
        exp_earned = int(sim['exp_reward'] * (final_score / 100)) if sim else 0
    else:
        exp_earned = 0
    
    conn.commit()
    cur.close()
    return_connection(conn)
    
    return {'success': True, 'exp_earned': exp_earned}


# ============================================================================
# TUTORIAL FUNCTIONS
# ============================================================================

TUTORIAL_SECTIONS = [
    {'id': 'welcome', 'title': 'Welcome to Business Tycoon', 'order': 1},
    {'id': 'navigation', 'title': 'Navigating the Hub', 'order': 2},
    {'id': 'scenarios', 'title': 'Playing Scenarios', 'order': 3},
    {'id': 'disciplines', 'title': 'Understanding Disciplines', 'order': 4},
    {'id': 'challenges', 'title': 'Educational Challenges', 'order': 5},
    {'id': 'simulations', 'title': 'Advanced Simulations', 'order': 6}
]


def get_tutorial_progress(player_id):
    """Get player's tutorial progress."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT tutorial_section, is_completed FROM tutorial_progress
        WHERE player_id = %s
    """, (player_id,))
    completed = {row['tutorial_section']: row['is_completed'] for row in cur.fetchall()}
    
    cur.close()
    return_connection(conn)
    
    result = []
    for section in TUTORIAL_SECTIONS:
        result.append({
            **section,
            'is_completed': completed.get(section['id'], False)
        })
    
    return result


def complete_tutorial_section(player_id, section_id):
    """Mark a tutorial section as complete."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO tutorial_progress (player_id, tutorial_section, is_completed, completed_at)
        VALUES (%s, %s, TRUE, CURRENT_TIMESTAMP)
        ON CONFLICT (player_id, tutorial_section) 
        DO UPDATE SET is_completed = TRUE, completed_at = CURRENT_TIMESTAMP
    """, (player_id, section_id))
    
    conn.commit()
    cur.close()
    return_connection(conn)
    
    return {'success': True}


def get_onboarding_seen(player_id):
    """Check if player has seen the onboarding modal."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT onboarding_seen FROM player_profiles WHERE player_id = %s
    """, (player_id,))
    row = cur.fetchone()
    
    cur.close()
    return_connection(conn)
    
    return row.get('onboarding_seen', False) if row else False


def mark_onboarding_seen(player_id):
    """Mark player's onboarding as seen."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        UPDATE player_profiles SET onboarding_seen = TRUE WHERE player_id = %s
    """, (player_id,))
    
    conn.commit()
    cur.close()
    return_connection(conn)
    
    return {'success': True}


# ============================================================================
# MENTORSHIP SYSTEM - Learn before you play
# ============================================================================

def get_mentorship_module(module_id):
    """Get a mentorship module by ID."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT * FROM mentorship_modules WHERE module_id = %s AND is_active = TRUE
    """, (module_id,))
    row = cur.fetchone()
    
    cur.close()
    return_connection(conn)
    
    return dict(row) if row else None


def get_mentorship_for_scenario(scenario_id):
    """Get required mentorship module for a scenario."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT mm.* FROM mentorship_modules mm
        JOIN scenario_mentorship sm ON mm.module_id = sm.module_id
        WHERE sm.scenario_id = %s AND sm.is_required = TRUE AND mm.is_active = TRUE
        LIMIT 1
    """, (scenario_id,))
    row = cur.fetchone()
    
    cur.close()
    return_connection(conn)
    
    return dict(row) if row else None


def check_mentorship_completed(player_id, module_id):
    """Check if player has completed a mentorship module."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT is_completed FROM player_mentorship_progress 
        WHERE player_id = %s AND module_id = %s
    """, (player_id, module_id))
    row = cur.fetchone()
    
    cur.close()
    return_connection(conn)
    
    return row['is_completed'] if row else False


def check_scenario_mentorship_ready(player_id, scenario_id):
    """Check if player can play a scenario (has completed required mentorship)."""
    module = get_mentorship_for_scenario(scenario_id)
    if not module:
        return {'ready': True, 'module': None}
    
    completed = check_mentorship_completed(player_id, module['module_id'])
    return {
        'ready': completed,
        'module': module if not completed else None
    }


def start_mentorship(player_id, module_id):
    """Start a mentorship module for a player."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO player_mentorship_progress (player_id, module_id, started_at)
        VALUES (%s, %s, CURRENT_TIMESTAMP)
        ON CONFLICT (player_id, module_id) DO NOTHING
    """, (player_id, module_id))
    
    conn.commit()
    cur.close()
    return_connection(conn)
    
    return {'success': True}


def validate_practice_answer(module_id, user_answer):
    """Server-side validation of practice question answer.
    Returns dict with 'correct' boolean and 'feedback' message.
    """
    module = get_mentorship_module(module_id)
    if not module:
        return {'correct': False, 'feedback': 'Module not found', 'score': 0}
    
    practice_answer = module.get('practice_answer', '')
    if not practice_answer:
        return {'correct': True, 'feedback': 'No practice question for this lesson', 'score': 100}
    
    user_answer = (user_answer or '').strip().lower()
    correct_answer = practice_answer.strip().lower()
    
    is_correct = (user_answer == correct_answer or 
                  user_answer in correct_answer or 
                  correct_answer in user_answer)
    
    return {
        'correct': is_correct,
        'feedback': module.get('practice_explanation', ''),
        'expected': practice_answer,
        'score': 100 if is_correct else 50
    }


def complete_mentorship(player_id, module_id, practice_score=100):
    """Mark a mentorship module as complete."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO player_mentorship_progress (player_id, module_id, is_completed, completed_at, practice_score)
        VALUES (%s, %s, TRUE, CURRENT_TIMESTAMP, %s)
        ON CONFLICT (player_id, module_id) 
        DO UPDATE SET is_completed = TRUE, completed_at = CURRENT_TIMESTAMP, practice_score = %s
    """, (player_id, module_id, practice_score, practice_score))
    
    conn.commit()
    cur.close()
    return_connection(conn)
    
    return {'success': True}


def get_player_mentorship_progress(player_id):
    """Get all mentorship progress for a player."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT mm.*, pmp.is_completed, pmp.practice_score, pmp.completed_at
        FROM mentorship_modules mm
        LEFT JOIN player_mentorship_progress pmp ON mm.module_id = pmp.module_id AND pmp.player_id = %s
        WHERE mm.is_active = TRUE
        ORDER BY mm.discipline, mm.required_level
    """, (player_id,))
    
    modules = [dict(row) for row in cur.fetchall()]
    
    cur.close()
    return_connection(conn)
    
    return modules


def get_mentorship_by_discipline(discipline, player_id=None):
    """Get all mentorship modules for a discipline."""
    conn = get_connection()
    cur = conn.cursor()
    
    if player_id:
        cur.execute("""
            SELECT mm.*, pmp.is_completed, pmp.practice_score
            FROM mentorship_modules mm
            LEFT JOIN player_mentorship_progress pmp ON mm.module_id = pmp.module_id AND pmp.player_id = %s
            WHERE mm.discipline = %s AND mm.is_active = TRUE
            ORDER BY mm.required_level
        """, (player_id, discipline))
    else:
        cur.execute("""
            SELECT * FROM mentorship_modules 
            WHERE discipline = %s AND is_active = TRUE
            ORDER BY required_level
        """, (discipline,))
    
    modules = [dict(row) for row in cur.fetchall()]
    
    cur.close()
    return_connection(conn)
    
    return modules


# ============================================================================
# MENTOR TRIALS - RPG-THEMED KNOWLEDGE QUIZZES
# ============================================================================

def get_all_mentor_trials(player_id=None):
    """Get all mentor trials with player progress if provided."""
    conn = get_connection()
    cur = conn.cursor()
    
    if player_id:
        cur.execute("""
            SELECT mt.*, ptp.is_passed, ptp.best_score, ptp.attempts
            FROM mentor_trials mt
            LEFT JOIN player_trial_progress ptp ON mt.trial_id = ptp.trial_id AND ptp.player_id = %s
            WHERE mt.is_active = TRUE
            ORDER BY mt.discipline, mt.difficulty
        """, (player_id,))
    else:
        cur.execute("""
            SELECT * FROM mentor_trials WHERE is_active = TRUE
            ORDER BY discipline, difficulty
        """)
    
    trials = [dict(row) for row in cur.fetchall()]
    cur.close()
    return_connection(conn)
    return trials


def get_mentor_trial(trial_id):
    """Get a specific mentor trial with questions."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM mentor_trials WHERE trial_id = %s", (trial_id,))
    trial = cur.fetchone()
    
    if trial:
        trial = dict(trial)
        cur.execute("""
            SELECT * FROM trial_questions WHERE trial_id = %s ORDER BY question_order
        """, (trial_id,))
        trial['questions'] = [dict(row) for row in cur.fetchall()]
    
    cur.close()
    return_connection(conn)
    return trial


def start_mentor_trial(player_id, trial_id):
    """Start or restart a mentor trial."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO player_trial_progress (player_id, trial_id, attempts)
        VALUES (%s, %s, 1)
        ON CONFLICT (player_id, trial_id)
        DO UPDATE SET started_at = CURRENT_TIMESTAMP, attempts = player_trial_progress.attempts + 1
    """, (player_id, trial_id))
    
    conn.commit()
    cur.close()
    return_connection(conn)
    return {'success': True}


def complete_mentor_trial(player_id, trial_id, score, max_score, is_passed):
    """Complete a mentor trial and award rewards."""
    conn = get_connection()
    cur = conn.cursor()
    
    # Update progress
    cur.execute("""
        UPDATE player_trial_progress 
        SET completed_at = CURRENT_TIMESTAMP, score = %s, max_score = %s, is_passed = %s,
            best_score = GREATEST(COALESCE(best_score, 0), %s)
        WHERE player_id = %s AND trial_id = %s
    """, (score, max_score, is_passed, score, player_id, trial_id))
    
    rewards = {'exp': 0, 'gold': 0, 'badge': None}
    
    if is_passed:
        # Get trial rewards
        cur.execute("SELECT exp_reward, gold_reward, badge_code FROM mentor_trials WHERE trial_id = %s", (trial_id,))
        trial = cur.fetchone()
        if trial:
            rewards['exp'] = trial['exp_reward']
            rewards['gold'] = trial['gold_reward']
            
            # Add gold reward
            cur.execute("UPDATE player_profiles SET total_cash = total_cash + %s WHERE player_id = %s",
                       (trial['gold_reward'], player_id))
            
            # Award badge if exists
            if trial['badge_code']:
                cur.execute("SELECT badge_id FROM learning_badges WHERE badge_code = %s", (trial['badge_code'],))
                badge = cur.fetchone()
                if badge:
                    cur.execute("""
                        INSERT INTO player_learning_badges (player_id, badge_id)
                        VALUES (%s, %s)
                        ON CONFLICT (player_id, badge_id) DO NOTHING
                    """, (player_id, badge['badge_id']))
                    rewards['badge'] = trial['badge_code']
    
    conn.commit()
    cur.close()
    return_connection(conn)
    return rewards


def get_player_trial_progress(player_id):
    """Get all trial progress for a player."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT mt.*, ptp.is_passed, ptp.best_score, ptp.attempts, ptp.completed_at
        FROM mentor_trials mt
        LEFT JOIN player_trial_progress ptp ON mt.trial_id = ptp.trial_id AND ptp.player_id = %s
        WHERE mt.is_active = TRUE
        ORDER BY mt.discipline, mt.difficulty
    """, (player_id,))
    
    progress = [dict(row) for row in cur.fetchall()]
    cur.close()
    return_connection(conn)
    return progress


# ============================================================================
# MERCHANT PUZZLES - INTERACTIVE BUSINESS CALCULATORS
# ============================================================================

def get_all_merchant_puzzles(player_id=None):
    """Get all merchant puzzles with player progress if provided."""
    conn = get_connection()
    cur = conn.cursor()
    
    if player_id:
        cur.execute("""
            SELECT mp.*, ppp.is_solved, ppp.attempts, ppp.best_time_seconds
            FROM merchant_puzzles mp
            LEFT JOIN player_puzzle_progress ppp ON mp.puzzle_id = ppp.puzzle_id AND ppp.player_id = %s
            WHERE mp.is_active = TRUE
            ORDER BY mp.discipline, mp.difficulty
        """, (player_id,))
    else:
        cur.execute("""
            SELECT * FROM merchant_puzzles WHERE is_active = TRUE
            ORDER BY discipline, difficulty
        """)
    
    puzzles = [dict(row) for row in cur.fetchall()]
    cur.close()
    return_connection(conn)
    return puzzles


def get_merchant_puzzle(puzzle_id):
    """Get a specific merchant puzzle."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM merchant_puzzles WHERE puzzle_id = %s", (puzzle_id,))
    puzzle = cur.fetchone()
    
    if puzzle:
        puzzle = dict(puzzle)
        # Parse challenge_data JSON
        import json
        if puzzle.get('challenge_data'):
            puzzle['challenge_data'] = json.loads(puzzle['challenge_data']) if isinstance(puzzle['challenge_data'], str) else puzzle['challenge_data']
    
    cur.close()
    return_connection(conn)
    return puzzle


def start_merchant_puzzle(player_id, puzzle_id):
    """Start or restart a merchant puzzle."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO player_puzzle_progress (player_id, puzzle_id, attempts)
        VALUES (%s, %s, 1)
        ON CONFLICT (player_id, puzzle_id)
        DO UPDATE SET started_at = CURRENT_TIMESTAMP, attempts = player_puzzle_progress.attempts + 1
    """, (player_id, puzzle_id))
    
    conn.commit()
    cur.close()
    return_connection(conn)
    return {'success': True}


def complete_merchant_puzzle(player_id, puzzle_id, time_seconds, is_correct):
    """Complete a merchant puzzle and award rewards."""
    conn = get_connection()
    cur = conn.cursor()
    
    # Update progress
    cur.execute("""
        UPDATE player_puzzle_progress 
        SET completed_at = CURRENT_TIMESTAMP, is_solved = %s,
            best_time_seconds = CASE 
                WHEN best_time_seconds IS NULL OR %s < best_time_seconds THEN %s 
                ELSE best_time_seconds 
            END
        WHERE player_id = %s AND puzzle_id = %s
    """, (is_correct, time_seconds, time_seconds, player_id, puzzle_id))
    
    rewards = {'exp': 0, 'gold': 0}
    
    if is_correct:
        # Get puzzle rewards
        cur.execute("SELECT exp_reward, gold_reward FROM merchant_puzzles WHERE puzzle_id = %s", (puzzle_id,))
        puzzle = cur.fetchone()
        if puzzle:
            rewards['exp'] = puzzle['exp_reward']
            rewards['gold'] = puzzle['gold_reward']
            
            # Add gold reward
            cur.execute("UPDATE player_profiles SET total_cash = total_cash + %s WHERE player_id = %s",
                       (puzzle['gold_reward'], player_id))
    
    conn.commit()
    cur.close()
    return_connection(conn)
    return rewards


def get_player_puzzle_progress(player_id):
    """Get all puzzle progress for a player."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT mp.*, ppp.is_solved, ppp.attempts, ppp.best_time_seconds, ppp.completed_at
        FROM merchant_puzzles mp
        LEFT JOIN player_puzzle_progress ppp ON mp.puzzle_id = ppp.puzzle_id AND ppp.player_id = %s
        WHERE mp.is_active = TRUE
        ORDER BY mp.discipline, mp.difficulty
    """, (player_id,))
    
    progress = [dict(row) for row in cur.fetchall()]
    cur.close()
    return_connection(conn)
    return progress


# ============================================================================
# LEARNING BADGES
# ============================================================================

def get_player_learning_badges(player_id):
    """Get all learning badges earned by a player."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT lb.*, plb.earned_at
        FROM learning_badges lb
        JOIN player_learning_badges plb ON lb.badge_id = plb.badge_id
        WHERE plb.player_id = %s
        ORDER BY plb.earned_at DESC
    """, (player_id,))
    
    badges = [dict(row) for row in cur.fetchall()]
    cur.close()
    return_connection(conn)
    return badges


def get_all_learning_badges():
    """Get all available learning badges."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM learning_badges ORDER BY badge_tier, discipline")
    badges = [dict(row) for row in cur.fetchall()]
    cur.close()
    return_connection(conn)
    return badges


# ============================================================================
# PHASE 4: STORYLINE QUEST SYSTEM
# ============================================================================

def get_story_arcs(player_id, player_level=1):
    """Get available story arcs for a player."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT sa.*, psp.current_chapter, psp.status as player_status, psp.choices_made
        FROM story_arcs sa
        LEFT JOIN player_story_progress psp ON sa.arc_id = psp.arc_id AND psp.player_id = %s
        WHERE sa.is_active = TRUE AND sa.unlock_level <= %s
        ORDER BY sa.unlock_level
    """, (player_id, player_level))
    
    arcs = []
    for row in cur.fetchall():
        arcs.append({
            'arc_id': row['arc_id'],
            'arc_name': row['arc_name'],
            'description': row['arc_description'],
            'world_type': row['world_type'],
            'total_chapters': row['total_chapters'],
            'current_chapter': row['current_chapter'] or 0,
            'status': row['player_status'] or 'not_started',
            'exp_reward': row['exp_reward'],
            'progress_pct': int((row['current_chapter'] or 0) / row['total_chapters'] * 100) if row['total_chapters'] > 0 else 0
        })
    
    cur.close()
    return_connection(conn)
    return arcs


def get_story_chapter(arc_id, chapter_number):
    """Get a specific story chapter."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT sc.*, sa.arc_name FROM story_chapters sc
        JOIN story_arcs sa ON sc.arc_id = sa.arc_id
        WHERE sc.arc_id = %s AND sc.chapter_number = %s
    """, (arc_id, chapter_number))
    
    chapter = cur.fetchone()
    cur.close()
    return_connection(conn)
    
    if chapter:
        return {
            'chapter_id': chapter['chapter_id'],
            'arc_id': chapter['arc_id'],
            'arc_name': chapter['arc_name'],
            'chapter_number': chapter['chapter_number'],
            'title': chapter['chapter_title'],
            'narrative': chapter['chapter_narrative'],
            'choices': [
                {'id': 'a', 'text': chapter['choice_a_text'], 'next': chapter['choice_a_next_chapter']},
                {'id': 'b', 'text': chapter['choice_b_text'], 'next': chapter['choice_b_next_chapter']},
                {'id': 'c', 'text': chapter['choice_c_text'], 'next': chapter['choice_c_next_chapter']} if chapter['choice_c_text'] else None
            ],
            'outcomes': {
                'a': chapter['choice_a_outcome'],
                'b': chapter['choice_b_outcome'],
                'c': chapter['choice_c_outcome']
            },
            'exp_reward': chapter['exp_reward'],
            'is_finale': chapter['is_finale']
        }
    return None


def start_story_arc(player_id, arc_id):
    """Start a new story arc for a player."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO player_story_progress (player_id, arc_id, current_chapter, status)
        VALUES (%s, %s, 1, 'in_progress')
        ON CONFLICT (player_id, arc_id) DO NOTHING
        RETURNING id
    """, (player_id, arc_id))
    
    result = cur.fetchone()
    conn.commit()
    cur.close()
    return_connection(conn)
    
    return {'success': result is not None, 'started': result is not None}


def make_story_choice(player_id, arc_id, chapter_number, choice):
    """Process a player's choice in a story chapter."""
    conn = get_connection()
    cur = conn.cursor()
    
    chapter = get_story_chapter(arc_id, chapter_number)
    if not chapter:
        cur.close()
        return_connection(conn)
        return {'success': False, 'error': 'Chapter not found'}
    
    choice_idx = {'a': 0, 'b': 1, 'c': 2}.get(choice.lower(), 0)
    next_chapter = chapter['choices'][choice_idx]['next'] if chapter['choices'][choice_idx] else None
    outcome = chapter['outcomes'].get(choice.lower(), '')
    exp_earned = chapter['exp_reward']
    
    if chapter['is_finale']:
        cur.execute("""
            UPDATE player_story_progress 
            SET status = 'completed', completed_at = CURRENT_TIMESTAMP,
                choices_made = choices_made || %s::jsonb
            WHERE player_id = %s AND arc_id = %s
        """, (json.dumps([{'chapter': chapter_number, 'choice': choice}]), player_id, arc_id))
    else:
        cur.execute("""
            UPDATE player_story_progress 
            SET current_chapter = %s,
                choices_made = choices_made || %s::jsonb
            WHERE player_id = %s AND arc_id = %s
        """, (next_chapter or chapter_number + 1, json.dumps([{'chapter': chapter_number, 'choice': choice}]), player_id, arc_id))
    
    conn.commit()
    cur.close()
    return_connection(conn)
    
    return {
        'success': True,
        'outcome': outcome,
        'exp_earned': exp_earned,
        'is_finale': chapter['is_finale'],
        'next_chapter': next_chapter
    }


# ============================================================================
# PHASE 4: MENTORSHIP & ADVISOR PROGRESSION
# ============================================================================

def get_advisor_relationships(player_id):
    """Get player's relationships with all advisors."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT a.*, par.affinity_level, par.total_interactions, par.is_mentor, par.unlocked_skills
        FROM advisors a
        LEFT JOIN player_advisor_relationships par ON a.advisor_id = par.advisor_id AND par.player_id = %s
        ORDER BY a.advisor_name
    """, (player_id,))
    
    advisors = []
    for row in cur.fetchall():
        advisors.append({
            'advisor_id': row['advisor_id'],
            'name': row['advisor_name'],
            'specialty': row['discipline_specialty'] or 'Business',
            'affinity': row['affinity_level'] or 0,
            'interactions': row['total_interactions'] or 0,
            'is_mentor': row['is_mentor'] or False,
            'unlocked_skills': row['unlocked_skills'] or []
        })
    
    cur.close()
    return_connection(conn)
    return advisors


def get_advisor_skill_tree(advisor_id):
    """Get the skill tree for a specific advisor."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT * FROM advisor_skill_trees WHERE advisor_id = %s ORDER BY skill_tier, skill_id
    """, (advisor_id,))
    
    skills = []
    for row in cur.fetchall():
        skills.append({
            'skill_id': row['skill_id'],
            'name': row['skill_name'],
            'description': row['skill_description'],
            'tier': row['skill_tier'],
            'bonus_type': row['bonus_type'],
            'bonus_value': float(row['bonus_value']),
            'unlock_cost': row['unlock_cost']
        })
    
    cur.close()
    return_connection(conn)
    return skills


def get_mentorship_missions(player_id, advisor_id=None):
    """Get available mentorship missions."""
    conn = get_connection()
    cur = conn.cursor()
    
    if advisor_id:
        cur.execute("""
            SELECT mm.*, a.advisor_name, pmm.status as player_status
            FROM mentorship_missions mm
            JOIN advisors a ON mm.advisor_id = a.advisor_id
            LEFT JOIN player_mentor_missions pmm ON mm.mission_id = pmm.mission_id AND pmm.player_id = %s
            WHERE mm.advisor_id = %s
            ORDER BY mm.required_affinity
        """, (player_id, advisor_id))
    else:
        cur.execute("""
            SELECT mm.*, a.advisor_name, pmm.status as player_status
            FROM mentorship_missions mm
            JOIN advisors a ON mm.advisor_id = a.advisor_id
            LEFT JOIN player_mentor_missions pmm ON mm.mission_id = pmm.mission_id AND pmm.player_id = %s
            ORDER BY mm.required_affinity
        """, (player_id,))
    
    missions = []
    for row in cur.fetchall():
        missions.append({
            'mission_id': row['mission_id'],
            'advisor_id': row['advisor_id'],
            'advisor_name': row['advisor_name'],
            'name': row['mission_name'],
            'description': row['mission_description'],
            'required_affinity': row['required_affinity'],
            'mission_type': row['mission_type'],
            'exp_reward': row['exp_reward'],
            'status': row['player_status'] or 'available'
        })
    
    cur.close()
    return_connection(conn)
    return missions


def increase_advisor_affinity(player_id, advisor_id, amount=1):
    """Increase affinity with an advisor."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO player_advisor_relationships (player_id, advisor_id, affinity_level, total_interactions)
        VALUES (%s, %s, %s, 1)
        ON CONFLICT (player_id, advisor_id) 
        DO UPDATE SET affinity_level = player_advisor_relationships.affinity_level + %s,
                      total_interactions = player_advisor_relationships.total_interactions + 1
        RETURNING affinity_level
    """, (player_id, advisor_id, amount, amount))
    
    result = cur.fetchone()
    conn.commit()
    cur.close()
    return_connection(conn)
    
    return {'success': True, 'new_affinity': result['affinity_level'] if result else amount}


# ============================================================================
# PHASE 4: BUSINESS NETWORK & PARTNERSHIPS
# ============================================================================

def get_business_partners(player_id, player_reputation=50):
    """Get available business partners."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT bp.*, pp.partnership_level, pp.trust_score, pp.joint_ventures_completed
        FROM business_partners bp
        LEFT JOIN player_partnerships pp ON bp.partner_id = pp.partner_id AND pp.player_id = %s
        WHERE bp.reputation_required <= %s
        ORDER BY bp.reputation_required
    """, (player_id, player_reputation))
    
    partners = []
    for row in cur.fetchall():
        partners.append({
            'partner_id': row['partner_id'],
            'name': row['partner_name'],
            'type': row['partner_type'],
            'industry': row['industry'],
            'description': row['description'],
            'reputation_required': row['reputation_required'],
            'partnership_level': row['partnership_level'] or 0,
            'trust_score': row['trust_score'] or 0,
            'ventures_completed': row['joint_ventures_completed'] or 0,
            'is_partner': row['partnership_level'] is not None
        })
    
    cur.close()
    return_connection(conn)
    return partners


def get_joint_ventures(player_id, partner_id=None):
    """Get available joint ventures."""
    conn = get_connection()
    cur = conn.cursor()
    
    if partner_id:
        cur.execute("""
            SELECT jv.*, bp.partner_name, pjv.status as player_status
            FROM joint_ventures jv
            JOIN business_partners bp ON jv.partner_id = bp.partner_id
            LEFT JOIN player_joint_ventures pjv ON jv.venture_id = pjv.venture_id AND pjv.player_id = %s
            WHERE jv.partner_id = %s
        """, (player_id, partner_id))
    else:
        cur.execute("""
            SELECT jv.*, bp.partner_name, pjv.status as player_status
            FROM joint_ventures jv
            JOIN business_partners bp ON jv.partner_id = bp.partner_id
            LEFT JOIN player_joint_ventures pjv ON jv.venture_id = pjv.venture_id AND pjv.player_id = %s
        """, (player_id,))
    
    ventures = []
    for row in cur.fetchall():
        ventures.append({
            'venture_id': row['venture_id'],
            'name': row['venture_name'],
            'description': row['venture_description'],
            'partner_name': row['partner_name'],
            'investment': float(row['investment_required']),
            'duration_weeks': row['duration_weeks'],
            'risk_level': row['risk_level'],
            'potential_return': float(row['potential_return']),
            'exp_reward': row['exp_reward'],
            'status': row['player_status'] or 'available'
        })
    
    cur.close()
    return_connection(conn)
    return ventures


def get_networking_events(player_reputation=50):
    """Get available networking events."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT * FROM networking_events 
        WHERE reputation_required <= %s
        ORDER BY reputation_required
    """, (player_reputation,))
    
    events = []
    for row in cur.fetchall():
        events.append({
            'event_id': row['event_id'],
            'name': row['event_name'],
            'type': row['event_type'],
            'description': row['description'],
            'entry_cost': float(row['entry_cost']),
            'reputation_required': row['reputation_required'],
            'contacts_gained': row['contacts_gained'],
            'exp_reward': row['exp_reward']
        })
    
    cur.close()
    return_connection(conn)
    return events


def attend_networking_event(player_id, event_id):
    """Attend a networking event and gain contacts."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM networking_events WHERE event_id = %s", (event_id,))
    event = cur.fetchone()
    
    if not event:
        cur.close()
        return_connection(conn)
        return {'success': False, 'error': 'Event not found'}
    
    contact_names = ['Alex Chen', 'Jordan Smith', 'Morgan Lee', 'Taylor Davis', 'Casey Brown', 'Riley Johnson']
    contact_types = ['investor', 'supplier', 'mentor', 'peer', 'expert']
    
    import random
    for _ in range(event['contacts_gained']):
        cur.execute("""
            INSERT INTO player_network (player_id, contact_name, contact_type, industry, relationship_strength, met_at_event)
            VALUES (%s, %s, %s, %s, 1, %s)
        """, (player_id, random.choice(contact_names), random.choice(contact_types), 'General', event_id))
    
    conn.commit()
    cur.close()
    return_connection(conn)
    
    return {
        'success': True,
        'contacts_gained': event['contacts_gained'],
        'exp_earned': event['exp_reward']
    }


def get_player_network(player_id):
    """Get player's business network contacts."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT pn.*, ne.event_name FROM player_network pn
        LEFT JOIN networking_events ne ON pn.met_at_event = ne.event_id
        WHERE pn.player_id = %s
        ORDER BY pn.added_at DESC
    """, (player_id,))
    
    contacts = []
    for row in cur.fetchall():
        contacts.append({
            'name': row['contact_name'],
            'type': row['contact_type'],
            'industry': row['industry'],
            'relationship': row['relationship_strength'],
            'met_at': row['event_name'] or 'Direct Contact',
            'referrals': row['referrals_given']
        })
    
    cur.close()
    return_connection(conn)
    return contacts


# ============================================================================
# PHASE 4: INDUSTRY SPECIALIZATION TRACKS
# ============================================================================

def get_industry_tracks(player_id):
    """Get all industry tracks with player progress."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT it.*, pip.current_level, pip.current_exp, pip.certifications_earned
        FROM industry_tracks it
        LEFT JOIN player_industry_progress pip ON it.track_id = pip.track_id AND pip.player_id = %s
        ORDER BY it.track_name
    """, (player_id,))
    
    tracks = []
    for row in cur.fetchall():
        tracks.append({
            'track_id': row['track_id'],
            'name': row['track_name'],
            'industry': row['industry'],
            'description': row['description'],
            'total_levels': row['total_levels'],
            'current_level': row['current_level'] or 0,
            'current_exp': row['current_exp'] or 0,
            'exp_to_next': row['base_exp_required'] * ((row['current_level'] or 0) + 1),
            'certifications': row['certifications_earned'] or []
        })
    
    cur.close()
    return_connection(conn)
    return tracks


def get_industry_certifications(track_id, player_level=0):
    """Get certifications for a track."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT * FROM industry_certifications 
        WHERE track_id = %s AND required_level <= %s
        ORDER BY required_level
    """, (track_id, player_level + 2))
    
    certs = []
    for row in cur.fetchall():
        certs.append({
            'cert_id': row['cert_id'],
            'name': row['cert_name'],
            'description': row['cert_description'],
            'required_level': row['required_level'],
            'passing_score': row['passing_score'],
            'exp_reward': row['exp_reward'],
            'is_unlocked': player_level >= row['required_level']
        })
    
    cur.close()
    return_connection(conn)
    return certs


def get_industry_challenges(track_id, player_level=0):
    """Get challenges for an industry track."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT * FROM industry_challenges
        WHERE track_id = %s AND required_level <= %s
        ORDER BY required_level
    """, (track_id, player_level + 1))
    
    challenges = []
    for row in cur.fetchall():
        challenges.append({
            'challenge_id': row['challenge_id'],
            'name': row['challenge_name'],
            'description': row['challenge_description'],
            'required_level': row['required_level'],
            'exp_reward': row['exp_reward']
        })
    
    cur.close()
    return_connection(conn)
    return challenges


# ============================================================================
# PHASE 4: DYNAMIC MARKET EVENTS
# ============================================================================

def get_active_market_events():
    """Get currently active market events."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT me.*, ame.start_time, ame.end_time, ame.current_phase, ame.status
        FROM active_market_events ame
        JOIN market_events me ON ame.event_id = me.event_id
        WHERE ame.status = 'active'
        ORDER BY ame.start_time DESC
    """)
    
    events = []
    for row in cur.fetchall():
        events.append({
            'event_id': row['event_id'],
            'name': row['event_name'],
            'type': row['event_type'],
            'description': row['description'],
            'modifier': float(row['market_modifier']),
            'is_global': row['is_global'],
            'phase': row['current_phase'],
            'status': row['status']
        })
    
    cur.close()
    return_connection(conn)
    return events


def get_current_market_cycle():
    """Get the current market cycle."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM market_cycles ORDER BY cycle_id LIMIT 1")
    cycle = cur.fetchone()
    
    cur.close()
    return_connection(conn)
    
    if cycle:
        return {
            'name': cycle['cycle_name'],
            'type': cycle['cycle_type'],
            'description': cycle['description'],
            'revenue_modifier': float(cycle['revenue_modifier']),
            'cost_modifier': float(cycle['cost_modifier']),
            'opportunity_modifier': float(cycle['opportunity_modifier'])
        }
    return None


def get_global_challenges():
    """Get active global challenges."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT * FROM global_challenges 
        WHERE status IN ('active', 'pending')
        ORDER BY start_time
    """)
    
    challenges = []
    for row in cur.fetchall():
        challenges.append({
            'challenge_id': row['challenge_id'],
            'name': row['challenge_name'],
            'description': row['challenge_description'],
            'target': row['target_value'],
            'progress': row['current_progress'],
            'participants': row['participants'],
            'reward_pool': row['reward_pool'],
            'progress_pct': int(row['current_progress'] / row['target_value'] * 100) if row['target_value'] > 0 else 0,
            'status': row['status']
        })
    
    cur.close()
    return_connection(conn)
    return challenges


def contribute_to_global_challenge(player_id, challenge_id, amount):
    """Contribute to a global challenge."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO player_global_contributions (player_id, challenge_id, contribution)
        VALUES (%s, %s, %s)
        ON CONFLICT (player_id, challenge_id) 
        DO UPDATE SET contribution = player_global_contributions.contribution + %s
    """, (player_id, challenge_id, amount, amount))
    
    cur.execute("""
        UPDATE global_challenges 
        SET current_progress = current_progress + %s,
            participants = (SELECT COUNT(DISTINCT player_id) FROM player_global_contributions WHERE challenge_id = %s)
        WHERE challenge_id = %s
    """, (amount, challenge_id, challenge_id))
    
    conn.commit()
    cur.close()
    return_connection(conn)
    
    return {'success': True}


def get_breaking_news():
    """Get recent breaking news."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT * FROM breaking_news 
        ORDER BY created_at DESC
        LIMIT 5
    """)
    
    news = []
    for row in cur.fetchall():
        news.append({
            'news_id': row['news_id'],
            'headline': row['headline'],
            'content': row['news_content'],
            'type': row['news_type'],
            'discipline': row['affected_discipline'],
            'exp_reward': row['exp_reward']
        })
    
    cur.close()
    return_connection(conn)
    return news


def respond_to_news(player_id, news_id, response):
    """Respond to a breaking news event."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM breaking_news WHERE news_id = %s", (news_id,))
    news = cur.fetchone()
    
    if not news:
        cur.close()
        return_connection(conn)
        return {'success': False, 'error': 'News not found'}
    
    quality = 70 if response == 'optimal' else 50
    exp_earned = int(news['exp_reward'] * (quality / 100))
    
    cur.execute("""
        INSERT INTO player_news_responses (player_id, news_id, response_choice, response_quality, exp_earned)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (player_id, news_id) DO NOTHING
    """, (player_id, news_id, response, quality, exp_earned))
    
    conn.commit()
    cur.close()
    return_connection(conn)
    
    return {'success': True, 'exp_earned': exp_earned}


# ============================================================================
# PHASE 5A: MULTIPLAYER & SOCIAL FEATURES
# ============================================================================

def get_guilds(player_id=None):
    """Get available guilds."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT g.*, 
               (SELECT COUNT(*) FROM guild_members WHERE guild_id = g.guild_id) as member_count,
               (SELECT member_role FROM guild_members WHERE guild_id = g.guild_id AND player_id = %s) as player_role
        FROM guilds g
        WHERE g.is_public = TRUE
        ORDER BY g.guild_level DESC, g.guild_exp DESC
    """, (player_id,))
    
    guilds = []
    for row in cur.fetchall():
        guilds.append({
            'guild_id': row['guild_id'],
            'name': row['guild_name'],
            'tag': row['guild_tag'],
            'description': row['guild_description'],
            'level': row['guild_level'],
            'exp': row['guild_exp'],
            'member_count': row['member_count'],
            'max_members': row['max_members'],
            'player_role': row['player_role']
        })
    
    cur.close()
    return_connection(conn)
    return guilds


def get_player_guild(player_id):
    """Get the guild the player belongs to."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT g.*, gm.member_role, gm.contribution_exp, gm.contribution_gold
        FROM guild_members gm
        JOIN guilds g ON gm.guild_id = g.guild_id
        WHERE gm.player_id = %s
    """, (player_id,))
    
    result = cur.fetchone()
    cur.close()
    return_connection(conn)
    
    if result:
        return {
            'guild_id': result['guild_id'],
            'name': result['guild_name'],
            'tag': result['guild_tag'],
            'level': result['guild_level'],
            'role': result['member_role'],
            'contribution_exp': result['contribution_exp'],
            'contribution_gold': result['contribution_gold']
        }
    return None


def create_guild(player_id, guild_name, guild_tag, description=""):
    """Create a new guild."""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO guilds (guild_name, guild_tag, guild_description, leader_id)
            VALUES (%s, %s, %s, %s) RETURNING guild_id
        """, (guild_name, guild_tag, description, player_id))
        guild_id = cur.fetchone()['guild_id']
        
        cur.execute("""
            INSERT INTO guild_members (guild_id, player_id, member_role)
            VALUES (%s, %s, 'leader')
        """, (guild_id, player_id))
        
        conn.commit()
        cur.close()
        return_connection(conn)
        return {'success': True, 'guild_id': guild_id}
    except Exception as e:
        conn.rollback()
        cur.close()
        return_connection(conn)
        return {'success': False, 'error': str(e)}


def join_guild(player_id, guild_id):
    """Join an existing guild."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as cnt FROM guild_members WHERE player_id = %s", (player_id,))
    if cur.fetchone()['cnt'] > 0:
        cur.close()
        return_connection(conn)
        return {'success': False, 'error': 'Already in a guild'}
    
    try:
        cur.execute("""
            INSERT INTO guild_members (guild_id, player_id, member_role)
            VALUES (%s, %s, 'member')
        """, (guild_id, player_id))
        conn.commit()
        cur.close()
        return_connection(conn)
        return {'success': True}
    except:
        conn.rollback()
        cur.close()
        return_connection(conn)
        return {'success': False, 'error': 'Could not join guild'}


def get_coop_challenges():
    """Get available co-op challenges."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM coop_challenges WHERE is_active = TRUE ORDER BY difficulty")
    
    challenges = []
    for row in cur.fetchall():
        challenges.append({
            'challenge_id': row['challenge_id'],
            'name': row['challenge_name'],
            'description': row['challenge_description'],
            'type': row['challenge_type'],
            'min_players': row['min_players'],
            'max_players': row['max_players'],
            'difficulty': row['difficulty'],
            'exp_reward': row['exp_reward'],
            'time_limit': row['time_limit_minutes']
        })
    
    cur.close()
    return_connection(conn)
    return challenges


def get_trade_listings(player_id=None):
    """Get active trade listings."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT tl.*, pp.player_name as seller_name
        FROM trade_listings tl
        JOIN player_profiles pp ON tl.seller_id = pp.player_id
        WHERE tl.status = 'active'
        ORDER BY tl.created_at DESC
        LIMIT 50
    """)
    
    listings = []
    for row in cur.fetchall():
        listings.append({
            'listing_id': row['listing_id'],
            'seller_name': row['seller_name'],
            'item_type': row['item_type'],
            'item_name': row['item_name'],
            'price': row['asking_price'],
            'quantity': row['quantity'],
            'is_own': row['seller_id'] == player_id
        })
    
    cur.close()
    return_connection(conn)
    return listings


def leave_guild(player_id):
    """Leave current guild."""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT guild_id, member_role FROM guild_members WHERE player_id = %s", (player_id,))
        membership = cur.fetchone()
        
        if not membership:
            return {'success': False, 'error': 'You are not in a guild'}
        
        if membership['member_role'] == 'master':
            cur.execute("SELECT COUNT(*) as cnt FROM guild_members WHERE guild_id = %s", (membership['guild_id'],))
            member_count = cur.fetchone()['cnt']
            if member_count > 1:
                return {'success': False, 'error': 'Transfer leadership before leaving'}
        
        cur.execute("DELETE FROM guild_members WHERE player_id = %s", (player_id,))
        conn.commit()
        return {'success': True}
    except Exception:
        conn.rollback()
        return {'success': False, 'error': 'Could not leave guild'}
    finally:
        cur.close()
        return_connection(conn)


def join_coop_challenge(player_id, challenge_id):
    """Join a co-op challenge."""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT * FROM coop_challenges WHERE challenge_id = %s AND is_active = TRUE", (challenge_id,))
        challenge = cur.fetchone()
        
        if not challenge:
            cur.close()
            return_connection(conn)
            return {'success': False, 'error': 'Challenge not found or inactive'}
        
        cur.execute("""
            INSERT INTO coop_participants (challenge_id, player_id, status)
            VALUES (%s, %s, 'waiting')
            ON CONFLICT (challenge_id, player_id) DO NOTHING
        """, (challenge_id, player_id))
        conn.commit()
        cur.close()
        return_connection(conn)
        return {'success': True}
    except:
        conn.rollback()
        cur.close()
        return_connection(conn)
        return {'success': False, 'error': 'Could not join challenge'}


def get_player_inventory(player_id):
    """Get player's inventory for trading."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT pi.*, i.item_name, i.item_type
        FROM player_items pi
        JOIN items i ON pi.item_id = i.item_id
        WHERE pi.player_id = %s
    """, (player_id,))
    
    items = []
    for row in cur.fetchall():
        items.append({
            'item_id': row['item_id'],
            'name': row['item_name'],
            'type': row['item_type'],
            'quantity': row.get('quantity', 1)
        })
    
    cur.close()
    return_connection(conn)
    return items


def create_trade_listing(player_id, item_id, price):
    """Create a trade listing with row locking and atomic operations."""
    if price <= 0 or price > 10000000:
        return {'success': False, 'error': 'Invalid price'}
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT pi.*, i.item_name, i.item_type FROM player_items pi
            JOIN items i ON pi.item_id = i.item_id
            WHERE pi.player_id = %s AND pi.item_id = %s
            FOR UPDATE
        """, (player_id, item_id))
        item = cur.fetchone()
        
        if not item:
            conn.rollback()
            return {'success': False, 'error': 'Item not in inventory'}
        
        cur.execute("""
            INSERT INTO trade_listings (seller_id, item_type, item_id, item_name, asking_price, quantity, status)
            VALUES (%s, %s, %s, %s, %s, 1, 'active')
        """, (player_id, item['item_type'], item_id, item['item_name'], price))
        
        cur.execute("DELETE FROM player_items WHERE player_id = %s AND item_id = %s", (player_id, item_id))
        
        conn.commit()
        return {'success': True}
    except Exception:
        conn.rollback()
        return {'success': False, 'error': 'Could not create listing'}
    finally:
        cur.close()
        return_connection(conn)


def buy_trade_item(player_id, listing_id):
    """Buy an item from the trading post with row locking and atomic operations."""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT * FROM trade_listings WHERE listing_id = %s AND status = 'active' FOR UPDATE", (listing_id,))
        listing = cur.fetchone()
        
        if not listing:
            conn.rollback()
            return {'success': False, 'error': 'Listing not found or already sold'}
        
        if listing['seller_id'] == player_id:
            conn.rollback()
            return {'success': False, 'error': 'Cannot buy your own listing'}
        
        cur.execute("SELECT gold FROM player_profiles WHERE player_id = %s FOR UPDATE", (player_id,))
        buyer = cur.fetchone()
        
        if not buyer or buyer['gold'] < listing['asking_price']:
            conn.rollback()
            return {'success': False, 'error': 'Not enough gold'}
        
        cur.execute("UPDATE trade_listings SET status = 'sold', buyer_id = %s WHERE listing_id = %s",
                   (player_id, listing_id))
        
        cur.execute("UPDATE player_profiles SET gold = gold - %s WHERE player_id = %s", 
                   (listing['asking_price'], player_id))
        cur.execute("UPDATE player_profiles SET gold = gold + %s WHERE player_id = %s", 
                   (listing['asking_price'], listing['seller_id']))
        
        cur.execute("""
            INSERT INTO player_items (player_id, item_id, equipped)
            VALUES (%s, %s, FALSE)
        """, (player_id, listing['item_id']))
        
        conn.commit()
        return {'success': True, 'price': listing['asking_price']}
    except Exception:
        conn.rollback()
        return {'success': False, 'error': 'Transaction failed'}
    finally:
        cur.close()
        return_connection(conn)


def cancel_trade_listing(player_id, listing_id):
    """Cancel a trade listing with row locking and atomic operations."""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT * FROM trade_listings WHERE listing_id = %s AND seller_id = %s AND status = 'active' FOR UPDATE",
                   (listing_id, player_id))
        listing = cur.fetchone()
        
        if not listing:
            conn.rollback()
            return {'success': False, 'error': 'Listing not found or not yours'}
        
        cur.execute("""
            INSERT INTO player_items (player_id, item_id, equipped)
            VALUES (%s, %s, FALSE)
        """, (player_id, listing['item_id']))
        
        cur.execute("UPDATE trade_listings SET status = 'cancelled' WHERE listing_id = %s", (listing_id,))
        
        conn.commit()
        return {'success': True}
    except Exception:
        conn.rollback()
        return {'success': False, 'error': 'Could not cancel listing'}
    finally:
        cur.close()
        return_connection(conn)


def claim_battle_pass_tier(player_id, tier):
    """Claim a battle pass tier reward."""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT pbp.*, bp.free_rewards, bp.premium_rewards
            FROM player_battle_pass pbp
            JOIN battle_passes bp ON pbp.pass_id = bp.pass_id
            WHERE pbp.player_id = %s
        """, (player_id,))
        progress = cur.fetchone()
        
        if not progress:
            cur.close()
            return_connection(conn)
            return {'success': False, 'error': 'No battle pass found'}
        
        if tier > progress['current_tier']:
            cur.close()
            return_connection(conn)
            return {'success': False, 'error': 'Tier not reached yet'}
        
        claimed = progress['claimed_tiers'] or []
        if tier in claimed:
            cur.close()
            return_connection(conn)
            return {'success': False, 'error': 'Already claimed'}
        
        claimed.append(tier)
        cur.execute("UPDATE player_battle_pass SET claimed_tiers = %s WHERE player_id = %s",
                   (claimed, player_id))
        
        import json
        rewards = json.loads(progress['free_rewards']) if progress['free_rewards'] else {}
        reward_name = rewards.get(str(tier), 'Mystery Reward')
        
        conn.commit()
        cur.close()
        return_connection(conn)
        return {'success': True, 'reward': reward_name}
    except:
        conn.rollback()
        cur.close()
        return_connection(conn)
        return {'success': False, 'error': 'Could not claim reward'}


def attack_limited_boss(player_id, boss_id):
    """Attack a limited-time boss."""
    import random
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT * FROM limited_bosses WHERE boss_id = %s AND is_active = TRUE", (boss_id,))
        boss = cur.fetchone()
        
        if not boss:
            cur.close()
            return_connection(conn)
            return {'success': False, 'error': 'Boss not found or inactive'}
        
        if boss['current_hp'] <= 0:
            cur.close()
            return_connection(conn)
            return {'success': False, 'error': 'Boss already defeated'}
        
        damage = random.randint(500, 2000)
        new_hp = max(0, boss['current_hp'] - damage)
        boss_defeated = new_hp <= 0
        
        cur.execute("UPDATE limited_bosses SET current_hp = %s WHERE boss_id = %s", (new_hp, boss_id))
        
        exp_earned = 50 + (damage // 100)
        if boss_defeated:
            exp_earned += boss['exp_reward']
        
        cur.execute("UPDATE player_profiles SET total_exp = total_exp + %s WHERE player_id = %s",
                   (exp_earned, player_id))
        
        cur.execute("""
            INSERT INTO boss_participants (boss_id, player_id, damage_dealt)
            VALUES (%s, %s, %s)
            ON CONFLICT (boss_id, player_id) DO UPDATE SET damage_dealt = boss_participants.damage_dealt + %s
        """, (boss_id, player_id, damage, damage))
        
        conn.commit()
        cur.close()
        return_connection(conn)
        return {'success': True, 'damage': damage, 'exp_earned': exp_earned, 'boss_defeated': boss_defeated}
    except:
        conn.rollback()
        cur.close()
        return_connection(conn)
        return {'success': False, 'error': 'Attack failed'}


# ============================================================================
# PHASE 5B: SEASONAL CONTENT & LIVE EVENTS
# ============================================================================

def get_current_season():
    """Get the current active season."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM seasons WHERE is_active = TRUE LIMIT 1")
    season = cur.fetchone()
    
    if not season:
        cur.close()
        return_connection(conn)
        return None
    
    cur.execute("SELECT * FROM battle_passes WHERE season_id = %s", (season['season_id'],))
    battle_pass = cur.fetchone()
    
    cur.close()
    return_connection(conn)
    
    return {
        'season_id': season['season_id'],
        'name': season['season_name'],
        'theme': season['season_theme'],
        'description': season['description'],
        'end_date': season['end_date'],
        'battle_pass': {
            'pass_id': battle_pass['pass_id'],
            'name': battle_pass['pass_name'],
            'max_tier': battle_pass['max_tier']
        } if battle_pass else None
    }


def get_player_battle_pass(player_id):
    """Get player's battle pass progress."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT pbp.*, bp.pass_name, bp.max_tier, bp.free_rewards, bp.premium_rewards
        FROM player_battle_pass pbp
        JOIN battle_passes bp ON pbp.pass_id = bp.pass_id
        JOIN seasons s ON bp.season_id = s.season_id
        WHERE pbp.player_id = %s AND s.is_active = TRUE
    """, (player_id,))
    
    result = cur.fetchone()
    cur.close()
    return_connection(conn)
    
    if result:
        return {
            'pass_id': result['pass_id'],
            'name': result['pass_name'],
            'current_tier': result['current_tier'],
            'current_exp': result['current_exp'],
            'max_tier': result['max_tier'],
            'is_premium': result['is_premium'],
            'rewards_claimed': result['rewards_claimed']
        }
    return None


def get_seasonal_events():
    """Get active seasonal events."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT * FROM seasonal_events 
        WHERE is_active = TRUE OR (start_time <= CURRENT_TIMESTAMP AND end_time >= CURRENT_TIMESTAMP)
        ORDER BY start_time
    """)
    
    events = []
    for row in cur.fetchall():
        events.append({
            'event_id': row['event_id'],
            'name': row['event_name'],
            'type': row['event_type'],
            'theme': row['event_theme'],
            'description': row['description'],
            'bonus_multiplier': float(row['bonus_multiplier']),
            'end_time': row['end_time']
        })
    
    cur.close()
    return_connection(conn)
    return events


def get_limited_bosses():
    """Get available limited-time bosses."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT * FROM limited_time_bosses 
        WHERE available_from <= CURRENT_TIMESTAMP AND available_until >= CURRENT_TIMESTAMP
        AND is_defeated = FALSE
        ORDER BY difficulty
    """)
    
    bosses = []
    for row in cur.fetchall():
        bosses.append({
            'boss_id': row['boss_id'],
            'name': row['boss_name'],
            'title': row['boss_title'],
            'description': row['description'],
            'difficulty': row['difficulty'],
            'hp': row['current_hp'],
            'max_hp': row['health_points'],
            'exp_reward': row['exp_reward'],
            'available_until': row['available_until']
        })
    
    cur.close()
    return_connection(conn)
    return bosses


# ============================================================================
# PHASE 5C: AI-POWERED PERSONALIZATION
# ============================================================================

def get_learning_profile(player_id):
    """Get or create player's learning profile."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM player_learning_profiles WHERE player_id = %s", (player_id,))
    profile = cur.fetchone()
    
    if not profile:
        cur.execute("""
            INSERT INTO player_learning_profiles (player_id)
            VALUES (%s) RETURNING *
        """, (player_id,))
        profile = cur.fetchone()
        conn.commit()
    
    cur.close()
    return_connection(conn)
    
    return {
        'learning_style': profile['learning_style'],
        'difficulty': float(profile['preferred_difficulty']),
        'weak_areas': profile['weak_areas'] or [],
        'strong_areas': profile['strong_areas'] or [],
        'recommended_path': profile['recommended_path']
    }


def get_adaptive_difficulty(player_id, discipline):
    """Get adaptive difficulty for a discipline."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT * FROM adaptive_difficulty 
        WHERE player_id = %s AND discipline = %s
    """, (player_id, discipline))
    
    result = cur.fetchone()
    cur.close()
    return_connection(conn)
    
    if result:
        return float(result['current_difficulty'])
    return 1.0


def update_adaptive_difficulty(player_id, discipline, success):
    """Update adaptive difficulty based on performance."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO adaptive_difficulty (player_id, discipline, current_difficulty, success_streak, failure_streak, total_attempts)
        VALUES (%s, %s, 1.0, %s, %s, 1)
        ON CONFLICT (player_id, discipline) DO UPDATE SET
            success_streak = CASE WHEN %s THEN adaptive_difficulty.success_streak + 1 ELSE 0 END,
            failure_streak = CASE WHEN %s THEN 0 ELSE adaptive_difficulty.failure_streak + 1 END,
            total_attempts = adaptive_difficulty.total_attempts + 1,
            current_difficulty = CASE 
                WHEN %s AND adaptive_difficulty.success_streak >= 2 THEN LEAST(adaptive_difficulty.current_difficulty * 1.1, 2.0)
                WHEN NOT %s AND adaptive_difficulty.failure_streak >= 2 THEN GREATEST(adaptive_difficulty.current_difficulty * 0.9, 0.5)
                ELSE adaptive_difficulty.current_difficulty
            END,
            last_updated = CURRENT_TIMESTAMP
    """, (player_id, discipline, 1 if success else 0, 0 if success else 1, 
          success, success, success, success))
    
    conn.commit()
    cur.close()
    return_connection(conn)


def get_learning_recommendations(player_id):
    """Get personalized learning recommendations."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT * FROM learning_recommendations 
        WHERE player_id = %s AND is_completed = FALSE
        ORDER BY priority DESC
        LIMIT 5
    """, (player_id,))
    
    recommendations = []
    for row in cur.fetchall():
        recommendations.append({
            'id': row['recommendation_id'],
            'type': row['recommendation_type'],
            'content_type': row['content_type'],
            'content_name': row['content_name'],
            'reason': row['reason'],
            'priority': row['priority']
        })
    
    cur.close()
    return_connection(conn)
    return recommendations


def get_coach_message(player_id, trigger_type):
    """Get a contextual coach message."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT * FROM coach_messages 
        WHERE trigger_type = %s AND is_active = TRUE
        ORDER BY priority DESC
        LIMIT 1
    """, (trigger_type,))
    
    message = cur.fetchone()
    cur.close()
    return_connection(conn)
    
    if message:
        return message['message_text']
    return None


# ============================================================================
# PHASE 5D: CONTENT EXPANSION
# ============================================================================

def get_expanded_worlds(player_level=1):
    """Get available expanded worlds."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT * FROM expanded_worlds 
        WHERE is_active = TRUE
        ORDER BY unlock_level
    """)
    
    worlds = []
    for row in cur.fetchall():
        worlds.append({
            'world_id': row['world_id'],
            'name': row['world_name'],
            'type': row['world_type'],
            'description': row['description'],
            'unlock_level': row['unlock_level'],
            'is_unlocked': player_level >= row['unlock_level'],
            'theme_color': row['theme_color'],
            'mechanics': row['special_mechanics']
        })
    
    cur.close()
    return_connection(conn)
    return worlds


def get_case_studies(discipline=None):
    """Get available case studies."""
    conn = get_connection()
    cur = conn.cursor()
    
    if discipline:
        cur.execute("SELECT * FROM case_studies WHERE discipline = %s ORDER BY difficulty", (discipline,))
    else:
        cur.execute("SELECT * FROM case_studies ORDER BY difficulty")
    
    cases = []
    for row in cur.fetchall():
        cases.append({
            'case_id': row['case_id'],
            'title': row['case_title'],
            'company': row['company_name'],
            'industry': row['industry'],
            'discipline': row['discipline'],
            'difficulty': row['difficulty'],
            'background': row['case_background'],
            'exp_reward': row['exp_reward'],
            'is_premium': row['is_premium']
        })
    
    cur.close()
    return_connection(conn)
    return cases


def get_guest_mentors():
    """Get available guest mentors."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM guest_mentors WHERE is_available = TRUE")
    
    mentors = []
    for row in cur.fetchall():
        mentors.append({
            'mentor_id': row['mentor_id'],
            'name': row['mentor_name'],
            'title': row['mentor_title'],
            'company': row['company'],
            'bio': row['bio'],
            'expertise': row['expertise_areas'],
            'unlock_requirement': row['unlock_requirement']
        })
    
    cur.close()
    return_connection(conn)
    return mentors


def get_advanced_disciplines():
    """Get advanced discipline tracks."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM advanced_disciplines WHERE is_active = TRUE ORDER BY base_discipline")
    
    disciplines = []
    for row in cur.fetchall():
        disciplines.append({
            'discipline_id': row['discipline_id'],
            'base': row['base_discipline'],
            'name': row['advanced_name'],
            'description': row['description'],
            'unlock_level': row['unlock_level'],
            'max_level': row['max_level'],
            'skills': row['special_skills']
        })
    
    cur.close()
    return_connection(conn)
    return disciplines


# ============================================================================
# PHASE 5E: PLAYER PREFERENCES & ACCESSIBILITY
# ============================================================================

def get_player_preferences(player_id):
    """Get player accessibility preferences."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM player_preferences WHERE player_id = %s", (player_id,))
    prefs = cur.fetchone()
    
    if not prefs:
        cur.execute("""
            INSERT INTO player_preferences (player_id)
            VALUES (%s) RETURNING *
        """, (player_id,))
        prefs = cur.fetchone()
        conn.commit()
    
    cur.close()
    return_connection(conn)
    
    return {
        'theme': prefs['theme'],
        'font_size': prefs['font_size'],
        'high_contrast': prefs['high_contrast'],
        'reduced_motion': prefs['reduced_motion'],
        'screen_reader_mode': prefs['screen_reader_mode'],
        'color_blind_mode': prefs['color_blind_mode']
    }


def update_player_preferences(player_id, preferences):
    """Update player accessibility preferences."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        UPDATE player_preferences SET
            theme = COALESCE(%s, theme),
            font_size = COALESCE(%s, font_size),
            high_contrast = COALESCE(%s, high_contrast),
            reduced_motion = COALESCE(%s, reduced_motion),
            screen_reader_mode = COALESCE(%s, screen_reader_mode),
            color_blind_mode = COALESCE(%s, color_blind_mode),
            updated_at = CURRENT_TIMESTAMP
        WHERE player_id = %s
    """, (
        preferences.get('theme'),
        preferences.get('font_size'),
        preferences.get('high_contrast'),
        preferences.get('reduced_motion'),
        preferences.get('screen_reader_mode'),
        preferences.get('color_blind_mode'),
        player_id
    ))
    
    conn.commit()
    cur.close()
    return_connection(conn)
    return {'success': True}


def get_learning_paths(player_id, discipline=None):
    """Get all learning paths with player progress."""
    conn = get_connection()
    cur = conn.cursor()
    
    if discipline:
        cur.execute("""
            SELECT lp.*, 
                   mm.module_title as lesson_title,
                   mt.trial_name,
                   mp.puzzle_name,
                   sm.scenario_title,
                   plpp.lesson_completed, plpp.trial_completed, 
                   plpp.puzzle_completed, 
                   COALESCE(plpp.scenario_completed, cs.scenario_id IS NOT NULL) as scenario_completed,
                   plpp.path_completed, plpp.bonus_claimed
            FROM learning_paths lp
            LEFT JOIN mentorship_modules mm ON lp.lesson_module_id = mm.module_id
            LEFT JOIN mentor_trials mt ON lp.trial_id = mt.trial_id
            LEFT JOIN merchant_puzzles mp ON lp.puzzle_id = mp.puzzle_id
            LEFT JOIN scenario_master sm ON lp.scenario_id = sm.scenario_id
            LEFT JOIN player_learning_path_progress plpp ON lp.path_id = plpp.path_id AND plpp.player_id = %s
            LEFT JOIN completed_scenarios cs ON lp.scenario_id = cs.scenario_id AND cs.player_id = %s
            WHERE lp.discipline = %s AND lp.is_active = TRUE
            ORDER BY lp.sort_order, lp.difficulty
        """, (player_id, player_id, discipline))
    else:
        cur.execute("""
            SELECT lp.*, 
                   mm.module_title as lesson_title,
                   mt.trial_name,
                   mp.puzzle_name,
                   sm.scenario_title,
                   plpp.lesson_completed, plpp.trial_completed, 
                   plpp.puzzle_completed, 
                   COALESCE(plpp.scenario_completed, cs.scenario_id IS NOT NULL) as scenario_completed,
                   plpp.path_completed, plpp.bonus_claimed
            FROM learning_paths lp
            LEFT JOIN mentorship_modules mm ON lp.lesson_module_id = mm.module_id
            LEFT JOIN mentor_trials mt ON lp.trial_id = mt.trial_id
            LEFT JOIN merchant_puzzles mp ON lp.puzzle_id = mp.puzzle_id
            LEFT JOIN scenario_master sm ON lp.scenario_id = sm.scenario_id
            LEFT JOIN player_learning_path_progress plpp ON lp.path_id = plpp.path_id AND plpp.player_id = %s
            LEFT JOIN completed_scenarios cs ON lp.scenario_id = cs.scenario_id AND cs.player_id = %s
            WHERE lp.is_active = TRUE
            ORDER BY lp.discipline, lp.sort_order, lp.difficulty
        """, (player_id, player_id))
    
    paths = cur.fetchall()
    cur.close()
    return_connection(conn)
    return paths


def get_learning_path_by_id(path_id, player_id):
    """Get a single learning path with full details and player progress."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT lp.*, 
               mm.module_id, mm.module_title as lesson_title, mm.theory_content as lesson_description,
               mt.trial_id, mt.trial_name, mt.mentor_name, mt.time_limit_seconds as trial_time,
               mp.puzzle_id, mp.puzzle_name, mp.merchant_name, mp.puzzle_type,
               sm.scenario_id, sm.scenario_title, sm.scenario_narrative,
               plpp.lesson_completed, plpp.lesson_completed_at,
               plpp.trial_completed, plpp.trial_completed_at, plpp.trial_score,
               plpp.puzzle_completed, plpp.puzzle_completed_at, plpp.puzzle_time_seconds,
               COALESCE(plpp.scenario_completed, cs.scenario_id IS NOT NULL) as scenario_completed,
               COALESCE(plpp.scenario_completed_at, cs.completed_at) as scenario_completed_at,
               COALESCE(plpp.scenario_stars, cs.stars_earned) as scenario_stars,
               plpp.path_completed, plpp.path_completed_at, plpp.bonus_claimed
        FROM learning_paths lp
        LEFT JOIN mentorship_modules mm ON lp.lesson_module_id = mm.module_id
        LEFT JOIN mentor_trials mt ON lp.trial_id = mt.trial_id
        LEFT JOIN merchant_puzzles mp ON lp.puzzle_id = mp.puzzle_id
        LEFT JOIN scenario_master sm ON lp.scenario_id = sm.scenario_id
        LEFT JOIN player_learning_path_progress plpp ON lp.path_id = plpp.path_id AND plpp.player_id = %s
        LEFT JOIN completed_scenarios cs ON lp.scenario_id = cs.scenario_id AND cs.player_id = %s
        WHERE lp.path_id = %s
    """, (player_id, player_id, path_id))
    
    path = cur.fetchone()
    cur.close()
    return_connection(conn)
    return path


def update_learning_path_progress(player_id, path_id, stage, score=None, time_seconds=None, stars=None):
    """Update player progress on a learning path stage."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO player_learning_path_progress (player_id, path_id)
        VALUES (%s, %s)
        ON CONFLICT (player_id, path_id) DO NOTHING
    """, (player_id, path_id))
    
    if stage == 'lesson':
        cur.execute("""
            UPDATE player_learning_path_progress 
            SET lesson_completed = TRUE, lesson_completed_at = CURRENT_TIMESTAMP
            WHERE player_id = %s AND path_id = %s
        """, (player_id, path_id))
    elif stage == 'trial':
        cur.execute("""
            UPDATE player_learning_path_progress 
            SET trial_completed = TRUE, trial_completed_at = CURRENT_TIMESTAMP, trial_score = %s
            WHERE player_id = %s AND path_id = %s
        """, (score, player_id, path_id))
    elif stage == 'puzzle':
        cur.execute("""
            UPDATE player_learning_path_progress 
            SET puzzle_completed = TRUE, puzzle_completed_at = CURRENT_TIMESTAMP, puzzle_time_seconds = %s
            WHERE player_id = %s AND path_id = %s
        """, (time_seconds, player_id, path_id))
    elif stage == 'scenario':
        cur.execute("""
            UPDATE player_learning_path_progress 
            SET scenario_completed = TRUE, scenario_completed_at = CURRENT_TIMESTAMP, scenario_stars = %s
            WHERE player_id = %s AND path_id = %s
        """, (stars, player_id, path_id))
    
    cur.execute("""
        UPDATE player_learning_path_progress 
        SET path_completed = TRUE, path_completed_at = CURRENT_TIMESTAMP
        WHERE player_id = %s AND path_id = %s
        AND lesson_completed = TRUE AND trial_completed = TRUE 
        AND puzzle_completed = TRUE AND scenario_completed = TRUE
    """, (player_id, path_id))
    
    conn.commit()
    cur.close()
    return_connection(conn)
    return {'success': True}


def claim_learning_path_bonus(player_id, path_id):
    """Claim the completion bonus for a learning path."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT plpp.*, lp.exp_bonus, lp.gold_bonus, lp.badge_code, lp.discipline
        FROM player_learning_path_progress plpp
        JOIN learning_paths lp ON plpp.path_id = lp.path_id
        WHERE plpp.player_id = %s AND plpp.path_id = %s AND plpp.path_completed = TRUE
    """, (player_id, path_id))
    
    progress = cur.fetchone()
    
    if not progress:
        cur.close()
        return_connection(conn)
        return {'error': 'Path not completed or not found'}
    
    if progress.get('bonus_claimed'):
        cur.close()
        return_connection(conn)
        return {'error': 'Bonus already claimed'}
    
    exp_bonus = progress.get('exp_bonus', 100)
    gold_bonus = progress.get('gold_bonus', 200)
    
    cur.execute("""
        UPDATE player_profiles SET total_cash = total_cash + %s WHERE player_id = %s
    """, (gold_bonus, player_id))
    
    discipline = progress.get('discipline', 'Marketing')
    cur.execute("""
        UPDATE player_discipline_progress 
        SET current_exp = current_exp + %s, total_exp_earned = total_exp_earned + %s
        WHERE player_id = %s AND discipline_name = %s
    """, (exp_bonus, exp_bonus, player_id, discipline))
    
    cur.execute("""
        UPDATE player_learning_path_progress SET bonus_claimed = TRUE WHERE player_id = %s AND path_id = %s
    """, (player_id, path_id))
    
    conn.commit()
    cur.close()
    return_connection(conn)
    
    return {
        'success': True,
        'exp_earned': exp_bonus,
        'gold_earned': gold_bonus,
        'discipline': discipline
    }


def check_learning_path_gate(player_id, scenario_id):
    """Check if a scenario is gated behind a learning path and if prerequisites are met.
    
    Gates ALL scenarios in a discipline until the foundational learning path is complete.
    """
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT discipline FROM scenario_master WHERE scenario_id = %s", (scenario_id,))
    scenario = cur.fetchone()
    
    if not scenario:
        cur.close()
        return_connection(conn)
        return {'gated': False, 'ready': True}
    
    discipline = scenario['discipline']
    
    cur.execute("""
        SELECT lp.*, plpp.lesson_completed, plpp.trial_completed, plpp.puzzle_completed, plpp.path_completed
        FROM learning_paths lp
        LEFT JOIN player_learning_path_progress plpp ON lp.path_id = plpp.path_id AND plpp.player_id = %s
        WHERE lp.discipline = %s AND lp.is_active = TRUE AND lp.difficulty = 1
        ORDER BY lp.sort_order
        LIMIT 1
    """, (player_id, discipline))
    
    path = cur.fetchone()
    cur.close()
    return_connection(conn)
    
    if not path:
        return {'gated': False, 'ready': True}
    
    if path.get('path_completed'):
        return {'gated': False, 'ready': True}
    
    lesson_done = path.get('lesson_completed', False) or path.get('lesson_module_id') is None
    trial_done = path.get('trial_completed', False) or path.get('trial_id') is None
    puzzle_done = path.get('puzzle_completed', False) or path.get('puzzle_id') is None
    
    ready = lesson_done and trial_done and puzzle_done
    
    return {
        'gated': True,
        'ready': ready,
        'path_id': path['path_id'],
        'path_name': path['path_name'],
        'discipline': discipline,
        'lesson_completed': lesson_done,
        'trial_completed': trial_done,
        'puzzle_completed': puzzle_done,
        'lesson_module_id': path.get('lesson_module_id'),
        'trial_id': path.get('trial_id'),
        'puzzle_id': path.get('puzzle_id')
    }


def get_player_next_step(player_id):
    """Get the player's next step in their learning journey.
    
    Returns what the player should do next: learning path, scenario, or exploration.
    """
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT lp.*, 
               plpp.lesson_completed, plpp.trial_completed, plpp.puzzle_completed, 
               plpp.scenario_completed, plpp.path_completed,
               mm.module_title as lesson_title,
               mt.trial_name,
               mp.puzzle_name,
               sm.scenario_title
        FROM learning_paths lp
        LEFT JOIN player_learning_path_progress plpp ON lp.path_id = plpp.path_id AND plpp.player_id = %s
        LEFT JOIN mentorship_modules mm ON lp.lesson_module_id = mm.module_id
        LEFT JOIN mentor_trials mt ON lp.trial_id = mt.trial_id
        LEFT JOIN merchant_puzzles mp ON lp.puzzle_id = mp.puzzle_id
        LEFT JOIN scenario_master sm ON lp.scenario_id = sm.scenario_id
        WHERE lp.is_active = TRUE 
        AND (plpp.path_completed IS NULL OR plpp.path_completed = FALSE)
        ORDER BY lp.difficulty, lp.sort_order
        LIMIT 1
    """, (player_id,))
    
    path = cur.fetchone()
    cur.close()
    return_connection(conn)
    
    if not path:
        return {
            'type': 'explore',
            'message': 'All learning paths complete! Explore freely.',
            'action_url': '/campaign',
            'action_text': 'Explore Campaign'
        }
    
    lesson_done = path.get('lesson_completed', False) or path.get('lesson_module_id') is None
    trial_done = path.get('trial_completed', False) or path.get('trial_id') is None
    puzzle_done = path.get('puzzle_completed', False) or path.get('puzzle_id') is None
    scenario_done = path.get('scenario_completed', False) or path.get('scenario_id') is None
    
    if not lesson_done:
        return {
            'type': 'lesson',
            'path_id': path['path_id'],
            'path_name': path['path_name'],
            'discipline': path['discipline'],
            'stage': 'Lesson',
            'stage_name': path.get('lesson_title', 'Learn the Basics'),
            'message': f"Start your {path['discipline']} journey with a lesson",
            'action_url': f"/mentorship/lesson/{path['lesson_module_id']}",
            'action_text': 'Start Lesson',
            'progress': {'lesson': False, 'trial': trial_done, 'puzzle': puzzle_done, 'scenario': scenario_done}
        }
    elif not trial_done:
        return {
            'type': 'trial',
            'path_id': path['path_id'],
            'path_name': path['path_name'],
            'discipline': path['discipline'],
            'stage': 'Quiz',
            'stage_name': path.get('trial_name', 'Knowledge Check'),
            'message': f"Test your {path['discipline']} knowledge",
            'action_url': f"/trials/{path['trial_id']}?path_id={path['path_id']}",
            'action_text': 'Take Quiz',
            'progress': {'lesson': True, 'trial': False, 'puzzle': puzzle_done, 'scenario': scenario_done}
        }
    elif not puzzle_done:
        return {
            'type': 'puzzle',
            'path_id': path['path_id'],
            'path_name': path['path_name'],
            'discipline': path['discipline'],
            'stage': 'Challenge',
            'stage_name': path.get('puzzle_name', 'Calculation Challenge'),
            'message': f"Apply {path['discipline']} formulas",
            'action_url': f"/puzzles/{path['puzzle_id']}?path_id={path['path_id']}",
            'action_text': 'Solve Challenge',
            'progress': {'lesson': True, 'trial': True, 'puzzle': False, 'scenario': scenario_done}
        }
    elif not scenario_done:
        return {
            'type': 'scenario',
            'path_id': path['path_id'],
            'path_name': path['path_name'],
            'discipline': path['discipline'],
            'stage': 'Scenario',
            'stage_name': path.get('scenario_title', 'Business Decision'),
            'message': f"Make a real {path['discipline']} decision",
            'action_url': f"/play/{path['scenario_id']}",
            'action_text': 'Play Scenario',
            'progress': {'lesson': True, 'trial': True, 'puzzle': True, 'scenario': False}
        }
    else:
        return {
            'type': 'complete',
            'path_id': path['path_id'],
            'path_name': path['path_name'],
            'discipline': path['discipline'],
            'message': f"Claim your {path['path_name']} rewards!",
            'action_url': f"/learning-paths/{path['path_id']}",
            'action_text': 'Claim Rewards',
            'progress': {'lesson': True, 'trial': True, 'puzzle': True, 'scenario': True}
        }
