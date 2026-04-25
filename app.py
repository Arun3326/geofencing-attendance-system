from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
import sqlite3
import bcrypt
from datetime import datetime
import pytz
from io import BytesIO
from reportlab.pdfgen import canvas
from geopy.distance import geodesic

app = Flask(__name__)
app.secret_key = 'your_secret_key'

OFFICE_LOCATION = (11.100998, 76.968579)

def init_db():
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'employee'
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            date TEXT NOT NULL,
            checkin TEXT,
            checkout TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY,
            radius INTEGER
        )
    ''')

    c.execute('SELECT COUNT(*) FROM settings')
    if c.fetchone()[0] == 0:
        c.execute('INSERT INTO settings (id, radius) VALUES (?, ?)', (1, 500))

    conn.commit()
    conn.close()

init_db()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')

        conn = sqlite3.connect('attendance.db')
        c = conn.cursor()
        c.execute("SELECT password, role FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        conn.close()

        if user and bcrypt.checkpw(password, user[0]):
            session['username'] = username
            session['role'] = user[1]
            return redirect(url_for('admin_dashboard' if user[1] == 'admin' else 'geofence'))
        else:
            return "Invalid credentials"
    return render_template('login.html')

@app.route('/geofence')
def geofence():
    if session.get('role') != 'employee':
        return redirect(url_for('login'))
    return render_template('geofence.html')

@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    if session.get('role') != 'employee':
        return jsonify({'message': 'Unauthorized'}), 403

    username = session['username']
    try:
        latitude = float(request.form.get('latitude'))
        longitude = float(request.form.get('longitude'))
    except:
        return jsonify({'message': 'Invalid location data'}), 400

    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute('SELECT radius FROM settings WHERE id = 1')
    radius = c.fetchone()[0]
    conn.close()

    distance = geodesic((latitude, longitude), OFFICE_LOCATION).meters
    if distance > radius:
        return jsonify({'message': '❌ Outside allowed geofence'}), 400

    now = datetime.now(pytz.timezone("Asia/Kolkata"))
    today = now.strftime('%Y-%m-%d')
    now_time = now.strftime('%H:%M:%S')

    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute("SELECT id, checkin, checkout FROM attendance WHERE username = ? AND date = ?", (username, today))
    record = c.fetchone()

    if record:
        if not record[2]:
            c.execute("UPDATE attendance SET checkout = ? WHERE id = ?", (now_time, record[0]))
            msg = "✅ Checked out successfully!"
        else:
            msg = "🟡 Already checked in and out today."
    else:
        c.execute("INSERT INTO attendance (username, date, checkin) VALUES (?, ?, ?)", (username, today, now_time))
        msg = "✅ Checked in successfully!"

    conn.commit()
    conn.close()
    return jsonify({'message': msg, 'redirect': url_for('attendance_history')})

@app.route('/attendance_history')
def attendance_history():
    if session.get('role') != 'employee':
        return redirect(url_for('login'))

    username = session['username']
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute("SELECT date, checkin, checkout FROM attendance WHERE username = ?", (username,))
    records = c.fetchall()
    conn.close()
    return render_template('attendance_history.html', username=username, records=records)

@app.route('/admin_dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute("SELECT username, date, checkin, checkout FROM attendance ORDER BY date DESC")
    records = c.fetchall()
    c.execute("SELECT radius FROM settings WHERE id = 1")
    radius = c.fetchone()[0]
    conn.close()
    return render_template('admin_dashboard.html', records=records, radius=radius)

@app.route('/update_radius', methods=['POST'])
def update_radius():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    new_radius = int(request.form.get('radius'))
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute("UPDATE settings SET radius = ? WHERE id = 1", (new_radius,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/export_pdf')
def export_pdf():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute("SELECT username, date, checkin, checkout FROM attendance ORDER BY date DESC")
    records = c.fetchall()
    conn.close()

    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.setFont("Helvetica", 12)
    p.drawString(200, 800, "Attendance Report")
    y = 760
    for i, (u, d, ci, co) in enumerate(records):
        p.drawString(50, y, f"{i+1}. {u} - {d} - In: {ci} - Out: {co or '---'}")
        y -= 20
        if y < 40:
            p.showPage()
            y = 800
    p.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='attendance.pdf', mimetype='application/pdf')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)


