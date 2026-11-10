# Custody chain

A buyer trusts a sack only if each hand it passed through left a record that nobody can change afterwards. This document defines the events of the custody chain, the fields each one carries, how a farm with no data registers a sack, how a repeated or late event stays harmless, and how events are written to the transactional database so that no two writes can corrupt a sack.

## Contents

1. Context and scope
2. Volumes
3. Event format
4. Event catalog
5. Responsible person and evidence
6. Sack code at a farm with no data
7. Idempotency
8. Logical order
9. Tables
10. Write path
11. Immutability
12. Sacks of a trip
13. What fails and what happens
14. Cost
15. Assumptions and pending confirmations

### Terms used

| Term | Meaning in this document |
|---|---|
| Custody | Who holds a sack at a given moment |
| Event | A dated fact about a sack, recorded by one person and never changed |
| Idempotency key | The value that identifies an event, so a repeat is ignored |
| Source | The trip of a carrier or the device of a center, each with its own counter |
| Projection | The current state of a sack, computed from its events and stored for fast reads |
| Version | A counter on the sack that detects two writes at the same moment |
| Issued code | A code the platform has drawn and printed, which no sack uses yet |

---

## 1. Context and scope

| Topic | Where it is defined |
|---|---|
| States, transitions, and what happens to an event that does not fit | [Sack states](sack-states.md) |
| Format of the code and the label | [Sack identity](sack-identity.md) |
| How records travel from a phone with no data | [Carrier tracking](../network/carrier-tracking.md) |
| Queue at a center with no WAN | [Collection center LAN](../network/collection-center-lan.md) |
| Reception, labels for sacks with no code and the reserve of codes at a center | [Collection center operations](../network/collection-center-operations.md) |
| Delivery at the port and its evidence | [Port delivery](../network/port-delivery.md) |

This document supplies the fields, the storage and the write. Recovery and the five-year deletion belong to the designs of recovery and persistence, and the fields each actor reads belong to the design of the views.

## 2. Volumes

| Measure | Value |
|---|---|
| Sacks a harvest month | Up to 36,000 |
| Events of one sack on the normal path | 7 |
| Events a harvest month | Up to 252,000 |
| Sacks a day, one center | Up to 400 |
| Writes on one sack at the same moment, normal case | One |

A sack passes through one pair of hands at a time, so two events rarely land on it at the same moment. A race becomes likely only when a phone returns data while a center works on the same sack.

## 3. Event format

Every event shares one envelope, sent through the endpoints of the carrier and of the center, which answer per record.

```json
{
  "event_id": "5b1f7c1e-8a44-4f7e-9d1b-2c6e0f3a7d21",
  "sack_code": "AP-7K3M-Q29X-TDHB-6",
  "name": "handed_to_carrier",
  "seq": 12,
  "captured_at": "2026-05-14T15:40:00Z",
  "time_source": "fix",
  "captured_by": "user-3c90",
  "location": { "lat": 2.4419, "lon": -76.6063, "accuracy_m": 12 },
  "data": { "trip_id": "c7a0e2b4-6d15-4a8e-b3f2-91d0c4e7a613" }
}
```

| Field | Purpose |
|---|---|
| `event_id` | UUID created at capture, and the idempotency key |
| `sack_code` | The sack this event belongs to |
| `name` | One event of the catalog |
| `seq` | Counter per source, the trip of a carrier or the device of a center |
| `captured_at` | Date and time of the fact |
| `time_source` | `fix`, `corrected` or `device`, which says how far to trust the time |
| `captured_by` | The person signed in on the device at capture |
| `location` | Where it happened, when the device has a fix |
| `data` | Fields of this event, listed in the catalog |

The platform adds three fields that no device can set.

| Field | Purpose |
|---|---|
| `recorded_by` | Identity from the token of the request |
| `received_at` | Time the platform stored the event |
| `outcome` | `applied`, `gap` or `anomaly` at the last replay |

A center uses `POST /centers/{center_id}/events`, and a carrier uses `POST /trips/{trip_id}/events`. A group action, such as scanning 30 sacks, creates 30 events in one request, and each one gets its own answer.

