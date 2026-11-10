# Mobile network validity

This document states what the public sources show about the mobile networks that the pilot can use in Cauca, Huila and Tolima, and what they leave open. It checks that no part of the design depends on a mobile generation that is being retired, it records what each source proves, and it lists what still needs confirmation from the Federation, the operators and the installers. Every figure carries the period of its data and the date it was published, because a figure from one period says nothing about another.

## Contents

1. What the platform needs from the mobile network
2. Three questions that must stay apart
3. Is a generation being retired
4. Published sites and coverage in the three departments
5. LTE-M and NB-IoT
6. Coverage at a farm
7. Compatibility of the device
8. What the design requires
9. Check of the design documents
10. Pending confirmations
11. Sources and how they were read

### Terms used

| Term | Meaning in this document |
|---|---|
| 2G, 3G, 4G, 5G | Generations of mobile networks. 4G is also called LTE |
| LTE-M and NB-IoT | Variants of LTE for devices that send little data and need little energy. They share the radio network of an operator and need the operator to enable them |
| Site | A base station location that an operator reports to the regulator, with the technologies it carries |
| Municipal seat | The main urban area of a municipality |
| Populated center | A municipal seat or another populated area in the regulator datasets. Farms lie outside these areas |
| CRC | The communications regulator of Colombia |
| Postdata | The open data platform of the CRC, with DaTIC as its interactive maps |
| Operator | A provider of mobile network and services. The datasets name Claro, Movistar, Tigo and WOM |

---

## 1. What the platform needs from the mobile network

| Component | Mobile network use | Owner of the device |
|---|---|---|
| Farm node with signal | Modem that publishes readings over MQTT and TLS | Federation |
| Shared LoRaWAN gateway | Backhaul to the cloud from a high point with signal, which also carries the traffic of the farms out of coverage | Federation |
| Carrier phones | HTTPS from the carrier application | Carriers |
| Farmer phones | Mobile push of alerts | Farmers |

Collection centers use a wired WAN, and farms with no coverage use LoRa to the shared gateway, so neither depends on a mobile network at the farm. The gateway backhaul still does, which is why the choice below applies to it as well.

## 2. Three questions that must stay apart

| Question | What can answer it | What it does not answer |
|---|---|---|
| Is the technology and the operator network still in service, and is a retirement announced | Regulator statements, operator announcements, site counts over time | Whether a signal reaches a farm, and whether a device works on that network |
| Does a signal reach this place | A coverage map read at the exact coordinates, then a field measurement or a SIM test at the site | Whether the technology will remain in service, and whether the device supports the bands |
| Does the chosen device work on this network | The bands, category and certification of the modem against the operator documents, and a test with the contracted SIM | Whether the place has coverage |

The 4G coverage of an operator also says nothing about LTE-M or NB-IoT, because those variants need the operator to enable them and to sell a plan that uses them.

## 3. Is a generation being retired

### National position

There is no official national schedule to retire 2G or 3G. The regulator replied on 10 February 2026 to a public request on this subject and said that, by the principle of technological neutrality of Law 1341 of 2009, each operator decides when and where it retires its networks, and that the regulator does not issue schedules or set obligations for the retirement. An earlier reply of 17 January 2025 says the same.

The absence of a national schedule does not guarantee that an operator keeps a network in service. Each operator can decide alone, and the only protection found in the sources is the notice rule below.

### By operator

| Operator | What the sources say | Source and date |
|---|---|---|
| Claro | Announced the end of its 2G network, with no date and no statement about 3G. The 2G sites it reports in the three departments fell in the last year, see section 4 | Claro institutional page of 6 October 2022. Postdata, 2026 second quarter |
| Movistar | Reports no 2G sites in Huila and Tolima, and none in Cauca in 2026 second quarter, against one in 2025 second quarter. An official page on the 2G switch-off listed by a search engine returned an error when it was opened, so no Movistar statement was read | Postdata, 2026 second quarter. Page not read |
| Tigo | States that it switched off 2G on 1 November 2022 and that phones that work on 3G or 4G see no change. The regulator says it has no 2G base stations nationwide. No notice about 3G was found | Tigo help article, undated. CRC replies of 17 January 2025 and 10 February 2026 |
| WOM | Reports sites with 3G and 4G and none with 2G. Its own site could not be reached on 10 November 2026, so no WOM statement was read | Postdata, 2026 second quarter. Site not read |

The statements of an operator describe what it said on a date. A missing notice proves nothing about the next quarter.

### Notice to users

