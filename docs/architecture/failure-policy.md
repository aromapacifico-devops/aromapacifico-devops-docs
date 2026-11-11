# Retries, dead letter queues and unchanged state on failure

An inference function can fail for many reasons. A model call times out, a service throttles, a permission is missing or the code has a defect. Whatever the cause, the source object stays where it was and the case, order or estimate keeps the state it had before the event. This document sets how many times each function retries, how long a message waits between attempts, where an exhausted message goes, which signal shows the failure and which alarm watches it, and how an operator sends the work back once the cause is fixed. It applies to the four inference functions, focus confirmation, verification, harvest estimation and telemetry batch.

## Contents

1. Terms
2. Context and volumes
3. The path of a failure
4. Retry and dead letter values for each function
5. What a failure leaves unchanged
6. Events the rule cannot deliver
7. Where the error is seen
8. Sending the work back after a fix
9. Cost
10. Alternatives discarded
11. Assumptions and pending confirmations
12. Sources

## 1. Terms

| Term | Meaning in this document |
|---|---|
| Work queue | The standard SQS queue that receives the events of one function and that Lambda polls |
| Dead letter queue | The SQS queue that keeps a message the work queue could not deliver after its receives ran out |
| Rule dead letter queue | The SQS queue that keeps an event the EventBridge rule could not deliver to the work queue |
| Receive | One delivery of a message from the work queue to the function. A message that is not deleted becomes visible again after the visibility timeout |
| Receives before the dead letter queue | The `maxReceiveCount` of the redrive policy. With 4, a message gets one first attempt and three retries |
| Visibility timeout | The time a received message stays hidden from other pollers. When it ends without a delete, the message returns to the queue |
| Function timeout | The longest time one invocation may run before Lambda stops it |
| Retry inside the invocation | A repeated call to Rekognition, Bedrock, S3 or DynamoDB by the SDK of the function, before the invocation reports a failure |
| Redrive | Moving the messages of a dead letter queue back to a queue that a function reads |
| Business state | The case, the fumigation order, the published estimate or the reconciliation history that people read and act on |

## 2. Context and volumes

The [inference functions](inference-functions.md) design fixes the parts this policy builds on. Each function has its own work queue and its own dead letter queue. Each result carries an idempotency key, the SHA-256 of the function, subject, exact source object versions, model and prompt version, and a conditional write refuses a second result with the same key. Each function role writes results with `dynamodb:PutItem` and holds no permission to update a case state, an order state or an alert state. The [verification](../drones/post-fumigation-verification.md) design adds the supervisor path after the dead letter queue, so a model outage never blocks the closure of an order.

The figures below are the harvest month volumes of the inference design, turned into messages. One drone message carries one published flight record, and one telemetry message carries one completed archive object.

| Function | Messages in a harvest month | Images or readings in each message | Basis |
|---|---:|---:|---|
| Focus confirmation | 60 | About 50 photos | 60 confirmation missions |
| Verification | 25 | About 20 photos | One mission for each fumigation order |
| Harvest estimation | 50 on average, 200 in a harvest | About 100 photos | One mission for each farm |
| Telemetry batch | Up to 1,440 | About 75 readings | Two stream partitions in each 900-second window |

These are small numbers. A whole harvest month gives the three drone functions about 135 messages, so a dead letter queue with a handful of messages is already a significant event, and the alarms below fire on the first message.

Account concurrency in the demonstration account is 10, and each event source mapping polls with at most two concurrent invocations. A throttled receive also counts as a receive, which matters for the count in section 4.

## 3. The path of a failure

A failure passes through four layers. Each layer retries within its own limits and hands over to the next only when those limits run out.

| Layer | What retries | Limit | What it hands over |
|---|---|---|---|
| SDK inside the invocation | Calls to Rekognition, Bedrock, S3 and DynamoDB that return a transient or throttling error | Standard retry mode, 3 attempts for most services and 4 for DynamoDB, with exponential backoff and jitter | An error to the function code |
| Function | Nothing more. The function logs the failure and reports the message as failed | One invocation | A failed message to the event source mapping |
| Work queue | The whole message, after the visibility timeout ends | 4 receives | The message to the dead letter queue |
| Dead letter queue | Nothing. It keeps the message for a person | Its retention, counted from the first enqueue | The message to an operator, through the alarm |

A non-retryable error, such as `AccessDeniedException` or `ValidationException`, skips the SDK retries and fails the invocation at once. The work queue still retries it, because a missing permission is often fixed by a deployment while the message waits.

The event source mapping reports failures one message at a time with `ReportBatchItemFailures`, and the batch size is 1. A failed message never pulls a healthy message back into the queue with it.

## 4. Retry and dead letter values for each function

