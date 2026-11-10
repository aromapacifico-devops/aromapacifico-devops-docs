# Cloud addressing

This document defines the private address plan of the cloud. Each environment has its own /16, the plan never overlaps the collection centers, all seven required subnets exist in every environment, and growth from 200 to 1,000 farms needs no change.

## Contents

1. Constraints
2. Reserved space
3. Why /16 per environment
4. Subnet structure
5. Plan per environment
6. What each subnet holds
7. Routes
8. Name convention
9. Growth
10. Cost of the network
11. Assumptions and pending confirmations

### Terms used

| Term | Meaning in this document |
|---|---|
| CIDR | Notation for a range of addresses, such as 10.70.0.0/16 |
| Availability zone | A separate data center group inside the region |
| Gateway endpoint | Free route to S3 or DynamoDB from private route tables |
| Interface endpoint | Private address in a subnet that fronts an AWS service, billed by the hour |
| Virtual private gateway | The AWS end of a site-to-site VPN |

---

## 1. Constraints

| Constraint | Source | Effect |
|---|---|---|
| No overlap with 10.41.0.0/16, 10.42.0.0/16 or 10.43.0.0/16 | Inventory of the centers | Cloud ranges start at 10.50 |
| Different ranges for development, test and production | Isolation | One /16 each |
| Seven subnets at least | Telemetry ingress, drone object ingress, application, data, object storage, administration, public query | Seven blocks |
| No redesign from 200 to 1,000 farms | Growth | Space held in reserve |

## 2. Reserved space

| Range | Use |
|---|---|
| 10.41.0.0/16 to 10.43.0.0/16 | Cauca, Huila, Tolima |
| 10.44.0.0/16 to 10.49.0.0/16 | Future centers |
| 10.50.0.0/16 | Development |
| 10.60.0.0/16 | Test |
| 10.70.0.0/16 | Production |

Six /16 ranges stay free for future centers, so a fourth department would extend the pattern with no new thinking. The distance between environment ranges keeps them readable, since the second octet alone tells which environment an address belongs to.

## 3. Why /16 per environment

The largest block AWS allows for a VPC is a /16, and using it costs nothing. A private range is free, so a tight plan would save nothing and could force a renumbering later. A smaller /20 per environment was discarded for that reason.

## 4. Subnet structure

Each subnet purpose receives a /20 block with 4,096 addresses. Inside it, each availability zone uses one /24.

| Level | Size | Addresses | Why |
|---|---|---|---|
| Purpose block | /20 | 4,096 | Room for more subnets of the same purpose |
| Subnet per zone | /24 | 251 usable, since AWS reserves 5 | Far more than endpoints need |

Production uses two zones. A third /24 stays free in each block for a third zone, and development and test use one zone to reduce the cost of endpoints, keeping the same plan.

## 5. Plan per environment

Production, 10.70.0.0/16.

| Purpose | Block | Zone a | Zone b |
|---|---|---|---|
| Telemetry ingress | 10.70.0.0/20 | 10.70.0.0/24 | 10.70.1.0/24 |
| Drone object ingress | 10.70.16.0/20 | 10.70.16.0/24 | 10.70.17.0/24 |
| Application | 10.70.32.0/20 | 10.70.32.0/24 | 10.70.33.0/24 |
| Data | 10.70.48.0/20 | 10.70.48.0/24 | 10.70.49.0/24 |
| Object storage | 10.70.64.0/20 | 10.70.64.0/24 | 10.70.65.0/24 |
| Administration | 10.70.80.0/20 | 10.70.80.0/24 | 10.70.81.0/24 |
| Public query | 10.70.96.0/20 | 10.70.96.0/24 | 10.70.97.0/24 |

Test, 10.60.0.0/16, and development, 10.50.0.0/16, repeat this table with their second octet.

