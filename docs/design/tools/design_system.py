"""Checks the design system applied to the three views and prints the tables of its document.

It reads the tokens of the visual identity document, computes the WCAG 2.2 contrast of every combination the
components use, derives accessible variants for the combinations that fall below AA, checks the icons, the
spacing scale and the buyer view fields against the schema, and can write the HTML of the sheet.
It does not change the tokens or the design file, and it proves nothing about a built application.

    python -I docs/design/tools/design_system.py            prints the tables, ends with OK
    python -I docs/design/tools/design_system.py --sheet out.html [--fonts DIR]
"""
import json
import re
import sys
from pathlib import Path

DESIGN = Path(__file__).resolve().parent.parent
DOCS = DESIGN.parent
errors = []


def check(cond, msg):
    if not cond:
        errors.append(msg)


# ---------------------------------------------------------------- tokens
def load_tokens():
    text = (DESIGN / "visual-identity.md").read_text(encoding="utf-8")
    m = re.search(r"```json\n(\{.*?\})\n```", text, re.S)
    check(m is not None, "the tokens block of the visual identity was not found")
    return json.loads(m.group(1)) if m else {}


TOKENS = load_tokens()


def tok(path):
    node = TOKENS.get("color", {})
    for part in path.split("/"):
        node = node.get(part) if isinstance(node, dict) else None
        if node is None:
            check(False, f"token {path} does not exist")
            return "#000000"
    while isinstance(node, dict) and "value" in node:
        v = node["value"]
        if isinstance(v, str) and v.startswith("{"):
            return tok(v.strip("{}").replace("color.", "", 1).replace(".", "/"))
        return v
    check(False, f"token {path} has no value")
    return "#000000"


