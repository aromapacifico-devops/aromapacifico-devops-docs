"""Checks the register of operational alarms against the signal catalog and the documents it cites, and prints its tables.

It fails when an alarm has no signal, no owner, no action or an unknown role, when an alarm sits on a metric that the
chosen telemetry does not keep, when a daily review is presented as an alarm, when an age threshold is taken from the
72 hour window of an order, or when the document and the cost no longer match the register.
It checks the register as written. It proves nothing about alarms, topics or rules that exist in an account.

    python -I docs/architecture/tools/alarms_catalog.py
"""
import re
import sys
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent.parent
errors = []


def check(cond, msg):
    if not cond:
        errors.append(msg)


def read(rel):
    p = DOCS / rel
    return p.read_text(encoding="utf-8") if p.exists() else None


OBS = read("architecture/observability.md") or ""
ROLES = {"Platform operator", "Drone operator, supervisor group"}
# the six custom metrics that the chosen telemetry keeps
KEPT = {"I-01", "I-06", "I-07", "I-08", "A-04", "D-05"}
PRICE_ALARM = 0.10
PRICE_COMPOSITE = 0.50
EMAIL_FREE = 1000
EMAIL_PER_1000 = 2.00 / 100  # USD 2.00 per 100,000 notifications

# kind: alarm (a billed metric alarm), rule (an event rule that notifies), review (a daily saved query read by a person), pending
# own: the card defines it, or the document that promised it
ALARMS = []


def al(i, crit, name, kind, signal, doc, kw, cond, owner, second, action, sev, count=1, own="new", note=""):
    ALARMS.append(dict(id=i, crit=crit, name=name, kind=kind, signal=signal, doc=doc, kw=kw, cond=cond, owner=owner, second=second, action=action, sev=sev, count=count, own=own, note=note))


# criterion 1, nodes and farms without telemetry
al("AL-01", 1, "Nodes silent over 24 hours", "alarm", "I-01", "iot/telemetry-ingestion.md", "Nodes silent over 24 hours",
   "The metric of silent nodes is above 0 in a daily period", "Platform operator", "",
   "Run the saved query of silent nodes by farm, tell a silent farm from a silent node, then check the gateway and the vereda before asking the Federation to contact the installer", "routine")
al("AL-02", 1, "Silent vereda on the LoRa path", "alarm", "I-13", "network/lora-out-of-coverage.md", "silent vereda",
   "Promised by the LoRa design. The document names no metric or event that carries it", "Platform operator", "",
   "Read the connection state of the gateway at the network server and check its power and backhaul", "routine", count=0,
   own="elsewhere", note="Counted as 0 alarms because the source of the signal is undefined. It stays on the list of open points.")
# criterion 2, crop alerts not delivered
al("AL-03", 2, "Alert not delivered", "alarm", "I-07", "iot/alert-delivery.md", "Undelivered alert",
   "The undelivered alert metric sums above 0 in 5 minutes", "Platform operator", "",
   "Open the alert by its identifier, read the push status and the SMS status in the log, and check whether the farm has a registered phone", "urgent")
al("AL-04", 2, "Slow live alert", "alarm", "I-06", "iot/alert-delivery.md", "Slow live alert",
   "The handoff time of a live alert has a maximum above 300 seconds in 5 minutes", "Platform operator", "",
   "Read the stage times of the alert record to see whether the wait was in the queue, the function or SNS", "routine")
al("AL-05", 2, "SMS of an urgent alert not delivered", "alarm", "I-08", "iot/alert-delivery.md", "SMS not delivered",
   "The SMS metric sums above 0 in 5 minutes", "Platform operator", "",
   "Read the SMS status of the alert and ask the Federation to reach the farmer by another way", "urgent")
al("AL-06", 2, "Delivery check queue dead letter", "alarm", "", "iot/alert-delivery.md", "Dead letter queue and alarm",
   "Messages visible in the dead letter queue above 0 in 5 minutes", "Platform operator", "",
   "Redrive after the cause is fixed. Until then no SMS and no missing-handoff metric exist for the alerts it holds", "urgent", own="elsewhere")
al("AL-07", 0, "Ingestion dead letter queue", "alarm", "I-03", "iot/telemetry-ingestion.md", "Messages in the dead letter queue",
   "Messages visible in the dead letter queue above 0", "Platform operator", "",
   "Read the failed message and the function log, fix the cause and redrive", "urgent", own="elsewhere")
