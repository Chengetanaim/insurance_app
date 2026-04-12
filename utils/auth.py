import sqlite3
import hashlib
import os
import streamlit as st
from datetime import datetime

DB_PATH = "insureiq.db"


def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT UNIQUE NOT NULL,
            email       TEXT UNIQUE NOT NULL,
            password    TEXT NOT NULL,
            full_name   TEXT,
            role        TEXT DEFAULT 'analyst',
            created_at  TEXT DEFAULT (datetime('now')),
            last_login  TEXT
        );

        CREATE TABLE IF NOT EXISTS quotes (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER NOT NULL,
            product_type    TEXT NOT NULL,
            insured_name    TEXT,
            premium         REAL,
            risk_score      REAL,
            inputs_json     TEXT,
            created_at      TEXT DEFAULT (datetime('now')),
            status          TEXT DEFAULT 'draft',
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS audit_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER,
            action      TEXT,
            detail      TEXT,
            ts          TEXT DEFAULT (datetime('now'))
        );
    """)
    conn.commit()
    conn.close()


def register_user(username, email, password, full_name) -> tuple[bool, str]:
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    conn = get_conn()
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO users (username, email, password, full_name) VALUES (?,?,?,?)",
            (username.strip(), email.strip().lower(), hash_password(password), full_name.strip()),
        )
        conn.commit()
        log_action(c.lastrowid, "REGISTER", f"New user: {username}", conn)
        return True, "Account created successfully!"
    except sqlite3.IntegrityError as e:
        if "username" in str(e):
            return False, "Username already taken."
        return False, "Email already registered."
    finally:
        conn.close()


def login_user(username, password) -> tuple[bool, dict | str]:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, username, email, full_name, role FROM users WHERE username=? AND password=?",
              (username.strip(), hash_password(password)))
    row = c.fetchone()
    if row:
        uid, uname, email, full_name, role = row
        c.execute("UPDATE users SET last_login=? WHERE id=?", (datetime.now().isoformat(), uid))
        conn.commit()
        log_action(uid, "LOGIN", "Successful login", conn)
        conn.close()
        return True, {"id": uid, "username": uname, "email": email, "full_name": full_name, "role": role}
    conn.close()
    return False, "Invalid username or password."


def get_current_user():
    return {
        "id": st.session_state.get("user_id"),
        "username": st.session_state.get("username"),
        "full_name": st.session_state.get("full_name", ""),
        "email": st.session_state.get("email", ""),
        "role": st.session_state.get("role", "analyst"),
    }


def log_action(user_id, action, detail, conn=None):
    close_after = conn is None
    if conn is None:
        conn = get_conn()
    conn.execute("INSERT INTO audit_log (user_id, action, detail) VALUES (?,?,?)",
                 (user_id, action, detail))
    conn.commit()
    if close_after:
        conn.close()


def save_quote(user_id, product_type, insured_name, premium, risk_score, inputs_json):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""INSERT INTO quotes (user_id, product_type, insured_name, premium, risk_score, inputs_json)
                 VALUES (?,?,?,?,?,?)""",
              (user_id, product_type, insured_name, premium, risk_score, inputs_json))
    conn.commit()
    qid = c.lastrowid
    conn.close()
    return qid


def get_user_quotes(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""SELECT id, product_type, insured_name, premium, risk_score, created_at, status
                 FROM quotes WHERE user_id=? ORDER BY created_at DESC""", (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows


def get_all_quotes_stats():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""SELECT product_type, COUNT(*) as cnt, AVG(premium) as avg_premium,
                        MIN(premium), MAX(premium)
                 FROM quotes GROUP BY product_type""")
    rows = c.fetchall()
    conn.close()
    return rows


def update_user_profile(user_id, full_name, email):
    conn = get_conn()
    try:
        conn.execute("UPDATE users SET full_name=?, email=? WHERE id=?", (full_name, email, user_id))
        conn.commit()
        return True, "Profile updated."
    except sqlite3.IntegrityError:
        return False, "Email already in use."
    finally:
        conn.close()


def change_password(user_id, old_pw, new_pw):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE id=? AND password=?", (user_id, hash_password(old_pw)))
    if not c.fetchone():
        conn.close()
        return False, "Current password is incorrect."
    if len(new_pw) < 6:
        conn.close()
        return False, "New password must be at least 6 characters."
    conn.execute("UPDATE users SET password=? WHERE id=?", (hash_password(new_pw), user_id))
    conn.commit()
    conn.close()
    return True, "Password changed successfully."


def delete_quote(quote_id, user_id):
    conn = get_conn()
    conn.execute("DELETE FROM quotes WHERE id=? AND user_id=?", (quote_id, user_id))
    conn.commit()
    conn.close()
