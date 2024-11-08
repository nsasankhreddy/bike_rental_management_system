from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime

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

# Route to add a new customer
@app.route('/add_customer', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Customers (first_name, last_name, email) VALUES (?, ?, ?)", 
                       (first_name, last_name, email))
        conn.commit()
        conn.close()
        flash("Customer added successfully!", "success")
        return redirect(url_for('view_customers'))
    
    return render_template('add_customer.html')

# Route to view all customers
@app.route('/view_customers')
def view_customers():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Customers")
    customers = cursor.fetchall()
    conn.close()
    return render_template('view_customers.html', customers=customers)

# Route to edit a customer
@app.route('/edit_customer/<int:customer_id>', methods=['GET', 'POST'])
def edit_customer(customer_id):
    conn = connect_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        cursor.execute("UPDATE Customers SET first_name = ?, last_name = ?, email = ? WHERE customer_id = ?", 
                       (first_name, last_name, email, customer_id))
        conn.commit()
        conn.close()
        flash("Customer updated successfully!", "success")
        return redirect(url_for('view_customers'))
    
    cursor.execute("SELECT * FROM Customers WHERE customer_id = ?", (customer_id,))
    customer = cursor.fetchone()
    conn.close()
    return render_template('edit_customer.html', customer=customer)

# Route to delete a customer
@app.route('/delete_customer/<int:customer_id>', methods=['POST'])
def delete_customer(customer_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Customers WHERE customer_id = ?", (customer_id,))
    conn.commit()
    conn.close()
    flash("Customer deleted successfully!", "success")
    return redirect(url_for('view_customers'))

# Route to add a new bike
@app.route('/add_bike', methods=['GET', 'POST'])
def add_bike():
    if request.method == 'POST':
        model = request.form['model']
        bike_type = request.form['type']
        availability_status = request.form.get('availability_status') == 'on'
        
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Bikes (model, type, availability_status) VALUES (?, ?, ?)", 
                       (model, bike_type, availability_status))
        conn.commit()
        conn.close()
        flash("Bike added successfully!", "success")
        return redirect(url_for('view_bikes'))
    
    return render_template('add_bike.html')

# Route to view all bikes
@app.route('/view_bikes')
def view_bikes():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Bikes")
    bikes = cursor.fetchall()
    conn.close()
    return render_template('view_bikes.html', bikes=bikes)

# Route to edit a bike
@app.route('/edit_bike/<int:bike_id>', methods=['GET', 'POST'])
def edit_bike(bike_id):
    conn = connect_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        model = request.form['model']
        bike_type = request.form['type']
        availability_status = request.form.get('availability_status') == 'on'
        cursor.execute("UPDATE Bikes SET model = ?, type = ?, availability_status = ? WHERE bike_id = ?", 
                       (model, bike_type, availability_status, bike_id))
        conn.commit()
        conn.close()
        flash("Bike updated successfully!", "success")
        return redirect(url_for('view_bikes'))
    
    cursor.execute("SELECT * FROM Bikes WHERE bike_id = ?", (bike_id,))
    bike = cursor.fetchone()
    conn.close()
    return render_template('edit_bike.html', bike=bike)

