# Farmer history and screens

Part of the farmers keep their records in a notebook and distrust replacing it with an application. The farmer application therefore shows a farm in three screens, Farm, Drying and Alerts, in plain language, with numbers only on request. This document defines what each screen shows and where each element comes from, how a farmer starts and finishes a drying, the records that keep five years of harvests, the query contract the application uses, and the monthly pilot report that the Federation reads. The application itself is designed elsewhere and is not built in the pilot.

## Contents

1. Terms
2. Context and volumes
3. Three screens
4. Starting and finishing a drying
5. Records behind the screens
6. How far back the farmer sees
7. Query contract for the farmer
8. Pilot report
9. What fails and what the platform does
10. Cost
11. What the infrastructure code covers
12. Assumptions and pending confirmations
13. Sources

## 1. Terms

| Term | Meaning in this document |
|---|---|
| Drying lot | One batch of coffee on the drying site, from the moment the farmer starts drying until the farmer finishes it |
| Drying flag | The value in the desired state of the node that turns hourly grain readings on or off |
| Farm register | The record of each farm, its owner and the nodes that served it over time |
| Node link | The period during which one node served one farm, with a start and an end |
| Lot summary | The figures of a drying lot written once it closes, which stay five years |
| Alert state | The current state of each variable of a node, in range or out of range |
| Pilot report | A monthly set of aggregated figures about how the pilot works, by department and municipality |
| Federation analyst | A Federation staff member who reads the pilot report and no individual record |

## 2. Context and volumes

The [sensors and operation](sensors-and-operation.md) design fixes what a node measures and that the farmer starts and stops the drying cadence from the application. The [telemetry ingestion](telemetry-ingestion.md) stores each reading and each alert, the [alert ranges](configurable-thresholds.md) decide when a value leaves its range, and the [alert delivery](alert-delivery.md) brings the alert to the phone. One node serves the cultivation zone and the drying site of a farm, and it reads its desired state after each hourly connection. [Identity and access](../security/identity-and-access.md) gives the farmer read access to the records of their own farms only.

| Figure | Normal month | Harvest month | Origin |
|---|---|---|---|
| Farmers with the application | 200 | 200 | One owner for each pilot farm |
| Farms drying | About 20 | About 100 | Sensors and operation |
| Drying lots started | About 60 | About 300 | Three lots for each farm drying, an assumption |
| Openings of the application | About 13,200 | About 18,000 | Two a day for each farmer, four a day while drying, an assumption |
| Requests to the platform | About 26,400 | About 36,000 | Two for each opening |
| Crop readings of one farm in 90 days | 540 | 540 | Six a day |
| Drying readings of one lot of seven days | 168 | 168 | One an hour |

A reading takes about 0.5 KB, so 90 days of crop readings of one farm come to about 270 KB, and one week of drying to about 84 KB. Each request of the application therefore reads a few kilobytes to a few hundred kilobytes.

## 3. Three screens

The application opens on the Farm screen. A bar at the bottom moves between Farm, Drying, Alerts and Sacks, each with an icon and a word. Sacks belongs to the registration of sacks, which the [custody chain](../traceability/custody-chain.md) defines, and this document leaves it out. A farmer with more than one farm picks it at the top of the screen, and a farmer with one farm never sees that choice.

Every screen answers one question in one sentence first, and the numbers sit one tap below. Times appear in Colombia time, five hours behind UTC with no daylight saving, while every store keeps UTC.

### Farm

The question is whether the crop is well.

| Element | What the farmer sees | Source |
|---|---|---|
| State of the crop | "Your crop is within range" or one sentence per variable out of range, such as "Soil humidity is below the range" | Alert state of each cultivation variable of the active node |
| Last news from the node | "The node reported 40 minutes ago", or "No data from the node for 26 hours" after 24 hours with no message | Newest `received_at` of the active node |
| Drying in progress | A short line "Drying since Monday" that opens the Drying screen | Open drying lot of the farm |
| See the numbers | The last value of each of the eight cultivation variables, with its recommended range where one exists, and a chart per variable for the last 7 days, extendable to 90 | Readings table, crop stream |
| Enter a pH reading | A form for a manual pH value, used when the probe fails | Written as a reading marked manual |

