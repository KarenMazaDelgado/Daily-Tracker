import sqlite3 # Python’s built‑in library for talking to SQLite databases
from pathlib import Path #npath is from the standard pathlib module. It makes file paths easier to work with across different operating systems
             
#__file__ is the path to this very dp.py, and .parent is its containing folder(project root)
DB_PATH = Path(__file__).parent / "dashboard.db" # DB_PATH holds a Path object pointing to <project‑root>/dashboard.db.

def get_conn():
    """Open a connection to dashboard.db with row access by column name."""
    conn = sqlite3.connect(DB_PATH) # creates dashboard.db is it doesn't exist and returns a connection object used to run queries
    conn.row_factory = sqlite3.Row # setting row_factory to row make each row behave like a dict, so we can do row["column_name"] instead of row[0].
    return conn

def init_db():
    """Create tables from db_schema.sql if they don’t exist yet."""
    schema_file = Path(__file__).parent / "db_schema.sql" # locating SQL script, schema_file is <project‑root>/db_schema.sql
    with get_conn() as conn, open(schema_file) as f:  # "with get_conn() as conn opens database connection and ensures its closed automatically at the end of block and commits changes, "open(schema_file) as f" reads raw SQL text
        conn.executescript(f.read()) # executes db.schema.sql as one batch
 