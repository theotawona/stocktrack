"""
UI rendering helpers — all inline HTML/CSS lives here.
app.py calls these functions; it never builds HTML strings itself.
"""
import html as _html
import streamlit as st


# ── Escape helper ─────────────────────────────────────────────
def _e(value) -> str:
    """HTML-escape a value for safe embedding in markup."""
    return _html.escape(str(value)) if value is not None else ""


# ── Page header ───────────────────────────────────────────────
def page_header(title: str, subtitle: str = "") -> None:
    st.markdown(
        f"<div class='page-title'>{_e(title)}</div>"
        + (f"<div class='page-sub'>{_e(subtitle)}</div>" if subtitle else ""),
        unsafe_allow_html=True,
    )


# ── Section label ─────────────────────────────────────────────
def section(label: str) -> None:
    st.markdown(f"<div class='section-header'>{_e(label)}</div>", unsafe_allow_html=True)


# ── Metric card ───────────────────────────────────────────────
def metric_card(label: str, value, sub: str = "", cls: str = "") -> str:
    sub_html = f"<div class='sub'>{_e(sub)}</div>" if sub else ""
    return (
        f"<div class='metric-card {_e(cls)}'>"
        f"<div class='label'>{_e(label)}</div>"
        f"<div class='value'>{_e(value)}</div>"
        f"{sub_html}"
        f"</div>"
    )


def metric_row(cards: list[tuple]) -> None:
    """
    cards = [(label, value, sub, cls), ...]
    sub and cls are optional.
    """
    cols = st.columns(len(cards))
    for col, card in zip(cols, cards):
        label, value, *rest = card
        sub = rest[0] if rest else ""
        cls = rest[1] if len(rest) > 1 else ""
        col.markdown(metric_card(label, value, sub, cls), unsafe_allow_html=True)


# ── Status badge (inline) ─────────────────────────────────────
_STATUS_CLS = {
    "OK":           "badge-ok",
    "Low":          "badge-low",
    "Out of stock": "badge-out",
}

def status_badge(status: str) -> str:
    cls = _STATUS_CLS.get(status, "badge-info")
    return f"<span class='badge {cls}'>{_e(status)}</span>"


# ── Requisition status pill ───────────────────────────────────
_REQ_STATUS_STYLE = {
    "Pending":   ("background:#FAEEDA;color:#854F0B",),
    "Approved":  ("background:#EAF3DE;color:#3B6D11",),
    "Rejected":  ("background:#FCEBEB;color:#A32D2D",),
    "Dispersed": ("background:#E6F1FB;color:#0C447C",),
    "Cancelled": ("background:#F1EFE8;color:#444441",),
}

def req_status_pill(status: str) -> str:
    style = _REQ_STATUS_STYLE.get(status, ("background:#F1EFE8;color:#444441",))[0]
    return (
        f"<span style='{style};padding:3px 10px;"
        f"border-radius:20px;font-size:11px;font-weight:600'>{_e(status)}</span>"
    )


def req_status_colors(status: str) -> tuple[str, str]:
    """Returns (bg_hex, fg_hex) for a requisition status."""
    mapping = {
        "Pending":   ("#FAEEDA", "#854F0B"),
        "Approved":  ("#EAF3DE", "#3B6D11"),
        "Rejected":  ("#FCEBEB", "#A32D2D"),
        "Dispersed": ("#E6F1FB", "#0C447C"),
        "Cancelled": ("#F1EFE8", "#444441"),
    }
    return mapping.get(status, ("#F1EFE8", "#444441"))


# ── Storeroom card ────────────────────────────────────────────
def store_card(name: str, property_name: str, item_count: int,
               value_str: str, alert: str = "") -> None:
    alert_html = (
        f"<div class='store-stat' style='color:#BA7517'>{_e(alert)}</div>"
        if alert else ""
    )
    st.markdown(
        f"<div class='store-card'>"
        f"<div class='store-name'>{_e(name)}</div>"
        f"<div class='store-location'>{_e(property_name)}</div>"
        f"<div class='store-meta'>"
        f"<div class='store-stat'><strong>{_e(item_count)}</strong> items</div>"
        f"<div class='store-stat'><strong>{_e(value_str)}</strong> value</div>"
        f"{alert_html}"
        f"</div>"
        f"</div>",
        unsafe_allow_html=True,
    )


