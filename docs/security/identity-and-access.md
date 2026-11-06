# Identity and access

Each actor has a separate identity with the least access its work needs. People, services and devices never share credentials.

## Human identities

| Role | Identity provider | MFA | Access path |
|---|---|---|---|
| Farmer | Cognito user pool | Optional | Farmer application |
| Carrier | Cognito user pool | Optional | Carrier application |
| Center operator | Cognito user pool | Required | Web application through the center network |
| Buyer | None, read by sack code | Not applicable | Public sack query |
| Drone operator | Cognito user pool | Required | Ground application |
| Platform operator | IAM Identity Center | Required | AWS console and command line |

The buyer does not sign in. The sack code acts as the capability to read one sack, and the buyer view exposes nothing else. A web application firewall limits request rates, and every read is audited.

## Access matrix

| Resource | Farmer | Carrier | Center operator | Buyer | Drone operator | Platform operator |
|---|---|---|---|---|---|---|
| Readings and alerts of own farms | Read | None | None | None | Read, for the assigned focus | None |
| Alert thresholds | None | None | None | None | None | Change, on Federation request |
| Sack registration | Create, for own farms | None | Create, when reissuing a code | None | None | None |
| Sack events | Read own | Create handover and transit | Create reception and dispatch | None | None | None |
| Buyer view of a sack | Read | Read | Read | Read | None | None |
| Trip of a sack | None | Read own | Read | None | None | None |
| Farm and lot polygon | Read own | None | None | None | Create, read | None |
| Fumigation order | Read own | None | None | None | Create, and authorize as supervisor | None |
| Flight objects and logs | Read own case | None | Read harvest estimate | None | Create, read assigned | None |
| Audit logs | None | None | None | None | None | Read |
| Platform configuration | None | None | None | None | None | Change through the pipeline |

A person with the drone supervisor attribute authorizes a fumigation order. The platform rejects an authorization from the same person who is assigned to fly it. No automated trigger can authorize one.

## Service identities

| Identity | Scope | Credential |
|---|---|---|
| Ingestion function | Write readings and alerts, read thresholds | Lambda execution role |
| Inference function | Read one prefix of the object bucket, write case results, invoke inference | Lambda execution role |
| API functions | One role per domain, sack, trip and drone | Lambda execution role |
| Pipeline, plan stage | Read-only role per account | GitHub OIDC federation |
| Pipeline, apply stage | Deployment role per account, limited to the protected environment | GitHub OIDC federation |

Service roles grant named actions on named resources. No role grants a wildcard action.

## Device identities

Each farm node and each drone ground station holds its own X.509 certificate, tied to one AWS IoT thing. An IoT policy limits it to publishing on topics that carry its own identifier. A stolen device can only publish as itself, and revocation stops it.

## Input for the security module

The infrastructure code creates the service roles for the ingestion and inference patterns, the pipeline roles and the KMS keys. Human pools and application roles stay in the architecture.