A value outside its recommended range appears with its range and raises nothing, as the alert ranges define. Nitrogen, phosphorus and potassium show the sentence "No range published yet" until the Federation publishes one.

### Drying

The question is whether the coffee on the drying site is safe.

| Element | What the farmer sees | Source |
|---|---|---|
| No lot drying | A large button "Start drying" | Farm register shows no open lot |
| Lot starting | "Starting. The node begins to measure within one hour" | Open lot whose start the node has not yet applied |
| Lot drying | Days and hours since the start, the last grain temperature and grain humidity, and the target of 12 percent next to the humidity | Open lot and the newest drying reading |
| Grain above 40 °C | A red band with "Grain temperature is above 40 °C. Act now" | Alert state of grain temperature |
| Finish drying | A button that asks for confirmation | Open lot |
| Past lots | One line per lot with its dates, its duration, the highest grain temperature and the last grain humidity, for five years | Drying lots table, lot summaries |
| Detail of a past lot | The summary, and a chart of grain temperature and humidity while the readings are less than 90 days old | Lot summary and readings table, drying stream |

Reaching the humidity target never finishes a lot. The farmer decides, since only the farmer sees the grain.

### Alerts

The question is what happened and what to do.

| Element | What the farmer sees | Source |
|---|---|---|
| Active alerts | Alerts whose variable is still out of range, first in the list | Alerts table joined with the alert state |
| History | Every alert of the farm, newest first, grouped by month, for five years | Alerts table |
| One alert | The sentence, the time of the reading, and an action in plain words, "Act now" for urgent drying alerts and "Check at your next visit" for the others | Alert record and the kind of range |
| Late alert | "This reading waited in the node and arrived at 14:20" when the reading reached the platform in a later cycle | `kind` of the alert record |
| Drone review | For a cultivation alert that opened a drone case, the state of that case | Case of the [alert to drone confirmation](alert-to-drone-confirmation.md) |

A push notification opens the alert it announces. An urgent drying alert opens the Drying screen, where the farmer acts.

### With no data on the phone

Farmers have data mostly in the municipal seat and on main roads. The application keeps the last answer of each screen and shows it with the line "Updated on Tuesday at 6:10", so a screen is never empty. Starting or finishing a drying with no data waits on the phone with the line "Will be sent when the phone has data", and the node changes its cadence only after the platform receives the request.

## 4. Starting and finishing a drying

| Step | Start | Finish |
|---|---|---|
| 1 | The farmer taps "Start drying" and confirms | The farmer taps "Finish drying" and confirms |
| 2 | The platform creates the lot in the state `open` and marks it as the open lot of the farm, in one transaction that fails if another lot is open | The platform moves the lot to `closing`, records the end time and clears the open lot of the farm |
| 3 | The platform sets the drying flag to on in the desired state of the node | The platform sets the drying flag to off |
| 4 | The node reads the flag at its next hourly connection and reports it, and the lot records when the node applied it | Same |
| 5 | Hourly grain readings arrive and are judged against the grain ranges | Readings taken before the end may still drain from the node buffer for up to 24 hours |
| 6 | | A daily job writes the lot summary 24 hours after the end and moves the lot to `closed` |

One node has one grain probe, so a farm has at most one open lot. The summary waits 24 hours because a reading can stay that long in the node buffer, and a summary written at once would leave out the last readings of a lot finished during an outage.

A node on the LoRa path has no Device Shadow. It receives the flag in a downlink with a version and reports the applied version in each frame, as the [LoRa path](../network/lora-out-of-coverage.md) defines. The screens and the lot behave the same.

A lot left open is a likely oversight, and an idle grain probe saves energy on the node. After 15 days the application reminds the farmer once, and after 30 days the daily job finishes the lot on its own and records that the platform finished it.

