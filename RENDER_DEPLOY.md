# Render Deployment Guide

## Quick Deploy Instructions

### 1. Update Render Build & Start Commands

In your Render dashboard, set:

**Build Command:**

```bash
pip install -r requirements.txt
```

**Start Command:**

```bash
bash start_render.sh
```

### 2. Environment Variables

Set these in Render dashboard under "Environment":

| Variable              | Value                | Description                  |
| --------------------- | -------------------- | ---------------------------- |
| `DATABASE_URL`        | (auto-set by Render) | PostgreSQL connection string |
| `GOOGLE_MAPS_API_KEY` | Your API key         | Google Maps API key          |
| `GEMINI_API_KEY`      | Your API key         | Google Gemini API key        |
| `MONTHLY_API_LIMIT`   | 1000                 | Monthly API request limit    |

### 3. Deploy

1. Push your code to GitHub:

   ```bash
   git add .
   git commit -m "Add database-backed authentication and usage tracking"
   git push
   ```

2. Render will automatically deploy

3. The `start_render.sh` script will:
   - Initialize the database
   - Create authentication tokens
   - Set API usage to 409 requests
   - Start the dashboard

### 4. Login Tokens

After deployment, use these tokens to log in:

**Admin Token (keep private):**

```
a9f8c2d4e1b7a5f3c8d6e2b9a7f4c1d8e5b3a6f9c2d7e4b1a8f5c3d9e6b2a7f4
```

**User Tokens (share with team):**

```
e5253049eace80bc217a443dcf985b55dfb88d71af81f67eb692cf50216f3474
b7b281c5e83f5996c3c19cc38fce45b42f3fc7fa250a2ef3f11853300521f407
5330c1f3196ce23a4a44a426ae8d248f9c4fef0301188a8ab48a033a62c9b4a5
```

## What's Fixed

### ✅ Persistent Usage Tracking

- API usage stored in PostgreSQL database
- Survives server restarts
- Shared across all users
- Auto-resets monthly

### ✅ Database-Backed Authentication

- Tokens stored in database (not files)
- Works on Render without shell access
- Admin and user roles

### ✅ Admin Settings Page

- Adjust API usage through web UI
- No shell access needed
- Admin-only access

## Admin Features

Login with admin token to access:

- **Admin Settings** page (sidebar)
- Modify API usage counts
- View all tokens
- Manage user access

## Troubleshooting

### Issue: "relation api_usage does not exist"

**Solution:** The start_render.sh script should fix this automatically. If not, check Render logs.

### Issue: "Invalid token"

**Solution:** Tokens are created automatically on first run. Wait for deployment to complete.

### Issue: Usage shows 0 instead of 409

**Solution:** Use admin token → Admin Settings → Update usage to 409

## Local Development

For local development, the system still uses JSON files:

- `auth_tokens.json` - Local authentication
- `leads.db` - Local SQLite database

On Render (production), it uses:

- PostgreSQL database for everything
- Environment variables for configuration
