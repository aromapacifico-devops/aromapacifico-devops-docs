# Operations and cost dashboards

This document defines the two pages the Federation and the platform operator use to follow the pilot. The operational dashboard shows, on one page, whether readings arrive, alerts reach farmers, drone work moves and the centers stay linked. The cost dashboard shows what the month costs and who spent it. Both split their figures by the cost center tag, so farms, drones, collection and tests appear apart. The document sets every widget with its source signal, how the split by tag works and where it cannot apply, what each page costs, and what has to exist in the account first. It is a design. No dashboard, report or setting was created, and the checker described in section 10 verifies the design as written.

## Contents

1. Terms
2. What is reused
3. Decisions
4. Operational dashboard
5. How the split by tag works
6. Cost dashboard
7. What fails and what shows it
8. Cost
9. Where each piece lives
10. What the checker proves
11. Assumptions and pending confirmations
12. Sources

## 1. Terms

| Term | Meaning in this document |
|---|---|
| Cost center | The value of the `CostCenter` tag on a resource. Farms, drones, collection and tests are `fincas`, `drones`, `acopio` and `pruebas`. Shared resources carry `plataforma`, keys and identities `seguridad`, and trip tracking `viajes` |
| Operational dashboard | One CloudWatch dashboard with metric widgets, an alarm status widget and text |
| Cost dashboard | A set of saved Cost Explorer reports, read in the Billing console |
| Service metric | A metric that an AWS service publishes for free, such as the errors of a function |
| Custom metric | One of the six metrics that the platform functions publish, billed per metric |
| Tag query | A Metrics Insights query that filters or groups service metrics by a resource tag |
| Resource tags for telemetry | An account setting that lets CloudWatch attach resource tags to service metrics, which tag queries need |
| Saved query | A Logs Insights query kept in the console that an operator runs by hand |

## 2. What is reused

| Document | What this design takes from it |
|---|---|
| [Observability](observability.md) | The signal catalog, the six custom metrics, the choice to read most signals by saved queries, and the telemetry cost of USD 2.13 in a normal month and USD 2.55 in a harvest month |
| [Operational alarms](operational-alarms.md) | The register of alarms, their owners and first actions, and the 28 billed alarms |
| [Service level objectives](service-levels.md) | The two objectives, computed once a day by saved queries |
| [Tags, policies and budgets](../governance/tags-policies-and-budgets.md) | The tag dictionary, the cost center of each module, the activation of cost allocation tags and the farm share by messages |
| [Telemetry ingestion](../iot/telemetry-ingestion.md) | The device message volumes of the pilot |
| [Landing zone](../governance/landing-zone.md) | One account per environment in the pilot, one shared account in the demonstration |

## 3. Decisions

### One CloudWatch dashboard for operations

The observability design gave up dashboards of its own to stay near its reference cost, so an operator had to open each service view and each saved query. That leaves no single page to look at during a harvest morning, and the pilot needs one. The platform keeps one dashboard per workload account. In the pilot that is the production account. In the demonstration account, which holds every environment, the same dashboard switches between them with a variable.

| Option | Why it was not chosen |
|---|---|
| No dashboard, only service views and saved queries | No single page shows the state of the pilot, and the operator rebuilds it each time |
| One dashboard counted inside the free allowance of three | The cost documents assume list prices with no free tier, and one exception would make every other figure inconsistent |
| One dashboard per environment | Test and development have no farmers to protect, and the variable already shows them in the demonstration account |
| Log widgets for the objectives and the lists | Each load of a log widget bills a query, and the objectives are computed once a day already |

### Saved Cost Explorer reports for cost

Cost Explorer reads the billing data with the cost allocation tags, groups it by any active tag and is free in the console. The cost dashboard is a set of saved reports there.

| Option | Why it was not chosen |
|---|---|
| Billing and Cost Management dashboards | They gather Cost Explorer widgets on one page, can be shared and sent as a PDF, but their price, whether a widget groups by a cost allocation tag and whether they can be declared in code were not found in official sources |
| A CloudWatch dashboard on the estimated charges metric | That metric splits by service and carries no tags, so farms, drones, collection and tests cannot appear apart |
| Exported billing data with a query and a reporting service | It adds a bucket, a query engine and a reporting license for a pilot whose cost fits a few reports |

## 4. Operational dashboard

