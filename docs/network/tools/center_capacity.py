"""Capacity of a collection center for 400 sacks a day, stage by stage, and the size of the reserve of codes.

Run with no arguments. It prints the tables of docs/network/collection-center-operations.md.
Origin of each input
  CASE     data of the case or of an earlier decision of the project
  ASSUMED  proposed assumption, approved as an assumption, to replace with the first harvest
Nothing here is a measured capacity. A calculation does not replace a time study at a center.
"""
import math

# CASE
SACKS_PER_DAY = 400
LOGISTICS_DEVICES = {"desktops": 2, "phones": 20}
LABEL_PRINTERS = 1
GROUP_SCAN = 30

# ASSUMED
DAY_HOURS = 8.0
PEAK_FACTOR = 3.0
UTIL_DAY, UTIL_PEAK = 0.70, 0.85
RECEPTION = [("Scan the label at the station", 15), ("Weigh", 20), ("Inspect", 90), ("Decide and record", 20), ("Move to the stack or the return area", 20)]
DISPATCH_SCAN = 15
NO_CODE_STEPS = [("Assign the code and register the sack", 20, "station"), ("Print one adhesive label", 30, "printer"), ("Attach the label and scan it to verify", 40, "station")]
REPRINT_STEPS = [("Withdraw or void the old label, print, attach and scan", 40, "station"), ("Print the label again", 30, "printer")]
NO_CODE_SHARE = 0.10
REPRINT_SHARE = 0.05
ACCEPTED_SHARE = 1.0  # upper bound, every sack is dispatched
SCALES = 1
OUTAGE_DAYS = 2


def reception_seconds():
    return sum(s for _, s in RECEPTION)


