# Each collection center contracts a dedicated WAN link

## Context

Each center has a 100 Mbps symmetric link shared with operations, and traffic classes guarantee rates to logistics and drone synchronization in both directions. The firewall of the center shapes only the traffic it sees, so a guarantee in the download holds only when the provider commits the rate. Operator references put a dedicated link of 80 to 120 Mbps at about USD 60 to 84 a month and shared business fiber at about USD 17 to 36.

## Options

A dedicated link with a committed rate, shared fiber with best-effort download, or leaving the type of link to the cost analysis.

## Decision

Each center contracts a dedicated 100 Mbps symmetric link with a committed rate. Where a municipality has no dedicated offer, the center takes shared fiber as a fallback. The upload classes and the local sharing still hold there, and the download guarantees become best effort.

## Consequences

The guarantees of the operation class hold in both directions. The three links cost more than shared fiber, and operator quotes for each municipality replace the references. The VPN tunnel bounds transfer efficiency at about 0.94, and the firewall clamps the TCP segment, since the tunnel has no path MTU discovery.
