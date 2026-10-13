from fastapi import FastAPI,Request,HTTPException,UploadFile,File,Form
from fastapi.responses import HTMLResponse,JSONResponse,RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel,Field
from decimal import Decimal,InvalidOperation,ROUND_HALF_UP
from pathlib import Path
import uuid
from app.db import init_db,db_conn
from app.security import hash_pw,check_pw,token,user_for,role_for
from fastapi.responses import Response
from app.storage import upload_proof, download_proof, delete_proof
app=FastAPI(title="RMG ENTERPRISES Retailer Ledger")
S = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=S), name="static")@app.on_event("startup")
def startup():init_db()
def paise(v):
 try:a=Decimal(str(v)).quantize(Decimal(".01"),rounding=ROUND_HALF_UP)
 except (InvalidOperation,ValueError):raise HTTPException(422,"Invalid amount.")
 if not a.is_finite() or a<=0:raise HTTPException(422,"Amount must be positive.")
 return int(a*100)
def rupees(p):return f"{Decimal(p)/100:.2f}"
def audit(c,u,a,d=""):c.execute("INSERT INTO audit_log(actor_id,action,details) VALUES(?,?,?)",(u["id"],a,d))
def balance(c,r):
 b=c.execute("SELECT COALESCE(SUM(due_paise),0) n FROM bills WHERE retailer_id=?",(r,)).fetchone()["n"]
 p=c.execute("SELECT COALESCE(SUM(amount_paise),0) n FROM payments WHERE retailer_id=?",(r,)).fetchone()["n"]
 return int(b)-int(p)
def retail(c,r):return {"id":r["id"],"name":r["name"],"address":r["address"],"phone":r["phone"],"agent_id":r["agent_id"],"outstanding":rupees(balance(c,r["id"]))}
def access(c,u,r):
 x=c.execute("SELECT * FROM retailers WHERE id=? AND active=1",(r,)).fetchone()
 if not x:raise HTTPException(404,"Retailer not found.")
 if u["role"]=="agent" and x["agent_id"]!=u["id"]:raise HTTPException(403,"Retailer is not assigned to you.")
 return x
class Login(BaseModel):username:str;password:str
class Agent(BaseModel):username:str=Field(min_length=3,max_length=60);password:str=Field(min_length=8,max_length=128)
class Retailer(BaseModel):name:str=Field(min_length=1,max_length=160);address:str="";phone:str="";agent_id:int|None=None
class Bill(BaseModel):retailer_id:int;bill_number:str=Field(min_length=1,max_length=100);due_amount:Decimal
class Batch(BaseModel):bills:list[Bill]=Field(min_length=1,max_length=250)
class Payment(BaseModel):amount:Decimal;note:str=""
@app.get("/")
def home():return RedirectResponse("/admin/login")
def login_html(role):
 h=(S/"login.html").read_text().replace("{{ROLE}}",role).replace("{{PORTAL}}",role.title()).replace("{{OTHER}}","Agent" if role=="admin" else "Admin").replace("{{OTHER_URL}}","/agent/login" if role=="admin" else "/admin/login")
 return HTMLResponse(h)
@app.get("/admin/login",response_class=HTMLResponse)
def alogin():return login_html("admin")
@app.get("/agent/login",response_class=HTMLResponse)
def elogin():return login_html("agent")
@app.get("/admin/dashboard",response_class=HTMLResponse)
def adash():return HTMLResponse((S/"dashboard.html").read_text().replace("{{ROLE}}","admin").replace("{{PORTAL}}","Admin"))
@app.get("/agent/dashboard",response_class=HTMLResponse)
def edash():return HTMLResponse((S/"dashboard.html").read_text().replace("{{ROLE}}","agent").replace("{{PORTAL}}","Agent"))

@app.post("/api/login")
def login(p: Login, req: Request):
    role = req.query_params.get("role")
    if role not in ("admin", "agent"):
        raise HTTPException(400, "Select a login portal.")

    with db_conn() as c:
        u = c.execute(
            "SELECT * FROM users WHERE username=? AND active=1",
            (p.username.strip(),)
        ).fetchone()

        if not u or u["role"] != role or not check_pw(
            p.password, u["password_hash"]
        ):
            raise HTTPException(401, "Invalid credentials for this portal.")

        res = JSONResponse({
            "redirect": "/admin/dashboard" if role == "admin"
            else "/agent/dashboard"
        })

        cookie_name = "rmg_admin_session" if role == "admin" else "rmg_agent_session"

        res.set_cookie(
            cookie_name,
            token(dict(u)),
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=43200
        )
        return res


