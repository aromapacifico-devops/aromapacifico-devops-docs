# Hardware, installation and monthly cost of a farm

This document estimates what one farm needs to join the platform and what it costs each month. It separates the initial investment from the monthly cost, gives the cost with the shared expenses assigned, prices the cellular farm and the LoRa farm apart, treats the gateway as shared equipment, and shows how the figures move from 200 to 1,000 farms. It is an estimate from listed prices and stated assumptions. Nothing was bought or quoted, and no figure here is a fee that a farmer is asked to pay.

## Contents

1. Terms and status of each figure
2. What is reused
3. What each figure contains
4. Prices
5. Hardware of one farm
6. Installation in one visit
7. Connectivity, energy, replacement and maintenance
8. Shared equipment
9. Monthly cost
10. From 200 to 1,000 farms
11. Context against the price of coffee
12. Consistency with the cost document
13. Assumptions and pending confirmations
14. Criteria of the story and their evidence
15. Sources

## 1. Terms and status of each figure

| Term | Meaning in this document |
|---|---|
| Verified | A price read on a page on 2026-11-10 and quoted as listed. It does not show that the part fits the node, which the node specification requires from the supplier |
| Estimate | A figure built from a stated rule, for example a listing of a different form or a currency conversion |
| Assumption | A value set by the team with no source, replaced by a quote or a measurement |
| Quote | No price could be read. The item stays pending, and it is never counted as zero |
| Investment | What is paid once for a farm, the hardware and the installation |
| Cash cost | What is paid each month |
| Reserve | Money set aside each month to replace parts that wear. A replacement is paid from it and is not added to the monthly total again |
| Fee | What a farmer is charged. No policy of the Federation sets one, so this document computes cost and no fee |

All amounts are in US dollars before tax, with pesos at the TRM of the price basis and euros at the reference rate of the European Central Bank of 2026-11-10. IVA and import duties are outside every figure and appear only as a scenario.

## 2. What is reused

| Document | What it fixes and this estimate keeps |
|---|---|
| [Price basis](price-basis.md) | USD as the currency, the TRM of 3,269.88 with its low and high, IVA of 19 percent excluded, the cellular module board at USD 35.86, the gateway at EUR 537.76 with German VAT, the mobile data price per MB and the 5.5 MB a month for a node |
| [Cloud cost](cloud-cost.md) | The fixed lines of USD 170.10 and the variable lines for 200 farms. Only two variable lines grow with the farms, telemetry ingestion and alert delivery. Every other line belongs to carriers, centers, buyers or drones and is not assigned to a farm here |
| [Autonomous node](../iot/autonomous-node.md) | The bill of materials by class, a 12.8 V 12 Ah battery, a 20 W panel, the five steps of 100 minutes on the site, and the cellular and LoRa variants |
| [LoRa out of coverage](../network/lora-out-of-coverage.md) | The shared gateway, a LoRa farm with no data plan, and the cloud message price of USD 6 per million |

## 3. What each figure contains

| Figure | Contains | Leaves out |
|---|---|---|
| Initial investment of a farm | The priced hardware and the installation visit | Every pending item, shipping, import duties and IVA |
| Marginal monthly cash cost | Mobile data, the cloud lines that grow with the farm count, the LoRa messages of a LoRa farm and one maintenance visit a year | The fee of each SIM, which is pending |
| Monthly cost with shared expenses assigned | The marginal cost, the fixed cloud lines divided by the farms, the cash recurring costs of the gateways and the replacement reserve | The gateway cellular plan, the pending parts and their reserve, shipping and duties. The fixed lines are assigned in full to the farms although the platform also serves carriers, centers and buyers, so the result can be higher than the share of a farm. It is not a ceiling, since pending items would raise it |
| Commercial fee | Not defined | A fee needs a policy of the Federation on margin, subsidy and who bears the platform |

The costs that other documents already carry are not repeated. The cloud lines come from the cost document once, the gateway is counted once for its purchase, installation, power, connectivity and maintenance, and the replacement reserve is shown apart from the cash cost.

## 4. Prices

| Item | Value | Source and date |
|---|---|---|
| COP per USD, central, low and high | 3,269.88, 3,048.12, 3,796.87 | Price basis, 10 November 2026 |
| USD per EUR | 1.1214 | European Central Bank euro reference rate, 10 November 2026 |
| IVA | 19% | Price basis. Every figure is before tax. Import duties are unknown and are not included |

