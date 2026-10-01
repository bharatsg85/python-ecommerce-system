from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, render

from .db import execute, fetch_all, fetch_one


def current_user(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return fetch_one("SELECT id, name, email FROM users WHERE id = %s", (user_id,))


def home(request):
    featured = fetch_all(
        "SELECT id, name, price, stock, category FROM products "
        "ORDER BY id DESC LIMIT 8"
    )
    return render(request, "home.html", {"products": featured, "user": current_user(request)})


def products(request):
    search = request.GET.get("q", "").strip()
    if search:
        rows = fetch_all(
            "SELECT id, name, price, stock, category FROM products "
            "WHERE name LIKE %s OR category LIKE %s ORDER BY id DESC",
            (f"%{search}%", f"%{search}%"),
        )
    else:
        rows = fetch_all(
            "SELECT id, name, price, stock, category FROM products ORDER BY id DESC"
        )
    return render(request, "products.html", {
        "products": rows,
        "search": search,
        "user": current_user(request),
    })


def product_detail(request, product_id):
    product = fetch_one(
        "SELECT id, name, price, stock, category FROM products WHERE id = %s",
        (product_id,),
    )
    if not product:
        return render(request, "404.html", status=404)
    return render(request, "product_detail.html", {
        "product": product,
        "user": current_user(request),
    })


def login_view(request):
    if request.session.get("user_id"):
        return redirect("products")

    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        user = fetch_one("SELECT * FROM users WHERE email = %s", (email,))
        if user and check_password(password, user["password"]):
            request.session["user_id"] = user["id"]
            request.session["user_name"] = user["name"]
            messages.success(request, f"Welcome, {user['name']}!")
            return redirect("products")

        # Supports an old plaintext-password database during migration.
        if user and user["password"] == password:
            new_hash = make_password(password)
            execute("UPDATE users SET password = %s WHERE id = %s", (new_hash, user["id"]))
            request.session["user_id"] = user["id"]
            request.session["user_name"] = user["name"]
            messages.success(request, f"Welcome, {user['name']}!")
            return redirect("products")

        messages.error(request, "Invalid email or password.")

    return render(request, "login.html")


def register_view(request):
    if request.session.get("user_id"):
        return redirect("products")

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        if not name or not email or not password:
            messages.error(request, "All fields are required.")
            return render(request, "register.html")

        existing = fetch_one("SELECT id FROM users WHERE email = %s", (email,))
        if existing:
            messages.error(request, "An account with that email already exists.")
            return render(request, "register.html")

        execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (name, email, make_password(password)),
        )
        messages.success(request, "Account created. You can now log in.")
        return redirect("login")

    return render(request, "register.html")


def logout_view(request):
    request.session.flush()
    messages.info(request, "You have been logged out.")
    return redirect("home")


def require_login(request):
    if not request.session.get("user_id"):
        messages.info(request, "Please log in first.")
        return redirect("login")
    return None


def cart_view(request):
    guard = require_login(request)
    if guard:
        return guard

    user_id = request.session["user_id"]
    cart = fetch_all(
        """SELECT c.product_id, p.name, p.price, p.stock, c.quantity,
                  (p.price * c.quantity) AS subtotal
           FROM cart c
           JOIN products p ON p.id = c.product_id
           WHERE c.user_id = %s
           ORDER BY c.id DESC""",
        (user_id,),
    )
    total = sum((Decimal(str(item["subtotal"])) for item in cart), Decimal("0"))
    return render(request, "cart.html", {"cart": cart, "total": total})


def add_to_cart(request, product_id):
    guard = require_login(request)
    if guard:
        return guard

    if request.method != "POST":
        return HttpResponseBadRequest("POST required.")

    user_id = request.session["user_id"]
    product = fetch_one(
        "SELECT id, name, price, stock FROM products WHERE id = %s",
        (product_id,),
    )

    if not product:
        messages.error(request, "Product not found.")
        return redirect("products")

    if product["stock"] <= 0:
        messages.error(request, "This product is out of stock.")
        return redirect("products")

    existing = fetch_one(
        "SELECT quantity FROM cart WHERE user_id = %s AND product_id = %s",
        (user_id, product_id),
    )

    if existing:
        new_qty = existing["quantity"] + 1
        if new_qty > product["stock"]:
            messages.error(request, "You cannot add more than available stock.")
            return redirect("cart")
        execute(
            "UPDATE cart SET quantity = %s WHERE user_id = %s AND product_id = %s",
            (new_qty, user_id, product_id),
        )
    else:
        execute(
            "INSERT INTO cart (user_id, product_id, quantity) VALUES (%s, %s, 1)",
            (user_id, product_id),
        )

    messages.success(request, "Product added to cart.")
    return redirect(request.POST.get("next") or "products")


def update_cart(request, product_id):
    guard = require_login(request)
    if guard:
        return guard

    if request.method != "POST":
        return HttpResponseBadRequest("POST required.")

    try:
        quantity = int(request.POST.get("quantity", "1"))
    except ValueError:
        quantity = 1

    user_id = request.session["user_id"]
    product = fetch_one(
        "SELECT stock FROM products WHERE id = %s", (product_id,)
    )

    if not product:
        messages.error(request, "Product not found.")
        return redirect("cart")

    if quantity <= 0:
        execute(
            "DELETE FROM cart WHERE user_id = %s AND product_id = %s",
            (user_id, product_id),
        )
    elif quantity <= product["stock"]:
        execute(
            "UPDATE cart SET quantity = %s WHERE user_id = %s AND product_id = %s",
            (quantity, user_id, product_id),
        )
    else:
        messages.error(request, f"Only {product['stock']} item(s) are available.")

    return redirect("cart")


