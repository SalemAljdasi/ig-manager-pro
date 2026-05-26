import sqlite3
import json
import os
import csv
from datetime import datetime

DB_PATH = os.path.join(os.path.expanduser("~"), ".igmanager_pro.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            status TEXT,
            followers INTEGER DEFAULT 0,
            following INTEGER DEFAULT 0,
            posts INTEGER DEFAULT 0,
            is_verified INTEGER DEFAULT 0,
            is_private INTEGER DEFAULT 0,
            guessed_email TEXT,
            security_score INTEGER DEFAULT 0,
            security_level TEXT,
            raw_data TEXT,
            scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS appeals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            full_name TEXT,
            email TEXT,
            country TEXT,
            phone TEXT,
            issue_type TEXT,
            description TEXT,
            appeal_text_ar TEXT,
            appeal_text_en TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS recovery_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            ban_reason TEXT,
            extra_info TEXT,
            recovery_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS verification_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            full_name TEXT,
            email TEXT,
            account_type TEXT,
            social_links TEXT,
            activities TEXT,
            followers_count TEXT,
            media_coverage TEXT,
            request_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()


def save_scan(username, status, followers=0, following=0, posts=0,
              is_verified=False, is_private=False, guessed_email="",
              security_score=0, security_level="unknown", raw_data=None):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO scans (username, status, followers, following, posts,
            is_verified, is_private, guessed_email, security_score,
            security_level, raw_data)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (username, status, followers, following, posts,
          int(is_verified), int(is_private), guessed_email,
          security_score, security_level,
          json.dumps(raw_data) if raw_data else "{}"))
    conn.commit()
    conn.close()


def get_all_scans(limit=200, status_filter=None, search=None):
    conn = get_connection()
    c = conn.cursor()
    query = "SELECT * FROM scans"
    params = []
    conditions = []
    if status_filter and status_filter != "all":
        conditions.append("status = ?")
        params.append(status_filter)
    if search:
        conditions.append("username LIKE ?")
        params.append(f"%{search}%")
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY scanned_at DESC LIMIT ?"
    params.append(limit)
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_recent_scans(limit=15):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM scans ORDER BY scanned_at DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_stats():
    conn = get_connection()
    c = conn.cursor()
    stats = {}
    for status in ["active", "disabled", "shadowban", "private", "hacked", "verified"]:
        if status == "verified":
            c.execute("SELECT COUNT(*) FROM scans WHERE is_verified=1")
        else:
            c.execute("SELECT COUNT(*) FROM scans WHERE status=?", (status,))
        stats[status] = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM scans")
    stats["total"] = c.fetchone()[0]
    conn.close()
    return stats


def save_appeal(username, full_name, email, country, phone,
                issue_type, description, appeal_text_ar, appeal_text_en):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO appeals (username, full_name, email, country, phone,
            issue_type, description, appeal_text_ar, appeal_text_en)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (username, full_name, email, country, phone,
          issue_type, description, appeal_text_ar, appeal_text_en))
    conn.commit()
    conn.close()


def get_all_appeals():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM appeals ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_recovery_request(username, ban_reason, extra_info, recovery_text):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO recovery_requests (username, ban_reason, extra_info, recovery_text)
        VALUES (?, ?, ?, ?)
    """, (username, ban_reason, extra_info, recovery_text))
    conn.commit()
    conn.close()


def save_verification_request(username, full_name, email, account_type,
                               social_links, activities, followers_count,
                               media_coverage, request_text):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO verification_requests
            (username, full_name, email, account_type, social_links,
             activities, followers_count, media_coverage, request_text)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (username, full_name, email, account_type, social_links,
          activities, followers_count, media_coverage, request_text))
    conn.commit()
    conn.close()


def save_chat(role, message):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO chat_history (role, message) VALUES (?, ?)", (role, message))
    conn.commit()
    conn.close()


def get_chat_history(limit=100):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM chat_history ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return list(reversed([dict(r) for r in rows]))


def clear_all():
    conn = get_connection()
    c = conn.cursor()
    c.executescript("""
        DELETE FROM scans;
        DELETE FROM appeals;
        DELETE FROM recovery_requests;
        DELETE FROM verification_requests;
        DELETE FROM chat_history;
    """)
    conn.commit()
    conn.close()


def export_to_json():
    data = {
        "scans": get_all_scans(limit=10000),
        "appeals": get_all_appeals(),
        "exported_at": datetime.now().isoformat(),
    }
    path = os.path.join(os.path.expanduser("~"), "ig_manager_export.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path


def export_to_csv():
    scans = get_all_scans(limit=10000)
    path = os.path.join(os.path.expanduser("~"), "ig_manager_scans.csv")
    if not scans:
        return None
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=scans[0].keys())
        writer.writeheader()
        writer.writerows(scans)
    return path


def export_to_html():
    scans = get_all_scans(limit=10000)
    stats = get_stats()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    rows_html = ""
    status_colors = {
        "active": "#10B981", "disabled": "#EF4444", "shadowban": "#F59E0B",
        "private": "#06B6D4", "hacked": "#EC4899", "unknown": "#475569",
    }
    status_labels = {
        "active": "نشط", "disabled": "معطل", "shadowban": "شادوبان",
        "private": "خاص", "hacked": "مخترق", "unknown": "غير معروف",
    }
    for s in scans:
        color = status_colors.get(s.get("status", "unknown"), "#475569")
        label = status_labels.get(s.get("status", "unknown"), "غير معروف")
        verified_badge = "✅" if s.get("is_verified") else ""
        rows_html += f"""
        <tr>
            <td>{s.get('username', '')}</td>
            <td><span style='background:{color};color:#fff;padding:2px 8px;border-radius:12px;font-size:12px;'>{label}</span></td>
            <td>{s.get('followers', 0):,}</td>
            <td>{s.get('following', 0):,}</td>
            <td>{s.get('posts', 0):,}</td>
            <td>{verified_badge}</td>
            <td>{s.get('security_score', 0)}%</td>
            <td>{s.get('scanned_at', '')[:16]}</td>
        </tr>"""
    html = f"""<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
