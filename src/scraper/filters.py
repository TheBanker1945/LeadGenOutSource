"""Logic to filter companies based on configurable criteria."""

from typing import Literal

# Profile pages that don't count as "real" websites
PROFILE_DOMAINS = [
    "facebook.com",
    "instagram.com",
    "linkedin.com",
    "werkspot.nl",
    "detelefoongids.nl",
    "telefoonboek.nl",
    "drimble.nl",
    "oozo.nl",
    "yelp.com",
    "google.com",
    "schilder-info.nl",
    "openingstijden.nl",
    "goudengids.nl",
    "local.infobel",
    "cylex-bedrijvengids",
    "twitter.com",
    "x.com",
    "youtube.com",
    "trustpilot.com",
    "kvk.nl",
]


FilterOption = Literal["Yes", "No", "Any"]


def is_profile_page(url: str) -> bool:
    """
    Check if a URL is a profile page on a third-party platform.
    
    Args:
        url: Website URL to check.
    
    Returns:
        True if the URL is a profile page, False if it's a real website.
    """
    if not url:
        return False
    
    url_lower = url.lower()
    for domain in PROFILE_DOMAINS:
        if domain in url_lower:
            return True
    return False


def has_real_website(place_data: dict) -> bool:
    """
    Check if a place has a REAL website (not just a profile page).
    
    Args:
        place_data: Place data dictionary from Google Maps API.
    
    Returns:
        True if the place has a real website, False if no website or only a profile page.
    """
    website = place_data.get("websiteUri", "")
    
    # No website at all
    if not website or not website.strip():
        return False
    
    # Has a URL, but it's just a profile page (Facebook, Werkspot, etc.)
    if is_profile_page(website):
        return False
    
    # Has a real website
    return True


def has_any_website(place_data: dict) -> bool:
    """
    Check if a place has any website (including profile pages).
    
    Args:
        place_data: Place data dictionary from Google Maps API.
    
    Returns:
        True if the place has any website URL, False otherwise.
    """
    website = place_data.get("websiteUri", "")
    return bool(website and website.strip())


def has_phone_number(place_data: dict) -> bool:
    """
    Check if a place has a phone number.
    
    Args:
        place_data: Place data dictionary from Google Maps API.
    
    Returns:
        True if the place has a phone number, False otherwise.
    """
    phone = place_data.get("nationalPhoneNumber", "")
    return bool(phone and phone.strip())


def is_operational(place_data: dict) -> bool:
    """
    Check if a business is currently operational.
    
    Args:
        place_data: Place data dictionary from Google Maps API.
    
    Returns:
        True if business status is OPERATIONAL, False otherwise.
    """
    status = place_data.get("businessStatus", "")
    return status == "OPERATIONAL"


def apply_filters(
    place_data: dict,
    has_website_filter: FilterOption = "Any",
    has_phone_filter: FilterOption = "Any",
    operational_only: bool = True
) -> tuple[bool, str]:
    """
    Apply configurable filters to a place.
    
    Args:
        place_data: Place data dictionary from Google Maps API.
        has_website_filter: "Yes" = must have website, "No" = must NOT have website, "Any" = don't care
        has_phone_filter: "Yes" = must have phone, "No" = must NOT have phone, "Any" = don't care
        operational_only: If True, skip non-operational businesses
    
    Returns:
        Tuple of (should_include: bool, reason: str)
        - should_include: True if place passes all filters
        - reason: Human-readable reason for exclusion (empty if included)
    """
    # Check operational status first
    if operational_only and not is_operational(place_data):
        return False, "not operational"
    
    # Check website filter
    has_website = has_real_website(place_data)
    if has_website_filter == "Yes" and not has_website:
        return False, "no website (required)"
    elif has_website_filter == "No" and has_website:
        return False, "has website (excluded)"
    
    # Check phone filter
    has_phone = has_phone_number(place_data)
    if has_phone_filter == "Yes" and not has_phone:
        return False, "no phone (required)"
    elif has_phone_filter == "No" and has_phone:
        return False, "has phone (excluded)"
    
    # Passes all filters
    return True, ""
