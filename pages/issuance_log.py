import streamlit as st
import ui
import database as db
from logger import logger

def render_issuance_log(username, sel_prop_id, sel_room_id):
    ui.page_header("Issuance log", "Full history of stock issued to recipients")
    logger.debug("Rendering Issuance Log for %s", username)

    c1, c2 = st.columns(2)
    recipient_filter = c1.text_input("Search recipient", placeholder="Name…", label_visibility="collapsed")
    month_filter     = c2.text_input("Month (YYYY-MM)", placeholder="e.g. 2026-03", label_visibility="collapsed")

    clean_month = None
    if month_filter:
        import re
        if re.match(r"^\d{4}-\d{2}$", month_filter.strip()):
            clean_month = month_filter.strip()
        else:
            st.warning("Month must be in YYYY-MM format, e.g. 2026-03")

    try:
        iss_df = db.get_issuances(
            property_id=sel_prop_id, storeroom_id=sel_room_id,
            month=clean_month, recipient=recipient_filter.strip() or None,
        )
    except Exception as exc:
        logger.error("get_issuances failed: %s", exc)
        st.error("Could not load issuance log.")
        iss_df = db.pd.DataFrame()

    if not iss_df.empty:
        ui.metric_row([
            ("Transactions",      len(iss_df),                          "", ""),
            ("Units issued",      int(iss_df["qty"].sum()),             "", "info"),
            ("Unique recipients", iss_df["recipient"].nunique(),        "", ""),
        ])

        ui.section("Records")
        disp = iss_df[["issued_date","recipient","issued_by","item_name","qty","uom",
                        "storeroom_name","property_name","note"]].copy()
        disp.columns = ["Date","Recipient","Issued by","Item","Qty","UOM","Storeroom","Property","Note"]
        st.dataframe(disp, width='stretch', hide_index=True)
        ui.export_csv(disp, "issuance_log.csv")

        ui.section("By recipient")
        by_recip = (
            iss_df.groupby("recipient")
            .agg(Transactions=("id","count"), Total_units=("qty","sum"))
            .reset_index()
            .sort_values("Total_units", ascending=False)
        )
        by_recip.columns = ["Recipient","Transactions","Total units"]
        import plotly.express as px
        fig = px.bar(by_recip.head(10), x="Recipient", y="Total units",
                     color_discrete_sequence=["#1D9E75"])
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            height=220, margin=dict(l=0,r=0,t=10,b=0),
            xaxis=dict(showgrid=False),
            yaxis=dict(gridcolor="rgba(0,0,0,0.06)"),
        )
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("No issuances found for the current filters.")
