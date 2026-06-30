import sqlite3

#creates tables
conn = sqlite3.connect("job_application.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    password TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS roles (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    job_title TEXT,
    company TEXT,
    job_description TEXT,
    resume TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS drafts(
    id INTEGER PRIMARY KEY,
    role_id INTEGER REFERENCES roles(id),
    resume_rewrite TEXT,
    cover_letter TEXT,
    interview_qa TEXT
)
""")


conn.commit()
conn.close()