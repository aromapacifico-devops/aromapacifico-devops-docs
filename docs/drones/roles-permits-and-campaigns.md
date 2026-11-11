# Drone roles, permits and campaigns

The farmer never flies the drone alone. This document says who flies each mission, who authorizes a fumigation, under which permit each flight takes place and how often the brigades fly in the pilot. It also defines what a campaign is and how missions raised by an alert fit between campaigns.

## Contents

1. Context and pilot figures
2. Who holds the operator certificate
3. Roles
4. Responsibility matrix
5. Permits
6. Fumigation authorization
7. Campaigns
8. Frequency in the pilot
9. What fails and what happens then
10. Assumptions and pending confirmations
11. Sources

### Terms used

| Term | Meaning in this document |
|---|---|
| Operator | The company that holds the UAS operator certificate of Aerocivil and employs the pilots |
| Pilot | The person who flies the drone, with a certificate of competence |
| Brigade | One pilot team with its drones and ground station, one per department |
| Drone supervisor | Federation staff member who plans campaigns, publishes lot polygons and authorizes fumigations in one department |
| Specific category | The category of RAC 100 for commercial or professional drone work, which needs certificates and a flight authorization |
| Flight authorization | The permission Aerocivil grants for an operation, backed by a risk analysis |
| Campaign | A planned round of the brigade through the farms of one department in one period |
| Alert-driven mission | A confirmation, fumigation or verification flight that starts from a sensor alert or a reported symptom |
| R, A, C, I | Responsible does the work, Accountable answers for it and signs it off, Consulted gives input before, Informed hears after |

---

## 1. Context and pilot figures

The [drone operating mode](operating-mode.md) defines the five services, the three brigades and the monthly volumes of a harvest month. This document takes those figures as given and adds who carries out each step and under which permit.

| Figure | Value | Source |
|---|---|---|
| Farms | 200 | Pilot definition |
| Departments | 3, Cauca, Huila and Tolima | Pilot definition |
| Brigades | 3, one per department, about 67 farms each | Operating mode |
| Harvest months | 4 a year | Operating mode |
| Harvest month | 40 confirmed foci, 25 fumigations, 25 verifications, 9,000 images | Operating mode |
| Harvest estimation | One flight per farm and per harvest, about 100 images | Harvest estimation |
| Campaign cadence | One a month in harvest, one every three months outside it | Pilot definition |

## 2. Who holds the operator certificate

