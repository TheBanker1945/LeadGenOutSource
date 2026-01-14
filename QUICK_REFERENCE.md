# 🚀 Quick Reference Card

## 🔑 Your Authentication Tokens

```
Token 1: e5253049eace80bc217a443dcf985b55dfb88d71af81f67eb692cf50216f3474
Token 2: b7b281c5e83f5996c3c19cc38fce45b42f3fc7fa250a2ef3f11853300521f407
Token 3: 5330c1f3196ce23a4a44a426ae8d248f9c4fef0301188a8ab48a033a62c9b4a5
```

⚠️ **Keep these tokens safe and secure!**

---

## 🎯 Quick Start (3 Steps)

### 1️⃣ Start Dashboard
```bash
python run_dashboard.py
```

### 2️⃣ Login
- Open http://localhost:8501
- Paste one of the tokens above
- Click "🚀 Login"

### 3️⃣ Configure & Scrape
- Set locations and niches in sidebar
- Set lead limit (e.g., 80)
- Click "💾 Save Configuration"
- Click "▶️ Start Scraping"

---

## ⚡ Common Commands

```bash
# Start dashboard
python run_dashboard.py

# Generate new tokens
python auth.py

# Run scraper directly (for testing)
python main.py

# Check database
python check_db.py
```

---

## 🎛️ Configuration Quick Settings

| Setting | Description | Default | Recommended |
|---------|-------------|---------|-------------|
| Max Pages | Pages per area | 1 | 1-3 |
| Lead Limit | Max leads to save | 0 (none) | 50-100 |
| Has Website | Filter by website | Any | Yes/Any |
| Has Phone | Filter by phone | Any | Yes |
| Operational Only | Skip closed businesses | True | True |

---

## 📊 Lead Limit Examples

| Limit | Use Case |
|-------|----------|
| 0 | No limit - scrape everything |
| 5 | Quick test of configuration |
| 20 | Small targeted list |
| 50 | Medium campaign |
| 100 | Large campaign |
| 500 | Bulk data collection |

---

## 🔐 Token Management Cheat Sheet

```python
from auth import AuthManager
auth = AuthManager()

# Generate new token
token = auth.generate_token("username")

# Validate token
is_valid = auth.validate_token(token)

# Revoke token
auth.revoke_token(token)

# List all tokens
all_tokens = auth.list_all_tokens()
```

---

## 🚨 Troubleshooting

| Problem | Solution |
|---------|----------|
| Can't access dashboard | Check if logged in, try re-login |
| Token doesn't work | Verify 64 characters, no spaces |
| Lead limit not working | Save configuration after changing |
| Scraper stops early | Check API limit or lead limit |
| Lost tokens | Run `python auth.py` to generate new ones |

---

## 📂 Important Files

```
auth.py                  ← Authentication system
login.py                 ← Login page
dashboard.py             ← Main dashboard (protected)
auth_tokens.json         ← Your tokens (BACKUP THIS!)
config.yaml              ← Scraping configuration
leads.db                 ← Database of leads
```

---

## 🎨 Dashboard Sections

```
📊 Overview         - Statistics and metrics
🚀 Scraping         - Start scraping jobs
📋 Leads Table      - View and manage leads
📤 Export           - Export to CSV
⚙️ Settings         - Configuration (sidebar)
```

---

## 💡 Pro Tips

1. **Test First**: Use lead limit of 5 to test configuration
2. **Save Often**: Click "💾 Save Configuration" after changes
3. **Monitor API**: Check remaining API requests before big scrapes
4. **Backup Tokens**: Save `auth_tokens.json` somewhere safe
5. **Export Regularly**: Export leads to CSV as backup
6. **Use Filters**: Enable "Has Website" to get better quality leads
7. **Logout**: Always logout when done for security

---

## 📞 Need Help?

Check these files:
- **AUTHENTICATION_SETUP.md** - Complete auth guide
- **IMPLEMENTATION_SUMMARY.md** - Technical details
- **VISUAL_GUIDE.md** - Visual diagrams
- **DASHBOARD_GUIDE.md** - Dashboard usage guide

---

## ✅ Daily Workflow

```
Morning:
1. Start dashboard (python run_dashboard.py)
2. Login with your token
3. Check remaining API requests

Configure:
4. Set locations and niches
5. Set lead limit (e.g., 80)
6. Save configuration

Scrape:
7. Start scraping
8. Monitor progress
9. Review leads in table

Export:
10. Export leads to CSV
11. Logout when done
```

---

**Remember:** 
- 🔐 Keep tokens secure
- 💾 Backup auth_tokens.json
- 📊 Monitor API usage
- 🎯 Use lead limits wisely
- 🚀 Test before big scrapes

---

## 🎉 You're All Set!

Everything is configured and ready to use. Just run `python run_dashboard.py` and start scraping! 🚀