Resolution CRC 5050 of 2016, article 5.1.1.3.8, as restated by Resolution CRC 6890 of 2022, says that when a technological migration of the provider requires an update of terminals, the operators must have warned the users at least six months in advance that service on the only network that supports their equipment will be switched off, and must offer options to replace the terminals. The text was read in the compilation published by the Ministry of Information and Communications Technologies on 10 November 2026. That compilation is a reference copy, and the validity of the article should be confirmed in the official publication before it is quoted in a contract.

The scope has limits that the project must not stretch.

| Point | What the text supports |
|---|---|
| Who receives the notice | The users of the operator, which are the holders of the lines. The project learns of it only if it holds the lines, or if the holder passes it on |
| When it applies | In a technological migration that requires a terminal update, and for a device that has no other network to use |
| What it gives | A notice and replacement options, and the end of the contract if the equipment is not replaced. It does not give continuity of service |
| Lines for devices | The sources read do not settle whether lines for machines and IoT devices are covered in the same way. This stays open |

A node modem that supports only a network being retired would receive, at best, a notice addressed to the line holder. The design therefore avoids that case in advance, see section 8.

## 4. Published sites and coverage in the three departments

Two public Postdata datasets were downloaded on 9 and 10 November 2026 and summarized with a script that is part of this repository, together with the derived table by municipality. Both datasets come from reports that the operators send to the regulator.

| Dataset | Content | Period of the data | Published or modified |
|---|---|---|---|
| Infrastructure of mobile access networks | Sites by municipality, operator and technology | Quarters 2021 second quarter to 2026 second quarter. This document uses 2025 and 2026 second quarters | File modified 16 September 2026 |
| Coverage of mobile services | Area covered by operator, technology and signal level inside each populated center | 2023 first quarter to 2025 fourth quarter. This document uses 2025 fourth quarter | File modified 6 May 2026 |

Limits of the data.
- The datasets are departmental and municipal. They give no figure at a farm.
- The coverage dataset covers municipal seats and other populated centers only, so it says nothing about the rural land where farms lie.
- The coverage dataset reports area by signal level, and the levels are not defined in the dataset page or in the files. The percentages below add all levels, so they show the share of the area with any reported signal and no information about its quality.
- The datasets list 2G, 3G, 4G and 5G. They do not separate LTE-M or NB-IoT.
- The infrastructure quarters and the coverage quarters differ, and they must not be read as one measurement. The national figures that the regulator published for 31 December 2024 are a third period, and they are not mixed here.
- A change between two quarters can come from a change in how an operator reports, so the counts show movement and give no cause. Movistar and Tigo report almost the same figures in 2026 second quarter, which is consistent with shared network operation reported in the press. This document did not verify that.

### Sites by operator and technology

| Department | Operator | Sites in 2026 second quarter (2025 second quarter) | With 2G | With 3G | With 4G | Municipalities with a site |
|---|---|---|---|---|---|---|
| Cauca | Claro | 284 (279) | 81 (107) | 178 (179) | 282 (277) | 42 |
| Cauca | Movistar | 180 (157) | 0 (1) | 122 (95) | 169 (137) | 39 |
| Cauca | Tigo | 185 (161) | 0 (0) | 123 (70) | 176 (160) | 39 |
| Cauca | WOM | 72 (72) | 0 (0) | 35 (39) | 72 (72) | 32 |
| Huila | Claro | 224 (216) | 108 (117) | 164 (165) | 223 (213) | 35 |
| Huila | Movistar | 207 (182) | 0 (0) | 163 (125) | 198 (158) | 35 |
| Huila | Tigo | 207 (156) | 0 (0) | 164 (70) | 198 (147) | 35 |
| Huila | WOM | 94 (93) | 0 (0) | 56 (56) | 94 (93) | 33 |
| Tolima | Claro | 335 (332) | 157 (162) | 235 (236) | 332 (329) | 47 |
| Tolima | Movistar | 306 (257) | 0 (0) | 219 (174) | 301 (228) | 46 |
| Tolima | Tigo | 322 (270) | 0 (0) | 217 (106) | 317 (261) | 46 |
| Tolima | WOM | 115 (115) | 0 (0) | 90 (91) | 115 (115) | 36 |

A site with several technologies counts once in each column. Of the three departments, only Claro reports sites with 2G in 2026 second quarter, and its count fell in each of them over the year. Claro reports about the same number of sites with 3G as a year before. No operator shows a drop of 3G sites large enough to read as a retirement in these figures.

### Coverage of populated centers in 2025 fourth quarter

Each cell gives the number of seats or centers where the operator reports any area of that technology, out of the total in the dataset, and in brackets the share of their area with any reported signal.

