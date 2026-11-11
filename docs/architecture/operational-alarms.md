# Operational alarms and response routes

This document lists the alarms that tell an operator that the pilot needs attention before a farmer is affected. For each alarm it names the signal, the condition, who answers, the first action and the route of the notice. It covers nodes and farms without telemetry, crop alerts that were not delivered, flights without a record, fumigations that cannot close, and inference invocations that failed and left the state unchanged. It also separates what the platform detects by itself from what a person finds by reading a daily list, and it counts the cost of the whole set against the reference of the cost document. It is a design. No alarm, topic or rule was created, and the checker described in section 12 verifies the register as written and not an account. Rows come in two kinds. A documented row restates a rule that a merged design already sets. An adopted row covers something that no merged design settles. It is adopted by the author of this design as an academic design assumption, carries its mechanism, its threshold and the assumption behind it, and is not a rule approved by the owners of the designs it touches.

## Contents

1. Terms
2. What is reused
3. Three ways to notice a problem
4. Register of alarms
5. Failed invocations that left the state unchanged
6. Slow live alerts and the live-only metric
7. Flights without a record and orders that do not close
8. Owners and routes
9. Cost
10. What the alarms do not see
11. Decisions that belong to the owners
12. What the checker proves
13. Assumptions and pending confirmations
14. Sources

## 1. Terms

| Term | Meaning in this document |
|---|---|
| Alarm | A CloudWatch metric alarm that changes state by itself and notifies. It is billed as an alarm metric |
| Event rule | An EventBridge rule that matches an event the platform publishes and sends a notice. It has no alarm charge |
| Daily review | A saved query that a person reads each day. It detects nothing by itself and sends no notice |
| Answering role | The role of the access design that receives the notice and acts first |
| Second role | The role that acts when the first one cannot, or that decides after the first has looked |
| Documented | A rule that a merged design already sets |
| Adopted | A row that no merged design settles and that the author of this design adopts as an academic assumption. Its threshold is an assumption, and its operational validation is pending before deployment |
| Urgent | A farmer, a flight or the data path is affected now |
| Routine | The platform needs attention and nobody is harmed yet |

## 2. What is reused

The signals and identifiers come from the observability design, and its chosen telemetry limits what an alarm can watch. That telemetry keeps six custom metrics, which are the silent nodes, the time from reading to handoff, the undelivered alert, the undelivered SMS, the gaps and anomalies together, and the failed or limited runs of the deletion job. Every other signal is read by a query, so no alarm in this document sits on one of them. No dashboard of our own exists, so no action sends an operator to one.

| Document | What this design takes from it |
|---|---|
| [Observability](observability.md) | The signal catalog, the identifiers of an operational log and the chosen telemetry |
| [Failure policy](failure-policy.md) | The retries, the dead letter queues and the three alarms of each inference function |
| [Telemetry ingestion](../iot/telemetry-ingestion.md) | Silent nodes over 24 hours, the age of the queue and the dead letter queue |
| [Alert delivery](../iot/alert-delivery.md) | The undelivered alert, the slow live alert and the SMS that was not delivered |
| [Flight objects](../drones/flight-objects.md) and [fumigation order](../drones/fumigation-order.md) | The events of the flight record, the states of the order and what an open order means |
| [Recovery](recovery.md), [persistence and archive](persistence-and-archive.md) and [delivery pipelines](delivery-pipelines.md) | Alarms that those designs already promise |
| [Identity and access](../security/identity-and-access.md) | The roles that can answer |
| [Cloud cost](../governance/cloud-cost.md) | The reference of USD 2.20 a month for alarms and platform logs |

## 3. Three ways to notice a problem

The register uses three kinds of row, and the difference matters when a person reads it.

| Kind | Who detects | When the notice arrives | Cost |
|---|---|---|---|
| Alarm | The platform, from a metric | Within the evaluation period of the alarm | USD 0.10 a month for each alarm metric |
| Event rule | The platform, from an event | When the event is published | No alarm charge, with the notification charges of section 9 |
| Daily review | A person, from a saved query | When the person reads the list | Inside the query allowance of the observability design |

A daily review is never counted as an alarm. Where the documents define no event and no deadline for a state, the register offers a review and says so.

