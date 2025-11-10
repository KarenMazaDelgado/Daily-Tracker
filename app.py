import matplotlib
matplotlib.use("Agg") 

# Standard library
import io

# Third‑party libraries
import matplotlib.pyplot as plt
import pandas as pd
import datetime


from flask import (
    Flask, render_template, request,
    redirect, url_for, send_file,
    flash
)

# Local modules
import analytics           # pandas/sklearn helpers
import assignments         # assignment CRUD
import pomodoro            # Pomodoro timer & logging
import todos  
import courses
import habits
from assignments import update_assignment_score
from db import init_db, get_conn

app = Flask(__name__) # Creates new Flask app and __name__ tells Flask where to look for templates and static files (uses this for modules location)
app.secret_key = "very-secret-key"  

# Initialize the database as soon as this module is loaded
init_db()

@app.route("/", methods=["GET","POST"]) # Registers this function to handle requests to the root URL
def index(): # Defining function for route
    # e.g., fetch courses & assignments to show on dashboard
    with get_conn() as conn: # Opens SQLite connection
        courses = conn.execute("SELECT id, code, title FROM courses").fetchall()  # Runs a SELECT and returns all rows as a listt of Row objects
    
    # Handle adding assingments
    if request.method == "POST" and request.form.get("action") == "add_assignment":
        # read form values
        assignments.add_assignment(
            course_id = int(request.form["course_id"]),
            title     = request.form["title"],
            due_date  = request.form["due_date"],
            weight    = float(request.form["weight"])
        )
        flash("Assignment added.")
        return redirect(url_for("index"))
    
    
    # Handle the new “what‑if” form:
    if request.method == "POST" and request.form.get("action") == "grade_hypo":
        course_id   = int(request.form["course_id"])
        w_hypo      = float(request.form["hypo_weight"])
        s_hypo      = float(request.form["hypo_score"])
        new_grade   = analytics.predict_with_hypothetical(course_id, w_hypo, s_hypo)
        flash(f"With a {s_hypo:.1f}% on a {w_hypo:.1f}% assignment, your final grade would be {new_grade:.1f}%.")
        return redirect(url_for("index"))
    
    #  Add Course
    if request.method == "POST" and request.form.get("action") == "add_course":
        code  = request.form["code"].strip()
        title = request.form["title"].strip()
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO courses (code, title) VALUES (?, ?)",
                (code, title)
            )
        flash(f"Course {code} added.")
        return redirect(url_for("index"))


    # on GET (or after redirect), render the dashboard
    todos_items       = todos.get_todos()            
    pomodoros   = analytics.load_pomodoro_data()

    # Handle table info for courses, to-do list, and upcoming assignments
    # 1) Courses & current final grade
    with get_conn() as conn:
        courses = conn.execute("SELECT id, code, title FROM courses").fetchall()
    courses_with_grades = []
    for c in courses:
        grade = analytics.actual_final_grade(c["id"])
        courses_with_grades.append({
            "id":    c["id"],
            "code":  c["code"],
            "title": c["title"],
            "grade": f"{grade:.1f}%"
        })

    # 2) To‑Do items
    if request.method == "POST" and request.form.get("description"):
        todos.add_todo(request.form["description"])
        return redirect(url_for("index"))
    todo_items = todos.get_todos()  # each has id, description, is_done

    # 3) Upcoming assignments, sorted by due_date then course
    with get_conn() as conn:
        raw = conn.execute("""
            SELECT a.id, c.code, a.title, a.due_date, a.is_done
              FROM assignments a
              JOIN courses c ON a.course_id = c.id
             ORDER BY a.due_date, c.code
        """).fetchall()
    upcoming = [
        {  "id":       r["id"],
            "course": r["code"],
          "title":r["title"],
          "due_date": r["due_date"],
          "is_done":  bool(r["is_done"])
          
          
          }
        for r in raw
    ]

    # Add Habit
   
    if request.method=="POST" and request.form.get("action")=="add_habit":
        name  = request.form["habit_name"].strip()
        htype = request.form["habit_type"]            # read the dropdown
        habits.add_habit(name, htype)                  # create with correct type
        flash(f"Habit '{name}' ({htype}) started.")
        return redirect(url_for("index"))

    # 2) Log a habit occurrence (with optional value)
    if request.method=="POST" and request.form.get("action")=="log_habit":
        # 1) Check if user typed a brand‑new habit
        new_name = request.form.get("new_habit","").strip()
        if new_name:
            # create it and grab its new id
            new_type = request.form.get("habit_type","boolean")
            habit_id = habits.add_habit(new_name, new_type)
        else:
            # else parse the dropdown (might be blank)
            habit_id = int(request.form["habit_id"])

        # 2) Now log the habit
        log_date = request.form["log_date"]
        value    = float(request.form.get("value", 1))
        habits.log_habit(habit_id, log_date, value)
        flash("Habit logged.")
        return redirect(url_for("index"))
    
    all_habits  = habits.get_habits()             # list of {"id","name"}
    recent_logs = habits.get_recent_logs(days=30)
    today = datetime.date.today().isoformat()


    return render_template("index.html", courses=courses_with_grades,todos=todos_items,
                           pomodoros=pomodoros,upcoming=upcoming, habits = all_habits,habit_logs=recent_logs,today=today) # Looks in index.html and passes it the courses list, returns rendered HTML

