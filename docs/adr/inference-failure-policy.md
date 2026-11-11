# A failed inference retries three times, waits in its own dead letter queue and never moves business state

## Context

When an inference invocation fails, the source object must stay and the case must keep its state, and the design must say how the platform retries, where failed work goes and where the error is seen. Each inference function already has a work queue, a dead letter queue, an idempotency key and a role that cannot update a case or an order. Three choices remained open. They were the number of receives before the dead letter queue, what happens to an event that EventBridge cannot deliver to the work queue, and where the policy is written.

## Options

For the receives, four, which is the first attempt and three retries and matches the module and the design documents, or five, which the Lambda guide for SQS recommends. For an undelivered event, a dead letter queue on each rule with its alarm, or only an alarm on the rule metric of failed deliveries. For the place, a document of its own or a new section of the inference design.

## Decision

Every inference function receives a message four times before its dead letter queue, with a visibility timeout of six times the function timeout and a dead letter retention of 14 days against 4 days in the work queue. Each rule has its own dead letter queue and an alarm on it, with the alarm on failed deliveries until the module adds that queue. Results are stored before any event announces them, and a retry resumes from the first photo with no stored result. The policy lives in its own document in the architecture folder, and the observability catalog gains the undelivered events and the failure entry of the log.

## Consequences

A failed invocation reaches the dead letter queue in about two hours for focus and verification, six hours for harvest estimation and 24 minutes for telemetry, with the business state as it was, and an operator sends it back after a fix with no duplicate result. A throttled receive also counts, so the test environment confirms whether four receives are enough, and five is the first change if they are not. Each function carries three alarms, 12 in all at USD 1.20 a month, and the alarm design decides whether some are merged. The inference module needs a new version with the rule dead letter queue and its alarm.
