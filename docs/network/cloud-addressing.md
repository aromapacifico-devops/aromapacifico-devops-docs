# Cloud addressing

Each environment has its own /16, chosen to stay clear of the collection centers. Growth from 200 to 1,000 farms needs no change, because farms connect to public service endpoints and hold no addresses in this plan.

## Reserved space

| Range | Use |
|---|---|
| 10.41.0.0/16 to 10.43.0.0/16 | Collection centers |
| 10.44.0.0/16 to 10.49.0.0/16 | Reserved for future centers |
| 10.50.0.0/16 | Development |
| 10.60.0.0/16 | Test |
| 10.70.0.0/16 | Production |

## Subnets

Each subnet purpose receives a /20 block, with a /24 per availability zone taken from its start. The pilot uses two zones, and a third /24 stays free in each block. This table uses production, and the other environments repeat it with their own second octet.

| Purpose | Block | Zone a | Zone b | Holds |
|---|---|---|---|---|
| Telemetry ingress | 10.70.0.0/20 | 10.70.0.0/24 | 10.70.1.0/24 | Interface endpoint for IoT Core data |
| Drone object ingress | 10.70.16.0/20 | 10.70.16.0/24 | 10.70.17.0/24 | Interface endpoint for S3 |
| Application | 10.70.32.0/20 | 10.70.32.0/24 | 10.70.33.0/24 | Interface endpoint for the private API |
| Data | 10.70.48.0/20 | 10.70.48.0/24 | 10.70.49.0/24 | Reserved, DynamoDB is reached by gateway endpoint |
| Object storage | 10.70.64.0/20 | 10.70.64.0/24 | 10.70.65.0/24 | Reserved, route association of the S3 gateway endpoint |
| Administration | 10.70.80.0/20 | 10.70.80.0/24 | 10.70.81.0/24 | Reserved for administrative endpoints |
| Public query | 10.70.96.0/20 | 10.70.96.0/24 | 10.70.97.0/24 | Reserved, CloudFront and API Gateway run outside the VPC |

Blocks from 10.70.112.0/20 onward stay free for new purposes.

## Why several subnets stay reserved

The workload is serverless. Functions, databases and queues are managed services that run outside the VPC, so the VPC exists for the path from the collection centers. Keeping all seven subnets in the plan means a later component lands in its place with no renumbering.

## Routes

| Route table | Destination | Target |
|---|---|---|
| Ingress and application | 10.41.3.0/24, 10.41.10.0/24 and equivalents | Virtual private gateway |
| All private | S3 and DynamoDB prefix lists | Gateway endpoints |

The VPC has no internet gateway and no NAT gateway. Functions reach AWS services from outside the VPC, under their IAM roles.
