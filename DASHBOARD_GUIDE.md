# Dashboard Quick Start Guide

## 🌐 Lead Generation Dashboard

The web dashboard provides a user-friendly interface for all lead generation operations.

---

## 🚀 Getting Started

### 1. Install Dependencies (First Time Only)

```bash
pip install -r requirements.txt
```

### 2. Set Up API Keys

Create a `.env` file with your API keys:

```env
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
GEMINI_API_KEY=your_gemini_api_key
```

### 3. Launch Dashboard

**Windows:**

```bash
# Double-click:
run_dashboard.bat

# Or in terminal:
python run_dashboard.py
```

**Mac/Linux:**

```bash
python run_dashboard.py

# Or directly:
streamlit run dashboard.py
```

### 4. Open Browser

Dashboard opens automatically at: **http://localhost:8501**

---

## 📱 Dashboard Interface

### Sidebar - Configuration Panel

**📍 Locations**

- Enter cities (one per line)
- Set country for better results

**🎯 Niches**

- Enter business types (one per line)
- Examples: plumbers, electricians, restaurants

**🔍 Filters**

- Website: Yes/No/Any
- Phone: Yes/No/Any
- Operational Only: checkbox

**⚡ Scraping Settings**

- Max pages per area
- Neighborhood splitting toggle

**🛡️ API Limits**

- Monthly request limit
- Default: 1000

**💾 Save Button**

- Click to save all changes
- Configuration saved to `config.yaml`

---

## 📊 Tab 1: Overview

### API Usage Section

- **Requests Made**: Current month usage
- **Requests Remaining**: Available requests
- **Current Month**: Auto-resets monthly
- **Status**: Visual usage indicator
  - 🟢 Green: <75% used
  - 🟡 Yellow: 75-90% used
  - 🔴 Red: >90% used

### Progress Bar

- Visual representation of API usage
- Warnings when approaching limit

### Database Statistics

- **Total Leads**: All leads in database
- **Leads by Niche**: Breakdown by business type
- **Top 10 Cities**: Most scraped locations

---

## ▶️ Tab 2: Scraper

### Configuration Summary

- Shows current settings
- Locations, niches, filters overview

### Estimated API Usage

- Calculates requests needed
- ✅ Green: Within limit
- ⚠️ Red: Exceeds remaining requests

### Scraping Controls

**🚀 Start Scraping**

- Begins scraping with current config
- Shows real-time progress bar
- Displays current job (X/Y)
- Updates as it processes

**🔄 Refresh Status**

- Updates all metrics
- Useful during long scrapes

**📊 Check Usage**

- Quick API usage check
- Updates usage statistics

### Progress Tracking

- Real-time job progress (e.g., "Processing 5/10")
- Progress bar shows completion %
- Status messages for each step

### Results Summary

After scraping completes:

- Total results scraped
- Leads saved to database
- Failed jobs (if any)

---

## 📋 Tab 3: Leads

### Lead Browser

**Filters**

- 🔍 **Search**: Find by name, city, phone
- **Niche Filter**: Filter by business type
- **City Filter**: Filter by location

**Data Table**

- Shows all leads matching filters
- Columns:
  - ID, Business Name, Address
  - City, Phone, Website
  - Niche, Rating, Hours, Added On
- Sortable by clicking headers
- Scrollable for large datasets

**Total Count**

- Shows number of leads displayed
- Updates based on filters

---

## 📤 Tab 4: Export

### Export Options

**Select Filters**

- **Niche**: Choose specific niche or "All Niches"
- **City**: Choose specific city or "All Cities"

**Preview**

- Shows count of leads to be exported
- Updates based on selections

**📥 Export to CSV**

- Creates CSV with selected filters
- Shows success message with:
  - Number of leads exported
  - File path
  - Download button

**💾 Download Button**

- Click to download CSV file
- Browser downloads file automatically
- File name: `{niche}_{location}_{timestamp}.csv`

### Bulk Export

- **📥 Export ALL Leads**: Export entire database
- No filters applied
- Downloads comprehensive CSV

---

## 💡 Common Workflows

### Workflow 1: Quick Single-City Scrape

