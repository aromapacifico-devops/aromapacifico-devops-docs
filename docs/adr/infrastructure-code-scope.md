# Infrastructure code covers telemetry ingestion and the focus confirmation function

## Context

The 100-hour code effort includes one workload module, ingestion or sack query, and the pattern of one function.

## Options

Telemetry ingestion, sack query, or both together.

## Decision

The code covers telemetry ingestion, the critical path that feeds the alert flow. The function pattern is focus confirmation, because that trigger reads an object, invokes inference and writes a result, which are the permissions the pattern must show.

## Consequences

Sack query stays in the architecture and uncoded. Both together would not fit the hours assigned to the module.
