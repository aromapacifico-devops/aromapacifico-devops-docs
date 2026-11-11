# Hardware, installation and monthly cost of a farm

This document estimates what one farm needs to join the platform and what it costs each month. It separates the initial investment from the recurring cost, gives low, base and high scenarios, prices the cellular farm and the LoRa farm apart, treats the gateway as shared equipment, shows how the figures move from 200 to 1,000 farms, and records the provisional option chosen for the monthly amount. It is an estimate from listed prices and stated assumptions. Nothing was bought, quoted or ordered, no supplier was contacted, and no figure here is a fee that a farmer is asked to pay.

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
11. The monthly charge
12. Context against the price of coffee
13. Consistency with the cost document
14. Assumptions and pending confirmations
15. Criteria of the story and their evidence
16. Sources

## 1. Terms and status of each figure

| Term | Meaning in this document |
|---|---|
| Verified | A price read on a page on 2026-11-10 and quoted as listed. It does not show that the part meets the node requirements |
| Estimate | A figure built from a stated rule, such as a listing of a different form, a conversion, or a published tariff times an assumed volume |
| Assumption | A value set by the team with no source, replaced by a quote or a measurement |
| Pending | No equivalent price was found. The item is out of every total, which then reads as a known subtotal plus the unknown cost of that item. A pending item is never counted as zero |
| Investment | What is paid once for a farm, the hardware, the first connection and the installation |
| Cash cost | What is paid each month |
| Reserve | Money set aside each month to replace parts that wear. A replacement is paid from it and is not added to the monthly total again |
| Fee | What a farmer is charged. No policy of the Federation sets one, so this document computes cost and no fee |
| Low, base, high | Three sets of the assumptions of this document. They do not move the pending items |

All amounts are in US dollars before tax, with pesos at the TRM of the price basis and euros at the reference rate of the European Central Bank of 2026-11-10. IVA, import duties and shipping are outside every figure.

## 2. What is reused

| Document | What it fixes and this estimate keeps |
|---|---|
| [Price basis](price-basis.md) | USD, the TRM of 3,269.88 with its low and high, IVA of 19 percent excluded, the cellular module board at USD 35.86, a prepaid plan of a global provider and the 5.5 MB a month for a node |
| [Cloud cost](cloud-cost.md) | The fixed lines of USD 170.10 and the variable lines for 200 farms. Only two variable lines grow with the farms, telemetry ingestion and alert delivery. Every other line belongs to carriers, centers, buyers or drones and is not assigned to a farm here |
| [Autonomous node](../iot/autonomous-node.md) | The bill of materials by class, a 12.8 V 12 Ah battery, a 20 W panel, the five steps of 100 minutes on the site, and the cellular and LoRa variants |
| [LoRa out of coverage](../network/lora-out-of-coverage.md) | The shared gateway, the energy table of its solar kit and a LoRa farm with no data plan |

## 3. What each figure contains

| Figure | Contains | Leaves out |
|---|---|---|
| Initial investment of a farm | The priced hardware, the SIM card of a cellular farm and the installation visit | Every pending item, shipping, import duties and IVA |
| Marginal monthly cash cost | Mobile data traffic, the fixed charge of the SIM, the cloud lines that grow with the farm count, the LoRa messages of a LoRa farm and the maintenance visits | The plan of the operator, which is not contracted, and the pending items |
| Monthly cost with shared expenses assigned | The marginal cost, the cash cost of the gateways, the replacement reserve and the fixed cloud lines divided by the farms | The pending parts and their reserve, the gateway mast and cables, shipping and duties. The fixed lines are assigned in full to the farms although the platform also serves carriers, centers and buyers. It is not a ceiling, since pending items would raise it |
| Commercial fee | Not defined | A fee needs a policy of the Federation, see section 11 |

The costs that other documents already carry are not repeated. The cloud lines come from the cost document once, the gateway is counted once for its purchase, installation, power, connectivity and maintenance, and the replacement reserve is shown apart from the cash cost.

## 4. Prices

| Item | Value | Source and date |
|---|---|---|
| COP per USD, central, low and high | 3,269.88, 3,048.12, 3,796.87 | Price basis, 10 November 2026 |
| USD per EUR | 1.1214 | European Central Bank euro reference rate, 10 November 2026 |
| IVA | 19% | Price basis. Every figure is before tax. Import duties are unknown and are not included |

