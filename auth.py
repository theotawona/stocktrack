"""
Authentication and authorisation for StockTrack.
"""
import yaml
from pathlib import Path
from yaml.loader import SafeLoader

import streamlit as st
import streamlit_authenticator as stauth

from logger import logger

CONFIG_PATH = Path(__file__).parent / "users.yaml"

ROLE_PERMISSIONS: dict = {
    "admin": [
        "Overview", "Storerooms", "Stock",
        "Issue Stock", "Reconciliation",
        "Issuance Log", "Reorder List", "History",
        "Properties", "Suppliers",
        "My Requisitions", "Requisition Approvals",
        "Users",
    ],
    "manager": [
        "Overview", "Storerooms", "Stock",
        "Issue Stock", "Reconciliation",
        "Issuance Log", "Reorder List", "History",
        "Properties", "Suppliers",
        "My Requisitions", "Requisition Approvals",
    ],
    "staff": [
        "Stock", "Reorder List", "My Requisitions",
    ],
}

VALID_ROLES = list(ROLE_PERMISSIONS.keys())


def _hash_passwords(passwords: list) -> list:
    """Hash passwords, handling both old and new stauth API."""
    try:
        return stauth.Hasher(passwords).generate()
    except Exception:
        return [stauth.Hasher.hash(p) for p in passwords]


def _default_config() -> dict:
    hashed = _hash_passwords(["admin123", "manager123", "staff123"])
    return {
        "credentials": {
            "usernames": {
                "admin":   {"name": "Administrator",    "email": "admin@stocktrack.co.za",   "password": hashed[0], "role": "admin"},
                "manager": {"name": "Property Manager", "email": "manager@stocktrack.co.za", "password": hashed[1], "role": "manager"},
                "staff":   {"name": "Storeroom Staff",  "email": "staff@stocktrack.co.za",   "password": hashed[2], "role": "staff"},
            }
        },
        "cookie": {
            "name": "stocktrack_auth",
            "key": "CHANGE_ME_IN_PRODUCTION_USE_A_LONG_RANDOM_STRING",
            "expiry_days": 7,
        },
        "preauthorized": {"emails": []},
    }


def _load_config() -> dict:
    if not CONFIG_PATH.exists():
        logger.info("users.yaml not found — creating with defaults.")
        try:
            config = _default_config()
            CONFIG_PATH.write_text(yaml.dump(config, default_flow_style=False), encoding="utf-8")
        except Exception as exc:
            logger.error("Failed to create users.yaml: %s", exc)
            raise RuntimeError(f"Cannot create user config: {exc}") from exc

    try:
        config = yaml.load(CONFIG_PATH.read_text(encoding="utf-8"), Loader=SafeLoader)
        if not isinstance(config, dict) or "credentials" not in config:
            raise ValueError("users.yaml is malformed.")
        return config
    except yaml.YAMLError as exc:
        logger.error("users.yaml YAML error: %s", exc)
        raise RuntimeError(f"users.yaml is invalid: {exc}") from exc


def _save_config(config: dict) -> None:
    try:
        CONFIG_PATH.write_text(yaml.dump(config, default_flow_style=False), encoding="utf-8")
    except OSError as exc:
        logger.error("Cannot write users.yaml: %s", exc)
        raise RuntimeError(f"Cannot save config: {exc}") from exc


def get_authenticator():
    config = _load_config()
    cookie = config.get("cookie", {})

    # Prefer secret injected via Streamlit Cloud; if unavailable locally, use users.yaml fallback.
    cookie_key = cookie.get("key", "CHANGE_ME_IN_PRODUCTION")
    try:
        secrets_obj = getattr(st, "secrets", None)
        if secrets_obj is not None:
            cookie_key = secrets_obj.get("COOKIE_KEY", cookie_key)
    except Exception:
        # Local runs may have no secrets.toml configured.
        pass

    # stauth 0.2.x: Authenticate(credentials, cookie_name, cookie_key, cookie_expiry_days)
    # stauth 0.3.x: Authenticate(credentials_dict, cookie_name, cookie_key, cookie_expiry_days)
    # Both accept the same positional args — safe to call the same way.
    try:
        auth = stauth.Authenticate(
            config["credentials"],
            cookie.get("name", "stocktrack_auth"),
            cookie_key,
            cookie.get("expiry_days", 7),
        )
    except TypeError:
        # Some builds accept only credentials + cookie dict
        auth = stauth.Authenticate(
            config["credentials"],
            cookie.get("name", "stocktrack_auth"),
            cookie_key,
        )
    return auth, config


def _call_login(auth) -> tuple | None:
    """
    Call auth.login() in a way that works across stauth versions.

    v0.2.x: auth.login("Form title", "main"|"sidebar")
            returns (name, auth_status, username)

    v0.3.x: auth.login(location="main")   <- location is 'main'|'sidebar'|'unrendered'
            returns (name, auth_status, username)  OR sets st.session_state directly

    v0.4.x+: auth.login() may set st.session_state["authentication_status"] with no return
    """
    import inspect
    sig    = inspect.signature(auth.login)
    params = list(sig.parameters.keys())
    logger.debug("stauth login() params: %s", params)

    # ── Try v0.3 / v0.4 keyword-only style first ─────────────
    if "location" in params:
        try:
            result = auth.login(location="main")
        except Exception:
            result = auth.login(location="unrendered")
    # ── Try v0.2 positional style ─────────────────────────────
    elif len(params) >= 2:
        result = auth.login("Login", "main")
    # ── Fallback: no-arg call ─────────────────────────────────
    else:
        result = auth.login()

    # Unpack — v0.3+ sometimes returns None and puts values in session_state
    if result is not None and isinstance(result, tuple) and len(result) == 3:
        return result

    # Read from session_state (v0.3+ / v0.4+)
    name        = st.session_state.get("name")
    auth_status = st.session_state.get("authentication_status")
    username    = st.session_state.get("username")
    return name, auth_status, username

    # IF auth came from cookie (no fresh login this session), treat as not logged in
    if auth_status and not st.session_state.get("_login_submitted"):
        return None, None, None

    return name, auth_status, username


