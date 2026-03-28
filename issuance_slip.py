"""
Generates a printable HTML issuance slip.
Returns an HTML string that opens in a new tab and auto-triggers the print dialog.
"""

def generate_slip(issuance: dict, company_name: str = "StockTrack") -> str:
    """
    issuance dict keys:
        slip_number, issued_date, recipient, issued_by, note,
        property_name, storeroom_name,
        items: list of {name, qty, uom, unit_cost}
    """
    items = issuance.get("items", [])
    total_value = sum(float(i.get("unit_cost", 0)) * float(i["qty"]) for i in items)
    total_units = sum(float(i["qty"]) for i in items)

    rows = ""
    for idx, item in enumerate(items, 1):
        value = float(item.get("unit_cost", 0)) * float(item["qty"])
        rows += f"""
        <tr>
            <td class="num">{idx}</td>
            <td>{item['name']}</td>
            <td class="num">{item['qty']}</td>
            <td>{item['uom']}</td>
            <td class="num">R {float(item.get('unit_cost', 0)):,.2f}</td>
            <td class="num">R {value:,.2f}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Issuance Slip #{issuance.get('slip_number','—')}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
    color: #1a1a2e;
    padding: 32px 40px;
    max-width: 780px;
    margin: 0 auto;
  }}

  /* Header */
  .header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 28px; }}
  .company-name {{ font-size: 22px; font-weight: 700; color: #1a1a2e; }}
  .company-sub {{ font-size: 12px; color: #888780; margin-top: 2px; }}
  .slip-title {{ text-align: right; }}
  .slip-title h2 {{ font-size: 18px; font-weight: 700; color: #1a1a2e; }}
  .slip-title .slip-num {{ font-size: 13px; color: #888780; margin-top: 2px; }}

  /* Divider */
  .divider {{ border: none; border-top: 1.5px solid #1a1a2e; margin: 0 0 20px; }}
  .divider-light {{ border: none; border-top: 0.5px solid #e0ddd6; margin: 16px 0; }}

  /* Info grid */
  .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px; }}
  .info-block {{ background: #f8f7f4; border-radius: 8px; padding: 12px 16px; }}
  .info-block .label {{ font-size: 10px; text-transform: uppercase; letter-spacing: 0.08em; color: #888780; font-weight: 600; margin-bottom: 6px; }}
  .info-row {{ display: flex; justify-content: space-between; margin-bottom: 4px; }}
  .info-row .key {{ color: #888780; }}
  .info-row .val {{ font-weight: 600; color: #1a1a2e; }}

  /* Table */
  table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
  thead tr {{ background: #1a1a2e; color: #fff; }}
  thead th {{ padding: 10px 12px; text-align: left; font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; font-weight: 600; }}
  thead th.num {{ text-align: right; }}
  tbody tr:nth-child(even) {{ background: #f8f7f4; }}
  tbody tr:hover {{ background: #f0ede6; }}
  tbody td {{ padding: 9px 12px; border-bottom: 0.5px solid #e8e5de; }}
  tbody td.num {{ text-align: right; font-variant-numeric: tabular-nums; }}

  /* Totals */
  .totals {{ display: flex; justify-content: flex-end; margin-bottom: 28px; }}
  .totals-box {{ min-width: 240px; }}
  .totals-row {{ display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 0.5px solid #e8e5de; }}
  .totals-row.total {{ font-weight: 700; font-size: 14px; border-bottom: none; padding-top: 10px; }}
  .totals-row .tkey {{ color: #888780; }}
  .totals-row.total .tkey {{ color: #1a1a2e; }}

  /* Signatures */
  .signatures {{ display: grid; grid-template-columns: 1fr 1fr; gap: 40px; margin-top: 32px; }}
  .sig-block {{ border-top: 1px solid #1a1a2e; padding-top: 8px; }}
  .sig-block .sig-label {{ font-size: 11px; color: #888780; }}
  .sig-block .sig-name {{ font-size: 13px; font-weight: 600; margin-top: 4px; }}

  /* Footer */
  .footer {{ margin-top: 32px; padding-top: 12px; border-top: 0.5px solid #e0ddd6;
             display: flex; justify-content: space-between; font-size: 11px; color: #aaa8a0; }}

  /* Notes box */
  .notes-box {{ background: #fffbf0; border-left: 3px solid #BA7517; border-radius: 0 8px 8px 0;
                padding: 10px 14px; margin-bottom: 24px; }}
  .notes-box .notes-label {{ font-size: 10px; text-transform: uppercase; letter-spacing: 0.08em;
                              color: #BA7517; font-weight: 600; margin-bottom: 4px; }}
  .notes-box .notes-text {{ color: #1a1a2e; }}

  @media print {{
    body {{ padding: 16px 24px; }}
    .no-print {{ display: none; }}
    @page {{ margin: 1cm; }}
  }}
</style>
</head>
<body>

<div class="header">
  <div>
    <div class="company-name">📦 {company_name}</div>
    <div class="company-sub">Property Stock Management</div>
  </div>
  <div class="slip-title">
    <h2>Issuance Slip</h2>
    <div class="slip-num">#{issuance.get('slip_number', '—')}</div>
  </div>
</div>

<hr class="divider">

<div class="info-grid">
  <div class="info-block">
    <div class="label">Issued to</div>
    <div class="info-row"><span class="key">Recipient</span><span class="val">{issuance.get('recipient','—')}</span></div>
    <div class="info-row"><span class="key">Date</span><span class="val">{issuance.get('issued_date','—')}</span></div>
    <div class="info-row"><span class="key">Issued by</span><span class="val">{issuance.get('issued_by','—')}</span></div>
  </div>
  <div class="info-block">
    <div class="label">Location</div>
    <div class="info-row"><span class="key">Property</span><span class="val">{issuance.get('property_name','—')}</span></div>
    <div class="info-row"><span class="key">Storeroom</span><span class="val">{issuance.get('storeroom_name','—')}</span></div>
  </div>
</div>

{"<div class='notes-box'><div class='notes-label'>Note</div><div class='notes-text'>" + issuance.get('note','') + "</div></div>" if issuance.get('note') else ""}

<table>
  <thead>
    <tr>
      <th class="num">#</th>
      <th>Item description</th>
      <th class="num">Qty</th>
      <th>Unit</th>
      <th class="num">Unit cost</th>
      <th class="num">Total</th>
    </tr>
  </thead>
  <tbody>
    {rows}
  </tbody>
</table>

<div class="totals">
  <div class="totals-box">
    <div class="totals-row">
      <span class="tkey">Total units</span>
      <span>{total_units:g}</span>
    </div>
    <div class="totals-row total">
      <span class="tkey">Total value</span>
      <span>R {total_value:,.2f}</span>
    </div>
  </div>
</div>

<div class="signatures">
  <div class="sig-block">
    <div class="sig-label">Issued by</div>
    <div class="sig-name">{issuance.get('issued_by','')}</div>
    <div style="margin-top:32px;border-top:0.5px solid #888;padding-top:4px;font-size:11px;color:#888">Signature &amp; date</div>
  </div>
  <div class="sig-block">
    <div class="sig-label">Received by</div>
    <div class="sig-name">{issuance.get('recipient','')}</div>
    <div style="margin-top:32px;border-top:0.5px solid #888;padding-top:4px;font-size:11px;color:#888">Signature &amp; date</div>
  </div>
</div>

<div class="footer">
  <span>Generated by {company_name} · {issuance.get('issued_date','')}</span>
  <span>Slip #{issuance.get('slip_number','—')}</span>
</div>

<script>
  window.onload = function() {{ window.print(); }}
</script>
</body>
</html>"""

    return html


def slip_download_button(html: str, slip_number: str, st_module):
    """Renders a download button for the slip HTML in Streamlit."""
    st_module.download_button(
        label="🖨 Download & print slip",
        data=html.encode("utf-8"),
        file_name=f"issuance_slip_{slip_number}.html",
        mime="text/html",
        help="Opens as HTML — use Ctrl+P / Cmd+P to print or save as PDF",
    )
