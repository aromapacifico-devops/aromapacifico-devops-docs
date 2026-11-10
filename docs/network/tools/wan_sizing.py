"""WAN and Wi-Fi sizing of a collection center. Prints the tables of docs/network/center-wan-sizing.md.

Run with no arguments. Each input says where it comes from.
  STATEMENT  the case as given to the project
  DECISION   an approved earlier decision or document
  ASSUMED    a new assumption of this design, with a sensitivity where it matters
A calculation here does not replace a measurement at a center. Throughput, overhead and event sizes are to measure.
"""
import math

# STATEMENT and DECISION
LINK_MBPS = 100.0                 # statement, symmetric, shared with the operation
RATE_DOWN, RATE_UP = 2.0, 0.5     # statement, per active client, Mbps
ZONES = {"Management": 7, "Support": 7, "Logistics": 22, "Transport": 20, "Visitors": 10}  # decision, LAN document
DESIGN_ACTIVE = 40                # decision, record on center WAN capacity
GUEST_CAP_MBPS = LINK_MBPS * 0.10  # decision, 10 percent of the link, applied to each direction
DRONE_BATCH_MEGABITS = 500 * 3 * 8  # 12,000 megabits
DRONE_IDEAL_MBPS = 20.0           # decision, LAN document, ideal rate for the estimate of about 10 minutes
SACKS_PER_DAY = 400               # statement

# ASSUMED
SYSTEM_MBPS = 1.0                 # monitoring, updates, name and time services, per direction
MISSION_DOWNLOAD_BURST_MBPS = 10.0  # mission, polygon and no-fly zone download of the drone station before departure
EVENTS_PER_SACK = 5               # events and requests at the center per sack
EVENT_BYTES = 2048                # size of one request plus its response, in each direction, with TLS and HTTP overhead
PEAK_FACTOR, PEAK_HOURS = 3.0, 8.0  # share of the day's sacks in the busiest hour is PEAK_FACTOR over an even split of PEAK_HOURS
WIFI_EFFICIENCIES = (0.3, 0.5, 0.7)  # real aggregate throughput over the PHY rate

# QoS values proposed here, by class and direction. Guarantee, cap, priority. None means no cap below the link.
GUARANTEE = {"Operation": {"down": 55.0, "up": 32.0}, "Business": {"down": 28.0, "up": 9.0}, "Guest": {"down": 0.0, "up": 0.0}}
CAP = {"Operation": {"down": None, "up": None}, "Business": {"down": None, "up": None}, "Guest": {"down": GUEST_CAP_MBPS, "up": GUEST_CAP_MBPS}}
PRIORITY = ["Operation", "Business", "Guest"]
CLASS_OF = {"Logistics": "Operation", "Management": "Business", "Support": "Business", "Transport": "Business", "Visitors": "Guest"}


def largest_remainder(total, weights):
    """Split an integer total in proportion to weights, with whole numbers that add up."""
    s = sum(weights.values())
    raw = {k: total * v / s for k, v in weights.items()}
    base = {k: math.floor(v) for k, v in raw.items()}
    rest = total - sum(base.values())
    for k in sorted(raw, key=lambda k: raw[k] - base[k], reverse=True)[:rest]:
        base[k] += 1
    return base, raw


def scenario_design():
    others = {z: n for z, n in ZONES.items() if z != "Logistics"}
    split, raw = largest_remainder(DESIGN_ACTIVE - ZONES["Logistics"], others)
    active = {"Logistics": ZONES["Logistics"], **split}
    return active, raw


def scenario_stress():
    # Logistics and Visitors all active, the other three zones at 50 percent rounded up
    active = {"Logistics": 22, "Management": math.ceil(7 * 0.5), "Support": math.ceil(7 * 0.5), "Transport": math.ceil(20 * 0.5), "Visitors": 10}
    return active


def scenario_all():
    return dict(ZONES)


