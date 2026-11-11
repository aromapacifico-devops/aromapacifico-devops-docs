# Service level objectives

The platform makes two promises that the Federation can check. A farmer receives a crop alert within five minutes of the reading that caused it, and a buyer who scans a sack gets an answer. This document turns each promise into a service level objective, defines the indicator that measures it, the window, the source of every number and the error budget, and says what the team does when the budget runs out.

## Contents

1. Context and volumes
2. Crop alert delivery
3. Availability of the sack query
4. Error budget policy
5. Measurement and reporting
6. Alternatives considered
7. What fails and what happens then
8. Cost
9. Assumptions and pending confirmations
10. Sources

### Terms used

| Term | Meaning in this document |
|---|---|
| Service level indicator | The share of good events among valid events, computed from a named source |
| Service level objective | The share of good events the platform commits to over a window |
| Window | The period over which the indicator is computed. Both objectives use the last 30 days, rolling |
| Error budget | The number of bad events the objective allows in the window |
| Live alert | An alert raised from a reading that reached the platform in its own hourly cycle |
| Drained alert | An alert raised from a reading that waited in the node buffer while the node had no signal |
| Handoff | The moment the notification service hands the push message to the push service of the phone |
| Lookup | One request for the buyer view of one sack code |

---

## 1. Context and volumes

The [alert delivery](../iot/alert-delivery.md) design records each alert in the alerts table with the time of the reading, the time of the handoff and the kind of alert, and its operational logs carry the same figures. The [public query](../traceability/public-query.md) design serves each lookup from a function with five reserved copies behind CloudFront and AWS WAF, and [recovery](recovery.md) brings the query back within 4 hours. The [observability](observability.md) design keeps six custom metrics, operational logs for 30 days and no dashboard of its own, so both objectives are computed from what those designs already record.

| Figure | Normal month | Harvest month | Origin |
|---|---|---|---|
| Alerts | About 140 | About 300 | Alert delivery, crop and drying alerts together |
| Lookups | 135,000 | 540,000 | Public query, the harvest month holds the peak 10 hours a day |
| Lookups a minute at the peak | 7.5 | 30 | Public query, the normal month is a quarter of the harvest month |

`tools/service_levels.py` computes every budget and cost figure in this document, and `tools/test_service_levels.py` checks them.

## 2. Crop alert delivery

| Element | Definition |
|---|---|
| Valid events | Live alerts of cellular farms raised in the window |
| Good event | The handoff happens 5 minutes or less after the reading was measured, `push_handoff_at` minus `measured_at` |
| Bad event | The handoff takes longer than 5 minutes, or the alert has no handoff 5 minutes after it was raised, or the push service reports a failure |
| Indicator | Good live alerts divided by valid live alerts |
| Objective | 99 percent over the last 30 days, rolling |
| Source | The handoff and undelivered entries of the delivery status and delivery check functions, read by a saved query. The alerts table holds the same fields for five years and settles any dispute |

The indicator stops at the handoff because that is the last step the platform controls. The phone receipt depends on the coverage of the farmer, so it stays as a separate figure in the alert delivery design and outside this objective.

Drained alerts stay out of the objective. Their reading waited in the node while the farm had no signal, and the alert delivery design gives them 24 hours. Farms on LoRa also stay out until the delay of the radio, the gateway and the network server is measured in the field. Their alerts are reported apart with the same rule, and they join the objective once that delay leaves room in the 5 minutes.

An alert for a farm with no registered phone counts as bad. The fault sits in the installation, and counting it is what makes the team fix it.

| Month | Live alerts, upper bound | Slow or undelivered alerts in budget |
|---|---|---|
| Normal | 140 | 1.4 |
| Harvest | 300 | 3.0 |

The alert counts include drained alerts, so the real budget is a little smaller. In a normal month the second slow alert in 30 days misses the objective. That is strict on purpose. The time budget of the alert delivery design leaves almost three minutes of margin, and an alert that arrives late can mean a lot of coffee dried above 40 °C.

## 3. Availability of the sack query

| Element | Definition |
|---|---|
| Valid events | Lookups that reach the lookup function, counted as invocations plus throttled requests |
| Good event | An invocation that ends without a function error. A code that does not exist returns the same answer as an unused code, and it is a good event |
| Bad event | A function error or timeout, or a request refused with 429 because every reserved copy was busy or the reservation was set to 0 |
| Indicator | 1 minus the sum of errors and throttles, divided by the sum of invocations and throttles |
| Objective | 99.5 percent over the last 30 days, rolling |
| Source | The `Invocations`, `Errors` and `Throttles` metrics of the lookup function, which Lambda publishes with no charge |

