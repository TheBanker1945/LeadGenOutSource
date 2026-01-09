"""Orchestrator for the scraping stage."""

from src.database.repository import LeadRepository
from src.scraper.filters import apply_filters, is_profile_page, FilterOption
from src.scraper.maps_client import GoogleMapsClient
from src.exporter.csv_exporter import format_operating_hours, format_rating


def run_scraper(
    city: str,
    niche: str,
    max_pages: int = 1,
    country: str = "",
    has_website_filter: FilterOption = "Any",
    has_phone_filter: FilterOption = "Any",
    operational_only: bool = True,
    monthly_limit: int = 1000
) -> dict:
    """
    Run the scraper for a specific city and niche with configurable filters.
    
    Args:
        city: City to search in (e.g., "Toronto")
        niche: Business niche to search for (e.g., "plumbers")
        max_pages: Maximum number of pages to fetch from Google Maps API
        country: Country to search in (e.g., "Netherlands")
        has_website_filter: "Yes" = must have website, "No" = must NOT have website, "Any" = don't care
        has_phone_filter: "Yes" = must have phone, "No" = must NOT have phone, "Any" = don't care
        operational_only: If True, skip non-operational businesses
        monthly_limit: Monthly API request limit (default: 1000)
    
    Returns:
        Dictionary with scraping statistics.
    """
    location = f"{city}, {country}" if country else city
    print(f"\n{'='*50}")
    print(f"Scraping: {niche} in {location}")
    print(f"Filters: Website={has_website_filter}, Phone={has_phone_filter}, Operational={operational_only}")
    print(f"{'='*50}")

    # Initialize clients
    client = GoogleMapsClient(monthly_limit=monthly_limit)
    repo = LeadRepository()

    # Construct search query
    query = f"{niche} in {location}"
    print(f"Query: {query}")

    # Fetch results from Google Maps
    print(f"\nFetching results from Google Maps (max {max_pages} pages)...")
    places = client.search_text(query, max_pages=max_pages)

    # Statistics
    stats = {
        "total": len(places),
        "filtered_out": {},
        "saved": 0,
        "duplicates": 0,
    }

    print(f"\nProcessing {stats['total']} results...")

    for place in places:
        # Extract display name
        display_name_obj = place.get("displayName", {})
        company_name = display_name_obj.get("text", "Unknown")
        
        # Apply filters
        should_include, reason = apply_filters(
            place,
            has_website_filter=has_website_filter,
            has_phone_filter=has_phone_filter,
            operational_only=operational_only
        )
        
        if not should_include:
            # Track filter reasons
            stats["filtered_out"][reason] = stats["filtered_out"].get(reason, 0) + 1
            continue

        # Extract all data fields
        website_url = place.get("websiteUri", "")
        phone = place.get("nationalPhoneNumber", "")
        address = place.get("formattedAddress", "")
        rating = place.get("rating")
        opening_hours_data = place.get("regularOpeningHours")
        
        # Format operating hours
        operating_hours = format_operating_hours(opening_hours_data)
        
        # Determine lead type for display
        if website_url and is_profile_page(website_url):
            lead_type = "PROFILE"
            icon = "🟠"
        elif website_url:
            lead_type = "WEBSITE"
            icon = "🟢"
        else:
            lead_type = "NO SITE"
            icon = "🔴"

        # Map to database schema
        lead_data = {
            "company_name": company_name,
            "address": address,
            "city": city if city else country,
            "phone": phone if phone else None,
            "website": website_url if website_url else None,
            "niche": niche,
            "rating": rating,
            "operating_hours": operating_hours if operating_hours else None,
        }

        # Save to database
        if repo.add_lead(lead_data):
            stats["saved"] += 1
            rating_str = format_rating(rating) if rating else "No rating"
            print(f"  {icon} [{lead_type}] {company_name} | ⭐ {rating_str} | 📞 {phone or 'No phone'}")
        else:
            stats["duplicates"] += 1

    # Print summary
    print(f"\n{'='*50}")
    print("SCRAPING COMPLETE")
    print(f"{'='*50}")
    print(f"Total results:        {stats['total']}")
    
    if stats["filtered_out"]:
        print(f"\nFiltered out:")
        for reason, count in stats["filtered_out"].items():
            print(f"  - {reason}: {count}")
    
    print(f"\nDuplicates:           {stats['duplicates']} (already in DB)")
    print(f"Saved to database:    {stats['saved']}")
    print(f"{'='*50}\n")

    return stats
