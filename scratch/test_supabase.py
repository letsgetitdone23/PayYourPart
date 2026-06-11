import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")

print(f"SUPABASE_URL configured: {bool(supabase_url)}")
print(f"SUPABASE_KEY configured: {bool(supabase_key)}")

if not supabase_url or not supabase_key:
    print("Error: SUPABASE_URL and SUPABASE_KEY must be configured in .env")
    exit(1)

try:
    supabase = create_client(supabase_url, supabase_key)
    print("Successfully initialized Supabase client.")
    
    # Try fetching public tables
    print("Testing connection and checking tables...")
    
    # Check if we can select from profiles
    res = supabase.table('profiles').select('count', count='exact').limit(0).execute()
    print("Connection works! The 'profiles' table is accessible.")
    
    # Check other tables
    for table in ['groups', 'group_members', 'expenses', 'expense_splits', 'settlements']:
        try:
            supabase.table(table).select('count', count='exact').limit(0).execute()
            print(f"Table '{table}' is accessible.")
        except Exception as te:
            print(f"Error accessing table '{table}': {te}")
            
except Exception as e:
    print(f"Failed to connect to Supabase: {e}")
    exit(1)