| Function | Function timeout | Visibility timeout | Receives before the dead letter queue | Work queue retention | Dead letter retention | Batch size | Concurrent invocations |
|---|---:|---:|---:|---:|---:|---:|---:|
| Focus confirmation | 300 s | 1,800 s | 4 | 4 days | 14 days | 1 | 2 |
| Verification | 300 s | 1,800 s | 4 | 4 days | 14 days | 1 | 2 |
| Harvest estimation | 900 s | 5,400 s | 4 | 4 days | 14 days | 1 | 2 |
| Telemetry batch | 60 s | 360 s | 4 | 4 days | 14 days | 1 | 2 |

The values follow three rules.

The visibility timeout is six times the function timeout. The Lambda guide for SQS asks for at least that much, so a message stays hidden while Lambda retries a throttled invocation, and Lambda refuses a mapping whose function timeout exceeds the visibility timeout.

The function timeout follows the work of one message. Focus confirmation and verification read 20 to 50 photos, each through the person filter and one model call. Harvest estimation builds an orthomosaic in about 5 minutes before its model calls, so it takes the Lambda maximum of 900 seconds. Telemetry batch reads one Parquet object in about 1 second and compares readings with no model call, so 60 seconds leaves a wide margin.

The dead letter queue keeps messages longer than the work queue. A standard queue keeps the first enqueue time of a message when it moves to the dead letter queue, so a message that spent hours in the work queue has that much less time in the dead letter queue. With 4 days in the work queue and 14 in the dead letter queue, an operator has at least 10 days to read a failed message.

The time from the first attempt to the dead letter queue is about four visibility periods, since each failed receive waits out its visibility timeout before the next.

| Function | Time to the dead letter queue |
|---|---|
| Focus confirmation | About 2 hours |
| Verification | About 2 hours |
| Harvest estimation | About 6 hours |
| Telemetry batch | About 24 minutes |

These times fit the business. A reviewer of a focus case or a supervisor of a verification learns of a lasting failure within a working morning, and a harvest estimate is a planning figure for the collection center, read days later.

Three retries after the first attempt are the policy for the four functions. The Lambda guide recommends at least five receives so that throttled receives do not exhaust a message. Here each result is idempotent and a person can work from the stored photos once a message reaches the dead letter queue, so a message that reaches the dead letter queue early costs a redrive and no lost data. The count of messages that reach the dead letter queue in the test environment confirms or corrects this value, and section 11 records it.

The focus confirmation pattern built in the infrastructure code uses these values as its defaults. The other three functions are designed with the same module shape and take their row of the table when they are built.

## 5. What a failure leaves unchanged

Three rules keep the business state safe whatever fails.

1. A function never writes business state directly. Each role holds `dynamodb:PutItem` for its results and no `dynamodb:UpdateItem` on cases, orders or alerts. A state move happens elsewhere, by a person or by a transition function that checks a stored result. A failure inside an inference function therefore cannot leave a half-moved state.
2. A result is stored before any event announces it. The function writes its result with a conditional write on the idempotency key, and only after that write succeeds does it publish `inference.completed` or `verification.result.persisted`. A failure between the two leaves a stored result with no event, and the retry finds the stored result and publishes the event.
3. A retry resumes and never repeats. A message for a flight with 50 photos may fail on photo 31. The next receive computes the same idempotency key for photos 1 to 30, finds their stored results and skips their model calls, and continues from photo 31. A result counts once however many receives the message takes.

| Function | Source object on failure | Business state on failure | What stays stored |
|---|---|---|---|
| Focus confirmation | The photo version stays in `focus/` | The case keeps its state. The reviewer still decides | Photo results already written |
| Verification | The photo version stays in `verification/` | The order stays `VERIFICATION_PENDING`. No attempt result and no `verification.result.persisted` exist | Photo results already written |
| Harvest estimation | The photos stay in `estimation/`, and a partial orthomosaic is overwritten on the next attempt | No estimate reaches the collection center | Person filter outcomes already written |
| Telemetry batch | The Parquet object stays in the archive | No live alert, notification or range changes. Live alerts belong to the ingestion function | Reconciliation items already written, found again by the same key on the retry |

The person filter is the one path that removes a source version, and it is a decision of the filter. A failure inside that path follows the same order. The function copies the object to `restricted/`, verifies the copy, and only then removes the source version. A failure before the removal leaves both copies, and the retry finds the restricted copy and completes the removal. A failure before the copy leaves the source untouched.

When the dead letter queue receives a message, the business state is exactly what it was when the event arrived. The verification supervisor may then record the result from the photos, and a reviewer of a focus case may decide from the stored photos without a model result.

## 6. Events the rule cannot deliver

Before a message reaches a work queue, EventBridge must deliver it. The rule sends each `flight.record.published` event, and each completed archive object event for telemetry, to the work queue through a delivery role. If that send fails, EventBridge retries for up to 24 hours and 185 attempts, and then drops the event. Some errors, such as a missing permission on the queue or its key, skip the retries.