@app.post("/api/logout")
def logout(req: Request):
    role = req.query_params.get("role")
    res = JSONResponse({"ok": True})

    if role in ("admin", "agent"):
        cookie_name = "rmg_admin_session" if role == "admin" else "rmg_agent_session"
        res.delete_cookie(cookie_name)

    return res

@app.get("/api/me")
def me(req:Request):
 with db_conn() as c:return {k:v for k,v in user_for(req,c).items() if k in ("id","username","role")}
@app.get("/api/summary")
def summary(req:Request):
 with db_conn() as c:
  u=user_for(req,c)
  if u["role"]=="admin":
   rs=c.execute("SELECT * FROM retailers WHERE active=1").fetchall(); return {"retailer_count":len(rs),"agent_count":c.execute("SELECT COUNT(*) n FROM users WHERE role='agent' AND active=1").fetchone()["n"],"bill_count":c.execute("SELECT COUNT(*) n FROM bills").fetchone()["n"],"outstanding":rupees(sum(max(0,balance(c,r["id"])) for r in rs))}
  rs=c.execute("SELECT * FROM retailers WHERE active=1 AND agent_id=?",(u["id"],)).fetchall()
  return {"retailer_count":len(rs),"agent_count":None,"bill_count":None,"outstanding":rupees(sum(max(0,balance(c,r["id"])) for r in rs))}
@app.get("/api/agents")
def agents(req:Request):
 with db_conn() as c:
  role_for(req,c,"admin")
  return [dict(x) for x in c.execute("SELECT u.id,u.username,u.active,COUNT(r.id) retailer_count FROM users u LEFT JOIN retailers r ON r.agent_id=u.id AND r.active=1 WHERE u.role='agent' GROUP BY u.id ORDER BY u.username")]

@app.post("/api/agents")
def new_agent(p: Agent, req: Request):
    with db_conn() as c:
        u = role_for(req, c, "admin")

        try:
            x = c.execute(
                """
                INSERT INTO users (username, password_hash, role)
                VALUES (?, ?, 'agent')
                RETURNING id
                """,
                (p.username.strip(), hash_pw(p.password)),
            ).fetchone()
        except Exception as e:
            if "UNIQUE" in str(e) or "unique" in str(e).lower():
                raise HTTPException(409, "Username already exists.")
            raise

        audit(c, u, "agent_created", p.username)
        return {"id": x["id"], "username": p.username}

@app.patch("/api/agents/{aid}")
def disable_agent(aid:int,req:Request):
 with db_conn() as c:
  u=role_for(req,c,"admin");x=c.execute("SELECT username,role FROM users WHERE id=?",(aid,)).fetchone()
  if not x or x["role"]!="agent":raise HTTPException(404,"Agent not found.")
  c.execute("UPDATE users SET active=0 WHERE id=?",(aid,));audit(c,u,"agent_deactivated",x["username"]);return {"ok":True}
@app.get("/api/retailers")
def retailers(req:Request):
 with db_conn() as c:
  u=user_for(req,c)
  rows=c.execute("SELECT * FROM retailers WHERE active=1 "+("AND agent_id=? " if u["role"]=="agent" else "")+"ORDER BY name",((u["id"],) if u["role"]=="agent" else ())).fetchall()
  return [retail(c,r) for r in rows]

@app.post("/api/retailers")
def new_retailer(p: Retailer, req: Request):
    with db_conn() as c:
        u = role_for(req, c, "admin")

        if p.agent_id is not None:
            agent = c.execute(
                """
                SELECT id FROM users
                WHERE id = ? AND role = 'agent' AND active = 1
                """,
                (p.agent_id,),
            ).fetchone()

            if not agent:
                raise HTTPException(422, "Choose an active agent.")

        x = c.execute(
            """
            INSERT INTO retailers (name, address, phone, agent_id)
            VALUES (?, ?, ?, ?)
            RETURNING id
            """,
            (
                p.name.strip(),
                p.address.strip(),
                p.phone.strip(),
                p.agent_id,
            ),
        ).fetchone()

        audit(c, u, "retailer_created", p.name)
        return {"id": x["id"], "name": p.name}

@app.patch("/api/retailers/{rid}/assignment")
def assign(rid:int,req:Request,agent_id:int|None=None):
 with db_conn() as c:
  u=role_for(req,c,"admin")
  if not c.execute("SELECT id FROM retailers WHERE id=? AND active=1",(rid,)).fetchone():raise HTTPException(404,"Retailer not found.")
  if agent_id is not None and not c.execute("SELECT id FROM users WHERE id=? AND role='agent' AND active=1",(agent_id,)).fetchone():raise HTTPException(422,"Choose an active agent.")
  c.execute("UPDATE retailers SET agent_id=? WHERE id=?",(agent_id,rid));audit(c,u,"retailer_reassigned",f"{rid}:{agent_id}");return {"ok":True}
