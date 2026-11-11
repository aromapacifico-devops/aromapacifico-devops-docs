"""Sizing of the public sack query. Prints the tables of docs/traceability/public-query.md.

Run with no arguments. Each input says where it comes from.
  STATEMENT  the case as given to the project
  DECISION   an approved earlier decision or document
  PRICE      the price basis, us-east-1, on-demand, USD
  ASSUMED    a new assumption of this design
"""

from math import factorial

# STATEMENT and DECISION
PEAK_PER_MINUTE = 30               # statement, harvest peak of sack reads
HARVEST_HOURS_A_DAY = 10           # decision, cloud cost, peak held for the working day
HARVEST_DAYS = 30                  # decision, cloud cost
CODES_ISSUED = 3_000_000           # decision, sack identity, five-year upper bound
CODE_SPACE = 2 ** 60               # decision, sack identity, 60 random bits
WAF_LIMIT = 300                    # decision, firewall policy, WAF-01 requests per address
WAF_WINDOW_S = 300                 # decision, firewall policy, WAF-01 window
RESERVED_CONCURRENCY = 5           # decision, ceiling of the lookup function in production
URL_RPS_PER_UNIT = 10              # AWS, a function URL serves at most 10 requests a second per unit of reserved concurrency
FUNCTION_MEMORY_GB = 0.25          # decision, cloud cost, 256 MB
READ_UNITS = 0.5                   # decision, views by actor, one eventually consistent GetItem under 4 KB

# PRICE
WAF_PER_MILLION = 0.60
LAMBDA_REQUEST_PER_MILLION = 0.20
LAMBDA_GB_SECOND = 0.0000166667
READ_UNIT_PER_MILLION = 0.125
CLOUDFRONT_FREE_REQUESTS = 10_000_000   # always-free tier, each month
CLOUDFRONT_PER_MILLION = 1.00           # HTTPS requests in North America after the free tier

# ASSUMED
FUNCTION_SECONDS = 0.2             # warm read, GetItem and audit write, as the cloud cost already prices it
CONTAINER_SACKS = 320              # sacks of 60 kg in a 20-foot container
CONTAINER_SCAN_MINUTES = 10        # an exporter scans one container from one address
ALARM_FACTOR = 10                  # the volume alarm fires at ten times the peak
RESPONSE_HOURS = 4                 # time from alarm to switch-off, the recovery time of the query

MONTH_S = 30 * 24 * 3600


def erlang_b(servers, load):
    """Chance that a request finds every reserved unit busy and receives a 429."""
    top = load ** servers / factorial(servers)
    return top / sum(load ** k / factorial(k) for k in range(servers + 1))


def per_million():
    function = LAMBDA_REQUEST_PER_MILLION + 1_000_000 * FUNCTION_MEMORY_GB * FUNCTION_SECONDS * LAMBDA_GB_SECOND
    table = READ_UNITS * READ_UNIT_PER_MILLION
    return {"web firewall": WAF_PER_MILLION, "function": function, "table read": table}


def ceiling_rps(units):
    return min(URL_RPS_PER_UNIT * units, units / FUNCTION_SECONDS)


def main():
    peak_rps = PEAK_PER_MINUTE / 60
    load = peak_rps * FUNCTION_SECONDS
    harvest_month = PEAK_PER_MINUTE * 60 * HARVEST_HOURS_A_DAY * HARVEST_DAYS
    normal_month = harvest_month // 4

    print("Load at the harvest peak")
    print(f"  requests a second            {peak_rps:.2f}")
    print(f"  requests in 5 minutes        {PEAK_PER_MINUTE * 5}")
    print(f"  average concurrent reads     {load:.2f}")
    print(f"  harvest month, ceiling       {harvest_month:,}")
    print(f"  normal month, a quarter      {normal_month:,}")

    print("\nChance of a 429 at the peak, by reserved concurrency")
    for units in range(1, 6):
        print(f"  {units}  {erlang_b(units, load):.1e}  ceiling {ceiling_rps(units):.0f} a second")

    ceiling = ceiling_rps(RESERVED_CONCURRENCY)
    print(f"\nCeiling with {RESERVED_CONCURRENCY} units: {ceiling:.0f} a second, {ceiling / peak_rps:.0f} times the peak")

    per_address = WAF_LIMIT / WAF_WINDOW_S
    container_5min = CONTAINER_SACKS / CONTAINER_SCAN_MINUTES * 5
    print("\nRate per address, WAF-01")
    print(f"  limit                        {WAF_LIMIT} in {WAF_WINDOW_S} s, {per_address:.0f} a second")
    print(f"  whole pilot peak, one address {PEAK_PER_MINUTE * 5} in 5 minutes")
    print(f"  one container scanned        {container_5min:.0f} in 5 minutes")
    print(f"  addresses that fill the ceiling {ceiling / per_address:.0f}")

    hit = CODES_ISSUED / CODE_SPACE
    guesses = ceiling * MONTH_S
    print("\nGuessing codes at the ceiling for a whole month")
    print(f"  guesses                      {guesses:,.0f}")
    print(f"  expected valid codes found   {guesses * hit:.1e}")

    prices = per_million()
    total = sum(prices.values())
    print("\nCost per million lookups, USD")
    for name, value in prices.items():
        print(f"  {name:<28} {value:.2f}")
    print(f"  {'total':<28} {total:.2f}")
    print(f"  harvest month                {harvest_month * total / 1e6:.2f}")
    print(f"  normal month                 {normal_month * total / 1e6:.2f}")
    print(f"  CloudFront requests          free under {CLOUDFRONT_FREE_REQUESTS:,} a month")

    alarm_rps = ALARM_FACTOR * peak_rps
    at_ceiling = ceiling * 3600 * RESPONSE_HOURS
    edge = at_ceiling * CLOUDFRONT_PER_MILLION / 1e6
    print("\nAbuse between alarm and switch-off")
    print(f"  alarm threshold              {alarm_rps:.0f} a second, {alarm_rps * 300:.0f} in 5 minutes")
    print(f"  lookups in {RESPONSE_HOURS} hours at the ceiling {at_ceiling:,.0f}")
    print(f"  cost, lookups served         {at_ceiling * total / 1e6:.2f}")
    print(f"  cost, CloudFront beyond free {edge:.2f}")
    print(f"  a whole month at the ceiling {ceiling * MONTH_S * total / 1e6:.2f}")


if __name__ == "__main__":
    main()
