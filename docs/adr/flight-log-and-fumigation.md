# Fumigation depends on two flight logs

## Context

No fumigation may be authorized without a closed flight log, and a fumigation may not close until its own log is stored. Read together as one log, those two rules are circular.

## Options

One log for the whole case, or separate logs for each flight.

## Decision

Each flight has its own log. The delimitation or confirmation flight closes its log first. A person then authorizes the order. The fumigation flight and the verification close the case with their own logs and objects.

## Consequences

The order of events is checkable at each step. A missing log leaves the case open, and the observability dashboards report it.
