"""Energy budget, solar sizing and firmware update cost of the autonomous farm node.

Run with no arguments. It prints the tables used in docs/iot/autonomous-node.md, so the document can be checked
against the script. Every input is marked as a design value of the approved documents or as an assumption.

Conventions
- All energy figures are at the battery terminals. A load figure given at a device rail is converted once with
  DC_EFFICIENCY, and the base case does not apply it to the modem, whose reference point the source does not state.
- The usable capacity factor, the charge path and the margin are three different things and are applied once each.
  The factor limits what may be drawn from the battery. The charge path limits what reaches the battery from the
  panel. The margin covers the uncertainty of the consumption estimate.
"""

# Design values of the approved documents. They are not measurements.
BATTERY_VOLTS = 12.8
BATTERY_AH = 12.0
AUTONOMY_DAYS = 5
PANEL_WATTS = 20.0
PEAK_SUN_HOURS = 3.0          # assumption of the approved documents, to confirm with field data
MODEM_WATTS = 1.5             # assumed average power of a connection, to measure with the chosen modem
CONNECTION_OK_SECONDS = 45
CONNECTION_FAILED_SECONDS = 120
CONNECTIONS_PER_DAY = 24

# Assumptions added by this specification. Each one is to confirm with a datasheet or a field measurement.
USABLE_FACTOR = 0.80          # share of the nominal capacity that may be drawn
PANEL_DERATING = 0.80         # temperature, soiling, orientation and wiring, as one factor
CHARGE_PATH_EFFICIENCY = 0.90  # charge controller and battery, as one factor
DC_EFFICIENCY = 0.85          # conversion from the battery to the rails
MARGIN = 0.20                 # allowed error of the consumption estimate


def watt_hours(power_watts, seconds):
    return power_watts * seconds / 3600.0


def main():
    nominal = BATTERY_VOLTS * BATTERY_AH
    usable = nominal * USABLE_FACTOR
    old_budget = nominal / AUTONOMY_DAYS
    budget = usable / AUTONOMY_DAYS
    target = budget / (1 + MARGIN)
    modem_ok = CONNECTIONS_PER_DAY * watt_hours(MODEM_WATTS, CONNECTION_OK_SECONDS)
    modem_worst = CONNECTIONS_PER_DAY * watt_hours(MODEM_WATTS, CONNECTION_FAILED_SECONDS)
    rest = target - modem_worst
    path = PANEL_DERATING * CHARGE_PATH_EFFICIENCY
    generation = PANEL_WATTS * PEAK_SUN_HOURS * path

    print("## Battery and daily ceiling")
    print("| Quantity | Value | Kind |")
    print("|---|---|---|")
    print(f"| Nominal capacity | {nominal:.1f} Wh | Design value, 12.8 V times 12 Ah |")
    print(f"| Daily figure of the earlier documents | {old_budget:.1f} Wh a day | Nominal capacity over {AUTONOMY_DAYS} days, which counts all of it as usable |")
    print(f"| Usable capacity | {usable:.2f} Wh | Assumption, factor {USABLE_FACTOR:.2f} |")
    print(f"| Ceiling of the daily draw for {AUTONOMY_DAYS} days | {budget:.2f} Wh a day, {budget / 24:.2f} W average | Calculation. A ceiling and not a consumption |")
    print(f"| Target for the estimated consumption with a {int(MARGIN * 100)} percent margin | {target:.2f} Wh a day | Calculation |")

    print("\n## Modem, a design value")
    print("| Case | Energy a day | Share of the ceiling |")
    print("|---|---|---|")
    print(f"| {CONNECTIONS_PER_DAY} connections of {CONNECTION_OK_SECONDS} s at {MODEM_WATTS} W | {modem_ok:.2f} Wh | {100 * modem_ok / budget:.1f} percent |")
    print(f"| {CONNECTIONS_PER_DAY} attempts of {CONNECTION_FAILED_SECONDS} s at {MODEM_WATTS} W, all failing | {modem_worst:.2f} Wh | {100 * modem_worst / budget:.1f} percent |")
    print(f"| Same worst case if {MODEM_WATTS} W is at the rail and the conversion is {DC_EFFICIENCY} | {modem_worst / DC_EFFICIENCY:.2f} Wh | {100 * modem_worst / DC_EFFICIENCY / budget:.1f} percent |")

    print("\n## Room left for everything else")
    print("| Quantity | Value |")
    print("|---|---|")
    print(f"| Target for the estimated total | {target:.2f} Wh a day |")
    print(f"| Worst case of the modem | {modem_worst:.2f} Wh a day |")
    print(f"| Room for the controller in sleep, probes, regulators and the radio idle | {rest:.2f} Wh a day, {rest / 24:.2f} W average |")
    print(f"| Reading events a day with drying | 30 |")
    print(f"| Energy a reading event could take if it used all the room | {rest / 30:.2f} Wh |")

    print("\n## Daily energy that reaches the battery from the panel")
    print(f"Panel {PANEL_WATTS:.0f} W, derating {PANEL_DERATING}, charge path {CHARGE_PATH_EFFICIENCY}, combined {path:.2f}. Base case {PEAK_SUN_HOURS} peak sun hours gives {generation:.1f} Wh a day.")
    efficiencies = [0.60, 0.72, 0.85]
    hours = [1.5, 2.0, 2.5, 3.0, 4.0]
    print("| Peak sun hours | " + " | ".join(f"Combined {e:.2f}" for e in efficiencies) + " |")
    print("|---|" + "---|" * len(efficiencies))
    for h in hours:
        print(f"| {h} | " + " | ".join(f"{PANEL_WATTS * h * e:.1f} Wh" for e in efficiencies) + " |")

    print("\n## Days to refill the usable capacity from empty, at the combined factor of the base case")
    loads = [0.25, 0.50, 1.00]
    print("| Peak sun hours | Panel | " + " | ".join(f"Draw {int(100 * l)} percent of the ceiling ({l * budget:.1f} Wh)" for l in loads) + " |")
    print("|---|---|" + "---|" * len(loads))
    for panel in (PANEL_WATTS, 30.0):
        for h in hours:
            gen = panel * h * path
            cells = []
            for l in loads:
                net = gen - l * budget
                cells.append(f"{usable / net:.1f} days" if net > 0 else "never")
            print(f"| {h} | {panel:.0f} W | " + " | ".join(cells) + " |")

    print("\n## Break even peak sun hours")
    print("| Draw | Peak sun hours needed to stay level, 20 W panel |")
    print("|---|---|")
    for l in loads:
        print(f"| {int(100 * l)} percent of the ceiling, {l * budget:.1f} Wh | {l * budget / (PANEL_WATTS * path):.2f} |")

    print("\n## Cost of one firmware update on the cellular path, scenarios")
    print("Throughput is a scenario and not a claim about any technology. Energy uses the assumed modem power of a connection.")
    print("| Image | Throughput | Transfer time | Modem energy | Share of the ceiling | Data |")
    print("|---|---|---|---|---|---|")
    for kb in (256, 512, 1024):
        for kbps in (10, 50, 200):
            seconds = kb * 8 / kbps
            energy = watt_hours(MODEM_WATTS, seconds)
            print(f"| {kb} KB | {kbps} kbps | {seconds:.0f} s | {energy:.3f} Wh | {100 * energy / budget:.2f} percent | {kb / 1024:.2f} MB |")


main()