# Analytics page
@app.route("/analytics")
def analytics_view():
    # Read optional ?days=… as before
    try:
        days = int(request.args.get("days", 30))
    except ValueError:
        days = 30 
        
    #Calculate and fetch grades for the analytics page
    with get_conn() as conn:
        courses = conn.execute("SELECT id, code, title FROM courses").fetchall()
    
    courses_with_grades = []
    for c in courses:
        # The analytics.actual_final_grade function is perfect for this
        grade = analytics.actual_final_grade(c["id"]) 
        courses_with_grades.append({
            "id": c["id"],
            "code": c["code"],
            "title": c["title"],
            # Store the raw float grade for now; format in HTML
            "grade": grade 
        })

    # FETCH the habit types
    all_habits = habits.get_habits()   # returns list of {"id","name"}

    # Pull whatever data you need, e.g. summaries or chart URLs
    return render_template("analytics.html",days=days,all_habits=all_habits)


# Assignment form handler
@app.route("/assignments/new", methods=["GET","POST"]) # Handles GET(shows blank form) and POST (when user submits form)
def new_assignment():
    conn    = get_conn()
    courses = conn.execute("SELECT id, code, title FROM courses").fetchall()
    if request.method == "POST": 
        assignments.add_assignment( # Pass parsed form values
            course_id=int(request.form["course_id"]), # request.form is a dict-like object containing the form fields by name
            title=request.form["title"],
            due_date=request.form["due_date"],
            weight=float(request.form["weight"])
        )
        return redirect(url_for("index")) # Redirect so user sees updated list
    return render_template("new_assignment.html", courses=courses)  # On GET return HTML form template (new_assignment.html) so user can fill it out 


# Edit assingment with grade

@app.route("/assignments/edit", methods=["POST"])
def edit_assignment_route():
    assignment_id = int(request.form["assignment_id"])
    score         = float(request.form["score"])
    update_assignment_score(assignment_id, score)
    flash("Score updated.")
    return redirect(url_for("index"))


#Habit plot

# Boolean habits chart (bar chart, 0 for missing)
@app.route("/plots/habits_boolean")
def habit_chart_boolean():
    days = int(request.args.get("days", 30) or 30)
    interval = f"-{days} days"
    df = pd.read_sql_query(f"""
        SELECT hl.log_date, h.name, hl.value
          FROM habit_logs hl
          JOIN habits      h  ON hl.habit_id = h.id
         WHERE h.habit_type = 'boolean'
           AND hl.log_date >= date('now','{interval}')
    """, get_conn())

    if df.empty:
        fig, ax = plt.subplots()
        ax.set_title(f"Daily Yes/No Habits (last {days}d)")
        ax.text(0.5, 0.5, "No habit logs yet", ha="center", va="center", transform=ax.transAxes, color="gray")
    else:
        # pivot, fill missing as 0, bar chart
        pivot = df.pivot(index="log_date", columns="name", values="value").fillna(0)
        fig, ax = plt.subplots()
        pivot.plot(kind="bar", ax=ax)
        ax.set_title(f"Daily Yes/No Habits (last {days}d)")
        ax.set_xlabel("Date")
        ax.set_ylabel("Done (1) or Not (0)")

    buf = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png")
    buf.seek(0)
    plt.close(fig)
    return send_file(buf, mimetype="image/png")


