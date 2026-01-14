# 🎨 Visual Guide - Authentication & Lead Limit

## Login Flow

```
┌─────────────────────────────────────────────┐
│                                             │
│              🔐 Login Page                  │
│                                             │
│  ┌───────────────────────────────────────┐ │
│  │ Authentication Token                  │ │
│  │ ••••••••••••••••••••••••••••••••••••• │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  ┌───────────────────────────────────────┐ │
│  │        🚀 Login                       │ │
│  └───────────────────────────────────────┘ │
│                                             │
└─────────────────────────────────────────────┘
                     ↓
            Token Valid?
                     ↓
              ┌─────┴─────┐
              │           │
             YES         NO
              │           │
              ↓           ↓
    ┌─────────────┐  ┌────────────┐
    │ Dashboard   │  │ Error Msg  │
    │ (Protected) │  │ Try Again  │
    └─────────────┘  └────────────┘
```

## Dashboard with Authentication

```
┌──────────────────────────────────────────────────────────┐
│  Lead Generation Dashboard                      [Logout] │
├──────────────────────────────────────────────────────────┤
│ ┌────────────┐                                           │
│ │ Sidebar    │  Main Content Area                        │
│ │            │  ┌─────────────────────────────────┐     │
│ │ ⚙️ Config  │  │  📊 Statistics                  │     │
│ │            │  │  - Total Leads: 150              │     │
│ │ 👤 User    │  │  - This Month: 25                │     │
│ │ 🔓 Logout  │  └─────────────────────────────────┘     │
│ │            │                                           │
│ │ 📍 Locs    │  ┌─────────────────────────────────┐     │
│ │ 🎯 Niches  │  │  🚀 Start Scraping              │     │
│ │            │  └─────────────────────────────────┘     │
│ │ ⚡ Settings│                                           │
│ │ • Max Pages│  ┌─────────────────────────────────┐     │
│ │ • Limit: 80│  │  📋 Leads Table                 │     │
│ │            │  │  [Search] [Filter] [Export]     │     │
│ │ 💾 Save    │  └─────────────────────────────────┘     │
│ └────────────┘                                           │
└──────────────────────────────────────────────────────────┘
```

## Lead Limit in Action

```
Scraping Process with Limit = 80

Start Scraper
    ↓
Fetch Results from Google Maps (Page 1)
    ↓
┌─────────────────────────────────────────┐
│ Result 1 → Filter → Pass → Save ✅      │ Saved: 1/80
│ Result 2 → Filter → Fail → Skip ⊗       │ Saved: 1/80
│ Result 3 → Filter → Pass → Duplicate ⊗  │ Saved: 1/80
│ Result 4 → Filter → Pass → Save ✅      │ Saved: 2/80
│ Result 5 → Filter → Pass → Save ✅      │ Saved: 3/80
│ ...                                      │ ...
│ Result 95 → Filter → Pass → Save ✅     │ Saved: 79/80
│ Result 96 → Filter → Pass → Save ✅     │ Saved: 80/80 🛑
└─────────────────────────────────────────┘
                    ↓
        ⚠️ LIMIT REACHED at 80 leads
                    ↓
            Stop Scraper
                    ↓
        Display Results Summary
```

## Configuration Panel

```
┌──────────────────────────────────┐
│    ⚡ Scraping Settings          │
├──────────────────────────────────┤
│                                  │
│  Max Pages per Area:  [1    ↕]  │
│                                  │
│  Lead Limit:          [80   ↕]  │
│  (0 = no limit)                  │
│                                  │
│  ┌────────────────────────────┐ │
│  │  💾 Save Configuration     │ │
│  └────────────────────────────┘ │
│                                  │
└──────────────────────────────────┘
```

## Token Structure

```
Token: 64 characters (hex)
┌────────────────────────────────────────────────────────────────┐
│ e5253049eace80bc217a443dcf985b55dfb88d71af81f67eb692cf50216f3474 │
└────────────────────────────────────────────────────────────────┘
   └─ 32 bytes = 256 bits of entropy (cryptographically secure)
```

## Token Storage (auth_tokens.json)

