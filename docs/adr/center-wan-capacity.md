# Center WAN gives priority to logistics and caps visitors

## Context

Each center has a 100 Mbps symmetric link shared with operations. The inventory lists 66 clients, and the reference capacity is 2 Mbps down and 0.5 Mbps up per active client, which would need 132 Mbps if all were active.

## Options

Oversize the link, or manage it with traffic classes.

## Decision

The link stays at 100 Mbps, which serves up to 40 simultaneous clients at the reference rate with room for system traffic. Logistics and drone synchronization get priority, and the visitor network is capped at 10 percent of the link.

## Consequences

Non-operational traffic gives way under load. Sustained use above 40 active clients would need a wider link.
