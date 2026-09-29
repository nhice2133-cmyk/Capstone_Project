"""
SMART ENTRY — Database Layer
Handles SQLite schema creation and all CRUD operations.
Tables: students, attendance_logs, security_alerts, admins
"""
import sqlite3
import os
from datetime import datetime
from config import Config


def get_db_connection():
    """Return a sqlite3 connection with row_factory set to Row."""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create tables if they do not already exist."""
    os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
    conn = get_db_connection()
    c = conn.cursor()

    # ── Students (enrolled users) ─────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name   TEXT    NOT NULL,
            student_id  TEXT    NOT NULL UNIQUE,
            program     TEXT    NOT NULL,
            status      TEXT    NOT NULL DEFAULT 'active',
            enrolled_at TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
        )
    """)

    # ── Attendance Logs ───────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS attendance_logs (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            student_db_id  INTEGER NOT NULL REFERENCES students(id),
            date           TEXT    NOT NULL,
            time_in        TEXT    NOT NULL,
            time_out       TEXT,
            visit_purpose  TEXT,
            node           TEXT    NOT NULL DEFAULT 'entry'
        )
    """)

    # ── Security Alerts ───────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS security_alerts (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            detected_at     TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
            snapshot_path   TEXT,
            confidence_score REAL,
            resolved        INTEGER NOT NULL DEFAULT 0
        )
    """)

    # ── Admins ────────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT    NOT NULL UNIQUE,
            password_hash TEXT    NOT NULL,
            created_at    TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
        )
    """)

    conn.commit()
    conn.close()


# ══════════════════════════════════════════════════════════════════════════════
# Student CRUD
# ══════════════════════════════════════════════════════════════════════════════

def create_student(full_name: str, student_id: str, program: str) -> int:
    """Insert a new student. Returns the new row id."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO students (full_name, student_id, program) VALUES (?, ?, ?)",
        (full_name, student_id, program),
    )
    conn.commit()
    new_id = c.lastrowid
    conn.close()
    return new_id


def get_all_students():
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT * FROM students ORDER BY full_name ASC"
    ).fetchall()
    conn.close()
    return rows


def get_student_by_db_id(db_id: int):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM students WHERE id = ?", (db_id,)).fetchone()
    conn.close()
    return row


def get_student_by_student_id(student_id: str):
    conn = get_db_connection()
    row = conn.execute(
        "SELECT * FROM students WHERE student_id = ?", (student_id,)
    ).fetchone()
    conn.close()
    return row


def update_student_status(db_id: int, status: str):
    conn = get_db_connection()
    conn.execute("UPDATE students SET status = ? WHERE id = ?", (status, db_id))
    conn.commit()
    conn.close()


def delete_student(db_id: int):
    conn = get_db_connection()
    conn.execute("DELETE FROM students WHERE id = ?", (db_id,))
    conn.commit()
    conn.close()


def count_students() -> int:
    conn = get_db_connection()
    n = conn.execute("SELECT COUNT(*) FROM students WHERE status = 'active'").fetchone()[0]
    conn.close()
    return n


# ══════════════════════════════════════════════════════════════════════════════
# Attendance CRUD
# ══════════════════════════════════════════════════════════════════════════════

def log_time_in(student_db_id: int, visit_purpose: str, node: str = "entry") -> int:
    """Create a new attendance record (Time In). Returns new record id."""
    now = datetime.now()
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        """INSERT INTO attendance_logs (student_db_id, date, time_in, visit_purpose, node)
           VALUES (?, ?, ?, ?, ?)""",
        (student_db_id, now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"),
         visit_purpose, node),
    )
    conn.commit()
    new_id = c.lastrowid
    conn.close()
    return new_id


def log_time_out(student_db_id: int) -> bool:
    """
    Update the most recent open (time_out IS NULL) attendance record for
    the given student with the current timestamp. Returns True if updated.
    """
    now = datetime.now()
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        """UPDATE attendance_logs
           SET time_out = ?
           WHERE student_db_id = ?
             AND time_out IS NULL
             AND id = (
                 SELECT id FROM attendance_logs
                 WHERE student_db_id = ? AND time_out IS NULL
                 ORDER BY id DESC LIMIT 1
             )""",
        (now.strftime("%H:%M:%S"), student_db_id, student_db_id),
    )
    conn.commit()
    updated = c.rowcount > 0
    conn.close()
    return updated


def get_attendance_logs(date_from: str = None, date_to: str = None,
                        program: str = None, purpose: str = None,
                        search: str = None, limit: int = 500):
    """Fetch filtered attendance logs joined with student info."""
    conn = get_db_connection()
    query = """
        SELECT al.id, s.full_name, s.student_id, s.program,
               al.date, al.time_in, al.time_out, al.visit_purpose, al.node
        FROM attendance_logs al
        JOIN students s ON al.student_db_id = s.id
        WHERE 1=1
    """
    params = []
    if date_from:
        query += " AND al.date >= ?"
        params.append(date_from)
    if date_to:
        query += " AND al.date <= ?"
        params.append(date_to)
    if program:
        query += " AND s.program = ?"
        params.append(program)
    if purpose:
        query += " AND al.visit_purpose = ?"
        params.append(purpose)
    if search:
        query += " AND (s.full_name LIKE ? OR s.student_id LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    query += " ORDER BY al.id DESC LIMIT ?"
    params.append(limit)
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows


