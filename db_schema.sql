-- Where all tables and columns are defined in plain SQL
--php-template <column_name>  <data_type>  <optional constraints>
--primary key is unique and not null and is tables main identifier

-- courses table
CREATE TABLE IF NOT EXISTS courses (
  id    INTEGER PRIMARY KEY,
  code  TEXT    UNIQUE NOT NULL,
  title TEXT    NOT NULL
);

-- assignments table
CREATE TABLE IF NOT EXISTS assignments (
  id         INTEGER PRIMARY KEY,
  course_id  INTEGER NOT NULL REFERENCES courses(id),
  title      TEXT    NOT NULL,
  due_date   DATE    NOT NULL,
  weight     REAL    NOT NULL,
  score      REAL, 
  is_done     INTEGER NOT NULL DEFAULT 0    -- 0 = not done, 1 = done
);

-- habits table
CREATE TABLE IF NOT EXISTS habits (
  id   INTEGER PRIMARY KEY,
  name TEXT    UNIQUE NOT NULL,
  habit_type  TEXT    NOT NULL CHECK(habit_type IN ('boolean','numeric')) DEFAULT 'boolean'
  
);

-- habit_logs table
CREATE TABLE IF NOT EXISTS habit_logs (
  id       INTEGER PRIMARY KEY,
  habit_id INTEGER NOT NULL REFERENCES habits(id),
  log_date DATE    NOT NULL,
  value     REAL    NOT NULL DEFAULT 1
);

-- pomodoros table
CREATE TABLE IF NOT EXISTS pomodoros (
  id         INTEGER PRIMARY KEY,
  start_time DATETIME NOT NULL,
  end_time   DATETIME NOT NULL,
  duration   INTEGER NOT NULL, 
  course     TEXT
);

-- screen_time table
CREATE TABLE IF NOT EXISTS screen_time (
  id         INTEGER PRIMARY KEY,
  start_time DATETIME NOT NULL,
  end_time   DATETIME NOT NULL,
  category   TEXT    CHECK(category IN ('focused','break')) NOT NULL
);

-- daily prompts table
CREATE TABLE IF NOT EXISTS prompts (
  id         INTEGER PRIMARY KEY,
  entry_date DATE    UNIQUE NOT NULL,
  prompt1    TEXT,
  prompt2    TEXT,
  prompt3    TEXT
);

-- todos table
CREATE TABLE IF NOT EXISTS todos (
  id           INTEGER PRIMARY KEY,
  description  TEXT    NOT NULL,
  created_at   DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  is_done      INTEGER NOT NULL DEFAULT 0   -- 0 = not done, 1 = done
);

