"""Hardware, installation and monthly cost of a farm node, with the shared equipment and a sensitivity from 200 to 1,000 farms.

Run with no arguments. It prints the tables of docs/governance/farm-hardware-and-fee.md and ends with OK.

Origin of each input
  VERIFIED   A price that was read on a page on 2026-11-10 and is quoted as listed. It says nothing about the model fitting the node.
  ESTIMATE   A figure built from a stated rule on a listing of a different form, or from a currency conversion.
  ASSUMPTION A value set by the team with no source, replaced by a quote or a measurement.
  QUOTE      No price could be read. The item stays pending and is never counted as zero.

Nothing here is a commercial fee. The script prices cost, and no policy of the Federation sets what a farmer pays.
"""
import math
import re
import sys
from pathlib import Path

# ---- Exchange rates ----
TRM = {"central": 3269.88, "low": 3048.12, "high": 3796.87}  # COP per USD, price basis, 10 November 2026
EUR_USD = 1.1214  # ECB euro reference rate, 10 November 2026
IVA = 0.19

# ---- Price register. usd is None for a QUOTE, so it is never added as zero ----
# key: (name, qty per farm or per gateway, usd, status, source, currency read, tax and shipping)
PRICES = {
    "battery_low": ("Battery 12.8 V 12 Ah LiFePO4 with BMS, lower listing", 70.99, "VERIFIED", "Kastar listing, mykastar.com, read 2026-11-10", "USD 70.99", "Tax not stated, shipping said to be free. The page gives conflicting capacity and cycle figures and no datasheet"),
    "battery_high": ("Battery 12.8 V 12 Ah LiFePO4, higher listing", 159.00, "VERIFIED", "Battery Space listing, batteryspace.com, read 2026-11-10", "USD 159.00", "Tax and shipping not stated. Charge 0 to 40 C, UN38.3 passed, no BMS statement"),
    "panel": ("Solar panel 20 W 12 V", 39.50, "VERIFIED", "ACOPower listing HY020-12M, acopower.com, read 2026-11-10", "USD 39.50", "Tax and shipping not stated"),
    "controller": ("Charge controller 10 A, MPPT", 60.00, "VERIFIED", "Victron SmartSolar MPPT 75/10, Renewable Outdoors, read 2026-11-10", "USD 60.00", "Tax and shipping not stated. The lithium profile was not read on the page"),
    "cell_module": ("Cellular module LTE-M and NB-IoT, mini PCIe board", 35.86, "ESTIMATE", "Price basis, BG95-M3 mini PCIe at a US distributor, read 2026-11-10", "USD 35.86", "A board and not the bare module the node would use. Tax and duties not stated"),
    "lora_module": ("LoRa module STM32WLE5, US915/AU915 variant", 5.99, "VERIFIED", "RAK3172 SKU 306042, store.rakwireless.com, read 2026-11-10", "USD 5.99", "Shipping extra, tax not stated. The radio band is not chosen, see the LoRa path document"),
    "lora_antenna": ("Antenna for LoRa, 2 dBi", 5.00, "VERIFIED", "RAK 2 dBi antenna, store.rakwireless.com, read 2026-11-10", "USD 5.00", "Shipping extra, tax not stated. Fit to the mast not checked"),
    "soil_probe": ("Soil probe, 7 variables, RS485", round(295 / 3.64, 2), "ESTIMATE", "Voltaat listing VT-1767, voltaat.com, read 2026-11-10", "QAR 295.00 at 3.64 QAR per USD", "The conversion rate is a peg that was not read from a primary source. No manufacturer datasheet, so range and accuracy are unverified"),
    "gateway": ("LoRaWAN gateway RAK7289 V2, without VAT", round(537.76 / 1.19 * EUR_USD, 2), "ESTIMATE", "Price basis, EUR 537.76 at a European retailer, read 2026-11-10", "EUR 537.76 including German VAT of 19 percent", "VAT removed, converted at the ECB rate of 1.1214. Shipping extra. The variant for the frequency plan is not fixed"),
}

# ---- Pending items, with no price ----
PENDING_FARM_COMMON = ["Enclosure IP67", "Controller board", "Climate sensor", "Grain probe", "Mast and fixings", "Cable and connectors", "Shipping, import duties and IVA of every item"]
PENDING_FARM_CELL = ["Cellular antenna", "SIM or subscription, monthly fee for each SIM (the data price per MB is known)"]
PENDING_GATEWAY = ["Mast and fixings", "Solar kit", "Backhaul cellular plan, monthly", "Antenna and cables", "Shipping, import duties and IVA"]

