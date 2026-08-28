# 💊 ApoLink - Integrated Pharmacy System

ApoLink is a lightweight, desktop-based pharmacy management system built with **Python** and **Tkinter**. It is designed to streamline pharmacy operations featuring a **Role-Based Access Control (RBAC)** system.

---

## ✨ Key Features

- **🛡️ Role-Based Access Control (RBAC)**:
  - **Admin**: Full system access, user management, inventory, and reporting.
  - **Cashier**: Access to Point of Sale (POS) cashier interface, receipt generation, and patient records.
  - **Pharmacist**: Access to product management, stock opname, supplier directory, and expiration reporting.
- **🛒 POS & Live Search**: Interactive checkout system with real-time product filtering and printable receipt output.
- **📦 Stock & Expiration Tracking**: Automatic tracking of inventory levels and expiration alerts (Active, Expiring Soon, Expired).
- **📜 Transaction History**: Detailed audit log of sales per product.

---

## 📁 Project Structure

```text
Apolink/
├── main.py          # Main application entry point
├── login.py         # Authentication & login interface
├── dashboard.py     # Core dashboard & modular features
└── README.md        # Project documentation
```

## 🚀 Getting Started

1. Clone this repository:
```bash
git clone https://github.com/devinayaritsha/ApoLink-Pharmacy-Management-System.git
```
2. Navigate to the project directory:
```bash
cd ApoLink-Pharmacy-Management-System
```
3. Run the application:
```bash
python main.py
```

## 🔑 Demo Credentials
| Role | Username | Password | Access Level |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `123` | Full Access (All Modules) |
| **Cashier** | `budi` | `123` | Dashboard, Cashier, Patients |
| **Pharmacist** | `siti` | `123` | Dashboard, Products, Expired Report, Suppliers, Stock Opname |

## 📝 License
Distributed under the MIT License. See LICENSE for more information.
