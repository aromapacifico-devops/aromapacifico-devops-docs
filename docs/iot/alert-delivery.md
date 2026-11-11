# Alert delivery

A farmer must receive an alert in under five minutes from the out-of-range reading whenever a delivery path exists, and an alert from a reading that waited in the node buffer must still go out within 24 hours. This document sets where the clock starts and stops, the time each stage may take and how it is measured, how the alert reaches the phone by mobile push with an SMS fallback for urgent alerts, and the delivery record that lets the platform prove each alert went out. The objectives and alarms of the platform read their figures from that record.

## Contents

1. Terms
2. Context and volumes
3. Two kinds of alert
4. Time budget
5. Mobile push
6. SMS fallback for urgent alerts
7. Delivery record
8. How the record is filled
9. Alerts from buffered readings
10. Figures for objectives and alarms
11. What fails and what the platform does
12. Cost
13. Infrastructure module
14. Assumptions and pending confirmations
15. Sources

## 1. Terms

| Term | Meaning in this document |
|---|---|
| Alert | The change of an alert state when a reading leaves its range, as the alert ranges define it |
| Urgent alert | Drying grain above 40 °C, where the farmer must act within the hour |
| Live alert | An alert from a reading that reached the platform within 5 minutes of its measured time, which means it was sent in its own cycle |
| Drained alert | An alert from a reading that waited in the node buffer and arrived in a later cycle |
| Handoff | The moment SNS passes the push message to Firebase Cloud Messaging or to the Apple push service |
| Receipt | The confirmation the farmer application sends when the push message arrives on the phone |
| Delivery record | The fields of an alert that hold each timestamp and status of its delivery |

## 2. Context and volumes

The [telemetry ingestion](telemetry-ingestion.md) stores each reading and evaluates it, the [alert ranges](configurable-thresholds.md) decide when a reading is out of range, and the [farm connectivity](../network/farm-connectivity.md) design fixes the hourly cycle of the node, its connection window of 120 seconds and its buffer of 24 hours. This document starts where an alert is raised and follows it to the phone.

| Figure | Normal month | Harvest month | Origin |
|---|---|---|---|
| Crop alerts | About 100 | About 100 | About 60 drone cases a harvest month, plus alerts attached to an open case |
| Urgent drying alerts | About 40 | About 200 | Two for each farm drying, 20 farms in a normal month and 100 in harvest |
| Alerts in total | About 140 | About 300 | Sum |
| Readings evaluated | About 50,400 | About 108,000 | Telemetry ingestion |

An alert fires on the change of state, so a long drying above 40 °C raises one alert and updates it, and the volume of alerts stays in the hundreds. The alert counts are estimates for the pilot and appear among the assumptions.

## 3. Two kinds of alert

The clock starts at `measured_at`, the time the node took the reading. Two situations follow from the node.

| Situation | What the platform promises | How the platform tells them apart |
|---|---|---|
| The node has signal in the cycle of the reading | The alert is handed to the push service in under 5 minutes from the reading | `received_at` minus `measured_at` is 5 minutes or less |
| The node has no signal in that cycle | The alert goes out when the buffer drains, within 24 hours of the reading, and it carries the time of the reading | `received_at` minus `measured_at` is more than 5 minutes |

The rule uses `received_at`, which the IoT rule adds from its own clock, so the classification needs no trust in the node. A node powers its modem off at the end of its 120-second window, so a reading sent in its own cycle reaches the platform in about two minutes, and anything later arrived in a following cycle. The `buffered` flag of the message is kept as a cross-check, and a disagreement between the two points to a node clock fault.

A crop reading happens every 4 hours, so a condition that starts between readings waits for the next one. That wait comes before the reading and falls outside the clock, as the five-minute objective counts from the reading.

The phone is the second half of the path. Farmers have data mostly in the municipal seat and on main roads, so a phone may be out of coverage when the alert is handed off. The objective therefore stops at the handoff, which the platform controls and can measure for every alert, and the receipt on the phone is recorded as a second figure. Section 10 defines both.

## 4. Time budget

| Stage | Limit | Kind of figure | Measured as |
|---|---|---|---|
| The node stores the reading, powers the modem and opens the connection | Up to 120 seconds | Design limit, the connection window | Part of `received_at` minus `measured_at` |
| The node publishes, and IoT Core and the rule stamp `received_at` and put the message in the queue | About 1 second | Design value, to measure in the field | Part of `received_at` minus `measured_at` |
| The function takes the message, evaluates it and publishes the push | Under 5 seconds for the evaluation, and the queue adds no batching wait | Design target, with the batching window at 0 seconds | `push_published_at` minus `received_at` |
| SNS hands the message to the push service | Reported per message as the dwell time | Measured by SNS for each alert | `push_handoff_at` minus `push_published_at` |