def remove_from_cart(request, product_id):
    guard = require_login(request)
    if guard:
        return guard

    if request.method != "POST":
        return HttpResponseBadRequest("POST required.")

    execute(
        "DELETE FROM cart WHERE user_id = %s AND product_id = %s",
        (request.session["user_id"], product_id),
    )
    messages.success(request, "Item removed from cart.")
    return redirect("cart")


def checkout(request):
    guard = require_login(request)
    if guard:
        return guard

    if request.method != "POST":
        return redirect("cart")

    user_id = request.session["user_id"]
    conn_cart = fetch_all(
        """SELECT c.product_id, c.quantity, p.name, p.price, p.stock
           FROM cart c JOIN products p ON p.id = c.product_id
           WHERE c.user_id = %s""",
        (user_id,),
    )

    if not conn_cart:
        messages.error(request, "Your cart is empty.")
        return redirect("cart")

    for item in conn_cart:
        if item["quantity"] > item["stock"]:
            messages.error(request, f"Not enough stock for {item['name']}.")
            return redirect("cart")

    total = sum(
        (Decimal(str(item["price"])) * item["quantity"] for item in conn_cart),
        Decimal("0"),
    )

    # Use a single connector transaction for order creation + stock updates.
    import os
    import mysql.connector
    from dotenv import load_dotenv
    load_dotenv()

    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        database=os.getenv("DB_NAME", "ecommerce"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
    )
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO orders (user_id, total_amount, status) VALUES (%s, %s, %s)",
            (user_id, total, "Placed"),
        )
        order_id = cursor.lastrowid

        for item in conn_cart:
            cursor.execute(
                """INSERT INTO order_items
                   (order_id, product_id, quantity, price)
                   VALUES (%s, %s, %s, %s)""",
                (order_id, item["product_id"], item["quantity"], item["price"]),
            )
            cursor.execute(
                "UPDATE products SET stock = stock - %s WHERE id = %s",
                (item["quantity"], item["product_id"]),
            )

        cursor.execute("DELETE FROM cart WHERE user_id = %s", (user_id,))
        conn.commit()

    except Exception:
        conn.rollback()
        messages.error(request, "Checkout failed. No changes were made.")
        return redirect("cart")
    finally:
        cursor.close()
        conn.close()

    messages.success(request, f"Order #{order_id} placed successfully.")
    return redirect("order_detail", order_id=order_id)


def orders(request):
    guard = require_login(request)
    if guard:
        return guard

    rows = fetch_all(
        """SELECT id, total_amount, status, order_date
           FROM orders WHERE user_id = %s
           ORDER BY order_date DESC""",
        (request.session["user_id"],),
    )
    return render(request, "orders.html", {"orders": rows})


def order_detail(request, order_id):
    guard = require_login(request)
    if guard:
        return guard

    user_id = request.session["user_id"]
    order = fetch_one(
        """SELECT id, total_amount, status, order_date
           FROM orders WHERE id = %s AND user_id = %s""",
        (order_id, user_id),
    )
    if not order:
        return render(request, "404.html", status=404)

    items = fetch_all(
        """SELECT oi.quantity, oi.price, p.name,
                  (oi.quantity * oi.price) AS subtotal
           FROM order_items oi
           JOIN products p ON p.id = oi.product_id
           WHERE oi.order_id = %s""",
        (order_id,),
    )
    return render(request, "order_detail.html", {"order": order, "items": items})


def cancel_order(request, order_id):
    guard = require_login(request)
    if guard:
        return guard

    if request.method != "POST":
        return HttpResponseBadRequest("POST required.")

    user_id = request.session["user_id"]
    order = fetch_one(
        "SELECT id, status FROM orders WHERE id = %s AND user_id = %s",
        (order_id, user_id),
    )

    if not order:
        messages.error(request, "Order not found.")
        return redirect("orders")

    if order["status"] == "Cancelled":
        messages.info(request, "Order is already cancelled.")
        return redirect("order_detail", order_id=order_id)

    items = fetch_all(
        "SELECT product_id, quantity FROM order_items WHERE order_id = %s",
        (order_id,),
    )

    import os
    import mysql.connector
    from dotenv import load_dotenv
    load_dotenv()

    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        database=os.getenv("DB_NAME", "ecommerce"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
    )
    cursor = conn.cursor()

    try:
        for item in items:
            cursor.execute(
                "UPDATE products SET stock = stock + %s WHERE id = %s",
                (item["quantity"], item["product_id"]),
            )
        cursor.execute(
            "UPDATE orders SET status = 'Cancelled' WHERE id = %s",
            (order_id,),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        messages.error(request, "Could not cancel the order.")
        return redirect("order_detail", order_id=order_id)
    finally:
        cursor.close()
        conn.close()

    messages.success(request, "Order cancelled and stock restored.")
    return redirect("order_detail", order_id=order_id)
