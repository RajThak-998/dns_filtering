from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from dashboard.db import get_db
from dashboard.schemas import PolicyUpdate

app = FastAPI(title="DNS Admin Dashboard")
templates = Jinja2Templates(directory="dashboard/templates")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM policies")
    policies = cur.fetchall()
    conn.close()

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "policies": policies}
    )

@app.post("/policy")
def update_policy(policy: PolicyUpdate):
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT OR REPLACE INTO policies
        (client_group, category, allowed)
        VALUES (?, ?, ?)
        """,
        (policy.client_group, policy.category, int(policy.allowed))
    )

    conn.commit()
    conn.close()

    return {"status": "updated"}