# Ingestion sizing from 200 to 1,000 farms

The platform receives every reading through one regional endpoint. This document calculates how many messages that endpoint receives in the pilot, projects the same calculation to 1,000 farms, and checks the result against the service quotas, so the team can show that growth needs no change to the address plan or to the ingestion point. It also fixes the figures that the cost document takes as its volumes.

## Contents

1. Pilot figures
2. Volume at 200 farms
3. Volume at 1,000 farms
4. Rates and quotas
5. Compute and storage at 1,000 farms
6. What stays and what grows
7. What fails and what happens
8. Cost
9. Assumptions and pending confirmations

### Terms used

| Term | Meaning in this document |
|---|---|
| Reading | One message from a farm node, with the time it was measured |
| Position | One location sample sent by the phone of a carrier |
| Cultivation node | A node that measures the crop and publishes 6 readings a day |
| Drying node | A node that measures grain during drying and publishes 24 readings a day |
| Harvest month | A month with drying at its widest, used as the worst case |
| Drain | A node sending the readings it held while it had no signal |

## 1. Pilot figures

| Figure | Value | Where it comes from |
|---|---|---|
| Farms with a cultivation node | 200 | Pilot scope |
| Cultivation readings a day, per node | 6 | One reading every 4 hours |
| Farms drying in a harvest month | About 100 | Half of the farms are in harvest at the same time |
| Farms drying in a normal month | About 20 | Pilot scope |
| Drying readings a day, per node | 24 | One reading every hour |
| Carriers | 60 | Pilot scope |
| Positions an hour, per carrier | 12 | One every 5 minutes |
| Working hours of a carrier a day | 10 | Pilot scope |
| Days in a month | 30 | Planning convention |
| Size of a reading | 0.5 KB | Message contract |

## 2. Volume at 200 farms

| Stream | Calculation | A day | A month |
|---|---|---|---|
| Cultivation readings | 200 farms × 6 | 1,200 | 36,000 |
| Drying readings, harvest | 100 farms × 24 | 2,400 | 72,000 |
| Drying readings, normal month | 20 farms × 24 | 480 | 14,400 |
| Carrier positions | 60 carriers × 12 positions × 10 hours | 7,200 | 216,000 |

| Month | Device readings | Per second, average | Readings and positions | Per second, average |
|---|---|---|---|---|
| Normal | 50,400 | 0.02 | 266,400 | 0.10 |
| Harvest | 108,000 | 0.04 | 324,000 | 0.13 |

A harvest month of device readings holds 54 MB at 0.5 KB each. Positions travel through the carrier API and share only the storage pattern, so the rest of this document counts them for reference and sizes the device path on readings.

## 3. Volume at 1,000 farms

Every figure grows by the same factor of 5, since the pilot repeats the same kind of farm. The carrier fleet is the one figure that the pilot does not fix for a larger program, so it is listed as an assumption.

| Stream | Calculation | A day | A month |
|---|---|---|---|
| Cultivation readings | 1,000 farms × 6 | 6,000 | 180,000 |
| Drying readings, harvest | 500 farms × 24 | 12,000 | 360,000 |
| Drying readings, normal month | 100 farms × 24 | 2,400 | 72,000 |
| Carrier positions | 300 carriers × 12 positions × 10 hours | 36,000 | 1,080,000 |

| Month | Device readings | Per second, average | Readings and positions | Per second, average |
|---|---|---|---|---|
| Normal | 252,000 | 0.10 | 1,332,000 | 0.51 |
| Harvest | 540,000 | 0.21 | 1,620,000 | 0.63 |

| Measure | 200 farms | 1,000 farms |
|---|---|---|
| Device readings in a harvest month | 108,000 | 540,000 |
| Size of those readings | 54 MB | 270 MB |
| Connections an hour, one per node | 200 | 1,000 |
| Connections a day, one per node and hour | 4,800 | 24,000 |

## 4. Rates and quotas

The average rate says little, because nodes wake on schedule and buffers drain together after an outage. Each node connects at a minute of the hour fixed for it, so connections spread across the hour. Two cases bound the load on the endpoint.

| Case | Calculation | 200 farms | 1,000 farms |
|---|---|---|---|
| Regular hour, connections a second | Nodes ÷ 3,600 seconds | 0.06 | 0.28 |
| Every node connects in the same minute | Nodes ÷ 60 seconds | 3.3 | 16.7 |
| Day-long outage ends, every node holds 30 readings | Nodes × 30 ÷ 3,600 seconds | 1.7 messages a second | 8.3 messages a second |

