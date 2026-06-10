from antigravity import Blueprint, request, session, redirect, render_template, url_for, flash
from middleware.auth_guard import require_login

groups_bp = Blueprint('groups', __name__)

@groups_bp.route('/dashboard')
@require_login
def dashboard():
    from app import supabase
    if not supabase:
        flash("Database connection not configured. Please set SUPABASE_URL and SUPABASE_KEY in .env.", "error")
        return redirect(url_for('auth.login'))
        
    try:
        user_id = session.get('user_id')
        
        # Query the groups the user belongs to
        memberships_res = supabase.table('group_members').select('group_id').eq('user_id', user_id).execute()
        group_ids = [m['group_id'] for m in memberships_res.data]
        
        groups = []
        if group_ids:
            # Query group details
            groups_res = supabase.table('groups').select('*').in_('id', group_ids).execute()
            groups = groups_res.data
            
            # Query member counts for all matching groups
            members_res = supabase.table('group_members').select('group_id').in_('group_id', group_ids).execute()
            
            # Count the occurrences of each group_id
            counts = {}
            for m in members_res.data:
                g_id = m['group_id']
                counts[g_id] = counts.get(g_id, 0) + 1
                
            from services.balance_engine import get_group_balances
            for g in groups:
                g['member_count'] = counts.get(g['id'], 0)
                balances = get_group_balances(g['id'])
                g['net_balance'] = balances.get(user_id, 0.0)
                
        return render_template('dashboard.html', groups=groups)
    except Exception as e:
        flash(f"Error loading dashboard: {str(e)}", "error")
        return render_template('dashboard.html', groups=[])

@groups_bp.route('/groups/create', methods=['POST'])
@require_login
def create_group():
    from app import supabase
    if not supabase:
        flash("Database connection not configured. Please set SUPABASE_URL and SUPABASE_KEY in .env.", "error")
        return redirect(url_for('auth.login'))
        
    name = request.form.get('name')
    description = request.form.get('description', '')
    user_id = session.get('user_id')
    
    if not name:
        flash("Group name is required.", "error")
        return redirect(url_for('groups.dashboard'))
        
    try:
        # 1. Insert the group
        group_data = {
            "name": name,
            "description": description,
            "created_by": user_id
        }
        group_res = supabase.table('groups').insert(group_data).execute()
        
        if not group_res.data:
            raise Exception("Failed to create group record.")
            
        group_id = group_res.data[0]['id']
        
        # 2. Add the creator as admin member
        member_data = {
            "group_id": group_id,
            "user_id": user_id,
            "role": "admin"
        }
        supabase.table('group_members').insert(member_data).execute()
        
        flash(f"Group '{name}' created successfully!", "success")
        return redirect(url_for('groups.group_detail', id=group_id))
    except Exception as e:
        flash(f"Failed to create group: {str(e)}", "error")
        return redirect(url_for('groups.dashboard'))

@groups_bp.route('/groups/<id>')
@require_login
def group_detail(id):
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
        
        # 3. Fetch all members with their profile details
        members_res = supabase.table('group_members').select('role, user_id, profiles(id, name, email)').eq('group_id', id).execute()
        
        members = []
        user_role = 'member'
        for m in members_res.data:
            # Determine logged-in user's role in this group
            if m['user_id'] == user_id:
                user_role = m['role']
                
            prof = m.get('profiles')
            if prof:
                members.append({
                    "user_id": prof.get('id'),
                    "name": prof.get('name'),
                    "email": prof.get('email'),
                    "role": m.get('role')
                })
                
        # 4. Fetch 3 most recent expenses
        expenses_res = supabase.table('expenses').select('*, profiles(name)').eq('group_id', id).order('created_at', desc=True).limit(3).execute()
        recent_expenses = []
        for e in expenses_res.data:
            payer_name = e.get('profiles', {}).get('name', 'Unknown') if e.get('profiles') else 'Unknown'
            recent_expenses.append({
                "id": e["id"],
                "title": e["title"],
                "amount": float(e["amount"]),
                "split_type": e["split_type"],
                "category": e["category"],
                "created_at": e["created_at"],
                "paid_by_name": payer_name
            })
            
        from app import supabase_url, supabase_key
        return render_template('group_detail.html', group=group, members=members, user_role=user_role, recent_expenses=recent_expenses, supabase_url=supabase_url, supabase_key=supabase_key)
    except Exception as e:
        flash(f"Error loading group: {str(e)}", "error")
        return redirect(url_for('groups.dashboard'))

@groups_bp.route('/groups/<id>/invite', methods=['POST'])
@require_login
def invite_member(id):
    from app import supabase
    if not supabase:
        flash("Database connection not configured. Please set SUPABASE_URL and SUPABASE_KEY in .env.", "error")
        return redirect(url_for('auth.login'))
        
    email = request.form.get('email', '').strip()
    user_id = session.get('user_id')
    
    if not email:
        flash("Email is required.", "error")
        return redirect(url_for('groups.group_detail', id=id))
        
    try:
        # 1. Verify current user is in group
        membership_res = supabase.table('group_members').select('*').eq('group_id', id).eq('user_id', user_id).execute()
        if not membership_res.data:
            flash("Unauthorized access.", "error")
            return redirect(url_for('groups.dashboard'))
            
        # 2. Look up the profile by email
        profile_res = supabase.table('profiles').select('*').eq('email', email).execute()
        if not profile_res.data:
            flash(f"User with email '{email}' has not registered on PayYourPart yet.", "error")
            return redirect(url_for('groups.group_detail', id=id))
            
        invitee = profile_res.data[0]
        invitee_id = invitee['id']
        
        # 3. Check if invitee is already in group
        existing_res = supabase.table('group_members').select('*').eq('group_id', id).eq('user_id', invitee_id).execute()
        if existing_res.data:
            flash(f"{invitee['name']} is already a member of this group.", "error")
            return redirect(url_for('groups.group_detail', id=id))
            
        # 4. Insert into group_members
        supabase.table('group_members').insert({
            "group_id": id,
            "user_id": invitee_id,
            "role": "member"
        }).execute()
        
        flash(f"Successfully added {invitee['name']} to the group!", "success")
        return redirect(url_for('groups.group_detail', id=id))
    except Exception as e:
        flash(f"Failed to invite member: {str(e)}", "error")
        return redirect(url_for('groups.group_detail', id=id))