def login_page():
    st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background: #1a1a2e; }
    [data-testid="stForm"] {
        background: #fff;
        border: 0.5px solid #e0e0e0;
        border-radius: 16px; padding: 28px 32px;
    }
    [data-testid="stForm"] label { color: #222 !important; font-size: 13px; }
    [data-testid="stForm"] input[type="text"],
    [data-testid="stForm"] input[type="password"],
    [data-testid="stForm"] input[type="email"],
    [data-testid="stForm"] textarea {
        background: #fff !important;
        color: #111 !important;
        border: 1px solid #e0e0e0 !important;
    }
    [data-testid="stForm"] input[type="text"]::placeholder,
    [data-testid="stForm"] input[type="password"]::placeholder,
    [data-testid="stForm"] input[type="email"]::placeholder,
    [data-testid="stForm"] textarea::placeholder {
        color: #888 !important;
    }
    .stButton > button {
        width:100%; background:#1D9E75 !important; color:#fff !important;
        border:none !important; border-radius:8px !important;
        padding:10px !important; font-weight:600 !important; font-size:15px !important;
    }
    .stButton > button:hover { background:#17855f !important; }
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

    col = st.columns([1, 1.2, 1])[1]
    with col:
        st.markdown(
            "<div style='text-align:center;padding:40px 0 24px'>"
            "<div style='font-size:36px'>📦</div>"
            "<div style='font-size:26px;font-weight:700;color:#fff;margin:8px 0 4px'>StockTrack</div>"
            "<div style='font-size:13px;color:#9c9a92'>Property Stock Management</div>"
            "</div>",
            unsafe_allow_html=True,
        )
        try:
            auth, config = get_authenticator()
            result = _call_login(auth)
            if result is None:
                st.stop()
            name, auth_status, username = result
            if auth_status is False:
                logger.warning("Failed login attempt.")
            elif auth_status:
                st.session_state["_login_submitted"] = True
                logger.info("User '%s' logged in.", username)
                # Store property_id for staff
                user_info = config.get("credentials", {}).get("usernames", {}).get(username, {})
                if user_info.get("role") == "staff":
                    st.session_state["property_id"] = user_info.get("property_id")
                else:
                    st.session_state["property_id"] = None
            return name, auth_status, username, auth, config
        except Exception as exc:
            logger.error("Login system error: %s", exc)
            st.error(f"Authentication error: {exc}")
            st.stop()


def current_role() -> str:
    return st.session_state.get("role", "staff")


def current_username() -> str:
    return st.session_state.get("username", "")


def can_access(page: str) -> bool:
    return page in ROLE_PERMISSIONS.get(current_role(), [])


def first_allowed_page() -> str:
    return ROLE_PERMISSIONS.get(current_role(), ["Stock"])[0]


def get_all_users() -> list:
    try:
        config = _load_config()
        return [
            {
                "username": u,
                "name": d.get("name",""),
                "email": d.get("email",""),
                "role": d.get("role","staff"),
                "property_id": d.get("property_id")
            }
            for u, d in config["credentials"]["usernames"].items()
        ]
    except Exception as exc:
        logger.error("get_all_users failed: %s", exc)
        return []

# Get the current user's property_id (None if not set)
def current_property_id() -> int | None:
    return st.session_state.get("property_id")


def add_user(username: str, name: str, email: str, password: str, role: str) -> None:
    if role not in VALID_ROLES:
        raise ValueError(f"Invalid role '{role}'.")
    config = _load_config()
    if username in config["credentials"]["usernames"]:
        raise ValueError(f"Username '{username}' already exists.")
    hashed = _hash_passwords([password])[0]
    config["credentials"]["usernames"][username] = {
        "name": name, "email": email, "password": hashed, "role": role,
    }
    _save_config(config)
    logger.info("User '%s' added with role '%s'.", username, role)


def delete_user(username: str) -> None:
    config = _load_config()
    if username not in config["credentials"]["usernames"]:
        logger.warning("Delete: user '%s' not found.", username)
        return
    del config["credentials"]["usernames"][username]
    _save_config(config)
    logger.info("User '%s' deleted.", username)


def update_user_role(username: str, role: str) -> None:
    if role not in VALID_ROLES:
        raise ValueError(f"Invalid role '{role}'.")
    config = _load_config()
    if username not in config["credentials"]["usernames"]:
        raise ValueError(f"User '{username}' not found.")
    config["credentials"]["usernames"][username]["role"] = role
    _save_config(config)
    logger.info("User '%s' role updated to '%s'.", username, role)


# Assign or update a user's property_id
def update_user_property(username: str, property_id: int | None) -> None:
    config = _load_config()
    if username not in config["credentials"]["usernames"]:
        raise ValueError(f"User '{username}' not found.")
    config["credentials"]["usernames"][username]["property_id"] = property_id
    _save_config(config)
    logger.info("User '%s' property_id updated to '%s'.", username, property_id)
