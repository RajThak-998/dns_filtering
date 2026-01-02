import sqlite3

SOCIAL_MEDIA_DOMAINS = [
    "facebook.com",
    "instagram.com",
    "twitter.com",
    "tiktok.com",
    "snapchat.com",
    "linkedin.com"
]

conn = sqlite3.connect("db/policy.db")
cur = conn.cursor()

for domain in SOCIAL_MEDIA_DOMAINS:
    cur.execute(
        "INSERT OR IGNORE INTO domains (domain, category) VALUES (?, ?)",
        (domain, "social_media")
    )

conn.commit()
conn.close()

print("[+] Social media domains ingested")
