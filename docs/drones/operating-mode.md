# Drone operating mode

The drone service combines area work and precision work. This document explains why, defines the event that moves a lot from one mode to the other, states how each of the five services works, who takes part, how often it flies in the pilot, and why it costs what it costs.

## Contents

1. What the service must do
2. Modes compared
3. Services and mode
4. Event that passes from area to precision
5. Who does what
6. Cadence
7. Mission package and link
8. Flight logs
9. Cost
10. Assumptions and pending confirmations

### Terms used

| Term | Meaning in this document |
|---|---|
| Precision agriculture | Working on one focus: confirm, fumigate, verify |
| Area agriculture | Working on a whole lot or farm: delimit, estimate |
| Focus | The area around the node whose reading raised the alert, or around a reported symptom |
| Polygon | The geographic outline of a lot |
| No-fly zone | Houses, the processing facility, roads and water sources, loaded before the first flight |
| No-spray strip | A band around those places where the drone may fly with the sprayer off |
| Campaign | A planned round of flights in a period |

---

## 1. What the service must do

| Service | Result | Hard rule |
|---|---|---|
| Delimit the lot | Polygon and no-spray zones | Without it, no fumigation order goes out |
| Confirm the alert | Evidence of the focus | The drone flies to the focus, never over the whole farm |
| Fumigate | Treated lot and flight log | Only on a delimited lot, with an authorized order |
| Verify | Photo or short path | Without it, the fumigation stays open |
| Estimate the harvest | Number of sacks for the center | One area flight per farm and per harvest, no fumigation |

The five services all enter the design, and none replaces another.

## 2. Modes compared

| Option | Delimit | Confirm | Fumigate | Verify | Estimate | Result |
|---|---|---|---|---|---|---|
| Precision only | No polygon | Yes | Blocked, no polygon | Yes | No | Discarded, misses two services and blocks a third |
| Area only | Yes | By sweeping everything | Would treat more than needed | By sweeping again | Yes | Discarded, flies far more and cannot act on one focus |
| Combination | Area | Precision | Precision | Precision | Area | **Chosen** |

Precision alone cannot work, since fumigation depends on a polygon that only area work produces. Area alone meets the letter of the services at a much higher flight cost, and the mode rules out fumigating a whole area. The combination gives each service the flight that suits it.

## 3. Services and mode

| Service | Mode | Trigger | Who starts it | Object produced |
|---|---|---|---|---|
| Delimit the lot | Area | First visit to a farm | Campaign plan | Polygon, map |
| Confirm the alert | Precision | Sensor alert or visible symptom | Platform | Focus photo |
| Fumigate | Precision | Authorized order | Supervisor | Flight log with product lot |
| Verify | Precision | Closed fumigation flight | Platform | Photo or short path |
| Estimate the harvest | Area | Once per farm and per harvest | Campaign plan | Orthomosaic, field sample, estimated sacks |

A visible symptom on a coffee plant also enters through the confirmation service, so no separate weekly review exists.

## 4. Event that passes from area to precision

The event is **lot polygon published**. A lot enters precision work only after its polygon and no-fly zones exist on the platform.

| State of the lot | What can happen |
|---|---|
| No polygon | Only a delimitation mission |
| Polygon published | A sensor alert can open a confirmation mission |
| Focus confirmed | A person can create and authorize a fumigation order |
| Fumigation closed | Verification closes the case |
| Harvest period | An estimation flight returns to area work on that lot |

The rule is enforced by the platform with a conditional write, so an order cannot exist for a lot with no polygon.

The [lot boundaries and exclusion zones](lot-boundaries-and-exclusions.md) define the polygon format, the no-spray strips and their legal distances, and the ground application the brigade uses when a strip keeps the drone away from a focus. The [harvest estimation](harvest-estimation.md) defines how the estimation flight becomes sacks for the center.

## 5. Who does what

The farmer neither buys nor flies a drone. The Federation runs the service.