def get_todays_visitor_count() -> int:
    today = datetime.now().strftime("%Y-%m-%d")
    conn = get_db_connection()
    n = conn.execute(
        "SELECT COUNT(*) FROM attendance_logs WHERE date = ?", (today,)
    ).fetchone()[0]
    conn.close()
    return n


def get_currently_inside_count() -> int:
    today = datetime.now().strftime("%Y-%m-%d")
    conn = get_db_connection()
    n = conn.execute(
        "SELECT COUNT(*) FROM attendance_logs WHERE date = ? AND time_out IS NULL",
        (today,),
    ).fetchone()[0]
    conn.close()
    return n


def get_hourly_traffic(date: str = None):
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    conn = get_db_connection()
    rows = conn.execute(
        """SELECT strftime('%H', time_in) AS hour, COUNT(*) AS count
           FROM attendance_logs
           WHERE date = ?
           GROUP BY hour ORDER BY hour""",
        (date,),
    ).fetchall()
    conn.close()
    return rows


def get_purpose_breakdown(date_from: str = None, date_to: str = None):
    conn = get_db_connection()
    query = """
        SELECT visit_purpose, COUNT(*) AS count
        FROM attendance_logs
        WHERE visit_purpose IS NOT NULL
    """
    params = []
    if date_from:
        query += " AND date >= ?"
        params.append(date_from)
    if date_to:
        query += " AND date <= ?"
        params.append(date_to)
    query += " GROUP BY visit_purpose"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows


def get_recent_logs(limit: int = 10):
    conn = get_db_connection()
    rows = conn.execute(
        """SELECT al.id, s.full_name, s.program, al.date, al.time_in,
                  al.time_out, al.visit_purpose
           FROM attendance_logs al
           JOIN students s ON al.student_db_id = s.id
           ORDER BY al.id DESC LIMIT ?""",
        (limit,),
    ).fetchall()
    conn.close()
    return rows


# ══════════════════════════════════════════════════════════════════════════════
# Security Alerts CRUD
# ══════════════════════════════════════════════════════════════════════════════

def log_alert(snapshot_path: str = None, confidence_score: float = None) -> int:
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        """INSERT INTO security_alerts (snapshot_path, confidence_score)
           VALUES (?, ?)""",
        (snapshot_path, confidence_score),
    )
    conn.commit()
    new_id = c.lastrowid
    conn.close()
    return new_id


def get_alerts(resolved: int = None, limit: int = 200):
    conn = get_db_connection()
    query = "SELECT * FROM security_alerts WHERE 1=1"
    params = []
    if resolved is not None:
        query += " AND resolved = ?"
        params.append(resolved)
    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows


def resolve_alert(alert_id: int):
    conn = get_db_connection()
    conn.execute("UPDATE security_alerts SET resolved = 1 WHERE id = ?", (alert_id,))
    conn.commit()
    conn.close()


def resolve_all_alerts():
    conn = get_db_connection()
    conn.execute("UPDATE security_alerts SET resolved = 1 WHERE resolved = 0")
    conn.commit()
    conn.close()


def delete_alert(alert_id: int):
    """Delete a single alert and return its snapshot path for file deletion."""
    conn = get_db_connection()
    row = conn.execute("SELECT snapshot_path FROM security_alerts WHERE id = ?", (alert_id,)).fetchone()
    conn.execute("DELETE FROM security_alerts WHERE id = ?", (alert_id,))
    conn.commit()
    conn.close()
    return row["snapshot_path"] if row else None


def delete_all_resolved_alerts():
    """Delete all resolved alerts and return their snapshot paths for file deletion."""
    conn = get_db_connection()
    rows = conn.execute("SELECT snapshot_path FROM security_alerts WHERE resolved = 1 AND snapshot_path IS NOT NULL").fetchall()
    conn.execute("DELETE FROM security_alerts WHERE resolved = 1")
    conn.commit()
    conn.close()
    return [row["snapshot_path"] for row in rows]


def count_unresolved_alerts() -> int:
    conn = get_db_connection()
    n = conn.execute(
        "SELECT COUNT(*) FROM security_alerts WHERE resolved = 0"
    ).fetchone()[0]
    conn.close()
    return n


# ══════════════════════════════════════════════════════════════════════════════
# Admins CRUD
# ══════════════════════════════════════════════════════════════════════════════

def get_admin_by_username(username: str):
    conn = get_db_connection()
    row = conn.execute(
        "SELECT * FROM admins WHERE username = ?", (username,)
    ).fetchone()
    conn.close()
    return row


def create_admin(username: str, password_hash: str):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO admins (username, password_hash) VALUES (?, ?)",
        (username, password_hash),
    )
    conn.commit()
    conn.close()

# ══════════════════════════════════════════════════════════════════════════════
# System Maintenance
# ══════════════════════════════════════════════════════════════════════════════

def factory_reset():
    """Wipe all system data EXCEPT the admins table. Useful for testing."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM attendance_logs")
    c.execute("DELETE FROM security_alerts")
    c.execute("DELETE FROM students")
    
    # Reset auto-increment counters
    c.execute("DELETE FROM sqlite_sequence WHERE name IN ('attendance_logs', 'security_alerts', 'students')")
    
    conn.commit()
    conn.close()
