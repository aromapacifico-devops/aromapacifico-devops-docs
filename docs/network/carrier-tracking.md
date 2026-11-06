# Carrier tracking

A carrier drives through stretches with no data, with sacks in custody and a trip that must stay complete. This document defines how the phone of a carrier reports its position every 5 minutes, what it keeps when it loses data, and how that information reaches the platform with no duplicates and no dependence on arrival order. It covers the path to the platform, capture on the phone, the local queue, synchronization, the message contract, and what fails.

## Contents

1. Context and scope
2. Volumes
3. Path to the platform
4. Capture on the phone
5. What the phone keeps with no data
6. Synchronization
7. Message contract
8. Duplicates and order
9. What fails and what happens
10. Cost
11. Assumptions and pending confirmations

### Terms used

| Term | Meaning in this document |
|---|---|
| Trip | The journey of one carrier from the first handover to the final delivery |
| Position | One location of the phone, with the time it was captured |
| Custody event | A record that a sack changed hands or arrived, such as a handover or an arrival |
| Record | A position or a custody event in the local queue |
| Location fix | A position computed by the satellite receiver of the phone, which also gives an accurate time |
| Foreground service | Android work that keeps running while the application is out of view, with a visible notification |
| Refresh token | The long-lived credential that lets the application renew its session with no new sign-in |

---

## 1. Context and scope

Carriers have a smartphone with data in municipal seats and on main roads. Farm tracks and mountain stretches may have none, and a handover can happen at a farm with no signal at all. The design therefore treats data as optional during a trip. Capturing needs no connection and no valid session, and only synchronization does.

| Topic | Where it is defined |
|---|---|
| Sack events, their states and valid transitions | Traceability design |
| Application flows and screens | Carrier application contract. The pilot does not build the application |
| Identity and session of a carrier | [Identity and access](../security/identity-and-access.md) |
| Retention of positions | [Personal data and retention](../security/personal-data-and-retention.md) |

This document covers how records travel, with or without data. The content and the meaning of each custody event belong to the traceability design, which receives two conditions from here, in section 8.

## 2. Volumes

Volumes come from the pilot figures of 60 carriers, 12 positions an hour and a working day of 10 hours.

| Measure | Value |
|---|---|
| Positions a day, all carriers | 7,200 |
| Positions a month | 216,000 |
| Positions a day, one carrier | 120 |
| Size of one position | About 0.3 KB |
| Payload a day, one carrier | About 36 KB |
| Data a month, one phone, at about 2.3 KB per request with headers and token | About 8 MB |
| Largest queue of positions, 24 hours of driving | 288 positions, about 86 KB |

The queue fits in three requests of 100 positions. If all 60 phones returned at once, the platform would receive about 180 requests, so the return of data needs no special handling. The 8 MB a month is an estimate that falls on the plan of the carrier.

## 3. Path to the platform

The phone sends positions and custody events over HTTPS to the API of the platform, with the Cognito token of the carrier. API Gateway validates the token, and the domain function writes to DynamoDB.

| Option | For | Against | Result |
|---|---|---|---|
| HTTPS on API Gateway | Same identity and path as every application action, per-record answers, retries are simple on a phone | One request for each position while online | **Chosen** |
| MQTT over WebSocket to IoT Core | Less overhead per message | A second identity path for a phone that already has a token, and a persistent connection through coverage gaps | Discarded |

Each record goes through the same steps.

1. The function checks that the token belongs to the carrier of the trip.
2. It sends positions to Firehose for the archive.
3. It writes the record to DynamoDB with a conditional write.
4. It answers per record.

The answer comes after both writes, so a record leaves the phone only when it is safe in the two stores. A failed archive write fails that record, and the phone sends it again.

## 4. Capture on the phone

The interval is fixed at 5 minutes during an open trip. A trip opens with the first handover and closes with the final delivery, so the phone reports nothing outside a trip. The position of a person is personal data, and this limit keeps tracking to what the pilot needs.

| Option for the rate | For | Against | Result |
|---|---|---|---|
| Fixed 5 minutes | Meets the pilot, and a gap always means something | A stopped vehicle repeats its position | **Chosen** |
| Adaptive, less often when stopped | Fewer records | A silent phone looks the same as a stopped one | Discarded |

The operating system decides whether this works. On Android 8 and later, an application in the background receives location only a few times each hour, which falls short of 12 positions. Android offers a foreground service of type `location` for long-running uses such as navigation and location sharing. It requires the `FOREGROUND_SERVICE_LOCATION` permission and a location permission, and it shows a permanent notification. That notification also tells the carrier that tracking is active. Google Play restricts background location to applications that need it for their core function, so publishing the application includes that review.

A web application cannot hold this interval, so the carrier application must be native or use a framework with access to these services. On iOS, the application needs the background location mode and permission from the carrier to use location at all times, which remains to confirm against current Apple documentation.

