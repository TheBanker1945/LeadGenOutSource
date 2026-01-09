import sqlite3

conn = sqlite3.connect('leads.db')
cursor = conn.execute('SELECT city, company_name FROM leads LIMIT 20')
print('\n' + '='*60)
print('Sample city values from database:')
print('='*60)
for row in cursor.fetchall():
    print(f'{row[0]:40} | {row[1]}')

print('\n' + '='*60)
print('Unique city values:')
print('='*60)
cursor = conn.execute('SELECT DISTINCT city FROM leads ORDER BY city')
for row in cursor.fetchall():
    print(f'  {row[0]}')

conn.close()
