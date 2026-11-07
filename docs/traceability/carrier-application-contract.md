# Carrier application contract

The carrier handles sacks and drives, so the application must ask for little and work with no data. This document is the contract a team would build from. It lists what the carrier does, how each step behaves with and without data, what the phone must hold, the API it calls, and what the device must allow. The pilot does not build the application, and the visual design belongs to the design system.

## Contents

1. Context and scope
2. What the carrier does
3. Two legs, two trips
4. Flows with and without data
5. Position every 5 minutes
6. Data on the phone
7. API
8. Device requirements
9. What fails and what happens
10. Cost
11. Assumptions and pending confirmations

### Terms used

| Term | Meaning in this document |
|---|---|
| Action | One thing the carrier does on the screen, such as a scan or a confirmation |
| Leg | One part of the route, from the farms to a center or from a center to the port |
| Trip | The record of one leg |
| Load | The sacks of one trip |
| Task | A problem the application shows to the carrier, such as a rejected record |
| Contract version | The number of this API, sent with each request |

---

## 1. Context and scope

| Topic | Where it is defined |
|---|---|
| Queue, synchronization and message format | [Carrier tracking](../network/carrier-tracking.md) |
| Events, their fields and the write path | [Custody chain](custody-chain.md) |
| States and what an event can do | [Sack states](sack-states.md) |
| Delivery and its evidence | [Port delivery](../network/port-delivery.md) |

This document joins those rules into one view and repeats only what a builder needs on the page.

## 2. What the carrier does

Six actions cover the work of a carrier. A load of 30 sacks serves as the example.

| Moment | Event | What the carrier does | Actions for 30 sacks |
|---|---|---|---|
| At each farm | `handed_to_carrier` | Scans each sack | 30 scans |
| At the center | `arrived_at_center` | Taps arrival, for the whole load | 1 |
| At the center, leaving for the port | `picked_up` | Scans each sack | 30 scans |
| At the port | `delivered_accepted`, `delivered_rejected` | Scans each sack, marks rejected ones, enters receiver and receipt, confirms | 30 scans, plus 3 |
| When a sack cannot be found | `reported_missing` | Picks the sack from the list | 1 |
| End of the working day | Trip pause | Taps pause, and resume the next day | 2 |

A scan changes custody, so it happens for each sack, with no shortcut. Arrival changes no custody, since the center records its own reception, so one action covers the load. Position needs no action at all. Signing in, opening a trip and synchronizing happen without the carrier asking for them.

## 3. Two legs, two trips

The route has two legs, and each one is a separate trip with its own `trip_id`.

| Leg | Opens with | Closes when each sack has |
|---|---|---|
| To the center | The first `handed_to_carrier` | `arrived_at_center` or `reported_missing` |
| To the port | The first `picked_up` | A delivery event or `reported_missing` |

The phone decides the closure with its own records, so a leg closes with no data. Tracking stops at that moment. A sack marked as missing closes for this purpose, so one lost sack cannot keep a person under tracking.

## 4. Flows with and without data

Capture never needs a connection. Data decides only when the platform learns about it.

| Flow | With data | Without data |
|---|---|---|
| Handover at a farm | Scan, and the event reaches the platform in seconds | Scan, the event waits in the queue, and the trip opens on the phone |
| Code that fails its check symbol | The application refuses the scan and asks to scan again | Same, since the check runs on the phone |
| Issued code with no registration yet | Stored as a gap until the registration arrives | Same, when the queue is sent |
| Well-formed code that was never issued | Stored as an anomaly, and the center reviews it | Same, when the queue is sent |
| Arrival at the center | One action, sent at once | One action, sent on return |
| Pickup for the port | Scan each sack, and a sack that is not at the center shows a warning | Scan each sack, and the check waits for the replay |
| Delivery at the port | Scan, mark, enter, confirm, sent at once | Same, and the events wait in the queue with no time limit |
| Rejected record | Shown as a task at once | Shown as a task on the first sync |
| Sign-in | Needs data, once | Capture continues if the session ends, and the sign-in waits |

Every flow links to the sack code through the scan. The carrier types a code only when a label cannot be read, and the check symbol catches a mistake.

## 5. Position every 5 minutes

During an open trip the phone captures a position every 5 minutes, and sends it when it can, with no action from the carrier. A notification stays on screen while tracking runs. [Carrier tracking](../network/carrier-tracking.md) defines the interval, the queue and the limit of 24 hours.

Tracking follows the person only while working.

| Option | For | Against | Result |
|---|---|---|---|
| Pause by the carrier, with a reminder | Follows the person only while working, matches the working day of 10 hours, one action | A carrier can forget, or pause while driving, which leaves a visible gap | **Chosen** |
| Continuous during an open trip | Simplest, no gaps in the route | Records where a person sleeps | Discarded |
| Automatic time window | No action needed | A night trip goes unrecorded, and working hours differ | Discarded |