| Department | Operator | 4G in municipal seats | 4G in other populated centers | 3G in municipal seats | 3G in other populated centers |
|---|---|---|---|---|---|
| Cauca | Claro | 42 of 42 (99.6 %) | 512 of 523 (94.9 %) | 41 of 42 (99.5 %) | 495 of 501 (96.2 %) |
| Cauca | Movistar | 36 of 42 (96.2 %) | 317 of 523 (68.0 %) | 36 of 42 (96.2 %) | 230 of 501 (52.5 %) |
| Cauca | Tigo | 37 of 42 (96.6 %) | 337 of 523 (70.7 %) | 34 of 42 (93.5 %) | 160 of 501 (41.0 %) |
| Cauca | WOM | 32 of 42 (83.1 %) | 114 of 523 (17.3 %) | 10 of 42 (57.1 %) | 52 of 501 (13.0 %) |
| Huila | Claro | 37 of 37 (98.4 %) | 158 of 171 (87.8 %) | 37 of 37 (99.9 %) | 146 of 159 (90.7 %) |
| Huila | Movistar | 37 of 37 (98.7 %) | 133 of 171 (79.4 %) | 37 of 37 (98.5 %) | 83 of 159 (63.1 %) |
| Huila | Tigo | 37 of 37 (98.8 %) | 133 of 171 (81.3 %) | 36 of 37 (97.6 %) | 65 of 159 (46.3 %) |
| Huila | WOM | 33 of 37 (89.1 %) | 32 of 171 (18.0 %) | 9 of 37 (72.7 %) | 13 of 159 (11.7 %) |
| Tolima | Claro | 47 of 47 (99.4 %) | 203 of 216 (81.2 %) | 47 of 47 (99.4 %) | 207 of 211 (95.9 %) |
| Tolima | Movistar | 46 of 47 (98.8 %) | 180 of 216 (82.4 %) | 45 of 47 (98.9 %) | 140 of 211 (71.6 %) |
| Tolima | Tigo | 46 of 47 (98.9 %) | 189 of 216 (86.4 %) | 44 of 47 (97.9 %) | 120 of 211 (58.8 %) |
| Tolima | WOM | 36 of 47 (86.5 %) | 39 of 216 (18.2 %) | 17 of 47 (77.2 %) | 28 of 211 (12.0 %) |

The municipal table in `data/mobile-coverage-cauca-huila-tolima.csv` holds the same figures by municipality, operator, technology and type of center, and `tools/mobile_coverage_extract.py` regenerates it from the two downloaded files.

What this table shows is that 4G is published in nearly every municipal seat of the three departments for Claro, Movistar and Tigo, and that outside seats the share of area with 4G varies between operators and between departments. It gives no signal at a farm.

## 5. LTE-M and NB-IoT

No operator confirmation of LTE-M or NB-IoT was obtained. The datasets do not separate them from 4G, so the 4G figures above show nothing about them.

| Operator | What was found | Status |
|---|---|---|
| Claro | A search found business pages on IoT connectivity over SIM. They were not opened in this review, so no statement from them is used | Not confirmed |
| Movistar | The business site offers a managed machine line service. The page does not name the radio technologies, and it directs the visitor to a sales line | Not confirmed |
| Tigo | A search listed a managed connectivity service with IoT SIMs. The page returned an access error when it was opened, so no statement was read | Not confirmed |
| WOM | Its site could not be reached | Not confirmed |

Each operator must confirm, for the municipalities of the pilot, whether LTE-M or NB-IoT is enabled, where it has coverage, which contracted plan applies, and which devices it accepts.

## 6. Coverage at a farm

No coverage is stated for any farm. The repository holds no list of pilot farms, and the datasets do not reach rural land. A statement about a farm needs its coordinates, the coverage map of each operator read at those coordinates on a known date, and a measurement or a SIM test at the site.

## 7. Compatibility of the device

The modem of the node and the gateway is not chosen, so no compatibility is shown. Each operator publishes the bands that a device must support for its 4G network, and the selection of the hardware compares them with the bands and the category of the candidate modems. The bands per operator were not collected in this document.

## 8. What the design requires

The design never depends on the availability of 2G or 3G. A node or gateway modem must work on 4G networks with no fallback to 2G or 3G.

LTE-M and NB-IoT are candidates for the node when the operator confirms the availability, the coverage, the contracted service and the compatibility of the device. A conventional LTE category can also be evaluated. No 4G modem is approved by default, and its selection considers the following.

