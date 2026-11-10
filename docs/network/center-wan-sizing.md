# Center WAN and Wi-Fi sizing

This document sizes the link of a collection center and the demand on its access points. It takes the 100 Mbps symmetric link of the center, the reference rate per active client and the zones of the LAN, and it shows the load of the approved design scenario, a stress scenario and the case in which every client is active. It separates what the clients request from what the traffic classes allow, validates each direction of the link, sizes the reserve for the operation, calculates the synchronization of a drone on the uplink, defines the guarantees, caps and priority of each class by direction, and states the demand that each access point must serve. Each figure carries its origin, and every assumption has a sensitivity or an owner who confirms it.

The link stays at 100 Mbps, with priority for logistics and drone synchronization and a cap on visitors, as the decision on center WAN capacity sets. This document gives the values behind that decision and requires the link to be dedicated, with a committed rate, so that the guarantees of the traffic classes hold.

## Contents

1. Origin of each figure
2. Scenarios
3. Requested demand and allowed bandwidth
4. Validation against the link
5. Traffic of the operation and the reserve
6. Synchronization of the drone
7. Traffic classes by zone
8. Wi-Fi demand for each access point
9. Assumptions and pending confirmations
10. Cost of the link
11. Sources

### Terms used

| Term | Meaning in this document |
|---|---|
| Active client | A device that uses the network at the same moment as the others |
| Requested demand | What the active clients ask for at the reference rate |
| Capacity available | The line rate of the link, 100 Mbps in each direction |
| Allocated bandwidth | What the guarantees, caps and priority of the classes give to a class or a flow |
| Effective throughput | What a transfer really achieves, which is the allocated bandwidth times an efficiency below one |
| Guarantee | A rate that a class receives first when it asks for it |
| Cap | The most that a class can receive, even if the link is free |
| Lending | Use by another class of the part of a guarantee that its owner does not use, returned at once when the owner asks for it |
| Down and up | Toward the center and away from it |

---

## 1. Origin of each figure

| Figure | Value | Origin |
|---|---|---|
| Link | 100 Mbps symmetric per center, shared with the operation | Pilot definition |
| Type of link | Dedicated, with a committed rate in each direction | Requirement of this design, section 7 |
| Reference rate | 2 Mbps down and 0.5 Mbps up for each active client | Pilot definition |
| Clients by zone | Management 7, Support 7, Logistics 22, Transport 20, Visitors 10, total 66 | Collection center LAN |
| Simultaneous clients of the design | 40 | Decision on center WAN capacity |
| Priority | Logistics and drone synchronization first | Same decision |
| Cap of visitors | 10 percent of the link, 10 Mbps. The record does not name a direction, and this document applies it to both | Same decision, with the direction as an assumption |
| Sacks | Up to 400 a day in harvest | Pilot definition |
| Drone batch | 500 photos of 3 MB, 1.5 GB or 12,000 megabits, about 10 minutes at 20 Mbps | Collection center LAN, as an ideal calculation |
| Mission download of the drone station before departure | Done at the center | Drone operating mode |
| Tunnel packet size | Inner MTU of 1,446 bytes and TCP segment of 1,406 bytes | AWS Site-to-Site VPN documentation |
| Split of the 40 active clients by zone | See section 2 | Assumption |
| Stress scenario of 50 clients | See section 2 | Assumption |
| System traffic | 1 Mbps in each direction | Assumption |
| Mission download burst | 10 Mbps | Assumption |
| Events for each sack and size of an event | 5 events of 2 KB with their responses | Assumption, with sensitivity in section 5 |
| Efficiency of a transfer and of Wi-Fi | Ranges in sections 6 and 8 | Assumptions, to measure |
| Guarantees and caps by class | Section 7 | Derived from the figures above |

## 2. Scenarios

