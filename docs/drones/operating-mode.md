# Drone operating mode

The drone service combines area work and precision work. Each of the five services stays, because each one answers a different need, and a brigade flies only when an order calls for it.

## Services and mode

| Service | Mode | Trigger | Result |
|---|---|---|---|
| Delimit the lot | Area | First visit to a farm | Polygon and no-fly zones |
| Confirm the alert | Precision | Sensor alert | Photo of the focus and confirmation |
| Fumigate | Precision | Authorized order | Flight log with window, operator and product lot |
| Verify | Precision | Closed fumigation flight | Photo or short path that closes the case |
| Estimate the harvest | Area | Once per harvest | Estimated sacks for the collection center |

No service replaces another. Estimation never fumigates, and fumigation never runs on a lot with no polygon.

## Event that passes from area to precision

The event is **lot polygon published**. A lot enters precision work only after its polygon and no-fly zones exist on the platform. From then on, a sensor alert on that lot can open a confirmation mission, and a confirmed case can reach a fumigation order.

## Why the combination

| Alternative | Result |
|---|---|
| Precision only | No polygon and no harvest estimate, so two services would be missing |
| Area only | Blanket flights to find foci, and no way to fumigate one focus |
| Combination | Each service uses the flight that suits it |

## Cost and cadence

| Period | Cadence |
|---|---|
| Harvest | One review campaign a month, plus fumigations from open cases |
| Outside harvest | One review campaign every three months |

Drones fly to the focus a sensor marks, so the service costs far less than a sweep of all 200 farms. The team's cost model puts the shared service at about USD 5,640 a year, against about USD 18,000 for weekly sweeps or one drone per farmer. In a harvest month, that is about USD 9.90 per farm. Fleet size and image counts behind those figures are estimates recorded with the assumptions.

The farmer neither buys nor flies a drone. Three brigades, one per department, operate for the Federation.