| Lot summary field | Calculation |
|---|---|
| `hours_monitored` | Hours from the first to the last drying reading of the lot |
| `readings_expected`, `readings_received` | One per hour between the applied start and the end, and the readings found |
| `grain_temp_max_c` | Highest grain temperature |
| `hours_above_40c` | Readings above 40 °C, one hour each |
| `grain_humidity_first_pct`, `grain_humidity_last_pct` | First and last grain humidity |
| `alerts` | Alerts of the lot |

## 5. Records behind the screens

Two records are new. The farm register links the readings, which are kept by node, to the farm, which is what the farmer owns. The drying lots table keeps each drying with its summary for five years. The readings table, the alert state items and the alerts table come from the telemetry ingestion and do not change.

### Farm register

| Item | Key | Fields | Written by |
|---|---|---|---|
| Profile | Partition `farm_id`, sort `profile` | `owner_id`, `owner_from`, `farm_name`, `department`, `municipality`, `open_drying_lot_id` | Enrollment of the farm by Federation field staff, and the drying functions for the open lot |
| Node link | Partition `farm_id`, sort `node#<valid_from>` | `node_id`, `link`, `lot_id`, `valid_from`, `valid_to` | Installation and replacement of a node |

An index on `owner_id` lists the farms of a farmer. `owner_id` is the subject of the farmer in the user pool, and the name and phone of the person stay in the pool, so the register holds no direct identity.

A replaced node closes its link with `valid_to`, and the new node opens a link from the same moment. The history of the farm then reads both nodes, each one within its own period, and no reading of the old node reaches another farm. When a farm changes owner, `owner_from` moves to the date of the change, and the new owner sees the records from that date on.

### Drying lots table

| Field | Meaning | Written by |
|---|---|---|
| `farm_id` | Partition key | Start function |
| `drying_lot_id` | Sort key, a time-ordered identifier, so lots list by start | Start function |
| `node_id` | Node that measured the lot | Start function, from the active node link |
| `state` | `open`, `closing` or `closed` | Each function moves it forward with a conditional update |
| `started_at`, `started_by` | Time the platform accepted the start, and who asked | Start function |
| `requested_at` | Time the farmer pressed the button on the phone | Start function, from the request |
| `applied_at` | Time the node reported the flag on | Rule on the shadow updates of the node |
| `ended_at`, `ended_by` | End time, and `farmer` or `platform` | Finish function or daily job |
| `summary`, `summarized_at` | Lot summary of section 4 and when it was written | Daily job |

A sparse index holds only lots in `open` or `closing`, so the daily job reads a few dozen items and never the whole table. Lots stay five years, the same as alerts.

### Link from a sack to its drying

A sack carries the drying variables to the buyer, so the registration of a sack at the farm accepts an optional `drying_lot_id`. The registration works with no connection, so the application offers the lots of the farm it already holds, with the most recent closed lot first. A sack registered at a center, or from coffee dried with no node, carries no lot, and the buyer view then shows no drying variables.

## 6. How far back the farmer sees

The farmer sees the readings of the last 90 days, and the alerts and the drying lots with their summaries for five years. Older readings stay in the telemetry archive, which the pilot report reads.

| Option | For | Against | Result |
|---|---|---|---|
| Readings of 90 days, alerts and lots for five years | Uses the stores already designed. Past harvests stay visible through the lot summaries, which hold what a notebook records | A farmer cannot chart the soil humidity of two years ago | **Chosen** |
| The same, plus older readings from the archive on request | Every reading reachable | Each query takes seconds and is charged by the data it scans, and a farmer session would reach the archive of every farm through one query engine | Discarded |
| The same, plus a daily summary per farm and variable kept five years | Years of crop history at low cost | One more writer and one more table, for a chart few farmers would open during a pilot | Discarded, and the first to add if farmers ask for it |

## 7. Query contract for the farmer

The application calls the platform API with the Cognito token of the farmer and sends the header `X-Contract-Version`, as the other applications do.