# ---- Cloud lines, copied from docs/governance/cloud-cost.md and checked against it ----
CLOUD_FIXED = 170.10
CLOUD_VAR = {"Telemetry ingestion": (0.72, 0.98), "Alert delivery": (2.03, 10.17)}  # normal, harvest, for 200 farms
CLOUD_BASE_FARMS = 200
LORA_MESSAGE_USD = 0.000006
LORA_MESSAGES_PER_MONTH = 1440

# ---- Mobile data ----
EUR_PER_MB = 0.0025
MB_PER_MONTH = 5.5

# ---- Time and labor, all assumptions ----
ON_SITE_MIN = 100  # node specification, five steps
PREP_MIN = 30  # assembly check and identity provisioning before shipment
TECHNICIANS = 1
TRAVEL_HOURS = {"1 h": 1, "2 h": 2, "4 h": 4}
TRAVEL_BASE = "2 h"
RATE_COP = {"low": 15000, "mid": 25000, "high": 40000}  # COP per technician hour
RATE_BASE = "mid"
VEHICLE_COP_PER_TRAVEL_HOUR = 25000
MAINT_VISITS_PER_YEAR = 1
MAINT_ON_SITE_MIN = 60
GATEWAY_INSTALL_ON_SITE_H = 4
GATEWAY_TECHNICIANS = 2
GATEWAY_MAINT_ON_SITE_H = 2

# ---- Lives in years, assumptions ----
LIFE_YEARS = {"battery": 5, "panel": 10, "controller": 8, "soil_probe": 3, "cell_module": 8, "lora_module": 8, "lora_antenna": 8, "gateway": 7}

FARMS = [200, 400, 600, 800, 1000]
MIX = [0.0, 0.25, 0.50]
GATEWAY_DENSITY = [5, 10, 20]
COFFEE_COP_PER_LOAD = 2000000  # reference price of 125 kg of dry parchment coffee, Federation, 2026-11-10
KG_PER_LOAD = 125


def cop_to_usd(cop, trm="central"):
    return cop / TRM[trm]


def usd(v):
    return f"{v:,.2f}"


def hw_items(variant, battery):
    """Priced hardware of one farm. A pending item is not here, it is listed apart."""
    keys = ["battery_" + battery, "panel", "controller", "soil_probe"]
    keys += ["cell_module"] if variant == "cell" else ["lora_module", "lora_antenna"]
    return keys


def hw_known(variant, battery):
    verified = sum(PRICES[k][1] for k in hw_items(variant, battery) if PRICES[k][2] == "VERIFIED")
    estimate = sum(PRICES[k][1] for k in hw_items(variant, battery) if PRICES[k][2] == "ESTIMATE")
    return verified, estimate


def labor_usd(hours, rate="mid", techs=1):
    return cop_to_usd(hours * techs * RATE_COP[rate])


def install_usd(rate=RATE_BASE, travel=TRAVEL_BASE, techs=TECHNICIANS):
    t = TRAVEL_HOURS[travel]
    labor = labor_usd(ON_SITE_MIN / 60 + t, rate, techs) + labor_usd(PREP_MIN / 60, rate, 1)
    vehicle = cop_to_usd(VEHICLE_COP_PER_TRAVEL_HOUR * t)
    return labor + vehicle, labor, vehicle


def visit_usd(rate=RATE_BASE, travel=TRAVEL_BASE):
    t = TRAVEL_HOURS[travel]
    labor = labor_usd(MAINT_ON_SITE_MIN / 60 + t, rate, 1)
    vehicle = cop_to_usd(VEHICLE_COP_PER_TRAVEL_HOUR * t)
    return labor + vehicle


def gateway_install_usd(rate=RATE_BASE, travel=TRAVEL_BASE):
    t = TRAVEL_HOURS[travel]
    labor = labor_usd(GATEWAY_INSTALL_ON_SITE_H + t, rate, GATEWAY_TECHNICIANS)
    vehicle = cop_to_usd(VEHICLE_COP_PER_TRAVEL_HOUR * t)
    return labor + vehicle


