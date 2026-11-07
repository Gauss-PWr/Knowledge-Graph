import sqlite3 as sq

conn = sq.connect('kb.sqlite')
cursor = conn.cursor()

cursor.execute('select text from chunks where doc like "vaswani%";')
records = cursor.fetchall()
cursor.execute('select DISTINCT(slug) from docs ')
titles = cursor.fetchall()

with open('test_chunks.md', 'w') as f1, open('titles.txt', 'w') as f2:
    for record in records:
        f1.write(record[0])

    for title in titles:
        row = title[0] + '\n'
        f2.write(row)


conn.close()