| Criterion | What is checked |
|---|---|
| Bands and category | Those that the chosen operator supports, and the ones it enables for its IoT plan |
| Energy | The consumption of each connection and the autonomy of the solar node, against the estimates in the farm connectivity document |
| Protocols and capacity | MQTT over TLS on port 8883 or 443, the size of the connection and the configuration exchange |
| Antenna and site | The antenna, the conditions of the slope and the behavior with no signal |
| Plan | The availability and the cost of the data plan |

The selection of the hardware belongs to the specification of the autonomous node. The decision also applies to the cellular backhaul of the shared gateway. It leaves unchanged the LoRa path for the farms out of coverage, and the data mule for their objects.

## 9. Check of the design documents

A search over the design documents for 2G, 3G, GSM, UMTS, GPRS, EDGE and fallback found no requirement of a retired generation. The documents mention LTE for the node modem, the gateway backhaul and the phones, the wired WAN for the centers, and LTE-M and NB-IoT only in the assumptions register. Optional SMS fallback for alerts and network time at each connection depend on the operator service and not on a named generation, and the modem selection must keep them working on 4G.

## 10. Pending confirmations

| Pending | Who confirms | What cannot be said until then |
|---|---|---|
| List of the pilot farms with municipality, vereda and coordinates | Federation | Coverage at any farm, and the share of farms with each operator |
| Operators that the Federation already uses or contracts, and whether an IoT or multi-operator SIM is acceptable | Federation | Which operator rows apply |
| LTE-M or NB-IoT enabled, covered, sold as a plan and compatible with the device, per operator and municipality | Each operator, through the Federation | Whether these variants are usable |
| Modem model, bands, category and energy use | Specification of the autonomous node | Compatibility, autonomy and the cost of the plan |
| Official statements on the retirement of 2G and 3G for Movistar and WOM, and for Claro on 3G | Each operator | Any statement about those operators beyond the site counts |
| Whether the notice rule covers lines of IoT devices, and the current text of the rule | Federation legal advice, with the regulator | To whom a notice is owed and how soon |
| Signal at each farm and high point, with a field measurement and a SIM test | Installer | Coverage at the place |
| Support for LTE on the phones of farmers | Federation | Delivery of alerts by mobile push |

## 11. Sources and how they were read

All sources were consulted on 9 and 10 November 2026.

| Source | Publisher | Published or period | Used for | Limits |
|---|---|---|---|---|
| Reply to a public request on the retirement of 2G and 3G, signed 10 February 2026 | CRC | 10 February 2026 | No national schedule, operator decides, notice rule, Tigo has no 2G sites | A general opinion with no schedule in it |
| Reply to a public request on the retirement of 2G and 3G, signed 17 January 2025 | CRC | 17 January 2025 | Same position, and the fall of 2G sites of Claro and Movistar in three years, in a report of 13 December 2024 with data to the second quarter of 2024 | The report itself was not opened |
| Data Flash on mobile infrastructure, 2025 edition 009 | CRC, Postdata | Published 26 June 2025, data at 31 December 2024 | National figures, which this document does not mix with the later periods | National, and no figure for the three departments was read in it |
| Infrastructure of mobile access networks, file F3 | CRC, Postdata | Data to 2026 second quarter, file modified 16 September 2026 | Sites by operator and technology | No license is stated on the dataset page. Reports of the operators |
| Coverage of mobile services, file 1T 2023 to 4T 2025 | CRC, Postdata | Data to 2025 fourth quarter, file modified 6 May 2026 | Coverage of populated centers | Signal levels not defined. Populated centers only |
| Resolution CRC 5050 of 2016, article 5.1.1.3.8, as restated by Resolution CRC 6890 of 2022 | MinTIC normograma compilation | Read 10 November 2026 | Notice of six months | A reference copy, validity to confirm in the official publication |
| Circular CRC 156 of 2024 | CRC | 2024 | Confirms that operators report coverage maps each quarter and that 5G is included from the report of 2024 second quarter | The attached instructions were not in the file read |
| Page on the end of 2G | Claro | 6 October 2022 | Announcement with no date | Old |
| Help article on the 2G switch-off | Tigo | Undated | 2G switched off on 1 November 2022 | Undated page |
| Business page on managed machine lines | Movistar | Page with an offer valid in June 2023 | The service is offered and the radio technologies are not named | No technology confirmation |
| Movistar page on the 2G switch-off, Tigo page on managed connectivity, WOM site, the Claro business pages on IoT and the GSMA page on mobile IoT | Operators and GSMA | | Not read | Access errors, no connection, or not opened |