A dropped event is the worst failure of the chain, because nothing downstream knows that work was due. The flight record is published, the photos are stored and no function ever starts.

Each rule therefore has its own rule dead letter queue, a standard SQS queue encrypted with the data key, with a 14-day retention and a queue policy that accepts `sqs:SendMessage` only from `events.amazonaws.com` for that rule. EventBridge adds the rule, the target, the error code and the retry count to each message it stores there. The rule retry policy keeps the default 24 hours and 185 attempts, so a short throttle or outage of SQS recovers without any person.

The module version in use today creates the rule and its target without a rule dead letter queue. Until the module adds it, the rule metric `FailedInvocations` is the signal of an undelivered event, and its alarm in section 7 covers the gap. A saved query also lists flight records published more than one hour ago with no result of the matching function, which finds an event that was lost before the alarm existed.

## 7. Where the error is seen

The table lists every signal of the chain and the alarm that watches it. All are service metrics or logs that exist with no custom metric. The alarm design chooses who receives each alarm and the response.

| Signal | Metric or log | Alarm condition | What it means |
|---|---|---|---|
| Failed invocations | Lambda `Errors` of the function | Sum above 0 in 5 minutes | A receive failed. It may still succeed on a retry, so it reads as a warning |
| Messages in the dead letter queue | SQS `ApproximateNumberOfMessagesVisible` of the dead letter queue | Maximum above 0 in 5 minutes | Work stopped after its retries. A person must act |
| Events the rule could not deliver | EventBridge `FailedInvocations` of the rule | Sum above 0 in 5 minutes | An event did not reach the work queue |
| Events in the rule dead letter queue | SQS `ApproximateNumberOfMessagesVisible` of the rule dead letter queue | Maximum above 0 in 5 minutes | An undelivered event is kept for a person. This alarm replaces the previous one once the queue exists |
| Age of the oldest message in the work queue | SQS `ApproximateAgeOfOldestMessage` of the work queue | No alarm. Read during an incident | Work is waiting longer than its retries explain, often because of throttling |
| Failed invocation that left the state unchanged | Operational log entry with `event_name` `inference.failed`, `outcome` `error`, `error_code`, the receive count and the subject identifiers | No alarm. Saved query | Which cases, orders or flights a failure touched, and proof that their state did not move |

The first two alarms exist in the infrastructure code for the focus confirmation pattern, with a 5-minute period and a threshold of zero. The alarm on `FailedInvocations` and the rule dead letter queue belong to the next version of the same module.

The operational log entry of a failure carries `case_id` or `order_id`, `mission_id` and `execution_id` where they apply, so an operator can open the case or order and confirm its state without reading any personal field. The [observability design](observability.md) defines these identifiers and the fields of an operational log.

A failure that leaves the business state unchanged is shown by two facts together. The message sits in a dead letter queue, and the case or order it names is still in the state it had before. The saved query joins the failure entries with the current state of each subject.

## 8. Sending the work back after a fix

An operator reads the message in the dead letter queue, which holds the flight record identifiers or the archive object key. The cause is in the operational log of the function, found by the same identifiers. Once the cause is fixed, the operator starts a dead letter queue redrive back to the work queue.

| Step | What the operator does | Why it is safe |
|---|---|---|
| 1 | Reads the message and the failure entries in the log | Reading changes nothing |
| 2 | Fixes the cause, such as a permission, a quota or a code release | The message waits up to its remaining retention |
| 3 | Starts the redrive from the dead letter queue to the work queue, with a low rate for a large batch | The idempotency key returns stored results, so a repeated message adds no duplicate |
| 4 | Watches the dead letter queue empty and the results appear | A message that fails again returns to the dead letter queue with a fresh retention |

A redrive gives each message a new identifier and a new enqueue time, so a message that fails again has its full retention. The person who redrives needs `sqs:StartMessageMoveTask`, `sqs:ReceiveMessage`, `sqs:DeleteMessage` and `sqs:GetQueueAttributes` on the dead letter queue, `sqs:SendMessage` on the work queue, and `kms:Decrypt` and `kms:GenerateDataKey` on the data key.

An event in a rule dead letter queue is sent back the same way to the work queue of its rule. The message body is the event that EventBridge would have delivered. Whether the move task accepts a rule dead letter queue as its source is confirmed in the test environment. Until then, the operator receives each message, sends its body to the work queue and deletes it.

For verification, the supervisor path may make the redrive unnecessary. Once a supervisor records the result by hand, a later automatic result for the same attempt is stored as evidence and moves nothing, because the order has already left `VERIFICATION_PENDING`.

## 9. Cost

