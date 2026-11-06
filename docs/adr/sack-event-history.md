# The state of a sack is derived from its event history

## Context

The people who handle a sack work on separate phones and networks, so a center can receive a sack before the handover reaches the platform. The pilot names seven states and leaves open what follows a rejection. A rejection must keep the history of the sack.

## Options

For the source of truth, an event history with a derived state, a current state validated on arrival, or the last write by time.

For a rejection at the center, return with the same code, a terminal state with re-entry as a new sack, or a terminal state with no re-entry.

For a rejection at the port, a terminal state, or a return to the center.

## Decision

Events are stored unchanged, and the state comes from replaying them in logical order, so any arrival order gives the same result. An event ahead of the history moves the state and marks a gap, an event against the history stays as an anomaly for review, and only a malformed event is refused. A sack rejected at a center returns to its farm with the same code. A rejection at the port ends the record.

## Consequences

One physical sack keeps one code and one history, and a late event never blocks the work of a center. Each event costs one more read and a transaction. A dispatch or a delivery can pass with a gap, so the operator reviews gaps older than 48 hours. If rejected sacks do not return to their farms, the return event must change.