al("AL-08", 0, "Ingestion queue age", "alarm", "I-02", "iot/telemetry-ingestion.md", "Age over 2 minutes",
   "Age of the oldest message above 2 minutes", "Platform operator", "",
   "Check the consumer, its throttles and the account concurrency", "routine", own="elsewhere")
# criterion 3, flights without record, fumigations without closure
al("AL-09", 3, "Object rejected at verification", "rule", "F-06", "drones/flight-objects.md", "flight.object.rejected",
   "The event flight.object.rejected is published", "Platform operator", "Drone operator, supervisor group",
   "Open the quarantine key from the event, tell the station to upload the object again under the same key", "routine", count=0)
al("AL-10", 3, "Flight record needs review", "rule", "F-06", "drones/flight-objects.md", "flight.record.review_required",
   "The event flight.record.review_required is published", "Drone operator, supervisor group", "Platform operator",
   "Open the order in review, read the reason of the event and decide whether to accept the record or ask for a new upload", "urgent", count=0)
al("AL-11", 3, "Flight whose log never arrives", "review", "F-04", "drones/fumigation-order.md", "The log never arrives",
   "A daily query lists every order in EXECUTED_PENDING_SYNC with the time since its execution ended. No age is defined, so none triggers a notice", "Platform operator", "Drone operator, supervisor group",
   "Read the daily list and pass each order to the drone supervisor, who asks the brigade whether the station holds the log and whether the link has returned", "routine", count=0,
   note="No event and no deadline exist for a log that never arrives, so this is a review and not an alarm.")
al("AL-12", 3, "Fumigation that cannot close", "review", "F-04", "drones/fumigation-order.md", "cannot close",
   "A daily query lists every order in VERIFICATION_PENDING or SYNC_REVIEW_REQUIRED with its age. No age is defined, so none triggers a notice", "Platform operator", "Drone operator, supervisor group",
   "Read the daily list and check whether the verification file exists and whether the function failed. The drone supervisor records the result by hand if needed", "routine", count=0,
   note="The documents set no time by which an order must close.")
# criterion 3, failed invocations of the four inference functions, from the failure policy
FUNCTIONS = ["Focus confirmation", "Verification", "Harvest estimation", "Telemetry batch"]
for n, f in enumerate(FUNCTIONS):
    al(f"AL-{13 + 3 * n}", 3, f"{f}, failed invocations", "alarm", "A-08", "architecture/failure-policy.md", "Failed invocations",
       "Lambda Errors of the function sum above 0 in 5 minutes", "Platform operator", "",
       "Read the failure entry of the log by case, order or flight identifier and check that the state did not move. It may still succeed on a retry", "routine")
    al(f"AL-{14 + 3 * n}", 3, f"{f}, messages in the dead letter queue", "alarm", "A-08", "architecture/failure-policy.md", "Messages in the dead letter queue",
       "Messages visible in the dead letter queue above 0 in 5 minutes", "Platform operator", "Drone operator, supervisor group" if f == "Verification" else "",
       "Fix the cause and redrive the work queue. For verification the supervisor may record the result by hand meanwhile", "urgent")
    al(f"AL-{15 + 3 * n}", 3, f"{f}, events the rule could not deliver", "alarm", "A-07", "architecture/failure-policy.md", "Events the rule could not deliver",
       "EventBridge FailedInvocations of the rule sums above 0 in 5 minutes", "Platform operator", "",
       "Read the rule dead letter queue once it exists, otherwise the saved query of flight records with no result", "urgent")
# promised by other documents and counted in the total
al("AL-25", 0, "Sack tables, failed writes", "alarm", "", "architecture/recovery.md", "failed writes to the sack tables",
   "As the recovery design states", "Platform operator", "", "Follow the recovery steps of the design", "urgent", own="elsewhere")
al("AL-26", 0, "Sack tables, throttled requests", "alarm", "", "architecture/recovery.md", "throttled requests",
   "As the recovery design states", "Platform operator", "", "Follow the recovery steps of the design", "routine", own="elsewhere")
