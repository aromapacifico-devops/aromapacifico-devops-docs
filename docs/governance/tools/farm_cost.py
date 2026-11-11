"""Hardware, installation and monthly cost of a farm node, with the shared equipment and a sensitivity from 200 to 1,000 farms.

Run with no arguments. It prints the tables of docs/governance/farm-hardware-and-fee.md and ends with OK.

Origin of each input
  VERIFIED   A price read on a page on 2026-11-10 and quoted as listed. It does not show that the part meets the node requirements.
  ESTIMATE   A figure built from a stated rule, such as a listing of a different form, a conversion, or a published tariff times an assumed volume.
  ASSUMPTION A value set by the team with no source, replaced by a quote or a measurement.
  PENDING    No equivalent price was found. The item stays out of every total and is named in it as an unknown.

Nothing here is a commercial fee. The script prices cost. A fee needs a policy of the Federation.
"""
import math
import re
from pathlib import Path

SC = ("low", "base", "high")

# ---- Exchange rates and tax ----
TRM = {"central": 3269.88, "low": 3048.12, "high": 3796.87}  # COP per USD, price basis, 10 November 2026
EUR_USD = 1.1214  # ECB euro reference rate, 10 November 2026
IVA = 0.19

# ---- Price register of what was read. usd is (low, base, high) ----
P = {
    "battery": ("Battery 12.8 V 12 Ah LiFePO4", (70.99, 159.00, 159.00), "VERIFIED", "Kastar listing for the low case, Battery Space listing for the base and high cases, read 2026-11-10", "USD 70.99 and USD 159.00", "Tax not stated on either page. See the equivalence table. Neither is shown equivalent to the node requirement"),
    "panel": ("Solar panel 20 W 12 V", (39.50,) * 3, "VERIFIED", "ACOPower HY020-12M, acopower.com, read 2026-11-10", "USD 39.50", "Tax and shipping not stated"),
    "controller": ("Charge controller 10 A, MPPT", (60.00,) * 3, "VERIFIED", "Victron SmartSolar MPPT 75/10, Renewable Outdoors, read 2026-11-10", "USD 60.00", "Tax and shipping not stated. The lithium profile was not read on the page"),
    "soil_probe": ("Soil probe, 7 variables, RS485", (round(295 / 3.64, 2),) * 3, "ESTIMATE", "Voltaat VT-1767, voltaat.com, read 2026-11-10", "QAR 295.00 at 3.64 QAR per USD", "The rate is a peg that was not read from a primary source. No datasheet, so range and accuracy are unverified"),
    "cell_board": ("Cellular board LTE-M and NB-IoT", (30.00, 35.86, 56.02), "VERIFIED", "RAK5860 with a BG77 module (low), a BG95-M3 mini PCIe board from the price basis (base), a BG95-M3 evaluation board at DigiKey (high), read 2026-11-10", "USD 30.00, USD 35.86, USD 56.02", "All three are boards and not the bare module that the node would use. Bands for Colombia not checked"),
    "cell_antenna": ("Cellular antenna", (39.97,) * 3, "VERIFIED", "ALFA AOA-4G-5AM N-male, Rokland, read 2026-11-10", "USD 39.97", "Covers 698 to 960 and 1,710 to 2,700 MHz. It is a larger antenna than a node may need. Fit to the mast not checked"),
    "lora_board": ("LoRa module STM32WLE5, US915/AU915", (5.99,) * 3, "VERIFIED", "RAK3172 SKU 306042, store.rakwireless.com, read 2026-11-10", "USD 5.99", "Shipping extra, tax not stated. The radio band is not chosen"),
    "lora_antenna": ("Antenna for LoRa, 2 dBi", (5.00,) * 3, "VERIFIED", "RAK 2 dBi antenna, store.rakwireless.com, read 2026-11-10", "USD 5.00", "Shipping extra, tax not stated. Fit to the mast not checked"),
    "gw_bundle": ("LoRaWAN gateway with solar kit, 8 channels AU915, cellular LTE variant", (1199.00,) * 3, "VERIFIED", "WisGate Edge Pro Solar, variant 817039, store.rakwireless.com, read 2026-11-10", "USD 1,199.00", "Includes the gateway, a 50 Ah battery, an 80 W panel with its mounting kit and the cables between them. Shipping extra, tax not stated. The LTE is a Cat 4 module and not LTE-M"),
    "gw_antenna": ("Antenna for the gateway, 915 MHz N-male", (16.97, 16.97, 42.97), "VERIFIED", "4 dBi fiberglass (low, base) and 5.8 dBi (high), Rokland, read 2026-11-10", "USD 16.97 and USD 42.97", "Fit to the gateway connector not checked"),
}

