"""Routes of the site-to-site VPN between the collection centers and the cloud, and the checks that bound them.

Run with no arguments. It prints the tables of docs/network/center-cloud-link.md and ends with OK or exits with 1.
Inputs come from the documented address plan, not from measurements.
  Centers          10.41.0.0/16 Cauca, 10.42.0.0/16 Huila, 10.43.0.0/16 Tolima (collection center LAN)
  Center zones     1 Management, 2 Support, 3 Logistics, 4 Transport, 5 Visitors, 10 Local servers, 20 Firewall
  Environments     10.50.0.0/16 dev, 10.60.0.0/16 test, 10.70.0.0/16 prod (cloud addressing)
  Subnets          one /20 block per purpose in a fixed order and one /24 per zone, as the environment roots build them
Routing is not authorization. A route only lets a packet find a path. The security groups of the endpoints, the network
ACLs and the firewall of the center decide whether it is allowed.
"""
import ipaddress
import re
import sys
from pathlib import Path

net = ipaddress.ip_network

CENTERS = {41: "Cauca", 42: "Huila", 43: "Tolima"}
CENTER_ZONES = {1: "Management", 2: "Support", 3: "Logistics", 4: "Transport", 5: "Visitors", 10: "Local servers", 20: "Firewall"}
AUTHORIZED = (3, 10)
NOT_AUTHORIZED = (1, 2, 4, 5, 20)
ENVIRONMENTS = {"dev": ("10.50.0.0/16", 1), "test": ("10.60.0.0/16", 1), "prod": ("10.70.0.0/16", 2)}
LINKED = {"test": [41], "prod": [41, 42, 43]}
PURPOSES = ["telemetry-ingress", "drone-ingress", "application", "data", "object-storage", "administration", "public-query"]
ENDPOINT_OF = {"telemetry-ingress": "IoT Core data", "drone-ingress": "S3", "application": "private REST API"}
ZONE_LETTERS = "ab"

errors = []


def check(condition, message):
    if not condition:
        errors.append(message)


def center_range(center, zone):
    return net(f"10.{center}.{zone}.0/24")


def subnets(env):
    cidr, zones = ENVIRONMENTS[env]
    vpc = net(cidr)
    out = {}
    for purpose_index, purpose in enumerate(PURPOSES):
        for zone_index in range(zones):
            sub = list(vpc.subnets(new_prefix=24))[purpose_index * 16 + zone_index]
            out[(purpose, ZONE_LETTERS[zone_index])] = sub
    return out


def endpoint_subnets(env):
    return {key: sub for key, sub in subnets(env).items() if key[0] in ENDPOINT_OF}