Time comes from the location fix, which does not depend on the clock of the phone. The application keeps the difference between both clocks, so a custody event with no fix still gets a corrected time. Each record states its time source. A cycle with no fix, as in a tunnel, writes a record that says so, which separates a phone with no sky from a phone that stopped working.

The trip identifier is a UUID created on the phone. A handover at a farm with no data would otherwise have no way to open a trip, and the platform binds the identifier to the carrier with the first record it receives.

## 5. What the phone keeps with no data

The phone keeps two classes of record, because they have different value.

| Class | Limit on the phone | At the limit | Reason |
|---|---|---|---|
| Custody event | None, kept until the platform answers | Never deleted by age | It proves who held a sack, and nothing can rebuild it |
| Position | 24 hours | Deleted and added to `dropped_total` | Same limit as the farm node, and it bounds the location history on a lost phone |

| Option | For | Against | Result |
|---|---|---|---|
| Two classes | One retention rule across devices, custody never lost by age, less personal data on the phone | An outage over 24 hours leaves a counted hole in the route | **Chosen** |
| Keep everything until confirmed | The route stays complete in every case | More location history on a lost phone, and a second rule to explain | Discarded |
| Keep custody events only | Simplest | Every outage leaves a hole in the trip | Discarded |

An outage of more than 24 hours inside a trip should be unusual, since the phone has data on main roads and in municipal seats. When it happens, the hole is visible and counted.

The queue lives in an encrypted database of the application, with its key in the keystore of the phone. Each record stays there until the platform answers for it. The application warns the carrier about pending custody events and refuses to sign out while any remain, because signing out would otherwise strand them.

## 6. Synchronization

The application tries whenever the phone reports a connection, and every 5 minutes during a trip. A failed request waits with exponential backoff and random jitter.

| Rule | Behavior | Reason |
|---|---|---|
| Custody first | Custody events go before any position | A short window of signal serves what matters most |
| Positions oldest first | Up to 100 in a request | The route fills in order in the normal case |
| One endpoint for both moments | Online the phone sends one position, and on return it sends batches | One path to build and to test |
| Delete on the answer | A record leaves on `accepted` or `repeated` | A lost answer costs one repeat and loses nothing |
| Rejected is final | A rejected record leaves the queue and appears as a task for the carrier | A bad record must never block the ones behind it |
| Request failure | Timeouts and server errors keep every record | The next attempt repeats the request |

A session problem never reaches the queue. The access token renews itself while the phone has data. The refresh token lasts 30 days, the default of Cognito, and rotation stays on with the grace period of 60 seconds, so a response lost on a poor signal leaves a moment to retry. Rotation never extends those 30 days. If the session ends during a trip, capture continues, the queue grows, and the carrier signs in when data returns. Only that same carrier can upload the queue, so a different person signing in on the phone cannot send records of another identity.

## 7. Message contract

```json
{
  "dropped_total": 0,
  "records": [
    {
      "record_id": "0f8c2a6e-1b7d-4c55-9a1e-3d2f6b7c8e10",
      "seq": 412,
      "captured_at": "2026-05-14T16:05:00Z",
      "time_source": "fix",
      "buffered": true,
      "lat": 2.4419,
      "lon": -76.6063,
      "accuracy_m": 12
    }
  ]
}
```

The request goes to `POST /trips/{trip_id}/positions`, and custody events use `POST /trips/{trip_id}/events` with the same envelope and the fields of the traceability design.

| Field | Purpose |
|---|---|
| `dropped_total` | Positions this trip has lost past 24 hours, a counter that only grows |
| `record_id` | UUID created at capture, which a repeat carries unchanged |
| `seq` | Counter per trip, covering positions and events, which gives the order on one phone and shows gaps |
| `captured_at` | Time of the record, correct when it arrives hours later |
| `time_source` | `fix`, `corrected` or `device`, which says how far to trust the time |
| `buffered` | Tells that the record waited in the queue |
| `lat`, `lon`, `accuracy_m` | Location, absent on a cycle with no fix |

The platform adds `received_at`, so the delay of a record needs no trust in the phone. The answer lists one result per record.

```json
{
  "results": [
    { "record_id": "0f8c2a6e-1b7d-4c55-9a1e-3d2f6b7c8e10", "status": "accepted" },
    { "record_id": "7a1d4f0c-92be-4e0a-b6c3-5e8d1f2a9c44", "status": "rejected", "reason": "unknown_sack_code" }
  ]
}
```

| Status | Meaning | The phone |
|---|---|---|
| `accepted` | Stored now | Deletes the record |
| `repeated` | Already stored | Deletes the record |
| `rejected` | Can never be stored, with a reason | Deletes it from the queue and shows a task for custody events |

## 8. Duplicates and order

**Duplicates.** A lost answer makes the phone send a record again, so repeats are normal. The positions table has the partition `trip_id` and the sort key `captured_at#record_id`, and custody events use `record_id` in the same way. A conditional write stores the first copy and answers `repeated` for the rest.

