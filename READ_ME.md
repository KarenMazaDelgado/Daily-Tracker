Author: Karen Maza Delgado :)

# Daily Dashboard

A gamified academic dashboard built with Python, Flask, and SQLite. It lets users track courses, assignments, habits, Pomodoro sessions, all persisted in a local database.

## Prerequisites

* Python 3.7 or higher installed on your machine
* Git installed

## Setup Instructions

1. **Clone the repository**

   git clone https://github.com/YourUser/daily-dashboard.git
   cd daily-dashboard
   

2. **Create and activate a virtual environment**

  
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate

   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate.ps1
  

3. **Install dependencies**

   pip install -r requirements.txt
 

4. **Initialize the database**

   python -c "from db import init_db; init_db()"
  

   This creates `dashboard.db` and all required tables based on `db_schema.sql`.

5. **Run the application**

   # macOS/Linux
   export FLASK_APP=app.py
   flask run

   # Windows (PowerShell)
   set FLASK_APP=app.py
   flask run
   

6. **Open in browser**
   Navigate to http://127.0.0.1:5000 to access the dashboard.

## Project Structure

daily-dashboard/
├── venv/             # Virtual environment (do not edit)
├── dashboard.db      # SQLite database file (auto‑created)
├── db.py             # Database connection & initialization
├── db_schema.sql     # SQL schema for creating tables
├── requirements.txt  # Python dependencies
├── app.py            # Flask application entrypoint
├── analytics.py      # Data‑science helpers (pandas/sklearn)
├── assignments.py    # Assignment CRUD functions
├── pomodoro.py       # Pomodoro timer & logging
├── schedule.py       # Class schedule helper functions
├── templates/        # Jinja2 HTML templates
│    ├── base.html
│    ├── index.html
│    └── new_assignment.html
└── static/           # Static assets (CSS/JS)
    ├── style.css
    └── script.js


## Usage

* **Add a new course**: Click "Add Course" on the homepage, fill out the course code and title.
* **Log assignments**: Go to "Assignments → New" to record upcoming due dates and weights.
* **Track habits**: Navigate to "Habits" to add and log daily habits
* **Start a Pomodoro**: Use the Pomodoro form on the homepage to begin a timed session, which logs automatically.


## Notes

* Your data is stored locally in `dashboard.db` and persists across restarts.
* To reset all data, simply delete `dashboard.db` and re-run the initialization step.

---

