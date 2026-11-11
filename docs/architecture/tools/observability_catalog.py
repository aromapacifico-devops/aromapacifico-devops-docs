"""Catalog of the signals and identifiers of the platform, with its checks and its cost scenario.

Run with no arguments. It prints the tables of docs/architecture/observability.md, ends with OK and exits with 1 on an inconsistency.

What the checks prove. The catalog agrees with the design documents it cites: each cited document exists and still names the signal or the
identifier, each identifier used by a signal is in the contract, no identifier is a metric dimension, nothing personal or secret is a log
field, and the cost scenario is computed from the volumes of the cost document. They check the design as written.
They do not prove that any log group, metric, dashboard or trace exists, and they are not a test of a deployed monitoring.

Status of a signal
  existing  Defined by a merged design document, which the row cites and the check reads.
  derived   Computed from fields that merged documents define, such as a count by center. This document defines the derivation.
  pending   Depends on the design of the flight objects and their transport, which another card owns and has not delivered.
"""
import math
import re
import sys
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent.parent
errors = []

# ---- Identifiers already defined by merged documents. Nothing here is a new contract ----
# name, what it identifies, created by, document, keyword that the document must contain
IDENTIFIERS = [
    ("sack_code", "Sack", "The platform, at registration or issuing", "traceability/sack-identity.md", "Sack code"),
    ("event_id", "Custody event and audit event", "The device at capture, or the function for a platform event", "traceability/custody-chain.md", "event_id"),
    ("trip_id", "Trip of a carrier", "The carrier application", "traceability/custody-chain.md", "trip_id"),
    ("center_id", "Collection center", "The platform, in the path of the center endpoint", "traceability/custody-chain.md", "center_id"),
    ("farm_id", "Farm", "Enrollment of the farm", "iot/farmer-history.md", "farm_id"),
    ("lot_id", "Farm lot, the agricultural lot", "Enrollment of the farm and the node link", "traceability/custody-chain.md", "lot_id"),
    ("drying_lot_id", "Drying lot", "The start function of a drying", "iot/farmer-history.md", "drying_lot_id"),
    ("node_id", "Farm node", "Provisioning of the node", "iot/telemetry-ingestion.md", "node_id"),
    ("reading_id", "Reading that raised an alert", "The ingestion function", "iot/alert-to-drone-confirmation.md", "reading_id"),
    ("case_id", "Case opened from an alert", "The case function", "iot/alert-to-drone-confirmation.md", "case_id"),
    ("correlation_id", "Chain from a reading through its case", "The ingestion function", "iot/alert-to-drone-confirmation.md", "correlation_id"),
    ("mission_id", "Mission of a flight, with its revision", "The platform, when it plans the mission", "network/drone-mission-link.md", "mission_id"),
    ("package_id", "Mission package", "The platform, when it builds the package", "network/drone-mission-link.md", "package_id"),
    ("execution_id", "One execution of a flight", "The ground station", "drones/fumigation-order.md", "execution_id"),
    ("record_id", "Record of a fumigation execution", "The platform, when it stores the record", "drones/fumigation-order.md", "record_id"),
    ("order_id", "Fumigation order, with its revision", "The order function", "drones/fumigation-order.md", "order_id"),
    ("request_id", "A request to an API of the platform", "API Gateway, called the API request ID in the audit design", "security/audit.md", "API request ID"),
    ("trace_id", "A publication that IoT Core logged", "IoT Core, called the trace ID in the audit design", "security/audit.md", "Trace ID"),
]
ID_NAMES = [i[0] for i in IDENTIFIERS]

# The three keys of the criterion, as the merged contracts define them
CRITERION_KEYS = {
    "sack": ["sack_code", "event_id"],
    "lot": ["lot_id", "drying_lot_id"],
    "flight": ["mission_id", "execution_id"],
}
NOT_DEFINED = [
    ("Group of sacks", "A group action creates one event for each sack in one request, and each event has its own `event_id`. The custody chain defines no identifier of the group, so none is used. The events of one request can be read together by the `request_id` of that request in the API log.", "traceability/custody-chain.md", "each one gets its own answer"),
]

