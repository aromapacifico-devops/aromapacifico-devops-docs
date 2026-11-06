# Farm connectivity

A farm has no cable, and its cellular signal comes and goes. This document defines how the farm node reaches the platform over the mobile network, what it does while the signal is gone, and how it recovers with no reading lost silently, duplicated or misread. It covers the output protocol, the ingestion point, the hourly cycle, the 24-hour buffer, the clock of the node, the way configuration reaches a node that sleeps, the sequences of connection, disconnection and recovery, and how order and duplicates are handled.

## Contents

1. Context and scope
2. What the link carries
3. Protocol and ingestion point
4. The hourly cycle
5. Store-and-forward buffer
6. Time on the node
7. Configuration back to the node

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

The endpoint scales with no change. Quotas for us-east-1 allow 3,000 connections and 20,000 inbound publishes a second per account, and 100 publishes a second per connection. At 1,000 farms the peak of section 4 reaches 8.3 messages a second.

Each node may act only on its own resources. The policy attached to the certificate uses the policy variable `iot:Connection.Thing.ThingName`, so a stolen certificate reaches nothing else.

| Action | Resource | Purpose |
|---|---|---|
| Connect | Client ID equal to the thing name | Identity of the connection |
| Publish | `aroma/{env}/farm/{node_id}/*` | Readings |
| Publish | `$aws/things/{node_id}/shadow/get`, `$aws/things/{node_id}/shadow/update` | Read configuration and report state |
| Subscribe, Receive | `$aws/things/{node_id}/shadow/get/accepted`, `.../get/rejected`, `.../update/accepted`, `.../update/rejected` | Answers to those requests |

## 4. The hourly cycle

The node runs one cycle each hour, all year, whether or not a reading is due. It wakes at a minute of the hour fixed for that node, taken from a hash of `node_id`, and it connects every time.

| Option | Worst delay added to an alert | Connections a day, crop only | Wait for drying to start | Modem energy a day |
|---|---|---|---|---|
| **One cycle each hour** | 1 hour | 24 | Up to 1 hour | 0.45 Wh, 1.2 Wh with every attempt failing |
| Connect on a reading, and hourly while data is pending | 1 hour | 6 | Up to 4 hours | 0.11 Wh with signal |
| Connect only on a reading | 4 hours | 6 | Up to 4 hours | 0.11 Wh with signal |

Energy assumes 1.5 W on average, 45 seconds for a good connection and 120 seconds for a failed attempt, to be measured with the chosen modem.

One rule covers reading, retry and configuration. A failed attempt needs no retry logic of its own, because the next hour is the retry, and a node whose certificate was revoked simply fails each hour with no special case. Short windows of signal are also caught, which a node on a 4-hour rhythm would miss. Grain above 40 °C is the most urgent alert of the design, so a farmer who starts drying should wait one hour at most for the node to begin measuring.

The cost is small. In the worst case, with every attempt failing, the modem uses 1.2 Wh a day, 4 percent of the 30.7 Wh daily budget of the node. A node already drying connects hourly under any of the three rules. For a node with crop readings only, the monthly data grows from about 1.4 MB to about 5.1 MB.

The fixed minute also removes the rush that follows an outage. Nodes on one shared schedule would all wake together, and all drain together when a tower returns. Each node keeps its own minute, so the load spreads evenly across the hour with no random delay and no wait added to the alert.

| Measure | 200 farms | 1,000 farms |
|---|---|---|
| Connections an hour | 200 | 1,000 |
| Messages after every node was out for a full day, at 30 readings each | 6,000 | 30,000 |
| Peak rate, spread over the hour | 1.7 a second | 8.3 a second |

An attempt has a window of 120 seconds, counted from powering the modem until the connection is open. Inside the window the node retries the connection with exponential backoff and random jitter. When the window closes, the modem powers off and the node sleeps. The hourly wake-up is the outer retry, and it needs no further backoff.

## 5. Store-and-forward buffer

The buffer is an append-only log in the encrypted flash of the node. Each record holds the sequence number, the time of the reading, the values and a checksum. The buffer retains 24 hours at most.

