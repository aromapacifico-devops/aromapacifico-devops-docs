# Telemetry ingestion

Farm nodes publish to one regional endpoint. Each reading is validated, stored once and evaluated against the current thresholds, with no compute waiting between messages. The same endpoint serves 200 or 1,000 farms.

## Path of a reading

1. The node publishes over MQTT with TLS to AWS IoT Core, using its device certificate.
2. An IoT rule sends each message to two destinations.
3. Amazon Data Firehose writes the message to the S3 archive.
4. An SQS queue feeds a Lambda function in batches.
5. The function validates the message, writes it to DynamoDB with a conditional write that rejects duplicates, and compares it with the thresholds.
6. A reading out of range creates an alert, which SNS delivers to the farmer's phone.

The SQS queue absorbs a burst from buffers draining at once. After three failed attempts a message moves to a dead letter queue, where an alarm reports it. The message stays intact in the archive either way.

## Message contract

Topic format is `aroma/{env}/farm/{node_id}/{stream}`, where stream is `crop` or `drying`.

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

The idempotency key is `node_id` with `seq`. A sequence number that survives restarts lets the platform drop a repeated message and detect a gap. `measured_at` is the time of the reading, so a reading drained hours later keeps its real time.

## Storage

| Table or bucket | Key | Retention |
|---|---|---|
| Readings table | Partition `node_id`, sort `measured_at#seq` | 90 days through time to live |
| Thresholds table | Partition `zone_type`, sort `variable` | Current values, with history in the audit log |
| Alerts table | Partition `farm_id`, sort `raised_at` | Five years |
| Telemetry archive | `stream/year/month/day/` prefixes in Parquet | Five years through a lifecycle rule |

Telemetry lives in DynamoDB for recent reads and in S3 for the five-year history, which Athena serves for pilot reports. The threshold change that the Federation makes reaches the next batch, since the function reads current values.

## Sizing

| Measure | Normal month | Harvest month |
|---|---|---|
| Crop readings | 36,000 | 36,000 |
| Drying readings | 14,400 | 72,000 |
| Carrier positions | 216,000 | 216,000 |
| Total messages | 266,400 | 324,000 |

Carrier positions travel through the carrier API and share the storage pattern. The drain of a full buffer sends up to 24 readings from one drying node, which is a small burst for the queue.

## Latency

With a delivery path available, the budget from the reading out of range to the alert is under five minutes. The queue batches for no more than 30 seconds, and the function and SNS take seconds. Without a signal, the alert goes out when the buffer drains, within 24 hours.

## Infrastructure code

This module of the first plan creates the IoT rule, the SQS queue and its dead letter queue, the Firehose stream, the DynamoDB tables and the S3 archive with its lifecycle rule. It receives KMS keys and execution roles from the security module, following the separation of domains in the infrastructure rules.
