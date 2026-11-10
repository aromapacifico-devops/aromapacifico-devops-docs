"""Monthly cost of the farmer history and of the pilot report.

Rates come from the AWS Price List API for us-east-1. Usage figures are the
assumptions stated in docs/iot/farmer-history.md.
"""

HTTP_API_PER_REQUEST = 1.00 / 1_000_000
LAMBDA_PER_REQUEST = 0.20 / 1_000_000
LAMBDA_ARM_PER_GB_SECOND = 0.0000133334
DYNAMODB_PER_READ_UNIT = 0.125 / 1_000_000
DYNAMODB_PER_WRITE_UNIT = 0.625 / 1_000_000
SHADOW_PER_OPERATION = 1.25 / 1_000_000
DYNAMODB_EXPORT_PER_GB = 0.10
ATHENA_PER_TB = 5.00
STEP_FUNCTIONS_PER_TRANSITION = 0.000025

FARMERS = 200
DAYS = 30
CALLS_PER_OPENING = 2
LAMBDA_MEMORY_GB = 0.25
LAMBDA_SECONDS = 0.15
READ_UNITS_PER_OPENING = 10
DRYING_LOTS_PER_DRYING_FARM = 3
WRITE_UNITS_PER_LOT = 6
SHADOW_OPERATIONS_PER_LOT = 12

TABLES_TO_EXPORT_GB = 0.05
REPORT_QUERIES = 12
GB_SCANNED_PER_QUERY = 0.1
REPORT_TRANSITIONS = 60


def openings(drying_farms):
    others = FARMERS - drying_farms
    return (drying_farms * 4 + others * 2) * DAYS


def application(drying_farms):
    opened = openings(drying_farms)
    calls = opened * CALLS_PER_OPENING
    lots = drying_farms * DRYING_LOTS_PER_DRYING_FARM
    lines = {
        "HTTP API requests": calls * HTTP_API_PER_REQUEST,
        "Lambda requests and duration": calls * LAMBDA_PER_REQUEST
        + calls * LAMBDA_MEMORY_GB * LAMBDA_SECONDS * LAMBDA_ARM_PER_GB_SECOND,
        "DynamoDB reads": opened * READ_UNITS_PER_OPENING * DYNAMODB_PER_READ_UNIT,
        "DynamoDB writes of drying lots": lots * WRITE_UNITS_PER_LOT * DYNAMODB_PER_WRITE_UNIT,
        "Device Shadow operations": lots * SHADOW_OPERATIONS_PER_LOT * SHADOW_PER_OPERATION,
    }
    return opened, calls, lots, lines


def report():
    return {
        "DynamoDB exports": TABLES_TO_EXPORT_GB * DYNAMODB_EXPORT_PER_GB,
        "Athena queries": REPORT_QUERIES * GB_SCANNED_PER_QUERY / 1000 * ATHENA_PER_TB,
        "Step Functions transitions": REPORT_TRANSITIONS * STEP_FUNCTIONS_PER_TRANSITION,
    }


def show(title, lines):
    print(title)
    for name, usd in lines.items():
        print(f"  {name:34} {usd:8.4f}")
    total = sum(lines.values())
    print(f"  {'Total':34} {total:8.4f}")
    return total


if __name__ == "__main__":
    for month, drying in (("Normal month", 20), ("Harvest month", 100)):
        opened, calls, lots, lines = application(drying)
        print(f"{month}: {opened:,} openings, {calls:,} calls, {lots} drying lots")
        app_total = show("  Application", lines)
        report_total = show("  Pilot report", report())
        print(f"  Month total {app_total + report_total:.4f}\n")
