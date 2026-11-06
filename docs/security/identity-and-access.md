# Identity and access

This document defines who and what can act on the platform. Each actor has a separate identity with the least access its work needs, and people, services and devices never share credentials. It covers the six human roles, the access matrix, strong authentication, service and device identities, and the input for the security module of the infrastructure code.

## Contents

1. Principles
2. The six human roles
3. Identity providers
4. Access matrix
5. Strong authentication
6. Fumigation authorization
7. Service identities
8. Device identities
9. Public query
10. What is audited
11. Input for the security module
12. Assumptions and pending confirmations

### Terms used

| Term | Meaning in this document |
|---|---|
| Least privilege | An identity holds only the permissions its work needs |
| Cognito user pool | Managed directory for application users |
| IAM Identity Center | Single sign-on for people who operate AWS |
| Token | Short-lived signed proof of identity that an application sends with each request |
| OIDC federation | Trust that lets the pipeline receive temporary credentials with no stored key |
| Thing | The AWS IoT record of one device |

---

## 1. Principles

| Principle | How it applies |
|---|---|
| One identity per actor | No shared accounts at centers or brigades |
| Short-lived credentials | Tokens expire. The pipeline and functions hold no static keys |
| Access by role | Permissions attach to groups or roles, never to a person |
| Separation of people and machines | Human identities never run in a pipeline or a function |
| Denied unless granted | No wildcard actions in service roles |
| Every sensitive action leaves a trace | Reads of a sack, threshold changes, publications and object deliveries are audited |

## 2. The six human roles

| Role | Who | Works from | Needs |
|---|---|---|---|
| Farmer | Owner of a farm | Phone with data in the municipal seat or on main roads | Alerts, history of own farms, sack registration |
| Carrier | Driver | Phone in transit | Handover, position, arrival and delivery |
| Center operator | Logistics staff | Station or phone on the center LAN | Reception, dispatch, code issuing |
| Buyer | Coffee buyer | Any browser | Read one sack |
| Drone operator | Brigade member | Ground application | Missions, objects, flight logs |
| Platform operator | Federation technical staff | Console | Operating the platform, no business data |

## 3. Identity providers

| Identity | Provider | Why this provider |
|---|---|---|
| Farmer, carrier, center operator, drone operator | Cognito user pool, one group per role | Designed for application users, with MFA and phone sign-in |
| Platform operator | IAM Identity Center | Gives temporary AWS credentials and one place to remove access |
| Buyer | None | Read-only access needs no account, and the code is the capability |

A single user pool with groups was preferred over one pool per role, since the applications share one API and the groups already separate permissions. API Gateway validates the token, and each function checks the group.

Federation staff could later sign in with a corporate directory by adding a federated provider to the pool, with no change to the applications.

## 4. Access matrix

| Resource | Farmer | Carrier | Center operator | Buyer | Drone operator | Platform operator |
|---|---|---|---|---|---|---|
| Readings and alerts of own farms | Read | None | None | None | Read, for the assigned focus | None |
| Alert ranges | None | None | None | None | None | Change, on Federation request |
| Sack registration | Create, own farms | None | Create, when issuing a code | None | None | None |
| Sack events | Read own, create reweighing | Create handover, arrival, pickup, delivery and missing report | Create reception, correction, return, dispatch, label reprint and missing report | None | None | None |
| Buyer view of a sack | Read | Read | Read | Read | None | None |
| Trip of a sack | None | Read own | Read | None | None | None |
| Farm and lot polygon | Read own | None | None | None | Create, read | None |
| No-fly zones | Read own | None | None | None | Create, read | None |
| Fumigation order | Read own | None | None | None | Create, and authorize as supervisor | None |
| Flight objects and logs | Read own case | None | Read harvest estimate | None | Create, read assigned | None |
| Audit logs | None | None | None | None | None | Read |
| Platform configuration | None | None | None | None | None | Change through the pipeline |

The platform operator holds no read on business data. Operating the platform does not require seeing whose coffee it is, and that separation limits the damage of a stolen operator session.

Own farms is enforced in each function by comparing the identity in the token with the owner of the record. A role alone would let any farmer read any farm.

