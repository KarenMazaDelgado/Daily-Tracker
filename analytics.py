#Analytics 

import pandas as pd
from db import get_conn

def load_pomodoro_data():
    df = pd.read_sql("SELECT * FROM pomodoros", get_conn())
    df["start_time"] = pd.to_datetime(df["start_time"])
    df["end_time"]   = pd.to_datetime(df["end_time"])
    return df


def predict_with_hypothetical(course_id: int, hypo_weight: float, hypo_score: float) -> float:
    """
    Compute final grade if the user scores `hypo_score` on
    a new assignment worth `hypo_weight` percent of the total course.
    """
    # Load only graded assignments:
    df = pd.read_sql_query(
        "SELECT weight, score FROM assignments WHERE course_id = ? AND score IS NOT NULL",
        get_conn(), params=(course_id,)
    )

    # Sum of weights & points for graded work
    W9 = df["weight"].sum()
    P9 = (df["weight"] * df["score"]).sum()

    # Total course weight after adding this hypothetical
    Gt = W9 + hypo_weight

    if Gt == 0:
        return 0.0

    # Total “points” after including hypothetical
    P_total = P9 + (hypo_weight * hypo_score)

    # Final % grade
    return P_total / Gt


def actual_final_grade(course_id: int) -> float:
    """
    Compute the current grade for a course based only on assignments
    that have a non-null score.
    Returns a percentage 0.0–100.0. If there are no graded assignments,
    returns 100.0.
    """
    import pandas as pd
    from db import get_conn

    df = pd.read_sql_query(
        """
        SELECT weight, score
          FROM assignments
         WHERE course_id = ? AND score IS NOT NULL
        """,
        get_conn(),
        params=(course_id,)
    )

    # *** Changed here ***
    if df.empty:
        return 100.0

    total_weighted = (df["weight"] * df["score"]).sum()
    total_weight   = df["weight"].sum()

    # Avoid DivisionByZero (shouldn't happen since df not empty)
    if total_weight == 0:
        return 100.0

    return float(total_weighted / total_weight)


def actual_final_grade(course_id: int) -> float:
    """
    Compute the current grade for a course based only on assignments
    that have a non-null score.
    Returns a percentage 0.0 to 100.0.
    """
    # Load graded assignments
    df = pd.read_sql_query(
        """
        SELECT weight, score
          FROM assignments
         WHERE course_id = ? AND score IS NOT NULL
        """,
        get_conn(),
        params=(course_id,)
    )

    if df.empty:
        return 100.0

    # Weighted average: sum(weight*score) / sum(weight)
    total_weighted = (df["weight"] * df["score"]).sum()
    total_weight   = df["weight"].sum()

    # Avoid DivisionByZero (shouldn't happen since df not empty)
    if total_weight == 0:
        return 100.0


    return float(total_weighted / total_weight)