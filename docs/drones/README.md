# Drone service — design documents

The pilot uses the approved **combined** model: area flights for lot delimitation and harvest estimates; precision flights for focus confirmation, authorized fumigation and verification. A platform publication event allows the transition to precision work. **None of the five services replaces another.**

| Document | Scope | GitHub issue |
|---|---|---|
| [Operating mode](operating-mode.md) | Approved ADR-aligned model, services, operators, cadence and budget assumptions | [#75](https://github.com/aromapacifico-devops/aromapacifico-devops-docs/issues/75) |
| [Lot boundaries and exclusion zones](lot-boundaries-and-exclusions.md) | GeoJSON contract, preflight exclusion review, published lot versions, mission gates | [#31](https://github.com/aromapacifico-devops/aromapacifico-devops-docs/issues/31) |
| [Harvest estimation](harvest-estimation.md) | One area mission per harvest, evidence and inference flow, read-only estimates for collection centers | [#35](https://github.com/aromapacifico-devops/aromapacifico-devops-docs/issues/35) |

These documents are **architecture and design only**: they do not implement business services, firmware, UAV operations or Terraform. See the [platform architecture](../architecture/overview.md) and the [flight-log decision](../adr/flight-log-and-fumigation.md) for shared guardrails.
