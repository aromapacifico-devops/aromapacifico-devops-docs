# LoRa path of the farms out of coverage

This document defines how a farm with no cellular signal sends its readings to the platform over LoRa and a gateway shared by the vereda. It covers the regulation and the radio parameters that apply and what is still unverified, the versioned frame and its size budget, identity, sequence and restarts, duplicates, order and gaps, the meaning and the limits of the acknowledgement, the time of a reading, the configuration of the node, the behavior of the gateway and of its link, the expected delivery time, and the conditions that need a site study. The solution is not ready for deployment. Section 4 states the radio items that remain pending and why.

The decision to use a shared LoRaWAN gateway for readings and a data mule for objects is already recorded in the [out-of-coverage decision](../adr/out-of-coverage-connectivity.md). The [autonomous farm node specification](../iot/autonomous-node.md) fixes the node, its buffer, its clock and the interface of the radio module. This document completes the LoRa side of that interface.

## Contents

Part A. The link and its reliability

1. Terms
2. The link alternatives
3. What is reused
4. Regulation, radio parameters and compatibility
5. The versioned frame
6. Size budget
7. Identity, sequence, order and gaps
8. Time of a reading
9. The acknowledgement
10. Configuration of the node

Part B. The gateway and the site

11. The gateway
12. Delivery time
13. Cost
14. Site study
15. Calculations and their limits
16. Assumptions and pending confirmations
17. Sources

---

## 1. Terms

| Term | Meaning in this document |
|---|---|
| Node | The enclosure on the farm with controller, LoRa module, probes, buffer and solar kit |
| Gateway | The radio station of the vereda that receives frames and relays them to the network server over a cellular link |
| Network server | AWS IoT Core for LoRaWAN, which manages devices and gateways and hands uplink messages to the platform |
| Uplink and downlink | A message from the node to the platform, and from the platform to the node |
| Class A | A device that listens for a downlink only in short windows right after one of its own uplinks |
| Data rate | A combination of spreading factor and bandwidth, named DR0 and onward in the regional parameters |
| Time on air | The time a frame occupies the radio channel |
| Dwell time | The longest time one transmission may stay on one channel, where a rule sets it |
| Sequence | A counter that numbers each reading of a node |
| Epoch | A counter that changes when the sequence of a node cannot continue |
| Cumulative acknowledgement | A message that tells the node that all readings up to a sequence are stored |

## 2. The link alternatives

| Option | No new base station | No weekly visit | Result |
|---|---|---|---|
| Shared LoRaWAN gateway at a high point with cellular signal | The gateway is the equipment of the project and uses the existing operator network for its backhaul, and no base station of an operator is added | Nodes send on their own every hour, with a buffer of 24 hours | Adopted, as already decided |
| Satellite modem on each farm | Met | Met | Discarded for the pilot because of the hardware and fee per farm, as already decided |
| Data mule alone for readings | Met | Not met, since a reading would wait for a person | Discarded for readings. It remains the way objects travel |

The shared gateway reaches the farms only if the site study shows line of sight or an acceptable path from each farm to the high point. This document claims no range.

## 3. What is reused

| Item | Where it is defined |
|---|---|
| Hourly cycle, 24 hour buffer, `dropped_total`, sequence, order and duplicates | [Farm connectivity](farm-connectivity.md) and [Sensors and operation](../iot/sensors-and-operation.md) |
| The node, its real-time clock, the radio interface contract, the identity of a LoRa node and the options for its firmware update | [Autonomous farm node specification](../iot/autonomous-node.md) |
| Mobile networks for the backhaul of the gateway | [Mobile network validity](mobile-network-validity.md) |
| Large objects from the drone never use LoRa and travel with the brigade, then over HTTPS | The drone design of the platform, which this document does not repeat |
| Compact binary frame, decoder before the queue, billing per LoRaWAN message | [Telemetry ingestion](../iot/telemetry-ingestion.md) |

## 4. Regulation, radio parameters and compatibility

Four different things decide whether a radio configuration can be used, and none of them proves the others.

### 4.1 Regulation in force in Colombia

| Source | What it says | Limit |
|---|---|---|
| Resolution 000028 of 2026 of the national spectrum agency, 26 January 2026, in the Official Gazette 53,390 of 6 February 2026, as compiled by the ministry | Updates the national table of frequency allocations for 902 to 928 MHz. It shows 915 to 928 MHz allocated to the fixed, amateur, mobile except aeronautical mobile and radiolocation services. Its considerations describe the 915 to 928 MHz segment as the one enabled for free use devices | An allocation table. It sets no emission limit |
| Resolution 105 of 2020 of the national spectrum agency, title 4 on free use, in the compilation of the agency | Annex 1 sets the bands, the emission limits and the technical and operational conditions for free use. Use within them needs no permit. Devices must follow the technical standards that the communications regulator sets, or hold homologation certificates where that applies. Free use may not interfere with primary or secondary services and has no protection against interference | The compilation does not state its consolidation date and lists changes up to 2024. Changes after that date may exist |
| The same compilation, Annex 1, section 3.6 on frequency hopping, digital modulation and hybrid devices, for 915 to 928 MHz | Frequency hopping devices with a hop channel bandwidth at 20 dB below 250 kHz must use at least 50 hop frequencies and keep the average occupancy of any frequency to 0.4 seconds in 20 seconds. With 250 kHz or more, at least 25 hop frequencies and 0.4 seconds in 10 seconds. The widest hop channel is 500 kHz. Digital modulation devices must have a bandwidth at 6 dB of at least 500 kHz. The conducted output power may not exceed 1 W for devices with at least 25 hop channels, 0.25 W for 13 to 24 hop channels and 1 W for digital modulation, reduced by the amount by which the gain of a directional antenna exceeds 6 dBi. Out of band emissions must be 20 dB below the in band level | The text of the annex. It is not a conformity opinion |