al("AL-27", 0, "Deletion job failed or limited", "alarm", "D-05", "architecture/persistence-and-archive.md", "alarm warns after two failed runs",
   "The metric of failed or limited runs. Two failed runs warn and reaching the run limit raises an alarm, and one metric cannot tell them apart", "Platform operator", "",
   "Read the record of the run and the limit that stopped it", "routine", own="elsewhere",
   note="Open point. The chosen telemetry keeps one metric for failed and limited runs.")
for k in range(3):
    al(f"AL-{28 + k}", 0, f"Telemetry function {k + 1}, errors during a release", "alarm", "I-09", "architecture/delivery-pipelines.md", "error alarm of any of the three functions",
       "Lambda Errors of the function, as the release design uses to stop a deployment", "Platform operator", "", "Stop the release and read the function log", "routine", own="elsewhere")
# events that notify with no alarm charge
al("AL-31", 0, "Encryption key state change", "rule", "D-03", "architecture/recovery.md", "state of the encryption key",
   "A key state change event", "Platform operator", "", "Confirm the change was planned and restore the key if not", "urgent", count=0, own="elsewhere")
al("AL-32", 0, "Point-in-time recovery turned off", "rule", "D-04", "architecture/recovery.md", "point-in-time recovery turned off",
   "A configuration change event of a sack table", "Platform operator", "", "Turn it on again through the infrastructure code", "urgent", count=0, own="elsewhere")

IDS = [a["id"] for a in ALARMS]
check(len(IDS) == len(set(IDS)), "an alarm id is listed twice")
KINDS = {"alarm", "rule", "review", "pending"}


def run_checks():
    for a in ALARMS:
        i = a["id"]
        check(a["kind"] in KINDS, f"{i} has an unknown kind")
        check(a["owner"] in ROLES and (not a["second"] or a["second"] in ROLES), f"{i} names a role outside the access design")
        check(bool(a["action"]) and bool(a["cond"]) and bool(a["name"]), f"{i} has no condition or action")
        check(a["sev"] in {"urgent", "routine"}, f"{i} has an unknown severity")
        t = read(a["doc"])
        check(t is not None, f"{i}: document {a['doc']} does not exist")
        if t is not None:
            check(a["kw"] in t, f"{i}: {a['doc']} no longer contains '{a['kw']}'")
        if a["signal"]:
            check(f"| {a['signal']} |" in OBS, f"{i}: signal {a['signal']} is not in the catalog")
        if a["kind"] == "alarm" and a["signal"] in {"I-01", "I-06", "I-07", "I-08", "A-04", "D-05", "I-04", "I-05", "I-15", "F-04"}:
            check(a["signal"] in KEPT, f"{i} sits on {a['signal']}, which the chosen telemetry reads by a query")
        if a["kind"] == "review":
            check(a["count"] == 0 and "alarm" not in a["name"].lower(), f"{i} is a daily review and cannot be billed or named as an alarm")
            check("no age is defined" in a["cond"].lower(), f"{i} states an age that no document defines")
        check("72" not in a["cond"], f"{i} takes a time from the 72 hour window of an order, which is not a deadline for the log")
        check("dashboard" not in a["action"].lower(), f"{i} sends the operator to a dashboard, which the chosen telemetry does not have")
    # the failure policy covers four inference functions with three alarms each
    fp = [a for a in ALARMS if a["doc"] == "architecture/failure-policy.md"]
    check(len(fp) == 12, "the failure policy gives three alarms for each of four functions")
    # the live-only metric of the slow live alert
    ad = read("iot/alert-delivery.md") or ""
    sl = read("architecture/service-levels.md") or ""
    check("kind` set to `live`" in ad, "the alert delivery design no longer states the live filter of the slow alert")
    check("no new metric" in sl.replace("\n", " ") or "saved queries" in sl, "the service levels no longer measure by saved queries")
    check("without dimensions" in OBS or "no split by kind and link" in OBS.lower() or "not split by kind and link" in OBS, "the chosen telemetry no longer keeps the handoff time without dimensions")
    # every criterion has a row
    for c in (1, 2, 3):
        check(any(a["crit"] == c for a in ALARMS), f"criterion {c} has no row")
    doc = read("architecture/operational-alarms.md") or ""
    check(bool(doc), "the alarm document is missing")
    covered = set(re.findall(r"AL-\d+", doc))
    for lo, hi in re.findall(r"AL-(\d+) to AL-(\d+)", doc):
        covered |= {f"AL-{k:02d}" for k in range(int(lo), int(hi) + 1)}
    for a_ in ALARMS:
        check(a_["id"] in covered, f"{a_['id']} is not in the document")
    tel = telemetry()
    n = sum(a_["count"] for a_ in ALARMS)
    check(f"| Alarms of the register | {n} | {n * PRICE_ALARM:.2f} |" in doc, "the document does not show the alarm count and cost of the register")
    for m, v in tel.items():
        check(f"| {m} | {v:.2f} | {n * PRICE_ALARM:.2f} | {v + n * PRICE_ALARM:.2f} | 2.20 | {v + n * PRICE_ALARM - 2.20:.2f} |" in doc, f"the document does not show the total of the {m.lower()}")
    check(any(a["kind"] == "alarm" for a in ALARMS if a["crit"] == 1), "criterion 1 has no alarm")
    for a in ALARMS:
        check((a["kind"] == "alarm") == (a["count"] > 0) or a["id"] == "AL-02", f"{a['id']} is billed inconsistently with its kind")


