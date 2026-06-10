from antigravity import Blueprint, request, session, redirect, render_template, url_for, flash
from middleware.auth_guard import require_login
from services.split_calculator import calculate_splits

expenses_bp = Blueprint('expenses', __name__)

@expenses_bp.route('/groups/<id>/expenses')
@require_login
def expense_list(id):
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
        
        # 3. Fetch expenses for this group
        expenses_res = supabase.table('expenses').select('*, profiles(name)').eq('group_id', id).order('created_at', desc=True).execute()
        expenses = []
        for e in expenses_res.data:
            payer_name = e.get('profiles', {}).get('name', 'Unknown') if e.get('profiles') else 'Unknown'
            expenses.append({
                "id": e["id"],
                "title": e["title"],
                "amount": float(e["amount"]),
                "split_type": e["split_type"],
                "category": e["category"],
                "created_at": e["created_at"],
                "paid_by_name": payer_name
            })
            
        return render_template('expense_list.html', group=group, expenses=expenses)
    except Exception as e:
        flash(f"Error loading expenses: {str(e)}", "error")
        return redirect(url_for('groups.group_detail', id=id))

@expenses_bp.route('/expenses/add')
@require_login
def add_expense_form():
    from app import supabase
    if not supabase:
        flash("Database connection not configured.", "error")
        return redirect(url_for('auth.login'))
        
    group_id = request.args.get('group_id')
    user_id = session.get('user_id')
    
    if not group_id:
        flash("Group ID is required.", "error")
        return redirect(url_for('groups.dashboard'))
        
    try:
        # Verify membership
        membership_res = supabase.table('group_members').select('*').eq('group_id', group_id).eq('user_id', user_id).execute()
        if not membership_res.data:
            flash("You do not have access to this group.", "error")
            return redirect(url_for('groups.dashboard'))
            
        # Fetch members profiles
        members_res = supabase.table('group_members').select('user_id, profiles(id, name, email)').eq('group_id', group_id).execute()
        members = []
        for m in members_res.data:
            prof = m.get('profiles')
            if prof:
                members.append({
                    "id": prof["id"],
                    "name": prof["name"],
                    "email": prof["email"]
                })
                
        return render_template('add_expense.html', group_id=group_id, members=members, expense=None, splits={})
    except Exception as e:
        flash(f"Error loading form: {str(e)}", "error")
        return redirect(url_for('groups.dashboard'))

@expenses_bp.route('/expenses/add', methods=['POST'])
@require_login
def add_expense():
    from app import supabase
    if not supabase:
        return redirect(url_for('auth.login'))
        
    group_id = request.form.get('group_id')
    title = request.form.get('title')
    amount_str = request.form.get('amount')
    category = request.form.get('category', 'other')
    paid_by = request.form.get('paid_by')
    split_type = request.form.get('split_type', 'equal')
    user_id = session.get('user_id')
    
    if not group_id or not title or not amount_str or not paid_by:
        flash("All fields are required.", "error")
        return redirect(request.referrer or url_for('groups.dashboard'))
        
    try:
        amount = float(amount_str)
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")
            
        # Verify membership
        membership_res = supabase.table('group_members').select('*').eq('group_id', group_id).eq('user_id', user_id).execute()
        if not membership_res.data:
            flash("Access denied.", "error")
            return redirect(url_for('groups.dashboard'))
            
        # Fetch group members
        members_res = supabase.table('group_members').select('user_id').eq('group_id', group_id).execute()
        members = [m['user_id'] for m in members_res.data]
        
        # Read overrides from form
        overrides = {}
        if split_type in ['exact', 'percentage']:
            for m_id in members:
                val = request.form.get(f'split_{m_id}', '0')
                overrides[m_id] = float(val) if val else 0.0
                
        # Calculate splits
        calculated_splits = calculate_splits(members, amount, split_type, overrides)
        
        # Insert expense
        expense_data = {
            "group_id": group_id,
            "paid_by": paid_by,
            "title": title,
            "amount": amount,
            "split_type": split_type,
            "category": category
        }
        ins_res = supabase.table('expenses').insert(expense_data).execute()
        if not ins_res.data:
            raise Exception("Failed to save expense.")
        expense_id = ins_res.data[0]['id']
        
        # Bulk-insert splits
        splits_to_insert = []
        for s in calculated_splits:
            splits_to_insert.append({
                "expense_id": expense_id,
                "user_id": s["user_id"],
                "amount_owed": s["amount_owed"]
            })
        supabase.table('expense_splits').insert(splits_to_insert).execute()
        
        flash("Expense added successfully!", "success")
        return redirect(url_for('expenses.expense_list', id=group_id))
    except ValueError as ve:
        flash(str(ve), "error")
        return redirect(url_for('expenses.add_expense_form', group_id=group_id))
    except Exception as e:
        flash(f"Error adding expense: {str(e)}", "error")
        return redirect(url_for('expenses.add_expense_form', group_id=group_id))

