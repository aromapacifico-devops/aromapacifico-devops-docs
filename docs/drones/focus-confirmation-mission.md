# Focus confirmation mission

A case asks the drone service to look at one focus, the area around the node whose reading raised an alert. This document defines that mission, what it carries, what it must bring back, and the chain of identifiers that links the case to the mission, the mission to each object, and each object to a result with its confidence, its time and its origin. A confirmed focus is evidence for a person, and it never authorizes a fumigation.

## Contents

1. Terms
2. Context and volumes
3. From case to result
4. The mission
5. What the flight brings back
6. The result and its confidence
7. The decision of the reviewer
8. Fumigation stays outside
9. What fails and what the platform does
10. Cost
11. Assumptions and pending confirmations
12. Sources

## 1. Terms

| Term | Meaning in this document |
|---|---|
| Focus | The circle of 50 m around the node, cut to the published lot polygon and outside no-fly zones |
| Mission | The planned confirmation flight for one case and one attempt |
| Execution | One flight of one mission package. A repeated flight is a new execution |
| Object | One file the flight brings back, a photo or the flight log, stored as a version in S3 |
| Result | What the managed model says about one photo, with its confidence |
| Confidence | The support the model reports for its label, between 0 and 1, which is no probability of a pest and no permission to act |
| Reviewer | The drone supervisor who confirms or discards the focus |

## 2. Context and volumes

The [alert to drone confirmation](../iot/alert-to-drone-confirmation.md) opens the case, builds the focus and emits `confirmation.requested`. The [drone mission link](../network/drone-mission-link.md) signs the package, carries it to the drone, and brings the evidence back until it publishes `flight.record.published`. The [lot boundaries](lot-boundaries-and-exclusions.md) give the polygon and the zones. This document fills the space between them, the confirmation mission itself and its result.

| Figure | Value | Origin |
|---|---|---|
| Confirmed foci in a harvest month | About 40 | Operating mode |
| Confirmation missions in a harvest month | About 60, counting the foci that end discarded | Alert to drone confirmation |
| Area of one focus | Up to 0.79 ha | Circle of 50 m |
| Photos of one confirmation | About 50 | Assumption, to measure on the first flights |
| Photos of confirmation in a harvest month | About 3,000 | 60 missions of 50 photos |
| Validity of a package with no spraying | 72 hours at most, inside its window | Mission link |

## 3. From case to result

Each link of the chain carries the identifier of the link before it, its own time in UTC and its own origin. A reviewer, an auditor or a later fumigation order can walk the chain in either direction.

| Link | Identifier | Time | Origin it points to |
|---|---|---|---|
| Reading | `node_id`, `measured_at` and `seq` | `measured_at`, `received_at` | The farm node and its certificate |
| Alert | `alert_id` | `raised_at` | The reading and the range version |
| Case | `case_id` | `opened_at` | The alert, or a symptom reported by the farmer |
| Focus | `case_id` and `focus_version` | `focused_at` | The node position, the radius, the polygon version and the zone versions |
| Mission | `mission_id`, `attempt` and `mission_revision` | `requested_at` | The case and the focus version |
| Execution | `mission_execution_id` | Takeoff and landing times | The package digest and the station that loaded it |
| Object | S3 key, version and SHA-256 | `captured_at`, `persisted_at` | The execution and the signed result manifest |
| Result | `result_id` | `evaluated_at` | The object version, the model and the prompt version |
| Decision | `case_id`, `attempt` and `review_revision` | `reviewed_at` | The results and the reviewer |

## 4. The mission

The mission service receives `confirmation.requested` and creates the mission with a conditional write keyed on the case, the attempt and the focus version, so a repeated request returns the same mission. It then builds the package that the mission link signs.

| Part | Content |
|---|---|
| Type | `FOCUS_CONFIRMATION`, precision mode, no spraying payload |
| Area | The focus polygon of the case, with its version and SHA-256 |
| Limits | The lot polygon version and every no-fly zone version that touches the focus |
| Window | A UTC window agreed with the brigade schedule, within the 72 hours of a package with no spraying |
| Capture | Photos over the whole focus area at a height and overlap the certified operator plans, below the 122 m of RAC 100, close enough to show leaves |
| Expected objects | The flight log and the photos of the focus, all mandatory |
| Lineage | `case_id`, `alert_id`, `focus_version` and `attempt` |

