"""Dependency-free, offline HTML and Markdown experiment reports."""
import csv
import html
import json
from pathlib import Path


def render(directory):
    directory = Path(directory)
    with (directory / "summary.csv").open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    metadata = json.loads((directory / "metadata.json").read_text(encoding="utf-8"))
    columns = [("method", "Scheduler"), ("reward", "Reward ↑"), ("cost_usd", "USD/day ↓"),
               ("fulfillment", "Energy fulfillment ↑"), ("completion_rate", "Sessions complete ↑"),
               ("solar_fraction", "Solar fraction ↑"), ("peak_grid_kw", "Peak grid kW ↓")]
    def cells(row):
        return [row["method"]] + [f"{float(row[k+'_mean']):.3f} ± {float(row[k+'_sd']):.3f}" for k,_ in columns[1:]]
    headers = [v for _,v in columns]
    caption = ("Synthetic e-bike charging simulation. Mean ± sample SD across seed-level means; "
               "each seed averages all evaluation days and stations. SD is not a confidence interval. "
               "Lower cost may reflect unmet demand: compare fulfillment and reward together.")
    md = "# FedCharge-RL — measured example results\n\n" + caption + "\n\n"
    md += "| " + " | ".join(headers) + " |\n|" + "---|" * len(headers) + "\n"
    md += "\n".join("| " + " | ".join(cells(r)) + " |" for r in rows)
    md += "\n\nConfiguration and environment: [metadata.json](metadata.json). Raw paired outcomes: [evaluation.csv](evaluation.csv).\n"
    (directory / "RESULTS.md").write_text(md, encoding="utf-8")
    head = "".join("<th>"+html.escape(h)+"</th>" for h in headers)
    body = "".join("<tr>"+"".join("<td>"+html.escape(c)+"</td>" for c in cells(r))+"</tr>" for r in rows)
    page = """<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>FedCharge-RL | Experiment report</title><style>
body{font:16px/1.6 system-ui;background:#0c1725;color:#e5edf5;max-width:1250px;margin:60px auto;padding:24px}
h1{font-size:42px;margin-bottom:8px}p{color:#bdcede;max-width:900px}table{border-collapse:collapse;width:100%;font-size:14px}
th,td{padding:14px;text-align:left;border-bottom:1px solid #324354}th{color:#65dcc0}td:first-child{font-weight:700}
.scroll{overflow:auto;background:#122235;border-radius:12px;padding:16px}pre{overflow:auto;padding:20px;background:#122235}
a{color:#65dcc0}</style><p>REPRODUCIBLE RESEARCH PROTOTYPE / v0.1.0</p><h1>FedCharge-RL</h1>
<p>Federated tabular reinforcement learning for solar-assisted e-bike charging.</p>"""
    page += "<p>"+html.escape(caption)+"</p><div class='scroll'><table><thead><tr>"+head+"</tr></thead><tbody>"+body+"</tbody></table></div>"
    page += "<p>All seven methods use identical held-out scenarios. This report describes a simulation, with no hardware validation or formal privacy guarantee.</p>"
    page += "<p><a href='evaluation.csv'>Raw evaluation CSV</a> · <a href='paired_deltas.csv'>Paired deltas</a> · <a href='metadata.json'>Provenance</a></p>"
    page += "<h2>Experiment configuration</h2><pre>"+html.escape(json.dumps(metadata,indent=2))+"</pre></html>"
    (directory / "report.html").write_text(page, encoding="utf-8")
