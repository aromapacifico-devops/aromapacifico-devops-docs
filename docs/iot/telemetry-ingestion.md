# Telemetry ingestion

Farm nodes publish to one regional endpoint. Each reading is validated, stored once and evaluated against the current ranges, with no compute waiting between messages. This document defines the service, the message contract, how duplicates and bursts are handled, how the alert meets its five-minute budget, where readings live for five years, what fails and how, and what the infrastructure module creates.

## Contents

1. Context and scope
2. Volume
3. Ingestion service
4. Path of a reading
5. Message contract
6. Duplicates and order
7. Bursts when buffers drain
8. Alert in under five minutes
9. Storage for five years
10. Out-of-coverage farms
11. What fails and what happens
12. Observability
13. Cost
14. Infrastructure module
15. Assumptions and pending confirmations

### Terms used

| Term | Meaning in this document |
|---|---|
| Reading | One message from a node, with the time it was measured |
| Idempotency key | The value that identifies a message, so a repeat is ignored |
| QoS 1 | MQTT delivery with confirmation, at least once |
| Dead letter queue | Queue that keeps messages a function could not process |
| TTL | Time to live, the automatic expiry of a table item |
| Parquet | Columnar file format, compact and cheap to query |

---

## 1. Context and scope

| Piece | What is needed | Section |
|---|---|---|
| Ingestion | Crop and drying telemetry over cellular, or LoRa where no signal exists | 3, 4, 10 |
| Validation | Message contract, identity per node, no duplicates | 5, 6 |
| Alert | Under five minutes from the out-of-range reading | 8 |
| History | Five years, for the farmer and the pilot report | 9 |

Carrier positions travel through the carrier API and share the storage pattern, so this document leaves them out. Drone objects have their own path.

## 2. Volume

| Measure | Normal month | Harvest month |
|---|---|---|
| Crop readings | 36,000 | 36,000 |
| Drying readings | 14,400 | 72,000 |
| Total device messages | 50,400 | 108,000 |
| Messages a second, average | 0.02 | 0.04 |

With 0.5 KB per message, a harvest month is 54 MB. The volume is tiny. What demands design is the arrival pattern, since nodes wake on schedule and buffers drain together when a tower returns.

## 3. Ingestion service

| Option | For | Against | Result |
|---|---|---|---|
| AWS IoT Core | Per-device identity, MQTT, revocation, rules engine, pay per message | Limits per connection, which this load never reaches | **Chosen** |
| API Gateway with HTTPS | Simple | A full TLS handshake and overhead per reading, identity must be built, more energy on the node | Discarded |
| Kinesis Data Streams | High throughput | Provisioned or billed by stream, far above this load | Discarded |
| Self-managed MQTT broker | Full control | A server running all day, against the idle-free design | Discarded |

MQTT uses little energy and few bytes on a node that wakes to publish, and IoT Core gives each device a revocable identity with no server to run.

IoT Core accepts payloads of up to 128 KB and 100 publish requests a second per connection, well above what a node sends. Up to 100 unacknowledged QoS 1 messages may be in flight, so a node drains its buffer in small groups.

## 4. Path of a reading

1. The node publishes over MQTT with TLS on port 8883, QoS 1, using its device certificate.
2. An IoT rule validates the topic and sends the message to two destinations.
3. Amazon Data Firehose receives a copy and writes Parquet files to the S3 archive.
4. An SQS queue receives the other copy.
5. A Lambda function reads batches from the queue, validates the contract and writes to DynamoDB with a conditional write.
6. The function compares the reading with the current ranges.
7. A reading out of range creates an alert, and SNS delivers it to the farmer's phone.

The queue sits between IoT Core and the function so that a slow or failing function loses nothing. Firehose takes its copy straight from the rule, so the archive stays complete even if the function fails.

## 5. Message contract

Topic format is `aroma/{env}/farm/{node_id}/{stream}`, where stream is `crop` or `drying`. The IoT policy allows a node to publish only on topics with its own identifier.

