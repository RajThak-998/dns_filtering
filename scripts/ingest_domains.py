import sqlite3

# SOCIAL_MEDIA_DOMAINS = [
#     "facebook.com",
#     "instagram.com",
#     "twitter.com",
#     "tiktok.com",
#     "snapchat.com",
#     "linkedin.com"
# ]

social_media = [
    "bluesky.com",
    "facebook.com",
    "instagram.com",
    "linkedin.com",
    "mailru.com",
    "misskey.com",
    "ok.com",
    "threads.com",
    "twitter.com",
    "vk.com",
    "truthsocial.com",
]

conn = sqlite3.connect("category_db/category.db")
cur = conn.cursor()

for domain in social_media:
    cur.execute(
        "INSERT OR IGNORE INTO domains (domain, category) VALUES (?, ?)",
        (domain, "social_media")
    )

conn.commit()
conn.close()

print("[+] Social media domains ingested")
