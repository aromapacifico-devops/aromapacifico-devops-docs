"""Validate every inference result example against the common schema."""
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ARCHITECTURE = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ARCHITECTURE / "schemas" / "inference-result.schema.json"
EXAMPLES = ARCHITECTURE / "examples" / "inference-results"
EXPECTED = {
    "focus-confirmation.json": "focus_confirmation",
    "verification.json": "verification",
    "harvest-estimation.json": "harvest_estimation",
    "telemetry-batch.json": "telemetry_batch",
}


def idempotency_key(example):
    payload = {
        "function": example["function"],
        "subject": example["subject"],
        "source_objects": sorted(
            example["source_objects"],
            key=lambda source: (
                source["bucket"],
                source["key"],
                source["version_id"],
                source["sha256"],
                source["role"],
            ),
        ),
        "model_id": example["model_id"],
        "prompt_version": example["prompt_version"],
    }
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


def main():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    paths = sorted(EXAMPLES.glob("*.json"))
    assert {path.name for path in paths} == set(EXPECTED), "The four examples must be present"

    errors = []
    for path in paths:
        example = json.loads(path.read_text(encoding="utf-8"))
        if example.get("function") != EXPECTED[path.name]:
            errors.append(f"{path.name}: function does not match the filename")
        errors.extend(
            f"{path.name}: {'/'.join(str(part) for part in error.path)} {error.message}"
            for error in validator.iter_errors(example)
        )
        expected_key = idempotency_key(example)
        if example.get("idempotency_key") != expected_key:
            errors.append(f"{path.name}: idempotency_key does not match the canonical value")

    if errors:
        print("\n".join(errors))
        raise SystemExit(1)
    print(f"OK {len(paths)} inference result examples")


if __name__ == "__main__":
    main()
