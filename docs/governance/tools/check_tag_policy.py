"""Checks the tag policy against the infrastructure code.

Usage: python3 check_tag_policy.py [code_dir ...]
With no arguments it reads the infrastructure and module repositories cloned next to this one.

1. The policy requires the six keys of the root validation, with the same capitalization.
2. CostCenter and ManagedBy allow the same values as the root validation.
3. Every resource type in the code is either required by the policy or listed as outside the
   provider cross reference.
4. Every required key covers every resource type of the cross reference map.
5. The policy fits the 10,000 characters of an Organizations tag policy.
Exits 1 on the first failed check.
"""
import json
import pathlib
import re
import sys

KEYS = ["Client", "Project", "Environment", "Owner", "CostCenter", "ManagedBy"]
LIMIT = 10000


def fail(message):
    print(f"FAIL {message}")
    sys.exit(1)


def main():
    here = pathlib.Path(__file__).resolve().parent.parent / "policies"
    policy = json.loads((here / "tag-policy.json").read_text())
    types = json.loads((here / "tag-resource-types.json").read_text())
    workspace = pathlib.Path(__file__).resolve().parents[4]
    dirs = [pathlib.Path(d) for d in sys.argv[1:]] or [workspace / "aromapacifico-devops-infra",
                                                      *sorted(workspace.glob("terraform-aws-*"))]

    tags = policy["tags"]
    if sorted(tags) != sorted(KEYS):
        fail(f"the policy keys are {sorted(tags)}, expected {sorted(KEYS)}")
    for key, rule in tags.items():
        if rule["tag_key"]["@@assign"] != key:
            fail(f"{key} assigns the capitalization {rule['tag_key']['@@assign']}")

    files = [f for d in dirs for f in d.rglob("*.tf") if ".terraform" not in f.parts]
    if not files:
        fail("no Terraform files found")
    text = "\n".join(f.read_text() for f in files)
    for key, pattern in (("CostCenter", r'contains\(\[([^\]]*)\], var\.common_tags\["CostCenter"\]\)'),
                         ("ManagedBy", r'var\.common_tags\["ManagedBy"\] == ("[^"]*")')):
        found = {tuple(sorted(re.findall(r'"([^"]+)"', m))) for m in re.findall(pattern, text)}
        if not found:
            fail(f"no root validation of {key} found")
        if found != {tuple(sorted(tags[key]["tag_value"]["@@assign"]))}:
            fail(f"{key} values differ between the policy and the root validation: {found}")

    used = set(re.findall(r'^resource "(aws_[a-z0-9_]+)"', text, re.M))
    known = set(types["required"]) | set(types["outside_cross_reference"])
    for name in sorted(used - known):
        fail(f"{name} is in the code but neither required nor listed outside the cross reference")

    wanted = set(types["required"].values())
    for key, rule in tags.items():
        listed = set(rule["report_required_tag_for"]["@@assign"])
        if listed != wanted:
            fail(f"{key} misses {sorted(wanted - listed)} or adds {sorted(listed - wanted)}")

    size = len(json.dumps(policy, separators=(",", ":")))
    if size > LIMIT:
        fail(f"the policy has {size} characters, above {LIMIT}")
    print(f"OK {len(KEYS)} keys, {len(wanted)} required resource types, "
          f"{len(used)} resource types in {len(files)} files, {size} characters")


if __name__ == "__main__":
    main()
