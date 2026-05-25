import streamlit as st
import ui
import database as db
import validators as v
from logger import logger
import pandas as pd

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

    ui.section("Units & common areas")
    try:
        props_df = db.get_properties()
    except Exception as exc:
        logger.error("get_properties failed for units section: %s", exc)
        props_df = pd.DataFrame()

    template_df = pd.DataFrame({"property": ["Example Property"], "unit_number": ["A-101"]})
    st.download_button(
        "Download units CSV template",
        data=template_df.to_csv(index=False),
        file_name="units_template.csv",
        mime="text/csv",
    )

    csv_file = st.file_uploader("Import units via CSV", type=["csv"], key="units_csv_upload")
    if csv_file is not None:
        try:
            import_df = pd.read_csv(csv_file)
            import_df.columns = [str(c).strip().lower().replace(" ", "_") for c in import_df.columns]
            if "unit_numbers" in import_df.columns and "unit_number" not in import_df.columns:
                import_df = import_df.rename(columns={"unit_numbers": "unit_number"})
            missing = [c for c in ["property", "unit_number"] if c not in import_df.columns]
            if missing:
                st.error(f"CSV is missing required columns: {', '.join(missing)}")
            else:
                rows = import_df[["property", "unit_number"]].fillna("").to_dict(orient="records")
                result = db.import_units_from_rows(rows)
                st.success(
                    f"Import complete. Created: {result['created']} · Updated: {result['updated']} · "
                    f"Errors: {len(result['errors'])}"
                )
                if result["errors"]:
                    st.warning("\n".join(result["errors"][:20]))
        except Exception as exc:
            logger.error("CSV import failed: %s", exc)
            st.error("Could not process CSV file.")

    if props_df.empty:
        st.info("Add a property first, then manage units.")
        return

    prop_names = props_df["name"].tolist()
    selected_property_name = st.selectbox("Property for unit editing", prop_names, key="units_property_filter")
    selected_property_id = int(props_df.loc[props_df["name"] == selected_property_name, "id"].iloc[0])

    with st.form("add_single_unit"):
        c1, c2 = st.columns([3, 1])
        unit_number = c1.text_input("Add unit number", placeholder="e.g. A-102")
        if c2.form_submit_button("Add unit"):
            if not unit_number.strip():
                st.error("Unit number is required.")
            else:
                try:
                    db.add_unit_location(selected_property_id, unit_number.strip())
                    st.success(f"Unit {unit_number.strip()} added.")
                    st.rerun()
                except Exception as exc:
                    logger.error("add_unit_location failed: %s", exc)
                    st.error("Could not add unit. It may already exist.")

    try:
        common_areas_df = db.get_property_locations(
            property_id=selected_property_id,
            location_type="COMMON_AREA",
            include_inactive=True,
        )
        units_df = db.get_property_locations(
            property_id=selected_property_id,
            location_type="UNIT",
            include_inactive=True,
        )
    except Exception as exc:
        logger.error("get_property_locations failed: %s", exc)
        st.error("Could not load units/common areas.")
        return

    st.markdown("**Prepopulated common areas**")
    if common_areas_df.empty:
        st.info("No common areas found.")
    else:
        show_common = common_areas_df[["location_code", "location_name", "is_active"]].copy()
        show_common.columns = ["Code", "Name", "Active"]
        show_common["Active"] = show_common["Active"].astype(int).eq(1)
        st.dataframe(show_common, width='stretch', hide_index=True)

    st.markdown("**Edit units**")
    if units_df.empty:
        st.info("No units yet. Add one manually or import from CSV.")
    else:
        editor_df = units_df[["id", "location_code", "is_active"]].copy()
        editor_df.columns = ["id", "unit_number", "active"]
        editor_df["active"] = editor_df["active"].astype(int).eq(1)
        edited = st.data_editor(
            editor_df,
            width='stretch',
            hide_index=True,
            disabled=["id"],
            key=f"units_editor_{selected_property_id}",
        )
        if st.button("Save unit changes", key=f"save_units_{selected_property_id}"):
            try:
                for _, row in edited.iterrows():
                    db.update_property_location(
                        int(row["id"]),
                        str(row["unit_number"]),
                        bool(row["active"]),
                    )
                st.success("Unit updates saved.")
                st.rerun()
            except Exception as exc:
                logger.error("update_property_location failed: %s", exc)
                st.error("Could not save one or more unit changes.")
