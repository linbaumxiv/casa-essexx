# 🏠  Casa Essexx - Multi-Vendor Marketplace

An e-commerce platform built with Django and MariaDB that allows Vendors to manage stores and Buyers to purchase products with verified review tracking.

### 🚀 Local Setup & Installation
Follow these steps in the exact order provided to get the application running on your local machine. Ensure you have MariaDB installed before starting.

1. Clone the Project:

First, download the project files to your local machine:

2. Set Up Virtual Environment:

Enter the project folder and create a virtual environment to isolate dependencies:

3. Configure Dependencies:

Install the required libraries, including the MariaDB client and REST framework, directly from the project folder:

4. Database Configuration (MariaDB):

Before migrations will work, you must manually create the database and a user within MariaDB.

Open your MariaDB/MySQL prompt:

Run the following commands to create the database and a fresh user account:

Update the DATABASES section in casa_essexx/settings.py with the credentials created above.

5. Initialize & Run:

Apply the migrations to set up the schema and create an admin account for the dashboard:

Once the server is running, open your web browser and go to: 
http://127.0.0.1:8000/

#### 🛠 Features & UI Logic

#### 🔐 Role-Based Security

Registration: Users select a single role (Buyer or Vendor) from a dropdown menu. Vendors cannot buy, and Buyers cannot manage stores.

Unique Credentials: Emails must be unique to support secure password resets and account integrity.

Auto-Login: Registered users are logged in immediately upon account creation for a seamless experience.

### 🛒 Shopping & Inventory

Contextual Navigation: The "View Cart" option is hidden for Vendors and Guests. It only appears for logged-in Buyers.

Quantity Selection: Buyers can type in specific quantities. The system validates this against current stock and the user's existing cart to prevent overselling.

Atomic Checkout: Stock is deducted automatically during the transaction process to ensure inventory accuracy.

Back to Shopping: A "Continue Shopping" button is provided in the cart view to return to the marketplace easily.

### ⭐ Verified Reviews

Reviews are automatically flagged as "Verified Purchase" if the system detects the user has successfully checked out with that specific product in their order history.

### 🧪 Testing
To verify the application logic, security permissions, and stock deduction