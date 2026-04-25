import sqlite3
import bcrypt

conn = sqlite3.connect('attendance.db')
c = conn.cursor()

# Admin credentials
admin_username = 'admin2'
admin_password = 'admin123'
admin_hashed = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt())
c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (admin_username, admin_hashed, 'admin'))

# Employee credentials
employee_username = 'employee2'
employee_password = 'emp123'
employee_hashed = bcrypt.hashpw(employee_password.encode('utf-8'), bcrypt.gensalt())
c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (employee_username, employee_hashed, 'employee'))

conn.commit()
conn.close()

print("Users created successfully.")
