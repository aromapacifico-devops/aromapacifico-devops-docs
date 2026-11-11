"""Flight frequency of the drone service in the pilot. Prints the tables of docs/drones/roles-permits-and-campaigns.md.

Run with no arguments. Each input says where it comes from.
  STATEMENT  the case as given to the project
  DECISION   an approved earlier decision or document
  ASSUMED    a new assumption of this design
The counts are estimates. The first harvest should replace them with real ones.
"""

# STATEMENT and DECISION
FARMS = 200                        # statement
DEPARTMENTS = 3                    # statement, Cauca, Huila and Tolima
BRIGADES = 3                       # decision, operating mode, one per department
HARVEST_MONTHS = 4                 # decision, operating mode
HARVEST_MONTH = {"Confirm the alert": 40, "Fumigate": 25, "Verify": 25}  # decision, operating mode
IMAGES_HARVEST_MONTH = 9000        # decision, operating mode
IMAGES_PER_ESTIMATION = 100        # decision, harvest estimation
ESTIMATIONS_PER_FARM = 1           # decision, one per farm and per harvest
CAMPAIGNS_IN_HARVEST = HARVEST_MONTHS  # statement, one a month in harvest
CAMPAIGN_GAP_OUTSIDE = 3           # statement, one every three months outside harvest

# ASSUMED
OUTSIDE_SHARE = 0.25               # outside harvest, alert-driven work runs at a quarter of the harvest rate
REDELIMIT_SHARE = 0.10             # after the first year, one farm in ten needs a new delimitation
FIELD_DAYS = 20                    # working days a brigade spends in the field each month
STARTUP_MONTHS = 2                 # the start-up round delimits every farm outside harvest, before the first harvest

OUTSIDE_MONTHS = 12 - HARVEST_MONTHS
SERVICES = ["Delimit the lot", "Confirm the alert", "Fumigate", "Verify", "Estimate the harvest"]


def outside_campaigns():
    """Campaigns outside harvest, counted from the last harvest month every CAMPAIGN_GAP_OUTSIDE months."""
    return len(range(CAMPAIGN_GAP_OUTSIDE, OUTSIDE_MONTHS + 1, CAMPAIGN_GAP_OUTSIDE))


def monthly(year):
    """Missions of the whole pilot in an average harvest month and outside-harvest month."""
    estimations = FARMS * ESTIMATIONS_PER_FARM / HARVEST_MONTHS
    delimitations = 0 if year == 1 else FARMS * REDELIMIT_SHARE
    harvest = {"Delimit the lot": 0, "Estimate the harvest": estimations, **HARVEST_MONTH}
    outside = {s: round(n * OUTSIDE_SHARE) for s, n in HARVEST_MONTH.items()}
    outside["Estimate the harvest"] = 0
    outside["Delimit the lot"] = delimitations / OUTSIDE_MONTHS
    return harvest, outside


def yearly(year):
    harvest, outside = monthly(year)
    total = {s: harvest[s] * HARVEST_MONTHS + outside[s] * OUTSIDE_MONTHS for s in SERVICES}
    if year == 1:
        total["Delimit the lot"] = FARMS
    return total


def row(*cells):
    print("| " + " | ".join(str(c) for c in cells) + " |")


def main():
    print("Missions by service")
    row("Service", "Harvest month", "Outside-harvest month, after the first year", "First year", "Following years")
    row("---", "---", "---", "---", "---")
    h1, o1 = monthly(1)
    _, o2 = monthly(2)
    y1, y2 = yearly(1), yearly(2)
    for s in SERVICES:
        row(s, f"{h1[s]:.0f}", f"{o2[s]:.0f}", f"{y1[s]:.0f}", f"{y2[s]:.0f}")
    row("Total", f"{sum(h1.values()):.0f}", f"{sum(o2.values()):.0f}", f"{sum(y1.values()):.0f}", f"{sum(y2.values()):.0f}")

    print("\nBrigade load")
    row("Period", "Missions a month per brigade", "Missions per field day")
    row("---", "---", "---")
    startup = dict(o1, **{"Delimit the lot": FARMS / STARTUP_MONTHS})
    for name, m in (("Start-up round month", startup), ("Harvest month", h1), ("Outside-harvest month, after start-up", o1),
                    ("Outside-harvest month, following years", o2)):
        per_brigade = sum(m.values()) / BRIGADES
        row(name, f"{per_brigade:.0f}", f"{per_brigade / FIELD_DAYS:.1f}")

    print("\nCampaigns")
    per_dept = CAMPAIGNS_IN_HARVEST + outside_campaigns()
    row("Campaigns a year per department", per_dept)
    row("Campaigns a year in the pilot", per_dept * DEPARTMENTS)
    row("Farms per brigade", f"{FARMS / BRIGADES:.0f}")
    row("Estimation flights per brigade in a harvest month", f"{h1['Estimate the harvest'] / BRIGADES:.0f}")

    print("\nImages in a harvest month")
    est_images = h1["Estimate the harvest"] * IMAGES_PER_ESTIMATION
    precision = sum(HARVEST_MONTH.values())
    row("Estimation flights", f"{est_images:.0f}")
    row("Precision flights", f"{IMAGES_HARVEST_MONTH - est_images:.0f}", f"about {(IMAGES_HARVEST_MONTH - est_images) / precision:.0f} per flight")

    assert HARVEST_MONTH == {"Confirm the alert": 40, "Fumigate": 25, "Verify": 25}
    assert HARVEST_MONTH["Fumigate"] == HARVEST_MONTH["Verify"], "every fumigation has one verification"
    assert est_images <= IMAGES_HARVEST_MONTH
    assert y1["Estimate the harvest"] == FARMS * ESTIMATIONS_PER_FARM


if __name__ == "__main__":
    main()
