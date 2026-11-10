# Autonomous farm node specification

This document specifies the farm node by requirements and classes of components. It states what the node does at the farm and at the drying site, which sensors and interfaces it needs, how its cycle, buffer and recovery work as requirements on the hardware, what the radio module must offer, how the energy balance and the solar kit are sized, what the enclosure must withstand, how the identity, the configuration and the firmware are protected, and the minimum list of materials for one farm. It is written so that a supplier can be asked to show compatibility and to quote, and it names no brand and no model.

The cellular variant is specified in full. The LoRa variant is specified only as far as the shared parts and the radio interface contract, and it stays incomplete until the design of the farms out of coverage defines its frame, its transmission limits and its configuration.

## Contents

1. How to read the statements
2. Function of the node
3. Requirements and the criteria they answer
4. Sensors and interfaces
5. Cycle, buffer and recovery as requirements
6. Radio module interface contract
7. Modem and radio alternatives
8. Energy balance and solar sizing
9. Environment
10. Identity, configuration and firmware
11. Cellular path and LoRa path
12. Minimum bill of materials and installation in one visit
13. Data in and out
14. Assumptions and pending confirmations
15. Sources

### Terms used

| Term | Meaning in this document |
|---|---|
| Node | The enclosure on the farm with controller, radio module, probes, buffer, battery and panel |
| Controller | The microcontroller that runs the cycle, owns the clock, the buffer, the identity and the configuration |
| Radio module | The cellular modem or the LoRa module. It carries messages and keeps none of the state of the node |
| Nominal capacity | The energy printed on the battery, 12.8 V times 12 Ah |
| Usable capacity | The part of the nominal capacity that the design allows to be drawn |
| Ceiling | The largest average daily draw that still gives the target autonomy. It is a limit and says nothing about what the node consumes |
| Peak sun hours | Hours a day at full solar output, a way to measure usable sun |
| Image | A firmware file that the controller can run |
| Manifest | The signed description of an image, with its version, its target hardware and its digest |

---

## 1. How to read the statements

Each table that states a value also states its kind, so that a figure from a source is not read as a measurement and a calculation is not read as a fact.

| Kind | Meaning |
|---|---|
| Source | Read in a published document, with its date in the list of sources |
| Design value | Fixed by an approved document of this design. It is an input and has not been measured |
| Calculation | Obtained from other values by an arithmetic that a script reproduces |
| Assumed | Taken for the design, and to confirm with a datasheet or a measurement |
| Pending | Not known today, with the party that confirms it |

Nothing in this document shows that a part exists, that a modem works on an operator, that a signal reaches a farm, or that the consumption of the node stays inside the budget. Those need datasheets, confirmations of the operators and measurements on the first nodes.

## 2. Function of the node

One node serves the cultivation zone and the drying site of a farm, with wired probes. This is already an assumption of the sensors design, and the site survey confirms it.

| Function | Detail |
|---|---|
| Measure cultivation | Soil nutrients, soil pH, soil humidity and temperature, air humidity and temperature, every 4 hours |
| Measure drying | Grain temperature and humidity, every hour while the farmer has a lot drying |
| Keep readings | Write each reading to an encrypted buffer before any attempt to send it |
| Send | Publish the buffer once an hour over the radio module, oldest first, with delivery confirmation |
| Receive configuration | Read the desired state, which today is the drying flag, after each drain |
| Keep time | Hold a real-time clock on backup power, and correct it from the network at each connection |
| Live on its own power | Run from a solar kit with no supply from the grid |
| Prove its identity | Hold a private key that never leaves the device, and a certificate for the platform |
| Be updated | Accept authenticated firmware updates, with recovery |

What the node does not do. It holds no alert ranges, which live on the platform. It does not decide what deserves an alert. It does not store readings beyond 24 hours. It does not route traffic for other devices.

## 3. Requirements and the criteria they answer

| Criterion of the story | Requirements that answer it | Section |
|---|---|---|
| Autonomous energy sized, with no reliable power supply | Usable capacity, ceiling, estimated consumption, solar generation and recovery, with sensitivity | 8 |
| Supports high humidity and temperature | Ingress protection, temperature and humidity requirements with what a supplier must show | 9 |
| Minimum list of materials per farm, installable in one visit | Classes of components with quantity and required specification, and the installation checklist | 12 |
| Specification sufficient to cost it and to receive and return data | Interfaces, supply, ranges, accuracy, consumption, communications, environment, data contract | 4, 6, 7, 13 |

This level of detail answers each criterion without naming a model. A quote still needs a model, and that belongs to the estimate of hardware that follows this specification.

## 4. Sensors and interfaces