## 4. Event catalog

| Event | Fields in `data` |
|---|---|
| `registered` | `farm_id`, `lot_id`, `weight_kg`, and `drying_lot_id` when the coffee dried under a node |
| `registered_at_center` | `center_id`, `farm_id`, `weight_kg` |
| `handed_to_carrier` | `trip_id` |
| `arrived_at_center` | `trip_id`, `center_id` |
| `received_accepted` | `center_id`, `weight_kg` |
| `received_rejected` | `center_id`, `weight_kg`, `reason_code`, `observation` |
| `reception_corrected_to_accepted` | `center_id`, `reason_code`, `observation` |
| `reception_corrected_to_rejected` | `center_id`, `reason_code`, `observation` |
| `returned_to_farm` | `center_id`, `reason_code`, `observation` |
| `dispatched_to_port` | `center_id`, `carrier_id` |
| `picked_up` | `trip_id`, `center_id` |
| `delivered_accepted` | `trip_id`, `received_by_org`, `receipt_ref` |
| `delivered_rejected` | `trip_id`, `received_by_org`, `receipt_ref`, `reason` |
| `reweighed` | `weight_kg` |
| `label_reprinted` | `center_id`, `reason_code`, `observation` |
| `reported_missing` | `trip_id`, `note` |

`drying_lot_id` links the sack to the drying lot whose summary gives the buyer the drying variables. The application offers the lots of the farm it already holds, so the field works with no connection, and the [farmer history](../iot/farmer-history.md) defines the lot. A sack registered at a center carries no lot.

The five facts the pilot names map to these events. Registration with weight and identifier is `registered`, the handover is `handed_to_carrier`, arrival is `arrived_at_center` with its reception decision, departure is `dispatched_to_port` with `picked_up`, and delivery is `delivered_accepted` or `delivered_rejected`.

`weight_kg` repeats at reception, on an accepted and on a rejected sack, because the center weighs every sack, and a difference from the farm reads as a fact of the history. `reason_code` takes one value from a closed list and `observation` holds free text, so reports can count events by reason. The [collection center operations](../network/collection-center-operations.md) define the lists of codes.

## 5. Responsible person and evidence

Each event names the person who captured it, and the platform checks that person against the token of the request, which the body cannot change.

| Who sends | Rule | Reason |
|---|---|---|
| Carrier | `captured_by` must equal `recorded_by` | A phone belongs to one person, so only that person can send its queue |
| Center operator | `recorded_by` must belong to the same center as `captured_by` | Stations are shared, so a queue from a WAN outage can be sent by the next shift |

The event keeps both identities, so the responsible person stays `captured_by` even when a colleague sends the queue.

A handover rests on a scan by the carrier, with its location and time.

| Option | For | Against | Result |
|---|---|---|---|
| Carrier scan with location | Works with no data on either side, one action, and the place and time support the claim | The farmer does not confirm at that moment | **Chosen** |
| Confirmation by the farmer | Two parties agree | A second step at a farm with no signal, for each sack or for a batch | Discarded |

Each extra step at a farm raises the risk of no record at all. The farmer sees the event in the application once data reaches the phone, and can report a wrong handover then. The arrival at the center, recorded by another person, closes the loop.

## 6. Sack code at a farm with no data

A farm has no printer and may have no data, and the code must exist before the sack leaves, because the handover scans it. The platform therefore issues codes ahead of time.

| Step | Action |
|---|---|
| 1 | The platform draws a block of codes, with a conditional write for each one, and stores them as issued |
| 2 | A center prints the block on label sheets |
| 3 | Sheets reach the farms with people already traveling, such as carriers and field staff |
| 4 | The farmer sticks a label on the sack, scans it and enters the weight, with no connection |
| 5 | The event waits on the phone until data returns |

| Option | For | Against | Result |
|---|---|---|---|
| Pre-printed labels | No printer at the farm, no connection needed, codes known in advance | Label logistics, and unused labels | **Chosen** |
| Code generated on the phone | No logistics | Thirteen symbols written by hand, no QR, frequent errors | Discarded |
| Registration only with data | Nothing new to build | Farm registration stops being real where it matters, and the handover has no code to scan | Discarded |