| Item | Price as read | Used, low, base and high, USD | Status | Source and date | Tax, shipping and limits |
|---|---|---|---|---|---|
| Battery 12.8 V 12 Ah LiFePO4, Power-Sonic PSL-SC-12120 F2 | USD 144.77 | 144.77, 144.77, 144.77 | verified | TRC Electronics listing, trcelectronics.com, and the Power-Sonic data sheet, both read 2026-11-10 | Tax and shipping not stated. The data sheet states 12.8 V, 12 Ah, 153.6 Wh, a BMS, charge 0 to 45 C, discharge minus 20 to 60 C, 2,000 cycles at 100 percent depth of discharge and 151 x 99 x 95 mm. It meets the battery line of the node requirement |
| Solar panel 20 W 12 V | USD 39.50 | 39.50, 39.50, 39.50 | verified | ACOPower HY020-12M, acopower.com, read 2026-11-10 | Tax and shipping not stated |
| Charge controller 10 A, MPPT | USD 60.00 | 60.00, 60.00, 60.00 | verified | Victron SmartSolar MPPT 75/10, Renewable Outdoors, read 2026-11-10 | Tax and shipping not stated. The lithium profile was not read on the page |
| Soil probe, 7 variables, RS485 | QAR 295.00 at 3.64 QAR per USD | 81.04, 81.04, 81.04 | estimate | Voltaat VT-1767, voltaat.com, read 2026-11-10 | The rate is a peg that was not read from a primary source. No datasheet, so range and accuracy are unverified |
| Cellular board LTE-M and NB-IoT | USD 30.00, USD 35.86, USD 56.02 | 30.00, 35.86, 56.02 | verified | RAK5860 with a BG77 module (low), a BG95-M3 mini PCIe board from the price basis (base), a BG95-M3 evaluation board at DigiKey (high), read 2026-11-10 | All three are boards and not the bare module that the node would use. Bands for Colombia not checked |
| Cellular antenna | USD 39.97 | 39.97, 39.97, 39.97 | verified | ALFA AOA-4G-5AM N-male, Rokland, read 2026-11-10 | Covers 698 to 960 and 1,710 to 2,700 MHz. It is a larger antenna than a node may need. Fit to the mast not checked |
| LoRa module STM32WLE5, US915/AU915 | USD 5.99 | 5.99, 5.99, 5.99 | verified | RAK3172 SKU 306042, store.rakwireless.com, read 2026-11-10 | Shipping extra, tax not stated. The radio band is not chosen |
| Antenna for LoRa, 2 dBi | USD 5.00 | 5.00, 5.00, 5.00 | verified | RAK 2 dBi antenna, store.rakwireless.com, read 2026-11-10 | Shipping extra, tax not stated. Fit to the mast not checked |
| LoRaWAN gateway with solar kit, 8 channels AU915, cellular LTE variant | USD 1,199.00 | 1,199.00, 1,199.00, 1,199.00 | verified | WisGate Edge Pro Solar, variant 817039, store.rakwireless.com, read 2026-11-10 | Includes the gateway, a 50 Ah battery, an 80 W panel with its mounting kit and the cables between them. Shipping extra, tax not stated. The LTE is a Cat 4 module and not LTE-M |
| Antenna for the gateway, 915 MHz N-male | USD 16.97 and USD 42.97 | 16.97, 16.97, 42.97 | verified | 4 dBi fiberglass (low, base) and 5.8 dBi (high), Rokland, read 2026-11-10 | Fit to the gateway connector not checked |
| Self-service SIM tariff of a global provider | USD 0.03 per MB, USD 1 a month for each SIM, USD 3 for each card | see connectivity | estimate | hologram.io/pricing, read 2026-11-10 | Coverage and LTE-M service in Colombia not confirmed, so it is a published tariff and not an offer |
| Prepaid plan of a global provider | USD 14 one time with 500 MB, card USD 1 | low case | estimate | Price basis, read 2026-11-10 | Colombia not named as covered. 500 MB lasts more than 7 years at 5.5 MB a month |

Reference listings found for the pending items. They are not equivalent and stay out of every total.

| Pending item | Listing found | Why it is not equivalent |
|---|---|---|
| Batteries that are not equivalent | Kastar at USD 70.99 and Battery Space at USD 159.00 | Neither is shown to meet the node requirement, see the equivalence table. They are references and stay out of every total |
| Enclosure | RAK Unify IP67 150 x 100 x 45 mm at USD 39.00 | Too small for a 151 x 98 x 95 mm battery, so it is not equivalent to the node enclosure |
| Controller board | RAK19007 base 9.99, RAK4631 core 17.99, RAK5802 RS485 6.00, RAK12002 RTC 9.50 and RAK15001 flash 5.00, together USD 48.48 | A development kit. Its flash is 16 Mbit against at least 64 MB with encryption, and it has no switched probe supplies or field input protection |
| Climate sensor | RAK1901 SHTC3 module at USD 4.60, Milesight NB300-TH at USD 59.90 | The first has no outdoor rating, and the second is a standalone NB-IoT device and not a probe for the controller |
| Grain probe | No listing found | No listing to compare |
| Mast and fixings | RAK Unify pole kit at USD 6.50 and a 12 inch pole mast at USD 19.50 | They fit a small enclosure and are not a mast of the height that the sensors design requires |
| Cable and connectors | No listing of the RS485 cable and glands of the node found | No listing to compare |

The pages that opened were read on 2026-11-10 from the sites named, and none of them was contacted. A price in this table is a reference for the order of magnitude, and a quote replaces it. The parts that the node needs and that have no equivalent listing stay pending.

### Equivalence of the batteries

The node specification asks for 12.8 V, 12 Ah nominal, LiFePO4, a battery management system, the datasheet limits including the low temperature charging limit, and the energy of 12.8 V times 12 Ah, which is 153.6 Wh.

