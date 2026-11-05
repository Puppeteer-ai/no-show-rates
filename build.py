#!/usr/bin/env python3
"""Generates index.html and the CSV from data/no-show-rates.json."""
import csv, html, json, pathlib

ROOT = pathlib.Path(__file__).parent
SITE = "https://puppeteer-ai.github.io/no-show-rates/"
RECUPRA = "https://recupra.com/"
CALCULATOR = "https://recupra.com/resources/no-show-rate-calculator"
FIELDS = ["id", "category", "setting", "rate_pct", "rate_low", "rate_high", "kind", "measure", "sample", "period",
          "location", "source_type", "citation", "year", "doi", "pmid", "url", "checked_against", "checked_on", "note"]
ORDER = ["Across settings", "Medical groups", "Primary care", "Specialty care", "Imaging", "Pediatrics",
         "Behavioral health", "Dental", "Visit type", "Hospital outpatient, outside the US"]
SCALE = 90  # bar axis in percent, wide enough for the largest confidence bound

rows = json.loads((ROOT / "data/no-show-rates.json").read_text())
rows.sort(key=lambda r: (ORDER.index(r["category"]), -r["rate_pct"]))

with (ROOT / "data/no-show-rates.csv").open("w", newline="") as f:
    w = csv.DictWriter(f, FIELDS, lineterminator="\n")
    w.writeheader()
    for r in rows:
        w.writerow({k: r.get(k, "") if r.get(k) is not None else "" for k in FIELDS})

e = html.escape


def fmt(n):
    return f"{n:g}%"


def bar(r):
    left, width = "", ""
    if "rate_low" in r:
        left = f'<i class="ci" style="left:{r["rate_low"] / SCALE * 100:.1f}%;width:{(r["rate_high"] - r["rate_low"]) / SCALE * 100:.1f}%"></i>'
    return f'<div class="bar {r["kind"]}" aria-hidden="true">{left}<b style="left:{r["rate_pct"] / SCALE * 100:.1f}%"></b></div>'


def row(r):
    value = ("&le; " if r["kind"] == "target" else "") + fmt(r["rate_pct"])
    span = f'<small>{fmt(r["rate_low"])} to {fmt(r["rate_high"])}</small>' if "rate_low" in r else ""
    note = f'<small class="note">{e(r["note"])}</small>' if r["note"] else ""
    return f"""<tr data-category="{e(r['category'])}">
<td class="setting"><span class="cat">{e(r['category'])}</span>{e(r['setting'])}<small>{e(r['measure'])}</small>{note}</td>
<td class="rate"><strong>{value}</strong>{span}{bar(r)}</td>
<td class="sample">{e(r['sample'])}<small>{e(r['period'])}. {e(r['location'])}.</small></td>
<td class="source"><a href="{e(r['url'])}">{e(r['citation'])}</a><small>{e(r['source_type'])}. Checked against the {e(r['checked_against'])}.</small></td>
</tr>"""


measured = [r for r in rows if r["kind"] == "measured"]
low, high = min(measured, key=lambda r: r["rate_pct"]), max(measured, key=lambda r: r["rate_pct"])
filters = "".join(f'<button type="button" data-filter="{e(c)}">{e(c)}</button>' for c in ORDER)
ld = {
    "@context": "https://schema.org", "@type": "Dataset", "name": "Published patient no-show rates by clinic setting",
    "description": "Published patient no-show rates by clinic setting, each linked to its source and checked by hand.",
    "url": SITE, "license": "https://creativecommons.org/licenses/by/4.0/", "isAccessibleForFree": True,
    "creator": {"@type": "Organization", "name": "Recupra", "url": RECUPRA}, "dateModified": max(r["checked_on"] for r in rows),
    "keywords": ["patient no-show rate", "missed appointments", "outpatient clinics", "healthcare benchmarks"],
    "distribution": [{"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": SITE + "data/no-show-rates.csv"},
                     {"@type": "DataDownload", "encodingFormat": "application/json", "contentUrl": SITE + "data/no-show-rates.json"}],
}