The texts give a conducted power limit and conditions that depend on how a device is classified, and they do not say how a LoRa device is classified. A LoRa uplink on a 125 kHz channel is not a digital modulation device in the sense of a 6 dB bandwidth of 500 kHz. It could meet the rule for frequency hopping devices only if it uses at least 50 hop frequencies and keeps the average occupancy of each frequency under the limit, which in practice means a dwell time of 0.4 seconds per transmission. A 500 kHz uplink channel, as in DR6, is nominally at the bandwidth that the digital modulation rule asks for, and whether its real bandwidth at 6 dB reaches 500 kHz is not shown. The agency studied LoRa in a report on smart meters and lists the AU915-928 and US902-928 band plans among those used in the world, and the report does not state which plan a Colombian device must use. Whether the homologation of the communications regulator applies to a LoRa module under free use was not found, and the available text refers it to the regulator.

The conducted power limit of 1 W and the existence of the 915 to 928 MHz free use band are read in official texts. Whether a given LoRaWAN configuration complies, and whether homologation is required, are not settled, and a conformity opinion of the agency, of the regulator or of an accredited laboratory is needed. This document therefore chooses no frequency, no power and no transmission limit.

### 4.2 Parameters of the LoRa Alliance

The regional parameters document RP002-1.0.2 of 2020 lists Colombia with 915 to 928 MHz under the AU915-928 plan, and with 433 to 434.79 MHz under the EU433 plan. An older revision, 1.0.3 revision A, lists Colombia with 902 to 928 MHz under AU915-928 and US902-928. The revisions differ, and the revision that a gateway, a module and the network server implement must be confirmed.

The AU915-928 section gives, among other things, the following, and none of it is a Colombian rule.

| Item | Value in RP002-1.0.2 |
|---|---|
| Data rates for uplink | DR0 to DR5 on 125 kHz with spreading factors 12 to 7, and DR6 on 500 kHz with spreading factor 8 |
| Default maximum EIRP | 30 dBm, which the network server may change |
| Uplink dwell time | May be 400 ms where the local regulation requires it. With that limit DR0 and DR1 are not allowed and the payload limits fall |
| Time between uplinks with the dwell limit | 20 seconds are recommended |
| Downlink dwell time | No limit |

The maximum application payload depends on the data rate and on the dwell time setting. It is 51 bytes at DR0 to DR2 without the limit, and with the 400 ms limit it is not allowed at DR0 and DR1, 11 bytes at DR2, 53 bytes at DR3 and 125 bytes at DR4. These figures are for the case with no MAC commands in the options field, and the repeater compatible tables are used here. The figure of 242 bytes that appears in other tables is not a limit that applies to every data rate.

### 4.3 What AWS supports

AWS IoT Core for LoRaWAN supports the bands EU863-870, US902-928, AU915 and AS923-1, follows the regional parameters of the LoRa Alliance and advises working with compliance teams for regulatory requirements. It supports devices of LoRaWAN 1.0.x and 1.1 in classes A, B and C, gateways that run LoRa Basics Station 2.0.4 or later, a queue of downlinks for each device, gateway management through a configuration and update service, and firmware updates over the air for devices. A downlink queued for a class A device waits for the next uplink. The documented limit of a queued downlink is 242 bytes. It is a limit of the queue, and the data rate in use sets its own limit.

### 4.4 Hardware

No gateway and no module is selected. Compatibility of a module and a gateway with the plan, with the revision of the regional parameters, with the network server and with the regulation needs their datasheets and certificates, and is pending.

### 4.5 Joint result

| Question | State |
|---|---|
| Is the 915 to 928 MHz band available for free use in Colombia | Read in official texts |
| What conducted power limit applies | 1 W for the classes read, with the antenna gain rule. Which class a LoRa device falls in is not settled |
| Which regional plan and which revision | Pending. The documents differ |
| Is the 400 ms dwell time needed | Possibly, by the frequency hopping reading. Not settled |
| Does a given module and gateway pair comply and hold a certificate | Pending |
| Does the network server support the plan, the functions and the downlink needed | Documented for the bands and the downlink queue. Not tested |

Until these items are settled the frame budget below is shown for the regimes that could apply, as a calculation with its conditions, and the solution is not declared ready for deployment. A calculated data rate or a calculated frame size is not an approval of that configuration.

## 5. The versioned frame

The node sends a compact binary frame that carries one or more readings, with a header that tells the platform which readings it holds. Integers are little endian. The decoder rejects a version it does not know.

