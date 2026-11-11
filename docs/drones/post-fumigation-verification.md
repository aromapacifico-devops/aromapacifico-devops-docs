# Verification after fumigation

An applied fumigation stays open until a separate drone flight brings back photos of the treated area and those photos are stored and evaluated. This document defines that verification mission, what it captures, how a function decides from the stored photos whether the order can move toward closure, and what happens when the photos never arrive or the function fails. Only the supervisor closes the order, and a failure anywhere before that leaves it open.

## Contents

1. Terms
2. Context and volumes
3. From application to closure
4. The verification mission
5. Photo set or short path
6. What the flight brings back
7. The verification function and its result
8. When inference fails
9. Closure by the supervisor
10. Open and closed states
11. What fails and what the platform does
12. Cost
13. Assumptions and pending confirmations
14. Sources

## 1. Terms

| Term | Meaning in this document |
|---|---|
| Order | The fumigation order of one focus, with its revisions and records |
| Applied area | The treated area of the order, or the part the supervisor recorded as applied when the application was partial |
| Verification mission | The drone flight that photographs the applied area after the application. Each attempt is a new mission execution |
| Attempt | One verification flight with its own package, record and result. A failed attempt leaves the order waiting for the next one |
| Usable photo | A stored photo that shows no person and that the model did not label as unusable |
| Coverage | Usable photos divided by the photos the package planned |
| Closable | The mark the function writes on an attempt when its photos are enough to judge the treatment |
| Verification record | The record on the order that holds the accepted attempt, its result, its source objects and who decided it |

## 2. Context and volumes

The [fumigation order](fumigation-order.md) defines the states, the records and who moves the order, and it reaches `VERIFICATION_PENDING` after the application record is stored or after the supervisor accepts a partial application. The [drone mission link](../network/drone-mission-link.md) signs the package, carries it to the drone and publishes the flight record when every object is stored and its hash matches. The [focus confirmation mission](focus-confirmation-mission.md) evaluates photos the same way before the order exists. This document fills the space between `VERIFICATION_PENDING` and `CLOSED`.

| Figure | Value | Origin |
|---|---|---|
| Verification flights in a harvest month | About 25, one per fumigation order | Operating mode |
| Verification flights outside harvest | About 6 a month | A quarter of the harvest rate, as the drone cost model counts them |
| Applied area of one order | Up to 0.79 ha | A focus circle of 50 m |
| Photos planned for one verification | About 20 | Assumption, to measure on the first flights |
| Photos of verification in a harvest month | About 500 | 25 flights of 20 photos |
| Validity of a package with no spraying | 72 hours at most | Mission link |

## 3. From application to closure

Each link carries the identifier of the link before it, so the closure points back to the photos and the photos point back to the application they judge.

| Link | Identifier | Time | Points to |
|---|---|---|---|
| Application | `execution_id` of the fumigation and its flight record | Start and end of the application | The authorized revision and the closed log |
| Verification request | Order, revision and attempt | `requested_at` | The applied area and the waiting time |
| Mission execution | `execution_id` of the verification | Takeoff and landing | The package digest and the station |
| Object | S3 key, version and SHA-256 | `captured_at`, `persisted_at` | The verification execution and its signed manifest |
| Photo result | `result_id` | `evaluated_at` | The object version, the model and the prompt version |
| Attempt result | Order, revision and attempt | `evaluated_at` | Every photo result of the attempt |
| Verification record | `record_id` on the order | `recorded_at` | The accepted attempt and its source objects |
| Closure | `record_id` on the order | `closed_at` | The verification record and any follow-up order |

## 4. The verification mission

When the order enters `VERIFICATION_PENDING`, the platform emits `verification.requested` and the mission service creates the mission with a conditional write keyed on the order, the revision and the attempt, so a repeated request returns the same mission.

| Part | Content |
|---|---|
| Type | `VERIFICATION`, precision mode, no spraying payload |
| Method | Always a drone flight, for drone and ground applications alike |
| Area | The applied area, with its object version and SHA-256 |
| Limits | The polygon version and every no-fly zone version of the order |
| Window | Opens at the end of the application plus the waiting time the supervisor set, and lasts up to the 72 hours of a package with no spraying |
| Capture | `photo_set` or `short_path`, with the number of planned photos, at a height the certified operator plans below the 122 m of RAC 100 |
| Expected objects | The flight log and the planned photos, all mandatory |
| Lineage | `order_id`, `revision`, `case_id`, the fumigation `execution_id` and `attempt` |

A ground application is verified by a drone too. The brigade that sprayed on foot would otherwise take the photos that close its own work, and a drone flight carries a signed manifest and a closed log that the platform checks the same way for every order. The 25 verification flights a month of the drone cost model already count these flights.

The waiting time depends on the product and the pest, which stay outside the platform design. The supervisor sets it when requesting the verification, and the mission refuses a window that opens earlier. Preload, the two acknowledgements, the flight with no connection and the upload follow the mission link with no change.

## 5. Photo set or short path