| Property | Requirement | Power-Sonic PSL-SC-12120 F2, USD 144.77, used in every scenario | Kastar, USD 70.99, reference | Battery Space, USD 159.00, reference |
|---|---|---|---|---|
| Chemistry and voltage | LiFePO4, 12.8 V | Nominal 12.8 V, 4 cells | 12.8 V stated | 12.8 V stated |
| Capacity | 12 Ah nominal | 12 Ah | 12 Ah at C/5 | Typical 12 Ah, minimum 11.85 Ah |
| Energy | 153.6 Wh | 153.6 Wh stated, and 153 Wh on the other sheet | The title says 153.6 Wh and a bullet says 84 Wh, so it conflicts | The title says 144 Wh, which is below 153.6 Wh |
| Protection | A battery management system | BMS with protection against over charge, over discharge, over current and cell balancing, with its values | Built-in BMS stated, no values | No BMS statement |
| Low temperature charge limit | Stated in the datasheet | Charge 0 to 45 C, discharge minus 20 to 60 C | Not stated | Charge 0 to 40 C, discharge minus 20 to 60 C |
| Cycle life | Datasheet figure | 2,000 cycles at 100 percent depth of discharge | Two figures that conflict | Not stated |
| Dimensions and weight | Fit the enclosure | 151 x 99 x 95 mm, 1.65 kg | 151 x 98 x 95 mm, 1.42 kg | Weight 2 lb 10 oz |
| Accessories | Not part of the requirement | F2 terminals, no accessory listed | None listed | None listed |
| Meets the node requirement | | Yes, on the data sheet | No, the energy and the charge limit are not consistent | No, the BMS is not stated and the energy is stated lower |

The base case no longer uses a battery that is known to fall short. The battery of every scenario is the Power-Sonic reference, which meets the requirement on its data sheet, and the two cheaper or other listings are kept as references that are not equivalent. The reserve of the battery uses this price. The calendar life of the battery was not read, and the lives in years remain assumptions.

## 5. Hardware of one farm

Known subtotal of priced parts. The pending items are not in it and are not zero. Every total below reads as the known subtotal plus the unknown cost of the pending items.

| Item | Low | Base | High | Status |
|---|---|---|---|---|
| Battery | 144.77 | 144.77 | 144.77 | verified |
| Solar panel 20 W | 39.50 | 39.50 | 39.50 | verified |
| Charge controller | 60.00 | 60.00 | 60.00 | verified |
| Soil probe | 81.04 | 81.04 | 81.04 | estimate |
| Cellular farm, radio board | 30.00 | 35.86 | 56.02 | verified, as a board |
| Cellular farm, antenna | 39.97 | 39.97 | 39.97 | verified |
| LoRa farm, module and antenna | 10.99 | 10.99 | 10.99 | verified |
| **Known subtotal, cellular farm** | 395.28 | 401.14 | 421.30 | known part only |
| **Known subtotal, LoRa farm** | 336.30 | 336.30 | 336.30 | known part only |
| SIM card or prepaid plan, one time, cellular farm | 15.00 | 3.00 | 3.00 | estimate, no plan is contracted |

Pending items of every farm, each an unknown cost: Enclosure IP67; Controller board; Climate sensor; Grain probe; Mast and fixings; Cable and connectors; Shipping, import duties and IVA of every item.

## 6. Installation in one visit

| Component | Low | Base | High | Origin |
|---|---|---|---|---|
| Work on the site, minutes | 100 | 100 | 100 | Assumption of the node specification, five steps of 30 + 20 + 10 + 15 + 25, and not measured |
| Preparation before the visit, minutes of one technician | 30 | 30 | 30 | Assumption |
| Technicians on the site | 1 | 1 | 2 | Assumption |
| Travel, round trip, hours | 1 | 2 | 4 | Assumption, no farm location is known |
| Technician rate, COP an hour | 15,000 | 25,000 | 40,000 | Assumption. No source for a technician rate was found, and the legal minimum wage is not a technician rate |
| Vehicle, COP an hour of travel | 25,000 | 25,000 | 25,000 | Assumption |
| Labor, USD | 14.53 | 31.86 | 144.76 | Calculation |
| Vehicle, USD | 7.65 | 15.29 | 30.58 | Calculation |
| **Installation total, USD** | 22.17 | 47.15 | 175.34 | Investment, one visit |

Conditions for a single visit. The installation fits one visit only when all of these hold, and a failed condition adds a visit that this document prices as a maintenance visit.

| Condition | Source |
|---|---|
| The node arrives assembled and provisioned, with its identity registered | Node specification, the preparation is priced here |
| The farm is already enrolled with its owner before the visit | Assumptions register, enrollment by field staff |
| The signal, and the port that the operator allows, are known to work at the site, or a gateway of the vereda is already in range for a LoRa farm | Node specification, step 4 of the installation. The operator confirmation is pending |
| The farmer or the person in charge is present for the last step | Node specification, step 5 |
| The mast, the panel and the probe cable lengths suit the site | Node specification, probe interface limits |
| The installer carries the node, the mast, the panel, the probes, a way to read the signal and the fixings | Node specification |

The 100 minutes are an estimate of the sensors design and are not measured. Later maintenance visits are priced apart in section 9.

### Investment of one farm

Initial investment only. Recurring cost is in the next table. Shipping, duties, IVA and the pending items are outside.

