import streamlit as st
import ui
import database as db
import validators as v
from logger import logger
from datetime import date

def render_reconciliation(username, sel_room_id, sel_room_name):
    ui.page_header("Reconciliation", "Physical count vs recorded stock")
    logger.debug("Rendering Reconciliation for %s", username)

    if not sel_room_id:
        st.info("Select a specific storeroom in the sidebar to start a reconciliation.")
    else:
        try:
            items_df = db.get_items(storeroom_id=sel_room_id)
        except Exception as exc:
            logger.error("get_items for recon failed: %s", exc)
            st.error("Could not load items.")
            items_df = db.pd.DataFrame()

        if items_df.empty:
            st.warning("No items in this storeroom.")
        else:
            st.markdown(f"**Counting:** {sel_room_name}")

            with st.form("recon_form"):
                c1, c2, c3 = st.columns(3)
                perf_by    = c1.text_input("Performed by", placeholder="Staff name")
                recon_date = c2.date_input("Date", value=date.today())
                recon_note = c3.text_input("Notes", placeholder="e.g. Monthly count")

                ui.section("Enter physical counts")
                header_cols = st.columns([3, 1, 1, 1])
                for col, label in zip(header_cols, ["Item", "Recorded", "Physical count", "Diff"]):
                    col.markdown(f"**{label}**")

                counts = {}
                for _, row in items_df.iterrows():
                    item_id  = int(row["id"])
                    recorded = float(row["qty"])
                    c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
                    c1.markdown(f"{row['name']} *({row['uom']})*")
                    c2.markdown(f"**{recorded:g}**")
                    counted = c3.number_input(
                        "", min_value=0.0, value=recorded, step=1.0,
                        key=f"rc_{item_id}", label_visibility="collapsed",
                    )
                    diff  = counted - recorded
                    color = "#3B6D11" if diff == 0 else ("#A32D2D" if diff < 0 else "#0C447C")
                    c4.markdown(
                        f"<span style='color:{color};font-weight:600'>{diff:+.0f}</span>",
                        unsafe_allow_html=True,
                    )
                    counts[item_id] = (recorded, counted)

                if st.form_submit_button("Apply reconciliation", type="primary"):
                    lines = [(iid, rec, cnt) for iid, (rec, cnt) in counts.items()]
                    try:
                        db.save_reconciliation(sel_room_id, perf_by.strip(), str(recon_date), recon_note.strip(), lines)
                        logger.info("Reconciliation saved for storeroom %s by %s", sel_room_id, username)
                        st.success("Reconciliation saved and stock updated.")
                        st.rerun()
                    except Exception as exc:
                        logger.error("save_reconciliation failed: %s", exc)
                        st.error("Could not save reconciliation.")
