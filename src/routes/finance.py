from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from src.routes.helpers import login_required, feature_gated, get_engine

finance_bp = Blueprint('finance', __name__)


@finance_bp.route('/accounting')
@login_required
def accounting():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    from src.database import initialize_player_accounting
    initialize_player_accounting(player_id)

    accounts = get_engine().get_player_chart_of_accounts(player_id)
    period = get_engine().get_current_accounting_period(player_id)
    pending_transactions = get_engine().get_pending_transactions(player_id)
    journal_entries = get_engine().get_journal_entries(player_id)
    trial_balance = get_engine().get_trial_balance(player_id)
    income_statement = get_engine().get_income_statement(player_id)
    balance_sheet = get_engine().get_balance_sheet(player_id)

    return render_template('finance/accounting.html',
                          stats=stats,
                          accounts=accounts,
                          period=period,
                          pending_transactions=pending_transactions,
                          journal_entries=journal_entries,
                          trial_balance=trial_balance,
                          income_statement=income_statement,
                          balance_sheet=balance_sheet)


@finance_bp.route('/accounting/process', methods=['POST'])
@login_required
def accounting_process():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    transaction_id = request.form.get('transaction_id', type=int)
    debit_account = request.form.get('debit_account')
    credit_account = request.form.get('credit_account')

    if transaction_id and debit_account and credit_account:
        result = get_engine().process_pending_transaction(player_id, transaction_id, debit_account, credit_account)
        if result.get('success'):
            flash(f"Transaction posted! +{result['exp_earned']} EXP earned.")
        else:
            flash(result.get('error', 'Failed to post transaction'))

    return redirect(url_for('finance.accounting'))


@finance_bp.route('/accounting/entry', methods=['POST'])
@login_required
def accounting_entry():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    description = request.form.get('description', '').strip()
    debit_account = request.form.get('debit_account', '').strip()
    credit_account = request.form.get('credit_account', '').strip()
    is_adjusting = request.form.get('is_adjusting') == 'on'

    try:
        debit_amount = float(request.form.get('debit_amount', 0) or 0)
        credit_amount = float(request.form.get('credit_amount', 0) or 0)
    except (ValueError, TypeError):
        flash('Invalid amount values!')
        return redirect(url_for('finance.accounting'))

    if debit_amount <= 0 or credit_amount <= 0:
        flash('Amounts must be greater than zero!')
        return redirect(url_for('finance.accounting'))

    if abs(debit_amount - credit_amount) > 0.01:
        flash('Debits must equal Credits!')
        return redirect(url_for('finance.accounting'))

    if not debit_account or not credit_account:
        flash('Please select valid accounts!')
        return redirect(url_for('finance.accounting'))

    if not description:
        flash('Please provide a description!')
        return redirect(url_for('finance.accounting'))

    lines = [
        {'account_code': debit_account, 'debit': debit_amount, 'credit': 0},
        {'account_code': credit_account, 'debit': 0, 'credit': credit_amount}
    ]

    result = get_engine().create_journal_entry(player_id, description, lines, is_adjusting)

    if result.get('success'):
        flash(f"Journal entry posted! +{result['exp_earned']} EXP earned.")
    else:
        flash(result.get('error', 'Failed to create entry'))

    return redirect(url_for('finance.accounting'))


@finance_bp.route('/projects')
@login_required
def projects():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    from src.database import initialize_player_projects
    initialize_player_projects(player_id)

    from src.game_engine import (get_player_initiatives, get_active_initiative,
                                  get_player_resources, get_scheduling_challenges,
                                  get_project_templates_list)

    active_project = get_active_initiative(player_id)
    all_initiatives = get_player_initiatives(player_id)
    resources = get_player_resources(player_id)
    templates = get_project_templates_list()

    player_level = stats.get('overall_level', 1) if isinstance(stats, dict) else 1
    challenges = get_scheduling_challenges(player_level)

    return render_template('finance/projects.html',
                          stats=stats,
                          active_project=active_project,
                          all_initiatives=all_initiatives,
                          resources=resources,
                          templates=templates,
                          challenges=challenges)


