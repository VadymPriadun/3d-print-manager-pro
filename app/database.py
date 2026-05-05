import os
import sqlite3
from pathlib import Path

# Налаштування шляхів
USER_DIR = os.path.join(str(Path.home()), "Documents", "3D_Print_Manager")
os.makedirs(USER_DIR, exist_ok=True) 

DB = os.path.join(USER_DIR, "3d_print.db")

def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client TEXT,
        model TEXT,
        weight REAL,
        plastic TEXT,
        deadline TEXT,
        status TEXT,
        cost REAL
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS plastic (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        color TEXT,
        stock REAL,
        price REAL
    )
    """)
    
    try:
        cur.execute("ALTER TABLE orders ADD COLUMN receipt_path TEXT")
    except sqlite3.OperationalError:
        pass 
        
    conn.commit()
    conn.close()