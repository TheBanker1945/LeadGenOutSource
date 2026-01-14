# 🧪 Testing Checklist

## Pre-Testing Setup

- [x] Authentication tokens generated
- [x] `auth_tokens.json` created
- [x] `.gitignore` updated to exclude `auth_tokens.json`
- [x] All files have no syntax errors

---

## 🔐 Authentication Tests

### Login Page Tests
- [ ] **Test 1.1**: Open login page - should load without errors
  - Command: `python run_dashboard.py`
  - Expected: Login page opens at http://localhost:8501

- [ ] **Test 1.2**: Login with valid token
  - Enter: `e5253049eace80bc217a443dcf985b55dfb88d71af81f67eb692cf50216f3474`
  - Expected: Success message, redirect to dashboard

- [ ] **Test 1.3**: Login with invalid token
  - Enter: `invalid_token_12345`
  - Expected: Error message "Invalid or inactive authentication token"

- [ ] **Test 1.4**: Login with empty token
  - Enter: (leave blank)
  - Expected: Error "Please enter an authentication token"

- [ ] **Test 1.5**: Login with wrong length token
  - Enter: `abc123` (too short)
  - Expected: Error "Token must be 64 characters long"

### Dashboard Access Tests
- [ ] **Test 2.1**: Direct dashboard access without login
  - URL: http://localhost:8501/dashboard.py
  - Expected: Redirect to login page with "Access Denied" message

- [ ] **Test 2.2**: Dashboard access after login
  - Login first, then access dashboard
  - Expected: Dashboard loads normally

- [ ] **Test 2.3**: Session persistence
  - Login → Refresh page
  - Expected: Still logged in, dashboard still accessible

- [ ] **Test 2.4**: Logout functionality
  - Click "🔓 Logout" button in sidebar
  - Expected: Redirect to login page, session cleared

- [ ] **Test 2.5**: Re-login after logout
  - Logout → Enter token again → Login
  - Expected: Can log back in successfully

### Token Management Tests
- [ ] **Test 3.1**: Generate new token
  - Command: `python auth.py`
  - Expected: 3 new tokens displayed and saved

- [ ] **Test 3.2**: Validate token programmatically
  ```python
  from auth import AuthManager
  auth = AuthManager()
  result = auth.validate_token("e5253049eace80bc217a443dcf985b55dfb88d71af81f67eb692cf50216f3474")
  # Expected: True
  ```

- [ ] **Test 3.3**: Revoke token
  ```python
  from auth import AuthManager
  auth = AuthManager()
  auth.revoke_token("token_here")
  # Then try to login with revoked token
  # Expected: Login fails
  ```

- [ ] **Test 3.4**: List all tokens
  ```python
  from auth import AuthManager
  auth = AuthManager()
  tokens = auth.list_all_tokens()
  # Expected: Returns list of all tokens with metadata
  ```

---

## 🎯 Lead Limit Tests

### Basic Lead Limit Tests
- [ ] **Test 4.1**: Set lead limit to 5
  - Configure: Lead Limit = 5
  - Location: Any city
  - Niche: Any niche
  - Expected: Scraper stops after saving exactly 5 leads

- [ ] **Test 4.2**: Set lead limit to 0 (no limit)
  - Configure: Lead Limit = 0
  - Expected: Scraper continues until all results processed

- [ ] **Test 4.3**: Lead limit with filters
  - Configure: Lead Limit = 10, Has Website = Yes
  - Expected: Saves 10 leads that have websites, others filtered out don't count

- [ ] **Test 4.4**: Lead limit display
  - Set limit to 80
  - Check configuration summary
  - Expected: Shows "Lead Limit: 80 leads"

- [ ] **Test 4.5**: Save configuration with lead limit
  - Set limit → Click "💾 Save Configuration"
  - Restart dashboard → Check limit
  - Expected: Limit persists after restart

### Advanced Lead Limit Tests
- [ ] **Test 5.1**: Lead limit with duplicates
  - Configure: Lead Limit = 10
  - Run scraper that finds duplicates
  - Expected: Only new (non-duplicate) saves count toward limit