The design scenario is the 40 simultaneous clients of the decision on center WAN capacity. The stress scenario of 50 clients only tests the design, and the design promises no service at that load. The case in which all 66 clients are active shows what the link cannot do. Whole clients are used in every zone.

Demand if every client is active, from the clients of the LAN and the reference rate.

| Zone | Clients | Down, Mbps | Up, Mbps | Source of the figures |
|---|---|---|---|---|
| Management | 7 | 14.0 | 3.5 | Clients from the LAN document, rate from the statement |
| Support | 7 | 14.0 | 3.5 | Clients from the LAN document, rate from the statement |
| Logistics | 22 | 44.0 | 11.0 | Clients from the LAN document, rate from the statement |
| Transport | 20 | 40.0 | 10.0 | Clients from the LAN document, rate from the statement |
| Visitors | 10 | 20.0 | 5.0 | Clients from the LAN document, rate from the statement |
| Total | 66 | 132.0 | 33.0 | |

How the clients of the design scenario are rounded. The 40 active clients are the approved total. Logistics is taken as fully active with 22 clients. The other 18 are split among the other zones in proportion to their clients, and the method of the largest remainder keeps whole numbers that add up.

| Zone | Clients | Share of the 18 | Whole clients |
|---|---|---|---|
| Management | 7 | 2.86 | 3 |
| Support | 7 | 2.86 | 3 |
| Transport | 20 | 8.18 | 8 |
| Visitors | 10 | 4.09 | 4 |
| Total of the 18 | 44 | 18.00 | 18 |

Active clients by scenario. The stress scenario takes all of Logistics and Visitors and 50 percent of Management, Support and Transport, rounded up to 4, 4 and 10.

| Zone | Clients | Design, 40 | Stress, 50 | All active, 66 |
|---|---|---|---|---|
| Management | 7 | 3 | 4 | 7 |
| Support | 7 | 3 | 4 | 7 |
| Logistics | 22 | 22 | 22 | 22 |
| Transport | 20 | 8 | 10 | 20 |
| Visitors | 10 | 4 | 10 | 10 |
| Total | 66 | 40 | 50 | 66 |

## 3. Requested demand and allowed bandwidth

Requested demand is what the active clients ask for at the reference rate, plus the system traffic and, where stated, the drone synchronization. Allowed bandwidth is what the guarantees, caps and priority leave to each class. The two differ whenever the link or a cap is short, and the allowed value is the one that applies. The visitors share one cap of 10 Mbps. If ten visitors are active, they cannot all receive 2 Mbps at the same time, since the 10 Mbps of the cap gives them 1 Mbps each on average.

