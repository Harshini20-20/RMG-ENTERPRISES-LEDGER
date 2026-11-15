# RMG Enterprises — Retailer Ledger

<p align="center">
  **A web-based retailer ledger and payment management system**
  
  [Live Application](https://rmg-enterprises-ledger.onrender.com/) · [Admin Login](https://rmg-enterprises-ledger.onrender.com/admin/login) · [GitHub Repository](https://github.com/Harshini20-20/RMG-ENTERPRISES-LEDGER)
</p>

## Overview

RMG Enterprises Retailer Ledger is a web-based application designed to simplify retailer billing, payment tracking, and field-agent operations.

The system provides a centralized platform for managing retailer transactions, recording payments, monitoring collections, and maintaining an auditable transaction history.

## Problem Statement

Managing retailer bills and payments manually can lead to inconsistent records, duplicate entries, delayed reconciliation, and difficulty tracking collections across field agents.

This application digitizes these workflows through a centralized ledger with role-based access and transaction tracking.

## Key Features

### Admin Management
- Separate administrator login.
- Manage field agents.
- Assign and reassign retailers to agents.
- Monitor retailer transactions and payment collections.
- Track payment handovers.

### Agent Operations
- Dedicated agent access.
- View assigned retailers.
- Enter retailer bills in bulk.
- Record payments through Cash or UPI.
- View retailer transaction history.

### Payment Tracking
- Record and track payment transactions.
- Maintain payment handover records.
- Support optional UPI payment proof uploads.
- Access uploaded proofs through authenticated routes.

### Data Integrity and Security
- Duplicate bill protection.
- Authentication and role-based access.
- Audit event tracking.
- Centralized transaction records.

## Application Workflow

1. Admin creates and manages agent accounts.
2. Retailers are assigned to field agents.
3. Agents enter retailer bills and record payments.
4. Payment handovers are tracked.
5. Admin monitors transactions and collection activity.
6. Audit records help maintain transaction accountability.

## Technology Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI |
| Frontend | HTML, CSS, JavaScript |
| Database | SQLite / PostgreSQL |
| ORM | SQLAlchemy |
| Database Hosting | Supabase |
| Application Hosting | Render |
| Server | Uvicorn |

## Architecture

The application follows a web-based client-server architecture.

- **Frontend:** Provides interfaces for administrators and field agents.
- **Backend:** FastAPI handles authentication, business logic, retailer operations, and transactions.
- **Database:** SQLAlchemy manages database interactions with SQLite or PostgreSQL.
- **Storage:** Supabase supports hosted database and file-storage functionality.
- **Deployment:** Render hosts the web application.

## Live Application

The application is deployed on Render.

- [Open RMG Enterprises](https://rmg-enterprises-ledger.onrender.com/)
- [Admin Login](https://rmg-enterprises-ledger.onrender.com/admin/login)

*Note: The hosted application may take a little time to respond after periods of inactivity.*

## Local Setup

Clone the repository:

```bash
git clone https://github.com/Harshini20-20/RMG-ENTERPRISES-LEDGER.git
cd RMG-ENTERPRISES-LEDGER
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure the required environment variables using your local environment configuration. Do not commit credentials or secret keys.

Run the application using the project's configured entry point.

## Engineering Highlights

- Implemented role-based workflows for administrators and field agents.
- Developed retailer billing and payment-recording functionality.
- Added duplicate transaction protection.
- Implemented payment handover tracking.
- Incorporated audit events for improved accountability.
- Integrated database-backed application workflows.

## Future Enhancements

- Advanced collection analytics and dashboards.
- Automated payment reconciliation.
- Exportable retailer statements.
- Improved reporting and financial summaries.
- Enhanced mobile experience for field agents.

## Author

**Harshini G**

[GitHub Profile](https://github.com/Harshini20-20)

---

<p align="center">
  Built to digitize retailer ledger operations and simplify payment management.
</p>
