"""
database.py
===========
Data access layer for the Sample Analysis plugin.
Creates and manages the SQLite database with all required tables.
"""

import sqlite3
import os

# Database file lives inside the plugin folder
_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_analysis.db")

_DUMMY_METHODS = [
    ("Cromatografía HPLC",      "HPLC-001", "USP <621>"),
    ("Espectrofotometría UV",    "UV-001",   "USP <857>"),
    ("Titulación ácido-base",   "TITR-001", "Ph. Eur. 2.2.20"),
    ("Prueba de identidad IR",  "IR-001",   "USP <197>"),
]


def get_connection() -> sqlite3.Connection:
    """Returns an open connection to the plugin database."""
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Creates all tables and seeds dummy data if needed."""
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS analysis_method (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                name          TEXT NOT NULL,
                code          TEXT NOT NULL UNIQUE,
                specification TEXT
            );

            CREATE TABLE IF NOT EXISTS lot (
                id                 INTEGER PRIMARY KEY AUTOINCREMENT,
                unique_code        TEXT NOT NULL UNIQUE,
                product            TEXT NOT NULL,
                capacity           TEXT,
                manufacturing_date TEXT,
                expiry_date        TEXT
            );

            CREATE TABLE IF NOT EXISTS retention_book (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_number TEXT NOT NULL UNIQUE,
                lot_id          INTEGER NOT NULL REFERENCES lot(id) ON DELETE RESTRICT
            );

            CREATE TABLE IF NOT EXISTS certificate_of_analysis (
                id                 INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_number    TEXT NOT NULL,
                date               TEXT NOT NULL,
                pharmacist_regent  TEXT NOT NULL,
                results            TEXT,
                observation        TEXT,
                attachment         TEXT,
                signature_image    TEXT,
                business_id        TEXT,
                analysis_method_id INTEGER REFERENCES analysis_method(id) ON DELETE SET NULL
            );
        """)

        # Seed dummy analysis methods if table is empty
        count = conn.execute("SELECT COUNT(*) FROM analysis_method").fetchone()[0]
        if count == 0:
            conn.executemany(
                "INSERT INTO analysis_method (name, code, specification) VALUES (?, ?, ?)",
                _DUMMY_METHODS
            )


# ─── Analysis Method ──────────────────────────────────────────────────────────

def get_all_analysis_methods():
    with get_connection() as conn:
        return conn.execute("SELECT * FROM analysis_method ORDER BY code").fetchall()

def save_analysis_method(name, code, specification, method_id=None):
    with get_connection() as conn:
        if method_id:
            conn.execute(
                "UPDATE analysis_method SET name=?, code=?, specification=? WHERE id=?",
                (name, code, specification, method_id)
            )
        else:
            conn.execute(
                "INSERT INTO analysis_method (name, code, specification) VALUES (?,?,?)",
                (name, code, specification)
            )

def delete_analysis_method(method_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM analysis_method WHERE id=?", (method_id,))


# ─── Lot ──────────────────────────────────────────────────────────────────────

def get_all_lots():
    with get_connection() as conn:
        return conn.execute("SELECT * FROM lot ORDER BY unique_code").fetchall()

def save_lot(unique_code, product, capacity, manufacturing_date, expiry_date, lot_id=None):
    with get_connection() as conn:
        if lot_id:
            conn.execute(
                """UPDATE lot SET unique_code=?, product=?, capacity=?,
                   manufacturing_date=?, expiry_date=? WHERE id=?""",
                (unique_code, product, capacity, manufacturing_date, expiry_date, lot_id)
            )
        else:
            conn.execute(
                """INSERT INTO lot (unique_code, product, capacity, manufacturing_date, expiry_date)
                   VALUES (?,?,?,?,?)""",
                (unique_code, product, capacity, manufacturing_date, expiry_date)
            )

def delete_lot(lot_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM lot WHERE id=?", (lot_id,))


# ─── Retention Book ───────────────────────────────────────────────────────────

def get_all_retention_entries():
    with get_connection() as conn:
        return conn.execute("""
            SELECT rb.id, rb.analysis_number, rb.lot_id, l.unique_code as lot_code, l.product
            FROM retention_book rb
            JOIN lot l ON rb.lot_id = l.id
            ORDER BY rb.analysis_number
        """).fetchall()

def save_retention_entry(analysis_number, lot_id, entry_id=None):
    with get_connection() as conn:
        if entry_id:
            conn.execute(
                "UPDATE retention_book SET analysis_number=?, lot_id=? WHERE id=?",
                (analysis_number, lot_id, entry_id)
            )
        else:
            conn.execute(
                "INSERT INTO retention_book (analysis_number, lot_id) VALUES (?,?)",
                (analysis_number, lot_id)
            )

def delete_retention_entry(entry_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM retention_book WHERE id=?", (entry_id,))


# ─── Certificate of Analysis ──────────────────────────────────────────────────

def get_all_certificates():
    with get_connection() as conn:
        return conn.execute("""
            SELECT c.*, am.name as method_name
            FROM certificate_of_analysis c
            LEFT JOIN analysis_method am ON c.analysis_method_id = am.id
            ORDER BY c.date DESC
        """).fetchall()

def save_certificate(data: dict, cert_id=None):
    fields = ["analysis_number", "date", "pharmacist_regent", "results",
              "observation", "attachment", "signature_image", "business_id", "analysis_method_id"]
    values = [data.get(f) for f in fields]
    with get_connection() as conn:
        if cert_id:
            set_clause = ", ".join(f"{f}=?" for f in fields)
            conn.execute(
                f"UPDATE certificate_of_analysis SET {set_clause} WHERE id=?",
                values + [cert_id]
            )
        else:
            placeholders = ", ".join("?" * len(fields))
            conn.execute(
                f"INSERT INTO certificate_of_analysis ({', '.join(fields)}) VALUES ({placeholders})",
                values
            )

def delete_certificate(cert_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM certificate_of_analysis WHERE id=?", (cert_id,))
