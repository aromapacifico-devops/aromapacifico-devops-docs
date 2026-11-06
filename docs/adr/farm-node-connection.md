# Farm nodes run one hourly cycle and read configuration from a Device Shadow

## Context

A farm node sleeps on solar power, and its signal comes and goes. It must publish when it can, keep readings for up to 24 hours, and learn when a farmer starts drying from the application. A crop reading is due only every 4 hours, so a node that connected only for readings would miss short windows of signal and could wait 4 hours to start monitoring a drying lot. A sleeping device cannot receive a push.

## Options

For the cycle, one hourly cycle with a connection each time, a connection on each reading with hourly retries while data is pending, or a connection only on each reading.

For configuration, a classic Device Shadow, a persistent session with a command topic, or a retained message per node.

For the ingestion point, the default IoT endpoint of the account, or a custom domain on a configurable endpoint.

## Decision

The node wakes each hour at a minute fixed for it and connects every time, reading only when a reading is due. It reads a classic Device Shadow after each drain, and it publishes to the default endpoint. One rule then covers reading, retry and configuration, a farmer waits one hour at most for drying monitoring to start, and the fixed minutes spread the return of a whole area across one hour.

## Consequences

A crop-only node uses about 5.1 MB a month in place of about 1.4 MB, the modem takes 1.2 Wh a day at worst, and the cloud adds about USD 0.48 a month for 200 farms. The node policy must allow its own shadow. A move of account or region changes the hostname on each node, through the shadow while the old endpoint still runs. Measured modem power or connection size well above the assumed values would reopen the choice of the cycle.