1. **Sidebar**: Enter 1 location, 1 niche
2. **Tab 2**: Click "Start Scraping"
3. **Tab 3**: Review collected leads
4. **Tab 4**: Export to CSV

### Workflow 2: Bulk Multi-City Scrape

1. **Sidebar**: Enter multiple locations and niches
2. **Tab 1**: Check estimated requests vs remaining
3. **Tab 2**: Start scraping
4. **Tab 1**: Monitor progress and usage
5. **Tab 4**: Export by city or niche

### Workflow 3: Targeted Export

1. **Tab 3**: Browse leads with filters
2. **Tab 4**: Select specific niche/city
3. Export filtered subset
4. Repeat for different combinations

### Workflow 4: Usage Monitoring

1. **Tab 1**: Check current API usage
2. Review percentage and warnings
3. Adjust scraping plan if near limit
4. Export existing leads before month ends

---

## ⚠️ Important Notes

### API Limit Protection

- Dashboard enforces 1000 req/month limit
- Scraping stops automatically at limit
- Clear error message when limit reached
- Limit resets automatically each month

### Real-Time Updates

- Usage stats update after each scrape
- Progress bars show live progress
- Database counts update automatically

### Configuration Persistence

- All settings saved to `config.yaml`
- Click "Save Configuration" to persist
- Page refresh loads saved config

### Browser Compatibility

- Works in Chrome, Firefox, Edge, Safari
- Best experience in Chrome
- Requires JavaScript enabled

---

## 🔧 Troubleshooting

### Dashboard Won't Start

```bash
# Check Streamlit is installed
pip install streamlit

# Try direct launch
streamlit run dashboard.py
```

### Port Already in Use

```bash
# Use different port
streamlit run dashboard.py --server.port=8502
```

### API Keys Not Found

- Check `.env` file exists
- Verify keys are correct
- Restart dashboard after adding keys

### Scraping Doesn't Start

- Check locations and niches are filled
- Verify API usage has remaining requests
- Look for error messages in dashboard

### Export Not Working

- Ensure leads exist in database
- Check `output/csv/` directory permissions
- Try exporting smaller subset first

---

## ⌨️ Keyboard Shortcuts

- **R**: Rerun dashboard (refresh)
- **Ctrl+C**: Stop dashboard server (in terminal)
- **F11**: Fullscreen browser

---

## 📱 Mobile Access

Access from another device on same network:

1. Find your computer's IP address
2. Open browser on mobile/tablet
3. Navigate to: `http://[YOUR-IP]:8501`

Example: `http://192.168.1.100:8501`

---

## 🎨 Dashboard Customization

The dashboard uses color coding:

- **Green boxes**: Success messages
- **Yellow boxes**: Warnings (75%+ usage)
- **Red boxes**: Errors or critical (90%+ usage)
- **Blue boxes**: Information
- **Gray boxes**: Neutral stats

---

## 📞 Support

**Common Questions:**

**Q: How do I change the API limit?**  
A: Sidebar → API Limits → Adjust number → Save Configuration

**Q: Can I run multiple scrapes simultaneously?**  
A: No, one scrape at a time. Wait for completion or stop current scrape.

**Q: Where are CSV files saved?**  
A: `output/csv/` directory. Also available for download in Export tab.

**Q: How do I clear the database?**  
A: Delete `leads.db` file. Database recreates automatically.

**Q: Can I schedule automatic scraping?**  
A: Use command line (`python main.py`) with task scheduler instead.

---

## 🎉 Tips for Best Results

1. **Start Small**: Test with 1-2 locations first
2. **Monitor Usage**: Check Overview tab regularly
3. **Use Filters**: Narrow down exports for specific needs
4. **Neighborhood Splitting**: Enable for comprehensive coverage
5. **Save Config Often**: Don't lose your setup
6. **Export Regularly**: Backup leads to CSV files
7. **Plan Requests**: Calculate needs before bulk scraping

---

## 🚀 You're Ready!

The dashboard makes lead generation simple and visual. Explore each tab, experiment with settings, and start collecting leads!

**Launch Command:**

```bash
python run_dashboard.py
```

**URL:**

```
http://localhost:8501
```

Happy scraping! 🎯
