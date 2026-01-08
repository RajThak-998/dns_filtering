from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from dashboard.db import *
from dashboard.schemas import PolicyUpdate

app = FastAPI(title="DNS Admin Dashboard")
templates = Jinja2Templates(directory="dashboard/templates")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    conn = get_db()
    cur = conn.cursor()

    conn_cat = get_cat_db()
    cur_cat = conn_cat.cursor()

    # Get all policies
    cur.execute("SELECT client_group, category, allowed FROM policies")
    policies = cur.fetchall()

    # Get all unique client groups
    cur.execute("SELECT DISTINCT client_group FROM policies")
    policy_groups = [row[0] for row in cur.fetchall()]

    cur.execute("SELECT DISTINCT client_group FROM clients")
    client_groups = [row[0] for row in cur.fetchall()]

    # Combine and deduplicate groups
    all_groups = list(set(policy_groups + client_groups + ["default"]))

    # Get all clients
    cur.execute("SELECT ip, client_group FROM clients")
    clients = cur.fetchall()

    # Get all categories from category database
    cur_cat.execute("SELECT DISTINCT category FROM domains")
    categories = [row[0] for row in cur_cat.fetchall()]

    conn.close()
    conn_cat.close()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "policies": policies,
            "clients": clients,
            "client_groups": all_groups,
            "categories": categories
        }
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