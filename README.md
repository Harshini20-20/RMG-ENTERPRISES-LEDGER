# RMG ENTERPRISES — Retailer Ledger Management System

**A Client-Oriented Digital Ledger and Payment Management Platform**

<p align="center">
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-3.12-blue?logo=python" />
  </a>
  <a href="https://fastapi.tiangolo.com/">
    <img src="https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi" />
  </a>
  <a href="https://render.com/">
    <img src="https://img.shields.io/badge/Deployment-Render-purple?logo=render" />
  </a>
  <a href="https://supabase.com/">
    <img src="https://img.shields.io/badge/Database-Supabase-green?logo=supabase" />
  </a>
</p>

## 🌐 Live Application

- **[Launch RMG Enterprises Ledger](https://rmg-enterprises-ledger.onrender.com/)**
- **[Admin Login](https://rmg-enterprises-ledger.onrender.com/admin/login)**
- **[Agent Login](https://rmg-enterprises-ledger.onrender.com/agent/login)**
- **[GitHub Repository](https://github.com/Harshini20-20/RMG-ENTERPRISES-LEDGER)**

> **Deployment Notice:** The application is currently undergoing database connectivity recovery. Live access may be temporarily unavailable.

---

## 📌 Project Overview

RMG Enterprises Retailer Ledger is a web-based business management application developed to digitize retailer transactions, payment collections and agent operations.

The system provides separate administrative and agent interfaces, allowing administrators to manage agents and retailer assignments while agents can record bills, collect payments and maintain retailer transaction records.

The application aims to reduce manual bookkeeping, improve transaction visibility and maintain structured financial records.

## 🎯 Problem Statement

Traditional retailer ledger management involves manual bill entries, payment tracking and coordination between field agents and administrators.

These processes can result in duplicate entries, inaccurate balances, delayed payment reconciliation and limited visibility into agent collections.

RMG Ledger addresses these challenges through a centralized digital platform with role-based access and structured transaction management.

## ✨ Key Features

### 1. Authentication and Access Management
- Separate Admin and Agent login interfaces.
- Role-specific application access.
- Centralized user and agent management.

### 2. Agent Management
- Create and manage agents.
- Assign retailers to agents.
- Reassign retailers when required.

### 3. Retailer Ledger Management
- Maintain retailer transaction histories.
- Record bills through bulk manual entry.
- Track outstanding balances.
- Prevent duplicate bill entries.

### 4. Payment Management
- Record retailer payment collections.
- Support Cash and UPI payment modes.
- Maintain payment transaction records.
- Optional UPI payment proof uploads.

### 5. Payment Handover Tracking
- Track collections recorded by agents.
- Display pending handovers to administrators.
- Allow administrators to confirm receipt of collected money.
- Maintain separate collection and handover records.

### 6. Audit and Transaction Tracking
- Maintain audit events for important operations.
- Preserve historical payment records.
- Provide authenticated access to payment proof files.

## 🔄 Application Workflow

```text
             Admin Login
                  |
                  v
          Admin Dashboard
                  |
          Manage Agents
                  |
          Assign Retailers
                  |
                  v
             Agent Login
                  |
                  v
          Retailer Selection
                  |
                  v
             Record Bills
                  |
                  v
          Record Collections
                  |
             Cash / UPI
                  |
                  v
          Pending Handovers
                  |
                  v
          Admin Confirmation
                  |
                  v
         Updated Ledger Records
```

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Backend | [Python](https://www.python.org/), [FastAPI](https://fastapi.tiangolo.com/) |
| Frontend | HTML, CSS, JavaScript |
| Local Database | [SQLite](https://www.sqlite.org/) |
| Cloud Database | [PostgreSQL](https://www.postgresql.org/) |
| Database Platform | [Supabase](https://supabase.com/) |
| Database Connectivity | [SQLAlchemy](https://www.sqlalchemy.org/) |
| ASGI Server | [Uvicorn](https://www.uvicorn.org/) |
| Cloud Hosting | [Render](https://render.com/) |
| Version Control | [Git](https://git-scm.com/), [GitHub](https://github.com/) |

## 🏗️ Project Structure

```text
RMG-ENTERPRISES-LEDGER/
│
├── app/
│   ├── main.py
│   └── create_admin.py
│
├── data/
│   ├── retailer_ledger.db
│   └── payment_proofs/
│
├── requirements.txt
├── .gitignore
└── README.md
```

## ⚙️ Installation and Setup

### Prerequisites
- Python 3.12
- Git
- pip

### 1. Clone the Repository

```bash
git clone https://github.com/Harshini20-20/RMG-ENTERPRISES-LEDGER.git

cd RMG-ENTERPRISES-LEDGER
```

### 2. Create a Virtual Environment

```bash
py -3.12 -m venv .venv
```

### 3. Activate the Environment

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Create an Administrator Account

```bash
python -m app.create_admin
```

Follow the prompts to configure administrator credentials.

### 6. Start the Application

```bash
uvicorn app.main:app --reload
```

### 7. Access the Application

| Interface | Local URL |
|---|---|
| Admin Login | http://127.0.0.1:8000/admin/login |
| Agent Login | http://127.0.0.1:8000/agent/login |
| API Documentation | http://127.0.0.1:8000/docs |

## 🔐 Security and Configuration

The application uses environment-based configuration for sensitive settings.

Important configuration variables include:

- `RMG_APP_SECRET`
- `DATABASE_URL`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `SUPABASE_STORAGE_BUCKET`

Security practices:
- Keep credentials outside source control.
- Use HTTPS for public deployments.
- Restrict access to payment proof files.
- Use secure authentication and session configuration.
- Maintain regular database backups.

Never commit `.env` files, database credentials, payment proofs or client information to GitHub.

## 🚀 Deployment

The application is deployed using:

- **Application Hosting:** [Render](https://render.com/)
- **Cloud Database:** [Supabase](https://supabase.com/)
- **Source Code Management:** [GitHub](https://github.com/)

The deployment uses environment variables to configure database connectivity and application secrets.

## 📚 Engineering Highlights

- Designed separate workflows for administrators and field agents.
- Implemented retailer assignment and reassignment functionality.
- Added duplicate bill protection.
- Designed payment collection and handover tracking.
- Maintained historical payment records.
- Implemented authenticated payment-proof access.
- Developed a centralized retailer ledger management workflow.

## 🔮 Future Improvements

- Automated bill generation and PDF receipts.
- Advanced financial reporting and analytics.
- Improved transaction reconciliation.
- Automated database backup and recovery.
- Enhanced mobile responsiveness.
- Real-time operational dashboards.

## 👩‍💻 Developer

**Harshini G**

Artificial Intelligence and Data Science Undergraduate

- **[GitHub Profile](https://github.com/Harshini20-20)**
- **[Project Repository](https://github.com/Harshini20-20/RMG-ENTERPRISES-LEDGER)**

---

<p align="center">
  Developed for RMG Enterprises.
</p>