# ── Reorder alert item ────────────────────────────────────────
def reorder_item(name: str, detail: str, critical: bool = False) -> None:
    cls = "reorder-item critical" if critical else "reorder-item"
    st.markdown(
        f"<div class='{cls}'>"
        f"<div class='ri-name'>{_e(name)}</div>"
        f"<div class='ri-detail'>{_e(detail)}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )


# ── Alert banner (info / success / warning) ───────────────────
def info_banner(text: str, kind: str = "info") -> None:
    """kind = 'info' | 'success' | 'warning'"""
    styles = {
        "info":    ("background:#E6F1FB", "border-left-color:#185FA5"),
        "success": ("background:#EAF3DE", "border-left-color:#3B6D11"),
        "warning": ("background:#FAEEDA", "border-left-color:#BA7517"),
    }
    bg, border = styles.get(kind, styles["info"])
    st.markdown(
        f"<div style='{bg};{border};border-left:3px solid;"
        f"border-radius:0 8px 8px 0;padding:10px 14px;"
        f"margin-bottom:16px;font-size:13px'>{_e(text)}</div>",
        unsafe_allow_html=True,
    )


def sidebar_notice(text: str, kind: str = "error") -> None:
    styles = {
        "error": (
            "background:#FDECEC;border:1px solid #D9534F;",
            "#7F1D1D",
        ),
        "success": (
            "background:#EAF7EC;border:1px solid #5C9E63;",
            "#1F5130",
        ),
        "warning": (
            "background:#FFF4E5;border:1px solid #D28B2D;",
            "#6E4508",
        ),
        "info": (
            "background:#EAF3FF;border:1px solid #4E79B8;",
            "#183A66",
        ),
    }
    container_style, text_color = styles.get(kind, styles["info"])
    st.markdown(
        f"<div class='sidebar-notice' style='{container_style}'>"
        f"<span style='color:{text_color} !important;font-weight:600'>{_e(text)}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )


# ── Error list ────────────────────────────────────────────────
def show_errors(errors: list[str]) -> None:
    for e in errors:
        st.error(e)


# ── Currency formatter ────────────────────────────────────────
def fmt_currency(v) -> str:
    try:
        return f"R {float(v):,.2f}"
    except (TypeError, ValueError):
        return "R 0.00"


# ── CSV export button ─────────────────────────────────────────
def export_csv(df, filename: str) -> None:
    import io
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    csv_data = buf.getvalue()
    # Keep button identity stable and avoid rerun-on-click to reduce stale media-id races.
    key = f"csv_download_{filename}_{len(df)}_{len(df.columns)}"
    st.download_button(
        "⬇ Export CSV",
        csv_data,
        file_name=filename,
        mime="text/csv",
        key=key,
        on_click="ignore",
    )


# ── Global CSS ────────────────────────────────────────────────
GLOBAL_CSS = """
<style>
/* ── Main background ── */
[data-testid="stAppViewContainer"] { background: #f8f7f4; }
.block-container { padding-top: 2rem; padding-bottom: 2rem; }
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] {
    background: transparent !important;
}

/* ── Sidebar background ── */
section[data-testid="stSidebar"] { background: #1a1a2e !important; }
section[data-testid="stSidebar"] > div:first-child { background: #1a1a2e !important; }
[data-testid="stSidebarNav"] { display: none; }

/* ── Sidebar text ── */
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] * { color: #e8e6df; }

/* Keep Streamlit alert colors intact inside sidebar */
section[data-testid="stSidebar"] [data-baseweb="notification"] * {
    color: inherit !important;
}

/* ── Sidebar nav buttons ── */
section[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: none !important;
    color: #9c9a92 !important;
    text-align: left !important;
    width: 100% !important;
    padding: 8px 16px !important;
    border-radius: 8px !important;
    font-size: 14px !important;
    font-weight: 400 !important;
    margin: 1px 0 !important;
    box-shadow: none !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.08) !important;
    color: #ffffff !important;
    border: none !important;
}
section[data-testid="stSidebar"] .stButton > button:focus {
    box-shadow: none !important;
    border: none !important;
}

/* ── Sidebar selectbox ── */
section[data-testid="stSidebar"] .stSelectbox label {
    color: #9c9a92 !important;
    font-size: 11px !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
section[data-testid="stSidebar"] .stSelectbox > div > div {
    background: rgba(255,255,255,0.06) !important;
    border-color: rgba(255,255,255,0.12) !important;
    color: #e8e6df !important;
}

/* ── Sidebar section labels ── */
.nav-section {
    font-size: 10px; text-transform: uppercase; letter-spacing: 0.1em;
    color: #5a5850; padding: 16px 16px 6px; font-weight: 600;
    display: block;
}

/* ── Sidebar logout button (stauth renders its own) ── */
section[data-testid="stSidebar"] .stButton > button[kind="secondary"] {
    color: #888780 !important;
    font-size: 12px !important;
    padding: 6px 16px !important;
}

/* ── Sidebar notices ── */
section[data-testid="stSidebar"] .sidebar-notice {
    margin: 8px 0 0;
    padding: 10px 12px;
    border-radius: 8px;
    font-size: 12px;
    line-height: 1.45;
    border: 1px solid transparent;
    font-weight: 500;
}
section[data-testid="stSidebar"] .sidebar-notice.sidebar-notice-error {
    background: rgba(163,45,45,0.18);
    border-color: rgba(163,45,45,0.5);
    color: #ffe9e9 !important;
}
section[data-testid="stSidebar"] .sidebar-notice.sidebar-notice-success {
    background: rgba(59,109,17,0.22);
    border-color: rgba(59,109,17,0.45);
    color: #effbdd !important;
}
section[data-testid="stSidebar"] .sidebar-notice.sidebar-notice-warning {
    background: rgba(186,117,23,0.22);
    border-color: rgba(186,117,23,0.45);
    color: #fff3de !important;
}
section[data-testid="stSidebar"] .sidebar-notice.sidebar-notice-info {
    background: rgba(24,95,165,0.22);
    border-color: rgba(24,95,165,0.45);
    color: #ebf5ff !important;
}

/* ── Metric cards ── */
.metric-card {
    background: #ffffff; border-radius: 12px;
    border: 0.5px solid rgba(0,0,0,0.08); padding: 20px 24px;
}
.metric-card .label { font-size: 12px; color: #888780; margin-bottom: 4px; }
.metric-card .value { font-size: 28px; font-weight: 600; color: #1a1a2e; line-height: 1; }
.metric-card .sub   { font-size: 12px; color: #888780; margin-top: 4px; }
.metric-card.ok     .value { color: #3B6D11; }
.metric-card.warn   .value { color: #BA7517; }
.metric-card.danger .value { color: #A32D2D; }
.metric-card.info   .value { color: #185FA5; }

/* ── Storeroom cards ── */
.store-card {
    background: #ffffff; border-radius: 12px;
    border: 0.5px solid rgba(0,0,0,0.08);
    padding: 18px 20px; margin-bottom: 12px;
}
.store-card .store-name     { font-size: 15px; font-weight: 600; color: #1a1a2e; margin-bottom: 2px; }
.store-card .store-location { font-size: 12px; color: #888780; margin-bottom: 12px; }
.store-card .store-meta     { display: flex; gap: 16px; }
.store-card .store-stat     { font-size: 12px; color: #5a5850; }
.store-card .store-stat strong { font-weight: 600; color: #1a1a2e; }

/* ── Badges ── */
.badge {
    display: inline-block; padding: 2px 10px;
    border-radius: 20px; font-size: 11px; font-weight: 600;
}
.badge-ok   { background: #EAF3DE; color: #3B6D11; }
.badge-low  { background: #FAEEDA; color: #854F0B; }
.badge-out  { background: #FCEBEB; color: #A32D2D; }
.badge-info { background: #E6F1FB; color: #0C447C; }

/* ── Section headers ── */
.section-header {
    font-size: 13px; font-weight: 600; color: #888780;
    text-transform: uppercase; letter-spacing: 0.06em;
    margin: 24px 0 12px; padding-bottom: 8px;
    border-bottom: 0.5px solid rgba(0,0,0,0.08);
}

/* ── Reorder alerts ── */
.reorder-item {
    background: #fff8f0; border-left: 3px solid #BA7517;
    border-radius: 0 8px 8px 0; padding: 10px 14px; margin-bottom: 8px;
}
.reorder-item.critical { background: #fff5f5; border-left-color: #A32D2D; }
.reorder-item .ri-name   { font-weight: 600; color: #1a1a2e; font-size: 14px; }
.reorder-item .ri-detail { font-size: 12px; color: #888780; margin-top: 2px; }

/* ── Tables ── */
.stDataFrame { border-radius: 8px; overflow: hidden; }
[data-testid="stDataFrame"] > div { border-radius: 8px; }

/* ── Forms ── */
[data-testid="stForm"] {
    background: #ffffff; border-radius: 12px;
    border: 0.5px solid rgba(0,0,0,0.08); padding: 20px 24px;
}
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
}

/* ── Page titles ── */
.page-title { font-size: 24px; font-weight: 700; color: #1976d2; margin-bottom: 4px; }
.page-sub   { font-size: 14px; color: #888780; margin-bottom: 24px; }

/* ── Charts ── */
.js-plotly-plot .plotly { background: transparent !important; }
/* ── Login/Landing logo override ── */
.stApp [data-testid="stAppViewContainer"] .block-container > div:first-child img + div {
    color: #1976d2 !important;
    font-weight: 700 !important;
    font-size: 2rem !important;
}
.stApp [data-testid="stAppViewContainer"] .block-container > div:first-child div[style*="color:#888780"] {
    color: #444 !important;
    font-size: 1.1rem !important;
}
</style>
"""
