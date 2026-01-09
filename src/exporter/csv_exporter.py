"""Export leads to CSV format."""

import csv
from datetime import datetime
from pathlib import Path
from typing import Optional


def format_operating_hours(hours_data: Optional[dict]) -> str:
    """
    Format operating hours from Google Maps API format to readable string.
    
    Args:
        hours_data: regularOpeningHours dict from Google Maps API
    
    Returns:
        Formatted string like "Mon-Fri: 9AM-5PM" or "See Google Maps" if unavailable
    """
    if not hours_data:
        return ""
    
    # Try to get weekday descriptions if available
    weekday_descriptions = hours_data.get("weekdayDescriptions", [])
    if weekday_descriptions:
        # Join all days with semicolon separator
        return "; ".join(weekday_descriptions)
    
    return "See Google Maps"


def format_rating(rating: Optional[float]) -> str:
    """
    Format rating as "X.X/5" or return empty string if no rating.
    
    Args:
        rating: Rating value (e.g., 4.5)
    
    Returns:
        Formatted string like "4.5/5" or empty string
    """
    if rating is None:
        return ""
    return f"{rating}/5"


def export_to_csv(
    leads: list[dict],
    output_path: str | Path,
    include_headers: bool = True
) -> int:
    """
    Export leads to CSV file.
    
    Args:
        leads: List of lead dictionaries with keys:
               - company_name: Business name
               - address: Business address
               - phone: Phone number
               - website: Website URL (or None)
               - rating: Google rating (or None)
               - operating_hours: Opening hours string (or None)
        output_path: Path where CSV file will be saved
        include_headers: Whether to include column headers
    
    Returns:
        Number of leads exported
    """
    if not leads:
        print("⚠️  No leads to export")
        return 0
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # CSV columns as specified
    fieldnames = [
        "Business Name",
        "Business Address",
        "Business Website",
        "Operating Hours",
        "Phone Number",
        "Email",  # Always empty - not available from Google Maps
        "Google Review Rating"
    ]
    
    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if include_headers:
            writer.writeheader()
        
        for lead in leads:
            # Format the data according to CSV requirements
            row = {
                "Business Name": lead.get("company_name", ""),
                "Business Address": lead.get("address", ""),
                "Business Website": lead.get("website", ""),
                "Operating Hours": lead.get("operating_hours", ""),
                "Phone Number": lead.get("phone", ""),
                "Email": "",  # Not available from Google Maps API
                "Google Review Rating": lead.get("rating", "")
            }
            writer.writerow(row)
    
    return len(leads)


def generate_csv_filename(niche: str, location: str, timestamp: Optional[datetime] = None) -> str:
    """
    Generate standardized CSV filename.
    
    Args:
        niche: Business niche (e.g., "plumbers")
        location: Location name (e.g., "Toronto")
        timestamp: Optional timestamp (defaults to now)
    
    Returns:
        Filename string like "plumbers_Toronto_20260109_143022.csv"
    """
    if timestamp is None:
        timestamp = datetime.now()
    
    # Clean niche and location for filename (remove special chars)
    clean_niche = "".join(c if c.isalnum() else "_" for c in niche)
    clean_location = "".join(c if c.isalnum() else "_" for c in location)
    
    # Format: niche_location_YYYYMMDD_HHMMSS.csv
    timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
    
    return f"{clean_niche}_{clean_location}_{timestamp_str}.csv"