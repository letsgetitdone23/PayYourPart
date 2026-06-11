from antigravity import Blueprint, request, session, redirect, render_template, url_for, flash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('groups.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash("Email and password are required.", "error")
            return redirect(url_for('auth.login'))
            
        try:
            from app import supabase
            if not supabase:
                raise Exception("Database connection not configured. Please set SUPABASE_URL and SUPABASE_KEY in .env.")
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            # Save session data
            session['user_id'] = response.user.id
            session['access_token'] = response.session.access_token
            session['user_email'] = response.user.email
            
            # Retrieve profile name if exists
            try:
                profile_res = supabase.table('profiles').select('name').eq('id', response.user.id).execute()
                if profile_res.data:
                    session['user_name'] = profile_res.data[0]['name']
                else:
                    session['user_name'] = response.user.email.split('@')[0]
            except Exception:
                session['user_name'] = response.user.email.split('@')[0]
                
            return redirect(url_for('groups.dashboard'))
        except Exception as e:
            # Clean up error message for display
            err_msg = str(e)
            if "invalid_credentials" in err_msg or "Invalid login credentials" in err_msg:
                err_msg = "Invalid email or password."
            flash(err_msg, "error")
            return redirect(url_for('auth.login'))
            
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('groups.dashboard'))

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not name or not email or not password:
            flash("All fields are required.", "error")
            return redirect(url_for('auth.register'))
            
        try:
            from app import supabase
            if not supabase:
                raise Exception("Database connection not configured. Please set SUPABASE_URL and SUPABASE_KEY in .env.")
            # Sign up in Supabase Auth
            auth_response = supabase.auth.sign_up({
                "email": email,
                "password": password
            })
            
            if not auth_response.user:
                raise Exception("Sign up failed: User creation failed.")
                
            user_id = auth_response.user.id
            
            # Create the public profile in profiles table
            profile_data = {
                "id": user_id,
                "name": name,
                "email": email
            }
            supabase.table('profiles').insert(profile_data).execute()
            
            flash("Account created successfully! Please login.", "success")
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(str(e), "error")
            return redirect(url_for('auth.register'))
            
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    try:
        from app import supabase
        if supabase:
            supabase.auth.sign_out()
    except Exception:
        pass
    session.clear()
    return redirect(url_for('auth.login'))

@auth_bp.route('/login/register')
def redirect_to_register():
    return redirect(url_for('auth.register'))

@auth_bp.route('/login/login')
def redirect_to_login():
    return redirect(url_for('auth.login'))
