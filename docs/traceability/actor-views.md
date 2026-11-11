# Views by actor and query authorization

A sack is read by people with very different rights. The buyer holds only the printed code and should learn the origin, the process dates, the state and the drying of that sack and nothing else. The collection center needs the trip that brings the sack, and the farmer needs the sacks of their own farms. This document sets which field each actor sees, how each view is built and which route serves it, and how the platform keeps personal data out of the buyer view.

## Contents

1. Context
2. Fields by actor
3. The buyer view
4. The center view
5. The farmer and carrier views
6. Routes and authorization
7. What fails and what happens then
8. Cost
9. Assumptions and pending confirmations
10. Sources

### Terms used

| Term | Meaning in this document |
|---|---|
| View | The set of fields one actor receives about a sack |
| Projection | A record computed from the events of a sack and stored for fast reads |
| Allow list | The closed list of fields a view may carry. Anything outside it is left out |
| Buyer view | The view anyone with the code reads, with no account |
| Personal data | Data that identifies a farmer, a carrier or a member of staff, directly or by combination |

---

## 1. Context

The [custody chain](custody-chain.md) stores every event of a sack in `sack_events` and the current state in `sacks`. Each event carries who captured it, where and when, and its own fields, such as the trip, the center, the weight or a rejection reason. The [farmer history](../iot/farmer-history.md) keeps each drying lot with a summary written 24 hours after the drying ends, and a sack links to its lot through `drying_lot_id`. The [sack identity](sack-identity.md) gives every sack a random code that encodes nothing.

| Figure | Value | Source |
|---|---|---|
| Sacks in a harvest month | Up to 36,000 | Custody chain |
| Events in a harvest month | Up to 252,000, seven per sack on the normal path | Custody chain |
| Sacks kept | Up to 720,000 over five years | Sack identity |
| Peak of public reads | 30 a minute, with the firewall limit far above | Identity and access |
| Recovery time of the public query | 4 hours | Recovery |

Most of these records hold personal data. The event envelope names the person who captured it and the place, a trip names the carrier and the vehicle, the farm profile names the owner, and an observation is free text that staff may fill with names. The buyer view therefore takes its fields from an allow list and never from what a record happens to contain.

## 2. Fields by actor

Each row is a field the platform holds about a sack or its journey. Yes means the actor receives it in its view.

| Field | Where it lives | Buyer | Center | Carrier | Farmer |
|---|---|---|---|---|---|
| Sack code | `sacks` | Yes | Yes | Own trip | Own farms |
| Origin, department | Farm profile | Yes | Yes | No | Own farms |
| Origin, municipality and farm name | Farm profile | No | Yes | No | Own farms |
| Farm and lot identifiers | `registered` event | No | Yes | No | Own farms |
| State | `sacks` | Yes | Yes | Own trip | Own farms |
| Date of each process step | Event `captured_at` | Day only | Day and time | Own trip | Day and time |
| Rejection reason from the catalog | `reason_code` | Yes | Yes | No | Own farms |
| Rejection observation, free text | `observation` | No | Yes | No | Own farms |
| Port rejection reason, free text | `delivered_rejected` event | No | Yes | Own trip | Own farms |
| Weight | `weight_kg` | No | Yes | No | Own farms |
| Drying summary | Drying lot | Yes | Yes | No | Own farms |
| Drying readings, hour by hour | Readings table | No | No | No | Own farms, 90 days |
| Trip identifier and state | Trip | No | Yes | Own trip | No |
| Carrier name and vehicle plate | Carrier table, `carrier_id` | No | Trips toward its center | Own | No |
| Carrier positions | Position table | No | Last position, open trips toward its center | Own | No |
| Center that received or dispatched it | Event `center_id` | No | Yes | Own trip | Own farms |
| Receiver at the port and receipt reference | `delivered_*` events | No | Yes | Own trip | No |
| Who captured or recorded each event | `captured_by`, `recorded_by` | No | Staff of its center only | No | No |
| Location of each event | `location` | No | No | Own trip | No |
| Gaps and anomalies | `outcome` | No | Yes | No | No |
| Note of a missing report | `reported_missing` event | No | Yes | Own trip | No |
| Event identifier, sequence, time source and time stored | Event envelope | No | Yes | Own trip | No |
| Drying lot identifier | `registered` event | No | No | No | Own farms |
| Farmer name, national ID, phone, address | Farm profile and user pool | No | No | No | Own |

The drone roles, the platform operator and the Federation analyst read no sack field. The analyst reads only the aggregated files of the pilot report, as the farmer history defines.

The center sees a sack once the sack has passed through it or is on a trip toward it. A sack that never reaches a center is invisible to that center.

## 3. The buyer view

### Content

| Field | Content | Why |
|---|---|---|
| `origin` | Country and department | A department holds about 67 pilot farms, so it names a region and no farmer. A municipality may hold a single pilot farm |
| `state` | One of the seven states of the sack | What the buyer asks first |
| `state_reason` | The catalog code of a rejection at the center, or empty | A reason such as `moisture` is quality information |
| `process_dates` | The day of registration, drying start and end, center reception, dispatch to the port and delivery | Shows the age and the pace of the coffee |
| `drying` | Hours monitored, completeness of readings, highest grain temperature, hours above 40 °C, first and last grain humidity | The drying variables of the lot, with how much of the drying the node saw |

