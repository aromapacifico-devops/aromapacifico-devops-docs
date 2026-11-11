# Architecture decisions

Each record states the problem, the options and the decision, in terms a reviewer can challenge. `template.md` is the format for new records.

| Decision | Result |
|---|---|
| [Primary and second cloud](cloud-platform.md) | AWS us-east-1, with Azure East US prepared and idle |
| [Out-of-coverage farms](out-of-coverage-connectivity.md) | Shared LoRaWAN gateway for readings, data mule for objects |
| [Mobile network generation](mobile-network-generation.md) | No dependence on 2G or 3G, and the modem chosen with the operator |
| [Farm node connection](farm-node-connection.md) | One cycle each hour, configuration through a Device Shadow, default IoT endpoint |
| [Carrier data on the phone](carrier-data-on-phone.md) | Positions for 24 hours, custody events until confirmed |
| [LoRa link reliability](lora-link-reliability.md) | Cumulative application acknowledgement, versioned batch frame, desired configuration with the applied version |
| [Sack event history](sack-event-history.md) | State derived from events, return after a center rejection, port rejection ends the record |
| [Custody chain storage](custody-chain-storage.md) | Pre-printed labels, two tables, handover by scan with location |
| [Port delivery evidence](port-delivery-evidence.md) | Receiver and receipt reference, delivery stays final |
| [Tracking outside working hours](tracking-pause.md) | One trip per leg, and a pause by the carrier with a reminder |
| [Drone operating mode](drone-operating-mode.md) | Combination of area and precision work |
| [pH measurement](ph-measurement.md) | Soil probe, with a manual reading as a fallback |
| [Flight log and fumigation](flight-log-and-fumigation.md) | Two logs, one before authorization and one before closure |
| [Drone mission signing](drone-mission-signing.md) | Packages signed with a KMS key, results signed with the station device key |
| [Spraying strips](spraying-strips.md) | Legal strips as parameters, ground application when the drone strip blocks a focus |
| [Harvest estimation method](harvest-estimation-method.md) | Tree count, field sample and Cenicafé factor, one mission per farm |
| [Alert ranges](alert-ranges.md) | Versions judged by measured time, humidity on the soil, temperature on the air |
| [Confirmation focus](confirmation-focus.md) | A circle around the node, only cultivation alerts open a case |
| [Infrastructure code scope](infrastructure-code-scope.md) | Telemetry ingestion and the focus confirmation function |
| [Telemetry storage](telemetry-storage.md) | DynamoDB for 90 days, S3 for five years |
| [Managed inference](managed-inference.md) | Bedrock for analysis, Rekognition as a person filter |
| [Fleet and harvest estimates](fleet-and-harvest-estimates.md) | Three brigades, four months of harvest |
| [Object storage access](object-storage-access.md) | Gateway endpoints for S3 and DynamoDB |
| [Center WAN capacity](center-wan-capacity.md) | Priority for logistics, visitors capped at 10 percent |
| [Dedicated center link](dedicated-center-link.md) | Committed rate at each center, shared fiber as the fallback |
| [Center cloud link](center-cloud-link.md) | Static site-to-site VPN on a virtual private gateway, explicit routes and endpoint names |
| [Farm module](farm-module.md) | One reusable module, certificate from a CSR |
| [Demonstration account](demonstration-accounts.md) | One standalone credit account, environments that go up and down |
| [Repository structure](repository-structure.md) | One repository per module, separate from the infrastructure repository |
| [State per environment](state-per-environment.md) | One root, one state and one bucket per environment |
| [Infrastructure checks](infrastructure-checks.md) | Automatic checks on each pull request, with pinned tools |
| [Public lookup path](public-lookup-path.md) | Function URL behind CloudFront, ceiling of five reserved copies |
