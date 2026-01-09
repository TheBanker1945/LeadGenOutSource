# Streamlit Cloud Deployment Guide

This guide explains how to deploy the Lead Generation Dashboard to Streamlit Cloud as a SaaS application with client authentication.

## 🎯 Overview

The dashboard is configured to:
- Run on Streamlit Cloud (free or paid tier)
- Require authentication for client access
- Keep your code private (they only get the URL)
- Allow you to update the app by pushing to GitHub

---

## 📋 Prerequisites

1. GitHub account (for private repository)
2. Streamlit Cloud account (sign up at [share.streamlit.io](https://share.streamlit.io))
3. Google Maps API key
4. Google Gemini API key (for neighborhood splitting)

---

## 🚀 Deployment Steps

### Step 1: Create Private GitHub Repository

1. Go to GitHub and create a **private** repository
2. Push your code to the repository:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### Step 2: Generate Password Hash

Before deploying, you need to create a secure password hash for your client.

Run this Python script locally:

```python
import streamlit_authenticator as stauth

# Generate hashed password
password = "your_client_password_here"  # Change this!
hashed_password = stauth.Hasher([password]).generate()[0]
print(f"Hashed password: {hashed_password}")
```

Or use the online generator at: https://docs.streamlit.io/library/api-reference/utilities/st.experimental_user

Copy the hashed password for the next step.

### Step 3: Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Select your private GitHub repository
4. Set main file: `run_dashboard.py`
5. Click "Advanced settings"
6. Add the following secrets (copy from template below):

```toml
# Client Authentication
[credentials.usernames.client1]
name = "Client Company Name"
password = "$2b$12$YOUR_HASHED_PASSWORD_FROM_STEP_2"

[cookie]
name = "lead_gen_auth"
key = "YOUR_RANDOM_SIGNATURE_KEY_HERE"  # Generate a random string
expiry_days = 30

# API Keys
[api_keys]
GOOGLE_MAPS_API_KEY = "your_google_maps_api_key"
GOOGLE_GEMINI_API_KEY = "your_gemini_api_key"
```

7. Click "Deploy"

### Step 4: Share Access with Client

Once deployed, you'll get a URL like: `https://your-app-name.streamlit.app`

**Give your client:**
- URL: `https://your-app-name.streamlit.app`
- Username: `client1`
- Password: (the plain text password you used in Step 2, NOT the hash)

---

## 🔐 Security Best Practices

### Keep Code Private
- Use a **private** GitHub repository
- Never share repository access with clients
- They only get the deployed URL + login credentials

### API Key Management

**Option A: You provide the API keys** (Recommended for SaaS)
- Add keys to Streamlit secrets
- Track usage yourself
- Bill clients accordingly
- Easier to manage

**Option B: Client provides their own API keys**
- They give you their keys
- You add them to Streamlit secrets
- They pay Google directly
- More transparent for them

### Password Security
- Use strong passwords (16+ characters)
- Don't reuse passwords across clients
- Store client passwords securely (use a password manager)
- Change passwords if client access needs to be revoked

---

## 📊 Adding Multiple Clients

To add more clients, update the secrets in Streamlit Cloud dashboard:

```toml
[credentials.usernames.client1]
name = "First Client"
password = "$2b$12$hashed_password_1"

[credentials.usernames.client2]
name = "Second Client"
password = "$2b$12$hashed_password_2"

[credentials.usernames.client3]
name = "Third Client"
password = "$2b$12$hashed_password_3"
```

Each client gets their own username (`client1`, `client2`, etc.) and password.

---

## 🔄 Updating the Application

When you need to update the app:

1. Make changes locally
2. Test thoroughly
3. Commit and push to GitHub:
```bash
git add .
git commit -m "Description of changes"
git push
```

Streamlit Cloud will automatically redeploy with your changes!

---

## 💾 Database Considerations

**Current Setup:** SQLite database (file-based)
- Works fine for single client
- Data persists on Streamlit Cloud
- **Limitation:** All clients share the same database

**For Multiple Clients:** You'll need to add database isolation:
- Option A: Separate SQLite file per client (simple)
- Option B: PostgreSQL with client_id field (scalable)
- Option C: Deploy separate Streamlit apps per client

---

## 💰 Pricing

### Streamlit Cloud Pricing
- **Free Tier:** 1 private app, limited resources
- **Creator Plan:** $20/month - 3 private apps, more resources
- **Teams Plan:** $250/month - unlimited apps, team features

### Recommendation
- Start with **Free tier** for 1 client
- Upgrade to **Creator** for 2-3 clients
- Consider VPS hosting if you have 5+ clients

---

## 🐛 Troubleshooting

### App won't deploy
- Check `requirements.txt` is in root directory
- Verify Python version compatibility (3.9-3.12)
- Check Streamlit Cloud logs for errors

### Authentication not working
- Verify secrets.toml syntax is correct
- Make sure password hash is correct
- Check username matches exactly

### API keys not working
- Confirm keys are in secrets with correct names
- Check if keys have proper permissions
- Verify billing is enabled on Google Cloud

### Database errors
- SQLite works on Streamlit Cloud
- Data persists between sessions
- Consider PostgreSQL for production

---

## 📞 Support

If you encounter issues:
1. Check Streamlit Cloud logs (click "Manage app" → "Logs")
2. Verify all secrets are correctly configured
3. Test authentication locally first
4. Review Streamlit docs: https://docs.streamlit.io

---

## 🔒 Revoking Client Access

To revoke a client's access:

1. Go to Streamlit Cloud dashboard
2. Click "Settings" → "Secrets"
3. Remove their username from the credentials
4. Click "Save"

The client will be immediately logged out and unable to login again.

---

## 📈 Next Steps for Scaling

When you have multiple clients:

1. **Add Multi-tenancy:**
   - Separate database per client
   - Add `client_id` to all database tables
   - Filter data by logged-in user

2. **Add Usage Tracking:**
   - Log scraping activities per client
   - Track API usage per client
   - Generate usage reports for billing

3. **Add Billing Integration:**
   - Integrate Stripe for automated billing
   - Track subscription status
   - Limit features based on plan

4. **Consider VPS:**
   - More control over infrastructure
   - Better for 5+ clients
   - Can run multiple instances

---

## 📝 Summary

You now have:
- ✅ Private codebase (they never see the code)
- ✅ Secure authentication (password-protected access)
- ✅ Easy deployment (push to GitHub = auto-update)
- ✅ Professional URL (streamlit.app domain)
- ✅ Zero server management (Streamlit handles it)

Your client pays you monthly for access, and you maintain full control of the application!