### Probes

| Probe | Variables | Cadence | Required measuring range | Accuracy | Interface | Supply | Kind |
|---|---|---|---|---|---|---|---|
| Soil probe | Nitrogen, phosphorus, potassium, pH, soil humidity, soil temperature | Every 4 hours | At least the alert ranges, pH 4.5 to 6.0, humidity 40 to 80 percent, temperature 14 to 30 °C, and the range that the Federation publishes for nutrients | The supplier states it. It must be small against the narrowest alert band, and the Federation sets the accepted value | RS485 | Pending | Design values for the ranges. Pending for the rest |
| Climate sensor | Air humidity, air temperature | Every 4 hours | At least 40 to 80 percent and 14 to 30 °C | The supplier states it | Pending | Pending | Pending |
| Grain probe | Grain temperature, grain humidity | Hourly while drying | Temperature up to above 40 °C and humidity down to near 12 percent | The supplier states it | Pending | Pending | Design values for the ranges. Pending for the rest |

The measuring ranges come from the alert ranges of the sensors design. A probe whose range ends at an alert limit cannot show that the limit was crossed, so each range must extend beyond both ends of the band it serves. The width of that extension is a requirement for the supplier to meet and the Federation to set.

### What each probe must state before it is accepted

| Item | Why |
|---|---|
| Electrical interface and protocol, with the register map or the command set | The controller needs a driver, and the cost of the software depends on it |
| Supply voltage range and current in measurement and in idle | Sets the regulators and the energy of a reading |
| Time from power on to a valid reading | Sets how long the probe stays powered each cycle |
| Accuracy, resolution and drift over a harvest | Decides whether the alert ranges can be trusted |
| Operating and storage temperature and humidity ranges, and the ingress protection of the head and the cable | Must meet section 9 |
| Calibration needed for pH and how long it holds | A pending item of the sensors design |
| Cable length allowed and the cable type | Decides whether one node reaches both zones |

### Interface of the controller

| Item | Requirement | Kind |
|---|---|---|
| RS485 port | A transceiver for one differential bus with the probes on it. The standard for RS485 allows up to 32 unit loads on one bus, and a trade between cable length and speed, so the length of the run decides the speed | Source |
| Other probe ports | Ports for the interface classes that the climate sensor and the grain probe turn out to use | Pending |
| Switched probe supply | Each probe supply is switched by the controller, so the probes are powered only during a reading | Design value, from the cycle |
| Protection of field cables | Surge and electrostatic protection on every cable that leaves the enclosure | Design requirement |
| Debug and programming ports | Locked or disabled in the delivered node, see section 10 | Design requirement |
| Battery monitoring | A measurement of the battery voltage that the controller reads, which section 10 and section 13 use | Design requirement |

## 5. Cycle, buffer and recovery as requirements

The rules of the cycle, the buffer and the recovery are approved and described in the farm connectivity design. This section turns them into requirements on the hardware and repeats none of them differently.

| Rule already approved | Requirement on the node |
|---|---|
| One cycle each hour at a minute fixed for the node | A timer that wakes the controller with no external help, and a way to hold the minute across restarts |
| The reading reaches the flash before the radio powers on | Non-volatile storage that accepts a write in the first seconds of the cycle, with the controller powered |
| The buffer is an append-only log in encrypted flash, with a checksum on each record | Flash with encryption and a record format with a sequence number, the time, the values and a checksum |
| Records of 24 hours or more are deleted before connecting and counted in `dropped_total` | A counter that survives restarts, and a clock that is right before the purge |
| A record leaves the buffer only after its confirmation | Storage that supports deletion of confirmed records without rewriting the whole log |
| A flash record cut by a power loss is discarded | Detection by checksum, and a controller that continues the sequence from the last good record |
| Time comes from a real-time clock with backup power, corrected by the network or NTP | A clock that runs through sleep and brownouts, and a backup power that outlasts a main power loss by days |
| The attempt window is 120 seconds, and the next hour is the retry | A radio module that can be powered off completely at the end of the window, and a controller that does not wait on it |

Capacity does not limit the buffer. A busy day is about 15 KB against 64 MB of flash, so the size of the flash follows from the firmware images and their recovery copies and from wear, and the readings need little.

| Requirement | Value | Kind |
|---|---|---|
| Flash for the buffer and the images | At least 64 MB of external flash in the approved design | Design value |
| Flash wear | The supplier states the write endurance, and the design writes about 30 records a day | Pending, with a calculation once the part is known |
| Backup power of the clock | The supplier states the current and the time it holds with no main power | Pending |

## 6. Radio module interface contract