# ---- Fields of an operational log entry. Only these may be written ----
LOG_FIELDS = [
    ("timestamp", "UTC time of the entry"),
    ("level", "ERROR, WARN or INFO"),
    ("service", "Function, API or component that writes the entry"),
    ("environment", "dev, test or prod"),
    ("event_name", "What happened, in a fixed vocabulary per service"),
    ("outcome", "applied, repeat, gap, anomaly, rejected or error, the values of the custody design and the failures"),
    ("error_code", "Short code of a failure, with no message text from a person"),
]
FORBIDDEN_FIELDS = ["captured_by", "recorded_by", "location", "cognito_subject", "presigned_url", "token", "password", "secret", "phone", "email", "name_of_person"]

# ---- Signals ----
# id, area, name, kind (service|custom|logquery|event), source, dimensions as (name, series), identifiers, document, keyword, status, note
S = []


def sig(i, area, name, kind, source, dims, ids, doc, keyword, status, note=""):
    S.append(dict(id=i, area=area, name=name, kind=kind, source=source, dims=dims, ids=ids, doc=doc, keyword=keyword, status=status, note=note))


# Ingestion
sig("I-01", "Ingestion", "Nodes silent over 24 hours", "custom", "A daily check of the last `received_at` of each node", [], ["node_id", "farm_id"], "iot/telemetry-ingestion.md", "Nodes silent over 24 hours", "existing")
sig("I-02", "Ingestion", "Depth and age of the ingestion queue", "service", "SQS, depth and age of the oldest message", [], [], "iot/telemetry-ingestion.md", "Depth and age of the queue", "existing")
sig("I-03", "Ingestion", "Messages in a dead letter queue", "service", "SQS, messages visible in each dead letter queue", [], [], "iot/telemetry-ingestion.md", "Messages in the dead letter queue", "existing")
sig("I-04", "Ingestion", "Readings lost at the edge, `dropped_total` grows", "custom", "Field `dropped_total` of the messages", [], ["node_id"], "iot/telemetry-ingestion.md", "dropped_total", "existing")
sig("I-05", "Ingestion", "Clock of a node far from the platform", "custom", "Difference between `measured_at` and `received_at`", [], ["node_id"], "iot/telemetry-ingestion.md", "far from `received_at`", "existing")
sig("I-06", "Ingestion", "Time from reading to push handoff", "custom", "Alert delivery record", [("kind", 2), ("link", 2)], ["reading_id", "correlation_id"], "iot/alert-delivery.md", "`kind` and `link`", "existing")
sig("I-07", "Ingestion", "Alert not delivered", "custom", "Delivery check and status function", [], ["reading_id"], "iot/alert-delivery.md", "metric for an undelivered alert", "existing")
sig("I-08", "Ingestion", "SMS of an urgent alert not delivered", "custom", "Status function", [], ["reading_id"], "iot/alert-delivery.md", "SMS not delivered", "existing")
sig("I-09", "Ingestion", "Ingestion function errors, throttles and duration", "service", "Lambda metrics of the ingestion function", [], [], "iot/telemetry-ingestion.md", "Function fails", "existing")
sig("I-10", "Ingestion", "Throttled requests of the readings table", "service", "DynamoDB metrics of the readings table", [], [], "iot/telemetry-ingestion.md", "DynamoDB throttled", "existing")
sig("I-11", "Ingestion", "Delivery of the archive stream", "service", "Firehose delivery metrics", [], [], "iot/telemetry-ingestion.md", "Firehose fails", "existing")
sig("I-12", "Ingestion", "Publications that IoT Core refuses or throttles", "service", "IoT Core metrics of the broker", [], [], "iot/telemetry-ingestion.md", "IoT Core throttled", "existing")
sig("I-13", "Ingestion", "Silent vereda of the LoRa path", "event", "Connection state of the gateway at the network server", [], [], "network/lora-out-of-coverage.md", "silent vereda", "existing")
sig("I-14", "Ingestion", "Readings lost on the LoRa path, counted from the gaps in the stored sequences", "logquery", "Stored sequences of each node", [], ["node_id"], "network/lora-out-of-coverage.md", "gap in the stored sequences", "existing")
sig("I-15", "Ingestion", "Readings with no range to judge them", "custom", "Outcome `no_range` of the ranges lookup", [], ["node_id"], "iot/configurable-thresholds.md", "gap metric", "existing")
# Applications
sig("A-01", "Applications", "Requests, errors and latency of the center and carrier APIs", "service", "API Gateway metrics of the private REST API and the HTTP API", [], ["request_id"], "traceability/custody-chain.md", "POST /centers/{center_id}/events", "existing")
sig("A-02", "Applications", "Errors, throttles and duration of every function", "service", "Lambda metrics of each function", [], [], "architecture/recovery.md", "throttled requests", "existing")
sig("A-03", "Applications", "Lookup volume and ceiling of the public query", "service", "Lambda invocations and throttles of the lookup function", [], [], "traceability/public-query.md", "Ceiling reached", "existing")
sig("A-04", "Applications", "Gaps and anomalies on the review list of the centers", "custom", "Outcome of each custody event after the last replay", [("kind", 2)], ["sack_code", "event_id", "center_id"], "traceability/sack-states.md", "review list", "existing")
sig("A-05", "Applications", "Repeated events answered as stored", "logquery", "Outcome `repeat` in the custody write log", [], ["event_id", "request_id"], "traceability/custody-chain.md", "idempotency", "derived", "A repeat is normal after a lost answer. The query shows its rate and not a failure.")
sig("A-06", "Applications", "A function that could not write its audit event", "logquery", "Errors in the audit write of each function, in the operational log", [], ["event_id", "request_id"], "security/audit.md", "before it answers", "derived")
sig("A-07", "Applications", "Events an EventBridge rule could not deliver to the work queue of an inference function", "service", "EventBridge `FailedInvocations` of each rule and messages visible in its rule dead letter queue", [], [], "architecture/failure-policy.md", "FailedInvocations", "existing")
sig("A-08", "Applications", "Failed inference invocations that left the case or order unchanged", "logquery", "Entries `inference.failed` with outcome `error` in the operational log of each inference function", [], ["case_id", "order_id", "mission_id", "execution_id"], "architecture/failure-policy.md", "inference.failed", "existing")
# Database
sig("D-01", "Database", "Failed writes to the sack tables", "service", "DynamoDB error metrics of the sack tables", [], [], "architecture/recovery.md", "failed writes to the sack tables", "existing")
sig("D-02", "Database", "Throttled requests of the tables", "service", "DynamoDB throttle metrics", [], [], "architecture/recovery.md", "throttled requests", "existing")
sig("D-03", "Database", "State of the encryption key", "event", "Key state change events", [], [], "architecture/recovery.md", "state of the encryption key", "existing")
sig("D-04", "Database", "A table with point-in-time recovery turned off", "event", "Configuration change events of the tables", [], [], "architecture/recovery.md", "point-in-time recovery turned off", "existing")
sig("D-05", "Database", "Runs of the deletion job that fail or reach their limit", "custom", "Record of each run of the job", [("outcome", 2)], [], "architecture/persistence-and-archive.md", "alarm warns after two failed runs", "existing")
sig("D-06", "Database", "Size and number of objects of the archive", "service", "S3 storage metrics of the archive bucket", [], [], "architecture/persistence-and-archive.md", "storage metrics", "existing", "The age of the oldest object is named in the cited document, and no source for that value is designed.")
# Three WAN links
sig("W-01", "WAN links", "State of each VPN tunnel", "service", "AWS VPN `TunnelState`, for each connection and tunnel address", [], [], "network/center-cloud-link.md", "TunnelState", "existing")
sig("W-02", "WAN links", "Bytes in and out of each tunnel", "service", "AWS VPN `TunnelDataIn` and `TunnelDataOut`", [], [], "network/center-cloud-link.md", "not a health signal", "existing", "They can report traffic while a tunnel is down, so they say how much and not whether it is healthy.")
sig("W-03", "WAN links", "Custody events received from each center", "logquery", "Count by `center_id` of the events that the center endpoint stores", [], ["center_id", "event_id"], "network/center-cloud-link.md", "center reports no events", "derived")
sig("W-04", "WAN links", "Delay between capture and receipt of the events of a center", "logquery", "`received_at` minus `captured_at` of each custody event, by `center_id`", [], ["center_id", "event_id"], "network/collection-center-operations.md", "queues events", "derived", "A long delay that then falls means the local queue absorbed an outage.")
# Arrival of flight objects
sig("F-01", "Flight objects", "Upload permission granted for a flight object", "event", "Audit event `flight_object.authorized` of the upload function", [], ["execution_id", "mission_id", "request_id"], "security/audit.md", "flight_object.authorized", "existing")
sig("F-02", "Flight objects", "A presigned URL that expired during an upload", "logquery", "Authorization errors of S3 on the upload, in the upload function and the station reports", [], ["execution_id"], "network/drone-mission-link.md", "Presigned URL expires", "existing", "Whether S3 request metrics are enabled depends on the bucket design.")
sig("F-03", "Flight objects", "An object whose hash does not match its manifest", "logquery", "Verification of the object against the manifest", [], ["execution_id", "package_id"], "network/drone-mission-link.md", "manifest", "existing")
sig("F-04", "Flight objects", "Flights not published because an object or the closed log is missing", "custom", "Orders in `EXECUTED_PENDING_SYNC` and flights below their completion rule", [], ["execution_id", "order_id"], "drones/fumigation-order.md", "EXECUTED_PENDING_SYNC", "existing")
sig("F-05", "Flight objects", "Transitions of a fumigation order, allowed and denied", "event", "Audit event `fumigation.transition`", [], ["order_id", "case_id", "execution_id", "record_id", "request_id"], "security/audit.md", "fumigation.transition", "existing")
sig("F-06", "Flight objects", "Arrival of flight objects, their storage events, quarantine and repeated deliveries", "logquery", "Platform events `flight.object.verified`, `flight.object.rejected`, `flight.record.published` and `flight.record.review_required`, and the EventBridge rule of the flight prefixes", [], ["execution_id", "mission_id", "package_id"], "drones/flight-objects.md", "flight.record.published", "derived", "A rejected object carries its quarantine key, and a repeated upload is a normal answer to a lost response.")