A verification is either a set of photos or a short path, and both forms produce still images, so the person filter, the model, the result and the cost per image stay the same as in the confirmation.

| Mode | What the drone does | When the supervisor picks it |
|---|---|---|
| `photo_set` | Photos over the whole applied area, as in the confirmation | Default for a treated focus |
| `short_path` | Photos at fixed spacing along one line across the applied area | A narrow or partial applied area, or a canopy where a line of close photos shows the leaves better |

A short video was considered and discarded. It needs a video person filter and video inference, with other prices and another function, and a line of photos answers the same question with the path the platform already has.

## 6. What the flight brings back

The flight counts only when the mission link publishes its record, which happens after every mandatory object is stored, its SHA-256 matches the signed manifest and its S3 version is recorded. A photo that arrives alone, or an upload that answers with success, does not move the order.

A verification flight that ends aborted, partial or failed is stored as it happened. Its record is published truthfully and does not count as a verification. The order stays in `VERIFICATION_PENDING`, and the platform plans the next attempt with a new package.

## 7. The verification function and its result

`flight.record.published` of a verification mission starts the verification function. It reads only stored, verified object versions. It screens each photo for people first, and a photo with a person goes to the restricted prefix and never reaches the model. A clean photo goes to the managed model with a versioned prompt, and the function stores one result for each photo version.

| Photo label | Meaning |
|---|---|
| `no_active_damage` | No sign of the pest or disease of the order is visible |
| `active_damage` | Signs of the pest or disease remain |
| `unusable_image` | Blurred, dark, out of the applied area or too far from the leaves |

When every photo has a result or is restricted, the function writes one attempt result with these rules.

| Condition | Attempt result |
|---|---|
| Coverage is below 80 percent | Not closable, with the reason `coverage_low`. The order stays open and the platform plans another attempt |
| No usable photo shows active damage | Closable, proposed result `effective` |
| Active damage in more than half of the usable photos | Closable, proposed result `not_effective` |
| Any other mix | Closable, proposed result `partly_effective` |

The confidence of the attempt is the median of the confidences of its usable photos. Until the agronomy review calibrates the labels against field checks, the thresholds and the confidence only order the evidence for the supervisor, and both thresholds live in configuration.

Example of the attempt result, with invented identifiers.

```json
{
  "schema_version": "1.0",
  "order_id": "order-demo-17",
  "revision": 2,
  "attempt": 1,
  "verification_execution_id": "exec-demo-61-1",
  "flight_record_id": "flight-record-demo-61-1",
  "capture_mode": "photo_set",
  "planned_photos": 20,
  "usable_photos": 18,
  "restricted_photos": 0,
  "active_damage_photos": 0,
  "closable": true,
  "reason": null,
  "proposed_result": "effective",
  "confidence": 0.81,
  "model_id": "configured-managed-model",
  "prompt_version": 1,
  "evaluated_at": "2026-11-27T14:52:00Z"
}
```

A closable attempt makes the function emit `verification.result.persisted`. The transition function then writes the verification record and moves the order to `VERIFIED` in one conditional write that names the expected state and revision. If the order changed in between, the write fails, the attempt result stays stored and the state does not move.

| Rule | Why |
|---|---|
| The function persists the photo results and the attempt result before any state change | A crash after inference loses no work, and a repeat returns the stored results |
| Idempotency on the object version, the model and the prompt version | A repeated storage event or a retry produces no second result |
| The function role can write results and request the move to `VERIFIED`, and nothing more | No function can close, reject or authorize an order |

## 8. When inference fails

A failed invocation never changes the order. The source photos stay in the bucket, no result is written, and the order stays in `VERIFICATION_PENDING`. The function retries a failed photo three times, and then the attempt goes to the dead letter queue with an alarm, the same treatment as the confirmation photos.

When an attempt reaches the dead letter queue, the supervisor sees the photos in the review screen and can record the result by hand. That writes a verification record with `decided_by` set to `supervisor`, the reviewer, no confidence and no model, and moves the order to `VERIFIED`. The move is a person's decision after the failure and leaves the failed invocation itself without effect. A model outage therefore never closes an order and never keeps all of them open. If the supervisor finds the photos insufficient, the platform plans another attempt.

## 9. Closure by the supervisor

From `VERIFIED`, only the supervisor of the department, or the named backup, signed in with the second factor, closes the order. The supervisor sees the applied area on the map, the photos sorted by confidence, the results and the flight record.

| Proposed result | Usual closure outcome | Effect on the case |
|---|---|---|
| `effective` | `treated` | The case can close |
| `partly_effective` | `treated_partly`, or `new_order_needed` | A follow-up order covers the rest when needed |
| `not_effective` | `new_order_needed` | The supervisor creates the follow-up order, named in the closure record |

The supervisor can close with an outcome other than the proposed one, and the audit event of the move records the reason code. A partial application cannot close as `treated`, since the order covered only part of the area and the rest already has its own order.

## 10. Open and closed states

An order is closed only in `CLOSED`, `REJECTED` or `CANCELLED`. Once product may have been applied, `CLOSED` is the only end, and the only way into it passes through `VERIFIED`.