# Numeric habits chart (line chart, only plots when values exist)
@app.route("/plots/habits_numeric")
def habit_chart_numeric():
    days = int(request.args.get("days", 30) or 30)
    interval = f"-{days} days"
    df = pd.read_sql_query(f"""
        SELECT hl.log_date, h.name, hl.value
          FROM habit_logs hl
          JOIN habits      h  ON hl.habit_id = h.id
         WHERE h.habit_type = 'numeric'
           AND hl.log_date >= date('now','{interval}')
    """, get_conn())
    if df.empty:
        fig, ax = plt.subplots()
        ax.set_title(f"Numeric Habit Values (last {days}d)")
        ax.text(0.5,0.5,"No habit logs yet",ha="center",va="center",transform=ax.transAxes,color="gray")
    else:
        pivot = df.pivot(index="log_date", columns="name", values="value")
        fig, ax = plt.subplots()
        pivot.plot(ax=ax, marker="o")
        ax.set_title(f"Numeric Habit Values (last {days}d)")
        ax.set_xlabel("Date")
        ax.set_ylabel("Value")

    buf = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png")
    buf.seek(0)
    plt.close(fig)
    return send_file(buf, mimetype="image/png")


# Pomodoro plot for weekly totals
@app.route("/plots/pomodoro")
def pomodoro_chart():
    # Load and prepare data
    df = analytics.load_pomodoro_data()
    # Ensure the column is datetime
    df["start_time"] = pd.to_datetime(df["start_time"])
    # Index by start_time and group by week
    weekly = df.set_index("start_time").resample("W").size()

    fig, ax = plt.subplots()
    if weekly.empty:
        # Draw an empty chart with axis labels and a message
        ax.set_title("Pomodoros per Week")
        ax.set_xlabel("Week")
        ax.set_ylabel("Sessions")
        # Create a single tick at zero so you see the axis
        ax.set_xticks([0])
        ax.set_xticklabels(["—"])
        ax.set_yticks([0])
        ax.annotate(
            "No data yet",
            xy=(0, 0), xycoords="data",
            xytext=(0.5, 0.5), textcoords="axes fraction",
            ha="center", va="center",
            fontsize=12, color="gray"
        )
    else:
        weekly.plot(ax=ax)
        ax.set_title("Pomodoros per Week")
        ax.set_xlabel("Week")
        ax.set_ylabel("Sessions")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)
    return send_file(buf, mimetype="image/png")

@app.route("/pomodoro", methods=["POST"])
def start_pomodoro():
    # pull duration & optional course out of the form
    duration = int(request.form.get("duration", 25))
    course   = request.form.get("course") or None
    # log the session
    pomodoro.log_pomodoro(duration, course)
    # back to home
    return redirect(url_for("index"))


@app.route("/grade-predict", methods=["POST"])
def grade_predict():
    course_id       = int(request.form["course_id"])
    projected_score = float(request.form.get("projected_score", 0))
    prediction = analytics.predict_final_grade(course_id, projected_score)
    flash(f"Predicted final grade: {prediction:.1f}%")
    return redirect(url_for("index"))



@app.route("/todos", methods=["GET","POST"])
def todo_list():
    # on POST, add a new task
    if request.method == "POST":
        todos.add_todo(request.form["description"])
        return redirect(url_for("todo_list"))

    # on GET, fetch and show
    items = todos.get_todos()
    return render_template("todos.html", todos=items)

@app.route("/todos/toggle/<int:todo_id>")
def todo_toggle(todo_id):
    todos.toggle_todo(todo_id)
    return redirect(url_for("todo_list"))


# Complete/ Incomplete toggles
@app.route("/toggle/todo/<int:todo_id>", methods=["POST"])
def toggle_todo_route(todo_id):
    todos.toggle_todo(todo_id)
    return redirect(url_for("index"))

@app.route("/toggle/assignment/<int:assignment_id>", methods=["POST"])
def toggle_assignment_route(assignment_id):
    assignments.toggle_assignment(assignment_id)
    return redirect(url_for("index"))



# Deleting from tables

@app.route("/delete/todo/<int:todo_id>", methods=["POST"])
def delete_todo_route(todo_id):
    todos.delete_todo(todo_id)
    flash("To‑Do item removed.")
    return redirect(url_for("index"))

@app.route("/delete/assignment/<int:assignment_id>", methods=["POST"])
def delete_assignment_route(assignment_id):
    assignments.delete_assignment(assignment_id)
    flash("Assignment deleted.")
    return redirect(url_for("index"))

@app.route("/delete/course/<int:course_id>", methods=["POST"])
def delete_course_route(course_id):
    courses.delete_course(course_id)
    flash("Course removed.")
    return redirect(url_for("index"))

if __name__ == "__main__": # This block lets us start the servery by running python app.py
    app.run(debug=True) # turns on auto-reload (restarts the server on code changes)