The page is 24 columns wide and reads from top to bottom, from the state of the alarms to the detail of each area. The environment variable at the top replaces the environment in every tag query, so the same body serves production, test and development in the demonstration account. The body is in [`examples/operational-dashboard.json`](examples/operational-dashboard.json), with placeholders in angle brackets for names that exist only after deployment.

| Row | Widget | Signal | Split | Alarm it explains |
|---|---|---|---|---|
| Header | Text with the environment and where saved queries and alarm actions are | none | none | none |
| Alarms | Alarm status of the 28 billed alarms, those in alarm first | none | none | Every billed alarm |
| By cost center | Function invocations | A-02 | Tag query grouped by cost center | none |
| By cost center | Function errors | A-02 | Tag query grouped by cost center | AL-13, AL-16, AL-19, AL-22, AL-28 to AL-30, AL-34, AL-35 |
| Farms | Nodes silent over 24 hours | I-01 | Custom metric, farms by saved query | AL-01 |
| Farms | Age of the oldest message in farm queues | I-02 | Tag query on `fincas`, by queue | AL-08 |
| Farms | Visible messages by cost center and queue, dead letter queues included | I-03 | Tag query grouped by cost center and queue | AL-06, AL-07, AL-14, AL-17, AL-20, AL-23, AL-33 |
| Alerts | Time from reading to handoff of a live alert | I-06 | Custom metric | AL-04 |
| Alerts | Alerts not delivered | I-07 | Custom metric | AL-03 |
| Alerts | Urgent SMS not delivered | I-08 | Custom metric | AL-05 |
| Drones | Errors of drone and inference functions | A-08 | Tag query on `drones`, by function | AL-13, AL-16, AL-19, AL-22, AL-34, AL-35 |
| Drones | Events a rule could not deliver | A-07 | Tag query on `drones`, by rule | AL-15, AL-18, AL-21, AL-24 |
| Drones | Drone work and dead letter queues | F-06 | Tag query on `drones`, by queue | AL-14, AL-17, AL-20, AL-23, AL-33 |
| Collection | State of the center tunnels | W-01 | Tag query on `acopio`, by connection | none |
| Collection | Server errors of the center API | A-01 | Named API, outside tag queries | none |
| Collection | Custody gaps and anomalies | A-04 | Custom metric | none |
| Data | Write throttles of the tables | D-02 | Tag query grouped by cost center | AL-26 |
| Data | Throttles and errors of the public sack query | A-03 | Named function | none |
| Data | Deletion runs failed or limited | D-05 | Custom metric | AL-27 |

Tests have no row of their own. A resource that exists only to test carries `pruebas`, and it appears as its own series in every widget grouped by cost center. Trip tracking appears the same way under `viajes` once its module exists.

The two service level objectives, the silent farms, overdue fumigation orders and the events of each center stay in saved queries. The header names them, and the operator runs them when an alarm or a widget points there. A log widget would run its query on every load of the page.

A sharing caveat applies. A person who receives a shared link to the dashboard sees the default environment and cannot switch it, so the dashboard is opened by signed-in operators only.

## 5. How the split by tag works

A tag query uses `WHERE tag.CostCenter = 'drones'` or `GROUP BY tag.CostCenter` over service metrics. It works only after the account turns on resource tags for telemetry, a setting at no additional cost that indexes resources and their tags with Resource Explorer and attaches the tags to their metrics. Each widget holds at most one tag query, and a query returns at most 500 series, far above the dozens of functions, queues and tables of the pilot.

| Resource | Tag query | What the dashboard does instead |
|---|---|---|
| Functions, queues, tables, event rules, the HTTP API, the archive stream and VPN connections | Supported | Tag query |
| The private REST API of the centers | Not in the list of supported resources | The widget names the API |
| Custom metrics | They come from a log entry and belong to no tagged resource | Each one comes from a single area, so its row already places it, and a saved query splits it by farm, node or center |
| The center links | Supported, but the network module tags them `plataforma` until it accepts a separate tag set for them | The tunnel widget shows nothing under `acopio` until then, and the cost dashboard places that cost under `plataforma` |

A farm is not a cost center. Farms share the same functions, queues and tables, so no tag separates one farm from another. The operational dashboard reaches a single farm through the saved query of silent nodes, and the cost dashboard through the farm share of section 6.