Lambda counts a throttled request in `Throttles` and never in `Invocations` or `Errors`, so the sum of invocations and throttles is every request that reached the function. A request that the web ACL blocks never reaches the function, and it stays out of the indicator. The rate rule blocks traffic that behaves like extraction, and a buyer who hits it retries after 5 minutes.

The switch-off of the public query sets the reserved concurrency to 0, so every lookup during it is a throttle. The switch-off spends budget like any other outage, which keeps it a last resort.

| Month | Lookups | Failed lookups in budget | Minutes of full outage at the peak | Lookups lost by a 4-hour outage at the peak |
|---|---|---|---|---|
| Normal | 135,000 | 675 | 90 | 1,800 |
| Harvest | 540,000 | 2,700 | 90 | 7,200 |

The budget equals about 90 minutes of full outage during working hours in either month, since the budget and the traffic scale together. The 4-hour recovery objective is the longest outage the platform tolerates, and an outage that long at the peak spends about 2.7 budgets in either month. Recovery and this objective therefore answer different questions. Recovery says how long the worst outage may last, and the objective says how much unavailability the buyers see across a month.

## 4. Error budget policy

The budget lets the team decide with numbers when to ship and when to stop.

| Budget left in the window | What the team does |
|---|---|
| More than half | Normal work. Production changes follow the usual approval and the harvest freeze |
| Half or less | The cause of each bad event is written down, and the next production change of the affected path goes out with its rollback ready |
| None | Production changes of the affected path are limited to fixes of the cause and security patches until the indicator is back above the objective. The cause gets a short written review with the action that prevents it |

The policy applies to each objective apart. A missed delivery objective does not stop changes to the sack query, and the other way round.

## 5. Measurement and reporting

Both indicators are computed once a day by saved queries, and the result is kept in the operations report of the month. The existing alarms tell the operator when budget is being spent, since at these volumes each bad event is a visible share of the budget.

| Objective | Alarm that signals spending | What it means for the budget |
|---|---|---|
| Crop alert delivery | Undelivered alert, slow live alert | Each alarm is one bad event, about 70 percent of the budget of a normal month |
| Availability of the sack query | Ceiling reached, any throttle in 5 minutes | Buyers are receiving 429. At the harvest peak a full outage spends the whole budget in 90 minutes |

The saved query of the delivery indicator runs over the log groups of the delivery status function and the delivery check function. Each handoff entry carries `alert_id`, `kind`, `link` and `handoff_latency_s`, and each undelivered entry carries `alert_id`, `kind` and `link`. An alert can appear in both, for example when it was reported undelivered and handed off later, so the query keeps the worst result of each alert.

```
fields alert_id, coalesce(handoff_latency_s, 1000000) as latency_s
| filter kind = "live" and link = "cellular"
| filter event_name in ["alert_handed_off", "alert_undelivered"]
| stats max(latency_s) as worst_s by alert_id
| stats count(*) as live_alerts,
        sum(if(worst_s > 300, 1, 0)) as bad_alerts
```

The indicator is 1 minus `bad_alerts` divided by `live_alerts`. The same query with `link = "lora"` gives the figure reported apart for LoRa farms. The operational logs keep 30 days, which covers the window exactly, and the alerts table remains the reference when the logs and the table disagree.

The availability indicator comes from the metrics of the lookup function, read in daily periods over the last 30 days.

```bash
aws cloudwatch get-metric-data \
  --start-time "$(date -u -d '30 days ago' +%FT%TZ)" --end-time "$(date -u +%FT%TZ)" \
  --metric-data-queries '[
    {"Id":"inv","MetricStat":{"Metric":{"Namespace":"AWS/Lambda","MetricName":"Invocations","Dimensions":[{"Name":"FunctionName","Value":"<lookup function>"}]},"Period":86400,"Stat":"Sum"},"ReturnData":false},
    {"Id":"err","MetricStat":{"Metric":{"Namespace":"AWS/Lambda","MetricName":"Errors","Dimensions":[{"Name":"FunctionName","Value":"<lookup function>"}]},"Period":86400,"Stat":"Sum"},"ReturnData":false},
    {"Id":"thr","MetricStat":{"Metric":{"Namespace":"AWS/Lambda","MetricName":"Throttles","Dimensions":[{"Name":"FunctionName","Value":"<lookup function>"}]},"Period":86400,"Stat":"Sum"},"ReturnData":false},
    {"Id":"bad","Expression":"FILL(err,0) + FILL(thr,0)","ReturnData":true},
    {"Id":"valid","Expression":"FILL(inv,0) + FILL(thr,0)","ReturnData":true}]'
```

The indicator is 1 minus the sum of the `bad` values divided by the sum of the `valid` values. CloudFront publishes its own 5xx error rate at no charge, and the operator reads it next to the indicator. A rise there with no rise in the function metrics points to the distribution or the firewall, which the indicator does not see.

