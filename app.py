import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date

import database as db
import auth as auth_module
import issuance_slip as slip_gen
import validators as v
import ui
from logger import logger

# ── Page config (must be first Streamlit call) ────────────────
st.set_page_config(
    page_title="StockTrack by Corporate Analytica",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)


def _apply_browser_branding() -> None:
        # Keep forcing title/favicon in case Streamlit re-renders the shell.
        components.html(
                """
                <script>
                (function () {
                    const title = "StockTrack by Corporate Analytica";
                    const favicon = "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='0.9em' font-size='90'>📦</text></svg>";

                    function applyBranding() {
                        try {
                            const doc = window.parent.document;
                            doc.title = title;

                            let icon = doc.querySelector("link[rel='icon']");
                            if (!icon) {
                                icon = doc.createElement("link");
                                icon.rel = "icon";
                                doc.head.appendChild(icon);
                            }
                            icon.href = favicon;
                        } catch (e) {
                            // Ignore cross-frame timing errors during first paint.
                        }
                    }

                    applyBranding();
                    setTimeout(applyBranding, 50);
                    setTimeout(applyBranding, 250);
                    setTimeout(applyBranding, 1000);
                })();
                </script>
                """,
                height=0,
                width=0,
        )


_apply_browser_branding()

# ── DB init ───────────────────────────────────────────────────
try:
    db.init_db()
except Exception as exc:
    logger.critical("Database init failed: %s", exc)
    st.error("Database initialisation failed. Check logs.")
    st.stop()

# ── Auth gate ─────────────────────────────────────────────────
name, auth_status, username, authenticator, auth_config = auth_module.login_page()

if auth_status is False:
    st.error("Incorrect username or password.")
    st.stop()

if auth_status is None:
    st.stop()

# ── Force password change ─────────────────────────────────────
if auth_module.must_change_password(username):
    st.markdown(ui.GLOBAL_CSS, unsafe_allow_html=True)
    col = st.columns([1, 1.2, 1])[1]
    with col:
        st.markdown(
            "<div style='text-align:center;padding:40px 0 16px'>"
            "<div style='font-size:36px'>🔑</div>"
            "<div style='font-size:22px;font-weight:700;margin:8px 0'>Password Change Required</div>"
            "<div style='font-size:13px;color:#888'>You must set a new password before continuing.</div>"
            "</div>",
            unsafe_allow_html=True,
        )
        with st.form("force_change_pw"):
            new_pw = st.text_input("New password", type="password")
            confirm_pw = st.text_input("Confirm new password", type="password")
            if st.form_submit_button("Set new password", type="primary"):
                errs = []
                ok, msg = v.password(new_pw)
                if not ok:
                    errs.append(msg)
                if new_pw != confirm_pw:
                    errs.append("Passwords do not match.")
                if errs:
                    for e in errs:
                        st.error(e)
                else:
                    try:
                        auth_module.set_forced_new_password(username, new_pw)
                        st.success("Password updated. Redirecting...")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Error: {exc}")
    st.stop()

if "role" not in st.session_state:
    users = auth_config.get("credentials", {}).get("usernames", {})
    st.session_state["role"]         = users.get(username, {}).get("role", "staff")
    st.session_state["display_name"] = name or username
    st.session_state["username"]     = username
    logger.info("Session started for '%s' (%s)", username, st.session_state["role"])

# ── Global CSS ────────────────────────────────────────────────
st.markdown(ui.GLOBAL_CSS, unsafe_allow_html=True)

