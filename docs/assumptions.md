# Assumptions

Everything the design takes as true without a source in the pilot definition. Each row states what would change if the assumption failed.

| Assumption | Basis | What changes if it fails |
|---|---|---|
| The farm node reaches the zones of cultivation and drying with one enclosure and wired probes | Minimum fixed hardware on the farm | A second small node per farm, with higher hardware cost |
| A shared LoRaWAN gateway can reach the out-of-coverage farms of a vereda from one high point with cellular signal | No new base station is allowed | Those farms need another link, such as satellite, or a data mule for readings as well |
| LTE is available on the routes and at the high points that matter | Current LTE-M and NB-IoT coverage in Colombia is unconfirmed | The node modem and the gateway backhaul change |
| Readings older than 24 hours in a full buffer are discarded and counted | The local buffer retains 24 hours at most | Storage on the node and the loss report change |
| Drone objects upload over HTTPS from the municipal seat or the collection center | Missions are preloaded at those same places | The object path and its subnet change |
| Harvest lasts four months a year | Team estimate for cost purposes | Monthly cost figures change |
| Three drone brigades, one per department, produce about 9,000 images in a harvest month | Team estimate for cost purposes | Inference and storage costs change |
| A designated drone-service supervisor authorizes fumigation, distinct from the pilot who flies | Human authorization with MFA is required | The authorizer role moves to another identity |
| Alerts reach the farmer by mobile push, and an SMS fallback stays optional | The price for Colombia could not be read from the price list | Alerts wait until the phone has data |
| The panel gives at least 3 peak sun hours on an average day | Needs field data | A larger panel or battery |
| Images average 3 MB | Common for a drone photo, to confirm with the supplier | Storage cost scales linearly |
| Three of the seven subnets hold interface endpoints and four stay reserved | Managed services and functions run outside subnets | A data or query service moves into a subnet |
| The United States is a valid destination for personal data under Colombian rules, with contractual clauses if needed | The status on the regulator's list is unconfirmed | Contract terms change, or personal data moves to another region |