The radio module is a transport. The controller owns the clock, the buffer, the identity, the configuration and the decision of when to send. The contract below fixes what the controller can rely on, so that a cellular module or a LoRa module can be fitted with no change to the rest of the node. It is the part of the specification that the design of the farms out of coverage fills in for the LoRa side.

| Item | Contract | Cellular | LoRa |
|---|---|---|---|
| Supply | One supply rail for the module that the controller switches on and off. Voltage range and peak current are stated by the module supplier | Pending, with the module | Pending, with the module |
| Control | Power enable, reset, and a line to tell the controller that the module is ready or has failed | Defined | Defined |
| Data link | A serial link between the controller and the module | Defined | Defined |
| Registration | The module reports registered or not registered and the reason for a failure | Defined | Defined by the other design |
| Signal quality | The module reports a signal quality figure that the installer reads, with the unit stated by the module | Defined | Defined by the other design |
| Time | The module returns network time when the network provides it | Defined | Pending, since a LoRa network may provide it differently |
| Send | The controller hands the module a message and receives a result per message, delivered or failed | MQTT over TLS, with a confirmation per message | Frame format, size limit and confirmation are defined by the other design |
| Receive | The controller reads the configuration that the platform holds for the node | Device Shadow, as approved | Defined by the other design, since a LoRa node has no shadow |
| Power off | The module can be powered off with nothing to save, and it keeps no state that the node needs | Defined | Defined |
| Identity | The private key is held by the controller side or by a protected store, never exposed on the serial link | Section 10 | Section 10 |
| Version | The module reports its firmware version, and the controller can read it | Defined | Defined |
| Attempt limit | The controller ends an attempt at 120 seconds and powers the module off | Defined | Defined |

Where the secure connection is built, in the controller or in the cellular module, is not fixed. It decides where the private key lives and how much memory the controller needs, and it is one of the compatibility checks of section 7.

The LoRa variant is not complete. Its frame and its size limit, its transmission limits and the time it may spend on air, its configuration path and the way the node reports the counters of the buffer are still to be defined by the design of the farms out of coverage. This document does not fill them in.

## 7. Modem and radio alternatives

The decision on mobile networks applies. The design does not depend on 2G or 3G. LTE-M and NB-IoT are candidates once an operator confirms availability, coverage, the contracted service and the compatibility of the device. A conventional LTE category may be evaluated. No modem is approved by default and no model is selected here. The shared gateway follows the same rule for its backhaul, and the LoRa path of the farms out of coverage stays as approved.

| Criterion | LTE-M class | NB-IoT class | Conventional LTE class, such as a low category module | LoRa module |
|---|---|---|---|---|
| Bands and category supported by the operator | Pending with the operator and the module | Pending with the operator and the module | Pending with the operator and the module | Defined by the other design |
| Enabled by the operator and sold as a plan | Pending. No operator has confirmed it | Pending. No operator has confirmed it | Pending | Not applicable |
| Energy and autonomy | Power saving modes exist in the standards and the operator decides whether to offer them and with which timers | Same | A conventional category usually has fewer deep sleep options. This is to confirm with a datasheet | Defined by the other design |
| Protocols and capacity | MQTT over TLS of about 6 KB a connection and 30 readings a day must fit. The capacity of the class is to confirm with a datasheet | Same, and the capacity may be lower | Same | Frames are short and the message differs |
| Antenna, site and behavior with no signal | Antenna type and gain are chosen for the slope and the mast. The module must give up at 120 seconds | Same | Same | Same |
| Availability and cost of the plan | Pending | Pending | Pending | Not applicable |
| Status | Candidate. Not approved | Candidate. Not approved | May be evaluated. Not approved | Interface only |

What a supplier must show for a modem to be evaluated.

| Item | Why |
|---|---|
| Bands and categories of the module and the certificates it holds for the country | Compatibility with the operator and permission to sell it |
| Power saving modes supported, and the current in each state | Energy of a connection and of sleep |
| Measured energy of an attach and a publish, and the time they take | Replaces the assumed 1.5 W and the 45 and 120 seconds |
| Built-in secure connection and credential storage, or the memory needed to build it in the controller | Decides where the private key lives |
| Behavior with no network, and the time to give up | The 120 second window |
| Firmware update of the module itself | Section 10 |
| Antenna interface and the antenna that the supplier recommends | Site and mast |

The power saving modes of NB-IoT and LTE-M need the network to accept the timers that the device requests, and each operator decides what it offers. The sources found describe this, and the operators of the pilot have not confirmed their settings.

## 8. Energy balance and solar sizing