A sack that arrives with no code still gets one at the center, as the sack identity design defines.

Issuing in advance helps validation. The platform knows every code that exists, so three cases stay apart.

| The code | Means | Result |
|---|---|---|
| Fails its check symbol | Misread or mistyped | Rejected, shown to the person as a task |
| Well-formed and never issued | Forged, or a copying error that passed the check | Stored as an anomaly |
| Issued, with no registration yet | The registration is still on a phone | Stored with a gap, which closes when it arrives |

An unused label costs almost nothing, and a buyer who reads it sees that no sack is registered with that code.

## 7. Idempotency

The idempotency key is `event_id` inside its `sack_code`. The device creates it at capture and stores it with the event, so every repeat carries the same value. A lost answer therefore costs one repeat and no second event. A group action gives each sack its own `event_id`, so a retry after a partial failure repeats only what is missing.

The key lives in the event itself, which keeps it valid for as long as the event exists. A key in a cache with a short life would expire before a phone returns from a long outage.

## 8. Logical order

Events are sorted by `captured_at`, then by the position of the event along the route, then by `seq`. Arrival time plays no part, so any arrival order gives the same history. [Sack states](sack-states.md) defines the replay and the outcome of each event.

`seq` is a counter per source. A carrier counts per trip, and a center counts per device, because a center queues events with no trip. A break in a counter shows that a record is missing from that source.

## 9. Tables

| Table | Key | Holds | Written by |
|---|---|---|---|
| `sack_events` | Partition `sack_code`, sort `event_id` | Every event, unchanged | Domain function, insert only |
| `sacks` | Partition `sack_code` | Current state, version, gaps, farm, current trip and the date from which the sack may be deleted | Domain function |

A code issued and not yet used exists as an item in `sacks` with version 0 and no state.

| Option | For | Against | Result |
|---|---|---|---|
| Two tables | The function can hold no permission to change or delete events | Two tables to create and restore together | **Chosen** |
| One table with item types | One table | Update and delete permissions cover the events too, so only the code protects them | Discarded |

Both tables are DynamoDB tables, the transactional database of the platform. Both must be restored to the same point, since issued codes live only in `sacks`.

## 10. Write path

Each event goes through these steps.

| Step | Action | Reason |
|---|---|---|
| 1 | Read the version of the sack with a strong read | Taken first, so a stale history always fails the condition below |
| 2 | Read the history of the sack with a strong read | The input of the replay |
| 3 | If `event_id` is in the history, answer `repeated` and stop | Avoids a write, and DynamoDB bills a canceled transaction |
| 4 | Replay the history with the new event | Gives the state, the gaps and the anomalies |
| 5 | Write in one transaction, inserting the event if it does not exist and updating the sack if its version is unchanged | Both happen or neither does |
| 6 | If the transaction is canceled, start again, up to three times | Another event landed in between |
| 7 | After three lost races, fail that record | The sender keeps it and retries later |

The version condition carries the whole design. With it, two events racing on a sack cannot overwrite each other, because the second one fails, reads the new history and replays.

This write path ran against DynamoDB Local, a local version of the service, with real transactions and eight threads racing on one sack. Each event was sent twice, in random order, over the eight valid histories of the sack states design.

| Check | Result |
|---|---|
| Sacks | 320 |
| Deliveries | 3,520 |
| Events written | 1,760, each exactly once |
| Repeats answered with no write | 1,760 |
| Transactions lost to a race | 5,198 |
| Records handed back to the sender after three races | 830 |
| Final state equal to the replay, version equal to the event count | Held on all 320 sacks |
| Same test with the version condition removed | 20 of 80 sacks ended with a wrong state, and all 80 with a wrong version |

The contention is deliberately extreme, since a real sack has one writer at a time. The last row shows that the test can fail, and that the condition is what prevents the failure. DynamoDB Local does not reproduce the conflict timing of the service, so a test against the real service remains pending.

