from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"


def get_db_connection():
    conn = sqlite3.connect("restaurant.db")
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def home():
    return "QR Restaurant Ordering System"


@app.route("/table/<int:table_id>")
def menu(table_id):

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

    conn.close()

    return render_template(
        "dashboard.html",
        order_data=order_data
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

if __name__ == "__main__":
    app.run(debug=True)