| Case | Low | Base | High |
|---|---|---|---|
| Cellular farm, known hardware and SIM start | 410.28 | 404.14 | 424.30 |
| Cellular farm, installation | 22.17 | 47.15 | 175.34 |
| **Cellular farm, known investment, plus the unknown cost of the pending items** | 432.45 plus pending | 451.29 plus pending | 599.64 plus pending |
| LoRa farm, without its gateway share, known hardware and SIM start | 336.30 | 336.30 | 336.30 |
| LoRa farm, without its gateway share, installation | 22.17 | 47.15 | 175.34 |
| **LoRa farm, without its gateway share, known investment, plus the unknown cost of the pending items** | 358.47 plus pending | 383.45 plus pending | 511.64 plus pending |

## 7. Connectivity, energy, replacement and maintenance

| Item | Treatment |
|---|---|
| Data traffic | The megabytes sent, priced per megabyte. A cellular node uses 5.5 MB a month in the low and base cases and 20 MB in the high case, which adds firmware and retries as an assumption. The price per megabyte is the published self-service tariff of a global provider, USD 0.03 |
| Fixed charge of the SIM | USD 1 a month for each SIM in the base and high cases, from the same tariff. The low case uses a prepaid plan of USD 14 with 500 MB, which lasts more than 7 years at 5.5 MB a month, and has no monthly charge |
| SIM card | USD 3 for each card in the base and high cases and USD 1 in the low case, paid once |
| Status of the plan | No plan is contracted. Coverage in Colombia and LTE-M service are not confirmed for either provider, so the connectivity lines are estimates and complete connectivity is not stated |
| LoRa farm | No data plan. It pays its cloud messages and a share of the gateway |
| Energy | A battery and a 20 W panel for each node, with no recurring cost. The gateway bundle includes its solar kit, so its energy is in the purchase once |
| Maintenance | One visit a year of 60 minutes on the site in the low and base cases and two in the high case. It is a cash cost and is separate from the installation |
| Replacement | A reserve for each priced part, its price divided by its life in months. A part with no price has no reserve yet. The lives are assumptions that differ by scenario, and the pages read give conflicting cycle figures for the battery |

## 8. Shared equipment

| Item for each gateway | Low | Base | High | Counted |
|---|---|---|---|---|
| Gateway with solar kit and antenna | 1,215.97 | 1,215.97 | 1,241.97 | once, investment |
| Installation, 4 hours with 2 technicians, travel, vehicle and the SIM card | 56.52 | 110.04 | 229.31 | once, investment |
| Backhaul data traffic, 20, 50, 150 MB a month | 0.60 | 1.50 | 4.50 | monthly cash |
| Fixed charge of the SIM | 1.00 | 1.00 | 1.00 | monthly cash |
| Maintenance visits with 2 technicians | 2.93 | 6.37 | 29.56 | monthly cash |
| Replacement reserve | 11.26 | 14.48 | 20.70 | monthly reserve |

The gateway bundle lists a solar kit with its battery, its panel and the mounting, so energy is bought once and has no recurring line. Whether the kit keeps the gateway running is a condition of viability and is not shown.

| Condition of viability | Calculation, with the assumptions of the LoRa path document | Result |
|---|---|---|
| Autonomy of 3 days | 50 Ah at 12.8 V is 640 Wh, and 512 Wh is usable at 0.80, so the load P must satisfy 24 h x 3 x P <= 512 Wh | P of 7.1 W or less |
| Autonomy of 5 days | 24 h x 5 x P <= 512 Wh | P of 4.3 W or less |
| Panel keeps the energy level | 80 W x 3 peak sun hours x 0.72 is 173 Wh a day, and it must cover 24 h x P | P of 7.2 W or less |

The consumption of the gateway and the usable energy of the kit are not read from the data sheet of the gateway or of the kit, so the contrast with them is pending. The statement of the seller that the kit gives more than 5 days is not checked here. If the load is above the limits above, the kit is not viable and a larger battery or panel is another pending cost.

Pending for each gateway: Mast of the height the site study sets; Cables and lightning protection; Shipping, import duties and IVA. The gateway of the price basis, EUR 537.76 at a retailer with VAT, differs from the USD 382.00 that the manufacturer store lists for the 8 channel variant without LTE and from the USD 1,199.00 for the bundle used here.

The number of farms for each gateway is an economic assumption and says nothing about radio coverage. Gateways are rounded up and each is counted once.

| Farms for each gateway | Investment from the gateway for each LoRa farm, base | Monthly cash for each LoRa farm, base | Monthly reserve for each LoRa farm, base |
|---|---|---|---|
| 5 | 265.20 | 1.77 | 2.90 |
| 10 | 132.60 | 0.89 | 1.45 |
| 20 | 66.30 | 0.44 | 0.72 |

These shares assume full gateways. The fleet tables show the rounding.

## 9. Monthly cost

Cash cost and the replacement reserve are kept apart. A replacement bought later is paid from the reserve and is not added to the monthly total a second time. Data traffic and the fixed charge of the SIM are separate lines.