| Field | Bytes | Meaning |
|---|---|---|
| version | 1 | Layout of the frame. This is version 1, and 0 is reserved |
| flags | 1 | Bits 0 and 1 give the clock status, 0 synchronized in the last 24 hours, 1 running on the real-time clock for more than 24 hours since synchronization, 2 no valid time, 3 reserved. Bit 2 says that the node holds more records after this frame. Bit 3 says that the last configuration received was rejected. Bits 4 to 7 are reserved and zero |
| epoch | 1 | Changes when the sequence cannot continue, see section 7 |
| first_seq | 4 | Sequence of the first record of the frame. The other records follow in order |
| count | 1 | Number of records in the frame |
| held_before | 2 | Number of records older than the first one of the frame that the node still holds as pending. Records older than the oldest pending one are no longer in the node, because they were confirmed or because they expired |
| dropped_total | 2 | Records that the node deleted because they were 24 hours old, counted since the node started, saturating at 65535 |
| config_version | 1 | Version of the configuration that the node has applied, 0 for the factory configuration |
| frame_time | 4 | Time of the node clock when it sent the frame, in seconds since 1 January 1970 UTC, and 4294967295 when the clock has no valid time |
| base_capture | 4 | Time of capture of the first record, same unit, and 4294967295 when unknown |

A record starts with a type byte, 0 for a cultivation record and 1 for a drying record, and a time offset of two bytes. The offset is the number of minutes between the capture of the first record of the frame and the capture of this record, and 65535 is reserved as invalid. When the clock has no valid time, the offset of each record is instead the number of minutes before the send time at which it was captured, counted on the monotonic counter of the node, see section 8.

| Value | Unit | Encoding | Reserved for absent or invalid |
|---|---|---|---|
| Nitrogen, phosphorus, potassium | The unit that the probe states, fixed by the frame version | Unsigned 16 bit | 65535 |
| Soil pH | pH times 100 | Unsigned 16 bit | 65535 |
| Soil humidity, air humidity, grain humidity | Percent times 10 | Unsigned 16 bit | 65535 |
| Soil temperature, air temperature, grain temperature | Degrees Celsius times 10 | Signed 16 bit | 32767 |

A cultivation record holds the three nutrients, the pH, the soil humidity, the soil temperature, the air humidity and the air temperature, in that order, and a drying record holds the grain temperature and the grain humidity. The nutrient unit and the exact range depend on the probe, which is not selected, so this field is fixed when the probe is known and before the first frame version is released.

The frame has no node identifier. The network server delivers the identifier of the wireless device with each uplink, and the platform maps it to the node. The name of the wireless device is the identifier of the node, set at provisioning.

The decoder rebuilds the JSON message that the ingestion design already defines, with the node identifier from the device, the sequence as first_seq plus the position of the record, and the time of capture as described in section 8. It marks the quality of the clock and the version of the frame in the message. A frame that does not decode goes to the dead letter queue with its raw bytes.

## 6. Size budget

None of the rows below is a configuration approved for Colombia. The classification of LoRa under the national regulation is pending, and so are the regional plan, the dwell time setting and the compatibility of the hardware. The tables show what the regional parameters would allow under each regime, as inputs for the radio tests and the site study. What may be used depends on the pending items of section 4. The real budget depends on the regional plan, the data rate, the dwell time setting, the overhead of the protocol and the control commands. The tables below use the data rates and payload limits of the AU915-928 section of RP002-1.0.2 as inputs, for the two dwell time regimes, and are not a statement that this plan is allowed or usable in Colombia.

Header of 21 bytes, cultivation record of 19 bytes and drying record of 7 bytes. The overhead of LoRaWAN on air is 13 bytes, which are the message header, the device address, the frame control, the frame counter, the port and the integrity code. The control commands that the network server may add in the options field of an uplink take up to 15 bytes of the payload, which the last column reserves.

| Data rate | Spreading factor and bandwidth | Largest application payload, no dwell limit | Largest, 400 ms dwell limit | Cultivation records in a frame, no dwell limit | Drying records in a frame, no dwell limit | Cultivation records, dwell limit | Drying records, dwell limit | Cultivation records, no dwell limit and 15 bytes reserved for MAC commands |
|---|---|---|---|---|---|---|---|---|
| DR0 | SF12 / 125 kHz | 51 B | not allowed | 1 | 4 | none | none | 0 |
| DR1 | SF11 / 125 kHz | 51 B | not allowed | 1 | 4 | none | none | 0 |
| DR2 | SF10 / 125 kHz | 51 B | 11 B | 1 | 4 | 0 | 0 | 0 |
| DR3 | SF9 / 125 kHz | 115 B | 53 B | 4 | 13 | 1 | 4 | 4 |
| DR4 | SF8 / 125 kHz | 222 B | 125 B | 10 | 28 | 5 | 14 | 9 |
| DR5 | SF7 / 125 kHz | 222 B | 222 B | 10 | 28 | 10 | 28 | 9 |
| DR6 | SF8 / 500 kHz | 222 B | 222 B | 10 | 28 | 10 | 28 | 9 |

The regime with a 400 ms dwell limit is a scenario that was calculated because one reading of the regulation could lead to it. It is not shown to apply, and it is not a configuration for Colombia. If it did apply, DR0 and DR1 would not be allowed and DR2 could not carry even one record with this header, so only DR3 and faster rates would be usable, with one cultivation record in a frame at DR3. Those rates have a smaller link margin than the slowest ones, so the range that a long spreading factor gives would not be available. This is a condition to check in the site study, and it states no range.

Time on air of a full frame, from the formula of the radio manufacturer.

