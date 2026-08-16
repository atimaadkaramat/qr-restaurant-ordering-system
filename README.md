# QR Restaurant Ordering System

#### Video Demo: <YOUR VIDEO URL HERE>

#### Description:

QR Restaurant Ordering System is a web-based restaurant ordering and management application developed as my final project for CS50x by Harvard University. The project is designed around a simple idea: each restaurant table has its own QR code, allowing customers to open a digital menu for their specific table, place an order, and check the current status of their latest order. Restaurant staff can then manage those orders through a protected administration dashboard.

The application was built using Python and Flask for the backend, SQLite for data storage, and HTML, CSS, Bootstrap, and Jinja templates for the frontend. I chose Flask because it allowed me to build the application's routes and server-side logic without introducing unnecessary framework complexity. SQLite was chosen because the project is relatively small and benefits from having a lightweight relational database that can be queried directly from Python.

### Customer Features

The main customer workflow begins with the QR code assigned to a table. Each QR code points to a route such as `/table/1` or `/table/2`. When the customer opens that route, the application stores the table number in the Flask session and displays the current menu from the database. This allows the application to associate the customer's cart and order with the correct table.

Customers can add menu items to their cart, increase or decrease quantities, remove individual items, and view the calculated total before placing an order. When an order is placed, the application creates a record in the `orders` table and creates corresponding records in `order_items`. After the order is submitted, the customer's cart is cleared.

The homepage also contains an order-tracking feature. A customer can enter a table number and the application retrieves the latest order for that table. The customer can then check whether the order is Pending, Preparing, Ready, or Completed.

### Admin Features

The administration area is protected by login authentication. Passwords are stored as hashes using Werkzeug's password hashing functions rather than being stored as plain text. Once authenticated, an administrator can access the dashboard, table overview, and menu-management features.

The admin dashboard displays incoming orders with their table numbers, ordered items, total prices, and current statuses. Administrators can update an order through the stages Pending, Preparing, Ready, and Completed. A completed order can be cleared individually, and the dashboard also provides a separate option to clear all orders when the restaurant needs to reset the order list.

The Tables page provides an overview of the restaurant's ten tables. Each table displays its QR code and is marked as Available or Occupied. A table is considered occupied when it has an order that has not yet been completed. The page also displays the current active order status when a table is occupied.

The Edit Menu page allows administrators to add menu items. Each item has a name, price, category, and image filename. Categories are selected from a dropdown menu to keep menu data consistent. Existing menu items are displayed in a table and can be deleted by the administrator.

### Database Design

The project uses SQLite with four main tables: `users`, `menu_items`, `orders`, and `order_items`.

The `users` table stores administrator accounts and password hashes. The `menu_items` table stores the restaurant's menu information. The `orders` table stores the overall details of each customer order, including the table number, total price, status, and creation time. The `order_items` table connects individual menu items to their orders and stores the quantity ordered.

I chose to keep `orders` and `order_items` as separate tables because one order can contain multiple menu items. This relational design avoids repeating the order's general information for every item and makes the database easier to query and maintain.

### Sessions and Access Control

Flask sessions are used for two important purposes. First, the customer session stores the current table number and cart. If a customer opens a different table, the existing cart is cleared so items from one table cannot accidentally be ordered for another table. Second, sessions are used to keep track of the authenticated administrator.

Administrative routes such as the dashboard, table overview, menu management, order status updates, and order deletion are protected so they cannot be accessed without an administrator session.

### Design Decisions

During development, I considered adding more advanced features such as online payment processing and real-time order updates. I decided not to include them because they would significantly increase the complexity of the application without being necessary to demonstrate the core restaurant workflow. Instead, I focused on making the QR ordering, cart, order management, table overview, menu management, and order tracking features work together as one complete system.

I also initially considered putting menu management directly inside the dashboard. I eventually separated it into its own `/edit_menu` page so that the dashboard could remain focused on active restaurant orders while menu administration had its own dedicated interface.

### Project Files

- `app.py` — Contains the Flask application, routes, authentication, session handling, database queries, cart logic, order processing, admin functionality, and table management.
- `schema.sql` — Contains the SQLite database schema for the `users`, `menu_items`, `orders`, and `order_items` tables.
- `restaurant.db` — The SQLite database used by the application during development and demonstration.
- `generate_qr.py` — Generates QR code images for restaurant tables 1 through 10.
- `requirements.txt` — Lists the Python packages required to run the application.
- `.gitignore` — Specifies files and directories that should not be tracked by Git, such as the virtual environment and Python cache files.
- `templates/layout.html` — Contains the shared page layout, navigation bar, customer/admin navigation logic, and footer.
- `templates/index.html` — Contains the public homepage and customer-facing introduction to the system.
- `templates/menu.html` — Displays the menu for the selected restaurant table and allows customers to add items to their cart.
- `templates/cart.html` — Displays the customer's cart, quantities, item totals, and overall order total.
- `templates/order_success.html` — Displays the confirmation page after an order has been successfully placed.
- `templates/track_order.html` — Allows customers to enter their table number and view the current status of their latest order.
- `templates/login.html` — Provides the administrator login form.
- `templates/dashboard.html` — Displays restaurant orders and provides controls for updating and clearing orders.
- `templates/tables.html` — Displays all restaurant tables, their QR codes, and their current availability or active order status.
- `templates/edit_menu.html` — Provides menu-item creation and deletion functionality for administrators.
- `static/style.css` — Contains custom CSS used in addition to Bootstrap.
- `static/images/` — Contains the menu item images used by the application.
- `static/qr/` — Contains the generated QR code images for the restaurant tables.

### Conclusion

This project gave me practical experience building a complete full-stack web application. It allowed me to apply concepts involving Flask routing, sessions, authentication, relational databases, SQL queries, CRUD operations, server-side templates, responsive interfaces, and application workflow design. More importantly, it gave me experience turning a real-world problem into a working software system rather than building separate features that do not interact with one another.
