import streamlit as st
import ui
import database as db
import validators as v
from logger import logger

def render_my_requisitions(username, role, sel_prop_id, sel_room_id, _item_opts):
    ui.page_header("My requisitions", "Request stock items from the storeroom")
    logger.debug("Rendering My Requisitions for %s", username)

    STATUS_COLORS = {
        "Pending":          ("#FAEEDA","#854F0B"),
        "Approved":         ("#EAF3DE","#3B6D11"),
        "Partially Issued": ("#E6F1FB","#0C447C"),
        "Issued":           ("#D6EAF8","#1A5276"),
        "Rejected":         ("#FCEBEB","#A32D2D"),
        "Dispersed":        ("#E6F1FB","#0C447C"),
        "Cancelled":        ("#F1EFE8","#444441"),
    }

    import auth as auth_module
    if role == "staff":
        staff_prop_id = auth_module.current_property_id() if hasattr(auth_module, 'current_property_id') else st.session_state.get('property_id')
        sel_prop_id = staff_prop_id
    item_opts_all = _item_opts(property_id=sel_prop_id, storeroom_id=sel_room_id)

    with st.expander("+ New requisition", expanded=False):
        with st.form("req_header", clear_on_submit=False):
            c1, c2       = st.columns(2)
            req_purpose  = c1.text_input("Purpose / reason *", placeholder="e.g. Monthly cleaning supplies")
            req_urgency  = c2.selectbox("Urgency", ["Normal","Urgent","Critical"])
            if st.form_submit_button("Set details"):
                errs = v.validate_requisition_form(req_purpose, ["placeholder"])
                errs = [e for e in errs if "item" not in e.lower()]
                if errs:
                    ui.show_errors(errs)
                else:
                    st.session_state.req_purpose = req_purpose.strip()
                    st.session_state.req_urgency = req_urgency

        # ── Stocked items basket ─────────────────────────────────
        if item_opts_all:
            st.markdown("**Add stocked items:**")
            with st.form("req_add_item", clear_on_submit=True):
                rc1, rc2, rc3 = st.columns([4, 1, 1])
                sel_req_item  = rc1.selectbox("Item", list(item_opts_all.keys()))
                req_qty       = rc2.number_input("Qty", min_value=0.1, value=1.0, step=1.0)
                if rc3.form_submit_button("Add"):
                    if req_qty <= 0:
                        st.error("Quantity must be greater than zero.")
                    else:
                        st.session_state.req_basket.append({
                            "label":   sel_req_item,
                            "item_id": item_opts_all[sel_req_item],
                            "qty":     req_qty,
                        })
                        st.rerun()
        else:
            st.info("No stocked items available to select — you can still request unlisted items below.")

        # ── Custom / unlisted items basket ───────────────────────
        st.markdown("**Add unlisted items (not yet in stock):**")
        with st.form("req_add_custom", clear_on_submit=True):
            cc1, cc2, cc3, cc4 = st.columns([3, 1, 1, 2])
            custom_name  = cc1.text_input("Item name *")
            custom_qty   = cc2.number_input("Qty", min_value=0.1, value=1.0, step=1.0)
            custom_uom   = cc3.text_input("UOM", value="units")
            custom_notes = cc4.text_input("Notes / specs")
            if st.form_submit_button("Add unlisted item"):
                if not custom_name.strip():
                    st.error("Item name is required.")
                elif custom_qty <= 0:
                    st.error("Quantity must be greater than zero.")
                else:
                    st.session_state.req_custom_basket.append({
                        "name":  custom_name.strip(),
                        "qty":   custom_qty,
                        "uom":   custom_uom.strip() or "units",
                        "notes": custom_notes.strip(),
                    })
                    st.rerun()

        basket        = st.session_state.req_basket
        custom_basket = st.session_state.req_custom_basket

        if basket or custom_basket:
            ui.section("Items in request")
            for i, b in enumerate(basket):
                c1, c2 = st.columns([5, 1])
                c1.markdown(f"• {b['label'].split(' (')[0]} — **{b['qty']}** *(stocked)*")
                if c2.button("✕", key=f"rem_req_{i}"):
                    st.session_state.req_basket.pop(i)
                    st.rerun()
            for i, b in enumerate(custom_basket):
                c1, c2 = st.columns([5, 1])
                c1.markdown(f"• {b['name']} — **{b['qty']} {b['uom']}** *(unlisted — procurement needed)*")
                if c2.button("✕", key=f"rem_cust_{i}"):
                    st.session_state.req_custom_basket.pop(i)
                    st.rerun()

            if st.button("✅ Submit requisition", type="primary"):
                purpose = st.session_state.get("req_purpose","")
                all_items_combined = basket + [{"label": b["name"], "item_id": None, "qty": b["qty"]} for b in custom_basket]
                errs = v.validate_requisition_form(purpose, all_items_combined)
                if errs:
                    ui.show_errors(errs)
                else:
                    try:
                        lines = [(b["item_id"], b["qty"]) for b in basket]
                        ref   = db.create_requisition(
                            requested_by=username,
                            role=role,
                            property_id=sel_prop_id,
                            storeroom_id=sel_room_id,
                            purpose=purpose,
                            urgency=st.session_state.get("req_urgency","Normal"),
                            lines=lines,
                            custom_lines=custom_basket,
                        )
                        logger.info("Requisition %s submitted by %s", ref, username)
                        st.session_state.req_basket = []
                        st.session_state.req_custom_basket = []
                        st.success(f"Requisition {ref} submitted.")
                        st.rerun()
                    except Exception as exc:
                        logger.error("create_requisition failed: %s", exc)
                        st.error("Could not submit requisition.")

        if st.button("🗑 Clear basket", key="clr_req"):
            st.session_state.req_basket = []
            st.session_state.req_custom_basket = []
            st.rerun()

    ui.section("Stock issued to you")
    sf1, sf2, sf3 = st.columns([2, 1, 1])
    issued_status_filter = sf1.selectbox(
        "Usage status",
        ["All", "Pending usage report", "Usage reported"],
        key="issued_to_me_status",
        label_visibility="collapsed",
    )
    issued_date_from = sf2.date_input("From", value=None, key="issued_to_me_date_from")
    issued_date_to = sf3.date_input("To", value=None, key="issued_to_me_date_to")
    issued_search = st.text_input(
        "Search item or requisition",
        key="issued_to_me_search",
        placeholder="e.g. Toilet Rolls or REQ-202603",
    )

    try:
        issued_df = db.get_issued_to_user(
            username=username,
            property_id=sel_prop_id,
            date_from=issued_date_from or None,
            date_to=issued_date_to or None,
        )
    except Exception as exc:
        logger.error("get_issued_to_user failed: %s", exc)
        issued_df = db.pd.DataFrame()
        st.error("Could not load issued stock.")

    if issued_df.empty:
        st.info("No stock has been issued to you yet.")
    else:
        issued_df = issued_df.copy()
        issued_df["Usage status"] = issued_df.apply(
            lambda r: (
                "Usage reported"
                if int(r.get("usage_reported", 0)) == 1
                else ("Pending usage report" if r.get("requisition_id") else "No requisition")
            ),
            axis=1,
        )

        if issued_search.strip():
            q = issued_search.strip().lower()
            issued_df = issued_df[
                issued_df["item_name"].fillna("").str.lower().str.contains(q)
                | issued_df["ref_number"].fillna("").str.lower().str.contains(q)
            ]

        if issued_status_filter != "All":
            issued_df = issued_df[issued_df["Usage status"] == issued_status_filter]

        if issued_df.empty:
            st.info("No issued-stock rows match your filters.")
        else:
            issued_dates = db.pd.to_datetime(issued_df["issued_date"], errors="coerce")
            month_start = db.pd.Timestamp.today().replace(day=1).normalize()
            units_this_month = float(issued_df.loc[issued_dates >= month_start, "qty"].sum())
            pending_reports = int((issued_df["Usage status"] == "Pending usage report").sum())
            last_issued = str(issued_df.iloc[0]["issued_date"])[:10]
            ui.metric_row([
                ("Units issued to you (month)", int(units_this_month), "", "info"),
                ("Pending usage reports", pending_reports, "", "warning" if pending_reports else "ok"),
                ("Last issued date", last_issued, "", "info"),
            ])

            show = issued_df[[
                "issued_date", "item_name", "qty", "uom", "ref_number",
                "issued_by", "property_name", "storeroom_name", "Usage status"
            ]].copy()
            show.columns = [
                "Date", "Item", "Qty", "UOM", "Requisition", "Issued by",
                "Property", "Storeroom", "Usage"
            ]
            st.dataframe(show, width='stretch', hide_index=True)

            pending = issued_df[
                (issued_df["Usage status"] == "Pending usage report")
                & issued_df["requisition_id"].notna()
            ][["requisition_id", "ref_number", "purpose"]].drop_duplicates()

            if not pending.empty:
                st.markdown("**Quick usage reporting**")
                for _, row in pending.iterrows():
                    req_id = int(row["requisition_id"])
                    label = str(row.get("ref_number") or f"REQ {req_id}")
                    purpose = str(row.get("purpose") or "No purpose provided")
                    txt_key = f"quick_usage_text_{req_id}"
                    st.caption(f"{label} · {purpose}")
                    usage_text = st.text_area(
                        "How was this stock used?",
                        key=txt_key,
                        placeholder="Example: Issued 4 bulbs to Unit B12 corridor maintenance.",
                    )
                    if st.button("Submit usage report", key=f"quick_usage_btn_{req_id}"):
                        if usage_text.strip():
                            db.add_usage_report(req_id, username, usage_text.strip())
                            st.success(f"Usage report submitted for {label}.")
                            st.rerun()
                        else:
                            st.warning("Please enter a usage report.")

    ui.section("My requisitions")
    from datetime import date as _date
    mf1, mf2, mf3 = st.columns([2, 1, 1])
    my_status_filter = mf1.selectbox(
        "Status", ["All", "Pending", "Approved", "Partially Issued", "Issued", "Rejected", "Cancelled"],
        key="my_req_status_filter", label_visibility="collapsed",
    )
    my_date_from = mf2.date_input("From", value=None, key="my_req_date_from")
    my_date_to   = mf3.date_input("To",   value=None, key="my_req_date_to")

    try:
        my_reqs = db.get_requisitions(
            requested_by=username,
            property_id=sel_prop_id,
            status=None if my_status_filter == "All" else my_status_filter,
            date_from=my_date_from or None,
            date_to=my_date_to or None,
        )
    except Exception as exc:
        logger.error("get_requisitions failed: %s", exc)
        my_reqs = db.pd.DataFrame()

    # Track last seen statuses in session state
    if 'last_req_statuses' not in st.session_state:
        st.session_state['last_req_statuses'] = {}
    last_statuses = st.session_state['last_req_statuses']
    status_changed = False
    changed_refs = []
    if not my_reqs.empty:
        for _, row in my_reqs.iterrows():
            ref = row['ref_number']
            status = row['status']
            if ref in last_statuses and last_statuses[ref] != status:
                status_changed = True
                changed_refs.append(ref)
            last_statuses[ref] = status
        st.session_state['last_req_statuses'] = last_statuses

    if my_reqs.empty:
        st.info("You have no requisitions yet.")
    else:
        if status_changed:
            st.success(f"Status updated for requisition(s): {', '.join(changed_refs)}")
        counts = my_reqs["status"].value_counts().to_dict()
        cols   = st.columns(max(len(counts), 1))
        for col, (s, cnt) in zip(cols, counts.items()):
            bg, fg = STATUS_COLORS.get(s, ("#F1EFE8","#444441"))
            col.markdown(
                f"<div style='background:{bg};color:{fg};padding:12px 16px;"
                f"border-radius:10px;text-align:center'>"
                f"<div style='font-size:22px;font-weight:700'>{cnt}</div>"
                f"<div style='font-size:11px;font-weight:600'>{s}</div></div>",
                unsafe_allow_html=True,
            )

        st.markdown("")
        for _, row in my_reqs.iterrows():
            highlight = row['ref_number'] in changed_refs
            with st.expander(f"{row['ref_number']}  ·  {row.get('purpose') or '—'}  ·  {str(row['created_at'])[:10]}"):
                c1, c2, c3 = st.columns(3)
                status_html = ui.req_status_pill(row['status'])
                if highlight:
                    status_html = f"<span style='background:#ffe082;color:#222;padding:2px 8px;border-radius:6px;margin-right:6px'>NEW</span> " + status_html
                c1.markdown(f"**Status:** {status_html}", unsafe_allow_html=True)
                c2.markdown(f"**Urgency:** {row['urgency']}")
                c3.markdown(f"**Property:** {row.get('property_name') or '—'}")
                if row.get("review_note"):
                    st.markdown(f"**Review note:** {row['review_note']}")
                if row.get("reviewed_by"):
                    st.markdown(f"**Reviewed by:** {row['reviewed_by']}  |  **Dispersed by:** {row.get('dispersed_by') or '—'}")
                try:
                    lines = db.get_requisition_lines(int(row["id"]))
                    if not lines.empty:
                        ld = lines[["item_name","uom","qty_requested","qty_approved","qty_dispersed","is_custom"]].copy()
                        ld["Type"] = ld["is_custom"].apply(lambda x: "🛒 Procurement" if x else "📦 Stocked")
                        ld = ld.drop(columns=["is_custom"])
                        ld.columns = ["Item","UOM","Requested","Approved","Dispersed","Type"]
                        ld = ld[["Type","Item","UOM","Requested","Approved","Dispersed"]]
                        st.dataframe(ld, width='stretch', hide_index=True)
                except Exception as exc:
                    logger.error("req lines fetch failed: %s", exc)


                # --- Usage reporting (persisted) ---
                st.markdown("**Usage reporting:**")
                usage_reports = db.get_usage_reports(int(row["id"]))
                if not usage_reports.empty:
                    for _, ur in usage_reports.iterrows():
                        st.markdown(f"<div style='background:#f6f6f6;padding:6px 10px;border-radius:6px;margin-bottom:4px;font-size:13px'><b>{ur['username']}</b> <span style='color:#888;font-size:11px'>({ur['created_at'][:16]})</span><br>{ur['report']}</div>", unsafe_allow_html=True)
                usage_key = f"usage_{row['id']}"
                usage_val = st.text_area("How was this stock used?", key=usage_key)
                if st.button("Submit usage report", key=f"submit_usage_{row['id']}"):
                    if usage_val.strip():
                        db.add_usage_report(int(row["id"]), username, usage_val.strip())
                        st.success("Usage report submitted.")
                        st.rerun()
                    else:
                        st.warning("Please enter a usage report.")

                # --- Document upload (persisted) ---
                st.markdown("**Supporting documents:**")
                docs = db.get_requisition_documents(int(row["id"]))
                if not docs.empty:
                    for _, doc in docs.iterrows():
                        st.markdown(f"<div style='font-size:13px;margin-bottom:2px'><b>{doc['username']}</b> <span style='color:#888;font-size:11px'>({doc['created_at'][:16]})</span> — <a href='/download_doc/{doc['id']}' target='_blank'>{doc['filename']}</a></div>", unsafe_allow_html=True)
                doc_file = st.file_uploader("Upload a document or photo", key=f"doc_{row['id']}")
                if doc_file:
                    db.add_requisition_document(
                        int(row["id"]), username, doc_file.name, doc_file.read(), doc_file.type
                    )
                    st.success(f"Uploaded: {doc_file.name}")
                    st.rerun()

                # --- Commenting/communication (persisted) ---
                st.markdown("**Comments / Communication:**")
                comments = db.get_requisition_comments(int(row["id"]))
                if not comments.empty:
                    for _, cm in comments.iterrows():
                        st.markdown(f"<div style='background:#f9f9f9;padding:6px 10px;border-radius:6px;margin-bottom:4px;font-size:13px'><b>{cm['username']}</b> <span style='color:#888;font-size:11px'>({cm['created_at'][:16]})</span><br>{cm['comment']}</div>", unsafe_allow_html=True)
                comment_key = f"comment_{row['id']}"
                comment_val = st.text_area("Add a comment or question", key=comment_key)
                if st.button("Post comment", key=f"post_comment_{row['id']}"):
                    if comment_val.strip():
                        db.add_requisition_comment(int(row["id"]), username, comment_val.strip())
                        st.success("Comment posted.")
                        st.rerun()
                    else:
                        st.warning("Please enter a comment.")

                if row["status"] in ("Pending","Approved"):
                    if st.button("Cancel", key=f"cancel_req_{row['id']}"):
                        try:
                            db.cancel_requisition(int(row["id"]), username)
                            logger.info("Requisition %s cancelled by %s", row["ref_number"], username)
                            st.success("Cancelled.")
                            st.rerun()
                        except Exception as exc:
                            logger.error("cancel_requisition failed: %s", exc)
                            st.error("Could not cancel.")