| Item | Price as read | Used in USD | Status | Source and date | Tax, shipping and limits |
|---|---|---|---|---|---|
| Battery 12.8 V 12 Ah LiFePO4 with BMS, lower listing | USD 70.99 | 70.99 | verified | Kastar listing, mykastar.com, read 2026-11-10 | Tax not stated, shipping said to be free. The page gives conflicting capacity and cycle figures and no datasheet |
| Battery 12.8 V 12 Ah LiFePO4, higher listing | USD 159.00 | 159.00 | verified | Battery Space listing, batteryspace.com, read 2026-11-10 | Tax and shipping not stated. Charge 0 to 40 C, UN38.3 passed, no BMS statement |
| Solar panel 20 W 12 V | USD 39.50 | 39.50 | verified | ACOPower listing HY020-12M, acopower.com, read 2026-11-10 | Tax and shipping not stated |
| Charge controller 10 A, MPPT | USD 60.00 | 60.00 | verified | Victron SmartSolar MPPT 75/10, Renewable Outdoors, read 2026-11-10 | Tax and shipping not stated. The lithium profile was not read on the page |
| Cellular module LTE-M and NB-IoT, mini PCIe board | USD 35.86 | 35.86 | estimate | Price basis, BG95-M3 mini PCIe at a US distributor, read 2026-11-10 | A board and not the bare module the node would use. Tax and duties not stated |
| LoRa module STM32WLE5, US915/AU915 variant | USD 5.99 | 5.99 | verified | RAK3172 SKU 306042, store.rakwireless.com, read 2026-11-10 | Shipping extra, tax not stated. The radio band is not chosen, see the LoRa path document |
| Antenna for LoRa, 2 dBi | USD 5.00 | 5.00 | verified | RAK 2 dBi antenna, store.rakwireless.com, read 2026-11-10 | Shipping extra, tax not stated. Fit to the mast not checked |
| Soil probe, 7 variables, RS485 | QAR 295.00 at 3.64 QAR per USD | 81.04 | estimate | Voltaat listing VT-1767, voltaat.com, read 2026-11-10 | The conversion rate is a peg that was not read from a primary source. No manufacturer datasheet, so range and accuracy are unverified |
| LoRaWAN gateway RAK7289 V2, without VAT | EUR 537.76 including German VAT of 19 percent | 506.76 | estimate | Price basis, EUR 537.76 at a European retailer, read 2026-11-10 | VAT removed, converted at the ECB rate of 1.1214. Shipping extra. The variant for the frequency plan is not fixed |

Items with no price read are listed as pending in the tables below and never counted as zero.

The pages that opened were read on 2026-11-10. A part with a price in this table is not selected. The listing is a reference for the order of magnitude, and a quote replaces it. Items with no readable price are pending and never zero.

## 5. Hardware of one farm

| Item | Cellular farm | LoRa farm | Status |
|---|---|---|---|
| Battery 12.8 V 12 Ah, lower listing | 70.99 | 70.99 | verified |
| Solar panel 20 W | 39.50 | 39.50 | verified |
| Charge controller 10 A | 60.00 | 60.00 | verified |
| Soil probe | 81.04 | 81.04 | estimate |
| Radio | 35.86 cellular module board | 10.99 LoRa module and antenna | cellular estimate, LoRa verified |
| **Verified listings subtotal, battery lower and higher** | 170.49 and 258.50 | 181.48 and 269.49 | verified |
| **Estimated items subtotal** | 116.90 | 81.04 | estimate |
| **Known subtotal, verified and estimated, battery lower and higher** | 287.39 and 375.40 | 262.52 and 350.53 | |
| Pending items | 9 | 7 | quote |

Pending items of a cellular farm: Enclosure IP67; Controller board; Climate sensor; Grain probe; Mast and fixings; Cable and connectors; Shipping, import duties and IVA of every item; Cellular antenna; SIM or subscription, monthly fee for each SIM (the data price per MB is known).
Pending items of a LoRa farm: Enclosure IP67; Controller board; Climate sensor; Grain probe; Mast and fixings; Cable and connectors; Shipping, import duties and IVA of every item. The gateway share is in the shared equipment tables.

