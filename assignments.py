#Python funcs to mainpulate assignments table

from db import get_conn
import datetime

def add_assignment(course_id: int, title: str, due_date: str, weight: float):
    # validate due_date format
    datetime.datetime.strptime(due_date, "%Y-%m-%d")
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO assignments (course_id, title, due_date, weight) VALUES (?,?,?,?)",
            (course_id, title, due_date, weight)
        )

def update_assignment_score(assignment_id: int, score: float):
    """Set the `score` column for one assignment."""
    with get_conn() as conn:
        conn.execute(
            "UPDATE assignments SET score = ? WHERE id = ?",
            (score, assignment_id)
        )
        
def toggle_assignment(assignment_id: int):
    with get_conn() as conn:
        conn.execute("""
            UPDATE assignments
               SET is_done = CASE WHEN is_done = 0 THEN 1 ELSE 0 END
             WHERE id = ?
        """, (assignment_id,))


def delete_assignment(assignment_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM assignments WHERE id = ?", (assignment_id,))