@expenses_bp.route('/expenses/<id>')
@require_login
def expense_detail(id):
    from app import supabase
    if not supabase:
        return redirect(url_for('auth.login'))
        
    user_id = session.get('user_id')
    
    try:
        # 1. Fetch expense with payer details
        expense_res = supabase.table('expenses').select('*, profiles(name)').eq('id', id).execute()
        if not expense_res.data:
            flash("Expense not found.", "error")
            return redirect(url_for('groups.dashboard'))
        expense = expense_res.data[0]
        group_id = expense['group_id']
        
        # 2. Verify membership
        membership_res = supabase.table('group_members').select('*').eq('group_id', group_id).eq('user_id', user_id).execute()
        if not membership_res.data:
            flash("Access denied.", "error")
            return redirect(url_for('groups.dashboard'))
            
        # 3. Fetch splits
        splits_res = supabase.table('expense_splits').select('*, profiles(name, email)').eq('expense_id', id).execute()
        
        splits = []
        for s in splits_res.data:
            name = s.get('profiles', {}).get('name', 'Unknown') if s.get('profiles') else 'Unknown'
            email = s.get('profiles', {}).get('email', '') if s.get('profiles') else ''
            splits.append({
                "user_id": s["user_id"],
                "name": name,
                "email": email,
                "amount_owed": float(s["amount_owed"])
            })
            
        payer_name = expense.get('profiles', {}).get('name', 'Unknown') if expense.get('profiles') else 'Unknown'
        expense_info = {
            "id": expense["id"],
            "group_id": group_id,
            "title": expense["title"],
            "amount": float(expense["amount"]),
            "category": expense["category"],
            "split_type": expense["split_type"],
            "paid_by": expense["paid_by"],
            "paid_by_name": payer_name,
            "created_at": expense["created_at"]
        }
        
        return render_template('expense_detail.html', expense=expense_info, splits=splits)
    except Exception as e:
        flash(f"Error loading expense details: {str(e)}", "error")
        return redirect(url_for('groups.dashboard'))

@expenses_bp.route('/expenses/<id>/edit')
@require_login
def edit_expense_form(id):
    from app import supabase
    if not supabase:
        return redirect(url_for('auth.login'))
        
    user_id = session.get('user_id')
    
    try:
        # Fetch expense
        expense_res = supabase.table('expenses').select('*').eq('id', id).execute()
        if not expense_res.data:
            flash("Expense not found.", "error")
            return redirect(url_for('groups.dashboard'))
        expense = expense_res.data[0]
        group_id = expense['group_id']
        
        # Verify membership
        membership_res = supabase.table('group_members').select('*').eq('group_id', group_id).eq('user_id', user_id).execute()
        if not membership_res.data:
            flash("Access denied.", "error")
            return redirect(url_for('groups.dashboard'))
            
        # Fetch group members
        members_res = supabase.table('group_members').select('user_id, profiles(id, name, email)').eq('group_id', group_id).execute()
        members = []
        for m in members_res.data:
            prof = m.get('profiles')
            if prof:
                members.append({
                    "id": prof["id"],
                    "name": prof["name"],
                    "email": prof["email"]
                })
                
        # Fetch splits
        splits_res = supabase.table('expense_splits').select('*').eq('expense_id', id).execute()
        splits_dict = {}
        for s in splits_res.data:
            # We want exact value or percentage based on type
            if expense['split_type'] == 'percentage':
                # Re-calculate pct: (owed / total) * 100
                total_amt = float(expense['amount'])
                owed = float(s['amount_owed'])
                pct = round((owed / total_amt) * 100, 2) if total_amt > 0 else 0
                splits_dict[s['user_id']] = pct
            else:
                splits_dict[s['user_id']] = float(s['amount_owed'])
                
        expense_info = {
            "id": expense["id"],
            "group_id": group_id,
            "title": expense["title"],
            "amount": float(expense["amount"]),
            "category": expense["category"],
            "split_type": expense["split_type"],
            "paid_by": expense["paid_by"]
        }
        
        return render_template('add_expense.html', group_id=group_id, members=members, expense=expense_info, splits=splits_dict)
    except Exception as e:
        flash(f"Error loading edit form: {str(e)}", "error")
        return redirect(url_for('groups.dashboard'))

