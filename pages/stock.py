import streamlit as st
import ui
import database as db
import validators as v
from logger import logger


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

        ui.section("Add new item")
        room_opts = _room_opts(sel_prop_id)
        sup_opts  = _sup_opts()

        if not room_opts:
            st.warning("Add a storeroom first.")
        else:
            with st.form("add_item"):
                c1, c2, c3 = st.columns(3)
                item_name = c1.text_input("Item name *")
                item_room = c2.selectbox("Storeroom *", list(room_opts.keys()))
                item_cat  = c3.selectbox("Category", CATEGORIES)
                c4, c5, c6, c7 = st.columns(4)
                item_qty  = c4.number_input("Quantity",          min_value=0.0, step=1.0)
                item_uom  = c5.selectbox("Unit", UOMS)
                item_min  = c6.number_input("Low-stock threshold", min_value=0.0, value=1.0, step=1.0)
                item_cost = c7.number_input("Unit cost (R)",      min_value=0.0, step=0.50)
                c8, c9    = st.columns([2, 1])
                item_desc = c8.text_input("Description / notes")
                item_sup  = c9.selectbox("Supplier", list(sup_opts.keys()))

                if st.form_submit_button("Add item", type="primary"):
                    errs = v.validate_item_form(item_name, item_room, item_qty, item_min, item_cost)
                    ok_low, warn_msg = v.min_lte_qty(item_qty, item_min)
                    if errs:
                        ui.show_errors(errs)
                    else:
                        if not ok_low:
                            st.warning(warn_msg)
                        try:
                            db.add_item(
                                room_opts[item_room], item_name.strip(), item_cat,
                                item_uom, item_qty, item_min,
                                sup_opts[item_sup], item_cost, item_desc.strip(),
                            )
                            logger.info("Item '%s' added by %s", item_name, username)
                            st.success(f"'{item_name}' added.")
                            # Generate movement slip for the new item addition
                            slip_num = "SMV-" + _dt.datetime.now().strftime("%Y%m%d%H%M%S")
                            movement = {
                                "slip_number": slip_num,
                                "movement_date": _dt.datetime.now().strftime("%d %B %Y %H:%M"),
                                "recorded_by": username,
                                "property_name": item_room,
                                "reason": "New item added",
                                "notes": item_desc.strip() if item_desc else "",
                                "items": [{
                                    "name": item_name.strip(),
                                    "storeroom": item_room,
                                    "qty_before": 0,
                                    "change": item_qty,
                                    "qty_after": item_qty,
                                    "uom": item_uom,
                                }],
                            }
                            st.session_state["_add_item_slip"] = (generate_movement_slip(movement), slip_num)
                            st.rerun()
                        except Exception as exc:
                            logger.error("add_item failed: %s", exc)
                            st.error("Could not add item.")

        if st.session_state.get("_add_item_slip"):
            slip_html, slip_num = st.session_state["_add_item_slip"]
            movement_slip_download_button(slip_html, slip_num, st)
            if st.button("Clear slip", key="clear_add_item_slip"):
                del st.session_state["_add_item_slip"]
                st.rerun()

        if not items_df.empty:
            _ADJ_REASONS = ["Count correction", "Damage / Loss", "Supplier delivery", "Write-off", "Other"]

            # ── Single adjustment ────────────────────────────────────────────
            ui.section("Quick quantity adjustment")
            item_names = {f"{r['name']} ({r['storeroom_name']})": _safe_int(r["id"]) for _, r in items_df.iterrows()}
            _PLACEHOLDER = "— Select an item —"
            with st.form("adj_qty", clear_on_submit=True):
                c1, c2 = st.columns([3, 1])
                sel_item = c1.selectbox("Item", [_PLACEHOLDER] + list(item_names.keys()))
                delta    = c2.number_input("Change (+/−)", step=1.0)
                reason   = st.selectbox("Reason", _ADJ_REASONS)
                notes    = st.text_input("Notes (optional)")
                if st.form_submit_button("Apply", type="primary"):
                    if sel_item == _PLACEHOLDER:
                        st.warning("Please select an item first.")
                    elif delta == 0:
                        st.warning("No change — enter a non-zero value.")
                    else:
                        try:
                            qty_before, qty_after = db.adjust_qty(item_names[sel_item], delta)
                            logger.info("Qty adjusted %+.0f on item %s by %s", delta, item_names[sel_item], username)
                            sign = "+" if delta > 0 else ""
                            st.success(f"{sel_item.split(' (')[0]}: {sign}{int(delta)} applied.")
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
                                }],
                            }
                            st.session_state["_single_movement_slip"] = (generate_movement_slip(movement), slip_num)
                        except Exception as exc:
                            logger.error("adjust_qty failed: %s", exc)
                            st.error("Could not adjust quantity.")

            if st.session_state.get("_single_movement_slip"):
                slip_html, slip_num = st.session_state["_single_movement_slip"]
                movement_slip_download_button(slip_html, slip_num, st)
                if st.button("Clear slip", key="clear_single_slip"):
                    del st.session_state["_single_movement_slip"]
                    st.rerun()

            # ── Batch adjustment ─────────────────────────────────────────────
            ui.section("Batch quantity adjustment")
            st.caption("Add multiple items to the batch, then record all at once and download a single movement slip.")

            if "_batch_adj" not in st.session_state:
                st.session_state["_batch_adj"] = []

            with st.form("batch_adj_add", clear_on_submit=True):
                bc1, bc2, bc3 = st.columns([3, 1, 2])
                b_item   = bc1.selectbox("Item", [_PLACEHOLDER] + list(item_names.keys()), key="batch_item_sel")
                b_delta  = bc2.number_input("Change (+/−)", step=1.0, key="batch_delta_inp")
                b_reason = bc3.selectbox("Reason", _ADJ_REASONS, key="batch_reason_sel")
                if st.form_submit_button("Add to batch"):
                    if b_item == _PLACEHOLDER:
                        st.warning("Please select an item first.")
                    elif b_delta == 0:
                        st.warning("Enter a non-zero change.")
                    else:
                        st.session_state["_batch_adj"].append({
                            "label": b_item,
                            "item_id": item_names[b_item],
                            "delta": b_delta,
                            "reason": b_reason,
                        })
                        st.success(f"Added: {b_item.split(' (')[0]}")

            basket = st.session_state["_batch_adj"]
            if basket:
                st.write(f"**{len(basket)} item(s) in batch:**")
                for idx, entry in enumerate(basket):
                    sign = "+" if entry["delta"] > 0 else ""
                    col_a, col_b = st.columns([5, 1])
                    col_a.write(f"{idx+1}. {entry['label'].split(' (')[0]}  —  {sign}{int(entry['delta'])}  |  _{entry['reason']}_")
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
                            qty_before, qty_after = db.adjust_qty(entry["item_id"], entry["delta"])
                            logger.info("Batch adj %+.0f on item %s by %s", entry["delta"], entry["item_id"], username)
                            slip_items.append({
                                "name": item_row["name"],
                                "storeroom": item_row.get("storeroom_name", "—"),
                                "qty_before": qty_before,
                                "change": entry["delta"],
                                "qty_after": qty_after,
                                "uom": item_row.get("uom", ""),
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
                        st.session_state["_batch_adj"] = []
                        st.success(f"{len(slip_items)} adjustment(s) recorded.")
                        st.rerun()

            if st.session_state.get("_batch_movement_slip"):
                slip_html, slip_num = st.session_state["_batch_movement_slip"]
                movement_slip_download_button(slip_html, slip_num, st)
                if st.button("Clear slip", key="clear_batch_slip"):
                    del st.session_state["_batch_movement_slip"]
                    st.rerun()
