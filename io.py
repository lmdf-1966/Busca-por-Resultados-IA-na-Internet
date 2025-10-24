
import os, sqlite3, pathlib, hashlib, datetime
from typing import Optional, Iterable, Tuple

DATA_DIR = pathlib.Path(__file__).resolve().parents[1] / "data"
OUT_DIR = pathlib.Path(__file__).resolve().parents[1] / "out"
LOG_DIR = pathlib.Path(__file__).resolve().parents[1] / "logs"
for d in (DATA_DIR, OUT_DIR, LOG_DIR):
    d.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "ia_digest.db"

def db() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH)
    con.execute("""CREATE TABLE IF NOT EXISTS items (
        id TEXT PRIMARY KEY,
        source TEXT,
        title TEXT,
        url TEXT,
        published TEXT,
        content TEXT,
        measurable INTEGER,
        value_signals TEXT,
        created_at TEXT
    )""")
    con.execute("CREATE INDEX IF NOT EXISTS idx_items_published ON items(published)")
    return con

def url_id(url: str) -> str:
    return hashlib.sha1(url.encode("utf-8")).hexdigest()

def upsert_item(conn: sqlite3.Connection, *, source:str, title:str, url:str, published:str,
                content:str, measurable:int, value_signals:str) -> bool:
    _id = url_id(url)
    now = datetime.datetime.utcnow().isoformat()
    conn.execute("""INSERT OR REPLACE INTO items
        (id, source, title, url, published, content, measurable, value_signals, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (_id, source, title, url, published, content, measurable, value_signals, now))
    conn.commit()
    return True

def fetch_recent(conn: sqlite3.Connection, days:int=3) -> Iterable[Tuple]:
    since = (datetime.datetime.utcnow() - datetime.timedelta(days=days)).isoformat()
    cur = conn.execute("""SELECT source, title, url, published, measurable, value_signals
                          FROM items WHERE created_at >= ? ORDER BY published DESC""", (since,))
    return cur.fetchall()