## 4. Register of alarms

The register holds 32 rows. Rows that other designs already promise are listed too, so that the owners and the cost are complete.

### Nodes and farms without telemetry

| Id | Alarm | Kind | Condition | Answers | Severity |
|---|---|---|---|---|---|
| AL-01 | Nodes silent over 24 hours | Alarm on the silent node metric | The metric is above 0 in the daily check | Platform operator | Routine |
| AL-02 | Silent vereda on the LoRa path | Alarm promised by the LoRa design | The document names no metric or event that carries it | Platform operator | Routine |

The metric counts nodes and takes no identifier as a dimension, since an identifier would create one metric for each node. A silent farm is a farm whose nodes are all silent, and the first action of AL-01 is to run the saved query that lists the silent nodes by farm. The alarm detects, and the list finds the farm. The check that publishes the metric runs once a day, so a day without the check is itself a gap. The alarm therefore treats missing data as a breach, which CloudWatch allows for a metric that should report continually.

AL-02 is counted as no alarm until the LoRa design names the metric or event that reports a silent vereda. That is an open point.

### Crop alerts not delivered

| Id | Alarm | Kind | Condition | Answers | Severity |
|---|---|---|---|---|---|
| AL-03 | Alert not delivered | Alarm | The undelivered alert metric sums above 0 in 5 minutes | Platform operator | Urgent |
| AL-04 | Slow live alert | Alarm | The handoff time of a live alert has a maximum above 300 seconds in 5 minutes | Platform operator | Routine |
| AL-05 | SMS of an urgent alert not delivered | Alarm | The SMS metric sums above 0 in 5 minutes | Platform operator | Urgent |
| AL-06 | Delivery check queue dead letter | Alarm | Messages visible above 0 in 5 minutes | Platform operator | Urgent |

AL-03 and AL-05 publish a value only when a bad event happens, so they treat missing data as good. AL-06 matters because a failure of the delivery check removes both the SMS and the missing-handoff metric for the alerts it holds, and the latency metric then becomes the only signal.

### Flights without a record, fumigations without a closure

| Id | Alarm | Kind | Status | Answers | Second |
|---|---|---|---|---|---|
| AL-09 | Object rejected at verification | Event rule | Documented, the event exists | Platform operator | Drone supervisor |
| AL-10 | Flight record needs review | Event rule | Documented, the event exists | Drone supervisor | Platform operator |
| AL-11 | Flight whose log never arrives, interim review | Daily review | Documented states, no age | Platform operator | Drone supervisor |
| AL-12 | Fumigation that cannot close, interim review | Daily review | Documented states, no age | Platform operator | Drone supervisor |
| AL-33 | Flight object verification, messages in the dead letter queue | Alarm | Adopted | Platform operator | None |
| AL-34 | Flight object verification, failed invocations | Alarm | Adopted | Platform operator | None |
| AL-35 | Flight completion, failed invocations | Alarm | Adopted | Platform operator | Drone supervisor |
| AL-36 | Fumigation log overdue | Event rule fed by a schedule | Adopted | Drone supervisor | Platform operator |
| AL-37 | Package past its window with no flight record | Event rule fed by a schedule | Adopted | Drone supervisor | Platform operator |
| AL-38 | Order waiting too long to close | Event rule fed by a schedule | Adopted | Drone supervisor | Platform operator |

The documented rows are the two events that the flight object design publishes and the states that the order design defines. AL-11 and AL-12 are the review that stays available until the adopted rows are built. Section 7 sets out the adopted rows, and section 5 explains why AL-33 to AL-35 belong to this criterion.

### Failed invocations and other alarms already promised

| Ids | Alarm | Kind | Source |
|---|---|---|---|
| AL-13 to AL-24 | Three alarms for each of the four inference functions | Alarm | The failure policy, section 5 below |
| AL-07, AL-08 | Ingestion dead letter queue and queue age | Alarm | Telemetry ingestion |
| AL-25, AL-26 | Failed writes and throttled requests of the sack tables | Alarm | Recovery |
| AL-27 | Deletion job failed or limited | Alarm | Persistence and archive |
| AL-28 to AL-30 | Errors of the three telemetry functions during a release | Alarm | Delivery pipelines |
| AL-31, AL-32 | Key state change and point-in-time recovery turned off | Event rule | Recovery |

