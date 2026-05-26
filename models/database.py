"""
IG Manager Pro - SQLite Database Manager
Local storage for scan results and app data
"""

import sqlite3
import os
import json
from datetime import datetime


DB_PATH = os.path.join(os.path.expanduser("~"), ".igmanager", "igmanager.db")


def get_db_path():
    """Return platform-appropriate DB path."""
    try:
        from android.storage import app_storage_path  # type: ignore
        base = app_storage_path()
    except ImportError:
        base = os.path.join(os.path.expanduser("~"), ".igmanager")
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, "igmanager.db")


class Database:
    """Manages all SQLite operations for IG Manager Pro."""

    def __init__(self):
        self.db_path = get_db_path()
        self._init_db()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Create tables if they don't exist."""
        conn = self._connect()
        c = conn.cursor()

        c.execute("""
            CREATE TABLE IF NOT EXISTS scans (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                username    TEXT NOT NULL,
                status      TEXT DEFAULT 'unknown',
                followers   INTEGER DEFAULT 0,
                following   INTEGER DEFAULT 0,
                posts       INTEGER DEFAULT 0,
                is_private  INTEGER DEFAULT 0,
                is_verified INTEGER DEFAULT 0,
                shadowban   INTEGER DEFAULT 0,
                full_name   TEXT DEFAULT '',
                bio         TEXT DEFAULT '',
                profile_pic TEXT DEFAULT '',
                scanned_at  TEXT DEFAULT (datetime('now')),
                raw_data    TEXT DEFAULT '{}'
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS appeals (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                username     TEXT NOT NULL,
                full_name    TEXT DEFAULT '',
                email        TEXT DEFAULT '',
                year_created TEXT DEFAULT '',
                country      TEXT DEFAULT '',
                issue_type   TEXT DEFAULT '',
                issue_detail TEXT DEFAULT '',
                appeal_ar    TEXT DEFAULT '',
                appeal_en    TEXT DEFAULT '',
                created_at   TEXT DEFAULT (datetime('now'))
            )
        """)

        conn.commit()
        conn.close()

    # ─── Scan Methods ─────────────────────────────────────────────────────────

    def save_scan(self, data: dict) -> int:
        """Insert or replace a scan result. Returns row id."""
        conn = self._connect()
        c = conn.cursor()
        c.execute("""
            INSERT INTO scans
              (username, status, followers, following, posts,
               is_private, is_verified, shadowban, full_name,
               bio, profile_pic, scanned_at, raw_data)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            data.get("username", ""),
            data.get("status", "unknown"),
            data.get("followers", 0),
            data.get("following", 0),
            data.get("posts", 0),
            1 if data.get("is_private") else 0,
            1 if data.get("is_verified") else 0,
            1 if data.get("shadowban") else 0,
            data.get("full_name", ""),
            data.get("bio", ""),
            data.get("profile_pic", ""),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            json.dumps(data.get("raw", {})),
        ))
        row_id = c.lastrowid
        conn.commit()
        conn.close()
        return row_id

    def get_all_scans(self, status_filter: str = None) -> list:
        conn = self._connect()
        c = conn.cursor()
        if status_filter and status_filter != "all":
            c.execute(
                "SELECT * FROM scans WHERE status=? ORDER BY scanned_at DESC",
                (status_filter,)
            )
        else:
            c.execute("SELECT * FROM scans ORDER BY scanned_at DESC")
        rows = [dict(r) for r in c.fetchall()]
        conn.close()
        return rows

    def get_recent_scans(self, limit: int = 10) -> list:
        conn = self._connect()
        c = conn.cursor()
        c.execute(
            "SELECT * FROM scans ORDER BY scanned_at DESC LIMIT ?", (limit,)
        )
        rows = [dict(r) for r in c.fetchall()]
        conn.close()
        return rows

    def get_stats(self) -> dict:
        conn = self._connect()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM scans")
        total = c.fetchone()[0]
        c.execute("SELECT status, COUNT(*) as cnt FROM scans GROUP BY status")
        by_status = {row[0]: row[1] for row in c.fetchall()}
        conn.close()
        return {
            "total":     total,
            "active":    by_status.get("active", 0),
            "disabled":  by_status.get("disabled", 0),
            "shadowban": by_status.get("shadowban", 0),
            "private":   by_status.get("private", 0),
            "unknown":   by_status.get("unknown", 0),
        }

    def clear_all_scans(self):
        conn = self._connect()
        conn.execute("DELETE FROM scans")
        conn.commit()
        conn.close()

    # ─── Appeal Methods ───────────────────────────────────────────────────────

    def save_appeal(self, data: dict) -> int:
        conn = self._connect()
        c = conn.cursor()
        c.execute("""
            INSERT INTO appeals
              (username, full_name, email, year_created, country,
               issue_type, issue_detail, appeal_ar, appeal_en, created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?)
        """, (
            data.get("username", ""),
            data.get("full_name", ""),
            data.get("email", ""),
            data.get("year_created", ""),
            data.get("country", ""),
            data.get("issue_type", ""),
            data.get("issue_detail", ""),
            data.get("appeal_ar", ""),
            data.get("appeal_en", ""),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ))
        row_id = c.lastrowid
        conn.commit()
        conn.close()
        return row_id

    def get_all_appeals(self) -> list:
        conn = self._connect()
        c = conn.cursor()
        c.execute("SELECT * FROM appeals ORDER BY created_at DESC")
        rows = [dict(r) for r in c.fetchall()]
        conn.close()
        return rows