@groups_bp.route('/groups/<id>/leave', methods=['POST'])
@require_login
def leave_group(id):
    from app import supabase
    if not supabase:
        flash("Database connection not configured. Please set SUPABASE_URL and SUPABASE_KEY in .env.", "error")
        return redirect(url_for('auth.login'))
        
    user_id = session.get('user_id')
    
    try:
        # 1. Check if user is in group
        membership_res = supabase.table('group_members').select('*').eq('group_id', id).eq('user_id', user_id).execute()
        if not membership_res.data:
            flash("You are not a member of this group.", "error")
            return redirect(url_for('groups.dashboard'))
            
        # 2. Delete member record
        supabase.table('group_members').delete().eq('group_id', id).eq('user_id', user_id).execute()
        
        flash("You have left the group.", "success")
        return redirect(url_for('groups.dashboard'))
    except Exception as e:
        flash(f"Failed to leave group: {str(e)}", "error")
        return redirect(url_for('groups.group_detail', id=id))

@groups_bp.route('/groups/<id>/balances-json')
@require_login
def balances_json(id):
    from app import supabase
    from services.balance_engine import get_group_balances
    from antigravity import jsonify
    
    if not supabase:
        return jsonify({"error": "Database not configured"}), 500
        
    user_id = session.get('user_id')
    try:
        # 1. Verify membership
        membership_res = supabase.table('group_members').select('*').eq('group_id', id).eq('user_id', user_id).execute()
        if not membership_res.data:
            return jsonify({"error": "Access denied"}), 403
            
        # 2. Get balances
        balances = get_group_balances(id)
        
        # 3. Get profiles
        members_res = supabase.table('group_members').select('user_id, profiles(name)').eq('group_id', id).execute()
        names = {m['user_id']: m['profiles']['name'] for m in members_res.data if m.get('profiles')}
        
        data = []
        for uid, bal in balances.items():
            data.append({
                "user_id": uid,
                "name": names.get(uid, "Unknown"),
                "balance": bal
            })
            
        return jsonify({"balances": data, "currentUser": user_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@groups_bp.route('/groups/<id>/activity')
@require_login
def group_activity(id):
    from app import supabase
    
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
        group_res = supabase.table('groups').select('*').eq('id', id).execute()
        if not group_res.data:
            flash("Group not found.", "error")
            return redirect(url_for('groups.dashboard'))
        group = group_res.data[0]
        
        # 3. Fetch all profile names in this group
        members_res = supabase.table('group_members').select('user_id, profiles(name)').eq('group_id', id).execute()
        names = {m['user_id']: m['profiles']['name'] for m in members_res.data if m.get('profiles')}
        
        # 4. Fetch expenses
        expenses_res = supabase.table('expenses').select('*').eq('group_id', id).execute()
        
        # 5. Fetch settlements
        settlements_res = supabase.table('settlements').select('*').eq('group_id', id).execute()
        
        # 6. Merge and format activity items
        activities = []
        
        # Format time helper
        from datetime import datetime, timezone
        import dateutil.parser
        
        def format_time_ago(dt_str):
            try:
                dt = dateutil.parser.isoparse(dt_str)
                now = datetime.now(timezone.utc)
                diff = now - dt
                seconds = diff.total_seconds()
                if seconds < 0:
                    return "just now"
                if seconds < 60:
                    return "just now"
                minutes = seconds / 60
                if minutes < 60:
                    return f"{int(minutes)}m ago"
                hours = minutes / 60
                if hours < 24:
                    return f"{int(hours)}h ago"
                days = hours / 24
                if days < 7:
                    return f"{int(days)}d ago"
                return dt_str.split('T')[0]
            except Exception:
                return dt_str.split('T')[0]
                
        for e in expenses_res.data:
            activities.append({
                "type": "expense",
                "title": e["title"],
                "paid_by_name": names.get(e["paid_by"], "Unknown"),
                "amount": float(e["amount"]),
                "created_at": e["created_at"],
                "time_ago": format_time_ago(e["created_at"]),
                "category": e["category"]
            })
            
        for s in settlements_res.data:
            activities.append({
                "type": "settlement",
                "paid_by_name": names.get(s["paid_by"], "Unknown"),
                "paid_to_name": names.get(s["paid_to"], "Unknown"),
                "amount": float(s["amount"]),
                "created_at": s["settled_at"],
                "time_ago": format_time_ago(s["settled_at"])
            })
            
        # Sort DESC
        activities.sort(key=lambda x: x["created_at"], reverse=True)
        
        return render_template('activity.html', group=group, activities=activities)
    except Exception as e:
        flash(f"Error loading activity feed: {str(e)}", "error")
        return redirect(url_for('groups.group_detail', id=id))