# Reference listings that were found and are not equivalent, so they stay out of every total
REFERENCES = [
    ("Enclosure", "RAK Unify IP67 150 x 100 x 45 mm at USD 39.00", "Too small for a 151 x 98 x 95 mm battery, so it is not equivalent to the node enclosure"),
    ("Controller board", "RAK19007 base 9.99, RAK4631 core 17.99, RAK5802 RS485 6.00, RAK12002 RTC 9.50 and RAK15001 flash 5.00, together USD 48.48", "A development kit. Its flash is 16 Mbit against at least 64 MB with encryption, and it has no switched probe supplies or field input protection"),
    ("Climate sensor", "RAK1901 SHTC3 module at USD 4.60, Milesight NB300-TH at USD 59.90", "The first has no outdoor rating, and the second is a standalone NB-IoT device and not a probe for the controller"),
    ("Grain probe", "No listing found", ""),
    ("Mast and fixings", "RAK Unify pole kit at USD 6.50 and a 12 inch pole mast at USD 19.50", "They fit a small enclosure and are not a mast of the height that the sensors design requires"),
    ("Cable and connectors", "No listing of the RS485 cable and glands of the node found", ""),
]
PENDING_FARM = ["Enclosure IP67", "Controller board", "Climate sensor", "Grain probe", "Mast and fixings", "Cable and connectors", "Shipping, import duties and IVA of every item"]
PENDING_GATEWAY = ["Mast of the height the site study sets", "Cables and lightning protection", "Shipping, import duties and IVA"]

# ---- Connectivity, cellular nodes and gateways. Data traffic is kept apart from the fixed charge of the SIM ----
HOLOGRAM = {"per_mb": 0.03, "per_month": 1.00, "card": 3.00}  # self-service tariff, hologram.io/pricing, read 2026-11-10
PREPAID = {"plan": 14.00, "card": 1.00, "mb_included": 500}  # global prepaid plan quoted in the price basis, coverage in Colombia not named
NODE_MB = (5.5, 5.5, 20.0)  # low, base (price basis), high (assumption: firmware and retries)
GATEWAY_MB = (20.0, 50.0, 150.0)  # assumption, no documented figure for a Basics Station gateway

# ---- Cloud lines, copied from docs/governance/cloud-cost.md and checked against it ----
CLOUD_FIXED = 170.10
CLOUD_VAR = {"Telemetry ingestion": (0.72, 0.98), "Alert delivery": (2.03, 10.17)}
CLOUD_BASE_FARMS = 200
LORA_MESSAGE_USD = 0.000006
LORA_MESSAGES_PER_MONTH = 1440

# ---- Time and labor, all assumptions, low, base, high ----
ON_SITE_MIN = 100
PREP_MIN = 30
TECHNICIANS = (1, 1, 2)
TRAVEL_H = (1, 2, 4)
RATE_COP = (15000, 25000, 40000)
VEHICLE_COP_PER_H = 25000
VISITS_PER_YEAR = (1, 1, 2)
MAINT_ON_SITE_MIN = 60
GW_INSTALL_H = 4
GW_TECHNICIANS = 2
GW_MAINT_H = 2
LIFE = {
    "battery": (8, 5, 3), "panel": (12, 10, 8), "controller": (10, 8, 6), "soil_probe": (5, 3, 2),
    "cell_board": (10, 8, 6), "cell_antenna": (10, 8, 6), "lora_board": (10, 8, 6), "lora_antenna": (10, 8, 6), "gw_bundle": (9, 7, 5), "gw_antenna": (10, 8, 6),
}

FARMS = [200, 400, 600, 800, 1000]
MIX = [0.0, 0.25, 0.50]
DENSITY = [5, 10, 20]
COFFEE_COP_PER_LOAD = 2000000
KG_PER_LOAD = 125
FINANCE_MONTHS = 36


