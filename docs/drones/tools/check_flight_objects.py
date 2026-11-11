"""Checks the flight object design against the documents and code it must agree with.

Usage: python3 check_flight_objects.py [docs_dir]
With no argument it reads the docs folder of this repository. It prints OK and exits 1 on the first failed check.

1. The map has unique prefixes, and only a prefix with no mission type nests in another one.
2. Every input prefix of the inference functions is in the map with the same anchor.
3. The overwrite denial of the bucket policy covers every conditional prefix and leaves out restricted and quarantine.
4. The lifecycle days match the retention and persistence designs.
5. The prefixes and bucket suffix of the infrastructure code exist in the map, when that repository is cloned beside this one.
6. Mission types agree across the map, the schemas, the order schema and the infrastructure code.
7. The samples follow their schemas, and their keys follow the map.
8. Only a published record or a reviewed and verified upload enters FLIGHT_RECORD_PERSISTED, and CLOSED is reached only from VERIFIED.
9. The events of the map are the events of the schema and of the document.
10. The document lists every key pattern and the cost table matches the rates and volumes.
"""
import json
import pathlib
import re
import sys

import jsonschema

RATES = {
    "event": 1.00 / 1_000_000,
    "sqs_request": 0.40 / 1_000_000,
    "get_request": 0.004 / 10_000,
    "gir_transition": 0.02 / 1_000,
}
OBJECTS = 9_300
IMAGES = 9_000
PLATFORM_EVENTS = 9_500
IMAGES_PER_YEAR = 4 * 9_000 + 8 * 1_500
ARCHIVE_BUCKET_ROOTS = {"crop/", "drying/"}


def fail(message):
    print(f"FAIL {message}")
    sys.exit(1)


def check(condition, message):
    if not condition:
        fail(message)


def validate(schema, instance, name):
    try:
        jsonschema.Draft202012Validator(schema).validate(instance)
    except jsonschema.ValidationError as error:
        fail(f"{name} does not follow its schema at {list(error.absolute_path)}, {error.message}")


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def anchor(pattern):
    parts = pattern.split("/")
    return parts[1] if len(parts) > 2 else None


def cost_rows():
    rows = [
        ("S3 events to EventBridge", OBJECTS * RATES["event"]),
        ("Platform events of verification and publication", PLATFORM_EVENTS * RATES["event"]),
        ("Verification queue", OBJECTS * 3 * RATES["sqs_request"]),
        ("Reads of object attributes", OBJECTS * RATES["get_request"]),
        ("Transitions to Glacier Instant Retrieval", IMAGES * RATES["gir_transition"]),
    ]
    return rows, sum(v for _, v in rows)


