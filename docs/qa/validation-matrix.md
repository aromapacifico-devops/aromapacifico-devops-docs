# Requirements validation and failure scenarios

This document lets the Federation architect check that the design covers every requirement of the pilot and behaves safely when something fails. Section 2 maps each requirement of the challenge to the document or the code that answers it. Section 3 follows each failure scenario from its starting condition to the safe state the platform keeps, with the evidence behind it. A requirement or a scenario counts as covered by design when a document specifies it, and as built only when code exists and ran in an environment. Field trials, restore exercises and production measurements are named where they are still pending.

## Contents

1. [Terms and status values](#1-terms-and-status-values)
2. [Requirements of the challenge and their evidence](#2-requirements-of-the-challenge-and-their-evidence)
3. [Failure scenarios](#3-failure-scenarios)
4. [Required scenarios](#4-required-scenarios)
5. [Coverage summary](#5-coverage-summary)
6. [Gaps that stay open](#6-gaps-that-stay-open)

## 1. Terms and status values

| Term | Meaning |
|---|---|
| Requirement | A statement of the challenge that the pilot must satisfy |
| Evidence | The document, schema, check script or code that answers a requirement or a scenario |
| Safe state | What the platform keeps true while a failure lasts, so nothing is lost, invented or authorized by mistake |
| Platform operator | The person who runs the cloud platform, its alarms and its recovery |
| Center operator | The person who receives sacks and runs the network of a collection center |
| Drone operator | The contracted crew that flies the missions |
| Federation supervisor | The Federation person who authorizes fumigations and closes them |

| Status | Meaning |
|---|---|
| `BUILT` | Implemented in the infrastructure code and run in the test environment |
| `COVERED-DESIGN` | A document specifies the requirement or the scenario and its safe result. Nothing is deployed for it yet |
| `PARTIAL` | The design exists, and an assumption, a known gap or an unmeasured value remains |
| `PENDING-EXECUTION` | A procedure exists and has not run in an environment or in the field |
| `PENDING` | The deliverable is not finished yet, and the linked card tracks it |

## 2. Requirements of the challenge and their evidence

Each row is one requirement, in the order of the challenge. Links point to the document that answers it.

### Context and connectivity updates

| ID | Requirement | Evidence | Status |
|---|---|---|---|
| R-01 | Crop and drying monitoring with an alert to the farmer | [Telemetry ingestion](../iot/telemetry-ingestion.md), [configurable thresholds](../iot/configurable-thresholds.md), [alert delivery](../iot/alert-delivery.md) | `BUILT` for the ingestion path, `COVERED-DESIGN` for the alerts |
| R-02 | Harvest record and packing in 60 kg sacks | [Sack identity](../traceability/sack-identity.md), [sack states](../traceability/sack-states.md) | `COVERED-DESIGN` |
| R-03 | Trip tracking to the collection center and to Buenaventura | [Carrier tracking](../network/carrier-tracking.md), [carrier application contract](../traceability/carrier-application-contract.md), [port delivery](../network/port-delivery.md) | `COVERED-DESIGN` |
| R-04 | Sack lookup by code for the farmer, the center and the buyer | [Actor views](../traceability/actor-views.md), [public query](../traceability/public-query.md) | `COVERED-DESIGN` |
| R-05 | Drone service with the five services and a chosen operating mode | [Operating mode](../drones/operating-mode.md), [drones](../drones/README.md) | `COVERED-DESIGN` |
| R-06 | The platform hosts the farmer, carrier and web lookup applications without building them | [Overview](../architecture/overview.md), [design system](../design/design-system.md) | `COVERED-DESIGN` |
| R-07 | Farm without wired access publishes over cellular, with store-and-forward of 24 hours at most | [Farm connectivity](../network/farm-connectivity.md), [autonomous node](../iot/autonomous-node.md) | `PARTIAL`, field timing pending |
| R-08 | Farms out of coverage send readings and objects with no new base station and no weekly visit | [LoRa out of coverage](../network/lora-out-of-coverage.md) | `PARTIAL`, spectrum and site study pending |
| R-09 | The mission loads before takeoff, the log comes back over a defined link and fumigation waits for its closure | [Drone mission link](../network/drone-mission-link.md), [flight objects](../drones/flight-objects.md) | `COVERED-DESIGN` |
| R-10 | The carrier publishes its position at a fixed interval and keeps the right events without data | [Carrier tracking](../network/carrier-tracking.md), [carrier application contract](../traceability/carrier-application-contract.md) | `COVERED-DESIGN` |
| R-11 | Each center gets a segmented LAN with WAN exit to the cloud | [Collection center LAN](../network/collection-center-lan.md), [center WLAN](../network/center-wlan.md), [center cloud link](../network/center-cloud-link.md) | `COVERED-DESIGN` |
| R-12 | Buenaventura holds no Federation equipment and the platform records only the delivery event | [Port delivery](../network/port-delivery.md) | `COVERED-DESIGN` |
| R-13 | No dependence on a mobile network generation that the operator switches off | [Mobile network validity](../network/mobile-network-validity.md) | `COVERED-DESIGN` |

### Constraints and figures

| ID | Requirement | Evidence | Status |
|---|---|---|---|
| R-14 | Farm installation in one visit with little equipment | [Sensors and operation](../iot/sensors-and-operation.md), [farm hardware and monthly amount](../governance/farm-hardware-and-fee.md) | `COVERED-DESIGN` |
| R-15 | Moderate hardware cost and monthly amount for the farmer | [Farm hardware and monthly amount](../governance/farm-hardware-and-fee.md), [pilot cost](../governance/pilot-cost.md) | `PARTIAL`, items without price and quotes pending |
| R-16 | Few screens in the farmer application | [Farmer history](../iot/farmer-history.md), [design system](../design/design-system.md) | `COVERED-DESIGN` |
| R-17 | Who flies, who authorizes, with which permit and how often | [Roles, permits and campaigns](../drones/roles-permits-and-campaigns.md) | `COVERED-DESIGN` |
| R-18 | Infrastructure code in 2 weeks and 100 hours, with modules, variables, remote state and a plan of one environment | [Implementation scope](../architecture/implementation-scope.md), [infrastructure repository](https://github.com/aromapacifico-devops/aromapacifico-devops-infra) | `BUILT` |
| R-19 | Minimal fixed hardware on the farm, autonomous in energy, for high humidity and temperature | [Autonomous node](../iot/autonomous-node.md) | `COVERED-DESIGN` |
| R-20 | Main cloud chosen and justified, field and platform teams may differ | [Cloud selection](../governance/cloud-selection.md) | `COVERED-DESIGN` |
| R-21 | Network and ingestion scale from 200 to 1,000 farms with no new addressing or ingestion point | [Cloud addressing](../network/cloud-addressing.md), [ingestion sizing](../iot/ingestion-sizing.md) | `COVERED-DESIGN` |
| R-22 | Alert ranges configured by the Federation and never fixed in the device | [Configurable thresholds](../iot/configurable-thresholds.md) | `BUILT` for the initial ranges, `COVERED-DESIGN` for their changes |
| R-23 | Readings every 4 hours for crops and every hour for drying, with the initial ranges | [Sensors and operation](../iot/sensors-and-operation.md), [configurable thresholds](../iot/configurable-thresholds.md) | `COVERED-DESIGN` |
| R-24 | Alert in less than 5 minutes when a delivery route exists, and within 24 hours when the buffer drains | [Alert delivery](../iot/alert-delivery.md), [service levels](../architecture/service-levels.md) | `PARTIAL`, latency not measured |
| R-25 | 60 carriers with a position every 5 minutes, 400 sacks a day per center, 30 lookups a minute at peak | [Ingestion sizing](../iot/ingestion-sizing.md), [public query](../traceability/public-query.md) | `COVERED-DESIGN` |
| R-26 | Five years of readings, photos, flights and sack history | [Persistence and archive](../architecture/persistence-and-archive.md), [personal data and retention](../security/personal-data-and-retention.md) | `COVERED-DESIGN` |

### Drones

| ID | Requirement | Evidence | Status |
|---|---|---|---|
| R-27 | The first flight leaves the polygon and the no-spray zones, and no order leaves without them | [Lot boundaries and exclusions](../drones/lot-boundaries-and-exclusions.md) | `COVERED-DESIGN` |
| R-28 | The drone flies to the focus that the reading marked | [Alert to drone confirmation](../iot/alert-to-drone-confirmation.md), [focus confirmation mission](../drones/focus-confirmation-mission.md) | `COVERED-DESIGN` |
| R-29 | Fumigation only on a delimited lot with an authorized order that records who authorized, who flew, the window, the product lot and the flight closure | [Fumigation order](../drones/fumigation-order.md) | `COVERED-DESIGN` |
| R-30 | A photo or short path closes the case, and the fumigation stays open while it is missing | [Post-fumigation verification](../drones/post-fumigation-verification.md) | `COVERED-DESIGN` |
| R-31 | One area flight per harvest tells the center how many sacks come, with no spraying | [Harvest estimation](../drones/harvest-estimation.md) | `COVERED-DESIGN` |
| R-32 | The design states which event moves work from one mode to the other | [Operating mode](../drones/operating-mode.md) | `COVERED-DESIGN` |
| R-33 | No-fly zones live in the platform before the first flight, and the mission is prepositioned when the link falls | [Lot boundaries and exclusions](../drones/lot-boundaries-and-exclusions.md), [drone mission link](../network/drone-mission-link.md) | `COVERED-DESIGN` |

### Governance and security

| ID | Requirement | Evidence | Status |
|---|---|---|---|
| R-34 | Separate accounts for security, network, production and test | [Landing zone](../governance/landing-zone.md) | `COVERED-DESIGN`. The demonstration runs on one account with environments separated by name, state and role |
| R-35 | Policies, identities, tags and budgets from the root, with tags that feed cost by farms, drones, centers, trips and environments | [Tags, policies and budgets](../governance/tags-policies-and-budgets.md) | `BUILT` for tags and the account budget, `COVERED-DESIGN` for the rest |
| R-36 | Audit of a sack read, a threshold change, a telemetry publication and a flight object delivery | [Audit](../security/audit.md) | `COVERED-DESIGN` |
| R-37 | Record of what 2020 requirement stays and which component is retired | [Requirements 2020 and 2026](../governance/requirements-2020-2026.md) | `COVERED-DESIGN` |
| R-38 | Separate identities with least privilege, and MFA for center, drone and platform operators | [Identity and access](../security/identity-and-access.md) | `BUILT` for the platform roles, `COVERED-DESIGN` for people |
| R-39 | Encryption in transit and at rest, with no telemetry or drone object in the clear | [Encryption, secrets and revocation](../security/encryption-secrets-revocation.md) | `BUILT` for the platform keys, `COVERED-DESIGN` for devices |
| R-40 | The sack code exposes neither the farmer identity nor the full trace, and each actor sees only its view | [Sack identity](../traceability/sack-identity.md), [actor views](../traceability/actor-views.md) | `COVERED-DESIGN` |
| R-41 | Personal data of farmers and carriers kept 5 years | [Personal data and retention](../security/personal-data-and-retention.md) | `COVERED-DESIGN` |
| R-42 | A retired node or a lost drone has its identity revoked and stops publishing | [Encryption, secrets and revocation](../security/encryption-secrets-revocation.md) | `COVERED-DESIGN` |

### Network of the centers and the cloud

| ID | Requirement | Evidence | Status |
|---|---|---|---|
| R-43 | Segmented WLAN by zone with its own SSID, and visitors with no route to logistics or management | [Center WLAN](../network/center-wlan.md), [collection center LAN](../network/collection-center-lan.md) | `COVERED-DESIGN` |
| R-44 | 2 Mbps down and 0.5 Mbps up per active client, with control of non-operational traffic | [Center WLAN](../network/center-wlan.md), [center WAN sizing](../network/center-wan-sizing.md) | `COVERED-DESIGN` |
| R-45 | Perimeter firewall at each center and a cloud firewall, with a policy table that marks pilot and temporary rules | [Firewall policy](../security/firewall-policy.md) | `BUILT` for the cloud rules, `COVERED-DESIGN` for the centers |
| R-46 | Cloud addressing outside 10.41 to 10.43, seven minimum subnets and separate ranges for each environment | [Cloud addressing](../network/cloud-addressing.md) | `BUILT` |
| R-47 | WAN of 100 Mbps symmetric at each center | [Center WAN sizing](../network/center-wan-sizing.md), [center cloud link](../network/center-cloud-link.md) | `COVERED-DESIGN`, operator quote pending |
| R-48 | Data paths of farm telemetry, carrier positions and drone objects | [Telemetry ingestion](../iot/telemetry-ingestion.md), [carrier tracking](../network/carrier-tracking.md), [flight objects](../drones/flight-objects.md) | `BUILT` for telemetry, `COVERED-DESIGN` for the others |

### Automation and change

| ID | Requirement | Evidence | Status |
|---|---|---|---|
| R-49 | Code of the network, security and one environment, with the reusable module of one farm | [Implementation scope](../architecture/implementation-scope.md), [infrastructure repository](https://github.com/aromapacifico-devops/aromapacifico-devops-infra) | `BUILT` |
| R-50 | Pipelines of the platform, the ingestion and the reception of flight objects | [Delivery pipelines](../architecture/delivery-pipelines.md) | `BUILT` for the platform, `COVERED-DESIGN` for ingestion and flight reception |
| R-51 | Development, test and production with controlled promotion | [Environments and promotion](../architecture/environments-and-promotion.md) | `BUILT` |
| R-52 | Secrets out of the repository and out of the state | [Encryption, secrets and revocation](../security/encryption-secrets-revocation.md), [verification of the infrastructure code](https://github.com/aromapacifico-devops/aromapacifico-devops-infra/blob/main/docs/verification.md) | `BUILT` |
| R-53 | Two release note templates, each filled with an example | [Release notes](../release-notes/README.md) | `COVERED-DESIGN` |
| R-54 | No production change from 05:00 to 18:00 in a harvest week, except for an incident | [Delivery pipelines](../architecture/delivery-pipelines.md) | `BUILT`, harvest calendar pending from the Federation |

### Workloads

| ID | Requirement | Evidence | Status |
|---|---|---|---|
| R-55 | Crop and drying ingestion with the thresholds of the figures | [Telemetry ingestion](../iot/telemetry-ingestion.md), [configurable thresholds](../iot/configurable-thresholds.md) | `BUILT` |
| R-56 | History for the farmer and for the pilot report | [Farmer history](../iot/farmer-history.md) | `COVERED-DESIGN` |
| R-57 | A visible symptom enters through the drone confirmation service | [Alert to drone confirmation](../iot/alert-to-drone-confirmation.md) | `COVERED-DESIGN` |
| R-58 | A review campaign a month in harvest and every three months outside it | [Roles, permits and campaigns](../drones/roles-permits-and-campaigns.md), [drone campaign cost](../drones/campaign-cost-estimation.md) | `COVERED-DESIGN` |
| R-59 | Sack states, registration, handoffs, center arrival, departure and delivery, each with date, time and responsible | [Sack states](../traceability/sack-states.md), [custody chain](../traceability/custody-chain.md) | `PARTIAL`, real database test pending |
| R-60 | The public lookup shows only the buyer view | [Public query](../traceability/public-query.md), [actor views](../traceability/actor-views.md) | `COVERED-DESIGN` |
| R-61 | A deployment loses no sack event, with RPO of 15 minutes and RTO of 4 hours for the public lookup | [Recovery](../architecture/recovery.md), [delivery pipelines](../architecture/delivery-pipelines.md) | `PENDING-EXECUTION`, first restore not measured |
| R-62 | WiFi and firewall of the inventory, logistics stations, printing of code sheets and the same pattern three times | [Collection center operations](../network/collection-center-operations.md), [collection center LAN](../network/collection-center-lan.md) | `COVERED-DESIGN` |
| R-63 | Event-driven functions that read a stored object, call managed inference and write the result | [Inference functions](../architecture/inference-functions.md) | `BUILT` for the infrastructure of focus confirmation, `COVERED-DESIGN` for its code and the other functions |
| R-64 | Telemetry in a transactional or time-series store, objects in object storage, sack events and orders in a transactional store | [Persistence and archive](../architecture/persistence-and-archive.md) | `BUILT` for telemetry, `COVERED-DESIGN` for the others |
| R-65 | Each result in the case record with timestamp, confidence and source object | [Inference functions](../architecture/inference-functions.md) | `COVERED-DESIGN` |
| R-66 | Four triggers with their limits, none of them authorizes a fumigation | [Inference functions](../architecture/inference-functions.md) | `COVERED-DESIGN` |
| R-67 | Retries, failure queue and where the error is seen, with the source object and the case unchanged | [Failure policy](../architecture/failure-policy.md) | `PARTIAL`, rule dead letter queue not yet in the module |
| R-68 | Service Region, objects that leave the country and cost per 1,000 invocations in harvest | [Inference data egress](../security/inference-data-egress.md), [inference cost](../governance/inference-cost.md) | `COVERED-DESIGN` |
| R-69 | An object with a person never reaches inference, and its handling is documented | [Inference data egress](../security/inference-data-egress.md), [flight objects](../drones/flight-objects.md) | `PARTIAL`, threshold needs real images |

### Observability

| ID | Requirement | Evidence | Status |
|---|---|---|---|
| R-70 | Metrics, logs and traces of ingestion, applications, database, the three WAN links and flight object arrival | [Observability](../architecture/observability.md) | `COVERED-DESIGN` |
| R-71 | Nodes and farms silent over 24 hours, undelivered crop alerts, flights without a stored record, fumigations without closure and failed invocations | [Operational alarms](../architecture/operational-alarms.md) | `PARTIAL`, two alarms built, the rest designed and pending operational validation |
| R-72 | Two SLOs with their SLIs, crop alert delivery and sack lookup availability | [Service levels](../architecture/service-levels.md) | `PARTIAL`, no observed SLI yet |
| R-73 | Operations and cost dashboards split by the tags of farms, drones, centers and tests | [Dashboards](../architecture/dashboards.md) | `COVERED-DESIGN` |

### Design system, cost and deliverables

| ID | Requirement | Evidence | Status |
|---|---|---|---|
| R-74 | Logo, isotype and one-ink and negative versions, palette with sack states and crop alert, type, spacing and grid | [Visual identity](../design/visual-identity.md) | `COVERED-DESIGN` |
| R-75 | Base components and usage rules applied to the three applications in one sheet | [Design system](../design/design-system.md) | `COVERED-DESIGN` |
| R-76 | Cost of the normal month, harvest month, farm hardware and drone campaign at current prices, with at least three savings decisions | [Pilot cost](../governance/pilot-cost.md) | `COVERED-DESIGN`, quotes pending |
| R-77 | Plan of the 100 hours with owner, order and dependency, each task pointing to a box of the diagram | [Implementation scope](../architecture/implementation-scope.md), planning workbook in `docs/planning/` | `BUILT` |
| R-78 | Architecture document of the seven points with the complete diagram | [Overview](../architecture/overview.md), [architecture diagrams](../architecture/diagrams/) | `PENDING`, the integrated document is tracked in [T-08](https://github.com/aromapacifico-devops/aromapacifico-devops-docs/issues/65) |
| R-79 | Presentation of 20 minutes to a Federation architect | Tracked in [T-09](https://github.com/aromapacifico-devops/aromapacifico-devops-docs/issues/66) | `PENDING` |
| R-80 | Every assumption outside the challenge is written down | [Assumptions](../assumptions.md) | `COVERED-DESIGN` |

## 3. Failure scenarios

Each row follows one failure from its starting condition to the safe state. Scenarios marked complementary go beyond the eight that the challenge names.

| ID | Requirement | Component | Scenario | Initial condition | Event or failure | Expected result | Safe state | Evidence | Verification | Responsible | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| V-01 | Monitor crop and drying despite intermittent coverage | Farm node, local flash buffer, IoT Core, ingestion queue | Farm without signal | The node has a valid identity, clock and free buffer; a reading is due | No cellular path at wake-up | Stop the attempt after 120 seconds, retain unconfirmed readings, retry next hour, purge only records aged 24 hours or more and report `dropped_total` | No fabricated current reading; last platform state remains; loss after the retention limit is counted | `docs/governance/requirements-2020-2026.md`, sections 3 and 6; `docs/network/farm-connectivity.md`, sections 5, 8 and 10; `docs/iot/alert-delivery.md`, sections 3 and 9 | Documentary review; simulation evidence in farm connectivity is not a field test | Platform operator | `PARTIAL`: field and LoRa timing measurements remain pending |
| V-02 | Deliver a crop alert in less than 5 minutes when live and within 24 hours when buffered | Alert delivery, SNS, farmer application | Offline reading raises an alert after reconnection | Reading is retained for less than 24 hours and later reaches ingestion | Signal returns and the node drains old readings | Evaluate with the range version valid at measurement time, mark the alert `drained`, retain the original time and avoid reopening a newer state | Newer alert state wins; an old condition stays in the history | `docs/iot/alert-delivery.md`, sections 3, 9 and 10; `docs/architecture/service-levels.md`, section 2 | Static SLO calculations; test/field latency still required | Platform operator | `PARTIAL`: target defined, observed SLI not found |
| V-03 | Load the exact mission before takeoff and require a closed flight record before downstream action | Signed mission package, station, drone, flight record | Drone without a flight record | A signed, unexpired package was acknowledged by station and drone | Flight lands but the closed log or a mandatory object is absent, corrupt or not uploaded | Do not publish `flight.record.published`; retry resumable upload and report the flight/order by age | No inference starts and no fumigation can be authorized from that execution | `docs/governance/requirements-2020-2026.md`, section 6; `docs/network/drone-mission-link.md`, sections 7 to 10; `docs/drones/flight-objects.md`, sections 6 to 10 | Contract/schema checkers and documentary review; no real flight claimed | Drone operator | `COVERED-DESIGN` |
| V-04 | Preserve custody and useful trip tracking without mobile data | Carrier application, encrypted phone store, public API | Carrier without data | Authenticated session is still valid; trip is open; encrypted storage is available | Phone loses data while custody events and positions are captured | Queue both locally, retain custody until acknowledged, send custody before positions on return, drop/count positions older than 24 hours | Custody does not advance in the platform until its immutable event is stored; the phone refuses sign-out with pending custody | `docs/traceability/carrier-application-contract.md`, sections 4, 6 and 9; `docs/network/carrier-tracking.md`, offline and failure sections; `docs/traceability/custody-chain.md`, sections 7 and 13 | Documentary contract review; device interruption test remains required | Platform operator | `COVERED-DESIGN` |
| V-05 | Continue center reception during a WAN outage | Center LAN/application queue, printer, VPN/WAN | WAN connectivity loss | Center application and local queue are operating on the segmented LAN | Center WAN fails and both VPN tunnels fall | Queue reception/custody events locally, continue permitted local printing, synchronize oldest pending events when WAN returns | No cloud state is guessed; unacknowledged events remain local | `docs/architecture/overview.md`, section 5; `docs/network/center-cloud-link.md`, sections 7 and 8; `docs/network/collection-center-operations.md`, offline operation section | Design review; first-center failover and outage measurements are pending | Center operator | `PARTIAL`: WAN recovery duration is explicitly not promised |
| V-06 | Tolerate failure of one VPN tunnel | Site-to-site VPN and center firewall | Complementary: one tunnel endpoint fails | WAN and the other tunnel are healthy | One of two AWS tunnels becomes unavailable | Route through the second tunnel and alarm on `TunnelState` | Center remains connected; no queued event is discarded | `docs/network/center-cloud-link.md`, sections 7 and 8; `docs/architecture/observability.md`, section 8 | Tunnel-state design review; appliance failover time must be measured at the first center | Center operator and platform operator | `PARTIAL`: tunnel alarm designed, appliance failover time not measured |
| V-07 | Allow fumigation only with valid permits, role and human authorization | Cognito roles, campaign/permit records, fumigation state machine | Permission denied | A user or function requests an authorization or launch transition | Actor lacks the required role, certificate, valid permit, second factor or current revision | Reject the transition, record the denied audit event and block launch/authorization | Order remains in its previous state; no spray payload becomes executable | `docs/drones/roles-permits-and-campaigns.md`, sections 3 to 6 and 9; `docs/drones/fumigation-order.md`, authorization and failure sections; `docs/network/drone-mission-link.md`, sections 3 and 9 | `docs/drones/tools/check_order_states.py`; IAM/deployed authorization test remains required | Federation supervisor | `COVERED-DESIGN` |
| V-08 | Keep rejection and its reason in the immutable sack history | Sack state machine, custody events, center application | Sack rejection | Sack arrives at a center or port with an existing history | Center records `received_rejected` or port records `delivered_rejected` | Append rejection with weight, reason and responsible identity; derive the rejected state; require an explicit correction/return event for later movement | Prior events stay immutable; rejection is visible and cannot be silently overwritten | `docs/traceability/sack-states.md`, sections 3, 7 to 9; `docs/traceability/custody-chain.md`, sections 4, 10, 11 and 13 | State replay/document review and local concurrency evidence; real DynamoDB test remains pending | Center operator | `PARTIAL`: production-service concurrency test is pending |
| V-09 | Reject invalid sack codes and preserve late/out-of-order evidence | Sack identity, custody replay, anomaly review list | Complementary: forged, duplicated or out-of-order sack event | A device submits an event with a check failure, unissued code, duplicate ID or missing predecessor | Validation or replay detects the defect | Reject a bad check symbol; retain well-formed unissued codes as anomalies; retain missing predecessors as gaps; answer duplicate IDs as repeated | Current sack projection is derived from valid logical history and does not regress | `docs/traceability/custody-chain.md`, sections 6 to 10 and 13; `docs/traceability/sack-states.md`, sections 6, 8 and 9 | Local replay/concurrency evidence only; cloud transaction test pending | Platform operator | `PARTIAL` |
| V-10 | A failed inference must leave source objects and business state unchanged | EventBridge, SQS work queue, Lambda, S3, DynamoDB | Inference failure | A verified flight record or complete telemetry object is queued | Model, dependency, timeout, permission or code failure exhausts one initial attempt plus three retries | Retain source and partial technical evidence, move the message to the function DLQ, alarm, permit controlled redrive or audited supervisor fallback | Case/order/current alert remains unchanged; no success event is emitted without a stored result | `docs/architecture/failure-policy.md`, sections 3 to 8; `docs/drones/post-fumigation-verification.md`, sections 8 and 11 | Observability and state-machine checkers; deployment/DLQ exercise not found | Platform operator | `PARTIAL`: alarms designed, no dead letter queue exercise run |
| V-11 | Do not lose an inference request before it reaches the work queue | EventBridge rule and rule DLQ | Complementary: EventBridge cannot deliver to SQS | A valid source event matches the rule | Queue/key permission is wrong or delivery retries expire | Capture the event in a rule-specific DLQ and alarm on failed delivery; resend only after the cause is fixed | Source and business state remain unchanged; no false success | `docs/architecture/failure-policy.md`, sections 6 to 8 and 11 | Documentary review only; current module gap and redrive assumptions are explicitly recorded | Platform operator | `PARTIAL`: the rule dead letter queue is designed and not yet in the inference module |
| V-12 | Protect personal data in drone images | Rekognition person filter, restricted S3 prefix | Complementary: person appears in a photo | Exact source version and hash were verified | Person filter exceeds the privacy-biased threshold | Copy to `restricted/`, verify restricted version/hash, then remove original; skip model inference and request recapture/review | No personal image reaches the model; business state does not advance from the withheld image | `docs/architecture/failure-policy.md`, section 5; `docs/drones/flight-objects.md`, privacy path; `docs/security/inference-data-egress.md` | Documentary path review; real-image calibration is pending | Platform operator | `PARTIAL`: threshold requires real-image review |
| V-13 | Preserve valid work and recover inference after the cause is fixed | Function DLQ, operator runbook, idempotent result | Service recovery after inference outage | Failed messages are retained and the dependency/permission/code defect is fixed | Operator starts a bounded redrive | Re-run schema, lineage, version, hash, privacy and authorization gates; reuse stored idempotent results; observe queue, DLQ and state invariants | At most one logical result; no blind business transition; unsafe messages return to DLQ | `docs/architecture/failure-policy.md`, sections 8 and 11; `docs/architecture/operational-alarms.md`, response routes | Runbook review; no executed redrive evidence found | Platform operator | `PENDING-EXECUTION` |
| V-14 | Restore sack history with RPO 15 minutes and public query within RTO 4 hours | DynamoDB PITR, event replay, IaC and public query | Service recovery after table corruption/deletion | Both sack tables have PITR, deletion protection and immutable events | State table is corrupt or tables are deleted/emptied | Choose one restore point, restore both tables under new names, reapply controls, replay/compare, switch configuration and verify the public query | Damaged tables are not overwritten; event/state consistency is checked before cutover | `docs/architecture/recovery.md`, sections 1, 3, 5 and 6 | Procedure and 3 h 30 min budget documented; first measured restore explicitly pending | Platform operator | `PENDING-EXECUTION` |
| V-15 | A deployment must not lose sack events | Delivery pipeline, sender retry, queues and idempotency | Complementary: bad deployment | A new function version is being promoted while senders may submit events | Requests fail or function returns after committing | Roll back function; senders retain unacknowledged events; repetitions return stored or write once; reject plans that replace sack tables | Immutable event history remains authoritative | `docs/architecture/recovery.md`, sections 2 and 4; `docs/architecture/delivery-pipelines.md`, rollback sections | Static pipeline/design review; no production rollback exercise claimed | Platform team | `COVERED-DESIGN` |
| V-16 | Measure availability of buyer sack lookup | CloudFront, WAF, public lookup function, sack tables | Complementary: public query outage | Valid buyer lookup traffic exists in the rolling 30-day window | Query returns 5xx/429, times out or cannot read restored tables | Count the lookup as bad, spend error budget, recover the public query within 4 hours and validate the buyer view | No unauthenticated write path; unavailable is safer than inconsistent history | `docs/architecture/service-levels.md`, sections 3 to 5; `docs/architecture/recovery.md`, sections 1 and 5; `docs/traceability/public-query.md` | SLI formulas/checker; observed SLO and restore duration not found | Platform operator | `PARTIAL` / `PENDING-EXECUTION` |
| V-17 | Detect node/vereda silence and operational failures | CloudWatch metrics, saved queries, EventBridge/SNS response routes | Complementary: shared gateway or many nodes go silent | Expected hourly telemetry baseline exists | Gateway/tower/farm path fails for 24 hours | Retain node buffers within their limit; raise the designed silence alarm and route it to the responsible owner | No invented telemetry or automatic unsafe agricultural action | `docs/network/lora-out-of-coverage.md`, delivery and pending-confirmation sections; `docs/architecture/operational-alarms.md`, sections 4, 8 and 12 | Alarm catalog checker is static; route/deployment and radio site study are pending | Platform operator | `PARTIAL`: alarm designed, radio site study pending |
| V-18 | Close fumigation only after independent verification | Verification mission, inference result, guarded transition, supervisor closure | Complementary: verification never arrives or is insufficient | Order is `VERIFICATION_PENDING` after an application | No record, aborted flight, missing photo, low coverage or failed inference | Keep the order open, schedule another attempt or allow audited supervisor review only under the documented DLQ guard | Order cannot reach `CLOSED` automatically; only the supervisor closes | `docs/drones/post-fumigation-verification.md`, sections 6 to 11; `docs/drones/fumigation-order.md`, state machine | `docs/drones/tools/check_order_states.py`; no field verification marked passed | Federation supervisor | `COVERED-DESIGN` |

## 4. Required scenarios

| Required scenario | Rows | Result |
|---|---|---|
| Farm without signal | V-01, V-02 | Covered by design, field timing pending |
| Drone without a flight record | V-03 | Covered by design, the publication gate blocks inference and authorization |
| Carrier without data | V-04 | Covered by design, custody first on reconnection |
| Permission denied | V-07 | Covered by design, the order keeps its state |
| Sack rejection | V-08 | Covered by design, real database test pending |
| WAN connectivity loss | V-05, V-06 | Covered by design, failover and outage times not measured |
| Inference failure | V-10, V-11 | Covered by design, the rule dead letter queue is not yet in the module |
| Service recovery | V-13, V-14 | Procedures written, redrive and restore not yet run |

## 5. Coverage summary

| Area | Design | Built or run | Overall |
|---|---|---|---|
| Architecture and trust boundaries | Overview and diagrams | Diagram and link checks | `COVERED-DESIGN` |
| Farm connectivity and offline operation | Buffer, retry, expiry, duplicates and late readings | Ingestion path built and its smoke test passed in test. Field and LoRa measurements pending | `PARTIAL` |
| Transport and custody | Offline queue, idempotency, immutable events, replay, gaps and anomalies | Local concurrency test only | `PARTIAL` |
| Drone objects and flight record | Manifest, hashes, versions, resumable upload and publication gate | Schema and contract checks | `COVERED-DESIGN` |
| Permits and fumigation | Human authorization, denied transitions and the verification gate | State machine check | `COVERED-DESIGN` |
| Inference failure policy | Retries, two dead letter layers, unchanged state and redrive | Work queue, dead letter queue and two alarms built. Rule dead letter queue and redrive exercise pending | `PARTIAL` |
| Observability and alarms | Signal catalog, thresholds, owners and routes | Two alarms built, the rest designed | `PARTIAL` |
| Service levels | Two SLIs, windows and error budgets | No production observation yet | `PARTIAL` |
| Recovery | Point-in-time restore, sequence and a budget of 3 h 30 min | First restore not measured | `PENDING-EXECUTION` |
| Infrastructure code | Network, security, ingestion, farm, inference pattern and pipelines | Planned, applied and destroyed in test, with the smoke test passed | `BUILT` |

## 6. Gaps that stay open

| Gap | Effect | What closes it |
|---|---|---|
| The inference module lacks the rule dead letter queue and its failed delivery alarm | An event that EventBridge cannot deliver to the work queue is lost after its retries | A new version of the inference module with the rule queue, its policy and the alarm |
| Four receives before the dead letter queue, while the Lambda guide recommends at least five | A throttled message may reach the dead letter queue sooner than needed, and a supervised redrive recovers it | A load test in test that confirms or raises the count |
| The first restore of the sack tables is not measured | The RTO of 4 hours rests on a budget of 3 h 30 min | A restore exercise once the sack tables exist |
| Several SLI inputs need the first harvest | The error budgets are calculated and not observed | The first harvest month in production |
| The LoRa path waits on the spectrum classification, the regional plan and the dwell time | Farms out of coverage are designed and not approved for field use | A radio site study and the regulatory confirmation |
| Alarms beyond the two of the inference module are designed only | Most operational signals have no deployed route yet | The alarm code in the modules and a first exercise in test |
| The person filter threshold is set without real images | Some photos with people may pass, or crop photos may be withheld | A calibration with real images from the first campaigns |