STATUS = {"existing", "derived", "pending"}
KINDS = {"service", "custom", "logquery", "event"}

# ---- Operational logs and their retention ----
OPERATIONAL_RETENTION_DAYS = 30  # assumption approved by isahrnd for the exercise
AUDIT_RETENTION = "90 days in CloudWatch and five years in S3, from the personal data design"

# ---- Prices, AWS Price List API read 2026-11-11, us-east-1 ----
PRICE = {"log_ingest_gb": 0.50, "log_store_gb_month": 0.03, "log_scan_gb": 0.005, "custom_metric_first_10000": 0.30, "dashboard": 3.00, "alarm": 0.10,
         "xray_stored_per_million": 5.00, "xray_read_per_million": 0.50}
FREE = {"log_gb": 5.0, "custom_metrics": 10, "dashboards": 3, "alarms": 10}  # stated on the CloudWatch pricing page, read 2026-11-11
BUDGET = 2.20  # reference of the cost document, not a guaranteed cost
BYTES_PER_INVOCATION = 700  # assumption, one structured line and the platform lines
BYTES_PER_API_REQUEST = 300  # assumption, one access log line
SCANNED_GB_PER_MONTH = 2.0  # assumption, queries of an operator
DASHBOARDS = 2  # assumption, platform operations and centers
GB = 2 ** 30

