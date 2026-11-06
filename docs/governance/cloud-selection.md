# Cloud selection

This document justifies AWS in us-east-1 as the primary cloud and Azure East US as the second cloud, prepared with no running resources. It compares the options against the real load of the pilot, states where the data lives, and defines exactly what "prepared" means.

## Contents

1. What the platform asks of a cloud
2. Options evaluated
3. Comparison
4. Cost compared on the pilot load
5. Region
6. Data residency
7. Second cloud
8. What would change this decision
9. Assumptions and pending confirmations

### Terms used

| Term | Meaning in this document |
|---|---|
| Primary cloud | The cloud where the pilot runs |
| Second cloud | The cloud kept ready as an exit, with no duplicated platform |
| Local Zone | AWS infrastructure in a metropolitan area, attached to a parent region |
| Provisioned unit | Capacity bought by the month, whether or not it is used |
| Managed inference | A model operated by the provider, called per request and never trained by the team |

---

## 1. What the platform asks of a cloud

| Need | Source in the pilot | Consequence for the cloud |
|---|---|---|
| Device ingestion with per-device identity | 200 nodes, revocable one by one | Managed IoT service with X.509 |
| Low-power radio for farms with no signal | Some farms lie outside coverage | Managed or simple LoRaWAN server |
| Event-driven inference, no compute waiting | The function ends when the result is stored | Functions triggered by object storage |
| Image analysis with no training | No model is trained | Pretrained multimodal model |
| Five-year retention at low cost | Readings, photos, flights, sack history | Lifecycle rules toward cold storage |
| Sack events losing at most 15 minutes | Recovery objective | Continuous backup of the database |
| Low monthly cost | The farmer invests little | Pay per use with no provisioned minimum |
| 100 hours of infrastructure code | Hard limit | Standards already written for that cloud |

## 2. Options evaluated

| Option | Reason to consider it | Result |
|---|---|---|
| AWS us-east-1 with Azure prepared | Covers every service, standards written for AWS | **Chosen** |
| AWS sa-east-1 with Azure prepared | Closer to Colombia on the map | Discarded, see section 5 |
| Azure East US as primary | Comparable services | Discarded, see sections 3 and 4 |
| GCP as primary | Cloud Functions and Vertex AI cover the need | Discarded, since the team's standards would need rewriting and it offers no gain for this load |

## 3. Comparison

| Criterion | AWS us-east-1 | Azure East US |
|---|---|---|
| IoT ingestion | IoT Core with MQTT over TLS 1.3 and TLS 1.2, per-device X.509, rules engine | IoT Hub with per-device identity |
| Billing of ingestion | Per message | Per provisioned unit |
| LoRaWAN | IoT Core for LoRaWAN, a managed network server | No managed network server identified |
| Functions | Lambda, triggered by S3 through EventBridge, and by SQS | Functions, triggered by Blob Storage and Event Grid |
| Managed inference | Bedrock multimodal models, Rekognition for the person filter | Azure OpenAI and Azure AI services |
| Object storage | S3 with lifecycle rules | Blob Storage with lifecycle rules |
| Database | DynamoDB with transactions and point-in-time recovery | Cosmos DB |
| Region in Colombia | None | None |
| Team standards | The 26 infrastructure rules are written for AWS | All 26 rules need adapting |

The last row weighs more than it seems. Adapting 26 rules would consume hours from the code budget, which is the one limit of the project that cannot move. Those rules date from December 2025, so each one is checked against current documentation before the code relies on it. That check applies on either cloud, and it takes far less time than rewriting the rules for another provider.

## 4. Cost compared on the pilot load

The pilot sends about 108,000 device messages in a harvest month, about 3,600 a day.

