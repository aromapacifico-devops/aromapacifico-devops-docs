"""Checks that the buyer view of a sack carries no personal or internal data.

Usage: python3 check_buyer_view.py [schema] [sample]
With no arguments it reads schemas/buyer-view.schema.json and schemas/buyer-view.sample.json.

1. Every property the schema declares is on the allow list, and none is on the deny list.
2. Every object in the schema closes with additionalProperties false, so no other field can appear.
3. The sample validates against the schema, for the keywords the schema uses.
Exits 1 on the first failed check.
"""
import datetime
import json
import pathlib
import re
import sys

ALLOWED = {
    "schema_version", "sack_code", "origin", "country", "department", "state", "state_reason",
    "process_dates", "registered_on", "drying_started_on", "drying_ended_on", "received_at_center_on",
    "dispatched_to_port_on", "delivered_on", "drying", "status", "hours_monitored",
    "readings_completeness_pct", "grain_temp_max_c", "hours_above_40c", "grain_humidity_first_pct",
    "grain_humidity_last_pct",
}
# Fields of the event envelope, the catalog, the farm profile, the lot and the people that never reach a buyer.
DENIED = re.compile(
    r"farm|lot_id|owner|farmer|carrier|trip|center_id|node|person|name|national|cedula|phone|email|address|"
    r"plate|location|lat|lon|position|observation|note|receipt|received_by|captured_by|recorded_by|"
    r"created_by|ended_by|event_id|seq|weight|municipality|vereda|polygon|_at$"
)


def properties(schema, path=""):
    """Yield (path, name, subschema) for every declared property, and fail on open objects."""
    if schema.get("type") == "object":
        if schema.get("additionalProperties") is not False:
            fail(f"{path or 'root'} does not set additionalProperties to false")
        for name, sub in schema.get("properties", {}).items():
            yield path, name, sub
            yield from properties(sub, f"{path}.{name}" if path else name)


def validate(value, schema, path="root"):
    types = schema.get("type")
    types = types if isinstance(types, list) else [types] if types else []
    kind = {dict: "object", str: "string", bool: "boolean", type(None): "null", list: "array"}.get(type(value))
    if isinstance(value, int) and not isinstance(value, bool):
        kind = "integer"
    elif isinstance(value, float):
        kind = "number"
    if types and kind not in types and not (kind == "integer" and "number" in types):
        fail(f"{path} is {kind}, expected {types}")
    if "enum" in schema and value not in schema["enum"]:
        fail(f"{path} value {value!r} is outside the enum")
    if kind == "string":
        if "pattern" in schema and not re.search(schema["pattern"], value):
            fail(f"{path} does not match its pattern")
        if schema.get("format") == "date":
            datetime.date.fromisoformat(value)
    if kind in ("integer", "number"):
        if value < schema.get("minimum", value) or value > schema.get("maximum", value):
            fail(f"{path} is outside its range")
    if kind == "object":
        for name in schema.get("required", []):
            if name not in value:
                fail(f"{path}.{name} is required")
        for name, sub in value.items():
            if name not in schema.get("properties", {}):
                fail(f"{path}.{name} is not declared")
            validate(sub, schema["properties"][name], f"{path}.{name}")


def fail(message):
    print(f"FAIL {message}")
    sys.exit(1)


def main():
    here = pathlib.Path(__file__).resolve().parent.parent / "schemas"
    schema_path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else here / "buyer-view.schema.json"
    sample_path = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else here / "buyer-view.sample.json"
    schema = json.loads(schema_path.read_text())
    sample = json.loads(sample_path.read_text())

    count = 0
    for path, name, _ in properties(schema):
        where = f"{path}.{name}" if path else name
        if name not in ALLOWED:
            fail(f"{where} is not on the allow list")
        if DENIED.search(name):
            fail(f"{where} matches the deny list")
        count += 1
    validate(sample, schema)
    print(f"OK {count} fields, all allowed, every object closed, sample valid")


if __name__ == "__main__":
    main()
