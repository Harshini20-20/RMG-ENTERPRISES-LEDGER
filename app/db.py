import os, sqlite3
from pathlib import Path
from contextlib import contextmanager
DB_PATH=Path(os.environ.get("RMG_DB_PATH",str(Path(__file__).resolve().parent.parent/"data"/"retailer_ledger.db")))
DB_PATH.parent.mkdir(parents=True,exist_ok=True)
@contextmanager
def db_conn():
 c=sqlite3.connect(DB_PATH,timeout=15); c.row_factory=sqlite3.Row; c.execute("PRAGMA foreign_keys=ON"); c.execute("PRAGMA journal_mode=WAL")
 try:
  yield c; c.commit()
 except Exception:
  c.rollback(); raise
 finally: c.close()
def init_db():
 with db_conn() as c:
  c.executescript('''
  CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,username TEXT UNIQUE NOT NULL,password_hash TEXT NOT NULL,role TEXT NOT NULL CHECK(role IN ('admin','agent')),active INTEGER NOT NULL DEFAULT 1,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
  CREATE TABLE IF NOT EXISTS retailers(id INTEGER PRIMARY KEY,name TEXT NOT NULL,address TEXT DEFAULT '',phone TEXT DEFAULT '',agent_id INTEGER REFERENCES users(id) ON DELETE SET NULL,active INTEGER NOT NULL DEFAULT 1,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
  CREATE TABLE IF NOT EXISTS bills(id INTEGER PRIMARY KEY,retailer_id INTEGER NOT NULL REFERENCES retailers(id),bill_number TEXT NOT NULL,due_paise INTEGER NOT NULL CHECK(due_paise>0),created_by INTEGER NOT NULL REFERENCES users(id),created_at TEXT DEFAULT CURRENT_TIMESTAMP,UNIQUE(retailer_id,bill_number));
  CREATE TABLE IF NOT EXISTS payments(id INTEGER PRIMARY KEY,retailer_id INTEGER NOT NULL REFERENCES retailers(id),amount_paise INTEGER NOT NULL CHECK(amount_paise>0),note TEXT DEFAULT '',created_by INTEGER NOT NULL REFERENCES users(id),created_at TEXT DEFAULT CURRENT_TIMESTAMP);
  CREATE TABLE IF NOT EXISTS audit_log(id INTEGER PRIMARY KEY,actor_id INTEGER NOT NULL REFERENCES users(id),action TEXT NOT NULL,details TEXT DEFAULT '',created_at TEXT DEFAULT CURRENT_TIMESTAMP);
  ''')
  # Additive migration: preserve all existing payment rows and their history.
  cols={row['name'] for row in c.execute('PRAGMA table_info(payments)').fetchall()}
  additions={
   'payment_mode': "TEXT NOT NULL DEFAULT 'LEGACY'",
   'proof_filename': 'TEXT',
   'handover_status': "TEXT NOT NULL DEFAULT 'legacy'",
   'handover_confirmed_by': 'INTEGER REFERENCES users(id)',
   'handover_confirmed_at': 'TEXT',
  }
  for name, declaration in additions.items():
   if name not in cols:
    c.execute(f'ALTER TABLE payments ADD COLUMN {name} {declaration}')