@expenses_bp.route('/expenses/<id>/edit', methods=['POST'])
@require_login
def edit_expense(id):
    from app import supabase
    if not supabase:
        return redirect(url_for('auth.login'))
        
    user_id = session.get('user_id')
    title = request.form.get('title')
    amount_str = request.form.get('amount')
    category = request.form.get('category', 'other')
    paid_by = request.form.get('paid_by')
    split_type = request.form.get('split_type', 'equal')
    
    try:
        amount = float(amount_str)
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")
            
        # Fetch expense to check group membership
        expense_res = supabase.table('expenses').select('*').eq('id', id).execute()
        if not expense_res.data:
            flash("Expense not found.", "error")
            return redirect(url_for('groups.dashboard'))
        expense = expense_res.data[0]
        group_id = expense['group_id']
        
        # Verify membership
        membership_res = supabase.table('group_members').select('*').eq('group_id', group_id).eq('user_id', user_id).execute()
        if not membership_res.data:
            flash("Access denied.", "error")
            return redirect(url_for('groups.dashboard'))
            
        # Fetch group members
        members_res = supabase.table('group_members').select('user_id').eq('group_id', group_id).execute()
        members = [m['user_id'] for m in members_res.data]
        
        # Read overrides from form
        overrides = {}
        if split_type in ['exact', 'percentage']:
            for m_id in members:
                val = request.form.get(f'split_{m_id}', '0')
                overrides[m_id] = float(val) if val else 0.0
                
        # Calculate new splits
        calculated_splits = calculate_splits(members, amount, split_type, overrides)
        
        # Update expense row
        update_data = {
            "paid_by": paid_by,
            "title": title,
            "amount": amount,
            "split_type": split_type,
            "category": category
        }
        supabase.table('expenses').update(update_data).eq('id', id).execute()
        
        # Delete old splits
        supabase.table('expense_splits').delete().eq('expense_id', id).execute()
        
        # Insert new splits
        splits_to_insert = []
        for s in calculated_splits:
            splits_to_insert.append({
                "expense_id": id,
                "user_id": s["user_id"],
                "amount_owed": s["amount_owed"]
            })
        supabase.table('expense_splits').insert(splits_to_insert).execute()
        
        flash("Expense updated successfully!", "success")
        return redirect(url_for('expenses.expense_detail', id=id))
    except ValueError as ve:
        flash(str(ve), "error")
        return redirect(url_for('expenses.edit_expense_form', id=id))
    except Exception as e:
        flash(f"Error updating expense: {str(e)}", "error")
        return redirect(url_for('expenses.edit_expense_form', id=id))

@expenses_bp.route('/expenses/<id>/delete', methods=['POST'])
@require_login
def delete_expense(id):
    from app import supabase
    if not supabase:
        return redirect(url_for('auth.login'))
        
    user_id = session.get('user_id')
    
    try:
        # Fetch expense to check group ID
        expense_res = supabase.table('expenses').select('*').eq('id', id).execute()
        if not expense_res.data:
            flash("Expense not found.", "error")
            return redirect(url_for('groups.dashboard'))
        expense = expense_res.data[0]
        group_id = expense['group_id']
        
        # Verify membership
        membership_res = supabase.table('group_members').select('*').eq('group_id', group_id).eq('user_id', user_id).execute()
        if not membership_res.data:
            flash("Access denied.", "error")
            return redirect(url_for('groups.dashboard'))
            
        # Delete expense row (cascades splits)
        supabase.table('expenses').delete().eq('id', id).execute()
        
        flash("Expense deleted.", "success")
        return redirect(url_for('expenses.expense_list', id=group_id))
    except Exception as e:
        flash(f"Failed to delete expense: {str(e)}", "error")
        return redirect(url_for('expenses.expense_detail', id=id))

@expenses_bp.route('/groups/<id>/export')
@require_login
def export_expenses(id):
    from app import supabase
    from antigravity import make_response
    import csv
    from io import StringIO
    
    if not supabase:
        flash("Database connection not configured.", "error")
        return redirect(url_for('auth.login'))
        
    user_id = session.get('user_id')
    
    try:
        # 1. Verify membership
        membership_res = supabase.table('group_members').select('*').eq('group_id', id).eq('user_id', user_id).execute()
        if not membership_res.data:
            flash("You do not have access to this group.", "error")
            return redirect(url_for('groups.dashboard'))
            
        # 2. Fetch group details
        group_res = supabase.table('groups').select('name').eq('id', id).execute()
        if not group_res.data:
            flash("Group not found.", "error")
            return redirect(url_for('groups.dashboard'))
        group_name = group_res.data[0]['name']
        
        # 3. Fetch expenses with splits and payer profiles
        expenses_res = supabase.table('expenses').select('*, expense_splits(*), profiles(name)').eq('group_id', id).order('created_at', desc=True).execute()
        
        # 4. Generate CSV
        csv_data = StringIO()
        writer = csv.writer(csv_data)
        writer.writerow(["Date", "Title", "Paid By", "Total Amount", "Your Share"])
        
        for e in expenses_res.data:
            date = e['created_at'].split('T')[0]
            title = e['title']
            paid_by_name = e.get('profiles', {}).get('name', 'Unknown') if e.get('profiles') else 'Unknown'
            total_amount = float(e['amount'])
            
            # Find current user's share from splits
            your_share = 0.0
            for s in e['expense_splits']:
                if s['user_id'] == user_id:
                    your_share = float(s['amount_owed'])
                    break
            
            writer.writerow([date, title, paid_by_name, f"{total_amount:.2f}", f"{your_share:.2f}"])
            
        output = csv_data.getvalue()
        response = make_response(output)
        
        # Clean group name for safe filename
        safe_name = "".join(c for c in group_name if c.isalnum() or c in (' ', '_', '-')).strip().replace(' ', '_')
        
        response.headers["Content-Disposition"] = f'attachment; filename="payyourpart-{safe_name}.csv"'
        response.headers["Content-Type"] = "text/csv"
        return response
        
    except Exception as e:
        flash(f"Failed to export CSV: {str(e)}", "error")
        return redirect(url_for('expenses.expense_list', id=id))
