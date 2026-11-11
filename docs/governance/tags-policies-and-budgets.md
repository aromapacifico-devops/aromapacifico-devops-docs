# Tags, tag policy and budgets

This document fixes the tags every cloud resource carries, the rules that stop a resource without them, and the budgets that warn before an environment spends more than planned. It turns the tag and budget controls of the [landing zone](landing-zone.md) into values the code and the cost dashboard can use. Costs split by farms, drones, collection, trips and environments, and each resource names the team that answers for it.

## Contents

1. Tag dictionary
2. Cost center of each part of the code
3. How a resource without tags is stopped
4. Budgets and alerts per environment
5. What the cost dashboard reads
6. Check script
7. Assumptions and pending confirmations
8. Sources

## 1. Tag dictionary

Every resource carries six tags. The root configuration of each environment sets them once through the provider default tags, and a module only adds `Name` and, where a resource belongs to another purpose, its own `CostCenter`.

| Tag | Answers | Allowed values | Set by |
|---|---|---|---|
| `Client` | Who pays | `fnc` | Root |
| `Project` | Which project | `aroma` | Root |
| `Environment` | Which environment | `dev`, `test`, `prod`, `shared` | Root |
| `Owner` | Which team answers for the resource | `platform`, `security`, `network` | Root |
| `CostCenter` | What the money was spent on | `fincas`, `drones`, `acopio`, `viajes`, `pruebas`, `plataforma`, `seguridad` | Root, overridden per module call |
| `ManagedBy` | How it was created | `Terraform` | Root |

`shared` marks what the bootstrap creates once for all environments, such as the state buckets and their keys.

The six purposes the Federation wants to cost map to these tags as follows.

| Purpose | Tag and value |
|---|---|
| Farms | `CostCenter = fincas` |
| Drones | `CostCenter = drones` |
| Collection centers | `CostCenter = acopio` |
| Trips of the carriers | `CostCenter = viajes` |
| Environment | `Environment` |
| Owner | `Owner` |

`pruebas` covers resources that exist only to test, `plataforma` the shared base, such as the network, and `seguridad` the keys and identities. A resource that serves several purposes takes the purpose it exists for. The center VPN carries `acopio`, because the centers are the reason it exists.

Two more tags appear on some resources. `Name` identifies each resource, and modules set it on every resource that takes tags. `Center` marks the link of each collection center in the network module. Neither one is required by the policy.

Tag keys and values are case sensitive, so `costcenter` and `CostCenter` count as two different tags. The values above are the only spelling allowed.

## 2. Cost center of each part of the code

Each environment root passes `CostCenter` to every module through `additional_tags`, which overrides the default value `plataforma` on that module's resources.

| Module | `CostCenter` | Why |
|---|---|---|
| Network | `plataforma` | The VPC, subnets, routes and endpoints serve every flow |
| Security | `seguridad` | Keys, roles, security groups and network ACLs |
| Telemetry ingestion | `fincas` | Readings and alerts come from the farm nodes |
| Farm | `fincas` | Registers one farm and its node |
| Inference function | `drones` | Confirms foci from drone photos |

The network module applies one set of tags to all its resources. The links of the centers, the VPN gateway, customer gateways and VPN connections, should carry `acopio`, and that needs the module to accept a separate set of tags for them. Until then they appear under `plataforma`, together with most of the fixed cost of the platform.

The trip tracking of carriers and the drone flight records have no module yet. Their modules take `viajes` and `drones` when they exist.

## 3. How a resource without tags is stopped

Three layers apply, and each one stops a different mistake.

| Layer | Where it runs | What it stops | Available in |
|---|---|---|---|
| Root validation | `terraform plan` of every root | A root whose tag map lacks a key, has another environment, an unknown cost center, or another value of `ManagedBy` | Demonstration and pilot |
| Tag policy | AWS Organizations, attached to the organization root | Resources of the listed types that lack a required key, reported as noncompliant, and values outside the allowed list | Pilot |
| Provider compliance check | `terraform plan` and `apply`, with `tag_policy_compliance = "error"` | Creating a resource, or changing its tags, when the effective tag policy requires a key the resource lacks | Pilot |

The policy lives in [`policies/tag-policy.json`](policies/tag-policy.json). It requires the six keys on the 29 resource types the platform creates or will create, listed in [`policies/tag-resource-types.json`](policies/tag-resource-types.json), and fixes the capitalization of every key and its allowed values. Tag policies are created in the management account, so the standalone demonstration account cannot attach one. There the root validation is the block, and the check script of section 6 keeps the policy ready for the pilot.

The provider check has three limits that the team must know.

- It enforces required keys only. Allowed values stay with the root validation and the tag policy report.
- It does not block an update that leaves tags untouched, so an old resource with missing tags keeps updating until someone edits its tags.
- It covers the resource types of the provider cross reference. Supporting resources outside it, such as bucket settings, routes, rules and attachments, carry no tags of their own and their cost lands on the resource they belong to.

