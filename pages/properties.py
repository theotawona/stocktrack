import streamlit as st
import ui
import database as db
import validators as v
from logger import logger

def render_properties(username):
    ui.page_header("Properties", "Manage your property portfolio")
    logger.debug("Rendering Properties for %s", username)

    try:
        props_df = db.get_properties()
        if not props_df.empty:
            st.dataframe(props_df[["name","address","notes","created_at"]], width='stretch', hide_index=True)
    except Exception as exc:
        logger.error("get_properties failed: %s", exc)
        st.error("Could not load properties.")

    ui.section("Add property")
    with st.form("add_property"):
        c1, c2    = st.columns(2)
        prop_name = c1.text_input("Property name *")
        prop_addr = c2.text_input("Address")
        prop_note = st.text_input("Notes")
        if st.form_submit_button("Add property", type="primary"):
            errs = v.validate_property_form(prop_name)
            if errs:
                ui.show_errors(errs)
            else:
                try:
                    db.add_property(prop_name.strip(), prop_addr.strip(), prop_note.strip())
                    logger.info("Property '%s' added by %s", prop_name, username)
                    st.success(f"'{prop_name}' added.")
                    st.rerun()
                except Exception as exc:
                    logger.error("add_property failed: %s", exc)
                    st.error("Could not add property.")