- [ ] **Test 5.2**: Lead limit across multiple areas
  - Configure: Lead Limit = 20
  - Enable neighborhood splitting
  - Location: Large city (e.g., Toronto)
  - Expected: Total across all neighborhoods = 20, then stops

- [ ] **Test 5.3**: Lead limit with multiple niches
  - Configure: Lead Limit = 50
  - Locations: 2 cities
  - Niches: 2 niches
  - Expected: Stops at 50 total across all combinations

- [ ] **Test 5.4**: Progress display during scraping
  - Start scraping with limit = 30
  - Watch status text
  - Expected: Shows "Saved: X/30" during scraping

- [ ] **Test 5.5**: Limit reached message
  - Set limit = 10
  - Run scraper
  - Expected: Success box shows "⚠️ Lead limit reached: Stopped at 10 leads"

### Edge Cases
- [ ] **Test 6.1**: Lead limit = 1
  - Expected: Stops after first lead saved

- [ ] **Test 6.2**: Lead limit larger than available results
  - Set limit = 1000, but only 50 results available
  - Expected: Saves all 50, no error

- [ ] **Test 6.3**: Lead limit with API limit
  - Set both lead limit and reach API limit
  - Expected: Whichever limit is reached first stops scraper

- [ ] **Test 6.4**: Change limit mid-session
  - Run scraper with limit = 10
  - Change to limit = 50
  - Run again
  - Expected: Second run uses new limit (50)

---

## 🚀 Integration Tests

### Complete Workflow Tests
- [ ] **Test 7.1**: Full workflow - New user
  ```
  1. Start dashboard
  2. Login with token
  3. Configure locations and niches
  4. Set lead limit = 20
  5. Save configuration
  6. Start scraping
  7. Wait for completion
  8. Verify 20 leads saved
  9. Export to CSV
  10. Logout
  ```

- [ ] **Test 7.2**: Multiple users workflow
  ```
  User A:
  1. Login with Token 1
  2. Set limit = 30
  3. Scrape NYC plumbers
  4. Logout
  
  User B:
  1. Login with Token 2
  2. Set limit = 50
  3. Scrape LA dentists
  4. Logout
  
  Expected: Both users' limits work independently
  ```

- [ ] **Test 7.3**: Configuration persistence
  ```
  1. Login
  2. Configure: Limit = 80, Filters = Yes Website
  3. Save
  4. Logout
  5. Login again
  6. Check configuration
  Expected: Limit and filters still set to 80 and Yes Website
  ```

### Error Handling Tests
- [ ] **Test 8.1**: Invalid configuration
  - Empty locations or niches
  - Expected: Appropriate error message

- [ ] **Test 8.2**: API limit exceeded during scraping
  - Expected: Scraper stops gracefully, shows error

- [ ] **Test 8.3**: Network error during scraping
  - Disconnect internet mid-scrape
  - Expected: Error message, partial results saved

- [ ] **Test 8.4**: Database error
  - Lock `leads.db` file
  - Try to scrape
  - Expected: Error message shown

---

## 🔍 Data Validation Tests

### Lead Data Tests
- [ ] **Test 9.1**: Lead limit accuracy
  - Set limit = 25
  - After scraping, count leads in database
  - Command: `python check_db.py`
  - Expected: Exactly 25 new leads (or fewer if not enough results)

- [ ] **Test 9.2**: Duplicate prevention
  - Run scraper twice with same configuration
  - Expected: Second run adds no duplicates (or very few)

- [ ] **Test 9.3**: Filter accuracy
  - Set "Has Website = Yes" and limit = 10
  - Check all 10 leads
  - Expected: All 10 have websites

- [ ] **Test 9.4**: Export accuracy
  - Scrape with limit = 15
  - Export to CSV
  - Count rows in CSV
  - Expected: 15 rows (plus header)

---

## 📊 Dashboard UI Tests

### UI Component Tests
- [ ] **Test 10.1**: Sidebar logout button
  - Visible when logged in
  - Expected: Shows username and logout button