def main():
    print("## Subnets that hold endpoints and the route table of each purpose")
    print("The module places the routes to the centers only in the table `rt-private-center`, which serves the subnets of three purposes. The table `rt-private` serves the other four and holds no route to a center.")
    print("| Environment | Purpose | Zone | Subnet | Holds | Route table |")
    print("|---|---|---|---|---|---|")
    for env in LINKED:
        for (purpose, zone), sub in subnets(env).items():
            holds = ENDPOINT_OF.get(purpose, "no endpoint")
            table = "rt-private-center" if purpose in ENDPOINT_OF else "rt-private"
            print(f"| {env} | {purpose} | {zone} | {sub} | {holds} | {table} |")

    print("\n## Routes in the cloud, table `rt-private-center` of each environment")
    print("One route for each range of logistics and local servers of each linked center, with the virtual private gateway of that environment as target. These are also the return routes of the answers of the endpoints.")
    print("| Environment | Destination | Center zone | Center | Target |")
    print("|---|---|---|---|---|")
    cloud_routes = {}
    for env, centers in LINKED.items():
        routes = []
        for center in centers:
            for zone in AUTHORIZED:
                rng = center_range(center, zone)
                routes.append((rng, CENTER_ZONES[zone], CENTERS[center]))
                print(f"| {env} | {rng} | {CENTER_ZONES[zone]} | {CENTERS[center]} | Virtual private gateway of {env} |")
        cloud_routes[env] = routes
    print("\nNo route to a center exists in `rt-private` of any environment, in any table of the environments with no link, or for the ranges of Management, Support, Transport, Visitors and the firewall.")

    print("\n## Static routes of each VPN connection, the ranges that the center announces")
    print("| Environment | Connection | Static routes |")
    print("|---|---|---|")
    for env, centers in LINKED.items():
        for center in centers:
            rs = ", ".join(str(center_range(center, z)) for z in AUTHORIZED)
            print(f"| {env} | {CENTERS[center]} | {rs} |")

    print("\n## Routes on the firewall of a center, one set for each environment tunnel pair")
    print("Only the subnets that hold the three endpoints. The other four purposes and the rest of the range of the environment have no route.")
    print("| Environment | Routes through the tunnels of that environment | Count |")
    print("|---|---|---|")
    center_side = {}
    for env in LINKED:
        subs = sorted(endpoint_subnets(env).values())
        center_side[env] = subs
        print(f"| {env} | {', '.join(str(s) for s in subs)} | {len(subs)} |")

    # Checks
    all_center_ranges = [net(f"10.{c}.0.0/16") for c in CENTERS]
    env_nets = {env: net(cidr) for env, (cidr, _) in ENVIRONMENTS.items()}
    for env, vpc in env_nets.items():
        check(not any(vpc.overlaps(c) for c in all_center_ranges), f"{env} overlaps a center")
    for a in env_nets:
        for b in env_nets:
            if a < b:
                check(not env_nets[a].overlaps(env_nets[b]), f"{a} overlaps {b}")

    forbidden_zone_ranges = [center_range(c, z) for c in CENTERS for z in NOT_AUTHORIZED]
    check(not set(AUTHORIZED) & set(NOT_AUTHORIZED), "a zone is both authorized and not authorized")
    for env, routes in cloud_routes.items():
        dests = [r[0] for r in routes]
        check(len(dests) == len(set(dests)), f"{env} has a duplicate destination")
        for dest in dests:
            check(dest.prefixlen == 24, f"{env} route {dest} is not a /24")
            check(not dest.overlaps(env_nets[env]), f"{env} route {dest} falls inside its own VPC")
            check(any(dest == center_range(c, z) for c in LINKED[env] for z in AUTHORIZED), f"{env} route {dest} is not an authorized range of a linked center")
        for forbidden in forbidden_zone_ranges:
            check(not any(forbidden.overlaps(d) for d in dests), f"{env} covers the range {forbidden} of an unauthorized zone")
        for c in CENTERS:
            if c not in LINKED[env]:
                check(not any(net(f"10.{c}.0.0/16").overlaps(d) for d in dests), f"{env} routes to center {c}, which is not linked")
        for d in dests:
            owners = [c for c in CENTERS if net(f"10.{c}.0.0/16").overlaps(d)]
            check(len(owners) == 1, f"{env} route {d} matches {len(owners)} centers")

    seen = {}
    for env, subs in center_side.items():
        for sub in subs:
            check(sub.subnet_of(env_nets[env]), f"{env} center route {sub} outside its environment")
            check(sub.prefixlen == 24, f"{env} center route {sub} is not a /24")
            for other, other_subs in center_side.items():
                if other != env:
                    check(not any(sub.overlaps(o) for o in other_subs), f"center route {sub} of {env} overlaps a route of {other}")
            seen[sub] = env
        purposes = {key[0] for key, sub in endpoint_subnets(env).items() if sub in subs}
        check(purposes == set(ENDPOINT_OF), f"{env} center routes miss an endpoint purpose")
        for key, sub in subnets(env).items():
            if key[0] not in ENDPOINT_OF:
                check(sub not in subs, f"{env} center routes include the subnet {key}, which holds no endpoint")
    check(all(not any(s.overlaps(c) for c in all_center_ranges) for s in seen), "a center route overlaps a center")

    text = Path(__file__).resolve().parent.parent.parent.joinpath("network", "cloud-addressing.md").read_text(encoding="utf-8")
    prod = subnets("prod")
    names = {"telemetry-ingress": "Telemetry ingress", "drone-ingress": "Drone object ingress", "application": "Application"}
    for purpose, label in names.items():
        m = re.search(r"\| " + re.escape(label) + r" \| (10\.70\.\d+\.0/20) \| (10\.70\.\d+\.0/24) \| (10\.70\.\d+\.0/24) \|", text)
        check(m is not None, f"cloud-addressing has no row for {label}")
        if m:
            check(net(m.group(2)) == prod[(purpose, "a")] and net(m.group(3)) == prod[(purpose, "b")], f"{label} subnets differ from cloud-addressing")
            check(prod[(purpose, "a")].subnet_of(net(m.group(1))), f"{label} subnet is outside its block")

    print("\n## Checks")
    print("Each route is a /24 of an authorized zone of a linked center, no route covers Management, Support, Transport, Visitors or the firewall, no route points to a center that is not linked, each center range has one owner, the center routes of an environment sit inside that environment and overlap none of another environment, only the three endpoint purposes are reachable from a center, and the production subnets agree with the cloud addressing document.")
    for e in errors:
        print("FAIL", e)
    print("OK" if not errors else f"{len(errors)} problems")
    sys.exit(1 if errors else 0)


main()