The first action of each row is in the table of section 8.

## 5. Failed invocations that left the state unchanged

The failure policy of the inference functions is part of the integrated documents. Four functions, focus confirmation, verification, harvest estimation and telemetry batch, each have a work queue, a dead letter queue and four receives before a message moves. A failed invocation leaves the source object where it was and the case, order or estimate in the state it had. The policy defines three alarms for each function, and this register takes them as they stand.

| Alarm of each function | Condition | Reading |
|---|---|---|
| Failed invocations | Lambda `Errors` sum above 0 in 5 minutes | A receive failed and may still succeed on a retry. Routine |
| Messages in the dead letter queue | Messages visible above 0 in 5 minutes | Work stopped after its retries and a person must act. Urgent |
| Events the rule could not deliver | EventBridge `FailedInvocations` of the rule sums above 0 in 5 minutes | An event never reached the work queue. Urgent |

Twelve alarms follow, at USD 1.20 a month. The first two of the focus function exist in the infrastructure code. The third alarm and the rule dead letter queue belong to the next version of the function module, and until then the rule metric is the signal of an undelivered event.

That a failure left the state unchanged is shown by two facts together, a message in a dead letter queue and a case or order still in the state it had. The saved query of the failure entries joins both, and no alarm is placed on that query.

### Which functions the criterion requires

The criterion asks for failed invocations that did not change the state. That describes a function whose failure leaves a case, an order or an estimate as it was, and whose work waits in a queue for a person. Read that way, the functions that matter are these.

| Function | Failure leaves the state unchanged | Alarm today | Required by the criterion |
|---|---|---|---|
| The four inference functions | Yes, by the failure policy | Three alarms each, AL-13 to AL-24 | Yes, covered |
| Flight object verification | Yes. The object stays unverified, the flight keeps waiting and the message goes to its dead letter queue | None in any document, and no retry count is set for its queue | Yes. AL-33 and AL-34 are adopted |
| Flight completion | Yes. A failed completion publishes no record, and the station repeats the request | None | Yes, because its failure is a flight without a record. AL-35 is adopted |
| Ingestion and alert delivery | Their own state, readings and alerts, and no case or order | Queue age and dead letter queues, AL-06 to AL-08 | No. They already have alarms |
| Custody write function | The conditional write refuses or applies, and the sender retries | None needed for this criterion | No |
| Order transition function | Every move is one conditional write, and a denied move is audited | Not a failure in the queue sense | No |

The flight object verification function runs from a queue with a dead letter queue, so it is the one function outside the inference set that the criterion reaches. The failure policy does not cover it and no document sets its retry count or its alarm. The adopted rows use the condition that two merged documents already use for a dead letter queue, which is any message, and set no retry value. The retry count of that queue belongs to the owner of the flight object design.

## 6. Slow live alerts and the live-only metric

The alert delivery design raises the slow live alert when a live alert takes more than 5 minutes from reading to handoff, and it emits the handoff time with the dimensions `kind` and `link`. The chosen telemetry keeps that metric without dimensions. A drained alert, which comes from a buffered reading, may take up to 24 hours, and an alarm on a metric with no `kind` would fire for every one of them.

The design adopts that the alert function publishes the handoff time as a metric for live alerts only, with no dimension, and writes the time of a drained alert to the log. The single metric of the chosen telemetry stays one series, and the alarm AL-04 reads only live alerts.

| Check | Result |
|---|---|
| The service level objectives | They measure alert delivery with saved queries over the alert record and add no metric. They are unaffected, and drained alerts keep their own 24 hour figure from the same query |
| The chosen telemetry | It keeps one handoff metric with no dimensions. A live-only metric is that metric, so the series count and the cost do not change |
| The alert delivery design | It states the dimensions `kind` and `link`, and a dashboard fed by the metric. Both differ from the chosen telemetry already, and the live-only rule changes one more instruction of that design |

