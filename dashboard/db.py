import sqlite3

DB_PATH = "/app/db/policy.db"
CAT_PATH = "/app/category_db/category.db"

def get_db():
    return sqlite3.connect(DB_PATH)

def get_cat_db():
    return sqlite3.coonect(CAT_PATH)