When a metric matches a resource whose tags changed more than ten times, a tag query keeps only the latest ten tagged versions. Tags in this platform change only through a Terraform change, so that limit is not reached in practice.

## 6. Cost dashboard

Cost Explorer shows cost by tag only for tags activated as cost allocation tags. The bootstrap of the account activates `Environment`, `CostCenter` and `Owner`. A key can take up to 24 hours to appear for activation after a resource first carries it, and up to 24 hours more to become active. Cost from before the activation carries no tag, so the first days of a new environment appear without a cost center.

| Report | Grouped by | Filter | Granularity and range | Question it answers |
|---|---|---|---|---|
| Cost by cost center | `CostCenter` | Environment of production | Monthly, last six months | Where the money of the pilot goes, farms against drones against collection |
| Cost by environment | `Environment` | none | Monthly, last six months | How much test and development add to production |
| This month by day | `CostCenter` | Environment of production | Daily, month to date | Whether a harvest week or a drone campaign moves the cost now |
| Test spending | Service | `CostCenter` equal to `pruebas` | Monthly, last three months | What exists only to test and whether it was left running |
| Cost without a cost center | Service | Resources with no `CostCenter` value | Monthly, month to date | Which spending escapes the tags, so the tag rules can be fixed |
| Cost by team | `CostCenter` | `Owner`, one team at a time | Monthly, last three months | What each team answers for |

In the pilot, where each environment has its own account, Cost Explorer in the management account also groups by linked account. The `Environment` tag and the account give the same split, and the tag keeps the reports equal in the demonstration account.

### Cost of one farm

The farm share divides the `fincas` cost of the month by each farm's share of device messages. A saved query counts messages by `farm_id` in the ingestion log. A farm that sent 2,160 of the 108,000 device messages of a harvest month carries 2 percent of the `fincas` cost. The calculation runs once a month for the operations report. A farm with more nodes or a longer drying season carries more, which matches how it uses the shared services.

### Budgets beside the reports

The account budget of the bootstrap warns by mail at its thresholds. The cost dashboard explains a warning, and it does not send one.

## 7. What fails and what shows it

| Case | What the operator sees | What shows it |
|---|---|---|
| Resource tags for telemetry are off | Tag widgets are empty while the alarms work | The setting page of CloudWatch, and the alarm widget still shows every alarm |
| A resource lacks `CostCenter` | Its metrics fall in the group without a value, and its cost in the report without a cost center | The tag rules of the roots stop it at the plan in the first place |
| A cost allocation tag is not active | Cost Explorer offers no grouping by that tag | The cost allocation tags page of the Billing console |
| A new function, queue or table | It appears in the tag widgets with no dashboard change | Tag queries select by tag, so no name is listed |
| A new custom metric | It has no widget | The checker fails while a widget points to a metric outside the six |
| The page is opened by a shared link | The viewer cannot switch environment | Sharing is not used |

## 8. Cost

Prices are from the AWS Price List API for us-east-1, CloudWatch publication of 2026-11-04 and Cost Explorer publication of 2026-09-11.

| Item | Rate | Pilot use | USD a month |
|---|---|---|---|
| CloudWatch dashboard | USD 3.00 per dashboard a month, prorated by the hour | One, in the production account | 3.00 |
| Metric requests while the dashboard loads | USD 0.01 per 1,000 metrics requested through the API | Console loads, see the assumption below | 0.00 |
| Resource tags for telemetry | No additional cost | One setting per account and Region | 0.00 |
| Cost Explorer in the console | Free | Six saved reports | 0.00 |
| Cost Explorer API | USD 0.01 per request | None, the reports are read in the console | 0.00 |

| Month | Telemetry before alarms | Alarms | Dashboard | Total | Reference | Above the reference |
|---|---|---|---|---|---|---|
| Normal month | 2.13 | 2.80 | 3.00 | 7.93 | 2.20 | 5.73 |
| Harvest month | 2.55 | 2.80 | 3.00 | 8.35 | 2.20 | 6.15 |

The dashboard is the largest single line of the monitoring cost and buys the one page an operator opens first. If console loads were billed as API requests, a load reads about 40 metrics and 100 loads a month add about USD 0.04. The reference of USD 2.20 was set before any alarm or dashboard was designed. The gap is for the owner of the cost document to settle, and the cost document is not changed here.

