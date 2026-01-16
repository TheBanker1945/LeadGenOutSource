# Location Specificity Guide

## State/Province Field (NEW!)

The State field has been added to make location searches more specific, especially for cities with duplicate names in the USA.

### How It Works:

- **If State is empty**: Scraper works as usual (City, Country)
- **If State is filled**: Location becomes "City, State, Country" for more precise results

### Examples:

| City | State | Country | Result Query |
|------|-------|---------|--------------|
| Springfield | IL | USA | Springfield, IL, USA |
| Springfield | MA | USA | Springfield, MA, USA |
| Portland | OR | USA | Portland, OR, USA |
| Portland | ME | USA | Portland, ME, USA |
| Cambridge | | USA | Cambridge, USA (ambiguous) |
| Cambridge | MA | USA | Cambridge, MA, USA (specific) |

### USA State Abbreviations:

```
AL - Alabama          MT - Montana
AK - Alaska           NE - Nebraska
AZ - Arizona          NV - Nevada
AR - Arkansas         NH - New Hampshire
CA - California       NJ - New Jersey
CO - Colorado         NM - New Mexico
CT - Connecticut      NY - New York
DE - Delaware         NC - North Carolina
FL - Florida          ND - North Dakota
GA - Georgia          OH - Ohio
HI - Hawaii           OK - Oklahoma
ID - Idaho            OR - Oregon
IL - Illinois         PA - Pennsylvania
IN - Indiana          RI - Rhode Island
IA - Iowa             SC - South Carolina
KS - Kansas           SD - South Dakota
KY - Kentucky         TN - Tennessee
LA - Louisiana        TX - Texas
ME - Maine            UT - Utah
MD - Maryland         VT - Vermont
MA - Massachusetts    VA - Virginia
MI - Michigan         WA - Washington
MN - Minnesota        WV - West Virginia
MS - Mississippi      WI - Wisconsin
MO - Missouri         WY - Wyoming
```

## Other Ways to Improve Location Specificity

### 1. **Use Full City Names**
❌ Bad: "St Pete"
✅ Good: "St Petersburg"

### 2. **Include ZIP Codes (Future Enhancement)**
- Could add ZIP code field for ultra-specific targeting
- Example: "Chicago 60601" for downtown only

### 3. **Use Neighborhood Names**
- Already supported with neighborhood splitting
- Example: "Downtown", "Midtown", "Financial District"

### 4. **Specify Metropolitan Areas**
❌ Bad: Just "LA" (ambiguous)
✅ Good: "Los Angeles" + State "CA"

### 5. **Use Proper Formatting**
- Avoid abbreviations unless commonly used
- Use proper capitalization
- Don't use special characters

### 6. **Combine with Niche Keywords**
Make your niche more specific:
- ❌ "restaurants" (too broad)
- ✅ "italian restaurants" (more targeted)
- ✅ "seafood restaurants" (even better)

## Common Duplicate City Names in USA

Cities that benefit most from the State field:

### High Priority (Many duplicates):
- **Springfield** - Found in 30+ states
- **Franklin** - Found in 30+ states
- **Clinton** - Found in 27+ states
- **Arlington** - Found in multiple states
- **Madison** - Found in multiple states
- **Washington** - Found in 30+ states
- **Manchester** - Found in multiple states
- **Portland** - ME and OR (major cities)
- **Cambridge** - MA and MD (major cities)

### Medium Priority:
- Columbus (OH, GA, IN)
- Salem (OR, MA)
- Richmond (VA, CA, IN)
- Rochester (NY, MN)
- Jackson (MS, MI, TN)

## Best Practices

1. **Always use State for duplicate city names**
   ```
   City: Springfield
   State: IL
   Country: USA
   ```

2. **Can use full state names or abbreviations**
   ```
   State: Illinois  ✅
   State: IL        ✅
   ```

3. **Leave State empty for unique city names**
   ```
   City: Los Angeles
   State: (empty)    ← Not needed, LA is unique
   Country: USA
   ```

4. **For international locations**, State can be used for provinces/regions:
   ```
   City: Toronto
   State: Ontario
   Country: Canada
   ```

5. **Test your location** before running large scrapes
   - Start with 1-2 test locations
   - Verify results are from correct location
   - Then scale up

## Future Enhancement Ideas

### 1. **ZIP Code Targeting** (Not yet implemented)
- Add ZIP code field
- Even more precise than city + state
- Useful for very targeted campaigns

### 2. **Radius Search** (Not yet implemented)
- Specify search radius in miles/km
- Example: "Within 10 miles of downtown"

### 3. **Location Validation** (Not yet implemented)
- Auto-suggest valid locations as you type
- Warn about ambiguous locations
- Show map preview

### 4. **Batch Location Import** (Not yet implemented)
- Import CSV of locations with state info
- Bulk upload for large campaigns

### 5. **Location Templates** (Not yet implemented)
- Save frequently used location sets
- Example: "All major Texas cities with states"

## Need Help?

If you're unsure about a location:
1. Google Maps is your friend - check what they use
2. Use State for any city you're not 100% sure about
3. The scraper will use your exact input in the Google Maps query

## Examples of Good Configuration:

### Example 1: Specific US Cities
```yaml
locations:
  - Springfield
  - Portland
  - Cambridge
country: USA
state: IL
niches:
  - gyms
```

### Example 2: Multiple Cities (same state)
Run separate scrapes for different states, or use neighborhood splitting with the main city having the state specified.

### Example 3: International with Province
```yaml
locations:
  - Toronto
  - Ottawa
country: Canada
state: Ontario
niches:
  - restaurants
```
