# Requirements kept, replaced and retired from the 2020 design

The 2020 pilot design was never deployed. The Federation resumes it in 2026 with the same territory and the same capabilities, and with a connectivity premise that no longer holds. This document records what survives, what changes, what leaves the design, and the reason for each one. It exists so that no outdated premise reaches the platform unnoticed.

## Contents

1. How to read the matrix
2. Capabilities
3. Connectivity premises
4. Sites
5. Products and prices
6. New requirements with no 2020 equivalent
7. Effect on the design

---

## 1. How to read the matrix

| Decision | Meaning |
|---|---|
| Kept | The requirement stands as it was |
| Replaced | The need stands, and the 2020 way of meeting it does not |
| Retired | The element leaves the design |
| Retired as invalid | The value is out of date and cannot be reused, even as a reference |

## 2. Capabilities

| Requirement | Decision | Reason | Affected component |
|---|---|---|---|
| Territory of Cauca, Huila and Tolima | Kept | The pilot keeps its scope | All |
| Crop and drying monitoring with an alert to the farmer | Kept | It is the core of the service to the farmer | Ingestion, alerts |
| Harvest and packing record in 60 kg sacks | Kept | Traceability starts here | Sack events |
| Trip tracking to the center and to Buenaventura | Kept | It proves custody along the route | Carrier application, trip events |
| Sack lookup by code for farmer, center and buyer | Kept | It is the visible product for the buyer | Sack query |
| Drone service with its five services | Kept | Each service answers a different need | Drones, objects, inference |

## 3. Connectivity premises

| Requirement or premise | Decision | Reason | Affected component |
|---|---|---|---|
| Data coverage on most farms | Replaced | Some pilot farms lie outside coverage, so a design that needs signal leaves them out | Store-and-forward, shared gateway |
| Device publishing straight to the ingestion point | Replaced | With no signal the reading would be lost | Node buffer of 24 hours at most |
| Weekly visits to farms | Retired | Travel is difficult, and a visit must not be a data path | Remote connectivity, drone confirmation |
| Dependence on a mobile generation being shut down | Retired | The access network changed, and the design must survive the pilot | Node modem on LTE |

## 4. Sites

| Requirement or premise | Decision | Reason | Affected component |
|---|---|---|---|
| Collection centers with no LAN | Replaced | Each center needs a segmented network | LAN, WLAN, firewall |
| Collection centers with no WAN | Replaced | Reception must reach the platform | 100 Mbps link, VPN |
| Port with no LAN or WAN | Replaced | The Federation deploys nothing in Buenaventura. The shipping company keeps its telemetry, and the platform records only the delivery of the sack | Delivery event |

## 5. Products and prices

| Element | Decision | Reason | Affected component |
|---|---|---|---|
| 2020 prices | Retired as invalid | They do not reflect current quotations | Cost document |
| 2020 devices | Retired as invalid | They do not reflect current specifications | Farm node, drone |
| 2020 cloud services | Retired as invalid | Services and prices changed, and the platform uses current ones | Cloud architecture |

## 6. New requirements with no 2020 equivalent

| Requirement | Reason | Component |
|---|---|---|
| Local buffer that retains 24 hours at most | Limits how stale a reading can be | Farm node |
| Mission loaded before takeoff | The drone flies far from any phone | Drone service |
| Flight log closed before fumigation is authorized | A fumigation needs a verified basis | Drone service |
| Inference that ends when the result is stored | No compute waits for objects | Functions |
| Network that grows from 200 to 1,000 farms | The pilot must scale with no redesign | Cloud network, ingestion |
| Five-year retention, personal data rules and audit | The platform handles personal data | Security, storage |

## 7. Effect on the design

Three changes shape the whole architecture.

| Change | Consequence |
|---|---|
| Coverage is no longer assumed | Every device buffers, and every flow defines its behavior with no signal |
| Centers and the port are now part of the design | Connectivity covers five kinds of site |
| Nothing from 2020 prices or products is reused | Costs and specifications start from current sources |
