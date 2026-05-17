from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"


def get_db_connection():
    conn = sqlite3.connect("restaurant.db")
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db_connection()

        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        conn.close()

        if user and check_password_hash(user["hash"], password):

            session["admin_id"] = user["id"]

            return redirect("/admin")

        return "Invalid username or password"

    session.pop("table_id", None)
    session.pop("cart", None)

    return render_template("login.html")

@app.route("/track_order", methods=["GET", "POST"])
def track_order():

    order = None

    if request.method == "POST":

        table_number = request.form.get("table_number")

        conn = get_db_connection()

        order = conn.execute("""
            SELECT *
            FROM orders
            WHERE table_number = ?
            ORDER BY created_at DESC
            LIMIT 1
        """, (table_number,)).fetchone()

        conn.close()

    return render_template(
        "track_order.html",
        order=order
    )

@app.route("/delete_order/<int:order_id>", methods=["POST"])
def delete_order(order_id):

    if "admin_id" not in session:
        return redirect("/login")

    conn = get_db_connection()

    conn.execute("""
        DELETE FROM order_items
        WHERE order_id = ?
    """, (order_id,))

    conn.execute("""
        DELETE FROM orders
        WHERE id = ?
    """, (order_id,))

    conn.commit()
    conn.close()

    return redirect("/admin")

@app.route("/clear_orders", methods=["POST"])
def clear_orders():

    if "admin_id" not in session:
        return redirect("/login")

    conn = get_db_connection()

    conn.execute("DELETE FROM order_items")

    conn.execute("DELETE FROM orders")

    conn.commit()
    conn.close()

    return redirect("/admin")

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

@app.route("/table/<int:table_id>")
def menu(table_id):

    if session.get("table_id") != table_id:
        session.pop("cart", None)

    session["table_id"] = table_id

    conn = get_db_connection()

    items = conn.execute(
        "SELECT * FROM menu_items"
    ).fetchall()

    conn.close()

    return render_template(
        "menu.html",
        items=items,
        table_id=table_id
    )

@app.route("/edit_menu", methods=["GET", "POST"])
def edit_menu():

    if "admin_id" not in session:
        return redirect("/login")

    conn = get_db_connection()

    if request.method == "POST":

        name = request.form.get("name")
        price = request.form.get("price")
        category = request.form.get("category")
        image = request.form.get("image")

        conn.execute("""
            INSERT INTO menu_items
            (name, price, category, image)
            VALUES (?, ?, ?, ?)
        """, (name, price, category, image))

        conn.commit()

    menu_items = conn.execute("""
        SELECT * FROM menu_items
    """).fetchall()

    conn.close()

    return render_template(
        "edit_menu.html",
        menu_items=menu_items
    )

@app.route("/delete_item/<int:item_id>", methods=["POST"])
def delete_item(item_id):

    if "admin_id" not in session:
        return redirect("/login")

    conn = get_db_connection()

    conn.execute("""
        DELETE FROM menu_items
        WHERE id = ?
    """, (item_id,))

    conn.commit()
    conn.close()

    return redirect("/admin")

@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():

    item_id = request.form.get("item_id")

    if "cart" not in session:
        session["cart"] = {}

    cart = session["cart"]

    if item_id in cart:
        cart[item_id] += 1
    else:
        cart[item_id] = 1

    session["cart"] = cart

    table_id = request.form.get("table_id")

    return redirect(url_for("menu", table_id=table_id))

@app.route("/cart")
def cart():

    if "table_id" not in session:
        return redirect("/")

    cart = session.get("cart", {})

    conn = get_db_connection()

    items = []
    total = 0

    for item_id, quantity in cart.items():

        item = conn.execute(
            "SELECT * FROM menu_items WHERE id = ?",
            (item_id,)
        ).fetchone()

        if item:

            subtotal = item["price"] * quantity
            total += subtotal

            items.append({
                "id": item["id"],
                "name": item["name"],
                "price": item["price"],
                "quantity": quantity,
                "subtotal": subtotal
            })

    conn.close()

    return render_template(
    "cart.html",
    items=items,
    total=total,
    table_id=session.get("table_id")
)

@app.route("/place_order", methods=["POST"])
def place_order():

    cart = session.get("cart", {})

    if not cart:
        return redirect("/cart")

    table_number = session.get("table_id")

    conn = get_db_connection()

    total_price = 0

    for item_id, quantity in cart.items():

        item = conn.execute(
            "SELECT * FROM menu_items WHERE id = ?",
            (item_id,)
        ).fetchone()

        if item:
            total_price += item["price"] * quantity

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO orders
        (table_number, total_price, status)
        VALUES (?, ?, ?)
        """,
        (table_number, total_price, "Pending")
    )

    order_id = cursor.lastrowid

    for item_id, quantity in cart.items():

        cursor.execute(
            """
            INSERT INTO order_items
            (order_id, menu_item_id, quantity)
            VALUES (?, ?, ?)
            """,
            (order_id, item_id, quantity)
        )

    conn.commit()
    conn.close()

    session.pop("cart", None)

    return redirect("/order_success")

@app.route("/order_success")
def order_success():
    return render_template("order_success.html")

@app.route("/admin")
def admin():

    if "admin_id" not in session:
        return redirect("/login")

    conn = get_db_connection()

    orders = conn.execute("""
        SELECT * FROM orders
        ORDER BY created_at DESC
    """).fetchall()

    order_data = []

    for order in orders:

        items = conn.execute("""
            SELECT
                menu_items.name,
                order_items.quantity
            FROM order_items
            JOIN menu_items
            ON order_items.menu_item_id = menu_items.id
            WHERE order_items.order_id = ?
        """, (order["id"],)).fetchall()

        order_data.append({
            "order": order,
            "items": items
        })

    menu_items = conn.execute("""
    SELECT * FROM menu_items
    """).fetchall()

    conn.close()

    return render_template(
    "dashboard.html",
    order_data=order_data,
    menu_items=menu_items
    )   
@app.route("/update_status/<int:order_id>", methods=["POST"])
def update_status(order_id):

    status = request.form.get("status")

    conn = get_db_connection()

    conn.execute("""
        UPDATE orders
        SET status = ?
        WHERE id = ?
    """, (status, order_id))

    conn.commit()
    conn.close()

    return redirect("/admin")

@app.route("/remove_from_cart/<int:item_id>", methods=["POST"])
def remove_from_cart(item_id):

    cart = session.get("cart", {})

    item_id = str(item_id)

    if item_id in cart:

        del cart[item_id]

        session["cart"] = cart

    return redirect("/cart")

@app.route("/increase_quantity/<int:item_id>", methods=["POST"])
def increase_quantity(item_id):

    cart = session.get("cart", {})

    item_id = str(item_id)

    if item_id in cart:
        cart[item_id] += 1

    session["cart"] = cart

    return redirect("/cart")

@app.route("/decrease_quantity/<int:item_id>", methods=["POST"])
def decrease_quantity(item_id):

    cart = session.get("cart", {})

    item_id = str(item_id)

    if item_id in cart:

        cart[item_id] -= 1

        if cart[item_id] <= 0:
            del cart[item_id]

    session["cart"] = cart

    return redirect("/cart")

if __name__ == "__main__":
    app.run(debug=True)