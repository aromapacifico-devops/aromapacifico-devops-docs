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
# volumes assumed for the small charges that the totals leave out because free allowances absorb them
SCHEDULED_CHECKS = 25 * 3 * 2  # orders a month in harvest, three waiting states, two checks
PLATFORM_EVENTS = 300
NOTICES = 1000
SNS_REQUESTS = 1000


def small_charges():
    """What the event rules, schedules and notices would cost with no free allowance at all."""
    return SCHEDULED_CHECKS * 1.00 / 1e6 + PLATFORM_EVENTS * 1.00 / 1e6 + NOTICES * 2.00 / 100000 + SNS_REQUESTS * 0.50 / 1e6


# kind: alarm (a billed metric alarm), rule (an event rule that notifies), review (a daily saved query read by a person), pending
# own: the card defines it, or the document that promised it
ALARMS = []


def al(i, crit, name, kind, signal, doc, kw, cond, owner, second, action, sev, count=1, own="new", note="", status="documented", mechanism="", threshold="", basis="", event=""):
    ALARMS.append(dict(status=status, mechanism=mechanism, threshold=threshold, basis=basis, event=event, id=i, crit=crit, name=name, kind=kind, signal=signal, doc=doc, kw=kw, cond=cond, owner=owner, second=second, action=action, sev=sev, count=count, own=own, note=note))


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

# proposals that cover what criterion 3 leaves open. None is an approved rule, and every threshold is an assumption
al("AL-33", 3, "Flight object verification, messages in the dead letter queue", "alarm", "F-06", "drones/flight-objects.md", "Verification function fails",
   "Messages visible in the dead letter queue above 0 in 5 minutes", "Platform operator", "",
   "Read the failed message and the function log, fix the cause and redrive. The object stays unverified and the flight keeps waiting for it", "urgent",
   status="proposed", mechanism="CloudWatch alarm on the SQS metric of the dead letter queue, with the condition that two merged documents already use for dead letter queues",
   threshold="Any message", basis="Assumption. The flight object design sets no retry count or alarm for this queue")
al("AL-34", 3, "Flight object verification, failed invocations", "alarm", "F-06", "drones/flight-objects.md", "Verification function fails",
   "Lambda Errors of the function sum above 0 in 5 minutes", "Platform operator", "",
   "Read the failure entry by execution identifier and check that the object is still unverified. It may still succeed on a retry", "routine",
   status="proposed", mechanism="CloudWatch alarm on the Lambda metric, as the failure policy does for the inference functions",
   threshold="Any error", basis="Assumption. Same condition as the failure policy")
al("AL-35", 3, "Flight completion, failed invocations", "alarm", "F-06", "drones/flight-objects.md", "Crash between the record object and the case item",
   "Lambda Errors of the completion function sum above 0 in 5 minutes", "Platform operator", "Drone operator, supervisor group",
   "Read the failure entry by execution identifier. The station repeats the completion request, and a repeat finds the stored record, so check that a record is published", "urgent",
   status="proposed", mechanism="CloudWatch alarm on the Lambda metric. The completion function answers the station directly and has no queue",
   threshold="Any error", basis="Assumption. The completion function is the step that publishes the flight record, so its failure is a flight without a record")
al("AL-36", 3, "Fumigation log overdue", "rule", "F-04", "drones/fumigation-order.md", "The log never arrives",
   "An order is still in EXECUTED_PENDING_SYNC when its check runs", "Drone operator, supervisor group", "Platform operator",
   "Ask the brigade whether the station holds the log and whether the link has returned, look for events of the execution in the flight object log, and run the incident procedure if the station is lost", "urgent", count=0,
   status="proposed", event="order.attention_required",
   mechanism="When the transition function moves the order into the state it creates a one-time schedule, as it already does for the end of the order window. At the check the function reads the order, and if the state and revision are the same it publishes one platform event that an event rule sends to the topic. A changed state makes the check do nothing",
   threshold="First check 24 hours after the order entered the state, second check at 48 hours", basis="Assumption. No document sets a time for the log to arrive. The orders in this state wait for a link that may be a day away")
al("AL-37", 3, "Package past its window with no flight record", "rule", "F-06", "drones/flight-objects.md", "flight.record.published",
   "A package whose execution window has ended has no flight.record.published and no flight.record.review_required for its package_id when the check runs", "Drone operator, supervisor group", "Platform operator",
   "Ask the brigade whether the flight took place. A package that was never flown shows here too, and the brigade closes the item", "routine", count=0,
   status="proposed", event="flight.package.overdue",
   mechanism="The package function creates a one-time schedule at the end of the execution window of the package plus the grace. The check looks for a record of the package and publishes one platform event when none exists",
   threshold="24 hours after the end of the package window", basis="Assumption. The package window is the one in the signed package and is not the 72 hour window of an order")