| Method and path | Purpose | Store and key |
|---|---|---|
| `GET /farms` | Farms of the farmer | Farm register, index on `owner_id` |
| `GET /farms/{farm_id}/status` | Content of the Farm screen and the head of the Drying screen | Profile, active node link, alert state items, newest readings, open lot |
| `GET /farms/{farm_id}/readings?stream=&from=&to=&cursor=` | Readings of one stream for a chart, 7 days by default and 90 days at most | Readings table, by node link and `measured_at` |
| `GET /farms/{farm_id}/alerts?from=&to=&cursor=` | Alert history, newest first | Alerts table, `farm_id` and `raised_at` |
| `GET /farms/{farm_id}/drying-lots?cursor=` | Past and current lots, newest first | Drying lots table, `farm_id` |
| `GET /farms/{farm_id}/drying-lots/{drying_lot_id}` | One lot with its summary, and its readings while they exist | Drying lots table and readings table |
| `POST /farms/{farm_id}/drying-lots` | Start a drying | Drying lots table, farm register and drying flag |
| `POST /farms/{farm_id}/drying-lots/{drying_lot_id}/finish` | Finish a drying | Same |
| `POST /farms/{farm_id}/manual-readings` | A manual pH value | Readings table, active node, marked manual |
| `POST /alerts/{alert_id}/receipt` | Receipt of a push, defined by the alert delivery | Alerts table |

Every path that names a farm reads its profile first and compares `owner_id` with the subject in the token. A farm of another owner answers 404, the same as a farm that does not exist, so a farmer cannot learn which farm identifiers exist. Every query reads DynamoDB by key, and no path reaches the archive.

A readings query lists the node links that overlap the period, reads each node within its own link and within the period of ownership, and merges the results by `measured_at`. A page holds up to 500 readings and returns a cursor for the next one, which keeps each answer well under the 1 MB that DynamoDB returns in one query.

| HTTP status | Meaning | The application |
|---|---|---|
| 200 | The answer | Shows it and keeps it for use with no data |
| 400 with `contract_version_unsupported` | The application is too old | Shows the kept answers and asks for an update |
| 401 | The session ended | Shows the kept answers and asks for a sign-in |
| 404 | The farm or lot is unknown to this farmer | Removes it from the kept list |
| 409 with `drying_lot_open` | A start while another lot is open | Opens the lot already drying |
| 429 | Too many requests | Retries after the time in `Retry-After` |
| 5xx or a timeout | A failure of the platform or the path | Shows the kept answers and retries with backoff |

Example answer of the status, with invented identifiers.

```json
{
  "farm_id": "farm-demo-001",
  "farm_name": "La Esperanza",
  "node": {
    "node_id": "node-41-00137",
    "last_received_at": "2026-05-14T14:01:52Z",
    "silent": false
  },
  "crop": {
    "measured_at": "2026-05-14T12:00:00Z",
    "out_of_range": [
      {"variable": "soil_humidity_pct", "value": 37.5, "since": "2026-05-14T08:00:00Z", "range_version": 1}
    ]
  },
  "drying": {
    "drying_lot_id": "dl-01HXRT6Q2A",
    "state": "open",
    "started_at": "2026-05-11T13:05:00Z",
    "applied_at": "2026-05-11T13:41:10Z",
    "measured_at": "2026-05-14T14:00:00Z",
    "grain_temp_c": 41.6,
    "grain_humidity_pct": 18.2,
    "grain_humidity_target_pct": 12,
    "urgent": true
  }
}
```

Example item of a closed lot.

```json
{
  "farm_id": "farm-demo-001",
  "drying_lot_id": "dl-01HXA2M7KE",
  "node_id": "node-41-00137",
  "state": "closed",
  "started_at": "2026-05-02T12:30:00Z",
  "applied_at": "2026-05-02T13:41:05Z",
  "ended_at": "2026-05-09T21:15:00Z",
  "ended_by": "farmer",
  "summary": {
    "hours_monitored": 175,
    "readings_expected": 176,
    "readings_received": 176,
    "grain_temp_max_c": 41.6,
    "hours_above_40c": 2,
    "grain_humidity_first_pct": 52.4,
    "grain_humidity_last_pct": 11.8,
    "alerts": 1
  },
  "summarized_at": "2026-05-10T23:00:04Z"
}
```

