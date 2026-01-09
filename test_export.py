import sqlite3
from src.database.repository import LeadRepository

# Test the export query
repo = LeadRepository()

print('\n' + '='*80)
print('Testing Export Queries:')
print('='*80)

# Test 1: Get all leads for Toronto
print('\n1. Testing Toronto + plumbers:')
leads = repo.get_all_leads(city='Toronto', niche='plumbers')
print(f'   Found: {len(leads)} leads')
if leads:
    print(f'   Sample: {leads[0]["company_name"]} in {leads[0]["city"]}')

# Test 2: Get all leads for Den Haag
print('\n2. Testing Den Haag + Schilder:')
leads = repo.get_all_leads(city='Den Haag', niche='Schilder')
print(f'   Found: {len(leads)} leads')
if leads:
    print(f'   Sample: {leads[0]["company_name"]} in {leads[0]["city"]}')

# Test 3: Get all plumbers (no city filter)
print('\n3. Testing all plumbers (no city filter):')
leads = repo.get_all_leads(niche='plumbers')
print(f'   Found: {len(leads)} leads')

# Test 4: Direct SQL query to see what's in DB
print('\n4. Direct SQL check - plumbers in database:')
conn = sqlite3.connect('leads.db')
cursor = conn.execute("SELECT COUNT(*) FROM leads WHERE niche = 'plumbers'")
count = cursor.fetchone()[0]
print(f'   Total plumbers in DB: {count}')

cursor = conn.execute("SELECT DISTINCT niche FROM leads")
niches = [row[0] for row in cursor.fetchall()]
print(f'   All niches in DB: {niches}')

conn.close()
