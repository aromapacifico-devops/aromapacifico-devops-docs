"""Checks the operations and cost dashboards against the signal catalog, the alarm register and the tag policy.

It fails when a widget cites an unknown signal, reads a custom metric that the chosen telemetry does not keep, holds a log
query or more than one tag query, queries a namespace without tag support, uses a cost center outside the tag policy,
names the environment outside the variable slots, or when the alarm widget, the widget table or the cost table of the
document no longer match the body, the register and the prices.
It checks the design as written. It proves nothing about dashboards, reports or settings in an account.

    python3 -I docs/architecture/tools/dashboards_catalog.py
"""
import json
import re
import sys
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent.parent
errors = []


def check(cond, msg):
    if not cond:
        errors.append(msg)


def read(rel):
    return (DOCS / rel).read_text(encoding="utf-8")


DOC = read("architecture/dashboards.md")
OBS = read("architecture/observability.md")
BODY = json.loads(read("architecture/examples/operational-dashboard.json"))
POLICY = json.loads(read("governance/policies/tag-policy.json"))

KEPT = {"I-01", "I-06", "I-07", "I-08", "A-04", "D-05"}
CUSTOM_NAMESPACE = "<custom namespace>"
# resource types listed as supported by resource tags for telemetry, by metric namespace
TAG_NAMESPACES = {"AWS/Lambda", "AWS/SQS", "AWS/DynamoDB", "AWS/Events", "AWS/VPN", "AWS/Firehose"}
ENV_SLOT = "tag.Environment = 'prod'"
PRICE_DASHBOARD = 3.00
PRICE_ALARM = 0.10
REFERENCE = 2.20


def register():
    """Loads the alarm register without running its report."""
    path = DOCS / "architecture/tools/alarms_catalog.py"
    src = path.read_text(encoding="utf-8").rsplit("\nmain()", 1)[0]
    ns = {"__file__": str(path), "__name__": "alarms_catalog"}
    exec(compile(src, str(path), "exec"), ns)
    billed = {a["id"] for a in ns["ALARMS"] if a["kind"] == "alarm" and a["count"] > 0}
    return billed, ns["telemetry"]()


def doc_table(heading):
    part = DOC.split(heading, 1)[1].split("\n## ", 1)[0]
    rows = [r for r in part.splitlines() if r.startswith("| ") and not r.startswith("| Row") and not r.startswith("|---")]
    return [[c.strip() for c in r.strip("|").split("|")] for r in rows]


def ids(text):
    out = set()
    for a, b in re.findall(r"AL-(\d\d)(?: to AL-(\d\d))?", text):
        out.update(f"AL-{i:02d}" for i in range(int(a), int(b or a) + 1))
    return out


def run_checks():
    catalog = set(re.findall(r"^\| ([IADWF]-\d\d) \|", OBS, re.M))
    centers = set(POLICY["tags"]["CostCenter"]["tag_value"]["@@assign"])
    billed, tel = register()
    widgets = BODY["widgets"]

    check(not any(w["type"] == "log" for w in widgets), "a log widget bills a query on every load")
    metric = [w for w in widgets if w["type"] == "metric"]
    for w in metric:
        p = w["properties"]
        signal = p["title"].split(" ", 1)[0]
        check(signal in catalog, f"{p['title']}: signal {signal} is not in the catalog")
        exprs = [m[0]["expression"] for m in p["metrics"] if isinstance(m[0], dict)]
        check(len(exprs) <= 1, f"{p['title']}: more than one Metrics Insights query")
        for e in exprs:
            ns = re.search(r'SCHEMA\("([^"]+)"', e).group(1)
            check(ns in TAG_NAMESPACES, f"{p['title']}: {ns} has no tag support")
            check(ENV_SLOT in e, f"{p['title']}: the query does not filter by the environment variable")
            for v in re.findall(r"tag\.CostCenter = '([^']+)'", e):
                check(v in centers, f"{p['title']}: cost center {v} is not allowed")
        if p["metrics"][0][0] == CUSTOM_NAMESPACE:
            check(signal in KEPT, f"{p['title']}: {signal} is not one of the six kept custom metrics")

    text = json.dumps(widgets)
    check(text.count("prod") == text.count(ENV_SLOT), "the environment appears outside the variable slots")
    var = BODY["variables"][0]
    check(var["type"] == "pattern" and var["pattern"] == "prod", "the environment variable is not the pattern of the slots")

    alarm = [w for w in widgets if w["type"] == "alarm"]
    check(len(alarm) == 1, "the dashboard needs one alarm widget")
    shown = {re.search(r"AL-\d\d", a).group(0) for a in alarm[0]["properties"]["alarms"]}
    check(len(alarm[0]["properties"]["alarms"]) <= 100, "an alarm widget holds at most 100 alarms")
    check(shown == billed, f"alarm widget differs from the billed alarms, missing {sorted(billed - shown)}, extra {sorted(shown - billed)}")

    table = doc_table("## 4. Operational dashboard")
    rows = [(r[2], r[1]) for r in table if r[2] != "none"]
    body_rows = [tuple(w["properties"]["title"].split(" ", 1)) for w in metric]
    check(rows == body_rows, f"the widget table and the body differ\n  doc  {rows}\n  body {body_rows}")
    for r in table:
        extra = ids(r[4]) - billed
        check(not extra, f"{r[1]}: explains alarms that are not billed {sorted(extra)}")
    check("Alarm status of the 28 billed" in DOC and len(billed) == 28, "the count of billed alarms in the document is stale")

    return billed, tel


def main():
    billed, tel = run_checks()
    alarms = len(billed) * PRICE_ALARM
    cost = doc_table("## 8. Cost")
    print("| Month | Telemetry | Alarms | Dashboard | Total | Above the reference |\n|---|---|---|---|---|---|")
    for month in ("Normal month", "Harvest month"):
        t = tel[month]
        total = t + alarms + PRICE_DASHBOARD
        line = f"| {month} | {t:.2f} | {alarms:.2f} | {PRICE_DASHBOARD:.2f} | {total:.2f} | {total - REFERENCE:.2f} |"
        print(line)
        row = next((r for r in cost if r[0] == month), None)
        expected = [month, f"{t:.2f}", f"{alarms:.2f}", f"{PRICE_DASHBOARD:.2f}", f"{total:.2f}", f"{REFERENCE:.2f}", f"{total - REFERENCE:.2f}"]
        check(row == expected, f"cost table of the document differs for {month}, expected {expected}")
    print(f"\nWidgets {len(BODY['widgets'])}, metric widgets {sum(w['type'] == 'metric' for w in BODY['widgets'])}, billed alarms on the page {len(billed)}.")
    for e in errors:
        print("FAIL", e)
    print("OK" if not errors else f"{len(errors)} problems")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