```json
{
  "schema": 1,
  "node_id": "node-41-00137",
  "seq": 48213,
  "measured_at": "2026-05-14T06:00:00Z",
  "stream": "crop",
  "buffered": false,
  "dropped_since_last": 0,
  "values": {
    "n_mg_kg": 42.1,
    "p_mg_kg": 18.4,
    "k_mg_kg": 96.2,
    "ph": 5.3,
    "soil_humidity_pct": 61.0,
    "soil_temp_c": 19.4,
    "air_humidity_pct": 72.5,
    "air_temp_c": 21.2
  }
}
```

| Field | Purpose |
|---|---|
| `schema` | Lets the contract evolve while old nodes keep working |
| `node_id` | Must match the certificate of the connection |
| `seq` | Counter that survives restarts, used for duplicates and gaps |
| `measured_at` | Time of the reading, which stays correct when drained hours later |
| `buffered` | Tells that the message waited in the buffer |
| `dropped_since_last` | Readings lost past the 24-hour limit |
| `values` | Variables of the stream |

Messages that fail validation go to the dead letter queue, and they stay in the archive for analysis.

## 6. Duplicates and order

QoS 1 delivers at least once, so a node that loses the confirmation sends the message again. Duplicates are normal and the design expects them.

The idempotency key is `node_id` with `seq`. The readings table uses a conditional write, so a repeat fails silently and creates no second reading or second alert.

Order does not matter for storage, since each reading carries its own time. For alerts, the function checks the age of the reading and labels drained alerts, so a farmer does not read an old alert as a current one.

## 7. Bursts when buffers drain

The worst plausible case is a tower that returns after a day of outage, with every drying node of an area draining at once.

| Scenario | Messages | If all arrive in 5 minutes |
|---|---|---|
| Every one of 200 nodes drains 24 readings | 4,800 | 16 messages a second |

That is a modest burst for these services. The queue absorbs it and the function scales by itself. Reserved concurrency stays low, so that a burst cannot exhaust DynamoDB capacity or the budget, and the queue simply takes longer. A random delay of a few seconds on each node before publishing spreads the arrivals.

## 8. Alert in under five minutes

The clock starts at the out-of-range reading and stops when the alert reaches the delivery service.

| Stage | Budget |
|---|---|
| Node reads and connects | 60 seconds |
| IoT Core and rule | 1 second |
| Queue batching | Up to 30 seconds |
| Function | Under 5 seconds |
| SNS to the phone | Under 60 seconds |
| **Total** | **About 2.5 minutes** |

The budget leaves more than two minutes of margin. With no signal at the node, the alert goes out when the buffer drains, within 24 hours, and it carries the time of the reading.

Alerts fire on the change of state. A reading out of range raises one alert, and further readings of the same condition update it. This avoids a stream of messages to a farmer during a long drying.

**Delivery depends on the phone.** Farmers have data in the municipal seat or on main roads, so a push may wait until the phone connects. The objective counts from a moment with a delivery path, and the second objective of the platform measures it. An SMS fallback would reach a phone with basic signal, and it is left as an open choice below, since its price for Colombia could not be read from the price list.

## 9. Storage for five years

| Store | Key | Retention | Purpose |
|---|---|---|---|
| Readings table | Partition `node_id`, sort `measured_at#seq` | 90 days through TTL | Recent history in the application |
| Ranges table | Partition `zone_type`, sort `variable` | Current values | Evaluation |
| Alerts table | Partition `farm_id`, sort `raised_at` | Five years | Alert history |
| Telemetry archive | Parquet, by `stream/year/month/day/` | Five years through a lifecycle rule | Pilot reports through Athena |

| Option for telemetry | For | Against | Result |
|---|---|---|---|
| DynamoDB and S3 archive | No instance, low cost, five years in S3 | Older history reads through Athena | **Chosen** |
| Timestream for LiveAnalytics | Built for time series | Closed to new customers since June 2025 | Not available |
| Timestream for InfluxDB | Time series engine | A provisioned instance running all day | Discarded |
| Aurora PostgreSQL | SQL | Billed while idle, more to operate | Discarded |

Point-in-time recovery covers the tables, with a restore point about 5 minutes behind the current time.

## 10. Out-of-coverage farms