| Scenario | Direction | Class | Requested, Mbps | Allowed, Mbps | Left free, Mbps | Visitors, average for each active client |
|---|---|---|---|---|---|---|
| Design, 40 | down | Operation | 45.0 | 45.0 |  |  |
| Design, 40 | down | Business | 28.0 | 28.0 |  |  |
| Design, 40 | down | Guest | 8.0 | 8.0 | 19.0 | 2.00 Mbps of 2.0 |
| Design, 40 | up | Operation | 12.0 | 12.0 |  |  |
| Design, 40 | up | Business | 7.0 | 7.0 |  |  |
| Design, 40 | up | Guest | 2.0 | 2.0 | 79.0 | 0.50 Mbps of 0.5 |
| Design, 40, with drone | down | Operation | 55.0 | 55.0 |  |  |
| Design, 40, with drone | down | Business | 28.0 | 28.0 |  |  |
| Design, 40, with drone | down | Guest | 8.0 | 8.0 | 9.0 | 2.00 Mbps of 2.0 |
| Design, 40, with drone | up | Operation | 32.0 | 32.0 |  |  |
| Design, 40, with drone | up | Business | 7.0 | 7.0 |  |  |
| Design, 40, with drone | up | Guest | 2.0 | 2.0 | 59.0 | 0.50 Mbps of 0.5 |
| Stress, 50 | down | Operation | 45.0 | 45.0 |  |  |
| Stress, 50 | down | Business | 36.0 | 36.0 |  |  |
| Stress, 50 | down | Guest | 20.0 | 10.0 | 9.0 | 1.00 Mbps of 2.0 |
| Stress, 50 | up | Operation | 12.0 | 12.0 |  |  |
| Stress, 50 | up | Business | 9.0 | 9.0 |  |  |
| Stress, 50 | up | Guest | 5.0 | 5.0 | 74.0 | 0.50 Mbps of 0.5 |
| Stress, 50, with drone | down | Operation | 55.0 | 55.0 |  |  |
| Stress, 50, with drone | down | Business | 36.0 | 36.0 |  |  |
| Stress, 50, with drone | down | Guest | 20.0 | 9.0 | 0.0 | 0.90 Mbps of 2.0 |
| Stress, 50, with drone | up | Operation | 32.0 | 32.0 |  |  |
| Stress, 50, with drone | up | Business | 9.0 | 9.0 |  |  |
| Stress, 50, with drone | up | Guest | 5.0 | 5.0 | 54.0 | 0.50 Mbps of 0.5 |
| All active, 66 | down | Operation | 45.0 | 45.0 |  |  |
| All active, 66 | down | Business | 68.0 | 55.0 |  |  |
| All active, 66 | down | Guest | 20.0 | 0.0 | 0.0 | 0.00 Mbps of 2.0 |
| All active, 66 | up | Operation | 12.0 | 12.0 |  |  |
| All active, 66 | up | Business | 17.0 | 17.0 |  |  |
| All active, 66 | up | Guest | 5.0 | 5.0 | 66.0 | 0.50 Mbps of 0.5 |

The stress scenario does not meet the reference service for every client. Its visitors receive less than the reference rate because they share the cap, and with the drone running the visitors share even less, since the link is full. What the scenario shows is that operation and business traffic stay protected when the link is under pressure.

## 4. Validation against the link

Validation in each direction, with the sum of requested demand and the sum of allowed bandwidth.

| Scenario | Down requested | Down allowed | Down free | Up requested | Up allowed | Up free | Reference service met for every client |
|---|---|---|---|---|---|---|---|
| Design, 40 | 81.0 | 81.0 | 19.0 | 21.0 | 21.0 | 79.0 | yes |
| Design, 40, with drone | 91.0 | 91.0 | 9.0 | 41.0 | 41.0 | 59.0 | yes |
| Stress, 50 | 101.0 | 91.0 | 9.0 | 26.0 | 26.0 | 74.0 | no |
| Stress, 50, with drone | 111.0 | 100.0 | 0.0 | 46.0 | 46.0 | 54.0 | no |
| All active, 66 | 133.0 | 100.0 | 0.0 | 34.0 | 34.0 | 66.0 | no |

The design scenario fits in both directions and meets the reference service for every active client, with and without the drone. The sums include the system traffic of 1 Mbps in each direction, so the design scenario asks 81 Mbps down and 21 Mbps up, and 19 Mbps down and 79 Mbps up remain before any other traffic. Without the system traffic, the 40 clients demand 80 Mbps down and 20 Mbps up, and 20 Mbps down and 80 Mbps up remain. Down is the direction that is closer to the limit, and the drone upload uses the up direction, where the reserve is larger.

In the stress scenario the requested demand is 101 Mbps down, above the link, and the cap on visitors brings the allowed bandwidth to 91 Mbps. With the drone the requested demand is 111 Mbps down and the link is full, so the visitors lose part of their cap. When all 66 clients are active the requested demand is 133 Mbps down. The operation keeps what it asks for, the business class receives the remaining capacity, and the visitors receive nothing, as the decision on center WAN capacity sets for non-operational traffic under load.

## 5. Traffic of the operation and the reserve

