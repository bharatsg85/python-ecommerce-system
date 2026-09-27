import mysql.connector
from database import get_connection


class Product:
    def __init__(self, name, price):
        self.name = name
        self.price = price

    def add_product(self, stock, category):
        store = get_connection()
        cursor = store.cursor()
        try:
            cursor.execute("INSERT INTO products (name, price, stock, category) VALUES (%s, %s, %s, %s)", (self.name, self.price, stock, category))
            store.commit()
        except Exception as e:
            print(f"An error occurred while adding the product: {e}")
            store.rollback()

        except Exception as e:
            print(f"An error occurred while adding the product: {e}")
            store.rollback()
        finally:
            cursor.close()
            store.close()


    @classmethod
    def update_product(cls, product_id, new_stock):
        
        store = get_connection()
        cursor = store.cursor()
        cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
        cursor.fetchone()
        
        cursor.execute("UPDATE products SET stock = %s WHERE id = %s", (new_stock, product_id))
        store.commit()
        
        cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
        
        updated_product = cursor.fetchone()
        print("Product updated successsfully!")

        if updated_product:
            print(f"Updated product: ID: {updated_product[0]}, Name: {updated_product[1]}, Price: ${updated_product[2]:.2f}, Stock: {updated_product[3]}, Category: {updated_product[4]}")
        else:
            print("Product not found or not updated")   
        cursor.close()
        store.close()     

    @classmethod
    def get_all_products(cls):
        store = get_connection()
        cursor = store.cursor()
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()
        cursor.close()
        store.close()
        return products

    @classmethod
    def delete_product(cls, product_id):
        store = get_connection()
        cursor = store.cursor()

        try:
            cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
            product = cursor.fetchone()

            if product is None:
                print("Product not found ")
                return

            print(
                f"ID: {product[0]}, "
                f"Name: {product[1]}, "
                f"Price: ${product[2]:.2f}, "
                f"Stock: {product[3]}, "
                f"Category: {product[4]}"
            )

            choice = input("Are you sure you want to delete it? (yes/no): ")
            if choice.lower() == "yes":
                cursor.execute(
                    "DELETE FROM products WHERE id = %s",
                    (product_id,)
                )

                store.commit()
                print("Product deleted successfully.")

            else:
                store.rollback()
                print("Not deleting, going back.")

        except mysql.connector.Error as e:
            store.rollback()
            print(f"Error deleting product: {e}")

        finally:
            cursor.close()
            store.close()



    @classmethod
    def search_product(cls, search_name):
        store = get_connection()
        cursor = store.cursor()

        cursor.execute(
            "SELECT * FROM products WHERE name LIKE %s",
            (f"%{search_name}%",)
        )

        products = cursor.fetchall()

        cursor.close()
        store.close()

        return products