def i_(s):
    return SC.index(s)


def usd(v):
    return f"{v:,.2f}"


def cop_usd(cop):
    return cop / TRM["central"]


def price(key, s):
    return P[key][1][i_(s)]


def farm_keys(variant):
    base = ["battery", "panel", "controller", "soil_probe"]
    return base + (["cell_board", "cell_antenna"] if variant == "cell" else ["lora_board", "lora_antenna"])


def hardware(variant, s):
    return sum(price(k, s) for k in farm_keys(variant))


def one_time_connectivity(variant, s):
    if variant == "lora":
        return 0.0
    return PREPAID["plan"] + PREPAID["card"] if s == "low" else HOLOGRAM["card"]


def data_cost(variant, s):
    if variant == "lora" or s == "low":
        return 0.0  # the prepaid plan of the low case has its data inside the one time payment
    return NODE_MB[i_(s)] * HOLOGRAM["per_mb"]


def sim_fixed(variant, s):
    if variant == "lora" or s == "low":
        return 0.0
    return HOLOGRAM["per_month"]


def install(s):
    k = i_(s)
    t = TRAVEL_H[k]
    labor = cop_usd(RATE_COP[k] * ((ON_SITE_MIN / 60 + t) * TECHNICIANS[k] + PREP_MIN / 60))
    vehicle = cop_usd(VEHICLE_COP_PER_H * t)
    return labor, vehicle


def visit(s):
    k = i_(s)
    t = TRAVEL_H[k]
    return cop_usd(RATE_COP[k] * (MAINT_ON_SITE_MIN / 60 + t)) + cop_usd(VEHICLE_COP_PER_H * t)


def maintenance_month(s):
    return visit(s) * VISITS_PER_YEAR[i_(s)] / 12


def cloud_var(month):
    return sum(v[month] for v in CLOUD_VAR.values()) / CLOUD_BASE_FARMS


def lora_msg():
    return LORA_MESSAGES_PER_MONTH * LORA_MESSAGE_USD


def reserve(variant, s):
    return sum(price(k, s) / (LIFE[k][i_(s)] * 12) for k in farm_keys(variant))


def gw_hardware(s):
    return price("gw_bundle", s) + price("gw_antenna", s)


def gw_install(s):
    k = i_(s)
    t = TRAVEL_H[k]
    return cop_usd(RATE_COP[k] * (GW_INSTALL_H + t) * GW_TECHNICIANS) + cop_usd(VEHICLE_COP_PER_H * t) + HOLOGRAM["card"]


def gw_data(s):
    return GATEWAY_MB[i_(s)] * HOLOGRAM["per_mb"]


def gw_fixed(s):
    return HOLOGRAM["per_month"]


def gw_maintenance(s):
    k = i_(s)
    t = TRAVEL_H[k]
    v = cop_usd(RATE_COP[k] * (GW_MAINT_H + t) * GW_TECHNICIANS) + cop_usd(VEHICLE_COP_PER_H * t)
    return v * VISITS_PER_YEAR[k] / 12


def gw_reserve(s):
    return gw_hardware(s) / (LIFE["gw_bundle"][i_(s)] * 12)


def gw_cash(s):
    return gw_data(s) + gw_fixed(s) + gw_maintenance(s)


def fleet(n, mix, dens, s):
    nl = round(n * mix)
    nc = n - nl
    g = math.ceil(nl / dens) if nl else 0
    inv_nodes = nc * (hardware("cell", s) + one_time_connectivity("cell", s)) + nl * hardware("lora", s)
    inv_install = n * sum(install(s))
    inv_gw = g * (gw_hardware(s) + gw_install(s))
    cv = cloud_var(0)
    rec_nodes = nc * (data_cost("cell", s) + sim_fixed("cell", s)) + n * (cv + maintenance_month(s)) + nl * lora_msg()
    rec_gw = g * gw_cash(s)
    res = nc * reserve("cell", s) + nl * reserve("lora", s) + g * gw_reserve(s)
    return {"nl": nl, "nc": nc, "g": g, "inv_nodes": inv_nodes, "inv_install": inv_install, "inv_gw": inv_gw, "inv": inv_nodes + inv_install + inv_gw,
            "rec_nodes": rec_nodes, "rec_gw": rec_gw, "rec_cash_own": rec_nodes + rec_gw, "fixed": CLOUD_FIXED, "reserve": res}


