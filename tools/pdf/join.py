"""Joins pandoc JSON documents into one, each later document on a new page.
usage: join.py OUT ID:JSON [ID:JSON ...]"""
import json
import sys

out, inputs = sys.argv[1], sys.argv[2:]
joined = None
for i, item in enumerate(inputs):
    anchor, path = item.split(":", 1)
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    classes = ["document"] if i == 0 else ["document", "page-break"]
    marker = {"t": "Div", "c": [[anchor, classes, []], []]}
    if joined is None:
        joined = doc
        joined["blocks"] = [marker] + doc["blocks"]
    else:
        joined["blocks"] += [marker] + doc["blocks"]
with open(out, "w", encoding="utf-8") as f:
    json.dump(joined, f)
