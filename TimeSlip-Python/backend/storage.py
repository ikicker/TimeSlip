# -*- coding: utf-8 -*-
"""SQLite storage for TimeSlip sessions and settings."""
from __future__ import print_function

import json
import os
import sqlite3
import uuid
from datetime import datetime


def support_dir():
    home = os.path.expanduser("~")
    path = os.path.join(home, "Library", "Application Support", "TimeSlip")
    if not os.path.isdir(path):
        os.makedirs(path)
    return path


def db_path():
    return os.path.join(support_dir(), "timeslip.db")


def connect():
    conn = sqlite3.connect(db_path())
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = connect()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            comment TEXT NOT NULL,
            start_ms INTEGER NOT NULL,
            end_ms INTEGER,
            duration_ms INTEGER
        );
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        );
        CREATE TABLE IF NOT EXISTS running (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            session_id TEXT,
            comment TEXT,
            start_ms INTEGER
        );
        """
    )
    conn.commit()
    conn.close()


def _row_session(row):
    if row is None:
        return None
    return {
        "id": row["id"],
        "comment": row["comment"],
        "startMs": row["start_ms"],
        "endMs": row["end_ms"],
        "durationMs": row["duration_ms"],
    }


def list_sessions():
    conn = connect()
    rows = conn.execute(
        "SELECT * FROM sessions ORDER BY start_ms DESC"
    ).fetchall()
    conn.close()
    return [_row_session(r) for r in rows]


def get_running():
    conn = connect()
    row = conn.execute("SELECT * FROM running WHERE id = 1").fetchone()
    conn.close()
    if not row or not row["session_id"]:
        return None
    return {
        "id": row["session_id"],
        "comment": row["comment"],
        "startMs": row["start_ms"],
    }


def start_session(comment):
    comment = (comment or "").strip()
    if not comment:
        raise ValueError("Add a short comment on the work first")
    if get_running():
        raise ValueError("A session is already running")
    now = int(_now_ms())
    sid = str(uuid.uuid4())
    conn = connect()
    conn.execute(
        "INSERT OR REPLACE INTO running (id, session_id, comment, start_ms) VALUES (1, ?, ?, ?)",
        (sid, comment, now),
    )
    conn.commit()
    conn.close()
    return {"id": sid, "comment": comment, "startMs": now}


def stop_session():
    running = get_running()
    if not running:
        raise ValueError("No session is running")
    end_ms = int(_now_ms())
    duration = max(1000, end_ms - int(running["startMs"]))
    conn = connect()
    conn.execute(
        "INSERT INTO sessions (id, comment, start_ms, end_ms, duration_ms) VALUES (?, ?, ?, ?, ?)",
        (running["id"], running["comment"], running["startMs"], end_ms, duration),
    )
    conn.execute(
        "INSERT OR REPLACE INTO running (id, session_id, comment, start_ms) VALUES (1, NULL, NULL, NULL)"
    )
    conn.commit()
    conn.close()
    return {
        "id": running["id"],
        "comment": running["comment"],
        "startMs": running["startMs"],
        "endMs": end_ms,
        "durationMs": duration,
    }


def update_session(sid, comment, start_ms, end_ms):
    start_ms = int(start_ms)
    end_ms = int(end_ms)
    if end_ms <= start_ms:
        raise ValueError("End time must be after start time")
    comment = (comment or "").strip() or "Untitled work"
    duration = end_ms - start_ms
    conn = connect()
    cur = conn.execute(
        "UPDATE sessions SET comment=?, start_ms=?, end_ms=?, duration_ms=? WHERE id=?",
        (comment, start_ms, end_ms, duration, sid),
    )
    conn.commit()
    changed = cur.rowcount
    conn.close()
    if not changed:
        raise ValueError("Session not found")
    return {
        "id": sid,
        "comment": comment,
        "startMs": start_ms,
        "endMs": end_ms,
        "durationMs": duration,
    }


def delete_session(sid):
    conn = connect()
    conn.execute("DELETE FROM sessions WHERE id=?", (sid,))
    conn.commit()
    conn.close()


def clear_sessions():
    conn = connect()
    conn.execute("DELETE FROM sessions")
    conn.commit()
    conn.close()


def get_rate():
    conn = connect()
    row = conn.execute(
        "SELECT value FROM settings WHERE key='rate'"
    ).fetchone()
    conn.close()
    if not row:
        return 0.0
    try:
        return float(row["value"])
    except ValueError:
        return 0.0


def set_rate(rate):
    try:
        rate = float(rate or 0)
    except ValueError:
        rate = 0.0
    if rate < 0:
        rate = 0.0
    conn = connect()
    conn.execute(
        "INSERT OR REPLACE INTO settings (key, value) VALUES ('rate', ?)",
        (str(rate),),
    )
    conn.commit()
    conn.close()
    return rate


def _now_ms():
    return int(datetime.now().timestamp() * 1000)


def dump_state():
    return {
        "sessions": list_sessions(),
        "running": get_running(),
        "rate": get_rate(),
    }
