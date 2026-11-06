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
| Issued code | A code the platform has drawn and printed, not yet attached to a sack |

---

## 1. Context and scope

| Topic | Where it is defined |
|---|---|
| States, transitions, and what happens to an event that does not fit | [Sack states](sack-states.md) |
| Format of the code and the label | [Sack identity](sack-identity.md) |
| How records travel from a phone with no data | [Carrier tracking](../network/carrier-tracking.md) |
| Queue at a center with no WAN | [Collection center LAN](../network/collection-center-lan.md) |

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
| `registered` | `farm_id`, `lot_id`, `weight_kg` |
| `registered_at_center` | `center_id`, `farm_id`, `weight_kg` |
| `handed_to_carrier` | `trip_id` |
| `arrived_at_center` | `trip_id`, `center_id` |
| `received_accepted` | `center_id`, `weight_kg` |
| `received_rejected` | `center_id`, `reason` |
| `reception_corrected_to_accepted` | `center_id`, `reason` |
| `reception_corrected_to_rejected` | `center_id`, `reason` |
| `returned_to_farm` | `center_id`, `reason` |
| `dispatched_to_port` | `center_id`, `carrier_id` |
| `picked_up` | `trip_id`, `center_id` |
| `delivered_accepted` | `trip_id`, `received_by` |
| `delivered_rejected` | `trip_id`, `received_by`, `reason` |
| `reweighed` | `weight_kg` |
| `label_reprinted` | `center_id` |
| `reported_missing` | `trip_id`, `note` |

The five facts the pilot names map to these events. Registration with weight and identifier is `registered`, the handover is `handed_to_carrier`, arrival is `arrived_at_center` with its reception decision, departure is `dispatched_to_port` with `picked_up`, and delivery is `delivered_accepted` or `delivered_rejected`.

`weight_kg` repeats at reception because the center weighs the sack, and a difference from the farm reads as a fact of the history. The design of the center operation defines the values of `reason`.

## 5. Responsible person and evidence

Each event names one responsible person, taken from the token and never from the body of the request. `captured_by` must match `recorded_by`, so a queue can only be sent by the person who captured it. This rule comes from the carrier application, which refuses a sign-in by anyone else while a queue is pending.

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
