import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import ui
import database as db
from logger import logger

def render_overview(username, sel_prop_id, sel_room_id):
    ui.page_header("Overview", "Stock health across all properties")
    logger.debug("Rendering Overview for %s", username)

    try:
        items_df    = db.get_items(property_id=sel_prop_id, storeroom_id=sel_room_id)
        issuances_df = db.get_issuances(property_id=sel_prop_id)
    except Exception as exc:
        logger.error("Overview data fetch failed: %s", exc)
        st.error("Could not load overview data.")
        st.stop()

    total_items  = len(items_df)
    ok_count     = len(items_df[items_df["status"] == "OK"])
    low_count    = len(items_df[items_df["status"] == "Low"])
    out_count    = len(items_df[items_df["status"] == "Out of stock"])
    total_value  = items_df["stock_value"].sum() if not items_df.empty else 0
    no_cost_count = len(items_df[items_df["unit_cost"] <= 0]) if not items_df.empty else 0

    issued_30d = 0
    if not issuances_df.empty:
        try:
            cutoff = pd.Timestamp.now() - pd.Timedelta(days=30)
            issued_30d = issuances_df[pd.to_datetime(issuances_df["issued_date"]) >= cutoff]["qty"].sum()
        except Exception:
            pass

    ui.metric_row([
        ("Total items",  total_items,  "", ""),
        ("In stock",     ok_count,     "", "ok"),
        ("Low stock",    low_count,    "", "warn"),
        ("Out of stock", out_count,    "", "danger"),
        ("No cost set",  no_cost_count, "", "warn" if no_cost_count else ""),
        ("Stock value",  ui.fmt_currency(total_value), f"{int(issued_30d)} units issued (30d)", "info"),
    ])

    ui.section("Stock by storeroom")
    try:
        store_summary = db.get_stock_value_by_storeroom(sel_prop_id)
    except Exception as exc:
        logger.error("store summary failed: %s", exc)
        store_summary = pd.DataFrame()

    if not store_summary.empty:
        col_a, col_b = st.columns([3, 2])
        with col_a:
            fig = px.bar(
                store_summary, x="storeroom", y="total_value",
                color="property", text_auto=".2s",
                color_discrete_sequence=["#1D9E75","#378ADD","#D85A30","#7F77DD"],
                labels={"total_value": "Stock value (R)", "storeroom": ""},
            )
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                showlegend=True, height=280, margin=dict(l=0,r=0,t=10,b=0),
                font=dict(size=12, color="#3d3d3a"),
                xaxis=dict(showgrid=False),
                yaxis=dict(gridcolor="rgba(0,0,0,0.06)"),
            )
            st.plotly_chart(fig, width='stretch')

        with col_b:
            for _, row in store_summary.iterrows():
                low = int(row.get("low_stock", 0))
                out = int(row.get("out_of_stock", 0))
                parts = []
                if low: parts.append(f"⚠ {low} low")
                if out: parts.append(f"🔴 {out} out")
                ui.store_card(
                    str(row["storeroom"]), str(row["property"]),
                    int(row.get("items", 0)),
                    ui.fmt_currency(row.get("total_value", 0)),
                    " · ".join(parts),
                )

    ui.section("Issuance trend (last 6 months)")
    try:
        monthly = db.get_monthly_summary(sel_prop_id, months=6)
    except Exception as exc:
        logger.error("monthly summary failed: %s", exc)
        monthly = pd.DataFrame()

    if not monthly.empty:
        monthly["month_label"] = pd.to_datetime(monthly["month"] + "-01").dt.strftime("%b %Y")
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=monthly["month_label"], y=monthly["units_issued"],
                              name="Units issued", marker_color="#D85A30", opacity=0.85))
        fig2.add_trace(go.Scatter(x=monthly["month_label"], y=monthly["recipients"],
                                   name="Recipients", mode="lines+markers",
                                   line=dict(color="#185FA5", width=2), yaxis="y2"))
        fig2.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            height=240, margin=dict(l=0,r=0,t=10,b=0),
            font=dict(size=12, color="#3d3d3a"),
            xaxis=dict(showgrid=False),
            yaxis=dict(gridcolor="rgba(0,0,0,0.06)", title="Units"),
            yaxis2=dict(overlaying="y", side="right", title="Recipients", showgrid=False),
            legend=dict(orientation="h", y=-0.2),
        )
        st.plotly_chart(fig2, width='stretch')

    low_count = len(items_df[items_df["status"] == "Low"])
    out_count = len(items_df[items_df["status"] == "Out of stock"])
    if low_count + out_count > 0:
        ui.section("Attention needed")
        alerts = items_df[items_df["status"] != "OK"]
        for _, row in alerts.iterrows():
            detail = (f"{row['property_name']} · {row['storeroom_name']} · "
                      f"{row['qty']} / {row['min_qty']} {row['uom']} · "
                      f"Supplier: {row.get('supplier_name') or '—'}")
            ui.reorder_item(str(row["name"]), detail, critical=(row["status"] == "Out of stock"))
