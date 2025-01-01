from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

def supabaseClient():
    supabase = create_client(
    supabase_url=os.environ.get("SUPABASE_URL"),
    supabase_key=os.environ.get("SUPABASE_KEY")
    )

    return supabase