This is a change to the instruction of the alert function, whose design belongs to another document, so the register records it as an adopted assumption that the owner of that design has not reviewed. The instruction of the alert function changes before deployment.

## 7. Flights without a record and orders that do not close

### What the documents fix

| Fact | Where |
|---|---|
| The platform publishes `flight.object.rejected` and `flight.record.review_required`, so both can drive an event rule | Flight objects |
| An order whose log never arrives stays in `EXECUTED_PENDING_SYNC`, and an order whose verification file is missing or whose function failed stays in `VERIFICATION_PENDING` and cannot close | Fumigation order and verification |
| An order closes only in `CLOSED`, and the only way into it passes through `VERIFIED` by a supervisor | Verification |
| Every move of an order writes a `fumigation.transition` event with the order, the states and the time | Fumigation order and audit |
| A one-time schedule at the end of the order window moves the order to `EXPIRED` through the same transition function | Fumigation order |
| A package carries its own execution window, with a ceiling of 12 hours for a fumigation and 72 hours for other missions | Drone mission link |
| The verification window opens at the end of the application plus the waiting time the supervisor sets | Verification |

No document sets a time by which a log must reach the platform or by which an order must close, and no event reports either state. The 72 hours of the order window and of the other missions are the time in which a flight may take place. They begin when the window opens and say nothing about when a record must arrive, so no row uses them.

The audit events sit in the log archive account, and the platform operator holds no access there. A saved query over them is therefore not a mechanism the operator can run, and the order list of the application is the only documented view of order states. The order design says that a dashboard reports a log that never arrives, without saying whether that is an application view or an operations dashboard. The chosen telemetry has no operations dashboard.

### What is adopted

The design reuses the scheduler that the order design already uses for the end of the order window. It adds no alarm and does not touch the six metrics of the chosen telemetry.

| Case | Signal | Mechanism | Threshold, an assumption | Answers | First action |
|---|---|---|---|---|---|
| A fumigation flight log never arrives, AL-36 | The order is still in `EXECUTED_PENDING_SYNC` | The transition function creates a one-time schedule when it moves the order into the state. At the check it reads the order, and if the state and revision are unchanged it publishes one platform event that an event rule sends to the topic. A changed state makes the check do nothing | First check 24 hours after the order entered the state, second at 48 hours | Drone supervisor, then platform operator | Ask the brigade whether the station holds the log and whether the link has returned, look for events of the execution, and run the incident procedure if the station is lost |
| Any other flight has no record, AL-37 | A package whose execution window ended with no `flight.record.published` and no `flight.record.review_required` for its `package_id` | The package function creates a one-time schedule at the end of the package window plus the grace, and the check looks for a record of the package | 24 hours after the end of the package window | Drone supervisor, then platform operator | Ask the brigade whether the flight took place. A package that was never flown shows here too and the brigade closes the item |
| An order does not close, AL-38 | The order is still in `SYNC_REVIEW_REQUIRED`, `PARTIAL`, `VERIFICATION_PENDING` or `VERIFIED` | The same schedule, created when the order enters each state. In `VERIFICATION_PENDING` the time counts from the end of the window of the latest verification package | 24 hours after the order entered the state or the verification window ended, second check at 48 hours | Drone supervisor, then platform operator | Open the order and find what it waits for. Decide the record in review, check the verification file and the function in verification, and review and close in verified |

The new events are `order.attention_required` and `flight.package.overdue`. No document defines them, so they exist only in this design. The checker fails if either name appears in another document, which tells the author that the assumption has become a design of another owner and that this row must be reconciled.

### A sync gap and a technical failure

The two are different and the register keeps them apart. A sync gap is the absence of something that should have arrived. Nothing failed that the platform can see, a link or a station may simply be late, so the platform waits and uses the 24 and 48 hour checks. A technical failure is something that arrived and failed, so it notifies at the first event, with no waiting period.

| Kind | Rows | When the notice arrives |
|---|---|---|
| Sync gap, nothing has arrived | AL-36, AL-37 and the log or package part of AL-38 | After the 24 hour check, and again at 48 hours |
| Technical failure, something arrived and failed | AL-09, AL-10, AL-33, AL-34, AL-35 and the inference alarms AL-13 to AL-24 | At the first event or the first failed invocation |
| Waiting for a person, the platform did its part | The review, verification and close states of AL-38 | After the 24 hour check, and again at 48 hours |