@app.get("/api/retailers/{rid}")
def detail(rid:int,req:Request):
 with db_conn() as c:
  u=user_for(req,c);r=access(c,u,rid)
  bills=[{"id":x["id"],"bill_number":x["bill_number"],"due_amount":rupees(x["due_paise"]),"created_at":x["created_at"]} for x in c.execute("SELECT * FROM bills WHERE retailer_id=? ORDER BY id DESC",(rid,))]
  pays=[{"id":x["id"],"amount":rupees(x["amount_paise"]),"note":x["note"],"created_at":x["created_at"],"payment_mode":x["payment_mode"],"handover_status":x["handover_status"],"proof_available":bool(x["proof_filename"]),"handover_confirmed_at":x["handover_confirmed_at"],"handover_confirmed_by":x["handover_confirmed_by_username"]} for x in c.execute("SELECT p.*,u.username AS handover_confirmed_by_username FROM payments p LEFT JOIN users u ON u.id=p.handover_confirmed_by WHERE p.retailer_id=? ORDER BY p.id DESC",(rid,))]
  return {"retailer":retail(c,r),"bills":bills,"payments":pays}
@app.post("/api/bills/bulk")
def bulk(p:Batch,req:Request):
 with db_conn() as c:
  u=role_for(req,c,"admin");clean=[];seen=set()
  for i,b in enumerate(p.bills,1):
   n=b.bill_number.strip();key=(b.retailer_id,n.casefold())
   if not n:raise HTTPException(422,f"Bill {i}: number required.")
   if key in seen:raise HTTPException(409,f"Bill {i}: duplicate within batch.")
   seen.add(key)
   if not c.execute("SELECT id FROM retailers WHERE id=? AND active=1",(b.retailer_id,)).fetchone():raise HTTPException(422,f"Bill {i}: invalid retailer.")
   clean.append((b.retailer_id,n,paise(b.due_amount)))
  for rid,n,_ in clean:
   if c.execute("SELECT id FROM bills WHERE retailer_id=? AND lower(bill_number)=lower(?)",(rid,n)).fetchone():raise HTTPException(409,f"Bill {n} already exists for that retailer.")
  for rid,n,a in clean:c.execute("INSERT INTO bills(retailer_id,bill_number,due_paise,created_by) VALUES(?,?,?,?)",(rid,n,a,u["id"]))
  audit(c,u,"bulk_bills_added",f"count={len(clean)}");return {"ok":True,"created":len(clean),"total_due":rupees(sum(x[2] for x in clean))}


@app.post("/api/retailers/{rid}/payments")
async def payment(
    rid: int,
    req: Request,
    amount: Decimal = Form(...),
    note: str = Form(""),
    payment_mode: str = Form(...),
    proof: UploadFile | None = File(None),
):
    mode = payment_mode.strip().upper()

    if mode not in ("CASH", "UPI"):
        raise HTTPException(422, "Choose Cash or UPI.")

    has_proof = proof is not None and bool(proof.filename)

    if has_proof and mode != "UPI":
        raise HTTPException(
            422, "Screenshot proof is only allowed for UPI payments."
        )

    proof_name = None
    data = None
    uploaded = False

    if has_proof:
        if proof.content_type not in (
            "image/jpeg", "image/png", "image/webp"
        ):
            raise HTTPException(
                422, "Upload a JPG, PNG or WEBP screenshot."
            )

        data = await proof.read(5 * 1024 * 1024 + 1)

        if len(data) > 5 * 1024 * 1024:
            raise HTTPException(
                413, "Screenshot must be 5 MB or smaller."
            )

        valid = (
            data.startswith(b"\xff\xd8\xff")
            if proof.content_type == "image/jpeg"
            else data.startswith(b"\x89PNG\r\n\x1a\n")
            if proof.content_type == "image/png"
            else (
                data.startswith(b"RIFF")
                and data[8:12] == b"WEBP"
            )
        )

        if not valid:
            raise HTTPException(
                422, "The uploaded file does not match its image type."
            )

        ext = {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/webp": ".webp",
        }[proof.content_type]

        proof_name = uuid.uuid4().hex + ext

    try:
        with db_conn() as c:
            u = user_for(req, c)
            access(c, u, rid)
            amount_paise = paise(amount)

            if amount_paise > balance(c, rid):
                raise HTTPException(
                    422, "Payment exceeds outstanding balance."
                )

            if proof_name:
                try:
                    upload_proof(
                        proof_name, data, proof.content_type
                    )
                    uploaded = True
                except Exception:
                    raise HTTPException(
                        502,
                        "Could not securely store the payment screenshot.",
                    )

            c.execute(
                """
                INSERT INTO payments(
                    retailer_id, amount_paise, note, created_by,
                    payment_mode, proof_filename, handover_status
                )
                VALUES(?,?,?,?,?,?, 'pending')
                """,
                (
                    rid,
                    amount_paise,
                    note.strip(),
                    u["id"],
                    mode,
                    proof_name,
                ),
            )

            audit(
                c,
                u,
                "payment_recorded",
                f"retailer={rid};amount={rupees(amount_paise)};"
                f"mode={mode};handover=pending",
            )

            result = {
                "ok": True,
                "outstanding": rupees(balance(c, rid)),
            }

        # The database transaction has committed successfully here.
        return result

    except Exception:
        if uploaded and proof_name:
            try:
                delete_proof(proof_name)
            except Exception:
                # Preserve the original error.
                pass
        raise
