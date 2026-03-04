# Casa Essexx - Multi-Vendor Marketplace

An e-commerce platform built with Django and MariaDB that allows Vendors to manage stores and Buyers to purchase products with verified review tracking.

## Features
- **Role-Based Access:** Distinct Vendor and Buyer accounts.
- **Store Management:** Full CRUD for Vendors to manage their retail space.
- **Session-Based Cart:** Anonymous cart storage using Django sessions.
- **Secure Checkout:** Transaction-safe inventory management and automated email invoices.
- **Verified Reviews:** Automatic detection of purchase history for reviewer credibility.

## Local Setup
1. **Database:** Create a MariaDB database named `casa_essexx_db`.
2. **Environment:** Create a `.env` file and add your database credentials and `SECRET_KEY`.
3. **Install Dependencies:** `pip install -r requirements.txt`
4. **Migrate:** `python manage.py migrate`
5. **Start Server:** `python manage.py runserver`