# Sacks use pre-printed labels, and events live in an insert-only table

## Context

A farm has no printer and may have no data, while the handover must scan a code. The custody chain is only worth trusting if its events cannot change, and two people can write on one sack at the same moment.

## Options

For the code at a farm, pre-printed labels, a code generated on the phone, or registration only with data.

For storage, two tables, or one table with item types.

For the evidence of a handover, a carrier scan with location, or a confirmation by the farmer.

## Decision

The platform issues codes ahead of time, and farms receive pre-printed labels. Events live in `sack_events`, where the function can insert and never update or delete, and the current state lives in `sacks`, written in the same transaction under a version condition. A handover rests on a scan by the carrier, with location and time.

## Consequences

A farm registers a sack with no connection, and the platform can tell an issued code from a forged one. Label logistics is new work. A policy cannot stop an insert from replacing an item, so the condition in the write protects that case, and deployment controls cover its code. The farmer confirms nothing at the handover, so a wrong one surfaces later.