## 5. Strong authentication

MFA is required for center operators, drone operators and platform operators, the three roles that can change the state of a sack, a fumigation or the platform.

| Role | Factor | Why |
|---|---|---|
| Center operator | Authenticator application | Works with no SMS coverage on the center LAN |
| Drone operator | Authenticator application | Works offline in the field, where SMS may not arrive |
| Platform operator | Security key or authenticator | Highest privilege |

Farmers and carriers sign in with their phone number and keep a session of 30 days with refresh token rotation, since a code at every use would be a barrier on a phone with intermittent data. A session that ends during a trip stops only synchronization, and capture continues on the phone. Their worst case is limited, because they act only on their own records.

Time-based codes work with no connection on the device, which matters at a lot with no signal.

## 6. Fumigation authorization

The authorization of a fumigation is a human identity, and no automated trigger can execute it.

| Rule | Enforcement |
|---|---|
| Only the supervisor group can authorize | Group claim checked by the function |
| The authorizer differs from the assigned pilot | The function rejects equal identities |
| The order needs a polygon and a closed flight log | Conditional write on the case |
| Each authorization records who, when and which order | Transaction with the audit event |

No function role holds the permission to write an authorization, so a compromised function cannot approve a fumigation.

## 7. Service identities

| Identity | Allowed actions | Scope |
|---|---|---|
| Ingestion function | Read messages, write readings and alerts, read ranges, publish alerts | Named queue, tables and topic |
| Focus confirmation function | Read one prefix of the object bucket, detect labels, invoke one model, write results | Named bucket prefix, model and table |
| Verification and estimation functions | Same pattern | Own prefix |
| Domain functions | One role per domain, sacks, trips and drones | Own tables |
| IoT rule | Send to one queue and one delivery stream | Named resources |
| Pipeline, plan stage | Read-only | One role per account |
| Pipeline, apply stage | Deploy, limited to the protected environment | One role per account |

GitHub OIDC replaces stored keys. AWS trusts tokens issued for this organization and repository, and the apply role also requires the protected production environment, so a branch cannot deploy to production by itself.

## 8. Device identities

Each node and each ground station holds an X.509 certificate of its own, tied to one thing. The IoT policy uses the thing name, so a device can only publish on topics that carry its own identifier.

| Stage | Action |
|---|---|
| Manufacture or preparation | The certificate is created and stored on the device |
| Installation | The installer links the thing to the farm |
| Operation | The device publishes with TLS client authentication |
| Loss or retirement | The certificate is revoked, see the encryption document |

A stolen device can only publish as itself, and revocation stops it. One certificate per device costs more effort at installation than a shared one, and a shared one could not be revoked without stopping all farms.

## 9. Public query

| Control | Purpose |
|---|---|
| Random code of 60 bits | A code cannot be derived or listed |
| Buyer view only | The response holds no farm, farmer or trip |
| WAF rate rule | Limits automated reading, with a threshold above the peak of 30 reads a minute |
| Audit of each read | Required for the sack |

## 10. What is audited

| Event | Where it is recorded | Retention |
|---|---|---|
| Read of a sack | Audit table, written by the function | Five years |
| Change of a threshold | Audit table and CloudTrail | Five years |
| Publication of telemetry | IoT Core logs and readings table | Five years |
| Delivery of a flight object | S3 data events and case | Five years |
| Fumigation authorization | Case and audit table | Five years |

## 11. Input for the security module

The infrastructure code creates the identities of the patterns it implements. Human pools and the application roles stay in the architecture.

| Created by the code | Consumers |
|---|---|
| Ingestion function role | Ingestion module |
| Focus confirmation function role | Function module |
| IoT rule role | Ingestion module |
| Pipeline plan and apply roles | Pipeline |
| KMS keys | All modules |

## 12. Assumptions and pending confirmations

| Item | Who confirms | Effect if it fails |
|---|---|---|
| A drone supervisor exists and differs from the pilot | Federation | The authorizer moves to another role |
| Farmers accept phone sign-in | Federation | A simpler flow is designed |
| Staff can use an authenticator application | Federation | Hardware tokens are added |
