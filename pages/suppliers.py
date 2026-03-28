import streamlit as st
import ui
import database as db
import validators as v
from logger import logger

def render_suppliers(username):
    ui.page_header("Suppliers", "Manage vendors and suppliers")
    logger.debug("Rendering Suppliers for %s", username)

    try:
        sups_df = db.get_suppliers()
        if not sups_df.empty:
            st.dataframe(sups_df[["name","contact","phone","email","notes"]], width='stretch', hide_index=True)
    except Exception as exc:
        logger.error("get_suppliers failed: %s", exc)
        st.error("Could not load suppliers.")

    ui.section("Add supplier")
    with st.form("add_supplier"):
        c1, c2      = st.columns(2)
        sup_name    = c1.text_input("Supplier name *")
        sup_contact = c2.text_input("Contact person")
        c3, c4      = st.columns(2)
        sup_phone   = c3.text_input("Phone")
        sup_email   = c4.text_input("Email")
        sup_note    = st.text_input("Notes")
        if st.form_submit_button("Add supplier", type="primary"):
            errs = v.validate_supplier_form(sup_name)
            ok_e, msg_e = v.email(sup_email)
            if not ok_e:
                errs.append(msg_e)
            if errs:
                ui.show_errors(errs)
            else:
                try:
                    db.add_supplier(sup_name.strip(), sup_contact.strip(), sup_phone.strip(), sup_email.strip(), sup_note.strip())
                    logger.info("Supplier '%s' added by %s", sup_name, username)
                    st.success(f"'{sup_name}' added.")
                    st.rerun()
                except Exception as exc:
                    logger.error("add_supplier failed: %s", exc)
                    st.error("Could not add supplier.")
