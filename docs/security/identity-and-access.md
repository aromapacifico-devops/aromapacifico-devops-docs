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
| Drone operator | Pilot of the contracted operator, or Federation drone supervisor | Ground application, or any browser for the supervisor | Missions, objects, flight logs, and for the supervisor polygons and authorizations |
| Platform operator | Federation technical staff | Console | Operating the platform, no business data |

The drone operator role holds two groups. The brigade group holds the pilots of the contracted operator, and the supervisor group holds one Federation supervisor per department. No account belongs to both, so the company that flies never authorizes its own fumigation. The [drone roles and permits](../drones/roles-permits-and-campaigns.md) explain why.

## 3. Identity providers

| Identity | Provider | Why this provider |
|---|---|---|
| Farmer, carrier, center operator, drone operator | Cognito user pool, one group per role | Designed for application users, with MFA and phone sign-in |
| Platform operator | IAM Identity Center | Gives temporary AWS credentials and one place to remove access |
| Federation analyst | IAM Identity Center | Reads only the files of the monthly pilot report, which are aggregated and name no person or farm |
| Buyer | None | Read-only access needs no account, and the code is the capability |

A single user pool with groups was preferred over one pool per role, since the applications share one set of users and the groups already separate permissions. Phones and the reports web call the public HTTP API, and center stations call a private REST API reached only through the tunnel. The buyer page calls the lookup function through the CloudFront distribution, with no token. Both validate the same token with a Cognito authorizer, and each function checks the group.

Federation staff could later sign in with a corporate directory by adding a federated provider to the pool, with no change to the applications.

## 4. Access matrix

| Resource | Farmer | Carrier | Center operator | Buyer | Drone brigade | Drone supervisor | Platform operator |
|---|---|---|---|---|---|---|---|
| Readings and alerts of own farms | Read | None | None | None | Read, for the assigned focus | Read, farms of the department | None |
| Alert ranges | None | None | None | None | None | None | Change, on Federation request |
| Sack registration | Create, own farms | None | Create, when issuing a code | None | None | None | None |
| Sack events | Read own, create reweighing | Create handover, arrival, pickup, delivery and missing report | Read those of its center, create reception, correction, return, dispatch, label reprint and missing report | None | None | None | None |
| Buyer view of a sack | Read | Read | Read | Read | None | None | None |
| Trip of a sack | None | Read own | Read | None | None | None | None |
| Farm and lot polygon | Read own | None | None | None | Read published, assigned | Create, publish, read | None |
| No-fly zones | Read own | None | None | None | Read, assigned | Create, read | None |
| Fumigation order | Read own, accept the visit | None | None | None | Create, read assigned | Read, authorize, suspend | None |
| Flight objects and logs | Read own case | None | Read harvest estimate | None | Create, read assigned | Read, department | None |
| Audit logs | None | None | None | None | None | None | Read |
| Platform configuration | None | None | None | None | None | None | Change through the pipeline |

A Federation analyst reads only the aggregated files of the pilot report and none of the resources above, as the [farmer history](../iot/farmer-history.md) defines.

The platform operator holds no read on business data. Operating the platform does not require seeing whose coffee it is, and that separation limits the damage of a stolen operator session.

Own farms is enforced in each function by comparing the identity in the token with the owner of the record. A role alone would let any farmer read any farm.

## 5. Strong authentication

MFA is required for center operators, drone operators and platform operators, the three roles that can change the state of a sack, a fumigation or the platform.

| Role | Factor | Why |
|---|---|---|
| Center operator | Authenticator application | Works with no SMS coverage on the center LAN |
| Drone brigade and supervisor | Authenticator application | Works offline in the field, where SMS may not arrive |
| Platform operator | Security key or authenticator | Highest privilege |

Farmers and carriers sign in with their phone number and keep a session of 30 days with refresh token rotation, since a code at every use would be a barrier on a phone with intermittent data. A session that ends during a trip stops only synchronization, and capture continues on the phone. Their worst case is limited, because they act only on their own records.

Time-based codes work with no connection on the device, which matters at a lot with no signal.