The traffic of the operation is small beside the reference rate of the clients. It follows from the sacks of the case and from three assumptions, and the table shows how it moves if an event is ten or a hundred times larger than assumed.

Traffic of the operation in the logistics zone, calculated from 400 sacks a day, 5 events or requests for each sack, and a peak hour that carries 3 times an even share of a day of 8 hours.

| Size of one event with its response | Average rate over the day | Rate in the peak hour |
|---|---|---|
| 2 KB | 0.00038 Mbps | 0.0034 Mbps |
| 20 KB | 0.00379 Mbps | 0.0341 Mbps |
| 200 KB | 0.03793 Mbps | 0.3413 Mbps |

Even if an event were a hundred times larger than assumed, the peak is a fraction of 1 Mbps. The reserve that the decision leaves for the operation therefore exists for two bursts that the center must absorb and for headroom. The first is the upload of the drone batch, which goes up and needs a rate that finishes in a time the brigade accepts, see section 6. The second is the download of the mission, the polygon and the no-fly zones by the drone station before departure, which goes down and is assumed to take 10 Mbps for a short time. The rest is headroom for system traffic and for the overhead of the encrypted tunnel, which section 6 estimates.

## 6. Synchronization of the drone

The upload of a batch goes up. Three things must be kept apart. The capacity available is the 100 Mbps of the link. The allocated bandwidth is the rate that the classes give to the synchronization, 20 Mbps in this design. The effective throughput is what the transfer really achieves, which is lower, since TCP, TLS, HTTP, the encrypted tunnel and any loss take part of the allocated rate.

Time to upload the batch of 12,000 megabits, by allocated rate and by efficiency of the transfer.

| Allocated rate | Efficiency 1.0, ideal | 0.9 | 0.8 | 0.7 |
|---|---|---|---|---|
| 10 Mbps | 20.0 min | 22.2 min | 25.0 min | 28.6 min |
| 20 Mbps | 10.0 min | 11.1 min | 12.5 min | 14.3 min |
| 40 Mbps | 5.0 min | 5.6 min | 6.2 min | 7.1 min |
| 80 Mbps | 2.5 min | 2.8 min | 3.1 min | 3.6 min |

The calculation of 10 minutes for 1.5 GB at 20 Mbps is the ideal calculation, with an efficiency of 1.0. The tunnel sets the first bound. AWS Site-to-Site VPN carries an inner MTU of 1,446 bytes and a TCP segment of 1,406 bytes, so a full packet of 1,500 bytes on the link carries at most 1,406 bytes of data, an efficiency of about 0.94, and the batch takes at least 10.7 minutes at 20 Mbps. TLS records and HTTP headers take well under 1 percent more. Retransmissions after loss, the link between the drone station and the firewall, and the behavior of the provider lower it further, and a measurement on a real center replaces the estimate. An upload from a municipal seat goes over the internet with no tunnel, so only the other overheads apply there. At the allocated 20 Mbps, an efficiency of 0.7 would give about 14 minutes, which a brigade can still use during a visit. Because 80 Mbps of the up direction remain before other traffic, the synchronization can use more than 20 Mbps when the link is free, which is lending, with no guarantee behind it.

## 7. Traffic classes by zone

The classes keep the decision on center WAN capacity, with priority for logistics and drone synchronization and a cap for visitors, and they add the values. A guarantee is first served, a cap is a ceiling, and the capacity that a class does not use can be lent to the others.

| Class | Zones and traffic | Priority | Guarantee down | Guarantee up | Cap down | Cap up |
|---|---|---|---|---|---|---|
| Operation | Logistics, local servers, tunnel traffic, drone synchronization | 1 | 55 Mbps | 32 Mbps | link | link |
| Business | Management, Support, Transport | 2 | 28 Mbps | 9 Mbps | link | link |
| Guest | Visitors | 3 | 0 Mbps | 0 Mbps | 10 Mbps | 10 Mbps |

How each guarantee is built.

