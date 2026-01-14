"""
Seed authentication tokens into database for Render deployment.
This script copies tokens from auth_tokens.json to the database.
Run this after deploying to Render to set up authentication.
"""

from datetime import datetime
from src.database.db_manager import init_db, get_connection, DATABASE_URL
import json
from pathlib import Path

def seed_tokens():
    """Seed authentication tokens from JSON into database."""
    print("=" * 80)
    print("🔑 SEEDING AUTHENTICATION TOKENS TO DATABASE")
    print("=" * 80)
    
    # Initialize database
    print("\n1️⃣ Initializing database schema...")
    init_db()
    print("   ✅ Database schema ready")
    
    # Load tokens from JSON
    tokens_file = Path("auth_tokens.json")
    if not tokens_file.exists():
        print("\n❌ ERROR: auth_tokens.json not found!")
        print("   Please ensure auth_tokens.json exists with your tokens.")
        return
    
    with open(tokens_file, 'r') as f:
        tokens = json.load(f)
    
    print(f"\n2️⃣ Found {len(tokens)} tokens to seed...")
    
    # Insert tokens into database
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        for token, data in tokens.items():
            username = data['username']
            is_admin = data.get('is_admin', False)
            created_at = data.get('created_at', datetime.now().isoformat())
            
            print(f"   📝 Seeding token for: {username} {'🔑 (Admin)' if is_admin else ''}")
            
            if DATABASE_URL:
                # PostgreSQL
                cursor.execute("""
                    INSERT INTO auth_tokens (token, username, created_at, last_used, active, is_admin)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (token) DO UPDATE 
                    SET username = %s, active = %s, is_admin = %s
                """, (token, username, created_at, None, True, is_admin,
                      username, True, is_admin))
            else:
                # SQLite
                cursor.execute("""
                    INSERT OR REPLACE INTO auth_tokens (token, username, created_at, last_used, active, is_admin)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (token, username, created_at, None, True, is_admin))
        
        conn.commit()
        print("   ✅ All tokens seeded successfully")
        
        # Verify
        print("\n3️⃣ Verification:")
        cursor.execute("SELECT username, is_admin, active FROM auth_tokens")
        results = cursor.fetchall()
        for row in results:
            row_dict = dict(row)
            role = "🔑 Admin" if row_dict['is_admin'] else "👤 User"
            status = "🟢 Active" if row_dict['active'] else "🔴 Inactive"
            print(f"   • {row_dict['username']}: {role} {status}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
    
    print("\n" + "=" * 80)
    print("✅ TOKEN SEEDING COMPLETE!")
    print("=" * 80)
    print("\n💡 Tokens are now stored in the database and ready for use.")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    seed_tokens()
