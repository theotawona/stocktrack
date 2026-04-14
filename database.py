# ── Requisition Usage Reports ───────────────────────────────
def add_usage_report(requisition_id, username, report):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO requisition_usage_reports (requisition_id, username, report) VALUES (?,?,?)",
            (requisition_id, username, report)
        )

def get_usage_reports(requisition_id):
    with get_conn() as conn:
        return pd.read_sql(
            "SELECT * FROM requisition_usage_reports WHERE requisition_id = ? ORDER BY created_at DESC",
            conn, params=[requisition_id]
        )

# ── Requisition Documents ──────────────────────────────────
def add_requisition_document(requisition_id, username, filename, filedata, mimetype):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO requisition_documents (requisition_id, username, filename, filedata, mimetype) VALUES (?,?,?,?,?)",
            (requisition_id, username, filename, filedata, mimetype)
        )

def get_requisition_documents(requisition_id):
    with get_conn() as conn:
        return pd.read_sql(
            "SELECT id, username, filename, mimetype, created_at FROM requisition_documents WHERE requisition_id = ? ORDER BY created_at DESC",
            conn, params=[requisition_id]
        )

def get_document_file(document_id):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT filename, filedata, mimetype FROM requisition_documents WHERE id = ?",
            (document_id,)
        ).fetchone()
        return row if row else None

# ── Requisition Comments ───────────────────────────────────
def add_requisition_comment(requisition_id, username, comment):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO requisition_comments (requisition_id, username, comment) VALUES (?,?,?)",
            (requisition_id, username, comment)
        )

def get_requisition_comments(requisition_id):
    with get_conn() as conn:
        return pd.read_sql(
            "SELECT * FROM requisition_comments WHERE requisition_id = ? ORDER BY created_at ASC",
            conn, params=[requisition_id]
        )

# ── Stock Movement Invoices ────────────────────────────────
def add_movement_invoice(slip_number, username, filename, filedata, mimetype):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO stock_movement_invoices (slip_number, username, filename, filedata, mimetype) VALUES (?,?,?,?,?)",
            (slip_number, username, filename, filedata, mimetype)
        )

def get_movement_invoices(slip_number):
    with get_conn() as conn:
        return pd.read_sql(
            "SELECT id, username, filename, mimetype, created_at FROM stock_movement_invoices WHERE slip_number = ? ORDER BY created_at DESC",
            conn, params=[slip_number]
        )

def get_movement_invoice_file(invoice_id):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT filename, filedata, mimetype FROM stock_movement_invoices WHERE id = ?",
            (invoice_id,)
        ).fetchone()
        return row if row else None

# ── Cost History ───────────────────────────────────────────
def get_cost_history(item_id=None, property_id=None, limit=200):
    q = """
        SELECT ch.*, i.name as item_name, i.uom, s.name as storeroom_name, p.name as property_name
        FROM cost_history ch
        JOIN items i ON i.id = ch.item_id
        JOIN storerooms s ON s.id = i.storeroom_id
        JOIN properties p ON p.id = s.property_id
        WHERE 1=1
    """
    params = []
    if item_id:
        q += " AND ch.item_id = ?"
        params.append(item_id)
    if property_id:
        q += " AND p.id = ?"
        params.append(property_id)
    q += " ORDER BY ch.created_at DESC LIMIT ?"
    params.append(limit)
    with get_conn() as conn:
        return pd.read_sql(q, conn, params=params)

def get_cost_history_for_item(item_id):
    q = """
        SELECT ch.cost_before, ch.cost_after, ch.qty_delta, ch.reason, ch.changed_by, ch.created_at
        FROM cost_history ch
        WHERE ch.item_id = ?
        ORDER BY ch.created_at ASC
    """
    with get_conn() as conn:
        return pd.read_sql(q, conn, params=[item_id])