def main():
    docs = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parents[2]
    drones = docs / "drones"
    schemas = drones / "schemas"
    doc = (drones / "flight-objects.md").read_text(encoding="utf-8")
    fmap = load(schemas / "flight-object-map.json")
    policy = load(schemas / "flight-objects.bucket-policy.json")
    prefixes = fmap["prefixes"]
    roots = [p["root"] for p in prefixes]
    by_root = {p["root"]: p for p in prefixes}

    # 1
    check(len(roots) == len(set(roots)), "a prefix is listed twice")
    for p in prefixes:
        check(p["key_pattern"].startswith(p["root"]), f"{p['root']} has a key pattern outside its prefix")
        check(p["lifecycle"] in fmap["lifecycle_rules"], f"{p['root']} uses an unknown lifecycle")
        for other in roots:
            if other != p["root"] and p["root"].startswith(other):
                check(p["mission_type"] is None and not p["storage_events"],
                      f"{p['root']} nests in {other} and must hold no mission and send no storage events")
    for special in ("restricted/", "quarantine/"):
        check(special in by_root, f"{special} is missing from the map")
        check(not any(r != special and (r.startswith(special) or special.startswith(r)) for r in roots),
              f"{special} nests in another prefix or holds one")
        check(not by_root[special]["conditional_write"], f"{special} must accept copies")

    # 2
    inference = (docs / "architecture" / "inference-functions.md").read_text(encoding="utf-8")
    scopes = set(re.findall(r"`([a-z]+/(?:derived/)?<[a-z_]+>/<[a-z_]+>/)`", inference))
    scopes |= {s for s in re.findall(r"`([a-z]+/)`", inference) if s not in ARCHIVE_BUCKET_ROOTS}
    check(scopes, "no input prefix found in the inference design")
    for scope in scopes:
        root = scope.split("<")[0]
        check(root in by_root, f"inference prefix {scope} has no prefix in the map")
        if "<" in scope:
            check(anchor(scope) == anchor(by_root[root]["key_pattern"]),
                  f"inference prefix {scope} and the map anchor {by_root[root]['key_pattern']} differ")

    # 3
    statements = {s["Sid"]: s for s in policy["Statement"]}
    for sid in ("DenyInsecureTransport", "DenyOldTls", "DenyOtherEncryption", "DenyOtherKey", "DenyOverwrite"):
        check(sid in statements, f"the bucket policy lacks {sid}")
    overwrite = statements["DenyOverwrite"]
    check(overwrite["Condition"] == {"Null": {"s3:if-none-match": "true"}, "Bool": {"s3:ObjectCreationOperation": "true"}},
          "the overwrite denial does not test the conditional header with the multipart exemption")
    covered = {r.split(":::", 1)[1].split("/", 1)[1].rstrip("*") for r in overwrite["Resource"]}
    for p in prefixes:
        inside = any(p["root"].startswith(c) for c in covered)
        check(inside == p["conditional_write"], f"{p['root']} conditional write and the overwrite denial disagree")
    check(statements["DenyOldTls"]["Condition"] == {"NumericLessThan": {"s3:TlsVersion": "1.2"}}, "TLS floor is not 1.2")
    check(len(policy["Statement"]) == 5 and "five denials" in doc, "the document and the policy disagree on the denials")

    # 4
    retention = (docs / "security" / "personal-data-and-retention.md").read_text(encoding="utf-8")
    persistence = (docs / "architecture" / "persistence-and-archive.md").read_text(encoding="utf-8")
    evidence, short, every = (fmap["lifecycle_rules"][k] for k in ("evidence", "short", "all"))
    check("| Photos, maps and polygons | S3 Standard, 90 days | Glacier Instant Retrieval, to five years |" in retention
          and evidence["transition_days"] == 90 and evidence["storage_class"] == "GLACIER_IR",
          "the evidence transition differs from the retention design")
    check("| Objects with a person | Restricted prefix, 30 days |" in retention and short["expire_current_days"] == 30,
          "the short lifecycle differs from the retention design")
    check("| Expire the current version | 1,826 days" in persistence and evidence["expire_current_days"] == 1826,
          "the evidence expiry differs from the persistence design")
    check("| Expire noncurrent versions | 30 days" in persistence and evidence["expire_noncurrent_days"] == 30,
          "the noncurrent expiry differs from the persistence design")
    check("| Abort incomplete uploads | 7 days |" in persistence and every["abort_incomplete_multipart_days"] == 7,
          "the multipart abort differs from the persistence design")
    check(evidence["transition_min_size_bytes"] == 128 * 1024, "the transition floor is not 128 KB")

    # 5
    infra = docs.parents[1] / "aromapacifico-devops-infra" / "envs"
    infra_types = set()
    if infra.is_dir():
        for locals_tf in infra.glob("*/locals.tf"):
            text = locals_tf.read_text(encoding="utf-8")
            for used in re.findall(r'_prefix\s*=\s*"([a-z/]+)"', text):
                check(used in by_root, f"{locals_tf} uses {used}, which is not in the map")
            check(fmap["bucket"].replace("<prefix>", "") in text, f"{locals_tf} names the flight bucket differently")
        for main_tf in infra.glob("*/main.tf"):
            infra_types |= set(re.findall(r'mission_type\s*=\s*"([A-Z_]+)"', main_tf.read_text(encoding="utf-8")))
    else:
        print("infra repository not cloned beside this one, step 5 skipped")

    # 6
    map_types = {p["mission_type"] for p in prefixes if p["mission_type"]}
    record_schema = load(schemas / "flight-record.schema.json")
    events_schema = load(schemas / "flight-object-events.schema.json")
    order_schema = load(schemas / "fumigation-order.schema.json")
    check(set(record_schema["properties"]["mission_type"]["enum"]) == map_types, "record schema and map mission types differ")
    for variant in events_schema["oneOf"]:
        check(set(variant["properties"]["detail"]["properties"]["mission_type"]["enum"]) <= map_types | {None},
              f"{variant['properties']['detail-type']['const']} names a mission type outside the map")
    prerequisite = order_schema["properties"]["prerequisite"]["properties"]["mission_type"]["enum"]
    check(set(prerequisite) <= map_types, "the order prerequisite names a mission type outside the map")
    check(infra_types <= map_types, f"the infrastructure code uses mission types {infra_types - map_types} outside the map")

    # 7
    record = load(schemas / "flight-record.sample.json")
    jsonschema.Draft202012Validator.check_schema(record_schema)
    validate(record_schema, record, "the sample flight record")
    root = next(p for p in prefixes if p["mission_type"] == record["mission_type"])
    base = f"{root['root']}{record['anchor']['id']}/{record['execution_id']}/"
    check(anchor(root["key_pattern"]) == f"<{record['anchor']['kind']}>", "the sample record anchor differs from the map")
    for key in [o["key"] for o in record["objects"]] + [record["result_manifest"]["object"]["key"]]:
        check(key.startswith(base), f"sample key {key} is outside {base}")
    check(record["flight_log"]["artifact_id"] in {o["artifact_id"] for o in record["objects"]},
          "the flight log of the sample record is not one of its objects")
    order = load(schemas / "fumigation-order.sample.json")
    execution = next(e for e in order["executions"] if e["execution_id"] == record["execution_id"])
    log = next(o for o in record["objects"] if o["artifact_id"] == record["flight_log"]["artifact_id"])
    check(execution["log"]["sha256"] == log["sha256"] and execution["flight_record_id"] == record["flight_record_id"],
          "the sample record and the sample order disagree")
    for event in load(schemas / "flight-object-events.sample.json"):
        validate(events_schema, event, f"the sample event {event['detail-type']}")
        detail = event["detail"]
        key = detail.get("key") or detail.get("record", {}).get("key")
        if key:
            owner = next(p for p in prefixes if p["mission_type"] == detail["mission_type"])
            check(key.startswith(owner["root"]) and f"/{detail['execution_id']}/" in key,
                  f"event key {key} does not follow the map")

    # 8
    machine = load(schemas / "fumigation-order-transitions.json")["transitions"]
    allowed_entries = {("platform_function", "flight.record.published"), ("supervisor", "sync_review.resolved")}
    for t in machine:
        if t["to"] == "FLIGHT_RECORD_PERSISTED":
            check((t["actor"], t["trigger"]) in allowed_entries, f"{t['from']} enters FLIGHT_RECORD_PERSISTED on {t['trigger']}")
            if t["actor"] == "supervisor":
                check("verified" in t["guard"], "the supervisor enters FLIGHT_RECORD_PERSISTED without verified evidence")
        if t["to"] == "CLOSED":
            check(t["from"] == "VERIFIED", f"CLOSED is reached from {t['from']}")
        if t["to"] == "VERIFIED":
            check("published" in t["guard"], f"VERIFIED is reached on {t['trigger']} without a published record")

    # 9
    map_events = {e["detail_type"] for e in fmap["platform_events"]}
    schema_events = {v["properties"]["detail-type"]["const"] for v in events_schema["oneOf"]}
    check(map_events == schema_events, "map and schema events differ")
    for name in map_events:
        check(f"| `{name}` | Platform |" in doc, f"the document does not list {name}")
    check({t["trigger"] for t in machine} >= {"flight.record.published", "flight.record.review_required"},
          "the order no longer moves on the flight record events")

    # 10
    for p in prefixes:
        check(f"`{p['key_pattern']}" in doc, f"the document does not list {p['key_pattern']}")
    rows, total = cost_rows()
    for label, value in rows:
        line = next((ln for ln in doc.splitlines() if ln.startswith(f"| {label}")), None)
        check(line is not None, f"the cost table lacks {label}")
        check(line.rstrip(" |").endswith(f"{value:.2f}"), f"{label} should be {value:.2f}")
    check(f"**About {total:.2f}**" in doc, f"the cost total should be {total:.2f}")
    check(f"USD {IMAGES_PER_YEAR * RATES['gir_transition']:.2f} a year" in doc, "the yearly transition cost differs")

    print(f"OK {len(prefixes)} prefixes, {len(map_events)} platform events, {len(scopes)} inference prefixes, "
          f"cost USD {total:.2f} a harvest month")


if __name__ == "__main__":
    main()
