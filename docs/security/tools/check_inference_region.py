"""Checks that inference stays in the United States.

Usage: python3 check_inference_region.py [code_dir ...]
With no arguments it reads the infrastructure and module repositories cloned next to this one.

1. Every model identifier in the code uses the US geographic profile, and no file names a global one.
2. The model Regions the roots allow are the destination Regions of that profile.
3. The service control policy denies the global profile, the global model ARN and any Region
   outside those destinations.
4. The AI services opt-out policy opts every service out.
Exits 1 on the first failed check.
"""
import json
import pathlib
import re
import sys

DESTINATIONS = ["us-east-1", "us-east-2", "us-west-2"]


def fail(message):
    print(f"FAIL {message}")
    sys.exit(1)


def main():
    here = pathlib.Path(__file__).resolve().parent.parent / "policies"
    workspace = pathlib.Path(__file__).resolve().parents[4]
    dirs = [pathlib.Path(d) for d in sys.argv[1:]] or [workspace / "aromapacifico-devops-infra",
                                                      *sorted(workspace.glob("terraform-aws-*"))]
    files = [f for d in dirs for f in d.rglob("*.tf") if ".terraform" not in f.parts]
    if not files:
        fail("no Terraform files found")

    model_ids, region_lists = [], []
    for f in files:
        text = f.read_text()
        if re.search(r'"global\.[a-z]', text):
            fail(f"{f} names a global inference profile")
        model_ids += re.findall(r'_model_id\s*=\s*"([^"]+)"', text)
        region_lists += re.findall(r'_model_regions\s*=\s*\[([^\]]*)\]', text)
    if not model_ids:
        fail("no model identifier found in the code")
    for model in model_ids:
        if not model.startswith("us."):
            fail(f"model {model} does not use the US geographic profile")
    for regions in region_lists:
        found = sorted(re.findall(r'"([^"]+)"', regions))
        if found != DESTINATIONS:
            fail(f"model Regions {found} differ from the profile destinations {DESTINATIONS}")

    scp = json.loads((here / "deny-global-inference.json").read_text())
    denied = {r for s in scp["Statement"] if s["Effect"] == "Deny" and "Condition" not in s
              for r in ([s["Resource"]] if isinstance(s["Resource"], str) else s["Resource"])}
    for arn in ("arn:aws:bedrock:*:*:inference-profile/global.*", "arn:aws:bedrock:::foundation-model/*"):
        if arn not in denied:
            fail(f"the service control policy does not deny {arn}")
    allowed = [s["Condition"]["StringNotEquals"]["aws:RequestedRegion"] for s in scp["Statement"]
               if s["Effect"] == "Deny" and "aws:RequestedRegion" in s.get("Condition", {}).get("StringNotEquals", {})]
    if sorted(allowed[0] if allowed else []) != DESTINATIONS:
        fail("the service control policy does not limit inference to the profile destinations")

    opt_out = json.loads((here / "ai-opt-out.json").read_text())
    if opt_out.get("services", {}).get("default", {}).get("opt_out_policy", {}).get("@@assign") != "optOut":
        fail("the opt-out policy does not opt every service out")
    print(f"OK {len(model_ids)} model identifiers on the US profile, {len(region_lists)} Region lists, "
          f"global profile denied, opt-out for every service")


if __name__ == "__main__":
    main()