Example of the mission record, with invented identifiers.

```json
{
  "schema_version": "1.0",
  "mission_id": "mission-demo-0042",
  "mission_type": "FOCUS_CONFIRMATION",
  "mission_revision": 1,
  "case_id": "case-demo-0088",
  "alert_id": "alert-demo-0098",
  "attempt": 1,
  "farm_id": "farm-demo-001",
  "lot_id": "lot-demo-a",
  "focus_version": 2,
  "geometry_version": 7,
  "zone_versions": [{"zone_id": "zone-demo-01", "version": 3}],
  "requested_at": "2026-11-09T14:05:00Z",
  "execution_window": {"not_before": "2026-11-10T11:00:00Z", "not_after": "2026-11-10T17:00:00Z"},
  "expected_objects": [
    {"object_id": "flight-log", "media_type": "application/json", "mandatory": true},
    {"object_id": "focus-photos", "media_type": "image/jpeg", "mandatory": true}
  ],
  "status": "requested"
}
```

A change of the window, the brigade or the expected objects before the flight raises `mission_revision`, and the old package can no longer launch. A change of the focus or of the polygon makes the mission stale, and the case builds a new attempt. Preload, the two acknowledgements, the flight with no connection and the upload follow the mission link with no change.

## 5. What the flight brings back

The flight is complete when the mission link publishes its record, which happens only after every mandatory object is stored and its hash matches. A photo that arrives alone, or an upload that answers with success, does not move the case.

| Field of each object | Meaning |
|---|---|
| `object_id` | Identifier inside the execution |
| S3 key and `version_id` | Where the object lives, encrypted and versioned |
| `sha256`, size | Content, checked against the signed result manifest |
| `captured_at` | Time the drone took it |
| `persisted_at` | Time the platform verified it |
| `mission_execution_id`, package digest, station | The flight that produced it |

A flight that ended aborted or partial is stored as it happened. Its photos can still be reviewed, and the case decides whether another attempt is needed.

## 6. The result and its confidence

After `flight.record.published`, the inference function takes each photo of the focus. It screens the photo for people first, and a photo with a person goes to the restricted prefix and never reaches the model. A clean photo goes to the managed model with a versioned prompt, and the function stores one result for each photo version. The result uses the common envelope and idempotency rule of the [inference functions](../architecture/inference-functions.md).

```json
{
  "schema_version": "1.0",
  "result_id": "result-demo-focus-0092",
  "function": "focus_confirmation",
  "subject": {
    "case_id": "case-demo-0088",
    "mission_execution_id": "mission-exec-demo-0042-01",
    "flight_record_id": "flight-record-demo-0042-01"
  },
  "source_objects": [
    {
      "bucket": "fnc-aroma-test-s3-flights",
      "key": "focus/case-demo-0088/exec-01/flight-record.json",
      "version_id": "v-demo-record-1",
      "sha256": "614280bb1169bfba11816a800648bb766cf9db52e594c6b5dc7e40106b4d4165",
      "role": "flight_record"
    },
    {
      "bucket": "fnc-aroma-test-s3-flights",
      "key": "focus/case-demo-0088/exec-01/photo-017.jpg",
      "version_id": "v-demo-1",
      "sha256": "8bcdb32c706ec233580607c1c4667738f62e52756c587aa877000c2231d6a2ae",
      "role": "photo"
    }
  ],
  "evaluated_at": "2026-11-10T19:43:20Z",
  "confidence": 0.87,
  "model_id": "us.amazon.nova-2-lite-v1:0",
  "prompt_version": 3,
  "idempotency_key": "938d981712c5a1888cd27d4171d03f55d3d42ce1ddccdb9cbc8905328f10834d",
  "result": {
    "label": "possible_focus",
    "review_status": "pending"
  }
}
```

