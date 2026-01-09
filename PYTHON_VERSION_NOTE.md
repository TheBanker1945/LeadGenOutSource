# Python Version Compatibility Notice

## ⚠️ Neighborhood Splitting Feature

The **neighborhood splitting feature** (which uses Gemini AI to break cities into 10-15 areas for comprehensive coverage) requires the `google-generativeai` package.

### Current Limitation

**Python 3.13 is NOT compatible** with `google-generativeai` due to:

- Missing pre-built wheels for grpcio
- Compilation issues with long Windows paths
- Rust compiler requirements for pydantic-core

### Solutions

#### Option 1: Disable Neighborhood Splitting (Quick Fix)

Edit [config.yaml](config.yaml) and set:

```yaml
use_neighborhood_splitting: false
```

This allows you to use the tool with Python 3.13, but:

- ✅ All features work (scraping, filtering, CSV export, rate limiting)
- ❌ Cities are NOT split into neighborhoods (less comprehensive results)
- ✅ No Gemini API calls (saves API costs)

#### Option 2: Downgrade Python (Full Features)

Install Python 3.11 or 3.12 for full neighborhood splitting support:

1. **Download Python 3.12:**

   - Visit: https://www.python.org/downloads/
   - Download Python 3.12.x (latest 3.12 version)
   - Install for Windows

2. **Recreate Virtual Environment:**

   ```powershell
   # Remove old venv
   Remove-Item -Recurse -Force .venv

   # Create new venv with Python 3.12
   py -3.12 -m venv .venv

   # Activate
   .venv\Scripts\Activate

   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Keep Neighborhood Splitting Enabled:**
   ```yaml
   use_neighborhood_splitting: true
   ```

### Current Status

You are running **Python 3.13**, which means:

- ⚠️ Dashboard will show a warning about neighborhood splitting
- ✅ All other features work normally
- 📝 Set `use_neighborhood_splitting: false` in config to hide the warning

### When Will Python 3.13 Be Supported?

The `google-generativeai` package will support Python 3.13 when:

- grpcio provides pre-built wheels for Python 3.13
- pydantic v2 fully supports Python 3.13 without Rust compilation

**ETA: Q1-Q2 2026** (estimated)

---

## Summary

| Python Version | Neighborhood Splitting | All Other Features |
| -------------- | ---------------------- | ------------------ |
| 3.11 ✅        | ✅ Works               | ✅ Works           |
| 3.12 ✅        | ✅ Works               | ✅ Works           |
| 3.13 ⚠️        | ❌ Doesn't Work        | ✅ Works           |

**Recommended:** Python 3.12 for best compatibility.
