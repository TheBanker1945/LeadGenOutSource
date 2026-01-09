# Migration Guide: Old System → New Generic Tool

If you were using the old specialized scraper (for finding businesses WITHOUT websites), here's what changed and how to migrate.

---

## 🔄 What Changed?

### Old System (Specialized)

- **Purpose**: Find businesses WITHOUT websites for mockup generation
- **Filters**: Hardcoded (skip websites, require phone)
- **Configuration**: Had to edit Python code
- **Output**: SQLite database only
- **Use Case**: Single-purpose mockup pipeline

### New System (Generic)

- **Purpose**: Find ANY type of business with ANY filtering criteria
- **Filters**: Configurable via YAML (Yes/No/Any)
- **Configuration**: Edit `config.yaml` file
- **Output**: SQLite database + CSV export
- **Use Case**: Multi-purpose lead generation

---

## 🆕 New Features You Get

1. **CSV Export**: Automatic CSV files after scraping
2. **Flexible Filters**: Choose website/phone requirements
3. **More Data Fields**: Address, rating, operating hours
4. **Bulk Processing**: Multiple locations × multiple niches
5. **Better Progress**: Real-time stats and progress tracking
6. **Easy Configuration**: No code changes needed

---

## 📋 Migration Steps

### Step 1: Update Your .env File

**Old** `.env`:

```env
GOOGLE_MAPS_API_KEY=your_key
```

**New** `.env` (add Gemini key):

```env
GOOGLE_MAPS_API_KEY=your_key
GEMINI_API_KEY=your_gemini_key  # NEW: For neighborhood splitting
```

### Step 2: Create config.yaml

**Old**: You edited Python code directly

**New**: Create `config.yaml`:

```yaml
# To replicate OLD behavior (businesses WITHOUT websites):
locations:
  - "Amsterdam"

country: "Netherlands"

niches:
  - "painters"

filters:
  has_website: "No" # Same as old hardcoded filter
  has_phone: "Yes" # Same as old hardcoded filter
  operational_only: true

scraping:
  max_pages_per_area: 1
  use_neighborhood_splitting: true

output:
  csv_output_dir: "output/csv"
  include_headers: true
```

### Step 3: Update Database (Automatic)

The new system automatically adds new columns to your database:

- `address`
- `rating`
- `operating_hours`

Your existing data is preserved!

### Step 4: Run the New System

**Old**:

```python
# You had to write custom code like:
from scraper import run_scraper
stats = run_scraper("Amsterdam", "painters", max_pages=1, country="Netherlands")
```

**New**:

```bash
# Just run main script with config:
python main.py
```

---

## 🔧 Code Changes (If You Integrated the Old System)

### If You Called `run_scraper()` Directly

**Old Code**:

```python
from src.scraper.main import run_scraper

stats = run_scraper(
    city="Amsterdam",
    niche="painters",
    max_pages=1,
    country="Netherlands"
)
```

**New Code** (add filter parameters):

```python
from src.scraper.main import run_scraper

stats = run_scraper(
    city="Amsterdam",
    niche="painters",
    max_pages=1,
    country="Netherlands",
    has_website_filter="No",   # NEW
    has_phone_filter="Yes",    # NEW
    operational_only=True      # NEW
)
```

### If You Used Filters

**Old Code**:

```python
from src.scraper.filters import has_real_website, is_operational

if has_real_website(place):
    continue  # Skip businesses WITH websites
```

**New Code**:

```python
from src.scraper.filters import apply_filters

should_include, reason = apply_filters(
    place,
    has_website_filter="No",
    has_phone_filter="Yes",
    operational_only=True
)

if not should_include:
    continue  # Skip based on configurable filters
```

### If You Accessed the Database

**Old Code**:

```python
from src.database.repository import LeadRepository

repo = LeadRepository()
leads = repo.get_pending_mockups()  # Only status='NEW'
```

**New Code**:

```python
from src.database.repository import LeadRepository

repo = LeadRepository()

# Get ALL leads (not just status='NEW')
all_leads = repo.get_all_leads()

# Or filter by city/niche:
city_leads = repo.get_all_leads(city="Amsterdam", niche="painters")

# Old method still works:
pending = repo.get_pending_mockups()  # Still exists
```

---

## 📊 Database Schema Changes

### Old Schema:

