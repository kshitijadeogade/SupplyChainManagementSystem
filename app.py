from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from config import Config
from db import init_db
import MySQLdb.cursors

app = Flask(__name__)
app.config.from_object(Config)

# Initialize MySQL
mysql = init_db(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User Class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

# User Loader Callback
@login_manager.user_loader
def load_user(user_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM Users WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()
    if user:
        return User(id=user['user_id'], username=user['username'], password=user['password'])
    return None

# Home Route
@app.route('/')
def index():
    return render_template('index.html')

# Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM Users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register'))
        hashed_password = generate_password_hash(password)
        cursor.execute("INSERT INTO Users (username, password) VALUES (%s, %s)", (username, hashed_password))
        mysql.connection.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM Users WHERE username = %s", (username,))
        user = cursor.fetchone()
        if user and check_password_hash(user['password'], password):
            user_obj = User(id=user['user_id'], username=user['username'], password=user['password'])
            login_user(user_obj)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html')

# Dashboard Route
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=current_user.username)

# Logout Route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Supplier Management Routes

# View Suppliers
@app.route('/suppliers')
@login_required
def suppliers():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM Suppliers")
    suppliers = cursor.fetchall()
    return render_template('suppliers.html', suppliers=suppliers)



# Add Supplier
@app.route('/add_supplier', methods=['GET', 'POST'])
@login_required
def add_supplier():
    if request.method == 'POST':
        name = request.form['name']
        contact_info = request.form['contact_info']
        address = request.form['address']
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO Suppliers (name, contact_info, address) VALUES (%s, %s, %s)",
                       (name, contact_info, address))
        mysql.connection.commit()
        flash('Supplier added successfully!', 'success')
        return redirect(url_for('suppliers'))
    return render_template('add_supplier.html')



# Edit Supplier
@app.route('/edit_supplier/<int:supplier_id>', methods=['GET', 'POST'])
@login_required
def edit_supplier(supplier_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        name = request.form['name']
        contact_info = request.form['contact_info']
        address = request.form['address']
        cursor.execute("UPDATE Suppliers SET name=%s, contact_info=%s, address=%s WHERE supplier_id=%s",
                       (name, contact_info, address, supplier_id))
        mysql.connection.commit()
        flash('Supplier updated successfully!', 'success')
        return redirect(url_for('suppliers'))
    cursor.execute("SELECT * FROM Suppliers WHERE supplier_id = %s", (supplier_id,))
    supplier = cursor.fetchone()
    return render_template('edit_supplier.html', supplier=supplier)

# Delete Supplier
@app.route('/delete_supplier/<int:supplier_id>', methods=['POST'])
@login_required
def delete_supplier(supplier_id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM Suppliers WHERE supplier_id = %s", (supplier_id,))
    mysql.connection.commit()
    flash('Supplier deleted successfully!', 'success')
    return redirect(url_for('suppliers'))


# View Products
@app.route('/products')
@login_required
def products():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM Products")
    products = cursor.fetchall()
    for product in products:
        id = product["supplier_id"]
        product["supplier"] = getSupplierById(id)
    return render_template('products.html', products=products)

# Add Product
@app.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        quantity_in_stock = request.form['quantity_in_stock']
        supplier_id = request.form['supplier_id']
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO Products (name,description, price, quantity_in_stock, supplier_id) VALUES (%s, %s, %s, %s, %s)",
                       (name, description, price, quantity_in_stock, supplier_id))
        mysql.connection.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('products'))
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Suppliers")
    suppliers = cursor.fetchall()
    return render_template('add_product.html', suppliers=suppliers)

# Edit Product
@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        quantity_in_stock = request.form['quantity_in_stock']
        supplier_id = request.form['supplier_id']
        cursor.execute("UPDATE Products SET name=%s, description=%s, price=%s, quantity_in_stock=%s, supplier_id=%s WHERE product_id=%s",
                       (name, description, price, quantity_in_stock, supplier_id, product_id))
        mysql.connection.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('products'))
    cursor.execute("SELECT * FROM Products WHERE product_id = %s", (product_id,))
    product = cursor.fetchone()
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Suppliers")
    suppliers = cursor.fetchall()
    return render_template('edit_product.html', product=product, suppliers=suppliers)

# Delete Product
@app.route('/delete_Product/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM Products WHERE product_id = %s", (product_id,))
    mysql.connection.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('products'))

# Orders management routes

