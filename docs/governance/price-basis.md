# Price basis of the cost estimate

Every cost in the platform documents comes from a price, a region, a currency, an exchange rate and a tax treatment. This document fixes those five choices in one place, lists the dated source of each price family, and states what could not be verified, so the cost estimate can be read, repeated and challenged. It sets the basis only. The monthly figures themselves belong to the cost estimate.

## Contents

1. Basis of the estimate
2. Exchange rate
3. Taxes
4. Cloud prices
5. Connectivity prices
6. Hardware references
7. Cost assumptions
8. Assumptions and pending confirmations

### Terms used

| Term | Meaning in this document |
|---|---|
| TRM | Tasa Representativa del Mercado, the official COP per USD rate that the financial regulator publishes each day |
| On-demand price | The public list price, with no commitment, credit or discount |
| IVA | Colombian value added tax |
| Price list | The file AWS publishes with the price of each service by region |
| Reference price | A published price that gives the order of magnitude and is not a quote |

## 1. Basis of the estimate

| Choice | Value | Reason |
|---|---|---|
| Reporting currency | USD | The cloud bills in USD, and most hardware is priced in USD |
| Cloud region | US East (N. Virginia), `us-east-1` | The chosen region of the platform |
| Cloud price type | On-demand list price | No commitment, credit or discount is assumed, which gives a ceiling |
| Taxes | Not included | See section 3 |
| Month | 730 hours for hourly items and 30 days for volumes | Keeps hourly and volume figures consistent |
| Retrieval date | 10 November 2026 | All prices in this document were read that day |

## 2. Exchange rate

Prices in pesos convert at the TRM of the retrieval date.

| Measure | COP per USD |
|---|---|
| TRM on 10 November 2026 | 3,269.88 |
| Lowest of the last 120 days | 3,048.12 |
| Highest of the last 120 days | 3,796.87 |
| Average of the last 120 days | 3,307.40 |

The 120 days run from 8 May to 10 November 2026. The source is the open data set of the Superintendencia Financiera de Colombia on the national open data portal. Fixing the rate is a decision of the Federation, so the estimate carries the sensitivity too. A stronger peso raises the dollar cost of every price quoted in pesos.

| Link, three centers | Monthly price per center, COP | At 3,048.12, USD | At 3,269.88, USD | At 3,796.87, USD |
|---|---|---|---|---|
| Dedicated, 80 to 120 Mbps | 250,000 to 350,000 | 246 to 345 | 229 to 321 | 198 to 277 |
| Shared business fiber | 70,000 to 150,000 | 69 to 148 | 64 to 138 | 55 to 119 |

## 3. Taxes

The general IVA rate in Colombia is 19 percent under article 468 of the Estatuto Tributario, according to the tax authority's published opinions. The estimate reports every figure before tax, so each one converts with a single multiplier. A charge of USD 100 becomes USD 119 if IVA applies in full.

Whether AWS charges IVA to the Federation's account is not confirmed. The tax settings of the billing account and the tax adviser of the Federation settle it. The same applies to the IVA on the peso prices of connectivity, since the operator reference does not say whether its figures include it, and to the import duties and IVA on the hardware that arrives from abroad.

## 4. Cloud prices

Prices come from the AWS Price List API, in files of the form `https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/<code>/current/us-east-1/index.json`. Each file carries its publication date. The last column lists the rates re-read from the file on the retrieval date. A service without rates there is read when the estimate uses it.

| Service | Code | Published | Rates re-read, USD |
|---|---|---|---|
| IoT Core | `AWSIoT` | 3 October 2026 | Messages 1.00 per million, rules triggered 0.15 per million, actions executed 0.15 per million |
| Lambda | `AWSLambda` | 30 October 2026 | Requests 0.20 per million |
| SQS | `AWSQueueService` | 11 September 2026 | Standard requests 0.40 per million |
| SNS | `AmazonSNS` | 4 November 2026 | |
| Data Firehose | `AmazonKinesisFirehose` | 4 November 2026 | Ingestion 0.029 per GB in the first tier |
| API Gateway | `AmazonApiGateway` | 13 October 2026 | HTTP API 1.00 per million in the first 300 million |
| VPC | `AmazonVPC` | 5 November 2026 | VPN connection 0.05 an hour, interface endpoint 0.01 an hour |
| KMS | `awskms` | 8 November 2026 | 1.00 a month per customer managed key |
| Secrets Manager | `AWSSecretsManager` | 11 September 2026 | 0.40 a month per secret |
| WAF | `awswaf` | 14 September 2026 | Web ACL 5.00 a month, rule 1.00 a month |
| CloudWatch | `AmazonCloudWatch` | 4 November 2026 | |
| DynamoDB | `AmazonDynamoDB` | 5 November 2026 | Writes 0.625 per million, reads 0.125 per million, storage 0.25 per GB a month after 25 GB |
| S3 | `AmazonS3` | 9 November 2026 | Standard 0.023 per GB a month, Glacier Instant Retrieval 0.004 per GB a month and 0.03 per GB retrieved |
| Athena | `AmazonAthena` | 11 September 2026 | 5.00 per TB scanned |
| Cognito | `AmazonCognito` | 20 October 2026 | |
| EventBridge | `AWSEvents` | 8 November 2026 | |
| Bedrock | `AmazonBedrock` | 6 November 2026 | |
| Rekognition | `AmazonRekognition` | 11 September 2026 | |

