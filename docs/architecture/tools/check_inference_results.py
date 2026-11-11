"""Validate every inference result example against the common schema."""
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

    if errors:
        print("\n".join(errors))
        raise SystemExit(1)
    print(f"OK {len(paths)} inference result examples")


if __name__ == "__main__":
    main()
