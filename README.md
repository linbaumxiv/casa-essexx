# 🏠  Casa Essexx - Multi-Vendor Marketplace

An e-commerce platform built with Django and MariaDB that allows Vendors to manage stores and Buyers to purchase products with verified review tracking.

## Features
- **Role-Based Access:** Distinct Vendor and Buyer accounts.
- **Store Management:** Full CRUD for Vendors to manage their retail space.
- **Session-Based Cart:** Anonymous cart storage using Django sessions.
- **Secure Checkout:** Transaction-safe inventory management and automated email invoices.
- **Verified Reviews:** Automatic detection of purchase history for reviewer credibility.

---

## 🛠 Prerequisites
- **Python 3.10+**
- **MariaDB Server** (Running locally or remotely)
- **Pip** (Python package manager)

---

## 🚀 Local Setup & Installation

### 1. Clone & Environment Setup
First, clone the repository and create a virtual environment to isolate project dependencies:
```bash
git clone <your-repo-url>
cd casa_essexx
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

### 2. Configure Dependencies

Install the required libraries. This includes mysqlclient (for MariaDB connection), djangorestframework (for the API), and tweepy (for social media signals):

Bash
pip install --upgrade pip
pip install -r requirements.txt

### 3. Database Configuration

Log into your MariaDB terminal and create the database:

SQL:
CREATE DATABASE casa_essexx_db;
Create a .env file in the root directory and add your credentials:

Code snippet:
DB_NAME=casa_essexx_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=3306
SECRET_KEY=your_django_secret_key

### 4. Database Migrations

Initialize the MariaDB schema by running the migration files:

Bash:
python3 manage.py makemigrations
python3 manage.py migrate

### 5. Create Administrative Access

To access the Vendor Dashboard and Admin panel, create a superuser:

Bash:
python3 manage.py createsuperuser

### 6. Start the Development Server

Bash:
python3 manage.py runserver
The application will be available at http://127.0.0.1:8000/.

### 🔐 API Security & Permissions
Important for Reviewers:
This project implements strict Role-Based Access Control (RBAC) via Django Rest Framework:

Guests/Unauthenticated Users: Can view products via GET requests but cannot create or modify data.

Buyers: Can browse and purchase but are blocked from creating Stores or Products.

Vendors: Have full CRUD permissions for their own Stores and Products.
Permissions are enforced in core/permissions.py and applied to ViewSets in core/views.py.

### 🧪 Testing the Application
To run the automated test suite (including mocked API calls for Twitter signals):

Bash:
python3 manage.py test

###📁 Project Structure Highlights

core/models.py: Custom User model with is_vendor and is_buyer flags.

core/signals.py: Automated Twitter announcements for new inventory.

core/serializers.py: Nested JSON serialization for the REST API.

