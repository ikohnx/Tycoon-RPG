from .connection import get_connection, return_connection


def get_default_chart_of_accounts():
    """Return the standard chart of accounts for a new player's business."""
    return [
        # Assets (Debit balance)
        {'code': '1000', 'name': 'Cash', 'type': 'Asset', 'normal': 'Debit', 'desc': 'Money in the bank and on hand'},
        {'code': '1100', 'name': 'Accounts Receivable', 'type': 'Asset', 'normal': 'Debit', 'desc': 'Money owed to you by customers'},
        {'code': '1200', 'name': 'Inventory', 'type': 'Asset', 'normal': 'Debit', 'desc': 'Goods available for sale'},
        {'code': '1300', 'name': 'Prepaid Expenses', 'type': 'Asset', 'normal': 'Debit', 'desc': 'Expenses paid in advance'},
        {'code': '1500', 'name': 'Equipment', 'type': 'Asset', 'normal': 'Debit', 'desc': 'Business equipment and tools'},
        {'code': '1510', 'name': 'Accumulated Depreciation', 'type': 'Asset', 'normal': 'Credit', 'desc': 'Total depreciation of equipment'},
        # Liabilities (Credit balance)
        {'code': '2000', 'name': 'Accounts Payable', 'type': 'Liability', 'normal': 'Credit', 'desc': 'Money you owe to suppliers'},
        {'code': '2100', 'name': 'Wages Payable', 'type': 'Liability', 'normal': 'Credit', 'desc': 'Unpaid employee wages'},
        {'code': '2200', 'name': 'Taxes Payable', 'type': 'Liability', 'normal': 'Credit', 'desc': 'Taxes owed to government'},
        {'code': '2300', 'name': 'Unearned Revenue', 'type': 'Liability', 'normal': 'Credit', 'desc': 'Payment received before service delivered'},
        {'code': '2500', 'name': 'Loans Payable', 'type': 'Liability', 'normal': 'Credit', 'desc': 'Business loans to repay'},
        # Equity (Credit balance)
        {'code': '3000', 'name': 'Owner Capital', 'type': 'Equity', 'normal': 'Credit', 'desc': 'Owner investment in business'},
        {'code': '3100', 'name': 'Retained Earnings', 'type': 'Equity', 'normal': 'Credit', 'desc': 'Accumulated profits kept in business'},
        {'code': '3200', 'name': 'Owner Withdrawals', 'type': 'Equity', 'normal': 'Debit', 'desc': 'Money taken out by owner'},
        # Revenue (Credit balance)
        {'code': '4000', 'name': 'Sales Revenue', 'type': 'Revenue', 'normal': 'Credit', 'desc': 'Income from selling products/services'},
        {'code': '4100', 'name': 'Service Revenue', 'type': 'Revenue', 'normal': 'Credit', 'desc': 'Income from providing services'},
        {'code': '4200', 'name': 'Interest Income', 'type': 'Revenue', 'normal': 'Credit', 'desc': 'Interest earned on investments'},
        {'code': '4900', 'name': 'Other Income', 'type': 'Revenue', 'normal': 'Credit', 'desc': 'Miscellaneous income'},
        # Expenses (Debit balance)
        {'code': '5000', 'name': 'Cost of Goods Sold', 'type': 'Expense', 'normal': 'Debit', 'desc': 'Direct cost of products sold'},
        {'code': '5100', 'name': 'Wages Expense', 'type': 'Expense', 'normal': 'Debit', 'desc': 'Employee salaries and wages'},
        {'code': '5200', 'name': 'Rent Expense', 'type': 'Expense', 'normal': 'Debit', 'desc': 'Monthly rent payments'},
        {'code': '5300', 'name': 'Utilities Expense', 'type': 'Expense', 'normal': 'Debit', 'desc': 'Electricity, water, internet'},
        {'code': '5400', 'name': 'Marketing Expense', 'type': 'Expense', 'normal': 'Debit', 'desc': 'Advertising and promotion costs'},
        {'code': '5500', 'name': 'Supplies Expense', 'type': 'Expense', 'normal': 'Debit', 'desc': 'Office and operational supplies'},
        {'code': '5600', 'name': 'Insurance Expense', 'type': 'Expense', 'normal': 'Debit', 'desc': 'Business insurance premiums'},
        {'code': '5700', 'name': 'Depreciation Expense', 'type': 'Expense', 'normal': 'Debit', 'desc': 'Equipment value reduction'},
        {'code': '5800', 'name': 'Interest Expense', 'type': 'Expense', 'normal': 'Debit', 'desc': 'Interest on loans'},
        {'code': '5900', 'name': 'Tax Expense', 'type': 'Expense', 'normal': 'Debit', 'desc': 'Business taxes'},
        {'code': '5950', 'name': 'Miscellaneous Expense', 'type': 'Expense', 'normal': 'Debit', 'desc': 'Other business expenses'},
    ]