# ---- Minimal alternative: the custom metrics kept, with the series each keeps ----
# Signals not listed here are read by a log query. A kept signal may lose its dimensions.
MINIMAL_METRICS = {
    "I-01": (1, "nodes silent over 24 hours"),
    "I-06": (1, "time from reading to handoff, with no split by kind and link"),
    "I-07": (1, "alert not delivered"),
    "I-08": (1, "SMS of an urgent alert not delivered"),
    "A-04": (1, "gaps and anomalies together, with no split by kind"),
    "D-05": (1, "failed or limited runs only"),
}
MINIMAL_DASHBOARDS = 0  # the console views of the services and saved queries replace the dashboards


def read(rel):
    p = DOCS / rel
    return p.read_text(encoding="utf-8") if p.exists() else None


def check(cond, msg):
    if not cond:
        errors.append(msg)


def volumes():
    text = read("governance/cloud-cost.md")
    check(text is not None, "cloud-cost.md is missing")

    def row(label):
        m = re.search(r"\| " + re.escape(label) + r" \| ([\d,]+) \| ([\d,]+) \|", text)
        check(m is not None, f"volume row {label} not found in the cost document")
        return (int(m.group(1).replace(",", "")), int(m.group(2).replace(",", ""))) if m else (0, 0)

    return {"readings": row("Farm readings"), "positions": row("Carrier positions"), "sack_events": row("Sack events"), "lookups": row("Public sack queries"), "images": row("Drone images")}


