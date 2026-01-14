"""
Migration script to initialize API usage in database with current value.
Run this once to set up the database-backed usage tracking.
"""

from datetime import datetime
from src.database.db_manager import init_db, get_connection, DATABASE_URL

def migrate_usage():
    """Initialize API usage in database with current month's usage."""
    print("=" * 60)
    print("🔄 MIGRATING API USAGE TO DATABASE")
    print("=" * 60)
    
    # Initialize database (creates api_usage table)
    print("\n1️⃣ Initializing database schema...")
    init_db()
    print("   ✅ Database schema ready")
    
    # Set current month's usage to 409 requests
    current_month = datetime.now().strftime("%Y-%m")
    current_usage = 409
    monthly_limit = 1000
    
    print(f"\n2️⃣ Setting usage for {current_month}...")
    print(f"   📊 Requests Made: {current_usage}")
    print(f"   🚫 Monthly Limit: {monthly_limit}")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        if DATABASE_URL:
            # PostgreSQL
            cursor.execute(
                """INSERT INTO api_usage (month, requests_made, monthly_limit, last_reset)
                   VALUES (%s, %s, %s, %s)
                   ON CONFLICT (month) DO UPDATE 
                   SET requests_made = %s, monthly_limit = %s""",
                (current_month, current_usage, monthly_limit, datetime.now(),
                 current_usage, monthly_limit)
            )
        else:
            # SQLite
            cursor.execute(
                """INSERT OR REPLACE INTO api_usage (month, requests_made, monthly_limit, last_reset)
                   VALUES (?, ?, ?, ?)""",
                (current_month, current_usage, monthly_limit, datetime.now())
            )
        
        conn.commit()
        print("   ✅ Usage data saved to database")
        
        # Verify
        if DATABASE_URL:
            cursor.execute("SELECT * FROM api_usage WHERE month = %s", (current_month,))
        else:
            cursor.execute("SELECT * FROM api_usage WHERE month = ?", (current_month,))
        
        result = cursor.fetchone()
        print(f"\n3️⃣ Verification:")
        print(f"   Month: {dict(result)['month']}")
        print(f"   Requests Made: {dict(result)['requests_made']}")
        print(f"   Monthly Limit: {dict(result)['monthly_limit']}")
        print(f"   Last Reset: {dict(result)['last_reset']}")
        
    finally:
        cursor.close()
        conn.close()
    
    print("\n" + "=" * 60)
    print("✅ MIGRATION COMPLETE!")
    print("=" * 60)
    print("\n💡 Usage is now stored in the database and will persist")
    print("   through server restarts on Render.")
    print("\n🗑️  You can now safely ignore/delete api_usage.json")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    migrate_usage()