| Class and direction | Guarantee | Built from |
|---|---|---|
| Operation, down | 55 Mbps | 22 Logistics clients at 2.0 Mbps = 44, plus 1 for system traffic, plus 10 for the mission download of the drone station |
| Operation, up | 32 Mbps | 22 Logistics clients at 0.5 Mbps = 11, plus 1 for system traffic, plus 20 for the drone synchronization at the ideal rate |
| Business, down | 28 Mbps | The 14 Business clients of the design scenario at 2.0 Mbps = 28 |
| Business, up | 9 Mbps | The 18 Business clients of the stress scenario at 0.5 Mbps = 9.0 |
| Guest, both | 0 and a cap of 10 Mbps | The decision on center WAN capacity caps visitors at 10 percent of the link and gives them no guarantee |

The guarantees fit. In the down direction they add up to 83 Mbps of 100, and in the up direction to 41 Mbps of 100, so even if every class asks for its guarantee at once, the link holds them, and 17 Mbps down and 59 Mbps up remain free.

Three different amounts are involved for each class. The guarantee is the minimum that the class always receives when it asks. The cap is the maximum, and only the visitors have one below the link. The lendable capacity is what a class does not use of its guarantee and the free capacity of the link, which other classes may use in order of priority and which returns to its owner when the owner asks. In the stress scenario the business class asks for 36 Mbps down and has a guarantee of 28, so it uses 8 Mbps of lent capacity, and it gives it back if the operation needs it.

When logistics and the drone coincide, both belong to the operation class, whose guarantee covers both at once. Logistics traffic is interactive and small, so it is served first inside the class, and the drone synchronization takes the rest of the guarantee and whatever the link has free. If logistics is idle, the drone can use more than its 20 Mbps. In the design scenario with the drone, the operation class asks for 55 Mbps down and 32 Mbps up and receives all of it.

What the local firewall can and cannot control. Shaping on the upload interface limits what the center sends, and shaping on the zone interfaces limits what each class receives from the link. Congestion of the download that happens in the network of the provider, before the traffic reaches the firewall, is not under the control of the firewall, and a local configuration does not guarantee that the download will have the allocated bandwidth. The design therefore requires a dedicated link with a committed rate of 100 Mbps in each direction, which keeps the provider network from taking the download guarantees away. Where a municipality offers only shared fiber, the center takes it as a fallback. The upload classes and the local sharing still hold, and the download guarantees become best effort, with logistics still protected by the reception queue that works with no link.

Functions that the equipment must have. They are requirements. None of them is shown to be configured or verified, and no firewall is selected.

| Function | Why |
|---|---|
| Classification by zone interface and by address, and marking of traffic | Puts each flow in its class |
| Hierarchical shaping in both directions with a guaranteed rate, a ceiling and lending between classes | Gives the guarantees, the caps and the lending of this section |
| A separate shaping inside the operation class that serves interactive traffic before bulk traffic | Serves logistics before the drone when they coincide |
| A cap for the visitor class with fair sharing among its clients | Keeps one visitor from using the cap |
| Marking of the traffic of the tunnel before it is encrypted, kept in the outer header | Keeps the priority of the tunnel traffic against internet traffic on the same link |
| Clamping of the TCP segment to 1,406 bytes or less on the tunnel | The tunnel does not support path MTU discovery, and larger segments would fragment |
| Counters of each class | Shows whether the values hold, and feeds the measurement of the first harvest |

## 8. Wi-Fi demand for each access point

The number of access points stays at two to three, and no model is selected. Active clients are shared evenly among the access points, rounded up, and each access point must sustain the aggregate throughput of its clients at the reference rate. The PHY rate that this implies depends on the efficiency of Wi-Fi, which is an assumption. The airtime of the five SSIDs and the capacity of a model remain pending validations of the center WLAN design.

