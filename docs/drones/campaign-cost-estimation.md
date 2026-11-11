# Drone campaign cost

This document gives the cost of the drone service of the pilot, by mission, by campaign of one department, by month and by year. It covers the five services, the certified operator, the brigade, the equipment, the travel and the storage of the flight evidence. Labor and equipment rates come from public Colombian and supplier references, the other operating rates are team estimates shown in three scenarios, and cloud prices come from the AWS Price List API. Every figure is in USD before tax and is reproduced by [`tools/campaign_cost.py`](tools/campaign_cost.py), which takes its flight counts from [`tools/flight_frequency.py`](tools/flight_frequency.py).

## Contents

1. Terms
2. Scope
3. Cadence and volumes
4. Rates and their sources
5. Cost model
6. Cost per mission
7. Cost per campaign of one department
8. Monthly and yearly cost
9. Scenarios and sensitivity
10. Previous figures
11. Risks
12. Assumptions and pending confirmations
13. Sources

## 1. Terms

| Term | Meaning |
|---|---|
| Brigade | One pilot and one support person with one spraying drone and one mapping drone, one per department |
| Campaign | The scheduled round of a brigade over the farms of its department, once a month in harvest and once every three months outside harvest |
| Alert mission | A confirmation, fumigation or verification flight raised by a sensor alert, flown on the next field day without waiting for a campaign |
| Campaign period | One department in one month, adding the scheduled round and the alert missions flown in that month |
| Start-up round | The first delimitation of all 200 farms, spread over two months of the first year |
| Variable cost | Cost of one completed mission, including the expected share of a repeated visit |
| Loaded cost | Variable cost plus an even share of the fixed lines, campaign mobilization and cloud cost over all missions of the year |

## 2. Scope

The totals include the operator management fee, pilot and support hours, equipment wear, maintenance, insurance and permits, non-chemical consumables, vehicle and fuel, per diem, equipment transport, campaign mobilization, repeated visits, and the storage, requests and processing of the drone images in S3 and Lambda.

The totals leave out four items, each for a stated reason.

| Item left out | Reason | Where it is counted |
|---|---|---|
| Inference and the person filter on images | It has its own cost per 1,000 invocations | The inference cost document, at about USD 1.75 per 1,000 images |
| Agrochemical product, water and disposal | Product, dose and treated area depend on an agronomic prescription | Pending, as treated area times dose times price |
| VAT, import duties, financing and discounts | Which lines bear VAT is unconfirmed | Section 9 shows a 19 percent ceiling |
| Federation supervisors, VPN, endpoints and keys | Supervisors are existing staff, and the network lines are in the platform cost | [Cloud cost](../governance/cloud-cost.md) |

## 3. Cadence and volumes

The service runs three brigades, one per department. A harvest of four months has one campaign a month per department, and the eight months outside harvest have one every three months, so each department has six campaigns a year and the pilot 18. Alert missions outside harvest run at a quarter of the harvest rate, and one farm in ten is delimited again each year after the first.

| Service | Trigger | Harvest month | Outside-harvest month, following years | First year | Following years |
|---|---|---:|---:|---:|---:|
| Delimit the lot | Scheduled | 0 | 2.5 | 200 | 20 |
| Confirm the alert | Sensor alert | 40 | 10 | 240 | 240 |
| Fumigate | Confirmed focus and human authorization | 25 | 6 | 148 | 148 |
| Verify | Closed fumigation | 25 | 6 | 148 | 148 |
| Estimate the harvest | Scheduled | 50 | 0 | 200 | 200 |
| **Total** | | **140** | **24.5** | **936** | **756** |

The frequency script prints 24 for the outside-harvest month because it rounds 2.5 delimitations down to 2, while its yearly count keeps the 20 delimitations. Mission hours are 3 for a delimitation, 1 for a confirmation, 1.5 for a fumigation, 1 for a verification and 3.5 for a harvest estimation, which gives 1,910 hours in the first year and 1,370 hours in the following years, about 457 hours per brigade.

A harvest estimation takes 100 images and each precision mission about 44, so a harvest month has `50 × 100 + 90 × 44.44 = 9,000` images. The first year adds 20,000 images of the start-up round and the following years 2,000 of the new delimitations.

| Period | Images |
|---|---:|
| Harvest month | 9,000 |
| Start-up month | about 10,978 |
| First year | 63,822 |
| Following year | 45,822 |

## 4. Rates and their sources

Exchange rate is COP 3,269.88 per USD and taxes are excluded, following the [price basis](../governance/price-basis.md).

### 4.1 Labor

Labor is paid by mission hour, which assumes a contracted operator that bills the hours it flies for the Federation and uses its staff for other clients in the remaining time. Section 9 shows the cost when the brigades are dedicated full time.

