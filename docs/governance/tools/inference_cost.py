"""Cost of the inference functions per 1,000 invocations and per month.

Prints the tables of docs/governance/inference-cost.md from the rates of the
AWS Price List API for us-east-1 and the volumes of the pilot. Run with no
arguments. With --check it also verifies that the document shows every figure.
"""
import argparse
from pathlib import Path

DOC = Path(__file__).resolve().parent.parent / "inference-cost.md"

# AWS Price List API, us-east-1, USD
RATE = {
    "bedrock_in_1k": 0.00033,     # Nova 2 Lite input tokens, FY8T82UUN7VZR55K
    "bedrock_out_1k": 0.00275,    # Nova 2 Lite output tokens, DY69Q8C3F88CHA2Q
    "rekognition": 0.001,         # DetectLabels per image to 1 million, 4R796AUWKTWNVC3X
    "lambda_request": 0.0000002,  # GU2ZS9HVP6QTQ7KE
    "lambda_gb_s": 0.0000166667,  # x86, TG3M4CAGBA3NYQBH
    "sqs_request": 0.0000004,     # standard, 8RN6B8U4MERHRXP3
    "event": 0.000001,            # custom event, ZA92ERYNKX457AJD
    "ddb_write": 0.000000625,     # on-demand write unit, FGXVD96DKJMUASY3
    "ddb_read": 0.000000125,      # on-demand read unit, 4W4ZMC46EHE8XTTZ
    "s3_get": 0.0000004,          # GET, ZWQ6Q48CRJXX4FXE
    "s3_put": 0.000005,           # PUT, E9YHNFENF4XQBZR6
}

# Planning profile of one vision call, from the inference design
IMAGE_TOKENS = 230      # flat billing per image in Nova 2
TEXT_IN_TOKENS = 50
OUT_TOKENS = 240
SECONDS_PER_IMAGE = 5   # filter, model call and result write inside the function
MEMORY_GB = 0.25        # 256 MB, the module default

# Telemetry batch
TELEMETRY_SECONDS = 1
RANGE_QUERIES_PER_READING = 8
RANGE_QUERY_READ_UNITS = 0.5

# Harvest estimation orthomosaic, one run per mission
ORTHO_SECONDS = 300
ORTHO_GB = 4
TILES_PER_MISSION = 100

# Volumes. A message is one function invocation that completes.
VOLUMES = {
    "harvest": {
        "focus": (60, 50),          # missions, photos each
        "verification": (25, 20),
        "estimation": (50, 100),    # 200 a harvest over four months
        "telemetry": (5760, 108000),  # objects, readings. Two streams, 96 windows of 900 s a day, 30 days
    },
    "normal": {
        "focus": (15, 50),          # 10 confirmations and half again in discarded attempts
        "verification": (6, 20),
        "estimation": (0, 100),
        "telemetry": (5760, 50400),
    },
}
NAMES = {"focus": "Focus confirmation", "verification": "Verification",
         "estimation": "Harvest estimation", "telemetry": "Telemetry batch"}


def per_image():
    model = (IMAGE_TOKENS + TEXT_IN_TOKENS) * RATE["bedrock_in_1k"] / 1000 + OUT_TOKENS * RATE["bedrock_out_1k"] / 1000
    compute = SECONDS_PER_IMAGE * MEMORY_GB * RATE["lambda_gb_s"]
    other = RATE["s3_get"] + RATE["ddb_write"]
    return {"Person filter": RATE["rekognition"], "Model call": model, "Function time": compute,
            "Object read and result write": other}


def per_message(kind, readings_per_object=0.0):
    # Every message: the event that starts it, the queue send, receive and delete, and one Lambda request.
    base = RATE["lambda_request"] + 3 * RATE["sqs_request"]
    if kind == "telemetry":
        # The S3 event reaches EventBridge as an AWS service event, which is not billed.
        compute = TELEMETRY_SECONDS * MEMORY_GB * RATE["lambda_gb_s"]
        writes = readings_per_object * RATE["ddb_write"]
        reads = readings_per_object * RANGE_QUERIES_PER_READING * RANGE_QUERY_READ_UNITS * RATE["ddb_read"]
        return base + compute + writes + reads + RATE["s3_get"]
    cost = base + 2 * RATE["event"]  # flight record published, and the completion event
    if kind == "estimation":
        cost += ORTHO_SECONDS * ORTHO_GB * RATE["lambda_gb_s"] + (TILES_PER_MISSION + 1) * RATE["s3_put"]
    return cost


def month(name):
    img = sum(per_image().values())
    rows = []
    for kind, (msgs, units) in VOLUMES[name].items():
        if kind == "telemetry":
            per_msg = per_message(kind, units / msgs)
            images = 0
            cost = msgs * per_msg
        else:
            images = msgs * units
            per_msg = per_message(kind) + units * img
            cost = msgs * per_msg
        rows.append((kind, msgs, images, per_msg, cost))
    return rows


def fmt(x, d=2):
    return f"{x:,.{d}f}"


def render():
    out = []
    img = per_image()
    total_img = sum(img.values())
    out.append("| Part of one image | USD |")
    out.append("|---|---:|")
    for k, v in img.items():
        out.append(f"| {k} | {v:.7f} |")
    out.append(f"| One image | {total_img:.7f} |")
    out.append(f"| 1,000 images | {fmt(total_img * 1000, 4)} |")
    for name, label in (("harvest", "Harvest month"), ("normal", "Normal month")):
        rows = month(name)
        out.append("")
        out.append(f"| {label} | Invocations | Images | USD per 1,000 invocations | USD in the month |")
        out.append("|---|---:|---:|---:|---:|")
        for kind, msgs, images, per_msg, cost in rows:
            out.append(f"| {NAMES[kind]} | {msgs:,} | {images:,} | {fmt(per_msg * 1000)} | {fmt(cost)} |")
        inv = sum(r[1] for r in rows)
        images = sum(r[2] for r in rows)
        cost = sum(r[4] for r in rows)
        vision = sum(r[4] for r in rows if r[0] != "telemetry")
        out.append(f"| Total | {inv:,} | {images:,} | {fmt(cost / inv * 1000)} | {fmt(cost)} |")
        if images:
            out.append(f"| Vision functions per 1,000 images | | | {fmt(vision / images * 1000, 4)} | |")
    est_msgs, est_units = 200, 100
    harvest = month("harvest")
    average = sum(r[4] for r in harvest)
    peak = sum(r[4] for r in harvest if r[0] != "estimation") + est_msgs * (per_message("estimation") + est_units * total_img)
    out.append("")
    out.append("| Harvest month | USD in the month |")
    out.append("|---|---:|")
    out.append(f"| Estimation flights spread over four months, 50 in the month | {fmt(average)} |")
    out.append(f"| All 200 estimation flights in one month | {fmt(peak)} |")
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = render()
    print(text)
    if args.check:
        doc = DOC.read_text()
        missing = [line for line in text.splitlines() if line.startswith("| ") and line not in doc]
        if missing:
            raise SystemExit("inference-cost.md does not show:\n" + "\n".join(missing))
        print("OK the document shows every figure")


if __name__ == "__main__":
    main()