## 11. Immutability

The role of the domain function has the fewest permissions that the write path allows.

| Table | Allowed | Absent |
|---|---|---|
| `sack_events` | `PutItem`, `Query` | `UpdateItem`, `DeleteItem` |
| `sacks` | `GetItem`, `UpdateItem` | `DeleteItem` |

No role of the platform can change or delete an event. DynamoDB ties the permissions of a transaction to those of each action inside it, so the transaction needs nothing more.

One limit remains. A policy cannot forbid `PutItem` from replacing an existing item. That protection comes from the condition `attribute_not_exists` on each insert, so it depends on the code of the function. Deployment controls cover that code, and the audit design covers access to the tables.

The five-year deletion runs through a service process and no application role, under the [persistence and archive](../architecture/persistence-and-archive.md) design.

## 12. Sacks of a trip

A center needs to know which sacks come in a trip. `sacks` keeps `current_trip_id`, set by `handed_to_carrier` and `picked_up`, and a sparse index on that field answers the query. The index updates shortly after the write, so a center may see a sack a moment late. A phone with no data delays this list, and the application shows the time of the latest update.

## 13. What fails and what happens

| Failure | Effect | Response |
|---|---|---|
| Lost answer | The sender repeats | Answered as `repeated`, with no write |
| Two events on one sack at the same moment | One transaction is canceled | The function replays and writes again |
| Three lost races | The record fails | The sender retries later, and nothing is lost |
| Function fails after the transaction | The sender gets no answer | The repeat finds the event and answers `repeated` |
| Function fails before the transaction | Nothing was written | The sender repeats |
| Farmer registers after the handover arrives | The sack shows a gap | The registration closes it |
| Label sheet lost | Codes stay unused | No effect on any sack |
| Same label used on two sacks | Second registration of a code | Anomaly, kept for review |
| Forged code | Well-formed and never issued | Anomaly, kept for review |
| Table restored | Recent events may be missing | Devices that got no answer send again, and the recovery design covers the rest |
| Index behind the table | A sack appears late in the trip list | Clears on its own |

## 14. Cost

Calculated from the AWS price list for us-east-1, for 252,000 events and 36,000 issued codes in a harvest month.

| Item | Rate | One request per event, USD | Grouped by truck, USD |
|---|---|---|---|
| API Gateway HTTP API | USD 1.00 per million | 0.25 | 0.01 |
| Lambda at 256 MB, 0.2 s per event or 1 s per group | USD 0.20 per million and USD 0.0000166667 per GB-second | 0.26 | 0.04 |
| DynamoDB transactional writes, 4 units per event | USD 0.625 per million | 0.63 | 0.63 |
| DynamoDB strong reads, 2 units per event | USD 0.125 per million | 0.06 | 0.06 |
| Index on the trip, 2 writes per sack | USD 0.625 per million | 0.05 | 0.05 |
| Issued codes, 1 write each | USD 0.625 per million | 0.02 | 0.02 |
| **Total** | | **About 1.27** | **About 0.81** |

The grouped figure and the positions of the carriers add up to about USD 1.39 in a harvest month, slightly above the USD 1.34 of the line for APIs in the monthly cost of the platform, before counting public queries. The cost analysis settles that line. The difference is a few cents against a total above USD 180, so it changes no decision.

Printing labels uses the printer of each center, and its materials belong to the hardware and fee estimate.

## 15. Assumptions and pending confirmations

| Item | Who confirms | Effect if it fails |
|---|---|---|
| Pre-printed labels can reach farms with people already traveling | Federation | Label logistics needs its own cost and route |
| A test against the real service confirms the behavior seen in DynamoDB Local | First deployment of the application | Retries or the limit of three may need adjusting |
| The center weighs each sack at reception | Center operation | `weight_kg` leaves that event |
| A wrong handover reported later by the farmer is rare | First harvest | A confirmation step may be worth its cost |

## Sources

- Amazon DynamoDB Developer Guide, transactions, and IAM with transactions.
- AWS Price List API for API Gateway, Lambda and DynamoDB in us-east-1.