| Input | Value | Source |
|---|---:|---|
| Pilot salary | COP 4,800,000 a month | Public job offer for a drone pilot in Bogotá |
| Support salary | Minimum wage COP 1,750,905 plus transport aid COP 249,095 | Decrees 1469 and 1470 of 2025 |
| Employer load on salary | 52 percent | Social security, benefits and payroll levies in Colombia |
| Hours a month | 182, a 42-hour week | Law 2101 of 2021, in force from July 2026 |
| Pilot hour | USD 12.26 | `4,800,000 × 1.52 / 182 / 3,269.88` |
| Support hour | USD 4.89 | `(1,750,905 × 1.52 + 249,095) / 182 / 3,269.88` |

The pilot offer is not specific to agriculture, and few operators hold the spraying certificate yet, so the high scenario raises labor by half.

### 4.2 Equipment

Each brigade carries one spraying drone of 40 kg payload in its ready-to-fly kit with batteries and charger, listed at USD 24,519, and one multispectral mapping drone, listed at USD 5,919. The equipment rate spreads that kit of USD 30,438 in a straight line over its life and the 457 mission hours a brigade flies a year.

| Scenario | Life | Equipment per mission hour |
|---|---:|---:|
| Low | 4 years | USD 16.66 |
| Base | 3 years | USD 22.22 |
| High | 2 years | USD 33.33 |

These are list prices of foreign dealers before import duties and VAT. A Colombian dealer quote replaces them.

### 4.3 Team estimates

| Input | Low | Base | High | Note |
|---|---:|---:|---:|---|
| Operator management, three brigades, per year | 6,000 | 9,000 | 13,500 | Contract and compliance management |
| Insurance and permits, per year | 3,000 | 4,500 | 7,000 | Third-party liability policy and operation permits |
| Maintenance per mission | 8 | 15 | 25 | Batteries, propellers and nozzles, on top of the equipment rate |
| Distance per mission, km | 30 | 45 | 70 | Round trip from the municipal seat |
| Vehicle per km | 0.18 | 0.25 | 0.35 | Gasoline at COP 15,886 a gallon is about USD 0.16 a km at 30 km a gallon, and the rest covers vehicle wear |
| Per diem per person and day | 15 | 25 | 40 | Two people, prorated by mission hours over 8 |
| Equipment transport per mission | 5 | 10 | 18 | On top of the vehicle cost |
| Campaign mobilization per department | 35 | 60 | 100 | Planning, loading and unloading of each round |
| Repeated visit | 5% × 35 | 10% × 60 | 20% × 110 | Weather, battery or a person in the area |
| Non-chemical consumables per mission | 1 to 5 | 2 to 8 | 3 to 12 | By service |

The Colombian aviation rules require a liability policy for commercial drone operation, and its amount and premium need a quote.

### 4.4 Cloud

| Item | Price, USD | Use |
|---|---:|---|
| S3 Standard | 0.023 per GB-month | First three months of each image |
| S3 Glacier Instant Retrieval | 0.004 per GB-month | Months 4 to 60, then deletion |
| S3 PUT, GET and lifecycle transition | 0.005, 0.0004 and 0.02 per 1,000 | One PUT and one GET per image, one transition |
| Data transfer into S3 | 0 | Egress depends on how often images are downloaded |
| Lambda | 0.0000166667 per GB-second, 0.20 per million requests | One second at 512 MB per image, and five minutes at 4 GB per orthomosaic |
| Image size | 3 MB | Retention design of the platform |

## 5. Cost model

For a service `s` in a scenario, the variable cost of one mission is the sum of operation and logistics.

```text
operation_s = hours_s × (pilot_hour + support_hour + equipment_hour)
              + maintenance + consumables_s

logistics_s = distance_km × vehicle_km
              + per_diem × 2 × hours_s / 8
              + equipment_transport
              + repeat_share × repeat_cost

annual = operator_management + insurance_permits
         + Σ missions_s × (operation_s + logistics_s)
         + campaigns × mobilization
         + storage + requests + processing
```

Storage is computed month by month for each cohort of images, as `images × 3 / 1024` GB at the Standard price for three months and at the Glacier Instant Retrieval price until month 60. Fuel sits inside the vehicle rate and is not added again. The loaded cost per mission spreads the fixed, mobilization and cloud lines over all missions of the year, so it serves as an internal unit price and is never added back to the yearly total.

## 6. Cost per mission

Base scenario, USD before tax.

| Service | Operation | Logistics | Variable | Loaded, following year |
|---|---:|---:|---:|---:|
| Delimit the lot | 136.10 | 46.00 | 182.10 | 201.43 |
| Confirm the alert | 56.37 | 33.50 | 89.87 | 109.19 |
| Fumigate | 82.05 | 36.62 | 118.68 | 138.00 |
| Verify | 56.37 | 33.50 | 89.87 | 109.19 |
| Estimate the harvest | 156.79 | 49.12 | 205.91 | 225.23 |