def lum(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def ratio(a, b):
    x, y = sorted((lum(a), lum(b)), reverse=True)
    return (x + 0.05) / (y + 0.05)


def level(r, text=True):
    if text:
        return "AAA" if r >= 7 else "AA" if r >= 4.5 else "fail"
    return "pass" if r >= 3 else "fail"


def darken(fg, bgs, target):
    base = [int(fg.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    for step in range(0, 101):
        t = step / 100
        c = "#%02X%02X%02X" % tuple(round(v * (1 - t)) for v in base)
        if all(ratio(c, b) >= target for b in bgs):
            return c
    return "#000000"


# ---------------------------------------------------------------- combinations that the components use
# name, foreground, background, where it is used, text or non-text
SURF = {"canvas": "surface/canvas", "card": "surface/card", "muted": "surface/muted"}
USES = [
    ("Body and titles", "text/primary", "surface/canvas", "Every screen", True),
    ("Body and titles on a card", "text/primary", "surface/card", "Cards, fields", True),
    ("Labels and metadata", "text/secondary", "surface/canvas", "Labels, offline bar text", True),
    ("Labels on a card", "text/secondary", "surface/card", "Card labels", True),
    ("Labels on a muted surface", "text/secondary", "surface/muted", "Offline bar, secondary sections", True),
    ("Microcopy on the canvas", "text/muted", "surface/canvas", "Relative times", True),
    ("Microcopy on a card", "text/muted", "surface/card", "Hints under a field", True),
    ("Microcopy on a muted surface", "text/muted", "surface/muted", "Offline bar, status bars", True),
    ("Link and primary text button", "action/primary", "surface/canvas", "Links, secondary button", True),
    ("Link on a card", "action/primary", "surface/card", "Links inside a card", True),
    ("Label of the primary button", "text/inverse", "action/primary", "Primary button", True),
    ("Brand red on white", "brand/red", "surface/card", "Logotype only", True),
    ("Brand sun on white", "brand/sun", "surface/card", "Graphic accent, never text", True),
    ("Badge preparing", "status/in-preparation/text", "status/in-preparation/bg", "Status badge", True),
    ("Badge in transit", "status/in-transit/text", "status/in-transit/bg", "Status badge", True),
    ("Badge accepted", "status/accepted/text", "status/accepted/bg", "Status badge", True),
    ("Badge rejected", "status/rejected/text", "status/rejected/bg", "Status badge", True),
    ("Alert normal", "alert/normal/text", "alert/normal/bg", "Alert", True),
    ("Alert preventive", "alert/warning/text", "alert/warning/bg", "Alert", True),
    ("Alert urgent", "alert/urgent/text", "alert/urgent/bg", "Alert", True),
]
# non-text boundaries that a user needs to find a control
NONTEXT = [
    ("Border of a card", "surface/border", "surface/canvas", "Decorative, the card is also found by its content"),
    ("Border of a field", "surface/border", "surface/card", "Fails as the only boundary of a field"),
    ("Field border with the muted text color", "text/muted", "surface/card", "Proposed boundary of a field"),
    ("Focus ring and active control", "action/primary", "surface/canvas", "Focus, selected tab, toggle on"),
    ("Urgent alert border", "alert/urgent/border", "surface/canvas", "Alert border, 2 px"),
]
NOT_TEXT = {"Brand sun on white"}  # graphic only, listed to show why it is never text


def build_matrix():
    rows = []
    for name, fg, bg, where, is_text in USES:
        r = ratio(tok(fg), tok(bg))
        rows.append((name, fg, bg, where, r, level(r)))
    return rows


MATRIX = build_matrix()
FAILING = [m for m in MATRIX if m[0] not in NOT_TEXT and m[5] == "fail"]

# every text combination reaches AA except the ones that carry a documented variant
VARIANT_FOR = {"Microcopy on a muted surface"}
for name, fg, bg, where, r, lv in MATRIX:
    if name not in NOT_TEXT and name not in VARIANT_FOR:
        check(r >= 4.5, f"{name} is {r:.2f}, below AA, and has no documented variant")
check({m[0] for m in FAILING} <= VARIANT_FOR, "a combination below AA has no variant")
# the contrast table of the document matches the computed ratios
DOC = (DESIGN / "design-system.md").read_text(encoding="utf-8")
for name, fg, bg, where, r, lv in MATRIX:
    if name in NOT_TEXT:
        continue
    shown = "Below AA" if lv == "fail" else lv
    check(any(f"| {r:.2f} | {shown} |" in line for line in DOC.splitlines()), f"the document does not show {name} as {r:.2f} {shown}")

# accessible variants proposed for the combinations below AA, never applied to the tokens
VARIANTS = []
for name, fg, bg, where, r, lv in FAILING:
    VARIANTS.append((fg + "-on-muted" if "muted" in bg else fg + "-strong", fg, [tok(bg)], 4.5, where))
VARIANTS = [(n.replace("text/muted-on-muted", "text/muted-strong"), fg, bgs, tgt, where) for n, fg, bgs, tgt, where in VARIANTS]


def variant_rows():
    out = []
    for name, fg, bgs, tgt, where in VARIANTS:
        # the variant must also pass on the other surfaces where its parent is used
        others = [tok(s) for s in SURF.values()]
        v = darken(tok(fg), bgs + others, tgt)
        out.append((name, fg, tok(fg), v, [round(ratio(v, b), 2) for b in others], where))
    return out


VARIANT_ROWS = variant_rows()
# text/muted-strong would be bounded by the three surfaces, so the proposal is checked on all of them
for name, fg, old, new, rs, where in VARIANT_ROWS:
    check(all(r >= 4.5 for r in rs), f"variant {name} does not reach AA on every surface")

# ---------------------------------------------------------------- spacing, grid and sizes
SPACING = {k: int(v["value"]) for k, v in TOKENS.get("space", {}).items()}
RADIUS = {k: int(v["value"]) for k, v in TOKENS.get("radius", {}).items()}
check(SPACING and all(v % 4 == 0 for v in SPACING.values()), "a spacing token is not a multiple of 4")
check(sorted(SPACING.values()) == list(SPACING.values()), "spacing tokens are not in ascending order")
GRID = [
    ("Phone", "390 and 360 wide", "4 columns", 16, 16, "Farmer, carrier and the buyer on a phone"),
    ("Desktop", "1440 wide", "12 columns", 24, 120, "Buyer on a desktop, content at most 960 wide"),
]
for g in GRID:
    check(g[3] in SPACING.values() or g[3] == 24, f"the gutter of {g[0]} is not a spacing token")
TOUCH = 48
check(TOUCH >= 44, "touch area below 44 px")

# ---------------------------------------------------------------- components
COMPONENTS = [
    ("Button", "Primary, secondary and destructive. Height 48, horizontal padding space/md, radius radius/lg, label text/body-bold. Primary uses action/primary with text/inverse. Secondary has a 1.5 px action/primary border on surface/card. Destructive has a 1.5 px alert/urgent/text border on surface/card and always asks for confirmation", "Default, pressed, disabled, focus", "Icon optional, left of the label"),
    ("Field", "Label above in text/secondary, input height 48, radius radius/md, fill surface/card, 1.5 px border text/muted, hint below in text/muted. Code fields use text/data-mono", "Empty, filled, focus (2 px action/primary), error (2 px alert/urgent/border with the message in alert/urgent/text), disabled", "Error always has an icon and words"),
    ("Alert", "Fill, border and text from the alert tokens, radius radius/lg, padding space/md, title text/body-bold. Urgent has a 2 px border and an icon", "Normal, preventive, urgent", "The action is a sentence in plain words"),
    ("Sack card", "Card with the sack code in text/data-mono, the status badge on the right, one line of detail in text/secondary and an optional action. Radius radius/lg, 1 px surface/border, padding space/md. Called a row when it sits in a list", "Default, selected, rejected (alert/urgent/bg fill)", "Whole card is one touch target of at least 48"),
    ("Status badge", "Pill with radius/full, fill, 1 px border and text from the status tokens, text/caption, always with its word. Four groups cover the seven states of a sack", "In preparation, in transit, accepted, rejected", "Color never carries the state alone"),
]
COMPONENT_NAMES = [c[0] for c in COMPONENTS]
ICONS = {
    "house": "Farm", "sun": "Drying", "bell": "Alerts", "package": "Sacks", "map-pin": "Location active",
    "scan-line": "Scan a sack", "qr-code": "Label of the sack", "wifi-off": "No connection", "pause": "Pause",
    "play": "Resume", "triangle-alert": "Urgent or preventive alert", "circle-check": "Accepted", "check": "Confirm",
    "x": "Rejected or close", "chevron-right": "Opens", "truck": "Trip to the center", "ship": "Delivery at the port",
    "info": "Explanation", "thermometer": "Grain temperature", "droplets": "Humidity",
    "languages": "Language switch", "arrow-left": "Back",
}
for name in ICONS:
    check((DESIGN / "icons" / f"{name}.svg").exists(), f"icon {name} is missing")
check((DESIGN / "icons" / "LICENSE.txt").exists(), "the license of the icon set is missing")

# ---------------------------------------------------------------- screens: view, id, name, components, icons
SCREENS = [
    ("Farmer", "C1", "Farm", ["Alert", "Button"], ["house", "sun", "bell", "package", "chevron-right"]),
    ("Farmer", "C2", "Farm with a variable out of range", ["Alert", "Button"], ["triangle-alert", "wifi-off"]),
    ("Farmer", "C3", "The numbers", ["Alert"], ["thermometer", "droplets", "arrow-left"]),
    ("Farmer", "C4", "Drying with no lot", ["Button"], ["sun"]),
    ("Farmer", "C5", "Drying with an urgent alert", ["Alert", "Button"], ["triangle-alert", "thermometer", "droplets"]),
    ("Farmer", "C6", "Confirm end of drying", ["Button"], ["x"]),
    ("Farmer", "C7", "Alerts", ["Alert", "Status badge"], ["bell", "triangle-alert"]),
    ("Farmer", "C8", "Register a sack", ["Field", "Sack card", "Button"], ["package", "scan-line"]),
    ("Carrier", "T1", "Open trip", ["Sack card", "Status badge", "Button"], ["truck", "map-pin", "pause", "scan-line"]),
    ("Carrier", "T2", "Scanner", ["Field", "Button"], ["scan-line", "qr-code", "check"]),
    ("Carrier", "T3", "Arrival at the center", ["Button", "Alert"], ["truck", "check", "circle-check"]),
    ("Carrier", "T4", "Delivery at the port, three steps", ["Sack card", "Field", "Button", "Status badge"], ["ship", "x", "check", "arrow-left"]),
    ("Carrier", "T5", "Reminder after 10 hours", ["Alert", "Button"], ["pause", "map-pin"]),
    ("Carrier", "T6", "No data and tasks", ["Alert", "Sack card"], ["wifi-off", "triangle-alert"]),
    ("Carrier", "T7", "Paused trip", ["Alert", "Button"], ["pause", "play"]),
    ("Buyer", "B1", "Result on a phone", ["Sack card", "Status badge", "Alert"], ["languages", "info"]),
    ("Buyer", "B2", "Result on a desktop", ["Sack card", "Status badge"], ["languages", "info"]),
    ("Buyer", "B3", "Rejected", ["Sack card", "Status badge"], ["x", "info"]),
    ("Buyer", "B4", "Code not registered", ["Alert", "Button"], ["info"]),
    ("Buyer", "B5", "Write the code", ["Field", "Button"], ["qr-code"]),
]
for v, i, n, comps, icons in SCREENS:
    check(all(c in COMPONENT_NAMES for c in comps), f"screen {i} uses an unknown component")
    check(all(ic in ICONS for ic in icons), f"screen {i} uses an icon outside the list")
check(len(SCREENS) == 20, "the identity has 20 screens")
check({c for _, _, _, comps, _ in SCREENS for c in comps} == set(COMPONENT_NAMES), "a component is used by no screen")
check({ic for _, _, _, _, icons in SCREENS for ic in icons} <= set(ICONS), "an icon is used outside the list")
check(set(ICONS) <= {ic for _, _, _, _, icons in SCREENS for ic in icons}, "an icon of the list is used by no screen")

# ---------------------------------------------------------------- buyer view: only the fields of the schema reach a screen
SCHEMA = json.loads((DOCS / "traceability" / "schemas" / "buyer-view.schema.json").read_text(encoding="utf-8"))
ALLOWED = set(SCHEMA["properties"]) | {f"drying.{k}" for k in SCHEMA["properties"]["drying"]["properties"]} | {f"process_dates.{k}" for k in SCHEMA["properties"]["process_dates"]["properties"]} | {f"origin.{k}" for k in SCHEMA["properties"].get("origin", {}).get("properties", {})}
BUYER_SHOWN = [
    ("Code of the sack", "sack_code"), ("Status badge and sentence", "state"), ("Reason of a rejection", "state_reason"),
    ("Origin", "origin.department"), ("Origin", "origin.country"),
    ("Drying dates", "process_dates.drying_started_on"), ("Drying dates", "process_dates.drying_ended_on"),
    ("Registered", "process_dates.registered_on"), ("Received at the center", "process_dates.received_at_center_on"),
    ("Dispatched to the port", "process_dates.dispatched_to_port_on"), ("Delivered at the port", "process_dates.delivered_on"),
    ("Hours monitored", "drying.hours_monitored"), ("Readings received", "drying.readings_completeness_pct"),
    ("Highest grain temperature", "drying.grain_temp_max_c"), ("Hours above 40", "drying.hours_above_40c"),
    ("Humidity at the start", "drying.grain_humidity_first_pct"), ("Humidity at the end", "drying.grain_humidity_last_pct"),
    ("Drying summary line", "drying.status"),
]
BUYER_LEFT_OUT = ["Weight", "Names of centers", "Hours and minutes of each step", "Free text of a rejection", "Who handled the sack", "The trip and every location", "Farm and lot identifiers"]
for label, field in BUYER_SHOWN:
    check(field in ALLOWED, f"the buyer screen shows {field}, which the schema of the view does not allow")
FORBIDDEN_WORDS = ["farm_id", "lot_id", "drying_lot_id", "trip_id", "center_id", "weight", "captured_by", "recorded_by", "location"]
for label, field in BUYER_SHOWN:
    check(not any(w in field for w in FORBIDDEN_WORDS), f"the buyer screen shows {field}, which is excluded")

# ---------------------------------------------------------------- output
def md(text):
    print(text)


def tables():
    md("## Contrast of the combinations that the components use")
    md("| Use | Foreground | Background | Ratio | Level | Where |")
    md("|---|---|---|---|---|---|")
    for name, fg, bg, where, r, lv in MATRIX:
        md(f"| {name} | `{fg}` {tok(fg)} | `{bg}` {tok(bg)} | {r:.2f} | {lv} | {where} |")
    n = {k: sum(1 for m in MATRIX if m[5] == k and m[0] not in NOT_TEXT) for k in ("AAA", "AA", "fail")}
    md(f"\nCombinations that reach AAA {n['AAA']}, that stop at AA {n['AA']}, and that fail AA {n['fail']}. Brand sun is graphic only.")
    md("\n## Non-text contrast")
    md("| Element | Color | Against | Ratio | Level | Note |")
    md("|---|---|---|---|---|---|")
    for name, a, b, note in NONTEXT:
        r = ratio(tok(a), tok(b))
        md(f"| {name} | `{a}` {tok(a)} | `{b}` | {r:.2f} | {level(r, False)} | {note} |")
    md("\n## Proposed accessible variants")
    md("| Variant | Replaces | Old | Proposed | Ratio on canvas, card, muted | Reason |")
    md("|---|---|---|---|---|---|")
    for name, fg, old, new, rs, where in VARIANT_ROWS:
        md(f"| `{name}` | `{fg}` | {old} | {new} | {rs[0]}, {rs[1]}, {rs[2]} | {where} |")
    md("\n## Spacing, grid and radius")
    md("| Token | Value |\n|---|---|")
    for k, v in SPACING.items():
        md(f"| `space/{k}` | {v} |")
    for k, v in RADIUS.items():
        md(f"| `radius/{k}` | {v} |")
    md("\n| View | Width | Columns | Gutter | Margin | Use |\n|---|---|---|---|---|---|")
    for g in GRID:
        md(f"| {g[0]} | {g[1]} | {g[2]} | {g[3]} | {g[4]} | {g[5]} |")
    md("\n## Screens")
    md("| View | Screen | Name | Components | Icons |\n|---|---|---|---|---|")
    for v, i, n_, comps, icons in SCREENS:
        md(f"| {v} | {i} | {n_} | {', '.join(comps)} | {', '.join(icons)} |")
    md("\n## Icons")
    md("| Icon | Meaning |\n|---|---|")
    for k, v in ICONS.items():
        md(f"| `{k}` | {v} |")
    md("\n## Buyer view fields")
    md("| Shown | Field of the view |\n|---|---|")
    for a, b in BUYER_SHOWN:
        md(f"| {a} | `{b}` |")


def main():
    if "--sheet" in sys.argv:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import design_sheet
        i = sys.argv.index("--sheet")
        fonts = sys.argv[sys.argv.index("--fonts") + 1] if "--fonts" in sys.argv else None
        design_sheet.write(Path(sys.argv[i + 1]), sys.modules[__name__], fonts)
        return
    tables()
    for e in errors:
        print("FAIL", e)
    print("OK" if not errors else f"{len(errors)} problems")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
