# Architecture decisions

Each record states the problem, the options and the decision, in terms a reviewer can challenge. `template.md` is the format for new records.

| Decision | Result |
|---|---|
| [Primary and second cloud](cloud-platform.md) | AWS us-east-1, with Azure East US prepared and idle |
| [Out-of-coverage farms](out-of-coverage-connectivity.md) | Shared LoRaWAN gateway for readings, data mule for objects |
| [Farm node connection](farm-node-connection.md) | One cycle each hour, configuration through a Device Shadow, default IoT endpoint |
| [Carrier data on the phone](carrier-data-on-phone.md) | Positions for 24 hours, custody events until confirmed |
| [Sack event history](sack-event-history.md) | State derived from events, return after a center rejection, port rejection ends the record |
| [Custody chain storage](custody-chain-storage.md) | Pre-printed labels, two tables, handover by scan with location |
| [Port delivery evidence](port-delivery-evidence.md) | Receiver and receipt reference, delivery stays final |
| [Drone operating mode](drone-operating-mode.md) | Combination of area and precision work |
| [pH measurement](ph-measurement.md) | Soil probe, with a manual reading as a fallback |
| [Flight log and fumigation](flight-log-and-fumigation.md) | Two logs, one before authorization and one before closure |
| [Infrastructure code scope](infrastructure-code-scope.md) | Telemetry ingestion and the focus confirmation function |
| [Telemetry storage](telemetry-storage.md) | DynamoDB for 90 days, S3 for five years |
| [Managed inference](managed-inference.md) | Bedrock for analysis, Rekognition as a person filter |
| [Fleet and harvest estimates](fleet-and-harvest-estimates.md) | Three brigades, four months of harvest |
| [Object storage access](object-storage-access.md) | Gateway endpoints for S3 and DynamoDB |
| [Center WAN capacity](center-wan-capacity.md) | Priority for logistics, visitors capped at 10 percent |
| [Farm module](farm-module.md) | One reusable module, certificate from a CSR |
| [Demonstration accounts](demonstration-accounts.md) | Standalone credit accounts, environments that go up and down |