import sqlite3
import pandas as pd
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "stock_tracker.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with get_conn() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS properties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            address TEXT,
            notes TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS storerooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            property_id INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
            name TEXT NOT NULL,
            location_notes TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            contact TEXT,
            phone TEXT,
            email TEXT,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            storeroom_id INTEGER NOT NULL REFERENCES storerooms(id) ON DELETE CASCADE,
            name TEXT NOT NULL,
            category TEXT DEFAULT 'General',
            uom TEXT DEFAULT 'units',
            qty REAL DEFAULT 0,
            min_qty REAL DEFAULT 1,
            supplier_id INTEGER REFERENCES suppliers(id) ON DELETE SET NULL,
            unit_cost REAL DEFAULT 0,
            description TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS issuances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL REFERENCES items(id) ON DELETE CASCADE,
            recipient TEXT NOT NULL,
            issued_by TEXT,
            qty REAL NOT NULL,
            issued_date TEXT NOT NULL,
            note TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS reconciliations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            storeroom_id INTEGER REFERENCES storerooms(id) ON DELETE SET NULL,
            performed_by TEXT,
            recon_date TEXT NOT NULL,
            notes TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS reconciliation_lines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reconciliation_id INTEGER NOT NULL REFERENCES reconciliations(id) ON DELETE CASCADE,
            item_id INTEGER NOT NULL REFERENCES items(id) ON DELETE CASCADE,
            recorded_qty REAL NOT NULL,
            counted_qty REAL NOT NULL,
            diff REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS requisitions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ref_number TEXT NOT NULL UNIQUE,
            requested_by TEXT NOT NULL,
            requested_by_role TEXT,
            property_id INTEGER REFERENCES properties(id) ON DELETE SET NULL,
            storeroom_id INTEGER REFERENCES storerooms(id) ON DELETE SET NULL,
            purpose TEXT,
            urgency TEXT DEFAULT 'Normal',
            status TEXT DEFAULT 'Pending',
            reviewed_by TEXT,
            reviewed_at TEXT,
            review_note TEXT,
            dispersed_by TEXT,
            dispersed_at TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS requisition_lines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            requisition_id INTEGER NOT NULL REFERENCES requisitions(id) ON DELETE CASCADE,
            item_id INTEGER NOT NULL REFERENCES items(id) ON DELETE CASCADE,
            qty_requested REAL NOT NULL,
            qty_approved REAL,
            qty_dispersed REAL
        );

        CREATE TABLE IF NOT EXISTS requisition_usage_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            requisition_id INTEGER NOT NULL REFERENCES requisitions(id) ON DELETE CASCADE,
            username TEXT NOT NULL,
            report TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS requisition_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            requisition_id INTEGER NOT NULL REFERENCES requisitions(id) ON DELETE CASCADE,
            username TEXT NOT NULL,
            filename TEXT NOT NULL,
            filedata BLOB NOT NULL,
            mimetype TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS requisition_comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            requisition_id INTEGER NOT NULL REFERENCES requisitions(id) ON DELETE CASCADE,
            username TEXT NOT NULL,
            comment TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS stock_movement_invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slip_number TEXT NOT NULL,
            username TEXT NOT NULL,
            filename TEXT NOT NULL,
            filedata BLOB NOT NULL,
            mimetype TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS cost_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL REFERENCES items(id) ON DELETE CASCADE,
            cost_before REAL NOT NULL,
            cost_after REAL NOT NULL,
            qty_delta REAL DEFAULT 0,
            reason TEXT,
            changed_by TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );
        """)
        # ── Schema migrations ──────────────────────────────────────
        for _col_sql in [
            "ALTER TABLE issuances ADD COLUMN requisition_id INTEGER REFERENCES requisitions(id)",
            "ALTER TABLE issuances ADD COLUMN requisition_line_id INTEGER REFERENCES requisition_lines(id)",
            "ALTER TABLE requisition_lines ADD COLUMN is_custom INTEGER DEFAULT 0",
            "ALTER TABLE requisition_lines ADD COLUMN custom_item_name TEXT",
            "ALTER TABLE requisition_lines ADD COLUMN custom_uom TEXT",
            "ALTER TABLE requisition_lines ADD COLUMN custom_notes TEXT",
            "ALTER TABLE requisition_lines ADD COLUMN linked_item_id INTEGER REFERENCES items(id)",
        ]:
            try:
                conn.execute(_col_sql)
            except Exception:
                pass  # column already exists

        # Older installs created requisition_lines.item_id as NOT NULL.
        # Mixed-basket requisitions store unlisted items with item_id = NULL.
        _ensure_requisition_lines_item_nullable(conn)
        _seed_demo_data(conn)


def _ensure_requisition_lines_item_nullable(conn):
    cols = conn.execute("PRAGMA table_info(requisition_lines)").fetchall()
    if not cols:
        return

    item_col = next((c for c in cols if c["name"] == "item_id"), None)
    if not item_col or item_col["notnull"] == 0:
        return

    existing = {c["name"] for c in cols}

    # SQLite cannot drop a NOT NULL constraint in place; rebuild table.
    conn.execute("PRAGMA foreign_keys = OFF")
    try:
        conn.execute("""
            CREATE TABLE requisition_lines_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                requisition_id INTEGER NOT NULL REFERENCES requisitions(id) ON DELETE CASCADE,
                item_id INTEGER REFERENCES items(id) ON DELETE CASCADE,
                qty_requested REAL NOT NULL,
                qty_approved REAL,
                qty_dispersed REAL,
                is_custom INTEGER DEFAULT 0,
                custom_item_name TEXT,
                custom_uom TEXT,
                custom_notes TEXT,
                linked_item_id INTEGER REFERENCES items(id)
            )
        """)

        conn.execute(f"""
            INSERT INTO requisition_lines_new (
                id, requisition_id, item_id, qty_requested, qty_approved, qty_dispersed,
                is_custom, custom_item_name, custom_uom, custom_notes, linked_item_id
            )
            SELECT
                id,
                requisition_id,
                item_id,
                qty_requested,
                qty_approved,
                qty_dispersed,
                {"is_custom" if "is_custom" in existing else "0"},
                {"custom_item_name" if "custom_item_name" in existing else "NULL"},
                {"custom_uom" if "custom_uom" in existing else "NULL"},
                {"custom_notes" if "custom_notes" in existing else "NULL"},
                {"linked_item_id" if "linked_item_id" in existing else "NULL"}
            FROM requisition_lines
        """)

        conn.execute("DROP TABLE requisition_lines")
        conn.execute("ALTER TABLE requisition_lines_new RENAME TO requisition_lines")
    finally:
        conn.execute("PRAGMA foreign_keys = ON")

def _seed_demo_data(conn):
    existing = conn.execute("SELECT COUNT(*) FROM properties").fetchone()[0]
    if existing > 0:
        return

    conn.execute("INSERT INTO properties (name, address, notes) VALUES (?, ?, ?)",
        ("Sandton Gardens", "12 Rivonia Rd, Sandton", "Main residential complex"))
    conn.execute("INSERT INTO properties (name, address, notes) VALUES (?, ?, ?)",
        ("Rosebank View", "45 Oxford Rd, Rosebank", "Mixed-use building"))

    conn.execute("INSERT INTO storerooms (property_id, name, location_notes) VALUES (1, 'Block A Storeroom', 'Ground floor, next to lift')")
    conn.execute("INSERT INTO storerooms (property_id, name, location_notes) VALUES (1, 'Basement Store', 'B1 level, cage 3')")
    conn.execute("INSERT INTO storerooms (property_id, name, location_notes) VALUES (2, 'Main Storeroom', 'Level 1, room 104')")

    conn.execute("INSERT INTO suppliers (name, contact, phone, email) VALUES (?, ?, ?, ?)",
        ("Makro", "Trade Desk", "011 000 1111", "trade@makro.co.za"))
    conn.execute("INSERT INTO suppliers (name, contact, phone, email) VALUES (?, ?, ?, ?)",
        ("Builders Warehouse", "Accounts", "011 000 2222", "accounts@builders.co.za"))

    items = [
        (1, "LED Bulbs (E27)", "Electrical", "units", 24, 10, 1, 18.50, "60W equivalent"),
        (1, "Toilet Rolls", "Cleaning", "rolls", 48, 20, 1, 4.20, "2-ply"),
        (1, "Bleach (5L)", "Cleaning", "bottles", 6, 3, 1, 45.00, "Domestos or equivalent"),
        (1, "AA Batteries", "Electrical", "units", 20, 8, 1, 12.00, "For remotes"),
        (2, "Air Filters", "Maintenance", "units", 4, 2, 2, 85.00, "HVAC replacement"),
        (2, "Refuse Bags (100L)", "Cleaning", "rolls", 5, 2, 1, 62.00, "Heavy duty"),
        (2, "Cable Ties", "Maintenance", "packs", 8, 3, 2, 24.00, "Assorted sizes"),
        (3, "Paint (White 20L)", "Maintenance", "tins", 3, 1, 2, 320.00, "Interior PVA"),
        (3, "Shower Heads", "Plumbing", "units", 5, 2, 2, 145.00, "Standard chrome"),
        (3, "Plumber's Tape", "Plumbing", "rolls", 12, 4, 2, 8.50, "PTFE thread seal"),
    ]
    conn.executemany(
        "INSERT INTO items (storeroom_id, name, category, uom, qty, min_qty, supplier_id, unit_cost, description) VALUES (?,?,?,?,?,?,?,?,?)",
        items
    )

    issuances = [
        (1, "John Dlamini", "Sipho M", 4, "2026-01-15", "Flat 4A bulb replacement"),
        (2, "Thandi Mokoena", "Sipho M", 12, "2026-01-22", "Unit 7B restock"),
        (3, "Lerato Khumalo", "Sipho M", 2, "2026-02-05", "Deep clean"),
        (4, "John Dlamini", "Ayanda N", 8, "2026-02-10", "Remote batteries"),
        (5, "Contractor - AC Fix", "Ayanda N", 2, "2026-02-18", "HVAC service"),
        (8, "Painter - Joe", "Sipho M", 1, "2026-03-01", "Touch-up Unit 3"),
        (9, "Plumber - Tom", "Ayanda N", 1, "2026-03-10", "Unit 12 shower"),
        (2, "Thandi Mokoena", "Sipho M", 24, "2026-03-15", "Monthly restock"),
    ]
    conn.executemany(
        "INSERT INTO issuances (item_id, recipient, issued_by, qty, issued_date, note) VALUES (?,?,?,?,?,?)",
        issuances
    )

# ── Properties ────────────────────────────────────────────────
def get_properties():
    with get_conn() as conn:
        return pd.read_sql("SELECT * FROM properties ORDER BY name", conn)

def add_property(name, address, notes):
    with get_conn() as conn:
        conn.execute("INSERT INTO properties (name, address, notes) VALUES (?,?,?)", (name, address, notes))

def update_property(id, name, address, notes):
    with get_conn() as conn:
        conn.execute("UPDATE properties SET name=?, address=?, notes=? WHERE id=?", (name, address, notes, id))

def delete_property(id):
    with get_conn() as conn:
        conn.execute("DELETE FROM properties WHERE id=?", (id,))

# ── Storerooms ────────────────────────────────────────────────
def get_storerooms(property_id=None):
    q = """
        SELECT s.*, p.name as property_name,
               COUNT(i.id) as item_count,
               COALESCE(SUM(i.qty), 0) as total_units
        FROM storerooms s
        JOIN properties p ON p.id = s.property_id
        LEFT JOIN items i ON i.storeroom_id = s.id
    """
    params = []
    if property_id:
        q += " WHERE s.property_id = ?"
        params.append(property_id)
    q += " GROUP BY s.id ORDER BY p.name, s.name"
    with get_conn() as conn:
        return pd.read_sql(q, conn, params=params)

def add_storeroom(property_id, name, location_notes):
    with get_conn() as conn:
        conn.execute("INSERT INTO storerooms (property_id, name, location_notes) VALUES (?,?,?)",
                     (property_id, name, location_notes))

def update_storeroom(id, name, location_notes):
    with get_conn() as conn:
        conn.execute("UPDATE storerooms SET name=?, location_notes=? WHERE id=?", (name, location_notes, id))

def delete_storeroom(id):
    with get_conn() as conn:
        conn.execute("DELETE FROM storerooms WHERE id=?", (id,))

# ── Suppliers ────────────────────────────────────────────────
def get_suppliers():
    with get_conn() as conn:
        return pd.read_sql("SELECT * FROM suppliers ORDER BY name", conn)

def add_supplier(name, contact, phone, email, notes):
    with get_conn() as conn:
        conn.execute("INSERT INTO suppliers (name, contact, phone, email, notes) VALUES (?,?,?,?,?)",
                     (name, contact, phone, email, notes))

def update_supplier(id, name, contact, phone, email, notes):
    with get_conn() as conn:
        conn.execute("UPDATE suppliers SET name=?,contact=?,phone=?,email=?,notes=? WHERE id=?",
                     (name, contact, phone, email, notes, id))

def delete_supplier(id):
    with get_conn() as conn:
        conn.execute("DELETE FROM suppliers WHERE id=?", (id,))

# ── Items ────────────────────────────────────────────────────
def get_items(storeroom_id=None, property_id=None, low_stock_only=False):
    q = """
        SELECT i.*, s.name as storeroom_name, p.name as property_name,
               p.id as property_id, s.property_id as s_property_id,
               sup.name as supplier_name,
               CASE WHEN i.qty = 0 THEN 'Out of stock'
                    WHEN i.qty <= i.min_qty THEN 'Low'
                    ELSE 'OK' END as status,
               (i.qty * i.unit_cost) as stock_value
        FROM items i
        JOIN storerooms s ON s.id = i.storeroom_id
        JOIN properties p ON p.id = s.property_id
        LEFT JOIN suppliers sup ON sup.id = i.supplier_id
        WHERE 1=1
    """
    params = []
    if storeroom_id:
        q += " AND i.storeroom_id = ?"
        params.append(storeroom_id)
    if property_id:
        q += " AND p.id = ?"
        params.append(property_id)
    if low_stock_only:
        q += " AND i.qty <= i.min_qty"
    q += " ORDER BY p.name, s.name, i.category, i.name"
    with get_conn() as conn:
        return pd.read_sql(q, conn, params=params)

def add_item(storeroom_id, name, category, uom, qty, min_qty, supplier_id, unit_cost, description, added_by=None):
    with get_conn() as conn:
        cur = conn.execute("""INSERT INTO items
            (storeroom_id, name, category, uom, qty, min_qty, supplier_id, unit_cost, description, updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,datetime('now'))""",
            (storeroom_id, name, category, uom, qty, min_qty, supplier_id or None, unit_cost, description))
        if unit_cost and unit_cost > 0:
            conn.execute(
                "INSERT INTO cost_history (item_id, cost_before, cost_after, qty_delta, reason, changed_by) VALUES (?,?,?,?,?,?)",
                (cur.lastrowid, 0.0, unit_cost, qty, 'Initial stock load', added_by))

def update_item(id, storeroom_id, name, category, uom, qty, min_qty, supplier_id, unit_cost, description):
    with get_conn() as conn:
        conn.execute("""UPDATE items SET storeroom_id=?, name=?, category=?, uom=?, qty=?,
            min_qty=?, supplier_id=?, unit_cost=?, description=?, updated_at=datetime('now')
            WHERE id=?""",
            (storeroom_id, name, category, uom, qty, min_qty, supplier_id or None, unit_cost, description, id))

def adjust_qty(item_id, delta, new_unit_cost=None, changed_by=None, reason=None):
    """Adjust quantity and optionally update unit cost using weighted average costing.

    When adding stock (delta > 0) with a new_unit_cost, the unit cost is recalculated
    as a weighted average:
        new_cost = ((old_qty × old_cost) + (delta × new_unit_cost)) / new_total_qty

    When only setting cost (delta == 0) or removing stock (delta < 0), the cost is
    set directly to new_unit_cost if provided.
    """
    with get_conn() as conn:
        row = conn.execute("SELECT qty, unit_cost FROM items WHERE id=?", (item_id,)).fetchone()
        qty_before = float(row["qty"]) if row else 0.0
        cost_before = float(row["unit_cost"]) if row else 0.0
        conn.execute("UPDATE items SET qty = MAX(0, qty + ?), updated_at=datetime('now') WHERE id=?",
                     (delta, item_id))
        if new_unit_cost is not None:
            if delta > 0 and qty_before > 0:
                # Weighted average costing: blend old and new cost
                total_qty = qty_before + delta
                weighted_cost = ((qty_before * cost_before) + (delta * new_unit_cost)) / total_qty
                conn.execute("UPDATE items SET unit_cost=?, updated_at=datetime('now') WHERE id=?",
                             (round(weighted_cost, 2), item_id))
            else:
                # Setting cost directly: first-time cost, zero-qty restock, or removal
                conn.execute("UPDATE items SET unit_cost=?, updated_at=datetime('now') WHERE id=?",
                             (new_unit_cost, item_id))
        row_after = conn.execute("SELECT qty, unit_cost FROM items WHERE id=?", (item_id,)).fetchone()
        qty_after = float(row_after["qty"]) if row_after else 0.0
        cost_after = float(row_after["unit_cost"]) if row_after else 0.0
        # Log cost change if cost actually changed
        if cost_after != cost_before:
            conn.execute(
                "INSERT INTO cost_history (item_id, cost_before, cost_after, qty_delta, reason, changed_by) VALUES (?,?,?,?,?,?)",
                (item_id, cost_before, cost_after, delta, reason, changed_by))
    return qty_before, qty_after, cost_before, cost_after

def delete_item(id):
    with get_conn() as conn:
        conn.execute("DELETE FROM items WHERE id=?", (id,))

# ── Issuances ────────────────────────────────────────────────
def get_issuances(property_id=None, storeroom_id=None, month=None, recipient=None):
    q = """
        SELECT iss.*, i.name as item_name, i.uom, s.name as storeroom_name, p.name as property_name
        FROM issuances iss
        JOIN items i ON i.id = iss.item_id
        JOIN storerooms s ON s.id = i.storeroom_id
        JOIN properties p ON p.id = s.property_id
        WHERE 1=1
    """
    params = []
    if property_id:
        q += " AND p.id = ?"
        params.append(property_id)
    if storeroom_id:
        q += " AND s.id = ?"
        params.append(storeroom_id)
    if month:
        q += " AND strftime('%Y-%m', iss.issued_date) = ?"
        params.append(month)
    if recipient:
        q += " AND LOWER(iss.recipient) LIKE ?"
        params.append(f"%{recipient.lower()}%")
    q += " ORDER BY iss.issued_date DESC, iss.id DESC"
    with get_conn() as conn:
        return pd.read_sql(q, conn, params=params)


def get_issued_to_user(username, property_id=None, date_from=None, date_to=None):
    """Return issuances where recipient is the given user, with requisition usage-report status."""
    q = """
        SELECT iss.id as issuance_id,
               iss.issued_date,
               iss.qty,
               iss.note,
               iss.issued_by,
               iss.recipient,
               i.name as item_name,
               i.uom,
               s.name as storeroom_name,
               p.name as property_name,
               iss.requisition_id,
               r.ref_number,
               r.purpose,
               CASE
                 WHEN iss.requisition_id IS NOT NULL AND EXISTS (
                     SELECT 1
                     FROM requisition_usage_reports ur
                     WHERE ur.requisition_id = iss.requisition_id
                       AND LOWER(ur.username) = LOWER(?)
                 ) THEN 1
                 ELSE 0
               END as usage_reported
        FROM issuances iss
        JOIN items i ON i.id = iss.item_id
        JOIN storerooms s ON s.id = i.storeroom_id
        JOIN properties p ON p.id = s.property_id
        LEFT JOIN requisitions r ON r.id = iss.requisition_id
        WHERE LOWER(iss.recipient) = LOWER(?)
    """
    params = [username, username]
    if property_id:
        q += " AND p.id = ?"
        params.append(property_id)
    if date_from:
        q += " AND date(iss.issued_date) >= ?"
        params.append(str(date_from))
    if date_to:
        q += " AND date(iss.issued_date) <= ?"
        params.append(str(date_to))
    q += " ORDER BY iss.issued_date DESC, iss.id DESC"
    with get_conn() as conn:
        return pd.read_sql(q, conn, params=params)

def add_issuance(item_id, recipient, issued_by, qty, issued_date, note):
    with get_conn() as conn:
        item = conn.execute("SELECT qty FROM items WHERE id=?", (item_id,)).fetchone()
        if not item or item["qty"] < qty:
            raise ValueError(f"Insufficient stock. Available: {item['qty'] if item else 0}")
        conn.execute("INSERT INTO issuances (item_id, recipient, issued_by, qty, issued_date, note) VALUES (?,?,?,?,?,?)",
                     (item_id, recipient, issued_by, qty, issued_date, note))
        conn.execute("UPDATE items SET qty = MAX(0, qty - ?), updated_at=datetime('now') WHERE id=?", (qty, item_id))

# ── Reconciliation ────────────────────────────────────────────
def get_reconciliation_history(storeroom_id=None, month=None):
    q = """
        SELECT r.*, s.name as storeroom_name, p.name as property_name,
               COUNT(rl.id) as line_count,
               SUM(CASE WHEN rl.diff < 0 THEN 1 ELSE 0 END) as shorts,
               SUM(CASE WHEN rl.diff > 0 THEN 1 ELSE 0 END) as surplus
        FROM reconciliations r
        JOIN storerooms s ON s.id = r.storeroom_id
        JOIN properties p ON p.id = s.property_id
        LEFT JOIN reconciliation_lines rl ON rl.reconciliation_id = r.id
        WHERE 1=1
    """
    params = []
    if storeroom_id:
        q += " AND r.storeroom_id = ?"
        params.append(storeroom_id)
    if month:
        q += " AND strftime('%Y-%m', r.recon_date) = ?"
        params.append(month)
    q += " GROUP BY r.id ORDER BY r.recon_date DESC"
    with get_conn() as conn:
        return pd.read_sql(q, conn, params=params)

def get_reconciliation_lines(reconciliation_id):
    with get_conn() as conn:
        return pd.read_sql("""
            SELECT rl.*, i.name as item_name, i.uom
            FROM reconciliation_lines rl
            JOIN items i ON i.id = rl.item_id
            WHERE rl.reconciliation_id = ?
        """, conn, params=[reconciliation_id])

def save_reconciliation(storeroom_id, performed_by, recon_date, notes, lines):
    """lines = list of (item_id, recorded_qty, counted_qty)"""
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO reconciliations (storeroom_id, performed_by, recon_date, notes) VALUES (?,?,?,?)",
            (storeroom_id, performed_by, recon_date, notes)
        )
        recon_id = cur.lastrowid
        for item_id, recorded_qty, counted_qty in lines:
            diff = counted_qty - recorded_qty
            conn.execute(
                "INSERT INTO reconciliation_lines (reconciliation_id, item_id, recorded_qty, counted_qty, diff) VALUES (?,?,?,?,?)",
                (recon_id, item_id, recorded_qty, counted_qty, diff)
            )
            conn.execute("UPDATE items SET qty=?, updated_at=datetime('now') WHERE id=?", (counted_qty, item_id))

# ── Analytics ────────────────────────────────────────────────
def get_monthly_summary(property_id=None, months=6):
    with get_conn() as conn:
        q = """
            SELECT strftime('%Y-%m', issued_date) as month,
                   COUNT(*) as transactions,
                   SUM(iss.qty) as units_issued,
                   COUNT(DISTINCT iss.recipient) as recipients
            FROM issuances iss
            JOIN items i ON i.id = iss.item_id
            JOIN storerooms s ON s.id = i.storeroom_id
            WHERE 1=1
        """
        params = []
        if property_id:
            q += " AND s.property_id = ?"
            params.append(property_id)
        q += f" AND issued_date >= date('now', '-{months} months') GROUP BY month ORDER BY month"
        return pd.read_sql(q, conn, params=params)

def get_stock_value_by_storeroom(property_id=None):
    with get_conn() as conn:
        q = """
            SELECT s.name as storeroom, p.name as property,
                   COUNT(i.id) as items,
                   SUM(i.qty * i.unit_cost) as total_value,
                   SUM(CASE WHEN i.qty=0 THEN 1 ELSE 0 END) as out_of_stock,
                   SUM(CASE WHEN i.qty>0 AND i.qty<=i.min_qty THEN 1 ELSE 0 END) as low_stock
            FROM storerooms s
            JOIN properties p ON p.id = s.property_id
            LEFT JOIN items i ON i.storeroom_id = s.id
            WHERE 1=1
        """
        params = []
        if property_id:
            q += " AND p.id = ?"
            params.append(property_id)
        q += " GROUP BY s.id ORDER BY p.name, s.name"
        return pd.read_sql(q, conn, params=params)

def get_top_issued_items(property_id=None, months=3):
    with get_conn() as conn:
        q = """
            SELECT i.name as item, i.uom, s.name as storeroom, p.name as property,
                   SUM(iss.qty) as total_issued, COUNT(iss.id) as transactions
            FROM issuances iss
            JOIN items i ON i.id = iss.item_id
            JOIN storerooms s ON s.id = i.storeroom_id
            JOIN properties p ON p.id = s.property_id
            WHERE issued_date >= date('now', '-? months')
        """
        params = [months]
        if property_id:
            q += " AND p.id = ?"
            params.append(property_id)
        q += " GROUP BY i.id ORDER BY total_issued DESC LIMIT 10"
        return pd.read_sql(q, conn, params=params)

# ── Requisitions ──────────────────────────────────────────────

def _gen_ref():
    from datetime import datetime
    import random
    return f"REQ-{datetime.now().strftime('%Y%m%d')}-{random.randint(100,999)}"

def create_requisition(requested_by, role, property_id, storeroom_id, purpose, urgency, lines, custom_lines=None):
    """
    lines        = list of (item_id, qty_requested)  — existing stock items
    custom_lines = list of {name, qty, uom, notes}   — unlisted / procurement items
    """
    ref = _gen_ref()
    with get_conn() as conn:
        cur = conn.execute("""
            INSERT INTO requisitions
              (ref_number, requested_by, requested_by_role, property_id, storeroom_id, purpose, urgency, status)
            VALUES (?,?,?,?,?,?,?,'Pending')""",
            (ref, requested_by, role, property_id, storeroom_id, purpose, urgency))
        req_id = cur.lastrowid
        for item_id, qty in (lines or []):
            conn.execute("""
                INSERT INTO requisition_lines (requisition_id, item_id, qty_requested, is_custom)
                VALUES (?,?,?,0)""", (req_id, item_id, qty))
        for cl in (custom_lines or []):
            conn.execute("""
                INSERT INTO requisition_lines
                  (requisition_id, item_id, qty_requested, is_custom, custom_item_name, custom_uom, custom_notes)
                VALUES (?,NULL,?,1,?,?,?)""",
                (req_id, cl["qty"], cl["name"], cl.get("uom", "units"), cl.get("notes", "")))
    return ref

def get_requisitions(requested_by=None, status=None, property_id=None, date_from=None, date_to=None):
    q = """
        SELECT r.*,
               p.name as property_name,
               s.name as storeroom_name,
               COUNT(rl.id) as line_count
        FROM requisitions r
        LEFT JOIN properties p ON p.id = r.property_id
        LEFT JOIN storerooms s ON s.id = r.storeroom_id
        LEFT JOIN requisition_lines rl ON rl.requisition_id = r.id
        WHERE 1=1
    """
    params = []
    if requested_by:
        q += " AND r.requested_by = ?"
        params.append(requested_by)
    if status:
        q += " AND r.status = ?"
        params.append(status)
    if property_id:
        q += " AND r.property_id = ?"
        params.append(property_id)
    if date_from:
        q += " AND date(r.created_at) >= ?"
        params.append(str(date_from))
    if date_to:
        q += " AND date(r.created_at) <= ?"
        params.append(str(date_to))
    q += " GROUP BY r.id ORDER BY r.created_at DESC"
    with get_conn() as conn:
        return pd.read_sql(q, conn, params=params)

def get_requisition_lines(requisition_id):
    with get_conn() as conn:
        return pd.read_sql("""
            SELECT rl.id, rl.requisition_id, rl.item_id, rl.qty_requested,
                   rl.qty_approved, rl.qty_dispersed,
                   rl.is_custom, rl.custom_item_name, rl.custom_uom, rl.custom_notes,
                   rl.linked_item_id,
                   COALESCE(i.name, rl.custom_item_name) as item_name,
                   COALESCE(i.uom,  rl.custom_uom)       as uom,
                   COALESCE(i.qty, 0)                    as stock_qty,
                   COALESCE(i.unit_cost, 0)              as unit_cost,
                   s.name as storeroom_name, p.name as property_name
            FROM requisition_lines rl
            LEFT JOIN items i ON i.id = rl.item_id
            LEFT JOIN storerooms s ON s.id = i.storeroom_id
            LEFT JOIN properties p ON p.id = s.property_id
            WHERE rl.requisition_id = ?
        """, conn, params=[requisition_id])

def review_requisition(req_id, reviewed_by, action, review_note, approved_qtys):
    """
    action: 'Approved' or 'Rejected'
    approved_qtys: dict of {line_id: qty_approved}
    """
    with get_conn() as conn:
        conn.execute("""
            UPDATE requisitions
            SET status=?, reviewed_by=?, reviewed_at=datetime('now'), review_note=?
            WHERE id=?""",
            (action, reviewed_by, review_note, req_id))
        if action == "Approved":
            for line_id, qty in approved_qtys.items():
                conn.execute(
                    "UPDATE requisition_lines SET qty_approved=? WHERE id=?",
                    (qty, line_id))

def disperse_requisition(req_id, dispersed_by):
    """Deducts approved quantities from stock and records issuances."""
    with get_conn() as conn:
        req = conn.execute("SELECT * FROM requisitions WHERE id=?", (req_id,)).fetchone()
        if not req or req["status"] != "Approved":
            raise ValueError("Requisition must be Approved before dispersal.")
        lines = conn.execute("""
            SELECT rl.*, i.qty as stock_qty, i.name as item_name, i.uom
            FROM requisition_lines rl
            JOIN items i ON i.id = rl.item_id
            WHERE rl.requisition_id = ?
        """, (req_id,)).fetchall()
        for line in lines:
            approved = line["qty_approved"] or 0
            if approved <= 0:
                continue
            if line["stock_qty"] < approved:
                raise ValueError(
                    f"Insufficient stock for '{line['item_name']}'. "
                    f"Available: {line['stock_qty']}, requested: {approved}")
        for line in lines:
            approved = line["qty_approved"] or 0
            if approved <= 0:
                continue
            conn.execute(
                "UPDATE items SET qty = qty - ?, updated_at=datetime('now') WHERE id=?",
                (approved, line["item_id"]))
            conn.execute("""
                INSERT INTO issuances (item_id, recipient, issued_by, qty, issued_date, note)
                VALUES (?, ?, ?, ?, date('now'), ?)""",
                (line["item_id"], req["requested_by"], dispersed_by,
                 approved, f"Requisition {req['ref_number']}"))
            conn.execute(
                "UPDATE requisition_lines SET qty_dispersed=? WHERE id=?",
                (approved, line["id"]))
        conn.execute("""
            UPDATE requisitions
            SET status='Dispersed', dispersed_by=?, dispersed_at=datetime('now')
            WHERE id=?""",
            (dispersed_by, req_id))

def cancel_requisition(req_id, cancelled_by):
    with get_conn() as conn:
        conn.execute("""
            UPDATE requisitions SET status='Cancelled',
            reviewed_by=?, reviewed_at=datetime('now'), review_note='Cancelled by user'
            WHERE id=? AND status IN ('Pending','Approved')""",
            (cancelled_by, req_id))

def get_requisition_counts():
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT status, COUNT(*) as cnt FROM requisitions GROUP BY status
        """).fetchall()
        return {r["status"]: r["cnt"] for r in rows}