The stages with a stated limit add up to about 126 seconds, or 2.1 minutes. That leaves about 2.9 minutes for the time the function takes to poll the queue and for the SNS dwell time. AWS publishes no figure for either one, so the record measures both for every alert and an alarm fires when the total passes five minutes.

The queue reads with a batch size of 10 and a batching window of 0 seconds, which are the defaults for SQS. A window above zero would hold the first message of a quiet hour while the batch fills, which adds delay and saves nothing at this volume. A burst after an outage still drains in seconds, because each batch of 10 is processed as soon as it is read.

When a node drains old readings in the same connection, the new reading waits behind them. The node sends the oldest first, ten at a time, so a full day of 30 readings adds a few seconds.

A LoRa farm adds the time on air, the gateway and the network server before `received_at`. Those delays are still to measure, so the record marks LoRa alerts and the objective is reported for each link apart until the field measurement exists.

## 5. Mobile push

The farmer application registers the phone with the platform after sign-in. The platform turns the token of the phone into an SNS platform endpoint for Firebase Cloud Messaging, or for the Apple push service on an iPhone, and stores the endpoint with the farm. The ingestion function publishes each alert straight to the endpoints of the farm.

| Setting | Value | Reason |
|---|---|---|
| Kind of message | Data message with high priority | The application runs its own code when it arrives, shows the notification and sends the receipt |
| Time to live | 24 hours | An alert older than a day no longer supports a timely decision, and the history in the application still shows it |
| Content | Alert identifier, farm, lot, variable, condition in plain words and time of the reading | Enough to show the notification with no extra call. No name, national ID or position |
| Delivery status | Success and failure logged for every message, sample rate 100 percent | The record needs the handoff of every alert, a sample would leave gaps |

A data message reaches the application in the background, where it has a few seconds to act. That is enough to show the notification and send the receipt, a single small call to the platform API. If the phone has no data when it tries, the application keeps the receipt and sends it with the next call, carrying the time the phone received the alert.

| Option for the channel | For | Against | Result |
|---|---|---|---|
| Mobile push through SNS | Costs USD 0.50 per million, rich content, the application confirms receipt | Needs data on the phone | **Chosen** as the main channel |
| SMS for every alert | Reaches a phone with basic signal | USD 0.05 per message and duplicates for every crop alert, which already waits days for a drone | Discarded |
| WhatsApp | Common among farmers | Needs a business account, approved templates and data on the phone, the same limit as push | Discarded |

## 6. SMS fallback for urgent alerts

Grain above 40 °C on the drying bed is damaged within hours, and the farmer may be at home in the vereda where the phone has basic signal and no data. For that case only, the platform sends an SMS when the application has not confirmed the push.

| Rule | Behavior |
|---|---|
| Which alerts | Urgent alerts only, drying grain above 40 °C |
| When | 5 minutes after the push is published, if no receipt arrived and the alert is still active |
| To whom | The phone number of the farm owner, read from the farm record |
| Content | The same plain sentence as the notification, with the lot and the time of the reading |
| How many | One SMS per alert. Updates of the same alert send nothing more |

Crop alerts go by push only. They open a drone case that takes days to resolve, so an SMS would add cost and nothing to the outcome.

Colombia accepts SMS from short codes only, with no sender ID and no local long code. A dedicated short code is requested through AWS Support, and its monthly fee and lead time do not appear on the price page. Until the Federation obtains one, the platform sends over international routes, where AWS delivers on a best-effort basis and the sender may appear as a shared number. The record keeps the SMS status from the carrier, so the share of SMS that arrive is known from the first harvest and supports the decision on the short code.

| Option | For | Against | Result |
|---|---|---|---|
| Push, then SMS for urgent alerts | Reaches the farmer when it matters, a few dollars a month | Needs a short code for reliable sending | **Chosen** |
| Push only | No cost and no short code | A farmer with no data waits, even with the grain above 40 °C | Discarded |
| Push and SMS for every alert | Widest reach | Every crop alert costs USD 0.05 and reaches the farmer twice | Discarded |