## 9. Where each piece lives

| Piece | Terraform resource or place | Where |
|---|---|---|
| Operational dashboard | `aws_cloudwatch_dashboard`, with the body of the example | The root of each workload account, production in the pilot |
| Resource tags for telemetry | `aws_observabilityadmin_telemetry_enrichment`, one per account and Region. Destroying it turns the setting off | The bootstrap of each workload account |
| Cost allocation tags | `aws_ce_cost_allocation_tag`, one per key, in the bootstrap | Management account in the pilot, the single account in the demonstration |
| Saved Cost Explorer reports | Saved in the Billing console by the platform operator, with the table of section 6 as their definition | Management account in the pilot |

The pinned provider has Cost Explorer resources for cost allocation tags, cost categories and anomaly monitors, and none for a saved report. The table of section 6 is therefore the definition of the reports, and six reports are quick to recreate from it.

## 10. What the checker proves

`tools/dashboards_catalog.py` reads the example body, this document, the observability catalog, the alarm register and the tag policy. It fails when a widget cites a signal outside the catalog, when a custom metric widget uses a metric outside the six that the chosen telemetry keeps, when a widget holds a log query or more than one tag query, when a tag query reads a namespace that tag queries do not support, when a cost center in a query is not an allowed value, when the environment appears in the body outside the variable slots, when the alarm widget does not hold exactly the billed alarms of the register, when the table of section 4 and the body differ, and when the cost table no longer matches the telemetry, the alarms and the dashboard price.

```sh
python3 -I docs/architecture/tools/dashboards_catalog.py
```

It checks the design as written. It does not prove that a dashboard, a report or a setting exists.

## 11. Assumptions and pending confirmations

| Item | Who confirms | Effect if it fails |
|---|---|---|
| Metric requests made by the console while a dashboard loads carry no charge beyond the dashboard price | Operator, with the first bill that includes the dashboard | About USD 0.04 a month at 100 loads |
| Saved Cost Explorer reports carry no charge, since the console is free and no price is listed for them | Operator, with the first bill | The cost dashboard adds that line |
| Tag queries return the metrics of the pilot functions, queues, tables, rules and tunnels once resource tags for telemetry is on | Operator, in the test environment | Those widgets fall back to listing names, as the center API widget does |
| The network module accepts a separate tag set for the center links | Owner of the network module | Tunnels and their cost stay under `plataforma` |
| The six custom metrics keep one metric each, with no environment dimension | Owner of the observability design | In the demonstration account their widgets mix environments, so they are read with that in mind |
| 100 dashboard loads a month and about 40 metrics per load | Operator practice | Only the request line moves, if it is billed at all |

## 12. Sources

| Source | Used for |
|---|---|
| AWS Price List API, CloudWatch, us-east-1, publication of 2026-11-04 | Dashboard and metric request prices |
| AWS Price List API, Cost Explorer, us-east-1, publication of 2026-09-11 | API request price, and no line for console use or saved reports |
| AWS Cost Management user guide, what Cost Explorer is, read 2026-11-11 | Console use free of charge |
| AWS Billing user guide, activating user-defined cost allocation tags, read 2026-11-11 | Up to 24 hours to appear and up to 24 hours to activate |
| Amazon CloudWatch user guide, Metrics Insights query language and its limits, read 2026-11-11 | Tag filters and grouping, one query per widget, 500 series, ten tagged versions |
| Amazon CloudWatch user guide, resource tags for telemetry and its supported resources, read 2026-11-11 | The setting, its cost and the supported resource types |
| Amazon CloudWatch API reference, dashboard body structure, read 2026-11-11 | Widget types, the alarm widget of up to 100 alarms, Metrics Insights in a metric widget and pattern variables |
| Amazon CloudWatch user guide, dashboard variables, read 2026-11-11 | Switching values and the limit of shared dashboards |
| Amazon CloudWatch pricing page, read 2026-11-11 | A dashboard that loads a logs query bills the query |
| Terraform AWS provider 6.72.0, `aws_cloudwatch_dashboard`, `aws_observabilityadmin_telemetry_enrichment` and the Cost Explorer resources | Where each piece is declared |
| Service metric pages of Lambda, SQS, DynamoDB, EventBridge, Site-to-Site VPN and API Gateway, read 2026-11-11 | Metric and dimension names of the example body |
