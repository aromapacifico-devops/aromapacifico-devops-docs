# Monthly cloud cost by service and environment

This document gives the monthly cost of the cloud platform for a normal month and for a harvest month, line by line, with the volumes of the pilot and the calculation behind each figure. It covers the production environment in full and the development and test environments by the hour, adds the dedicated links of the collection centers, and shows how the cost grows as history accumulates. Prices, exchange rate and tax treatment follow the [price basis](price-basis.md). The drones, the field hardware and the savings decisions belong to their own cost documents.

## Contents

1. Volumes of the case
2. Production by service
3. Environments
4. Totals
5. Sensitivity
6. Assumptions and pending confirmations

### Terms used

| Term | Meaning in this document |
|---|---|
| Normal month | A month with cultivation monitoring, a little drying and a quarter of the harvest reception |
| Harvest month | A month with drying at its widest and sack reception at its peak |
| Fixed line | A cost that does not change with the volume of the month |
| Variable line | A cost that grows with messages, requests, objects or alerts |
| Upper bound | A figure chosen so the real cost cannot exceed it |

## 1. Volumes of the case

| Measure | Normal month | Harvest month | Where it comes from |
|---|---|---|---|
| Farm readings | 50,400 | 108,000 | 200 farms with cultivation readings, and about 20 or 100 farms drying |
| Carrier positions | 216,000 | 216,000 | 60 carriers × 12 positions an hour × 10 hours × 30 days |
| Sacks received | 9,000 | 36,000 | Up to 400 a day at each of 3 centers in harvest, a quarter in a normal month |
| Sack events | 63,000 | 252,000 | 7 events for each sack |
| Public sack queries | 135,000 | 540,000 | Peak of 30 a minute, for 10 hours a day and 30 days in harvest, a quarter in a normal month |
| Drone images | 1,500 | 9,000 | 3 MB each |
| Urgent alerts sent by SMS | 40 | 200 | Upper bound, since an alert confirmed on the phone sends no SMS |

The public queries are the one volume the pilot gives only as a peak. The calculation uses the peak for the whole day, so it is a ceiling, and the real cost is lower.

## 2. Production by service

Rates are the on-demand prices of `us-east-1` read on the retrieval date of the price basis. Amounts are in USD before tax.

| Line | Calculation | Normal month | Harvest month |
|---|---|---|---|
| Telemetry ingestion | Messages, rules, queue, function, tables, archive and the hourly configuration read of each node | 0.72 | 0.98 |
| Carrier positions | 216,000 requests through the API, function and table writes | 0.58 | 0.58 |
| Sack events | Transactional writes, reads and the trip index, with events grouped by truck. Center requests use the private REST API at USD 3.50 per million and add at most 0.03 | 0.20 | 0.81 |
| Public sack queries | Per million requests through the function URL, 0.60 web firewall, 1.03 function and 0.06 table read, which is 1.70. CloudFront requests stay inside its free tier | 0.23 | 0.92 |
| Inference | Trigger-derived image and telemetry workload from [inference cost](inference-cost.md), including the person filter, model, function time and estimation orthomosaic | 1.63 | 16.26 |
| New objects in S3 | Storage and uploads of the images of the month | 0.11 | 0.65 |
| Alert delivery | 40 or 200 SMS at USD 0.05087, plus push, logs and queues under USD 0.01 | 2.03 | 10.17 |
| Ranges, cases and delivery queues | Reads and writes of the small tables, under USD 0.05 together | 0.05 | 0.05 |
| Audit logs and trail | Sack reads, telemetry entries, delivery stream, storage and trail events, at the busiest case | 0.40 | 0.40 |
| **Variable lines** | | **5.95** | **30.82** |
| Site-to-site VPN | 3 connections × USD 0.05 × 730 hours | 109.50 | 109.50 |
| Interface endpoints | 3 endpoints × 2 zones × USD 0.01 × 730 hours | 43.80 | 43.80 |
| KMS | 5 keys × USD 1.00, four platform keys and one to sign drone packages | 5.00 | 5.00 |
| Secrets Manager | 4 secrets × USD 0.40 | 1.60 | 1.60 |
| Web firewall | 1 web ACL at USD 5.00 and 3 rules at USD 1.00 | 8.00 | 8.00 |
| CloudWatch | Allowance for alarms at USD 0.10 each and platform logs at USD 0.50 per GB ingested | 2.20 | 2.20 |
| Cognito | Within the free allowance of 10,000 monthly users with direct sign-in | 0.00 | 0.00 |
| **Fixed lines** | | **170.10** | **170.10** |
| **Cloud platform, production** | | **176.05** | **200.92** |

The network lines, VPN and endpoints, are 153.30 and make up about 87 percent of a normal month. Variable cost is small, so the serverless design leaves the savings in the network, and the demonstration environments exist only while the team uses them, which protects the credits. Removing the endpoints would save USD 43.80 a month and would send center traffic over the internet with MFA and TLS alone, so the design keeps them.

