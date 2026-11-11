# aromapacifico-ingestion 1.1.0, delivery functions log the fields of the delivery objective

This example fills the [application template](../application-template.md) with a release of the ingestion pipeline. The version, the window, the names and the dates are an example.

| Field | Value |
|---|---|
| Kind of change | Low impact |
| Pipeline | Ingestion |
| Functions and versions | Delivery status function and delivery check function, from the versions of release 1.0.0 to new versions published by this release. The ingestion function keeps its version |
| Artifact | `ingestion/delivery-status/1.1.0.zip` and `ingestion/delivery-check/1.1.0.zip` in the artifact bucket, each with the SHA-256 recorded in the release |
| Test deployment | Release 1.1.0 in test, with the validation hook and the smoke test passed |
| Written by | Platform team member |
| On duty during the window | Platform team member |

## What changes

The crop alert delivery objective counts live alerts handed off within 5 minutes of the reading, and it reads that from the logs of the two delivery functions. This release makes both functions write what the count needs.

- The delivery status function writes an entry named `alert_handed_off` for each push handoff, with `alert_id`, `kind`, `link` and `handoff_latency_s`, the seconds from the reading to the handoff.
- The delivery check function writes an entry named `alert_undelivered` for each alert with no handoff after 5 minutes, with `alert_id`, `kind` and `link`.

The alerts table, the messages to the farmer and the SMS rule stay as they are.

## Window

| Field | Value |
|---|---|
| Date | Wednesday, outside a harvest week |
| Start and end, Bogota time | 10:00 to 11:00 |
| Harvest week | No |
| Release pace | Canary of 10 percent for 10 minutes, then all calls |

## Impact

| Field | Value |
|---|---|
| Who notices | Nobody outside the team. The operator gets a delivery indicator that matches the alerts table |
| Expected interruption | None. The `live` alias moves between two versions that both run |
| Data written differently | Two new log entries. The alerts table keeps the same fields, and version 1.0.0 still reads every record |
| Service level objectives affected | Crop alert delivery. Its indicator becomes measurable from the logs after this release |
| Main risk | A delivery status function that fails would stop writing handoffs, so the delivery check would report alerts as undelivered and send SMS to farmers whose push already arrived. The error alarm of the function and the undelivered alert alarm show it |

## Approval

| Field | Value |
|---|---|
| Approver | Platform team member |
| Production run | Production release run of version 1.1.0 in the protected `prod` environment |
| What the approver checked | The change is low impact and the notice went out one working day before, release 1.1.0 passed in test, and the rollback below |

## Notice to the Federation

| Field | Value |
|---|---|
| Sent to | Change contact of the Federation |
| Notice sent | Tuesday, one working day before |
| Summary sent | Wednesday after the window, with the first daily figure of the delivery indicator |

## Rollback

| Field | Value |
|---|---|
| Automatic trigger | The error alarm of any of the three ingestion functions, or a message in the dead letter queue of the ingestion queue, during the canary |
| Manual trigger | An undelivered alert alarm for an alert that the alerts table shows as handed off, within a day of the release |
| Steps | Run the production release workflow with version 1.0.0. It moves the `live` alias of both functions back with the same approval |
| Time to go back | Seconds during the canary, about 2 minutes by hand |
| What does not go back | The log entries already written stay for their 30 days. The previous version ignores them, and the delivery indicator stops counting new alerts until the release goes out again |

## Verification after the change

The saved query of the delivery objective, run over the day after the release, returns a count of live alerts equal to the live alerts of cellular farms in the alerts table for the same day, and a count of bad alerts that matches the slow and undelivered alarms of that day.
