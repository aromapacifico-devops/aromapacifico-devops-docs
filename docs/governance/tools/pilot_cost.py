"""Consolidated cost of the pilot.

Reads the figures of the cost documents of this repository, adds them into the
tables of docs/governance/pilot-cost.md and prints those tables. Run with no
arguments. With --check it also verifies that the document shows every row.
"""
import argparse
import re
from pathlib import Path

GOV = Path(__file__).resolve().parent.parent
DOCS = GOV.parent
DOC = GOV / "pilot-cost.md"

# Labor of the infrastructure code, from the planning workbook. Hours by rate, USD an hour.
CODE_HOURS = {"Senior": (34, 32.0), "Junior": (66, 18.0)}

HARVEST_MONTHS = 4
NORMAL_MONTHS = 8
FARMS = 200


def read(path):
    return (DOCS / path).read_text(encoding="utf-8")


def num(text):
    return float(text.replace(",", ""))


def find(text, pattern):
    m = re.search(pattern, text)
    assert m, pattern
    return m.groups()


def row(text, label, cells):
    """Numbers of the first table row that starts with label, cells after it."""
    m = re.search(r"^\| " + re.escape(label) + r" \|(.*)$", text, re.M)
    assert m, label
    values = [c.strip().strip("*") for c in m.group(1).split("|")[:-1]]
    return [num(values[i]) for i in cells]


def sources():
    cloud = read("governance/cloud-cost.md")
    infer = read("governance/inference-cost.md")
    farm = read("governance/farm-hardware-and-fee.md")
    drone = read("drones/campaign-cost-estimation.md")
    basis = read("governance/price-basis.md")
    obs = read("architecture/observability.md")
    alerts = read("iot/alert-delivery.md")
    archive = read("architecture/persistence-and-archive.md")
    s = {}
    s["cloud"] = row(cloud, "**Cloud platform, production**", [1, 2])
    s["variable"] = row(cloud, "**Variable lines**", [1, 2])
    s["fixed"] = row(cloud, "**Fixed lines**", [1])[0]
    s["vpn"] = row(cloud, "Site-to-site VPN", [1])[0]
    s["endpoints"] = row(cloud, "Interface endpoints", [1])[0]
    s["inference_line"] = row(cloud, "Inference", [1, 2])
    lo, hi = find(cloud, r"\| Dedicated links of three centers[^|]*\| (\d+) to (\d+) \|")
    s["links"] = (num(lo), num(hi))
    s["envs"] = row(cloud, "Development and test, 80 hours each in a month", [0])[0]
    s["keys"] = row(cloud, "Platform keys of shared, development and test, kept by the bootstrap", [0])[0]
    s["dev_80"] = row(cloud, "Development", [3])[0]
    s["test_month"] = num(find(cloud, r"A test environment forgotten for a month at 24 hours a day costs USD ([\d.]+)")[0])
    harvest_rows = infer.split("| Harvest month | Invocations")[1].split("| Normal month | Invocations")[0]
    s["triggers"] = {name: row(harvest_rows, name, [0, 1, 2, 3]) for name in ("Focus confirmation", "Verification", "Harvest estimation", "Telemetry batch")}
    s["infer_harvest"] = row(harvest_rows, "Total", [0, 1, 2, 3])
    s["per_image"] = row(harvest_rows, "Vision functions per 1,000 images", [2])[0]
    s["infer_peak"] = row(infer, "All 200 estimation flights in one month", [0])[0]
    fleet = row(farm, "200 | 25% | 5", [3, 4, 5])
    s["farm_investment"], s["farm_cash"], s["farm_reserve"] = fleet
    s["farm_each"] = row(farm, "Total, for each farm", [0])[0]
    s["fee"] = num(find(farm, r"\| \*\*Option C, known part\*\* \| \| ([\d.]+) plus pending")[0])
    grow = re.search(r"CLOUD_VAR = \{\"Telemetry ingestion\": \(([\d.]+), [\d.]+\), \"Alert delivery\": \(([\d.]+), [\d.]+\)\}", read("governance/tools/farm_cost.py"))
    s["farm_cloud_var"] = num(grow.group(1)) + num(grow.group(2))
    drone = drone.split("## 8. Monthly and yearly cost")[1]
    s["drone_startup"] = row(drone, "Start-up month", [1])[0]
    s["drone_harvest"] = row(drone, "Harvest month", [1])[0]
    s["drone_off_first"] = row(drone, "Outside-harvest month, first year", [1])[0]
    s["drone_off"] = row(drone, "Outside-harvest month, following years", [1])[0]
    s["drone_year"] = row(drone, "**Total**", [0, 1])
    s["drone_dedicated"] = row(drone, "Brigades dedicated full time to the Federation", [0])[0]
    s["drone_sweeps"] = num(find(drone, r"cost about USD ([\d.]+) million a year")[0]) * 1e6
    s["trm"] = num(find(basis, r"\| TRM on 10 November 2026 \| ([\d,.]+) \|")[0])
    s["trm_low"] = num(find(basis, r"\| Lowest of the last 120 published rates \| ([\d,.]+) \|")[0])
    s["trm_high"] = num(find(basis, r"\| Highest of the last 120 published rates \| ([\d,.]+) \|")[0])
    s["obs_full"] = (row(obs, "Normal month | 465,900", [7])[0], row(obs, "Harvest month | 1,125,000", [7])[0])
    s["obs_chosen"] = (row(obs, "Normal month | 0.38", [4])[0], row(obs, "Harvest month | 0.86", [4])[0])
    s["dashboard"] = 3.00
    s["sms"] = num(find(alerts, r"\| SMS to Colombia \| USD ([\d.]+) per message")[0])
    s["crop_alerts"] = num(find(alerts, r"About (\d+) crop alerts and up to \d+ urgent drying alerts in a harvest month")[0])
    gb, glacier = find(archive, r"\| Photos and flight logs in Glacier Instant Retrieval \| ([\d,]+) GB × USD ([\d.]+) \|")
    s["archive_gb"], s["glacier"] = num(gb), num(glacier)
    s["standard"] = num(find(archive, r"against USD ([\d.]+) for S3 Standard")[0])
    return s