| Environment | Telemetry ingress, zone a | Public query, zone a |
|---|---|---|
| Development | 10.50.0.0/24 | 10.50.96.0/24 |
| Test | 10.60.0.0/24 | 10.60.96.0/24 |
| Production | 10.70.0.0/24 | 10.70.96.0/24 |

Blocks from .112.0/20 onward stay free in each environment.

## 6. What each subnet holds

The workload is serverless, so most services run outside the VPC. The VPC exists for the private path from the collection centers. Seven subnets remain in the plan so that a later component lands in its place with no renumbering, and the table says honestly which ones hold something today.

| Subnet | Holds now | Why |
|---|---|---|
| Telemetry ingress | Interface endpoint for IoT Core data | A device at a center can publish through the tunnel |
| Drone object ingress | Interface endpoint for S3 | Gateway endpoints cannot be reached through a VPN, so uploads from a center need this one |
| Application | Interface endpoint for the private REST API | Logistics stations reach the center API privately, since only a private REST API accepts calls through an interface endpoint |
| Data | Reserved | DynamoDB is reached by a gateway endpoint |
| Object storage | Reserved, holds the route association | S3 does not live in a subnet |
| Administration | Reserved | Available for administrative endpoints |
| Public query | Reserved | CloudFront and API Gateway run outside the VPC |

Functions stay outside the VPC unless they need a private resource. Inside it, they would need interface endpoints or a NAT gateway to reach AWS services, adding hourly cost with no isolation gain, since IAM and TLS protect those calls.

## 7. Routes

| Route table | Destination | Target |
|---|---|---|
| Ingress and application | 10.41.3.0/24, 10.41.10.0/24 | Virtual private gateway, Cauca |
| Ingress and application | 10.42.3.0/24, 10.42.10.0/24 | Virtual private gateway, Huila |
| Ingress and application | 10.43.3.0/24, 10.43.10.0/24 | Virtual private gateway, Tolima |
| All private | S3 prefix list | Gateway endpoint |
| All private | DynamoDB prefix list | Gateway endpoint |

The VPC has no internet gateway and no NAT gateway. Only logistics and local servers receive a route, so the visitor network has no path into the cloud even if a firewall rule failed at the center.

Endpoint security groups allow TCP 443 from those same ranges and deny all else.

## 8. Name convention

Names follow `{client}-{project}-{env}-{type}-{name}`.

| Resource | Example |
|---|---|
| VPC | `fnc-aroma-prod-vpc-main` |
| Subnet | `fnc-aroma-prod-subnet-telemetry-ingress-a` |
| Route table | `fnc-aroma-prod-rt-private` |

## 9. Growth

| Growth | Effect on addresses |
|---|---|
| 200 to 1,000 farms | None, farms connect to public service endpoints |
| More carriers | None |
| A fourth center | One new /16 from 10.44 upward and one more VPN |
| A new component in the VPC | Free /24 inside its block, or a free block |
| A third availability zone | Third /24 of each block |

## 10. Cost of the network

| Item | Calculation | Monthly cost, USD |
|---|---|---|
| Site-to-site VPN | 3 × USD 0.05 per hour × 730 hours | 109.50 |
| Interface endpoints in production | 3 endpoints × 2 zones × USD 0.01 per hour × 730 hours | 43.80 |
| Gateway endpoints | No charge | 0 |
| NAT gateway | Not used | 0 |
| **Total** | | **153.30** |

This is about 87 percent of the monthly cloud cost of a normal month, so any review of cost starts here. A NAT gateway in each zone was avoided, which would have added hourly and per-GB charges.

## 11. Assumptions and pending confirmations

| Item | Who confirms | Effect if it fails |
|---|---|---|
| The Federation networks use none of the planned ranges | Federation | Ranges move |
| Test connects to one center for validation | Team | One more VPN during tests, USD 36.50 a month |
| Availability zones are chosen at deployment | Team | Names change, the plan stays |

## Sources

- AWS Price List API for VPC in us-east-1.
- Amazon VPC documentation on reserved addresses and endpoints.
