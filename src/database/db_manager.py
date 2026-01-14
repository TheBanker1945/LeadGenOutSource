"""Handles database connection and schema creation (PostgreSQL + SQLite support)."""

import os
import sqlite3
from pathlib import Path
from contextlib import contextmanager

# Check if PostgreSQL is available (via DATABASE_URL env var)
DATABASE_URL = os.getenv("DATABASE_URL")

# SQLite fallback path (for local development)
DB_PATH = Path(__file__).parent.parent.parent / "leads.db"


def get_connection():
    """
    Returns a database connection (PostgreSQL if available, otherwise SQLite).
    Uses appropriate connection for the environment.
    """
    if DATABASE_URL:
        # PostgreSQL connection for production (Render)
        import psycopg2
        from psycopg2.extras import RealDictCursor
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        return conn
    else:
        # SQLite connection for local development
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn


def init_db() -> None:
    """
    Initializes the database by creating the leads table if it doesn't exist.
    Works with both PostgreSQL and SQLite.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    if DATABASE_URL:
        # PostgreSQL schema
        cursor.execute("""
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
        
        # API usage tracking table (persists through server restarts)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_usage (
                id SERIAL PRIMARY KEY,
                month TEXT UNIQUE NOT NULL,
                requests_made INTEGER DEFAULT 0,
                monthly_limit INTEGER NOT NULL,
                last_reset TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_request TIMESTAMP
            )
        """)
        
        # Authentication tokens table (for Render deployment)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auth_tokens (
                token TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP,
                active BOOLEAN DEFAULT TRUE,
                is_admin BOOLEAN DEFAULT FALSE
            )
        """)
    else:
        # SQLite schema
        cursor.execute("""
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
        
        # API usage tracking table (persists through server restarts)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                month TEXT UNIQUE NOT NULL,
                requests_made INTEGER DEFAULT 0,
                monthly_limit INTEGER NOT NULL,
                last_reset TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_request TIMESTAMP
            )
        """)
        
        # Authentication tokens table (for Render deployment)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auth_tokens (
                token TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP,
                active BOOLEAN DEFAULT TRUE,
                is_admin BOOLEAN DEFAULT FALSE
            )
        """)
    
    conn.commit()
    cursor.close()
    conn.close()