The approved kit is a 12.8 V and 12 Ah battery of the LiFePO4 type and a 20 W panel, for 5 days of autonomy with no sun. This section keeps that kit and checks whether it holds once the usable capacity is made explicit. The script `tools/node_energy_budget.py` prints every table of this section from its inputs.

### What is counted, and once

| Item | Where it enters |
|---|---|
| Nominal and usable capacity | The usable capacity factor applies to the battery only |
| Ceiling of the daily draw | Usable capacity divided by the days of autonomy, at the battery terminals |
| Conversion losses of the loads | Each load is stated at the battery terminals. A datasheet figure at a rail is converted once. The base case does not convert the modem figure, whose reference point is not stated |
| Margin | A separate allowance for the error of the consumption estimate |
| Panel derating and charge path | Applied once to the panel output to give the energy that reaches the battery |

### Battery and ceiling

| Quantity | Value | Kind |
|---|---|---|
| Nominal capacity | 153.6 Wh | Design value |
| Daily figure of the earlier documents | 30.7 Wh a day | Calculation. It divides all the nominal capacity by 5 days and so counts all of it as usable |
| Usable capacity | 122.88 Wh | Assumed. The factor is 0.80 |
| Ceiling of the daily draw for 5 days | 24.58 Wh a day, 1.02 W on average | Calculation. A ceiling and no estimate of consumption |
| Target for the estimated consumption with a 20 percent margin | 20.48 Wh a day | Calculation, margin assumed |

The 80 percent factor is a design assumption. Search results that summarize datasheets of several makers of 12.8 V LiFePO4 packs mention a recommended discharge depth of 80 percent and no charging below 0 °C, and none of them is the datasheet of the pack that this design will use. The datasheet of the chosen pack sets the real factor, and the low temperature charging limit.

### Consumption of the components

Only the modem has a figure in the approved design, and it is an assumed average power. The other components have no estimate until their datasheets exist.

| Case | Energy a day | Share of the ceiling | Kind |
|---|---|---|---|
| 24 connections of 45 s at 1.5 W | 0.45 Wh | 1.8 percent | Design value |
| 24 attempts of 120 s at 1.5 W, all failing | 1.20 Wh | 4.9 percent | Design value |
| Same worst case if 1.5 W is at the rail and the conversion is 0.85 | 1.41 Wh | 5.7 percent | Assumed |

The room left for everything else is a requirement for the other components, and says nothing about what they consume.

| Quantity | Value | Kind |
|---|---|---|
| Target for the estimated total | 20.48 Wh a day | Calculation |
| Worst case of the modem | 1.20 Wh a day | Design value |
| Room for the controller in sleep, probes, regulators and the radio idle | 19.28 Wh a day, 0.80 W on average | Calculation |
| Reading events a day with drying | 30 | Design value |
| Energy a reading event could take if it used all the room | 0.64 Wh | Calculation |

The controller, the probes and the regulators must show, with datasheets and then with measurements, an estimated total inside that room. A part list whose estimated total goes over it needs another design.

### Generation and recovery

| Quantity | Value | Kind |
|---|---|---|
| Panel | 20 W | Design value |
| Peak sun hours | 3 | Assumed in the approved design, to confirm with field data |
| Panel derating | 0.80 | Assumed |
| Charge path efficiency | 0.90 | Assumed |
| Energy reaching the battery on an average day | 43.2 Wh | Calculation |

Daily energy that reaches the battery from the panel, by peak sun hours and by the combined factor of derating and charge path.

| Peak sun hours | Combined 0.60 | Combined 0.72 | Combined 0.85 |
|---|---|---|---|
| 1.5 | 18.0 Wh | 21.6 Wh | 25.5 Wh |
| 2.0 | 24.0 Wh | 28.8 Wh | 34.0 Wh |
| 2.5 | 30.0 Wh | 36.0 Wh | 42.5 Wh |
| 3.0 | 36.0 Wh | 43.2 Wh | 51.0 Wh |
| 4.0 | 48.0 Wh | 57.6 Wh | 68.0 Wh |

Days to refill the usable capacity from empty after a spell with no sun, at the combined factor of 0.72, for three levels of average draw.

| Peak sun hours | Panel | Draw 25 percent of the ceiling (6.1 Wh) | Draw 50 percent of the ceiling (12.3 Wh) | Draw 100 percent of the ceiling (24.6 Wh) |
|---|---|---|---|---|
| 1.5 | 20 W | 8.0 days | 13.2 days | never |
| 2.0 | 20 W | 5.4 days | 7.4 days | 29.1 days |
| 2.5 | 20 W | 4.1 days | 5.2 days | 10.8 days |
| 3.0 | 20 W | 3.3 days | 4.0 days | 6.6 days |
| 4.0 | 20 W | 2.4 days | 2.7 days | 3.7 days |

