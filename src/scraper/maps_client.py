"""Wrapper for Google Maps API."""

import os
import time
from typing import Optional

import requests
from dotenv import load_dotenv

from src.scraper.rate_limiter import RateLimiter, RequestLimitExceeded

load_dotenv()


class GoogleMapsClient:
    """Client for Google Maps Places API (New)."""

    BASE_URL = "https://places.googleapis.com/v1/places:searchText"
    
    # Field mask to get all needed data in a single request (cost optimization)
    FIELD_MASK = (
        "places.displayName,"
        "places.formattedAddress,"
        "places.nationalPhoneNumber,"
        "places.websiteUri,"
        "places.businessStatus,"
        "places.googleMapsUri,"
        "places.rating,"  # Review rating (e.g., 4.5)
        "places.regularOpeningHours,"  # Operating hours
        "nextPageToken"  # Required for pagination
    )

    def __init__(self, monthly_limit: int = 1000):
        """
        Initialize the client with API key from environment.
        
        Args:
            monthly_limit: Maximum API requests allowed per month (default: 1000)
        """
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_MAPS_API_KEY not found in environment variables")
        
        # Initialize rate limiter with hard monthly limit
        self.rate_limiter = RateLimiter(monthly_limit=monthly_limit)

    def search_text(self, query: str, max_pages: int = 1, language_code: str = "en") -> list[dict]:
        """
        Search for places using text query.
        
        Raises:
            RequestLimitExceeded: If monthly API limit would be exceeded
        """
        # Check if we can make this many requests
        can_proceed, used, remaining = self.rate_limiter.check_limit(max_pages)
        
        if not can_proceed:
            error_msg = (
                f"\n{'='*60}\n"
                f"🚫 MONTHLY API LIMIT REACHED!\n"
                f"{'='*60}\n"
                f"Requests used this month: {used}\n"
                f"Requests remaining: {remaining}\n"
                f"Requests needed for this query: {max_pages}\n"
                f"\n"
                f"This limit prevents unexpected API costs.\n"
                f"The limit will reset at the start of next month.\n"
                f"{'='*60}\n"
            )
            print(error_msg)
            raise RequestLimitExceeded(error_msg)
        
        # Show usage stats if getting close to limit
        if remaining <= 100 or (used / self.rate_limiter.monthly_limit) >= 0.8:
            self.rate_limiter.print_usage_warning()
        
        print(f"  Searching: {query}")
        print(f"  Max pages to fetch: {max_pages}")
        print(f"  API requests remaining this month: {remaining}")
        
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": self.FIELD_MASK,
        }

        all_places = []
        page_token: Optional[str] = None
        pages_fetched = 0

        while pages_fetched < max_pages:
            payload = {
                "textQuery": query,
                "languageCode": language_code,
            }
            
            if page_token:
                payload["pageToken"] = page_token

            try:
                response = requests.post(
                    self.BASE_URL,
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                response.raise_for_status()
                data = response.json()
                
                # Record successful request
                self.rate_limiter.record_request(1)

            except requests.RequestException as e:
                print(f"API request failed: {e}")
                # Still record the failed request (it counts against quota)
                self.rate_limiter.record_request(1)
                break

            places = data.get("places", [])
            all_places.extend(places)
            pages_fetched += 1

            print(f"  Page {pages_fetched}: fetched {len(places)} places")

            # Check for next page
            page_token = data.get("nextPageToken")
            print(f"  Next page token present: {bool(page_token)}")
            if not page_token:
                print(f"  No more pages available from API")
                break

            # Delay before next request - nextPageToken needs time to become valid
            print(f"  Waiting 2 seconds for next page token...")
            time.sleep(2)

        return all_places
