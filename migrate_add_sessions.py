"""
Manual migration script to add session tracking to existing database.
Run this once to add the session_id column to the leads table.
"""

from src.database.db_manager import get_connection, DATABASE_URL

def migrate():
    """Add scrape_sessions table and session_id column to leads table."""
    print("=" * 80)
    print("🔄 RUNNING SESSION MIGRATION")
    print("=" * 80)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Step 1: Create scrape_sessions table if it doesn't exist
        print("\n1️⃣ Creating scrape_sessions table...")
        if DATABASE_URL:
            # PostgreSQL
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scrape_sessions (
                    id SERIAL PRIMARY KEY,
                    session_name TEXT NOT NULL,
                    locations TEXT,
                    niches TEXT,
                    country TEXT,
                    state TEXT,
                    total_leads INTEGER DEFAULT 0,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    status TEXT DEFAULT 'running'
                )
            """)
        else:
            # SQLite
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scrape_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_name TEXT NOT NULL,
                    locations TEXT,
                    niches TEXT,
                    country TEXT,
                    state TEXT,
                    total_leads INTEGER DEFAULT 0,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    status TEXT DEFAULT 'running'
                )
            """)
        conn.commit()
        print("   ✅ scrape_sessions table ready")
        
        # Step 2: Check if session_id column exists in leads table
        print("\n2️⃣ Checking leads table for session_id column...")
        
        if DATABASE_URL:
            # PostgreSQL - check information_schema
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'leads' AND column_name = 'session_id'
            """)
            column_exists = cursor.fetchone() is not None
        else:
            # SQLite - check PRAGMA
            cursor.execute("PRAGMA table_info(leads)")
            columns = [row[1] for row in cursor.fetchall()]
            column_exists = 'session_id' in columns
        
        if not column_exists:
            print("   📝 Adding session_id column to leads table...")
            cursor.execute("""
                ALTER TABLE leads 
                ADD COLUMN session_id INTEGER REFERENCES scrape_sessions(id)
            """)
            conn.commit()
            print("   ✅ Successfully added session_id column!")
        else:
            print("   ℹ️  session_id column already exists")
        
        # Step 3: Verify the migration
        print("\n3️⃣ Verifying migration...")
        if DATABASE_URL:
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name IN ('leads', 'scrape_sessions')
                ORDER BY table_name, ordinal_position
            """)
            print("   Database columns:")
            for row in cursor.fetchall():
                print(f"   - {row[0]}: {row[1]}")
        else:
            cursor.execute("PRAGMA table_info(leads)")
            print("   Leads table columns:")
            for row in cursor.fetchall():
                print(f"   - {row[1]}: {row[2]}")
        
        print("\n" + "=" * 80)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERROR during migration: {e}")
        conn.rollback()
        import traceback
        traceback.print_exc()
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    migrate()
