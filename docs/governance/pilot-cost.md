# Cost of the pilot

This document gathers in one place what the pilot costs the Federation at current prices. It covers the cloud platform in a normal month and in a harvest month, the links of the three collection centers, the development and test environments, inference with its cost per 1,000 invocations in harvest, the hardware and monthly amount of a farm, the drone service and the 100 hours of infrastructure code. It closes with the decisions that lower or avoid cost, the savings the design leaves on purpose, and the assumptions that still need a confirmation. Each section summarizes a detailed cost document of this repository, which holds the calculation line by line.

## Contents

1. [Terms](#1-terms)
2. [Summary](#2-summary)
3. [Basis of the figures](#3-basis-of-the-figures)
4. [Cloud platform](#4-cloud-platform)
5. [Links of the collection centers](#5-links-of-the-collection-centers)
6. [Development and test environments](#6-development-and-test-environments)
7. [Inference in harvest](#7-inference-in-harvest)
8. [Farm hardware and monthly amount](#8-farm-hardware-and-monthly-amount)
9. [Drone service](#9-drone-service)
10. [Infrastructure code](#10-infrastructure-code)
11. [Decisions that lower or avoid cost](#11-decisions-that-lower-or-avoid-cost)
12. [Savings left on purpose](#12-savings-left-on-purpose)
13. [Exchange rate and tax](#13-exchange-rate-and-tax)
14. [Assumptions and pending confirmations](#14-assumptions-and-pending-confirmations)
15. [Sources](#15-sources)

## 1. Terms

| Term | Meaning in this document |
|---|---|
| Normal month | One of the eight months a year with crop monitoring, little drying and a quarter of the sack reception of a harvest month |
| Harvest month | One of the four months a year with drying at its widest, sack reception at its peak and the harvest estimation flights |
| Following year | Any year after the first, once the farms are installed and every lot is delimited |
| Field operation | What the farms cost each month once installed, which is data, SIM charges, maintenance visits, the shared gateways and a reserve to replace parts at the end of their life |
| Known part | The sum of the items with a verified or estimated price. Items still without a price are listed apart and are never counted as zero |
| TRM | Tasa Representativa del Mercado, the official rate of pesos per dollar |
| IVA | Colombian value added tax |

## 2. Summary

Figures in USD before IVA, at the prices of the [price basis](price-basis.md).

| Item | Normal month | Harvest month | Following year |
|---|---:|---:|---:|
| Cloud platform, production | 181.78 | 207.07 | 2,282.52 |
| Links of the three collection centers | 229 to 321 | 229 to 321 | 2,748 to 3,852 |
| Development and test, with their keys | 12.24 | 12.24 | 146.88 |
| Field operation of 200 farms | 2,176.88 | 2,176.88 | 26,122.56 |
| Drone service | 3,777.46 | 20,410.90 | 111,864.52 |
| **Total without the links** | **6,148.36** | **22,807.09** | **140,416.48** |
| **Total with the links** | **6,377 to 6,469** | **23,036 to 23,128** | **143,164 to 144,268** |

A following year holds eight normal months and four harvest months. The harvest month of the drone service is the one of the first year, and in later years the storage of earlier images adds about USD 0.31 to it. The year column takes the drone service from its own yearly figure, so it is about USD 1 above eight normal months plus four harvest months.

| One-time item | USD | COP at the TRM |
|---|---:|---:|
| Field hardware and installation of 200 farms, known part | 93,495.54 | 305,719,196 |
| Start-up round of the drone service, extra cost of the first year | 32,954.95 | 107,758,732 |
| Infrastructure code, 100 hours | 2,276.00 | 7,442,247 |

| Share of the following year | Percent |
|---|---:|
| Drone service | 77.8 |
| Field operation | 18.2 |
| Links of the centers | 2.3 |
| Cloud platform and environments | 1.7 |

The drone service carries almost four fifths of a year, and the cloud platform less than two percent. Any review of the budget should therefore start with the drone contract and the visits to the farms, and the cloud figures matter mostly as a check that nothing runs without need. The shares use the middle of the link range.

## 3. Basis of the figures

| Choice | Value |
|---|---|
| Currency | USD, since the cloud bills in dollars and most hardware is priced in dollars |
| Cloud prices | On-demand list prices of `us-east-1`, with no credit, free tier or discount, read from the AWS Price List API on 10 November 2026 |
| Exchange rate | TRM of 10 November 2026, 3,269.88 pesos per dollar, for every price quoted in pesos |
| Tax | Every figure before IVA. Section 13 shows the effect of IVA of 19 percent |
| Month | 730 hours for hourly items and 30 days for volumes |
| Volumes | The pilot figures, 200 farms in Cauca, Huila and Tolima, 60 carriers, up to 400 sacks a day at each of three centers in harvest, and a harvest of four months |

The Federation decides which exchange rate and which tax treatment the budget uses. Until it does, the figures follow the price basis, and section 13 shows how much they move.

## 4. Cloud platform

The [monthly cloud cost](cloud-cost.md) gives each line with its calculation.

| Group of lines | Normal month | Harvest month |
|---|---:|---:|
| Variable lines, which follow the volume of the month | 8.08 | 33.37 |
| VPN and interface endpoints | 153.30 | 153.30 |
| Keys, secrets, web firewall, alarms and dashboard | 20.40 | 20.40 |
| **Cloud platform, production** | **181.78** | **207.07** |
| Harvest month with all estimation flights | | 236.76 |

The variable lines cover telemetry ingestion, carrier positions, sack events, public sack lookups, inference, new drone objects, alert delivery with SMS at its upper bound, the small tables, audit and operational telemetry. Together they stay under USD 34 even in harvest, because every workload runs on services that bill by use and cost almost nothing while idle.

The VPN to the three centers and the private endpoints make up about 84 percent of a normal month. They are what keeps the center traffic off the internet, so the design pays for them. Section 12 shows what removing the endpoints would save and why it is not done.

The last row is the month in which every farm flies its harvest estimation at once. Inference then costs USD 45.95 instead of 16.26, and the platform reaches USD 236.76. The production budget of USD 230 warns at that point, and that warning is expected in such a month.

## 5. Links of the collection centers

Each center contracts a dedicated link of 80 to 120 Mbps. A Colombian operator publishes reference prices of 250,000 to 350,000 pesos a month for each link, which at the TRM gives USD 229 to 321 a month for the three centers. The reference is indicative and does not say whether it includes IVA, so a quote from an operator with coverage in each municipality replaces it. Shared business fiber, the fallback, costs 70,000 to 150,000 pesos a month for each center, USD 64 to 138 for the three.

These links belong to the centers and are billed by the operator, so they stay outside the cloud budgets.

## 6. Development and test environments

The development and test environments exist only while the team works on them. At 80 hours a month each they cost USD 9.24, and the keys that protect their state cost USD 3.00 a month whether they are up or not. The [environments and promotion](../architecture/environments-and-promotion.md) design describes how they come up and down.

## 7. Inference in harvest

Each inference function starts when a complete input arrives, a published flight record for the drone functions and a batch of readings for telemetry. The [inference cost](inference-cost.md) counts every billed piece of a run, the person filter, the model, the function time, the queues and, for the harvest estimation, the orthomosaic.

| Trigger in a harvest month | Invocations | Images | USD per 1,000 invocations | USD in the month |
|---|---:|---:|---:|---:|
| Focus confirmation | 60 | 3,000 | 88.72 | 5.32 |
| Verification | 25 | 500 | 35.49 | 0.89 |
| Harvest estimation | 50 | 5,000 | 197.93 | 9.90 |
| Telemetry batch | 5,760 | 0 | 0.03 | 0.16 |
| **Total** | **5,895** | **8,500** | **2.76** | **16.26** |

A single cost per 1,000 invocations hides the difference between a telemetry batch and a drone flight, so the table shows it by trigger. Per 1,000 images analyzed, the drone functions cost USD 1.89 in harvest. A normal month runs no estimation flight and costs USD 1.63. Inference runs on the United States inference profile, so crop images leave the country for AWS Regions in the United States, and an image with a person never reaches the model.

## 8. Farm hardware and monthly amount

The [farm hardware and monthly amount](farm-hardware-and-fee.md) prices each part of a node and each visit, in a low, a base and a high scenario. The figures here are the base scenario, with a quarter of the farms on LoRa sharing one gateway for every ten farms.

| Item | Fleet of 200 farms | Each farm |
|---|---:|---:|
| Hardware and installation, known part, once | 93,495.54 | 467.48 |
| Data, SIM, maintenance and gateways, monthly | 856.67 | 4.28 |
| Replacement reserve, monthly | 1,320.21 | 6.60 |
| **Field operation, monthly** | **2,176.88** | **10.88** |
| Monthly amount proposed for each farm, with its share of the fixed cloud lines | | 11.77 |

The investment is the known part. The enclosure, the controller board, the climate and grain probes, the mast, the cables, shipping, import duties and IVA still have no price, and each one raises the investment and the reserve. The monthly amount is a proposal of the team that recovers every recurring cost with no margin, while the investment is presented apart. Whether the farmer pays any of it, and how much the Federation subsidizes, is a decision of the Federation.

The known investment of a cellular farm, USD 451.29, equals about 92 kilograms of dry parchment coffee at the reference price of the Federation of 10 November 2026.

## 9. Drone service

A contracted operator runs three brigades, one for each department, each with a pilot, a support person, a spraying drone and a mapping drone. The [drone campaign cost](../drones/campaign-cost-estimation.md) prices the five services by mission hour from public Colombian labor and equipment rates.

| Period | USD | Each farm | COP at the TRM |
|---|---:|---:|---:|
| Start-up month, first year | 21,622.25 | 108.11 | 70,702,163 |
| Harvest month | 20,410.90 | 102.05 | 66,741,194 |
| Outside-harvest month, first year | 3,321.90 | 16.61 | 10,862,214 |
| Outside-harvest month, following years | 3,777.46 | 18.89 | 12,351,841 |
| First year | 144,819.47 | 724.10 | 473,542,289 |
| Following years | 111,864.52 | 559.32 | 365,783,557 |

A harvest month flies about 140 missions, 40 confirmations, 25 fumigations, 25 verifications and 50 harvest estimations. The first year adds the delimitation of all 200 farms, spread over two start-up months. The agrochemical product stays out, since its dose and area depend on an agronomic prescription, and so does inference, which section 7 already counts.

The operator rates, insurance, permits and logistics are team estimates shown in three scenarios. The low scenario gives USD 75,601 for a following year and the high scenario USD 188,830, so a quote moves this line more than any other.

## 10. Infrastructure code

The infrastructure code of the network, the security, the ingestion pattern, the inference pattern, the farm module and the pipelines took 100 hours over two weeks. It is a one-time cost.

| Profile | Hours | USD an hour | USD |
|---|---:|---:|---:|
| Senior | 34 | 32.00 | 1,088.00 |
| Junior | 66 | 18.00 | 1,188.00 |
| **Total** | **100** | | **2,276.00** |

The hourly rates are team estimates of the Colombian market. The code is reused for every new center and for every new farm through variables, so growing the pilot adds no new code.

## 11. Decisions that lower or avoid cost

Each decision is already part of the design, and its effect comes from the detailed cost documents.

| Decision | Alternative avoided | Effect, USD |
|---|---|---:|
| Drone missions only where a sensor alert or a scheduled service calls them, paid by mission hour | Weekly sweeps of every farm | About 2.04 million a year |
| Drone operator paid by mission hour | Three brigades dedicated full time | 88,872.99 a year |
| Development and test up only while the team works | Both environments on all month | 75.07 a month |
| Six custom metrics, one dashboard and saved queries | Fifteen metric series and two dashboards | 5.58 a normal month, 5.42 a harvest month |
| Push first, SMS only for urgent drying alerts | SMS for every crop alert too | 5.09 a harvest month |
| Photos and flight logs in Glacier Instant Retrieval after 90 days | Five years in S3 Standard | 13.68 a month in year five |

**Drones directed by the sensors.** A drone flies to a farm when a sensor reading opens a case, when a fumigation needs its verification, or once a harvest for the estimation. Sweeping every farm every week with the same rates would cost about USD 2.15 million a year, about 19 times the service. Paying the operator by mission hour, and letting its staff serve other clients between campaigns, avoids the cost of six people dedicated all year, since outside harvest a brigade flies about 0.4 missions a field day. The risk is an operator that asks for a retainer to keep brigades available, so the tender asks for both prices.

**Environments on demand.** Development and test come up through the pipeline for a work session and come down when it ends. Left on all month they would cost USD 84.31 instead of 9.24. The account budget warns when an environment is forgotten.

**Minimal telemetry.** The platform keeps as metrics only the six signals an alarm needs and reads the rest with saved queries, which cost almost nothing per scan. A full catalog of fifteen series and two dashboards would cost USD 10.71 in a normal month against 5.13 with the chosen set and its one operations dashboard.

**Push before SMS.** A crop alert opens a drone case that takes days to resolve, so it travels by push only. An SMS goes out only for an urgent drying alert that the phone did not confirm. Sending an SMS for each of the about 100 crop alerts of a harvest month would add USD 5.09 to that month.

**Cold storage for photos.** Drone photos and flight logs must stay five years and are rarely read after a case closes. After 90 days they move to Glacier Instant Retrieval, which still returns an object in milliseconds for a claim. By year five the archive holds about 720 GB, and the colder class saves USD 13.68 a month against S3 Standard.

## 12. Savings left on purpose

Some cheaper options exist and the design does not take them. Each one is listed with its effect, so the Federation can weigh it.

| Option | Saving, USD | Why it is not taken |
|---|---:|---|
| Remove the private endpoints and send center traffic over the internet | 43.80 a month | The center traffic would rely on TLS and multi-factor sign-in alone. The endpoints keep it on the private link |
| CloudFront flat-rate Free plan in place of the pay-as-you-go web firewall | 8.00 a month | The plan allows 1 million requests a month, and the public lookup makes about 1.6 million in a harvest month. Above the allowance AWS may serve the traffic from fewer locations, which would slow the lookup in the busiest weeks |
| Bedrock batch inference at half the token price | About 3.20 a harvest month | Batch jobs may take hours, and a focus confirmation must reach the reviewer the same day |
| Global inference profile, about 10 percent cheaper on the model | About 0.64 a harvest month | It may process crop images outside the United States, beyond the declared Region |
| Count the free tiers of CloudWatch, Lambda and Rekognition | A few dollars a month | Free tiers depend on the account and its age, so the estimate assumes none and stays a ceiling |

## 13. Exchange rate and tax

Converting the following year at other rates shows the size of the budget in pesos.

| Rate, COP per USD | Following year with the links, COP million |
|---|---:|
| TRM of the price basis, 3,269.88 | 468.1 to 471.7 |
| Lowest of the last 120 rates, 3,048.12 | 436.4 to 439.7 |
| Highest of the last 120 rates, 3,796.87 | 543.6 to 547.8 |

This conversion keeps every figure fixed in dollars. The lines priced in pesos, the center links, the drone labor and the farm visits, would also change in dollars with the rate, in the opposite direction, so the real effect on a peso budget is smaller than the table shows for those lines.

| Tax treatment | Following year with the links, USD |
|---|---:|
| Before IVA | 143,164 to 144,268 |
| IVA of 19 percent on every line | 170,366 to 171,679 |

Whether AWS, the operators and the drone contractor charge IVA to the Federation is not confirmed, and import duties on the field hardware and the drones are unknown. The second row is therefore a ceiling for IVA, with duties still outside.

## 14. Assumptions and pending confirmations

| Assumption | Who confirms | What changes if it fails |
|---|---|---|
| The TRM of the price basis and figures before IVA | Federation | Section 13 shows the range |
| A harvest lasts four months and the estimation flights spread over them | Departmental committees | A harvest of another length moves the drone and inference lines in proportion. All flights in one month raise inference to USD 45.95 in that month |
| Public sack lookups run at their peak all day in harvest | Federation | The lookup line falls, by less than one dollar |
| The operator bills by mission hour and uses its staff elsewhere between campaigns | Federation procurement and the operator | A following year rises to about USD 200,738 |
| Operator, insurance, permits and logistics at team estimates | Operator quote and legal review | The drone line moves between USD 75,601 and 188,830 a year |
| The agrochemical product stays outside the drone cost | Agronomy and the supplier | Fumigation adds treated area times dose times product price |
| The field items without a price are bought at a reasonable price | Quotes for the enclosure, controller board, probes, mast and cables | Each raises the investment and the reserve |
| A data plan with coverage and LTE-M service in the three departments | Operator quote | The data and SIM lines of the farms change |
| The dedicated links cost what the operator reference says | Operator quotes in each municipality | The links move, from USD 64 for shared fiber to 345 at the strongest peso |
| The team keeps 28 alarms and one dashboard | Platform team | Each alarm moves USD 0.10 a month and each dashboard USD 3.00 |
| Hourly rates of the infrastructure code | Team | The one-time line scales with the rate |

## 15. Sources

- [Price basis](price-basis.md), for prices, exchange rate and tax.
- [Monthly cloud cost](cloud-cost.md), for each cloud line, the environments and the links.
- [Inference cost](inference-cost.md), for the cost per trigger and per 1,000 images.
- [Farm hardware and monthly amount](farm-hardware-and-fee.md), for the investment, the field operation and the proposed amount.
- [Drone campaign cost](../drones/campaign-cost-estimation.md), for the drone service by mission, month and year.
- [Observability](../architecture/observability.md), [operational alarms](../architecture/operational-alarms.md) and [dashboards](../architecture/dashboards.md), for the monitoring cost.
- [Alert delivery](../iot/alert-delivery.md) and [persistence and archive](../architecture/persistence-and-archive.md), for the SMS and storage savings.
- AWS, [CloudFront flat-rate pricing plans](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/flat-rate-pricing-plan.html).
- The figures of the summary are reproduced with `python3 docs/governance/tools/pilot_cost.py --check`, which reads them from the documents above and fails when this document differs.