| Data rate | Frame size, no dwell limit | Time on air | Frame size, dwell limit | Time on air |
|---|---|---|---|---|
| DR0 | 51 B application, 64 B on air | 2.793 s |  | not allowed |
| DR1 | 51 B application, 64 B on air | 1.561 s |  | not allowed |
| DR2 | 51 B application, 64 B on air | 0.698 s | 11 B | 0.371 s |
| DR3 | 115 B application, 128 B on air | 0.677 s | 53 B | 0.390 s |
| DR4 | 222 B application, 235 B on air | 0.656 s | 125 B | 0.400 s |
| DR5 | 222 B application, 235 B on air | 0.369 s | 222 B | 0.369 s |
| DR6 | 222 B application, 235 B on air | 0.164 s | 222 B | 0.164 s |

The self test of the script checks that the time on air formula of the radio manufacturer reproduces the 400 ms payload limits that the regional parameters give for DR2, DR3 and DR4.

Drain of one day of readings after an outage of 23 hours, with the attempt window of 120 seconds of the cellular path used as a reference, and the spacing between uplinks of each regime.

| Case | Data rate | Regime | Frames | Total time on air | Time to send all frames | Fits in the window |
|---|---|---|---|---|---|---|
| Crop only, 6 readings | DR2 | no dwell limit | 6 | 3.70 s | 3.7 s | yes |
| Crop only, 6 readings | DR2 | dwell limit | no record fits | | | |
| Crop only, 6 readings | DR3 | no dwell limit | 2 | 1.03 s | 1.0 s | yes |
| Crop only, 6 readings | DR3 | dwell limit | 6 | 1.97 s | 102.0 s | yes |
| Crop only, 6 readings | DR4 | no dwell limit | 1 | 0.43 s | 0.4 s | yes |
| Crop only, 6 readings | DR4 | dwell limit | 2 | 0.56 s | 20.6 s | yes |
| Crop only, 6 readings | DR5 | no dwell limit | 1 | 0.24 s | 0.2 s | yes |
| Crop only, 6 readings | DR5 | dwell limit | 1 | 0.24 s | 0.2 s | yes |
| Crop and drying, 30 readings | DR2 | no dwell limit | 12 | 8.13 s | 8.1 s | yes |
| Crop and drying, 30 readings | DR2 | dwell limit | no record fits | | | |
| Crop and drying, 30 readings | DR3 | no dwell limit | 3 | 2.03 s | 2.0 s | yes |
| Crop and drying, 30 readings | DR3 | dwell limit | 12 | 4.31 s | 224.3 s | no |
| Crop and drying, 30 readings | DR4 | no dwell limit | 2 | 0.99 s | 1.0 s | yes |
| Crop and drying, 30 readings | DR4 | dwell limit | 3 | 1.14 s | 41.1 s | yes |
| Crop and drying, 30 readings | DR5 | no dwell limit | 2 | 0.56 s | 0.6 s | yes |
| Crop and drying, 30 readings | DR5 | dwell limit | 2 | 0.56 s | 20.6 s | yes |

The window of 120 seconds is a reference taken from the cellular path and is not a rule of LoRa. A drain that does not fit in one window continues in the next cycles, since the pending records stay in the node until they are acknowledged or expire.

A shorter header for the continuation frames of one drain would fit more records in a dwell limited frame. It is possible in a later version of the frame and is not part of version 1.

## 7. Identity, sequence, order and gaps

| Item | Rule |
|---|---|
| Identity | The network server identifies the node by its device identifier, and the platform maps it to the node identifier. The frame does not carry it |
| Sequence | Each record of a node has a sequence number of 32 bits that grows by one. After a restart with an intact log, the node continues from the last record in its log, in the same epoch, as the buffer rules already say. A restart with a lost log starts a new epoch |
| Epoch | If the log is lost and the sequence cannot continue, the node starts a new epoch with sequence 1. The platform keys a record by node, epoch and sequence. When it sees a higher epoch, it closes the previous one. A sequence of the closed epoch that it never stored is counted as lost, since the node can no longer send it, and the acknowledgement queued for the old epoch is removed. A frame of a lower epoch that arrives late is stored and is not acknowledged. The epoch counter has 8 bits, and after 256 changes the platform treats the node as replaced |
| Duplicates | The platform stores a record once, by a conditional write keyed by node, epoch and sequence. A repeat is accepted and ignored |
| Order | Frames can arrive in any order and a record is stored by its key. The platform does not rely on arrival order. The alert state keeps the existing rule of the newer reading |
| Gaps | A sequence that the platform does not hold is in one of three states. It is open, which means in flight or lost, if it is not older than the oldest record that the node reports holding. It is declared expired, if it is older than that and was never stored, because the node deleted it at the 24 hour limit. It is stored. The field `held_before` of each frame gives the oldest record that the node holds, and so separates the first two states |
| Counting losses | The platform counts as lost the sequences that it declared expired and never stored. It does not rely on `dropped_total` alone, since a record that the platform stored and that the node deleted at 24 hours, because the acknowledgement did not arrive, is counted by the node as dropped and is not lost |

## 8. Time of a reading

Four things are kept apart, and the platform stores them separately.

| Time | What it is | Where it comes from |
|---|---|---|
| Time of capture | When the probe was read | The real-time clock of the node, as a base time and an offset in minutes per record. The requirement of a clock with backup power of the node specification stays |
| Time of transmission | When the node sent the frame | The clock of the node, in `frame_time` |
| Time of reception | When the platform received the frame | The platform, from the message that the rule receives. This is the time at which the message reached the platform and is later than the transmission by the latency of the gateway, of its link and of the network server, which is not known |
| Quality of the clock | How far the time of capture can be trusted | The clock status of the frame, and the difference between the time of transmission and the time of reception |