The two listings of the battery differ by a factor of 2.2. One page gives conflicting capacity and cycle figures and no datasheet, and the other states a charge range of 0 to 40 C, which matters because the node specification asks for a low temperature charging limit. The estimate carries both.

## 6. Installation in one visit

| Component | Value | Origin |
|---|---|---|
| Work on the site | 100 minutes in five steps, 30 + 20 + 10 + 15 + 25 | Assumption of the node specification, not measured |
| Preparation before the visit | 30 minutes of one technician, assembly check and provisioning | Assumption |
| Technicians on the site | 1, with 2 as a scenario | Assumption, the specification names one installer |
| Travel, round trip | 1 h, 2 h, 4 h, base 2 h, paid at the technician rate | Assumption, no farm location is known |
| Technician rate, COP per hour | low 15,000, mid 25,000, high 40,000, base mid | Assumption. No source for a technician rate was found, and the legal minimum wage is not a technician rate |
| Vehicle, COP per hour of travel | 25,000 | Assumption |

| Rate | Travel | Installation labor, USD | Vehicle, USD | Installation total, USD | With 2 technicians, USD |
|---|---|---|---|---|---|
| low | 1 h | 14.53 | 7.65 | 22.17 | 34.40 |
| low | 2 h | 19.11 | 15.29 | 34.40 | 51.23 |
| low | 4 h | 28.29 | 30.58 | 58.87 | 84.87 |
| mid | 1 h | 24.21 | 7.65 | 31.86 | 52.24 |
| mid | 2 h | 31.86 | 15.29 | 47.15 | 75.18 |
| mid | 4 h | 47.15 | 30.58 | 77.73 | 121.05 |
| high | 1 h | 38.74 | 7.65 | 46.38 | 79.00 |
| high | 2 h | 50.97 | 15.29 | 66.26 | 111.12 |
| high | 4 h | 75.44 | 30.58 | 106.02 | 175.34 |

Base case, mid rate and 2 hours of travel, one technician, USD 47.15. Later maintenance visits are not part of it, see the monthly tables.

Conditions for a single visit. The installation fits one visit only when all of these hold, and a failed condition adds a visit that this document prices as a maintenance visit.

| Condition | Source |
|---|---|
| The node arrives assembled and provisioned, with its identity registered | Node specification, the preparation is priced here |
| The farm is already enrolled with its owner before the visit | Assumptions register, enrollment by field staff |
| The signal, and the port that the operator allows, are known to work at the site, or a gateway of the vereda is already in range for a LoRa farm | Node specification, step 4 of the installation. The operator confirmation is pending |
| The farmer or the person in charge is present for the last step | Node specification, step 5 |
| The mast, the panel and the probe cable lengths suit the site | Node specification, probe interface limits |
| The installer carries the node, the mast, the panel, the probes, a way to read the signal and the fixings | Node specification |

The 100 minutes are an estimate of the sensors design and are not measured. Later maintenance visits are priced apart in section 7.

## 7. Connectivity, energy, replacement and maintenance

| Item | Treatment |
|---|---|
| Mobile data | 5.5 MB a month at EUR 0.0025 per MB, from the price basis. The fee of each SIM is not published and is pending, and it may exceed the data cost many times, so the cellular monthly figures are lower than the real cost by that fee |
| LoRa farm | No data plan. It pays its cloud messages and a share of the gateway |
| Energy | Each node has a battery and a 20 W panel with no recurring cost. The gateway has a solar kit that is pending, with no recurring line |
| Maintenance | One visit a year of 60 minutes on the site, as an assumption that the sensors design may replace. It is a cash cost and is separate from the installation |
| Replacement | A reserve for each priced part, its price divided by its life in months. A part with no price has no reserve yet. The lives are assumptions, and the pages read give conflicting cycle figures for the battery |

## 8. Shared equipment

| Item for each gateway | Value, USD | Origin | Counted |
|---|---|---|---|
| Gateway RAK7289 V2 without VAT | 506.76 | estimate from the price basis, EUR 537.76 with VAT | once, in the investment |
| Installation, 4 hours with 2 technicians, base travel and vehicle | 107.04 | assumption | once, in the investment |
| Mast, solar kit, antenna and cables, shipping, duties | pending | quote | pending |
| Energy | solar kit, no recurring cost | the kit is pending | no recurring line |
| Backhaul cellular plan | pending, monthly | quote | pending, monthly |
| Maintenance visit, 1 a year, 2 hours with 2 technicians | 6.37 a month | assumption | monthly cash |
| Replacement reserve of the gateway, 7 years | 6.03 a month | assumption | monthly reserve |