al("AL-38", 3, "Order waiting too long to close", "rule", "F-04", "drones/post-fumigation-verification.md", "VERIFICATION_PENDING",
   "An order is still in SYNC_REVIEW_REQUIRED, PARTIAL, VERIFICATION_PENDING or VERIFIED when its check runs", "Drone operator, supervisor group", "Platform operator",
   "Open the order and find what it waits for. In SYNC_REVIEW_REQUIRED decide the record. In VERIFICATION_PENDING check the verification file and the function. In VERIFIED review the verification and close", "routine", count=0,
   status="proposed", event="order.attention_required",
   mechanism="The same schedule as the log check, created when the order enters each waiting state. For VERIFICATION_PENDING the check time is counted from the end of the window of the latest verification package, which each attempt records, and for the other states from the transition",
   threshold="24 hours after the order entered the state or after the verification window ended, second check at 48 hours", basis="Assumption. The documents give each state one exit and no time for it")

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
    for a_ in ALARMS:
        if a_["status"] == "proposed":
            check(bool(a_["mechanism"]) and bool(a_["threshold"]) and "assumption" in a_["basis"].lower(), f"{a_['id']} is a proposal and needs its mechanism, threshold and an assumption as basis")
        else:
            check(not a_["threshold"], f"{a_['id']} is documented and cannot carry a proposed threshold")
        if a_["event"]:
            # a proposed event name must not be defined by any other document, otherwise it is no longer a proposal
            for path in DOCS.rglob("*.md"):
                if path.name != "operational-alarms.md":
                    check(a_["event"] not in path.read_text(encoding="utf-8"), f"{a_['event']} appears in {path.name}, so it is no longer only a proposal")
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
    check(f"about USD {small_charges():.2f} a month" in doc, "the document does not state the small charges that the free allowances absorb")
    check("apply no free tier to CloudWatch" in doc, "the document does not say where free allowances are and are not used")
    tel = telemetry()
    nd = sum(a_["count"] for a_ in ALARMS if a_["status"] == "documented")
    npr = sum(a_["count"] for a_ in ALARMS if a_["status"] == "proposed")
    check(f"| Alarms in merged documents | {nd} | {nd * PRICE_ALARM:.2f} |" in doc, "the document does not show the count and cost of the documented alarms")
    check(f"| Proposed alarms for the flight object functions | {npr} | {npr * PRICE_ALARM:.2f} |" in doc, "the document does not show the count and cost of the proposed alarms")
    for m, v in tel.items():
        d1, d2 = v + nd * PRICE_ALARM, v + (nd + npr) * PRICE_ALARM
        check(f"| {m} | {v:.2f} | {d1:.2f} | {d1 - 2.20:.2f} | {d2:.2f} | {d2 - 2.20:.2f} |" in doc, f"the document does not show the totals of the {m.lower()}")


def telemetry():
    rows = re.findall(r"\| (Normal month|Harvest month) \| [\d.]+ \| [\d.]+ \| [\d.]+ \| [\d.]+ \| [\d.]+ \| ([\d.]+) \| USD 0.10 \|", OBS)
    check(len(rows) == 2, "the chosen telemetry table was not found")
    return {k: float(v) for k, v in rows}


def totals():
    tel = telemetry()
    n_all = sum(a["count"] for a in ALARMS if a["status"] == "documented")
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
    npr = sum(a["count"] for a in ALARMS if a["status"] == "proposed")
    print("\n## Cost")
    print("| Item | Count | USD a month |\n|---|---|---|")
    print(f"| Alarms in merged documents | {n_all} | {n_all * PRICE_ALARM:.2f} |")
    print(f"| Proposed alarms for the flight object functions | {npr} | {npr * PRICE_ALARM:.2f} |")
    print(f"| Alarms with the proposals | {n_all + npr} | {(n_all + npr) * PRICE_ALARM:.2f} |")
    print("\n| Month | Telemetry before alarms | Total with documented alarms | Above the reference | Total with the proposals | Above the reference |\n|---|---|---|---|---|---|")
    for m in ("Normal month", "Harvest month"):
        v = tel.get(m, 0)
        d1, d2 = v + n_all * PRICE_ALARM, v + (n_all + npr) * PRICE_ALARM
        print(f"| {m} | {v:.2f} | {d1:.2f} | {d1 - 2.20:.2f} | {d2:.2f} | {d2 - 2.20:.2f} |")
    print(f"\nMetric math merges nothing, since each metric in an expression is billed as one alarm metric. A composite alarm costs USD {PRICE_COMPOSITE:.2f} and adds to its parts.")
    print(f"Without any free allowance, the schedules, platform events and notices at the assumed volumes would add about USD {small_charges():.2f} a month, and the totals leave them out because the allowances of Scheduler and SNS absorb them.")
    print(f"Event rules carry no alarm charge. The events are billed to the bus at USD 1.00 per million custom events and email notifications are free up to {EMAIL_FREE:,} a month and USD {EMAIL_PER_1000:.2f} per 1,000 after. One-time schedules are free for the first 14 million invocations a month.")
    for e in errors:
        print("FAIL", e)
    print("OK" if not errors else f"{len(errors)} problems")
    sys.exit(1 if errors else 0)


main()