def get_approved_requisitions_for_issuing(property_id=None):
    """Return Approved or Partially Issued requisitions ready for stock issuing."""
    q = """
        SELECT r.*, p.name as property_name, s.name as storeroom_name
        FROM requisitions r
        LEFT JOIN properties p ON p.id = r.property_id
        LEFT JOIN storerooms s ON s.id = r.storeroom_id
        WHERE r.status IN ('Approved', 'Partially Issued')
    """
    params = []
    if property_id:
        q += " AND r.property_id = ?"
        params.append(property_id)
    q += " ORDER BY r.created_at DESC"
    with get_conn() as conn:
        return pd.read_sql(q, conn, params=params)


def get_requisition_lines_remaining(requisition_id):
    """Return stocked lines with remaining qty to issue (custom/procurement lines excluded)."""
    with get_conn() as conn:
        return pd.read_sql("""
            SELECT rl.id, rl.requisition_id, rl.item_id, rl.qty_requested,
                   i.name as item_name, i.uom, i.qty as stock_qty, i.unit_cost,
                   COALESCE(rl.qty_approved, 0) as qty_approved,
                   COALESCE(rl.qty_dispersed, 0) as qty_dispersed,
                   (COALESCE(rl.qty_approved, 0) - COALESCE(rl.qty_dispersed, 0)) as qty_remaining
            FROM requisition_lines rl
            JOIN items i ON i.id = rl.item_id
            WHERE rl.requisition_id = ?
              AND COALESCE(rl.is_custom, 0) = 0
              AND COALESCE(rl.qty_approved, 0) > 0
        """, conn, params=[requisition_id])