The schema of the view is `schemas/buyer-view.schema.json`, with a sample next to it. Every object in it is closed, so no field outside the list can appear. `tools/check_buyer_view.py` fails when a field outside the allow list, or a name that suggests a farm, a lot, a trip, a person, a place or a free text, enters the schema. It also validates the sample.

```json
{
  "schema_version": 1,
  "sack_code": "AP-7K3M-Q29X-TDHB-6",
  "origin": { "country": "CO", "department": "Cauca" },
  "state": "in_transit_to_port",
  "state_reason": null,
  "process_dates": {
    "registered_on": "2026-05-14",
    "drying_started_on": "2026-05-02",
    "drying_ended_on": "2026-05-09",
    "received_at_center_on": "2026-05-15",
    "dispatched_to_port_on": "2026-05-18"
  },
  "drying": {
    "status": "available",
    "hours_monitored": 175,
    "readings_completeness_pct": 100,
    "grain_temp_max_c": 41.6,
    "hours_above_40c": 2,
    "grain_humidity_first_pct": 52.4,
    "grain_humidity_last_pct": 11.8
  }
}
```

The values are invented for the example.

`drying.status` is `available` once the lot summary exists, `pending` while the drying has ended and the summary is less than a day away, and `not_monitored` for a sack registered at a center or from coffee dried with no node. Completeness is readings received over readings expected, which tells the buyer whether the node watched the whole drying.

### What stays out, and why

| Left out | Why |
|---|---|
| Hours and minutes of each step | The time of a handover or a pickup shows when a carrier works and where they stop. The day is enough to judge the coffee |
| Weight | A weight that differs from the farm weight starts a dispute between the farmer and the center, which the buyer has no part in |
| Center names | They add no quality information and narrow the origin |
| The free text of a rejection or a port refusal | Staff may write names or remarks about a person in it |
| Who handled the sack, the trip and every location | Personal data of carriers and staff |

### How it is built

| Option | For | Against | Result |
|---|---|---|---|
| A separate `buyer_views` table, written with each event | The public function can only read that table, so even a flaw in it cannot reach a farm, a trip or a person | One more table and one more write per event | **Chosen** |
| Filter at read time | No new table | The function that anyone can reach holds read access to every record, and one missed field leaks data | Discarded |
| A buyer map inside `sacks`, limited with the `dynamodb:Attributes` condition of IAM | No new table | Protection rests on a condition list that must name every attribute exactly, and a missing or misspelled name shows up only in testing | Discarded |

The domain function writes the buyer view in the same transaction as the event and the `sacks` item, so the view never disagrees with the state. It builds the view from the allow list, and the schema check runs in the pipeline of the function.

Drying arrives later than the sack in most cases. A sack registered after its lot summary exists copies the summary at registration. When the daily job writes a summary, it finds the sacks of that lot through a sparse index on `drying_lot_id` in `sacks` and updates the drying block of their buyer views.

The view is a projection, so it can always be rebuilt by replaying the events of a sack. Recovery has to restore `buyer_views` with point-in-time recovery to the same second as the two sack tables, and a replay of a sample checks it. That keeps the public query inside its 4 hours. The [recovery](../architecture/recovery.md) design does not list this table yet, and its owners add it.

### Unknown and unused codes

An unknown code and a code printed but never registered receive the same answer, that no sack is registered with that code. A reader cannot tell whether a code was ever issued, which keeps guessing from yielding even that fact.

## 4. The center view

A center works with the sacks it receives and dispatches, and with the trips that bring them.

| A center sees | Detail |
|---|---|
| Sacks | Every event and field of a sack that passed through the center or is on a trip toward it, including weight, reasons and observations |
| Incoming trips | Trip state, sack count, carrier name and vehicle plate, and the last position with its time while the trip is open toward the center |
| People | The staff of its own center who captured events. Carriers by name only |
| Review list | Gaps and anomalies of its sacks, as the sack states define |

| Option for the trip | Result |
|---|---|
| Last position while the trip is open toward the center | **Chosen.** Enough to prepare the reception and to call the carrier when a trip stalls |
| The whole track of the trip | Discarded. The track is personal data of the carrier, and the platform keeps it for claims, where the Federation reads it on request |

A center never sees a track history, positions of a trip toward another center, or any position after the trip closes.

## 5. The farmer and carrier views

The farmer sees every field of the sacks registered from their own farms, from registration until delivery, with dates and times, the center that received each sack, weights, reasons and observations. The observation tells the farmer why a sack came back, which they have a right to know. The farmer sees no trip, carrier or receiver at the port.

The carrier sees the sacks of their own trips while the trip is open and its history afterwards, as the [carrier application contract](carrier-application-contract.md) defines. The carrier sees no farmer data beyond what a handover shows on the label.

## 6. Routes and authorization

