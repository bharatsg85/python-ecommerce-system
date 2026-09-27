from product import Product
from user import User
from cart import Cart
from order import Order


def show_menu():
    print("\n------- E-Commerce System -------")
    print("1. Display Products")
    print("2. Search Products")
    print("3. Add Product")
    print("4. Update Product Stock")
    print("5. Delete Product")
    print("6. Add Product to Cart")
    print("7. View Cart")
    print("8. Remove Product from Cart")
    print("9. Place Order")
    print("10. Order History")
    print("11. Order Details")
    print("12. Cancel Order")
    print("13. Exit")
    print("--------------------------------")


def display_products():
    products = Product.get_all_products()

    if not products:
        print("No products available.")
        return

    for product in products:
        print(
            f"ID: {product[0]}, "
            f"Name: {product[1]}, "
            f"Price: ${product[2]:.2f}, "
            f"Stock: {product[3]}, "
            f"Category: {product[4]}"
        )


def search_products():
    search_name = input("Enter the product name to search: ")

    products = Product.search_product(search_name)

    if not products:
        print("No products found.")
        return

    for product in products:
        print(
            f"ID: {product[0]}, "
            f"Name: {product[1]}, "
            f"Price: ${product[2]:.2f}, "
            f"Stock: {product[3]}, "
            f"Category: {product[4]}"
        )


def main():

    # ---------------- LOGIN / REGISTER ----------------

    while True:
        print("\n------- Welcome -------")
        print("1. Register")
        print("2. Login")
        print("3. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            name = input("Enter your name: ")
            email = input("Enter your email: ")
            password = input("Enter your password: ")

            user = User(name, email, password)
            user.register_user()

        elif choice == "2":
            email = input("Enter your email: ")
            password = input("Enter your password: ")

            logged_user = User.login_user(email, password)

            if logged_user:
                user_id = logged_user[0]
                print("Login successful!")
                break

        elif choice == "3":
            print("Exiting...")
            return

        else:
            print("Invalid choice.")

    # ---------------- USER SESSION ----------------

    cart = Cart(user_id)
    order = Order(user_id)

    # ---------------- MAIN MENU ----------------

    while True:

        show_menu()

        choice = input("Enter your choice: ")

        # DISPLAY PRODUCTS
        if choice == "1":
            display_products()

        # SEARCH PRODUCTS
        elif choice == "2":
            search_products()

        # ADD PRODUCT
        elif choice == "3":

            name = input("Enter the product name: ")
            price = float(input("Enter the product price: "))
            stock = int(input("Enter the product stock: "))
            category = input("Enter the product category: ")

            product = Product(name, price)
            product.add_product(stock, category)

        # UPDATE STOCK
        elif choice == "4":

            product_id = int(
                input("Enter the product ID to update: ")
            )

            new_stock = int(
                input("Enter the new stock value: ")
            )

            Product.update_product(product_id, new_stock)

        # DELETE PRODUCT
        elif choice == "5":

            product_id = int(
                input("ID of product to remove: ")
            )

            Product.delete_product(product_id)

        # ADD TO CART
        elif choice == "6":

            product_id = int(
                input("Enter product ID: ")
            )

            quantity = int(
                input("Enter quantity: ")
            )

            cart.add_to_cart(product_id, quantity)

        # VIEW CART
        elif choice == "7":

            cart.view_cart()

            total = cart.calculate_total()

            print(f"Cart Total: ${total:.2f}")

        # REMOVE FROM CART
        elif choice == "8":

            product_id = int(
                input("Enter product ID to remove: ")
            )

            cart.remove_from_cart(product_id)

        # PLACE ORDER
        elif choice == "9":

            cart.view_cart()

            total = cart.calculate_total()

            if total > 0:
                print(f"Order Total: ${total:.2f}")

                confirm = input(
                    "Place this order? (yes/no): "
                )

                if confirm.lower() == "yes":
                    order.place_order()
                else:
                    print("Order cancelled. Going back.")

        # ORDER HISTORY
        elif choice == "10":

            order.get_order_history()

        # ORDER DETAILS
        elif choice == "11":

            order_id = int(
                input("Enter order ID: ")
            )

            order.get_order_details(order_id)

        # CANCEL ORDER
        elif choice == "12":

            order_id = int(
                input("Enter order ID to cancel: ")
            )

            order.cancel_order(order_id)

        # EXIT
        elif choice == "13":

            print("Exiting...")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main() 