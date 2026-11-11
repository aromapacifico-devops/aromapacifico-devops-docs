# Platform overview

This document explains the complete platform in one reading. It covers what the pilot must achieve, the shape of the solution, why that shape fits a pilot with little connectivity and little budget, how each flow works when everything is fine and when it is not, and where each of the seven subjects of the proposal is developed. The documents listed at the end carry the detail.

In the diagram, blue boxes are what the infrastructure code implements. White boxes are designed and documented, and they stay out of the code.

![Target platform on AWS, from the farm to the port of Buenaventura](diagrams/00-platform-overview.drawio.png)

## Contents

1. What the pilot needs
2. The solution in one page
3. Why this shape
4. The six flows
5. What happens when something fails
6. Scale from 200 to 1,000 farms
7. Monthly cost of the cloud platform
8. What the infrastructure code builds
9. Environments
10. Where each subject is developed

### Terms used

| Term | Meaning in this document |
|---|---|
| Node | Autonomous device on a farm that reads probes and publishes readings |
| Store-and-forward | The device keeps a reading while it has no signal and sends it when the path returns |
| Data mule | A person or vehicle already traveling a route who carries data from a site with no signal |
| Case | The record that follows a pest from the alert to the verified fumigation |
| Expediente | Same as case. The result of every function is written there |
| Trust boundary | The line where the platform stops trusting the network and starts checking identity |
| Presigned URL | A temporary address that lets one client upload one object, with no stored credential |
| Landing zone | The set of accounts and rules that exist before any workload |

---

## 1. What the pilot needs

The pilot follows coffee from the farm to the buyer in three departments. Five capabilities carry over from the design of 2020, and the connectivity assumption behind that design no longer holds.

| Capability | What it means in numbers |
|---|---|
| Crop and drying monitoring, with an alert to the farmer | 200 farms, with a reading every 4 hours in cultivation and every hour in drying. The alert arrives in under 5 minutes with a delivery path, and within 24 hours with no signal |
| Harvest and packing record | Up to 400 sacks a day at each of the 3 centers |
| Trip tracking | 60 carriers, one position every 5 minutes |
| Sack lookup | Peaks of 30 reads a minute in harvest, available within 4 hours of a failure |
| Drone service | Five services that do not replace one another |

Two requirements apply across all of them.

| Requirement | What it means in numbers |
|---|---|
| Retention | Five years for readings, photos, flights, sack history and personal data |
| Recovery | Sack events lose at most 15 minutes |

The hard part is the field. Farms have no cable, some have no signal, drones fly far from any phone, and each center starts with no network at all. The load itself is small, and the design treats it that way.

## 2. The solution in one page

Sites at the edge hold their data until a path exists. A serverless platform in AWS receives each event, stores it once, and runs a function that ends when its result is written. Between events, nothing runs and almost nothing is billed.

| Zone | What lives there | Key decision |
|---|---|---|
| Field | Solar nodes, LoRa nodes, shared gateways, drones and phones | Each device buffers locally and needs no local server |
| Collection centers | One LAN pattern repeated three times, with [perimeter firewall](../security/firewall-policy.md) and a dedicated 100 Mbps WAN | The second octet is the only difference between centers |
| Governance | Seven accounts under one AWS Organization | Controls apply from the root, and every account inherits them |
| Production | IoT Core, API Gateway, functions, queues, DynamoDB, S3, Bedrock | No servers, no instances, no idle compute |
| Network | One VPC per environment, with seven subnets and a VPN per center | The VPC exists for the path from the centers |
| Security and observability | KMS, Secrets Manager, CloudTrail, GuardDuty, CloudWatch | Separate account, so a compromised workload cannot erase its trail |
| Delivery | Repositories, pipeline, remote state | Plan, a person approves, then apply |
| Second cloud | Azure East US | Prepared with contracts and nothing running |

## 3. Why this shape

**Event-driven and serverless.** The load is about 11,000 messages a day in harvest, counting device readings and carrier positions, which is 0.13 messages a second. A server sized for that would sit idle almost all the time, and the budget of the pilot cannot justify it. Persistent compute waiting for objects is also ruled out for the pilot.

**Buffer at the edge.** Coverage cannot be bought with the budget of a farm. A device that holds its data for up to 24 hours turns a connectivity problem into a delay, and the alert path tolerates that delay by definition.

**One regional endpoint.** Every farm publishes to the same address. Adding a farm means adding a certificate, with no change to the network, which is what lets the pilot grow to 1,000 farms with no redesign.

**Managed inference.** No model is trained. A function starts on a verified flight record or a completed telemetry object, reads the exact stored version, calls a managed service and writes an idempotent result. Replacing the model later touches one configuration value.

**A person decides.** Functions confirm, classify and estimate. Only a named person authorizes a fumigation, and no trigger can do it. This follows from the risk of the action, since a wrong fumigation cannot be undone.

## 4. The six flows

| Flow | Path | Identity | Protocol |
|---|---|---|---|
| 1. Telemetry | Node, IoT Core, SQS, ingestion function, DynamoDB, with a second copy through Firehose to S3 | X.509 certificate per device | MQTT over TLS |
| 2. Crop alert | Ingestion function, SNS, farmer's phone | IAM role of the function | Mobile push |
| 3. Sack, trip and order events | Application, API Gateway, domain function, DynamoDB transaction | Cognito token, MFA at centers and for drones | HTTPS, or IPsec from a center |
| 4. Drone objects | Ground station, S3, EventBridge, work queue, inference function, Rekognition, Bedrock, case | Cognito token and presigned URL | HTTPS, or IPsec from a center |
| 5. Public query | Browser, CloudFront with WAF, lookup function through its function URL | None, read by code | HTTPS |
| 6. Infrastructure delivery | Pull request, plan, approval, apply | GitHub OIDC role | HTTPS |

