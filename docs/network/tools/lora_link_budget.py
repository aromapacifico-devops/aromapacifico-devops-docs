"""Frame budget, time on air, drain time, energy and capacity of the LoRa path of a farm node.

Run with no arguments. It prints the tables used in docs/network/lora-out-of-coverage.md.

What is verified and what is a parameter
- Data rates and maximum application payload per data rate come from the LoRa Alliance document RP002-1.0.2,
  section 2.8 for AU915-928, tables for the repeater compatible case. They are inputs, and the regional plan that
  the hardware and the network server really implement must be confirmed. They are not a statement that this plan is
  allowed or usable in Colombia.
- The time on air formula is the one of the SX1276 datasheet of Semtech, revision 4. The script checks it against
  the 400 ms limit of the RP002 payload table, as a self test.
- Frame layout, record sizes, the number of nodes, channels, transmit power and gateway load are design values or
  scenarios. A simulation or a calculation does not replace a radio test in the field.
"""
import math

# AU915-928 data rates DR0 to DR6 of RP002-1.0.2, spreading factor and bandwidth in kHz
DATA_RATES = {0: (12, 125), 1: (11, 125), 2: (10, 125), 3: (9, 125), 4: (8, 125), 5: (7, 125), 6: (8, 500)}
# Maximum application payload N in bytes with no FOpts, repeater compatible case, by uplink dwell time setting
N_NO_DWELL = {0: 51, 1: 51, 2: 51, 3: 115, 4: 222, 5: 222, 6: 222}
N_DWELL_400 = {0: None, 1: None, 2: 11, 3: 53, 4: 125, 5: 222, 6: 222}
LORAWAN_OVERHEAD = 13  # MHDR 1, DevAddr 4, FCtrl 1, FCnt 2, FPort 1, MIC 4. M equals N plus 8, and M plus MHDR and MIC gives the PHY payload
FOPTS_RESERVE = 15     # largest FOpts field, reserved in one scenario for MAC commands that ride on the uplink
PREAMBLE_SYMBOLS = 8
INTER_FRAME_SECONDS = {"no dwell limit": 0, "dwell limit": 20}  # RP002 recommends 20 s between uplinks with the dwell limit

# Frame layout of version 1, sizes in bytes. A design value that the node and the decoder must share.
HEADER = [
    ("version", 1), ("flags", 1), ("epoch", 1), ("first_seq", 4), ("count", 1), ("held_before", 2),
    ("dropped_total", 2), ("config_version", 1), ("frame_time", 4), ("base_capture", 4),
]
HEADER_BYTES = sum(size for _, size in HEADER)
RECORD_BYTES = {"cultivation": 3 + 8 * 2, "drying": 3 + 2 * 2}  # type 1, delta in minutes 2, then the values of the zone

# Approved node figures and assumptions shared with the node specification
READINGS_PER_DAY = {"cultivation": 6, "drying": 24}
ATTEMPT_WINDOW_SECONDS = 120
DAILY_CEILING_WH = 24.58  # ceiling of the node daily draw from the node energy budget, which rests on assumptions there


def time_on_air(payload_bytes, sf, bw_khz, crc=1, header_explicit=True, cr=1):
    """Time on air in seconds of a LoRa packet of payload_bytes PHY bytes, formula of the SX1276 datasheet."""
    tsym = (2 ** sf) / (bw_khz * 1000.0)
    de = 1 if (sf >= 11 and bw_khz == 125) else 0
    ih = 0 if header_explicit else 1
    numerator = 8 * payload_bytes - 4 * sf + 28 + 16 * crc - 20 * ih
    symbols = 8 + max(math.ceil(numerator / (4 * (sf - 2 * de))) * (cr + 4), 0)
    return (PREAMBLE_SYMBOLS + 4.25) * tsym + symbols * tsym


def phy_bytes(n_application):
    return n_application + LORAWAN_OVERHEAD


def self_test():
    """The RP002 payload limit with a 400 ms dwell time must be the largest payload that fits in 400 ms."""
    problems = []
    for dr, n in N_DWELL_400.items():
        if n is None or dr in (5, 6):
            continue
        sf, bw = DATA_RATES[dr]
        fits = time_on_air(phy_bytes(n), sf, bw) <= 0.4
        over = time_on_air(phy_bytes(n + 1), sf, bw) > 0.4
        if not (fits and over):
            problems.append((dr, n, round(time_on_air(phy_bytes(n), sf, bw), 3), round(time_on_air(phy_bytes(n + 1), sf, bw), 3)))
    return problems


