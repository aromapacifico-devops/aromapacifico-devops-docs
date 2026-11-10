# Alert ranges

The Federation sets the ranges that turn a reading into an alert, and it changes them from the platform with no visit to a farm and no firmware update. This document defines the initial ranges and the sensor each one applies to, how a range is stored as an immutable version, which version judges each reading, how a change is published, reviewed and audited, and what happens when a range is missing or wrong.

## Contents

1. Terms
2. Context and volumes
3. Initial ranges
4. Kinds of range
5. Ranges table
6. Which version judges a reading
7. Publishing a change
8. What fails and what the platform does
9. Infrastructure code
10. Cost
11. Assumptions and pending confirmations
12. Sources

## 1. Terms

| Term | Meaning in this document |
|---|---|
| Range | The limits of one variable in one zone type, cultivation or drying |
| Version | One immutable set of limits for a range, with the time from which it applies |
| Alert range | Limits outside which a reading raises an alert |
| Recommended range | Limits shown to the farmer as guidance, which raise no alert |
| Reference | A target value shown to a person, such as grain humidity near 12 percent, which raises no alert and closes nothing |
| Evaluation | The comparison of one reading with the version that applies to it |
| Measured time | `measured_at`, the time the node took the reading |

## 2. Context and volumes

The node measures and publishes, and the platform decides. The [sensors and operation](sensors-and-operation.md) document lists the variables, the [telemetry ingestion](telemetry-ingestion.md) document stores each reading once and evaluates it, and the [audit design](../security/audit.md) records every change of a range. A node holds no range, so a change reaches the next evaluation with no visit.

| Figure | Value | Origin |
|---|---|---|
| Cultivation readings | 1,200 a day, 200 farms every 4 hours | Sensors and operation |
| Drying readings in harvest | 2,400 a day, 100 farms every hour | Sensors and operation |
| Evaluations in a harvest month | About 108,000 readings, each with up to 8 variables | 3,600 a day for 30 days |
| Ranges | 7 at the start, in 2 zone types | Section 3 |
| Changes of a range | A few a year, by the Federation | Assumption |

A reading can arrive up to 24 hours late, when a node drains its buffer. That is the main reason ranges are versioned by time.

## 3. Initial ranges

The pilot gives the ranges below. The text says humidity and temperature without naming soil or air, and the node measures both. The design binds each range to one field of the message.

| Zone | Variable, message field | Kind | Initial limits |
|---|---|---|---|
| Cultivation | Soil pH, `ph` | Alert range | Outside 4.5 to 6.0 |
| Cultivation | Soil pH, `ph` | Recommended range | 4.9 to 5.6 |
| Cultivation | Soil humidity, `soil_humidity_pct` | Alert range | Outside 40 to 80 percent |
| Cultivation | Air temperature, `air_temp_c` | Alert range | Outside 14 to 30 °C |
| Cultivation | Air temperature, `air_temp_c` | Recommended range | 17 to 23 °C |
| Cultivation | Nitrogen, phosphorus and potassium, `n_mg_kg`, `p_mg_kg`, `k_mg_kg` | Alert range | None until the Federation publishes them |
| Cultivation | Air humidity, `air_humidity_pct`, and soil temperature, `soil_temp_c` | None | Stored and shown, with no alert |
| Drying | Grain temperature, `grain_temp_c` | Alert range | Above 40 °C |
| Drying | Grain humidity, `grain_humidity_pct` | Reference | Near 12 percent |

Temperature goes to the air because the published climate of the coffee zone is an air temperature. Cenicafé describes a mean of 18 to 22.5 °C for the zone, close to the recommended 17 to 23 °C. Humidity goes to the soil because the same source gives a mean air relative humidity of 70 to 85 percent, so an upper limit of 80 percent on the air would raise alerts on ordinary days. The Federation confirms both bindings, and a change is a new version of the range.

pH comes from the soil probe every 4 hours, and a manual reading entered in the application is the fallback when the probe fails. The reading keeps its source, so a manual value is always identifiable.

