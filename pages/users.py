import streamlit as st
import ui
import auth as auth_module
import validators as v
from logger import logger
import pandas as pd

def render_users(username):
    ui.page_header("Users", "Manage staff access and roles")
    logger.debug("Rendering Users page for %s", username)

    st.markdown(
        "<div class='reorder-item'>"
        "<div class='ri-name'>Role summary</div>"
        "<div class='ri-detail'>"
        "Admin — full access &nbsp;|&nbsp; "
        "Manager — all except Users &nbsp;|&nbsp; "
        "Staff — Stock, Issue, Reconcile, Reorder, Requisitions"
        "</div></div>",
        unsafe_allow_html=True,
    )


    users = auth_module.get_all_users()
    properties = []
    try:
        import database
        properties = database.get_properties().to_dict(orient="records")
    except Exception as exc:
        logger.error("Failed to load properties: %s", exc)
    property_choices = {int(p['id']): p['name'] for p in properties}

    # Show users table with property assignment
    if users:
        df = pd.DataFrame(users)
        if 'property_id' in df.columns:
            def get_property_name(pid):
                try:
                    if pid is None or pd.isna(pid):
                        return "(None)"
                    return property_choices.get(int(pid), "(None)")
                except Exception:
                    return "(None)"
            df['property'] = df['property_id'].apply(get_property_name)
        st.dataframe(df[["username","name","email","role","property"]] if 'property' in df.columns else df[["username","name","email","role"]],
                     width='stretch', hide_index=True)


    ui.section("Add user")
    with st.form("add_user"):
        c1, c2       = st.columns(2)
        new_uname    = c1.text_input("Username *", placeholder="e.g. sipho_m")
        new_name     = c2.text_input("Full name *", placeholder="e.g. Sipho Mokoena")
        c3, c4       = st.columns(2)
        new_email    = c3.text_input("Email")
        new_role     = c4.selectbox("Role", ["staff","manager","admin"])
        new_password = st.text_input("Password *", type="password")
        new_property = None
        if property_choices and new_role == "staff":
            new_property = st.selectbox("Assign property", options=["(None)"] + list(property_choices.keys()), format_func=lambda x: property_choices.get(x, "(None)"))

        if st.form_submit_button("Add user", type="primary"):
            errs = v.validate_user_form(new_uname, new_name, new_password, new_email)
            if errs:
                ui.show_errors(errs)
            else:
                try:
                    auth_module.add_user(new_uname.strip(), new_name.strip(), new_email.strip(), new_password, new_role)
                    # Assign property if staff and property selected
                    if new_role == "staff" and new_property and new_property != "(None)":
                        auth_module.update_user_property(new_uname.strip(), int(new_property))
                    logger.info("User '%s' created by admin %s", new_uname, username)
                    st.success(f"User '{new_name}' added.")
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))
                except Exception as exc:
                    logger.error("add_user failed: %s", exc)
                    st.error("Could not add user.")

    ui.section("Change role / remove user / assign property")
    other_users = [u["username"] for u in users if u["username"] != username]
    if other_users:
        with st.form("manage_user"):
            c1, c2, c3 = st.columns(3)
            sel_manage  = c1.selectbox("User", other_users)
            new_r       = c2.selectbox("New role", ["staff","manager","admin"])
            action      = c3.radio("Action", ["Change role","Delete user","Assign property"])
            assign_property = None
            if action == "Assign property" and property_choices:
                assign_property = st.selectbox("Property to assign", options=["(None)"] + list(property_choices.keys()), format_func=lambda x: property_choices.get(x, "(None)"))
            if st.form_submit_button("Apply"):
                try:
                    if action == "Change role":
                        auth_module.update_user_role(sel_manage, new_r)
                        logger.info("Role of '%s' changed to '%s' by %s", sel_manage, new_r, username)
                        st.success(f"Role updated for {sel_manage}.")
                    elif action == "Assign property":
                        if assign_property and assign_property != "(None)":
                            auth_module.update_user_property(sel_manage, int(assign_property))
                            logger.info("Property of '%s' set to '%s' by %s", sel_manage, assign_property, username)
                            st.success(f"Property assigned for {sel_manage}.")
                        else:
                            auth_module.update_user_property(sel_manage, None)
                            logger.info("Property of '%s' cleared by %s", sel_manage, username)
                            st.success(f"Property cleared for {sel_manage}.")
                    else:
                        auth_module.delete_user(sel_manage)
                        logger.warning("User '%s' deleted by admin %s", sel_manage, username)
                        st.success(f"User {sel_manage} removed.")
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))
                except Exception as exc:
                    logger.error("manage_user failed: %s", exc)
                    st.error("Operation failed.")
    else:
        st.info("No other users to manage.")
