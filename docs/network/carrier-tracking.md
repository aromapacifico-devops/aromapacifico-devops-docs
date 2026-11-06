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
