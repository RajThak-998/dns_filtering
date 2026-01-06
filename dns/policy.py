import sqlite3

DB_PATH = "/app/db/policy.db"
CAT_PATH = "/app/category_db/category.db"


class PolicyEngine:
    def __init__(self, db_path=DB_PATH, cat_path=CAT_PATH):
        self.db_path = db_path
        self.cat_path = cat_path

    def _connect_policy(self):
        return sqlite3.connect(self.db_path)

    def _connect_category(self):
        return sqlite3.connect(self.cat_path)

    def get_client_group(self, client_ip):
        conn = self._connect_policy()
        cur = conn.cursor()

        cur.execute(
            "SELECT client_group FROM clients WHERE ip=?",
            (client_ip,)
        )
        row = cur.fetchone()
        conn.close()

        return row[0] if row else "default"

    def get_domain_category(self, domain):
        # NOTE: category lookup must come from category DB, not policy DB
        conn = self._connect_category()
        cur = conn.cursor()

        # longest suffix match
        parts = domain.rstrip(".").split(".")
        for i in range(len(parts)):
            candidate = ".".join(parts[i:])
            cur.execute(
                "SELECT category FROM domains WHERE domain=?",
                (candidate,)
            )
            row = cur.fetchone()
            if row:
                conn.close()
                return row[0]

        conn.close()
        return "uncategorized"

    def is_allowed(self, client_ip, domain):
        client_group = self.get_client_group(client_ip)
        category = self.get_domain_category(domain)

        if category == "uncategorized":
            return True, category

        conn = self._connect_policy()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT allowed FROM policies
            WHERE client_group=? AND category=?
            """,
            (client_group, category)
        )
        row = cur.fetchone()
        conn.close()

        if row is None:
            return True, category  # default allow

        return bool(row[0]), category
