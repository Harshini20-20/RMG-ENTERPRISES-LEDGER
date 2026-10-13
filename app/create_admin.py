import getpass
from app.db import init_db,db_conn
from app.security import hash_pw
def main():
 init_db()
 with db_conn() as c:
  if c.execute("SELECT 1 FROM users WHERE role='admin'").fetchone(): print("Admin already exists; unchanged."); return
  name=input("Admin username: ").strip()
  while not name: name=input("Username required: ").strip()
  while True:
   p=getpass.getpass("Password (8+ characters): "); q=getpass.getpass("Confirm password: ")
   if p!=q: print("Passwords do not match.")
   elif len(p)<8: print("Password too short.")
   else: break
  c.execute("INSERT INTO users(username,password_hash,role) VALUES(?,?,'admin')",(name,hash_pw(p)))
 print("Admin created.")
if __name__=="__main__":main()
