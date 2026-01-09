import pandas as pd
import sqlite3

# Test the extract_main_city function
def extract_main_city(city_str):
    if pd.isna(city_str) or not city_str:
        return ""
    city_str = str(city_str).strip()
    
    # If city contains comma, take the part after comma (main city)
    if ',' in city_str:
        return city_str.split(',')[-1].strip()
    
    # Handle Toronto neighborhoods (they don't have ", Toronto" suffix)
    toronto_neighborhoods = ['Etobicoke', 'Scarborough', 'North York', 'Downtown', 'Yorkville', 
                            'Entertainment District', 'Financial District', 'Junction Triangle',
                            'Kensington Market', 'The Annex', 'The Beaches', 'Leslieville',
                            'Liberty Village', 'Parkdale', 'Mimico', 'Weston']
    if city_str in toronto_neighborhoods:
        return 'Toronto'
    
    # Handle Calgary neighborhoods
    calgary_neighborhoods = ['Beltline', 'Crescent Heights', 'Inglewood', 'Kensington', 'Sunalta',
                           'Bridgeland', 'East Village', 'Forest Lawn', 'Manchester', 'Ogden',
                           'Alyth/Bonnybrook', 'Acadia', 'Midnapore', 'Montgomery']
    if city_str in calgary_neighborhoods:
        return 'Calgary'
    
    # Handle Miami neighborhoods
    miami_neighborhoods = ['Brickell', 'Coconut Grove', 'Edgewater', 'Wynwood', 'Little Havana',
                          'South Beach', 'Overtown', 'Little Haiti', 'Liberty City', 'Allapattah',
                          'West Little River', 'Doral', 'Hialeah', 'Medley', 'Opa-locka', 'Sweetwater']
    if city_str in miami_neighborhoods:
        return 'Miami'
    
    # Otherwise, return as is (it's already a main city)
    return city_str

# Test with database
conn = sqlite3.connect('leads.db')
df = pd.read_sql_query('SELECT DISTINCT city FROM leads', conn)
df['main_city'] = df['city'].apply(extract_main_city)

print('\n' + '='*80)
print('City Mapping Test:')
print('='*80)
print(f"{'Original City':<40} -> {'Main City':<20}")
print('-'*80)
for _, row in df.iterrows():
    print(f"{row['city']:<40} -> {row['main_city']:<20}")

print('\n' + '='*80)
print('Unique Main Cities:')
print('='*80)
for city in sorted(df['main_city'].unique()):
    print(f"  - {city}")

# Test export query for Toronto
print('\n' + '='*80)
print('Testing export query for Toronto plumbers:')
print('='*80)
cursor = conn.execute("""
    SELECT city, company_name 
    FROM leads 
    WHERE niche = 'plumbers'
      AND (city LIKE '%,Toronto' OR city IN ('Etobicoke','Scarborough','North York','Downtown','Yorkville','Entertainment District','Financial District','Junction Triangle','Kensington Market','The Annex','The Beaches','Leslieville','Liberty Village','Parkdale','Mimico','Weston'))
    LIMIT 10
""")
results = cursor.fetchall()
print(f"Found {len(results)} results (showing first 10):")
for row in results:
    print(f"  {row[0]:<40} | {row[1]}")

conn.close()
