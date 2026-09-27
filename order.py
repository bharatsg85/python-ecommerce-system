import mysql.connector
from database import get_connection


class Order:

    def __init__(self, user_id):
        self.user_id = user_id

    # PLACE ORDER
    def place_order(self):
        store = get_connection()
        cursor = store.cursor()

        try:
            # Get cart items
            cursor.execute(
                """
                SELECT product_id, quantity
                FROM cart
                WHERE user_id = %s
                """,
                (self.user_id,)
            )

            cart_items = cursor.fetchall()

            if not cart_items:
                print("Your cart is empty.")
                return

            total_amount = 0

            # Calculate total
            for item in cart_items:
                product_id = item[0]
                quantity = item[1]

                cursor.execute(
                    """
                    SELECT price, stock
                    FROM products
                    WHERE id = %s
                    """,
                    (product_id,)
                )

                product = cursor.fetchone()

                if product is None:
                    print("Product not found.")
                    return

                price = product[0]
                stock = product[1]

                if quantity > stock:
                    print(
                        f"Not enough stock for product ID {product_id}."
                    )
                    return

                total_amount += price * quantity

            # Create order
            cursor.execute(
                """
                INSERT INTO orders (user_id, total_amount)
                VALUES (%s, %s)
                """,
                (self.user_id, total_amount)
            )

            order_id = cursor.lastrowid

            # Add order items and update stock
            for item in cart_items:
                product_id = item[0]
                quantity = item[1]

                cursor.execute(
                    """
                    SELECT price
                    FROM products
                    WHERE id = %s
                    """,
                    (product_id,)
                )

                price = cursor.fetchone()[0]

                cursor.execute(
                    """
                    INSERT INTO order_items
                    (order_id, product_id, quantity, price)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (order_id, product_id, quantity, price)
                )

                cursor.execute(
                    """
                    UPDATE products
                    SET stock = stock - %s
                    WHERE id = %s
                    """,
                    (quantity, product_id)
                )

            # Empty cart
            cursor.execute(
                """
                DELETE FROM cart
                WHERE user_id = %s
                """,
                (self.user_id,)
            )

            store.commit()

            print("\nOrder placed successfully!")
            print(f"Order ID: {order_id}")
            print(f"Total amount: ${total_amount:.2f}")

        except mysql.connector.Error as e:
            store.rollback()
            print(f"Error placing order: {e}")

        finally:
            cursor.close()
            store.close()

    # VIEW ORDER HISTORY
    def get_order_history(self):
        store = get_connection()
        cursor = store.cursor()

        try:
            cursor.execute(
                """
                SELECT id, total_amount, status, order_date
                FROM orders
                WHERE user_id = %s
                ORDER BY order_date DESC
                """,
                (self.user_id,)
            )

            orders = cursor.fetchall()

            if not orders:
                print("No orders found.")
                return

            print("\n---------- ORDER HISTORY ----------")

            for order in orders:
                print(
                    f"Order ID: {order[0]}, "
                    f"Total: ${order[1]:.2f}, "
                    f"Status: {order[2]}, "
                    f"Date: {order[3]}"
                )

            print("-----------------------------------")

        except mysql.connector.Error as e:
            print(f"Error getting order history: {e}")

        finally:
            cursor.close()
            store.close()

    # VIEW SINGLE ORDER
    def get_order_details(self, order_id):
        store = get_connection()
        cursor = store.cursor()

        try:
            cursor.execute(
                """
                SELECT
                    order_items.product_id,
                    products.name,
                    order_items.quantity,
                    order_items.price,
                    order_items.quantity * order_items.price
                FROM order_items
                JOIN products
                    ON order_items.product_id = products.id
                JOIN orders
                    ON order_items.order_id = orders.id
                WHERE order_items.order_id = %s
                AND orders.user_id = %s
                """,
                (order_id, self.user_id)
            )

            items = cursor.fetchall()

            if not items:
                print("Order not found.")
                return

            print("\n---------- ORDER DETAILS ----------")

            for item in items:
                print(
                    f"Product ID: {item[0]}, "
                    f"Name: {item[1]}, "
                    f"Quantity: {item[2]}, "
                    f"Price: ${item[3]:.2f}, "
                    f"Total: ${item[4]:.2f}"
                )

            print("-----------------------------------")

        except mysql.connector.Error as e:
            print(f"Error getting order details: {e}")

        finally:
            cursor.close()
            store.close()

    # CANCEL ORDER
    def cancel_order(self, order_id):
        store = get_connection()
        cursor = store.cursor()

        try:
            cursor.execute(
                """
                SELECT status
                FROM orders
                WHERE id = %s AND user_id = %s
                """,
                (order_id, self.user_id)
            )

            order = cursor.fetchone()

            if order is None:
                print("Order not found.")
                return

            if order[0] == "Cancelled":
                print("Order is already cancelled.")
                return

            choice = input(
                "Are you sure you want to cancel this order? (yes/no): "
            )

            if choice.lower() != "yes":
                print("Order not cancelled.")
                return

            # Get ordered items
            cursor.execute(
                """
                SELECT product_id, quantity
                FROM order_items
                WHERE order_id = %s
                """,
                (order_id,)
            )

            items = cursor.fetchall()

            # Restore stock
            for item in items:
                cursor.execute(
                    """
                    UPDATE products
                    SET stock = stock + %s
                    WHERE id = %s
                    """,
                    (item[1], item[0])
                )

            # Update order status
            cursor.execute(
                """
                UPDATE orders
                SET status = 'Cancelled'
                WHERE id = %s
                """,
                (order_id,)
            )

            store.commit()

            print("Order cancelled successfully.")

        except mysql.connector.Error as e:
            store.rollback()
            print(f"Error cancelling order: {e}")

        finally:
            cursor.close()
            store.close()