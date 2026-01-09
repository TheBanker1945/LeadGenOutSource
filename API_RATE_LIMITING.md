# API Rate Limiting Feature

## Overview

Added a **hard monthly limit of 1000 Google Maps API requests** that automatically resets each month and cannot be exceeded.

---

## 🎯 What Was Added

### 1. **Rate Limiter Module** (`src/scraper/rate_limiter.py`)

- Tracks API usage in `api_usage.json`
- Automatically resets counter at start of each month
- Enforces hard limit (cannot be exceeded)
- Provides usage statistics

### 2. **Integration with Maps Client** (`src/scraper/maps_client.py`)

- Checks limit before each API call
- Records each request (success or failure)
- Raises `RequestLimitExceeded` exception when limit reached
- Shows warnings when approaching limit (80%+ usage)

### 3. **Configuration** (`config.yaml`)

```yaml
api_limits:
  monthly_request_limit: 1000 # Configurable limit
```

### 4. **Usage Checker** (`check_usage.py`)

- Command-line tool to check current usage
- Shows: requests made, remaining, percentage, progress bar
- Visual warnings when approaching limit

### 5. **Updated Main Script** (`main.py`)

- Passes monthly limit to scraper
- Handles `RequestLimitExceeded` exception gracefully
- Stops scraping when limit reached
- Shows clear error message

---

## 🛡️ How It Works

### Tracking

```
api_usage.json (auto-created):
{
  "month": "2026-01",
  "requests_made": 145,
  "monthly_limit": 1000,
  "last_reset": "2026-01-01T00:00:00",
  "last_request": "2026-01-09T14:30:22"
}
```

### Monthly Reset

- Automatically detects when month changes
- Resets `requests_made` to 0
- Preserves history in console output
- No manual intervention needed

### Request Flow

```
1. User runs: python main.py
2. Before each API call:
   ✓ Check: requests_made + 1 <= monthly_limit?
   ✓ If yes: Make request, increment counter
   ✗ If no: Raise RequestLimitExceeded, stop scraping
3. User sees clear message about limit
4. Scraping resumes next month automatically
```

---

## 📊 Usage Examples

### Check Current Usage

```bash
python check_usage.py
```

Output:

```
============================================================
📊 GOOGLE MAPS API USAGE
============================================================

📅 Current Month: 2026-01
✅ Requests Made: 145
🚫 Monthly Limit: 1000
⏳ Requests Remaining: 855
📈 Usage: 14.5%

🕒 Last Request: 2026-01-09T14:30:22.123456
🔄 Last Reset: 2026-01-01T00:00:00

[███████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 14.5%

============================================================
```

### When Limit Is Reached

```
============================================================
🚫 MONTHLY API LIMIT REACHED!
============================================================
Requests used this month: 1000
Requests remaining: 0
Requests needed for this query: 1

This limit prevents unexpected API costs.
The limit will reset at the start of next month.
============================================================

🛑 STOPPING: Monthly API limit reached
============================================================
Processed 47 out of 50 jobs before hitting limit
The limit will reset at the start of next month
============================================================
```

### Warning Before Limit

```
============================================================
⚠️  API USAGE WARNING
============================================================
Month: 2026-01
Requests used: 850 / 1000
Remaining: 150
Usage: 85.0%
============================================================
```

---

## ⚙️ Configuration Options

### Change the Limit

Edit `config.yaml`:

```yaml
api_limits:
  monthly_request_limit: 2000 # Increase to 2000/month
```

### Disable Limit (Not Recommended)

Set a very high number:

```yaml
api_limits:
  monthly_request_limit: 999999
```

**Warning**: This defeats the purpose of cost protection!

---

## 🧮 Request Calculation

### Formula

```
Total Requests = Locations × Niches × Neighborhoods × Pages
```

### Example 1: Small Job

```
1 location × 1 niche × 10 neighborhoods × 1 page = 10 requests
```

### Example 2: Medium Job

```
5 locations × 3 niches × 10 neighborhoods × 2 pages = 300 requests
```

### Example 3: Large Job (Would Hit Limit)

```
20 locations × 10 niches × 10 neighborhoods × 1 page = 2000 requests
❌ Exceeds 1000 limit - will stop after ~1000 requests
```

---

## 🔒 Safety Features

### 1. Cannot Be Exceeded

- Hard stop at limit
- No "grace period"
- Immediate exception raised

### 2. Tracks Failed Requests

- Even failed API calls count against limit
- Prevents retry abuse

### 3. Persistent Tracking

- Survives program restarts
- Stored in `api_usage.json`
- Not in git (in `.gitignore`)

### 4. Automatic Reset

- No manual intervention needed
- Detects month change automatically
- Shows reset message in console

### 5. Early Warnings

- Warning at 80% usage
- Warning at 100 requests remaining
- Visual progress bar

---

## 📂 New Files

1. **`src/scraper/rate_limiter.py`** - Rate limiting logic
2. **`check_usage.py`** - Usage checker tool
3. **`api_usage.json`** - Usage tracking (auto-created)

## 📝 Modified Files

1. **`src/scraper/maps_client.py`** - Integrated rate limiter
2. **`src/scraper/main.py`** - Added monthly_limit parameter
3. **`main.py`** - Pass limit, handle exception
4. **`config.yaml`** - Added api_limits section
5. **`.gitignore`** - Added api_usage.json
6. **`README.md`** - Documented feature

---

## 🎯 Benefits

✅ **Cost Control**: Never exceed budget  
✅ **Automatic**: Resets monthly without intervention  
✅ **Transparent**: Clear warnings and messages  
✅ **Configurable**: Easy to adjust limit  
✅ **Persistent**: Survives restarts  
✅ **User-Friendly**: Simple usage checker

---

## 🚀 Testing

### Test the Limit

1. Set a low limit for testing:

   ```yaml
   api_limits:
     monthly_request_limit: 5
   ```

2. Run scraper:

   ```bash
   python main.py
   ```

3. Should stop after 5 requests with clear message

4. Check usage:

   ```bash
   python check_usage.py
   ```

5. Reset for testing (delete tracking file):
   ```bash
   rm api_usage.json
   ```

---

## 🔮 Future Enhancements (Optional)

- Daily limits in addition to monthly
- Email alerts when approaching limit
- Multiple limit tiers (warning/soft/hard)
- API cost calculator
- Usage history/analytics dashboard

---

## ✅ Summary

The API rate limiting feature provides **robust cost protection** with minimal configuration. It automatically tracks usage, enforces limits, resets monthly, and provides clear feedback to users. The 1000 request/month default is conservative and prevents unexpected API bills.