### Rules of the merged designs and assumptions of this design

| Set by a merged design | Assumed here |
|---|---|
| The states, the exits and the events listed above | The 24 and 48 hour checks |
| The scheduler pattern for the end of the order window | That the scheduler pattern extends to the states of this section |
| The roles that answer | That the drone supervisor answers first and the platform operator second |
| The dead letter queue condition of any message | That it applies to the flight object verification queue |
| | The two event names and the new checks of the transition function and the package function |

The cost of the mechanism is small. About 25 orders a month in a harvest month, with three states and two checks each, give a few hundred scheduled invocations, and the first 14 million a month are free. The events add custom event charges of USD 1.00 per million and the notices count toward the email allowance, so the mechanism adds no alarm and no measurable charge, and it adds work to two functions that other designs own.

Until the owners accept this, AL-11 and AL-12 remain. They list the same states as a daily review with no age, and they need the order list of the application to show each order with the time it entered its state. That requirement is not verified in the documents.

## 8. Owners and routes

The answering roles come from the access design. The platform operator is Federation technical staff who operate the platform and hold no read on business data. The drone supervisor is the Federation supervisor of a department, in the supervisor group of the drone operator role.

| Id | First action |
|---|---|
| AL-01 | Run the saved query of silent nodes by farm, tell a silent farm from a silent node, then check the gateway and the vereda before asking the Federation to contact the installer |
| AL-02 | Read the connection state of the gateway at the network server and check its power and backhaul |
| AL-03 | Open the alert by its identifier, read the push status and the SMS status in the log, and check whether the farm has a registered phone |
| AL-04 | Read the stage times of the alert record to see whether the wait was in the queue, the function or SNS |
| AL-05 | Read the SMS status of the alert and ask the Federation to reach the farmer by another way |
| AL-06 | Redrive after the cause is fixed, knowing that the alerts it holds have no SMS and no missing-handoff metric |
| AL-07 | Read the failed message and the function log, fix the cause and redrive |
| AL-08 | Check the consumer, its throttles and the account concurrency |
| AL-09 | Open the quarantine key from the event and tell the station to upload the object again under the same key |
| AL-10 | Open the order in review, read the reason of the event and decide whether to accept the record or ask for a new upload |
| AL-11 | Read the daily list and pass each order to the drone supervisor, who asks the brigade whether the station holds the log and whether the link has returned |
| AL-12 | Read the daily list and check whether the verification file exists and whether the function failed. The drone supervisor records the result by hand if needed |
| AL-13, AL-16, AL-19, AL-22 | Read the failure entry of the log by case, order or flight identifier and check that the state did not move |
| AL-14, AL-17, AL-20, AL-23 | Fix the cause and redrive the work queue. For verification the supervisor may record the result by hand meanwhile |
| AL-15, AL-18, AL-21, AL-24 | Read the rule dead letter queue once it exists, otherwise the saved query of flight records with no result |
| AL-33 | Read the failed message and the function log, fix the cause and redrive. The object stays unverified and the flight keeps waiting for it |
| AL-34 | Read the failure entry by execution identifier and check that the object is still unverified. It may still succeed on a retry |
| AL-35 | Read the failure entry by execution identifier. The station repeats the completion request, and a repeat finds the stored record, so check that a record is published |
| AL-36 to AL-38 | The first action of the table in section 7 |
| AL-25 to AL-32 | Follow the recovery, persistence and release steps of their own designs |

Where the action says to read a case, an order or a flight, the platform operator reads identifiers, states and error codes from the operational log. The content of a case belongs to the drone supervisor, since the platform operator holds no read on business data.

### Route

The channel that the documents already name is an operations mailbox, with an SNS topic per environment and the addresses passed at run time, as the budget alerts use. Every alarm and event rule sends to that topic, and urgent rows are marked so a filter can separate them. The supervisor also sees a flight in review in the review state of the order, which is the route that the flight design gives. The real mailboxes are not in the repository and the Federation confirms them. No pager, no call and no on-call hours are defined, so the document promises no response time.

