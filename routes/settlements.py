from antigravity import Blueprint, request, session, redirect, render_template, url_for, flash
from middleware.auth_guard import require_login
from services.balance_engine import get_group_balances, simplify_debts

settlements_bp = Blueprint('settlements', __name__)

@settlements_bp.route('/groups/<id>/balances')
@require_login
def group_balances(id):
    from app import supabase
    if not supabase:
        flash("Database connection not configured. Please set SUPABASE_URL and SUPABASE_KEY in .env.", "error")
        return redirect(url_for('auth.login'))
        
    user_id = session.get('user_id')
    
    try:
        # 1. Verify membership
        membership_res = supabase.table('group_members').select('*').eq('group_id', id).eq('user_id', user_id).execute()
        if not membership_res.data:
            flash("You do not have access to this group.", "error")
            return redirect(url_for('groups.dashboard'))
            
        # 2. Fetch group details
        group_res = supabase.table('groups').select('*').eq('id', id).execute()
        if not group_res.data:
            flash("Group not found.", "error")
            return redirect(url_for('groups.dashboard'))
        group = group_res.data[0]
        
        # 3. Fetch all group members with profiles
        members_res = supabase.table('group_members').select('user_id, role, profiles(id, name, email)').eq('group_id', id).execute()
        
        # 4. Get net balances
        balances = get_group_balances(id)
        
        members_balances = []
        for m in members_res.data:
            prof = m.get('profiles')
            if prof:
                uid = prof['id']
                net_bal = balances.get(uid, 0.0)
                members_balances.append({
                    "user_id": uid,
                    "name": prof['name'],
                    "email": prof['email'],
                    "role": m['role'],
                    "net_balance": net_bal
                })
                
        # Sort so user comes first, then by balance descending
        members_balances.sort(key=lambda x: (x['user_id'] != user_id, -x['net_balance']))
        
        return render_template('balances.html', group=group, members=members_balances)
    except Exception as e:
        flash(f"Error loading balances: {str(e)}", "error")
        return redirect(url_for('groups.group_detail', id=id))

@settlements_bp.route('/groups/<id>/settle-up')
@require_login
def settle_up_form(id):
    from app import supabase
    if not supabase:
        return redirect(url_for('auth.login'))
        
    user_id = session.get('user_id')
    
    try:
        # 1. Verify membership
        membership_res = supabase.table('group_members').select('*').eq('group_id', id).eq('user_id', user_id).execute()
        if not membership_res.data:
            flash("You do not have access to this group.", "error")
            return redirect(url_for('groups.dashboard'))
            
        # 2. Fetch group details
        group_res = supabase.table('groups').select('*').eq('id', id).execute()
        if not group_res.data:
            flash("Group not found.", "error")
            return redirect(url_for('groups.dashboard'))
        group = group_res.data[0]
        
        # 3. Fetch all group members with profiles
        members_res = supabase.table('group_members').select('user_id, profiles(id, name)').eq('group_id', id).execute()
        
        user_profiles = {}
        for m in members_res.data:
            prof = m.get('profiles')
            if prof:
                user_profiles[prof['id']] = prof['name']
                
        # 4. Get net balances and simplify debts
        balances = get_group_balances(id)
        transactions = simplify_debts(balances, user_profiles)
        
        return render_template('settle_up.html', group=group, transactions=transactions)
    except Exception as e:
        flash(f"Error loading settle up sheet: {str(e)}", "error")
        return redirect(url_for('groups.group_detail', id=id))

@settlements_bp.route('/groups/<id>/settle-up', methods=['POST'])
@require_login
def record_settlement(id):
    from app import supabase
    if not supabase:
        return redirect(url_for('auth.login'))
        
    user_id = session.get('user_id')
    paid_by = request.form.get('paid_by')  # Debtor paying off debt
    paid_to = request.form.get('paid_to')  # Creditor receiving payment
    amount_str = request.form.get('amount')
    
    if not paid_by or not paid_to or not amount_str:
        flash("Invalid settlement data.", "error")
        return redirect(url_for('settlements.settle_up_form', id=id))
        
    try:
        amount = float(amount_str)
        if amount <= 0:
            raise ValueError("Amount must be positive.")
            
        # Verify current user is a member of the group
        membership_res = supabase.table('group_members').select('*').eq('group_id', id).eq('user_id', user_id).execute()
        if not membership_res.data:
            flash("Access denied.", "error")
            return redirect(url_for('groups.dashboard'))
            
        # Verify both debtor and creditor belong to group
        participants_res = supabase.table('group_members').select('user_id').eq('group_id', id).in_('user_id', [paid_by, paid_to]).execute()
        if len(participants_res.data) < 2:
            # If paid_by == paid_to and they are in the group, it would return length 1, but they shouldn't settle to themselves
            raise Exception("Invalid settlement participants.")
            
        # Record settlement
        settlement_data = {
            "group_id": id,
            "paid_by": paid_by,
            "paid_to": paid_to,
            "amount": amount
        }
        supabase.table('settlements').insert(settlement_data).execute()
        
        flash("Settlement recorded successfully!", "success")
        return redirect(url_for('settlements.settle_up_form', id=id))
    except Exception as e:
        flash(f"Failed to record settlement: {str(e)}", "error")
        return redirect(url_for('settlements.settle_up_form', id=id))

@settlements_bp.route('/me/balances')
@require_login
def me_balances():
    from app import supabase
    if not supabase:
        return redirect(url_for('auth.login'))
        
    user_id = session.get('user_id')
    
    try:
        # Fetch user's group memberships with group details
        memberships_res = supabase.table('group_members').select('group_id, groups(id, name, description)').eq('user_id', user_id).execute()
        
        group_balances = []
        global_total = 0.0
        
        for m in memberships_res.data:
            g = m.get('groups')
            if g:
                g_id = g['id']
                balances = get_group_balances(g_id)
                net_bal = balances.get(user_id, 0.0)
                global_total += net_bal
                
                group_balances.append({
                    "id": g_id,
                    "name": g['name'],
                    "description": g['description'],
                    "net_balance": net_bal
                })
                
        return render_template('me_balances.html', groups=group_balances, global_total=global_total)
    except Exception as e:
        flash(f"Error loading your balances: {str(e)}", "error")
        return redirect(url_for('groups.dashboard'))
