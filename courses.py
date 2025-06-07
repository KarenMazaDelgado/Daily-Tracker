from db import get_conn

def delete_course(course_id: int):
    with get_conn() as conn:
        # if you want to cascade-deletes, you could also delete assignments first
        conn.execute("DELETE FROM courses WHERE id = ?", (course_id,))
