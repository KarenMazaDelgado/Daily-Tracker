# Timer logic and tracking each session
import time, datetime
from db import get_conn

def start_pomodoro(duration_min: int = 25, course: str = None):
    start = datetime.datetime.now()
    try:
        time.sleep(duration_min * 60)
    except KeyboardInterrupt:
        pass
    end = datetime.datetime.now()
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO pomodoros (start_time, end_time, course) VALUES (?,?,?)",
            (start.isoformat(), end.isoformat(), course)
        )
def log_pomodoro(duration, course=None):
    conn = get_conn()
    now   = datetime.datetime.now()
    start = now - datetime.timedelta(minutes=duration)
    conn.execute("""
       INSERT INTO pomodoros (start_time, end_time, duration, course)
            VALUES (?, ?, ?, ?)
    """, (start, now, duration, course))
    conn.commit()
