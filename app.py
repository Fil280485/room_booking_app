import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Create rooms table
    c.execute('''
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            capacity INTEGER NOT NULL
        )
    ''')

    # Create bookings table
    c.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id INTEGER,
            start_time TEXT,
            end_time TEXT,
            FOREIGN KEY(room_id) REFERENCES rooms(id)
        )
    ''')

    # Adding some sample rooms
    c.execute("INSERT INTO rooms (name, capacity) VALUES ('Room A', 4), ('Room B', 10), ('Room C', 20)")

    conn.commit()
    conn.close()

# Initialize the database when the app starts
init_db()

from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Helper function to get all rooms
def get_rooms():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM rooms")
    rooms = c.fetchall()
    conn.close()
    return rooms

# Helper function to get bookings for a specific room
def get_bookings_for_room(room_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM bookings WHERE room_id = ?", (room_id,))
    bookings = c.fetchall()
    conn.close()
    return bookings

# Helper function to add a booking
def add_booking(room_id, start_time, end_time):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO bookings (room_id, start_time, end_time) VALUES (?, ?, ?)", 
              (room_id, start_time, end_time))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    rooms = get_rooms()
    return render_template('index.html', rooms=rooms)

@app.route('/book/<int:room_id>', methods=['GET', 'POST'])
def book(room_id):
    room = None
    rooms = get_rooms()
    for r in rooms:
        if r[0] == room_id:
            room = r
            break
    
    if request.method == 'POST':
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        add_booking(room_id, start_time, end_time)
        return redirect(url_for('index'))

    return render_template('booking.html', room=room)

@app.route('/view_bookings')
def view_bookings():
    bookings = []
    rooms = get_rooms()
    for room in rooms:
        bookings.append({
            'room': room,
            'bookings': get_bookings_for_room(room[0])
        })
    return render_template('bookings.html', bookings=bookings)

if __name__ == '__main__':
    app.run(debug=True)