| Line | Cellular low | Cellular base | Cellular high | LoRa base | Kind |
|---|---|---|---|---|---|
| Mobile data traffic | 0.00 | 0.16 | 0.60 | 0.00 | cash |
| Fixed charge of the SIM | 0.00 | 1.00 | 1.00 | 0.00 | cash |
| Cloud lines that grow with the farm count | 0.01 | 0.01 | 0.01 | 0.01 | cash |
| LoRaWAN messages of the cloud | 0.00 | 0.00 | 0.00 | 0.01 | cash |
| Maintenance visits | 1.40 | 3.19 | 15.29 | 3.19 | cash |
| **Marginal cash cost** | 1.42 | 4.36 | 16.90 | 3.21 | cash |
| Replacement reserve of the priced parts | 4.22 | 6.41 | 9.98 | 5.73 | reserve |
| **Marginal cash plus reserve** | 5.63 | 10.77 | 26.88 | 8.94 | |

The plan of the operator is not contracted. The connectivity lines use a published self-service tariff of a global provider, whose coverage and LTE-M service in Colombia are not confirmed, and a prepaid plan for the low case. They are estimates and not the connectivity cost of an offer, so complete connectivity is not stated.
The earlier figure of USD 3.21 a month for a cellular farm held 3.19 of maintenance visit labor and vehicle, 0.01 of cloud lines and 0.02 of data traffic. It held no fixed charge of a SIM. The maintenance visit was 99 percent of it.

The monthly cost with the shared expenses assigned for a whole fleet, with the fixed cloud lines, the gateways and the reserve, is in section 10.

## 10. From 200 to 1,000 farms

### Fleet by number of farms and share of LoRa farms

Investment and recurring cost are separate. Recurring cash holds the nodes, the cloud lines that grow with the farms, the gateways and the fixed cloud lines of the cost document, which are assigned in full to the farms. The reserve is not in the cash column.

| Farms | LoRa share | Gateways | Investment, nodes | Investment, installation | Investment, gateways | Investment total, known | Monthly cash | Monthly reserve | Cash and reserve for each farm |
|---|---|---|---|---|---|---|---|---|---|
| 200 | 0% | 0 | 80,828.00 | 9,429.50 | 0.00 | 90,257.50 | 1,042.98 | 1,281.60 | 11.62 |
| 200 | 25% | 5 | 77,436.00 | 9,429.50 | 6,630.04 | 93,495.54 | 1,029.52 | 1,320.21 | 11.75 |
| 200 | 50% | 10 | 74,044.00 | 9,429.50 | 13,260.08 | 96,733.58 | 1,016.06 | 1,358.82 | 11.87 |
| 400 | 0% | 0 | 161,656.00 | 18,859.00 | 0.00 | 180,515.00 | 1,915.86 | 2,563.20 | 11.20 |
| 400 | 25% | 10 | 154,872.00 | 18,859.00 | 13,260.08 | 186,991.08 | 1,888.93 | 2,640.42 | 11.32 |
| 400 | 50% | 20 | 148,088.00 | 18,859.00 | 26,520.15 | 193,467.15 | 1,862.01 | 2,717.64 | 11.45 |
| 600 | 0% | 0 | 242,484.00 | 28,288.50 | 0.00 | 270,772.50 | 2,788.74 | 3,844.80 | 11.06 |
| 600 | 25% | 15 | 232,308.00 | 28,288.50 | 19,890.11 | 280,486.61 | 2,748.35 | 3,960.63 | 11.18 |
| 600 | 50% | 30 | 222,132.00 | 28,288.50 | 39,780.23 | 290,200.73 | 2,707.97 | 4,076.45 | 11.31 |
| 800 | 0% | 0 | 323,312.00 | 37,718.00 | 0.00 | 361,030.00 | 3,661.61 | 5,126.41 | 10.99 |
| 800 | 25% | 20 | 309,744.00 | 37,718.00 | 26,520.15 | 373,982.15 | 3,607.77 | 5,280.84 | 11.11 |
| 800 | 50% | 40 | 296,176.00 | 37,718.00 | 53,040.30 | 386,934.30 | 3,553.92 | 5,435.27 | 11.24 |
| 1000 | 0% | 0 | 404,140.00 | 47,147.50 | 0.00 | 451,287.50 | 4,534.49 | 6,408.01 | 10.94 |
| 1000 | 25% | 25 | 387,180.00 | 47,147.50 | 33,150.19 | 467,477.69 | 4,467.18 | 6,601.05 | 11.07 |
| 1000 | 50% | 50 | 370,220.00 | 47,147.50 | 66,300.38 | 483,667.88 | 4,399.88 | 6,794.09 | 11.19 |

Every total is a known subtotal. The pending items of the nodes and gateways and the shipping, duties and IVA add to it.

### Gateways for each assumption of farms in range