@app.get("/api/admin/payment-handovers")
def payment_handovers(req:Request):
 with db_conn() as c:
  role_for(req,c,"admin")
  rows=c.execute("""SELECT p.id,p.retailer_id,r.name retailer_name,p.amount_paise,p.note,p.created_at,p.payment_mode,p.proof_filename,u.username agent_username
   FROM payments p JOIN retailers r ON r.id=p.retailer_id JOIN users u ON u.id=p.created_by
   WHERE p.handover_status='pending' ORDER BY p.id DESC""").fetchall()
  return [{"id":x["id"],"retailer_id":x["retailer_id"],"retailer_name":x["retailer_name"],"amount":rupees(x["amount_paise"]),"note":x["note"],"created_at":x["created_at"],"payment_mode":x["payment_mode"],"proof_available":bool(x["proof_filename"]),"agent_username":x["agent_username"]} for x in rows]


@app.post("/api/admin/payment-handovers/{payment_id}/confirm")
def confirm_handover(payment_id: int, req: Request):
    with db_conn() as c:
        u = role_for(req, c, "admin")

        p = c.execute(
            """
            SELECT id, retailer_id, amount_paise, handover_status
            FROM payments
            WHERE id = ?
            """,
            (payment_id,),
        ).fetchone()

        if not p:
            raise HTTPException(404, "Payment not found.")

        if p["handover_status"] != "pending":
            raise HTTPException(409, "This handover is no longer pending.")

        updated = c.execute(
            """
            UPDATE payments
            SET handover_status = 'received',
                handover_confirmed_by = ?,
                handover_confirmed_at = CURRENT_TIMESTAMP
            WHERE id = ? AND handover_status = 'pending'
            RETURNING id, handover_confirmed_at
            """,
            (u["id"], payment_id),
        ).fetchone()

        if not updated:
            raise HTTPException(409, "This handover was already confirmed.")

        audit(
            c,
            u,
            "payment_handover_confirmed",
            f"payment={payment_id};retailer={p['retailer_id']};"
            f"amount={rupees(p['amount_paise'])}",
        )

        return {
            "ok": True,
            "payment_id": payment_id,
            "handover_status": "received",
            "confirmed_at": updated["handover_confirmed_at"],
        }


@app.get("/api/payments/{payment_id}/proof")
def payment_proof(payment_id: int, req: Request):
    with db_conn() as c:
        u = user_for(req, c)

        p = c.execute(
            """
            SELECT p.proof_filename, p.created_by, r.agent_id
            FROM payments p
            JOIN retailers r ON r.id = p.retailer_id
            WHERE p.id = ?
            """,
            (payment_id,),
        ).fetchone()

        if not p or not p["proof_filename"]:
            raise HTTPException(404, "Payment proof not found.")

        if (
            u["role"] != "admin"
            and p["created_by"] != u["id"]
            and p["agent_id"] != u["id"]
        ):
            raise HTTPException(
                403, "You cannot access this proof."
            )

        filename = p["proof_filename"]

    try:
        data = download_proof(filename)
    except Exception:
        raise HTTPException(
            502, "Unable to retrieve the payment screenshot."
        )

    suffix = Path(filename).suffix.lower()
    media_type = {
        ".jpg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }.get(suffix)

    if not media_type:
        raise HTTPException(415, "Unsupported payment proof format.")

    return Response(
        content=data,
        media_type=media_type,
        headers={
            "Content-Disposition": f'inline; filename="payment-proof{suffix}"',
            "X-Content-Type-Options": "nosniff",
            "Cache-Control": "private, no-store",
        },
    )

@app.get("/api/audit")
def audit_list(req:Request):
 with db_conn() as c:
  role_for(req,c,"admin")
  return [dict(x) for x in c.execute("SELECT a.*,u.username FROM audit_log a JOIN users u ON u.id=a.actor_id ORDER BY a.id DESC LIMIT 100")]