A fumigation excludes the product. A focus covers up to 0.79 ha, and a commercial spraying service in Colombia charges COP 60,000 to 70,000 a hectare on large areas, mapping included, which puts the flight over one focus near USD 16. The rest of the fumigation cost is the trip and the setup that a single focus cannot share with other hectares.

## 7. Cost per campaign of one department

A campaign period adds the scheduled round of one department and the alert missions it flies in that month. No single period carries all five services, since delimitation happens at start-up and on one farm in ten a year, harvest estimation only in harvest, and the three alert services only after an alert. Flying the five in every round would add flights the farms do not need. The table shows each service in each kind of period, with zero where the service does not fly, and the year of one department, where all five appear.

Base scenario, USD before tax, missions and cost.

| Service | Start-up month, first year | Harvest month | Outside-harvest month, following years | Year of one department, following years |
|---|---:|---:|---:|---:|
| Delimit the lot | 33.33 missions, 6,070.12 | 0 | 0.83 missions, 151.75 | 6.67 missions, 1,214.02 |
| Confirm the alert | 3.33 missions, 299.56 | 13.33 missions, 1,198.24 | 3.33 missions, 299.56 | 80 missions, 7,189.43 |
| Fumigate | 2 missions, 237.35 | 8.33 missions, 988.97 | 2 missions, 237.35 | 49.33 missions, 5,854.72 |
| Verify | 2 missions, 179.74 | 8.33 missions, 748.90 | 2 missions, 179.74 | 49.33 missions, 4,433.48 |
| Estimate the harvest | 0 | 16.67 missions, 3,431.87 | 0 | 66.67 missions, 13,727.50 |
| Mobilization, fixed lines and cloud | 420.65 | 435.75 | 390.75 | 4,869.02 |
| **Total** | **7,207.42** | **6,803.74** | **1,259.15** | **37,288.17** |

The outside-harvest month is the average of the eight months, with a campaign in a quarter of them. In the first year a department costs USD 48,273.16, because its 66.67 start-up delimitations add USD 12,140.24.

## 8. Monthly and yearly cost

Base scenario, whole pilot, USD before tax.

| Period | Missions | Cost | Per farm |
|---|---:|---:|---:|
| Start-up month | 122 | 21,622.25 | 108.11 |
| Harvest month | 140 | 20,410.90 | 102.05 |
| Outside-harvest month, first year | 22 | 3,321.90 | 16.61 |
| Outside-harvest month, following years | 24.5 | 3,777.46 | 18.89 |

The first year is `2 × 21,622.25 + 4 × 20,410.90 + 6 × 3,321.90 = 144,819.47`.

| Line | First year | Following years |
|---|---:|---:|
| Delimit the lot | 36,420.71 | 3,642.07 |
| Confirm the alert | 21,568.28 | 21,568.28 |
| Fumigate | 17,564.16 | 17,564.16 |
| Verify | 13,300.44 | 13,300.44 |
| Estimate the harvest | 41,182.49 | 41,182.49 |
| Operator management, insurance and permits | 13,500.00 | 13,500.00 |
| Campaign mobilization, 21 and 18 campaigns | 1,260.00 | 1,080.00 |
| Cloud storage, requests and processing | 23.39 | 27.07 |
| **Total** | **144,819.47** | **111,864.52** |
| Per department | 48,273.16 | 37,288.17 |
| Per farm | 724.10 | 559.32 |
| In COP | 473.5 million | 365.8 million |

The cloud line grows each year as images accumulate in Glacier Instant Retrieval, from USD 23.39 in the first year to 27.07, 33.57, 40.02 and 46.46 in the fifth. Inference adds `images × inference rate` beside these totals.

## 9. Scenarios and sensitivity

The three scenarios keep the same cadence and change rates, distance and the share of repeated visits.

| Scenario | First year | Following years | Per farm, first year | Per farm, following years |
|---|---:|---:|---:|---:|
| Low | 98,980.59 | 75,601.04 | 494.90 | 378.01 |
| Base | 144,819.47 | 111,864.52 | 724.10 | 559.32 |
| High | 243,424.26 | 188,829.99 | 1,217.12 | 944.15 |

| Change, base scenario, following years | Total | Effect |
|---|---:|---:|
| Missions × 0.75 | 87,550.16 | −24,314.36 |
| Missions × 1.25 | 136,178.88 | +24,314.36 |
| Missions × 1.50 | 160,493.24 | +48,628.72 |
| Brigades dedicated full time to the Federation | 200,737.51 | +88,872.99 |
| VAT of 19 percent on every line, as a ceiling | 133,118.78 | +21,254.26 |