The age of a record, the time of transmission minus the time of capture, is a complementary field that the platform derives. It is not a substitute for the time of capture. The platform compares the time of transmission with the time of reception, flags a frame whose clock differs from the platform by more than a threshold, and keeps the existing rules for a reading ahead of the platform clock or far behind it. The difference includes the delay of the radio path, so the threshold must leave room for it, and its value is to measure.

Recovery of the time. After a restart the real-time clock on backup power keeps the time. If the clock is lost, the node reads on schedule and stores the monotonic counter of its readings, as the cellular path does, and sends the offset of each record as the minutes before the send time, with the clock status 2. The platform then estimates the capture as the reception time minus that offset, marks the estimate as low quality and does not present it as a measured time. The node recovers its clock when a time synchronization is available. Which synchronization the network server supports over LoRa is not verified. The LoRaWAN specifications define a MAC command for the time and an application layer clock synchronization, which the network server documents for its firmware update service. A coarse time in the downlink of the platform would be stale by the time the downlink waited in the queue, so it cannot give a precise time.

## 9. The acknowledgement

The node sends its frames without asking for a confirmation of each one. The platform acknowledges readings with one cumulative message that it emits after the readings are stored.

### Three states of a reading

A reading that the node produced is in one of three states, and only the first one means delivery.

| State | Where the reading is | What it means | Delivered |
|---|---|---|---|
| Persisted and confirmed | The platform stored it, and an acknowledgement told the node, which deleted its copy | The platform has the reading | Yes |
| Pending | In the node, younger than 24 hours, not yet covered by an acknowledgement. The platform may or may not have it | Unknown to the node | Not known |
| Expired | Deleted by the node when it reached 24 hours with no acknowledgement. The node counts it in `dropped_total` | The node gave up its copy. The platform may hold it if the frame arrived and the acknowledgement did not | No. It is not delivery, and the platform decides from what it stored |

The rule of retention has one exception that is stated here once. A pending reading stays in the node until it is confirmed, and the only case in which it leaves the node without a confirmation is the limit of 24 hours that the pilot sets, where it becomes expired. Expiry is a loss of the copy of the node, counted and visible, and it is never taken as delivery.

### What the acknowledgement says

The acknowledgement has two values for a node and an epoch. The first is the declared floor, the oldest sequence that the node reported holding as pending in the last frame the platform used. Sequences below the floor are not covered by the message. They were confirmed earlier or they expired, and the platform keeps for each of them whether it stored it or declared it expired. The second is the persisted limit, the largest sequence such that every sequence from the floor to it is stored by the platform. The message therefore tells the node that the records from the floor to the persisted limit are stored, and it does not tell it that everything numbered below the limit was delivered.

| Step | Rule |
|---|---|
| Emission | After a write is confirmed by the readings table, the platform computes the floor and the persisted limit for the node and the epoch. If the persisted limit grew, it replaces the acknowledgement waiting for the node and queues the new one. The acceptance of a request to send a downlink by the network server, the acknowledgement of a radio frame by a gateway and the arrival of a frame at the network server are not emission points |
| Content | The version, the epoch, the declared floor and the persisted limit, 10 bytes, and no other data |
| Transport | A class A downlink, queued for the node and sent in the receive windows after its next uplink. The unacknowledged mode of the queue is enough, since the next uplink brings a newer acknowledgement |
| Use by the node | The node deletes the pending records from its oldest one up to the persisted limit, and no others. A pending record above a hole stays in the node, although the platform may already hold it, until the hole is stored or expires |
| Late, repeated or out of order acknowledgements | An acknowledgement of another epoch is ignored. One whose persisted limit is not higher than the highest one already applied is ignored. One whose persisted limit is beyond the last sequence that the node assigned is invalid and ignored. One for records that the node already deleted has no effect. After a restart with an intact log, the node applies an acknowledgement of its epoch as usual, since the stored records remain true |
| Restart and epoch | After a restart with an intact log nothing changes. If the log was lost, the node starts a new epoch, and the platform closes the old one, removes its waiting acknowledgement and counts its open sequences as lost |

### Loss and delay of the acknowledgement

The acknowledgement can be lost or arrive late, since it travels only after an uplink and the windows are short. The effect is that the node keeps records that the platform already has and sends them again, which the platform ignores and which the next acknowledgement covers. If no acknowledgement ever arrives, the node keeps its records until they expire, and the platform holds whatever frames arrived.

### Retry and airtime

The node does not repeat a frame in the same cycle. A record that was sent is not sent again before two cycles, since the acknowledgement of its first send is not known before the second cycle transmits. After that, the node resends the pending records, oldest first, up to the number of frames that fits in the attempt window of 120 seconds at the data rate in use, which section 6 calculates with the spacing between uplinks of the regime. The window of 120 seconds is taken from the cellular path as a reference and is not a rule of LoRa. A maximum number of sends for each record and a daily airtime budget are parameters that the radio tests set. The regulation read in section 4 sets a conducted power limit and, by one reading, a dwell time per transmission, and the regime that applies is pending. No duty cycle limit was found, and none is assumed.

### Expiry and the count of losses

Before each attempt the node deletes pending records of 24 hours or more, marks them as expired and adds them to `dropped_total`, with or without an acknowledgement. The platform may hold a record that the node counted as dropped. The true loss is the set of sequences that the platform declared expired and never stored, and the loss of a closed epoch, as section 7 says. `dropped_total` is therefore an upper bound.

