# todos.py
from db import get_conn

def add_todo(description: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO todos (description) VALUES (?)",
            (description,)
        )

def toggle_todo(todo_id: int):
    with get_conn() as conn:
        # flip 0→1 or 1→0
        conn.execute("""
            UPDATE todos
               SET is_done = CASE WHEN is_done = 0 THEN 1 ELSE 0 END
             WHERE id = ?
        """, (todo_id,))

def get_todos():
    with get_conn() as conn:
        return conn.execute("""
          SELECT id, description, is_done
            FROM todos
           ORDER BY created_at DESC
        """).fetchall()

def delete_todo(todo_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