def telemetry():
    rows = re.findall(r"\| (Normal month|Harvest month) \| [\d.]+ \| [\d.]+ \| [\d.]+ \| [\d.]+ \| [\d.]+ \| ([\d.]+) \| USD 0.10 \|", OBS)
    check(len(rows) == 2, "the chosen telemetry table was not found")
    return {k: float(v) for k, v in rows}


def totals():
    tel = telemetry()
    n_all = sum(a["count"] for a in ALARMS)
    n_new = sum(a["count"] for a in ALARMS if a["crit"] in (1, 2))
    n_fp = sum(a["count"] for a in ALARMS if a["doc"] == "architecture/failure-policy.md")
    return tel, n_all, n_new, n_fp


def main():
    run_checks()
    tel, n_all, n_new, n_fp = totals()
    print("## Register of alarms")
    print("| Id | Criterion | Alarm | Kind | Signal | Condition | Answers | Second | Severity |")
    print("|---|---|---|---|---|---|---|---|---|")
    for a in ALARMS:
        print(f"| {a['id']} | {a['crit']} | {a['name']} | {a['kind']} | {a['signal'] or 'service metric'} | {a['cond']} | {a['owner']} | {a['second'] or 'none'} | {a['sev']} |")
    print("\n## Actions")
    print("| Id | First action | Note |\n|---|---|---|")
    for a in ALARMS:
        print(f"| {a['id']} | {a['action']} | {a['note']} |")
    kinds = {k: sum(1 for a in ALARMS if a["kind"] == k) for k in KINDS}
    print(f"\n## Counts\nRows {len(ALARMS)}, alarms billed {n_all}, of which {n_new} serve criteria 1 and 2 and {n_fp} come from the failure policy. Kinds {kinds}.")
    print("\n## Cost")
    print("| Item | Count | Rate | USD a month |\n|---|---|---|---|")
    print(f"| Standard metric alarms of the register | {n_all} | USD {PRICE_ALARM:.2f} | {n_all * PRICE_ALARM:.2f} |")
    print(f"| Of them for silent nodes and undelivered alerts | {n_new} | USD {PRICE_ALARM:.2f} | {n_new * PRICE_ALARM:.2f} |")
    print("\n| Month | Telemetry before alarms | Alarms of the register | Total | Reference | Above the reference |\n|---|---|---|---|---|---|")
    for m in ("Normal month", "Harvest month"):
        tot = tel.get(m, 0) + n_all * PRICE_ALARM
        print(f"| {m} | {tel.get(m, 0):.2f} | {n_all * PRICE_ALARM:.2f} | {tot:.2f} | 2.20 | {tot - 2.20:.2f} |")
    print(f"\nMetric math merges nothing, since each metric in an expression is billed as one alarm metric. A composite alarm costs USD {PRICE_COMPOSITE:.2f} and adds to its parts.")
    print(f"Event rules carry no alarm charge. The events are billed to the bus at USD 1.00 per million custom events and email notifications are free up to {EMAIL_FREE:,} a month and USD {EMAIL_PER_1000:.2f} per 1,000 after.")
    for e in errors:
        print("FAIL", e)
    print("OK" if not errors else f"{len(errors)} problems")
    sys.exit(1 if errors else 0)


main()
