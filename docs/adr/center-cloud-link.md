# Each center reaches the cloud through a static site-to-site VPN on a virtual private gateway

## Context

A collection center needs an encrypted link to the cloud to register sacks without exposing its network. The platform already places a virtual private gateway in each environment, a firewall at each center with IKEv2, two tunnels and a static public address, and endpoints for IoT Core, S3 and the private REST API that only logistics and local servers may reach. The firewall model is not chosen, so a routing protocol on it cannot be required today.

## Options

A site-to-site VPN on a virtual private gateway or on a transit gateway, Direct Connect, or a client VPN on each device. For the VPN, static routes of the two center ranges or BGP.

## Decision

Each center uses one site-to-site VPN connection on the virtual private gateway of each environment it serves, with static routes. The connection carries the logistics and local servers ranges of the center, and the cloud tables hold explicit routes to only those ranges. The firewall of the center routes only to the subnets that hold endpoints. BGP stays a future alternative with stated conditions and is not an automatic backup of the static routes.

Cloud names reach a center through the endpoint-specific names of the interface endpoints for the private REST API and S3, and through a local record on the firewall for the IoT Core data name. A Route 53 Resolver inbound endpoint is not adopted, since it adds USD 182.50 a month for each environment.

## Consequences

- The firewall needs no routing protocol, and the design has no extra complexity of BGP.
- Failover between the two tunnels depends on the health checks of the firewall, since there is no BGP liveness check. No recovery time is promised, and both tunnels share the WAN link and the firewall of the center.
- The routes and the names are design read in documentation and are not tested. The first center must show the names, the ports of IoT Core, presigned URLs for S3 and the failover.
- A change to BGP, to a resolver in the cloud or to a different link type needs a new record.
