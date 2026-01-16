"""
Initialize database for Render deployment.
This script runs automatically on Render startup.
"""

import os
from datetime import datetime
from src.database.db_manager import init_db, get_connection, DATABASE_URL

def init_render_database():
    """Initialize database with schema and default tokens."""
    print("=" * 80)
    print("🔄 INITIALIZING RENDER DATABASE")
    print("=" * 80)
    
    # Initialize database schema
    print("\n1️⃣ Creating database tables...")
    init_db()
    print("   ✅ Database schema ready")
    
    # Check if running on Render
    if not DATABASE_URL:
        print("\n⚠️  Not running on Render (DATABASE_URL not set)")
        print("   Skipping token initialization")
        return
    
    # Add session_id column to existing leads table if it doesn't exist (migration)
    print("\n🔧 Running database migrations...")
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            ALTER TABLE leads 
            ADD COLUMN IF NOT EXISTS session_id INTEGER REFERENCES scrape_sessions(id)
        """)
        conn.commit()
        print("   ✅ Added session_id column to leads table")
    except Exception as e:
        # Column might already exist, that's okay
        conn.rollback()
        print(f"   ℹ️  Migration skipped (already applied or not needed)")
    
    try:
        # Check if tokens already exist
        cursor.execute("SELECT COUNT(*) FROM auth_tokens")
        count_result = cursor.fetchone()
        token_count = count_result[0] if count_result else 0
        
        print(f"\n2️⃣ Checking authentication tokens...")
        print(f"   Found {token_count} existing tokens in database")
        
        # Define all required tokens
        default_tokens = [
            {
                "token": "a9f8c2d4e1b7a5f3c8d6e2b9a7f4c1d8e5b3a6f9c2d7e4b1a8f5c3d9e6b2a7f4",
                "username": "admin",
                "is_admin": True
            },
            {
                "token": "e5253049eace80bc217a443dcf985b55dfb88d71af81f67eb692cf50216f3474",
                "username": "user_1",
                "is_admin": False
            },
            {
                "token": "b7b281c5e83f5996c3c19cc38fce45b42f3fc7fa250a2ef3f11853300521f407",
                "username": "user_2",
                "is_admin": False
            },
            {
                "token": "5330c1f3196ce23a4a44a426ae8d248f9c4fef0301188a8ab48a033a62c9b4a5",
                "username": "user_3",
                "is_admin": False
            }
        ]
        
        # Insert or update all tokens (ensures all exist)
        for token_data in default_tokens:
            cursor.execute("""
                INSERT INTO auth_tokens (token, username, created_at, active, is_admin)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (token) DO UPDATE 
                SET username = EXCLUDED.username, 
                    active = EXCLUDED.active,
                    is_admin = EXCLUDED.is_admin
            """, (token_data['token'], token_data['username'], 
                  datetime.now(), True, token_data['is_admin']))
            print(f"   ✅ Ensured token exists for: {token_data['username']} " +
                  ("🔑 (Admin)" if token_data['is_admin'] else ""))
        
        conn.commit()
        
        # Check API usage initialization
        current_month = datetime.now().strftime("%Y-%m")
        cursor.execute("SELECT * FROM api_usage WHERE month = %s", (current_month,))
        usage_result = cursor.fetchone()
        
        if not usage_result:
            print(f"\n3️⃣ Initializing API usage for {current_month}...")
            monthly_limit = int(os.getenv('MONTHLY_API_LIMIT', 1000))
            cursor.execute("""
                INSERT INTO api_usage (month, requests_made, monthly_limit, last_reset)
                VALUES (%s, %s, %s, %s)
            """, (current_month, 409, monthly_limit, datetime.now()))
            conn.commit()
            print(f"   ✅ Usage initialized: 409/{monthly_limit} requests")
        else:
            usage_dict = dict(usage_result)
            print(f"\n3️⃣ API usage already initialized for {current_month}")
            print(f"   📊 Current: {usage_dict['requests_made']}/{usage_dict['monthly_limit']} requests")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
    
    print("\n" + "=" * 80)
    print("✅ RENDER DATABASE INITIALIZATION COMPLETE!")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    init_render_database()
