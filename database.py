import sqlite3
from datetime import datetime

conn = sqlite3.connect("data/monitoring.db", check_same_thread=False)
c = conn.cursor()

# Create tables
c.execute("""
CREATE TABLE IF NOT EXISTS urls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT UNIQUE,
    status TEXT,
    monitoring INTEGER DEFAULT 1
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url_id INTEGER,
    timestamp DATETIME,
    status TEXT,
    response_time REAL,
    FOREIGN KEY(url_id) REFERENCES urls(id)
)
""")
conn.commit()

def add_url(url):
    try:
        c.execute("INSERT INTO urls (url, status) VALUES (?, ?)", (url, 'UNKNOWN'))
        conn.commit()
        return True
    except:
        return False

# database.py
def delete_url(url_id):
    c.execute("DELETE FROM urls WHERE id=?", (url_id,))
    c.execute("DELETE FROM history WHERE url_id=?", (url_id,))
    conn.commit()


def get_urls():
    c.execute("SELECT * FROM urls")
    return c.fetchall()

def update_status(url_id, status, response_time):
    c.execute("UPDATE urls SET status=? WHERE id=?", (status, url_id))
    c.execute("INSERT INTO history (url_id, timestamp, status, response_time) VALUES (?, ?, ?, ?)",
              (url_id, datetime.now(), status, response_time))
    conn.commit()

def stop_monitoring(url_id):
    c.execute("UPDATE urls SET monitoring=0 WHERE id=?", (url_id,))
    conn.commit()

def start_monitoring(url_id):
    c.execute("UPDATE urls SET monitoring=1 WHERE id=?", (url_id,))
    conn.commit()

def get_history(url_id):
    c.execute("SELECT timestamp, status, response_time FROM history WHERE url_id=? ORDER BY timestamp DESC", (url_id,))
    return c.fetchall()