## 9. Cost

Prices are from the AWS Price List API for us-east-1, publication of 2026-11-04 for CloudWatch, 2026-11-08 for EventBridge and 2026-11-04 for SNS. The totals below apply no free tier to CloudWatch alarms, metrics or logs, and none to X-Ray. They do leave out the small charges of the event rules, the schedules and the notices, which fall inside the free allowances of EventBridge Scheduler and SNS email at the volumes of this section. Without those allowances they would add about USD 0.02 a month. The next table lists each allowance.

| Item | Rate and allowance |
|---|---|
| Standard metric alarm | USD 0.10 a month for each metric in its expression |
| Composite alarm | USD 0.50 a month, added to the alarms it combines |
| Custom event on the platform bus | USD 1.00 per million received, billed to the publisher |
| SNS email notification | First 1,000 a month free, then USD 2.00 per 100,000 |
| SNS requests | First 1,000,000 a month free, then USD 0.50 per million |
| EventBridge Scheduler | First 14 million scheduled invocations a month free, then USD 1.00 per million |

The volumes assumed for the small charges are 150 scheduled checks a month, which is 25 orders in a harvest month with three waiting states and two checks each, 300 platform events, 1,000 email notices and 1,000 SNS requests.

The price list holds no charge for an event rule or for an invocation of a target in the same account, so an event rule adds no alarm charge. That is not the same as free. The events it matches are custom events that the platform bus already bills at USD 1.00 per million, and each notification counts toward the email allowance. Below 1,000 email notifications a month the notices add nothing, and each 1,000 above that adds USD 0.02.

Merging alarms does not lower the cost. The CloudWatch pricing page bills a metric alarm for each metric listed in its expression, up to 10 with metric math, so one alarm over four metrics costs as four. A composite alarm adds USD 0.50 to its parts.

| Item | Count | USD a month |
|---|---|---|
| Alarms in merged documents | 25 | 2.50 |
| Adopted alarms for the flight object functions | 3 | 0.30 |
| Alarms with the adopted rows | 28 | 2.80 |

| Month | Telemetry before alarms | Total with documented alarms | Above the reference | Total with the adopted rows | Above the reference |
|---|---|---|---|---|---|
| Normal month | 2.13 | 4.63 | 2.43 | 4.93 | 2.73 |
| Harvest month | 2.55 | 5.05 | 2.85 | 5.35 | 3.15 |

The telemetry figure is the chosen telemetry of the observability design at list price, with its custom metrics, logs, queries and traces. The reference of USD 2.20 is a reference and not an accepted budget. The documented alarms and the telemetry together are USD 2.43 above it in a normal month and USD 2.85 above it in a harvest month, and the adopted rows raise that by USD 0.30. The figures depend on which alarms the team keeps, and the three adopted event rules add no alarm. The levers are to drop the routine alarms on failed invocations, which are four and USD 0.40, to let the release alarms and the error alarms of the same functions watch one metric, or to raise the reference. The team decides. The cost document is not changed.

The daily reviews are Logs Insights queries and fall inside the 2 GB a month of scanned data that the observability design assumes.

## 10. What the alarms do not see

| Case | Why it is not seen | What shows it |
|---|---|---|
| A farm with no node alarm because one of its nodes still reports | The alarm counts nodes and not farms | The saved query by farm |
| A flight whose log never arrives | No event and no deadline exist in the merged designs | The interim review, or the adopted schedule check once it is built |
| A center that is open and has no sacks | It looks like a closed center | The usual silence of each center, which is not known |
| A provider link down while the firewall holds a tunnel | The cloud sees a down tunnel only | The tunnel metric and the events of the center |
| Failures of the custody write function, the order transition function and the alert functions | They are outside the criterion, since a failure there either keeps the sender retrying or already has an alarm | Their own error metrics and the audit events |

## 11. Adopted decisions and pending validation

### Adoption

On 2026-11-11 the following were adopted by the author of this design as academic design assumptions.

1. The handoff metric for live alerts only, with no dimension.
2. The scheduled checks and the events `order.attention_required` and `flight.package.overdue` to detect missing flight records and orders that do not close.
3. The ages of 24 and 48 hours, as assumptions, for sync gaps and waiting states.
4. The alarms AL-33 to AL-35 for flight object verification and completion, with the condition of any message or any error.

