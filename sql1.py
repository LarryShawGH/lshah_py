import sqlite3

# Step 1: Connect to database (creates file if it doesn't exist)
conn = sqlite3.connect('example.db')
cursor = conn.cursor()

# Step 2: Create a table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER
    )
''')

# Step 3: Insert data
cursor.execute('INSERT INTO users (name, age) VALUES (?, ?)', ("Alice", 30))
cursor.execute('INSERT INTO users (name, age) VALUES (?, ?)', ("Bob", 25))

# Commit the changes
conn.commit()

# Step 4: Read data
cursor.execute('SELECT * FROM users')
rows = cursor.fetchall()
print("All users:")
for row in rows:
    print(row)

# Step 5: Update data
cursor.execute('UPDATE users SET age = ? WHERE name = ?', (31, "Alice"))
conn.commit()

# Step 6: Delete data
cursor.execute('DELETE FROM users WHERE name = ?', ("Bob",))
conn.commit()

# Final read to see changes
cursor.execute('SELECT * FROM users')
print("\nAfter updates:")
print(cursor.fetchall())

# Close connection
conn.close()
