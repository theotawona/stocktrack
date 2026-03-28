import streamlit as st
import ui
import database as db
from logger import logger

def render_history(sel_room_id):
    ui.page_header("Reconciliation history", "Past stock count records")
    logger.debug("Rendering History")

    import re
    month_h = st.text_input("Filter by month (YYYY-MM)", placeholder="e.g. 2026-03", label_visibility="collapsed")
    clean_h = month_h.strip() if month_h and re.match(r"^\d{4}-\d{2}$", month_h.strip()) else None
    if month_h and not clean_h:
        st.warning("Month must be in YYYY-MM format.")

    try:
        history_df = db.get_reconciliation_history(storeroom_id=sel_room_id, month=clean_h)
    except Exception as exc:
        logger.error("get_reconciliation_history failed: %s", exc)
        st.error("Could not load history.")
        history_df = db.pd.DataFrame()

    if history_df.empty:
        st.info("No reconciliation history yet.")
    else:
        for _, row in history_df.iterrows():
            shorts  = int(row.get("shorts", 0))
            surplus = int(row.get("surplus", 0))
            label   = f"\U0001F4CB {row['recon_date']} — {row['property_name']} · {row['storeroom_name']}  ({int(row['line_count'])} items · {shorts} short · {surplus} surplus)"
            with st.expander(label):
                st.markdown(f"**By:** {row.get('performed_by') or '—'}  |  **Notes:** {row.get('notes') or '—'}")
                try:
                    lines = db.get_reconciliation_lines(int(row["id"]))
                    if not lines.empty:
                        ld = lines[["item_name","uom","recorded_qty","counted_qty","diff"]].copy()
                        ld.columns = ["Item","UOM","Recorded","Counted","Diff"]
                        st.dataframe(ld, width='stretch', hide_index=True)
                except Exception as exc:
                    logger.error("get_reconciliation_lines failed: %s", exc)