Peak sun hours needed to stay level with a 20 W panel and the combined factor of 0.72 are 0.43 hours at a draw of 25 percent of the ceiling, 0.85 at 50 percent and 1.71 at 100 percent.

### Is the sizing viable

Under the stated assumptions the kit is viable on one condition. It holds if the real average draw stays well under the ceiling and the sun is not far below the 3 peak sun hours of the design.

- At 3 peak sun hours, a draw at the ceiling refills the battery in 6.6 days, and a draw of half the ceiling in 4.0 days.
- At 2 peak sun hours, a draw at the ceiling takes 29 days to refill, which does not recover between spells of bad weather. A draw of half the ceiling takes 7.4 days.
- At 1.5 peak sun hours, a draw at the ceiling never recovers, and a draw of half the ceiling takes 13 days.

Those results depend on four assumptions and on a consumption that has not been measured, so the sizing is not confirmed. It is confirmed when the datasheets of the components give an estimated total inside the room above, the pack datasheet confirms the usable factor, the real peak sun hours of the sites are known, and the first nodes measure their draw.

If those confirmations fail, the approved kit changes only after a decision. A 30 W panel is shown below as an alternative that this document does not adopt. A larger battery would raise the ceiling and lengthen the refill, and it is not tabulated.

| Peak sun hours | Panel | Draw 25 percent of the ceiling (6.1 Wh) | Draw 50 percent of the ceiling (12.3 Wh) | Draw 100 percent of the ceiling (24.6 Wh) |
|---|---|---|---|---|
| 1.5 | 30 W | 4.7 days | 6.1 days | 15.7 days |
| 2.0 | 30 W | 3.3 days | 4.0 days | 6.6 days |
| 2.5 | 30 W | 2.6 days | 2.9 days | 4.2 days |
| 3.0 | 30 W | 2.1 days | 2.3 days | 3.1 days |
| 4.0 | 30 W | 1.5 days | 1.7 days | 2.0 days |

With 20 W, a draw at the ceiling and 2.5 peak sun hours take 10.8 days to refill, against 4.2 days with 30 W.

## 9. Environment

The approved design names an IP67 enclosure and a battery and controller rated for the range. This section turns that into requirements and states what is not yet known.

| Condition | Requirement | Kind |
|---|---|---|
| Water and dust | An enclosure rated IP67, with the test report of the supplier. The code and its tests are defined in IEC 60529, whose listing says it classifies the degrees of protection that enclosures provide. The levels of each numeral were not read in this review | Design value. Source for the standard |
| Probes and cables | Heads and cables rated for burial or immersion where they are buried, with connectors of the same rating | Pending, with the probes |
| Ambient temperature | Operating and storage ranges of every component stated by the supplier and covering the extremes of the sites plus the rise inside a closed enclosure in the sun | Pending. Only mean temperatures were found |
| Humidity and condensation | A way to keep condensation from the electronics, such as a vent, a desiccant or a coating, with the supplier stating the rated humidity | Pending. No humidity data was retrieved |
| Battery temperature | The charging limit of the pack at low temperature, and its operating range, stated by the pack datasheet | Pending, see section 8 |
| Sunlight | Enclosure and cable sheaths rated for sunlight over the life of the node | Pending |
| Animals, tools and weather | Buried cable, mast height and a mast that resists wind | Design value, from the sensors design |

What was found. Coffee growing in Colombia lies between about 200 and 1,900 m, with over 90 percent of the crops between 600 and 1,800 m, where the mean air temperature is about 20 °C, and about 23 °C below 1,100 m, according to publications of the coffee research institute as summarized by a search. Those are mean temperatures and give neither the extremes nor the humidity. The requirement therefore stays open until the extremes and the humidity of the sites are known, and a supplier must state ranges that cover them.

## 10. Identity, configuration and firmware

The platform gives each node its own X.509 certificate, created from a request so that the private key stays on the device, with a policy limited to the resources of that node. A stolen or lost node is revoked. The flash of the controller is encrypted. This section adds how the identity is provisioned, how the key is protected, how the firmware is verified and updated, and how the cellular and LoRa variants differ.

### Provisioning of the identity

| Step | Requirement |
|---|---|
| 1 | The key pair is generated on the node, and the private key is not readable from outside |
| 2 | The node exports a certificate request, which the platform operator signs and registers for that node only |
| 3 | The certificate and the node identifier are written to the node, and the node reports its firmware version |
| 4 | The node is linked to a farm at installation, with no secret handled by the installer |

Two points to provision are possible.