<meta charset="UTF-8">
<title>تقرير IG Manager Pro v4.0</title>
<style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #0A0A1A; color: #F8FAFC; margin: 0; padding: 20px; }}
  h1 {{ color: #A78BFA; text-align: center; font-size: 28px; margin-bottom: 5px; }}
  .subtitle {{ text-align: center; color: #94A3B8; margin-bottom: 30px; font-size: 14px; }}
  .stats-grid {{ display: grid; grid-template-columns: repeat(3,1fr); gap: 16px; margin-bottom: 30px; }}
  .stat-card {{ background: #12122A; border: 1px solid #2D2D5E; border-radius: 12px; padding: 16px; text-align: center; }}
  .stat-card .num {{ font-size: 32px; font-weight: bold; color: #A78BFA; }}
  .stat-card .lbl {{ font-size: 13px; color: #94A3B8; margin-top: 4px; }}
  table {{ width: 100%; border-collapse: collapse; background: #12122A; border-radius: 12px; overflow: hidden; }}
  th {{ background: #1A1A3A; color: #A78BFA; padding: 12px 10px; font-size: 13px; border-bottom: 1px solid #2D2D5E; }}
  td {{ padding: 10px; font-size: 13px; border-bottom: 1px solid #1A1A3A; color: #F8FAFC; }}
  tr:hover {{ background: #1A1A3A; }}
  .footer {{ text-align: center; color: #475569; font-size: 12px; margin-top: 30px; }}
</style>
</head>
<body>
<h1>🌟 IG Manager Pro v4.0</h1>
<div class="subtitle">تقرير فحص الحسابات — تم التصدير في {now}</div>
<div class="stats-grid">
  <div class="stat-card"><div class="num">{stats.get('total',0)}</div><div class="lbl">إجمالي الفحوصات</div></div>
  <div class="stat-card"><div class="num" style="color:#10B981">{stats.get('active',0)}</div><div class="lbl">نشط</div></div>
  <div class="stat-card"><div class="num" style="color:#EF4444">{stats.get('disabled',0)}</div><div class="lbl">معطل</div></div>
  <div class="stat-card"><div class="num" style="color:#F59E0B">{stats.get('shadowban',0)}</div><div class="lbl">شادوبان</div></div>
  <div class="stat-card"><div class="num" style="color:#06B6D4">{stats.get('private',0)}</div><div class="lbl">خاص</div></div>
  <div class="stat-card"><div class="num" style="color:#EC4899">{stats.get('hacked',0)}</div><div class="lbl">مخترق</div></div>
</div>
<table>
<thead><tr>
  <th>اسم المستخدم</th><th>الحالة</th><th>المتابعون</th>
  <th>يتابع</th><th>المنشورات</th><th>موثق</th><th>الأمان</th><th>وقت الفحص</th>
</tr></thead>
<tbody>{rows_html}</tbody>
</table>
<div class="footer">IG Manager Pro v4.0 — © 2025 All Rights Reserved</div>
</body></html>"""
    path = os.path.join(os.path.expanduser("~"), "ig_manager_report.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return path