### What the design does not guarantee

It does not guarantee that every reading arrives. A reading is lost if no frame carrying it reaches the platform within 24 hours, because of range, a collision, a gateway outage or a platform outage, and the node then discards it as expired. The design makes the loss visible and counted, keeps every pending reading until the limit of 24 hours and treats expiry as a loss and never as delivery.

### Is it viable

The downlink queue and the receive windows are documented for class A in the network server and in the regional parameters, and the size of the acknowledgement is far below any limit. The viability with the real plan, gateway and network server needs a radio test, and no such test was run.

## 10. Configuration of the node

The LoRa node has no shadow. The platform keeps the desired configuration, such as the drying flag, and sends it as a downlink. The node reports the version it applied. Three states are kept apart.

| State | Meaning | How it is known |
|---|---|---|
| Received | The downlink reached the node | Only by the node. The transport acknowledgement of the network server shows that the node answered at the radio level and does not show that the parameter was applied |
| Validated | The node checked the version and the values | The node rejects a message of an unknown version, a value out of range or a reserved bit that is not zero, and reports a rejection with a flag in the next frame |
| Applied | The node changed its behavior | The node reports the version it applied in the field `config_version` of its next frame |

| Item | Rule |
|---|---|
| Message | A downlink with a version, a configuration version, the values and the time at which the platform issued it, and fits in a few bytes |
| Versions | The configuration version grows by one. The node ignores a version lower than or equal to the one it applied, which also deduplicates a repeat |
| Expiry | The platform issued time lets a node with a valid clock ignore a message older than a limit. A node with no valid clock applies it, since it cannot judge its age |
| Pending state | The application shows a change as pending until the node reports the new version |
| Lost confirmation | The node reports its applied version in every frame, so a lost report is repaired by the next one. The platform requeues the configuration at every uplink until the reported version matches, up to an expiry after which the change is shown as failed to the operator |
| Separation | Configuration changes values that the firmware already reads. It does not change code, and the firmware update is a different mechanism with its own messages, see the node specification |

## 11. The gateway

The gateway is the radio station of the vereda, at a high point with cellular signal. Nodes in the field cannot reach the cloud without it.

| Item | Requirement |
|---|---|
| Software | A gateway that runs LoRa Basics Station 2.0.4 or later, as the network server requires |
| Backhaul | A cellular link under the decision on mobile networks. It does not depend on 2G or 3G, and the modem and the plan are chosen with the operator |
| Energy | Solar kit, sized from its real load, which the table below parameterizes. The gateway has no other supply |
| Identity | A certificate that the configuration and update service of the network server manages |
| Maintenance | Firmware of the gateway through that service, with the connectivity of its backhaul |
| Enclosure and mast | The environment requirements of the node specification, and a mast height that the site study sets |

Energy of the gateway, as a calculation with its load as a parameter, since the gateway is not chosen. It uses the same assumptions as the node energy budget, a usable share of 0.80 of the battery, 0.72 from panel to battery and 3 peak sun hours.

| Gateway load | Energy a day | Battery for 3 days with 0.80 usable, at 12.8 V | Battery for 5 days | Panel to stay level at 3 peak sun hours |
|---|---|---|---|---|
| 2 W | 48 Wh | 180 Wh, 14 Ah | 300 Wh, 23 Ah | 22 W |
| 5 W | 120 Wh | 450 Wh, 35 Ah | 750 Wh, 59 Ah | 56 W |
| 10 W | 240 Wh | 900 Wh, 70 Ah | 1500 Wh, 117 Ah | 111 W |

No documented behavior states whether a Basics Station gateway keeps the frames it receives while its link to the network server is down, and this design does not assume it does. The table gives the behavior when the cellular link of the gateway fails.

| What | Behavior |
|---|---|
| In the node | Keeps every record up to 24 hours and deletes none without an acknowledgement. Sends its frames at each cycle, and the gateway cannot relay them |
| In the gateway | Frames received while the link is down can be lost. The design does not depend on any being kept |
| In the platform | The network server reports the connection state of the gateway. An alarm reports a silent vereda, as already designed |
| Recovery | When the link returns, the next cycles of each node send the records that are still unacknowledged, and the platform stores them and acknowledges them. The drain time per node is in section 6 |
| Loss | A record is lost only if its frame never reaches the platform within 24 hours. The loss is counted from the gap in the stored sequences |

## 12. Delivery time

| Case | Expected delivery | Kind |
|---|---|---|
| Healthy link, a reading of the cycle | The node reads and then transmits in the same cycle. The reading reaches the platform after the time on air of the frame, the delay of the gateway and the network server, and the ingestion. The cloud part of the existing alert budget is about 96 seconds | The radio part and the delay of the gateway and the network server are to measure. The cloud part is a design value |
| Alert on that reading | The alert path of the platform adds its own steps. The total depends on the radio part, which is not measured | Not stated until measured |
| One frame lost | The platform does not see the reading, and the node does not know. The reading is sent again no earlier than two cycles after the first send, and only if the acknowledgement did not arrive, so a reading can be delayed by two hours or more | Calculation from the cycle |
| Gateway link down | The readings wait in the node up to 24 hours. After the link returns, each node drains in the next cycles. The delivery time is the outage plus one cycle plus the drain time | Calculation, with the drain from section 6 |
| Outage longer than 23 hours | The oldest records are deleted and counted. The alert for a deleted reading is not generated | Design rule |
| Objects | They travel by data mule, and their delivery time follows the route of the data mule | Defined by the drone design |