## 7. Delivery record

The delivery record lives in the alerts table of the telemetry ingestion, which already keeps every alert for five years under the partition `farm_id` and the sort key `raised_at`. Each field has one writer.

| Field | Meaning | Written by |
|---|---|---|
| `alert_id` | Identifier of the alert | Ingestion function |
| `node_id`, `variable`, `value`, `range_version` | What was out of range and under which version | Ingestion function |
| `urgent` | True for drying grain above 40 °C | Ingestion function |
| `link` | `cellular` or `lora` | IoT rule of each path, copied by the function |
| `measured_at` | Time of the reading | Node, from the message |
| `received_at` | Time the platform saw the message | IoT rule |
| `kind` | `live` or `drained`, from the rule of section 3 | Ingestion function |
| `raised_at` | Time the function decided the alert | Ingestion function |
| `push_message_id`, `push_published_at` | Identifier and time of the publish to SNS | Ingestion function |
| `push_handoff_at`, `push_status`, `push_provider_code` | Handoff time, success or failure, and the answer of the push service | Delivery status function |
| `receipt_at`, `device_received_at` | Time the platform got the receipt, and time the phone says it received the alert | Receipt function, through the API |
| `sms_message_id`, `sms_sent_at` | Identifier and time of the SMS | Delivery check function |
| `sms_status`, `sms_status_at` | Last status reported by the carrier, such as delivered, unreachable or blocked | Delivery status function |
| `delivery_state` | `published`, `handed_off`, `received`, `sms_sent`, `sms_delivered` or `failed` | Each writer moves it forward with a conditional update |

The handoff time is the publish timestamp of the SNS log plus its `dwellTimeMs`. A sparse index on `push_message_id` lets the status function find the alert from the log entry.

Example of a record of an urgent alert that went to SMS, with invented identifiers.

```json
{
  "farm_id": "farm-demo-001",
  "raised_at": "2026-05-14T14:01:58Z",
  "alert_id": "alert-demo-0201",
  "node_id": "node-41-00137",
  "variable": "grain_temp_c",
  "value": 41.6,
  "range_version": 1,
  "urgent": true,
  "link": "cellular",
  "measured_at": "2026-05-14T14:00:00Z",
  "received_at": "2026-05-14T14:01:52Z",
  "kind": "live",
  "push_message_id": "push-demo-7f3a",
  "push_published_at": "2026-05-14T14:01:59Z",
  "push_handoff_at": "2026-05-14T14:01:59.4Z",
  "push_status": "SUCCESS",
  "push_provider_code": "200",
  "sms_message_id": "sms-demo-91c2",
  "sms_sent_at": "2026-05-14T14:07:01Z",
  "sms_status": "TEXT_DELIVERED",
  "sms_status_at": "2026-05-14T14:07:09Z",
  "delivery_state": "sms_delivered"
}
```

The reading-to-handoff time of this alert is 119.4 seconds, within the objective. The phone sent no receipt, so the urgent rule sent the SMS five minutes after the publish.

## 8. How the record is filled

The [alert delivery sequence](../architecture/diagrams/15-alert-delivery-sequence.drawio.png) shows these steps across the services.

1. The ingestion function raises the alert, writes the first fields and publishes to SNS. It stores `push_message_id` and `push_published_at` in the same item.
2. In the same step it sends a check message for the alert to a delay queue, with a delay of 5 minutes.
3. SNS writes the delivery status of the push to CloudWatch Logs. A subscription filter passes each entry to the delivery status function, which writes the handoff time, the status and the answer of the push service.
4. When the push reaches the phone, the application calls `POST /alerts/{alert_id}/receipt` with the time on the phone. The receipt function checks that the alert belongs to a farm of the caller and writes the receipt.
5. After 5 minutes the delivery check function reads the alert. If the handoff is missing, it publishes a metric for an undelivered alert. If the alert is urgent, still active and has no receipt, it sends the SMS.
6. AWS End User Messaging SMS sends its events to CloudWatch Logs, and the same delivery status function writes the SMS status.

Each writer uses a conditional update, so a repeat of a log entry or a late event cannot move the state back. The function also emits the reading-to-handoff time as a metric with the dimensions `kind` and `link`, which feeds the dashboard and the latency alarm with no query on the table.

The status logs hold the push token or the phone number, so their log groups keep entries for 30 days. The record keeps only the status, and the phone number stays in the farm record.

## 9. Alerts from buffered readings