@finance_bp.route('/projects/start', methods=['POST'])
@login_required
def start_project():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    template_index = request.form.get('template_index', 0, type=int)

    from src.game_engine import create_initiative_from_template
    result = create_initiative_from_template(player_id, template_index)

    if result.get('success'):
        flash(f"Started new project: {result['title']}")
    else:
        flash(result.get('error', 'Failed to start project'))

    return redirect(url_for('finance.projects'))


@finance_bp.route('/projects/advance', methods=['POST'])
@login_required
def advance_project():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    initiative_id = request.form.get('initiative_id', type=int)

    from src.game_engine import advance_project_week
    result = advance_project_week(player_id, initiative_id)

    if result.get('success'):
        if result.get('project_completed'):
            bonus_type = "On-Time Bonus!" if result.get('on_time') else "Project Complete!"
            flash(f"{bonus_type} +{result['exp_earned']} EXP, +${result.get('bonus_earned', 0)} cash!")
        else:
            completed = ", ".join(result.get('completed_tasks', []))
            msg = f"Week {result['new_week']} complete!"
            if completed:
                msg += f" Finished: {completed}"
            if result['exp_earned'] > 0:
                msg += f" +{result['exp_earned']} EXP"
            flash(msg)
    else:
        flash(result.get('error', 'Failed to advance project'))

    return redirect(url_for('finance.projects'))


