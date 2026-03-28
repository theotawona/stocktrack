import streamlit as st
import ui
import database as db
import validators as v
from logger import logger

def render_storerooms(username, sel_prop_id, _safe_int, _prop_opts):
    ui.page_header("Storerooms", "Manage storeroom locations per property")
    logger.debug("Rendering Storerooms for %s", username)

    try:
        rooms_df = db.get_storerooms(sel_prop_id)
    except Exception as exc:
        logger.error("get_storerooms failed: %s", exc)
        st.error("Could not load storerooms.")
        rooms_df = db.pd.DataFrame()

    if not rooms_df.empty:
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
                        if not items_in_room.empty:
                            disp = items_in_room[["name","category","qty","uom","status","unit_cost"]].copy()
                            disp.columns = ["Item","Category","Qty","UOM","Status","Unit cost (R)"]
                            st.dataframe(disp, width='stretch', hide_index=True)
                    except Exception as exc:
                        logger.error("items for storeroom %s failed: %s", room_id, exc)

                with c2:
                    with st.form(f"edit_room_{room_id}"):
                        new_name = st.text_input("Name", value=str(row["name"]))
                        new_loc  = st.text_input("Location notes", value=str(row["location_notes"] or ""))
                        if st.form_submit_button("Save"):
                            errs = v.validate_storeroom_form(new_name, "placeholder")
                            errs = [e for e in errs if "Property" not in e]  # property already set
                            if errs:
                                ui.show_errors(errs)
                            else:
                                try:
                                    db.update_storeroom(room_id, new_name.strip(), new_loc.strip())
                                    logger.info("Storeroom %s updated by %s", room_id, username)
                                    st.success("Saved.")
                                    st.rerun()
                                except Exception as exc:
                                    logger.error("update_storeroom failed: %s", exc)
                                    st.error("Could not save changes.")

                    if st.button("\U0001F5D1 Delete", key=f"del_room_{room_id}", type="secondary"):
                        try:
                            db.delete_storeroom(room_id)
                            logger.warning("Storeroom %s deleted by %s", room_id, username)
                            st.rerun()
                        except Exception as exc:
                            logger.error("delete_storeroom %s failed: %s", room_id, exc)
                            st.error("Could not delete storeroom.")
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