The node keeps readings for 24 hours at most. It deletes records of age 24 hours or more before it connects and counts them in `dropped_total`, and it drains the rest oldest first when the signal returns. The [farm connectivity](../network/farm-connectivity.md) design gives the full rules.

| Length of the outage | What the platform receives | Alerts |
|---|---|---|
| Under 1 hour | Every reading at the next cycle | Drained alerts, within about one hour of the reading |
| 1 to 23 hours | Every reading | Drained alerts, within the outage plus one hour |
| Over 23 hours | The readings of the last 23 hours | Readings past the limit are gone, so their alerts are never raised. The growth of `dropped_total` shows the loss |

A drained alert goes through the same path and the same record. The function evaluates the reading under the range version in force at its measured time, marks the alert as drained and keeps the time of the reading in the notification, so a farmer does not read an old condition as a current one. If a newer reading already cleared the condition, the old reading stays as history and raises no alert, as the alert state only moves forward in time.

On a LoRa farm the gateway may also be down. Readings then wait in the node the same way, and a lost frame delays a reading by two cycles or more until the cumulative acknowledgement shows it missing.

## 10. Figures for objectives and alarms

Each figure is a filter over the fields of section 7, so the objectives and alarms of the platform need no other source.

| Figure | Alerts counted | Good when |
|---|---|---|
| Live alert latency | `kind` is `live` | `push_handoff_at` minus `measured_at` is 5 minutes or less |
| Live alert receipt | `kind` is `live` | `receipt_at` exists and `device_received_at` minus `measured_at` is 5 minutes or less |
| Drained alert latency | `kind` is `drained` | `push_handoff_at` minus `measured_at` is 24 hours or less |
| Urgent alert reach | `urgent` is true | `receipt_at` exists, or `sms_status` is delivered |
| Undelivered alert | Any alert | `push_handoff_at` is missing 5 minutes after `raised_at`, or `push_status` is a failure with no delivered SMS |
| Readings lost at the edge | Every node | Growth of `dropped_total`, a count of readings that never raised their possible alert |

Each figure is split by `link`, so cellular and LoRa farms are reported apart until the LoRa radio delay is measured. The live alert latency is the figure of the delivery objective. The receipt figure shows how often the phone itself is reachable, which depends on the coverage of the farmer and stays outside the control of the platform. The [service level objectives](../architecture/service-levels.md) set the target, window and error budget of the delivery objective.

| Alarm | Fires when | Signal |
|---|---|---|
| Undelivered alert | Any alert without a handoff 5 minutes after it was raised, or with a push failure | Metric from the delivery check and the status function |
| Slow live alert | A live alert above 5 minutes from reading to handoff | Latency metric with `kind` set to `live` |
| SMS not delivered | An urgent alert whose SMS ends unreachable, blocked or failed | Metric from the status function |

## 11. What fails and what the platform does

| Failure | Effect | Response |
|---|---|---|
| The node has no signal | The reading waits in the buffer | The alert goes out at the drain, marked as drained, within 24 hours |
| The phone has no data | The push waits at the push service | The time to live keeps it for 24 hours. An urgent alert goes by SMS after 5 minutes |
| The push token is no longer valid | The push service rejects the message | Failure status in the record, undelivered alarm, and the application registers again at its next start |
| SNS throttles the publish | The function fails the message | The message returns to the queue and is retried, then goes to the dead letter queue with an alarm |
| The status log entry never arrives | The handoff is missing in the record | The delivery check counts it as undelivered, and the alarm shows it |
| The receipt call fails on the phone | The receipt is late | The application sends it with its next call, carrying the time on the phone |
| The SMS cannot be delivered | The carrier reports unreachable or blocked | SMS alarm, and the alert stays in the history of the application |
| The farm has no registered phone | No endpoint to publish to | Undelivered alarm on the first alert, so the installer registers the phone |
| The delivery check queue fails | No SMS and no missing-handoff metric | Dead letter queue and alarm, and the latency metric still shows each alert |

## 12. Cost

Rates come from the AWS Price List API for us-east-1 and, for SMS, from the AWS End User Messaging price sheet.

