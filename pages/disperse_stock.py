import streamlit as st
import pandas as pd
from datetime import date
import database as db
import ui
from logger import logger
import issuance_slip as slip_gen

def render_disperse_stock(username, sel_prop_id, _safe_int):
	ui.page_header("Disperse stock", "Release approved requisitions — deducts from stock and generates slip")
	logger.debug("Rendering Disperse Stock for %s", username)

	import auth as auth_module
	role = auth_module.current_role() if hasattr(auth_module, 'current_role') else st.session_state.get('role', 'staff')
	if role == "staff":
		staff_prop_id = auth_module.current_property_id() if hasattr(auth_module, 'current_property_id') else st.session_state.get('property_id')
		sel_prop_id = staff_prop_id
	try:
		approved_reqs = db.get_requisitions(status="Approved", property_id=sel_prop_id)
	except Exception as exc:
		logger.error("get_requisitions (approved) failed: %s", exc)
		st.error("Could not load approved requisitions.")
		approved_reqs = pd.DataFrame()

	if approved_reqs.empty:
		st.success("No approved requisitions waiting for dispersal.")
	else:
		ui.info_banner(f"{len(approved_reqs)} approved requisition(s) ready to disperse.", "success")

		for _, row in approved_reqs.iterrows():
			try:
				lines = db.get_requisition_lines(_safe_int(row["id"]))
			except Exception:
				lines = pd.DataFrame()

			total_val = 0.0
			if not lines.empty:
				total_val = (lines["qty_approved"].fillna(0) * lines["unit_cost"].fillna(0)).sum()

			with st.expander(
				f"{row['ref_number']}  ·  {row['requested_by']}  ·  "
				f"{row.get('property_name') or '—'}  ·  {ui.fmt_currency(total_val)}",
				expanded=True,
			):
				c1, c2, c3 = st.columns(3)
				c1.markdown(f"**Requested by:** {row['requested_by']} ({row.get('requested_by_role','')})")
				c2.markdown(f"**Purpose:** {row.get('purpose') or '—'}")
				c3.markdown(f"**Approved by:** {row.get('reviewed_by') or '—'}")

				if not lines.empty:
					disp = lines[["item_name","uom","qty_requested","qty_approved","stock_qty","unit_cost"]].copy()
					disp["total"] = disp["qty_approved"].fillna(0) * disp["unit_cost"].fillna(0)
					disp.columns  = ["Item","UOM","Requested","Approved","In stock","Unit cost (R)","Total (R)"]
					st.dataframe(disp, width='stretch', hide_index=True)

					insufficient = lines[lines["stock_qty"] < lines["qty_approved"].fillna(0)]
					for _, il in insufficient.iterrows():
						st.error(f"Insufficient stock: {il['item_name']} — {il['stock_qty']} available, {il['qty_approved']} approved")

				if st.button(f"Disperse {row['ref_number']}", key=f"disp_{row['id']}", type="primary"):
					try:
						db.disperse_requisition(_safe_int(row["id"]), username)
						logger.info("Requisition %s dispersed by %s", row["ref_number"], username)

						slip_items = [
							{
								"name":      str(ln["item_name"]),
								"qty":       float(ln["qty_approved"] or 0),
								"uom":       str(ln["uom"]),
								"unit_cost": float(ln["unit_cost"] or 0),
							}
							for _, ln in lines.iterrows()
						] if not lines.empty else []

						slip_html = slip_gen.generate_slip({
							"slip_number":    row["ref_number"],
							"issued_date":    str(date.today()),
							"recipient":      row["requested_by"],
							"issued_by":      username,
							"note":           f"Requisition: {row.get('purpose','')}",
							"property_name":  row.get("property_name",""),
							"storeroom_name": row.get("storeroom_name",""),
							"items":          slip_items,
						})
						st.session_state[f"slip_{row['ref_number']}"] = slip_html
						st.success(f"{row['ref_number']} dispersed. Download slip below.")
						st.rerun()
					except ValueError as exc:
						st.error(str(exc))
					except Exception as exc:
						logger.error("disperse_requisition %s failed: %s", row["ref_number"], exc)
						st.error("Could not disperse requisition.")
