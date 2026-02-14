from flask import Blueprint, render_template, redirect, url_for, session, flash
from src.routes.helpers import login_required, feature_gated, get_engine

inventory_bp = Blueprint('inventory', __name__)


@inventory_bp.route('/shop')
@login_required
def shop():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    items = get_engine().get_shop_items()

    return render_template('inventory/shop.html', stats=stats, items=items)


@inventory_bp.route('/buy/<int:item_id>', methods=['POST'])
@login_required
def buy_item(item_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    result = get_engine().purchase_item(item_id)

    if result.get('error'):
        flash(result['error'])
    else:
        flash(f"Purchased {result['item']['item_name']}!")

    return redirect(url_for('inventory.shop'))


@inventory_bp.route('/inventory')
@login_required
def inventory():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()

    return render_template('inventory/inventory.html', stats=stats)


@inventory_bp.route('/equipment')
@login_required
def equipment():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    equipment_data = get_engine().get_equipment()

    return render_template('inventory/equipment.html', stats=stats, equipment_data=equipment_data)


@inventory_bp.route('/purchase_equipment/<int:equipment_id>', methods=['POST'])
@login_required
def purchase_equipment(equipment_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    result = get_engine().purchase_equipment(equipment_id)

    if result.get('error'):
        flash(result['error'])
    else:
        flash(f"Purchased {result['equipment_name']}!")

    return redirect(url_for('inventory.equipment'))


@inventory_bp.route('/equip_item/<int:equipment_id>', methods=['POST'])
@login_required
def equip_item(equipment_id):
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    result = get_engine().equip_item(equipment_id)

    if result.get('error'):
        flash(result['error'])
    else:
        flash(f"Equipped {result['equipped']} to {result['slot']} slot!")

    return redirect(url_for('inventory.equipment'))


@inventory_bp.route('/prestige')
@login_required
@feature_gated('prestige')
def prestige():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    stats = get_engine().get_player_stats()
    prestige_status = get_engine().get_prestige_status()

    return render_template('inventory/prestige.html', stats=stats, prestige_status=prestige_status)


@inventory_bp.route('/perform_prestige', methods=['POST'])
@login_required
def perform_prestige():
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('auth.index'))

    get_engine().load_player(player_id)
    result = get_engine().perform_prestige()

    if result.get('error'):
        flash(result['error'])
    else:
        flash(f"Prestige complete! Now at Prestige Level {result['new_prestige_level']}. EXP x{result['new_exp_multiplier']:.1f}, Gold x{result['new_gold_multiplier']:.2f}")

    return redirect(url_for('core.hub'))