Every rate re-read matches the one used in the platform documents. Bedrock bills by model, so the inference estimate reads the rate of its model and records it.

## 5. Connectivity prices

**Links of the collection centers.** The reference is a Colombian operator article published on 19 February 2026, which gives approximate monthly prices in pesos.

| Link | Monthly price, COP | What the source says |
|---|---|---|
| Dedicated, 80 to 120 Mbps | 250,000 to 350,000 | Availability of about 99.6 percent under the service agreement, and no committed rate figure |
| Shared business fiber | 70,000 to 150,000 | Depends on speed and on bundling with other services |

The source calls its figures indicative and does not say whether they include IVA. A quote from an operator with coverage in each municipality replaces them.

**Mobile data of the farm nodes.** No Colombian operator publishes a price for machine connections. A multi-operator IoT connectivity provider lists data from EUR 0.0025 per MB and covers two Colombian networks, and it does not publish a monthly fee per SIM or the price of the card. At 5.5 MB a month for a node, data alone costs about EUR 0.014, so 200 nodes cost about EUR 2.75 a month. The fee per SIM is the figure that decides the cost, and only a quote provides it.

## 6. Hardware references

Only one hardware listing could be read directly on the retrieval date.

| Item | Reference | Price as listed | Notes |
|---|---|---|---|
| Outdoor LoRaWAN gateway | RAK7289 V2 WisGate Edge Pro at a European retailer, offered with 8 or 16 channels and several backhaul options | EUR 537.76 for the listing | Includes German VAT of 19 percent, shipping extra. The variant for the Colombian frequency plan is not fixed |

No verified listing price could be read for the cellular module of the node, the multiparameter probe, the solar kit and the spraying drone, since the listings found either did not open or showed prices in other currencies and without a stated tax. The hardware and drone estimates request quotes for those items and record them with their date.

## 7. Cost assumptions

| Assumption | Value | Used by |
|---|---|---|
| Cloud prices | On-demand, `us-east-1`, no credits | Every cloud line |
| Exchange rate | 3,269.88 COP per USD | Every price in pesos |
| Taxes | Excluded | Every line |
| Month | 730 hours, 30 days | Hourly and volume lines |
| Data per node | 5.5 MB a month | Mobile data |

## 8. Assumptions and pending confirmations

| Item | Who confirms | Effect if it fails |
|---|---|---|
| The TRM of the retrieval date represents the estimate period | Federation | Peso prices move with the rate, as the sensitivity table shows |
| IVA applies to the AWS account and to connectivity | Federation and tax adviser | Costs rise by up to 19 percent |
| Operator prices in pesos include IVA or not, as the quote says | Operators | Same effect on the connectivity lines |
| Import duties and IVA on hardware | Federation and customs agent | Hardware cost rises by the duties and IVA |
| Prices in the operator article hold for the municipalities of the pilot | Operator quotes | The connectivity lines change |
| The fee per SIM of the IoT connectivity provider | Quote | Mobile data cost changes, and the fee may exceed the data cost |

## Sources

- Superintendencia Financiera de Colombia, TRM data set on the national open data portal, `datos.gov.co`.
- AWS Price List API, by service code in section 4.
- Estatuto Tributario, article 468, as applied in the opinions of the tax authority published in its legal compilation.
- Edatel, article on dedicated and shared business internet, published 19 February 2026.
- Onomondo, pricing page.
- IoT-shop, RAK7289 V2 WisGate Edge Pro listing.