def run_checks():
    ids_seen = set()
    for name, what, who, doc, kw in IDENTIFIERS:
        check(name not in ids_seen, f"identifier {name} is listed twice")
        ids_seen.add(name)
        t = read(doc)
        check(t is not None, f"identifier {name}: document {doc} does not exist")
        if t is not None:
            check(kw in t, f"identifier {name}: {doc} no longer contains '{kw}'")
    for key, members in CRITERION_KEYS.items():
        check(all(m in ID_NAMES for m in members), f"the key '{key}' uses an identifier that is not in the contract")
    check(len({CRITERION_KEYS['lot'][0], CRITERION_KEYS['lot'][1]}) == 2, "the farm lot and the drying lot must be two identifiers")
    for what, why, doc, kw in NOT_DEFINED:
        t = read(doc)
        check(t is not None and kw in t, f"'{what}' is not defined: {doc} no longer contains '{kw}'")
    check(not set(f[0] for f in LOG_FIELDS) & set(FORBIDDEN_FIELDS), "a forbidden field is a log field")
    check(not (set(ID_NAMES) & set(FORBIDDEN_FIELDS)), "an identifier is a forbidden field")
    sids = set()
    for s in S:
        check(s["id"] not in sids, f"signal {s['id']} is listed twice")
        sids.add(s["id"])
        check(s["status"] in STATUS and s["kind"] in KINDS, f"{s['id']} has an unknown status or kind")
        for f in ("area", "name", "kind", "source"):
            check(bool(s[f]), f"{s['id']} has no {f}")
        for i in s["ids"]:
            check(i in ID_NAMES, f"{s['id']} uses the identifier {i}, which is not in the contract")
        for d, n in s["dims"]:
            check(d not in ID_NAMES, f"{s['id']} uses the identifier {d} as a metric dimension, which creates one metric for each value")
            check(n <= 6, f"{s['id']} has a dimension with {n} values, which is not low cardinality")
        if s["status"] == "pending":
            check(s["doc"] == "" and "design of the flight objects" in s["note"], f"{s['id']} is pending and must say what it waits on")
        else:
            t = read(s["doc"]) if s["doc"] else None
            check(t is not None, f"{s['id']}: document {s['doc']!r} does not exist")
            if t is not None:
                check(s["keyword"] in t, f"{s['id']}: {s['doc']} no longer contains '{s['keyword']}'")
        if s["kind"] == "custom":
            check(len(s["dims"]) <= 2, f"{s['id']} has more than two dimensions")
    custom_ids = {s["id"]: s for s in S if s["kind"] == "custom"}
    for i, (n, _) in MINIMAL_METRICS.items():
        check(i in custom_ids, f"the minimal alternative keeps {i}, which is not a custom signal")
        if i in custom_ids:
            full = 1
            for _, c in custom_ids[i]["dims"]:
                full *= c
            check(1 <= n <= full, f"the minimal alternative gives {i} {n} series and the full design has {full}")
    check({s["area"] for s in S} >= {"Ingestion", "Applications", "Database", "WAN links", "Flight objects"}, "an area of the criterion has no signal")
    wan = [s for s in S if s["area"] == "WAN links"]
    check(any("TunnelState" in s["source"] for s in wan), "the WAN links have no TunnelState signal")
    check(any("center_id" in s["ids"] for s in wan), "the WAN links have no signal by center")


def custom_series():
    total = 0
    for s in S:
        if s["kind"] == "custom":
            n = 1
            for _, c in s["dims"]:
                n *= c
            total += n
    return total


