import streamlit as st
import ui
import database as db
import validators as v
from logger import logger


def _show_attached_invoices(slip_number):
    """Display download buttons for any invoices already attached to a movement slip."""
    invoices = db.get_movement_invoices(slip_number)
    if invoices.empty:
        return
    st.caption(f"{len(invoices)} invoice(s) attached:")
    for _, inv in invoices.iterrows():
        doc = db.get_movement_invoice_file(int(inv["id"]))
        if doc:
            st.download_button(
                label=f"📄 {doc['filename']}",
                data=doc["filedata"],
                file_name=doc["filename"],
                mime=doc["mimetype"] or "application/octet-stream",
                key=f"dl_inv_{inv['id']}",
            )


def render_stock(username, sel_prop_id, sel_room_id, _safe_int, _room_opts, _sup_opts, CATEGORIES, UOMS):
    import auth as auth_module
    role = auth_module.current_role() if hasattr(auth_module, 'current_role') else st.session_state.get('role', 'staff')
    # If staff, force property filter to their assigned property
    if role == "staff":
        staff_prop_id = auth_module.current_property_id() if hasattr(auth_module, 'current_property_id') else st.session_state.get('property_id')
        sel_prop_id = staff_prop_id

    # For staff: show their own issued stock
    if role == "staff":
        ui.section("Stock issued to you")
        try:
            issued = db.get_issuances(property_id=sel_prop_id, recipient=username)
            if not issued.empty:
                disp = issued[["issued_date","item_name","qty","uom","storeroom_name","property_name","note"]].copy()
                disp.columns = ["Date","Item","Qty","UOM","Storeroom","Property","Note"]
                st.dataframe(disp, width='stretch', hide_index=True)
            else:
                st.info("No stock has been issued to you yet.")
        except Exception as exc:
            logger.error("fetch staff issued stock failed: %s", exc)
            st.error("Could not load your issued stock.")

    ui.page_header("Stock", "All items across your storerooms")
    logger.debug("Rendering Stock for %s", username)

    c_f1, c_f2, c_f3 = st.columns([2, 2, 1])
    search     = c_f1.text_input("Search", placeholder="Name or category…", label_visibility="collapsed")
    cat_filter = c_f2.text_input("Category", placeholder="Filter by category…", label_visibility="collapsed")
    low_only   = c_f3.checkbox("Low / out only")

    try:
        items_df = db.get_items(property_id=sel_prop_id, storeroom_id=sel_room_id, low_stock_only=low_only)
    except Exception as exc:
        logger.error("get_items failed: %s", exc)
        st.error("Could not load stock data.")
        items_df = db.pd.DataFrame()

    if search and not items_df.empty:
        mask = (items_df["name"].str.contains(search, case=False, na=False) |
                items_df["category"].str.contains(search, case=False, na=False))
        items_df = items_df[mask]
    if cat_filter and not items_df.empty:
        items_df = items_df[items_df["category"].str.contains(cat_filter, case=False, na=False)]

    stock_val = items_df["stock_value"].sum() if not items_df.empty else 0
    ui.metric_row([
        ("Items shown",  len(items_df), "", ""),
        ("Stock value",  ui.fmt_currency(stock_val), "", "info"),
        ("Low stock",    len(items_df[items_df["status"]=="Low"]) if not items_df.empty else 0, "", "warn"),
        ("Out of stock", len(items_df[items_df["status"]=="Out of stock"]) if not items_df.empty else 0, "", "danger"),
    ])

    if not items_df.empty:
        ui.section("Items")
        cols_show = ["name","category","property_name","storeroom_name","qty","uom","min_qty","status","supplier_name","unit_cost","stock_value"]
        disp = items_df[cols_show].copy()
        disp.columns = ["Item","Category","Property","Storeroom","Qty","UOM","Min qty","Status","Supplier","Unit cost (R)","Stock value (R)"]
        st.dataframe(disp, width='stretch', hide_index=True)
        ui.export_csv(disp, "stock_report.csv")
    else:
        st.info("No items match the current filters.")

    import auth as auth_module
    role = auth_module.current_role() if hasattr(auth_module, 'current_role') else st.session_state.get('role', 'staff')

    # Only allow add/adjust for non-staff
    if role != "staff":
        from issuance_slip import generate_movement_slip, movement_slip_download_button
        import datetime as _dt
        import pandas as _pd

        ui.section("Add new items")
        st.caption("Build up a basket of items to add, then submit all at once and download a single movement slip.")
        room_opts = _room_opts(sel_prop_id)
        sup_opts  = _sup_opts()

        if not room_opts:
            st.warning("Add a storeroom first.")
        else:
            if "_new_items_basket" not in st.session_state:
                st.session_state["_new_items_basket"] = []

            with st.form("add_item_to_basket", clear_on_submit=True):
                c1, c2, c3 = st.columns(3)
                item_name = c1.text_input("Item name *")
                item_room = c2.selectbox("Storeroom *", list(room_opts.keys()))
                item_cat  = c3.selectbox("Category", CATEGORIES)
                c4, c5, c6, c7 = st.columns(4)
                item_qty  = c4.number_input("Quantity",            min_value=0.0, step=1.0)
                item_uom  = c5.selectbox("Unit", UOMS)
                item_min  = c6.number_input("Low-stock threshold", min_value=0.0, value=1.0, step=1.0)
                item_cost = c7.number_input("Unit cost (R)",       min_value=0.0, step=0.50)
                c8, c9    = st.columns([2, 1])
                item_desc = c8.text_input("Description / notes")
                item_sup  = c9.selectbox("Supplier", list(sup_opts.keys()))

                if st.form_submit_button("Add to basket"):
                    errs = v.validate_item_form(item_name, item_room, item_qty, item_min, item_cost)
                    ok_low, warn_msg = v.min_lte_qty(item_qty, item_min)
                    if errs:
                        ui.show_errors(errs)
                    else:
                        if not ok_low:
                            st.warning(warn_msg)
                        # Warn if an item with the same name already exists in this storeroom
                        _stripped = item_name.strip().lower()
                        _room_id = room_opts[item_room]
                        existing = items_df[
                            (items_df["name"].str.lower() == _stripped) &
                            (items_df["storeroom_id"] == _room_id)
                        ]
                        if not existing.empty:
                            st.warning(
                                f"⚠️ **'{item_name.strip()}'** already exists in {item_room} "
                                f"(qty: {existing.iloc[0]['qty']:g}). Use **Quick item adjustment** "
                                f"to add stock to the existing item instead of creating a duplicate."
                            )
                        st.session_state["_new_items_basket"].append({
                            "name": item_name.strip(),
                            "room_label": item_room,
                            "room_id": room_opts[item_room],
                            "cat": item_cat,
                            "qty": item_qty,
                            "uom": item_uom,
                            "min_qty": item_min,
                            "cost": item_cost,
                            "desc": item_desc.strip(),
                            "sup_id": sup_opts[item_sup],
                        })
                        st.success(f"'{item_name.strip()}' added to basket.")

            new_basket = st.session_state["_new_items_basket"]
            if new_basket:
                st.write(f"**{len(new_basket)} item(s) in basket:**")
                for idx, entry in enumerate(new_basket):
                    col_a, col_b = st.columns([5, 1])
                    col_a.write(
                        f"{idx+1}. **{entry['name']}** — {entry['room_label']} | "
                        f"{entry['qty']:g} {entry['uom']} @ R{entry['cost']:g}"
                    )
                    if col_b.button("Remove", key=f"rm_new_{idx}"):
                        st.session_state["_new_items_basket"].pop(idx)
                        st.rerun()

                batch_notes = st.text_input("Notes for slip (optional)", key="new_items_batch_notes")

                if st.button("✅ Submit all & generate slip", type="primary", key="submit_new_items_btn"):
                    slip_items = []
                    errors = []
                    for entry in new_basket:
                        try:
                            db.add_item(
                                entry["room_id"], entry["name"], entry["cat"],
                                entry["uom"], entry["qty"], entry["min_qty"],
                                entry["sup_id"], entry["cost"], entry["desc"],
                                added_by=username,
                            )
                            logger.info("Batch add item '%s' by %s", entry["name"], username)
                            slip_items.append({
                                "name": entry["name"],
                                "storeroom": entry["room_label"],
                                "qty_before": 0,
                                "change": entry["qty"],
                                "qty_after": entry["qty"],
                                "uom": entry["uom"],
                            })
                        except Exception as exc:
                            logger.error("add_item failed for '%s': %s", entry["name"], exc)
                            errors.append(entry["name"])

                    if errors:
                        st.error(f"Failed to add: {', '.join(errors)}")

                    if slip_items:
                        storerooms = list(dict.fromkeys(e["room_label"] for e in new_basket))
                        prop_label = storerooms[0] if len(storerooms) == 1 else ", ".join(storerooms[:3])
                        slip_num = "SMV-" + _dt.datetime.now().strftime("%Y%m%d%H%M%S")
                        movement = {
                            "slip_number": slip_num,
                            "movement_date": _dt.datetime.now().strftime("%d %B %Y %H:%M"),
                            "recorded_by": username,
                            "property_name": prop_label,
                            "reason": "New items added",
                            "notes": batch_notes.strip() if batch_notes else "",
                            "items": slip_items,
                        }
                        st.session_state["_new_items_slip"] = (generate_movement_slip(movement), slip_num)
                        st.session_state["_new_items_movement"] = movement
                        st.session_state["_new_items_basket"] = []
                        st.success(f"{len(slip_items)} item(s) added to stock.")
                        st.rerun()

        if st.session_state.get("_new_items_slip"):
            slip_html, slip_num = st.session_state["_new_items_slip"]
            movement_slip_download_button(slip_html, slip_num, st)
            # Invoice attachment for new items
            inv_files = st.file_uploader(
                "📎 Attach invoice(s) for this delivery",
                type=["pdf", "png", "jpg", "jpeg"],
                accept_multiple_files=True,
                key="inv_new_items",
            )
            if inv_files:
                if st.button("Upload invoice(s)", key="upload_inv_new_items"):
                    for f in inv_files:
                        db.add_movement_invoice(slip_num, username, f.name, f.read(), f.type)
                    # Regenerate slip with invoice references
                    mvmt = st.session_state.get("_new_items_movement", {})
                    inv_records = db.get_movement_invoices(slip_num)
                    mvmt["invoices"] = [{"filename": r["filename"]} for _, r in inv_records.iterrows()]
                    st.session_state["_new_items_slip"] = (generate_movement_slip(mvmt), slip_num)
                    st.success(f"{len(inv_files)} invoice(s) attached to {slip_num}.")
                    st.rerun()
            _show_attached_invoices(slip_num)
            if st.button("Clear slip", key="clear_new_items_slip"):
                del st.session_state["_new_items_slip"]
                st.session_state.pop("_new_items_movement", None)
                st.rerun()

        if not items_df.empty:
            _ADJ_REASONS = ["Count correction", "Damage / Loss", "Supplier delivery", "Write-off", "Other"]

            # ── Single adjustment ────────────────────────────────────────────
            ui.section("Quick item adjustment")
            item_names = {f"{r['name']} ({r['storeroom_name']})": _safe_int(r["id"]) for _, r in items_df.iterrows()}
            _PLACEHOLDER = "— Select an item —"
            with st.form("adj_qty", clear_on_submit=True):
                c1, c2, c3 = st.columns([3, 1, 1])
                sel_item  = c1.selectbox("Item", [_PLACEHOLDER] + list(item_names.keys()))
                delta     = c2.number_input("Qty change (+/−)", step=1.0)
                new_cost  = c3.number_input("New unit cost (R)", min_value=0.0, step=0.50, value=0.0,
                                            help="Cost of the new stock. When adding qty, a weighted average is calculated automatically. Leave at 0 to keep current cost.")
                reason   = st.selectbox("Reason", _ADJ_REASONS)
                notes    = st.text_input("Notes (optional)")
                if st.form_submit_button("Apply", type="primary"):
                    if sel_item == _PLACEHOLDER:
                        st.warning("Please select an item first.")
                    elif delta == 0 and new_cost == 0:
                        st.warning("No change — enter a quantity change and/or a new unit cost.")
                    else:
                        try:
                            cost_arg = new_cost if new_cost > 0 else None
                            qty_before, qty_after, cost_before, cost_after = db.adjust_qty(
                                item_names[sel_item], delta, new_unit_cost=cost_arg,
                                changed_by=username, reason=reason)
                            logger.info("Adjusted item %s by %s: qty %+.0f, cost %s→%s",
                                        item_names[sel_item], username, delta, cost_before, cost_after)
                            parts = []
                            if delta != 0:
                                sign = "+" if delta > 0 else ""
                                parts.append(f"qty {sign}{int(delta)}")
                            if cost_arg is not None:
                                parts.append(f"cost R{cost_before:.2f} → R{cost_after:.2f}")
                            st.success(f"{sel_item.split(' (')[0]}: {', '.join(parts)} applied.")
                            # Build movement slip
                            item_row = items_df[items_df["id"] == item_names[sel_item]].iloc[0]
                            slip_num = "SMV-" + _dt.datetime.now().strftime("%Y%m%d%H%M%S")
                            movement = {
                                "slip_number": slip_num,
                                "movement_date": _dt.datetime.now().strftime("%d %B %Y %H:%M"),
                                "recorded_by": username,
                                "property_name": item_row.get("property_name", "—"),
                                "reason": reason,
                                "notes": notes.strip() if notes else "",
                                "items": [{
                                    "name": item_row["name"],
                                    "storeroom": item_row.get("storeroom_name", "—"),
                                    "qty_before": qty_before,
                                    "change": delta,
                                    "qty_after": qty_after,
                                    "uom": item_row.get("uom", ""),
                                    "cost_before": cost_before,
                                    "cost_after": cost_after,
                                }],
                            }
                            st.session_state["_single_movement_slip"] = (generate_movement_slip(movement), slip_num)
                            st.session_state["_single_movement"] = movement
                        except Exception as exc:
                            logger.error("adjust_qty failed: %s", exc)
                            st.error("Could not adjust quantity.")

            if st.session_state.get("_single_movement_slip"):
                slip_html, slip_num = st.session_state["_single_movement_slip"]
                movement_slip_download_button(slip_html, slip_num, st)
                # Invoice attachment for single adjustment
                inv_files = st.file_uploader(
                    "📎 Attach invoice(s) for this delivery",
                    type=["pdf", "png", "jpg", "jpeg"],
                    accept_multiple_files=True,
                    key="inv_single_adj",
                )
                if inv_files:
                    if st.button("Upload invoice(s)", key="upload_inv_single"):
                        for f in inv_files:
                            db.add_movement_invoice(slip_num, username, f.name, f.read(), f.type)
                        mvmt = st.session_state.get("_single_movement", {})
                        inv_records = db.get_movement_invoices(slip_num)
                        mvmt["invoices"] = [{"filename": r["filename"]} for _, r in inv_records.iterrows()]
                        st.session_state["_single_movement_slip"] = (generate_movement_slip(mvmt), slip_num)
                        st.success(f"{len(inv_files)} invoice(s) attached to {slip_num}.")
                        st.rerun()
                _show_attached_invoices(slip_num)
                if st.button("Clear slip", key="clear_single_slip"):
                    del st.session_state["_single_movement_slip"]
                    st.session_state.pop("_single_movement", None)
                    st.rerun()

            # ── Batch adjustment ─────────────────────────────────────────────
            ui.section("Batch item adjustment")
            st.caption("Add multiple items to the batch, then record all at once and download a single movement slip.")

            if "_batch_adj" not in st.session_state:
                st.session_state["_batch_adj"] = []

            with st.form("batch_adj_add", clear_on_submit=True):
                bc1, bc2, bc3, bc4 = st.columns([3, 1, 1, 2])
                b_item   = bc1.selectbox("Item", [_PLACEHOLDER] + list(item_names.keys()), key="batch_item_sel")
                b_delta  = bc2.number_input("Qty change (+/−)", step=1.0, key="batch_delta_inp")
                b_cost   = bc3.number_input("New cost (R)", min_value=0.0, step=0.50, value=0.0,
                                            key="batch_cost_inp", help="0 = keep current")
                b_reason = bc4.selectbox("Reason", _ADJ_REASONS, key="batch_reason_sel")
                if st.form_submit_button("Add to batch"):
                    if b_item == _PLACEHOLDER:
                        st.warning("Please select an item first.")
                    elif b_delta == 0 and b_cost == 0:
                        st.warning("Enter a quantity change and/or a new unit cost.")
                    else:
                        st.session_state["_batch_adj"].append({
                            "label": b_item,
                            "item_id": item_names[b_item],
                            "delta": b_delta,
                            "new_cost": b_cost if b_cost > 0 else None,
                            "reason": b_reason,
                        })
                        st.success(f"Added: {b_item.split(' (')[0]}")

            basket = st.session_state["_batch_adj"]
            if basket:
                st.write(f"**{len(basket)} item(s) in batch:**")
                for idx, entry in enumerate(basket):
                    sign = "+" if entry["delta"] > 0 else ""
                    cost_label = f"  |  cost → R{entry['new_cost']:.2f}" if entry.get("new_cost") else ""
                    col_a, col_b = st.columns([5, 1])
                    col_a.write(f"{idx+1}. {entry['label'].split(' (')[0]}  —  {sign}{int(entry['delta'])}{cost_label}  |  _{entry['reason']}_")
                    if col_b.button("Remove", key=f"rm_batch_{idx}"):
                        st.session_state["_batch_adj"].pop(idx)
                        st.rerun()

                batch_notes = st.text_input("Batch notes (optional)", key="batch_notes_inp")

                if st.button("✅ Record all & generate slip", type="primary", key="batch_record_btn"):
                    slip_items = []
                    errors = []
                    for entry in basket:
                        try:
                            item_row = items_df[items_df["id"] == entry["item_id"]]
                            if item_row.empty:
                                raise ValueError("Item not found in current view")
                            item_row = item_row.iloc[0]
                            qty_before, qty_after, cost_before, cost_after = db.adjust_qty(
                                entry["item_id"], entry["delta"], new_unit_cost=entry.get("new_cost"),
                                changed_by=username, reason=entry["reason"])
                            logger.info("Batch adj %+.0f on item %s by %s, cost %s→%s",
                                        entry["delta"], entry["item_id"], username, cost_before, cost_after)
                            slip_items.append({
                                "name": item_row["name"],
                                "storeroom": item_row.get("storeroom_name", "—"),
                                "qty_before": qty_before,
                                "change": entry["delta"],
                                "qty_after": qty_after,
                                "uom": item_row.get("uom", ""),
                                "cost_before": cost_before,
                                "cost_after": cost_after,
                            })
                        except Exception as exc:
                            logger.error("Batch adj failed for item %s: %s", entry["item_id"], exc)
                            errors.append(entry["label"].split(" (")[0])

                    if errors:
                        st.error(f"Failed to adjust: {', '.join(errors)}")

                    if slip_items:
                        # Derive common reason or list them
                        reasons_set = list(dict.fromkeys(e["reason"] for e in basket))
                        combined_reason = " / ".join(reasons_set)
                        property_names = items_df["property_name"].dropna().unique()
                        prop_name = property_names[0] if len(property_names) == 1 else ", ".join(property_names[:3])
                        slip_num = "SMV-" + _dt.datetime.now().strftime("%Y%m%d%H%M%S")
                        movement = {
                            "slip_number": slip_num,
                            "movement_date": _dt.datetime.now().strftime("%d %B %Y %H:%M"),
                            "recorded_by": username,
                            "property_name": prop_name,
                            "reason": combined_reason,
                            "notes": batch_notes.strip() if batch_notes else "",
                            "items": slip_items,
                        }
                        st.session_state["_batch_movement_slip"] = (generate_movement_slip(movement), slip_num)
                        st.session_state["_batch_movement"] = movement
                        st.session_state["_batch_adj"] = []
                        st.success(f"{len(slip_items)} adjustment(s) recorded.")
                        st.rerun()

            if st.session_state.get("_batch_movement_slip"):
                slip_html, slip_num = st.session_state["_batch_movement_slip"]
                movement_slip_download_button(slip_html, slip_num, st)
                # Invoice attachment for batch adjustment
                inv_files = st.file_uploader(
                    "📎 Attach invoice(s) for this delivery",
                    type=["pdf", "png", "jpg", "jpeg"],
                    accept_multiple_files=True,
                    key="inv_batch_adj",
                )
                if inv_files:
                    if st.button("Upload invoice(s)", key="upload_inv_batch"):
                        for f in inv_files:
                            db.add_movement_invoice(slip_num, username, f.name, f.read(), f.type)
                        mvmt = st.session_state.get("_batch_movement", {})
                        inv_records = db.get_movement_invoices(slip_num)
                        mvmt["invoices"] = [{"filename": r["filename"]} for _, r in inv_records.iterrows()]
                        st.session_state["_batch_movement_slip"] = (generate_movement_slip(mvmt), slip_num)
                        st.success(f"{len(inv_files)} invoice(s) attached to {slip_num}.")
                        st.rerun()
                _show_attached_invoices(slip_num)
                if st.button("Clear slip", key="clear_batch_slip"):
                    del st.session_state["_batch_movement_slip"]
                    st.session_state.pop("_batch_movement", None)
                    st.rerun()

            # ── Price History ────────────────────────────────────────────────
            ui.section("Price history")
            st.caption("Track how unit costs have changed over time. Select an item to see its full cost timeline.")

            ph_item = st.selectbox("Select item", [_PLACEHOLDER] + list(item_names.keys()), key="ph_item_sel")

            if ph_item != _PLACEHOLDER:
                ph_item_id = item_names[ph_item]
                history = db.get_cost_history_for_item(ph_item_id)
                if history.empty:
                    st.info("No price changes recorded for this item yet.")
                else:
                    # Current cost
                    current_row = items_df[items_df["id"] == ph_item_id]
                    if not current_row.empty:
                        current_cost = current_row.iloc[0]["unit_cost"]
                        first_cost = history.iloc[0]["cost_after"]
                        if len(history) > 1:
                            overall_change = current_cost - first_cost
                            pct = (overall_change / first_cost * 100) if first_cost else 0
                            direction = "📈" if overall_change > 0 else "📉" if overall_change < 0 else "➡️"
                            st.metric(
                                label="Current unit cost",
                                value=f"R{current_cost:,.2f}",
                                delta=f"R{overall_change:+,.2f} ({pct:+.1f}%) since first recorded",
                                delta_color="inverse",
                            )
                        else:
                            st.metric(label="Current unit cost", value=f"R{current_cost:,.2f}")

                    # Timeline chart
                    import plotly.graph_objects as go
                    history["created_at"] = _pd.to_datetime(history["created_at"])
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=history["created_at"],
                        y=history["cost_after"],
                        mode="lines+markers",
                        name="Unit cost",
                        line=dict(color="#185FA5", width=2),
                        marker=dict(size=8),
                        hovertemplate="R%{y:,.2f}<br>%{x|%d %b %Y %H:%M}<extra></extra>",
                    ))
                    fig.update_layout(
                        plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)",
                        height=260,
                        margin=dict(l=0, r=0, t=10, b=0),
                        font=dict(size=12, color="#3d3d3a"),
                        xaxis=dict(showgrid=False, title=""),
                        yaxis=dict(gridcolor="rgba(0,0,0,0.06)", title="Unit cost (R)"),
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    # Detailed log table
                    log_display = history[["created_at", "cost_before", "cost_after", "qty_delta", "reason", "changed_by"]].copy()
                    log_display.columns = ["Date", "Cost before", "Cost after", "Qty change", "Reason", "Changed by"]
                    log_display["Date"] = log_display["Date"].dt.strftime("%d %b %Y %H:%M")
                    log_display["Cost before"] = log_display["Cost before"].apply(lambda x: f"R{x:,.2f}")
                    log_display["Cost after"] = log_display["Cost after"].apply(lambda x: f"R{x:,.2f}")
                    log_display["Qty change"] = log_display["Qty change"].apply(lambda x: f"{x:+g}" if x else "—")
                    log_display["Changed by"] = log_display["Changed by"].fillna("—")
                    log_display["Reason"] = log_display["Reason"].fillna("—")
                    st.dataframe(log_display.iloc[::-1], width='stretch', hide_index=True)