def get_requisition_custom_lines_remaining(requisition_id):
    """Return unlisted/custom lines that have not yet been fully marked as fulfilled."""
    with get_conn() as conn:
        return pd.read_sql("""
            SELECT rl.id, rl.requisition_id, rl.custom_item_name as item_name,
                   COALESCE(rl.custom_uom, 'units') as uom,
                   COALESCE(rl.custom_notes, '') as notes,
                   COALESCE(rl.qty_approved, 0) as qty_approved,
                   COALESCE(rl.qty_dispersed, 0) as qty_dispersed,
                   (COALESCE(rl.qty_approved, 0) - COALESCE(rl.qty_dispersed, 0)) as qty_remaining
            FROM requisition_lines rl
            WHERE rl.requisition_id = ?
              AND COALESCE(rl.is_custom, 0) = 1
              AND COALESCE(rl.qty_approved, 0) > 0
        """, conn, params=[requisition_id])


def mark_custom_line_fulfilled(line_id, issued_by, req_id,
                               storeroom_id=None, category="General",
                               unit_cost=0.0, issued_date=None, note=None):
    """Mark a custom requisition line as fulfilled.
    If storeroom_id is provided, the item is added to the stock catalogue (qty=0)
    and an issuance record is created so it appears in future selectboxes.
    Returns (new_status, item_id or None).
    """
    from datetime import date as _date
    with get_conn() as conn:
        line = conn.execute(
            """SELECT rl.*, r.requested_by, r.ref_number
               FROM requisition_lines rl
               JOIN requisitions r ON r.id = rl.requisition_id
               WHERE rl.id=? AND COALESCE(rl.is_custom,0)=1""",
            (line_id,)
        ).fetchone()
        if not line:
            raise ValueError("Custom line not found.")

        qty = line["qty_approved"] or 0
        item_id = None

        if storeroom_id:
            # Add to stock catalogue with qty=0 (item is being issued directly to recipient)
            conn.execute(
                """INSERT INTO items
                     (storeroom_id, name, category, uom, qty, min_qty,
                      unit_cost, description, created_at, updated_at)
                   VALUES (?, ?, ?, ?, 0, 0, ?, ?, datetime('now'), datetime('now'))""",
                (
                    storeroom_id,
                    line["custom_item_name"],
                    category,
                    line["custom_uom"] or "units",
                    unit_cost,
                    line["custom_notes"] or "",
                )
            )
            item_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

            # Create issuance record so the item appears in issuance history
            conn.execute(
                """INSERT INTO issuances
                     (item_id, recipient, issued_by, qty, issued_date, note,
                      requisition_id, requisition_line_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    item_id,
                    line["requested_by"],
                    issued_by,
                    qty,
                    issued_date or str(_date.today()),
                    note or f"Requisition {line['ref_number']}",
                    req_id,
                    line_id,
                )
            )

        # Mark line as fully dispersed
        conn.execute(
            "UPDATE requisition_lines SET qty_dispersed=qty_approved WHERE id=?",
            (line_id,)
        )

        # Recalculate requisition status
        totals = conn.execute("""
            SELECT SUM(COALESCE(qty_approved,0)) as total_approved,
                   SUM(COALESCE(qty_dispersed,0)) as total_dispersed
            FROM requisition_lines WHERE requisition_id=?
        """, (req_id,)).fetchone()
        total_approved = totals["total_approved"] or 0
        total_dispersed = totals["total_dispersed"] or 0
        new_status = "Issued" if total_approved > 0 and total_dispersed >= total_approved else "Partially Issued"
        conn.execute(
            "UPDATE requisitions SET status=?, dispersed_by=?, dispersed_at=datetime('now') WHERE id=?",
            (new_status, issued_by, req_id)
        )
        return new_status, item_id


def issue_against_requisition(req_id, issued_by, issued_date, note, lines_to_issue):
    """
    Issue stock against an approved requisition.
    lines_to_issue: list of (line_id, item_id, qty_to_issue)
    Returns dict with status, issued lines, and restock guidance.
    """
    with get_conn() as conn:
        req = conn.execute("SELECT * FROM requisitions WHERE id=?", (req_id,)).fetchone()
        if not req or req["status"] not in ("Approved", "Partially Issued"):
            raise ValueError("Requisition must be Approved before issuing.")

        # Validate approved remaining first (stock shortfalls are handled by partial issue)
        for line_id, item_id, qty in lines_to_issue:
            if qty <= 0:
                continue
            line = conn.execute(
                "SELECT qty_approved, qty_dispersed FROM requisition_lines WHERE id=?",
                (line_id,)
            ).fetchone()
            if not line:
                continue
            remaining = (line["qty_approved"] or 0) - (line["qty_dispersed"] or 0)
            if qty > remaining:
                item_row = conn.execute("SELECT name FROM items WHERE id=?", (item_id,)).fetchone()
                name = item_row["name"] if item_row else str(item_id)
                raise ValueError(
                    f"Cannot issue {qty} of '{name}' — only {remaining} remaining from approved qty."
                )

        issued_lines = []
        shortfalls = []

        # Execute with auto-partial issuing based on available stock
        for line_id, item_id, qty in lines_to_issue:
            if qty <= 0:
                continue
            line = conn.execute(
                """
                SELECT rl.qty_approved, rl.qty_dispersed, i.name as item_name, i.uom, i.qty as stock_qty
                FROM requisition_lines rl
                JOIN items i ON i.id = rl.item_id
                WHERE rl.id=?
                """,
                (line_id,)
            ).fetchone()
            if not line:
                continue

            remaining = (line["qty_approved"] or 0) - (line["qty_dispersed"] or 0)
            qty_capped_to_remaining = min(float(qty), float(remaining))
            issue_qty = min(qty_capped_to_remaining, float(line["stock_qty"] or 0))
            short_qty = max(0.0, qty_capped_to_remaining - issue_qty)

            if issue_qty <= 0:
                shortfalls.append({
                    "item_id": item_id,
                    "item_name": line["item_name"],
                    "uom": line["uom"],
                    "requested_now": qty_capped_to_remaining,
                    "issued_now": 0.0,
                    "short_now": short_qty,
                    "stock_available": float(line["stock_qty"] or 0),
                })
                continue

            conn.execute(
                "UPDATE items SET qty = MAX(0, qty - ?), updated_at=datetime('now') WHERE id=?",
                (issue_qty, item_id)
            )
            conn.execute("""
                INSERT INTO issuances
                  (item_id, recipient, issued_by, qty, issued_date, note, requisition_id, requisition_line_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (item_id, req["requested_by"], issued_by, issue_qty, issued_date,
                 note or f"Requisition {req['ref_number']}", req_id, line_id)
            )
            conn.execute(
                "UPDATE requisition_lines SET qty_dispersed = COALESCE(qty_dispersed, 0) + ? WHERE id=?",
                (issue_qty, line_id)
            )

            issued_lines.append({
                "line_id": line_id,
                "item_id": item_id,
                "item_name": line["item_name"],
                "uom": line["uom"],
                "qty": issue_qty,
            })
            if short_qty > 0:
                shortfalls.append({
                    "item_id": item_id,
                    "item_name": line["item_name"],
                    "uom": line["uom"],
                    "requested_now": qty_capped_to_remaining,
                    "issued_now": issue_qty,
                    "short_now": short_qty,
                    "stock_available": float(line["stock_qty"] or 0),
                })

        # Determine new status
        totals = conn.execute("""
            SELECT SUM(COALESCE(qty_approved, 0)) as total_approved,
                   SUM(COALESCE(qty_dispersed, 0)) as total_dispersed
            FROM requisition_lines WHERE requisition_id=?
        """, (req_id,)).fetchone()
        total_approved = totals["total_approved"] or 0
        total_dispersed = totals["total_dispersed"] or 0
        if total_approved > 0 and total_dispersed >= total_approved:
            new_status = "Issued"
        elif total_dispersed > 0:
            new_status = "Partially Issued"
        else:
            new_status = req["status"]

        conn.execute(
            "UPDATE requisitions SET status=?, dispersed_by=?, dispersed_at=datetime('now') WHERE id=?",
            (new_status, issued_by, req_id)
        )

        restock_rows = conn.execute(
            """
            SELECT i.id as item_id, i.name as item_name, i.uom, i.qty as stock_available,
                   (COALESCE(rl.qty_approved, 0) - COALESCE(rl.qty_dispersed, 0)) as qty_remaining
            FROM requisition_lines rl
            JOIN items i ON i.id = rl.item_id
            WHERE rl.requisition_id = ?
              AND (COALESCE(rl.qty_approved, 0) - COALESCE(rl.qty_dispersed, 0)) > 0
            """,
            (req_id,)
        ).fetchall()
        restock_needed = []
        for r in restock_rows:
            need_to_add = max(0.0, float(r["qty_remaining"] or 0) - float(r["stock_available"] or 0))
            restock_needed.append({
                "item_id": r["item_id"],
                "item_name": r["item_name"],
                "uom": r["uom"],
                "remaining_to_issue": float(r["qty_remaining"] or 0),
                "stock_available": float(r["stock_available"] or 0),
                "need_to_add": need_to_add,
            })

        return {
            "status": new_status,
            "issued_lines": issued_lines,
            "shortfalls": shortfalls,
            "restock_needed": restock_needed,
        }
