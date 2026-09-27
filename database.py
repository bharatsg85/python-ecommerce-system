import mysql.connector

def get_connection():
    try:
        store = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",
            database="ecommerce"
        )
        return store
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

