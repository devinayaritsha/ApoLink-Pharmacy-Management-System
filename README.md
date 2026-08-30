# 💊 ApoLink - Integrated Pharmacy System
ApoLink is a lightweight, desktop-based pharmacy management system built with **Python**, **Tkinter**, and **PostgreSQL**. It is designed to streamline pharmacy operations featuring a **Role-Based Access Control (RBAC)** system and persistent, database-backed data storage.
---
## ✨ Key Features
- **🛡️ Role-Based Access Control (RBAC)**:
  - **Admin**: Full system access, user management, inventory, and reporting.
  - **Cashier**: Access to Point of Sale (POS) cashier interface, receipt generation, and patient records.
  - **Pharmacist**: Access to product management, stock opname, supplier directory, and expiration reporting.
- **🛒 POS & Live Search**: Interactive checkout system with real-time product filtering and printable receipt output.
- **📦 Stock & Expiration Tracking**: Automatic tracking of inventory levels and expiration alerts (Active, Expiring Soon, Expired).
- **📜 Transaction History**: Detailed audit log of sales per product.
- **🗄️ PostgreSQL-Backed Storage**: All data (users, products, patients, suppliers, stock opname, and transactions) is persisted in a PostgreSQL database, so nothing is lost when the app is closed.
---
## 🛠️ Tech Stack
- **Python 3** + **Tkinter** — desktop UI
- **PostgreSQL** — persistent data storage
- **psycopg2** — PostgreSQL database adapter
- **python-dotenv** — environment variable management
---
## 📁 Project Structure
```text
ApoLink-Pharmacy-Management-System/
├── main.py             # Main application entry point
├── login.py            # Authentication & login interface
├── dashboard.py        # Core dashboard & modular features
├── db.py                # Database connection & CRUD functions (PostgreSQL)
├── schema.sql           # Database schema & seed data
├── requirements.txt      # Python dependencies
├── .env.example         # Template for database credentials
└── README.md            # Project documentation
```
## 🚀 Getting Started

### 1. Clone this repository
```bash
git clone https://github.com/devinayaritsha/ApoLink-Pharmacy-Management-System.git
cd ApoLink-Pharmacy-Management-System
```

### 2. Install Python dependencies
```bash
pip3 install -r requirements.txt
```

### 3. Set up the PostgreSQL database
Create a new database (name it whatever you like, e.g. `apolink`), then run the schema file against it to create the tables and seed initial data:
```bash
psql -U your_postgres_user -d apolink -f schema.sql
```
(Or open `schema.sql` in a GUI tool like DBeaver/pgAdmin and execute it as a script.)

### 4. Configure environment variables
Copy the example env file and fill in your own database credentials:
```bash
cp .env.example .env
```
Then edit `.env`:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=apolink
DB_USER=your_postgres_user
DB_PASSWORD=your_postgres_password
```
> ⚠️ `.env` contains real credentials and is excluded via `.gitignore` — never commit it.

### 5. Run the application
```bash
python3 main.py
```

## 🔑 Demo Credentials
| Role | Username | Password | Access Level |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `123` | Full Access (All Modules) |
| **Cashier** | `budi` | `123` | Dashboard, Cashier, Patients |
| **Pharmacist** | `siti` | `123` | Dashboard, Products, Expired Report, Suppliers, Stock Opname |

> These accounts are seeded automatically by `schema.sql`.

## 📝 License
Distributed under the MIT License. See LICENSE for more information.