```json
{
    "e5253049eace...": {
        "username": "user_1",
        "created_at": "2026-01-14T10:30:00",
        "last_used": "2026-01-14T12:45:00",
        "active": true
    },
    "b7b281c5e83f...": {
        "username": "user_2",
        "created_at": "2026-01-14T10:30:00",
        "last_used": null,
        "active": true
    },
    "5330c1f3196c...": {
        "username": "user_3",
        "created_at": "2026-01-14T10:30:00",
        "last_used": "2026-01-14T11:20:00",
        "active": false  ← Revoked
    }
}
```

## Authentication Check Flow

```
Every Dashboard Page Load
        ↓
┌───────────────────────┐
│ Check Session State   │
│ authenticated?        │
└───────┬───────────────┘
        │
    ┌───┴───┐
    │       │
   YES     NO
    │       │
    ↓       ↓
┌───────┐ ┌──────────────┐
│ Allow │ │ Redirect to  │
│ Access│ │ Login Page   │
└───────┘ └──────────────┘
```

## Complete System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     User Browser                        │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────┐
│                  Streamlit Server                       │
│                                                         │
│  ┌────────────┐         ┌─────────────┐               │
│  │ login.py   │ ←──→    │ dashboard.py│               │
│  │ (Entry)    │         │ (Protected) │               │
│  └─────┬──────┘         └──────┬──────┘               │
│        │                       │                       │
│        ↓                       ↓                       │
│  ┌──────────────────────────────────────┐             │
│  │         auth.py (AuthManager)        │             │
│  └─────────────┬────────────────────────┘             │
│                │                                       │
│                ↓                                       │
│  ┌──────────────────────────────────────┐             │
│  │      auth_tokens.json                │             │
│  │  (Token Storage)                     │             │
│  └──────────────────────────────────────┘             │
│                                                         │
│  ┌──────────────────────────────────────┐             │
│  │   src/scraper/main.py                │             │
│  │   (Lead Limit Logic)                 │             │
│  └─────────────┬────────────────────────┘             │
│                │                                       │
│                ↓                                       │
│  ┌──────────────────────────────────────┐             │
│  │        leads.db (SQLite)             │             │
│  │    (Stored Leads)                    │             │
│  └──────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────┘
```

## Usage Example Scenarios

### Scenario 1: First Time User
```
1. Admin generates tokens    → python auth.py
2. Admin shares token        → user_1 gets token via secure channel
3. User opens dashboard      → http://localhost:8501
4. Login page appears        → Enter token
5. User logs in              → Redirected to dashboard
6. User configures scraping  → Set limit to 50 leads
7. User starts scraping      → Scraper stops at 50
8. User exports results      → Download CSV
```

### Scenario 2: Multiple Users
```
User A (Token 1)        User B (Token 2)        User C (Token 3)
     ↓                       ↓                       ↓
Login with Token 1      Login with Token 2      Login with Token 3
     ↓                       ↓                       ↓
Set limit: 80          Set limit: 100          Set limit: 50
     ↓                       ↓                       ↓
Scrape NYC plumbers    Scrape LA dentists      Scrape SF lawyers
     ↓                       ↓                       ↓
Gets 80 leads          Gets 100 leads          Gets 50 leads
```

### Scenario 3: Testing Configuration
```
1. Login to dashboard
2. Configure:
   - Location: Toronto
   - Niche: Coffee Shops
   - Filters: Has Website = Yes
   - Lead Limit: 5  ← Small test batch
3. Start scraping
4. Review 5 leads
5. If good → Increase limit to 100
6. Run again with full limit
```

## Security Model

```
┌─────────────────────────────────────────────────┐
│           Security Layers                       │
├─────────────────────────────────────────────────┤
│                                                 │
│  Layer 1: No Registration                       │
│  └─ Only admin can create tokens                │
│                                                 │
│  Layer 2: Token-Based Auth                      │
│  └─ 256-bit secure random tokens                │
│                                                 │
│  Layer 3: Session State                         │
│  └─ Auth check on every page load               │
│                                                 │
│  Layer 4: Token Storage                         │
│  └─ Excluded from git (.gitignore)              │
│                                                 │
│  Layer 5: Token Management                      │
│  └─ Can revoke compromised tokens               │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

This visual guide helps understand the complete authentication and lead limit system!