def cost_rows(vol):
    inv_names = ["readings", "positions", "sack_events", "lookups", "images"]
    api_names = ["positions", "sack_events"]
    out = []
    for m, label in ((0, "Normal month"), (1, "Harvest month")):
        inv = sum(vol[k][m] for k in inv_names)
        req = sum(vol[k][m] for k in api_names)
        gb = (inv * BYTES_PER_INVOCATION + req * BYTES_PER_API_REQUEST) / GB
        out.append((label, inv, req, gb))
    return out


def main():
    run_checks()
    vol = volumes()
    series = custom_series()

    print("## Identifiers of the contract")
    print("| Identifier | What it identifies | Created by | Defined in |")
    print("|---|---|---|---|")
    for name, what, who, doc, kw in IDENTIFIERS:
        print(f"| `{name}` | {what} | {who} | [{doc.split('/')[-1][:-3].replace('-', ' ').capitalize()}](../{doc}) |")

    print("\n## Keys of the criterion")
    print("| Key | Identifiers | Note |")
    print("|---|---|---|")
    print("| Sack | `sack_code` and, for each event, `event_id` | An event is the unit that travels and is repeated |")
    print("| Lot | `lot_id` for the farm lot and `drying_lot_id` for the drying lot | They are two identifiers with two meanings, and neither stands for the other |")
    print("| Flight | `mission_id` for the mission and `execution_id` for one execution, with `package_id` and `record_id` where they exist | A repeated flight gets a new `execution_id` and links to the original |")
    print("")
    for what, why, doc, kw in NOT_DEFINED:
        print(f"Not defined. {what}. {why}")

    print("\n## Log fields")
    print("| Field | Meaning |")
    print("|---|---|")
    for f, d in LOG_FIELDS:
        print(f"| `{f}` | {d} |")
    print("")
    print("An entry also carries the identifiers of the contract that apply to what it records, with the names above. It never carries " + ", ".join(f"`{f}`" for f in FORBIDDEN_FIELDS[:6]) + " or a presigned URL, a token or a secret.")

    for area in ("Ingestion", "Applications", "Database", "WAN links", "Flight objects"):
        print(f"\n## Signals, {area}")
        print("| Id | Signal | Kind | Source | Identifiers | Status | Defined in |")
        print("|---|---|---|---|---|---|---|")
        for s in S:
            if s["area"] != area:
                continue
            ids = ", ".join(f"`{i}`" for i in s["ids"]) or "none"
            doc = f"[{s['doc'].split('/')[-1][:-3].replace('-', ' ').capitalize()}](../{s['doc']})" if s["doc"] else "Not yet designed"
            note = f" {s['note']}" if s["note"] else ""
            dims = (" Dimensions " + ", ".join(f"{d} ({n} values)" for d, n in s["dims"]) + ".") if s["dims"] else ""
            print(f"| {s['id']} | {s['name']}.{dims}{note} | {s['kind']} | {s['source']} | {ids} | {s['status']} | {doc} |")

    kinds = {k: sum(1 for s in S if s["kind"] == k) for k in KINDS}
    print("\n## Counts")
    print("| Item | Count |")
    print("|---|---|")
    print(f"| Signals | {len(S)} |")
    for k in ("service", "custom", "logquery", "event"):
        print(f"| of kind {k} | {kinds[k]} |")
    print(f"| Custom metric series, the product of the dimension values of each custom signal | {series} |")

    print("\n## Cost scenario of the operational telemetry")
    print(f"Reference budget USD {BUDGET:.2f} a month, from the cost document, as a reference and not as a guaranteed cost. Prices are the AWS Price List API for us-east-1, publication of 2026-11-04 for CloudWatch and 2026-11-08 for X-Ray. The free tier is the one the CloudWatch pricing page states on 2026-11-11, and the cost document does not assume it.")
    print("")
    print("| Input | Value | Origin |")
    print("|---|---|---|")
    print(f"| Log ingestion, standard class | USD {PRICE['log_ingest_gb']:.2f} per GB | Price List API |")
    print(f"| Log storage | USD {PRICE['log_store_gb_month']} per GB a month | Price List API |")
    print(f"| Logs Insights scan | USD {PRICE['log_scan_gb']} per GB scanned | Price List API |")
    print(f"| Custom metric | USD {PRICE['custom_metric_first_10000']:.2f} a month each, first 10,000 | Price List API |")
    print(f"| Dashboard | USD {PRICE['dashboard']:.2f} a month each | Price List API |")
    print(f"| Alarm | USD {PRICE['alarm']:.2f} a month each | Price List API |")
    print(f"| Free tier | {FREE['log_gb']:g} GB of logs, {FREE['custom_metrics']} custom metrics, {FREE['dashboards']} dashboards, {FREE['alarms']} alarms | CloudWatch pricing page |")
    print(f"| Bytes written for each function invocation | {BYTES_PER_INVOCATION} | Assumption |")
    print(f"| Bytes written for each API request | {BYTES_PER_API_REQUEST} | Assumption |")
    print(f"| Gigabytes scanned by queries a month | {SCANNED_GB_PER_MONTH:g} | Assumption |")
    print(f"| Dashboards | {DASHBOARDS} | Assumption |")
    print(f"| Retention of operational logs | {OPERATIONAL_RETENTION_DAYS} days | Assumption approved by isahrnd for the exercise |")
    print(f"| Custom metric series of the catalog | {series} | The catalog above |")
    print("")
    print("| Month | Function invocations | API requests | Logs ingested, GB | Ingestion | Storage | Queries | Metrics | Dashboards | Total at list price | Total with the free tier | Alarms that fit the rest of the budget, with the free tier |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for label, inv, req, gb in cost_rows(vol):
        ing = gb * PRICE["log_ingest_gb"]
        sto = gb * PRICE["log_store_gb_month"] * (OPERATIONAL_RETENTION_DAYS / 30)
        qry = SCANNED_GB_PER_MONTH * PRICE["log_scan_gb"]
        met = series * PRICE["custom_metric_first_10000"]
        dash = DASHBOARDS * PRICE["dashboard"]
        total = ing + sto + qry + met + dash
        free_total = max(0.0, gb - FREE["log_gb"]) * (PRICE["log_ingest_gb"] + PRICE["log_store_gb_month"]) + max(0, series - FREE["custom_metrics"]) * PRICE["custom_metric_first_10000"] + max(0, DASHBOARDS - FREE["dashboards"]) * PRICE["dashboard"]
        fits = FREE["alarms"] + max(0, math.floor(round((BUDGET - free_total) / PRICE["alarm"], 6)))
        print(f"| {label} | {inv:,} | {req:,} | {gb:.2f} | {ing:.2f} | {sto:.2f} | {qry:.3f} | {met:.2f} | {dash:.2f} | {total:.2f} | {free_total:.2f} | {fits} |")
    gap = max(0.0, (series * PRICE["custom_metric_first_10000"] + DASHBOARDS * PRICE["dashboard"]) - BUDGET)
    print("")
    print(f"At list price the custom metrics and the dashboards alone cost USD {series * PRICE['custom_metric_first_10000'] + DASHBOARDS * PRICE['dashboard']:.2f}, which is USD {gap:.2f} above the whole reference budget, before any alarm. The logs are small by comparison. With the free tier that the pricing page states, the total falls to the figures of the last but one column. The cost document assumes no free tier, so this is a gap to record and not a change to that document.")
    print("")
    print("| Way to reduce the gap | Effect |")
    print("|---|---|")
    keep = sum(1 for s in S if s["kind"] == "custom")
    print(f"| Keep as custom metrics only the signals that an alarm needs, and read the others by a query | A query costs USD {PRICE['log_scan_gb']} per GB scanned, so a signal read by a query adds almost nothing, and each custom series it replaces saves USD {PRICE['custom_metric_first_10000']:.2f} a month |")
    print(f"| Use one dashboard of up to 50 metrics instead of {DASHBOARDS} | Saves USD {(DASHBOARDS - 1) * PRICE['dashboard']:.2f} at list price, and none within the free tier |")
    print(f"| Take the free tier into account in the cost document | Brings the series, the dashboards and the logs inside the reference budget, and its owner decides |")
    print(f"There are {keep} custom signals and {series} series in this catalog. Which of them an alarm needs is decided by the alarm design, and this document does not choose.")

    print("")
    print("## Chosen operational telemetry")
    kept = sum(n for n, _ in MINIMAL_METRICS.values())
    print("The design adopts the minimal alternative, with X-Ray active tracing at 5 percent on functions and APIs.")
    print("")
    print("| Month | Logs ingested, GB | Logs and queries | Metrics | Dashboards | X-Ray at 5 percent | Total at list price before alarms | Each alarm adds |")
    print("|---|---|---|---|---|---|---|---|")
    for label, inv, req, gb in cost_rows(vol):
        logs = gb * PRICE["log_ingest_gb"] + gb * PRICE["log_store_gb_month"] * (OPERATIONAL_RETENTION_DAYS / 30)
        qry = SCANNED_GB_PER_MONTH * PRICE["log_scan_gb"]
        met = kept * PRICE["custom_metric_first_10000"]
        dash = MINIMAL_DASHBOARDS * PRICE["dashboard"]
        traces = inv * 0.05 * PRICE["xray_stored_per_million"] / 1e6
        print(f"| {label} | {gb:.2f} | {logs + qry:.2f} | {met:.2f} | {dash:.2f} | {traces:.2f} | {logs + qry + met + dash + traces:.2f} | USD {PRICE['alarm']:.2f} |")
    print("")
    print("| Signal | Chosen treatment |")
    print("|---|---|")
    for s in S:
        if s["kind"] == "custom":
            if s["id"] in MINIMAL_METRICS:
                print(f"| {s['id']} | Kept as {MINIMAL_METRICS[s['id']][0]} metric, {MINIMAL_METRICS[s['id']][1]} |")
            else:
                print(f"| {s['id']} | Read by a log query |")
    print(f"MINIMAL_SERIES={kept}")

    print("\n### X-Ray active tracing")
    print("Functions and APIs run active tracing at 5 percent sampling. A trace follows a request through the services that report to X-Ray. A reading published by a node reaches IoT Core with no trace, and IoT Core records its own trace ID in the audit design. A custody event travels from a device that carries none. A trace is kept 30 days.")
    print("")
    print("| Month | Function and API operations | Traced at 5 percent | Traces stored, USD |")
    print("|---|---|---|---|")
    for label, inv, req, gb in cost_rows(vol):
        traced = inv * 0.05
        cost = traced * PRICE["xray_stored_per_million"] / 1e6
        print(f"| {label} | {inv:,} | {traced:,.0f} | {cost:.2f} |")
    print("")
    print(f"At USD {PRICE['xray_stored_per_million']:.2f} per million traces stored, X-Ray adds USD 0.12 in a normal month and USD 0.28 in a harvest month. Reading and scanning cost USD {PRICE['xray_read_per_million']:.2f} per million. The free tier of X-Ray was not read and is not assumed.")

    print("\n## Reading the signals of a center")
    print("A quiet center is not always a broken one. The table reads the tunnel and the events together, with no heartbeat added to any application.")
    print("")
    print("| `TunnelState` of the center | Events from the center | What it means | What to read next |")
    print("|---|---|---|---|")
    print("| 1, both tunnels up | Arriving as usual for that center | Healthy | Nothing |")
    print("| 1 | None for longer than that center usually goes quiet | Normal inactivity or a fault on the center side or in the application. The tunnel is not the cause | Hours and days of operation of the center, which the Federation has not stated, then the errors of the center API and the delay of its next events |")
    print("| Below 1, one tunnel down | Arriving | One tunnel is out, for maintenance or an AWS endpoint failure, and the other carries the traffic | The tunnel address that fell and how long |")
    print("| 0, both down | None | The link, the WAN of the center or its firewall is out. The cloud cannot tell which, and the center keeps receiving sacks and queues the events | The delay between capture and receipt when the link returns |")
    print("| 0 | Arriving | The tunnel metric lags or the data counters mislead. Trust the events | The tunnel metric again after a few minutes |")
    print("| 1 | Arriving with a long and falling delay | An outage that the local queue absorbed has just ended | Nothing, the queue is draining |")
    print("")
    print("What the cloud cannot see. A provider link that fails while the firewall still holds a tunnel is seen only as a down tunnel. A center that is open and has no sacks looks like a center that is closed. The usual silence of each center is learned from its own history and is a threshold for the alarm design.")

    print("OK" if not errors else "")
    for e in errors:
        print("FAIL", e)
    if errors:
        print(f"{len(errors)} problems")
        sys.exit(1)


main()