The number of farms for each gateway is an economic assumption and says nothing about radio coverage. Gateways needed are rounded up, and each gateway is counted once.

| Farms for each gateway | Investment known for each LoRa farm from the gateway, USD | Monthly cash for each LoRa farm, USD | Monthly reserve for each LoRa farm, USD |
|---|---|---|---|
| 5 | 122.76 | 1.27 | 1.21 |
| 10 | 61.38 | 0.64 | 0.60 |
| 20 | 30.69 | 0.32 | 0.30 |

These shares assume full gateways. A gateway with fewer farms costs each of them more, which the fleet table shows with the rounding.

A LoRaWAN gateway serves the farms of a vereda. The number of farms for each gateway of 5, 10 and 20 is an economic assumption that gives a cost for each farm. It says nothing about radio coverage, which needs the site study of each vereda. The gateways needed are the farms on LoRa divided by that number and rounded up, so a vereda with few farms carries a whole gateway.

## 9. Monthly cost

Cash cost and the replacement reserve are kept apart. A replacement bought later is paid from the reserve and is not added to the monthly total a second time.

| Line | Cellular farm | LoRa farm, own part | Kind | Included |
|---|---|---|---|---|
| Mobile data, 5.5 MB at EUR 0.0025 per MB | 0.02 | 0.00 | cash | yes |
| Fee for each SIM | pending | none | cash | no, pending a quote |
| Cloud lines driven by the farm count, normal and harvest | 0.01 and 0.06 | 0.01 and 0.06 | cash | yes |
| LoRaWAN messages of the cloud, possible overlap with the line above | 0.00 | 0.01 | cash | yes, shown apart |
| Maintenance visit, 1 a year, 60 minutes on the site | 3.19 | 3.19 | cash | yes |
| **Marginal cash cost, normal and harvest** | 3.21 and 3.26 | 3.21 and 3.25 | cash | without the pending SIM fee |
| Replacement reserve of the priced parts, battery lower and higher | 4.76 and 6.23 | 4.50 and 5.97 | reserve | priced parts only, pending parts have no reserve yet |
| **Marginal economic cost, cash plus reserve, normal month, battery lower** | 7.98 | 7.71 | | |

Lives used for the reserve, in years, are assumptions: battery 5, panel 10, controller 8, soil probe 3, cell module 8, lora module 8, lora antenna 8, gateway 7. The pages read give conflicting cycle figures for the battery and no datasheet.

The monthly cost with the shared expenses assigned for a whole fleet, with the fixed cloud lines, the gateways and the reserve, is in section 10.

## 10. From 200 to 1,000 farms

### Fleet by number of farms and share of LoRa farms

Investment is the known subtotal with the battery at the lower listing, with installation, and without the pending items. Monthly cash adds the shared cloud lines and the gateways. The shared cloud lines are the fixed lines of the cost document divided by the farms, which includes what the platform also does for carriers, centers and buyers.