def gateway_visit_usd(rate=RATE_BASE, travel=TRAVEL_BASE):
    t = TRAVEL_HOURS[travel]
    labor = labor_usd(GATEWAY_MAINT_ON_SITE_H + t, rate, GATEWAY_TECHNICIANS)
    vehicle = cop_to_usd(VEHICLE_COP_PER_TRAVEL_HOUR * t)
    return labor + vehicle


def reserve_month(variant, battery):
    total = 0.0
    for k in hw_items(variant, battery):
        life = LIFE_YEARS["battery" if k.startswith("battery") else k]
        total += PRICES[k][1] / (life * 12)
    return total


def data_cost_month():
    return EUR_PER_MB * MB_PER_MONTH * EUR_USD


def cloud_var_per_farm(month):
    return sum(v[month] for v in CLOUD_VAR.values()) / CLOUD_BASE_FARMS


def lora_msg_month():
    return LORA_MESSAGES_PER_MONTH * LORA_MESSAGE_USD


def check_cost_document():
    text = (Path(__file__).resolve().parent.parent / "cloud-cost.md").read_text(encoding="utf-8")

    def row(label):
        m = re.search(r"\| " + re.escape(label) + r" \|[^|]*\| ([\d.]+) \| ([\d.]+) \|", text)
        assert m, label
        return float(m.group(1)), float(m.group(2))

    for label, (a, b) in CLOUD_VAR.items():
        assert row(label) == (a, b), label
    fixed = re.search(r"\| \*\*Fixed lines\*\* \| \| \*\*([\d.]+)\*\*", text)
    assert fixed and float(fixed.group(1)) == CLOUD_FIXED
    tot = re.search(r"\| \*\*Cloud platform, production\*\* \| \| \*\*([\d.]+)\*\* \| \*\*([\d.]+)\*\*", text)
    assert tot
    return float(tot.group(1)), float(tot.group(2))