| Farms | LoRa share | Farms for each gateway | Gateways, rounded up | Investment known | Monthly cash | Monthly reserve | Cash and reserve for each farm |
|---|---|---|---|---|---|---|---|
| 200 | 25% | 5 | 10 | 100,125.58 | 1,073.87 | 1,392.59 | 12.33 |
| 200 | 25% | 10 | 5 | 93,495.54 | 1,029.52 | 1,320.21 | 11.75 |
| 200 | 25% | 20 | 3 | 90,843.52 | 1,011.77 | 1,291.26 | 11.52 |
| 200 | 50% | 5 | 20 | 109,993.65 | 1,104.77 | 1,503.58 | 13.04 |
| 200 | 50% | 10 | 10 | 96,733.58 | 1,016.06 | 1,358.82 | 11.87 |
| 200 | 50% | 20 | 5 | 90,103.54 | 971.70 | 1,286.44 | 11.29 |
| 1000 | 25% | 5 | 50 | 500,627.88 | 4,688.97 | 6,962.94 | 11.65 |
| 1000 | 25% | 10 | 25 | 467,477.69 | 4,467.18 | 6,601.05 | 11.07 |
| 1000 | 25% | 20 | 13 | 451,565.60 | 4,360.73 | 6,427.34 | 10.79 |
| 1000 | 50% | 5 | 100 | 549,968.26 | 4,843.44 | 7,517.88 | 12.36 |
| 1000 | 50% | 10 | 50 | 483,667.88 | 4,399.88 | 6,794.09 | 11.19 |
| 1000 | 50% | 20 | 25 | 450,517.69 | 4,178.09 | 6,432.19 | 10.61 |

### Scenarios low, base and high

| Farms | Scenario | Investment known | Recurring cash a month | Reserve a month | Recurring cash and reserve for each farm |
|---|---|---|---|---|---|
| 200 | low | 89,153.86 | 476.27 | 874.94 | 6.76 |
| 200 | base | 93,495.54 | 1,029.52 | 1,320.21 | 11.75 |
| 200 | high | 122,883.94 | 3,646.81 | 2,039.68 | 28.43 |
| 1000 | low | 445,769.29 | 1,700.96 | 4,374.68 | 6.08 |
| 1000 | base | 467,477.69 | 4,467.18 | 6,601.05 | 11.07 |
| 1000 | high | 614,419.68 | 17,553.66 | 10,198.39 | 27.75 |

The low case lowers travel and labor and lengthens the lives of the parts, and the high case does the opposite. The low case also pays connectivity up front with a prepaid plan, so its investment of a cellular farm can exceed the base case while its monthly amount is lower. A scenario does not move the pending items, whose cost is unknown in all three.

### Cost for each farm by number of farms

| Farms | Marginal cash cost | Fixed cloud lines | Gateway cash | Reserve | Cash and reserve for each farm |
|---|---|---|---|---|---|
| 200 | 4.08 | 0.85 | 0.22 | 6.60 | 11.75 |
| 400 | 4.08 | 0.43 | 0.22 | 6.60 | 11.32 |
| 600 | 4.08 | 0.28 | 0.22 | 6.60 | 11.18 |
| 800 | 4.08 | 0.21 | 0.22 | 6.60 | 11.11 |
| 1000 | 4.08 | 0.17 | 0.22 | 6.60 | 11.07 |

At 200 farms the fixed cloud lines add USD 0.85 for each farm and at 1,000 farms USD 0.17. The cost for each farm falls with the number of farms because the fixed cloud lines spread, and it rises with the share of LoRa farms in this estimate because a gateway is a whole unit. The cloud lines that grow with the farms are linear, since the cloud addressing design holds from 200 to 1,000 farms with no change.

## 11. The monthly amount

The card asks for the cost of the equipment and the monthly charge, so that a farmer can judge whether the investment is moderate. A charge depends on a policy of the Federation, which has not set one. This document therefore computes the monthly cost of a farm and records a provisional choice for the exercise.

Decision recorded. isahrnd chose option C as an academic provisional proposal for the exercise, which is the monthly cost with operation, the replacement reserve and the shared cloud expenses, with no margin and no financing. The initial investment is presented apart. The decision is isahrnd's for the exercise. It is not an approval by the Federation, it is not a fee contracted with anyone, and the amount stays provisional while essential costs are missing, which are listed below.

A fee is a policy decision. These are the ways considered to build a monthly amount from the figures above. Option C was chosen by isahrnd for the exercise, and A and B are kept as references. A financed investment and a margin are not part of this version. Values are base scenario, 25 percent LoRa, 10 farms for each gateway, in USD for each farm a month, before the pending items, tax and duties.

| Option | How it is built | At 200 farms | At 1,000 farms |
|---|---|---|---|
| A. Recover only the marginal cash cost | Data, SIM, cloud lines that grow, maintenance, with no reserve and no shared cost | 4.08 | 4.08 |
| B. Recover the cash cost, the gateways and the reserve, and the Federation bears the fixed cloud lines | Option A plus the gateway cash cost and the reserve | 10.90 | 10.90 |
| C. Recover everything recurring, with the fixed cloud lines divided by the farms. Chosen for the exercise | Option B plus the fixed cloud lines of the cost document | 11.75 | 11.07 |

Each option leaves out the pending items. A subsidy, an interest rate, a margin or a different share of the fixed cloud lines are decisions that no document of the project makes, and whether the farmer is charged any of this is also open.

Option C was chosen by isahrnd as an academic provisional proposal for this exercise. The Federation did not approve it, it is not a contracted fee, and it stays provisional while essential costs are missing. It has no margin and no financing. The initial investment is presented apart and is not part of the monthly amount.

Formula for each farm a month, base scenario, 25 percent LoRa, 10 farms for each gateway, with N farms and NL = 0.25 N farms on LoRa and NC = N - NL on cellular:

