"""Checks the firewall policy matrix against the rules it must satisfy."""
import ipaddress
import re
import sys
from pathlib import Path

SOURCE = Path(__file__).resolve().parent.parent / "firewall-policy.md"
CENTERS = [ipaddress.ip_network(f"10.{octet}.0.0/16") for octet in (41, 42, 43)]
CLOUDS = [ipaddress.ip_network(f"10.{octet}.0.0/16") for octet in (50, 60, 70)]
CENTER_SOURCES = {ipaddress.ip_network(f"10.{octet}.{zone}.0/24") for octet in (41, 42, 43) for zone in (3, 10)}
PREFIXES = ("CTR", "TUN", "SG", "NACL", "WAF")


def tables(text):
    """Returns each rule table, one with an Action column whose rows start with a rule ID."""
    found, current = [], []
    for line in text.splitlines() + [""]:
        if line.startswith("|"):
            current.append([cell.strip() for cell in line.strip("|").split("|")])
        else:
            rows = [r for r in current[2:] if re.match(rf"({'|'.join(PREFIXES)})-\d+", r[0])]
            if rows and "Action" in current[0]:
                found.append((current[0], rows))
            current = []
    return found


def networks(cell):
    return [ipaddress.ip_network(m) for m in re.findall(r"\b10\.\d+\.\d+\.\d+/\d+\b", cell)]


def main():
    errors = []
    found = tables(SOURCE.read_text(encoding="utf-8"))
    ids = [row[0] for _, rows in found for row in rows]
    if len(ids) != len(set(ids)):
        errors.append("duplicate rule IDs")

    for cloud in CLOUDS:
        if any(cloud.overlaps(center) for center in CENTERS):
            errors.append(f"{cloud} overlaps a center")

    for header, rows in found:
        prefix = rows[0][0].split("-")[0]
        col = {name: i for i, name in enumerate(header)}
        if prefix != "WAF" and "Action" in col:
            last = rows[-1][col["Action"]].lower()
            if "deny" not in last and "no route" not in last:
                errors.append(f"{prefix} table does not end in a deny, it ends with {rows[-1][0]}")
        for row in rows:
            text = " ".join(row)
            if "Duration" in col and not re.search(r"Permanent|Temporary|Pending|temporary", row[col["Duration"]]):
                errors.append(f"{row[0]} has no duration")
            if prefix in ("SG", "NACL"):
                if "0.0.0.0/0" in text and "Allow" in row[col["Action"]]:
                    errors.append(f"{row[0]} allows the whole internet inside the VPC")
                if row[col["Action"]] == "Allow" and "Center source ranges" not in text and "center source ranges" not in text:
                    errors.append(f"{row[0]} allows a source other than the center source ranges")
            if prefix == "CTR" and row[col["Action"]] == "Allow":
                for net in networks(row[col["Destination"]]):
                    if any(net.overlaps(center) for center in CENTERS):
                        errors.append(f"{row[0]} allows a destination inside a center range")

    text = SOURCE.read_text(encoding="utf-8")
    for net in CENTER_SOURCES:
        x, zone = str(net).split(".")[1:3]
        if f"10.X.{zone}.0/24" not in text:
            errors.append(f"center source {net} is not named")

    temporary = re.findall(r"^\| (CTR-\d+|SG-\d+ to SG-\d+[^|]*) \| [^|]+ \| [^|]+ \| ([^|]+) \|$", text, re.M)
    if not temporary or any(not end.strip() for _, end in temporary):
        errors.append("a temporary rule has no end condition")

    for error in errors:
        print("FAIL", error)
    print("OK" if not errors else f"{len(errors)} problems")
    print(f"{len(ids)} rules in {len(found)} tables")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