Dedicated brigades pay six people for twelve months, about USD 112,000 a year, against USD 23,496 of flown hours. Missions are few outside harvest, about 0.4 per brigade and field day, so a contract per mission hour costs less as long as the operator can serve other clients between campaigns. Twice the distance adds `missions × distance × vehicle rate`, more foci raise confirmations first, and fumigations follow the share of foci that become an order. A second harvest a year adds 200 estimations and their campaigns.

## 10. Previous figures

An earlier estimate of the shared service gave about USD 5,640 a year and USD 1,980 in a harvest month, USD 9.90 per farm. Spread over the 140 missions of a harvest month, that figure leaves about USD 14 per mission for the pilot, the support person, the vehicle, the drone, the permits and the cloud, which no component of this model supports. The model of this document replaces those figures. Weekly area sweeps of all 200 farms, the alternative the shared service avoids, cost about USD 2.15 million a year with the same rates, about 19 times the sensor-directed service.

## 11. Risks

| Risk | Effect | Control |
|---|---|---|
| The operator asks for a retainer to keep brigades available | Labor approaches the dedicated case of section 9 | Ask for both prices in the tender, per mission hour and per month |
| Permits are granted per flight | More time and cost per mission | Legal review of the permit period before contracting |
| Rural distances exceed the base | Fuel, per diem and days rise | Quote by department with real routes |
| Brigades fly fewer than 2.3 missions a field day in harvest | More days, per diem and delay | Measure the route during the start-up round |
| Repeated visits above 10 percent | Logistics rise | Record the cause and rate of each repeated visit |
| Unknown product and dose | Fumigation is understated | Keep the product out of the totals until a prescription and quote exist |
| Frequent downloads from Glacier Instant Retrieval | Retrieval and egress cost appear | Measure reviews and add the retrieval cost |
| Import duties and VAT on the drones | Equipment rises by 19 percent or more | Tax and customs review per line |

## 12. Assumptions and pending confirmations

| Assumption | Who confirms | What changes if it fails |
|---|---|---|
| The operator bills by mission hour and uses its staff elsewhere between campaigns | Federation procurement and operator | Following-year total rises to about USD 201,000 in the base scenario |
| Pilot cost follows a public offer of COP 4.8 million a month with a 52 percent employer load | Operator quote | Labor lines scale with the quoted rate |
| One spraying drone and one mapping drone per brigade, used for three years | Operator and dealer | Equipment rate scales with price and inversely with life |
| Mission hours of 3, 1, 1.5, 1 and 3.5 by service | First campaign | Labor, equipment and per diem scale with hours |
| Management, insurance, permits, vehicle, per diem and mobilization at team estimates | Operator quote and legal review | Fixed and logistics lines change |
| Agrochemical product stays out of the totals | Agronomy and supplier | Fumigation adds treated area × dose × product price |
| Harvest lasts four months | Departmental committees | Estimations and campaigns change |
| Images of 3 MB, 100 per estimation and about 44 per precision mission | First campaign | Cloud line scales, still below USD 50 a year |

## 13. Sources

- AWS Price List API, [Amazon S3](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonS3/current/us-east-1/index.json) and [AWS Lambda](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AWSLambda/current/us-east-1/index.json), `us-east-1`.
- Superintendencia Financiera, [representative exchange rate](https://www.datos.gov.co/Econom-a-y-Finanzas/Tasa-de-Cambio-Representativa-del-Mercado-TRM/32sa-8pi3).
- Minimum wage and transport aid of 2026, [Decrees 1469 and 1470 of 2025](https://consultorsalud.com/aumento-del-salario-minimo-en-colombia-2026/).
- Employer load on payroll, [hacecuentas, cost of hiring in Colombia](https://hacecuentas.com/co/trabajo/costo-de-contratar).
- Drone pilot job offer, [cazvid, Bogotá](https://cazvid.com/empleo/piloto-de-drone-en-bogota-colombia).
- Spraying drone list price and ready-to-fly kit, [AgTecher, DJI Agras T50](https://agtecher.com/product/dji-agras-t50).
- Mapping drone list price, [Advexure, DJI Mavic 3 Multispectral](https://advexure.com/products/dji-mavic-3-multispectral).
- Commercial spraying price per hectare, [Contexto Ganadero, Agrodron](https://www.contextoganadero.com/regiones/agrodron-integra-mapeo-y-aspersion-con-drones-en-un-solo-servicio).
- Fuel price, [Ministry of Mines and Energy, November prices](https://minenergia.gov.co/es/sala-de-prensa/noticias-index/en-noviembre-el-gobierno-nacional-mantiene-estables-los-precios-de-la-gasolina-y-el-acpm/).
- Aerocivil, [drones and urban air mobility](https://www.aerocivil.gov.co/preguntas-frecuentes/18/drones-y-movilidad-urbana-aerea/), for the specific category, operator certificate and authorization.
