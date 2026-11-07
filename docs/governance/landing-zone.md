# Landing zone

This document defines the accounts of the platform, the controls that apply from the root, and how environments stay apart. The landing zone exists before any workload, so that every account is born with its rules and no team has to remember them.

![Landing zone with organization units, accounts and root controls](../architecture/diagrams/05-landing-zone.drawio.png)

## Contents

1. Why several accounts
2. Structure
3. What each account holds
4. Controls from the root
5. Tags and cost by purpose
6. Human access
7. Environments and promotion
8. Network sharing
9. Cost of the landing zone
10. Creation and scope of the code
11. Assumptions and pending confirmations

### Terms used

| Term | Meaning in this document |
|---|---|
| Account | The AWS boundary for resources, permissions and billing |
| Organizational unit | A folder of accounts that shares policies |
| Service control policy | A rule at the organization level that limits what any identity in an account can do, even an administrator |
| Tag policy | A rule that standardizes the tags on resources |
| Resource Access Manager | The AWS service that shares resources, such as subnets, between accounts |

---

## 1. Why several accounts

Security, network, production and testing must stay separate. An account is the strongest boundary AWS offers, stronger than a role or a tag, for three reasons.

| Reason | Effect in the pilot |
|---|---|
| Blast radius | An error in test cannot touch production data |
| Protected evidence | A compromised workload cannot erase its own audit trail, since the trail lives in another account |
| Clear cost | Billing separates by account with no tag work |

A single account with tags was discarded, because a tag cannot stop an administrator. Accounts per department were also discarded. The three departments share one platform, and separating them would multiply fixed cost with no isolation need behind it.

## 2. Structure

| Organizational unit | Account | Holds workloads |
|---|---|---|
| Root | Management | No |
| Security | Log archive | No |
| Security | Security tooling | No |
| Infrastructure | Network | No |
| Workloads | Production | Yes |
| Workloads | Test | Yes |
| Workloads | Development | Yes |

## 3. What each account holds

| Account | Contents | Who enters |
|---|---|---|
| Management | Organization, consolidated billing, IAM Identity Center | Two named platform operators |
| Log archive | Organization trail, audit logs with five-year retention and object lock | Read-only, security role |
| Security tooling | Security Hub, GuardDuty, administration of keys | Security role |
| Network | VPCs, VPN, DNS, gateway and interface endpoints | Network role |
| Production | Functions, tables, buckets, queues of production | Read-only for people, changes through the pipeline |
| Test | Same resources, with synthetic data | Pipeline and developers |
| Development | Same resources, disposable | Developers |

## 4. Controls from the root

| Control | Mechanism | What it stops |
|---|---|---|
| Region limit | Service control policy | Creating regional resources outside us-east-1, except global services |
| Audit protection | Service control policy | Stopping or deleting the organization trail |
| Organization exit | Service control policy | An account leaving the organization |
| Encryption | Service control policy | Creating unencrypted volumes or buckets without default encryption |
| Root user | Service control policy | Using the root user in member accounts |
| Identity | IAM Identity Center | Long-lived users, since sign-in carries MFA |
| Tags | Tag policy | Resources with missing or misspelled cost tags |
| Budgets | AWS Budgets per account | Silent overspending, with alerts at 80 and 100 percent |
| Detection | GuardDuty and Security Hub | Unnoticed threats, since findings gather in one account |

Policies apply to organizational units, so an account added later inherits them with no extra step.

## 5. Tags and cost by purpose

Costs must split by farms, drones, collection, trips and environments. Every resource carries these tags, which the root configuration of the code applies as defaults.

| Tag | Values |
|---|---|
| `Client` | `fnc` |
| `Project` | `aroma` |
| `Environment` | `dev`, `test`, `prod` |
| `CostCenter` | `fincas`, `drones`, `acopio`, `viajes`, `pruebas`, `plataforma`, `seguridad` |
| `ManagedBy` | `Terraform` |

The cost dashboard reads these tags. Shared items, such as the VPN, carry `acopio`, because the centers are the reason they exist.

## 6. Human access

Platform operators sign in through IAM Identity Center with MFA and receive temporary credentials through permission sets, one for each job.

| Permission set | Accounts | Allows |
|---|---|---|
| Read-only | All | Reading configuration |
| Security | Log archive, security tooling | Reading logs, managing findings |
| Network | Network | Operating VPN and DNS |
| Break-glass | All | Full access, with an alarm on every use |

Production changes go through the pipeline. Direct changes stay reserved for incidents through the break-glass set, and each use must be reviewed afterward.

## 7. Environments and promotion

| Environment | Account | Range | Data | Purpose |
|---|---|---|---|---|
| Development | Development | 10.50.0.0/16 | Simulated nodes | Trying changes |
| Test | Test | 10.60.0.0/16 | Synthetic data | Validating before production, and the first plan of the code |
| Production | Production | 10.70.0.0/16 | Real data | The pilot |

A change moves from development to test to production through the pipeline, and production needs a person's approval. No production change happens between 05:00 and 18:00 in a harvest week, except during an incident.

## 8. Network sharing

The network account owns the VPCs and shares their subnets with the workload account of each environment. Network and workload teams keep separate duties, since a workload team can place an endpoint in a shared subnet but cannot change routes or the VPN.

Sharing is free, and the alternative, a Transit Gateway, would add hourly charges for each attachment with no need in a design with no traffic between VPCs.

## 9. Cost of the landing zone

| Item | Monthly cost, USD |
|---|---|
| AWS Organizations and IAM Identity Center | No charge |
| Accounts | No charge |
| Service control and tag policies | No charge |
| AWS Budgets, first two per account | No charge in the free allowance, to be confirmed |
| First organization trail, management events | No charge for the first copy |
| GuardDuty and Security Hub | Billed by volume, small at this load |

The landing zone itself adds almost no fixed cost, so isolation does not compete with the budget of the pilot.

## 10. Creation and scope of the code

The organization and its accounts are created once, as a prerequisite. The 100-hour infrastructure code produces the plan of one environment and receives account identifiers as variables. Automating the landing zone itself stays outside those hours.

This structure is the target for the pilot. The demonstration runs on one standalone credit account, because joining an Organization moves a free account to the paid plan, so service control policies stay in the design. The environments document explains it.

## 11. Assumptions and pending confirmations

| Item | Who confirms | Effect if it fails |
|---|---|---|
| The Federation owns the organization and its billing | Federation | Accounts move under another payer |
| Two platform operators are enough for the pilot | Federation | Permission sets are assigned to more people |
| Budget thresholds of 80 and 100 percent suit the Federation | Federation | Alert levels change |