C(N) = [ NC x (data traffic + fixed charge of the SIM) + N x (cloud lines that grow + maintenance visits) + NL x LoRa messages + G x (gateway data + gateway SIM charge + gateway maintenance) + reserve of the priced parts of the nodes and the gateways + fixed cloud lines ] / N, with G = NL / 10 rounded up.

| Component | Pays | At 200 farms | At 1,000 farms |
|---|---|---|---|
| Data traffic and fixed charge of the SIM of the cellular nodes | Monthly cash | 0.87 | 0.87 |
| Cloud lines that grow with the farms | Monthly cash | 0.01 | 0.01 |
| Maintenance visits of the nodes | Monthly cash | 3.19 | 3.19 |
| LoRaWAN messages of the cloud | Monthly cash | 0.00 | 0.00 |
| Gateways: data traffic, SIM charge and maintenance visits | Monthly cash | 0.22 | 0.22 |
| Replacement reserve of the priced parts of nodes and gateways | Reserve for later replacements | 6.60 | 6.60 |
| Fixed cloud lines divided by the farms | Monthly cash, assigned in full to the farms | 0.85 | 0.17 |
| **Option C, known part** | | 11.75 plus pending | 11.07 plus pending |

| Paid by the initial investment, once | Covered by the monthly amount of option C |
|---|---|
| Purchase of the priced hardware of the node, including the SIM card | Data traffic, SIM charge, cloud lines, LoRa messages and maintenance visits |
| Installation visit of the node, labor and vehicle | The cash cost of the gateways |
| Purchase and installation of the gateways, including their solar kit and SIM card | The fixed cloud lines divided by the farms |
| | The reserve that pays the replacement of a part after its life |

Nothing is counted twice. The initial purchase is paid only by the investment, and no amortization of it is in the monthly amount. The reserve pays only the replacements that come after the life of a part, so the purchase of a replacement is paid from it and is not added again. Maintenance visits are cash and are not in the investment. The installation visit is in the investment and is not in the monthly amount.

Investment of a farm apart, base scenario, 25 percent LoRa, 10 farms for each gateway, known part.

| Case | At 200 farms | At 1,000 farms |
|---|---|---|
| Nodes, hardware and SIM card, for each farm | 387.18 | 387.18 |
| Installation visits, for each farm | 47.15 | 47.15 |
| Gateways, purchase and installation, for each farm | 33.15 | 33.15 |
| Total, for each farm | 467.48 | 467.48 |

Pending items with the exact datum that is missing and their effect. A pending item raises the investment, the monthly amount through its reserve, or both. None is counted as zero.

| Pending item | Datum that is missing | Effect on the investment | Effect on the monthly amount |
|---|---|---|---|
| Enclosure IP67 of the node | A price for an IP67 enclosure that holds the controller board, a 151 x 99 x 95 mm battery and the charge controller, with glands | Raises it by the price | Raises the reserve by the price over its life |
| Controller board | A price of a board with RS485, a clock with backup power, at least 64 MB of encrypted external flash, switched probe supplies and protected inputs | Raises it by the price | Raises the reserve |
| Climate sensor | The interface that the node specification leaves pending, and the price of an outdoor probe for 40 to 80 percent humidity and 14 to 30 C | Raises it by the price | Raises the reserve |
| Grain probe | A price of a probe for grain temperature above 40 C and humidity near 12 percent | Raises it by the price | Raises the reserve |
| Soil probe | A manufacturer data sheet with range and accuracy, and a price in a stated currency | The estimate may move | The reserve moves with it |
| Mast and fixings | The mast height and wind rating from the sensors design, and a price | Raises it by the price | Raises the reserve a little |
| Cable and connectors | The cable lengths of each site and their ratings, and a price | Raises it by the price | None, or a small reserve |
| Shipping, import duties and IVA | A shipping quote, the customs classification and the rates, and whether IVA applies | Raises it, with IVA up to 19 percent | Raises the reserve in the same proportion |
| Plan of the operator | A quote with the fixed charge, the price per megabyte and LTE-M service in Colombia | Replaces the SIM card price | Replaces the data and SIM lines of the nodes and gateways |
| Technician rate, travel and visits | A quote for a technician day and the locations of the farms | Moves the installation | Moves the maintenance visits |
| Gateway mast, cables and lightning protection | A mast of the height the site study sets, and prices | Raises the gateway purchase | Raises the gateway reserve |
| Gateway load and kit energy | The consumption of the gateway and the usable energy of the kit from their data sheets | A larger kit raises the gateway purchase if the load is above the limits of the viability table | Raises the gateway reserve |
| Controller of the battery charge | The lithium profile of the charge controller on its data sheet | A different controller changes its price | Changes its reserve |
| Calendar life of the parts | Data sheet lives of the battery, panel, probes and radio | None | Moves the reserve in inverse proportion |
| Fixed cloud lines share | A decision on how much of the fixed lines belongs to the farms | None | Lowers the fixed line share if part is assigned to others |

What a fee still needs. The Federation decides whether it charges the farmer at all, whether it subsidizes the platform or the equipment, whether a margin or financing applies, and what share of the fixed cloud lines belongs to the farms. Until it does, option C is a cost and the card does not have a fee.

## 12. Context against the price of coffee

The known investment of a farm, base scenario, in kilograms of dry parchment coffee at the reference price of the Federation of 10 November 2026, COP 2,000,000 for a load of 125 kg, so COP 16,000 a kilogram.