Rates come from the AWS Price List API for us-east-1, as used in the inference and observability designs.

| Item | Rate |
|---|---:|
| CloudWatch alarm on a standard metric | USD 0.10 a month |
| SQS standard requests | USD 0.40 per million |
| One image through the person filter and the model | USD 0.0017524 |

Each function carries three alarms, the failed invocations, the dead letter queue and the undelivered events. Four functions give 12 alarms, USD 1.20 a month. The pattern built today has two alarms, USD 0.20, and the third adds USD 0.10. The rule dead letter queues add no fixed cost, since an empty SQS queue is billed only by its requests.

Retries repeat only the work that did not store a result. If 1 percent of the 8,500 images of a harvest month fails on every one of its 4 receives, the three extra attempts cost 3 x 85 x 0.0017524, USD 0.45. A message that fails before any model call, such as a missing permission, costs only queue requests and a short invocation.

The alarm count matters for the telemetry budget. The [observability design](observability.md) records that the harvest month already sits above its reference before alarms, and the alarm design decides whether the per-function alarms remain separate or are merged by metric math into fewer alarms.

## 10. Alternatives discarded

| Alternative | Why it was discarded |
|---|---|
| One receive and straight to the dead letter queue | A throttle or a short outage of Bedrock would stop the work and call a person for a fault that clears in seconds |
| Five or more receives | It follows the general Lambda recommendation, and it delays the supervisor and the reviewer by another visibility period with no data gained, since results are idempotent and a redrive is cheap. It stays the first change if throttled receives fill the dead letter queues in test |
| No dead letter queue, relying on retention | A message would vanish when its retention ends, with no alarm and no record of the work that never ran |
| One dead letter queue for all functions | A failure of one function would hide the failures of the others, and a redrive could not target one work queue |
| Retries inside the function code with a loop | It holds compute while it waits, multiplies the invocation time and hides the failure from the queue metrics |
| Direct delivery from EventBridge to Lambda | It mixes delivery failures with processing failures and removes the queue as the single place where work waits |
| Dropping the rule dead letter queue and relying on the 24-hour retry | Errors such as a missing permission are never retried, and after the retries the event is lost with no copy |

## 11. Assumptions and pending confirmations

| Assumption | Why it is reasonable | If false | Confirms |
|---|---|---|---|
| Three retries are enough with two concurrent invocations under an account concurrency of 10 | The volumes are small and the SDK already retries throttles inside each invocation | Messages reach the dead letter queue after throttling, and the count rises to five receives | Platform operator, from the dead letter queues in the test environment |
| 300 seconds cover one focus confirmation flight of about 50 photos, and 900 seconds one orthomosaic | About 5 seconds for each photo through the filter and the model, and 5 minutes for the orthomosaic in the cost analysis | Invocations time out and retry from where they stopped. The function timeout and the visibility timeout rise together | Platform operator, from the duration of the first flights in test |
| A move task accepts the rule dead letter queue as its source, with the work queue as the destination | The redrive accepts a custom destination of the same queue type | The operator resends the events by receiving, sending and deleting each one | Platform operator, on the first undelivered event in test |
| A message body in the rule dead letter queue is the event the work queue would have received | EventBridge stores the event and adds its error details as message attributes | The resend reshapes the body before sending it | Platform operator, on the first undelivered event in test |

## 12. Sources

- [Lambda with SQS, configuring the queue and the event source mapping](https://docs.aws.amazon.com/lambda/latest/dg/services-sqs-configure.html), visibility timeout of six times the function timeout and the receive count recommendation.
- [Lambda, partial batch responses for SQS](https://docs.aws.amazon.com/lambda/latest/dg/services-sqs-errorhandling.html), failures reported for each message.
- [SQS dead letter queues](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html), `maxReceiveCount`, the first enqueue time and the retention of a dead letter queue.
- [SQS dead letter queue redrive](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-configure-dead-letter-queue-redrive.html), move tasks, custom destinations, the reset of retention and the permissions of a redrive.
- [EventBridge retry policy](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-rule-retry-policy.html), 24 hours and 185 attempts, and the event dropped after them.
- [EventBridge dead letter queues for targets](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-rule-dlq.html), the errors sent with no retry, the message attributes and the queue policy.
- [AWS SDK retry behavior](https://docs.aws.amazon.com/sdkref/latest/guide/feature-retry-behavior.html), standard mode, attempts for each service and the errors it retries.
- AWS Price List API for [CloudWatch](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonCloudWatch/current/us-east-1/index.json) and [SQS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AWSQueueService/current/us-east-1/index.json), us-east-1.
- [Inference functions](inference-functions.md), [verification after fumigation](../drones/post-fumigation-verification.md), [observability](observability.md) and [telemetry ingestion](../iot/telemetry-ingestion.md) of this platform.