def usd(v):
    return f"{v:,.2f}"


def whole(v):
    return f"{v:,.0f}"


def render():
    s = sources()
    out = []
    p = out.append

    field = s["farm_cash"] - s["fixed"] - s["farm_cloud_var"] + s["farm_reserve"]
    labor = sum(h * r for h, r in CODE_HOURS.values())
    envs = s["envs"] + s["keys"]
    normal = s["cloud"][0] + envs + field + s["drone_off"]
    harvest = s["cloud"][1] + envs + field + s["drone_harvest"]
    year_cloud = NORMAL_MONTHS * s["cloud"][0] + HARVEST_MONTHS * s["cloud"][1]
    year = year_cloud + 12 * envs + 12 * field + s["drone_year"][1]
    links = s["links"]

    p("## Summary")
    p("| Item | Normal month | Harvest month | Following year |")
    p("|---|---:|---:|---:|")
    p(f"| Cloud platform, production | {usd(s['cloud'][0])} | {usd(s['cloud'][1])} | {usd(year_cloud)} |")
    p(f"| Links of the three collection centers | {whole(links[0])} to {whole(links[1])} | {whole(links[0])} to {whole(links[1])} | {whole(12 * links[0])} to {whole(12 * links[1])} |")
    p(f"| Development and test, with their keys | {usd(envs)} | {usd(envs)} | {usd(12 * envs)} |")
    p(f"| Field operation of {FARMS} farms | {usd(field)} | {usd(field)} | {usd(12 * field)} |")
    p(f"| Drone service | {usd(s['drone_off'])} | {usd(s['drone_harvest'])} | {usd(s['drone_year'][1])} |")
    p(f"| **Total without the links** | **{usd(normal)}** | **{usd(harvest)}** | **{usd(year)}** |")
    p(f"| **Total with the links** | **{whole(normal + links[0])} to {whole(normal + links[1])}** | **{whole(harvest + links[0])} to {whole(harvest + links[1])}** | **{whole(year + 12 * links[0])} to {whole(year + 12 * links[1])}** |")
    p("")
    p("| One-time item | USD | COP at the TRM |")
    p("|---|---:|---:|")
    p(f"| Field hardware and installation of {FARMS} farms, known part | {usd(s['farm_investment'])} | {whole(s['farm_investment'] * s['trm'])} |")
    p(f"| Start-up round of the drone service, extra cost of the first year | {usd(s['drone_year'][0] - s['drone_year'][1])} | {whole((s['drone_year'][0] - s['drone_year'][1]) * s['trm'])} |")
    p(f"| Infrastructure code, 100 hours | {usd(labor)} | {whole(labor * s['trm'])} |")
    p("")
    p("| Share of the following year | Percent |")
    p("|---|---:|")
    mid = year + 12 * sum(links) / 2
    for label, v in [("Drone service", s["drone_year"][1]), ("Field operation", 12 * field), ("Links of the centers", 12 * sum(links) / 2), ("Cloud platform and environments", year_cloud + 12 * envs)]:
        p(f"| {label} | {100 * v / mid:.1f} |")

    p("\n## Cloud")
    p("| Group of lines | Normal month | Harvest month |")
    p("|---|---:|---:|")
    p(f"| Variable lines, which follow the volume of the month | {usd(s['variable'][0])} | {usd(s['variable'][1])} |")
    p(f"| VPN and interface endpoints | {usd(s['vpn'] + s['endpoints'])} | {usd(s['vpn'] + s['endpoints'])} |")
    p(f"| Keys, secrets, web firewall, alarms and dashboard | {usd(s['fixed'] - s['vpn'] - s['endpoints'])} | {usd(s['fixed'] - s['vpn'] - s['endpoints'])} |")
    p(f"| **Cloud platform, production** | **{usd(s['cloud'][0])}** | **{usd(s['cloud'][1])}** |")
    p(f"| Harvest month with all estimation flights | | {usd(s['cloud'][1] - s['inference_line'][1] + s['infer_peak'])} |")

    p("\n## Inference")
    p("| Trigger in a harvest month | Invocations | Images | USD per 1,000 invocations | USD in the month |")
    p("|---|---:|---:|---:|---:|")
    for name, (inv, img, k, month) in s["triggers"].items():
        p(f"| {name} | {whole(inv)} | {whole(img)} | {usd(k)} | {usd(month)} |")
    inv, img, k, month = s["infer_harvest"]
    p(f"| **Total** | **{whole(inv)}** | **{whole(img)}** | **{usd(k)}** | **{usd(month)}** |")

    p("\n## Farms")
    p("| Item | Fleet of 200 farms | Each farm |")
    p("|---|---:|---:|")
    p(f"| Hardware and installation, known part, once | {usd(s['farm_investment'])} | {usd(s['farm_each'])} |")
    cash = s["farm_cash"] - s["fixed"] - s["farm_cloud_var"]
    p(f"| Data, SIM, maintenance and gateways, monthly | {usd(cash)} | {usd(cash / FARMS)} |")
    p(f"| Replacement reserve, monthly | {usd(s['farm_reserve'])} | {usd(s['farm_reserve'] / FARMS)} |")
    p(f"| **Field operation, monthly** | **{usd(field)}** | **{usd(field / FARMS)}** |")
    p(f"| Monthly amount proposed for each farm, with its share of the fixed cloud lines | | {usd(s['fee'])} |")

    p("\n## Drones")
    p("| Period | USD | Each farm | COP at the TRM |")
    p("|---|---:|---:|---:|")
    for label, v in [("Start-up month, first year", s["drone_startup"]), ("Harvest month", s["drone_harvest"]), ("Outside-harvest month, first year", s["drone_off_first"]), ("Outside-harvest month, following years", s["drone_off"]), ("First year", s["drone_year"][0]), ("Following years", s["drone_year"][1])]:
        p(f"| {label} | {usd(v)} | {usd(v / FARMS)} | {whole(v * s['trm'])} |")

    p("\n## Code")
    p("| Profile | Hours | USD an hour | USD |")
    p("|---|---:|---:|---:|")
    for label, (h, r) in CODE_HOURS.items():
        p(f"| {label} | {h} | {usd(r)} | {usd(h * r)} |")
    p(f"| **Total** | **{sum(h for h, _ in CODE_HOURS.values())}** | | **{usd(labor)}** |")

    always = s["dev_80"] / 80 * 730 + s["test_month"]
    obs_save = [full - chosen - s["dashboard"] for full, chosen in zip(s["obs_full"], s["obs_chosen"])]
    sms_save = s["crop_alerts"] * s["sms"]
    glacier_save = s["archive_gb"] * (s["standard"] - s["glacier"])
    p("\n## Savings")
    p("| Decision | Alternative avoided | Effect, USD |")
    p("|---|---|---:|")
    p(f"| Drone missions only where a sensor alert or a scheduled service calls them, paid by mission hour | Weekly sweeps of every farm | About {(s['drone_sweeps'] - s['drone_year'][1]) / 1e6:,.2f} million a year |")
    p(f"| Drone operator paid by mission hour | Three brigades dedicated full time | {usd(s['drone_dedicated'] - s['drone_year'][1])} a year |")
    p(f"| Development and test up only while the team works | Both environments on all month | {usd(always - s['envs'])} a month |")
    p(f"| Six custom metrics, one dashboard and saved queries | Fifteen metric series and two dashboards | {usd(obs_save[0])} a normal month, {usd(obs_save[1])} a harvest month |")
    p(f"| Push first, SMS only for urgent drying alerts | SMS for every crop alert too | {usd(sms_save)} a harvest month |")
    p(f"| Photos and flight logs in Glacier Instant Retrieval after 90 days | Five years in S3 Standard | {usd(glacier_save)} a month in year five |")

    p("\n## Exchange rate")
    p("| Rate, COP per USD | Following year with the links, COP million |")
    p("|---|---:|")
    for label, rate in [("TRM of the price basis", s["trm"]), ("Lowest of the last 120 rates", s["trm_low"]), ("Highest of the last 120 rates", s["trm_high"])]:
        p(f"| {label}, {rate:,.2f} | {(year + 12 * links[0]) * rate / 1e6:,.1f} to {(year + 12 * links[1]) * rate / 1e6:,.1f} |")
    p("")
    p("| Tax treatment | Following year with the links, USD |")
    p("|---|---:|")
    p(f"| Before IVA | {whole(year + 12 * links[0])} to {whole(year + 12 * links[1])} |")
    p(f"| IVA of 19 percent on every line | {whole((year + 12 * links[0]) * 1.19)} to {whole((year + 12 * links[1]) * 1.19)} |")
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = render()
    print(text)
    if args.check:
        doc = DOC.read_text(encoding="utf-8")
        missing = [line for line in text.splitlines() if line.startswith("| ") and not line.startswith("|---") and line not in doc]
        if missing:
            raise SystemExit("pilot-cost.md does not show:\n" + "\n".join(missing))
        print("OK the document shows every row")


main()