The buyer flow deserves a note. A buyer does not sign in, so the sack code works as a capability to read one sack. The code is random and reveals nothing, and the response holds only the buyer view. Every read is [audited](../security/audit.md).

## 5. What happens when something fails

| Failure | What the platform does | What is lost |
|---|---|---|
| Node loses signal | Stores readings and retries each hour | Nothing in an outage of up to 23 hours. Older readings are dropped and counted |
| Shared gateway fails | Nodes keep buffering, and an alarm reports the silent vereda | Nothing in an outage of up to 23 hours |
| Carrier loses data | The application queues positions and custody events, and sends custody first on return | No custody event. Positions older than 24 hours are dropped and counted |
| Center loses WAN | Staff keep receiving sacks in the application queue, and the printer works on the local network | Nothing, it synchronizes on return |
| Tunnel fails | The second tunnel of the same connection takes over | Nothing |
| Function fails | Three retries, then the dead letter queue and an alarm | Nothing. The object stays and the case does not change |
| Person in a photo | The object moves to a restricted prefix and skips inference | The capture is repeated |
| Verification never arrives | The fumigation stays open and appears on the dashboard | Nothing |
| Bad deployment | Pipeline rollback to the previous version | Nothing. Events wait in queues |
| Table corrupted | Point-in-time restore to a new table, as the [recovery](recovery.md) design details | At most about 5 minutes, inside the 15-minute objective |
| Region lost | Rebuild from code and the archive, in a planned effort | Outside the recovery objectives of the pilot |

## 6. Scale from 200 to 1,000 farms

| Measure | 200 farms | 1,000 farms | What changes |
|---|---|---|---|
| Device messages a harvest month | 108,000 | 540,000 | Nothing, all services scale by themselves |
| Telemetry cost a harvest month | About USD 1 | About USD 5 | Linear |
| Addresses in the cloud plan | Same | Same | Nothing, farms hold no VPC addresses |
| Ingestion endpoint | One | One | Nothing |
| Node connections an hour | 200 | 1,000 | Nothing, each node keeps its own minute, far below the quota of 3,000 a second |

The [ingestion sizing](../iot/ingestion-sizing.md) document shows the calculation behind these figures and the margin against each service quota.

The stress point at scale sits in the field. A larger pilot needs more shared gateways and more brigades, and neither one changes the cloud.

## 7. Monthly cost of the cloud platform

These figures come from the AWS price list for us-east-1 and from the volumes of the pilot. The [price basis](../governance/price-basis.md) states the date of each price, the exchange rate and the tax treatment. They cover the cloud platform and leave out the WAN links, drones and field hardware, which the cost document covers.

| Item | Normal month, USD | Harvest month, USD |
|---|---|---|
| Telemetry ingestion | 0.72 | 0.98 |
| APIs for positions, sacks and queries | 1.01 | 2.31 |
| Inference | 2.63 | 15.75 |
| New objects in S3, for that month | 0.11 | 0.65 |
| Alert delivery, SMS at its upper bound | 2.03 | 10.17 |
| Audit and the small event-driven pieces | 0.45 | 0.45 |
| VPN, three connections | 109.50 | 109.50 |
| Interface endpoints, three in two zones | 43.80 | 43.80 |
| KMS, five keys | 5.00 | 5.00 |
| Secrets, four | 1.60 | 1.60 |
| WAF, web ACL and three rules | 8.00 | 8.00 |
| CloudWatch, alarms and logs | 2.20 | 2.20 |
| **Total** | **177.05** | **200.41** |

About 87 percent of the normal month is fixed network, the VPN and the endpoints. Variable cost is small, which confirms the serverless choice and shows where any saving must come from. The [monthly cloud cost](../governance/cloud-cost.md) document gives the calculation of each line, the development and test environments, and the dedicated links.

## 8. What the infrastructure code builds

The infrastructure code implements the pattern of network, security and one environment, and it stays inside the 100 hours. It does not instantiate the 200 farms, and it delivers the reusable module of one farm instead. The boxes marked C01 to C10 on the diagram are the ones it builds, and the implementation scope document explains them one by one.

| Code | Box | Implemented by |
|---|---|---|
| C01 | Repository, root and environments | Root configuration and environment variables |
| C02 | Remote state | S3 backend with native locking |
| C03 | VPC, subnets and routes | Network module |
| C04 | Link to one collection center | Network module |
| C05 | Platform identities and encryption | Security module |
| C06 | Permanent cloud firewall rules | Security module |
| C07 | Telemetry ingestion pattern | Ingestion module |
| C08 | Inference function pattern | Function module |
| C09 | Pipeline, approval and validation evidence | Pipeline workflows |
| C10 | Reusable module of one farm | Farm module |

## 9. Environments

Development, test and production come from the same code with different variables, accounts and address ranges. A change moves from development to test to production through the pipeline, and production needs a person's approval. The environments document explains promotion, rollback, the change window and how the demonstration runs on one credit account.

## 10. Where each subject is developed

| Subject | Documents |
|---|---|
| Governance | Landing zone, cloud selection, requirement matrix |
| Security | Identity and access, encryption and revocation, personal data and retention |
| Network and connectivity | Collection center LAN, cloud addressing, farm connectivity, drone mission link, carrier tracking, port delivery |
| Automation and change | Implementation scope, environments and promotion |
| Workloads | Sensors, alert ranges, telemetry ingestion, alert to drone confirmation, inference functions, drone operating mode, drone roles and permits, lot boundaries, harvest estimation, sack identity, sack states, custody chain, views by actor, carrier application contract |
| Decisions and assumptions | Decision records and assumption register |