def records_per_frame(n_max, kind):
    room = n_max - HEADER_BYTES
    return max(room // RECORD_BYTES[kind], 0)


def pack(n_max, readings):
    """Greedy packing of a list of record kinds, oldest first. Returns the list of frame sizes in bytes."""
    frames, current, used = [], 0, HEADER_BYTES
    for kind in readings:
        size = RECORD_BYTES[kind]
        if HEADER_BYTES + size > n_max:
            return None
        if used + size > n_max:
            frames.append(used)
            used = HEADER_BYTES
        used += size
        current += 1
    if current:
        frames.append(used)
    return frames


def day_readings(drying):
    items = ["cultivation"] * READINGS_PER_DAY["cultivation"]
    if drying:
        items += ["drying"] * READINGS_PER_DAY["drying"]
    # cultivation every 4 hours and drying every hour, interleaved by time
    timeline = []
    for hour in range(24):
        if hour % 4 == 0:
            timeline.append("cultivation")
        if drying:
            timeline.append("drying")
    return timeline


def main():
    problems = self_test()
    print("## Self test of the time on air formula")
    print("The payload limits that RP002 gives for a 400 ms dwell time are the largest that fit in 400 ms for DR2, DR3 and DR4." if not problems else f"MISMATCH {problems}")

    print("\n## Frame layout, version 1")
    print("| Field | Bytes |")
    print("|---|---|")
    for name, size in HEADER:
        print(f"| {name} | {size} |")
    print(f"| Header total | {HEADER_BYTES} |")
    for kind, size in RECORD_BYTES.items():
        print(f"| Record, {kind} | {size} |")

    print("\n## Payload budget by data rate")
    print("| Data rate | Spreading factor and bandwidth | Largest application payload, no dwell limit | Largest, 400 ms dwell limit | Cultivation records in a frame, no dwell limit | Drying records in a frame, no dwell limit | Cultivation records, dwell limit | Drying records, dwell limit | Cultivation records, no dwell limit and 15 bytes reserved for MAC commands |")
    print("|---|---|---|---|---|---|---|---|---|")
    for dr, (sf, bw) in DATA_RATES.items():
        a, b = N_NO_DWELL[dr], N_DWELL_400[dr]
        row = [f"DR{dr}", f"SF{sf} / {bw} kHz", f"{a} B", "not allowed" if b is None else f"{b} B",
               records_per_frame(a, "cultivation"), records_per_frame(a, "drying"),
               "none" if b is None else records_per_frame(b, "cultivation"),
               "none" if b is None else records_per_frame(b, "drying"),
               records_per_frame(a - FOPTS_RESERVE, "cultivation")]
        print("| " + " | ".join(str(x) for x in row) + " |")
    print(f"\nHeader {HEADER_BYTES} bytes, cultivation record {RECORD_BYTES['cultivation']} bytes, drying record {RECORD_BYTES['drying']} bytes. A value of zero or none means that not even one record fits with the header.")

    print("\n## Time on air of a full frame")
    print("| Data rate | Frame size, no dwell limit | Time on air | Frame size, dwell limit | Time on air |")
    print("|---|---|---|---|---|")
    for dr, (sf, bw) in DATA_RATES.items():
        a, b = N_NO_DWELL[dr], N_DWELL_400[dr]
        ta = time_on_air(phy_bytes(a), sf, bw)
        tb = "not allowed" if b is None else f"{time_on_air(phy_bytes(b), sf, bw):.3f} s"
        print(f"| DR{dr} | {a} B application, {phy_bytes(a)} B on air | {ta:.3f} s | {'' if b is None else str(b) + ' B'} | {tb} |")

    print("\n## Drain of one day of readings after an outage of 23 hours")
    print(f"The attempt window is {ATTEMPT_WINDOW_SECONDS} s, as for the cellular path. Frames are sent oldest first, with the spacing of the regime.")
    print("| Case | Data rate | Regime | Frames | Total time on air | Time to send all frames | Fits in the window |")
    print("|---|---|---|---|---|---|---|")
    for label, drying in (("Crop only, 6 readings", False), ("Crop and drying, 30 readings", True)):
        readings = day_readings(drying)
        for dr in (2, 3, 4, 5):
            sf, bw = DATA_RATES[dr]
            for regime, table in (("no dwell limit", N_NO_DWELL), ("dwell limit", N_DWELL_400)):
                n = table[dr]
                if n is None:
                    continue
                frames = pack(n, readings)
                if frames is None:
                    print(f"| {label} | DR{dr} | {regime} | no record fits | | | |")
                    continue
                airtime = sum(time_on_air(phy_bytes(size), sf, bw) for size in frames)
                spacing = INTER_FRAME_SECONDS[regime] * (len(frames) - 1)
                total = airtime + spacing
                print(f"| {label} | DR{dr} | {regime} | {len(frames)} | {airtime:.2f} s | {total:.1f} s | {'yes' if total <= ATTEMPT_WINDOW_SECONDS else 'no'} |")

    print("\n## Collision probability, pure random access scenario")
    print("One frame per node and hour. Equal use of the channels, one spreading factor, no capture effect and no orthogonality of spreading factors. A scenario, not a measurement.")
    print("| Data rate | Channels | Nodes | Load per channel | Probability that a frame collides |")
    print("|---|---|---|---|---|")
    for dr in (3, 4):
        sf, bw = DATA_RATES[dr]
        size = HEADER_BYTES + RECORD_BYTES["cultivation"]
        toa = time_on_air(phy_bytes(size), sf, bw)
        for channels in (8, 64):
            for nodes in (10, 25, 50, 100):
                load = nodes * toa / 3600.0 / channels
                collide = 1 - math.exp(-2 * load)
                print(f"| DR{dr}, frame of {size} B, {toa:.3f} s | {channels} | {nodes} | {load:.5f} | {100 * collide:.3f} percent |")

    print("\n## Energy of the transmissions, scenarios for the transmit power")
    print("The transmit power of the module is a parameter until its datasheet exists. The energy counts only the time on air.")
    print("| Data rate | Frame | Time on air | Power | Energy of a frame | 24 frames a day | Share of the daily ceiling |")
    print("|---|---|---|---|---|---|---|")
    for dr in (2, 3, 4):
        sf, bw = DATA_RATES[dr]
        size = HEADER_BYTES + RECORD_BYTES["cultivation"]
        toa = time_on_air(phy_bytes(size), sf, bw)
        for power in (0.1, 0.3, 0.5):
            e = power * toa / 3600.0
            print(f"| DR{dr} | {size} B | {toa:.3f} s | {power} W | {e * 1000:.3f} mWh | {24 * e:.4f} Wh | {100 * 24 * e / DAILY_CEILING_WH:.3f} percent |")

    print("\n## Gateway energy, parameterized")
    print("Same assumptions as the node energy budget, usable share 0.80, panel and charge path 0.72, 3 peak sun hours. The load is a parameter until the gateway is chosen.")
    print("| Gateway load | Energy a day | Battery for 3 days with 0.80 usable, at 12.8 V | Battery for 5 days | Panel to stay level at 3 peak sun hours |")
    print("|---|---|---|---|---|")
    for watts in (2, 5, 10):
        daily = watts * 24.0
        cells = []
        for days in (3, 5):
            wh = daily * days / 0.8
            cells.append(f"{wh:.0f} Wh, {wh / 12.8:.0f} Ah")
        panel = daily / (3.0 * 0.72)
        print(f"| {watts} W | {daily:.0f} Wh | {cells[0]} | {cells[1]} | {panel:.0f} W |")

    print("\n## Delivery time of a reading, calculated parts")
    print("| Part | Value | Kind |")
    print("|---|---|---|")
    print(f"| Reading of a node, then its transmission in the same cycle | the time on air of the frame, from the first table, and the window of {ATTEMPT_WINDOW_SECONDS} s as an upper bound for the whole node side | Calculation and design value |")
    print("| Cloud side of the alert path, after the radio | about 96 s, from the earlier alert budget of 216 s without its 120 s node window | Design value of the platform |")
    print("| Network server and gateway latency | not known | To measure |")
    print("| Acknowledgement | arrives in the receive windows of the next uplink, so at least one cycle later | Calculation from the cycle |")
    print("| Earliest repeat of a frame that was lost | two cycles after the first attempt, since the acknowledgement of the first attempt is not known before the second cycle sends | Calculation from the cycle |")


main()