Nitrogen, phosphorus and potassium have no range until the Federation publishes one with its unit. Their readings are stored and shown, and the platform records that no range applies, which differs from a range of zero.

## 4. Kinds of range

| Kind | Fields | Raises an alert |
|---|---|---|
| Alert range | `min`, `max`, each optional, with whether each limit is included | Yes, when the value falls outside |
| Recommended range | `min`, `max` | No. The application shows the value as outside the recommendation |
| Reference | `target`, and a tolerance once the Federation defines one | No. It never closes a drying lot, which stays a decision of the farmer |

Grain temperature above 40 °C is an alert range with `max` 40 excluded, so exactly 40.0 °C raises nothing. Grain humidity near 12 percent has no tolerance in the pilot definition, so the platform shows the value and the target and decides nothing.

## 5. Ranges table

The ranges table keeps every version. Its partition key stays `zone_type`, and its sort key becomes `variable#valid_from`, so the versions of one variable sort by time.

| Attribute | Meaning |
|---|---|
| `zone_type` | `cultivation` or `drying`, partition key |
| `variable#valid_from` | Message field and the UTC time from which the version applies, sort key |
| `kind` | `alert`, `recommended` or `reference` |
| `min`, `max`, `min_included`, `max_included` | Limits of a range |
| `target`, `tolerance` | Value of a reference, with the tolerance empty until defined |
| `unit` | Unit of the field, matched against the message contract |
| `version` | Integer that grows by one for each version of the variable and kind |
| `reason` | Why the version exists |
| `published_by` | Cognito subject of the platform operator who published it |
| `published_at` | UTC time of publication |
| `reverts_to` | Version copied by a rollback, empty otherwise |

Example of one version.

```json
{
  "zone_type": "cultivation",
  "variable#valid_from": "ph#2026-11-10T00:00:00Z",
  "kind": "alert",
  "min": 4.5,
  "min_included": true,
  "max": 6.0,
  "max_included": true,
  "unit": "pH",
  "version": 1,
  "reason": "Initial range of the pilot",
  "published_by": "8a7b6c5d-4e3f-4a2b-9c1d-0e9f8a7b6c51",
  "published_at": "2026-11-09T15:30:00Z",
  "reverts_to": null
}
```

Ranges apply to the whole Federation, one set for each zone type. Ranges for one farm or one lot would add a scope to the key and are left for after the pilot.

## 6. Which version judges a reading

A reading is judged by the version in force at its measured time, never at its arrival. The evaluation queries the partition of the zone type for the sort keys of the variable up to `variable#measured_at`, newest first, and takes one item. A reading drained hours later therefore gets the same result it would have had on time.

| Situation | Result | Effect on the alert |
|---|---|---|
| A version applies | `in_range`, `out_of_range`, or the recommendation or reference shown | An alert only for `out_of_range` on an alert range |
| No version applies | `no_range` | No alert. The reading is stored, and a metric shows the gap |
| The version is invalid | `invalid_range` | No alert, the message goes to the dead letter queue, and an alarm fires |
| The reading is a duplicate | The earlier result | Nothing changes |
| The reading is late and newer than the alert state | Judged by its own version and marked late | The alert state moves, and the alert carries both times |
| The reading is late and older than the alert state | Judged and kept as history | The current alert does not change |
| The reading is more than 5 minutes in the future | `clock_fault` | No alert, as ingestion already defines |

Each evaluation stores the `version` it used next to the reading. The alert state changes with a conditional write only when the reading is newer than the one that set it, as the ingestion design defines. A change of range never re-judges past readings. A re-evaluation is an explicit command with a reason, and it writes a new evaluation next to the original.

## 7. Publishing a change

Only the platform operator publishes a range, through the platform API, signed in with Cognito and a second factor. A device identity cannot reach this API.

1. The operator enters the new limits, the time from which they apply and the reason.
2. The function validates the change with the rules below.
3. A conditional write creates the new item, which fails if a version with the same `valid_from` exists.
4. The function writes the `threshold.changed` event of the audit design, with the zone type, the variable, the limits before and after, and the reason.

