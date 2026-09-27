import mysql.connector
from database import get_connection


class User:

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

    def register_user(self):
        store = get_connection()
        cursor = store.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO users (name, email, password)
                VALUES (%s, %s, %s)
                """,
                (self.name, self.email, self.password)
            )

            store.commit()
            print("User registered successfully.")

        except mysql.connector.Error as e:
            store.rollback()
            print(f"Error registering user: {e}")

        finally:
            cursor.close()
            store.close()

    
    @classmethod
    def login_user(cls, email, password):
        store = get_connection()
        cursor = store.cursor()

        try:
            cursor.execute(
                """
                SELECT * FROM users
                WHERE email = %s AND password = %s
                """,
                (email, password)
            )

            user = cursor.fetchone()

            if user:
                print(f"Welcome, {user[1]}!")
                return user
            else:
                print("Invalid email or password.")
                return None

        except mysql.connector.Error as e:
            print(f"Error logging in: {e}")
            return None

        finally:
            cursor.close()
            store.close()

    @classmethod
    def get_user(cls, user_id):
        store = get_connection()
        cursor = store.cursor()

        try:
            cursor.execute(
                "SELECT * FROM users WHERE id = %s",
                (user_id,)
            )

            user = cursor.fetchone()

            if user:
                return user
            else:
                print("User not found.")
                return None

        except mysql.connector.Error as e:
            print(f"Error getting user: {e}")
            return None

        finally:
            cursor.close()
            store.close()

    @classmethod
    def get_all_users(cls):
        store = get_connection()
        cursor = store.cursor()

        try:
            cursor.execute("SELECT * FROM users")

            users = cursor.fetchall()

            return users

        except mysql.connector.Error as e:
            print(f"Error getting users: {e}")
            return []

        finally:
            cursor.close()
            store.close()

    @classmethod
    def update_user(cls, user_id, new_name, new_email):
        store = get_connection()
        cursor = store.cursor()

        try:
            cursor.execute(
                """
                UPDATE users
                SET name = %s, email = %s
                WHERE id = %s
                """,
                (new_name, new_email, user_id)
            )

            if cursor.rowcount == 0:
                print("User not found.")
            else:
                store.commit()
                print("User updated successfully.")

        except mysql.connector.Error as e:
            store.rollback()
            print(f"Error updating user: {e}")

        finally:
            cursor.close()
            store.close()

    @classmethod
    def delete_user(cls, user_id):
        store = get_connection()
        cursor = store.cursor()

        try:
            # Find user first
            cursor.execute(
                "SELECT * FROM users WHERE id = %s",
                (user_id,)
            )

            user = cursor.fetchone()

            if user is None:
                print("User not found.")
                return

            # Show selected user
            print(
                f"ID: {user[0]}, "
                f"Name: {user[1]}, "
                f"Email: {user[2]}"
            )

            choice = input(
                "Are you sure you want to delete this user? (yes/no): "
            )

            if choice.lower() == "yes":
                cursor.execute(
                    "DELETE FROM users WHERE id = %s",
                    (user_id,)
                )

                store.commit()
                print("User deleted successfully.")

            else:
                store.rollback()
                print("Not deleting, going back.")

        except mysql.connector.Error as e:
            store.rollback()
            print(f"Error deleting user: {e}")

        finally:
            cursor.close()
            store.close()