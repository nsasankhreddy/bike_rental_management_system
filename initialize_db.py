import sqlite3

# Function to initialize the database and create tables if they don't exist
def initialize_db():
    conn = sqlite3.connect('bike_rental.db')
    cursor = conn.cursor()

    # Create Customers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Customers (
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL
    )
    ''')

    # Create Bikes table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Bikes (
        bike_id INTEGER PRIMARY KEY AUTOINCREMENT,
        model TEXT NOT NULL,
        type TEXT NOT NULL CHECK (type IN ('road', 'mountain', 'hybrid')),
        availability_status BOOLEAN DEFAULT TRUE
    )
    ''')

    # Create Rentals table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Rentals (
        rental_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        bike_id INTEGER,
        rental_date TEXT NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES Customers(customer_id),
        FOREIGN KEY (bike_id) REFERENCES Bikes(bike_id)
    )
    ''')

    # Create Returns table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Returns (
        return_id INTEGER PRIMARY KEY AUTOINCREMENT,
        rental_id INTEGER,
        return_date TEXT NOT NULL,
        late_fee REAL DEFAULT 0.0,
        FOREIGN KEY (rental_id) REFERENCES Rentals(rental_id)
    )
    ''')

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

# Run the initialization function if this script is executed directly
if __name__ == '__main__':
    initialize_db()