| Method and path | API | Who | Check | Reads |
|---|---|---|---|---|
| `GET /public/sacks/{sack_code}` | Function URL behind CloudFront and the firewall | Anyone with the code | Code format and check symbol, firewall rate rule | `buyer_views`, `GetItem` |
| `GET /farms/{farm_id}/sacks?cursor=` | Public HTTP API | Farmer | Group `farmer`, and the token subject owns the farm | `sacks`, index on `farm_id` |
| `GET /farms/{farm_id}/sacks/{sack_code}` | Public HTTP API | Farmer | The same, and the sack belongs to that farm | `sacks`, `sack_events` |
| `GET /centers/{center_id}/sacks/{sack_code}` | Private REST API, through the tunnel | Center operator | Group `center_operator`, the center in the token equals the path, and the sack passed through or travels toward that center | `sacks`, `sack_events` |
| `GET /centers/{center_id}/trips?state=open` | Private REST API | Center operator | The same center check | Trips and the last position |
| `GET /trips/{trip_id}` | Public HTTP API | Carrier | Group `carrier`, and the trip belongs to the token subject | Trip and its sacks |

A center operator account carries the center where the person works as an attribute that the Federation sets and the person cannot change. A farmer who asks for a farm or a sack that is not theirs receives the same not found answer as for a farm that does not exist, so no route confirms that another farmer's record exists.

Each read of a sack writes an audit event with the view returned, `buyer`, `center` or `farmer`, as the [audit](../security/audit.md) design records. The public query uses no cache in front of the function, since a cached answer would skip that record. The [public query](public-query.md) document sizes that route and sets its limits against bulk reads.

The role of the public query function holds `dynamodb:GetItem` on `buyer_views` and nothing else on the data tables. Only the domain function and the daily job of the drying lots write that table. The two indexes this document needs on `sacks`, on `farm_id` and on `drying_lot_id`, keep only the keys. The custody chain does not define them yet, and its owner adds them.

## 7. What fails and what happens then

| Failure | What the platform does | Effect |
|---|---|---|
| The write of the buyer view fails | The whole transaction fails, and the event is retried as any other write | The view and the state never disagree |
| The daily job cannot update the drying block | The block stays `pending`, and the job retries the next day | The buyer sees drying a day later |
| A bug writes a wrong buyer view | The schema check of the pipeline stops a field outside the list. A wrong value is fixed by replaying the sack | A wrong value lasts until the replay |
| `buyer_views` is lost or damaged | It is restored with the sack tables, or rebuilt by replay | The public query returns within its 4 hours |
| A center operator asks for a sack of another center | The function refuses it and audits the attempt | No data leaves |
| Someone guesses codes | The firewall limits the rate, and a hit returns only one buyer view | No personal data is exposed |
| The farm of a sack is sold | The new owner sees new sacks only. Sacks registered before the sale stay with the owner at registration | No farmer reads the sacks of another |

## 8. Cost

Calculated from the AWS price list for us-east-1 for a harvest month, at USD 0.625 per million write units and USD 0.125 per million read units.

| Item | Calculation | USD a month |
|---|---|---|
| Buyer view written in the event transaction | 252,000 events, 2 write units each, since a transactional write of an item up to 1 KB costs two | About 0.32 |
| Drying block updated by the daily job | 36,000 sacks, 1 write unit each | About 0.02 |
| Sparse index on `drying_lot_id` | 36,000 sacks, 1 write unit each | About 0.02 |
| Index on `farm_id` for the farmer list | 36,000 sacks, 1 write unit each | About 0.02 |
| Public reads | 108,000 reads, three per sack, at half a read unit each | About 0.01 |
| Storage | 720,000 views of about 0.6 KB, about 0.4 GB, at USD 0.25 per GB a month | About 0.10, or nothing while the account stays under the 25 GB that carry no charge |
| **Total** | | **About 0.49** |

The extra table costs less than a dollar in the busiest month, which is a small price for keeping the internet-facing function away from personal data.

## 9. Assumptions and pending confirmations

| Item | Who confirms | Effect if it fails |
|---|---|---|
| Department-level origin with about 67 pilot farms each does not identify a farmer | Federation | Origin drops to the country level |
| The buyer needs no hour of each step | Federation, with buyers | The view adds hours for steps that involve no carrier, such as the center reception |
| Three public reads per sack in a month | First harvest | Read cost scales linearly, still well under a dollar |
| A center operator account can carry its center as an attribute the person cannot change | First user pool deployment | The center comes from a group per center instead |

## 10. Sources

| Fact | Source |
|---|---|
| `GetItem` and `Query` accept the condition keys `dynamodb:Attributes`, `dynamodb:LeadingKeys` and `dynamodb:Select` | [Service authorization reference for DynamoDB](https://servicereference.us-east-1.amazonaws.com/v1/dynamodb/dynamodb.json) |
| A transactional write consumes two write units per item up to 1 KB | [DynamoDB read and write capacity](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/read-write-operations.html) |
| DynamoDB prices for us-east-1, storage included | [Price basis](../governance/price-basis.md) |
| Event catalog, tables and volumes | [Custody chain](custody-chain.md) |
| Lot summary fields | [Farmer history](../iot/farmer-history.md) |
