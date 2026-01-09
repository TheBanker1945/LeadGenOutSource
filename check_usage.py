"""
Check current Google Maps API usage statistics.
Shows how many requests have been made this month and how many remain.
"""

from src.scraper.rate_limiter import RateLimiter


def main():
    """Display current API usage statistics."""
    print("=" * 60)
    print("📊 GOOGLE MAPS API USAGE")
    print("=" * 60)
    
    limiter = RateLimiter(monthly_limit=1000)  # Default limit
    stats = limiter.get_usage_stats()
    
    print(f"\n📅 Current Month: {stats['month']}")
    print(f"✅ Requests Made: {stats['requests_made']}")
    print(f"🚫 Monthly Limit: {stats['monthly_limit']}")
    print(f"⏳ Requests Remaining: {stats['requests_remaining']}")
    print(f"📈 Usage: {stats['percentage_used']}%")
    
    if stats['last_request'] != "Never":
        print(f"\n🕒 Last Request: {stats['last_request']}")
    
    print(f"🔄 Last Reset: {stats['last_reset']}")
    
    # Visual progress bar
    bar_length = 50
    filled = int(bar_length * stats['requests_made'] / stats['monthly_limit'])
    bar = "█" * filled + "░" * (bar_length - filled)
    print(f"\n[{bar}] {stats['percentage_used']}%")
    
    # Warnings
    if stats['percentage_used'] >= 90:
        print("\n⚠️  WARNING: You've used 90%+ of your monthly limit!")
    elif stats['percentage_used'] >= 75:
        print("\n⚠️  CAUTION: You've used 75%+ of your monthly limit")
    elif stats['requests_remaining'] <= 50:
        print(f"\n⚠️  LOW: Only {stats['requests_remaining']} requests remaining")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
