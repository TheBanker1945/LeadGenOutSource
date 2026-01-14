# Authentication & Lead Limit Setup Guide

## 🔐 Authentication System

The dashboard now uses **token-based authentication** for secure access. There is no registration page - users can only log in with pre-generated authentication tokens.

### Authentication Tokens Generated

Three authentication tokens have been generated and saved to `auth_tokens.json`:

```
Token 1: e5253049eace80bc217a443dcf985b55dfb88d71af81f67eb692cf50216f3474
Token 2: b7b281c5e83f5996c3c19cc38fce45b42f3fc7fa250a2ef3f11853300521f407
Token 3: 5330c1f3196ce23a4a44a426ae8d248f9c4fef0301188a8ab48a033a62c9b4a5
```

**⚠️ IMPORTANT:** Keep these tokens secure! Anyone with a valid token can access the dashboard.

### How to Use

1. **Starting the Dashboard:**
   ```bash
   python run_dashboard.py
   # OR
   streamlit run login.py
   ```

2. **Logging In:**
   - The login page will open in your browser at http://localhost:8501
   - Enter one of the authentication tokens (64 characters)
   - Click "🚀 Login"
   - You'll be redirected to the dashboard automatically

3. **Logging Out:**
   - Click the "🔓 Logout" button in the sidebar
   - You'll be redirected to the login page

### Managing Authentication Tokens

#### Generate New Tokens

```python
from auth import AuthManager

auth = AuthManager()
new_token = auth.generate_token("username_or_label")
print(f"New token: {new_token}")
```

Or run the auth script directly:
```bash
python auth.py
```

#### Revoke a Token

```python
from auth import AuthManager

auth = AuthManager()
auth.revoke_token("token_to_revoke")
```

#### List All Tokens

```python
from auth import AuthManager

auth = AuthManager()
tokens = auth.list_all_tokens()
for token_info in tokens:
    print(f"Token: {token_info['token']}")
    print(f"Username: {token_info['username']}")
    print(f"Active: {token_info['active']}")
    print(f"Created: {token_info['created_at']}")
    print(f"Last Used: {token_info['last_used']}")
    print("-" * 50)
```

### Token Storage

Tokens are stored in `auth_tokens.json` in the project root. This file contains:
- Token strings
- Usernames/labels
- Creation timestamps
- Last used timestamps
- Active/inactive status

**Backup this file** to preserve access tokens!

---

## 🎯 Lead Limit Feature

The scraper now supports a **lead limit** to control how many leads are saved in each scraping session.

### How It Works

1. **Set the Limit in Dashboard:**
   - In the sidebar, find "⚡ Scraping Settings"
   - Set "Lead Limit (per scrape)" to your desired number (e.g., 80)
   - Set to 0 for no limit
   - Click "💾 Save Configuration"

2. **Scraping Behavior:**
   - The scraper will **stop automatically** when it reaches the specified number of saved leads
   - The limit counts **saved leads**, not total results
   - Duplicates and filtered-out results don't count toward the limit
   - Each scraping session respects the limit independently

3. **Example:**
   - Lead Limit: 80
   - Scraper processes results from Google Maps
   - Once 80 new leads are saved to the database, scraping stops
   - You'll see "⚠️ LIMIT REACHED: Stopped at 80 leads" in the output

### Configuration

The lead limit is saved in `config.yaml`:

```yaml
scraping:
  max_pages_per_area: 1
  lead_limit: 80  # Set your desired limit here (0 = no limit)
  use_neighborhood_splitting: true
  language_code: "en"
```

### Use Cases

- **Budget Control:** Limit leads to avoid excessive API usage
- **Testing:** Scrape a small batch first (e.g., 10 leads) to test configuration
- **Targeted Lists:** Get exactly 50 leads per niche for focused outreach
- **Quality Over Quantity:** Stop early to manually review results

### API Usage Note

The lead limit helps control how many leads you save, but the scraper still makes API requests to fetch results. The lead limit stops processing once enough leads are saved, potentially saving API requests by stopping early.

---

## 🚀 Quick Start

1. **Launch the dashboard:**
   ```bash
   python run_dashboard.py
   ```

2. **Log in with a token:**
   - Use one of the tokens listed above
   - The dashboard will open automatically after login

3. **Configure scraping:**
   - Set locations, niches, and filters in the sidebar
   - Set your lead limit (e.g., 80 for 80 leads max)
   - Click "💾 Save Configuration"

4. **Start scraping:**
   - Click "▶️ Start Scraping"
   - Monitor progress in real-time
   - Scraping will stop automatically when the lead limit is reached

---

## 📝 Security Best Practices

1. **Store tokens securely** - Don't commit `auth_tokens.json` to public repositories
2. **Add to .gitignore:**
   ```
   auth_tokens.json
   ```
3. **Regenerate tokens** if they are compromised
4. **Revoke unused tokens** to limit access
5. **Backup `auth_tokens.json`** to avoid losing access

---

## 🛠️ Technical Details

### Files Modified/Created

- **auth.py** - Token generation, validation, and management
- **login.py** - Streamlit login page interface
- **dashboard.py** - Protected with authentication check
- **src/scraper/main.py** - Lead limit logic added
- **run_dashboard.py** - Updated to launch login page
- **.streamlit/config.toml** - Streamlit configuration

### Session State

The authentication system uses Streamlit session state:
- `st.session_state.authenticated` - Boolean indicating login status
- `st.session_state.auth_token` - Current user's token
- `st.session_state.username` - Current user's username

### Authentication Flow

1. User opens login page
2. Enters authentication token
3. Token is validated against `auth_tokens.json`
4. If valid, session state is set and user is redirected to dashboard
5. Dashboard checks session state on every page load
6. If not authenticated, user is redirected back to login

---

## ❓ Troubleshooting

**Q: I lost my tokens, how do I regain access?**  
A: If you have access to the server, run `python auth.py` to generate new tokens. The old tokens will still work unless revoked.

**Q: Can I change a token's username?**  
A: Edit `auth_tokens.json` manually and modify the username field for any token.

**Q: How do I disable authentication temporarily?**  
A: Not recommended, but you can comment out the authentication check in `dashboard.py` (lines after "AUTHENTICATION CHECK").

**Q: The lead limit isn't working.**  
A: Make sure you saved the configuration after setting the limit. Check that the limit appears in the configuration summary on the dashboard.

**Q: Scraper stopped before reaching the limit.**  
A: Check if you ran out of API requests or if there are no more results from Google Maps.

---

## 📞 Support

For issues or questions, refer to the main project README or check the configuration files.
