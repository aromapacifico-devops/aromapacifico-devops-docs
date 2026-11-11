# Inference cost is reported per image analyzed, with a cost for each trigger beside it

## Context

The platform must state what its managed inference costs for every thousand invocations in harvest. A function run can analyze one photo or one hundred, and the telemetry batch calls no model at all, so the meaning of an invocation sets the figure. The drone operating mode counts 9,000 images in a harvest month, while the inference design counts 8,500 images that reach a function.

## Options

For the unit, the image analyzed, the function run, or the image as headline with a cost for each trigger beside it. For the volume, the 8,500 images that reach a function by trigger or the 9,000 drone images of the operating mode.

## Decision

The headline unit is 1,000 images analyzed, USD 1.89 in harvest with the run overhead and the orthomosaic spread over them. Each trigger has its own cost per 1,000 function runs. The volume is the 8,500 images that reach a function in an average harvest month, with the month that holds every estimation flight as the ceiling. The figures live in their own governance document, computed by a script that checks the document.

## Consequences

The figure follows what the bill follows and compares directly with a quote or another model. A single figure for all function runs would be set by the telemetry objects and would hide the vision cost. The fumigation photos stay out because no function reads them. The monthly cloud cost and the [pilot cost](../governance/pilot-cost.md) use USD 16.26 for an average harvest month, and the pilot cost keeps USD 45.95 as the ceiling of the estimation month.