# ── Session state defaults ────────────────────────────────────
for key, default in [
    ("page",          "Overview"),
    ("issue_basket",  []),
    ("req_basket",    []),
    ("req_custom_basket", []),
    ("last_slip",     None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Sidebar helpers ───────────────────────────────────────────
def _safe_int(val, fallback=0):
    try:
        return int(val)
    except (TypeError, ValueError):
        return fallback

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    # Custom CSS for sidebar buttons
    st.markdown(
        """
        <style>
        /* Sidebar button style */
        section[data-testid="stSidebar"] button {
            background: #fff !important;
            color: #111 !important;
            border-radius: 6px !important;
            border: 1px solid #e0e0e0 !important;
            font-weight: 600 !important;
            margin-bottom: 4px !important;
        }
        section[data-testid="stSidebar"] button:hover {
            background: #f0f0f0 !important;
            color: #000 !important;
        }
        /* Login input visibility fix */
        input[type="text"], input[type="password"] {
            background: #fff !important;
            color: #111 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    role         = auth_module.current_role()
    display_name = st.session_state.get("display_name", username or "")

    # ── Branding + user pill ──────────────────────────────────
    st.markdown(
        f"<div style='padding:24px 16px 8px'>"
        f"<div style='font-size:20px;font-weight:700;color:#1976d2;line-height:1.2'>📦 StockTrack</div>"
        f"<div style='font-size:11px;color:#5a5850;margin-top:2px'>Property Stock Manager</div>"
        f"</div>"
        f"<div style='padding:10px 14px;background:rgba(255,255,255,0.06);"
        f"border-radius:8px;margin:4px 12px 12px'>"
        f"<div style='font-size:13px;font-weight:600;color:#e8e6df'>{ui._e(display_name)}</div>"
        f"<div style='font-size:11px;color:#5a5850;text-transform:capitalize;margin-top:2px'>{ui._e(role)}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # ── Sign out ──────────────────────────────────────────────
    # Isolated in its own try/except so a broken logout never
    # prevents the nav buttons from rendering below.
    import inspect as _inspect
    def _force_logout():
        for _k in list(st.session_state.keys()):
            del st.session_state[_k]
        st.rerun()
    try:
        _sig    = _inspect.signature(authenticator.logout)
        _params = list(_sig.parameters.keys())
        if "location" in _params:
            if authenticator.logout(location="sidebar"):
                _force_logout()
        elif len(_params) >= 2:
            if authenticator.logout("Sign out", "sidebar"):
                _force_logout()
        else:
            if authenticator.logout():
                _force_logout()
    except Exception as _exc:
        logger.warning("Logout widget error: %s", _exc)
        if st.button("Sign out", key="manual_signout"):
            _force_logout()

    # ── Change password (self-service) ────────────────────────
    with st.expander("🔑 Change password"):
        with st.form("change_pw_sidebar"):
            _cur_pw = st.text_input("Current password", type="password", key="cpw_cur")
            _new_pw = st.text_input("New password", type="password", key="cpw_new")
            _cfm_pw = st.text_input("Confirm new password", type="password", key="cpw_cfm")
            if st.form_submit_button("Update password"):
                _errs = []
                ok, msg = v.password(_new_pw)
                if not ok:
                    _errs.append(msg)
                if _new_pw != _cfm_pw:
                    _errs.append("Passwords do not match.")
                if not _cur_pw:
                    _errs.append("Current password is required.")
                if _errs:
                    for _e in _errs:
                        st.error(_e)
                else:
                    try:
                        auth_module.change_own_password(username, _cur_pw, _new_pw)
                        st.success("Password updated successfully.")
                    except ValueError as _exc:
                        st.error(str(_exc))
                    except Exception as _exc:
                        st.error(f"Error: {_exc}")

    st.markdown("<hr style='border:none;border-top:0.5px solid rgba(255,255,255,0.08);margin:8px 0'>",
                unsafe_allow_html=True)

    # ── Navigation ────────────────────────────────────────────
    nav = {
        "MAIN":         ["Overview", "Storerooms", "Stock"],
        "OPERATIONS":   ["Issue Stock", "Reconciliation"],
        "REQUISITIONS": ["My Requisitions", "Requisition Approvals"],
        "REPORTS":      ["Issuance Log", "Reorder List", "History"],
        "SETTINGS":     ["Properties", "Suppliers"],
    }
    if role == "admin":
        nav["ADMIN"] = ["Users"]

    for section_name, pages in nav.items():
        visible = [p for p in pages if auth_module.can_access(p)]
        if not visible:
            continue
        st.markdown(
            f"<div class='nav-section'>{section_name}</div>",
            unsafe_allow_html=True,
        )
        for pg in visible:
            if st.button(pg, key=f"nav_{pg}", use_container_width=True):
                st.session_state.page = pg
                st.rerun()

    # Redirect if current page is not accessible for this role
    if not auth_module.can_access(st.session_state.page):
        st.session_state.page = auth_module.first_allowed_page()
        st.rerun()

    st.markdown("<hr style='border:none;border-top:0.5px solid rgba(255,255,255,0.08);margin:8px 0'>",
                unsafe_allow_html=True)

    # ── Global filters ────────────────────────────────────────
    st.markdown(
        "<div style='font-size:11px;color:#5a5850;text-transform:uppercase;"
        "letter-spacing:0.1em;padding:8px 4px 6px;font-weight:600'>Filters</div>",
        unsafe_allow_html=True,
    )
    try:
        props_df      = db.get_properties()
        prop_names    = ["All properties"] + list(props_df["name"])
        sel_prop_name = st.selectbox("Property", prop_names, label_visibility="collapsed")
        sel_prop_id   = (
            None if sel_prop_name == "All properties"
            else _safe_int(props_df.loc[props_df["name"] == sel_prop_name, "id"].values[0])
        )
        rooms_all     = db.get_storerooms(sel_prop_id)
        room_names    = ["All storerooms"] + list(rooms_all["name"])
        sel_room_name = st.selectbox("Storeroom", room_names, label_visibility="collapsed")
        sel_room_id   = None
        if sel_room_name != "All storerooms":
            match = rooms_all[rooms_all["name"] == sel_room_name]
            if not match.empty:
                sel_room_id = _safe_int(match["id"].values[0])
    except Exception as exc:
        logger.error("Sidebar filter error: %s", exc)
        sel_prop_id = None
        sel_room_id = None

page = st.session_state.page

# ── Shared option loaders ─────────────────────────────────────
def _prop_opts():
    props = db.get_properties()
    return {row["name"]: _safe_int(row["id"]) for _, row in props.iterrows()}

def _room_opts(prop_id=None):
    rooms = db.get_storerooms(prop_id)
    return {f"{r['property_name']} — {r['name']}": _safe_int(r["id"]) for _, r in rooms.iterrows()}

def _item_opts(storeroom_id=None, property_id=None):
    items = db.get_items(storeroom_id=storeroom_id, property_id=property_id)
    return {
        f"{r['name']} ({r['storeroom_name']}, {r['qty']} {r['uom']})": _safe_int(r["id"])
        for _, r in items.iterrows()
    }

def _sup_opts():
    sups = db.get_suppliers()
    opts = {"None": None}
    opts.update({r["name"]: _safe_int(r["id"]) for _, r in sups.iterrows()})
    return opts

CATEGORIES = ["Cleaning", "Electrical", "Maintenance", "Plumbing", "Safety", "General", "Other"]
UOMS = ["units", "rolls", "bottles", "boxes", "packs", "litres", "kg", "metres", "tins", "pairs"]

# Move all page imports to the top
import pages.overview as overview_page
import pages.storerooms as storerooms_page
import pages.stock as stock_page
import pages.issue_stock as issue_stock_page
import pages.reconciliation as reconciliation_page
import pages.issuance_log as issuance_log_page
import pages.reorder_list as reorder_list_page
import pages.history as history_page
import pages.properties as properties_page
import pages.suppliers as suppliers_page
import pages.users as users_page
import pages.my_requisitions as my_requisitions_page
import pages.requisition_approvals as req_approvals_page

# ══════════════════════════════════════════════════════════════
# OVERVIEW
# ══════════════════════════════════════════════════════════════
if page == "Overview":
    overview_page.render_overview(username, sel_prop_id, sel_room_id)
# ══════════════════════════════════════════════════════════════
# STOREROOMS
# ══════════════════════════════════════════════════════════════
elif page == "Storerooms":
    storerooms_page.render_storerooms(username, sel_prop_id, _safe_int, _prop_opts)
# ══════════════════════════════════════════════════════════════
# STOCK
# ══════════════════════════════════════════════════════════════
elif page == "Stock":
    stock_page.render_stock(username, sel_prop_id, sel_room_id, _safe_int, _room_opts, _sup_opts, CATEGORIES, UOMS)
# ══════════════════════════════════════════════════════════════
# ISSUE STOCK
# ══════════════════════════════════════════════════════════════
elif page == "Issue Stock":
    issue_stock_page.render_issue_stock(username, sel_prop_id, sel_room_id, _item_opts)
# ══════════════════════════════════════════════════════════════
# RECONCILIATION
# ══════════════════════════════════════════════════════════════
elif page == "Reconciliation":
    sel_room_name = None
    try:
        rooms_all = db.get_storerooms()
        match = rooms_all[rooms_all["id"] == sel_room_id]
        if not match.empty:
            sel_room_name = match["name"].values[0]
    except Exception:
        sel_room_name = ""
    reconciliation_page.render_reconciliation(username, sel_room_id, sel_room_name)
# ══════════════════════════════════════════════════════════════
# ISSUANCE LOG
# ══════════════════════════════════════════════════════════════
elif page == "Issuance Log":
    issuance_log_page.render_issuance_log(username, sel_prop_id, sel_room_id)
# ══════════════════════════════════════════════════════════════
# REORDER LIST
# ══════════════════════════════════════════════════════════════
elif page == "Reorder List":
    reorder_list_page.render_reorder_list(sel_prop_id, sel_room_id)
# ══════════════════════════════════════════════════════════════
# HISTORY (reconciliation)
# ══════════════════════════════════════════════════════════════
elif page == "History":
    history_page.render_history(sel_room_id)
# ══════════════════════════════════════════════════════════════
# PROPERTIES
# ══════════════════════════════════════════════════════════════
elif page == "Properties":
    properties_page.render_properties(username)
# ══════════════════════════════════════════════════════════════
# SUPPLIERS
# ══════════════════════════════════════════════════════════════
elif page == "Suppliers":
    suppliers_page.render_suppliers(username)
# ══════════════════════════════════════════════════════════════
# USERS  (admin only)
# ══════════════════════════════════════════════════════════════
elif page == "Users":
    users_page.render_users(username)
# ══════════════════════════════════════════════════════════════
# MY REQUISITIONS
# ══════════════════════════════════════════════════════════════
elif page == "My Requisitions":
    my_requisitions_page.render_my_requisitions(username, role, sel_prop_id, sel_room_id, _item_opts)
# ══════════════════════════════════════════════════════════════
# REQUISITION APPROVALS
# ══════════════════════════════════════════════════════════════
elif page == "Requisition Approvals":
    req_approvals_page.render_requisition_approvals(username, sel_prop_id, _safe_int)