## 6. Alternatives considered

| Alternative | What it offers | Why it was discarded |
|---|---|---|
| CloudWatch service level objectives on metrics | Budget, attainment and burn rate computed by CloudWatch, with burn rate alarms | About USD 1.06 a month for both objectives, with two new custom metrics for the good and valid alerts and two burn rate alarms. The observability budget is already above its reference in harvest, and the saved queries give the same figures for about USD 0.02 |
| A calendar month window | Matches the monthly report | A bad week at the end of a month and one at the start of the next fall in different windows, and the team sees a healthy figure on day one of each month. The rolling window always shows the last 30 days |
| A time-based availability indicator, minutes with no failure | Simple to read | Counts a quiet night the same as the harvest peak. The request-based indicator weighs each minute by the buyers it affected |
| Receipt on the phone as the delivery indicator | Closer to what the farmer sees | Depends on the coverage and the battery of the phone, which the platform cannot fix. The receipt stays as a separate figure |
| 95 percent for delivery | A budget of 7 to 15 alerts | Too loose for a promise of five minutes, since one alert in twenty could arrive late every month |
| 99 percent for availability | A budget of 1,350 to 5,400 lookups | Allows about three hours of full outage at the peak every month, which the buyers at a port would notice |

## 7. What fails and what happens then

| Failure | Effect on the measure | Response |
|---|---|---|
| The status log entry of a push never arrives | The delivery check reports the alert as undelivered, and the indicator counts it bad | The alarm shows it, and the alerts table tells whether the push was in fact handed off |
| A function stops writing the handoff fields to its log | The saved query finds fewer valid alerts than the alerts table | The daily report compares the count of live alerts with the table and flags a gap |
| Logs older than 30 days are gone | The query cannot cover a longer window | The window is 30 days for this reason. A longer review reads the alerts table |
| The lookup function never runs because of a fault in CloudFront or the firewall | The indicator stays high while buyers fail | The CloudFront 5xx error rate shows it, and the operator records the outage by hand in the report |
| A deployment breaks the lookup | Errors rise and the indicator falls | The pipeline moves the alias back to the previous version, and the budget shows the cost of the bad release |

## 8. Cost

Prices come from the AWS Price List API for us-east-1, CloudWatch publication of 2026-11-04.

| Item | Price | Use a month | USD a month |
|---|---|---|---|
| Logs Insights scan | USD 0.005 per GB | 60 runs over about 0.05 GB | 0.015 |
| GetMetricData | USD 0.01 per 1,000 metrics requested | 30 runs of 3 metrics | 0.001 |
| Lambda and CloudFront service metrics | No charge | | 0 |
| Alarms | Already counted in the observability design | | 0 |
| **Total** | | | **About 0.02** |

The discarded CloudWatch service level objectives cost about USD 1.06 a month. Each objective with a one-minute period emits 86,400 application signals a month at USD 1.50 a million, and the delivery objective needs two custom metrics at USD 0.30 each, with two burn rate alarms at USD 0.10 each.

## 9. Assumptions and pending confirmations

| Assumption | If it fails | Who confirms |
|---|---|---|
| Live alerts are close to the total of 140 and 300 a month | A smaller count makes each slow alert a larger share of the budget, and the objective may need a longer window | The alerts table, after the first month in production |
| The harvest peak holds 10 hours a day, so the budget in lookups follows the month | A shorter peak lowers the budget in lookups and the minutes of outage it allows | Lookup volumes of the first harvest |
| The saved delivery query returns the same count of live alerts as the alerts table | The functions must log the missing fields before the indicator is trusted | The first alerts in the test environment |
| A request blocked by the web ACL is a request the platform chose to refuse | A buyer blocked by a busy shared address is a failure the indicator misses, and the firewall logs must join the measure | Count mode weeks of the first harvest |

## 10. Sources

| Source | What it gives |
|---|---|
| AWS Lambda Developer Guide, types of metrics for functions | `Invocations` excludes throttled requests, and throttles count in `Throttles` only |
| AWS Lambda Developer Guide, monitoring function URLs | Function URL metrics, used to understand the 4xx and 5xx counts at the URL |
| Amazon CloudWatch User Guide, service level objectives | Request-based and period-based objectives, rolling and calendar windows, burn rate, any metric as an indicator |
| AWS Price List API, Amazon CloudWatch, us-east-1, publication of 2026-11-04 | Prices of Logs Insights, GetMetricData, custom metrics, alarms and application signals |
| AWS What's New, CloudWatch Application Signals SLO capabilities, March 2026 | Each objective emits two application signals per indicator period |