The expected delivery time of readings is therefore one cycle at most with a healthy link and a received frame, and up to 24 hours with an outage. The figures that depend on radio and network latency are marked to measure, and no latency is assumed.

## 13. Cost

The cloud bills each LoRaWAN message, and the farm pays no data plan of its own. The shared gateway carries the radio hardware and the only cellular plan of the vereda.

### Cloud

AWS IoT Core for LoRaWAN charges USD 0.000006 per message in us-east-1, which is USD 6 per million, from the AWS Price List API. The count below takes one uplink each hour, as section 15 assumes, and one downlink each hour for the acknowledgement as the worst case, since an acknowledgement is queued only when the persisted limit grows.

| Item | Per node a month | 40 nodes a month | Kind |
|---|---|---|---|
| Uplinks, one each hour | 720 | 28,800 | Calculation |
| Acknowledgement downlinks, at most one each hour | 720 | 28,800 | Calculation, worst case |
| Configuration downlinks | A few, when the drying flag changes | A few hundred | Estimate |
| Messages | About 1,440 | About 57,600 | Calculation |
| Cost at USD 6 per million | About USD 0.009 | About USD 0.35 | Calculation |

Firmware updates over the air bill per task, USD 0.006 each in the first 250,000, and no update is assumed in the monthly figure.

### Hardware and fee per farm

| Item | Cellular farm | LoRa farm | Shared by the vereda |
|---|---|---|---|
| Radio | Cellular module and antenna | LoRa module and antenna | |
| Data plan | One SIM plan per node | None | One cellular plan for the gateway |
| Gateway | None | None | Gateway, mast, antenna and the solar kit of section 11 |

The rest of the node, its probes, battery and panel, is the same on both paths. A LoRa farm therefore replaces the cellular module and its monthly plan with a LoRa module and its share of the gateway, which is the cost of the gateway, its kit and its plan divided by the farms in range. The prices of the modules, the gateway and the plans belong to the hardware estimate of one farm, and the number of farms per gateway comes from the site study.

## 14. Site study

A study of each vereda must record the following before a gateway is placed. It claims no range, and the first rows depend on the regime of section 4.

| Item | What is recorded | Who |
|---|---|---|
| Regulation and approval | The configuration of the radio, the certificates of the equipment and the opinion that section 4 needs | The agency, the regulator or an accredited laboratory |
| Data rates that the link must work at | The rates that the verified regime allows. DR3 or faster if a 400 ms dwell limit were to apply | Equipment supplier, with the datasheet sensitivity |
| Distance and line of sight | Distance of each farm to the high point, and obstacles on the path, with the terrain profile | Installer |
| Terrain and vegetation | Slopes, ridges and vegetation that block or reflect the signal | Installer |
| Mast and antenna | Height, antenna gain, cable loss, and the 6 dBi rule of the conducted power | Installer |
| Cellular signal at the gateway site | The signal quality of the operator measured at the mast, with a SIM test | Installer |
| Power at the site | The sun at the gateway, the shade and the real load of the gateway | Installer |
| Radio test | Real frames from each farm location at the intended data rate, with the success rate and the margin | Installer |
| Number of nodes per gateway | The real list of farms in range | Federation |

## 15. Calculations and their limits

The script `tools/lora_link_budget.py` prints every table of this document that comes from a calculation. It uses the data rates and the payload limits of RP002-1.0.2 as inputs, the time on air formula of the radio manufacturer, the layout of section 5, and scenarios for the number of nodes, the channels, the transmit power and the gateway load. The collision table uses pure random access with equal use of the channels, one spreading factor and no capture effect. Those are scenarios, and a simulation or a calculation does not replace a radio test in the field. The energy table counts only the time on air at a stated power and leaves out the receive windows and the controller.

Collision probability in the random access scenario, with one frame per node and hour.

| Data rate | Channels | Nodes | Load per channel | Probability that a frame collides |
|---|---|---|---|---|
| DR3, frame of 40 B, 0.329 s | 8 | 10 | 0.00011 | 0.023 percent |
| DR3, frame of 40 B, 0.329 s | 8 | 25 | 0.00029 | 0.057 percent |
| DR3, frame of 40 B, 0.329 s | 8 | 50 | 0.00057 | 0.114 percent |
| DR3, frame of 40 B, 0.329 s | 8 | 100 | 0.00114 | 0.228 percent |
| DR3, frame of 40 B, 0.329 s | 64 | 10 | 0.00001 | 0.003 percent |
| DR3, frame of 40 B, 0.329 s | 64 | 25 | 0.00004 | 0.007 percent |
| DR3, frame of 40 B, 0.329 s | 64 | 50 | 0.00007 | 0.014 percent |
| DR3, frame of 40 B, 0.329 s | 64 | 100 | 0.00014 | 0.029 percent |
| DR4, frame of 40 B, 0.185 s | 8 | 10 | 0.00006 | 0.013 percent |
| DR4, frame of 40 B, 0.185 s | 8 | 25 | 0.00016 | 0.032 percent |
| DR4, frame of 40 B, 0.185 s | 8 | 50 | 0.00032 | 0.064 percent |
| DR4, frame of 40 B, 0.185 s | 8 | 100 | 0.00064 | 0.128 percent |
| DR4, frame of 40 B, 0.185 s | 64 | 10 | 0.00001 | 0.002 percent |
| DR4, frame of 40 B, 0.185 s | 64 | 25 | 0.00002 | 0.004 percent |
| DR4, frame of 40 B, 0.185 s | 64 | 50 | 0.00004 | 0.008 percent |
| DR4, frame of 40 B, 0.185 s | 64 | 100 | 0.00008 | 0.016 percent |

