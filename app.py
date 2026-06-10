from antigravity import Antigravity, redirect, url_for, session
from dotenv import load_dotenv
from supabase import create_client, Client
import os
from middleware.auth_guard import require_login

# Load environment variables
load_dotenv()

# Initialize Antigravity (Flask) App
app = Antigravity(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_fallback_secret_key_12983712983')

from flask import g
from werkzeug.local import LocalProxy

# Initialize Supabase Client
supabase_url = os.environ.get("SUPABASE_URL", "")
supabase_key = os.environ.get("SUPABASE_KEY", "")

def get_supabase_client():
    if 'supabase_client' not in g:
        client = None
        if supabase_url and supabase_url.startswith("http"):
            try:
                client = create_client(supabase_url, supabase_key)
                if 'access_token' in session:
                    # Authenticate connection for postgrest RLS policies
                    client.postgrest.auth(session['access_token'])
                    client.options.headers["Authorization"] = f"Bearer {session['access_token']}"
            except Exception as e:
                print(f"ERROR: Failed to initialize Supabase client: {e}")
        else:
            print("WARNING: SUPABASE_URL not configured. Supabase operations will fail.")
        g.supabase_client = client
    return g.supabase_client

supabase = LocalProxy(get_supabase_client)


# Register Blueprints
from routes.auth import auth_bp
from routes.groups import groups_bp
from routes.expenses import expenses_bp
from routes.settlements import settlements_bp
app.register_blueprint(auth_bp)
app.register_blueprint(groups_bp)
app.register_blueprint(expenses_bp)
app.register_blueprint(settlements_bp)

# Core Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('groups.dashboard'))
    return redirect(url_for('auth.login'))

# Error Handlers
@app.errorhandler(404)
def page_not_found(e):
    from antigravity import render_template
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    from antigravity import render_template
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

