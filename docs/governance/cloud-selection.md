# Cloud selection

The pilot runs on AWS in us-east-1, with Azure East US prepared as a second cloud that holds no running resources.

## Comparison

| Criterion | AWS us-east-1 | Azure East US |
|---|---|---|
| IoT ingestion | IoT Core with MQTT over TLS 1.3, per-device X.509 identity and a rules engine | IoT Hub with per-device identity. One S1 or B1 unit handles 400,000 messages a day |
| LoRaWAN | IoT Core for LoRaWAN offers a managed network server | No managed network server identified |
| Event-driven functions | Lambda, triggered by S3, SQS and EventBridge | Functions, triggered by Blob Storage and Event Grid |
| Managed inference | Bedrock multimodal models and Rekognition | Azure AI services and Azure OpenAI |
| Object storage | S3, with lifecycle rules for five-year retention | Blob Storage, with lifecycle rules |
| Transactional database | DynamoDB with transactions and point-in-time recovery | Cosmos DB |
| Region and residency | Virginia, United States. No AWS region in Colombia | Virginia, United States. No Azure region in Colombia |
| Pricing model | Pay per message, with no provisioned unit. USD 1 per million messages in the published example | Provisioned units billed monthly |
| Team standards | The 26 infrastructure rules are written for AWS | Rules need adapting |

Azure list prices could not be read from the public pricing page, so this comparison uses the pricing model and leaves unit prices out. A quotation must come from the Azure calculator before any figure for that cloud is used.

## Why AWS

Pay-per-message pricing suits a load of about 324,000 messages in a harvest month. That is about 11,000 a day, far below the 400,000 a day of one provisioned hub unit, so most of that capacity would sit idle. The rest of the platform follows the same pattern, since nothing runs while no event arrives. The infrastructure rules also apply without adaptation, which protects the 100-hour plan.

## Residency and region

Data lives in us-east-1, in Virginia. Latency from the pilot's sites has not been measured and is not part of the justification. The alert budget of five minutes is wide compared with any expected round trip, and the first deployment should measure it.

The Bogota Local Zone is announced and unavailable. Its parent region is us-east-1, so this choice stays compatible with it.

Personal data leaves the country under every option evaluated. The personal data policy describes how that transfer is handled.

## Second cloud

The second cloud exists to keep an exit available without paying for a copy of the platform.

| Prepared | Left out |
|---|---|
| Portable contracts, with MQTT topics and JSON messages | Running resources of any kind |
| Equivalence table between services, shown below | Replicated data |
| Object layout and event schemas documented | A network link between clouds |
| Recovery procedure from the S3 archive | Automatic failover |

| Function | AWS | Azure |
|---|---|---|
| Device ingestion | IoT Core | IoT Hub |
| Functions | Lambda | Azure Functions |
| Objects | S3 | Blob Storage |
| Records | DynamoDB | Cosmos DB |
| Event routing | EventBridge | Event Grid |
| Queues | SQS | Service Bus |
| Inference | Bedrock | Azure OpenAI |
| Keys | KMS | Key Vault |

Activating Azure means provisioning from these contracts and restoring the archive, a planned migration that sits outside the recovery objectives of the pilot.