## 8. Pilot report

The pilot report shows the Federation how the monitoring of farms works across the pilot, month by month. It names no person and no farm.

| Figure | Calculation | Source |
|---|---|---|
| Farms reporting | Farms with at least one reading in the month, over farms with an active node link | Readings archive and farm register |
| Completeness of readings | Readings received over readings expected, six a day for crop and one an hour for each open lot | Readings archive, farm register and drying lots |
| Readings that waited in the buffer | Share of readings with `buffered` true | Readings archive |
| Readings lost past 24 hours | Growth of `dropped_total` of each node during the month | Readings archive |
| Alerts | Count by variable, by live or drained, and urgent ones | Alerts |
| Alerts handed off within 5 minutes | Share of live alerts with `push_handoff_at` minus `measured_at` of 5 minutes or less | Alerts |
| Alerts received on the phone, and SMS sent and delivered | Shares over the alerts of the month | Alerts |
| Drying lots | Count, median duration, share with any hour above 40 °C, median last grain humidity | Drying lots |
| Crop outside the recommended range | Share of crop readings outside the recommended pH and air temperature ranges | Readings archive and ranges table |

Every figure is grouped by department and by municipality. A municipality with fewer than three farms in the month joins the figure of its department, so no line describes one farm. A figure for each farm, such as a node with no data for 24 hours, belongs to the operational alarms of the platform.

The handoff figure uses the same definition as the alert delivery objective of the platform, so the report and the objective never disagree. The report counts the month, and the objective follows its own window.

### How the report is produced

| Step | Action |
|---|---|
| 1 | A schedule starts a Step Functions workflow on the second day of each month at 06:00 Colombia time, so a reading drained up to 24 hours late is in the archive |
| 2 | The workflow exports the alerts table, the drying lots table and the farm register to S3 through the DynamoDB export, which reads from point-in-time recovery and uses no table capacity |
| 3 | It waits for each export and points the Athena table of each one to the new export |
| 4 | It runs the report queries in an Athena workgroup with a limit of 1 GB scanned per query, waiting for each one |
| 5 | The results land as CSV files in the reports prefix, under the year and month |
| 6 | Exports expire after 35 days through a lifecycle rule, and the report files stay five years |

The readings archive is organized by the day of arrival, so the queries filter by `measured_at` and scan one more day, since a reading drained after midnight falls in the next day. The exports hold the farm register, including `owner_id`, so the queries never select it, and the exports expire once the report exists.

### Who reads it

A Federation analyst signs in through IAM Identity Center with a permission set that reads only the reports prefix and decrypts only with its key. The analyst runs no query and sees no record of a farm, a farmer, an alert or a reading. The platform operator keeps no access to business data, and the workflow runs under its own role.

| Option | For | Against | Result |
|---|---|---|---|
| Federation analyst reading aggregated files | No personal data in the report, operation and business data stay apart, one place to remove access | One more identity to manage | **Chosen** |
| The platform operator runs and reads the report | No new identity | The operator would see business data, which the access design rules out | Discarded |
| A report for each farmer only | Nothing new | No view of the pilot as a whole | Discarded |

## 9. What fails and what the platform does

| Failure | How it shows | What the platform does |
|---|---|---|
| The phone has no data | The request does not leave | The application shows the kept answer with its time, and requests wait on the phone |
| The node does not apply the drying flag within two hours | `applied_at` stays empty | The Drying screen says the node has not picked up the change, and the node with no telemetry alarm covers a silent node |
| A reading arrives after the lot summary | Its `measured_at` falls inside a closed lot | The summary stays, and the reading still appears in the chart while it is less than 90 days old |
| The farmer forgets to finish a lot | The lot is open for 15 days | One reminder, then the platform finishes it at 30 days |
| Two phones start a lot at the same time | The transaction finds an open lot | The second start answers 409 and opens the lot already drying |
| A node is replaced | A new node link opens | Both nodes appear in the history within their own periods |
| An export or a report query fails | The workflow ends in a failed state | The workflow retries each step twice, then alarms the platform operator, and a run can be started again for the same month |
| A report query would scan more than 1 GB | Athena cancels it | The workflow fails, which points to a query without a time filter |
| A request for another owner's farm | The owner check fails | 404, and the request appears in the API logs |

