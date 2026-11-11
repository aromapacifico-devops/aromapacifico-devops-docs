"""Error budgets and measurement cost of the two service level objectives.

Prints the tables of docs/architecture/service-levels.md. Run with no arguments.
Each input says where it comes from.
  DECISION   an approved earlier decision or document
  PRICE      AWS Price List API, us-east-1, USD
  ASSUMED    a new assumption of this design
"""

# DECISION
ALERTS = {"normal": 140, "harvest": 300}           # alert delivery, alerts a month, upper bound for live alerts
LOOKUPS = {"normal": 135_000, "harvest": 540_000}  # public query, lookups a month
PEAK_PER_MINUTE = {"normal": 7.5, "harvest": 30}   # public query, the normal month is a quarter of harvest
DELIVERY_GOAL = 0.99
AVAILABILITY_GOAL = 0.995
WINDOW_DAYS = 30
LOG_RETENTION_DAYS = 30                           # observability, operational logs
RECOVERY_HOURS = 4                                # recovery, time objective of the public query

# PRICE
APP_SIGNAL = 1.50 / 1_000_000                     # each Application Signal, first 100 million
CUSTOM_METRIC = 0.30                              # each custom metric a month
ALARM = 0.10                                      # each standard alarm a month
GET_METRIC_DATA = 0.01 / 1000                     # each metric requested
LOGS_INSIGHTS_GB = 0.005                          # each GB scanned

# ASSUMED
SLI_PERIOD_MINUTES = 1                            # period of a CloudWatch SLO
SIGNALS_PER_PERIOD = 2                            # each SLO emits two signals per SLI period
STATUS_LOG_GB = 0.05                              # status and check function logs scanned by one report
REPORTS_A_MONTH = 30                              # one daily run of each saved query


def delivery_budget(month):
    return ALERTS[month] * (1 - DELIVERY_GOAL)


def availability_budget(month):
    return LOOKUPS[month] * (1 - AVAILABILITY_GOAL)


def outage_minutes_in_budget(month):
    return availability_budget(month) / PEAK_PER_MINUTE[month]


def recovery_outage_lookups(month):
    return PEAK_PER_MINUTE[month] * RECOVERY_HOURS * 60


def saved_query_cost():
    queries = 2 * REPORTS_A_MONTH
    return queries * STATUS_LOG_GB * LOGS_INSIGHTS_GB + queries * 3 * GET_METRIC_DATA


def managed_slo_cost():
    periods = WINDOW_DAYS * 24 * 60 / SLI_PERIOD_MINUTES
    signals = 2 * periods * SIGNALS_PER_PERIOD
    good_and_total_metrics = 2
    burn_alarms = 2
    return signals * APP_SIGNAL + good_and_total_metrics * CUSTOM_METRIC + burn_alarms * ALARM


def main():
    print("| Month | Live alerts, upper bound | Slow or undelivered alerts in budget |")
    print("|---|---|---|")
    for month in ALERTS:
        print(f"| {month.capitalize()} | {ALERTS[month]} | {delivery_budget(month):.1f} |")
    print()
    print("| Month | Lookups | Failed lookups in budget | Minutes of full outage at the peak "
          "| Lookups lost by a 4-hour outage at the peak |")
    print("|---|---|---|---|---|")
    for month in LOOKUPS:
        print(f"| {month.capitalize()} | {LOOKUPS[month]:,} | {availability_budget(month):,.0f} "
              f"| {outage_minutes_in_budget(month):.0f} | {recovery_outage_lookups(month):,.0f} |")
    print()
    print("| Way to measure | USD a month |")
    print("|---|---|")
    print(f"| Saved queries and existing alarms | {saved_query_cost():.4f} |")
    print(f"| CloudWatch service level objectives | {managed_slo_cost():.2f} |")


if __name__ == "__main__":
    main()
