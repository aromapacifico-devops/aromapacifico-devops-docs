# Requirements kept, replaced and retired from the 2020 design

The 2020 pilot design was never deployed. The Federation resumes it in 2026 with the same territory and capabilities, on connectivity assumptions that hold today. This matrix records what survives and what does not, so that no outdated premise reaches the platform.

## Matrix

| Requirement or premise from 2020 | Decision | Reason | Affected component |
|---|---|---|---|
| Territory of Cauca, Huila and Tolima | Kept | The pilot keeps its scope | All |
| Crop and drying monitoring with farmer alerts | Kept | Core capability of the pilot | Telemetry ingestion, alerts |
| Harvest and packing record in 60 kg sacks | Kept | Core capability of the pilot | Sack events |
| Trip tracking to the collection center and to Buenaventura | Kept | Core capability of the pilot | Carrier application, trip events |
| Sack lookup by code for farmer, center and buyer | Kept | Core capability of the pilot | Sack query |
| Drone service for delimiting, confirming, fumigating, verifying and estimating | Kept | The five services stay, and none replaces another | Drone service, flight objects, inference |
| Data coverage on most farms | Replaced | Part of the pilot lies outside coverage | Farm connectivity, store-and-forward with a 24-hour limit |
| Device publishing straight to the ingestion point | Replaced | Without signal the device must hold its readings | Farm node buffer, shared LoRaWAN gateway |
| Weekly visits as a data path | Retired | Travel in the veredas is difficult and costly | Remote connectivity, drone confirmation |
| Collection centers without LAN | Replaced | Each center needs a segmented network | Center LAN, WLAN, perimeter firewall |
| Collection centers without WAN | Replaced | Each center needs a route to the cloud | 100 Mbps link, site-to-site VPN |
| Port without LAN or WAN | Replaced | The Federation deploys no equipment in Buenaventura. The shipping company keeps its telemetry and the platform records the delivery event | Delivery event |
| Dependence on a mobile network generation being retired | Retired | The access network changed since 2020 and 2G and 3G are being withdrawn | Node modem, drone link |
| 2020 prices | Retired as invalid | They do not reflect current quotations | Cost document |
| 2020 devices | Retired as invalid | They do not reflect current specifications | Farm node, drone |
| 2020 cloud services | Retired as invalid | The platform is designed on current services | Cloud architecture |

## New requirements with no 2020 equivalent

| Requirement | Component |
|---|---|
| Local buffer that retains readings for 24 hours at most | Farm node |
| Mission loaded before takeoff and flight log closed before fumigation is authorized | Drone service |
| Event-driven inference that ends when the result is stored | Inference functions |
| Network pattern that grows from 200 to 1,000 farms with no change to addressing or the ingestion point | Cloud network, ingestion |