def demand_by_class(active, drone_sync=False):
    d = {"down": {c: 0.0 for c in PRIORITY}, "up": {c: 0.0 for c in PRIORITY}}
    for zone, n in active.items():
        c = CLASS_OF[zone]
        d["down"][c] += n * RATE_DOWN
        d["up"][c] += n * RATE_UP
    d["down"]["Operation"] += SYSTEM_MBPS
    d["up"]["Operation"] += SYSTEM_MBPS
    if drone_sync:
        d["down"]["Operation"] += MISSION_DOWNLOAD_BURST_MBPS
        d["up"]["Operation"] += DRONE_IDEAL_MBPS
    return d


def allocate(demand, direction):
    """Guarantees first, then free capacity by priority up to the cap of each class."""
    alloc = {}
    for c in PRIORITY:
        alloc[c] = min(demand[c], GUARANTEE[c][direction])
    free = LINK_MBPS - sum(alloc.values())
    for c in PRIORITY:
        want = demand[c] - alloc[c]
        cap = CAP[c][direction]
        room = want if cap is None else max(min(want, cap - alloc[c]), 0)
        give = max(min(room, free), 0)
        alloc[c] += give
        free -= give
    return alloc, free


def fmt(x):
    return f"{x:.1f}"


def main():
    # self checks against the existing documents
    total_clients = sum(ZONES.values())
    assert total_clients == 66
    assert math.isclose(total_clients * RATE_DOWN, 132.0) and math.isclose(total_clients * RATE_UP, 33.0)
    assert math.isclose(DESIGN_ACTIVE * RATE_DOWN, 80.0) and math.isclose(DESIGN_ACTIVE * RATE_UP, 20.0)
    assert math.isclose(DRONE_BATCH_MEGABITS / DRONE_IDEAL_MBPS / 60.0, 10.0)
    print("## Self check")
    print("The script reproduces 132 and 33 Mbps for 66 clients, 80 and 20 Mbps for 40 clients, and 10 minutes for 1.5 GB at 20 Mbps.")

    print("\n## Demand if every client is active")
    print("| Zone | Clients | Down, Mbps | Up, Mbps | Source of the figures |")
    print("|---|---|---|---|---|")
    for z, n in ZONES.items():
        print(f"| {z} | {n} | {fmt(n * RATE_DOWN)} | {fmt(n * RATE_UP)} | Clients from the LAN document, rate from the statement |")
    print(f"| Total | {total_clients} | {fmt(total_clients * RATE_DOWN)} | {fmt(total_clients * RATE_UP)} | |")

    design, raw = scenario_design()
    print("\n## Rounding of the design scenario")
    print("The 40 active clients are the approved total. Logistics is taken as fully active, with 22 clients. The other 18 are split among the other zones in proportion to their clients, with the method of the largest remainder so that whole numbers add up.")
    print("| Zone | Clients | Share of the 18 | Whole clients |")
    print("|---|---|---|---|")
    for z in ("Management", "Support", "Transport", "Visitors"):
        print(f"| {z} | {ZONES[z]} | {raw[z]:.2f} | {design[z]} |")
    print(f"| Total of the 18 | 44 | 18.00 | {sum(design[z] for z in ('Management', 'Support', 'Transport', 'Visitors'))} |")

    stress = scenario_stress()
    print("\n## Active clients by scenario")
    print("| Zone | Clients | Design, 40 | Stress, 50 | All active, 66 |")
    print("|---|---|---|---|---|")
    for z, n in ZONES.items():
        print(f"| {z} | {n} | {design[z]} | {stress[z]} | {n} |")
    print(f"| Total | {total_clients} | {sum(design.values())} | {sum(stress.values())} | {total_clients} |")
    print("The stress scenario takes 50 percent of Management, Support and Transport, rounded up to a whole client, which gives 4, 4 and 10, and all of Logistics and Visitors.")

    print("\n## Requested demand and bandwidth allowed by the classes")
    print("Requested demand is what the active clients ask for at the reference rate, plus the system traffic and, where stated, the drone synchronization. Allowed bandwidth is what the guarantees, the caps and the priority leave to each class. The two are different, and the allowed value is the one that applies.")
    print("| Scenario | Direction | Class | Requested, Mbps | Allowed, Mbps | Left free, Mbps | Visitors, average for each active client |")
    print("|---|---|---|---|---|---|---|")
    rows = [("Design, 40", design, False), ("Design, 40, with drone", design, True),
            ("Stress, 50", stress, False), ("Stress, 50, with drone", stress, True),
            ("All active, 66", dict(ZONES), False)]
    for name, active, drone in rows:
        d = demand_by_class(active, drone)
        for direction in ("down", "up"):
            alloc, free = allocate(d[direction], direction)
            for c in PRIORITY:
                guest_avg = ""
                if c == "Guest":
                    n = active["Visitors"]
                    guest_avg = f"{alloc[c] / n:.2f} Mbps of {RATE_DOWN if direction == 'down' else RATE_UP}" if n else ""
                print(f"| {name} | {direction} | {c} | {fmt(d[direction][c])} | {fmt(alloc[c])} | {fmt(free) if c == 'Guest' else ''} | {guest_avg} |")

    print("\n## Validation against the link in each direction")
    print("| Scenario | Down requested | Down allowed | Down free | Up requested | Up allowed | Up free | Reference service met for every client |")
    print("|---|---|---|---|---|---|---|---|")
    for name, active, drone in rows:
        d = demand_by_class(active, drone)
        out = []
        met = True
        for direction in ("down", "up"):
            alloc, free = allocate(d[direction], direction)
            req = sum(d[direction].values())
            out += [fmt(req), fmt(sum(alloc.values())), fmt(free)]
            if any(alloc[c] + 1e-9 < d[direction][c] for c in PRIORITY):
                met = False
        print(f"| {name} | " + " | ".join(out) + f" | {'yes' if met else 'no'} |")

    print("\n## Guarantees, caps and priority by class and direction")
    print("| Class | Zones and traffic | Priority | Guarantee down | Guarantee up | Cap down | Cap up |")
    print("|---|---|---|---|---|---|---|")
    members = {"Operation": "Logistics, local servers, tunnel traffic, drone synchronization", "Business": "Management, Support, Transport", "Guest": "Visitors"}
    for i, c in enumerate(PRIORITY, start=1):
        cap = lambda v: "link" if v is None else f"{v:.0f} Mbps"
        print(f"| {c} | {members[c]} | {i} | {GUARANTEE[c]['down']:.0f} Mbps | {GUARANTEE[c]['up']:.0f} Mbps | {cap(CAP[c]['down'])} | {cap(CAP[c]['up'])} |")
    for direction in ("down", "up"):
        total = sum(GUARANTEE[c][direction] for c in PRIORITY)
        assert total <= LINK_MBPS
        print(f"\nGuarantees in the {direction} direction add up to {total:.0f} Mbps of {LINK_MBPS:.0f}, so they fit, and {LINK_MBPS - total:.0f} Mbps stay free to lend.")

    print("\n## How the guarantees are built")
    print("| Class and direction | Guarantee | Built from |")
    print("|---|---|---|")
    print(f"| Operation, down | {GUARANTEE['Operation']['down']:.0f} Mbps | {ZONES['Logistics']} Logistics clients at {RATE_DOWN} Mbps = {ZONES['Logistics'] * RATE_DOWN:.0f}, plus {SYSTEM_MBPS:.0f} for system traffic, plus {MISSION_DOWNLOAD_BURST_MBPS:.0f} for the mission download of the drone station |")
    print(f"| Operation, up | {GUARANTEE['Operation']['up']:.0f} Mbps | {ZONES['Logistics']} Logistics clients at {RATE_UP} Mbps = {ZONES['Logistics'] * RATE_UP:.0f}, plus {SYSTEM_MBPS:.0f} for system traffic, plus {DRONE_IDEAL_MBPS:.0f} for the drone synchronization at the ideal rate |")
    biz_design = sum(design[z] for z in ('Management', 'Support', 'Transport'))
    biz_stress = sum(stress[z] for z in ('Management', 'Support', 'Transport'))
    print(f"| Business, down | {GUARANTEE['Business']['down']:.0f} Mbps | The {biz_design} Business clients of the design scenario at {RATE_DOWN} Mbps = {biz_design * RATE_DOWN:.0f} |")
    print(f"| Business, up | {GUARANTEE['Business']['up']:.0f} Mbps | The {biz_stress} Business clients of the stress scenario at {RATE_UP} Mbps = {biz_stress * RATE_UP:.1f} |")
    print("| Guest, both | 0 and a cap of 10 Mbps | The accepted decision caps visitors at 10 percent of the link and gives them no guarantee |")

    print("\n## Drone synchronization on the uplink, ideal and effective")
    print("Capacity available is the 100 Mbps of the link. Bandwidth allocated is the rate that the classes give to the synchronization. Effective throughput is what the file transfer really achieves, which is the allocated rate times an efficiency that the overhead of TCP, TLS, HTTP and the encrypted tunnel lowers. The efficiency is an assumption to measure, and 1.0 is the ideal calculation.")
    print("| Allocated rate | Efficiency 1.0, ideal | 0.9 | 0.8 | 0.7 |")
    print("|---|---|---|---|---|")
    for rate in (10.0, 20.0, 40.0, 80.0):
        cells = [f"{DRONE_BATCH_MEGABITS / (rate * e) / 60:.1f} min" for e in (1.0, 0.9, 0.8, 0.7)]
        print(f"| {rate:.0f} Mbps | " + " | ".join(cells) + " |")
    print(f"Batch of 500 photos of 3 MB is {DRONE_BATCH_MEGABITS:,.0f} megabits, 1.5 GB.")

    print("\n## Operation traffic from the volumes of the case")
    print(f"{SACKS_PER_DAY} sacks a day, {EVENTS_PER_SACK} events or requests for each sack, a peak hour that carries {PEAK_FACTOR:g} times an even share of a {PEAK_HOURS:g} hour day. The size of an event is an assumption, with its sensitivity.")
    print("| Size of one event with its response | Average rate over the day | Rate in the peak hour |")
    print("|---|---|---|")
    for mult in (1, 10, 100):
        size_bits = EVENT_BYTES * mult * 8
        per_day = SACKS_PER_DAY * EVENTS_PER_SACK * size_bits
        avg = per_day / 86400 / 1e6
        peak = SACKS_PER_DAY / PEAK_HOURS * PEAK_FACTOR * EVENTS_PER_SACK * size_bits / 3600 / 1e6
        print(f"| {EVENT_BYTES * mult / 1024:.0f} KB | {avg:.5f} Mbps | {peak:.4f} Mbps |")

    print("\n## Wi-Fi demand for each access point")
    print("Active clients are shared evenly among the access points, rounded up. The access point must sustain the aggregate throughput at the reference rate. The PHY rate that it implies depends on the efficiency, which is an assumption.")
    print("| Scenario | Access points | Clients on the busiest one | Aggregate down and up, Mbps | PHY rate needed at efficiency " + ", ".join(f"{e}" for e in WIFI_EFFICIENCIES) + " |")
    print("|---|---|---|---|---|")
    for name, active in (("Design, 40", design), ("Stress, 50", stress)):
        n = sum(active.values())
        for aps in (2, 3):
            per = math.ceil(n / aps)
            agg = per * (RATE_DOWN + RATE_UP)
            phys = ", ".join(f"{agg / e:.0f} Mbps" for e in WIFI_EFFICIENCIES)
            print(f"| {name} | {aps} | {per} | {agg:.1f} | {phys} |")


main()
