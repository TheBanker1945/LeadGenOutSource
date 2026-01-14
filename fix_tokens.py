"""
Manual token fix script - run this if tokens aren't working on Render.
This forces all 4 tokens to be added/updated in the database.
"""

import os
from datetime import datetime

# Set this to your Render DATABASE_URL if running locally to fix Render DB
# Otherwise it will fix your local database
# os.environ['DATABASE_URL'] = 'your_render_database_url_here'

from src.database.db_manager import get_connection, DATABASE_URL

def fix_tokens():
    """Manually fix all authentication tokens in database."""
    print("=" * 80)
    print("🔧 MANUAL TOKEN FIX")
    print("=" * 80)
    
    if not DATABASE_URL:
        print("\n⚠️  WARNING: DATABASE_URL not set!")
        print("   This will update your LOCAL SQLite database.")
        print("   To fix Render, set DATABASE_URL environment variable first.")
        response = input("\n   Continue with local database? (y/n): ")
        if response.lower() != 'y':
            print("   Cancelled.")
            return
    else:
        print(f"\n🌐 Connected to: PostgreSQL (Render)")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # All tokens that should exist
        tokens = [
            ("a9f8c2d4e1b7a5f3c8d6e2b9a7f4c1d8e5b3a6f9c2d7e4b1a8f5c3d9e6b2a7f4", "admin", True),
            ("e5253049eace80bc217a443dcf985b55dfb88d71af81f67eb692cf50216f3474", "user_1", False),
            ("b7b281c5e83f5996c3c19cc38fce45b42f3fc7fa250a2ef3f11853300521f407", "user_2", False),
            ("5330c1f3196ce23a4a44a426ae8d248f9c4fef0301188a8ab48a033a62c9b4a5", "user_3", False),
        ]
        
        print("\n🔄 Upserting all tokens...")
        
        for token, username, is_admin in tokens:
            if DATABASE_URL:
                # PostgreSQL
                cursor.execute("""
                    INSERT INTO auth_tokens (token, username, created_at, last_used, active, is_admin)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (token) DO UPDATE 
                    SET username = EXCLUDED.username,
                        active = EXCLUDED.active,
                        is_admin = EXCLUDED.is_admin
                """, (token, username, datetime.now(), None, True, is_admin))
            else:
                # SQLite
                cursor.execute("""
                    INSERT OR REPLACE INTO auth_tokens (token, username, created_at, last_used, active, is_admin)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (token, username, datetime.now(), None, True, is_admin))
            
            role = "🔑 Admin" if is_admin else "👤 User"
            print(f"   ✅ {username}: {role}")
        
        conn.commit()
        
        # Verify
        print("\n✅ Verification:")
        if DATABASE_URL:
            cursor.execute("SELECT username, is_admin, active FROM auth_tokens ORDER BY is_admin DESC, username")
        else:
            cursor.execute("SELECT username, is_admin, active FROM auth_tokens ORDER BY is_admin DESC, username")
        
        results = cursor.fetchall()
        for row in results:
            row_dict = dict(row)
            role = "🔑 Admin" if row_dict['is_admin'] else "👤 User"
            status = "🟢" if row_dict['active'] else "🔴"
            print(f"   {status} {row_dict['username']}: {role}")
        
        print("\n" + "=" * 80)
        print("✅ ALL TOKENS FIXED!")
        print("=" * 80)
        print("\n💡 You can now login with any of the 4 tokens.")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    fix_tokens()
