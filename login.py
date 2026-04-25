import sqlite3

# Connect to the correct database file
db_path = r"C:\Users\NANDHA M\attendance.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if the "user" table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user';")
table_exists = cursor.fetchone()

if not table_exists:
    print("Error: 'user' table does not exist in the database.")
else:
    # Get user input
    username = input("Enter username: ")
    password = input("Enter password: ")

    # Check if the user exists in the database
    cursor.execute("SELECT * FROM user WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()

    if user:
        print("Login successful!")
    else:
        print("Invalid username or password.")

# Close the connection
conn.close()

