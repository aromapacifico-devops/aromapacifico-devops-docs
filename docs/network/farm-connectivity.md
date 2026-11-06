# Farm connectivity

A farm has no cable, and its cellular signal comes and goes. This document defines how the farm node reaches the platform over the mobile network, what it does while the signal is gone, and how it recovers with no reading lost silently, duplicated or misread. It covers the output protocol, the ingestion point, the hourly cycle, the 24-hour buffer, the clock of the node, the way configuration reaches a node that sleeps, the sequences of connection, disconnection and recovery, and how order and duplicates are handled.

## Contents

1. Context and scope
2. What the link carries
3. Protocol and ingestion point

### Terms used

| Term | Meaning in this document |
|---|---|
| Node | The enclosure on the farm with controller, modem, flash buffer and battery |
| Reading | One message from a node, with the time it was measured |
| Cycle | One wake-up of the node, from reading to sleep |
| Store-and-forward | The node keeps a reading while it has no path and sends it when the path returns |
| Attach | The modem registering on the mobile network |
| QoS 1 | MQTT delivery with confirmation, at least once |
| PUBACK | The confirmation of the broker for one QoS 1 message |
| Clean session | An MQTT connection with no state kept by the broker after it closes |
| Device Shadow | A document in AWS IoT that holds the desired and the reported state of a device |

---

## 1. Context and scope

The node lives on a solar kit and sleeps almost all the time. Coverage on a coffee slope changes with the weather, the load of the tower and the season, so the design treats signal as something that may be missing at any wake-up. A device that holds its data for up to 24 hours turns a connectivity problem into a delay, and every rule below serves that idea.

| Topic | Where it is defined |
|---|---|
| What the node measures, its energy and installation | [Sensors and operation](../iot/sensors-and-operation.md) |
| What happens to a reading after IoT Core | [Telemetry ingestion](../iot/telemetry-ingestion.md) |
| Farms with no coverage at all | [Out-of-coverage farms](../adr/out-of-coverage-connectivity.md) |
| Device identity and revocation | [Encryption, secrets and revocation](../security/encryption-secrets-revocation.md) |

This document covers a node on the cellular path, with signal and without it. The node keeps the same buffer and the same rules on the LoRa path, while its radio, frames and configuration path belong to the design of out-of-coverage farms. The generation of the modem stays open until coverage in Cauca, Huila and Tolima is confirmed, and nothing here depends on one in particular.

## 2. What the link carries

Volumes come from the pilot figures of 200 farms, 6 crop readings a day on each farm, and 24 drying readings a day on about 100 farms in harvest.

| Measure | Crop only | Crop and drying |
|---|---|---|
| Readings a day | 6 | 30 |
| Payload a day, at 0.5 KB a reading | 3 KB | 15 KB |
| Connections a day | 24 | 24 |
| TLS and MQTT overhead, at about 6 KB a connection | 144 KB | 144 KB |
| Configuration read, at about 1 KB a connection | 24 KB | 24 KB |
| **Total a day** | **171 KB** | **183 KB** |
| **Total in a 30-day month** | **About 5.1 MB** | **About 5.5 MB** |

Payload is the smallest part of the traffic. A connection costs far more than a reading, because a mutual TLS handshake exchanges certificates each time. The figure of 6 KB is an estimate to measure on the first nodes, and it scales the data plan linearly.

## 3. Protocol and ingestion point

The node publishes MQTT over TLS to AWS IoT Core, with its own X.509 certificate. Readings enter through one regional endpoint in us-east-1.

| Item | Value | Reason |
|---|---|---|
| Protocol | MQTT 3.1.1 over TLS 1.2 or 1.3 | Few bytes and little energy for a node that wakes to publish |
| Port | 8883, or 443 with ALPN `x-amzn-mqtt-ca` | The installer sets 443 where the carrier filters 8883 |
| Endpoint | Default `iot:Data-ATS` endpoint of the production account | Needs no domain or certificate of its own |
| Identity | X.509 certificate per node, client ID equal to the thing name | Revocable per device |
| Delivery | QoS 1 | The node deletes a reading only after its confirmation |
| Session | Clean session, keep-alive of 60 seconds | The node holds the buffer, so the broker keeps nothing for it |
| Publish topic | `aroma/{env}/farm/{node_id}/{stream}` | One topic per node and stream |
| Last will | None | Silence between cycles is normal, so a will message would say nothing |

| Option for the protocol | For | Against | Result |
|---|---|---|---|
| MQTT over TLS | Keeps one connection for a whole drain, low overhead, confirmation per message | Needs a TLS handshake per wake-up | **Chosen** |
| HTTPS publish | Works through any carrier filter | Overhead on each request, higher power use according to AWS, and no subscribe for configuration | Discarded |
| MQTT over WebSocket | Port 443 with no ALPN | Signature or custom authentication in place of the device certificate | Discarded |

QoS 2 is not an option, because IoT Core supports QoS 0 and 1 only. Duplicates are therefore part of the design, and section 9 handles them.

| Option for the endpoint | For | Against | Result |
|---|---|---|---|
| Default endpoint of the account | No domain, no certificate to renew, already serves 1,000 farms | A move of account or region changes the hostname on each node | **Chosen** |
| Custom domain on a configurable endpoint | The hostname survives a move | Needs a registered domain and a public certificate, and device certificates must still be registered at the target | Discarded for the pilot |

Device certificates tie the fleet to an account in either case, so a custom domain buys little. If the platform ever moves, the new hostname reaches each node through its configuration while the old endpoint still runs, and no visit is needed.

The endpoint scales with no change. Quotas for us-east-1 allow 3,000 connections and 20,000 inbound publishes a second per account, and 100 publishes a second per connection. At 1,000 farms the peak of section 5 reaches 8.3 messages a second.

Each node may act only on its own resources. The policy attached to the certificate uses the policy variable `iot:Connection.Thing.ThingName`, so a stolen certificate reaches nothing else.

| Action | Resource | Purpose |
|---|---|---|
| Connect | Client ID equal to the thing name | Identity of the connection |
| Publish | `aroma/{env}/farm/{node_id}/*` | Readings |
| Publish | `$aws/things/{node_id}/shadow/get`, `$aws/things/{node_id}/shadow/update` | Read configuration and report state |
| Subscribe, Receive | `$aws/things/{node_id}/shadow/get/accepted`, `.../get/rejected`, `.../update/accepted`, `.../update/rejected` | Answers to those requests |
