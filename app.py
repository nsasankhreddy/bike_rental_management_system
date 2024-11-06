from flask import Flask, render_template
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session and flash messages

# Function to connect to the SQLite database
def connect_db():
    conn = sqlite3.connect('bike_rental.db')
    conn.row_factory = sqlite3.Row  # Allows accessing columns by name
    return conn

# Homepage route
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
