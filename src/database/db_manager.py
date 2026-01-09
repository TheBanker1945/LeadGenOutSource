"""Handles SQLite connection and schema creation."""

import sqlite3
from pathlib import Path

# Database file path in root directory
DB_PATH = Path(__file__).parent.parent.parent / "leads.db"


def get_connection() -> sqlite3.Connection:
    """
    Returns a SQLite connection to the leads database.
    Uses Row factory for dict-like access to columns.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """
    Initializes the database by creating the leads table if it doesn't exist.
    """
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        conn.commit()