```sql
CREATE TABLE leads (
    id INTEGER PRIMARY KEY,
    company_name TEXT,
    city TEXT,
    phone TEXT UNIQUE,
    website TEXT,
    niche TEXT,
    status TEXT DEFAULT 'NEW',
    mockup_path TEXT,
    laptop_mockup_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### New Schema:

```sql
CREATE TABLE leads (
    id INTEGER PRIMARY KEY,
    company_name TEXT,
    address TEXT,              -- NEW
    city TEXT,
    phone TEXT UNIQUE,
    website TEXT,
    niche TEXT,
    rating REAL,               -- NEW
    operating_hours TEXT,      -- NEW
    status TEXT DEFAULT 'NEW',
    mockup_path TEXT,
    laptop_mockup_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**Migration**: Automatic! New columns are added when you run `init_db()`.

---

## 🎯 Use Cases: Old vs New

### Use Case 1: Original Mockup Pipeline

**Old Way**:

- Run scraper (hardcoded filters)
- Get businesses WITHOUT websites from database
- Generate mockups

**New Way** (same workflow):

1. Set `config.yaml`:
   ```yaml
   filters:
     has_website: "No"
     has_phone: "Yes"
   ```
2. Run: `python main.py`
3. Get CSV file with leads
4. Generate mockups from CSV

**Benefit**: CSV export for easier processing!

### Use Case 2: Find Businesses WITH Websites (New!)

**Old Way**: Not possible (would need to edit filter code)

**New Way**:

```yaml
filters:
  has_website: "Yes" # Just change config!
  has_phone: "Any"
```

---

## ⚠️ Breaking Changes

### 1. `run_scraper()` Function Signature

**Old**:

```python
run_scraper(city, niche, max_pages=1, country="")
```

**New**:

```python
run_scraper(
    city, niche, max_pages=1, country="",
    has_website_filter="Any",    # NEW
    has_phone_filter="Any",      # NEW
    operational_only=True        # NEW
)
```

**Migration**: Add the new parameters with your desired values.

### 2. Filter Functions

**Removed**:

- `has_website()` - Use `has_any_website()` instead

**Changed**:

- `has_real_website()` - Same behavior, still available

**Added**:

- `apply_filters()` - Main filtering function
- `has_phone_number()` - New helper
- `has_any_website()` - Replaces old `has_website()`

### 3. Repository Methods

**Added**:

- `get_all_leads(city=None, niche=None)` - Get all leads

**Changed**:

- `add_lead(data)` - Now accepts address, rating, operating_hours

**Unchanged**:

- `get_pending_mockups()` - Still works the same

---

## ✅ Compatibility Checklist

- [ ] Updated `.env` with Gemini API key (optional)
- [ ] Created `config.yaml` file
- [ ] Tested with 1 location, 1 niche first
- [ ] Verified CSV output format
- [ ] Checked filter behavior matches expectations
- [ ] Updated any custom code that calls `run_scraper()`
- [ ] Updated any custom code that uses filters directly

---

## 🆘 Troubleshooting

### "My old code doesn't work!"

**Problem**: `run_scraper()` missing required arguments

**Solution**: Add new filter parameters:

```python
stats = run_scraper(
    city="Amsterdam",
    niche="painters",
    max_pages=1,
    country="Netherlands",
    has_website_filter="No",   # Add this
    has_phone_filter="Yes",    # Add this
    operational_only=True      # Add this
)
```

### "I want the OLD behavior exactly"

**Solution**: Use these settings in `config.yaml`:

```yaml
filters:
  has_website: "No" # Skip businesses WITH websites
  has_phone: "Yes" # Require phone number
  operational_only: true # Skip closed businesses
```

This replicates the old hardcoded behavior!

### "Where are my leads?"

**Old**: In SQLite database only

**New**: In SQLite database AND CSV files in `output/csv/`

Both locations have the same data!

---

## 🎉 Benefits of Migrating

1. **CSV Export**: No more manual database exports
2. **Flexibility**: Change filters without code changes
3. **Bulk Processing**: Process 100s of cities at once
4. **More Data**: Get ratings, hours, addresses
5. **Better UX**: Progress indicators, clear stats
6. **Future-Proof**: Easy to add new features

---

## 💬 Need Help?

If you're having trouble migrating:

1. Run `python test_setup.py` to verify your setup
2. Start with a small test (1 city, 1 niche)
3. Check `EXAMPLES.md` for common use cases
4. Compare your old code with new examples in this guide

The new system is backward-compatible for the most part. Your existing database works fine, and you can gradually migrate your custom code.
