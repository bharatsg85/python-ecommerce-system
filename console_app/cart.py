import mysql.connector
from database import get_connection


class Cart:

    def __init__(self, user_id):
        self.user_id = user_id

    def add_to_cart(self, product_id, quantity):
        store = get_connection()
        cursor = store.cursor()

        try:
            cursor.execute(
                "SELECT * FROM products WHERE id = %s",
                (product_id,)
            )

            product = cursor.fetchone()

            if product is None:
                print("Product not found.")
                return

            if quantity <= 0:
                print("Quantity must be greater than 0.")
                return

            if quantity > product[3]:
                print(f"Only {product[3]} items available.")
                return

            cursor.execute(
                """
                SELECT * FROM cart
                WHERE user_id = %s AND product_id = %s
                """,
                (self.user_id, product_id)
            )

            existing_product = cursor.fetchone()

            if existing_product:
                new_quantity = existing_product[3] + quantity

                if new_quantity > product[3]:
                    print(f"Only {product[3]} items available.")
                    return

                cursor.execute(
                    """
                    UPDATE cart
                    SET quantity = %s
                    WHERE user_id = %s AND product_id = %s
                    """,
                    (new_quantity, self.user_id, product_id)
                )

            else:
                cursor.execute(
                    """
                    INSERT INTO cart (user_id, product_id, quantity)
                    VALUES (%s, %s, %s)
                    """,
                    (self.user_id, product_id, quantity)
                )

            store.commit()
            print("Product added to cart.")

        except mysql.connector.Error as e:
            store.rollback()
            print(f"Error adding to cart: {e}")

        finally:
            cursor.close()
            store.close()

    def view_cart(self):
        store = get_connection()
        cursor = store.cursor()

        try:
            cursor.execute(
                """
                SELECT
                    cart.id,
                    products.id,
                    products.name,
                    products.price,
                    cart.quantity,
                    products.price * cart.quantity
                FROM cart
                JOIN products
                    ON cart.product_id = products.id
                WHERE cart.user_id = %s
                """,
                (self.user_id,)
            )

            cart_items = cursor.fetchall()

            if not cart_items:
                print("Your cart is empty.")
                return

            print("\n---------- YOUR CART ----------")

            for item in cart_items:
                print(
                    f"Cart ID: {item[0]}, "
                    f"Product ID: {item[1]}, "
                    f"Name: {item[2]}, "
                    f"Price: ${item[3]:.2f}, "
                    f"Quantity: {item[4]}, "
                    f"Total: ${item[5]:.2f}"
                )

            print("-------------------------------")

        except mysql.connector.Error as e:
            print(f"Error viewing cart: {e}")

        finally:
            cursor.close()
            store.close()

    def remove_from_cart(self, product_id):
        store = get_connection()
        cursor = store.cursor()

        try:
            cursor.execute(
                """
                SELECT cart.id, products.name, cart.quantity
                FROM cart
                JOIN products
                    ON cart.product_id = products.id
                WHERE cart.user_id = %s
                AND cart.product_id = %s
                """,
                (self.user_id, product_id)
            )

            item = cursor.fetchone()

            if item is None:
                print("Product is not in your cart.")
                return

            print(
                f"Product: {item[1]}, "
                f"Quantity: {item[2]}"
            )

            choice = input(
                "Are you sure you want to remove this product? (yes/no): "
            )

            if choice.lower() == "yes":
                cursor.execute(
                    """
                    DELETE FROM cart
                    WHERE user_id = %s
                    AND product_id = %s
                    """,
                    (self.user_id, product_id)
                )

                store.commit()
                print("Product removed from cart.")

            else:
                store.rollback()
                print("Not removing, going back.")

        except mysql.connector.Error as e:
            store.rollback()
            print(f"Error removing from cart: {e}")

        finally:
            cursor.close()
            store.close()

    def calculate_total(self):
        store = get_connection()
        cursor = store.cursor()

        try:
            cursor.execute(
                """
                SELECT SUM(products.price * cart.quantity)
                FROM cart
                JOIN products
                    ON cart.product_id = products.id
                WHERE cart.user_id = %s
                """,
                (self.user_id,)
            )

            result = cursor.fetchone()

            total = result[0]

            if total is None:
                total = 0

            return total

        except mysql.connector.Error as e:
            print(f"Error calculating total: {e}")
            return 0

        finally:
            cursor.close()
            store.close()