| Rule | Behavior | Reason |
|---|---|---|
| Write first | The reading reaches the flash before the modem powers on | A failed connection loses nothing |
| Purge before connecting | Each cycle deletes records of age 24 hours or more, then connects | No reading ever passes 24 hours |
| Count what is deleted | Each deleted record adds one to `dropped_total` | The platform knows what is missing |
| Drain oldest first | Up to 10 unconfirmed messages at a time | The history arrives in order in the normal case |
| Delete on confirmation | A record leaves the buffer only after its PUBACK | A lost connection leaves it safe for the next cycle |
| Sequence survives restarts | On boot the node continues from the last record in the log | Duplicates and gaps stay detectable |

Capacity sets no limit. A full day holds 30 readings, or 15 KB, against 64 MB of flash. The limit of 24 hours is a rule of the pilot, because an older reading no longer supports a timely decision.

The ten-message window sits well below the quota of 100 unacknowledged messages. With an unstable signal it limits how many messages must be sent again, and 30 readings still drain in three rounds of confirmation, a matter of seconds.

The purge runs before the connection, so with one attempt each hour the last chance for a reading comes at an age of about 23 hours.

| Length of the outage | What reaches the platform | Delay |
|---|---|---|
| Under 1 hour | Everything | At the next cycle, 1 hour at most |
| 1 to 23 hours | Everything | The outage, plus up to 1 hour |
| 23 to 24 hours | Everything, except the oldest reading in some cases | The outage, plus up to 1 hour |
| Over 24 hours | The readings of the last 23 hours. Older ones are counted in `dropped_total` | Up to 1 hour after the signal returns |

With no ranges on the node, it cannot tell which reading deserves an alert, so the drain gives no priority to any of them. The platform evaluates each reading on arrival. An alert from a buffered reading goes out at the drain, within the 24-hour limit, and it carries the time of the reading.

## 6. Time on the node

`measured_at` is the base of the buffer limit, the order of readings and the age of an alert, and TLS itself needs a valid date to check the certificate of the endpoint. The clock therefore has to work before the connection.

| Source | When it is used |
|---|---|
| Real-time clock with backup power | Always, including sleep and a brownout |
| Network time from the modem | At each attach, when the carrier provides it |
| NTP from `time.aws.com`, UDP port 123 | When the carrier provides no time |

The node synchronizes right after the attach and before TLS. An ordinary 20 ppm crystal drifts less than 2 seconds a day, so an outage of one day leaves the readings well within what the alert needs.

A node that lost its clock, for example with a dead battery and a failed backup, still reads on schedule. It stores the seconds elapsed since boot in place of the time, and the first synchronization turns them into `measured_at`. If power fails again before that happens, those readings have no recoverable time, so the node deletes them and counts them in `dropped_total`.

The platform never relies on the node clock alone. The IoT rule adds `received_at` from `timestamp()`, the time seen by the rules engine, and the ingestion function compares both values.

| Check | Action |
|---|---|
| `measured_at` more than 5 minutes ahead of `received_at` | Dead letter queue and a clock alarm |
| `measured_at` more than 25 hours behind `received_at` | Stored in the history, no alert, clock alarm |
| Anything else | Normal path, and the difference is the drain delay |

## 7. Configuration back to the node

The node keeps no alert ranges, since those live on the platform. It still needs one fact from the platform, whether a lot is drying, because the farmer starts and stops that cadence from the application. A node that sleeps cannot receive a push, so it must fetch the value when it wakes.

| Option | For | Against | Result |
|---|---|---|---|
| Classic Device Shadow | Built for devices that disconnect, keeps the last value with no expiry, shows the application what the node applied | One more exchange per connection | **Chosen** |
| Persistent session with a command topic | Plain MQTT | Sessions expire after one hour by default, so a node out for longer loses them, and queued messages are billed again on delivery | Discarded |
| Retained message per node | Plain MQTT, no expiry in MQTT 3 | No reported state, so the application cannot tell whether the node applied the change | Discarded |

The application writes the desired state, and the node writes the reported state and nothing else.

```json
{
  "state": {
    "desired": { "drying": true },
    "reported": { "drying": false }
  }
}
```

The node reads the shadow after the drain, so a long configuration exchange can never delay a reading. It applies any difference and reports the new value, and the application then shows that drying monitoring is active. A farmer who presses start while the node has no signal sees the request as pending, and the node applies it on the first connection.

The same document can carry a new endpoint if the platform ever moves. A LoRa node has no shadow, so its configuration path belongs to the design of out-of-coverage farms.
