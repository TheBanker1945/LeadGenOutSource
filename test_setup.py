"""
Quick test script to verify your setup works correctly.
Run this before doing bulk scraping to catch configuration issues early.
"""

import os
import sys

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_api_keys():
    """Check if API keys are configured."""
    print("🔑 Checking API keys...")
    
    google_key = os.getenv("GOOGLE_MAPS_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    if not google_key:
        print("❌ GOOGLE_MAPS_API_KEY not found in .env file")
        return False
    else:
        print(f"✅ Google Maps API key found: {google_key[:20]}...")
    
    if not gemini_key:
        print("⚠️  GEMINI_API_KEY not found (neighborhood splitting disabled)")
    else:
        print(f"✅ Gemini API key found: {gemini_key[:20]}...")
    
    return True


def test_imports():
    """Test that all required packages are installed."""
    print("\n📦 Checking Python packages...")
    
    required_packages = {
        "requests": "requests",
        "yaml": "pyyaml",
        "google.generativeai": "google-generativeai",
        "dotenv": "python-dotenv"
    }
    
    all_installed = True
    for import_name, package_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"✅ {package_name} installed")
        except ImportError:
            print(f"❌ {package_name} not installed")
            all_installed = False
    
    return all_installed


def test_config():
    """Test that config.yaml is valid."""
    print("\n📋 Checking config.yaml...")
    
    try:
        import yaml
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
        
        # Check required fields
        if not config.get("locations"):
            print("❌ No locations specified in config.yaml")
            return False
        
        if not config.get("niches"):
            print("❌ No niches specified in config.yaml")
            return False
        
        print(f"✅ Config valid: {len(config['locations'])} location(s), {len(config['niches'])} niche(s)")
        return True
        
    except FileNotFoundError:
        print("❌ config.yaml not found")
        return False
    except Exception as e:
        print(f"❌ Error reading config.yaml: {e}")
        return False


def test_database():
    """Test database initialization."""
    print("\n💾 Testing database...")
    
    try:
        from src.database.db_manager import init_db, get_connection
        
        init_db()
        
        # Test connection
        with get_connection() as conn:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            if "leads" in tables:
                print("✅ Database initialized successfully")
                return True
            else:
                print("❌ Leads table not created")
                return False
                
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False


def test_scraper():
    """Test a minimal scrape (just fetch, don't save)."""
    print("\n🔍 Testing Google Maps API connection...")
    
    try:
        from src.scraper.maps_client import GoogleMapsClient
        
        client = GoogleMapsClient()
        
        # Try a very simple query (won't scrape much, just test API)
        print("   Attempting test query: 'coffee shop in Seattle'")
        results = client.search_text("coffee shop in Seattle", max_pages=1)
        
        if results:
            print(f"✅ API working! Found {len(results)} result(s)")
            
            # Show first result
            if results:
                first = results[0]
                name = first.get("displayName", {}).get("text", "Unknown")
                address = first.get("formattedAddress", "No address")
                print(f"   Example: {name}")
                print(f"   Address: {address[:50]}...")
            
            return True
        else:
            print("⚠️  API returned no results (might be query-specific)")
            return True  # Still counts as working
            
    except Exception as e:
        print(f"❌ Scraper error: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 SETUP VERIFICATION TEST")
    print("=" * 60)
    
    tests = [
        ("API Keys", test_api_keys),
        ("Python Packages", test_imports),
        ("Configuration", test_config),
        ("Database", test_database),
        ("Google Maps API", test_scraper),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            results.append(test_func())
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ ALL TESTS PASSED ({passed}/{total})")
        print("\n🚀 You're ready to run: python main.py")
    else:
        print(f"⚠️  SOME TESTS FAILED ({passed}/{total} passed)")
        print("\n🔧 Fix the issues above before running main.py")
        sys.exit(1)
    
    print("=" * 60)


if __name__ == "__main__":
    main()