The adoption is that of the author of this design. It is not an approval by the owners of the fumigation order, flight object or alert delivery designs, by the team or by the drone supervisor. Those designs have not been changed, and operational validation is pending before deployment.

### Pending before deployment

| Item | Who validates | Why it is not needed to complete the design |
|---|---|---|
| The instruction of the alert function emits the live-only metric | Owner of the alert delivery design | The register states the rule and no literal criterion depends on it |
| The schedule, the two events and the checks are added to the order and flight object designs and code | Owners of the fumigation order and flight object designs | The register defines signal, mechanism, threshold, answering role and action |
| The ages of 24 and 48 hours | Drone supervisor | They are assumptions, and the checks use the ages the supervisor sets |
| The retry count and the redrive of the flight object verification queue | Owner of the flight object design | The alarm uses the condition of any message and needs no retry value |
| The real mailboxes of the operations topic | Federation | Criterion 4 asks for an owner and an action, and the addresses are passed at run time |
| The alarms kept against the reference | Team and owner of the cost document | A decision on cost and not a criterion |
| One metric for failed and limited deletion runs | Owner of the persistence design | Not a criterion |
| The source of the silent vereda signal | Owner of the LoRa design | Not a criterion. The silent nodes alarm covers the farms of a vereda after 24 hours |

## 12. What the checker proves

`tools/alarms_catalog.py` reads the register and the documents it cites. It fails when an alarm has no signal in the catalog, no condition, no action or a role outside the access design, when an alarm sits on a metric that the chosen telemetry reads by a query, when a daily review is billed or named as an alarm or states an age that no document defines, when an adopted row lacks its mechanism, its threshold or an assumption as basis, when a documented row carries an adopted threshold, when an adopted event name appears in another document, when a row takes a time from the 72 hour window, when an action sends the operator to a dashboard, when the failure policy no longer gives three alarms to each of four functions, and when a cited document stops naming what the row cites. It prints the register and the cost from the same rows.

It checks the register as written. It does not prove that any alarm, topic or rule exists, and it measures no traffic.

## 13. Assumptions and pending confirmations

| Item | Who confirms | Effect if it fails |
|---|---|---|
| The alert function publishes the handoff metric for live alerts only | Owner of the alert delivery design | AL-04 fires on drained alerts, or the dimension `kind` is added at one more series |
| The real mailboxes of the operations topic | Federation | No notice reaches anyone when the platform operates. The design is complete without them |
| The age at which an open order or a missing log becomes a notice, adopted as 24 and 48 hours | Drone supervisor | The two daily reviews stay manual |
| The schedule mechanism and the events `order.attention_required` and `flight.package.overdue` | Owners of the order and flight object designs | The checks do not exist and the reviews stay |
| The order list of the application shows each order with the time it entered its state | Owner of the order design | The interim review has nothing to read |
| The flight object verification queue takes the condition of any message | Owner of the flight object design | AL-33 takes its retry count and alarm |
| The source of the silent vereda signal | Owner of the LoRa design | AL-02 stays defined and unbuilt |
| One metric for failed and limited deletion runs can serve both conditions of the design | Owner of the persistence design | One more metric or one alarm less |
| Failures of functions outside the inference set | Team | Those functions have no consolidated failure policy |
| The number of alarms the team keeps | Team and owner of the cost document | The total moves USD 0.10 for each alarm |
| Fewer than 1,000 email notifications a month | Operator practice | Each 1,000 above adds USD 0.02 |

## 14. Sources

| Source | Used for |
|---|---|
| Amazon CloudWatch user guide, alarms and how they treat missing data, read 2026-11-11 | Missing data options for a metric that reports on events and for one that should report always |
| Amazon CloudWatch pricing page, read 2026-11-11 | Alarm billing for each metric in an expression, and the composite alarm |
| AWS Price List API, CloudWatch, EventBridge and SNS, us-east-1 | Alarm, custom event, email notification and request prices |
| The integrated designs of section 2 | Signals, conditions, roles and failure values |
