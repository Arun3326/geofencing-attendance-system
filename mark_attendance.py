import requests

BASE_URL = "http://127.0.0.1:5000"
session = requests.Session()

# Login credentials
login_data = {
    "username": "admin",
    "password": "password123"
}

# 1️⃣ Login Request
login_response = session.post(f"{BASE_URL}/", data=login_data)  # Changed to match the Flask login route

print("\n🔹 Login Attempt:")
print("🔹 Status Code:", login_response.status_code)
print("🔹 Response Text:", login_response.text)  # Debugging login response

if login_response.status_code == 200 and "Invalid" not in login_response.text:
    print("✅ Login successful!")

    # 2️⃣ Mark Attendance Request
    attendance_data = {
        "latitude": 12.971598,  # Example coordinates
        "longitude": 77.594566
    }

    response = session.get(f"{BASE_URL}/mark_attendance")  # Changed to GET request to match Flask route

    print("\n🔹 Marking Attendance:")
    print("🔹 Status Code:", response.status_code)
    print("🔹 Response:", response.text)  # Debugging attendance response

    if response.status_code == 200:
        print("✅ Attendance marked successfully!")
    else:
        print("❌ Failed to mark attendance.")

else:
    print("❌ Login failed. Check username/password or Flask server response.")
