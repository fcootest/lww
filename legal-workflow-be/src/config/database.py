"""SQLite database module — shared connection and schema."""

import sqlite3
import os

_connection: sqlite3.Connection | None = None
_db_path: str | None = None


def get_db() -> sqlite3.Connection:
    """Get the shared SQLite connection. Creates it if needed."""
    global _connection, _db_path
    if _connection is None:
        if _db_path is None:
            _db_path = os.environ.get(
                "LEGAL_DB_PATH",
                os.path.join(os.path.dirname(__file__), "..", "..", "legal.db"),
            )
        _connection = sqlite3.connect(_db_path, check_same_thread=False)
        _connection.row_factory = sqlite3.Row
        _connection.execute("PRAGMA journal_mode=WAL")
        _connection.execute("PRAGMA foreign_keys=ON")
    return _connection


def init_db():
    """Create all tables if they don't exist."""
    db = get_db()
    db.executescript(SCHEMA)
    db.commit()


def reset_db(path: str = ":memory:"):
    """Reset database (used by tests). Closes current connection and creates new one."""
    global _connection, _db_path
    if _connection:
        _connection.close()
    _db_path = path
    _connection = None
    init_db()


def table_has_data(table_name: str) -> bool:
    """Check if a table has any rows."""
    db = get_db()
    row = db.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
    return row[0] > 0


SCHEMA = """
CREATE TABLE IF NOT EXISTS tst (
    tst_id TEXT PRIMARY KEY,
    tst_code TEXT NOT NULL,
    tst_name TEXT NOT NULL,
    tst_level INTEGER NOT NULL,
    my_parent_task TEXT,
    description TEXT,
    sla_days INTEGER,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tnt (
    tnt_id TEXT PRIMARY KEY,
    from_tst_id TEXT NOT NULL,
    to_tst_id TEXT NOT NULL,
    condition_expression TEXT,
    condition_description TEXT,
    priority INTEGER,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tdt (
    tdt_id TEXT PRIMARY KEY,
    tdt_code TEXT NOT NULL,
    tdt_name TEXT NOT NULL,
    description TEXT,
    file_extensions TEXT,
    max_file_size_mb INTEGER,
    is_required INTEGER DEFAULT 0,
    tdtp_id TEXT,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tdtp (
    tdtp_id TEXT PRIMARY KEY,
    tdt_id TEXT NOT NULL,
    tdtp_code TEXT NOT NULL,
    tdtp_name TEXT NOT NULL,
    description TEXT,
    template_file_ref TEXT,
    template_structure TEXT,
    sample_data TEXT,
    version INTEGER NOT NULL DEFAULT 1,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS trt (
    trt_id TEXT PRIMARY KEY,
    trt_code TEXT NOT NULL,
    trt_name TEXT NOT NULL,
    description TEXT,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tst_trt (
    tst_id TEXT NOT NULL,
    trt_id TEXT NOT NULL,
    is_required INTEGER DEFAULT 0,
    PRIMARY KEY (tst_id, trt_id)
);

CREATE TABLE IF NOT EXISTS emp (
    emp_id TEXT PRIMARY KEY,
    emp_code TEXT NOT NULL UNIQUE,
    emp_name TEXT NOT NULL,
    email TEXT NOT NULL,
    department TEXT,
    position TEXT,
    grade_code TEXT,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tsi (
    tsi_id TEXT PRIMARY KEY,
    tsi_code TEXT NOT NULL,
    tst_id TEXT NOT NULL,
    my_parent_task TEXT,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL,
    priority TEXT,
    requested_by TEXT,
    assigned_to TEXT,
    due_date TEXT,
    actual_completion_date TEXT,
    current_tst_level INTEGER,
    current_tst_id TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tsi_counter (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    counter INTEGER NOT NULL DEFAULT 0
);
INSERT OR IGNORE INTO tsi_counter (id, counter) VALUES (1, 0);

CREATE TABLE IF NOT EXISTS tdi (
    tdi_id TEXT PRIMARY KEY,
    tdt_id TEXT NOT NULL,
    tsi_id TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_url TEXT NOT NULL,
    file_size_bytes INTEGER,
    version INTEGER NOT NULL DEFAULT 1,
    uploaded_by TEXT NOT NULL,
    uploaded_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'ACTIVE',
    notes TEXT
);

CREATE TABLE IF NOT EXISTS tsev (
    tsev_id TEXT PRIMARY KEY,
    tsi_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    emp_id TEXT NOT NULL,
    event_data TEXT,
    tdi_id TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tri (
    tri_id TEXT PRIMARY KEY,
    trt_id TEXT NOT NULL,
    tsi_id TEXT,
    emp_id TEXT NOT NULL,
    assigned_at TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS tsi_filter (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tsi_id TEXT NOT NULL,
    filter_type TEXT NOT NULL,
    filter_code TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tst_filter (
    tst_id TEXT NOT NULL,
    filter_type TEXT NOT NULL,
    filter_code TEXT NOT NULL,
    PRIMARY KEY (tst_id, filter_type, filter_code)
);

CREATE TABLE IF NOT EXISTS tst_tdt (
    tst_id TEXT NOT NULL,
    tdt_id TEXT NOT NULL,
    is_required INTEGER DEFAULT 0,
    PRIMARY KEY (tst_id, tdt_id)
);
"""