def main():
    rec = reception_seconds()
    assert rec == 165
    assert rec + DISPATCH_SCAN == 180
    assert sum(s for _, s, _ in NO_CODE_STEPS) == 90
    avg_per_hour = SACKS_PER_DAY / DAY_HOURS
    peak_per_hour = avg_per_hour * PEAK_FACTOR

    print("## Self check")
    print("The times of the reception steps add up to 165 seconds without the dispatch scan and 180 seconds with it, and the three steps of a sack with no code add up to the 90 seconds that were approved for issuing and printing.")

    print("\n## Time of each activity for one sack, each counted once")
    print("| Activity | Seconds | Who or what is busy | Applies to |")
    print("|---|---|---|---|")
    for name, s in RECEPTION:
        print(f"| {name} | {s} | Person at a reception station | Every sack |")
    print(f"| Reception subtotal | {rec} | | Every sack |")
    print(f"| Scan for dispatch to the port | {DISPATCH_SCAN} | Person at the dispatch station | Every accepted sack, taken as all sacks as an upper bound |")
    print(f"| Reception and dispatch | {rec + DISPATCH_SCAN} | | Every accepted sack |")
    for name, s, who in NO_CODE_STEPS:
        print(f"| {name} | {s} | {'Person at a station' if who == 'station' else 'Label printer'} | Sack that arrives with no code |")
    for name, s, who in REPRINT_STEPS:
        print(f"| {name} | {s} | {'Person at a station' if who == 'station' else 'Label printer'} | Each reprint |")

    print("\n## Demand")
    print("| Quantity | Value | Origin |")
    print("|---|---|---|")
    print(f"| Sacks a day | {SACKS_PER_DAY} | Case |")
    print(f"| Hours of a harvest day | {DAY_HOURS:g} | Assumed |")
    print(f"| Average sacks an hour | {avg_per_hour:.0f} | Calculation |")
    print(f"| Busiest hour as a multiple of the average | {PEAK_FACTOR:g} | Assumed |")
    print(f"| Sacks in the busiest hour | {peak_per_hour:.0f} | Calculation |")
    print(f"| Share of sacks that arrive with no code | {NO_CODE_SHARE:.0%} | Assumed, sensitivity below |")
    print(f"| Share of sacks that need a reprint | {REPRINT_SHARE:.0%} | Assumed |")
    print(f"| Utilization target, day and busiest hour | {UTIL_DAY:.0%} and {UTIL_PEAK:.0%} | Assumed |")

    print("\n## Capacity by stage")
    print("Work is in seconds for each sack. Capacity of one unit is sacks an hour at the utilization target of the busiest hour. Units needed are rounded up.")
    print("| Stage | Resource | Seconds for a sack | Capacity of one unit, sacks an hour | Units for the average hour at 70 percent | Units for the busiest hour at 85 percent |")
    print("|---|---|---|---|---|---|")

    def row(stage, resource, seconds, rate_per_hour):
        cap = 3600 * UTIL_PEAK / seconds
        day_units = math.ceil(rate_per_hour * seconds / 3600 / UTIL_DAY)
        peak_units = math.ceil(peak_per_hour * seconds / 3600 / UTIL_PEAK) if rate_per_hour == avg_per_hour else math.ceil(rate_per_hour * PEAK_FACTOR * seconds / 3600 / UTIL_PEAK)
        print(f"| {stage} | {resource} | {seconds:g} | {cap:.1f} | {day_units} | {peak_units} |")

    row("Reception, all five steps", "People at reception stations", rec, avg_per_hour)
    row("Weighing only, inside reception", "Scales", 20, avg_per_hour)
    row("Inspection only, inside reception", "People who inspect", 90, avg_per_hour)
    nc = NO_CODE_SHARE
    station_nc = sum(s for _, s, w in NO_CODE_STEPS if w == "station")
    printer_nc = sum(s for _, s, w in NO_CODE_STEPS if w == "printer")
    row("Sacks with no code, station steps", "People at a station", station_nc * nc, avg_per_hour)
    row("Sacks with no code and reprints, printer", "Label printers", printer_nc * nc + 30 * REPRINT_SHARE, avg_per_hour)
    row("Dispatch scan", "People at the dispatch station", DISPATCH_SCAN * ACCEPTED_SHARE, avg_per_hour)
    total_seconds = rec + DISPATCH_SCAN * ACCEPTED_SHARE + station_nc * nc + 40 * REPRINT_SHARE
    print(f"\nPeople time for one average sack, all station activities: {total_seconds:.1f} seconds. For {SACKS_PER_DAY} sacks that is {SACKS_PER_DAY * total_seconds / 3600:.1f} station hours a day.")
    print(f"The scale in one unit serves {3600 * UTIL_PEAK / 20:.0f} sacks an hour at the target. The busiest hour asks for {peak_per_hour:.0f}, so {SCALES} scale runs at {peak_per_hour * 20 / 3600:.0%} of its time in that hour.")

    print("\n## Bottleneck")
    print("| Stage | Share of the person time of a sack | Note |")
    print("|---|---|---|")
    for name, s in RECEPTION:
        print(f"| {name} | {100 * s / total_seconds:.0f} percent | Inside reception |")
    print(f"| Dispatch scan | {100 * DISPATCH_SCAN / total_seconds:.0f} percent | |")
    print(f"| Station steps for no code and reprints | {100 * (station_nc * nc + 40 * REPRINT_SHARE) / total_seconds:.0f} percent | |")
    print("Inspection takes the largest share of the person time, so the people who inspect, and not the devices, set the pace.")

    print("\n## What a number of people can do in the busiest hour")
    print("People at reception stations, with every one of them busy. Peak demand is the sacks of the busiest hour. The backlog is what is left unreceived at the end of that hour, and it clears at the average rate that follows, if the people stay.")
    print("| People | Sacks an hour at 100 percent busy | At 85 percent | Backlog after the busiest hour | Hours to clear it at the average demand |")
    print("|---|---|---|---|---|")
    for people in (2, 4, 6, 8, 10):
        full = people * 3600 / rec
        at85 = full * UTIL_PEAK
        backlog = max(peak_per_hour - full, 0)
        spare = full - avg_per_hour
        clear = "never, below the average demand" if (backlog > 0 and spare <= 0) else (f"{backlog / spare:.1f}" if backlog > 0 else "no backlog")
        print(f"| {people} | {full:.0f} | {at85:.0f} | {backlog:.0f} sacks | {clear} |")
    print(f"The logistics zone has {LOGISTICS_DEVICES['desktops']} desktops and {LOGISTICS_DEVICES['phones']} phones, {sum(LOGISTICS_DEVICES.values())} devices. Devices do not limit the stations. People, scales and the pace of inspection do, and the number of people at a center is not known.")

    print("\n## Label printer load")
    print("| Share with no code | Labels in the busiest hour | Printer seconds in that hour | Printer busy |")
    print("|---|---|---|---|")
    for share in (0.02, 0.10, 0.30):
        labels = peak_per_hour * (share + REPRINT_SHARE)
        busy = labels * 30
        print(f"| {share:.0%}, with {REPRINT_SHARE:.0%} reprints | {labels:.0f} | {busy:.0f} | {busy / 3600:.0%} |")
    print(f"The speed of the printer is not known, and {LABEL_PRINTERS} printer serves a center. The 30 seconds for a label include the handling of the printer and are an assumption.")

    print("\n## Reserve of codes for an outage, sized for the center first")
    print(f"The reserve is the number of sacks with no code that the center expects in the days of the outage, and it is shared among the devices that register such sacks, with no overlap.")
    print("| Share with no code | 1 day | 2 days | 3 days |")
    print("|---|---|---|---|")
    for share in (0.02, 0.10, 0.30):
        print(f"| {share:.0%} | " + " | ".join(str(math.ceil(share * SACKS_PER_DAY * d)) for d in (1, 2, 3)) + " |")
    total = math.ceil(NO_CODE_SHARE * SACKS_PER_DAY * OUTAGE_DAYS)
    print(f"\nWith {NO_CODE_SHARE:.0%} and {OUTAGE_DAYS} days, the reserve of the center is {total} codes.")
    print("| Devices that register sacks | Blocks, exclusive to each device | Sum |")
    print("|---|---|---|")
    for k in (2, 3, 4):
        base, extra = divmod(total, k)
        blocks = [base + 1] * extra + [base] * (k - extra)
        print(f"| {k} | {', '.join(str(b) for b in blocks)} | {sum(blocks)} |")
    print("The reserve of one center is the total above and is not repeated for each device.")


main()