| Point | For | Against |
|---|---|---|
| In a controlled place before shipment | A single visit at the farm with no special tool, and secrets handled by trained staff | The nodes must be linked to a farm later, and a stock of provisioned nodes needs control |
| At the farm during installation | The node is linked to the farm at once | The installer needs a tool and a connection at the lot, and the key generation happens in the field |

The proposal is the controlled place before shipment, and it is pending approval.

### Protection of the private key

| Requirement | Detail |
|---|---|
| Not extractable | The key is generated and used inside a protected store of the controller, a secure element or the cellular module, and never leaves it |
| Equivalent protections | If the part has no secure element, the controller must offer readout protection and flash encryption, and the choice must be justified in the datasheet and reviewed |
| No key on the serial link | The radio module never receives the private key, unless it is the protected store itself |
| Debug locked | Ports that read the memory are locked in the delivered node |

### Verified boot or an equivalent

The controller starts only firmware whose signature it has verified against a public key held in memory that cannot be rewritten. The stage that does the verification cannot be updated, or only with the same protection. An equivalent mechanism is accepted only when it stops an altered image from running and the supplier documents how. The image is authenticated and integrity protected, which is the first requirement of the update architecture for constrained devices, and confidentiality of the image is optional.

### Firmware update on the cellular path

| Requirement | Detail |
|---|---|
| Authenticated manifest | The manifest carries the version, the target hardware, the digest and a signature. The node checks the signature and the target before it installs anything |
| Where the image goes | A second slot or a recovery image, so that the running firmware is kept until the new one is confirmed |
| Download across cycles | The image arrives in parts over several cycles and resumes where it stopped, so that a weak signal does not restart it |
| Interrupted update | A power loss or a network loss at any point leaves a node that boots the previous image. This is a requirement of the update architecture |
| Compatibility | The node accepts an image only for its own hardware and only from a version it supports |
| Rollback | The node returns to the previous image if the new one fails to boot or fails to connect and report within a set number of cycles. A security version stops a rollback to an image known to be vulnerable |
| Confirmation | The node reports its version after it runs the new image, and the platform records it |
| Rollout | Nodes update in batches and not all at once, so that the load and the risk spread |

Constraints that bound the update.

| Constraint | Requirement |
|---|---|
| Battery | The node starts or continues an update only above a battery level that the design sets after the measurements. The level is pending |
| Connectivity | The update uses the connection of a normal cycle and ends at the 120 second window, with the rest on the next hour |
| Size | The image size is limited by the slot size and by the data cost, see below |
| Data plan | The base traffic is about 5.5 MB a month, and an update adds its image once for each version |

Cost of one update in energy, as scenarios. The throughput is a scenario and is not a claim about any technology, and the energy uses the assumed modem power of a connection.

| Image | Throughput | Transfer time | Modem energy | Share of the ceiling | Data |
|---|---|---|---|---|---|
| 256 KB | 10 kbps | 205 s | 0.085 Wh | 0.35 percent | 0.25 MB |
| 256 KB | 50 kbps | 41 s | 0.017 Wh | 0.07 percent | 0.25 MB |
| 256 KB | 200 kbps | 10 s | 0.004 Wh | 0.02 percent | 0.25 MB |
| 512 KB | 10 kbps | 410 s | 0.171 Wh | 0.69 percent | 0.50 MB |
| 512 KB | 50 kbps | 82 s | 0.034 Wh | 0.14 percent | 0.50 MB |
| 512 KB | 200 kbps | 20 s | 0.009 Wh | 0.03 percent | 0.50 MB |
| 1024 KB | 10 kbps | 819 s | 0.341 Wh | 1.39 percent | 1.00 MB |
| 1024 KB | 50 kbps | 164 s | 0.068 Wh | 0.28 percent | 1.00 MB |
| 1024 KB | 200 kbps | 41 s | 0.017 Wh | 0.07 percent | 1.00 MB |

The cloud side can use a job service that tells a device which file to fetch and records the result, together with a signing service for the images. Both are options noted here. Their design and their cost are outside this specification.

### Firmware update on the LoRa path

A full firmware update over LoRa is not assumed. The options below are viable candidates, and the design of the farms out of coverage decides among them with the measures in the last table.

| Option | What it needs | Open points |
|---|---|---|
| Update on site with a local link | A person with a programmer or a short range link at the farm, or at the visit of the carrier that moves the objects from those farms | Visit cost, and who is trusted to do it |
| Update over the air with the LoRa application layer specifications | Remote multicast setup, fragmented data block transport and clock synchronization, which AWS IoT Core for LoRaWAN documents for its devices. The nodes must listen at a scheduled time | Energy of the listening windows, the size of the image, the success rate with a shared gateway, and whether the specifications versions match the stack |
| Update of the parameters only | The configuration that the platform holds, sent as downlink | Does not replace a firmware fix |

