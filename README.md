# Python E-Commerce System

## Overview
A console-based e-commerce application built with Python and MySQL.

The project allows users to register and log in, browse and search products, manage a shopping cart, place orders, view order history, and cancel orders.

The application uses object-oriented programming and a MySQL database to manage users, products, carts, and orders.

## Features

* User registration and login
* Product management
* Product search
* Shopping cart management
* Add and remove products from cart
* Automatic cart total calculation
* Order placement
* Order history
* Order cancellation
* Stock management
* MySQL database integration
* Object-oriented Python architecture



## Technologies Used

* **Python 3**
* **MySQL**
* **mysql-connector-python**
* **Object-Oriented Programming (OOP)**
* **Git & GitHub**


## Project Structure

```text
python-ecommerce-system/
│
├── main.py          # Main application and menu
├── database.py      # MySQL database connection
├── product.py       # Product management
├── user.py          # User registration and login
├── cart.py          # Shopping cart operations
├── order.py         # Order management
├── ecommerce.db     # Local database file
├── requirements.txt # Python dependencies
├── .gitignore       # Files excluded from Git
└── README.md        # Project documentation
```


## Database

The project uses **MySQL** as the database management system.

The database stores and manages:

* User accounts
* Product information
* Shopping cart data
* Orders
* Order items

The main tables are:

```text
users
products
cart
orders
order_items
```

Foreign keys are used to maintain relationships between users, products, carts, and orders.


## Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/bharatsg85/python-ecommerce-system.git
cd python-ecommerce-system
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

**Windows:**

```bash
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure MySQL

Create a MySQL database named `ecommerce` and create the required tables:

* `users`
* `products`
* `cart`
* `orders`
* `order_items`

Update the database connection settings in `database.py` with your MySQL credentials.

### 6. Run the application

```bash
python main.py
```

## How to Run

After completing the setup, start the application with:

```bash
python main.py
```

The application will display a console menu where you can:

1. Register or log in
2. Browse and search products
3. Manage your shopping cart
4. Place and cancel orders
5. View order history
6. Manage products

## Python Concepts Demonstrated

This project demonstrates practical use of:

* Object-Oriented Programming (OOP)
* Classes and objects
* Constructors
* Class methods
* Encapsulation
* Modular programming
* Exception handling
* Functions and control flow
* SQL queries from Python
* Database connectivity
* CRUD operations



## Future Improvements


* Add a graphical or web-based user interface
* Implement secure password hashing
* Add automated tests
* Improve input validation and error handling
* Add product categories and filtering
* Add an admin dashboard
* Add payment gateway integration
* Deploy the application as a web service



**Bharat Gurjar**

This project was built as a practical project to strengthen Python, Object-Oriented Programming, MySQL, and Git/GitHub skills.


## Author
