"""Checks the diagram source against the rules it must satisfy."""
import ipaddress
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

SOURCE = Path(__file__).resolve().parent.parent / "diagrams" / "platform-architecture.drawio"
CODES = [f"C{i:02d}" for i in range(1, 11)]
ELEMENTS = ["Farm with signal", "Farm out of coverage", "Drone brigade", "Carrier in transit", "Centers",
            "AWS us-east-1", "Buyer browser", "Port of Buenaventura"]
SUBNET_BLOCKS = 7


def main():
    root = ET.parse(SOURCE).getroot()
    pages = {d.get("name"): d for d in root.findall("diagram")}
    errors = []
    if len(pages) != 11:
        errors.append(f"expected 11 pages, found {len(pages)}")

    deployment = pages["02 Implementation scope"]
    codes = Counter(c.get("value") for c in deployment.iter("mxCell"))
    for code in CODES:
        if codes[code] != 1:
            errors.append(f"{code} appears {codes[code]} times on the deployment page")

    text = " ".join(c.get("value") or "" for c in pages["01 End to end"].iter("mxCell"))
    for element in ELEMENTS:
        if element not in text:
            errors.append(f"end to end page misses {element}")

    for name, page in pages.items():
        if not any((c.get("value") or "") == "Legend" for c in page.iter("mxCell")):
            errors.append(f"{name} has no legend")

    labelled = [c for c in pages["01 End to end"].iter("mxCell") if c.get("edge") and c.get("source")]
    unlabelled = [c.get("id") for c in labelled if not c.get("value") and "stations" not in (c.get("source"), c.get("target"))]
    if unlabelled:
        errors.append(f"unlabelled edges on the end to end page: {unlabelled}")

    all_text = " ".join(c.get("value") or "" for p in pages.values() for c in p.iter("mxCell"))
    centers = [ipaddress.ip_network(f"10.{o}.0.0/16") for o in (41, 42, 43)]
    clouds = {env: ipaddress.ip_network(f"10.{o}.0.0/16") for env, o in (("development", 50), ("test", 60), ("production", 70))}
    for net in clouds.values():
        if any(net.overlaps(c) for c in centers):
            errors.append(f"{net} overlaps a center")
    subnets = [ipaddress.ip_network(m) for m in re.findall(r"10\.70\.\d+\.\d+/\d+", all_text)]
    subnets = [n for n in subnets if n.prefixlen == 24]
    if len(subnets) != SUBNET_BLOCKS * 2 or len(set(subnets)) != len(subnets):
        errors.append(f"expected {SUBNET_BLOCKS * 2} unique production subnets, found {len(set(subnets))}")
    if any(not n.subnet_of(clouds["production"]) for n in subnets):
        errors.append("a subnet falls outside the production range")

    for error in errors:
        print("FAIL", error)
    print("OK" if not errors else f"{len(errors)} problems")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