@finance_bp.route('/projects/challenge/<int:challenge_id>')
@login_required
def scheduling_challenge(challenge_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    from src.game_engine import get_scheduling_challenge
    challenge = get_scheduling_challenge(challenge_id)

    if not challenge:
        flash('Challenge not found')
        return redirect(url_for('finance.projects'))

    return render_template('finance/scheduling_challenge.html',
                          stats=stats,
                          challenge=challenge)


@finance_bp.route('/projects/challenge/<int:challenge_id>/submit', methods=['POST'])
@login_required
def submit_scheduling_challenge(challenge_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    from src.game_engine import submit_scheduling_challenge as submit_challenge_fn, get_scheduling_challenge

    challenge = get_scheduling_challenge(challenge_id)
    if not challenge:
        flash('Challenge not found')
        return redirect(url_for('finance.projects'))

    answer = {}
    if challenge['challenge_type'] == 'critical_path':
        answer['duration'] = request.form.get('duration', 0, type=int)
    elif challenge['challenge_type'] == 'estimation':
        answer['expected'] = request.form.get('expected', 0, type=float)
    elif challenge['challenge_type'] == 'compression':
        answer['choice'] = request.form.get('choice', '')
    elif challenge['challenge_type'] == 'resource_leveling':
        answer['assignments'] = {}
        for key, value in request.form.items():
            if key.startswith('assign_'):
                task_id = key.replace('assign_', '')
                answer['assignments'][task_id] = value

    result = submit_challenge_fn(player_id, challenge_id, answer)

    if result['is_correct']:
        flash(f"Correct! +{result['exp_earned']} EXP earned!")
    else:
        flash(f"Not quite right. {result['feedback']} (+{result['exp_earned']} EXP for effort)")

    return redirect(url_for('finance.projects'))


@finance_bp.route('/cashflow')
@login_required
def cashflow():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    from src.game_engine import get_cash_flow_challenges, get_player_cash_flow_forecast

    challenges = get_cash_flow_challenges(stats.get('overall_level', 1) if isinstance(stats, dict) else 1)
    forecast = get_player_cash_flow_forecast(player_id)

    return render_template('finance/cashflow.html',
                          stats=stats,
                          challenges=challenges,
                          forecast=forecast)


@finance_bp.route('/cashflow/challenge/<int:challenge_id>')
@login_required
def cashflow_challenge(challenge_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    from src.game_engine import get_cash_flow_challenge
    challenge = get_cash_flow_challenge(challenge_id)

    if not challenge:
        flash('Challenge not found')
        return redirect(url_for('finance.cashflow'))

    return render_template('finance/cashflow_challenge.html',
                          stats=stats,
                          challenge=challenge)


@finance_bp.route('/cashflow/challenge/<int:challenge_id>/submit', methods=['POST'])
@login_required
def submit_cashflow_challenge(challenge_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    from src.game_engine import submit_cash_flow_challenge, get_cash_flow_challenge

    challenge = get_cash_flow_challenge(challenge_id)
    if not challenge:
        flash('Challenge not found')
        return redirect(url_for('finance.cashflow'))

    answer = {}
    if challenge['challenge_type'] == 'timing':
        answer['choice'] = request.form.get('choice', '')
    elif challenge['challenge_type'] == 'planning':
        answer['weeks'] = request.form.get('weeks', 0, type=int)
    elif challenge['challenge_type'] == 'forecast':
        answer['credit_needed_week'] = request.form.get('credit_needed_week', 0, type=int)
    elif challenge['challenge_type'] == 'prioritization':
        priority_str = request.form.get('priority', '')
        answer['priority'] = [int(x.strip()) for x in priority_str.split(',') if x.strip().isdigit()]
    elif challenge['challenge_type'] == 'seasonal':
        answer['savings_needed'] = request.form.get('savings_needed', 0, type=int)

    result = submit_cash_flow_challenge(player_id, challenge_id, answer)

    if result['is_correct']:
        flash(f"Correct! +{result['exp_earned']} EXP earned! {result['feedback']}")
    else:
        flash(f"Not quite right. {result['feedback']} (+{result['exp_earned']} EXP for effort)")

    return redirect(url_for('finance.cashflow'))


@finance_bp.route('/businessplan')
@login_required
def businessplan():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    from src.game_engine import get_player_business_plans, BUSINESS_PLAN_SECTIONS

    plans = get_player_business_plans(player_id)

    return render_template('finance/businessplan.html',
                          stats=stats,
                          plans=plans,
                          section_templates=BUSINESS_PLAN_SECTIONS)


@finance_bp.route('/businessplan/create', methods=['POST'])
@login_required
def create_businessplan():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    plan_name = request.form.get('plan_name', 'My Business Plan')
    business_type = request.form.get('business_type', '')

    from src.game_engine import create_business_plan
    result = create_business_plan(player_id, plan_name, business_type)

    if result.get('success'):
        flash(f"Created new business plan: {plan_name}")
        return redirect(url_for('finance.edit_businessplan', plan_id=result['plan_id']))
    else:
        flash('Failed to create business plan')
        return redirect(url_for('finance.businessplan'))


@finance_bp.route('/businessplan/<int:plan_id>')
@login_required
def edit_businessplan(plan_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    from src.game_engine import get_business_plan
    plan = get_business_plan(plan_id)

    if not plan or plan['player_id'] != player_id:
        flash('Business plan not found')
        return redirect(url_for('finance.businessplan'))

    return render_template('finance/businessplan_edit.html',
                          stats=stats,
                          plan=plan)


@finance_bp.route('/businessplan/section/<int:section_id>/save', methods=['POST'])
@login_required
def save_businessplan_section(section_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    content = request.form.get('content', '')

    from src.game_engine import update_business_plan_section
    result = update_business_plan_section(section_id, content)

    if result.get('success'):
        flash(f"Section saved! Score: {result['score']}/100. {result['feedback']}")
    else:
        flash('Failed to save section')

    return redirect(request.referrer or url_for('finance.businessplan'))


@finance_bp.route('/negotiation')
@login_required
@feature_gated('negotiation')
def negotiation():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    from src.game_engine import get_negotiation_scenarios

    scenarios = get_negotiation_scenarios(stats.get('overall_level', 1) if isinstance(stats, dict) else 1)

    return render_template('finance/negotiation.html',
                          stats=stats,
                          scenarios=scenarios)


@finance_bp.route('/negotiation/<int:scenario_id>')
@login_required
def negotiation_scenario(scenario_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    from src.game_engine import get_negotiation_scenario, start_negotiation

    scenario = get_negotiation_scenario(scenario_id)
    if not scenario:
        flash('Scenario not found')
        return redirect(url_for('finance.negotiation'))

    result = start_negotiation(player_id, scenario_id)

    return render_template('finance/negotiation_play.html',
                          stats=stats,
                          scenario=scenario,
                          negotiation_id=result.get('negotiation_id'))


@finance_bp.route('/negotiation/offer/<int:negotiation_id>', methods=['POST'])
@login_required
def submit_negotiation_offer(negotiation_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    from src.game_engine import submit_negotiation_offer as submit_offer

    offer = {}
    for key, value in request.form.items():
        if key.startswith('issue_'):
            issue_name = key.replace('issue_', '')
            try:
                offer[issue_name] = float(value)
            except ValueError:
                offer[issue_name] = value

    result = submit_offer(negotiation_id, offer)

    if result.get('deal_reached'):
        flash(f"{result['message']} +{result['exp_earned']} EXP earned!")
        return redirect(url_for('finance.negotiation'))
    else:
        flash(result.get('message', 'Offer submitted'))
        return redirect(request.referrer or url_for('finance.negotiation'))


@finance_bp.route('/risks')
@login_required
@feature_gated('risks')
def risks():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    from src.game_engine import get_risk_categories, get_player_risks

    categories = get_risk_categories()
    player_risks = get_player_risks(player_id)

    return render_template('finance/risks.html',
                          stats=stats,
                          categories=categories,
                          risks=player_risks)


@finance_bp.route('/risks/add', methods=['POST'])
@login_required
def add_risk():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    from src.game_engine import add_player_risk

    category_id = request.form.get('category_id', type=int)
    risk_name = request.form.get('risk_name', '')
    description = request.form.get('description', '')
    probability = request.form.get('probability', 50, type=int)
    impact = request.form.get('impact', 50, type=int)
    mitigation = request.form.get('mitigation', '')

    result = add_player_risk(player_id, category_id, risk_name, description, probability, impact, mitigation)

    if result.get('success'):
        flash(f"Risk added! Risk Score: {result['risk_score']}")
    else:
        flash('Failed to add risk')

    return redirect(url_for('finance.risks'))


@finance_bp.route('/supplychain')
@login_required
@feature_gated('supplychain')
def supplychain():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    from src.game_engine import initialize_player_supply_chain, get_player_inventory, get_player_suppliers

    initialize_player_supply_chain(player_id)

    inventory = get_player_inventory(player_id)
    suppliers = get_player_suppliers(player_id)

    return render_template('finance/supplychain.html',
                          stats=stats,
                          inventory=inventory,
                          suppliers=suppliers)


@finance_bp.route('/supplychain/order', methods=['POST'])
@login_required
def create_order():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    from src.game_engine import create_purchase_order

    supplier_id = request.form.get('supplier_id', type=int)
    product_id = request.form.get('product_id', type=int)
    quantity = request.form.get('quantity', type=int)

    result = create_purchase_order(player_id, supplier_id, product_id, quantity)

    if result.get('success'):
        flash(f"Purchase order created! Total: ${result['total_cost']:.2f}")
    else:
        flash(result.get('error', 'Failed to create order'))

    return redirect(url_for('finance.supplychain'))


@finance_bp.route('/market')
@login_required
@feature_gated('market')
def market():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    from src.game_engine import get_market_segments, get_market_challenges, initialize_player_market, get_player_market_position

    initialize_player_market(player_id)

    segments = get_market_segments()
    challenges = get_market_challenges(stats.get('overall_level', 1) if isinstance(stats, dict) else 1)
    position = get_player_market_position(player_id)

    return render_template('finance/market.html',
                          stats=stats,
                          segments=segments,
                          challenges=challenges,
                          position=position)


@finance_bp.route('/market/challenge/<int:challenge_id>')
@login_required
def market_challenge(challenge_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    from src.game_engine import get_market_challenge
    challenge = get_market_challenge(challenge_id)

    if not challenge:
        flash('Challenge not found')
        return redirect(url_for('finance.market'))

    return render_template('finance/market_challenge.html',
                          stats=stats,
                          challenge=challenge)


@finance_bp.route('/market/challenge/<int:challenge_id>/submit', methods=['POST'])
@login_required
def submit_market_challenge(challenge_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    from src.game_engine import submit_market_challenge as submit_challenge_fn, get_market_challenge

    challenge = get_market_challenge(challenge_id)
    if not challenge:
        flash('Challenge not found')
        return redirect(url_for('finance.market'))

    answer = {}
    if challenge['challenge_type'] == 'pricing':
        answer['new_revenue'] = request.form.get('new_revenue', 0, type=float)
    elif challenge['challenge_type'] == 'competition':
        answer['decision'] = request.form.get('decision', '')
    elif challenge['challenge_type'] == 'marketing':
        answer['roi'] = request.form.get('roi', 0, type=float)
    elif challenge['challenge_type'] == 'segmentation':
        answer['best_segment'] = request.form.get('best_segment', '')
    elif challenge['challenge_type'] == 'positioning':
        answer['strategy'] = request.form.get('strategy', '')

    result = submit_challenge_fn(player_id, challenge_id, answer)

    if result['is_correct']:
        flash(f"Correct! +{result['exp_earned']} EXP earned! {result['feedback']}")
    else:
        flash(f"Not quite right. {result['feedback']} (+{result['exp_earned']} EXP for effort)")

    return redirect(url_for('finance.market'))


@finance_bp.route('/hrmanagement')
@login_required
@feature_gated('hrmanagement')
def hrmanagement():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    from src.game_engine import get_employee_roles, get_hr_challenges, get_player_employees

    roles = get_employee_roles()
    challenges = get_hr_challenges(stats.get('overall_level', 1) if isinstance(stats, dict) else 1)
    employees = get_player_employees(player_id)

    return render_template('finance/hrmanagement.html',
                          stats=stats,
                          roles=roles,
                          challenges=challenges,
                          employees=employees)


@finance_bp.route('/hrmanagement/challenge/<int:challenge_id>')
@login_required
def hr_challenge(challenge_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    from src.game_engine import get_hr_challenge
    challenge = get_hr_challenge(challenge_id)

    if not challenge:
        flash('Challenge not found')
        return redirect(url_for('finance.hrmanagement'))

    return render_template('finance/hr_challenge.html',
                          stats=stats,
                          challenge=challenge)


@finance_bp.route('/hrmanagement/challenge/<int:challenge_id>/submit', methods=['POST'])
@login_required
def submit_hr_challenge(challenge_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    from src.game_engine import submit_hr_challenge as submit_challenge_fn, get_hr_challenge

    challenge = get_hr_challenge(challenge_id)
    if not challenge:
        flash('Challenge not found')
        return redirect(url_for('finance.hrmanagement'))

    answer = {}
    if challenge['challenge_type'] == 'hiring':
        answer['choice'] = request.form.get('choice', '')
    elif challenge['challenge_type'] == 'performance':
        answer['rating'] = request.form.get('rating', 0, type=int)
    elif challenge['challenge_type'] == 'conflict':
        answer['approach'] = request.form.get('approach', '')
    elif challenge['challenge_type'] == 'retention':
        perks_str = request.form.get('perks', '')
        answer['perks'] = [p.strip() for p in perks_str.split(',') if p.strip()]
    elif challenge['challenge_type'] == 'culture':
        answer['choice'] = request.form.get('choice', '')

    result = submit_challenge_fn(player_id, challenge_id, answer)

    if result['is_correct']:
        flash(f"Correct! +{result['exp_earned']} EXP earned! {result['feedback']}")
    else:
        flash(f"Not quite right. {result['feedback']} (+{result['exp_earned']} EXP for effort)")

    return redirect(url_for('finance.hrmanagement'))


@finance_bp.route('/hrmanagement/hire', methods=['POST'])
@login_required
def hire_employee():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    from src.game_engine import hire_employee as do_hire

    role_id = request.form.get('role_id', type=int)
    employee_name = request.form.get('employee_name', '')
    salary = request.form.get('salary', type=float)

    result = do_hire(player_id, role_id, employee_name, salary)

    if result.get('success'):
        flash(f"Hired {employee_name}!")
    else:
        flash('Failed to hire employee')

    return redirect(url_for('finance.hrmanagement'))


@finance_bp.route('/pitch')
@login_required
@feature_gated('pitch')
def pitch():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    from src.game_engine import get_player_pitch_decks, get_investor_profiles, PITCH_SECTIONS

    decks = get_player_pitch_decks(player_id)
    investors = get_investor_profiles()

    return render_template('finance/pitch.html',
                          stats=stats,
                          decks=decks,
                          investors=investors,
                          section_templates=PITCH_SECTIONS)


@finance_bp.route('/pitch/create', methods=['POST'])
@login_required
def create_pitch():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    deck_name = request.form.get('deck_name', 'My Pitch Deck')
    funding_stage = request.form.get('funding_stage', 'seed')
    target_amount = request.form.get('target_amount', 100000, type=float)

    from src.game_engine import create_pitch_deck
    result = create_pitch_deck(player_id, deck_name, funding_stage, target_amount)

    if result.get('success'):
        flash(f"Created new pitch deck: {deck_name}")
        return redirect(url_for('finance.edit_pitch', deck_id=result['deck_id']))
    else:
        flash('Failed to create pitch deck')
        return redirect(url_for('finance.pitch'))


@finance_bp.route('/pitch/<int:deck_id>')
@login_required
def edit_pitch(deck_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    from src.game_engine import get_pitch_deck
    deck = get_pitch_deck(deck_id)

    if not deck or deck['player_id'] != player_id:
        flash('Pitch deck not found')
        return redirect(url_for('finance.pitch'))

    return render_template('finance/pitch_edit.html',
                          stats=stats,
                          deck=deck)


@finance_bp.route('/pitch/section/<int:section_id>/save', methods=['POST'])
@login_required
def save_pitch_section(section_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    content = request.form.get('content', '')

    from src.game_engine import update_pitch_section
    result = update_pitch_section(section_id, content)

    if result.get('success'):
        flash(f"Section saved! Score: {result['score']}/100. {result['feedback']}")
    else:
        flash('Failed to save section')

    return redirect(request.referrer or url_for('finance.pitch'))


@finance_bp.route('/pitch/<int:deck_id>/present/<int:investor_id>')
@login_required
def present_pitch(deck_id, investor_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    from src.game_engine import start_pitch_session, get_pitch_deck

    deck = get_pitch_deck(deck_id)
    if not deck or deck['player_id'] != player_id:
        flash('Pitch deck not found')
        return redirect(url_for('finance.pitch'))

    result = start_pitch_session(player_id, deck_id, investor_id)

    if not result.get('success'):
        flash(result.get('error', 'Failed to start pitch session'))
        return redirect(url_for('finance.pitch'))

    return render_template('finance/pitch_present.html',
                          stats=stats,
                          deck=deck,
                          investor=result['investor'],
                          questions=result['questions'],
                          session_id=result['session_id'])


@finance_bp.route('/pitch/session/<int:session_id>/submit', methods=['POST'])
@login_required
def submit_pitch(session_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    answers = []
    i = 0
    while True:
        answer = request.form.get(f'answer_{i}')
        if answer is None:
            break
        answers.append(answer)
        i += 1

    from src.game_engine import submit_pitch_answers
    result = submit_pitch_answers(session_id, answers)

    if result.get('success'):
        flash(f"{result['message']} +{result['exp_earned']} EXP earned!")
    else:
        flash(result.get('error', 'Pitch session failed'))

    return redirect(url_for('finance.pitch'))


@finance_bp.route('/analytics')
@login_required
def analytics():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    from src.game_engine import get_player_analytics, get_player_skill_chart_data

    analytics_data = get_player_analytics(player_id)
    chart_data = get_player_skill_chart_data(player_id)

    return render_template('finance/analytics.html',
                          stats=stats,
                          analytics=analytics_data,
                          chart_data=chart_data)


@finance_bp.route('/learning-paths')
@login_required
def learning_paths_list():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    discipline = request.args.get('discipline')

    from src.game_engine import get_learning_paths
    paths = get_learning_paths(player_id, discipline)

    return render_template('finance/learning_paths.html', stats=stats, paths=paths, filter_discipline=discipline)


@finance_bp.route('/learning-paths/<int:path_id>')
@login_required
def learning_path_detail(path_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    from src.game_engine import get_learning_path_by_id
    path = get_learning_path_by_id(path_id, player_id)

    if not path:
        flash('Learning path not found!')
        return redirect(url_for('finance.learning_paths_list'))

    return render_template('finance/learning_path_detail.html', stats=stats, path=path)


@finance_bp.route('/learning-paths/<int:path_id>/claim-bonus', methods=['POST'])
@login_required
def claim_path_bonus(path_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    from src.game_engine import claim_learning_path_bonus
    result = claim_learning_path_bonus(player_id, path_id)

    if result.get('error'):
        flash(result['error'])
    else:
        flash(f"Claimed +{result['gold_earned']} gold and +{result['exp_earned']} XP!")

    return redirect(url_for('finance.learning_path_detail', path_id=path_id))


@finance_bp.route('/simulations')
@login_required
@feature_gated('simulations')
def simulations():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    from src.game_engine import get_advanced_simulations

    level = stats.get('overall_level', 1) if isinstance(stats, dict) else 1
    sims = get_advanced_simulations(level)

    ma_sims = [s for s in sims if s['simulation_type'] == 'ma']
    intl_sims = [s for s in sims if s['simulation_type'] == 'international']
    crisis_sims = [s for s in sims if s['simulation_type'] == 'crisis']

    return render_template('finance/simulations.html',
                          stats=stats,
                          ma_simulations=ma_sims,
                          international_simulations=intl_sims,
                          crisis_simulations=crisis_sims)


@finance_bp.route('/simulations/<int:simulation_id>')
@login_required
def simulation_detail(simulation_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    from src.game_engine import get_simulation
    sim = get_simulation(simulation_id)

    if not sim:
        flash('Simulation not found')
        return redirect(url_for('finance.simulations'))

    return render_template('finance/simulation_detail.html',
                          stats=stats,
                          simulation=sim)


@finance_bp.route('/simulations/<int:simulation_id>/start', methods=['POST'])
@login_required
def start_simulation(simulation_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    from src.game_engine import start_simulation as do_start
    result = do_start(player_id, simulation_id)

    if result.get('success'):
        flash('Simulation started!')
        return redirect(url_for('finance.simulation_play', progress_id=result['progress_id']))
    else:
        flash('Failed to start simulation')
        return redirect(url_for('finance.simulations'))


@finance_bp.route('/simulations/play/<int:progress_id>')
@login_required
def simulation_play(progress_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    return render_template('finance/simulation_play.html',
                          stats=stats,
                          progress_id=progress_id)


@finance_bp.route('/trials')
@login_required
def mentor_trials_list():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    from src.game_engine import get_all_mentor_trials
    trials = get_all_mentor_trials(player_id)

    return render_template('finance/mentor_trials.html', stats=stats, trials=trials)


@finance_bp.route('/trials/<int:trial_id>')
@login_required
def mentor_trial(trial_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    path_id = request.args.get('path_id', type=int)

    from src.game_engine import get_mentor_trial, start_mentor_trial
    trial = get_mentor_trial(trial_id)

    if not trial:
        flash('Trial not found!')
        return redirect(url_for('finance.mentor_trials_list'))

    start_mentor_trial(player_id, trial_id)

    return render_template('finance/mentor_trial_play.html', stats=stats, trial=trial, path_id=path_id)


@finance_bp.route('/trials/<int:trial_id>/submit', methods=['POST'])
@login_required
def submit_mentor_trial(trial_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    from src.game_engine import get_mentor_trial, complete_mentor_trial

    path_id = request.form.get('path_id', type=int)

    trial = get_mentor_trial(trial_id)
    if not trial:
        flash('Trial not found!')
        return redirect(url_for('finance.mentor_trials_list'))

    score = 0
    max_score = 0
    results = []

    for q in trial['questions']:
        answer = request.form.get(f'q_{q["question_id"]}')
        is_correct = answer and answer.upper() == q['correct_answer'].upper()
        points = q['points'] if is_correct else 0
        score += points
        max_score += q['points']
        results.append({
            'question': q['question_text'],
            'your_answer': answer,
            'correct_answer': q['correct_answer'],
            'is_correct': is_correct,
            'explanation': q['explanation'],
            'points': points
        })

    percentage = (score / max_score * 100) if max_score > 0 else 0
    is_passed = percentage >= trial['passing_score']

    rewards = complete_mentor_trial(player_id, trial_id, score, max_score, is_passed)

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    return render_template('finance/mentor_trial_result.html',
                          stats=stats,
                          trial=trial,
                          results=results,
                          score=score,
                          max_score=max_score,
                          percentage=percentage,
                          is_passed=is_passed,
                          rewards=rewards,
                          path_id=path_id)


@finance_bp.route('/puzzles')
@login_required
def merchant_puzzles_list():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    from src.game_engine import get_all_merchant_puzzles
    puzzles = get_all_merchant_puzzles(player_id)

    return render_template('finance/merchant_puzzles.html', stats=stats, puzzles=puzzles)


@finance_bp.route('/puzzles/<int:puzzle_id>')
@login_required
def merchant_puzzle(puzzle_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    path_id = request.args.get('path_id', type=int)

    from src.game_engine import get_merchant_puzzle, start_merchant_puzzle
    puzzle = get_merchant_puzzle(puzzle_id)

    if not puzzle:
        flash('Puzzle not found!')
        return redirect(url_for('finance.merchant_puzzles_list'))

    start_merchant_puzzle(player_id, puzzle_id)

    return render_template('finance/merchant_puzzle_play.html', stats=stats, puzzle=puzzle, path_id=path_id)


@finance_bp.route('/puzzles/<int:puzzle_id>/submit', methods=['POST'])
@login_required
def submit_merchant_puzzle(puzzle_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    from src.game_engine import get_merchant_puzzle, complete_merchant_puzzle

    path_id = request.form.get('path_id', type=int)

    puzzle = get_merchant_puzzle(puzzle_id)
    if not puzzle:
        flash('Puzzle not found!')
        return redirect(url_for('finance.merchant_puzzles_list'))

    answer = request.form.get('answer', '')
    time_seconds = int(request.form.get('time_seconds', 0))

    try:
        player_answer = float(answer)
    except (ValueError, TypeError):
        player_answer = None

    challenge = puzzle.get('challenge_data', {})
    correct_answer = challenge.get('correct_margin') or challenge.get('correct_breakeven') or challenge.get('correct_roi') or challenge.get('correct_price') or challenge.get('correct_rate')
    tolerance = challenge.get('tolerance', 0)

    is_correct = player_answer is not None and abs(player_answer - correct_answer) <= tolerance

    rewards = complete_merchant_puzzle(player_id, puzzle_id, time_seconds, is_correct)

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    return render_template('finance/merchant_puzzle_result.html',
                          stats=stats,
                          puzzle=puzzle,
                          player_answer=player_answer,
                          correct_answer=correct_answer,
                          is_correct=is_correct,
                          time_seconds=time_seconds,
                          rewards=rewards,
                          path_id=path_id)