| Scenario | Access points | Clients on the busiest one | Aggregate down and up, Mbps | PHY rate needed at efficiency 0.3, 0.5, 0.7 |
|---|---|---|---|---|
| Design, 40 | 2 | 20 | 50.0 | 167 Mbps, 100 Mbps, 71 Mbps |
| Design, 40 | 3 | 14 | 35.0 | 117 Mbps, 70 Mbps, 50 Mbps |
| Stress, 50 | 2 | 25 | 62.5 | 208 Mbps, 125 Mbps, 89 Mbps |
| Stress, 50 | 3 | 17 | 42.5 | 142 Mbps, 85 Mbps, 61 Mbps |

A real access point model, its radios and the site survey decide whether it can sustain these figures, and no claim is made here about any model.

## 9. Assumptions and pending confirmations

| Item | Origin | Who confirms | Effect if it fails |
|---|---|---|---|
| Split of the 40 active clients by zone | Assumption | Federation, with the first harvest | The guarantees of the business class and the visitor demand change |
| Stress scenario of 50 clients | Assumption | Federation | It is only a test of the design, and the classes still hold |
| Visitor cap applies to each direction | Assumption on the decision | Team | If it applies to one direction only, the other direction has no cap and visitors use more of the link |
| System traffic of 1 Mbps and mission download of 10 Mbps | Assumptions | Measurement at the first center | The guarantee of the operation class changes by the difference |
| Events for each sack and their size | Assumption | Measurement at the first center | Section 5 shows that a hundred times more still leaves the reserve unchanged |
| Efficiency of the drone transfer beyond the tunnel bound of 0.94 | Assumption | Measurement at the first center | The time of the drone synchronization lengthens, see section 6 |
| Efficiency of Wi-Fi | Assumption | Access point model and site survey | The PHY rate that an access point needs changes |
| A dedicated 100 Mbps symmetric link is available in the municipality of each center | Requirement | Federation, with operator quotes | The center takes shared fiber, and the download guarantees become best effort |
| Price of the link | Secondary source | Operator quotes for each municipality | The cost of section 10 changes |
| Shaping functions of the firewall, in both directions | Not verified | Equipment selection | The classes may need another mechanism |
| Real number of active clients at the peak of harvest | Not measured | First harvest | The scenarios are replaced by measured values |

## 10. Cost of the link

The prices below are references published by a Colombian operator, converted at COP 4,150 per USD, the rate of the planning workbook. Quotes from operators with coverage in each municipality replace them.

| Link | Monthly price per center, COP | Per center, USD | Three centers, USD |
|---|---|---|---|
| Dedicated, 80 to 120 Mbps, committed rate | From 250,000 to 350,000 | 60 to 84 | 181 to 253 |
| Shared business fiber, best effort | 70,000 to 150,000 | 17 to 36 | 51 to 108 |

The platform cost so far counts USD 45 a month per center, USD 135 for the three, which falls in the shared range. The dedicated link this design requires adds about USD 46 to 118 a month for the three centers over that figure. The VPN connections and the cloud side of the tunnel are in the platform cost of the overview, and the firewall and access points are equipment of the center.

## 11. Sources

- [Collection center LAN](collection-center-lan.md), [center WLAN](center-wlan.md), [decision on center WAN capacity](../adr/center-wan-capacity.md), [drone operating mode](../drones/operating-mode.md) and [drone mission link](drone-mission-link.md) of this platform.
- `tools/wan_sizing.py`, which prints every calculated table of this document and checks itself against the figures of the LAN document.
- AWS, [Site-to-Site VPN quotas](https://docs.aws.amazon.com/vpn/latest/s2svpn/vpn-limits.html), for the maximum transmission unit, the segment size and the absence of path MTU discovery.
- Edatel, [dedicated and shared business internet, differences and prices](https://edatel.net.co/internet-dedicado-vs-internet-empresarial-compartido-diferencias-precios-y-cual-conviene/), an operator reference to replace with quotes.
