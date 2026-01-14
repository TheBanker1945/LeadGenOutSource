"""
Google Maps API Request Rate Limiter
Enforces a hard monthly limit to prevent unexpected API costs.
Now uses database storage for persistence across server restarts.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.database.db_manager import get_connection, DATABASE_URL


class RequestLimitExceeded(Exception):
    """Raised when the monthly API request limit is exceeded."""
    pass


class RateLimiter:
    """Tracks and enforces monthly API request limits using database storage."""
    
    def __init__(self, limit_file: str = "api_usage.json", monthly_limit: int = 1000):
        """
        Initialize the rate limiter.
        
        Args:
            limit_file: DEPRECATED - Kept for backwards compatibility only
            monthly_limit: Maximum requests allowed per month
        """
        self.monthly_limit = monthly_limit
        self._ensure_usage_exists()
    
    def _ensure_usage_exists(self):
        """Ensure usage record exists for current month in database."""
        current_month = datetime.now().strftime("%Y-%m")
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            if DATABASE_URL:
                # PostgreSQL - check if current month exists
                cursor.execute(
                    "SELECT * FROM api_usage WHERE month = %s",
                    (current_month,)
                )
                result = cursor.fetchone()
                
                if not result:
                    # Create new record for current month
                    cursor.execute(
                        """INSERT INTO api_usage (month, requests_made, monthly_limit, last_reset)
                           VALUES (%s, %s, %s, %s)""",
                        (current_month, 0, self.monthly_limit, datetime.now())
                    )
                    conn.commit()
            else:
                # SQLite
                cursor.execute(
                    "SELECT * FROM api_usage WHERE month = ?",
                    (current_month,)
                )
                result = cursor.fetchone()
                
                if not result:
                    # Create new record for current month
                    cursor.execute(
                        """INSERT INTO api_usage (month, requests_made, monthly_limit, last_reset)
                           VALUES (?, ?, ?, ?)""",
                        (current_month, 0, self.monthly_limit, datetime.now())
                    )
                    conn.commit()
        finally:
            cursor.close()
            conn.close()
    
    def _load_usage(self) -> dict:
        """Load usage data from database."""
        current_month = datetime.now().strftime("%Y-%m")
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            if DATABASE_URL:
                cursor.execute(
                    "SELECT * FROM api_usage WHERE month = %s",
                    (current_month,)
                )
            else:
                cursor.execute(
                    "SELECT * FROM api_usage WHERE month = ?",
                    (current_month,)
                )
            
            result = cursor.fetchone()
            
            if result:
                return dict(result)
            else:
                # No record exists, create one
                self._ensure_usage_exists()
                return self._load_usage()
        finally:
            cursor.close()
            conn.close()
    
    def _save_usage(self, data: dict):
        """Save usage data to database."""
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            if DATABASE_URL:
                cursor.execute(
                    """UPDATE api_usage 
                       SET requests_made = %s, monthly_limit = %s, last_request = %s
                       WHERE month = %s""",
                    (data["requests_made"], data["monthly_limit"], 
                     data.get("last_request"), data["month"])
                )
            else:
                cursor.execute(
                    """UPDATE api_usage 
                       SET requests_made = ?, monthly_limit = ?, last_request = ?
                       WHERE month = ?""",
                    (data["requests_made"], data["monthly_limit"], 
                     data.get("last_request"), data["month"])
                )
            conn.commit()
        finally:
            cursor.close()
            conn.close()
    
    def _reset_usage(self):
        """Reset usage to zero for current month."""
        current_month = datetime.now().strftime("%Y-%m")
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            if DATABASE_URL:
                # Update existing or insert new
                cursor.execute(
                    """INSERT INTO api_usage (month, requests_made, monthly_limit, last_reset)
                       VALUES (%s, %s, %s, %s)
                       ON CONFLICT (month) DO UPDATE 
                       SET requests_made = %s, monthly_limit = %s, last_reset = %s""",
                    (current_month, 0, self.monthly_limit, datetime.now(),
                     0, self.monthly_limit, datetime.now())
                )
            else:
                # SQLite - use INSERT OR REPLACE
                cursor.execute(
                    """INSERT OR REPLACE INTO api_usage (month, requests_made, monthly_limit, last_reset)
                       VALUES (?, ?, ?, ?)""",
                    (current_month, 0, self.monthly_limit, datetime.now())
                )
            conn.commit()
        finally:
            cursor.close()
            conn.close()
    
    def _check_month_reset(self, usage_data: dict) -> dict:
        """Check if we've entered a new month and reset if needed."""
        current_month = datetime.now().strftime("%Y-%m")
        stored_month = usage_data.get("month", "")
        
        if current_month != stored_month:
            print(f"📅 New month detected! Resetting API usage counter...")
            print(f"   Previous month ({stored_month}): {usage_data.get('requests_made', 0)} requests used")
            self._reset_usage()
            return self._load_usage()
        
        return usage_data
    
    def check_limit(self, requests_needed: int = 1) -> tuple[bool, int, int]:
        """
        Check if we can make the requested number of API calls.
        
        Args:
            requests_needed: Number of requests about to be made
        
        Returns:
            Tuple of (can_proceed, requests_used, requests_remaining)
        
        Raises:
            RequestLimitExceeded: If the limit would be exceeded
        """
        usage_data = self._load_usage()
        usage_data = self._check_month_reset(usage_data)
        
        requests_used = usage_data["requests_made"]
        requests_remaining = self.monthly_limit - requests_used
        
        if requests_used + requests_needed > self.monthly_limit:
            return False, requests_used, requests_remaining
        
        return True, requests_used, requests_remaining
    
    def record_request(self, count: int = 1):
        """
        Record that API request(s) were made.
        
        Args:
            count: Number of requests made
        """
        usage_data = self._load_usage()
        usage_data = self._check_month_reset(usage_data)
        
        usage_data["requests_made"] += count
        usage_data["last_request"] = datetime.now()
        
        self._save_usage(usage_data)
    
    def get_usage_stats(self) -> dict:
        """
        Get current usage statistics.
        
        Returns:
            Dictionary with usage stats
        """
        usage_data = self._load_usage()
        usage_data = self._check_month_reset(usage_data)
        
        return {
            "month": usage_data["month"],
            "requests_made": usage_data["requests_made"],
            "monthly_limit": usage_data["monthly_limit"],
            "requests_remaining": usage_data["monthly_limit"] - usage_data["requests_made"],
            "percentage_used": round((usage_data["requests_made"] / usage_data["monthly_limit"]) * 100, 1),
            "last_reset": str(usage_data.get("last_reset", "Unknown")),
            "last_request": str(usage_data.get("last_request", "Never"))
        }
    
    def print_usage_warning(self):
        """Print a warning about current usage."""
        stats = self.get_usage_stats()
        
        print(f"\n{'='*60}")
        print(f"⚠️  API USAGE WARNING")
        print(f"{'='*60}")
        print(f"Month: {stats['month']}")
        print(f"Requests used: {stats['requests_made']} / {stats['monthly_limit']}")
        print(f"Remaining: {stats['requests_remaining']}")
        print(f"Usage: {stats['percentage_used']}%")
        print(f"{'='*60}\n")
