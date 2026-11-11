# Drone service

The drone service combines area flights, which delimit lots and estimate the harvest, with precision flights, which confirm a focus, fumigate it and verify the result. A lot passes to precision work when its polygon is published on the platform, and none of the five services replaces another.

| Document | What it answers |
|---|---|
| [Operating mode](operating-mode.md) | Why the service combines area and precision work, who does what, how often it flies and what it costs |
| [Lot boundaries and exclusion zones](lot-boundaries-and-exclusions.md) | How lot polygons, no-fly zones and no-spray strips are stored, published and enforced, and which legal distances apply |
| [Focus confirmation mission](focus-confirmation-mission.md) | What the confirmation flight carries and brings back, and how the case links to each object and to a result with its confidence |
| [Harvest estimation](harvest-estimation.md) | How one area flight per farm and a field sample give the collection center the expected sacks |
| [Roles, permits and campaigns](roles-permits-and-campaigns.md) | Who flies, who authorizes a fumigation, under which permit, what a campaign carries and how often each service flies in the pilot |
| [Drone campaign cost](campaign-cost-estimation.md) | What a mission, a campaign of one department, a month and a year of the service cost, with the rates and their sources |
| [Fumigation order](fumigation-order.md) | What a fumigation order holds, which records prove who authorized and who applied it, and which states it moves through until the verification closes it |
| [Flight objects and their transport](flight-objects.md) | Where photos, maps, polygons and logs live in the bucket, which events report their arrival, how an upload stays encrypted, whole and counted once, and why no order closes before its record is stored |
| [Verification after fumigation](post-fumigation-verification.md) | How a drone flight photographs the applied area, how a function decides from stored photos whether the order can close, and why a missing photo or a failed function leaves the fumigation open |

The [drone mission link](../network/drone-mission-link.md) explains how missions reach the drone and how flight logs and objects return to the platform. The [platform overview](../architecture/overview.md) places the service in the whole architecture.