# View Orders
@app.route('/orders')
@login_required
def orders():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM Orders")
    orders = cursor.fetchall()
    for order in orders:
        id = order["product_id"]
        order["product"] = getProductById(id)
    return render_template('orders.html', orders=orders)

# Add Orders
@app.route('/add_order', methods=['GET', 'POST'])
@login_required
def add_order():
    if request.method == 'POST':
        product_id = request.form['product_id']
        quantity = request.form['quantity']
        order_date = request.form['order_date']
        status = request.form['status']
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO Orders (product_id, quantity, order_date, status) VALUES (%s, %s, %s, %s)",
                       (product_id, quantity, order_date, status))
        mysql.connection.commit()
        flash('Order added successfully!', 'success')
        return redirect(url_for('orders'))
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Products")
    products = cursor.fetchall()
    return render_template('add_order.html', products=products)

# Edit Order
@app.route('/edit_order/<int:order_id>', methods=['GET', 'POST'])
@login_required
def edit_order(order_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        product_id = request.form['product_id']
        quantity = request.form['quantity']
        order_date = request.form['order_date']
        status = request.form['status']
        cursor.execute("UPDATE Orders SET product_id=%s, quantity=%s, order_date=%s, status=%s WHERE order_id=%s",
                       (product_id,quantity, order_date, status, order_id))
        mysql.connection.commit()
        flash('Order updated successfully!', 'success')
        return redirect(url_for('orders'))
    cursor.execute("SELECT * FROM Orders WHERE order_id = %s", (order_id,))
    order = cursor.fetchone()
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Products")
    products = cursor.fetchall()
    return render_template('edit_order.html', order=order, products=products)

# Delete Order
@app.route('/delete_order/<int:order_id>', methods=['POST'])
@login_required
def delete_order(order_id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM Orders WHERE order_id = %s", (order_id,))
    mysql.connection.commit()
    flash('Order deleted successfully!', 'success')
    return redirect(url_for('orders'))

# Inventory management routes

# View Inventory
@app.route('/inventory')
@login_required
def inventory():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM Inventory")
    inventory = cursor.fetchall()
    for item in inventory:
        id = item["product_id"]
        item["product"] = getProductById(id)
    return render_template('inventory.html', inventory=inventory)

# Add Inventory
@app.route('/add_inventory', methods=['GET', 'POST'])
@login_required
def add_inventory():
    if request.method == 'POST':
        product_id = request.form['product_id']
        warehouse_location= request.form['location']
        quantity = request.form['quantity']
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO Inventory (product_id, warehouse_location, quantity) VALUES (%s, %s, %s)",
                       (product_id, warehouse_location, quantity))
        mysql.connection.commit()
        flash('Inventory added successfully!', 'success')
        return redirect(url_for('inventory'))
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Products")
    products = cursor.fetchall()
    return render_template('add_inventory.html', products=products)

# Edit Inventory
@app.route('/edit_inventory/<int:inventory_id>', methods=['GET', 'POST'])
@login_required
def edit_inventory(inventory_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        product_id = request.form['product_id']
        warehouse_location= request.form['location']
        quantity = request.form['quantity']
        cursor.execute("UPDATE Inventory SET product_id=%s,warehouse_location=%s, quantity=%s WHERE inventory_id=%s",
                       (product_id,warehouse_location,quantity, inventory_id))
        mysql.connection.commit()
        flash('Inventory updated successfully!', 'success')
        return redirect(url_for('inventory'))
    cursor.execute("SELECT * FROM Inventory WHERE inventory_id = %s", (inventory_id,))
    inventory = cursor.fetchone()
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Products")
    products = cursor.fetchall()
    return render_template('edit_inventory.html', inventory=inventory, products=products)

# Delete Inventory
@app.route('/delete_inventory/<int:inventory_id>', methods=['POST'])
@login_required
def delete_inventory(inventory_id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM Inventory WHERE inventory_id = %s", (inventory_id,))
    mysql.connection.commit()
    flash('Inventory deleted successfully!', 'success')
    return redirect(url_for('inventory'))

def getSupplierById(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    query = "SELECT * FROM Suppliers WHERE supplier_id = " + str(id)
    cursor.execute(query)
    supplier = cursor.fetchone()
    return supplier


def getProductById(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    query = "SELECT * FROM Products WHERE product_id = " + str(id)
    cursor.execute(query)
    product = cursor.fetchone()
    return product


if __name__ == '__main__':
    app.secret_key = Config.SECRET_KEY
    app.run(debug=True)
