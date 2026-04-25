import sqlite3
import bcrypt

# Connect to the database
conn = sqlite3.connect('attendance.db')
c = conn.cursor()

# User data: (username, password, role)
users = [
    ('admin', 'admin123', 'admin'),
    ('employee1', 'emp123', 'employee')
]

for username, password, role in users:
    # Hash password
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Insert user if not already present
    try:
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, hashed, role))
        print(f"User '{username}' with role '{role}' created successfully.")
    except sqlite3.IntegrityError:
        print(f"User '{username}' already exists. Skipping.")

# Save and close
conn.commit()
conn.close()
