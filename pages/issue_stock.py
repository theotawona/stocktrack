import streamlit as st
import ui
import database as db
import issuance_slip as slip_gen
from logger import logger
from datetime import date, datetime


def render_issue_stock(username, sel_prop_id, sel_room_id, _item_opts):
    ui.page_header("Issue stock", "Issue stock against an approved requisition")
    logger.debug("Rendering Issue Stock for %s", username)

    import auth as auth_module
    role = auth_module.current_role() if hasattr(auth_module, 'current_role') else st.session_state.get('role', 'staff')
    if role == "staff":
        staff_prop_id = auth_module.current_property_id() if hasattr(auth_module, 'current_property_id') else st.session_state.get('property_id')
        sel_prop_id = staff_prop_id

    # Load approved / partially issued requisitions
    try:
        approved_reqs = db.get_approved_requisitions_for_issuing(property_id=sel_prop_id)
    except Exception as exc:
        logger.error("get_approved_requisitions_for_issuing failed: %s", exc)
        st.error("Could not load approved requisitions.")
        approved_reqs = db.pd.DataFrame()

    if approved_reqs.empty:
        st.info(
            "No approved requisitions available for issuing. "
            "A requisition must be submitted and approved before stock can be issued against it."
        )
    else:
        req_labels = {
            f"{row['ref_number']} — {row['requested_by']}  ({row.get('property_name', '')})": int(row['id'])
            for _, row in approved_reqs.iterrows()
        }
        sel_label   = st.selectbox("Select approved requisition", list(req_labels.keys()), key="sel_req_label")
        sel_req_id  = req_labels[sel_label]
        sel_req_row = approved_reqs[approved_reqs['id'] == sel_req_id].iloc[0]

        with st.expander("Issuance details", expanded=True):
            c1, c2, c3 = st.columns(3)
            c1.text_input("Recipient", value=str(sel_req_row.get('requested_by', '')), disabled=True)
            c2.text_input("Issued by", value=st.session_state.get("display_name", username), key="iss_by")
            c3.date_input("Date", value=date.today(), key="iss_date")
            st.text_input("Note / reason", value=str(sel_req_row.get('purpose', '')), key="iss_note")

        # Load remaining lines for the selected requisition
        try:
            lines_df = db.get_requisition_lines_remaining(sel_req_id)
        except Exception as exc:
            logger.error("get_requisition_lines_remaining failed: %s", exc)
            st.error("Could not load requisition lines.")
            lines_df = db.pd.DataFrame()

        if lines_df.empty:
            st.warning("This requisition has no approved stocked items remaining to issue.")
        else:
            ui.section("Items to issue")
            hdr = st.columns([3, 1, 1, 1, 1])
            for col, lbl in zip(hdr, ["Item", "UOM", "Approved", "Already issued", "Issue now"]):
                col.markdown(f"**{lbl}**")

            issue_quantities = {}
            for _, line in lines_df.iterrows():
                c1, c2, c3, c4, c5 = st.columns([3, 1, 1, 1, 1])
                c1.markdown(str(line["item_name"]))
                c2.markdown(str(line["uom"]))
                approved = float(line["qty_approved"])
                dispersed = float(line["qty_dispersed"])
                remaining = float(line["qty_remaining"])
                c3.markdown(str(int(approved)))
                c4.markdown(str(int(dispersed)))
                if remaining > 0:
                    qty = c5.number_input(
                        "", min_value=0.0, max_value=remaining,
                        value=remaining, step=1.0,
                        key=f"issue_line_{line['id']}",
                        label_visibility="collapsed",
                    )
                    issue_quantities[int(line["id"])] = {
                        "item_id":   int(line["item_id"]),
                        "qty":       qty,
                        "name":      str(line["item_name"]),
                        "uom":       str(line["uom"]),
                        "unit_cost": float(line["unit_cost"]),
                    }
                else:
                    c5.markdown("✅ Fully issued")

            if issue_quantities:
                if st.button("✅ Confirm & record issuance", type="primary"):
                    lines_to_issue = [
                        (lid, v["item_id"], v["qty"])
                        for lid, v in issue_quantities.items()
                        if v["qty"] > 0
                    ]
                    if not lines_to_issue:
                        st.warning("Enter at least one quantity greater than zero.")
                    else:
                        try:
                            result = db.issue_against_requisition(
                                req_id=sel_req_id,
                                issued_by=st.session_state.get("iss_by", username),
                                issued_date=str(st.session_state.get("iss_date", date.today())),
                                note=st.session_state.get("iss_note", ""),
                                lines_to_issue=lines_to_issue,
                            )
                            new_status = result.get("status", "Partially Issued")
                            issued_lines = result.get("issued_lines", [])
                            shortfalls = result.get("shortfalls", [])
                            restock_needed = result.get("restock_needed", [])

                            logger.info(
                                "Issued against requisition %s by %s — new status: %s",
                                sel_req_row['ref_number'], username, new_status,
                            )
                            unit_cost_by_item = {v["item_id"]: v["unit_cost"] for v in issue_quantities.values()}
                            slip_items = [
                                {
                                    "name":      line["item_name"],
                                    "qty":       line["qty"],
                                    "uom":       line["uom"],
                                    "unit_cost": unit_cost_by_item.get(line["item_id"], 0.0),
                                }
                                for line in issued_lines
                            ]
                            if slip_items:
                                slip_num = datetime.now().strftime("%Y%m%d%H%M%S")
                                st.session_state.last_slip = slip_gen.generate_slip({
                                    "slip_number":    slip_num,
                                    "issued_date":    str(st.session_state.get("iss_date", date.today())),
                                    "recipient":      str(sel_req_row.get('requested_by', '')),
                                    "issued_by":      st.session_state.get("iss_by", username),
                                    "note":           st.session_state.get("iss_note", ""),
                                    "property_name":  str(sel_req_row.get('property_name', '')),
                                    "storeroom_name": str(sel_req_row.get('storeroom_name', '')),
                                    "items":          slip_items,
                                })

                            st.session_state.issue_shortfalls = shortfalls
                            st.session_state.issue_restock_needed = restock_needed

                            if issued_lines:
                                st.success(
                                    f"Stock issued for requisition {sel_req_row['ref_number']}. "
                                    f"Requisition status: **{new_status}**."
                                )
                            else:
                                st.warning(
                                    "No stock could be issued right now due to insufficient availability. "
                                    f"Requisition status remains **{new_status}**."
                                )
                            st.rerun()
                        except ValueError as exc:
                            st.error(str(exc))
                        except Exception as exc:
                            logger.error("issue_against_requisition failed: %s", exc)
                            st.error(f"Could not record issuance: {exc}")

        # ── Procured / unlisted items ──────────────────────────────────────
        try:
            custom_df = db.get_requisition_custom_lines_remaining(sel_req_id)
        except Exception as exc:
            logger.error("get_requisition_custom_lines_remaining failed: %s", exc)
            custom_df = db.pd.DataFrame()

        if not custom_df.empty:
            ui.section("Procured / unlisted items")
            st.caption(
                "These items were requested but were not in stock. "
                "Once you have received them, mark each as fulfilled to record the issuance "
                "and add the item to the stock catalogue for future requisitions."
            )
            try:
                rooms_df = db.get_storerooms(property_id=sel_prop_id)
                room_opts = {
                    f"{r['name']}": int(r['id'])
                    for _, r in rooms_df.iterrows()
                } if not rooms_df.empty else {}
            except Exception:
                room_opts = {}

            _CATEGORIES = ["Cleaning", "Electrical", "Maintenance", "Plumbing", "Safety", "General", "Other"]
            _PLACEHOLDER_ROOM = "— Select storeroom —"

            for _, cline in custom_df.iterrows():
                if float(cline["qty_remaining"]) <= 0:
                    continue
                with st.expander(
                    f"📦 {cline['item_name']} — {int(cline['qty_approved'])} {cline['uom']}  *(pending procurement)*",
                    expanded=True,
                ):
                    if cline["notes"]:
                        st.caption(f"Notes / specs: {cline['notes']}")
                    with st.form(f"custom_fulfill_{int(cline['id'])}"):
                        cf1, cf2, cf3 = st.columns(3)
                        room_sel = cf1.selectbox(
                            "Add to storeroom *",
                            [_PLACEHOLDER_ROOM] + list(room_opts.keys()),
                        )
                        cat_sel = cf2.selectbox("Category", _CATEGORIES)
                        cost_sel = cf3.number_input("Unit cost (R)", min_value=0.0, step=0.50)
                        if st.form_submit_button("✅ Mark as received & issue", type="primary"):
                            if room_sel == _PLACEHOLDER_ROOM:
                                st.warning("Please select a storeroom to assign this item to.")
                            else:
                                try:
                                    new_status, new_item_id = db.mark_custom_line_fulfilled(
                                        line_id=int(cline['id']),
                                        issued_by=st.session_state.get("iss_by", username),
                                        req_id=sel_req_id,
                                        storeroom_id=room_opts[room_sel],
                                        category=cat_sel,
                                        unit_cost=cost_sel,
                                        issued_date=str(st.session_state.get("iss_date", date.today())),
                                        note=st.session_state.get("iss_note", ""),
                                    )
                                    logger.info(
                                        "Custom line %s fulfilled by %s, item_id=%s, req status=%s",
                                        cline['id'], username, new_item_id, new_status
                                    )
                                    st.success(
                                        f"'{cline['item_name']}' added to stock catalogue and issued. "
                                        f"Requisition status: **{new_status}**."
                                    )
                                    st.rerun()
                                except Exception as exc:
                                    logger.error("mark_custom_line_fulfilled failed: %s", exc)
                                    st.error(f"Could not complete: {exc}")

    if st.session_state.get("issue_shortfalls"):
        ui.section("Items not fully issued")
        short_df = db.pd.DataFrame(st.session_state.get("issue_shortfalls", []))
        if not short_df.empty:
            show_short = short_df[["item_name", "requested_now", "issued_now", "short_now", "stock_available", "uom"]].copy()
            show_short.columns = ["Item", "Requested now", "Issued now", "Short now", "Stock available", "UOM"]
            st.dataframe(show_short, width='stretch', hide_index=True)

    if st.session_state.get("issue_restock_needed"):
        ui.section("Restock needed to fully issue requisition")
        restock_df = db.pd.DataFrame(st.session_state.get("issue_restock_needed", []))
        if not restock_df.empty:
            show_restock = restock_df[["item_name", "remaining_to_issue", "stock_available", "need_to_add", "uom"]].copy()
            show_restock.columns = ["Item", "Remaining to issue", "Stock available", "Need to add", "UOM"]
            st.dataframe(show_restock, width='stretch', hide_index=True)

    if st.session_state.get('last_slip'):
        ui.section("Issuance slip ready")
        slip_gen.slip_download_button(st.session_state.last_slip, datetime.now().strftime("%Y%m%d"), st)
        st.caption("Open the downloaded file in a browser, then Ctrl+P / Cmd+P to print or save as PDF.")
        if st.button("Clear slip"):
            st.session_state.last_slip = None
            st.rerun()

    ui.section("Recent issuances")
    try:
        recent = db.get_issuances(property_id=sel_prop_id, storeroom_id=sel_room_id)
        if not recent.empty:
            disp = recent[["issued_date", "recipient", "issued_by", "item_name", "qty", "uom",
                           "storeroom_name", "property_name", "note"]].head(20).copy()
            disp.columns = ["Date", "Recipient", "Issued by", "Item", "Qty", "UOM",
                            "Storeroom", "Property", "Note"]
            st.dataframe(disp, width='stretch', hide_index=True)
        else:
            st.info("No issuances recorded yet.")
    except Exception as exc:
        logger.error("recent issuances fetch failed: %s", exc)
        st.error("Could not load recent issuances.")