# Route to delete a bike
@app.route('/delete_bike/<int:bike_id>', methods=['POST'])
def delete_bike(bike_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Bikes WHERE bike_id = ?", (bike_id,))
    conn.commit()
    conn.close()
    flash("Bike deleted successfully!", "success")
    return redirect(url_for('view_bikes'))

# Route to add a new rental
@app.route('/add_rental', methods=['GET', 'POST'])
def add_rental():
    if request.method == 'POST':
        customer_id = request.form['customer_id']
        bike_id = request.form['bike_id']
        rental_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        expected_return_date = request.form['expected_return_date']

        conn = connect_db()
        cursor = conn.cursor()

        # Check if the bike is available for rent
        cursor.execute("SELECT availability_status, price_per_hour FROM Bikes WHERE bike_id = ?", (bike_id,))
        bike = cursor.fetchone()
        
        if bike and bike['availability_status']:
            # Insert the rental record with the expected return date
            cursor.execute("INSERT INTO Rentals (customer_id, bike_id, rental_date, expected_return_date) VALUES (?, ?, ?, ?)", 
                           (customer_id, bike_id, rental_date, expected_return_date))
            cursor.execute("UPDATE Bikes SET availability_status = 0 WHERE bike_id = ?", (bike_id,))
            conn.commit()
            flash("Rental record created successfully!", "success")
        else:
            flash("The selected bike is not available for rent.", "danger")

        conn.close()
        return redirect(url_for('view_rentals'))

    # Fetch available customers and bikes for selection in the form
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Customers")
    customers = cursor.fetchall()
    cursor.execute("SELECT * FROM Bikes WHERE availability_status = 1")
    available_bikes = cursor.fetchall()
    conn.close()

    return render_template('add_rental.html', customers=customers, bikes=available_bikes)

# Route to view all rentals
@app.route('/view_rentals')
def view_rentals():
    conn = connect_db()
    cursor = conn.cursor()
    query = '''
    SELECT Rentals.rental_id, Customers.first_name, Customers.last_name, Bikes.model, Rentals.rental_date
    FROM Rentals
    JOIN Customers ON Rentals.customer_id = Customers.customer_id
    JOIN Bikes ON Rentals.bike_id = Bikes.bike_id
    '''
    cursor.execute(query)
    rentals = cursor.fetchall()
    conn.close()
    return render_template('view_rentals.html', rentals=rentals)

# Route to process a return
@app.route('/return_bike/<int:rental_id>', methods=['GET', 'POST'])
def return_bike(rental_id):
    if request.method == 'POST':
        return_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        conn = connect_db()
        cursor = conn.cursor()

        # Get rental details, including bike type and rental start time
        cursor.execute("""
        SELECT Rentals.rental_date, Bikes.price_per_hour
        FROM Rentals
        JOIN Bikes ON Rentals.bike_id = Bikes.bike_id
        WHERE Rentals.rental_id = ?
        """, (rental_id,))
        rental = cursor.fetchone()

        if rental:
            rental_start = datetime.strptime(rental['rental_date'], '%Y-%m-%d %H:%M:%S')
            return_time = datetime.strptime(return_date, '%Y-%m-%d %H:%M:%S')
            rental_duration = (return_time - rental_start).total_seconds() / 3600  # in hours

            # Calculate total price based on the type of vehicle
            price_per_hour = rental['price_per_hour']
            total_price = round(rental_duration * price_per_hour, 2)

            # Insert the return record with total price
            cursor.execute("INSERT INTO Returns (rental_id, return_date, late_fee) VALUES (?, ?, ?)", 
                           (rental_id, return_date, total_price))

            # Update bike availability status
            cursor.execute("UPDATE Bikes SET availability_status = 1 WHERE bike_id = (SELECT bike_id FROM Rentals WHERE rental_id = ?)", (rental_id,))
            conn.commit()
            flash(f"Bike returned successfully! Total charge: ${total_price}", "success")
        else:
            flash("Rental not found.", "danger")

        conn.close()
        return redirect(url_for('view_rentals'))

    return render_template('return_bike.html', rental_id=rental_id)

# Route to reset the database
@app.route('/reset_database', methods=['POST'])
def reset_database():
    conn = connect_db()
    cursor = conn.cursor()

    # Clear all data from the tables
    cursor.execute("DELETE FROM Rentals")
    cursor.execute("DELETE FROM Returns")
    cursor.execute("DELETE FROM Bikes")
    cursor.execute("DELETE FROM Customers")

    # Optionally reset auto-increment values
    cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('Rentals', 'Returns', 'Bikes', 'Customers')")

    conn.commit()
    conn.close()

    # This message will show after the reset has been confirmed by the user on the frontend
    flash("Database reset successfully!", "warning")
    return redirect(url_for('index'))

# Route to show the most rented bikes
@app.route('/most_rented_bikes')
def most_rented_bikes():
    conn = connect_db()
    cursor = conn.cursor()
    query = '''
    SELECT Bikes.model, COUNT(Rentals.bike_id) AS rental_count
    FROM Rentals
    JOIN Bikes ON Rentals.bike_id = Bikes.bike_id
    GROUP BY Bikes.model
    ORDER BY rental_count DESC
    LIMIT 5;
    '''
    cursor.execute(query)
    most_rented = cursor.fetchall()
    conn.close()
    return render_template('most_rented_bikes.html', most_rented=most_rented)

# Route to show customers with overdue rentals
@app.route('/overdue_customers')
def overdue_customers():
    conn = connect_db()
    cursor = conn.cursor()
    query = '''
    SELECT Customers.first_name, Customers.last_name, Rentals.rental_date
    FROM Rentals
    JOIN Customers ON Rentals.customer_id = Customers.customer_id
    LEFT JOIN Returns ON Rentals.rental_id = Returns.rental_id
    WHERE Returns.return_date IS NULL AND Rentals.rental_date < DATE('now', '-7 days');
    '''
    cursor.execute(query)
    overdue_customers = cursor.fetchall()
    conn.close()
    return render_template('overdue_customers.html', overdue_customers=overdue_customers)

# Route to show total revenue from late fees
@app.route('/total_revenue')
def total_revenue():
    conn = connect_db()
    cursor = conn.cursor()
    query = '''
    SELECT SUM(late_fee) AS total_revenue
    FROM Returns;
    '''
    cursor.execute(query)
    total_revenue = cursor.fetchone()['total_revenue']
    
    # Handle None value if there are no returns
    total_revenue = total_revenue if total_revenue is not None else 0.0
    
    conn.close()
    return render_template('total_revenue.html', total_revenue=total_revenue)

@app.route('/rental_history')
def rental_history():
    conn = connect_db()
    cursor = conn.cursor()
    query = '''
    SELECT Rentals.rental_id, Customers.first_name, Customers.last_name, Bikes.model, Rentals.rental_date, Returns.return_date, Returns.late_fee
    FROM Rentals
    JOIN Customers ON Rentals.customer_id = Customers.customer_id
    JOIN Bikes ON Rentals.bike_id = Bikes.bike_id
    JOIN Returns ON Rentals.rental_id = Returns.rental_id
    ORDER BY Rentals.rental_date DESC;
    '''
    cursor.execute(query)
    rental_history = cursor.fetchall()
    conn.close()
    return render_template('rental_history.html', rental_history=rental_history)


if __name__ == '__main__':
    app.run(debug=True)