page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Patient No-Show Rates by Clinic Setting</title>
<meta name="description" content="{len(rows)} published patient no-show figures by clinic setting, each linked to its source. Free to download as CSV or JSON.">
<link rel="canonical" href="{SITE}">
<meta name="color-scheme" content="light">
<script type="application/ld+json">{json.dumps(ld)}</script>
<style>
:root {{ --paper:#faf7f2; --ink:#1a1f2e; --muted:#5b6070; --wine:#712f4a; --rule:#e8e2d3; --tint:#f0ece4; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--paper); color:var(--ink); font:16px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif; }}
main {{ max-width:1120px; margin:0 auto; padding:56px 16px 72px; }}
h1,h2 {{ font-family:Georgia,"Times New Roman",serif; font-weight:400; letter-spacing:-.01em; }}
h1 {{ font-size:clamp(32px,5vw,48px); line-height:1.1; margin:0 0 16px; max-width:18em; }}
h2 {{ font-size:24px; margin:48px 0 8px; }}
p {{ max-width:44em; }}
a {{ color:var(--wine); }}
.lede {{ font-size:18px; }}
.actions a {{ display:inline-block; margin:4px 8px 4px 0; padding:8px 14px; border:1px solid var(--wine); border-radius:4px; text-decoration:none; }}
.filters {{ display:flex; flex-wrap:wrap; gap:6px; margin:32px 0 12px; }}
.filters button {{ font:inherit; font-size:14px; padding:5px 11px; color:var(--ink); background:none; border:1px solid var(--rule); border-radius:4px; cursor:pointer; }}
.filters button[aria-pressed=true] {{ background:var(--wine); border-color:var(--wine); color:#fff; }}
table {{ width:100%; border-collapse:collapse; font-size:15px; }}
th {{ text-align:left; font-size:13px; font-weight:500; color:var(--muted); padding:8px 12px 8px 0; border-bottom:1px solid var(--ink); }}
td {{ vertical-align:top; padding:14px 12px 14px 0; border-bottom:1px solid var(--rule); }}
small {{ display:block; font-size:13px; line-height:1.4; color:var(--muted); margin-top:2px; }}
.note {{ color:var(--ink); }}
.cat {{ display:block; font-size:12px; color:var(--wine); }}
.setting {{ width:32%; }} .rate {{ width:18%; }} .sample {{ width:20%; }} .source {{ font-size:13px; line-height:1.4; }}
.rate strong {{ font:400 24px/1.1 Georgia,serif; font-variant-numeric:tabular-nums; }}
.bar {{ position:relative; height:10px; margin-top:8px; background:var(--tint); border-radius:2px; }}
.bar b {{ position:absolute; top:0; width:3px; height:10px; margin-left:-1px; background:var(--wine); }}
.bar .ci {{ position:absolute; top:3px; height:4px; background:#c9a3b2; }}
.bar.target b {{ background:none; border:1px solid var(--wine); width:5px; }}
ul {{ max-width:44em; padding-left:20px; }} li {{ margin:6px 0; }}
pre {{ max-width:44em; white-space:pre-wrap; font-size:14px; background:var(--tint); padding:12px; border-radius:4px; }}
footer {{ margin-top:48px; padding-top:16px; border-top:1px solid var(--rule); font-size:14px; color:var(--muted); }}
@media (max-width:720px) {{
  main {{ padding-top:32px; }}
  thead {{ display:none; }}
  table,tbody,tr,td {{ display:block; width:100%; }}
  tr {{ padding:14px 0; border-bottom:1px solid var(--rule); }}
  td,.setting,.rate,.sample {{ border:0; padding:4px 0; width:100%; }}
}}
</style>
</head>
<body>
<main>
<h1>Patient no-show rates by clinic setting</h1>
<p class="lede">{len(rows)} published figures, each linked to its source. Measured rates here run from {fmt(low['rate_pct'])} to {fmt(high['rate_pct'])}, which is why a single national average tells a clinic very little.</p>
<p class="actions"><a href="data/no-show-rates.csv">Download CSV</a><a href="data/no-show-rates.json">Download JSON</a></p>

<div class="filters" role="group" aria-label="Filter by category"><button type="button" data-filter="" aria-pressed="true">All</button>{filters}</div>
<table>
<thead><tr><th>Setting and measure</th><th>Rate</th><th>Sample and period</th><th>Source</th></tr></thead>
<tbody>
{chr(10).join(row(r) for r in rows)}
</tbody>
</table>

<h2>How to read these numbers</h2>
<ul>
<li><strong>Do not rank them.</strong> Studies count differently. Some divide by every scheduled visit, others only by completed and missed visits, and late cancellations are sometimes counted separately.</li>
<li><strong>Most are single sites.</strong> A study from one academic or safety-net system describes that system, not its whole specialty.</li>
<li><strong>Population and visit type matter.</strong> One safety-net center reports 25% for in-person visits and 12% for telemedicine, so compare against a similar clinic.</li>
<li><strong>The pandemic is in some periods.</strong> Check the dates before treating a figure as current.</li>
<li><strong>Bars</strong> share a 0% to 90% axis. The lighter band is a range or a confidence interval, where the source gives one. The hollow marker is a target, not a measurement.</li>
</ul>

<h2>What is included</h2>
<p>A figure is listed when the source states the rate directly and says what population it describes. Each was checked against the abstract, full text or publisher page named in its row on {max(r['checked_on'] for r in rows)}. Nothing here is modeled, blended or averaged by us. This is a selection, not a systematic review. Physical therapy, oncology and general dentistry have no measured row yet, because the sources we found were small, or we could not read them.</p>
<p>Found a mistake or a better source? <a href="https://github.com/Puppeteer-ai/no-show-rates/issues">Open an issue</a>.</p>

<h2>Cite or reuse</h2>
<p>The data is free to use under <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>. Please cite the original study for any single figure, and this page for the compilation.</p>
<pre>Recupra. Patient no-show rates by clinic setting [dataset]. {SITE}</pre>

<footer>
<p>Compiled by <a href="{RECUPRA}">Recupra</a>, which sells no-show recovery software to clinics. None of these figures are Recupra's, and no patient data is included. To work out your own clinic's rate and what it costs, use the <a href="{CALCULATOR}">no-show rate calculator</a>.</p>
</footer>
</main>
<script>
var buttons = document.querySelectorAll('.filters button');
buttons.forEach(function (b) {{
  b.addEventListener('click', function () {{
    buttons.forEach(function (o) {{ o.setAttribute('aria-pressed', o === b); }});
    document.querySelectorAll('tbody tr').forEach(function (tr) {{
      tr.hidden = b.dataset.filter !== '' && tr.dataset.category !== b.dataset.filter;
    }});
  }});
}});
</script>
</body>
</html>
"""
(ROOT / "index.html").write_text(page)
(ROOT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{SITE}</loc><lastmod>{ld["dateModified"]}</lastmod></url></urlset>\n')