| From | To | Who | Trigger | Guard |
|---|---|---|---|---|
| `FLIGHT_RECORD_PERSISTED` | `VERIFICATION_PENDING` | Platform function | `verification.requested` | The verification mission is planned for the applied area |
| `PARTIAL` | `VERIFICATION_PENDING` | Supervisor | `verification.requested` | The supervisor records the part applied, and the rest goes to a new order |
| `VERIFICATION_PENDING` | `VERIFIED` | Platform function | `verification.result.persisted` | The verification flight record is published and the function persisted a closable result for that attempt |
| `VERIFICATION_PENDING` | `VERIFIED` | Supervisor | `verification.reviewed` | The verification flight record is published, inference of that attempt reached the dead letter queue, and the supervisor records the result |
| `VERIFIED` | `CLOSED` | Supervisor | `order.closed` | The supervisor reviews the verification and records the outcome |

`VERIFICATION_PENDING` has no other exit. A missing photo, a failed flight, a failed invocation, a low coverage or a refused write all leave the order there. Every move, allowed or denied, writes a `fumigation.transition` audit event. The full list of 41 moves lives in [`schemas/fumigation-order-transitions.json`](schemas/fumigation-order-transitions.json), and `tools/check_order_states.py` fails when an automated actor can reach `CLOSED`.

```
$ python3 docs/drones/tools/check_order_states.py
OK 17 states, 41 transitions, only people reach AUTHORIZED, CLOSED, REJECTED
```

## 11. What fails and what the platform does

| Situation | What the platform does | State of the order |
|---|---|---|
| The verification request arrives twice | The same mission returns | `VERIFICATION_PENDING` |
| No brigade or drone is free in the window | The mission waits with a new window | `VERIFICATION_PENDING` |
| The package expires before the flight | The station blocks the launch, and a new package is issued | `VERIFICATION_PENDING` |
| The flight lands and the record never reaches the platform | No photo is evaluated, and the dashboard reports the open order by age | `VERIFICATION_PENDING` |
| A mandatory photo is missing or its hash fails | The mission link keeps the record unpublished, and the station uploads again | `VERIFICATION_PENDING` |
| The verification flight aborts or ends partial | The record is stored as it happened, and the platform plans the next attempt | `VERIFICATION_PENDING` |
| A photo shows a person | Restricted prefix, no inference, and the photo counts as unusable | `VERIFICATION_PENDING` until coverage is enough |
| Coverage below 80 percent | Not closable, and another attempt | `VERIFICATION_PENDING` |
| The model fails three times | Dead letter queue and alarm, no state change, and the supervisor may record the result by hand | `VERIFICATION_PENDING` |
| The order changed while the function ran | The conditional write fails, and the result stays stored | Unchanged |
| A function tries to close the order | The transition function refuses it and records a denied event | Unchanged |
| The treatment did not work | The supervisor closes with `new_order_needed` and a follow-up order | `CLOSED`, with a new order open |

The open orders by age in `VERIFICATION_PENDING`, the attempts that reached the dead letter queue and the failed invocations that left the state unchanged are the signals the operational alarms watch.

## 12. Cost

| Item | Rate | Harvest month | USD |
|---|---|---|---|
| Person filter and inference | About 1.75 per 1,000 images | About 500 photos | About 0.88 |
| Storage of new photos | 0.023 per GB-month | About 1.5 GB at 3 MB a photo | About 0.03 for each month kept |
| Mission, result and order writes | 0.625 per million write request units | A few hundred writes | Below 0.01 |

These photos are part of the 9,000 images a month of the operating mode, so the platform cost already counts them. The verification flights belong to the drone service cost.

## 13. Assumptions and pending confirmations

| Item | Who confirms | Effect if it fails |
|---|---|---|
| About 20 photos cover the verification of one treated focus | Brigades, on the first flights | Inference and storage cost scale with the real count |
| The supervisor knows how long to wait before the effect of a treatment is visible | Agronomy review with the operator | Early flights return `not_effective` or low coverage and need repeats |
| 80 percent coverage is enough to judge a treatment | Agronomy review against field checks | The threshold changes in configuration |
| The labels, the two thresholds of the result and the meaning of confidence | Agronomy review against field checks | Until then they only order the evidence for the supervisor |

## 14. Sources

- Aerocivil, [RAC 100](https://www.aerocivil.gov.co/documentos/254/reglamentos-aeronauticos-de-colombia-rac/), height limit of 122 m above ground.
- AWS Price List API, [S3](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonS3/current/us-east-1/index.json) and [DynamoDB](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonDynamoDB/current/us-east-1/index.json), us-east-1, and the managed inference cost of the platform.
- [Fumigation order](fumigation-order.md), [focus confirmation mission](focus-confirmation-mission.md), [drone mission link](../network/drone-mission-link.md), [drone operating mode](operating-mode.md), [drone campaign cost](campaign-cost-estimation.md), [managed inference decision](../adr/managed-inference.md) and [flight log decision](../adr/flight-log-and-fumigation.md) of this platform.