def initialize_player_accounting(player_id):
    """Initialize the accounting system for a player with default accounts and first period."""
    conn = get_connection()
    cur = conn.cursor()
    
    # Check if player already has accounts
    cur.execute("SELECT COUNT(*) as count FROM chart_of_accounts WHERE player_id = %s", (player_id,))
    if cur.fetchone()['count'] > 0:
        cur.close()
        return_connection(conn)
        return False
    
    # Create default chart of accounts
    accounts = get_default_chart_of_accounts()
    for acc in accounts:
        cur.execute("""
            INSERT INTO chart_of_accounts (player_id, account_code, account_name, account_type, normal_balance, description)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (player_id, acc['code'], acc['name'], acc['type'], acc['normal'], acc['desc']))
    
    # Create first accounting period (Month 1)
    from datetime import date, timedelta
    today = date.today()
    start_of_month = today.replace(day=1)
    if today.month == 12:
        end_of_month = today.replace(year=today.year+1, month=1, day=1) - timedelta(days=1)
    else:
        end_of_month = today.replace(month=today.month+1, day=1) - timedelta(days=1)
    
    cur.execute("""
        INSERT INTO accounting_periods (player_id, period_name, period_number, start_date, end_date)
        VALUES (%s, %s, %s, %s, %s)
    """, (player_id, 'Month 1', 1, start_of_month, end_of_month))
    
    # Get the new period ID
    cur.execute("SELECT period_id FROM accounting_periods WHERE player_id = %s AND period_number = 1", (player_id,))
    period_id = cur.fetchone()['period_id']
    
    # Get cash account and set opening balance from player's current cash
    cur.execute("SELECT cash FROM player_profiles WHERE player_id = %s", (player_id,))
    player_cash = cur.fetchone()['cash'] or 0
    
    cur.execute("SELECT account_id FROM chart_of_accounts WHERE player_id = %s AND account_code = '1000'", (player_id,))
    cash_account_id = cur.fetchone()['account_id']
    
    cur.execute("""
        INSERT INTO account_balances (player_id, account_id, period_id, opening_balance, closing_balance)
        VALUES (%s, %s, %s, %s, %s)
    """, (player_id, cash_account_id, period_id, player_cash, player_cash))
    
    # Set opening balance for Owner Capital to match
    cur.execute("SELECT account_id FROM chart_of_accounts WHERE player_id = %s AND account_code = '3000'", (player_id,))
    capital_account_id = cur.fetchone()['account_id']
    
    cur.execute("""
        INSERT INTO account_balances (player_id, account_id, period_id, opening_balance, closing_balance)
        VALUES (%s, %s, %s, %s, %s)
    """, (player_id, capital_account_id, period_id, player_cash, player_cash))
    
    conn.commit()
    cur.close()
    return_connection(conn)
    return True


def get_project_templates():
    """Return sample project templates for different worlds/industries."""
    return [
        {
            'title': 'Restaurant Grand Opening',
            'description': 'Plan and execute the grand opening of your new restaurant location.',
            'world_type': 'Modern',
            'industry': 'Restaurant',
            'planned_duration_weeks': 6,
            'budget': 15000,
            'completion_bonus_exp': 200,
            'completion_bonus_cash': 5000,
            'tasks': [
                {'name': 'Site Selection & Lease', 'effort': 16, 'week_start': 1, 'week_end': 2, 'priority': 'high'},
                {'name': 'Permits & Licensing', 'effort': 8, 'week_start': 1, 'week_end': 2, 'priority': 'high', 'depends_on': []},
                {'name': 'Interior Design', 'effort': 24, 'week_start': 2, 'week_end': 3, 'priority': 'medium', 'depends_on': ['Site Selection & Lease']},
                {'name': 'Equipment Procurement', 'effort': 16, 'week_start': 2, 'week_end': 4, 'priority': 'high', 'depends_on': ['Site Selection & Lease']},
                {'name': 'Staff Hiring', 'effort': 20, 'week_start': 3, 'week_end': 4, 'priority': 'high'},
                {'name': 'Staff Training', 'effort': 40, 'week_start': 4, 'week_end': 5, 'priority': 'high', 'depends_on': ['Staff Hiring']},
                {'name': 'Menu Development', 'effort': 16, 'week_start': 3, 'week_end': 4, 'priority': 'medium'},
                {'name': 'Marketing Campaign', 'effort': 12, 'week_start': 4, 'week_end': 6, 'priority': 'medium'},
                {'name': 'Soft Opening', 'effort': 8, 'week_start': 5, 'week_end': 5, 'priority': 'high', 'depends_on': ['Staff Training', 'Equipment Procurement']},
                {'name': 'Grand Opening Event', 'effort': 16, 'week_start': 6, 'week_end': 6, 'priority': 'high', 'depends_on': ['Soft Opening', 'Marketing Campaign']}
            ]
        },
        {
            'title': 'New Product Launch',
            'description': 'Coordinate the launch of a new signature dish across all locations.',
            'world_type': 'Modern',
            'industry': 'Restaurant',
            'planned_duration_weeks': 4,
            'budget': 5000,
            'completion_bonus_exp': 150,
            'completion_bonus_cash': 2500,
            'tasks': [
                {'name': 'Recipe Development', 'effort': 16, 'week_start': 1, 'week_end': 1, 'priority': 'high'},
                {'name': 'Cost Analysis', 'effort': 8, 'week_start': 1, 'week_end': 1, 'priority': 'medium', 'depends_on': ['Recipe Development']},
                {'name': 'Supplier Sourcing', 'effort': 12, 'week_start': 2, 'week_end': 2, 'priority': 'high', 'depends_on': ['Cost Analysis']},
                {'name': 'Staff Training', 'effort': 16, 'week_start': 2, 'week_end': 3, 'priority': 'high', 'depends_on': ['Recipe Development']},
                {'name': 'Marketing Materials', 'effort': 12, 'week_start': 2, 'week_end': 3, 'priority': 'medium'},
                {'name': 'Soft Launch', 'effort': 8, 'week_start': 3, 'week_end': 3, 'priority': 'high', 'depends_on': ['Staff Training', 'Supplier Sourcing']},
                {'name': 'Full Rollout', 'effort': 8, 'week_start': 4, 'week_end': 4, 'priority': 'high', 'depends_on': ['Soft Launch', 'Marketing Materials']}
            ]
        }
    ]


def initialize_player_projects(player_id):
    """Initialize the project management system for a player with default resources."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM project_resources WHERE player_id = %s", (player_id,))
    if cur.fetchone()['count'] > 0:
        cur.close()
        return_connection(conn)
        return False
    
    default_resources = [
        {'name': 'You (Manager)', 'type': 'manager', 'capacity': 40, 'cost': 0, 'bonus': 10},
        {'name': 'Staff Member 1', 'type': 'staff', 'capacity': 40, 'cost': 25, 'bonus': 0},
        {'name': 'Staff Member 2', 'type': 'staff', 'capacity': 40, 'cost': 25, 'bonus': 0}
    ]
    
    for res in default_resources:
        cur.execute("""
            INSERT INTO project_resources (player_id, resource_name, resource_type, capacity_hours_per_week, hourly_cost, skill_bonus)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (player_id, res['name'], res['type'], res['capacity'], res['cost'], res['bonus']))
    
    conn.commit()
    cur.close()
    return_connection(conn)
    return True
