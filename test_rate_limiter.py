"""
Test script to demonstrate API rate limiting functionality.
This simulates API usage without making actual API calls.
"""

import json
from pathlib import Path
from datetime import datetime

from src.scraper.rate_limiter import RateLimiter, RequestLimitExceeded


def test_rate_limiter():
    """Test the rate limiter with a low limit."""
    print("=" * 60)
    print("🧪 TESTING API RATE LIMITER")
    print("=" * 60)
    
    # Use a test file so we don't affect real usage
    test_file = "api_usage_test.json"
    
    # Clean up any existing test file
    if Path(test_file).exists():
        Path(test_file).unlink()
    
    # Create limiter with very low limit for testing
    limiter = RateLimiter(limit_file=test_file, monthly_limit=10)
    
    print("\n✅ Created rate limiter with 10 request/month limit\n")
    
    # Test 1: Check initial usage
    print("Test 1: Initial Usage")
    stats = limiter.get_usage_stats()
    print(f"  Requests made: {stats['requests_made']}")
    print(f"  Remaining: {stats['requests_remaining']}")
    assert stats['requests_made'] == 0, "Should start at 0"
    assert stats['requests_remaining'] == 10, "Should have 10 remaining"
    print("  ✓ PASSED\n")
    
    # Test 2: Make some requests
    print("Test 2: Recording Requests")
    for i in range(8):
        can_proceed, used, remaining = limiter.check_limit(1)
        assert can_proceed, f"Request {i+1} should be allowed"
        limiter.record_request(1)
        print(f"  Request {i+1}: Used={used+1}, Remaining={remaining-1}")
    
    stats = limiter.get_usage_stats()
    assert stats['requests_made'] == 8, "Should have 8 requests"
    assert stats['requests_remaining'] == 2, "Should have 2 remaining"
    print("  ✓ PASSED\n")
    
    # Test 3: Approaching limit
    print("Test 3: Approaching Limit")
    can_proceed, used, remaining = limiter.check_limit(2)
    print(f"  Can make 2 more requests? {can_proceed}")
    print(f"  Used: {used}, Remaining: {remaining}")
    assert can_proceed, "Should allow 2 more requests"
    limiter.record_request(2)
    print("  ✓ PASSED\n")
    
    # Test 4: At limit
    print("Test 4: At Limit")
    stats = limiter.get_usage_stats()
    print(f"  Requests made: {stats['requests_made']}")
    print(f"  Remaining: {stats['requests_remaining']}")
    assert stats['requests_made'] == 10, "Should be at limit"
    assert stats['requests_remaining'] == 0, "Should have 0 remaining"
    print("  ✓ PASSED\n")
    
    # Test 5: Exceeding limit
    print("Test 5: Exceeding Limit")
    can_proceed, used, remaining = limiter.check_limit(1)
    print(f"  Can make 1 more request? {can_proceed}")
    assert not can_proceed, "Should NOT allow more requests"
    print("  ✓ PASSED - Correctly blocked!\n")
    
    # Test 6: Monthly reset simulation
    print("Test 6: Monthly Reset")
    # Manually modify the month to simulate next month
    with open(test_file, 'r') as f:
        data = json.load(f)
    
    data['month'] = '2025-12'  # Previous month
    
    with open(test_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    # Now check - should trigger reset
    can_proceed, used, remaining = limiter.check_limit(1)
    print(f"  After month change:")
    print(f"  Can make request? {can_proceed}")
    print(f"  Used: {used}, Remaining: {remaining}")
    assert can_proceed, "Should allow requests after reset"
    assert used == 0, "Should reset to 0"
    assert remaining == 10, "Should have full limit"
    print("  ✓ PASSED - Monthly reset works!\n")
    
    # Cleanup
    Path(test_file).unlink()
    
    print("=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nThe rate limiter is working correctly:")
    print("  ✓ Tracks requests accurately")
    print("  ✓ Enforces monthly limit")
    print("  ✓ Blocks requests when limit reached")
    print("  ✓ Automatically resets each month")
    print("\n🎉 Your API costs are protected!\n")


if __name__ == "__main__":
    try:
        test_rate_limiter()
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