def check_cost_document():
    text = (Path(__file__).resolve().parent.parent / "cloud-cost.md").read_text(encoding="utf-8")

    def row(label):
        m = re.search(r"\| " + re.escape(label) + r" \|[^|]*\| ([\d.]+) \| ([\d.]+) \|", text)
        assert m, label
        return float(m.group(1)), float(m.group(2))

    for label, v in CLOUD_VAR.items():
        assert row(label) == v, label
    fixed = re.search(r"\| \*\*Fixed lines\*\* \| \| \*\*([\d.]+)\*\*", text)
    assert fixed and float(fixed.group(1)) == CLOUD_FIXED
    tot = re.search(r"\| \*\*Cloud platform, production\*\* \| \| \*\*([\d.]+)\*\* \| \*\*([\d.]+)\*\*", text)
    assert tot
    return float(tot.group(1)), float(tot.group(2))


def main():
    cost_total = check_cost_document()
    assert 30 + 20 + 10 + 15 + 25 == ON_SITE_MIN
    assert math.isclose(CLOUD_FIXED, 109.50 + 43.80 + 5.00 + 1.60 + 8.00 + 2.20)
    assert math.isclose(12.8 * 12, 153.6)
    assert PREPAID["mb_included"] / NODE_MB[0] > 12

    print("## Exchange rates and tax")
    print("| Item | Value | Source and date |")
    print("|---|---|---|")
    print(f"| COP per USD, central, low and high | {TRM['central']:,.2f}, {TRM['low']:,.2f}, {TRM['high']:,.2f} | Price basis, 10 November 2026 |")
    print(f"| USD per EUR | {EUR_USD} | European Central Bank euro reference rate, 10 November 2026 |")
    print(f"| IVA | {IVA:.0%} | Price basis. Every figure is before tax. Import duties are unknown and are not included |")

    print("\n## Price register")
    print("| Item | Price as read | Used, low, base and high, USD | Status | Source and date | Tax, shipping and limits |")
    print("|---|---|---|---|---|---|")
    for k, (name, v, st, src, raw, note) in P.items():
        print(f"| {name} | {raw} | {', '.join(usd(x) for x in v)} | {st.lower()} | {src} | {note} |")
    print("| Self-service SIM tariff of a global provider | USD 0.03 per MB, USD 1 a month for each SIM, USD 3 for each card | see connectivity | estimate | hologram.io/pricing, read 2026-11-10 | Coverage and LTE-M service in Colombia not confirmed, so it is a published tariff and not an offer |")
    print("| Prepaid plan of a global provider | USD 14 one time with 500 MB, card USD 1 | low case | estimate | Price basis, read 2026-11-10 | Colombia not named as covered. 500 MB lasts more than 7 years at 5.5 MB a month |")
    print("\nReference listings found for the pending items. They are not equivalent and stay out of every total.")
    print("")
    print("| Pending item | Listing found | Why it is not equivalent |")
    print("|---|---|---|")
    for name, listing, why in REFERENCES:
        print(f"| {name} | {listing} | {why or 'No listing to compare'} |")

    print("\n## Equivalence of the two batteries")
    print("The node specification asks for 12.8 V, 12 Ah nominal, LiFePO4, a battery management system, the datasheet limits including the low temperature charging limit, and the energy of 12.8 V times 12 Ah, which is 153.6 Wh.")
    print("")
    print("| Property | Requirement | Lower listing, USD 70.99 | Higher listing, USD 159.00 |")
    print("|---|---|---|---|")
    print("| Chemistry and voltage | LiFePO4, 12.8 V | 12.8 V stated | 12.8 V stated |")
    print("| Capacity | 12 Ah nominal | 12 Ah at C/5 | Typical 12 Ah, minimum 11.85 Ah at 0.2C |")
    print("| Energy | 153.6 Wh | The title says 153.6 Wh and a bullet says 84 Wh, so it conflicts | The title says 144 Wh, which is below 153.6 Wh |")
    print("| Protection | A battery management system | Built-in BMS stated | No BMS statement on the page. UN38.3 passed |")
    print("| Low temperature charge limit | Stated in the datasheet | Not stated | Charge 0 to 40 C, discharge minus 20 to 60 C |")
    print("| Cycle life | Datasheet figure | Two figures that conflict, 2,500 to 7,000 and more than 2,000 | Not stated |")
    print("| Accessories | Not part of the requirement | None listed, free shipping stated | None listed |")
    print("| Shown equivalent | | No. The energy and the charge limit are not consistent | No. The BMS is not stated and the energy is stated lower |")
    print("")
    print("The low case uses the lower listing, and the base and high cases use the higher listing, which states the temperature limits that the specification needs. The cheapest listing is not taken as the base because it is not shown equivalent. A datasheet decides which one the node uses.")

    print("\n## Hardware of one farm, by scenario")
    print("Known subtotal of priced parts. The pending items are not in it and are not zero. Every total below reads as the known subtotal plus the unknown cost of the pending items.")
    print("")
    print("| Item | Low | Base | High | Status |")
    print("|---|---|---|---|---|")
    for key, label in [("battery", "Battery"), ("panel", "Solar panel 20 W"), ("controller", "Charge controller"), ("soil_probe", "Soil probe")]:
        print(f"| {label} | {' | '.join(usd(price(key, s)) for s in SC)} | {P[key][2].lower()} |")
    print(f"| Cellular farm, radio board | {' | '.join(usd(price('cell_board', s)) for s in SC)} | verified, as a board |")
    print(f"| Cellular farm, antenna | {' | '.join(usd(price('cell_antenna', s)) for s in SC)} | verified |")
    print(f"| LoRa farm, module and antenna | {' | '.join(usd(price('lora_board', s) + price('lora_antenna', s)) for s in SC)} | verified |")
    print(f"| **Known subtotal, cellular farm** | {' | '.join(usd(hardware('cell', s)) for s in SC)} | known part only |")
    print(f"| **Known subtotal, LoRa farm** | {' | '.join(usd(hardware('lora', s)) for s in SC)} | known part only |")
    print(f"| SIM card or prepaid plan, one time, cellular farm | {' | '.join(usd(one_time_connectivity('cell', s)) for s in SC)} | estimate, no plan is contracted |")
    print("")
    print("Pending items of every farm, each an unknown cost: " + "; ".join(PENDING_FARM) + ".")

    print("\n## Installation, one visit, of one farm, by scenario")
    print("| Component | Low | Base | High | Origin |")
    print("|---|---|---|---|---|")
    print(f"| Work on the site, minutes | {ON_SITE_MIN} | {ON_SITE_MIN} | {ON_SITE_MIN} | Assumption of the node specification, five steps of 30 + 20 + 10 + 15 + 25, and not measured |")
    print(f"| Preparation before the visit, minutes of one technician | {PREP_MIN} | {PREP_MIN} | {PREP_MIN} | Assumption |")
    print(f"| Technicians on the site | {' | '.join(str(x) for x in TECHNICIANS)} | Assumption |")
    print(f"| Travel, round trip, hours | {' | '.join(str(x) for x in TRAVEL_H)} | Assumption, no farm location is known |")
    print(f"| Technician rate, COP an hour | {' | '.join(f'{x:,}' for x in RATE_COP)} | Assumption. No source for a technician rate was found, and the legal minimum wage is not a technician rate |")
    print(f"| Vehicle, COP an hour of travel | {VEHICLE_COP_PER_H:,} | {VEHICLE_COP_PER_H:,} | {VEHICLE_COP_PER_H:,} | Assumption |")
    print(f"| Labor, USD | {' | '.join(usd(install(s)[0]) for s in SC)} | Calculation |")
    print(f"| Vehicle, USD | {' | '.join(usd(install(s)[1]) for s in SC)} | Calculation |")
    print(f"| **Installation total, USD** | {' | '.join(usd(sum(install(s))) for s in SC)} | Investment, one visit |")

    print("\n## Investment of one farm by scenario, USD")
    print("Initial investment only. Recurring cost is in the next table. Shipping, duties, IVA and the pending items are outside.")
    print("")
    print("| Case | Low | Base | High |")
    print("|---|---|---|---|")
    for variant, label in [("cell", "Cellular farm"), ("lora", "LoRa farm, without its gateway share")]:
        print(f"| {label}, known hardware and SIM start | {' | '.join(usd(hardware(variant, s) + one_time_connectivity(variant, s)) for s in SC)} |")
        print(f"| {label}, installation | {' | '.join(usd(sum(install(s))) for s in SC)} |")
        print(f"| **{label}, known investment, plus the unknown cost of the pending items** | {' | '.join(usd(hardware(variant, s) + one_time_connectivity(variant, s) + sum(install(s))) + ' plus pending' for s in SC)} |")

    print("\n## Monthly cost of one farm by scenario, USD, normal month")
    print("Cash cost and the replacement reserve are kept apart. A replacement bought later is paid from the reserve and is not added to the monthly total a second time. Data traffic and the fixed charge of the SIM are separate lines.")
    print("")
    print("| Line | Cellular low | Cellular base | Cellular high | LoRa base | Kind |")
    print("|---|---|---|---|---|---|")
    cv = cloud_var(0)
    print(f"| Mobile data traffic | {' | '.join(usd(data_cost('cell', s)) for s in SC)} | 0.00 | cash |")
    print(f"| Fixed charge of the SIM | {' | '.join(usd(sim_fixed('cell', s)) for s in SC)} | 0.00 | cash |")
    print(f"| Cloud lines that grow with the farm count | {usd(cv)} | {usd(cv)} | {usd(cv)} | {usd(cv)} | cash |")
    print(f"| LoRaWAN messages of the cloud | 0.00 | 0.00 | 0.00 | {usd(lora_msg())} | cash |")
    print(f"| Maintenance visits | {' | '.join(usd(maintenance_month(s)) for s in SC)} | {usd(maintenance_month('base'))} | cash |")
    cash = {s: data_cost("cell", s) + sim_fixed("cell", s) + cv + maintenance_month(s) for s in SC}
    cash_l = cv + lora_msg() + maintenance_month("base")
    print(f"| **Marginal cash cost** | {' | '.join(usd(cash[s]) for s in SC)} | {usd(cash_l)} | cash |")
    print(f"| Replacement reserve of the priced parts | {' | '.join(usd(reserve('cell', s)) for s in SC)} | {usd(reserve('lora', 'base'))} | reserve |")
    print(f"| **Marginal cash plus reserve** | {' | '.join(usd(cash[s] + reserve('cell', s)) for s in SC)} | {usd(cash_l + reserve('lora', 'base'))} | |")
    print("")
    print("The plan of the operator is not contracted. The connectivity lines use a published self-service tariff of a global provider, whose coverage and LTE-M service in Colombia are not confirmed, and a prepaid plan for the low case. They are estimates and not the connectivity cost of an offer, so complete connectivity is not stated.")
    m3 = maintenance_month("base")
    print(f"The earlier figure of USD 3.21 a month for a cellular farm held {usd(m3)} of maintenance visit labor and vehicle, {usd(cv)} of cloud lines and 0.02 of data traffic. It held no fixed charge of a SIM. The maintenance visit was 99 percent of it.")

    print("\n## Gateways, shared equipment, by scenario")
    print("| Item for each gateway | Low | Base | High | Counted |")
    print("|---|---|---|---|---|")
    print(f"| Gateway with solar kit and antenna | {' | '.join(usd(gw_hardware(s)) for s in SC)} | once, investment |")
    print(f"| Installation, {GW_INSTALL_H} hours with {GW_TECHNICIANS} technicians, travel, vehicle and the SIM card | {' | '.join(usd(gw_install(s)) for s in SC)} | once, investment |")
    print(f"| Backhaul data traffic, {', '.join(f'{x:g}' for x in GATEWAY_MB)} MB a month | {' | '.join(usd(gw_data(s)) for s in SC)} | monthly cash |")
    print(f"| Fixed charge of the SIM | {' | '.join(usd(gw_fixed(s)) for s in SC)} | monthly cash |")
    print(f"| Maintenance visits with {GW_TECHNICIANS} technicians | {' | '.join(usd(gw_maintenance(s)) for s in SC)} | monthly cash |")
    print(f"| Replacement reserve | {' | '.join(usd(gw_reserve(s)) for s in SC)} | monthly reserve |")
    print("")
    print("The gateway bundle includes the solar kit, its battery, the panel and the mounting, so energy is in the purchase once and has no recurring line. The kit has a 50 Ah battery at 12.8 V, which is 640 Wh and 512 Wh usable at 0.80. The LoRa path document asks 450 Wh for 3 days and 750 Wh for 5 days at a load of 5 W, and a panel of 56 W. The kit meets the 3 day case and the panel, and reaches 5 days only up to about 4.3 W, so it is equivalent under a load of 4 W or less. The load of the gateway was not read, and the page says the kit gives more than 5 days.")
    print("")
    print(f"Pending for each gateway: {'; '.join(PENDING_GATEWAY)}. The gateway of the price basis, EUR 537.76 at a retailer with VAT, differs from the USD 382.00 that the manufacturer store lists for the 8 channel variant without LTE and from the USD 1,199.00 for the bundle used here.")
    print("")
    print("The number of farms for each gateway is an economic assumption and says nothing about radio coverage. Gateways are rounded up and each is counted once.")
    print("")
    print("| Farms for each gateway | Investment from the gateway for each LoRa farm, base | Monthly cash for each LoRa farm, base | Monthly reserve for each LoRa farm, base |")
    print("|---|---|---|---|")
    for dens in DENSITY:
        print(f"| {dens} | {usd((gw_hardware('base') + gw_install('base')) / dens)} | {usd(gw_cash('base') / dens)} | {usd(gw_reserve('base') / dens)} |")
    print("")
    print("These shares assume full gateways. The fleet tables show the rounding.")

    print("\n## Fleet, base scenario, 10 farms for each gateway, USD")
    print("Investment and recurring cost are separate. Recurring cash holds the nodes, the cloud lines that grow with the farms, the gateways and the fixed cloud lines of the cost document, which are assigned in full to the farms. The reserve is not in the cash column.")
    print("")
    print("| Farms | LoRa share | Gateways | Investment, nodes | Investment, installation | Investment, gateways | Investment total, known | Monthly cash | Monthly reserve | Cash and reserve for each farm |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for n in FARMS:
        for mx in MIX:
            f = fleet(n, mx, 10, "base")
            ct = f["rec_cash_own"] + f["fixed"]
            print(f"| {n} | {mx:.0%} | {f['g']} | {usd(f['inv_nodes'])} | {usd(f['inv_install'])} | {usd(f['inv_gw'])} | {usd(f['inv'])} | {usd(ct)} | {usd(f['reserve'])} | {usd((ct + f['reserve']) / n)} |")
    print("")
    print("Every total is a known subtotal. The pending items of the nodes and gateways and the shipping, duties and IVA add to it.")

    print("\n## Gateways for each assumption of farms in range, base scenario")
    print("| Farms | LoRa share | Farms for each gateway | Gateways, rounded up | Investment known | Monthly cash | Monthly reserve | Cash and reserve for each farm |")
    print("|---|---|---|---|---|---|---|---|")
    for n in (200, 1000):
        for mx in (0.25, 0.50):
            for dens in DENSITY:
                f = fleet(n, mx, dens, "base")
                c = f["rec_cash_own"] + f["fixed"]
                print(f"| {n} | {mx:.0%} | {dens} | {f['g']} | {usd(f['inv'])} | {usd(c)} | {usd(f['reserve'])} | {usd((c + f['reserve']) / n)} |")

    print("\n## Scenarios low, base and high at 200 and 1,000 farms, 25 percent LoRa, 10 farms for each gateway")
    print("| Farms | Scenario | Investment known | Recurring cash a month | Reserve a month | Recurring cash and reserve for each farm |")
    print("|---|---|---|---|---|---|")
    for n in (200, 1000):
        for s in SC:
            f = fleet(n, 0.25, 10, s)
            c = f["rec_cash_own"] + f["fixed"]
            print(f"| {n} | {s} | {usd(f['inv'])} | {usd(c)} | {usd(f['reserve'])} | {usd((c + f['reserve']) / n)} |")
    print("")
    print("The low case also lowers the hardware, travel and labor, uses the prepaid plan and lengthens the lives of the parts, and the high case does the opposite. A scenario does not move the pending items, whose cost is unknown in all three.")

    print("\n## Cost for each farm by number of farms, base scenario, 25 percent LoRa, 10 farms for each gateway")
    print("| Farms | Marginal cash cost | Fixed cloud lines | Gateway cash | Reserve | Cash and reserve for each farm |")
    print("|---|---|---|---|---|---|")
    for n in FARMS:
        f = fleet(n, 0.25, 10, "base")
        gc = f["rec_gw"]
        print(f"| {n} | {usd(f['rec_nodes'] / n)} | {usd(f['fixed'] / n)} | {usd(gc / n)} | {usd(f['reserve'] / n)} | {usd((f['rec_cash_own'] + f['fixed'] + f['reserve']) / n)} |")

    print("\n## Options for a charge, for the Federation to approve")
    print("A fee is a policy decision, so these are ways to build one from the figures above, and none is proposed here. Values are base scenario, 25 percent LoRa, 10 farms for each gateway, in USD for each farm a month, before the pending items, tax and duties.")
    print("")
    print("| Option | How it is built | At 200 farms | At 1,000 farms |")
    print("|---|---|---|---|")
    vals = {}
    for n in (200, 1000):
        f = fleet(n, 0.25, 10, "base")
        a = f["rec_nodes"] / n
        b = (f["rec_cash_own"] + f["reserve"]) / n
        c = (f["rec_cash_own"] + f["fixed"] + f["reserve"]) / n
        dd = c + f["inv"] / n / FINANCE_MONTHS
        vals[n] = (a, b, c, dd)
    print(f"| A. Recover only the marginal cash cost | Data, SIM, cloud lines that grow, maintenance, with no reserve and no shared cost | {usd(vals[200][0])} | {usd(vals[1000][0])} |")
    print(f"| B. Recover the cash cost, the gateways and the reserve, and the Federation bears the fixed cloud lines | Option A plus the gateway cash cost and the reserve | {usd(vals[200][1])} | {usd(vals[1000][1])} |")
    print(f"| C. Recover everything recurring, with the fixed cloud lines divided by the farms | Option B plus the fixed cloud lines of the cost document | {usd(vals[200][2])} | {usd(vals[1000][2])} |")
    print(f"| D. Option C and the investment financed over {FINANCE_MONTHS} months at no interest | Option C plus the known investment divided by {FINANCE_MONTHS} | {usd(vals[200][3])} | {usd(vals[1000][3])} |")
    print("")
    print("Each option leaves out the pending items. A subsidy, an interest rate, a margin or a different share of the fixed cloud lines are decisions that no document of the project makes, and whether the farmer is charged any of this is also open.")

    vi = {v: hardware(v, "base") + one_time_connectivity(v, "base") + sum(install("base")) for v in ("cell", "lora")}
    print("\n## Context, not a judgment")
    print("The known investment of a farm, base scenario, in kilograms of dry parchment coffee at the reference price of the Federation of 10 November 2026, COP 2,000,000 for a load of 125 kg, so COP 16,000 a kilogram.")
    print("")
    print("| Case | Known investment, USD | COP at the central TRM | Kilograms of dry parchment coffee | Same at the low and high TRM |")
    print("|---|---|---|---|---|")
    per = COFFEE_COP_PER_LOAD / KG_PER_LOAD
    for label, v in [("Cellular farm", vi["cell"]), ("LoRa farm without the gateway share", vi["lora"])]:
        cop = v * TRM["central"]
        print(f"| {label} | {usd(v)} | {cop:,.0f} | {cop / per:,.1f} | {v * TRM['low'] / per:,.1f} to {v * TRM['high'] / per:,.1f} |")
    print("")
    print("The comparison shows no profitability and no capacity to pay. The pending items would raise both figures.")

    print("\n## IVA scenario")
    print(f"If IVA of {IVA:.0%} applies in full to the known investment, a cellular farm goes from {usd(vi['cell'])} to {usd(vi['cell'] * (1 + IVA))}. Import duties are unknown and are in neither figure.")

    print("\n## Cost document, two values for one total")
    print(f"The cost document of this repository gives {cost_total[0]} for a normal month and {cost_total[1]} for a harvest month. The project status of the handbook gives 177.23 and 201.11. The script reads the first.")
    print("OK")


main()
