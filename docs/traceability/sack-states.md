# Sack states

A sack moves from a farm to the port of Buenaventura through seven states, and every step needs a date, a time and a responsible person. This document defines those states, the events that move a sack between them, which movements are valid, what happens with the ones that are not, and how a rejection stays in the record. The state of a sack comes from its history of events, so a sack keeps the correct state even when its events reach the platform late or out of order.

## Contents

1. Context and scope
2. Volumes
3. States
4. Events
5. Valid transitions
6. Invalid transitions
7. Rejection and correction
8. How the state is derived
9. What fails and what happens
10. Cost
11. Assumptions and pending confirmations

### Terms used

| Term | Meaning in this document |
|---|---|
| State | Where a sack stands, one of seven values |
| Event | A dated fact about a sack, recorded by one person and never changed |
| Transition | A change of state caused by an event |
| History | All the events of one sack, in logical order |
| Replay | Applying the history from the first event to compute the state |
| Gap | A missing earlier event, expected to arrive later |
| Anomaly | An event that does not fit the history, kept for review |

---

## 1. Context and scope

The pilot names seven states and leaves open what happens between them. The sack identity design fixed their values in the `state` field. This document adds the movements. It relies on two facts of the field. The people who handle a sack work on separate phones and networks, and a carrier may have no data for hours. A center can therefore hold a sack in its hands while the event that says who brought it is still waiting on a phone.

| Topic | Where it is defined |
|---|---|
| Sack code and the values of `state` | [Sack identity](sack-identity.md) |
| How events travel from a phone with no data | [Carrier tracking](../network/carrier-tracking.md) |
| Roles and their permissions | [Identity and access](../security/identity-and-access.md) |

Event fields, the idempotency key and the tables belong to the design of the custody chain. The operating flow at a center and the reasons for a rejection belong to the design of the centers, and the fields each actor reads belong to the design of the views.

## 2. Volumes

Volumes come from the pilot figure of 400 sacks a day per center in harvest, across three centers.

| Measure | Value |
|---|---|
| Sacks a day in harvest | Up to 1,200 |
| Sacks a harvest month | Up to 36,000 |
| Events of one sack on the normal path | 7 |
| Events a harvest month | Up to 252,000 |
| Events a day at one center, reception and dispatch | Up to 800 |

The history of one sack stays short, about 7 events and rarely above 20, so reading it to compute a state is cheap.

## 3. States

| Value | Meaning | Who holds the sack | Badge in the design system |
|---|---|---|---|
| `in_preparation` | Registered, waiting to leave | Farmer, or center for a sack with no code | In preparation |
| `in_transit_to_center` | On the way to the center | Carrier | In transit |
| `at_center_accepted` | Inspected and accepted at the center | Center | Accepted |
| `at_center_rejected` | Inspected and rejected at the center | Center | Rejected |
| `in_transit_to_port` | On the way to Buenaventura | Carrier | In transit |
| `delivered_accepted` | Delivered at the port and accepted | Outside the platform | Accepted |
| `delivered_rejected` | Delivered at the port and rejected | Outside the platform | Rejected |

Two states end the record, `delivered_accepted` and `delivered_rejected`. What follows a delivery is a commercial matter between the parties, and the platform records the delivery and nothing further.

`at_center_rejected` is a resting state. A rejected sack that never returns stays there, with its history intact.

## 4. Events

Each event stores the date, the time and the responsible person. Some events change the state, and others only add to the history.

| Event | Recorded by | Effect |
|---|---|---|
| `registered` | Farmer | Starts the sack in `in_preparation` |
| `registered_at_center` | Center operator | Starts a sack that arrived with no code, in `in_preparation` |
| `handed_to_carrier` | Carrier | Moves it to `in_transit_to_center` |
| `received_accepted`, `received_rejected` | Center operator | Reception decision |
| `reception_corrected_to_accepted`, `reception_corrected_to_rejected` | Center operator | Changes a decision, with a reason |
| `returned_to_farm` | Center operator | Sends a rejected sack back to `in_preparation` |
| `dispatched_to_port` | Center operator | Moves it to `in_transit_to_port` |
| `delivered_accepted`, `delivered_rejected` | Carrier, naming who received | Ends the record |
| `arrived_at_center` | Carrier | No change of state |
| `picked_up` | Carrier | No change of state, opens the trip to the port |
| `reweighed` | Farmer | No change of state, records a new weight on re-entry |
| `label_reprinted` | Center operator | No change of state |
| `reported_missing` | Carrier or center operator | No change of state, marks the sack for review |

Arrival is an event with no change of state, because a center can receive 400 sacks in a day and inspect them later. The sack stays `in_transit_to_center` until someone decides, and the history shows both moments.

## 5. Valid transitions

Eleven of the 42 possible movements are valid.

| From | To | Event | Recorded by |
|---|---|---|---|
| `in_preparation` | `in_transit_to_center` | `handed_to_carrier` | Carrier |
| `in_preparation` | `at_center_accepted` | `received_accepted`, only for a sack registered at the center | Center operator |
| `in_preparation` | `at_center_rejected` | `received_rejected`, only for a sack registered at the center | Center operator |
| `in_transit_to_center` | `at_center_accepted` | `received_accepted` | Center operator |
| `in_transit_to_center` | `at_center_rejected` | `received_rejected` | Center operator |
| `at_center_accepted` | `at_center_rejected` | `reception_corrected_to_rejected` | Center operator |
| `at_center_accepted` | `in_transit_to_port` | `dispatched_to_port` | Center operator |
| `at_center_rejected` | `in_preparation` | `returned_to_farm` | Center operator |
| `at_center_rejected` | `at_center_accepted` | `reception_corrected_to_accepted` | Center operator |
| `in_transit_to_port` | `delivered_accepted` | `delivered_accepted` | Carrier |
| `in_transit_to_port` | `delivered_rejected` | `delivered_rejected` | Carrier |

The route always passes through a center, and there is no direct path from a farm to the port.
