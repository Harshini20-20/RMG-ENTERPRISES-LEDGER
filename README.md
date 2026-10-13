# RMG ENTERPRISES Retailer Ledger

Responsive starter for phones and PCs. Includes separate admin/agent login routes, dynamic agents, retailer assignments/reassignment, bulk manual bill entry, payments, retailer history, duplicate bill protection and audit events.

## Windows PowerShell
```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m app.create_admin
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000. Admin login: `/admin/login`; Agent login: `/agent/login`; API docs: `/docs`.

The admin creation command prompts for a username and password. Local SQLite file is `data/retailer_ledger.db`.

**Before public deployment:** configure a strong `RMG_APP_SECRET`, HTTPS, secure cookies, backups, rate limiting and production database settings. This is a development starter, not yet a production-hardened deployment.


## Version 2 — Payment handover tracking

- Agents record collections using required Cash or UPI mode. UPI screenshot proof is optional (JPG/PNG/WEBP, up to 5 MB).
- A recorded collection reduces the retailer outstanding balance once and is shown to admins under Pending Handovers.
- Admins use **Confirm Money Received** after physically receiving the money. This updates only handover metadata; it does not deduct the retailer balance again. There is no reject workflow.
- Existing payment rows are preserved and marked `LEGACY` / `legacy`; they are not incorrectly added to Pending Handovers.
- Proof files are stored under `data/payment_proofs`, outside the static directory, and served only through an authenticated endpoint.

### Upgrade and backup

1. Stop the server before replacing files. Back up `data/retailer_ledger.db` and the entire project folder.
2. Install dependencies with `py -m pip install -r requirements.txt`.
3. Start with `py -m uvicorn app.main:app --reload`. Startup applies additive columns to the existing payments table; it does not delete payment history.
4. Keep the database and proof files private and out of Git. Test on a backup database before using the live data.
