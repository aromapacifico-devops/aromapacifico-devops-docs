# AWS us-east-1 is the primary cloud and Azure East US is the prepared second cloud

## Context

The platform needs managed IoT ingestion, event-driven functions, object storage and managed image inference. The team's infrastructure standards are written for AWS. Neither AWS nor Azure has a region in Colombia.

## Options

AWS us-east-1 with Azure prepared, AWS sa-east-1 with Azure prepared, and Azure or GCP as primary.

## Decision

AWS us-east-1 is primary, because every service in the design is available there and the 26 infrastructure rules apply as written. Azure East US is the second cloud and stays idle.

Latency is left out as an argument, since it has not been measured from the pilot's sites. The Bogota Local Zone is announced and unavailable, and its parent region is us-east-1, so adopting it later would extend this choice.

## Consequences

Personal data leaves Colombia, as it would with any option. Moving to Azure would mean rebuilding the platform from the contracts and the equivalence table, since nothing runs there. A measured latency above the alert budget would reopen the region choice.
