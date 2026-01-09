"""
Google Maps API Request Rate Limiter
Enforces a hard monthly limit to prevent unexpected API costs.
"""

import json
from datetime import datetime
from pathlib import Path


class RequestLimitExceeded(Exception):
    """Raised when the monthly API request limit is exceeded."""
    pass


class RateLimiter:
    """Tracks and enforces monthly API request limits."""
    
    def __init__(self, limit_file: str = "api_usage.json", monthly_limit: int = 1000):
        """
        Initialize the rate limiter.
        
        Args:
            limit_file: Path to the JSON file tracking usage
            monthly_limit: Maximum requests allowed per month
        """
        self.limit_file = Path(limit_file)
        self.monthly_limit = monthly_limit
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Create the usage file if it doesn't exist."""
        if not self.limit_file.exists():
            self._reset_usage()
    
    def _load_usage(self) -> dict:
        """Load usage data from file."""
        try:
            with open(self.limit_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            # Corrupted or missing file - reset
            self._reset_usage()
            with open(self.limit_file, 'r') as f:
                return json.load(f)
    
    def _save_usage(self, data: dict):
        """Save usage data to file."""
        with open(self.limit_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _reset_usage(self):
        """Reset usage to zero for current month."""
        now = datetime.now()
        data = {
            "month": now.strftime("%Y-%m"),
            "requests_made": 0,
            "monthly_limit": self.monthly_limit,
            "last_reset": now.isoformat()
        }
        self._save_usage(data)
    
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
        usage_data["last_request"] = datetime.now().isoformat()
        
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
            "last_reset": usage_data.get("last_reset", "Unknown"),
            "last_request": usage_data.get("last_request", "Never")
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