## 6. Fumigation authorization

The authorization of a fumigation is a human identity, and no automated trigger can execute it.

| Rule | Enforcement |
|---|---|
| Only the supervisor group can authorize | Group claim checked by the function |
| No account belongs to both the brigade and the supervisor groups | The function rejects a token that carries both groups, and the group assignment process refuses it |
| The authorizer is the supervisor of the farm's department or its named backup | Department of the supervisor checked against the farm |
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
| Public query function | Read one item of the buyer view table | `buyer_views` only, with no other data table |
| IoT rule | Send to one queue and one delivery stream | Named resources |
| Pilot report workflow | Export three tables, run queries in one Athena workgroup, write report files | Named tables, workgroup and reports prefix |
| Firehose delivery | Write to the telemetry archive | Named bucket and key |
| Pipeline, plan stage | Read-only | One role per environment |
| Pipeline, apply stage | Deploy, limited to the protected environment | One role per environment |

GitHub OIDC replaces stored keys. AWS trusts tokens issued for this organization and repository, and the apply role also requires the protected production environment, so a branch cannot deploy to production by itself.

## 8. Device identities

Each node and each ground station holds an X.509 certificate of its own, tied to one thing. The IoT policy uses the thing name, so a device can only publish on topics that carry its own identifier. A ground station also signs each flight result with the private key of that certificate, and the platform checks the signature against the registry, so revoking the certificate stops both paths.

| Stage | Action |
|---|---|
| Manufacture or preparation | The certificate is created and stored on the device |
| Installation | The installer links the thing to the farm and records its lot and GPS position |
| Operation | The device publishes with TLS client authentication |
| Loss or retirement | The certificate is revoked, see the encryption document |

A stolen device can only publish as itself, and revocation stops it. One certificate per device costs more effort at installation than a shared one, and a shared one could not be revoked without stopping all farms.

## 9. Public query

| Control | Purpose |
|---|---|
| Random code of 60 bits | A code cannot be derived or listed |
| Buyer view only | The response comes from a table that holds only the buyer view, and the function can read nothing else. [Views by actor](../traceability/actor-views.md) lists every field |
| WAF rate rule | Limits automated reading, with a threshold above the peak of 30 reads a minute |
| Only path through the firewall | The function URL admits only requests that the distribution signed, so no request skips the rate rule |
| Ceiling | Five reserved copies of the lookup function bound the rate at about 25 lookups a second, whatever the number of addresses |
| Audit of each read | Required for the sack |

## 10. What is audited

| Event | Where it is recorded | Retention |
|---|---|---|
| Read of a sack | Audit event written by the query function | Five years |
| Change of a threshold | Audit event with values before and after, plus CloudTrail data events on the ranges table | Five years |
| Publication of telemetry | IoT Core log entry of each publication, for the farm thing groups | Five years |
| Delivery of a flight object | Audit event of the URL grant, plus CloudTrail data events for `PutObject` | Five years |
| Fumigation authorization | Case and audit event | Five years |

Every record ends in a bucket of the log archive account under S3 Object Lock in compliance mode, which no account can alter for five years. [Audit of sensitive events](audit.md) defines each record, the path and the evidence queries.

## 11. Input for the security module

The infrastructure code creates the identities of the patterns it implements. Human pools and the application roles stay in the architecture.

| Created by the code | Consumers |
|---|---|
| Ingestion function role | Ingestion module |
| Focus confirmation function role | Function module |
| IoT rule role | Ingestion module |
| Firehose delivery role | Ingestion module |
| Pipeline plan and apply roles, created in bootstrap | Pipeline |
| KMS keys, with the platform key created in bootstrap | All modules |

## 12. Assumptions and pending confirmations

| Item | Who confirms | Effect if it fails |
|---|---|---|
| The Federation names one drone supervisor per department, outside the contracted operator, and a backup | Federation | Authorization slows down, and the brigade can never stand in |
| Farmers accept phone sign-in | Federation | A simpler flow is designed |
| Staff can use an authenticator application | Federation | Hardware tokens are added |