The application reminds the carrier after 10 hours of tracking. A pause keeps the trip open and the sacks in custody, and a resume continues it. Each pause and resume is recorded with the positions of the trip, so a break in the route explains itself. These records concern the person and the trip, so they add nothing to the history of a sack.

## 6. Data on the phone

| Data | Purpose | Kept until |
|---|---|---|
| Open trips and their sacks, built from its own scans | Close a leg and deliver with no data | The trip closes and its records are confirmed |
| Custody events in the queue | Send them later | The platform answers, with no time limit |
| Positions in the queue | Send them later | The platform answers, or 24 hours pass |
| Counter `seq` and `dropped_total` of each trip | Order and loss accounting | The trip closes |
| Offset between the location fix and the device clock | Correct the time of an event | Replaced at each fix |
| Tasks | Show rejected records | The carrier resolves them |
| Session tokens | Synchronize | Sign-out or expiry |

Everything lives in an encrypted store, with its key in the keystore of the phone. The application refuses to sign out while custody events are pending, and it warns when the session has seven days left, so the carrier can renew it with data.

## 7. API

The application calls one API with the Cognito token of the carrier. Each request sends the header `X-Contract-Version`.

| Method and path | Purpose |
|---|---|
| `POST /trips/{trip_id}/positions` | Send 1 to 100 positions, including pause and resume records |
| `POST /trips/{trip_id}/events` | Send 1 to 100 custody events |
| `GET /trips/{trip_id}` | Read the state of the sacks of a trip, when data exists |

Formats and per-record answers are defined in [carrier tracking](../network/carrier-tracking.md) and the [custody chain](custody-chain.md).

| HTTP status | Meaning | The application |
|---|---|---|
| 200 | Results per record, `accepted`, `repeated` or `rejected` | Applies each result |
| 400 with `contract_version_unsupported` | The application is too old | Keeps the queue and asks for an update |
| 401 | The session ended | Keeps capturing and asks for a sign-in |
| 403 | The token does not match the carrier of the trip | Keeps the record and shows a task |
| 429 | Too many requests | Retries after the time in `Retry-After` |
| 5xx or a timeout | A failure of the platform or the path | Retries with backoff and jitter |

The platform accepts the current contract version and the previous one, so a phone with no data for days can still send its queue. A queue is never deleted over a version problem, and the application sends it after updating.

## 8. Device requirements

| Requirement | Why |
|---|---|
| Foreground location with a visible notification | Android gives background location only a few times each hour |
| Camera | Scanning the QR of a label |
| Encrypted local store | The queue holds personal data |
| Background synchronization | The queue must leave when data returns |
| Keystore of the phone | Protects the key of the store and the tokens |

Android and iOS are both targets, and the contract stays neutral on how the application is built. A web application cannot meet the first requirement, so the application must be native or use a framework with access to these services. The iOS requirements remain to confirm against current Apple documentation.

## 9. What fails and what happens

| Failure | Effect | Response |
|---|---|---|
| Carrier forgets to pause | Tracking runs past the working day | The reminder at 10 hours repeats until the carrier answers |
| Carrier pauses while driving | A gap in the route | The pause record explains the gap, and the positions on both sides show how far the vehicle moved |
| Carrier forgets the arrival | The leg stays open and tracking continues | The center sees the reception, and the application asks when the next handover starts |
| Application too old | Sends are refused | The queue stays, and the application asks for an update |
| First sign-in with no data | The application cannot start | The carrier signs in before the first trip |
| Phone replaced during a trip | Unsent records are lost | The next event shows the gap, and the center operator reviews it |
| Rejected record | It leaves the queue | The task stays until the carrier resolves it |

## 10. Cost

The application adds no cloud resource beyond those counted in carrier tracking and the custody chain. Pause records travel in the same requests as positions. Building, publishing and maintaining the application lie outside the pilot.

## 11. Assumptions and pending confirmations

| Item | Who confirms | Effect if it fails |
|---|---|---|
| Carriers accept location at all times during a trip | Federation and carriers | A dedicated device, or a lower expectation for the route |
| The phone stays charged in the vehicle during a trip | First trips | Battery becomes a limit |
| Current iOS requirements for background location | Whoever builds the application | The iOS version may need a different method |
| Google Play accepts background location for this use | Publication | Distribution outside the store for the pilot |
| A reminder at 10 hours fits the working day of carriers | First trips | The time changes, with no effect on the design |

## Sources

- Android Developers, foreground service types, and access to location in the background.
- RFC 6585, status code 429.
