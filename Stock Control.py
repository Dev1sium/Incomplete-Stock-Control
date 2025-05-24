import sqlite3
import datetime
import random
from collections import defaultdict
##import matplotlib.pyplot as plt

class User:
    def __init__(self, user_id, username, password, role, external_id=None):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.role = role
        self.external_id = external_id

class Product:
    def __init__(self, product_id, product_name, description, stock_quantity=0, unit_price=0.0):
        self.product_id = product_id
        self.product_name = product_name
        self.description = description
        self.stock_quantity = stock_quantity
        self.unit_price = unit_price

class Invoice:
    def __init__(self, invoice_id, user_id, products=None, invoice_date=None):
        self.invoice_id = invoice_id
        self.user_id = user_id
        self.invoice_date = invoice_date or datetime.datetime.now()
        self.products = products or []

    def add_product(self, product, quantity):
        self.products.append({'product': product, 'quantity': quantity})

class StockControlSystem:
    def __init__(self, db_name='stock_control_system.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.users = {}
        self.products = {}
        self.invoices = defaultdict(list)
        self.current_user = None

    def create_tables(self):
        # Users table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS User (
                User_ID INTEGER PRIMARY KEY,
                Username TEXT UNIQUE NOT NULL,
                Password TEXT NOT NULL,
                Role TEXT NOT NULL,
                External_ID TEXT
            );
        ''')

        # Products table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Product (
                Product_ID INTEGER PRIMARY KEY,
                Product_Name TEXT NOT NULL,
                Description TEXT,
                Stock_Quantity INTEGER DEFAULT 0,
                Unit_Price REAL DEFAULT 0.00
            );
        ''')

        # Invoices table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Invoice (
                Invoice_ID INTEGER PRIMARY KEY,
                User_ID INTEGER,
                Invoice_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (User_ID) REFERENCES User(User_ID)
            );
        ''')

        # Invoice Line Items table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Invoice_Line_Item (
                Line_Item_ID INTEGER PRIMARY KEY,
                Invoice_ID INTEGER,
                Product_ID INTEGER,
                Quantity INTEGER DEFAULT 0,
                FOREIGN KEY (Invoice_ID) REFERENCES Invoice(Invoice_ID),
                FOREIGN KEY (Product_ID) REFERENCES Product(Product_ID)
            );
        ''')

        self.conn.commit()

    def add_user(self, username, password, role, external_id=None):
        try:
            self.cursor.execute('''
                INSERT INTO User (Username, Password, Role, External_ID)
                VALUES (?, ?, ?, ?);
            ''', (username, password, role, external_id))
            self.conn.commit()
            print("User added successfully.")
        except sqlite3.IntegrityError:
            print("Error: Username already exists. Please choose a different username.")
            self.conn.rollback()

    def add_product(self, product_name, description, stock_quantity=0, unit_price=0.0):
        self.cursor.execute('''
            INSERT INTO Product (Product_Name, Description, Stock_Quantity, Unit_Price)
            VALUES (?, ?, ?, ?);
        ''', (product_name, description, stock_quantity, unit_price))
        self.conn.commit()

    def create_invoice(self, user_id, products):
        self.cursor.execute('''
            INSERT INTO Invoice (User_ID) VALUES (?);
        ''', (user_id,))
        self.conn.commit()

        # Retrieve the last inserted invoice ID
        self.cursor.execute("SELECT last_insert_rowid();")
        invoice_id = self.cursor.fetchone()[0]

        invoice = Invoice(invoice_id, user_id, products)
        self.invoices[user_id].append(invoice)
        return invoice

    def authenticate_user(self, username, password):
        self.cursor.execute('SELECT * FROM User WHERE Username=? AND Password=?;', (username, password))
        user_data = self.cursor.fetchone()
        if user_data:
            user = User(*user_data)
            self.current_user = user
            return user
        return None

    def generate_auth_code(self):
        return ''.join(random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(8))

    def display_stock_list(self):
        # Display stock information as a formatted table
        self.cursor.execute('SELECT * FROM Product;')
        products = self.cursor.fetchall()
        print("\nStock Information (List):")
        print("-" * 70)
        print("{:<8} {:<20} {:<20} {:<15} {:<15}".format("ID", "Product Name", "Description", "Stock Quantity", "Unit Price"))
        print("-" * 70)
        for product in products:
            print("{:<8} {:<20} {:<20} {:<15} {:<15}".format(product[0], product[1], product[2], product[3], product[4]))
        print("-" * 70)

    def display_invoice_information(self, user_id):
        # Display information about invoices for a specific user
        print("\nInvoices for User ID {}: ".format(user_id))
        print("-" * 60)
        print("{:<10} {:<20} {:<20} {:<15}".format("Invoice ID", "User ID", "Invoice Date", "Products"))
        print("-" * 60)
        for invoice in self.invoices[user_id]:
            products_info = ", ".join([f"{item['product'].product_name} ({item['quantity']})" for item in invoice.products])
            print("{:<10} {:<20} {:<20} {:<15}".format(invoice.invoice_id, invoice.user_id, invoice.invoice_date, products_info))
        print("-" * 60)

    def display_stock_pie_chart(self):
        # Display pie chart for stock information
        labels = [product[1] for product in self.products.values()]
        sizes = [product[3] for product in self.products.values()]
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', normalize=False)
        plt.title('Stock Distribution')
        plt.show()

    def display_stock(self):
        # Ask the user how they want to view the stock
        print("\nView Stock:")
        print("1. View as List")
        print("2. View as Pie Chart")

        choice = input("Enter your choice (1-2): ")
        if choice == '1':
            self.display_stock_list()
        elif choice == '2':
            self.display_stock_pie_chart()
        else:
            print("Invalid choice. Please enter 1 or 2.")

    def admin_actions(self):
        while True:
            print("\nAdmin Actions:")
            print("1. Add Product")
            print("2. Edit Product")
            print("3. Delete Product")
            print("4. View Invoices")
            print("5. View Stock")
            print("6. Add New Staff Member")
            print("7. Log Out")
            print("8. Exit")
            
            choice = input("Enter your choice (1-8): ")

            if choice == '1':
                self.add_product_prompt()
            elif choice == '2':
                self.edit_product_prompt()
            elif choice == '3':
                self.delete_product_prompt()
            elif choice == '4':
                self.display_invoice_information('admin')
            elif choice == '5':
                self.display_stock()
            elif choice == '6':
                self.add_staff_user_prompt()
            elif choice == '7':
                self.current_user = None
                break
            elif choice == '8':
                exit()
            else:
                print("Invalid choice. Please enter a number between 1 and 8.")

    def staff_actions(self):
        while True:
            print("\nStaff Actions:")
            print("1. View Invoices")
            print("2. View Stock")
            print("3. Log Out")
            print("4. Exit")

            choice = input("Enter your choice (1-4): ")

            if choice == '1':
                self.display_invoice_information('staff')
            elif choice == '2':
                self.display_stock()
            elif choice == '3':
                self.current_user = None
                break
            elif choice == '4':
                exit()
            else:
                print("Invalid choice. Please enter a number between 1 and 4.")

    def add_staff_user_prompt(self):
        username = input("Enter the username for the new staff user: ")
        password = input("Enter the password for the new staff user: ")

        # Add the new staff user with 'staff' role
        self.add_user(username, password, 'staff')
        print("New staff user added successfully.")

    def add_product_prompt(self):
        product_name = input("Enter the product name: ")
        description = input("Enter the product description: ")
        stock_quantity = int(input("Enter the stock quantity: "))
        unit_price = float(input("Enter the unit price: "))

        self.add_product(product_name, description, stock_quantity, unit_price)
        print("Product added successfully.")

    def edit_product_prompt(self):
        product_id = int(input("Enter the product ID to edit: "))
        product = self.get_product_by_id(product_id)

        if product:
            print("Current Product Information:")
            print("Product Name:", product.product_name)
            print("Description:", product.description)
            print("Stock Quantity:", product.stock_quantity)
            print("Unit Price:", product.unit_price)

            product_name = input("Enter the new product name (press Enter to keep the current value): ")
            description = input("Enter the new product description (press Enter to keep the current value): ")
            stock_quantity = input("Enter the new stock quantity (press Enter to keep the current value): ")
            unit_price = input("Enter the new unit price (press Enter to keep the current value): ")

            if product_name:
                product.product_name = product_name
            if description:
                product.description = description
            if stock_quantity:
                product.stock_quantity = int(stock_quantity)
            if unit_price:
                product.unit_price = float(unit_price)

            self.update_product(product)
            print("Product updated successfully.")
        else:
            print("Product not found.")

    def delete_product_prompt(self):
        product_id = int(input("Enter the product ID to delete: "))
        product = self.get_product_by_id(product_id)

        if product:
            self.delete_product(product_id)
            print("Product deleted successfully.")
        else:
            print("Product not found.")

    def get_product_by_id(self, product_id):
        self.cursor.execute('SELECT * FROM Product WHERE Product_ID=?;', (product_id,))
        product_data = self.cursor.fetchone()
        if product_data:
            return Product(*product_data)
        return None

    def update_product(self, product):
        self.cursor.execute('''
            UPDATE Product
            SET Product_Name=?, Description=?, Stock_Quantity=?, Unit_Price=?
            WHERE Product_ID=?;
        ''', (product.product_name, product.description, product.stock_quantity, product.unit_price, product.product_id))
        self.conn.commit()

    def delete_product(self, product_id):
        self.cursor.execute('DELETE FROM Product WHERE Product_ID=?;', (product_id,))
        self.conn.commit()

    def close_connection(self):
        self.conn.close()

def main():
    # Initialize the stock control system
    stock_system = StockControlSystem()

    # Create tables if not exists
    stock_system.create_tables()

    while True:
        print("\nWelcome to Stock Control System!")
        print("1. Log In")
        print("2. Exit")

        choice = input("Enter your choice (1-2): ")

        if choice == '1':
            # Log in
            username = input("Enter your username: ")
            password = input("Enter your password: ")
            authenticated_user = stock_system.authenticate_user(username, password)

            if authenticated_user:
                print("Login successful. Welcome, {}!".format(authenticated_user.username))
                if authenticated_user.role == 'admin':
                    stock_system.admin_actions()
                else:
                    stock_system.staff_actions()
            else:
                print("Invalid credentials. Please try again.")

        elif choice == '2':
            # Exit
            stock_system.close_connection()
            print("Exiting Stock Control System...")
            exit()

        else:
            print("Invalid choice. Please enter a number between 1 and 2.")

if __name__ == "__main__":
    main()
