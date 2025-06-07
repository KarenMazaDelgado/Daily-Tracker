# habits.py
from db import get_conn
import pandas as pd

def add_habit(name: str, htype: str='boolean') -> int:
    with get_conn() as conn:
        cur = conn.execute("""
            INSERT OR IGNORE INTO habits (name, habit_type)
            VALUES (?, ?)
        """, (name, htype))
        if cur.lastrowid:
            return cur.lastrowid
        row = conn.execute("SELECT id FROM habits WHERE name=?", (name,)).fetchone()
        return row["id"]
    
def get_habits():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, name, habit_type FROM habits"
        ).fetchall()
    # Map the SQL column `habit_type` into a Python dict key `"type"`
    return [
        {"id":   r["id"],
         "name": r["name"],
         "type": r["habit_type"]}
        for r in rows
    ]

def log_habit(habit_id: int, log_date: str, value: float=1.0):
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO habit_logs (habit_id, log_date, value)
            VALUES (?, ?, ?)
        """, (habit_id, log_date, value))

def get_recent_logs(days=14):
    # returns DataFrame for analytics, or list of dicts for template
    df = pd.read_sql_query("""
        SELECT h.name, hl.log_date, hl.value
          FROM habit_logs hl
          JOIN habits h ON hl.habit_id = h.id
         WHERE hl.log_date >= date('now', ?||' days')
         ORDER BY hl.log_date DESC
    """, get_conn(), params=(-days,))
    return df