| Farms | LoRa share | Gateways for 5, 10, 20 farms | Investment known, 10 farms for each gateway | Monthly cash, 10 farms for each gateway | Monthly reserve, 10 farms for each gateway | Monthly cash and reserve for each farm | Fixed cloud lines for each farm |
|---|---|---|---|---|---|---|---|
| 200 | 0% | 0, 0, 0 | 66,907.50 | 813.06 | 952.40 | 8.83 | 0.85 |
| 200 | 25% | 10, 5, 3 | 68,732.99 | 844.58 | 969.61 | 9.07 | 0.85 |
| 200 | 50% | 20, 10, 5 | 70,558.48 | 876.10 | 986.82 | 9.31 | 0.85 |
| 400 | 0% | 0, 0, 0 | 133,815.00 | 1,456.02 | 1,904.79 | 8.40 | 0.43 |
| 400 | 25% | 20, 10, 5 | 137,465.98 | 1,519.06 | 1,939.22 | 8.65 | 0.43 |
| 400 | 50% | 40, 20, 10 | 141,116.95 | 1,582.09 | 1,973.64 | 8.89 | 0.43 |
| 600 | 0% | 0, 0, 0 | 200,722.50 | 2,098.99 | 2,857.19 | 8.26 | 0.28 |
| 600 | 25% | 30, 15, 8 | 206,198.96 | 2,193.54 | 2,908.83 | 8.50 | 0.28 |
| 600 | 50% | 60, 30, 15 | 211,675.43 | 2,288.09 | 2,960.46 | 8.75 | 0.28 |
| 800 | 0% | 0, 0, 0 | 267,630.00 | 2,741.95 | 3,809.59 | 8.19 | 0.21 |
| 800 | 25% | 40, 20, 10 | 274,931.95 | 2,868.02 | 3,878.43 | 8.43 | 0.21 |
| 800 | 50% | 80, 40, 20 | 282,233.90 | 2,994.09 | 3,947.28 | 8.68 | 0.21 |
| 1000 | 0% | 0, 0, 0 | 334,537.50 | 3,384.91 | 4,761.99 | 8.15 | 0.17 |
| 1000 | 25% | 50, 25, 13 | 343,664.94 | 3,542.50 | 4,848.04 | 8.39 | 0.17 |
| 1000 | 50% | 100, 50, 25 | 352,792.38 | 3,700.09 | 4,934.10 | 8.63 | 0.17 |

The monthly figures hold the SIM fee, the gateway plan and the pending items out, so they are lower than the real cost by those amounts.

### Gateways for each assumption of farms in range

| Farms | LoRa share | Farms for each gateway | Gateways, rounded up | Investment known | Monthly cash | Monthly reserve | Cash and reserve for each farm |
|---|---|---|---|---|---|---|---|
| 200 | 25% | 5 | 10 | 71,801.98 | 876.44 | 999.77 | 9.38 |
| 200 | 25% | 10 | 5 | 68,732.99 | 844.58 | 969.61 | 9.07 |
| 200 | 25% | 20 | 3 | 67,505.39 | 831.84 | 957.54 | 8.95 |
| 200 | 50% | 5 | 20 | 76,696.45 | 939.81 | 1,047.15 | 9.93 |
| 200 | 50% | 10 | 10 | 70,558.48 | 876.10 | 986.82 | 9.31 |
| 200 | 50% | 20 | 5 | 67,489.49 | 844.24 | 956.66 | 9.00 |
| 1000 | 25% | 5 | 50 | 359,009.88 | 3,701.78 | 4,998.86 | 8.70 |
| 1000 | 25% | 10 | 25 | 343,664.94 | 3,542.50 | 4,848.04 | 8.39 |
| 1000 | 25% | 20 | 13 | 336,299.37 | 3,466.04 | 4,775.65 | 8.24 |
| 1000 | 50% | 5 | 100 | 383,482.26 | 4,018.65 | 5,235.74 | 9.25 |
| 1000 | 50% | 10 | 50 | 352,792.38 | 3,700.09 | 4,934.10 | 8.63 |
| 1000 | 50% | 20 | 25 | 337,447.44 | 3,540.80 | 4,783.28 | 8.32 |

### Cost for each farm by number of farms

| Farms | Marginal cash cost for each farm | Shared cloud lines for each farm | Reserve of the parts and gateway share for each farm | Cash and reserve for each farm |
|---|---|---|---|---|
| 200 | 3.21 | 0.85 | 5.01 | 9.07 |
| 400 | 3.21 | 0.43 | 5.01 | 8.65 |
| 600 | 3.21 | 0.28 | 5.01 | 8.50 |
| 800 | 3.21 | 0.21 | 5.01 | 8.43 |
| 1000 | 3.21 | 0.17 | 5.01 | 8.39 |

At 200 farms the fixed cloud lines add USD 0.85 for each farm and at 1,000 farms USD 0.17. The cost for each farm falls with the number of farms because the fixed cloud lines spread, and it rises with the share of LoRa farms in this estimate because each gateway is a whole unit. The cloud lines that grow with the farms are linear in the table, since the cloud addressing design holds from 200 to 1,000 farms with no change.

## 11. Context against the price of coffee

The investment of a cellular farm, known subtotal with installation and the battery at the lower listing, in kilograms of dry parchment coffee at the reference price of the Federation of 10 November 2026, COP 2,000,000 for a load of 125 kg, so COP 16,000 a kilogram.