| Field | Rule |
|---|---|
| `label` | `possible_focus`, `no_focus_seen` or `unusable_image` |
| `confidence` | Between 0 and 1, as the model reports it. Until the agronomy review calibrates it against field checks, it orders the photos for the reviewer and decides nothing |
| `model_id`, `prompt_version` | Pinned in configuration, so a change of model or prompt is visible in every result |
| `evaluated_at` | Time of the inference, apart from the capture and storage times |
| `source_objects` | The published flight record and the exact photo version, each with bucket, key, version and SHA-256 |
| `review_status` | `pending` until the reviewer decides |
| Idempotency | Function, subject, source versions, model and prompt version, so a repeat returns the stored result |

The case moves to review when every photo has a result or is restricted, or when inference failed three times and the reviewer works from the photos alone.

## 7. The decision of the reviewer

The reviewer sees the focus on the map, the photos sorted by confidence, the results and the flight record, and decides.

| Decision | Effect on the case |
|---|---|
| `confirmed` | The focus is confirmed. A supervisor may create a fumigation order |
| `discarded` | The case closes. A later alert opens a new case |
| `inconclusive` | A new attempt, with a new execution and the earlier evidence kept |

The decision records the reviewer, the time, the results and objects it rests on, and a reason. A correction is a new review revision, and the earlier one stays.

## 8. Fumigation stays outside

A confirmed focus only allows a supervisor to start a fumigation order. That order needs its own fields, the closed log of this confirmation flight, a named supervisor with a second factor who is not the pilot, and the treated area that the lot boundaries compute. No event, function, label, confidence, upload or state of this mission can create, release or authorize an order, and no function role can write a reviewer decision.

## 9. What fails and what the platform does

| Situation | What the platform does |
|---|---|
| The same request arrives twice | The same mission returns |
| No brigade or drone is free in the window | The mission waits with a new window, and nothing claims a flight |
| The focus or the polygon changes before the flight | The mission is stale, and the case builds a new attempt |
| The package expires before the flight | The station blocks the launch, and a new revision is issued |
| The flight lands and its log is not published | The case waits, and no photo is evaluated |
| A mandatory photo is missing | The mission link keeps the record incomplete, and the station uploads again |
| A photo shows a person | Restricted prefix, no inference, and the reviewer sees that it was withheld |
| The model fails three times | Dead letter queue and alarm, and the reviewer decides from the photos |
| The confidence is high | The result waits for the reviewer like any other |
| The reviewer finds it inconclusive | A new attempt, with the earlier evidence kept |

## 10. Cost

| Item | Rate | Harvest month | USD |
|---|---|---|---|
| Person filter and inference | About 1.75 per 1,000 images | About 3,000 photos | About 5.25 |
| Storage of new photos | 0.023 per GB-month | About 8.8 GB at 3 MB a photo | About 0.20 |
| Mission and result records | 0.625 per million write request units | A few thousand writes | Below 0.01 |

These photos are part of the 9,000 images a month of the operating mode, so the platform cost already counts them in its inference and storage lines. The flights belong to the drone service cost.

## 11. Assumptions and pending confirmations

| Item | Who confirms | Effect if it fails |
|---|---|---|
| About 50 photos cover one focus | Brigades, on the first flights | Inference and storage cost scale with the real count |
| The capture height shows leaves well enough for the model and the reviewer | Certified operator and agronomy review | The height and the photo count change |
| The labels and the meaning of confidence | Agronomy review against field checks | Until then confidence only sorts photos |
| A brigade reaches a focus within the 72 hours of a package | Federation, with the brigade schedule | Packages are reissued more often |

## 12. Sources

- Aerocivil, [RAC 100](https://www.aerocivil.gov.co/documentos/254/reglamentos-aeronauticos-de-colombia-rac/), height limit of 122 m above ground.
- AWS Price List API, [S3](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonS3/current/us-east-1/index.json) and [DynamoDB](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonDynamoDB/current/us-east-1/index.json), us-east-1, and the managed inference cost of the platform.
- [Alert to drone confirmation](../iot/alert-to-drone-confirmation.md), [drone mission link](../network/drone-mission-link.md), [lot boundaries and exclusion zones](lot-boundaries-and-exclusions.md), [drone operating mode](operating-mode.md), [managed inference decision](../adr/managed-inference.md) and [flight log decision](../adr/flight-log-and-fumigation.md) of this platform.
