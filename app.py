from flask import Flask, render_template, request, redirect, url_for, flash
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


if __name__ == '__main__':
    app.run(debug=True)
