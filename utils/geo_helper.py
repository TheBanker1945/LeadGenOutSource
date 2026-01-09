"""Geographic helper functions for neighborhood splitting."""

import json
import os
import re

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


def clean_area_name(area: str) -> str:
    """
    Clean area name by removing parentheses and their contents.
    
    Examples:
        "Bijlmer (older sections)" -> "Bijlmer"
        "Noord (NDSM area)" -> "Noord"
    
    Args:
        area: Area name to clean
    
    Returns:
        Cleaned area name
    """
    cleaned = re.sub(r'\s*\(.*?\)', '', area).strip()
    return cleaned if cleaned else area


def get_search_areas(city: str, country: str = "") -> list[str]:
    """
    Use Gemini AI to generate a list of neighborhoods/districts for a city.
    This splits the city into smaller search areas for more comprehensive scraping.
    
    Args:
        city: The city to split into areas (e.g., "Toronto")
        country: The country for context (e.g., "Canada")
    
    Returns:
        List of area names (10-15 neighborhoods). Falls back to just the city if AI fails.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("⚠️  GEMINI_API_KEY not found, using city only")
        return [city]
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-pro")  # Use the stable gemini-pro model
    
    location = f"{city}, {country}" if country else city
    
    prompt = f"""Generate a list of 10-15 neighborhoods or districts within {location}.

PRIORITY: Include industrial areas, working-class neighborhoods, and commercial districts.

CRITICAL RULES:
1. Return ONLY short neighborhood names (1-3 words max)
2. NO descriptions or explanations in parentheses
3. NO phrases like "area", "district", "zone" unless it's the actual name
4. Just the plain neighborhood name as locals would say it

BAD examples: "Bijlmer (older sections)", "Noord (NDSM area)", "Westpoort industrial zone"
GOOD examples: "Bijlmer", "Noord", "Westpoort", "Sloterdijk", "De Pijp"

Return ONLY a valid JSON array of strings:"""

    try:
        print(f"\n🤖 Asking Gemini for neighborhoods in {location}...")
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean up response - remove markdown code blocks if present
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()
        
        areas = json.loads(response_text)
        
        if isinstance(areas, list) and len(areas) > 0:
            # Clean each area name
            areas = [clean_area_name(area) for area in areas]
            print(f"✅ Found {len(areas)} areas: {', '.join(areas)}")
            return areas
        else:
            raise ValueError("Invalid response format")
            
    except (json.JSONDecodeError, ValueError, Exception) as e:
        print(f"⚠️  Gemini parsing failed ({e}), using city only")
        return [city]