| Rule | On failure |
|---|---|
| The variable and its unit exist in the message contract | Rejected |
| Limits are finite numbers, and `min` is below `max` | Rejected |
| `valid_from` is UTC and no earlier than the time of publication | Rejected, so history never changes |
| A recommended range or a reference carries no alert behavior | Rejected |
| A reference for grain humidity carries no closing action | Rejected |
| The reason is present | Rejected |

A rollback publishes a new version that copies the limits of an older one and fills `reverts_to`. No version is ever edited or deleted, and versions are kept for five years with the rest of the audit evidence. The evaluation function caches the versions of a zone type for one minute, so a change applies to readings measured after its `valid_from` within a minute of publication.

A write on the table that does not come from the platform function still leaves a CloudTrail data event, which the audit design compares with the `threshold.changed` events.

## 8. What fails and what the platform does

| Situation | What the platform does |
|---|---|
| pH 6.2 against the alert range of 4.5 to 6.0 | One `out_of_range` evaluation with its version, and one alert |
| pH 4.7 | Inside the alert range and outside the recommendation. The application shows it, and no alert is raised |
| Grain at 40.1 °C | One drying alert. At 40.0 °C nothing is raised |
| Grain humidity at 12 percent | The value and the target are shown, and the lot stays open until the farmer closes it |
| Nitrogen has no published range | `no_range`, the reading is stored, and the gap metric grows |
| The same reading arrives twice | One evaluation and one alert effect |
| A drained reading arrives after a change of range | The version in force at its measured time judges it |
| An older reading arrives after a newer one | It is kept as history, and the alert does not change |
| The operator rolls back a change | A new version with the old limits, its reason and `reverts_to` |
| A change has bad limits or an unknown unit | Rejected, and the current version stays |
| The ranges table cannot be read | The function retries, then the message goes to the dead letter queue with an alarm. Nothing is judged with a guessed value |

## 9. Infrastructure code

The telemetry ingestion module creates the ranges table with the sort key `variable#valid_from` and receives the initial ranges in its `alert_ranges` input, which it writes as version 1 of each range. Later versions come only through the platform API, so a new `terraform apply` never overwrites a range the Federation changed. The audit design already names the table in its CloudTrail selector.

## 10. Cost

Rates come from the AWS Price List API for us-east-1.

| Item | Rate | Harvest month | USD |
|---|---|---|---|
| Version reads by the evaluation | 0.125 per million read request units | About 108,000 queries, fewer with the one-minute cache | Below 0.02 |
| Version writes | 0.625 per million write request units | A few a year | Below 0.01 |
| Storage | 0.25 per GB-month beyond the free 25 GB | A few kilobytes | 0.00 |

The ranges add nothing visible to the platform cost, whose telemetry line already includes the evaluation.

## 11. Assumptions and pending confirmations

| Item | Who confirms | Effect if it fails |
|---|---|---|
| Crop humidity applies to the soil and crop temperature to the air | Federation | A new version binds the range to the other field |
| Nitrogen, phosphorus and potassium ranges and units | Federation | Until then those readings raise no alert |
| A tolerance for grain humidity near 12 percent | Federation | Until then the platform only shows value and target |
| One set of ranges for the whole Federation is enough for the pilot | Federation | Ranges by farm or lot add a scope to the key |
| Ranges change a few times a year | Federation | Nothing changes in the design, only the count of versions |

## 12. Sources

- Cenicafé, [the climate of the coffee zone](https://publicaciones.cenicafe.org/index.php/avances_tecnicos/article/view/2164), for the mean air temperature and air relative humidity of the zone.
- AWS Price List API, [DynamoDB](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonDynamoDB/current/us-east-1/index.json), us-east-1.
- [Sensors and operation](sensors-and-operation.md), [telemetry ingestion](telemetry-ingestion.md), [pH measurement decision](../adr/ph-measurement.md), [audit of sensitive events](../security/audit.md) and [identity and access](../security/identity-and-access.md) of this platform.