| Item | AWS | Azure |
|---|---|---|
| List price | USD 1.00 per million messages | USD 25 per month for an S1 unit, USD 10 for B1 |
| Unit capacity | Not applicable | 400,000 messages a day per unit |
| Cost at pilot load | USD 0.11 a month in messages | USD 25 a month for S1 |
| Use of capacity | Pays for what is sent | About 1 percent of the unit |
| Cost at 1,000 farms | USD 0.54 a month | USD 25 a month, the unit still covers it |

Both are small amounts, and neither would decide the matter alone. The difference shows the pattern. At this load, pay-per-use means the platform costs almost nothing until the pilot succeeds, while a provisioned unit charges for 99 percent idle capacity. S1 is the comparable tier, since B1 leaves out cloud-to-device messaging and device twins.

## 5. Region

| Option | For | Against |
|---|---|---|
| us-east-1, Virginia | Every service in the design, widest model catalog, lowest list prices, parent of the Bogota Local Zone | Not in Colombia |
| sa-east-1, Sao Paulo | Same continent | IoT messages cost USD 1.50 per million against USD 1.00, and fewer models are available for inference |
| Bogota Local Zone | Would be in Colombia | Announced and unavailable, and a Local Zone offers only a subset of services |

The choice rests on service coverage and alignment with the standards. Latency from the pilot's sites has not been measured, so it is left out of the argument. The alert budget of five minutes is wide compared with any network round trip, so latency cannot decide this region. The first deployment should measure it from a center.

## 6. Data residency

Data resides in Virginia, in the United States, since neither AWS nor Azure has a region in Colombia. Personal data leaves the country under every option evaluated, so this point does not separate them. The personal data policy describes how the transfer is handled.

## 7. Second cloud

The second cloud exists to keep an exit available without paying for a copy of the platform. Replicating the platform would double fixed cost and would give a recovery the pilot does not require, since the objectives of 15 minutes and 4 hours are met inside the primary region.

| Prepared | Left out, on purpose |
|---|---|
| Portable contracts, with MQTT topics and JSON messages | Running resources of any kind |
| Equivalence table, below | Replicated data |
| Object layout and event schemas documented | A network link between clouds |
| Recovery procedure from the S3 archive | Automatic failover |

| Function | AWS | Azure | Effort to move |
|---|---|---|---|
| Device ingestion | IoT Core | IoT Hub | Medium, since devices need new certificates and a new endpoint |
| Functions | Lambda | Azure Functions | Low, handlers hold little provider code |
| Objects | S3 | Blob Storage | Low, copy from the archive |
| Records | DynamoDB | Cosmos DB | Medium, access patterns change |
| Event routing | EventBridge | Event Grid | Low |
| Queues | SQS | Service Bus | Low |
| Inference | Bedrock | Azure OpenAI | Low, the prompt moves with small changes |
| Keys | KMS | Key Vault | Low |

Activating Azure would be a planned migration, sitting outside the recovery objectives of the pilot.

Nothing is deployed on Azure, and the 100-hour scope holds no Azure code.

## 8. What would change this decision

| Event | Effect |
|---|---|
| The Bogota Local Zone opens with the needed services | Review moving latency-sensitive parts, with no change of provider |
| The regulator rules out the United States as a destination | Personal data moves to another region or provider, and this document is reviewed |
| A measured round trip breaks the alert budget | Region is reviewed |
| A provider retires a service in the design | The equivalence table limits the impact |

## 9. Assumptions and pending confirmations

| Item | Who confirms | Effect if it fails |
|---|---|---|
| The Federation accepts data outside Colombia | Federation | Region is reviewed |
| The adequacy status of the United States | Legal counsel | Contract clauses or destination change |
| Latency from a center to us-east-1 | First deployment | Region is reviewed only if it breaks the alert budget |

## Sources

- AWS Price List API for IoT Core in us-east-1.
- Azure Retail Prices API for IoT Hub in East US.
- AWS Local Zones locations page, which lists Bogota as announced.
- Microsoft list of Azure regions.
- AWS IoT Core transport security documentation.