The audit line and the alert delivery line are upper bounds. A normal month spends less on audit than the busiest case, and the SMS line assumes that every urgent alert reaches the phone only by SMS.

The harvest column spreads 200 harvest-estimation flights evenly over four months. If all 200 flights occur in one month, the inference line reaches USD 45.95 and the production platform reaches USD 230.61. Inference appears once in the table: the line imports the complete workload total from the inference-cost document and no model, filter, function or telemetry charge is added elsewhere.

Cognito stays free while the users who sign in directly stay under 10,000 a month, and the pilot has a few hundred. Users who federate through an external identity provider are billed beyond the first 50.

## 3. Environments

Serverless resources cost almost nothing while idle, so an environment costs what its network pieces cost by the hour. Test and development come up for a work session and come down at night.

| Environment | Pieces billed by the hour | USD an hour | A session of 8 hours | 80 hours in a month |
|---|---|---|---|---|
| Development | 3 interface endpoints in one zone, data and objects keys | 0.033 | 0.26 | 2.62 |
| Test | 1 VPN connection, 3 interface endpoints in one zone, data and objects keys | 0.083 | 0.66 | 6.62 |
| Production, always on | 3 VPN connections, 3 endpoints in two zones, data and objects keys | 0.213 | 1.70 | 17.02 |

Production runs all month in the pilot, so its monthly cost is the one in section 2. The row above shows the cost of an environment that comes up for a session, as the demonstration does. A test environment forgotten for a month at 24 hours a day costs USD 60.40, and a production environment forgotten the same way costs USD 155.30.

The platform key of each environment encrypts its state, so the bootstrap creates it once and it stays when the environment comes down. The keys of shared, development and test therefore bill all month, USD 3.00, whether or not those environments are up. The production platform key is one of the five keys of section 2.

## 4. Totals

| Item | Normal month | Harvest month |
|---|---|---|
| Cloud platform, production | 176.05 | 200.92 |
| Dedicated links of three centers, at the exchange rate of the price basis | 229 to 321 | 229 to 321 |
| **Platform with links** | **405 to 497** | **430 to 522** |
| Development and test, 80 hours each in a month | 9.24 | 9.24 |
| Platform keys of shared, development and test, kept by the bootstrap | 3.00 | 3.00 |
| Stored history and its backup, added at the end of year five | About 10.2 | About 10.2 |

The stored history is the cost of keeping five years of records, and it grows from nothing in the first month. It adds about USD 7.0 of storage, which the [persistence and archive](../architecture/persistence-and-archive.md) document calculates, and USD 3.24 of continuous backup of the sack tables, which the [recovery](../architecture/recovery.md) design calculates. The links are priced from an operator reference in pesos, so a quote changes them. Every figure is before IVA, which adds up to 19 percent if it applies.

## 5. Sensitivity

| Change | Effect on the harvest month |
|---|---|
| Public queries at half the ceiling | 0.46 less |
| No SMS, every urgent alert confirmed on the phone | 10.17 less |
| Images double | 15.08 more for inference, 0.65 more for storage |
| Sack events not grouped by truck, one request per event | 0.46 more |
| Peso at its strongest in the last 120 published rates | Links 246 to 345 |
| IVA on every line | Up to 19 percent more |

## 6. Assumptions and pending confirmations

| Item | Who confirms | Effect if it fails |
|---|---|---|
| A normal month receives a quarter of the sacks and of the public queries of a harvest month | Federation | The sack and query lines change in proportion, by less than USD 2 |
| Public sack queries run at their peak all day in harvest | Federation | The ceiling falls and the line with it |
| A public query reads half a read unit of the table, since a buyer view stays under 4 KB | Schema of the buyer view | The table line doubles, by cents |
| SMS reaches the phone only for urgent alerts | Federation | The SMS line changes, up to its upper bound |
| Users who sign in directly stay under 10,000 a month | Federation | Cognito costs USD 0.015 per user above the allowance |
| Cost of the dedicated links | Operator quotes | The totals with links change |
| CloudWatch alarms and platform logs stay within USD 2.20 a month | Team, when the operational alarms are defined | Each extra alarm adds USD 0.10 and each extra GB of logs USD 0.50 |

## Sources

- [Price basis](price-basis.md), for rates, exchange rate and tax.
- The cost sections of the [telemetry ingestion](../iot/telemetry-ingestion.md), [farm connectivity](../network/farm-connectivity.md), [carrier tracking](../network/carrier-tracking.md), [custody chain](../traceability/custody-chain.md), [alert delivery](../iot/alert-delivery.md), [drone mission link](../network/drone-mission-link.md), [audit](../security/audit.md), [center WAN sizing](../network/center-wan-sizing.md) and [environments and promotion](../architecture/environments-and-promotion.md) documents of this platform.
- AWS, Amazon Cognito pricing page, for the free allowance of direct sign-in users.
