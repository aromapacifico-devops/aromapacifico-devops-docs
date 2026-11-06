# Carrier phones keep positions for 24 hours and custody events until confirmed

## Context

A carrier loses data on farm tracks and mountain stretches, and the phone must decide what to hold until data returns. A custody event proves who held a sack and cannot be rebuilt. A position is one point of a route and is personal data on a device that can be lost.

## Options

Two classes of record with different limits, everything kept until confirmed, or custody events only.

## Decision

Positions stay on the phone for 24 hours at most, then they are deleted and counted. Custody events stay until the platform answers, with no time limit, and they go first on return. This keeps one retention rule across field devices, and custody is never lost by age.

## Consequences

An outage over 24 hours inside a trip leaves a counted hole in the route. A lost phone exposes at most one day of positions, in an encrypted store. If outages that long turn out to be common on the routes of the pilot, the limit on positions should rise, and the rest of the design holds.
