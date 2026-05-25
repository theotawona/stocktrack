import streamlit as st
import ui
import database as db
import validators as v
from logger import logger

_CATEGORIES = ["Cleaning", "Electrical", "Maintenance", "Plumbing", "Safety", "General", "Other"]
_UOMS = ["units", "rolls", "bottles", "boxes", "packs", "litres", "kg", "metres", "tins", "pairs"]

def render_storerooms(username, sel_prop_id, _safe_int, _prop_opts):
    ui.page_header("Storerooms", "Manage storeroom locations per property")
    logger.debug("Rendering Storerooms for %s", username)
    import auth as auth_module
    role = auth_module.current_role() if hasattr(auth_module, 'current_role') else st.session_state.get('role', 'staff')

    try:
        rooms_df = db.get_storerooms(sel_prop_id)
    except Exception as exc:
        logger.error("get_storerooms failed: %s", exc)
        st.error("Could not load storerooms.")
        rooms_df = db.pd.DataFrame()

    if not rooms_df.empty:
        prop_opts = _prop_opts()
        for _, row in rooms_df.iterrows():
            room_id = _safe_int(row["id"])
            with st.expander(
                f"\U0001F4E6 {row['property_name']} — {row['name']}  ({_safe_int(row['item_count'])} items)",
                expanded=False,
            ):
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"**Location:** {row['location_notes'] or '—'}")
                    try:
                        items_in_room = db.get_items(storeroom_id=room_id)
                        stock_cols = ["name","category","qty","uom","status","unit_cost"]
                        if not items_in_room.empty:
                            disp = items_in_room[stock_cols].copy()
                            disp.columns = ["Item","Category","Qty","UOM","Status","Unit cost (R)"]
                            st.dataframe(disp, width='stretch', hide_index=True)
                        else:
                            disp = db.pd.DataFrame(columns=["Item","Category","Qty","UOM","Status","Unit cost (R)"])
                            st.info("No items in this storeroom yet.")

                        ui.export_csv(disp, f"storeroom_{room_id}_stock.csv")
                        stock_item_opts = {
                            f"{r['name']} ({r['qty']} {r['uom']})": _safe_int(r['id'])
                            for _, r in items_in_room.iterrows()
                        }
                        if role != "staff":
                            sup_opts = {"None": None}
                            for _, sup in db.get_suppliers().iterrows():
                                sup_opts[sup["name"]] = _safe_int(sup["id"])

                            with st.expander("Stock actions", expanded=False):
                                st.subheader("Add stock to this storeroom")
                                with st.form(f"add_room_stock_{room_id}", clear_on_submit=True):
                                    ac1, ac2, ac3 = st.columns(3)
                                    item_name = ac1.text_input("Item name *", key=f"add_item_name_{room_id}")
                                    item_cat  = ac2.selectbox("Category", _CATEGORIES, key=f"add_item_cat_{room_id}")
                                    item_qty  = ac3.number_input("Quantity", min_value=0.0, step=1.0, key=f"add_item_qty_{room_id}")
                                    ac4, ac5, ac6 = st.columns(3)
                                    item_uom  = ac4.selectbox("Unit", _UOMS, key=f"add_item_uom_{room_id}")
                                    item_min  = ac5.number_input("Low-stock threshold", min_value=0.0, value=1.0, step=1.0, key=f"add_item_min_{room_id}")
                                    item_cost = ac6.number_input("Unit cost (R)", min_value=0.0, step=0.50, key=f"add_item_cost_{room_id}")
                                    item_desc = st.text_input("Description / notes", key=f"add_item_desc_{room_id}")
                                    item_sup  = st.selectbox("Supplier", list(sup_opts.keys()), key=f"add_item_sup_{room_id}")
                                    if st.form_submit_button("Add item", type="primary"):
                                        errs = v.validate_item_form(item_name, row["name"], item_qty, item_min, item_cost)
                                        ok_low, warn_msg = v.min_lte_qty(item_qty, item_min)
                                        if errs:
                                            ui.show_errors(errs)
                                        else:
                                            if not ok_low:
                                                st.warning(warn_msg)
                                            try:
                                                db.add_item(
                                                    room_id,
                                                    item_name.strip(),
                                                    item_cat,
                                                    item_uom,
                                                    item_qty,
                                                    item_min,
                                                    sup_opts[item_sup],
                                                    item_cost,
                                                    item_desc.strip(),
                                                    added_by=username,
                                                )
                                                logger.info("Added item '%s' to storeroom %s by %s", item_name, room_id, username)
                                                st.success("Item added to storeroom.")
                                                st.rerun()
                                            except Exception as exc:
                                                logger.error("add_item in storeroom %s failed: %s", room_id, exc)
                                                st.error("Could not add item.")

                                st.markdown("---")
                                st.subheader("Delete an item from this storeroom")
                                with st.form(f"delete_room_stock_{room_id}"):
                                    if stock_item_opts:
                                        del_item = st.selectbox("Item", ["-- Select item --"] + list(stock_item_opts.keys()), key=f"del_room_item_{room_id}")
                                        confirm_delete_item = st.checkbox(
                                            "I understand this will permanently delete the selected item.",
                                            key=f"confirm_del_item_{room_id}",
                                        )
                                        if st.form_submit_button("Delete item", type="secondary"):
                                            if del_item == "-- Select item --":
                                                st.warning("Choose an item to delete.")
                                            elif not confirm_delete_item:
                                                st.warning("Please confirm deletion before proceeding.")
                                            else:
                                                item_id = stock_item_opts[del_item]
                                                try:
                                                    db.delete_item(item_id)
                                                    logger.warning("Deleted item %s from storeroom %s by %s", item_id, room_id, username)
                                                    st.success("Item deleted.")
                                                    st.rerun()
                                                except Exception as exc:
                                                    logger.error("delete_item %s failed: %s", item_id, exc)
                                                    st.error("Could not delete item.")
                                    else:
                                        st.info("No items to delete in this storeroom.")

                                st.markdown("---")
                                st.subheader("Adjust quantity / price")
                                with st.form(f"adjust_room_stock_{room_id}", clear_on_submit=True):
                                    if stock_item_opts:
                                        adj_item = st.selectbox("Item", ["-- Select item --"] + list(stock_item_opts.keys()), key=f"adj_room_item_{room_id}")
                                        adj_delta = st.number_input("Qty change (+/−)", step=1.0, key=f"adj_room_delta_{room_id}")
                                        adj_cost = st.number_input("New unit cost (R)", min_value=0.0, step=0.50, value=0.0, key=f"adj_room_cost_{room_id}")
                                        adj_reason = st.text_input("Reason", key=f"adj_room_reason_{room_id}")
                                        if st.form_submit_button("Apply adjustment"):
                                            if adj_item == "-- Select item --":
                                                st.warning("Please select an item first.")
                                            elif adj_delta == 0 and adj_cost == 0:
                                                st.warning("Enter a quantity change and/or a new unit cost.")
                                            else:
                                                item_id = stock_item_opts[adj_item]
                                                cost_arg = adj_cost if adj_cost > 0 else None
                                                try:
                                                    db.adjust_qty(item_id, adj_delta, cost_arg, username, adj_reason.strip() or "Storeroom adjustment")
                                                    logger.info("Adjusted item %s in storeroom %s by %s", item_id, room_id, username)
                                                    st.success("Item updated.")
                                                    st.rerun()
                                                except Exception as exc:
                                                    logger.error("adjust_qty %s failed: %s", item_id, exc)
                                                    st.error("Could not adjust item.")
                                    else:
                                        st.info("No items to adjust in this storeroom.")

                                st.markdown("---")
                                st.subheader("Transfer stock to another storeroom")
                                with st.form(f"transfer_stock_{room_id}", clear_on_submit=True):
                                    if stock_item_opts:
                                        t_item = st.selectbox("Item", ["-- Select item --"] + list(stock_item_opts.keys()), key=f"transfer_item_{room_id}")
                                        # Destination storerooms (exclude current)
                                        all_rooms = db.get_storerooms()
                                        dest_opts = {f"{r['property_name']} — {r['name']}": _safe_int(r['id']) for _, r in all_rooms.iterrows() if _safe_int(r['id']) != room_id}
                                        if dest_opts:
                                            t_dest = st.selectbox("Destination storeroom", ["-- Select --"] + list(dest_opts.keys()), key=f"transfer_dest_{room_id}")
                                        else:
                                            t_dest = None
                                        t_qty = st.number_input("Quantity to transfer", min_value=0.0, step=1.0, key=f"transfer_qty_{room_id}")
                                        t_slip = st.text_input("Slip / reference", key=f"transfer_slip_{room_id}")
                                        t_reason = st.text_input("Reason", key=f"transfer_reason_{room_id}")
                                        if st.form_submit_button("Transfer"):
                                            if t_item == "-- Select item --":
                                                st.warning("Choose an item to transfer.")
                                            elif not t_dest or t_dest == "-- Select --":
                                                st.warning("Choose a destination storeroom.")
                                            elif t_qty <= 0:
                                                st.warning("Enter a positive quantity to transfer.")
                                            else:
                                                src_item_id = stock_item_opts[t_item]
                                                dest_room_id = dest_opts[t_dest]
                                                try:
                                                    db.transfer_stock(src_item_id, dest_room_id, t_qty, transferred_by=username, reason=t_reason.strip() or "Transfer", slip_number=t_slip.strip() or None)
                                                    logger.info("Transferred %s of item %s from storeroom %s to %s by %s", t_qty, src_item_id, room_id, dest_room_id, username)
                                                    st.success("Transfer completed.")
                                                    st.rerun()
                                                except Exception as exc:
                                                    logger.error("transfer_stock failed: %s", exc)
                                                    st.error(f"Could not transfer stock: {exc}")
                                    else:
                                        st.info("No items to transfer in this storeroom.")
                    except Exception as exc:
                        logger.error("items for storeroom %s failed: %s", room_id, exc)

                with c2:
                    with st.form(f"edit_room_{room_id}"):
                        current_property_label = row["property_name"]
                        prop_names = list(prop_opts.keys())
                        selected_property = st.selectbox(
                            "Property *",
                            prop_names,
                            index=prop_names.index(current_property_label) if current_property_label in prop_names else 0,
                        )
                        new_name = st.text_input("Name", value=str(row["name"]))
                        new_loc  = st.text_input("Location notes", value=str(row["location_notes"] or ""))

                        moved = selected_property != current_property_label
                        confirm_move = False
                        if moved:
                            st.warning("Moving this storeroom will also move all stock items stored in it to the selected property.")
                            confirm_move = st.checkbox(
                                "I understand and want to move this storeroom and its items.",
                                key=f"move_confirm_{room_id}",
                            )

                        if st.form_submit_button("Save"):
                            errs = v.validate_storeroom_form(new_name, selected_property)
                            if errs:
                                ui.show_errors(errs)
                            elif moved and not confirm_move:
                                st.warning("Check the confirmation box before moving the storeroom.")
                            else:
                                try:
                                    db.update_storeroom(room_id, prop_opts[selected_property], new_name.strip(), new_loc.strip())
                                    logger.info("Storeroom %s updated by %s", room_id, username)
                                    st.success("Saved.")
                                    st.rerun()
                                except Exception as exc:
                                    logger.error("update_storeroom failed: %s", exc)
                                    st.error("Could not save changes.")

                    st.markdown("---")
                    st.warning("Deleting this storeroom will also delete all items stored in it.")
                    confirm_delete = st.checkbox(
                        "I understand this will permanently delete the storeroom and its stock items.",
                        key=f"del_confirm_{room_id}",
                    )
                    if st.button("\U0001F5D1 Delete", key=f"del_room_{room_id}", type="secondary"):
                        if not confirm_delete:
                            st.warning("Please confirm deletion before proceeding.")
                        else:
                            try:
                                db.delete_storeroom(room_id)
                                logger.warning("Storeroom %s deleted by %s", room_id, username)
                                st.rerun()
                            except Exception as exc:
                                logger.error("delete_storeroom %s failed: %s", room_id, exc)
                                st.error("Could not delete storeroom.")

                    st.markdown("---")
                    st.subheader("Duplicate this storeroom (quantities set to 0)")
                    with st.form(f"duplicate_room_{room_id}"):
                        # Allow selecting property to duplicate into (default current)
                        prop_names = list(prop_opts.keys())
                        current_property_label = row["property_name"]
                        sel_prop = st.selectbox("Target property", prop_names, index=prop_names.index(current_property_label) if current_property_label in prop_names else 0)
                        dup_name = st.text_input("New storeroom name", value=f"{row['name']} (Copy)")
                        dup_loc = st.text_input("Location notes", value=str(row["location_notes"] or ""))
                        confirm_dup = st.checkbox("I understand this will create a new storeroom with the same items but zero quantities.", key=f"dup_confirm_{room_id}")
                        if st.form_submit_button("Duplicate", type="primary"):
                            if not confirm_dup:
                                st.warning("Please confirm duplication before proceeding.")
                            else:
                                try:
                                    new_id = db.duplicate_storeroom(room_id, prop_opts[sel_prop], dup_name.strip(), dup_loc.strip(), created_by=username)
                                    logger.info("Storeroom %s duplicated to %s by %s", room_id, new_id, username)
                                    st.success(f"Storeroom duplicated (ID: {new_id}).")
                                    st.rerun()
                                except Exception as exc:
                                    logger.error("duplicate_storeroom failed: %s", exc)
                                    st.error(f"Could not duplicate storeroom: {exc}")
    else:
        st.info("No storerooms yet. Add one below.")

    ui.section("Add new storeroom")
    prop_opts = _prop_opts()
    if not prop_opts:
        st.warning("Add a property first before creating storerooms.")
    else:
        with st.form("add_storeroom"):
            sel_p    = st.selectbox("Property *", list(prop_opts.keys()))
            c1, c2   = st.columns(2)
            room_name = c1.text_input("Storeroom name *", placeholder="e.g. Block A Storeroom")
            room_loc  = c2.text_input("Location notes",   placeholder="e.g. Ground floor, room 102")
            if st.form_submit_button("Add storeroom", type="primary"):
                errs = v.validate_storeroom_form(room_name, sel_p)
                if errs:
                    ui.show_errors(errs)
                else:
                    try:
                        db.add_storeroom(prop_opts[sel_p], room_name.strip(), room_loc.strip())
                        logger.info("Storeroom '%s' added by %s", room_name, username)
                        st.success(f"Storeroom '{room_name}' added.")
                        st.rerun()
                    except Exception as exc:
                        logger.error("add_storeroom failed: %s", exc)
                        st.error("Could not add storeroom.")