| Case | Known investment, USD | COP at the central TRM | Kilograms of dry parchment coffee | Same at the low and high TRM |
|---|---|---|---|---|
| Cellular farm | 451.29 | 1,475,656 | 92.2 | 86.0 to 107.1 |
| LoRa farm without the gateway share | 383.45 | 1,253,827 | 78.4 | 73.0 to 91.0 |

The comparison shows no profitability and no capacity to pay. The pending items would raise both figures.

The reference price is the internal reference price for dry parchment coffee that the Federation shows on its site, read on 2026-11-10. It varies with the distance to the purchase point. The comparison is context. It shows no profitability and no capacity to pay, and the Federation decides whether an investment of this order is moderate.

### IVA

If IVA of 19% applies in full to the known investment, a cellular farm goes from 451.29 to 537.03. Import duties are unknown and are in neither figure.

## 13. Consistency with the cost document

The cloud lines of this estimate come from the cost document of this repository and are checked against it by the script, which fails if a value changes.

The cost document gives USD 177.05 for a normal month and USD 200.41 for a harvest month for the production platform, after its later correction. The project status file of the handbook gives USD 177.23 and USD 201.11 for the same total. The two sources differ by 0.18 and 0.70, and this estimate reads the cost document. The status file is not edited here, and its owner decides which value stands.

The price basis lists a gateway at EUR 537.76 at a retailer with VAT. The manufacturer store lists USD 382.00 for the 8 channel variant without LTE and USD 1,199.00 for the bundle with a solar kit and LTE, which is the one priced here. The two are listings of different items, and the owner of the price basis decides whether to add the manufacturer listing.

## 14. Assumptions and pending confirmations

| Item | Origin | Who confirms | Effect if it fails |
|---|---|---|---|
| Farms for each gateway, 5, 10 and 20 | Assumption | Site study of each vereda | The gateway share of a LoRa farm moves in inverse proportion |
| Share of LoRa farms, 0, 25 and 50 percent | Assumption, no farm list exists | Federation | The blended investment and cost move between the two variants |
| Technician rate, COP 15,000 to 40,000 an hour | Assumption | Quote from a technician or a contractor | Installation, visits and gateway work move in proportion |
| Technicians on the site, 1 with 2 in the high case | Assumption | First installations | Installation labor rises with the number |
| Travel of 1, 2 and 4 hours for the round trip | Assumption | Farm and vereda locations | Installation and visits move in proportion |
| One or two maintenance visits a year | Assumption | Sensors design | The monthly share moves in proportion |
| Lives of the parts in years, by scenario | Assumption | Datasheets | The reserve moves in inverse proportion |
| Data of a node, 5.5 and 20 MB a month, and of a gateway, 20, 50 and 150 MB a month | Price basis for the node in the base case, otherwise assumption | Measurement at the first installations | The data lines move in proportion |
| Published tariff of a global provider as the price of connectivity | Estimate | Operator quote with coverage and LTE-M service in Colombia | The SIM and data lines change |
| Pending hardware, shipping, import duties and IVA | Pending | Quotes and customs agent | Investment and the reserve rise |
| The fixed cloud lines are assigned in full to the farms | Assumption | Federation | The loaded cost falls if part is assigned to carriers, centers and buyers |
| The LoRa message cost does not overlap the telemetry line of the cost document | Assumption | Owner of the cost document | At most USD 0.01 a month for each LoRa farm |
| A commercial fee policy | Pending | Federation | No fee can be stated until it exists |

## 15. Criteria of the story and their evidence

| Literal criterion | Where it is answered | Gaps | Assumptions accepted |
|---|---|---|---|
| Hardware, installation in one visit and monthly charge for each farm | Sections 4 to 11 and the script. The hardware has a known subtotal and a list of pending items, the installation is priced with its conditions, and the monthly cost is given as cash, reserve and with shared expenses assigned, in three scenarios | Essential parts have no equivalent listing, which are the enclosure, the controller board, the climate sensor, the grain probe, the mast and the cables. The plan of the operator is not contracted. The monthly amount of option C is a provisional cost chosen by isahrnd for the exercise and is not a fee, since a fee needs a policy of the Federation. The totals are known subtotals plus those unknowns, which section 11 lists with the datum that is missing | Section 14 |
| Sensitivity from 200 to 1,000 farms | Section 10 and the script, in three scenarios | None for the known subtotal | Section 14 |

## 16. Sources

| Source | Used for |
|---|---|
| Price basis, cloud cost, autonomous node and LoRa path documents of this repository | Rates, cloud lines, the bill of materials, times and the shared gateway |
| Listings read on 2026-11-10 at mykastar.com, batteryspace.com, acopower.com, renewableoutdoors.com, store.rakwireless.com, store.rokland.com, voltaat.com and digikey.com | The price register |
| Hologram, pricing page, hologram.io/pricing, 2026-11-10 | The published self-service tariff used as a reference for connectivity |
| European Central Bank, euro foreign exchange reference rates, 2026-11-10 | The euro to dollar conversion |
| Federación Nacional de Cafeteros de Colombia, internal reference price of dry parchment coffee, federaciondecafeteros.org, 2026-11-10 | The context of section 12 |