| Item | Rate | Harvest month | USD |
|---|---|---|---|
| Mobile push | USD 0.50 per million notifications | About 300 | Below 0.01 |
| Delivery status logs | USD 0.50 per GB ingested and USD 0.03 per GB-month stored | About 300 entries of 1 KB | Below 0.01 |
| Delay queue, functions and receipt calls | USD 0.40 per million SQS requests, USD 0.20 per million Lambda requests, USD 1.00 per million HTTP API requests | About 2,000 requests | Below 0.01 |
| SMS to Colombia | USD 0.05087 per message | Up to 200 urgent alerts | Up to 10.17 |
| **Total** | | | **Up to about 10.20** |

In a normal month the SMS line is up to USD 2.03, for about 40 urgent alerts. The SMS line is an upper bound, since an alert confirmed on the phone sends no SMS. A dedicated short code would add a monthly fee that AWS quotes on request.

## 13. Infrastructure module

The telemetry ingestion module of the first plan creates these resources together with its queue and tables. Keys and roles come from the security module.

| Resource | Setting |
|---|---|
| Event source mapping of the ingestion queue | Batch size 10, batching window 0 seconds, batch item failures reported |
| SNS platform applications | One for Firebase Cloud Messaging, one for the Apple push service when an iPhone application exists, with success and failure feedback roles and a success sample rate of 100. The operator creates them with the AWS CLI under the names the module fixes, since SNS checks the credential at creation |
| Delay queue for delivery checks | Delay of 300 seconds, with a dead letter queue |
| Delivery status and delivery check functions | Execution roles from the security module |
| Log groups of push and SMS status | Retention of 30 days, encrypted with the platform key |
| Alerts table | Sparse index on `push_message_id` |
| SMS configuration set | Event destination to CloudWatch Logs |
| API route | `POST /alerts/{alert_id}/receipt` on the platform API, with the farmer group |

The credentials of the push services are secrets, and SNS rejects a platform application whose credential the push service does not accept. The applications are therefore created outside the infrastructure code, so a credential never reaches the state. The module creates the two status log groups that SNS writes to and builds the ARN the ingestion function publishes under.

## 14. Assumptions and pending confirmations

| Item | Who confirms | Effect if it fails |
|---|---|---|
| About 100 crop alerts and up to 200 urgent drying alerts in a harvest month | First harvest | SMS cost moves at USD 0.05 per urgent alert, the rest barely moves |
| Most farmers use Android phones | Federation, with the farmer application | iPhones need a notification service extension to send the receipt in the background |
| A dedicated short code for Colombia can be obtained, with its fee and lead time | Federation, through AWS Support | SMS stays on best-effort routes, and the share delivered decides whether the fallback is worth keeping |
| The phone number of the farm owner can receive SMS | Federation, at registration | The urgent alert reaches only a phone with data |
| Queue polling and SNS dwell time stay within the 2.9 minutes left in the budget | Measurement in the test environment and in the field | The objective is missed, and the measured stage shows where |
| Radio and gateway delay of the LoRa path | Field measurement | LoRa alerts keep their own figure until measured |

## 15. Sources

- Amazon SNS, [message delivery status](https://docs.aws.amazon.com/sns/latest/dg/sns-topic-attributes.html), [mobile application attributes and log format](https://docs.aws.amazon.com/sns/latest/dg/sns-msg-status.html) and [time to live for mobile push](https://docs.aws.amazon.com/sns/latest/dg/sns-ttl.html).
- AWS Lambda, [CreateEventSourceMapping](https://docs.aws.amazon.com/lambda/latest/api/API_CreateEventSourceMapping.html), batch size and batching window defaults for SQS.
- Amazon SQS, [delay queues](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-delay-queues.html), up to 15 minutes.
- Firebase, [receive messages on Android](https://firebase.google.com/docs/cloud-messaging/android/receive-messages), data messages in the background.
- AWS End User Messaging SMS, [supported countries](https://docs.aws.amazon.com/sms-voice/latest/userguide/phone-numbers-sms-by-country.html), [event types](https://docs.aws.amazon.com/sms-voice/latest/userguide/configuration-sets-event-types.html) and the [SMS price sheet](https://aws.amazon.com/end-user-messaging/pricing/).
- AWS Price List API, [SNS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonSNS/current/us-east-1/index.json), [CloudWatch](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonCloudWatch/current/us-east-1/index.json) and [API Gateway](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonApiGateway/current/us-east-1/index.json), us-east-1.
- [Telemetry ingestion](telemetry-ingestion.md), [alert ranges](configurable-thresholds.md), [farm connectivity](../network/farm-connectivity.md) and [LoRa path of the farms out of coverage](../network/lora-out-of-coverage.md) of this platform.
