from app import db, User

db.create_all()

# Add a default user (admin)
admin = User(username="admin", password="password123")
db.session.add(admin)
db.session.commit()

print("Admin user created: Username - admin, Password - password123")