Energy of the transmissions as a function of the transmit power, which is a scenario until a module is chosen.

| Data rate | Frame | Time on air | Power | Energy of a frame | 24 frames a day | Share of the daily ceiling |
|---|---|---|---|---|---|---|
| DR2 | 40 B | 0.616 s | 0.1 W | 0.017 mWh | 0.0004 Wh | 0.002 percent |
| DR2 | 40 B | 0.616 s | 0.3 W | 0.051 mWh | 0.0012 Wh | 0.005 percent |
| DR2 | 40 B | 0.616 s | 0.5 W | 0.086 mWh | 0.0021 Wh | 0.008 percent |
| DR3 | 40 B | 0.329 s | 0.1 W | 0.009 mWh | 0.0002 Wh | 0.001 percent |
| DR3 | 40 B | 0.329 s | 0.3 W | 0.027 mWh | 0.0007 Wh | 0.003 percent |
| DR3 | 40 B | 0.329 s | 0.5 W | 0.046 mWh | 0.0011 Wh | 0.004 percent |
| DR4 | 40 B | 0.185 s | 0.1 W | 0.005 mWh | 0.0001 Wh | 0.001 percent |
| DR4 | 40 B | 0.185 s | 0.3 W | 0.015 mWh | 0.0004 Wh | 0.002 percent |
| DR4 | 40 B | 0.185 s | 0.5 W | 0.026 mWh | 0.0006 Wh | 0.003 percent |

## 16. Assumptions and pending confirmations

| Item | Who confirms | Effect if it fails |
|---|---|---|
| Which class of the regulation a LoRa device falls in, and whether homologation applies | The national spectrum agency and the communications regulator, or an accredited laboratory, with the supplier test reports | No frequency, power or limit can be chosen, and the solution is not ready for deployment |
| Whether Annex 1 of the free use resolution was changed after the compilation read | The national spectrum agency | The conditions of section 4 change |
| Regional plan and revision implemented by the module, the gateway and the network server | Suppliers and the network server documentation | The payload limits and the data rates of section 6 change |
| Whether a dwell time of 400 ms applies | The conformity opinion above | If it applies, only DR3 and faster would be usable and the link margin falls. If it does not, the budget of the other regime applies |
| Support of the time synchronization over LoRa | The network server documentation or a test | The time of a node with a lost clock stays an estimate |
| Whether a Basics Station gateway keeps frames while its link is down | The Semtech documentation or a bench test | The loss during a backhaul outage may be larger, and the design already assumes it keeps none |
| Latency of the gateway, the network server and the ingestion | Measurement | The delivery times of section 12 stay unstated |
| Nutrient unit and range of the soil probe | Probe supplier | The frame version cannot be released |
| Nodes per gateway and the mix of data rates | Federation list and the site study | The collision and drain tables change |
| Objects other than drone objects that travel from these farms | Federation | A separate path may be needed |
| The sequence and the acknowledgement as designed hold with the real network server | A radio and network test | The reliability rules need a change before deployment |

## 17. Sources

| Source | Publisher and date | Used for | Limits |
|---|---|---|---|
| AWS IoT price list for us-east-1, offer AWSIoT | AWS Price List API, publication of 3 October 2026 | USD 0.000006 per LoRaWAN message and USD 0.006 per firmware update task | Prices change, and the offer is read at each estimate |
| Resolution 000028 of 2026 | National spectrum agency, 26 January 2026, Official Gazette of 6 February 2026, ministry compilation | Allocation table for 902 to 928 MHz and the statement on the enabled free use segment | An allocation table |
| Resolution 105 of 2020, title 4 and Annex 1, section 3.6 | National spectrum agency, compilation PDF of the agency and the ministry compilation of the text | Free use conditions, 915 to 928 MHz power limits and hopping and bandwidth rules, homologation clause | The compilation date is not stated. Later changes may exist. Not a conformity opinion |
| Impact analysis on free use spectrum for smart meters | National spectrum agency, undated | The agency lists the AU915-928 and US902-928 LoRa plans among those used in the world | Does not set a plan for Colombia |
| LoRaWAN Regional Parameters RP002-1.0.2 and v1.0.3 revision A | LoRa Alliance, 2020 and earlier | Colombia in the country table, AU915-928 data rates, payload limits, dwell time, default EIRP | They differ for Colombia. Not a Colombian rule |
| SX1276/77/78/79 datasheet, revision 4 | Semtech, March 2015 | Time on air formula | The extraction of the formula was garbled, and the self test checks it against RP002 |
| AWS IoT Core for LoRaWAN pages on the service, onboarding, profiles, frequency bands and the downlink queue | AWS documentation, read in November 2026 | Supported bands, versions, classes, Basics Station version, downlink queue and acknowledge mode | Documentation of a service. Not tested |
| LoRa Basics Station documentation pages read | Semtech | Station protocol, time synchronization messages | They do not say what the gateway does with frames while its link is down |
| Farm connectivity, sensors and operation, telemetry ingestion, the autonomous farm node specification, the mobile network validity | This repository | Approved rules and inputs | Design documents |
