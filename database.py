
import sqlite3
from datetime import datetime

DB_NAME = "task_history.db"


def initialize_database():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            result TEXT,
            status TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_task(task, result, status):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO tasks
        (task, result, status, created_at)
        VALUES (?, ?, ?, ?)
    """, (
        task,
        result,
        status,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


def get_task_history():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, task, status, created_at
        FROM tasks
        ORDER BY id DESC
    """)

    records = cursor.fetchall()

    conn.close()

    return records


def get_task_result(task_id):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT task, result, status, created_at
        FROM tasks
        WHERE id = ?
    """, (task_id,))

    record = cursor.fetchone()

    conn.close()

    return record
