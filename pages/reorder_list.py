import streamlit as st
import ui
import database as db
from logger import logger

def render_reorder_list(sel_prop_id, sel_room_id):
    ui.page_header("Reorder list", "Items at or below their low-stock threshold")
    logger.debug("Rendering Reorder List")

    try:
        reorder_df = db.get_items(property_id=sel_prop_id, storeroom_id=sel_room_id, low_stock_only=True)
    except Exception as exc:
        logger.error("get_items (low stock) failed: %s", exc)
        st.error("Could not load reorder list.")
        reorder_df = db.pd.DataFrame()

    if reorder_df.empty:
        st.success("All items are above their reorder thresholds.")
    else:
        ui.metric_row([
            ("Items to reorder", len(reorder_df),                                              "", "warn"),
            ("Out of stock",     len(reorder_df[reorder_df["status"] == "Out of stock"]),       "", "danger"),
        ])

        ui.section("Items to reorder")
        for _, row in reorder_df.iterrows():
            detail = (
                f"{row['property_name']} · {row['storeroom_name']} · "
                f"{row['category']}  |  "
                f"Current: {row['qty']} {row['uom']}  |  "
                f"Min: {row['min_qty']} {row['uom']}  |  "
                f"Supplier: {row.get('supplier_name') or '—'}  |  "
                f"Unit cost: R {float(row.get('unit_cost', 0)):.2f}"
            )
            ui.reorder_item(str(row["name"]), detail, critical=(row["status"] == "Out of stock"))

        ui.section("Export")
        exp = reorder_df[["name","category","property_name","storeroom_name","qty","uom","min_qty","supplier_name","unit_cost"]].copy()
        exp.columns = ["Item","Category","Property","Storeroom","Current qty","UOM","Min qty","Supplier","Unit cost (R)"]
        ui.export_csv(exp, "reorder_list.csv")
