import os,hashlib,hmac,base64,json,time
from fastapi import HTTPException,Request
SECRET = os.environ.get("RMG_APP_SECRET")

if not SECRET or len(SECRET) < 32:
    raise RuntimeError(
        "Set RMG_APP_SECRET to a random secret of at least 32 characters."
    )
def hash_pw(p):
 if len(p)<8: raise ValueError("Password must be at least 8 characters.")
 salt=os.urandom(16); d=hashlib.pbkdf2_hmac("sha256",p.encode(),salt,310000)
 return base64.urlsafe_b64encode(salt).decode()+"."+base64.urlsafe_b64encode(d).decode()
def check_pw(p,s):
 try:
  a,b=s.split(".",1); salt=base64.urlsafe_b64decode(a); want=base64.urlsafe_b64decode(b); got=hashlib.pbkdf2_hmac("sha256",p.encode(),salt,310000); return hmac.compare_digest(got,want)
 except Exception:return False
def token(u):
 body=base64.urlsafe_b64encode(json.dumps({"id":u["id"],"role":u["role"],"exp":int(time.time())+43200}).encode()).decode()
 sig=hmac.new(SECRET.encode(),body.encode(),hashlib.sha256).hexdigest()
 return body+"."+sig
def decode(t):
 try:
  b,s=t.split(".",1); exp=hmac.new(SECRET.encode(),b.encode(),hashlib.sha256).hexdigest()
  if not hmac.compare_digest(s,exp): raise ValueError()
  p=json.loads(base64.urlsafe_b64decode(b)); 
  if p["exp"]<time.time(): raise ValueError()
  return p
 except Exception: raise HTTPException(401,"Please log in again.")


def user_for(req, c):
    path = req.url.path

    if path.startswith("/admin/"):
        cookie_name = "rmg_admin_session"
        expected_role = "admin"
    elif path.startswith("/agent/"):
        cookie_name = "rmg_agent_session"
        expected_role = "agent"
    else:
        # API requests use the role-specific cookie that is present.
        if req.cookies.get("rmg_admin_session"):
            cookie_name = "rmg_admin_session"
            expected_role = "admin"
        elif req.cookies.get("rmg_agent_session"):
            cookie_name = "rmg_agent_session"
            expected_role = "agent"
        else:
            cookie_name = "rmg_session"
            expected_role = None

    t = req.cookies.get(cookie_name)
    if not t:
        raise HTTPException(401, "Please log in.")

    p = decode(t)

    u = c.execute(
        "SELECT id, username, role, active FROM users WHERE id=?",
        (p["id"],)
    ).fetchone()

    if not u or not u["active"] or u["role"] != p["role"]:
        raise HTTPException(401, "Account unavailable.")

    if expected_role and u["role"] != expected_role:
        raise HTTPException(403, "You do not have permission.")

    return dict(u)

def role_for(req,c,role):
 u=user_for(req,c)
 if u["role"]!=role: raise HTTPException(403,"You do not have permission.")
 return u
