# Generic Lead Generation Tool

A powerful, configurable Google Maps scraper for generating business leads with neighborhood-based splitting and bulk processing capabilities.

## 🎯 Features

- **Smart Neighborhood Splitting**: Uses Gemini AI to split cities into 10-15 areas for comprehensive coverage
- **Configurable Filters**: Flexible filtering by website presence, phone availability, and operational status
- **Bulk Processing**: Scrape multiple locations × multiple niches in one run
- **Automatic Deduplication**: SQLite database prevents duplicate entries (by phone number)
- **CSV Export**: Clean, standardized CSV output with all business details
- **API Cost Optimization**: Efficient field masking and pagination
- **Progress Tracking**: Real-time statistics and progress indicators
- **🛡️ Monthly API Limit**: Hard limit of 1000 requests/month prevents unexpected costs (auto-resets monthly)

## 📋 Requirements

- Python 3.10+
- Google Maps API key (Places API - New)
- Gemini API key (for neighborhood splitting, optional)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Create a `.env` file in the project root:

```env
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
GEMINI_API_KEY=your_gemini_api_key
```

### 3. Configure Your Scraping Job

Edit `config.yaml`:

```yaml
locations:
  - "Toronto"
  - "Vancouver"

country: "Canada"

niches:
  - "plumbers"
  - "electricians"

filters:
  has_website: "Any" # Yes/No/Any
  has_phone: "Yes" # Yes/No/Any
  operational_only: true

scraping:
  max_pages_per_area: 1
  use_neighborhood_splitting: true
```

### 4. Run the Scraper

```bash
python main.py
```

## 📁 Project Structure

```
project/
├── main.py                      # Main entry point
├── config.yaml                  # Configuration file
├── requirements.txt             # Python dependencies
├── .env                         # API keys (not in git)
│
├── src/
│   ├── scraper/
│   │   ├── maps_client.py      # Google Maps API client
│   │   ├── filters.py          # Business filtering logic
│   │   └── main.py             # Scraper orchestration
│   │
│   ├── database/
│   │   ├── db_manager.py       # SQLite setup
│   │   └── repository.py       # CRUD operations
│   │
│   └── exporter/
│       └── csv_exporter.py     # CSV export functionality
│
├── utils/
│   └── geo_helper.py           # Neighborhood splitting (Gemini AI)
│
└── output/
    └── csv/                     # Generated CSV files
```

## 🎛️ Configuration Guide

### Filter Options

**`has_website`**: Controls website filtering

- `"Yes"`: Only businesses WITH websites
- `"No"`: Only businesses WITHOUT websites (original use case)
- `"Any"`: All businesses regardless of website

**`has_phone`**: Controls phone number filtering

- `"Yes"`: Only businesses WITH phone numbers
- `"No"`: Only businesses WITHOUT phone numbers
- `"Any"`: All businesses regardless of phone

**`operational_only`**: Skip permanently closed businesses (recommended: `true`)

### Common Use Cases

**Find businesses WITHOUT websites** (original mockup pipeline):

```yaml
filters:
  has_website: "No"
  has_phone: "Yes"
```

**Find ALL businesses**:

```yaml
filters:
  has_website: "Any"
  has_phone: "Any"
```

**Find businesses WITH websites but NO phone**:

```yaml
filters:
  has_website: "Yes"
  has_phone: "No"
```

### Bulk Processing

Process 100 locations × 5 niches = 500 CSV files:

```yaml
locations:
  - "Toronto"
  - "Vancouver"
  - "Montreal"
  # ... add more cities

niches:
  - "plumbers"
  - "electricians"
  - "roofers"
  - "hvac"
  - "landscapers"
```

## 📊 CSV Output Format

Each CSV file contains:

| Column               | Description                   | Source           |
| -------------------- | ----------------------------- | ---------------- |
| Business Name        | Company name                  | Google Maps      |
| Business Address     | Full address                  | Google Maps      |
| Business Website     | Website URL (or profile page) | Google Maps      |
| Operating Hours      | Business hours                | Google Maps      |
| Phone Number         | Contact number                | Google Maps      |
| Email                | Email address                 | ❌ Not available |
| Google Review Rating | Rating (e.g., "4.5/5")        | Google Maps      |

**Note**: Email is not available from Google Maps API and will be empty.

## 🔧 How It Works

1. **Load Configuration**: Reads `config.yaml` for locations, niches, and filters
2. **Initialize Database**: Creates SQLite database for deduplication
3. **Check API Limit**: Verifies monthly request limit hasn't been exceeded
4. **Neighborhood Splitting**: Uses Gemini AI to split each city into 10-15 areas
5. **Scrape Each Area**: Queries Google Maps for businesses in each neighborhood
6. **Track Requests**: Each API call is counted against monthly limit
7. **Apply Filters**: Filters results based on website/phone requirements
8. **Store in Database**: Saves leads (deduplicates by phone number)
9. **Export to CSV**: Generates CSV file for each location×niche combination

## 🛡️ API Cost Protection

### Monthly Request Limit

The tool enforces a **hard limit of 1000 Google Maps API requests per month** to prevent unexpected costs:

- ✅ Limit is tracked in `api_usage.json` (auto-created)
- ✅ Resets automatically at the start of each month
- ✅ Cannot be exceeded - scraping stops when limit reached
- ✅ Warning shown when 80% of limit is used
- ✅ Configurable in `config.yaml`

### Check Current Usage

```bash
python check_usage.py
```

This shows:

- Requests made this month
- Requests remaining
- Usage percentage
- Visual progress bar

### Configure the Limit

Edit `config.yaml`:

```yaml
api_limits:
  monthly_request_limit: 1000 # Change to your desired limit
```

**Note**: Each "page" of results = 1 API request. With 10 neighborhoods and 2 pages each = 20 requests per location×niche.

## 🌍 Supported Countries

Works with any country! Examples:

- 🇨🇦 Canada (`country: "Canada"`)
- 🇺🇸 USA (`country: "USA"`)
- 🇬🇧 UK (`country: "UK"`)
- 🇦🇺 Australia (`country: "Australia"`)
- 🇳🇿 New Zealand (`country: "New Zealand"`)
- 🇳🇱 Netherlands (`country: "Netherlands"`)

## 💡 Tips & Best Practices

1. **Start Small**: Test with 1-2 locations and 1 niche first
2. **Monitor API Costs**: Run `python check_usage.py` to track usage
3. **Use Neighborhood Splitting**: More comprehensive results
4. **Check Rate Limits**: Tool enforces 1000 requests/month automatically
5. **Backup Database**: `leads.db` contains all scraped data
6. **Plan Your Scraping**: 1 location × 1 niche × 10 neighborhoods × 1 page = 10 requests

## 🐛 Troubleshooting

**No results found?**

- Check your filter settings (too restrictive?)
- Verify API keys are correct
- Try `use_neighborhood_splitting: false` for smaller cities

**Duplicate entries?**

- Database automatically deduplicates by phone number
- Check if businesses have the same phone number

**Gemini API errors?**

- Fallback to city-only search (no neighborhoods)
- Check `GEMINI_API_KEY` in `.env`

## 📝 License

This is a refactored version of a specialized scraper, now generalized for any lead generation use case.

## 🙏 Credits

Original specialized scraper built for mockup generation pipeline. Refactored for generic lead generation use cases.