The identity that runs Terraform in the pilot needs the permission `tag:ListRequiredTags`, which the pipeline roles must include when the check is turned on.

## 4. Budgets and alerts per environment

Budgets without actions cost nothing, so every environment gets its own. Each budget is monthly, filtered by the `Environment` tag, and sends three alerts.

| Alert | Fires when |
|---|---|
| Actual 80 percent | Spending of the month reaches 80 percent of the limit |
| Actual 100 percent | Spending of the month reaches the limit |
| Forecast 100 percent | AWS forecasts that the month will end above the limit |

### Pilot

Each environment has its own account in the pilot, so the budget of an environment is also the budget of its account. Limits come from the [cloud cost](cloud-cost.md) document. The dedicated links of the centers are billed by the operator and stay outside these budgets.

| Environment | Monthly limit, USD | Basis |
|---|---|---|
| Production | 230 | USD 207.07 in a harvest month, plus a margin |
| Test | 15 | 80 hours of use and its platform key |
| Development | 10 | 80 hours of use and its platform key |

A normal month of production costs USD 181.78, 79 percent of the limit, and stays quiet. A harvest month reaches about 90 percent and sends the 80 percent alert. That alert is expected in harvest. It asks for a look at the volumes and opens no incident. A harvest month in which all 200 estimation flights fall reaches about USD 236.76, 103 percent, and sends the 100 percent alert as well.

### Demonstration

The demonstration shares one account with promotional credits. Its account budget, created by the bootstrap with alerts at USD 20 and USD 50, stays the safeguard for an environment left up by mistake. Three budgets filtered by `Environment` show which environment spent the money.

| Environment | Monthly limit, USD |
|---|---|
| Production | 20 |
| Test | 10 |
| Development | 10 |

A forgotten test environment costs about USD 60 a month at 24 hours a day, so its budget warns within the first week.

### Recipients

Alerts go to a platform operations mailbox and to a Federation finance mailbox. Addresses are personal data, so they never appear in the repository. The bootstrap receives them as a variable at run time.

## 5. What the cost dashboard reads

User tags reach the billing data only after they are activated as cost allocation tags. The bootstrap activates `Environment`, `CostCenter` and `Owner` once. A key shows up for activation up to 24 hours after a resource first carries it, so the first apply of an environment comes before the activation, and costs from before the activation carry no tag.

The cost dashboard groups monthly cost by `CostCenter` and by `Environment`, and filters by `Owner`. Farms, drones, collection and tests appear as the values `fincas`, `drones`, `acopio` and `pruebas`.

The cost of a single farm does not come from a tag. Farms share the same functions, tables and queues, and a tag per farm would not split them. The dashboard divides the `fincas` cost among farms by their share of messages in the month.

## 6. Check script

`tools/check_tag_policy.py` reads the policy, the resource type map and the Terraform files of the infrastructure and module repositories cloned next to this one. It fails when the policy loses a key or changes its capitalization, when the cost centers or `ManagedBy` differ from the root validation, when the code uses a resource type the map does not classify, when a key does not cover every mapped type, or when the policy passes the 10,000 characters AWS allows.

```sh
python3 docs/governance/tools/check_tag_policy.py
```

A new module that adds a resource type makes the script fail until the type is added to the map, either as required with its tag resource type or as outside the cross reference.

## 7. Assumptions and pending confirmations

| Item | Who confirms | Effect if it fails |
|---|---|---|
| Alerts reach a platform mailbox and a Federation finance mailbox, passed at run time | Federation | An SNS topic per environment replaces the e-mail list |
| The cost of a single farm comes from its share of messages | Federation | Resources created per farm, such as device records, take a farm tag |
| The 80 and 100 percent thresholds suit the Federation | Federation | Thresholds change in the budgets |
| The network module accepts separate tags for the center links | Owner of the network module | The links stay under `plataforma` |

## 8. Sources

| Fact | Source |
|---|---|
| `tag_policy_compliance`, its limits, the permission it needs and the resource type cross reference | Terraform AWS provider 6.72.0, guide Tag Policy Compliance |
| Budget filters by tag and notifications | Terraform AWS provider 6.72.0, resource `aws_budgets_budget` |
| Activation of cost allocation tags and the 24 hour delay | Terraform AWS provider 6.72.0, resource `aws_ce_cost_allocation_tag` |
| Tag policy syntax, capitalization and wildcards | [Example tag policies](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_example-tag-policies.html) |
| 10,000 characters per tag policy | [Organizations quotas](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_reference_limits.html) |
| Budgets without actions are free | [AWS Budgets pricing](https://aws.amazon.com/aws-cost-management/aws-budgets/pricing/) |
| Monthly cost of each environment | [Cloud cost](cloud-cost.md) |
