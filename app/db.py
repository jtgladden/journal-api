import os
import sqlite3
from datetime import date, datetime, timezone

PATH = os.environ.get("JOURNAL_DB", "journal_entries.db")

def get_conn():
    conn = sqlite3.connect(PATH)
    conn.row_factory = sqlite3.Row
    return conn

    
def init_journal_store():
    conn = get_conn()
    try:
        with conn:   
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS journal_entries (
                    id INTEGER PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    entry_date TEXT NOT NULL,
                    entry_type TEXT NOT NULL CHECK (entry_type IN ('journal', 'study')),
                    content TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE (user_id, entry_date, entry_type)
                )
            """)
    finally:
        conn.close()

def get_entry(user_id, entry_date, entry_type):
    conn = get_conn()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM journal_entries WHERE user_id = ? AND entry_date = ? AND entry_type = ?",
                (user_id, entry_date, entry_type)
            )
            entry = cursor.fetchone()
            if entry is None:
                return None
            else:
                return dict(entry)
    finally:
        conn.close()

def upsert_entry(user_id, entry_date, entry_type, content):
    conn = get_conn()
    now = datetime.now(timezone.utc).isoformat()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO journal_entries (user_id, entry_date, entry_type, content, created_at, updated_at)
                VALUES (?, ?, ?, ? ,? ,?)
                ON CONFLICT (user_id, entry_date, entry_type)
                DO UPDATE SET
                    content = excluded.content,
                    updated_at = excluded.updated_at
                RETURNING *
            """,
                           (user_id, entry_date, entry_type, content, now, now))
            row = cursor.fetchone()
            return dict(row) 
    finally:
        conn.close()
        
def list_entries(user_id, start = None, end = None, entry_type = None):
    conn = get_conn()

    sql = "SELECT * FROM journal_entries WHERE user_id = ?"
    params = [user_id]

    try:
        cursor = conn.cursor()

        if start is not None:
            sql += " AND entry_date >= ?"
            params.append(start)
        if end is not None:
            sql += " AND entry_date <= ?"
            params.append(end)
        if entry_type is not None:
            sql += " AND entry_type = ?"
            params.append(entry_type)

        sql += " ORDER BY entry_date ASC, entry_type ASC;"

        cursor.execute(sql, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

#
# init_journal_store()
# upsert_entry('jar', date.today().isoformat(), 'journal', "This is test 1")
# print(str(get_entry('jar', date.today().isoformat(), 'journal')))
# upsert_entry('jar', date.today().isoformat(), 'journal', "This is test 2")
# print(str(get_entry('jar', date.today().isoformat(), 'journal')))







