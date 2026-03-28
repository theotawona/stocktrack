"""
Integration tests for database.py.
Uses a temporary SQLite file so the production DB is never touched.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import tempfile
import os

# Point the DB to a temp file before importing database
_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp.close()
os.environ["STOCKTRACK_TEST_DB"] = _tmp.name

import database as db

# Monkey-patch DB_PATH for tests
db.DB_PATH = Path(_tmp.name)


@pytest.fixture(autouse=True)
def fresh_db():
    """Re-create schema before every test; wipe after."""
    if Path(_tmp.name).exists():
        os.remove(_tmp.name)
    db.init_db()
    yield
    if Path(_tmp.name).exists():
        os.remove(_tmp.name)


# ── Properties ────────────────────────────────────────────────
class TestProperties:
    def test_get_seeded_properties(self):
        props = db.get_properties()
        assert not props.empty
        assert "name" in props.columns

    def test_add_property(self):
        before = len(db.get_properties())
        db.add_property("Test Block", "1 Test St", "notes")
        after = len(db.get_properties())
        assert after == before + 1

    def test_update_property(self):
        props = db.get_properties()
        pid   = int(props.iloc[0]["id"])
        db.update_property(pid, "Renamed", "New Addr", "New note")
        updated = db.get_properties()
        row = updated[updated["id"] == pid].iloc[0]
        assert row["name"] == "Renamed"

    def test_delete_property(self):
        db.add_property("ToDelete", "", "")
        props = db.get_properties()
        pid   = int(props[props["name"] == "ToDelete"]["id"].values[0])
        db.delete_property(pid)
        after = db.get_properties()
        assert pid not in after["id"].values


# ── Storerooms ────────────────────────────────────────────────
class TestStorerooms:
    def _prop_id(self):
        return int(db.get_properties().iloc[0]["id"])

    def test_get_storerooms(self):
        rooms = db.get_storerooms()
        assert not rooms.empty

    def test_add_storeroom(self):
        pid    = self._prop_id()
        before = len(db.get_storerooms(pid))
        db.add_storeroom(pid, "New Room", "Level 2")
        after  = len(db.get_storerooms(pid))
        assert after == before + 1

    def test_update_storeroom(self):
        pid  = self._prop_id()
        db.add_storeroom(pid, "EditMe", "Old loc")
        rooms = db.get_storerooms(pid)
        rid   = int(rooms[rooms["name"] == "EditMe"]["id"].values[0])
        db.update_storeroom(rid, "Renamed Room", "New loc")
        rows = db.get_storerooms(pid)
        row  = rows[rows["id"] == rid].iloc[0]
        assert row["name"] == "Renamed Room"


# ── Items ─────────────────────────────────────────────────────
class TestItems:
    def _storeroom_id(self):
        return int(db.get_storerooms().iloc[0]["id"])

    def test_get_items(self):
        items = db.get_items()
        assert not items.empty

    def test_add_item(self):
        sid    = self._storeroom_id()
        before = len(db.get_items(storeroom_id=sid))
        db.add_item(sid, "Test Item", "General", "units", 10, 2, None, 5.0, "desc")
        after  = len(db.get_items(storeroom_id=sid))
        assert after == before + 1

    def test_item_status_ok(self):
        items = db.get_items()
        ok_items = items[items["qty"] > items["min_qty"]]
        assert all(ok_items["status"] == "OK")

    def test_item_status_low(self):
        sid = self._storeroom_id()
        db.add_item(sid, "LowItem", "General", "units", 1, 5, None, 0, "")
        items = db.get_items(storeroom_id=sid)
        low_row = items[items["name"] == "LowItem"]
        assert not low_row.empty
        assert low_row.iloc[0]["status"] == "Low"

    def test_item_status_out(self):
        sid = self._storeroom_id()
        db.add_item(sid, "OutItem", "General", "units", 0, 2, None, 0, "")
        items = db.get_items(storeroom_id=sid)
        out_row = items[items["name"] == "OutItem"]
        assert not out_row.empty
        assert out_row.iloc[0]["status"] == "Out of stock"

    def test_adjust_qty(self):
        sid  = self._storeroom_id()
        db.add_item(sid, "AdjItem", "General", "units", 10, 1, None, 0, "")
        item = db.get_items(storeroom_id=sid)
        item = item[item["name"] == "AdjItem"].iloc[0]
        iid  = int(item["id"])
        db.adjust_qty(iid, -3)
        updated = db.get_items(storeroom_id=sid)
        row     = updated[updated["id"] == iid].iloc[0]
        assert row["qty"] == 7

    def test_adjust_qty_cannot_go_negative(self):
        sid = self._storeroom_id()
        db.add_item(sid, "ZeroItem", "General", "units", 2, 1, None, 0, "")
        item = db.get_items(storeroom_id=sid)
        iid  = int(item[item["name"] == "ZeroItem"]["id"].values[0])
        db.adjust_qty(iid, -100)
        row = db.get_items(storeroom_id=sid)
        row = row[row["id"] == iid].iloc[0]
        assert row["qty"] == 0  # clamped to 0

    def test_low_stock_filter(self):
        items = db.get_items(low_stock_only=True)
        assert all(items["qty"] <= items["min_qty"])


# ── Issuances ─────────────────────────────────────────────────
class TestIssuances:
    def _item_id(self):
        return int(db.get_items().iloc[0]["id"])

    def test_add_issuance_deducts_stock(self):
        iid      = self._item_id()
        items    = db.get_items()
        before   = float(items[items["id"] == iid]["qty"].values[0])
        db.add_issuance(iid, "Test Recipient", "Tester", 1, "2026-01-01", "test")
        after_df = db.get_items()
        after    = float(after_df[after_df["id"] == iid]["qty"].values[0])
        assert after == before - 1

    def test_insufficient_stock_raises(self):
        iid   = self._item_id()
        items = db.get_items()
        qty   = float(items[items["id"] == iid]["qty"].values[0])
        with pytest.raises(ValueError, match="Insufficient"):
            db.add_issuance(iid, "Greedy", "Tester", qty + 9999, "2026-01-01", "")

    def test_get_issuances(self):
        iid = self._item_id()
        db.add_issuance(iid, "Alice", "Bob", 1, "2026-02-01", "note")
        result = db.get_issuances()
        assert not result.empty

    def test_issuance_month_filter(self):
        iid = self._item_id()
        db.add_issuance(iid, "Alice", "Bob", 1, "2026-02-15", "")
        result = db.get_issuances(month="2026-02")
        assert not result.empty
        result2 = db.get_issuances(month="2025-01")
        assert result2.empty


# ── Requisitions ──────────────────────────────────────────────
class TestRequisitions:
    def _setup(self):
        items = db.get_items()
        iid   = int(items.iloc[0]["id"])
        sid   = int(db.get_storerooms().iloc[0]["id"])
        pid   = int(db.get_properties().iloc[0]["id"])
        return iid, sid, pid

    def test_create_requisition(self):
        iid, sid, pid = self._setup()
        ref = db.create_requisition("tester", "staff", pid, sid, "Test purpose", "Normal", [(iid, 1)])
        assert ref.startswith("REQ-")
        reqs = db.get_requisitions()
        assert not reqs.empty

    def test_default_status_pending(self):
        iid, sid, pid = self._setup()
        ref  = db.create_requisition("tester", "staff", pid, sid, "Purpose", "Normal", [(iid, 1)])
        reqs = db.get_requisitions()
        row  = reqs[reqs["ref_number"] == ref].iloc[0]
        assert row["status"] == "Pending"

    def test_approve_requisition(self):
        iid, sid, pid = self._setup()
        ref  = db.create_requisition("tester", "staff", pid, sid, "Purpose", "Normal", [(iid, 1)])
        reqs = db.get_requisitions()
        rid  = int(reqs[reqs["ref_number"] == ref]["id"].values[0])
        lines = db.get_requisition_lines(rid)
        lid   = int(lines.iloc[0]["id"])
        db.review_requisition(rid, "manager", "Approved", "looks good", {lid: 1})
        reqs  = db.get_requisitions()
        row   = reqs[reqs["id"] == rid].iloc[0]
        assert row["status"] == "Approved"

    def test_reject_requisition(self):
        iid, sid, pid = self._setup()
        ref  = db.create_requisition("tester", "staff", pid, sid, "Purpose", "Normal", [(iid, 1)])
        reqs = db.get_requisitions()
        rid  = int(reqs[reqs["ref_number"] == ref]["id"].values[0])
        db.review_requisition(rid, "manager", "Rejected", "not needed", {})
        reqs = db.get_requisitions()
        row  = reqs[reqs["id"] == rid].iloc[0]
        assert row["status"] == "Rejected"

    def test_disperse_deducts_stock(self):
        iid, sid, pid = self._setup()
        items  = db.get_items()
        before = float(items[items["id"] == iid]["qty"].values[0])
        ref    = db.create_requisition("tester", "staff", pid, sid, "Purpose", "Normal", [(iid, 1)])
        reqs   = db.get_requisitions()
        rid    = int(reqs[reqs["ref_number"] == ref]["id"].values[0])
        lines  = db.get_requisition_lines(rid)
        lid    = int(lines.iloc[0]["id"])
        db.review_requisition(rid, "manager", "Approved", "", {lid: 1})
        db.disperse_requisition(rid, "admin")
        after_df = db.get_items()
        after    = float(after_df[after_df["id"] == iid]["qty"].values[0])
        assert after == before - 1

    def test_disperse_non_approved_raises(self):
        iid, sid, pid = self._setup()
        ref  = db.create_requisition("tester", "staff", pid, sid, "Purpose", "Normal", [(iid, 1)])
        reqs = db.get_requisitions()
        rid  = int(reqs[reqs["ref_number"] == ref]["id"].values[0])
        with pytest.raises(ValueError, match="Approved"):
            db.disperse_requisition(rid, "admin")

    def test_cancel_requisition(self):
        iid, sid, pid = self._setup()
        ref  = db.create_requisition("tester", "staff", pid, sid, "Purpose", "Normal", [(iid, 1)])
        reqs = db.get_requisitions()
        rid  = int(reqs[reqs["ref_number"] == ref]["id"].values[0])
        db.cancel_requisition(rid, "tester")
        reqs = db.get_requisitions()
        row  = reqs[reqs["id"] == rid].iloc[0]
        assert row["status"] == "Cancelled"


# ── Reconciliation ────────────────────────────────────────────
class TestReconciliation:
    def test_save_reconciliation_updates_qty(self):
        items = db.get_items()
        iid   = int(items.iloc[0]["id"])
        sid   = int(db.get_storerooms().iloc[0]["id"])
        db.save_reconciliation(sid, "Tester", "2026-03-01", "Monthly", [(iid, 99.0, 50.0)])
        updated = db.get_items()
        row     = updated[updated["id"] == iid].iloc[0]
        assert row["qty"] == 50

    def test_reconciliation_history(self):
        items = db.get_items()
        iid   = int(items.iloc[0]["id"])
        sid   = int(db.get_storerooms().iloc[0]["id"])
        db.save_reconciliation(sid, "Tester", "2026-03-01", "", [(iid, 5.0, 3.0)])
        hist = db.get_reconciliation_history(storeroom_id=sid)
        assert not hist.empty
