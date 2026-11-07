# Port delivery

The record of a sack ends at the port of Buenaventura. The Federation installs nothing there, and the shipping company keeps the telemetry of its ship. This document defines what the platform records at the port, with what evidence, how a truck with some rejected sacks is handled, when a trip closes, and where the responsibility of the platform stops.

## Contents

1. Context and scope
2. Volumes
3. What exists at the port
4. Delivery flow
5. Evidence of the delivery
6. Partial rejection
7. End of the trip
8. Where the record stops
9. A wrong delivery
10. What fails and what happens
11. Cost
12. Assumptions and pending confirmations

### Terms used

| Term | Meaning in this document |
|---|---|
| Receiver | The organization that takes the sack at the port, such as a buyer or a terminal |
| Receipt | The document the receiver issues for a load |
| Load | The sacks of one trip |
| Port area | A map zone of the platform that marks where deliveries are expected |

---

## 1. Context and scope

Trucks arrive at the port from the three collection centers. A receiver inspects the load, accepts or rejects each sack, and takes custody. For the platform, that is one event per sack.

| Topic | Where it is defined |
|---|---|
| States and the two delivery events | [Sack states](../traceability/sack-states.md) |
| Event format, tables and write path | [Custody chain](../traceability/custody-chain.md) |
| Queue on the phone and the path to the platform | [Carrier tracking](carrier-tracking.md) |

## 2. Volumes

| Measure | Value |
|---|---|
| Sacks a day reaching the port in harvest, three centers | Up to 1,200 |
| Sacks in a truck, as an estimate | About 30 |
| Trucks a day at the port | About 40 |
| Delivery events a day | Up to 1,200 |

These events are part of the 252,000 of a harvest month in the custody chain, so the port adds no load of its own.

## 3. What exists at the port

The only device involved is the phone of the carrier, on a public mobile network.

| Element | At the port |
|---|---|
| Local network | None |
| WAN link or VPN tunnel | None |
| Firewall rule or cloud address range | None |
| Fixed device, reader or printer | None |
| Federation staff | None |
| Account for the receiver | None |
| Phone of the carrier | Yes, the same application as the rest of the trip |

The protocol is HTTPS over the mobile network, and the buffer is the queue of the application. With no data, the event waits there with no time limit, as every custody event does, and the carrier can leave.

Port areas are a setting of the platform. They need no equipment on site.

## 4. Delivery flow

| Step | Carrier | Platform |
|---|---|---|
| 1 | Arrives with the load, and the application shows the sacks of the trip | |
| 2 | Scans each sack | |
| 3 | Marks the rejected sacks with a reason, and the rest stay accepted | |
| 4 | Enters the receiver and the receipt reference | |
| 5 | Confirms, and the application saves one event per sack | |
| 6 | Sends the events, now or when data returns | Stores each event once and updates the state |

The carrier is the responsible person of each event, and the event stores date, time and location, as the custody chain defines. The application works from the list of the trip that it already holds, so scanning needs no connection.

## 5. Evidence of the delivery

| Field | Purpose |
|---|---|
| `received_by_org` | The organization that took the sack |
| `receipt_ref` | Reference of the receipt issued for the load |
| `location` | Where the event happened |
| `captured_at` | When it happened |

| Option | For | Against | Result |
|---|---|---|---|
| Organization and receipt reference | No personal data of a third party, and the reference can be audited against the document of the receiver | Names no person | **Chosen** |
| Name of the person who received | Names someone | That person never signs up, so no consent covers the data | Discarded |
| Photo of the signed receipt | Strongest evidence | Holds a name and a signature, and adds an upload path to the phone | Discarded |

The pilot collects only what operating it needs, and the receipt already names the people involved on a document that belongs to the receiver. If a dispute arises, the reference leads to that document.

A delivery recorded outside the port areas is stored and flagged for the review list. A carrier with a poor location fix must still be able to deliver, so the check never refuses an event.

## 6. Partial rejection

Each sack has its own event, so a receiver can reject some of a load. The carrier marks those sacks, and the reason stays in the event. A truck of 30 sacks with 3 rejected ends with 27 in `delivered_accepted` and 3 in `delivered_rejected`.

A rejected sack ends its record at the port. What happens to that coffee afterwards is a commercial claim between the parties, and any trip back happens outside the platform.

## 7. End of the trip

The trip to the port closes when each of its sacks has a delivery or a `reported_missing`. Tracking stops at that moment, so the phone reports no position after the work ends. A sack marked as missing keeps its state and appears on the review list, so one lost sack cannot keep a person under tracking.

## 8. Where the record stops

The delivery event is the last fact the platform holds about a sack.

| Data | Holder |
|---|---|
| Sack, its events and its delivery | The platform |
| Receipt of the load | The receiver |
| Booking, container and bill of lading | The shipping company and the exporter |
| Position of the ship | The shipping company |

The platform stores no ship, no booking and no container, and it has no integration with the shipping company. The buyer view ends at the delivery. A buyer who wants to follow the ship does so with the shipping company.

## 9. A wrong delivery

Delivery ends the record, so a mistake cannot be undone by another event. The application therefore asks for confirmation before saving, and shows the count of accepted and rejected sacks.

| Option | For | Against | Result |
|---|---|---|---|
| Final, with a confirmation step | Keeps the record simple, and needs no new permission | A confirmed mistake stays in the state | **Chosen** |
| Correction event | The state can be fixed | The carrier has left, the center no longer holds the sack, and some role would need a new permission | Discarded |

A second delivery event on the same sack becomes an anomaly. Both events stay in the history, and the review list shows the conflict. The first state stands.

## 10. What fails and what happens

| Failure | Effect | Response |
|---|---|---|
| No data at the port | The events stay in the queue | Sent on return, with no limit of time |
| Phone runs out of battery at the port | Delivery cannot be recorded then | The carrier charges it in the vehicle and records with the receipt in hand |
| Sack not on the list of the trip | The scan finds an unexpected sack | The event is stored and resolved by the replay, as a gap or an anomaly |
| Label unreadable | The scan fails | The carrier types the code, and the check symbol catches a mistake |
| Receiver issues no receipt | No reference to enter | The event stands on the scan, location and time, and the empty reference shows on the review list |
| Delivery outside the port areas | The event looks suspicious | Stored and flagged |
| Second delivery of a sack | Conflict in the history | Anomaly, with the first state kept |
| A sack never delivered | The trip stays open | `reported_missing` lets it close |

## 11. Cost

The port adds no cloud resource and no line of cost. Delivery events are already counted in the custody chain, and they travel over the data plan of the carrier.

## 12. Assumptions and pending confirmations

| Item | Who confirms | Effect if it fails |
|---|---|---|
| The receiver issues a receipt with a reference the carrier can enter | Federation | The evidence falls to the scan and the location |
| The carrier can record the delivery with the organization and the receipt | Federation | The port needs another role or a record from a third party |
| About 30 sacks fit a truck | Carriers | The number of trucks changes, with no effect on the design |

## Sources

This document relies on the design documents it links and adds no external service.
