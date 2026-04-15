"""
Input validation for all forms.
Every function returns (ok: bool, error_message: str).
"""
import re
from typing import Optional


# ── Generic ───────────────────────────────────────────────────
def required(value: str, label: str = "This field") -> tuple[bool, str]:
    if not value or not value.strip():
        return False, f"{label} is required."
    return True, ""


def max_length(value: str, limit: int, label: str = "This field") -> tuple[bool, str]:
    if len(value.strip()) > limit:
        return False, f"{label} must be {limit} characters or fewer."
    return True, ""


def positive_number(value: float, label: str = "Value") -> tuple[bool, str]:
    if value < 0:
        return False, f"{label} cannot be negative."
    return True, ""


def non_zero_qty(value: float, label: str = "Quantity") -> tuple[bool, str]:
    if value <= 0:
        return False, f"{label} must be greater than zero."
    return True, ""


def safe_name(value: str, label: str = "Name") -> tuple[bool, str]:
    """No angle brackets or script injection characters."""
    if re.search(r"[<>\"']", value):
        return False, f"{label} contains invalid characters."
    return True, ""


# ── Username ──────────────────────────────────────────────────
def username(value: str) -> tuple[bool, str]:
    value = value.strip()
    if not value:
        return False, "Username is required."
    if len(value) < 3:
        return False, "Username must be at least 3 characters."
    if len(value) > 50:
        return False, "Username must be 50 characters or fewer."
    if not re.match(r"^[a-zA-Z0-9_.-]+$", value):
        return False, "Username may only contain letters, numbers, underscores, hyphens, and dots."
    return True, ""


def password(value: str) -> tuple[bool, str]:
    if len(value) < 8:
        return False, "Password must be at least 8 characters."
    if len(value) > 128:
        return False, "Password must be 128 characters or fewer."
    if not re.search(r"[A-Z]", value):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[0-9]", value):
        return False, "Password must contain at least one digit."
    if not re.search(r"[^A-Za-z0-9]", value):
        return False, "Password must contain at least one special character."
    return True, ""


def email(value: str) -> tuple[bool, str]:
    if not value:
        return True, ""   # email is optional in most forms
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value.strip()):
        return False, "Please enter a valid email address."
    return True, ""


# ── Business rules ────────────────────────────────────────────
def min_lte_qty(qty: float, min_qty: float) -> tuple[bool, str]:
    """Warn (not block) when current qty < min_qty at creation time."""
    if qty < min_qty:
        return False, f"Current quantity ({qty}) is below the low-stock threshold ({min_qty}). The item will immediately show as Low."
    return True, ""


def sufficient_stock(available: float, requested: float, item_name: str = "item") -> tuple[bool, str]:
    if requested > available:
        return False, f"Only {available} unit(s) of '{item_name}' in stock — cannot issue {requested}."
    return True, ""


def issue_qty(value: float) -> tuple[bool, str]:
    if value <= 0:
        return False, "Issue quantity must be greater than zero."
    if value != int(value) and value > 0:
        # fractional quantities are allowed — just a note
        return True, ""
    return True, ""


# ── Composite validators ──────────────────────────────────────
def validate_item_form(name: str, storeroom_key: str, qty: float, min_qty: float,
                       unit_cost: float) -> list[str]:
    errors: list[str] = []

    ok, msg = required(name, "Item name"); errors += [msg] if not ok else []
    ok, msg = max_length(name, 100, "Item name"); errors += [msg] if not ok else []
    ok, msg = safe_name(name, "Item name"); errors += [msg] if not ok else []
    ok, msg = required(storeroom_key, "Storeroom"); errors += [msg] if not ok else []
    ok, msg = positive_number(qty, "Quantity"); errors += [msg] if not ok else []
    ok, msg = positive_number(min_qty, "Low-stock threshold"); errors += [msg] if not ok else []
    ok, msg = positive_number(unit_cost, "Unit cost"); errors += [msg] if not ok else []

    return errors


def validate_issuance_form(recipient: str, qty: float) -> list[str]:
    errors: list[str] = []
    ok, msg = required(recipient, "Recipient name"); errors += [msg] if not ok else []
    ok, msg = max_length(recipient, 100, "Recipient name"); errors += [msg] if not ok else []
    ok, msg = safe_name(recipient, "Recipient name"); errors += [msg] if not ok else []
    ok, msg = non_zero_qty(qty, "Quantity"); errors += [msg] if not ok else []
    return errors


def validate_storeroom_form(name: str, property_key: str) -> list[str]:
    errors: list[str] = []
    ok, msg = required(name, "Storeroom name"); errors += [msg] if not ok else []
    ok, msg = max_length(name, 80, "Storeroom name"); errors += [msg] if not ok else []
    ok, msg = safe_name(name, "Storeroom name"); errors += [msg] if not ok else []
    ok, msg = required(property_key, "Property"); errors += [msg] if not ok else []
    return errors


def validate_property_form(name: str) -> list[str]:
    errors: list[str] = []
    ok, msg = required(name, "Property name"); errors += [msg] if not ok else []
    ok, msg = max_length(name, 100, "Property name"); errors += [msg] if not ok else []
    ok, msg = safe_name(name, "Property name"); errors += [msg] if not ok else []
    return errors


def validate_supplier_form(name: str) -> list[str]:
    errors: list[str] = []
    ok, msg = required(name, "Supplier name"); errors += [msg] if not ok else []
    ok, msg = max_length(name, 100, "Supplier name"); errors += [msg] if not ok else []
    ok, msg = safe_name(name, "Supplier name"); errors += [msg] if not ok else []
    return errors


def validate_user_form(uname: str, full_name: str, pwd: str, email_val: str) -> list[str]:
    errors: list[str] = []
    ok, msg = username(uname); errors += [msg] if not ok else []
    ok, msg = required(full_name, "Full name"); errors += [msg] if not ok else []
    ok, msg = max_length(full_name, 80, "Full name"); errors += [msg] if not ok else []
    ok, msg = password(pwd); errors += [msg] if not ok else []
    ok, msg = email(email_val); errors += [msg] if not ok else []
    return errors


def validate_requisition_form(purpose: str, basket: list) -> list[str]:
    errors: list[str] = []
    ok, msg = required(purpose, "Purpose / reason"); errors += [msg] if not ok else []
    ok, msg = max_length(purpose, 200, "Purpose"); errors += [msg] if not ok else []
    ok, msg = safe_name(purpose, "Purpose"); errors += [msg] if not ok else []
    if not basket:
        errors.append("Add at least one item to the requisition.")
    return errors
