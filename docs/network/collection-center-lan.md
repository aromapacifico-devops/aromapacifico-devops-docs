# Collection center LAN

Each of the three centers uses one network pattern, and only the second octet changes, with 41 for Cauca, 42 for Huila and 43 for Tolima. The pattern is drawn once in the connectivity diagram.

## Pattern

| Zone | Use | Expected clients | Network |
|---|---|---|---|
| Management | Desktops and phones | 2 desktops, 5 phones | 10.X.1.0/24 |
| Support | Desktops and phones | 2 desktops, 5 phones | 10.X.2.0/24 |
| Logistics | Sack reception and printing | 2 desktops, 20 phones | 10.X.3.0/24 |
| Transport | Driver phones in the yard | 20 phones | 10.X.4.0/24 |
| Visitors | Guests | 10 phones | 10.X.5.0/24 |
| Local servers | Printing and network control | To be sized | 10.X.10.0/24 |
| Cloud link | Edge firewall | Center firewall | 10.X.20.0/24 |

The inventory totals 66 clients per center, and every zone has room to grow inside its /24.

## Networks per center

| Zone | Cauca | Huila | Tolima |
|---|---|---|---|
| Management | 10.41.1.0/24 | 10.42.1.0/24 | 10.43.1.0/24 |
| Support | 10.41.2.0/24 | 10.42.2.0/24 | 10.43.2.0/24 |
| Logistics | 10.41.3.0/24 | 10.42.3.0/24 | 10.43.3.0/24 |
| Transport | 10.41.4.0/24 | 10.42.4.0/24 | 10.43.4.0/24 |
| Visitors | 10.41.5.0/24 | 10.42.5.0/24 | 10.43.5.0/24 |
| Local servers | 10.41.10.0/24 | 10.42.10.0/24 | 10.43.10.0/24 |
| Cloud link | 10.41.20.0/24 | 10.42.20.0/24 | 10.43.20.0/24 |

The first usable address of each network is its gateway, on the center firewall.

## Paths out of the center

Only logistics and local servers reach the cloud through the VPN tunnel, with the routes 10.X.3.0/24 and 10.X.10.0/24. The cloud link network holds the tunnel endpoint and carries no client traffic. The remaining zones use the internet through the firewall, and the visitor network has no route to logistics or management.

![Connectivity and collection center pattern](../architecture/diagrams/03-connectivity-and-centers.drawio.png)