## 10. Cost

Rates come from the AWS Price List API for us-east-1. The script `tools/farmer_history_cost.py` repeats the calculation.

| Item | Rate | Harvest month | USD |
|---|---|---|---|
| HTTP API requests | USD 1.00 per million | 36,000 | 0.04 |
| Lambda requests and duration, 256 MB on Arm for 150 ms | USD 0.20 per million and USD 0.0000133334 per GB-second | 36,000 | 0.03 |
| DynamoDB reads | USD 0.125 per million read request units | About 180,000 | 0.02 |
| DynamoDB writes of lots and Device Shadow operations | USD 0.625 per million write request units and USD 1.25 per million operations | 300 lots | Below 0.01 |
| DynamoDB exports for the report | USD 0.10 per GB | About 0.05 GB | Below 0.01 |
| Athena queries | USD 5 per TB scanned | 12 queries of about 0.1 GB | Below 0.01 |
| Step Functions | USD 0.000025 per state transition | About 60 | Below 0.01 |
| **Total** | | | **About 0.10** |

A normal month costs about USD 0.08. Storage of the drying lots and of the report files stays under a few megabytes over five years, so it adds nothing visible. The cost grows with the number of openings, and ten times more openings would still cost under USD 1 a month.

## 11. What the infrastructure code covers

The infrastructure code of the pilot implements the telemetry ingestion, which already creates the readings table, the alerts table and their point-in-time recovery. The farm register, the drying lots table, the API routes of section 7, the daily job and the report workflow belong to the application layer, which is designed here and stays outside the code. A later application module would create them with the keys and roles of the security module.

## 12. Assumptions and pending confirmations

| Item | Who confirms | Effect if it fails |
|---|---|---|
| A farmer opens the application about twice a day, four times while drying | First harvest | Cost moves in proportion, and stays under a few dollars a month |
| A farm dries about three lots in a harvest month | Federation, with the farmers | Volumes of lots change, with no effect on the design |
| A farmer holds one to three farms, each with one active node | Federation | Queries read more node partitions and page sooner |
| 30 days is longer than any real drying | Federation, with the farmers | The automatic finish moves to a longer limit |
| Federation field staff enroll each farm with its owner before the node is installed | Federation | Installation also creates the farm profile |
| Most farmer phones run Android | Federation, with the farmer application | iPhones need a notification extension for the receipt, and the screens do not change |
| A municipality with fewer than three farms is enough to hide a single farm in the report | Federation and legal counsel | The grouping threshold rises, or the report goes to department level only |

## 13. Sources

- Amazon DynamoDB, [export to S3](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/S3DataExport.HowItWorks.html) and [export output format](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/S3DataExport.Output.html), and [Query pagination](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Query.Pagination.html) with its 1 MB page.
- Amazon Athena, [per query data usage control](https://docs.aws.amazon.com/athena/latest/ug/workgroups-setting-control-limits-cloudwatch.html).
- AWS Step Functions, [Athena integration with the run a job pattern](https://docs.aws.amazon.com/step-functions/latest/dg/connect-athena.html).
- AWS Price List API, us-east-1, for [DynamoDB](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonDynamoDB/current/us-east-1/index.json), [Athena](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonAthena/current/us-east-1/index.json), [Step Functions](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonStates/current/us-east-1/index.json), [Lambda](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AWSLambda/current/us-east-1/index.json), [API Gateway](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonApiGateway/current/us-east-1/index.json) and [IoT Core](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AWSIoT/current/us-east-1/index.json).
- [Sensors and operation](sensors-and-operation.md), [telemetry ingestion](telemetry-ingestion.md), [alert ranges](configurable-thresholds.md), [alert delivery](alert-delivery.md), [custody chain](../traceability/custody-chain.md) and [identity and access](../security/identity-and-access.md) of this platform.
