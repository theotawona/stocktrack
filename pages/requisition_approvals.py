import streamlit as st
import pandas as pd
from datetime import date
import database as db
import ui
import logging

logger = logging.getLogger(__name__)

def render_requisition_approvals(username, sel_prop_id, _safe_int):
	ui.page_header("Requisition approvals", "Review and approve or reject pending stock requests")
	logger.debug("Rendering Requisition Approvals for %s", username)

	STATUS_COLORS = {
		"Pending":          ("#FAEEDA","#854F0B"),
		"Approved":         ("#EAF3DE","#3B6D11"),
		"Partially Issued": ("#E6F1FB","#0C447C"),
		"Issued":           ("#D6EAF8","#1A5276"),
		"Rejected":         ("#FCEBEB","#A32D2D"),
		"Dispersed":        ("#E6F1FB","#0C447C"),
		"Cancelled":        ("#F1EFE8","#444441"),
	}

	try:
		counts = db.get_requisition_counts()
	except Exception:
		counts = {}

	ui.metric_row([
		("Pending",          counts.get("Pending",          0), "", "warn"),
		("Approved",         counts.get("Approved",         0), "", "ok"),
		("Partially Issued", counts.get("Partially Issued", 0), "", "info"),
		("Issued",           counts.get("Issued",           0), "", ""),
		("Rejected",         counts.get("Rejected",         0), "", "danger"),
	])

	fc1, fc2, fc3 = st.columns([2, 1, 1])
	status_filter = fc1.selectbox(
		"Status", ["All", "Pending", "Approved", "Partially Issued", "Issued", "Rejected", "Dispersed", "Cancelled"],
		label_visibility="collapsed",
	)
	date_from = fc2.date_input("From", value=None, key="appr_date_from")
	date_to   = fc3.date_input("To",   value=None, key="appr_date_to")

	try:
		reqs = db.get_requisitions(
			status=None if status_filter == "All" else status_filter,
			property_id=sel_prop_id,
			date_from=date_from or None,
			date_to=date_to or None,
		)
	except Exception as exc:
		logger.error("get_requisitions failed: %s", exc)
		st.error("Could not load requisitions.")
		reqs = pd.DataFrame()

	if reqs.empty:
		st.info(f"No {status_filter.lower()} requisitions.")
	else:
		URGENCY_COLOR = {"Normal":"#888780","Urgent":"#BA7517","Critical":"#A32D2D"}
		for _, row in reqs.iterrows():
			bg, fg    = STATUS_COLORS.get(row["status"], ("#F1EFE8","#444441"))
			urg_color = URGENCY_COLOR.get(row["urgency"],"#888780")
			with st.expander(
				f"{row['ref_number']} — {row['requested_by']} — {row['status']}",
				expanded=(row["status"] == "Pending"),
			):
				st.markdown(
					f"**Purpose:** {row.get('purpose') or '—'}  |  "
					f"**Urgency:** <span style='color:{urg_color};font-weight:600'>{row['urgency']}</span>  |  "
					f"**Submitted:** {str(row['created_at'])[:16]}",
					unsafe_allow_html=True,
				)

				try:
					lines = db.get_requisition_lines(_safe_int(row["id"]))
				except Exception as exc:
					logger.error("req lines failed: %s", exc)
					lines = pd.DataFrame()

				approved_qtys = {}
				if not lines.empty:
					hdr = st.columns([3, 1, 1, 1, 1])
					for col, lbl in zip(hdr, ["Item","UOM","Requested","In stock","Approve qty"]):
						col.markdown(f"**{lbl}**")

					for _, line in lines.iterrows():
						lc1,lc2,lc3,lc4,lc5 = st.columns([3,1,1,1,1])
						is_custom = bool(line.get("is_custom", 0))
						if is_custom:
							lc1.markdown(
								f"🛒 **{line['item_name']}** "
								f"<span style='background:#FFF3CD;color:#856404;font-size:11px;"
								f"padding:2px 6px;border-radius:4px;margin-left:4px'>Procurement needed</span>"
								+ (f"<br><small style='color:#888'>{line['custom_notes']}</small>" if line.get('custom_notes') else ""),
								unsafe_allow_html=True,
							)
							lc2.markdown(str(line["uom"]))
							lc3.markdown(str(line["qty_requested"]))
							lc4.markdown("—")
							if row["status"] == "Pending":
								approved_qtys[_safe_int(line["id"])] = lc5.number_input(
									"", min_value=0.0, value=float(line["qty_requested"]),
									step=1.0, key=f"appr_{line['id']}",
									label_visibility="collapsed",
								)
							else:
								lc5.markdown(str(line.get("qty_approved") or "—"))
						else:
							lc1.markdown(str(line["item_name"]))
							lc2.markdown(str(line["uom"]))
							lc3.markdown(str(line["qty_requested"]))
							stock_ok = float(line["stock_qty"]) >= float(line["qty_requested"])
							lc4.markdown(
								f"<span style='color:{'#3B6D11' if stock_ok else '#A32D2D'};"
								f"font-weight:600'>{line['stock_qty']}</span>",
								unsafe_allow_html=True,
							)
							if row["status"] == "Pending":
								approved_qtys[_safe_int(line["id"])] = lc5.number_input(
									"", min_value=0.0, value=float(line["qty_requested"]),
									step=1.0, key=f"appr_{line['id']}",
									label_visibility="collapsed",
								)
							else:
								lc5.markdown(str(line.get("qty_approved") or "—"))

				if row["status"] == "Pending":
					with st.form(f"review_{row['id']}"):
						review_note = st.text_input("Note to requester (optional)")
						ra, rb, _   = st.columns([1, 1, 3])
						approve_btn = ra.form_submit_button("✅ Approve", type="primary")
						reject_btn  = rb.form_submit_button("❌ Reject")
						if approve_btn or reject_btn:
							action = "Approved" if approve_btn else "Rejected"
							try:
								db.review_requisition(
									_safe_int(row["id"]), username, action,
									review_note,
									approved_qtys if approve_btn else {},
								)
								logger.info("Requisition %s %s by %s", row["ref_number"], action, username)
								st.success(f"Requisition {row['ref_number']} {action.lower()}.")
								st.rerun()
							except Exception as exc:
								logger.error("review_requisition failed: %s", exc)
								st.error("Could not save review.")
