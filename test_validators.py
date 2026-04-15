"""Unit tests for validators.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import validators as v


# ── Generic ───────────────────────────────────────────────────
class TestRequired:
    def test_empty_string(self):
        ok, msg = v.required("")
        assert not ok
        assert "required" in msg.lower()

    def test_whitespace_only(self):
        ok, _ = v.required("   ")
        assert not ok

    def test_valid_value(self):
        ok, msg = v.required("hello")
        assert ok
        assert msg == ""


class TestMaxLength:
    def test_within_limit(self):
        ok, _ = v.max_length("hello", 10)
        assert ok

    def test_at_limit(self):
        ok, _ = v.max_length("a" * 10, 10)
        assert ok

    def test_exceeds_limit(self):
        ok, msg = v.max_length("a" * 11, 10)
        assert not ok
        assert "10" in msg


class TestSafeName:
    def test_clean_name(self):
        ok, _ = v.safe_name("Block A Storeroom")
        assert ok

    def test_angle_bracket(self):
        ok, _ = v.safe_name("<script>")
        assert not ok

    def test_quote_char(self):
        ok, _ = v.safe_name("O'Malley")
        assert not ok


# ── Username / password ───────────────────────────────────────
class TestUsername:
    def test_valid(self):
        ok, _ = v.username("sipho_m")
        assert ok

    def test_too_short(self):
        ok, _ = v.username("ab")
        assert not ok

    def test_spaces(self):
        ok, _ = v.username("john doe")
        assert not ok

    def test_special_chars(self):
        ok, _ = v.username("john@company")
        assert not ok

    def test_dots_and_dashes(self):
        ok, _ = v.username("john.doe-2")
        assert ok


class TestPassword:
    def test_too_short(self):
        ok, _ = v.password("Abc1!")
        assert not ok

    def test_no_uppercase(self):
        ok, _ = v.password("secure123!")
        assert not ok

    def test_no_digit(self):
        ok, _ = v.password("Securepass!")
        assert not ok

    def test_no_special(self):
        ok, _ = v.password("Secure123")
        assert not ok

    def test_valid(self):
        ok, _ = v.password("Secure123!")
        assert ok

    def test_too_long(self):
        ok, _ = v.password("x" * 129)
        assert not ok


class TestEmail:
    def test_empty_is_ok(self):
        ok, _ = v.email("")
        assert ok  # email is optional

    def test_valid(self):
        ok, _ = v.email("user@domain.co.za")
        assert ok

    def test_no_at(self):
        ok, _ = v.email("notanemail")
        assert not ok

    def test_no_domain(self):
        ok, _ = v.email("user@")
        assert not ok


# ── Business rules ────────────────────────────────────────────
class TestSufficientStock:
    def test_enough(self):
        ok, _ = v.sufficient_stock(10, 5, "Bleach")
        assert ok

    def test_exact(self):
        ok, _ = v.sufficient_stock(5, 5, "Bleach")
        assert ok

    def test_not_enough(self):
        ok, msg = v.sufficient_stock(2, 5, "Bleach")
        assert not ok
        assert "Bleach" in msg
        assert "2" in msg


class TestMinLteQty:
    def test_qty_above_min(self):
        ok, _ = v.min_lte_qty(10, 3)
        assert ok

    def test_qty_equals_min(self):
        ok, _ = v.min_lte_qty(3, 3)
        assert ok

    def test_qty_below_min(self):
        ok, msg = v.min_lte_qty(1, 5)
        assert not ok
        assert "Low" in msg


class TestPositiveNumber:
    def test_zero(self):
        ok, _ = v.positive_number(0)
        assert ok  # zero is allowed (item with no stock yet)

    def test_negative(self):
        ok, _ = v.positive_number(-1)
        assert not ok

    def test_positive(self):
        ok, _ = v.positive_number(5.5)
        assert ok


class TestNonZeroQty:
    def test_zero(self):
        ok, _ = v.non_zero_qty(0)
        assert not ok

    def test_positive(self):
        ok, _ = v.non_zero_qty(1)
        assert ok

    def test_negative(self):
        ok, _ = v.non_zero_qty(-1)
        assert not ok


# ── Composite validators ──────────────────────────────────────
class TestValidateItemForm:
    def test_valid(self):
        errs = v.validate_item_form("LED Bulbs", "Block A", 10, 3, 18.50)
        assert errs == []

    def test_missing_name(self):
        errs = v.validate_item_form("", "Block A", 10, 3, 18.50)
        assert any("name" in e.lower() for e in errs)

    def test_missing_storeroom(self):
        errs = v.validate_item_form("Bleach", "", 0, 1, 0)
        assert any("storeroom" in e.lower() for e in errs)

    def test_negative_cost(self):
        errs = v.validate_item_form("Bleach", "Block A", 5, 1, -10)
        assert any("cost" in e.lower() for e in errs)


class TestValidateIssuanceForm:
    def test_valid(self):
        errs = v.validate_issuance_form("John Dlamini", 3)
        assert errs == []

    def test_empty_recipient(self):
        errs = v.validate_issuance_form("", 3)
        assert len(errs) > 0

    def test_zero_qty(self):
        errs = v.validate_issuance_form("John", 0)
        assert len(errs) > 0


class TestValidateRequisitionForm:
    def test_valid(self):
        errs = v.validate_requisition_form("Monthly supplies", [{"item_id": 1}])
        assert errs == []

    def test_missing_purpose(self):
        errs = v.validate_requisition_form("", [{"item_id": 1}])
        assert len(errs) > 0

    def test_empty_basket(self):
        errs = v.validate_requisition_form("Monthly supplies", [])
        assert any("item" in e.lower() for e in errs)


class TestValidateUserForm:
    def test_valid(self):
        errs = v.validate_user_form("sipho_m", "Sipho Mokoena", "Secure123!", "sipho@co.za")
        assert errs == []

    def test_bad_username(self):
        errs = v.validate_user_form("s m", "Sipho", "Secure123!", "")
        assert len(errs) > 0

    def test_short_password(self):
        errs = v.validate_user_form("sipho_m", "Sipho", "abc", "")
        assert len(errs) > 0

    def test_bad_email(self):
        errs = v.validate_user_form("sipho_m", "Sipho", "Secure123!", "notanemail")
        assert len(errs) > 0
