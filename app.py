from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "farmermarket123"
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- DATABASE ----------------

def init_db():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    # Products Table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        category TEXT,
        price REAL,
        quantity INTEGER,
        image TEXT
    )
    ''')

    # Users Table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT
    )
    ''')

    conn.commit()
    conn.close()

init_db()

# ---------------- ROUTES ----------------
@app.route('/')
def home():

    username = session.get('user_name', 'Farmer')

    search = request.args.get('search', '')

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    if search:

        cur.execute("""
            SELECT id, name, category, price, quantity, image
            FROM products
            WHERE name LIKE ?
            ORDER BY id DESC
        """, ('%' + search + '%',))

    else:

        cur.execute("""
            SELECT id, name, category, price, quantity, image
            FROM products
            ORDER BY id DESC
        """)

    products = cur.fetchall()

    conn.close()

    return render_template(
        'index.html',
        username=username,
        products=products,
        search=search
    )

@app.route('/my_ads')
def my_ads():

    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM products WHERE user_id=?",
        (user_id,)
    )

    products = cur.fetchall()

    conn.close()

    return render_template('my_ads.html', products=products)

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():

    if request.method == 'POST':

        name = request.form['name']
        category = request.form['category']
        price = request.form['price']
        quantity = request.form['quantity']

        user_id = session['user_id']

        image = request.files['image']

        filename = ""

        if image and image.filename != "":
            filename = secure_filename(image.filename)

            image.save(
                os.path.join(
                    app.config['UPLOAD_FOLDER'],
                    filename
                )
            )

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO products
            (name, category, price, quantity, image, user_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (name, category, price, quantity, filename, user_id)
        )

        conn.commit()
        conn.close()

        return redirect('/my_ads')

    return render_template('add_product.html')
@app.route('/weather')
def weather():
    return render_template('weather.html')

@app.route('/notifications')
def notifications():
    return render_template('notifications.html')

@app.route('/inbox')
def inbox():
    return render_template('inbox.html')

@app.route('/category')
def category():
    return render_template('category.html')
@app.route('/delete_product/<int:id>')
def delete_product(id):

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute("DELETE FROM products WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect('/my_ads')
@app.route('/edit_product/<int:id>', methods=['GET', 'POST'])
def edit_product(id):

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    if request.method == 'POST':

        name = request.form['name']
        category = request.form['category']
        price = request.form['price']
        quantity = request.form['quantity']

        cur.execute("""
            UPDATE products
            SET name=?, category=?, price=?, quantity=?
            WHERE id=?
        """, (name, category, price, quantity, id))

        conn.commit()
        conn.close()

        return redirect('/my_ads')

    cur.execute("SELECT * FROM products WHERE id=?", (id,))
    product = cur.fetchone()

    conn.close()

    return render_template('edit_product.html', product=product)
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, password)
        )

        conn.commit()
        conn.close()

        return redirect('/')

    return render_template('register.html')
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        )

        user = cur.fetchone()

        conn.close()

        if user:

            session['user_id'] = user[0]      # User ID
            session['user_name'] = user[1]    # Name

            return redirect('/')

        else:
            return "Invalid Email or Password"

    return render_template('login.html')
@app.route('/market_watch')
def market_watch():

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM products
        ORDER BY price DESC
        LIMIT 10
    """)

    products = cur.fetchall()

    conn.close()

    return render_template(
        'market_watch.html',
        products=products
    )
@app.route('/commodities')
def commodities():

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute("""
        SELECT category, name, price
        FROM products
        ORDER BY category
    """)

    products = cur.fetchall()

    conn.close()

    return render_template(
        'commodities.html',
        products=products
    )
@app.route('/market_update')
def market_update():

    return render_template('market_update.html')
@app.route('/fieldforce')
def fieldforce():

    return render_template('fieldforce.html')
@app.route('/profile')
def profile():

    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute(
        """
       SELECT name, email, address, phone
        FROM users
        WHERE id=?
        """,
        (session['user_id'],)
    )

    user = cur.fetchone()

    conn.close()

    return render_template(
        'profile.html',
        user=user
    )
@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():

    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        address = request.form['address']
        phone = request.form['phone']

        cur.execute(
            """
            UPDATE users
            SET name=?, email=?, address=?, phone=?
            WHERE id=?
            """,
           (name, email, address, phone, session['user_id'])
        )

        conn.commit()
        conn.close()

        session['user_name'] = name

        return redirect('/profile')

    cur.execute(
        """
        SELECT name, email, address, phone
        FROM users
        WHERE id=?
        """,
        (session['user_id'],)
    )

    user = cur.fetchone()

    conn.close()

    return render_template(
        'edit_profile.html',
        user=user
    )
@app.route('/product/<int:id>')
def product_details(id):

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute("""
        SELECT
            p.id,
            p.name,
            p.category,
            p.price,
            p.quantity,
            p.image,
            u.name,
            u.address,
            u.phone
        FROM products p
        LEFT JOIN users u
        ON p.user_id = u.id
        WHERE p.id = ?
    """, (id,))

    product = cur.fetchone()

    conn.close()

    if not product:
        return "Product not found"

    return render_template(
        'product_details.html',
        product=product
    )
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)