Nodes outside coverage send readings over LoRa to a gateway shared by the vereda, at a high point with LTE signal. AWS IoT Core for LoRaWAN acts as the network server, and an IoT rule joins the same path as cellular readings.

LoRa carries short frames, far below the 0.5 KB of the JSON message. The node therefore sends a compact binary frame on that path, with the same fields, and a decoder function rebuilds the contract before it enters the queue. Everything after that point stays identical, so a LoRa farm costs no extra design in the platform.

Billing is USD 6 per million LoRaWAN messages. If 40 farms use this path, they send about 7,200 crop messages a month, which costs under USD 0.05.

## 11. What fails and what happens

| Failure | Effect | Response |
|---|---|---|
| Node loses signal | Buffer holds readings | Publishes on return |
| Tower or gateway fails | Many nodes silent | Alarm for silent nodes, buffers hold 24 hours |
| IoT Core throttled | Publish fails | Node retries next cycle |
| Function fails | Message returns to the queue | Three retries, then the dead letter queue and an alarm |
| Invalid message | Function rejects it | Dead letter queue, kept in the archive |
| DynamoDB throttled | Function retries | Queue grows, nothing lost |
| Firehose fails | Archive delayed | Firehose retries to S3 |
| Deployment | Function version changes | Queue holds messages during the change |

## 12. Observability

| Signal | Why | Alarm |
|---|---|---|
| Nodes silent over 24 hours | Required, shows dead nodes and farms | Yes |
| Depth and age of the queue | Shows a stuck consumer | Age over 2 minutes |
| Messages in the dead letter queue | Failed processing | Any |
| `dropped_since_last` above zero | Data lost at the edge | Yes, on the operations dashboard |
| Alerts not delivered | Required | Yes |
| Latency from `measured_at` to alert | First objective of the platform | Yes |

## 13. Cost

Calculated from the AWS price list for us-east-1, at the volumes of section 2.

| Item | Rate | Harvest month, USD |
|---|---|---|
| IoT Core messages | USD 1.00 per million | 0.11 |
| Rules and actions | USD 0.15 per million each | 0.05 |
| Connection minutes | USD 0.08 per million | 0.01 |
| SQS requests | USD 0.40 per million | 0.13 |
| Lambda, 0.2 s at 256 MB | USD 0.20 per million and USD 0.0000166667 per GB-second | 0.11 |
| DynamoDB writes and reads | USD 0.625 and USD 0.125 per million | 0.08 |
| Firehose ingestion and conversion | USD 0.029 and USD 0.018 per GB | Under 0.01 |
| S3 requests | USD 0.005 per 1,000 PUT | 0.01 |
| **Total** | | **About 0.50** |

At 1,000 farms, the same model gives about USD 2.50 a month. Telemetry is the least of the costs of the platform, so no effort goes into optimizing it.

## 14. Infrastructure module

This module of the first plan implements box C07. It creates the IoT rule, the SQS queue with its dead letter queue, the Firehose stream, the DynamoDB tables and the S3 archive with its lifecycle rule. It receives KMS keys and execution roles from the security module, and it creates no network or identity resources, following the separation of domains in the infrastructure rules.

| Input | Output |
|---|---|
| `kms_key_arn`, `execution_role_arn`, `alert_ranges` | `iot_rule_name`, `queue_arn`, `readings_table_arn`, `archive_bucket_arn` |

## 15. Assumptions and pending confirmations

| Item | Who confirms | Effect if it fails |
|---|---|---|
| SMS fallback for alerts | Federation, with a price for Colombia | Without it, the alert waits for data on the phone |
| The share of farms outside coverage | Federation | Number of gateways, cost barely moves in the cloud |
| Messages average 0.5 KB | First nodes | Linear effect on small amounts |
| LoRa frequency plan for Colombia | Network survey | Radios and gateways are selected accordingly |

## Sources

- AWS Price List API for IoT Core, SQS, Lambda, DynamoDB, Firehose and S3 in us-east-1.
- AWS IoT Core endpoints and quotas.
- Amazon Timestream availability notice.
- DynamoDB point-in-time recovery documentation.
