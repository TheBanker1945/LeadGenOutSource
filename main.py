"""
Generic Lead Generation Tool
Scrapes Google Maps for business leads with configurable filters.
"""

import sys
from datetime import datetime
from pathlib import Path

import yaml

from src.database.db_manager import init_db
from src.database.repository import LeadRepository
from src.exporter.csv_exporter import export_to_csv, generate_csv_filename, format_operating_hours, format_rating
from src.scraper.main import run_scraper
from src.scraper.rate_limiter import RequestLimitExceeded
from utils.geo_helper import get_search_areas


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError:
        print(f"❌ Config file not found: {config_path}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"❌ Error parsing config file: {e}")
        sys.exit(1)


def export_leads_to_csv(
    niche: str,
    location: str,
    output_dir: str,
    include_headers: bool = True
) -> tuple[int, str]:
    """
    Export all leads for a specific niche/location to CSV.
    
    Returns:
        Tuple of (lead_count, csv_path)
    """
    repo = LeadRepository()
    
    # Get all leads for this niche/location
    leads = repo.get_all_leads(city=location, niche=niche)
    
    if not leads:
        return 0, ""
    
    # Prepare leads for CSV export (format fields properly)
    formatted_leads = []
    for lead in leads:
        formatted_lead = {
            "company_name": lead.get("company_name", ""),
            "address": lead.get("address", ""),
            "website": lead.get("website", ""),
            "phone": lead.get("phone", ""),
            "rating": format_rating(lead.get("rating")),
            "operating_hours": lead.get("operating_hours", ""),
        }
        formatted_leads.append(formatted_lead)
    
    # Generate filename and export
    filename = generate_csv_filename(niche, location)
    output_path = Path(output_dir) / filename
    
    count = export_to_csv(formatted_leads, output_path, include_headers=include_headers)
    
    return count, str(output_path)


def main():
    """Main entry point for the lead generation tool."""
    print("=" * 70)
    print("🚀 GENERIC LEAD GENERATION TOOL")
    print("=" * 70)
    
    # Load configuration
    print("\n📋 Loading configuration...")
    config = load_config()
    
    # Extract configuration
    locations = config.get("locations", [])
    country = config.get("country", "")
    niches = config.get("niches", [])
    
    filters = config.get("filters", {})
    has_website_filter = filters.get("has_website", "Any")
    has_phone_filter = filters.get("has_phone", "Any")
    operational_only = filters.get("operational_only", True)
    
    scraping_settings = config.get("scraping", {})
    max_pages = scraping_settings.get("max_pages_per_area", 1)
    use_neighborhood_splitting = scraping_settings.get("use_neighborhood_splitting", True)
    language_code = scraping_settings.get("language_code", "en")
    
    # API limits
    api_limits = config.get("api_limits", {})
    monthly_request_limit = api_limits.get("monthly_request_limit", 1000)
    
    output_settings = config.get("output", {})
    csv_output_dir = output_settings.get("csv_output_dir", "output/csv")
    include_headers = output_settings.get("include_headers", True)
    
    # Validate configuration
    if not locations:
        print("❌ No locations specified in config.yaml")
        sys.exit(1)
    if not niches:
        print("❌ No niches specified in config.yaml")
        sys.exit(1)
    
    print(f"✅ Locations: {len(locations)}")
    print(f"✅ Niches: {len(niches)}")
    print(f"✅ Filters: Website={has_website_filter}, Phone={has_phone_filter}, Operational={operational_only}")
    print(f"✅ Monthly API Limit: {monthly_request_limit} requests")
    print(f"✅ Output directory: {csv_output_dir}")
    
    # Initialize database
    print("\n🔧 Initializing database...")
    init_db()
    
    # Calculate total combinations
    total_combinations = len(locations) * len(niches)
    current_combination = 0
    
    print(f"\n📊 Total scraping jobs: {total_combinations}")
    print(f"    ({len(locations)} locations × {len(niches)} niches)")
    
    # Overall statistics
    overall_stats = {
        "total_scraped": 0,
        "total_saved": 0,
        "total_csvs": 0,
        "failed_jobs": 0
    }
    
    start_time = datetime.now()
    
    # Process each location × niche combination
    for location in locations:
        for niche in niches:
            current_combination += 1
            
            print(f"\n{'='*70}")
            print(f"📍 Job {current_combination}/{total_combinations}: {niche} in {location}")
            print(f"{'='*70}")
            
            try:
                # Determine search areas
                if use_neighborhood_splitting:
                    search_areas = get_search_areas(location, country)
                else:
                    search_areas = [location]
                
                print(f"🔍 Searching in {len(search_areas)} area(s)...")
                
                # Scrape each area
                job_stats = {
                    "total": 0,
                    "saved": 0,
                    "duplicates": 0
                }
                
                for i, area in enumerate(search_areas, 1):
                    print(f"\n  📌 Area {i}/{len(search_areas)}: {area}")
                    
                    # Run scraper for this area
                    area_stats = run_scraper(
                        city=area,
                        niche=niche,
                        max_pages=max_pages,
                        country=country,
                        has_website_filter=has_website_filter,
                        has_phone_filter=has_phone_filter,
                        operational_only=operational_only,
                        monthly_limit=monthly_request_limit,
                        language_code=language_code
                    )
                    
                    # Aggregate statistics
                    job_stats["total"] += area_stats.get("total", 0)
                    job_stats["saved"] += area_stats.get("saved", 0)
                    job_stats["duplicates"] += area_stats.get("duplicates", 0)
                
                # Export to CSV
                print(f"\n💾 Exporting results to CSV...")
                lead_count, csv_path = export_leads_to_csv(
                    niche=niche,
                    location=location,
                    output_dir=csv_output_dir,
                    include_headers=include_headers
                )
                
                if lead_count > 0:
                    print(f"✅ Exported {lead_count} leads to: {csv_path}")
                    overall_stats["total_csvs"] += 1
                else:
                    print(f"⚠️  No leads found for this combination")
                
                # Update overall statistics
                overall_stats["total_scraped"] += job_stats["total"]
                overall_stats["total_saved"] += job_stats["saved"]
                RequestLimitExceeded as e:
                print(f"\n{'='*70}")
                print(f"🛑 STOPPING: Monthly API limit reached")
                print(f"{'='*70}")
                print(f"Processed {current_combination - 1} out of {total_combinations} jobs before hitting limit")
                print(f"The limit will reset at the start of next month")
                print(f"{'='*70}\n")
                overall_stats["failed_jobs"] += 1
                break  # Stop processing entirely
                
            except 
            except Exception as e:
                print(f"❌ Error processing {niche} in {location}: {e}")
                overall_stats["failed_jobs"] += 1
                continue
    
    # Final summary
    end_time = datetime.now()
    duration = end_time - start_time
    
    print(f"\n{'='*70}")
    print("🎉 SCRAPING COMPLETE!")
    print(f"{'='*70}")
    print(f"⏱️  Total time: {duration}")
    print(f"📊 Jobs completed: {current_combination - overall_stats['failed_jobs']}/{total_combinations}")
    print(f"🔍 Total results scraped: {overall_stats['total_scraped']}")
    print(f"💾 Total leads saved: {overall_stats['total_saved']}")
    print(f"📄 CSV files created: {overall_stats['total_csvs']}")
    
    if overall_stats["failed_jobs"] > 0:
        print(f"⚠️  Failed jobs: {overall_stats['failed_jobs']}")
    
    print(f"\n📁 Output directory: {csv_output_dir}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()