| Actor | Role |
|---|---|
| Brigade | Three, one per department, with the certified pilot and equipment |
| Pilot | Flies the mission and closes the flight log |
| Drone supervisor | Authorizes the order, with MFA, and never the same person as the pilot |
| Platform | Creates missions, stores objects, checks preconditions |
| Farmer | Receives the visit and sees the case |
| Center | Receives the harvest estimate |

Fumigation is authorized with a human identity, and no trigger can execute it.

Flights fall under RAC 100, the Colombian regulation for unmanned aircraft. Spraying as a service is a commercial activity, so it belongs to the [specific category](https://www.aerocivil.gov.co/preguntas-frecuentes/18/drones-y-movilidad-urbana-aerea/), which covers aircraft up to 250 kg and needs a flight authorization from Aerocivil. The open category allows no commercial work, so a farmer cannot fly these missions with a personal drone. The authorization rests on three documents.

| Document | Held by |
|---|---|
| Registration certificate of the aircraft | Brigade operator, one per drone |
| UAS operator certificate, specific category | Brigade operator |
| Pilot certificate of competence, with the spraying addition | Each pilot |

Aerocivil issued its [first operator certificate for spraying](https://x.com/AerocivilCol/status/2051378340129394763) in 2026, so few companies hold one yet. The Federation should expect to contract a certified operator or to allow lead time for certifying its own.

## 6. Cadence

| Period | Review campaigns | Fumigations |
|---|---|---|
| Harvest | One a month | Those that open cases, about 25 a month |
| Outside harvest | One every three months | Few |

| Estimate for a harvest month | Value |
|---|---|
| Foci confirmed | About 40 |
| Fumigation orders | About 25 |
| Verification flights | About 25 |
| Images | About 9,000 |

These counts are estimates. The team sets them from the pilot size, and the first harvest should replace them with real ones.

## 7. Mission package and link

The drone operates far from the farmer's phone, so a mission never depends on signal at the lot.

| Moment | Where | What happens |
|---|---|---|
| Before departure | Municipal seat or center | The ground station downloads the mission, polygon and no-fly zones |
| At the lot | No signal needed | The drone flies the loaded mission |
| After landing | Lot | Objects and log stay in the drone and ground station buffers |
| On return | Municipal seat or center | The ground station uploads with presigned URLs |

If the link falls at the lot, the mission stays in the buffer of the drone. The fumigation does not close until its flight log is stored on the platform.

The [drone mission link](../network/drone-mission-link.md) defines the signed package, the exact polygon and exclusion versions, how long a package stays valid offline, the acknowledgements of the station and the drone, the resumable upload and when a flight counts as complete. Presigned URLs are requested after the connection returns, so none has to last through the trip.

## 8. Flight logs

Each flight closes its own log. The confirmation or delimitation flight closes first, a person authorizes after that, and the fumigation and verification close the case with their own logs. This reading removes the apparent circle between "no authorization without a closed log" and "no closure without a stored log".

## 9. Cost

The shared service avoids two expensive alternatives, a drone for each farmer and weekly sweeps over all 200 farms.

| Option | Yearly cost in the team's model, USD |
|---|---|
| Own drone per farmer or weekly sweeps | About 18,000 |
| Shared brigades directed by sensors | About 5,640 |

In a harvest month, the shared service costs about USD 1,980, or USD 9.90 per farm. These are estimates from the team's model, resting on the assumptions of section 6, and the cost document holds their detail.

Cloud cost for inference is small next to flight cost. At about USD 1.75 per 1,000 images, a harvest month of 9,000 images costs about USD 16.

## 10. Assumptions and pending confirmations

| Item | Who confirms | Effect if it fails |
|---|---|---|
| Three brigades cover the three departments | Federation | Fleet and cost change |
| A supervisor can authorize remotely in time | Federation | Authorization moves to the brigade lead |
| Who holds the operator certificate, the Federation or a contractor | Federation | Hiring and brigade cost change |
| Spraying addition of the pilot and liability insurance, taken from secondary sources | Current text of RAC 100, legal review | Training time and brigade cost change |
| Yearly harvest of four months | Federation | Cadence and cost change |