| Case | Investment known, USD | COP at the central TRM | Kilograms of dry parchment coffee | Same at the low and high TRM |
|---|---|---|---|---|
| Cellular farm | 334.54 | 1,093,897 | 68.4 | 63.7 to 79.4 |
| LoRa farm without the gateway share | 309.67 | 1,012,576 | 63.3 | 59.0 to 73.5 |

The comparison shows no profitability and no capacity to pay. The pending items would raise both figures.

The reference price is the internal reference price for dry parchment coffee that the Federation shows on its site, read on 2026-11-10. It varies with the distance to the purchase point. The comparison is context. It shows no profitability and no capacity to pay, and the Federation decides whether an investment of this order is moderate.

### IVA

If IVA of 19% applies in full to the known subtotal, a cellular farm with installation goes from 334.54 to 398.10. Import duties are unknown and are not in either figure.

## 12. Consistency with the cost document

The cloud lines of this estimate come from the cost document of this repository and are checked against it by the script, which fails if a value changes.

The cost document gives USD 177.05 for a normal month and USD 200.41 for a harvest month for the production platform, after its later correction. The project status file of the handbook gives USD 177.23 and USD 201.11 for the same total. The two sources differ by 0.18 and 0.70, and this estimate reads the cost document. The status file is not edited here, and its owner decides which value stands.

## 13. Assumptions and pending confirmations

| Item | Origin | Who confirms | Effect if it fails |
|---|---|---|---|
| Farms for each gateway, 5, 10 and 20 | Assumption | Site study of each vereda | The gateway share of a LoRa farm moves in inverse proportion |
| Share of LoRa farms, 0, 25 and 50 percent | Assumption, no farm list exists | Federation | The blended investment and cost move between the two variants |
| Technician rate, COP 15,000 to 40,000 an hour | Assumption | Quote from a technician or a contractor | Installation, visits and gateway work move in proportion |
| Technicians on the site, 1 with 2 as a scenario | Assumption | First installations | Installation labor rises with the number |
| Travel of 1, 2 and 4 hours for the round trip | Assumption | Farm and vereda locations | Installation and visits move in proportion |
| One maintenance visit a year | Assumption | Sensors design | The monthly share moves in proportion |
| Lives of the parts in years | Assumption | Datasheets | The reserve moves in inverse proportion |
| Fee of each SIM and the gateway cellular plan | Pending | Operator quote | Cellular and gateway monthly cost rise by those amounts |
| Pending hardware, shipping, import duties and IVA | Pending | Quotes and customs agent | Investment and the reserve rise |
| The fixed cloud lines are assigned in full to the farms | Assumption | Federation | The loaded cost falls if part is assigned to carriers, centers and buyers |
| The LoRa message cost does not overlap the telemetry line of the cost document | Assumption | Owner of the cost document | At most USD 0.01 a month for each LoRa farm |
| A commercial fee policy | Pending | Federation | No fee can be stated until it exists |

## 14. Criteria of the story and their evidence

| Literal criterion | Where it is answered | Gaps | Assumptions accepted |
|---|---|---|---|
| Hardware, installation in one visit and monthly cost for each farm | Sections 4 to 9 and the script. The hardware has a known subtotal and a list of pending items, the installation is priced with its conditions, and the monthly cost is given as cash, reserve and with shared expenses assigned | The pending parts and the SIM fee are quotes, so the totals are known subtotals and not complete costs. There is no fee because no policy exists | Section 13 |
| Sensitivity from 200 to 1,000 farms | Section 10 and the script | None | Section 13 |

## 15. Sources

| Source | Used for |
|---|---|
| Price basis, cloud cost, autonomous node and LoRa path documents of this repository | Rates, cloud lines, the bill of materials, times and the shared gateway |
| Listings read on 2026-11-10 of the battery (mykastar.com, batteryspace.com), the panel (acopower.com), the controller (renewableoutdoors.com), the LoRa module and antenna (store.rakwireless.com), a soil probe (voltaat.com) and a cellular board at a distributor (digikey.com) | The price register |
| European Central Bank, euro foreign exchange reference rates, 2026-11-10 | The euro to dollar conversion |
| Federación Nacional de Cafeteros de Colombia, internal reference price of dry parchment coffee, federaciondecafeteros.org, 2026-11-10 | The context of section 11 |
