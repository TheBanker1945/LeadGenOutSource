"""
Lead Generation Dashboard
Web-based interface for the Generic Lead Generation Tool
"""

import streamlit as st
import pandas as pd
import yaml
from pathlib import Path
from datetime import datetime
import sys
import os

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.db_manager import init_db, get_connection
from src.database.repository import LeadRepository
from src.scraper.rate_limiter import RateLimiter, RequestLimitExceeded
from src.scraper.main import run_scraper
from src.exporter.csv_exporter import export_to_csv, generate_csv_filename, format_rating
from auth import AuthManager

# Try to import geo_helper, but make it optional
try:
    from utils.geo_helper import get_search_areas
    NEIGHBORHOOD_SPLITTING_AVAILABLE = True
except ImportError:
    NEIGHBORHOOD_SPLITTING_AVAILABLE = False
    st.warning("⚠️ Neighborhood splitting feature unavailable (google-generativeai not installed). Disable 'enable_neighborhoods' in config.")

# Page config
st.set_page_config(
    page_title="Lead Generation Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# AUTHENTICATION CHECK - Must be logged in to access dashboard
# ============================================================================
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.error("🔒 **Access Denied** - You must be logged in to access the dashboard")
    st.info("👉 Please return to the login page")
    st.stop()

# ============================================================================
# END AUTHENTICATION CHECK
# ============================================================================

# Auto-refresh for real-time monitoring (refreshes every 30 seconds)
import time
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = time.time()

# Add refresh button and auto-refresh timer
col_refresh1, col_refresh2 = st.columns([6, 1])
with col_refresh2:
    if st.button("🔄 Refresh", help="Manually refresh data"):
        st.rerun()

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        color: #856404;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'scraping_active' not in st.session_state:
    st.session_state.scraping_active = False
if 'last_scrape_result' not in st.session_state:
    st.session_state.last_scrape_result = None


def load_config():
    """Load configuration from YAML file."""
    try:
        with open("config.yaml", "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        st.error("❌ config.yaml not found!")
        return None


def save_config(config):
    """Save configuration to YAML file."""
    with open("config.yaml", "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)


def get_usage_stats():
    """Get API usage statistics."""
    config = load_config()
    if not config:
        return None
    
    # Get monthly limit from environment variable or config (fallback to 1000)
    monthly_limit = int(os.getenv('MONTHLY_API_LIMIT', 
                                   config.get("api_limits", {}).get("monthly_request_limit", 1000)))
    limiter = RateLimiter(monthly_limit=monthly_limit)
    return limiter.get_usage_stats()


def get_leads_dataframe():
    """Get all leads as a pandas DataFrame."""
    init_db()
    repo = LeadRepository()
    leads = repo.get_all_leads()
    
    if not leads:
        return pd.DataFrame()
    
    # Convert to DataFrame
    df = pd.DataFrame(leads)
    
    # Extract main city from city field (remove neighborhood details)
    # e.g., "Scheveningen, Den Haag" -> "Den Haag"
    # e.g., "Etobicoke" -> "Toronto" (Toronto neighborhoods without city suffix)
    def extract_main_city(city_str):
        if pd.isna(city_str) or not city_str:
            return ""
        city_str = str(city_str).strip()
        
        # If city contains comma, take the part after comma (main city)
        if ',' in city_str:
            return city_str.split(',')[-1].strip()
        
        # Handle Toronto neighborhoods (they don't have ", Toronto" suffix)
        toronto_neighborhoods = ['Etobicoke', 'Scarborough', 'North York', 'Downtown', 'Yorkville', 
                                'Entertainment District', 'Financial District', 'Junction Triangle',
                                'Kensington Market', 'The Annex', 'The Beaches', 'Leslieville',
                                'Liberty Village', 'Parkdale', 'Mimico', 'Weston']
        if city_str in toronto_neighborhoods:
            return 'Toronto'
        
        # Handle Calgary neighborhoods
        calgary_neighborhoods = ['Beltline', 'Crescent Heights', 'Inglewood', 'Kensington', 'Sunalta',
                               'Bridgeland', 'East Village', 'Forest Lawn', 'Manchester', 'Ogden',
                               'Alyth/Bonnybrook', 'Acadia', 'Midnapore', 'Montgomery']
        if city_str in calgary_neighborhoods:
            return 'Calgary'
        
        # Handle Miami neighborhoods
        miami_neighborhoods = ['Brickell', 'Coconut Grove', 'Edgewater', 'Wynwood', 'Little Havana',
                              'South Beach', 'Overtown', 'Little Haiti', 'Liberty City', 'Allapattah',
                              'West Little River', 'Doral', 'Hialeah', 'Medley', 'Opa-locka', 'Sweetwater']
        if city_str in miami_neighborhoods:
            return 'Miami'
        
        # Handle New York neighborhoods
        ny_neighborhoods = ['Sunset Park', 'Long Island City', 'Bushwick', 'Red Hook', 'Chinatown',
                           'The Garment District', 'Mott Haven', 'Astoria', 'DUMBO', 'Hunts Point',
                           'Jamaica', 'Washington Heights', 'East Harlem', 'Concourse']
        if city_str in ny_neighborhoods:
            return 'New York'
        
        # Otherwise, return as is (it's already a main city)
        return city_str
    
    df['main_city'] = df['city'].apply(extract_main_city)
    
    # Select and rename columns for display
    display_columns = {
        'id': 'ID',
        'company_name': 'Business Name',
        'address': 'Address',
        'city': 'City',
        'phone': 'Phone',
        'website': 'Website',
        'niche': 'Niche',
        'rating': 'Rating',
        'operating_hours': 'Hours',
        'created_at': 'Added On',
        'main_city': 'Main City'
    }
    
    df = df[list(display_columns.keys())].rename(columns=display_columns)
    
    # Format rating
    df['Rating'] = df['Rating'].apply(lambda x: f"{x}/5" if pd.notna(x) else "N/A")
    
    return df


def export_leads_ui(niche=None, city=None):
    """Export leads to CSV - returns CSV data and count for browser download only."""
    repo = LeadRepository()
    leads = repo.get_all_leads(city=city, niche=niche)
    
    if not leads:
        return None, 0
    
    # Format leads for export
    formatted_leads = []
    for lead in leads:
        formatted_lead = {
            "Company Name": lead.get("company_name", ""),
            "Address": lead.get("address", ""),
            "Website": lead.get("website", ""),
            "Phone": lead.get("phone", ""),
            "Rating": format_rating(lead.get("rating")),
            "Operating Hours": lead.get("operating_hours", ""),
        }
        formatted_leads.append(formatted_lead)
    
    # Generate CSV data in memory (no file saving)
    import io
    import csv
    
    output = io.StringIO()
    if formatted_leads:
        fieldnames = formatted_leads[0].keys()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(formatted_leads)
    
    csv_data = output.getvalue()
    
    # Generate filename for download
    location_str = city if city else "all_locations"
    niche_str = niche if niche else "all_niches"
    filename = generate_csv_filename(niche_str, location_str)
    
    return csv_data, len(formatted_leads), filename


# ============================================================================
# SIDEBAR - Configuration
# ============================================================================

st.sidebar.title("⚙️ Configuration")

# Add logout button at the top of sidebar
st.sidebar.markdown("---")
user_display = st.session_state.get('username', 'User')
st.sidebar.info(f"👤 Logged in as: **{user_display}**")
if st.sidebar.button("🔓 Logout", use_container_width=True):
    st.session_state.authenticated = False
    st.session_state.auth_token = None
    st.session_state.username = None
    st.rerun()
st.sidebar.markdown("---")

# Load config
config = load_config()
if not config:
    st.stop()

# Locations
st.sidebar.subheader("📍 Locations")
locations_text = st.sidebar.text_area(
    "Enter locations (one per line)",
    value="\n".join(config.get("locations", [])),
    height=100
)
locations = [loc.strip() for loc in locations_text.split("\n") if loc.strip()]

country = st.sidebar.text_input(
    "Country",
    value=config.get("country", "")
)

# Niches
st.sidebar.subheader("🎯 Niches")
niches_text = st.sidebar.text_area(
    "Enter niches (one per line)",
    value="\n".join(config.get("niches", [])),
    height=100
)
niches = [niche.strip() for niche in niches_text.split("\n") if niche.strip()]

# Filters
st.sidebar.subheader("🔍 Filters")
has_website = st.sidebar.selectbox(
    "Website Requirement",
    ["Any", "Yes", "No"],
    index=["Any", "Yes", "No"].index(config.get("filters", {}).get("has_website", "Any"))
)

has_phone = st.sidebar.selectbox(
    "Phone Requirement",
    ["Any", "Yes", "No"],
    index=["Any", "Yes", "No"].index(config.get("filters", {}).get("has_phone", "Yes"))
)

operational_only = st.sidebar.checkbox(
    "Operational Only",
    value=config.get("filters", {}).get("operational_only", True)
)

# Scraping Settings
st.sidebar.subheader("⚡ Scraping Settings")
# Max pages is now fixed at 1 (removed from UI)
max_pages = 1

lead_limit = st.sidebar.number_input(
    "Lead Limit (per scrape)",
    min_value=0,
    max_value=10000,
    value=config.get("scraping", {}).get("lead_limit", 0),
    help="Maximum number of leads to save per scraping session. Set to 0 for no limit."
)

# Convert 0 to None for no limit
lead_limit = None if lead_limit == 0 else lead_limit

# Save button
if st.sidebar.button("💾 Save Configuration", type="primary"):
    new_config = {
        "locations": locations,
        "country": country,
        "niches": niches,
        "filters": {
            "has_website": has_website,
            "has_phone": has_phone,
            "operational_only": operational_only
        },
        "scraping": {
            "max_pages_per_area": 1,
            "lead_limit": 0 if lead_limit is None else lead_limit,
            "use_neighborhood_splitting": config.get("scraping", {}).get("use_neighborhood_splitting", True),
            "language_code": config.get("scraping", {}).get("language_code", "en")
        },
        "api_limits": {
            "monthly_request_limit": int(os.getenv('MONTHLY_API_LIMIT', 1000))
        },
        "output": config.get("output", {
            "csv_output_dir": "output/csv",
            "include_headers": True
        })
    }
    save_config(new_config)
    st.sidebar.success("✅ Configuration saved!")
    st.rerun()

# ============================================================================
# MAIN CONTENT
# ============================================================================

st.markdown('<h1 class="main-header">🚀 Lead Generation Dashboard</h1>', unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "▶️ Scraper", "📋 Leads", "📤 Export"])

# ============================================================================
# TAB 1: Overview
# ============================================================================

with tab1:
    st.header("📊 System Overview")
    
    # API Usage
    col1, col2, col3, col4 = st.columns(4)
    
    usage_stats = get_usage_stats()
    if usage_stats:
        with col1:
            st.metric(
                "Requests Made",
                usage_stats['requests_made'],
                delta=f"{usage_stats['percentage_used']}% used"
            )
        
        with col2:
            st.metric(
                "Requests Remaining",
                usage_stats['requests_remaining'],
                delta=f"of {usage_stats['monthly_limit']}"
            )
        
        with col3:
            st.metric(
                "Current Month",
                usage_stats['month'],
                delta="Auto-resets monthly"
            )
        
        with col4:
            # Progress color based on usage
            if usage_stats['percentage_used'] >= 90:
                progress_color = "🔴"
            elif usage_stats['percentage_used'] >= 75:
                progress_color = "🟡"
            else:
                progress_color = "🟢"
            
            st.metric(
                "Status",
                f"{progress_color} {usage_stats['percentage_used']}%",
                delta="Usage Level"
            )
    
    # Progress Bar
    if usage_stats:
        st.subheader("API Usage Progress")
        progress_value = usage_stats['requests_made'] / usage_stats['monthly_limit']
        st.progress(progress_value)
        
        # Warning messages
        if usage_stats['percentage_used'] >= 90:
            st.markdown(
                '<div class="error-box">⚠️ <strong>Critical:</strong> You\'ve used 90%+ of your monthly limit!</div>',
                unsafe_allow_html=True
            )
        elif usage_stats['percentage_used'] >= 75:
            st.markdown(
                '<div class="warning-box">⚠️ <strong>Warning:</strong> You\'ve used 75%+ of your monthly limit.</div>',
                unsafe_allow_html=True
            )
    
    st.divider()
    
    # Database Stats
    st.subheader("📊 Database Statistics")
    
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    is_postgres = bool(os.getenv("DATABASE_URL"))
    
    # Total leads
    cursor.execute("SELECT COUNT(*) as count FROM leads")
    result = cursor.fetchone()
    total_leads = result['count'] if is_postgres else result[0]
    
    # Leads with website
    cursor.execute("SELECT COUNT(*) as count FROM leads WHERE website IS NOT NULL AND website != ''")
    result = cursor.fetchone()
    leads_with_website = result['count'] if is_postgres else result[0]
    
    # Leads with phone
    cursor.execute("SELECT COUNT(*) as count FROM leads WHERE phone IS NOT NULL AND phone != ''")
    result = cursor.fetchone()
    leads_with_phone = result['count'] if is_postgres else result[0]
    
    # Recent leads (last 24 hours) - use INTERVAL for PostgreSQL compatibility
    if is_postgres:
        cursor.execute("SELECT COUNT(*) as count FROM leads WHERE created_at >= NOW() - INTERVAL '1 day'")
    else:
        cursor.execute("SELECT COUNT(*) as count FROM leads WHERE datetime(created_at) >= datetime('now', '-1 day')")
    result = cursor.fetchone()
    recent_leads = result['count'] if is_postgres else result[0]
    
    # Leads by niche
    cursor.execute("SELECT niche, COUNT(*) as count FROM leads GROUP BY niche ORDER BY count DESC")
    niche_counts = cursor.fetchall()
    
    # Leads by city
    cursor.execute("SELECT city, COUNT(*) as count FROM leads GROUP BY city ORDER BY count DESC LIMIT 10")
    city_counts = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    # Top metrics row
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    
    with metric_col1:
        st.metric("Total Leads", total_leads)
    
    with metric_col2:
        st.metric("With Website", leads_with_website, delta=f"{int(leads_with_website/total_leads*100) if total_leads > 0 else 0}%")
    
    with metric_col3:
        st.metric("With Phone", leads_with_phone, delta=f"{int(leads_with_phone/total_leads*100) if total_leads > 0 else 0}%")
    
    with metric_col4:
        st.metric("Added (24h)", recent_leads, delta="Recent activity")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Leads by Niche")
        if niche_counts:
            niche_df = pd.DataFrame(niche_counts, columns=['Niche', 'Count'])
            st.dataframe(niche_df, use_container_width=True, hide_index=True)
        else:
            st.info("No leads yet")
    
    with col2:
        st.subheader("Top 10 Cities")
        if city_counts:
            city_df = pd.DataFrame(city_counts, columns=['City', 'Count'])
            st.dataframe(city_df, use_container_width=True, hide_index=True)

# ============================================================================
# TAB 2: Scraper
# ============================================================================

with tab2:
    st.header("▶️ Lead Scraper")
    
    # Current configuration summary
    st.subheader("Current Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"""
        **Locations:** {len(locations)}  
        **Country:** {country or 'Not specified'}  
        **Niches:** {len(niches)}  
        """)
    
    with col2:
        lead_limit_display = f"{lead_limit} leads" if lead_limit else "No limit"
        st.info(f"""
        **Filters:** Website={has_website}, Phone={has_phone}  
        **Lead Limit:** {lead_limit_display}  
        **Neighborhood Splitting:** {'Enabled' if config.get('scraping', {}).get('use_neighborhood_splitting', True) else 'Disabled'}  
        """)
    
    # Estimated requests
    st.subheader("📊 Estimated API Usage")
    
    if config.get('scraping', {}).get('use_neighborhood_splitting', True):
        avg_neighborhoods = 10
        estimated_requests = len(locations) * len(niches) * avg_neighborhoods * max_pages
    else:
        estimated_requests = len(locations) * len(niches) * max_pages
    
    usage_stats = get_usage_stats()
    if usage_stats:
        remaining = usage_stats['requests_remaining']
        
        if estimated_requests <= remaining:
            st.success(f"✅ Estimated {estimated_requests} requests (within limit of {remaining} remaining)")
        else:
            st.error(f"⚠️ Estimated {estimated_requests} requests EXCEEDS remaining limit of {remaining}")
            st.warning("Scraping will stop when limit is reached. Consider reducing locations, niches, or pages.")
    
    st.divider()
    
    # Scraping controls
    st.subheader("🎮 Scraping Controls")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        start_button = st.button(
            "🚀 Start Scraping",
            type="primary",
            disabled=st.session_state.scraping_active or not locations or not niches,
            use_container_width=True
        )
    
    with col2:
        if st.button("🔄 Refresh Status", use_container_width=True):
            st.rerun()
    
    with col3:
        if st.button("📊 Check Usage", use_container_width=True):
            st.rerun()
    
    # Start scraping
    if start_button:
        st.session_state.scraping_active = True
        
        # Get monthly limit from config
        config = load_config()
        monthly_limit = int(os.getenv('MONTHLY_API_LIMIT',
                                       config.get("api_limits", {}).get("monthly_request_limit", 1000)))
        language_code = config.get("scraping", {}).get("language_code", "en")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        total_jobs = len(locations) * len(niches)
        current_job = 0
        
        overall_stats = {
            "total_scraped": 0,
            "total_saved": 0,
            "failed_jobs": 0,
            "limit_reached": False
        }
        
        # Track cumulative leads for global limit
        cumulative_saved = 0
        
        # Initialize database
        init_db()
        
        try:
            for location in locations:
                for niche in niches:
                    # Check if global lead limit reached
                    if lead_limit and cumulative_saved >= lead_limit:
                        overall_stats["limit_reached"] = True
                        status_text.text(f"⚠️ Lead limit of {lead_limit} reached! Stopping scraper...")
                        break
                    
                    current_job += 1
                    progress = current_job / total_jobs
                    progress_bar.progress(progress)
                    
                    status_text.text(f"Processing {current_job}/{total_jobs}: {niche} in {location} (Saved: {cumulative_saved}/{lead_limit or '∞'})")
                    
                    try:
                        # Get search areas
                        use_neighborhood_splitting = config.get('scraping', {}).get('use_neighborhood_splitting', True)
                        if use_neighborhood_splitting:
                            search_areas = get_search_areas(location, country)
                        else:
                            search_areas = [location]
                        
                        # Scrape each area
                        for area in search_areas:
                            # Check if global lead limit reached before each area
                            if lead_limit and cumulative_saved >= lead_limit:
                                overall_stats["limit_reached"] = True
                                break
                            
                            # Calculate remaining leads for this area
                            remaining_limit = None
                            if lead_limit:
                                remaining_limit = lead_limit - cumulative_saved
                            
                            # If using neighborhood splitting, pass the main city
                            main_city_param = location if (use_neighborhood_splitting and area != location) else None
                            
                            area_stats = run_scraper(
                                city=area,
                                niche=niche,
                                max_pages=max_pages,
                                country=country,
                                has_website_filter=has_website,
                                has_phone_filter=has_phone,
                                operational_only=operational_only,
                                monthly_limit=monthly_limit,
                                main_city=main_city_param,
                                language_code=language_code,
                                lead_limit=remaining_limit
                            )
                            
                            overall_stats["total_scraped"] += area_stats.get("total", 0)
                            overall_stats["total_saved"] += area_stats.get("saved", 0)
                            cumulative_saved += area_stats.get("saved", 0)
                            
                            # Check if limit was reached in this area
                            if area_stats.get("limit_reached"):
                                overall_stats["limit_reached"] = True
                                break
                    
                    except RequestLimitExceeded:
                        st.error("🚫 Monthly API limit reached! Scraping stopped.")
                        overall_stats["failed_jobs"] += 1
                        break
                    
                    except Exception as e:
                        st.warning(f"⚠️ Error processing {niche} in {location}: {str(e)}")
                        overall_stats["failed_jobs"] += 1
                
                # Break outer loop if limit reached
                if overall_stats.get("limit_reached"):
                    break
            
            # Success
            progress_bar.progress(1.0)
            status_text.empty()
            
            # Show success message with limit info if applicable
            limit_msg = ""
            if overall_stats.get("limit_reached"):
                limit_msg = f'<br>⚠️ <strong>Lead limit reached:</strong> Stopped at {lead_limit} leads'
            
            st.markdown(
                f'<div class="success-box">'
                f'<strong>✅ Scraping Complete!</strong><br>'
                f'Total results: {overall_stats["total_scraped"]}<br>'
                f'Leads saved: {overall_stats["total_saved"]}<br>'
                f'Failed jobs: {overall_stats["failed_jobs"]}'
                f'{limit_msg}'
                f'</div>',
                unsafe_allow_html=True
            )
            
            st.session_state.last_scrape_result = overall_stats
        
        except Exception as e:
            st.error(f"❌ Scraping error: {str(e)}")
        
        finally:
            st.session_state.scraping_active = False
    
    # Show last result
    if st.session_state.last_scrape_result:
        st.divider()
        st.subheader("📊 Last Scraping Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Scraped", st.session_state.last_scrape_result["total_scraped"])
        with col2:
            st.metric("Leads Saved", st.session_state.last_scrape_result["total_saved"])
        with col3:
            st.metric("Failed Jobs", st.session_state.last_scrape_result["failed_jobs"])

# ============================================================================
# TAB 3: Leads
# ============================================================================

with tab3:
    st.header("📋 Leads Database")
    
    # Get leads
    df = get_leads_dataframe()
    
    if df.empty:
        st.info("No leads in database yet. Start scraping to collect leads!")
    else:
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_term = st.text_input("🔍 Search", placeholder="Search business name, city, phone...")
        
        with col2:
            filter_niche = st.selectbox("Filter by Niche", ["All"] + sorted(df['Niche'].unique().tolist()))
        
        with col3:
            # Use Main City for filtering (shows only base cities, not neighborhoods)
            filter_city = st.selectbox("Filter by City", ["All"] + sorted(df['Main City'].unique().tolist()))
        
        # Apply filters
        filtered_df = df.copy()
        
        if search_term:
            filtered_df = filtered_df[
                filtered_df.apply(lambda row: search_term.lower() in str(row).lower(), axis=1)
            ]
        
        if filter_niche != "All":
            filtered_df = filtered_df[filtered_df['Niche'] == filter_niche]
        
        if filter_city != "All":
            filtered_df = filtered_df[filtered_df['Main City'] == filter_city]
        
        # Display stats
        st.metric("Total Leads Shown", len(filtered_df))
        
        # Hide Main City column from display (only used for filtering)
        display_df = filtered_df.drop(columns=['Main City'])
        
        # Display table
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            height=500
        )

# ============================================================================
# TAB 4: Export
# ============================================================================

with tab4:
    st.header("📤 Export Leads")
    
    st.subheader("Export Options")
    
    # Get actual niches and cities from database
    db_df = get_leads_dataframe()
    
    if db_df.empty:
        st.info("No leads in database yet. Start scraping to collect leads!")
    else:
        available_niches = sorted(db_df['Niche'].unique().tolist())
        available_cities = sorted(db_df['Main City'].unique().tolist())
        
        col1, col2 = st.columns(2)
        
        with col1:
            export_niche = st.selectbox(
                "Select Niche",
                ["All Niches"] + available_niches,
                key="export_niche"
            )
        
        with col2:
            export_city = st.selectbox(
                "Select City",
                ["All Cities"] + available_cities,
                key="export_city"
            )
        
        # Preview
        niche_filter = None if export_niche == "All Niches" else export_niche
        city_filter = None if export_city == "All Cities" else export_city
        
        repo = LeadRepository()
        preview_leads = repo.get_all_leads(city=city_filter, niche=niche_filter)
        
        st.info(f"📊 {len(preview_leads)} leads will be exported")
        
        # Export button
        if st.button("📥 Export to CSV", type="primary", use_container_width=True):
            if not preview_leads:
                st.warning("No leads to export with selected filters!")
            else:
                csv_data, count, filename = export_leads_ui(niche=niche_filter, city=city_filter)
                
                if csv_data:
                    st.success(f"✅ Ready to download {count} leads!")
                    
                    st.download_button(
                        label="💾 Download CSV File",
                        data=csv_data,
                        file_name=filename,
                        mime="text/csv",
                        use_container_width=True
                    )
        
        st.divider()
        
        # Quick export all
        st.subheader("📦 Bulk Export")
        
        if st.button("📥 Export ALL Leads", use_container_width=True):
            csv_data, count, filename = export_leads_ui()
            
            if csv_data:
                st.success(f"✅ Ready to download {count} leads!")
                
                st.download_button(
                    label="💾 Download All Leads CSV",
                    data=csv_data,
                    file_name=filename,
                    mime="text/csv",
                    use_container_width=True
                )

# Footer
st.divider()
st.markdown(
    """
    <div style="text-align: center; color: #888; padding: 1rem;">
        <small>Lead Generation Dashboard v1.0 | Built with Streamlit</small>
    </div>
    """,
    unsafe_allow_html=True
)