def main():
    cost_total = check_cost_document()
    assert 30 + 20 + 10 + 15 + 25 == ON_SITE_MIN
    assert math.isclose(CLOUD_FIXED, 109.50 + 43.80 + 5.00 + 1.60 + 8.00 + 2.20)

    print("## Exchange rates and tax")
    print("| Item | Value | Source and date |")
    print("|---|---|---|")
    print(f"| COP per USD, central, low and high | {TRM['central']:,.2f}, {TRM['low']:,.2f}, {TRM['high']:,.2f} | Price basis, 10 November 2026 |")
    print(f"| USD per EUR | {EUR_USD} | European Central Bank euro reference rate, 10 November 2026 |")
    print(f"| IVA | {IVA:.0%} | Price basis. Every figure is before tax. Import duties are unknown and are not included |")

    print("\n## Price register")
    print("| Item | Price as read | Used in USD | Status | Source and date | Tax, shipping and limits |")
    print("|---|---|---|---|---|---|")
    for k, (name, v, status, src, raw, note) in PRICES.items():
        print(f"| {name} | {raw} | {usd(v)} | {status.lower()} | {src} | {note} |")
    print("Items with no price read are listed as pending in the tables below and never counted as zero.")

    print("\n## Hardware of one farm, known subtotal and pending items")
    print("| Item | Cellular farm | LoRa farm | Status |")
    print("|---|---|---|---|")
    for label, ck, lk in [("Battery 12.8 V 12 Ah, lower listing", "battery_low", "battery_low"), ("Solar panel 20 W", "panel", "panel"), ("Charge controller 10 A", "controller", "controller"), ("Soil probe", "soil_probe", "soil_probe")]:
        print(f"| {label} | {usd(PRICES[ck][1])} | {usd(PRICES[lk][1])} | {PRICES[ck][2].lower()} |")
    print(f"| Radio | {usd(PRICES['cell_module'][1])} cellular module board | {usd(PRICES['lora_module'][1] + PRICES['lora_antenna'][1])} LoRa module and antenna | cellular estimate, LoRa verified |")
    vl_c, el_c = hw_known("cell", "low")
    vh_c, eh_c = hw_known("cell", "high")
    vl_l, el_l = hw_known("lora", "low")
    vh_l, eh_l = hw_known("lora", "high")
    print(f"| **Verified listings subtotal, battery lower and higher** | {usd(vl_c)} and {usd(vh_c)} | {usd(vl_l)} and {usd(vh_l)} | verified |")
    print(f"| **Estimated items subtotal** | {usd(el_c)} | {usd(el_l)} | estimate |")
    print(f"| **Known subtotal, verified and estimated, battery lower and higher** | {usd(vl_c + el_c)} and {usd(vh_c + eh_c)} | {usd(vl_l + el_l)} and {usd(vh_l + eh_l)} | |")
    print(f"| Pending items | {len(PENDING_FARM_COMMON) + len(PENDING_FARM_CELL)} | {len(PENDING_FARM_COMMON)} | quote |")
    print("\nPending items of a cellular farm: " + "; ".join(PENDING_FARM_COMMON + PENDING_FARM_CELL) + ".")
    print("Pending items of a LoRa farm: " + "; ".join(PENDING_FARM_COMMON) + ". The gateway share is in the shared equipment tables.")

    print("\n## Installation, one visit, of one farm")
    print("| Component | Value | Origin |")
    print("|---|---|---|")
    print(f"| Work on the site | {ON_SITE_MIN} minutes in five steps, 30 + 20 + 10 + 15 + 25 | Assumption of the node specification, not measured |")
    print(f"| Preparation before the visit | {PREP_MIN} minutes of one technician, assembly check and provisioning | Assumption |")
    print(f"| Technicians on the site | {TECHNICIANS}, with 2 as a scenario | Assumption, the specification names one installer |")
    print(f"| Travel, round trip | {', '.join(TRAVEL_HOURS)}, base {TRAVEL_BASE}, paid at the technician rate | Assumption, no farm location is known |")
    print(f"| Technician rate, COP per hour | low {RATE_COP['low']:,}, mid {RATE_COP['mid']:,}, high {RATE_COP['high']:,}, base {RATE_BASE} | Assumption. No source for a technician rate was found, and the legal minimum wage is not a technician rate |")
    print(f"| Vehicle, COP per hour of travel | {VEHICLE_COP_PER_TRAVEL_HOUR:,} | Assumption |")
    print("\n| Rate | Travel | Installation labor, USD | Vehicle, USD | Installation total, USD | With 2 technicians, USD |")
    print("|---|---|---|---|---|---|")
    for rate in RATE_COP:
        for travel in TRAVEL_HOURS:
            tot, lab, veh = install_usd(rate, travel, 1)
            tot2, _, _ = install_usd(rate, travel, 2)
            print(f"| {rate} | {travel} | {usd(lab)} | {usd(veh)} | {usd(tot)} | {usd(tot2)} |")
    base_total, base_lab, base_veh = install_usd()
    print(f"\nBase case, mid rate and 2 hours of travel, one technician, USD {usd(base_total)}. Later maintenance visits are not part of it, see the monthly tables.")

    print("\n## Monthly cost of one farm, USD, normal and harvest month")
    print("Cash cost and the replacement reserve are kept apart. A replacement bought later is paid from the reserve and is not added to the monthly total a second time.")
    print("| Line | Cellular farm | LoRa farm, own part | Kind | Included |")
    print("|---|---|---|---|---|")
    d = data_cost_month()
    lm = lora_msg_month()
    cvn, cvh = cloud_var_per_farm(0), cloud_var_per_farm(1)
    visit = visit_usd() * MAINT_VISITS_PER_YEAR / 12
    print(f"| Mobile data, {MB_PER_MONTH} MB at EUR {EUR_PER_MB} per MB | {usd(d)} | 0.00 | cash | yes |")
    print("| Fee for each SIM | pending | none | cash | no, pending a quote |")
    print(f"| Cloud lines driven by the farm count, normal and harvest | {usd(cvn)} and {usd(cvh)} | {usd(cvn)} and {usd(cvh)} | cash | yes |")
    print(f"| LoRaWAN messages of the cloud, possible overlap with the line above | 0.00 | {usd(lm)} | cash | yes, shown apart |")
    print(f"| Maintenance visit, {MAINT_VISITS_PER_YEAR} a year, {MAINT_ON_SITE_MIN} minutes on the site | {usd(visit)} | {usd(visit)} | cash | yes |")
    cash_c_n = d + cvn + visit
    cash_c_h = d + cvh + visit
    cash_l_n = cvn + lm + visit
    cash_l_h = cvh + lm + visit
    print(f"| **Marginal cash cost, normal and harvest** | {usd(cash_c_n)} and {usd(cash_c_h)} | {usd(cash_l_n)} and {usd(cash_l_h)} | cash | without the pending SIM fee |")
    rc = reserve_month("cell", "low")
    rl = reserve_month("lora", "low")
    rch = reserve_month("cell", "high")
    rlh = reserve_month("lora", "high")
    print(f"| Replacement reserve of the priced parts, battery lower and higher | {usd(rc)} and {usd(rch)} | {usd(rl)} and {usd(rlh)} | reserve | priced parts only, pending parts have no reserve yet |")
    print(f"| **Marginal economic cost, cash plus reserve, normal month, battery lower** | {usd(cash_c_n + rc)} | {usd(cash_l_n + rl)} | | |")

    print("\nLives used for the reserve, in years, are assumptions: " + ", ".join(f"{k.replace('_', ' ')} {v}" for k, v in LIFE_YEARS.items()) + ". The pages read give conflicting cycle figures for the battery and no datasheet.")

    print("\n## Shared equipment, gateways")
    gh_usd = PRICES["gateway"][1]
    gi = gateway_install_usd()
    gv = gateway_visit_usd() * MAINT_VISITS_PER_YEAR / 12
    gres = gh_usd / (LIFE_YEARS["gateway"] * 12)
    print("| Item for each gateway | Value, USD | Origin | Counted |")
    print("|---|---|---|---|")
    print(f"| Gateway RAK7289 V2 without VAT | {usd(gh_usd)} | estimate from the price basis, EUR 537.76 with VAT | once, in the investment |")
    print(f"| Installation, {GATEWAY_INSTALL_ON_SITE_H} hours with {GATEWAY_TECHNICIANS} technicians, base travel and vehicle | {usd(gi)} | assumption | once, in the investment |")
    print("| Mast, solar kit, antenna and cables, shipping, duties | pending | quote | pending |")
    print("| Energy | solar kit, no recurring cost | the kit is pending | no recurring line |")
    print("| Backhaul cellular plan | pending, monthly | quote | pending, monthly |")
    print(f"| Maintenance visit, {MAINT_VISITS_PER_YEAR} a year, {GATEWAY_MAINT_ON_SITE_H} hours with {GATEWAY_TECHNICIANS} technicians | {usd(gv)} a month | assumption | monthly cash |")
    print(f"| Replacement reserve of the gateway, {LIFE_YEARS['gateway']} years | {usd(gres)} a month | assumption | monthly reserve |")
    print("\nThe number of farms for each gateway is an economic assumption and says nothing about radio coverage. Gateways needed are rounded up, and each gateway is counted once.")
    print("| Farms for each gateway | Investment known for each LoRa farm from the gateway, USD | Monthly cash for each LoRa farm, USD | Monthly reserve for each LoRa farm, USD |")
    print("|---|---|---|---|")
    for dens in GATEWAY_DENSITY:
        print(f"| {dens} | {usd((gh_usd + gi) / dens)} | {usd(gv / dens)} | {usd(gres / dens)} |")
    print("These shares assume full gateways. A gateway with fewer farms costs each of them more, which the fleet table shows with the rounding.")

    print("\n## Fleet at 200 and 1,000 farms and in between, normal month, USD")
    print("Investment is the known subtotal with the battery at the lower listing, with installation, and without the pending items. Monthly cash adds the shared cloud lines and the gateways. The shared cloud lines are the fixed lines of the cost document divided by the farms, which includes what the platform also does for carriers, centers and buyers.")
    print("| Farms | LoRa share | Gateways for 5, 10, 20 farms | Investment known, 10 farms for each gateway | Monthly cash, 10 farms for each gateway | Monthly reserve, 10 farms for each gateway | Monthly cash and reserve for each farm | Fixed cloud lines for each farm |")
    print("|---|---|---|---|---|---|---|---|")
    vi_c = vl_c + el_c + base_total
    vi_l = vl_l + el_l + base_total
    rows = {}
    for n in FARMS:
        for s in MIX:
            nl = round(n * s)
            nc = n - nl
            gs = [math.ceil(nl / dens) if nl else 0 for dens in GATEWAY_DENSITY]
            g = math.ceil(nl / 10) if nl else 0
            inv = nc * vi_c + nl * vi_l + g * (gh_usd + gi)
            cash_var = n * (cvn) + nc * (d + visit) + nl * (lm + visit) + g * gv
            fixed = CLOUD_FIXED
            reserve = nc * rc + nl * rl + g * gres
            total_cash = cash_var + fixed
            per_farm = (total_cash + reserve) / n
            rows[(n, s)] = (inv, total_cash, reserve, per_farm)
            print(f"| {n} | {s:.0%} | {', '.join(str(x) for x in gs)} | {usd(inv)} | {usd(total_cash)} | {usd(reserve)} | {usd(per_farm)} | {usd(fixed / n)} |")
    print("\nThe monthly figures hold the SIM fee, the gateway plan and the pending items out, so they are lower than the real cost by those amounts.")

    print("\n## Gateways for each assumption of farms in range, 200 and 1,000 farms, normal month, USD")
    print("| Farms | LoRa share | Farms for each gateway | Gateways, rounded up | Investment known | Monthly cash | Monthly reserve | Cash and reserve for each farm |")
    print("|---|---|---|---|---|---|---|---|")
    for n in (200, 1000):
        for s_ in (0.25, 0.50):
            for dens in GATEWAY_DENSITY:
                nl_ = round(n * s_)
                nc_ = n - nl_
                g_ = math.ceil(nl_ / dens)
                inv_ = nc_ * vi_c + nl_ * vi_l + g_ * (gh_usd + gi)
                cash_ = n * cvn + nc_ * (d + visit) + nl_ * (lm + visit) + g_ * gv + CLOUD_FIXED
                res_ = nc_ * rc + nl_ * rl + g_ * gres
                print(f"| {n} | {s_:.0%} | {dens} | {g_} | {usd(inv_)} | {usd(cash_)} | {usd(res_)} | {usd((cash_ + res_) / n)} |")

    print("\n## Loaded and marginal cost of one farm by number of farms, 10 farms for each gateway, 25 percent LoRa, normal month")
    print("| Farms | Marginal cash cost for each farm | Shared cloud lines for each farm | Reserve of the parts and gateway share for each farm | Cash and reserve for each farm |")
    print("|---|---|---|---|---|")
    for n in FARMS:
        nl = round(n * 0.25)
        nc = n - nl
        g = math.ceil(nl / 10)
        marg = (nc * (d + cvn + visit) + nl * (cvn + lm + visit)) / n
        shared = CLOUD_FIXED / n
        gw = (g * (gv + gres)) / n
        res_own = (nc * rc + nl * rl) / n
        print(f"| {n} | {usd(marg)} | {usd(shared)} | {usd(gw + res_own)} | {usd(marg + shared + gw + res_own)} |")

    print("\n## Context, not a judgment")
    print("The investment of a cellular farm, known subtotal with installation and the battery at the lower listing, in kilograms of dry parchment coffee at the reference price of the Federation of 10 November 2026, COP 2,000,000 for a load of 125 kg, so COP 16,000 a kilogram.")
    print("| Case | Investment known, USD | COP at the central TRM | Kilograms of dry parchment coffee | Same at the low and high TRM |")
    print("|---|---|---|---|---|")
    for label, v in [("Cellular farm", vi_c), ("LoRa farm without the gateway share", vi_l)]:
        cop = v * TRM["central"]
        kg = cop / (COFFEE_COP_PER_LOAD / KG_PER_LOAD)
        lo = v * TRM["low"] / (COFFEE_COP_PER_LOAD / KG_PER_LOAD)
        hi = v * TRM["high"] / (COFFEE_COP_PER_LOAD / KG_PER_LOAD)
        print(f"| {label} | {usd(v)} | {cop:,.0f} | {kg:,.1f} | {lo:,.1f} to {hi:,.1f} |")
    print("The comparison shows no profitability and no capacity to pay. The pending items would raise both figures.")

    print("\n## IVA scenario")
    print(f"If IVA of {IVA:.0%} applies in full to the known subtotal, a cellular farm with installation goes from {usd(vi_c)} to {usd(vi_c * (1 + IVA))}. Import duties are unknown and are not in either figure.")

    print("\n## Cost document, two values for one total")
    print(f"The cost document of this repository gives {cost_total[0]} for a normal month and {cost_total[1]} for a harvest month. The project status of the handbook gives 177.23 and 201.11. The script reads the first.")
    print("OK")


main()
