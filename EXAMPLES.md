# Usage Examples

## Example 1: Find Businesses WITHOUT Websites (Original Use Case)

**Scenario**: You want to generate mockups for businesses that don't have websites yet.

**config.yaml**:

```yaml
locations:
  - "Amsterdam"
  - "Rotterdam"

country: "Netherlands"

niches:
  - "painters"
  - "plumbers"

filters:
  has_website: "No" # MUST NOT have website
  has_phone: "Yes" # MUST have phone number
  operational_only: true

scraping:
  max_pages_per_area: 2
  use_neighborhood_splitting: true
```

**Expected Output**:

- `painters_Amsterdam_20260109_143022.csv`
- `painters_Rotterdam_20260109_143025.csv`
- `plumbers_Amsterdam_20260109_143030.csv`
- `plumbers_Rotterdam_20260109_143035.csv`

---

## Example 2: Find ALL Businesses in a City

**Scenario**: You want a comprehensive database of all businesses in a city.

**config.yaml**:

```yaml
locations:
  - "Toronto"

country: "Canada"

niches:
  - "restaurants"
  - "cafes"
  - "gyms"

filters:
  has_website: "Any" # Don't care about website
  has_phone: "Any" # Don't care about phone
  operational_only: true

scraping:
  max_pages_per_area: 3
  use_neighborhood_splitting: true
```

---

## Example 3: Find Businesses WITH Websites

**Scenario**: You want to build a list of established businesses with online presence.

**config.yaml**:

```yaml
locations:
  - "Seattle"
  - "Portland"

country: "USA"

niches:
  - "software companies"
  - "marketing agencies"

filters:
  has_website: "Yes" # MUST have website
  has_phone: "Any" # Don't care about phone
  operational_only: true

scraping:
  max_pages_per_area: 1
  use_neighborhood_splitting: false # Not needed for this use case
```

---

## Example 4: Bulk Processing (Multiple Cities × Multiple Niches)

**Scenario**: You're a lead gen agency scraping 50 cities for 10 niches = 500 CSV files.

**config.yaml**:

```yaml
locations:
  - "New York"
  - "Los Angeles"
  - "Chicago"
  - "Houston"
  - "Phoenix"
  # ... add 45 more cities

country: "USA"

niches:
  - "plumbers"
  - "electricians"
  - "roofers"
  - "hvac services"
  - "landscaping"
  - "painting contractors"
  - "flooring companies"
  - "window installation"
  - "garage door repair"
  - "pest control"

filters:
  has_website: "No"
  has_phone: "Yes"
  operational_only: true

scraping:
  max_pages_per_area: 1
  use_neighborhood_splitting: true
```

**Run Time**: ~30-60 minutes (depending on API speed)  
**Output**: 500 CSV files in `output/csv/`

---

## Example 5: Target Specific Rating Range (Post-Processing)

**Scenario**: You want businesses with good ratings (4+ stars).

**Step 1**: Scrape with ANY filters

```yaml
filters:
  has_website: "Any"
  has_phone: "Yes"
  operational_only: true
```

**Step 2**: Filter CSV by rating >= 4.0

```python
import pandas as pd

df = pd.read_csv("output/csv/restaurants_Toronto_20260109_143022.csv")

# Filter for 4+ stars
df_filtered = df[df["Google Review Rating"].str.extract(r'(\d+\.\d+)')[0].astype(float) >= 4.0]

df_filtered.to_csv("high_rated_restaurants.csv", index=False)
```

---

## Example 6: Niche Scraping (Very Specific)

**Scenario**: You need leads for a very specific niche.

**config.yaml**:

```yaml
locations:
  - "San Francisco"

country: "USA"

niches:
  - "organic coffee roasters"
  - "vegan bakeries"
  - "craft breweries"

filters:
  has_website: "Yes" # These businesses usually have websites
  has_phone: "Yes"
  operational_only: true

scraping:
  max_pages_per_area: 1
  use_neighborhood_splitting: false # Small niche, not many results
```

---

## Example 7: Test Run (Before Big Bulk Job)

**Scenario**: You want to test before scraping 1000 locations.

**config.yaml**:

```yaml
locations:
  - "Boston" # Just one city

country: "USA"

niches:
  - "plumbers" # Just one niche

filters:
  has_website: "No"
  has_phone: "Yes"
  operational_only: true

scraping:
  max_pages_per_area: 1 # Just 1 page (~20 results)
  use_neighborhood_splitting: false # Faster testing
```

**Run**:

```bash
python test_setup.py  # Verify setup first
python main.py        # Run small test
```

**Check Output**:

- Look at CSV format
- Check lead quality
- Verify filters are working

**Then Scale Up** to bulk processing.

---

## Command Reference

```bash
# 1. Verify setup
python test_setup.py

# 2. Run scraper
python main.py

# 3. Check results
ls output/csv/

# 4. View a CSV
head output/csv/plumbers_Toronto_*.csv
```

---

## Tips

1. **Start small**: 1 location, 1 niche first
2. **Test filters**: Make sure you're getting the right businesses
3. **Check CSV quality**: Open one CSV and verify data
4. **Monitor API costs**: Google Maps API charges per request
5. **Use neighborhood splitting**: More comprehensive results
6. **Backup database**: `cp leads.db leads.db.backup` before big jobs