The quotas of AWS IoT Core for us-east-1 are the following.

| Quota | Default | Adjustable | Use at 1,000 farms |
|---|---|---|---|
| Connect requests a second, per account | 3,000 | Yes | 16.7 in the worst case, 0.6 percent |
| Concurrent connections, per account | 500,000 | Yes | Fewer than 1,000, since a node stays connected about a minute |
| Inbound publish requests a second, per account | 20,000 | Yes | 8.3 in the drain case, 0.04 percent |
| Publish requests a second, per connection | 100 | No | A node sends 30 readings in groups of 10 |
| Unacknowledged QoS 1 messages, per connection | 100 | No | Windows of 10 stay far below it |
| Payload size | 128 KB | No | A reading is 0.5 KB |

Every quota sits at least two orders of magnitude above the load, and the ones that can be raised stay available if the program ever grows past the pilot by a large factor.

## 5. Compute and storage at 1,000 farms

**Compute.** A function that runs 0.2 seconds for each message, receiving 8.3 messages a second in the drain case, keeps about 2 executions running at the same time (8.3 × 0.2 = 1.7). The function reads batches from the queue, so the real figure is lower. The low reserved concurrency of the ingestion design covers it.

**Recent readings.** The table keeps readings for 90 days. If three harvest months fell inside that window, it would hold 3 × 540,000 = 1,620,000 readings, about 810 MB at 0.5 KB.

**Archive.** Every reading also goes to the five-year archive. If every month of a year had the load of a harvest month, a year would add 6,480,000 readings, about 3.2 GB, and five years about 16 GB before Parquet compression. Real use is lower, since only part of the year is harvest.

## 6. What stays and what grows

| Piece | Change from 200 to 1,000 farms |
|---|---|
| Ingestion endpoint | None. All farms publish to the same regional endpoint |
| Address plan of the cloud | None. A farm holds no address in the VPC and reaches public service endpoints |
| Subnets, firewall and VPN of the cloud | None |
| Ingestion rule, queue, function and tables | None. They scale with the load and keep their limits |
| Certificates and things | 800 more. Each node receives its identity before it ships |
| Minute assigned to each node | Computed from the node identifier, so no table to maintain |
| Shared gateways and brigades in the field | More units. This is where growth is felt |

The stress point of a larger pilot is in the field, since coverage and drone brigades grow with the number of farms. The cloud absorbs the increase without redesign.

## 7. What fails and what happens

| Failure | What happens | Data lost |
|---|---|---|
| A connection attempt is throttled by the quota | The node ends the attempt and tries again at its next hour | None, the node holds readings for 24 hours |
| The function falls behind during a drain | The queue holds the messages and the function catches up | None |
| A message is rejected as invalid | It goes to the dead letter queue for inspection | None, the archive holds its copy |
| The account quota is too low for a future program | The quota is raised through a request to AWS before the program grows | None |

## 8. Cost

The volumes of this document feed the cost document. Telemetry ingestion costs about USD 1 in a harvest month at 200 farms and grows linearly to about USD 5 at 1,000 farms. The hourly configuration read, which each node performs on connection, adds about USD 0.48 at 200 farms and about USD 2.40 at 1,000 farms, and it is already inside those totals. Telemetry stays the smallest cost of the platform.

| Volume used by the cost document | 200 farms | 1,000 farms |
|---|---|---|
| Device readings, harvest month | 108,000 | 540,000 |
| Device readings, normal month | 50,400 | 252,000 |
| Carrier positions, month | 216,000 | 1,080,000 |
| Connections, month | 144,000 | 720,000 |

The connections of a month come from one connection each hour, all year, which is 24 × 30 = 720 a month for each node.

## 9. Assumptions and pending confirmations

| Item | Who confirms | Effect if it fails |
|---|---|---|
| The farms at 1,000 repeat the pilot, so the shares of drying and cultivation stay the same | Federation | Volumes change in proportion, quotas still hold |
| The carrier fleet grows to 300 | Federation | Position volume and the carrier API cost change in proportion |
| Half of the farms dry at the same time in a harvest month | Federation | A higher share raises harvest volume, which the quotas still absorb |
| Messages average 0.5 KB | First nodes in the field | Storage changes in proportion |
| The quotas of the account match the defaults of AWS | Team, in the Service Quotas console of the account | A lower quota is raised before the program grows |

## Sources

- AWS, IoT Core message broker and protocol limits and quotas, for the default values of us-east-1.
- AWS Price List API for IoT Core, SQS, Lambda, DynamoDB, Firehose and S3 in us-east-1.