| Measure to decide | Why |
|---|---|
| Image size and the number of fragments | Decides the session time |
| Energy of a session, with the listening windows | Compared with the ceiling of section 8 |
| Success rate and the cost of repeating a session | Decides if a fix reaches every node |
| Whether a key and a manifest can be checked with the memory of the LoRa node | Section 10 requirements still apply |

### Configuration

The cellular node reads its configuration from the Device Shadow, as approved, and reports what it applied. The LoRa node has no shadow, and its configuration path is defined by the design of the farms out of coverage. The installer needs a way to read the signal quality and the registration of the node during installation, and no secret is shown on a screen or left on a phone.

| Control | Requirement |
|---|---|
| Update events | The node records and reports the version it runs and the result of the last update |
| Revocation | Unchanged. The platform marks the certificate as revoked and the next attempt fails at the secure connection |
| Replacement | A replacement node gets a new key and a new certificate, and certificates are never reused |
| Theft | Encrypted flash, locked debug ports and revocation |

## 11. Cellular path and LoRa path

| Topic | Cellular | LoRa | Status of the LoRa side |
|---|---|---|---|
| Radio | Cellular module | LoRa module | Interface contract only |
| Message | JSON of about 0.5 KB per reading, over MQTT with TLS | Compact binary frame | Frame to be defined |
| Confirmation | Per message, from the broker | To be defined | To be defined |
| Configuration | Device Shadow | A path that needs no shadow | To be defined |
| Time | Network time, NTP as a fallback, real-time clock | Clock of the node, and the network may not give time | To be defined |
| Buffer and counters | Same rules, 24 hours, `dropped_total` | Same rules, and the counter must travel in the compact frame | To be defined |
| Energy of a transmission | Assumed 1.5 W for 45 to 120 seconds | To be measured with the module | To be defined |
| Firmware update | Section 10 | Options in section 10 | To be decided |
| Gateway | None. The node uses the operator network | A gateway shared by the vereda with a backhaul | Defined by the other design |

The LoRa variant is not complete while its frame, its transmission limits, its configuration and its update are undefined.

## 12. Minimum bill of materials and installation in one visit

The list gives classes, quantities and required specifications. It has no prices and no models.

| Item | Quantity | Required specification |
|---|---|---|
| Enclosure | 1 | Rated IP67 with a test report, with cable glands of the same rating, resistant to sunlight, with a way to keep condensation out |
| Controller board | 1 | RS485 port, ports for the other probes, a timer wake-up, a real-time clock with backup power, at least 64 MB of external flash with encryption, battery voltage measurement, switched probe supplies, protected field inputs, and the protections of section 10 |
| Radio module | 1 | Cellular module of a class of section 7 once confirmed, with its antenna, or the LoRa module of the other design |
| Antenna | 1 | Suited to the module, to the band and to the mast |
| Battery | 1 | 12.8 V LiFePO4, 12 Ah nominal in the approved design, with a battery management system, and the datasheet limits of section 8 |
| Solar panel | 1 | 20 W in the approved design, with a bracket and a cable of the rating of section 9 |
| Charge controller | 1 | Suited to the panel and to the battery, with the low temperature charging limit of the pack |
| Soil probe | 1 | The class of section 4, with its cable |
| Climate sensor | 1 | The class of section 4 |
| Grain probe | 1 | The class of section 4, with its cable to the drying site |
| Mast and fixings | 1 | Height and wind resistance as the sensors design requires |
| SIM or subscription | 1 | Only for the cellular variant, with the plan that the operator confirms |
| Cable and connectors | As the site requires | Ratings of section 9, lengths within what the probe interfaces allow |

The installation fits one visit with little equipment. The steps and the estimated times come from the sensors design and are validated on the first installations.

| Step | Action | Time |
|---|---|---|
| 1 | Fix the mast and the panel | 30 min |
| 2 | Bury the soil probe and fix the climate sensor | 20 min |
| 3 | Place the grain probe in the drying zone | 10 min |
| 4 | Power on, check the signal, the port that the operator allows and the first reading on the platform | 15 min |
| 5 | Link the node to the farm and show the application to the farmer | 25 min |

The node arrives assembled and provisioned. The installer carries the node, the mast, the panel and the probes, a way to read the signal quality and the registration of the node, and the fixings, with no special tool.

## 13. Data in and out

The node sends and receives what the connectivity and ingestion designs already approve. This section lists it so that the platform and the cost can be built from it, and it adds nothing to those designs.