- [ ] **Test 10.2**: Lead limit input
  - Accepts numbers 0-10000
  - Shows help text
  - Expected: Working number input with validation

- [ ] **Test 10.3**: Configuration summary
  - Set various options
  - Check configuration panel
  - Expected: All settings displayed correctly including lead limit

- [ ] **Test 10.4**: Progress indicators
  - Start scraping
  - Watch progress bar and status text
  - Expected: Real-time updates with lead count

- [ ] **Test 10.5**: Success/Error messages
  - Trigger various scenarios
  - Expected: Appropriate colored boxes (green/red/yellow)

---

## 🛡️ Security Tests

### Security Validation
- [ ] **Test 11.1**: Token not in git
  - Command: `git status`
  - Expected: `auth_tokens.json` not listed (in .gitignore)

- [ ] **Test 11.2**: Token storage security
  - Check `auth_tokens.json` file permissions
  - Expected: Only owner can read/write

- [ ] **Test 11.3**: Session hijacking prevention
  - Login → Copy session ID → Use in different browser
  - Expected: Doesn't work (session is browser-specific)

- [ ] **Test 11.4**: Token visibility
  - Check browser DevTools
  - Expected: Token stored in session state only, not in URL

---

## 📝 Documentation Tests

### Documentation Verification
- [ ] **Test 12.1**: AUTHENTICATION_SETUP.md accuracy
  - Follow guide step-by-step
  - Expected: All instructions work correctly

- [ ] **Test 12.2**: QUICK_REFERENCE.md usability
  - Use quick reference for common tasks
  - Expected: All commands work as documented

- [ ] **Test 12.3**: Token list in docs matches reality
  - Check generated tokens vs docs
  - Expected: Tokens in docs match actual tokens

---

## 🎯 Performance Tests

### Performance Validation
- [ ] **Test 13.1**: Login speed
  - Time from token entry to dashboard load
  - Expected: < 2 seconds

- [ ] **Test 13.2**: Lead limit efficiency
  - Set limit = 50
  - Measure time to reach limit
  - Expected: Stops immediately when limit reached (no extra processing)

- [ ] **Test 13.3**: Large limit performance
  - Set limit = 1000
  - Monitor memory usage
  - Expected: No memory leaks or crashes

---

## ✅ Final Validation

### Complete System Test
- [ ] **Test 14.1**: Fresh install simulation
  ```
  1. Generate new tokens
  2. Start dashboard
  3. Login
  4. Configure everything from scratch
  5. Run scraping job with lead limit
  6. Export results
  7. Verify all data correct
  ```

- [ ] **Test 14.2**: Multi-day persistence
  ```
  Day 1: Configure and scrape
  Day 2: Login again, verify config persists
  Day 3: Change config, scrape again
  Expected: All data persists correctly
  ```

---

## 🎊 Sign-Off Checklist

- [ ] All authentication tests passed
- [ ] All lead limit tests passed
- [ ] All integration tests passed
- [ ] All security tests passed
- [ ] Documentation accurate and complete
- [ ] No errors in any files
- [ ] System ready for production use

---

## 📞 Test Results Template

```
Test Date: ___________
Tester: ___________

Authentication Tests: ___/14 passed
Lead Limit Tests: ___/13 passed
Integration Tests: ___/8 passed
Security Tests: ___/4 passed

Total Tests: ___/39 passed
Pass Rate: ___%

Issues Found:
1. 
2. 
3. 

Notes:


Conclusion: [ ] Ready for Production  [ ] Needs Work
```

---

## 💡 Testing Tips

1. **Use fresh browser** - Test in incognito mode to avoid session conflicts
2. **Check console** - Watch browser console for JavaScript errors
3. **Monitor terminal** - Keep eye on terminal output for backend errors
4. **Test incrementally** - Test one feature at a time
5. **Document issues** - Note any problems found during testing
6. **Backup before testing** - Backup `auth_tokens.json` and `leads.db`
7. **Test with real data** - Use actual cities/niches for realistic tests

---

**Good luck with testing! 🚀**
