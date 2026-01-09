# Quick Start - Streamlit Cloud Setup

## 🚀 Quick 5-Minute Setup

### Step 1: Generate Client Password (2 minutes)

Run this command to generate a secure password hash:

```bash
.venv\Scripts\python.exe generate_password.py
```

Enter a password for your client, and copy the hashed output.

### Step 2: Test Locally (1 minute)

Create `.streamlit/secrets.toml` (copy from `.streamlit/secrets.toml.example`):

```toml
[credentials.usernames.client1]
name = "Client Name"
password = "PASTE_HASHED_PASSWORD_HERE"

[cookie]
name = "lead_gen_auth"
key = "your_random_key_12345"
expiry_days = 30
```

Run the dashboard:
```bash
python run_dashboard.py
```

Try logging in with username: `client1` and your password.

### Step 3: Deploy to Streamlit Cloud (2 minutes)

1. Push code to private GitHub repo
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app" → Select your repo → `run_dashboard.py`
4. Click "Advanced settings" → Paste your secrets.toml content
5. Click "Deploy"

Done! Share the URL with your client.

---

## 🔑 What to Give Your Client

- **URL:** `https://your-app-name.streamlit.app`
- **Username:** `client1`
- **Password:** `the_plain_text_password` (NOT the hash)

They'll see a login page, enter credentials, and access the dashboard!

---

## 📝 Notes

- **Development mode:** If no secrets.toml exists, auth is bypassed (for local testing)
- **Production mode:** On Streamlit Cloud, auth is required via secrets
- **Multiple clients:** Add more usernames to the credentials section
- **Updates:** Push to GitHub = automatic deployment

---

For detailed instructions, see [STREAMLIT_DEPLOYMENT.md](STREAMLIT_DEPLOYMENT.md)