| Direction | Content | Defined by |
|---|---|---|
| Out | One message per reading with the identifier of the node, the sequence number, the time of the reading, the variables of the zone and the checksum. About 0.5 KB | Farm connectivity and ingestion designs |
| Out | The running total of readings lost beyond 24 hours, `dropped_total`, with the next message | Farm connectivity design |
| Out | The reported state of the shadow | Farm connectivity design |
| In | The desired state of the shadow, which today carries the drying flag | Farm connectivity design |
| In and out | The messages of the firmware update, from the manifest to the result | Section 10 |

Two fields would help the platform and are proposed here, with nothing changed until the owners of those designs agree. They are the firmware version, which the update needs, and a battery measurement, which the energy monitoring needs. The tables of section 8 show why the battery measurement matters, since the real draw and the real sun are the two unknowns that decide the sizing.

## 14. Assumptions and pending confirmations

| Item | Who confirms | Effect if it fails |
|---|---|---|
| Usable share of the battery is 80 percent | Datasheet of the chosen pack | The ceiling moves in proportion, and the kit may need another battery |
| Panel derating of 0.80 and charge path of 0.90 | Datasheets and field measurement | Daily generation moves in proportion |
| 3 peak sun hours on an average day | Field data of the sites | Recovery after a spell with no sun lengthens, see section 8 |
| The 1.5 W modem figure and its reference point | Measurement with the chosen modem | The share of the ceiling changes |
| The estimated total of the other components stays inside the room of section 8 | Datasheets and then measurement | The kit or the components change |
| One node reaches the cultivation zone and the drying site with wired probes | Site survey | A second small node per farm |
| Interface, supply, power up time and accuracy of each probe | Probe supplier | Drivers, regulators and the accepted accuracy change |
| Operator support for the modem class, its bands and its power saving settings | Each operator, through the Federation | The modem class or the plan changes |
| Where the secure connection is built, in the controller or in the cellular module | Module supplier | Memory, key storage and energy change |
| Extremes of temperature and the humidity of the sites, and the rise inside the enclosure | Weather data and the enclosure supplier | The enclosure and component ranges change |
| Battery level below which an update does not start | Measurements of the first nodes | The update window shrinks |
| Provisioning in a controlled place before shipment | Team | The installer needs a tool and a connection |
| Firmware version and battery measurement added to the reported data | Owners of the ingestion design | The update and the energy monitoring have less data |
| Frame, transmission limits, configuration and update of the LoRa variant | Design of the farms out of coverage | The LoRa variant stays incomplete |

## 15. Sources

| Source | Publisher and date | Used for | Limits |
|---|---|---|---|
| A firmware update architecture for IoT devices, RFC 9019 | IETF, April 2021 | Authenticated and integrity protected images, a bootloader that can select valid firmware, devices that must not fail on a power or network loss during an update | Informational. It is an architecture and fixes no product |
| Foundational cybersecurity activities for IoT device manufacturers, NISTIR 8259A | NIST, December 2020 | Software update as a device capability, with verification and authentication before install, authorized rollback and authorized entities only | Capability baseline |
| AWS IoT Jobs and AWS IoT Core for LoRaWAN FUOTA documentation | AWS, read in November 2026 | Jobs that run firmware updates on devices, and FUOTA with multicast, fragmentation and clock synchronization based on the LoRa Alliance specifications | Documentation of a service. The versions of the specifications differ between pages |
| TI application notes on RS-485, as summarized by a search | Texas Instruments | Up to 32 unit loads and a trade between cable length and data rate | The notes were not opened in full. The figures must be checked in them before use |
| IEC 60529, product listing | IEC webstore | The IP code classifies degrees of protection of enclosures | Only the listing was read. The levels were not |
| Publications of the coffee research institute, as summarized by a search | Cenicafé | Altitude of the coffee area and mean air temperatures by altitude | Mean temperatures only. No extremes and no humidity |
| Datasheets of 12.8 V LiFePO4 packs of several makers, as summarized by a search | Makers | Recommended discharge depth of 80 percent and a charging floor at 0 °C in some of them | Not opened and not the pack of this design |
| PSM and eDRX descriptions of operators and of cellular connectivity providers, as summarized by a search | Providers | Power saving modes exist in LTE-M and NB-IoT and the network decides whether to accept the timers | Not the specifications. The operators of the pilot have not confirmed any setting |
| Farm connectivity, sensors and operation, telemetry ingestion, encryption, secrets and revocation, and the decision records on the node cycle and the farm module | This repository | Approved rules, design values and the security model | Design documents |