Every service of the pilot is commercial work, so every flight falls in the specific category. That category needs a UAS operator certificate held by a company, a registered drone and a certified pilot. Aerocivil issued its [first operator certificate for spraying](https://x.com/AerocivilCol/status/2051378340129394763) in 2026, so few companies hold one.

| Option | What it means | Result |
|---|---|---|
| One contracted operator for the three brigades | A certified company provides pilots, drones and the operator certificate. The Federation owns the service, the platform, the data and the authorization | **Chosen** |
| The Federation certifies its own brigades | The Federation becomes the operator, trains and certifies its pilots and registers its drones | Discarded for the pilot. The certification process takes months before the first spraying flight |
| Own brigades for mapping and a contractor for spraying | The Federation flies delimitation and estimation, and a contractor flies fumigation | Discarded. Two operators visit the same farms with two procedures, two insurance policies and two chains of evidence |

The contract keeps the platform, the flight data and the evidence with the Federation. The operator's staff use platform accounts the Federation grants and revokes. Moving the service to Federation brigades after the pilot therefore changes the contract and the people, and no part of the platform.

## 3. Roles

| Role | Belongs to | Does |
|---|---|---|
| Federation coordinator | Federation | Owns the drone service and the operator contract, and follows the permits and the yearly plan |
| Drone supervisor | Federation, one per department | Plans the campaigns of the department, maps no-fly zones, publishes polygons, reviews estimates and authorizes fumigations |
| Operator | Contracted company | Holds the operator certificate, registers the drones, employs the pilots, requests flight authorizations and reports incidents to Aerocivil |
| Pilot | Operator | Flies the mission, aborts it when it is unsafe, closes the flight log and uploads the objects |
| Farmer | Farm | Accepts the visit, shares what they know about the farm and sees the case |
| Collection center | Federation | Receives the harvest estimate |

The supervisor never works for the operator. The company that flies and is paid per flight never approves its own fumigation, and the person who answers for the farm's agronomy is a Federation employee.

The platform holds two separate groups for drone work, the brigade and the drone supervisors. No account belongs to both, as the [identity and access](../security/identity-and-access.md) document defines.

## 4. Responsibility matrix

Each activity has exactly one accountable role.

| Activity | Coordinator | Supervisor | Operator | Pilot | Farmer | Center |
|---|---|---|---|---|---|---|
| Contract the operator and follow its certificates | A, R | I | C | | | |
| Keep the operator certificate, drone registrations and pilot certificates valid | I | I | A, R | R | | |
| Plan the campaign of a department, with farms, route and dates | I | A, R | C | | I | I |
| Request the flight authorization with its risk analysis | I | C | A, R | | | |
| Map no-fly zones before the first flight | | A, R | | I | C | |
| Fly the delimitation and upload its objects | | I | A | R | I | |
| Review and publish the lot polygon | | A, R | | | C | |
| Fly the confirmation of an alert | | I | A | R | I | |
| Prepare the fumigation order with lot, reason, window, pilot and product lot | | A | R | C | C | |
| Accept the visit | | I | | | A, R | |
| Authorize the fumigation | | A, R | I | I | I | |
| Fly the fumigation and close its flight log | | I | A | R | I | |
| Abort a flight that has become unsafe | | I | I | A, R | | |
| Fly the verification | | I | A | R | I | |
| Fly the harvest estimation and record the field sample | | I | A | R | C | |
| Review the estimate and send it to the center | | A, R | | | I | I |
| Report an accident or incident to Aerocivil | I | I | A, R | R | | |

The pilot answers for the flight once the drone is in the air, which is why only the pilot is accountable for aborting it. The supervisor answers for whether a farm is treated at all, and the operator answers for how the flight is carried out.

## 5. Permits

### By holder

| Permit | Held by | What it needs | How the platform uses it |
|---|---|---|---|
| UAS operator certificate, specific category | Operator | Certification by Aerocivil | Its number and expiry date are stored with the operator |
| Registration of each drone on the UAS platform of Aerocivil | Operator | One registration per aircraft | Each drone in the platform carries its registration, and an unregistered drone cannot be assigned |
| Certificate of competence of the pilot | Each pilot | Theory exam and medical certificate, plus the spraying addition for fumigation pilots | Its expiry date is stored with the pilot, and an expired pilot cannot be assigned |
| Flight authorization | Operator, per department and campaign period | The authorization form and a risk analysis of the operation | Its reference and validity are stored with the campaign, and no mission package is issued outside them |
| Civil liability insurance | Operator | Policy for third-party damage | Its expiry date is stored with the operator |
| Platform account with a second factor | Pilot, supervisor | Granted by the Federation | Signs every mission, upload and authorization |

The supervisor and the farmer hold no aviation permit. The supervisor's power comes from the Federation and lives in the platform.

### By service

| Service | Permits that apply | Extra condition |
|---|---|---|
| Delimit the lot | Operator certificate, drone registration, pilot certificate, flight authorization | No-fly zones mapped before the first flight |
| Confirm the alert | The same | Published polygon |
| Fumigate | The same, with the spraying addition of the pilot | Authorized order, and the safety strips of agricultural spraying from the [lot boundaries](lot-boundaries-and-exclusions.md) |
| Verify | The same as confirmation | Closed fumigation |
| Estimate the harvest | The same as delimitation | Published polygon |

Drone spraying falls under the rules of agricultural aviation and Decree 1843 of 1991, as section 100.430 of RAC 100 states. Product, dose and mix stay outside this design.

## 6. Fumigation authorization

The authorizer of a fumigation is the drone supervisor of the farm's department, a Federation employee with a platform account protected by a second factor.

| Option | Result |
|---|---|
| Drone supervisor of the Federation, one per department | **Chosen.** Separates the company that flies from the person who decides to treat |
| Brigade lead of the operator | Discarded. Faster in the field, and the company paid per flight would approve its own work |
| The farmer | Discarded. The farmer cannot act alone, and the decision needs an agronomic review of the evidence |

The supervisor authorizes remotely, from any place with a connection, after reading the confirmation evidence of the focus. No one has to be at the lot. Before the authorization, the farmer is consulted and accepts the visit, and that acceptance is recorded with the order.

The platform accepts an authorization only when all of these hold.

| Rule | Why |
|---|---|
| The authorizer belongs to the supervisor group and to no brigade group | The company that flies never authorizes |
| The authorizer is the supervisor of the farm's department, or the backup named for it | Each farm has one clear authorizer |
| The authorizer differs from the assigned pilot | Separation of duties inside the order |
| The authorizer signed in with the second factor | A stolen password cannot authorize |
| The lot has a published polygon and a closed confirmation log | No order exists without them |
| The farmer accepted the visit | The farmer is never surprised by a spraying flight |
| The pilot, the drone and the campaign hold valid permits | No flight leaves under an expired permit |

The order then carries the farm, the lot, the reason, the window, the operator, the pilot, the drone, the flight authorization reference and the identity of the authorizer. After the flight, the platform also stores who flew, the product lot used and the closure of the flight log. No automated trigger can authorize. The [fumigation order](fumigation-order.md) defines the fields, the records and the states of the order.

## 7. Campaigns

A campaign is a planned round of one brigade through the farms of its department in one period. It carries the area work, which has no urgency and benefits from a planned route.

| Option | Result |
|---|---|
| Campaigns carry area work, and alert-driven missions run as soon as they are ready | **Chosen** |
| Weekly campaigns in harvest that also batch alert-driven missions | Discarded. Shorter routes, and a focus could wait a week, which can cost the crop the alert was meant to protect |

| A campaign carries | Detail |
|---|---|
| Harvest estimation | The farms whose harvest falls in that month, about 17 per brigade |
| Delimitation | New farms, and lots that changed by renovation, new plantings or sale |
| Review of no-fly zones | The supervisor checks houses, facilities, roads and water sources on the route |
| Permits | The flight authorization that covers the campaign period, checked before the first mission |
| Route | Municipalities in order, with the seats and collection centers where packages download and objects upload |

Alert-driven missions never wait for a campaign. When an alert opens a case, the confirmation enters the brigade's next field day, and the fumigation and the verification follow as soon as the order is authorized. During a campaign they take priority over estimation and delimitation flights, which can move within the month.

| Period | Campaigns per department | Content |
|---|---|---|
| Start-up, before the first harvest | One round of about two months | Delimitation of every farm and mapping of every no-fly zone |
| Harvest | One a month, four a year | Harvest estimation, plus any pending delimitation |
| Outside harvest | One every three months, two a year | Delimitation of changed lots, review of no-fly zones |

That gives six campaigns a year per department and eighteen in the pilot, plus the start-up round. Each department's committee gives the months of its main harvest, and its supervisor sets the dates.

## 8. Frequency in the pilot

The figures come from `tools/flight_frequency.py`, which takes the volumes of the operating mode and prints these tables. Outside harvest, alert-driven work is assumed at a quarter of the harvest rate.

| Service | Harvest month | Outside-harvest month | First year | Following years |
|---|---|---|---|---|
| Delimit the lot | 0 | 2 | 200 | 20 |
| Confirm the alert | 40 | 10 | 240 | 240 |
| Fumigate | 25 | 6 | 148 | 148 |
| Verify | 25 | 6 | 148 | 148 |
| Estimate the harvest | 50 | 0 | 200 | 200 |
| Total | 140 | 24 | 936 | 756 |

The first year carries 200 delimitations in the start-up round. After that, about one farm in ten needs a new polygon each year.

| Period | Missions a month per brigade | Missions per field day |
|---|---|---|
| Start-up round month | 41 | 2.0 |
| Harvest month | 47 | 2.3 |
| Outside-harvest month | 7 to 8 | 0.4 |

With 20 field days a month, a brigade flies about two missions a day in harvest, which leaves room for travel between farms on rural roads. Outside harvest, the brigades have spare capacity for maintenance, training and missions raised by symptoms.

The 9,000 images of a harvest month split into about 5,000 from the 50 estimation flights and about 4,000 from the 90 precision flights, or about 44 images per precision flight.

## 9. What fails and what happens then

| Failure | What the platform and the people do | Effect |
|---|---|---|
| The supervisor of the department is not available | The named backup, the supervisor of another department, authorizes. The brigade never does | The order waits for a supervisor |
| The farmer does not accept the visit | No order goes out. The case records the refusal and stays open | The focus stays untreated by the service |
| The flight authorization of the department expires or is not issued | The platform issues no mission package for that department | Flights wait for the authorization, and alert-driven missions are delayed |
| A pilot certificate or drone registration expires | The platform rejects the assignment | The operator assigns another pilot or drone |
| The operator loses its certificate or the contract ends | Every flight stops. The platform, the data and the evidence stay with the Federation | A new operator is contracted, with no platform change |
| A harvest month brings more foci than a brigade can fly | Alert-driven missions go first, and estimation flights move within the month | Estimates reach the center later |
| The pilot aborts a fumigation in the air | The flight log closes as aborted, and the order stays authorized within its window | The pilot flies again within the window, or the supervisor issues a new order |

## 10. Assumptions and pending confirmations

| Item | Who confirms | Effect if it fails |
|---|---|---|
| One flight authorization covers the operations of a brigade in its department for a campaign period, including alert-driven missions | The operator, with Aerocivil | Each mission needs its own request, and alert-driven missions wait for the response of Aerocivil |
| Each department has one main harvest a year inside the four harvest months, with months set by its committee | Federation | Campaign months shift, and a second estimation flight per farm may be needed for the secondary harvest |
| Outside harvest, foci, fumigations and verifications run at a quarter of the harvest rate | First pilot year | Outside-harvest load and yearly totals change |
| One farm in ten needs a new delimitation each year after the first | Supervisors, during the first year | Outside-harvest campaigns carry more or fewer delimitations |
| A brigade spends 20 days a month in the field | Operator | Missions per field day change |
| The Federation names one supervisor per department and a backup | Federation | Authorization slows down, and the brigade can never stand in |
| A contracted operator certified for spraying is available for the three departments | Federation, through the tender | The pilot starts with delimitation and estimation, and fumigation waits for a certified operator |
| The spraying addition of the pilot and the liability insurance come from secondary sources | Current text of RAC 100, legal review | Training time and operator cost change |

## 11. Sources

| Fact | Source |
|---|---|
| Open category for non-commercial use, specific category for commercial work, drone registration, operator certificate, pilot certificate with theory exam and medical certificate, flight authorization with a risk analysis | [Aerocivil, drones and urban air mobility](https://www.aerocivil.gov.co/preguntas-frecuentes/18/drones-y-movilidad-urbana-aerea/) |
| First operator certificate for spraying | [Aerocivil announcement](https://x.com/AerocivilCol/status/2051378340129394763) |
| Drone spraying refers to agricultural aviation and Decree 1843 of 1991 | RAC 100, section 100.430, as the [lot boundaries](lot-boundaries-and-exclusions.md) explain |
| Harvest calendar by region | The [Federation harvest page](https://federaciondecafeteros.org/cosecha-cafetera/) loads its calendar dynamically, and it could not be read. The harvest months remain an assumption |