**Order of positions.** Order on the path does not matter, because the sort key orders the route by time of capture. The latest position of a trip comes from a query on that key, with no separate item to maintain, so a late arrival cannot replace a newer position.

**Archive.** The function writes to Firehose before the conditional write, so a repeat reaches the archive. Reports through Athena remove repeats on `record_id`, filter by `captured_at`, and scan one extra day, the same rule as telemetry.

**Order of custody events.** Two phones can report one sack, so arrival order cannot be trusted. A center with a working link can record an arrival while the handover waits on the phone of the carrier. The traceability design receives two conditions from this flow.

- Lateness alone never rejects an event. A valid event that arrives late is stored and takes its place in the history.
- Logical order comes from `seq` inside one phone and from `captured_at` across phones, with `received_at` kept as evidence.

**Clock.** A record more than 5 minutes ahead of `received_at`, or with `time_source` set to `device`, is stored and flagged. A custody event is never refused over its clock, because refusing it would lose proof of custody. An operator reviews flagged records.

**Model of the rules.** The queue and the API ran in a simulation of one phone, over 5,000 runs of 2 to 6 days. The rates are hostile by choice and come from no field measurement, with outages of up to 33 hours, 10 percent of requests lost, 10 percent of answers lost, 5 percent of custody events invalid, and sessions that expire during a trip.

| Check | Result |
|---|---|
| Positions generated | 2,399,640 |
| Custody events generated | 59,991 |
| Each custody event stored once, or shown to the carrier as rejected | Held in every run |
| Each position stored once, or counted as lost | Held in every run |
| Oldest position at any attempt | 23.9 hours |
| Positions sent while a custody event waited | 0 |
| Repeats answered without a second record | 243,178 |
| Archive after removing repeats equals the table | Held in every run |
| Positions counted as lost, under these outages | 222,332, or 9.3 percent |
| Of those, stored already after a lost answer | 2,674 |
| Runs with a wrong latest position, if the last arrival won | 3,887 of 5,000 |

The loss rate reflects outages far longer than the route should produce. As on the farm node, `dropped_total` is an upper bound, since a position stored just before it aged out counts as lost when its answer was lost.

## 9. What fails and what happens

| Failure | Effect | Response |
|---|---|---|
| No data on the road | Records stay in the queue | Sent on return, custody first |
| No data at the handover | The trip opens on the phone | The identifier binds to the carrier with the first record |
| Answer lost | The phone sends again | Answered as `repeated` |
| Session ended during a trip | Sync stops, capture continues | The carrier signs in when data returns |
| No location fix | A record with no position | The gap reads as no sky, and the phone keeps its clock offset |
| Carrier denies the location permission | The trip has no route | The application asks again and warns at the handover. Custody events still work |
| Application closed by the system | Tracking stops | The notification disappears, and a break in the times of the route shows the missing period |
| Battery runs out | Tracking stops | The queue survives on the phone and syncs after charging |
| Invalid sack code read with no data | The platform cannot accept the event | Rejected with a reason, and shown to the carrier as a task |
| Phone lost or broken | Records not yet sent are lost | The next event, such as the arrival at the center, shows the gap, and the operator completes the history |
| Phone stolen | Risk to the stored data | The operator ends the session, and the store on the phone stays encrypted |
| API or function down | Requests fail | Records stay on the phone, with no loss on the platform side |

## 10. Cost

Calculated from the AWS price list for us-east-1, with the worst case of one request per position.

| Item | Rate | USD a month |
|---|---|---|
| API Gateway HTTP API, 216,000 requests | USD 1.00 per million | 0.22 |
| Lambda, 0.2 s at 256 MB | USD 0.20 per million and USD 0.0000166667 per GB-second | 0.22 |
| DynamoDB writes | USD 0.625 per million | 0.14 |
| Firehose, about 65 MB | USD 0.029 per GB | Under 0.01 |
| **Total** | | **About 0.58** |

This fits inside the line for APIs in the monthly cost of the platform, so no total changes. Every batch on return lowers the number of requests. The data plan belongs to the carrier, at about 8 MB a month.

## 11. Assumptions and pending confirmations

| Item | Who confirms | Effect if it fails |
|---|---|---|
| Carriers use Android or iOS phones and accept location at all times during a trip | Federation and carriers | A dedicated device, or a lower expectation for the route |
| The phone stays charged in the vehicle during a trip | First trips | Battery becomes a limit, and the interval may need review |
| Current iOS requirements for background location | Application contract | The iOS version may need a different method |
| Google Play accepts background location for this use | Publication of the application | Distribution outside the store for the pilot |
| One request costs about 2.3 KB with headers and token | First trips | The monthly data scales linearly |

## Sources

- Android Developers, foreground service types, and access to location in the background.
- Amazon Cognito Developer Guide, refresh tokens.
- API Gateway Developer Guide, quotas for HTTP APIs.
- AWS Price List API for API Gateway, Lambda, DynamoDB and Firehose in us-east-1.
