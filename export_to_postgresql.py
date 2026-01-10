"""
Export SQLite database to PostgreSQL (Render)
Run this script once after setting up PostgreSQL on Render
"""

import sqlite3
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Check if DATABASE_URL is set
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ DATABASE_URL environment variable not set!")
    print("Please set DATABASE_URL in your .env file.")
    sys.exit(1)

try:
    import psycopg2
except ImportError:
    print("❌ psycopg2 not installed!")
    print("Run: pip install psycopg2-binary")
    sys.exit(1)

def export_data():
    """Export all data from SQLite to PostgreSQL."""
    
    # Connect to SQLite
    print("📖 Reading from SQLite database...")
    sqlite_conn = sqlite3.connect("leads.db")
    sqlite_conn.row_factory = sqlite3.Row
    cursor = sqlite_conn.cursor()
    
    # Get all leads
    cursor.execute("SELECT * FROM leads")
    leads = [dict(row) for row in cursor.fetchall()]
    print(f"✅ Found {len(leads)} leads in SQLite")
    
    if len(leads) == 0:
        print("⚠️  No leads to export")
        sqlite_conn.close()
        return
    
    # Connect to PostgreSQL
    print("\n📤 Connecting to PostgreSQL...")
    pg_conn = psycopg2.connect(DATABASE_URL)
    pg_cursor = pg_conn.cursor()
    
    # Create table if not exists
    print("🔧 Creating table...")
    pg_cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id SERIAL PRIMARY KEY,
            company_name TEXT NOT NULL,
            address TEXT,
            city TEXT,
            phone TEXT UNIQUE,
            website TEXT,
            niche TEXT,
            rating REAL,
            operating_hours TEXT,
            status TEXT DEFAULT 'NEW',
            mockup_path TEXT,
            laptop_mockup_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    pg_conn.commit()
    
    # Insert leads
    print("📥 Inserting leads into PostgreSQL...")
    success_count = 0
    duplicate_count = 0
    
    for lead in leads:
        try:
            pg_cursor.execute("""
                INSERT INTO leads (
                    company_name, address, city, phone, website,
                    niche, rating, operating_hours, status,
                    mockup_path, laptop_mockup_path, created_at
                )
                VALUES (
                    %(company_name)s, %(address)s, %(city)s, %(phone)s, %(website)s,
                    %(niche)s, %(rating)s, %(operating_hours)s, %(status)s,
                    %(mockup_path)s, %(laptop_mockup_path)s, %(created_at)s
                )
            """, lead)
            pg_conn.commit()
            success_count += 1
        except psycopg2.IntegrityError:
            # Duplicate phone number - skip
            pg_conn.rollback()
            duplicate_count += 1
            continue
    
    print(f"\n✅ Successfully exported {success_count} leads")
    if duplicate_count > 0:
        print(f"⚠️  Skipped {duplicate_count} duplicates")
    
    # Close connections
    pg_cursor.close()
    pg_conn.close()
    sqlite_conn.close()
    
    print("\n🎉 Export complete!")

if __name__ == "__main__":
    export_data()
