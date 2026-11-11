"""Checks the state machine of the fumigation order.

Usage: python3 check_order_states.py [transitions] [schema]
With no arguments it reads schemas/fumigation-order-transitions.json and schemas/fumigation-order.schema.json.

1. The states of the transitions match the state enum of the order schema.
2. Every state is reachable from the initial state, and every state can reach a terminal state.
3. Terminal states have no exit, and every other state has at least one.
4. Once an application starts, the order cannot reach the states in after_application except through the listed moves.
5. Only the people listed in human_only move an order into AUTHORIZED, CLOSED or REJECTED.
6. Every transition names a known actor, a trigger and a guard, and the file names its audit event.
Exits 1 on the first failed check.
"""
import json
import pathlib
import re
import sys

ACTORS = {"supervisor", "farmer", "applicator", "platform_function", "scheduler"}


def fail(message):
    print(f"FAIL {message}")
    sys.exit(1)


def reach(start, edges):
    seen, todo = {start}, [start]
    while todo:
        for nxt in edges.get(todo.pop(), ()):
            if nxt not in seen:
                seen.add(nxt)
                todo.append(nxt)
    return seen


def main():
    here = pathlib.Path(__file__).resolve().parent.parent / "schemas"
    machine_path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else here / "fumigation-order-transitions.json"
    schema_path = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else here / "fumigation-order.schema.json"
    machine = json.loads(machine_path.read_text())
    states = set(json.loads(schema_path.read_text())["properties"]["state"]["enum"])

    if not re.fullmatch(r"[a-z_]+\.[a-z_]+", machine.get("audit_event", "")):
        fail("the file names no audit event")
    for state, actors in machine["human_only"].items():
        if not set(actors) <= set(machine["people"]):
            fail(f"human_only lets an automated actor reach {state}")
    terminal = set(machine["terminal"])
    forward, backward = {}, {}
    for t in machine["transitions"]:
        move = f"{t['from']} -> {t['to']} by {t['actor']}"
        for state in (t["from"], t["to"]):
            if state not in states:
                fail(f"{move} uses {state}, which the schema does not declare")
        if t["actor"] not in ACTORS:
            fail(f"{move} has an unknown actor")
        if not t.get("trigger") or not t.get("guard"):
            fail(f"{move} has no trigger or no guard")
        allowed = machine["human_only"].get(t["to"])
        if allowed is not None and t["actor"] not in allowed:
            fail(f"{move} lets {t['actor']} reach {t['to']}")
        forward.setdefault(t["from"], set()).add(t["to"])
        backward.setdefault(t["to"], set()).add(t["from"])

    for state in sorted(states - reach(machine["initial"], forward)):
        fail(f"{state} is not reachable from {machine['initial']}")
    ends = set().union(*(reach(s, backward) for s in terminal))
    for state in sorted(states - ends):
        fail(f"{state} cannot reach a terminal state")
    for state in sorted(states):
        if state in terminal and state in forward:
            fail(f"terminal state {state} has an exit")
        if state not in terminal and state not in forward:
            fail(f"{state} has no exit and is not terminal")
    rule = machine["after_application"]
    skip = {tuple(move) for move in rule["except"]}
    after = {}
    for t in machine["transitions"]:
        if (t["from"], t["to"]) not in skip:
            after.setdefault(t["from"], set()).add(t["to"])
    for state in sorted(set(rule["unreachable"]) & reach(rule["from"], after)):
        fail(f"{state} is reachable after {rule['from']}, so applied product could skip the verification")
    print(f"OK {len(states)} states, {len(machine['transitions'])} transitions, "
          f"only people reach {', '.join(sorted(machine['human_only']))}")


if __name__ == "__main__":
    main()
