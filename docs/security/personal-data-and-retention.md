# Personal data and retention

The platform collects the personal data it needs to operate the pilot, keeps operational records for five years and deletes them after that. This document classifies the data, defines retention and deletion, states the rule for the sack identifier, sets the treatment of objects that show a person, and explains the transfer of data abroad.

## Contents

1. Principles
2. Classification
3. Retention, archive and deletion
4. Sack identifier rule
5. Who sees what
6. Objects that contain a person
7. Rights of the data subject
8. Transfer abroad
9. Cost of retention
10. Assumptions and pending confirmations

### Terms used

| Term | Meaning in this document |
|---|---|
| Data subject | The person the data refers to, such as a farmer or a carrier |
| Personal data | Data that identifies or can identify a person |
| Controller | Who decides why data is processed, here the Federation |
| Processor | Who handles data on behalf of the controller, here the cloud provider |
| Transfer | Sending personal data abroad to another controller |
| Transmission | Sending personal data abroad to a processor acting under contract |

---

## 1. Principles

| Principle | How it applies |
|---|---|
| Minimum data | The platform asks only what operating the pilot needs |
| Stated purpose | Consent names traceability, alerts and the drone service |
| Separation | Personal data lives apart from operational data, joined by an internal identifier |
| Limited exposure | Each role sees only its own view |
| Defined end | Every class of data has a deletion rule |

## 2. Classification

| Data | Subject | Class | Where it lives |
|---|---|---|---|
| Name, national ID, phone, address | Farmer | Personal | User pool and farm table |
| Name, national ID, phone, vehicle plate | Carrier | Personal | User pool and carrier table |
| Farm location and lot polygon | Farmer | Personal when tied to the farmer | Farm table and object storage |
| Carrier position in transit | Carrier | Personal | Position table and archive |
| Farm readings | Farm | Operational | Readings table and archive |
| Sack identifier and states | Sack | Operational | Sack table |
| Name of who received a sack at the port | Port receiver | Personal | Sack event table |
| Drone photos and flight logs | Farm | Operational, personal if a person appears | Object storage |
| Operator accounts and logs | Staff | Personal | User pool and audit logs |

National ID is stored encrypted, stays out of every response, and is never used as a key.

## 3. Retention, archive and deletion

Five years applies to readings, photos, flights, sack history and personal data.

| Data | Active storage | Archive | Deletion |
|---|---|---|---|
| Readings | DynamoDB, 90 days | S3, to five years | Lifecycle rule at five years |
| Photos, maps and polygons | S3 Standard, 90 days | Glacier Instant Retrieval, to five years | Lifecycle rule at five years |
| Flight logs | S3 Standard, 90 days | Glacier Instant Retrieval, to five years | Lifecycle rule at five years |
| Sack history | DynamoDB, five years | None | Scheduled deletion at five years |
| Carrier positions | DynamoDB, 90 days | S3, to five years | Lifecycle rule at five years |
| Positions queued on the carrier phone | Encrypted application store, 24 hours at most | None | Deleted on confirmation or at 24 hours |
| Personal data | While the relationship lasts | Five years after it ends | Deletion or anonymization at term or by request |
| Audit logs | CloudWatch, 90 days | S3 in the log archive account, five years | Lifecycle rule at five years |

The pilot sets five years for personal data and gives no starting point. Every other record counts from the day it is written, and that clock does not fit a person who is still active, since deleting the identity of a farmer who keeps delivering coffee would break the service. Personal data therefore counts from the end of the relationship, which is the closing of the account or the last delivery. The term is a limit from that date, and a request from the person can shorten it.
| Objects with a person | Restricted prefix, 30 days | None | Lifecycle rule at 30 days |

Glacier Instant Retrieval was chosen over slower archive classes because a case review or a claim may need a photo at once. At USD 0.004 per GB a month against USD 0.023 for S3 Standard, it costs about 83 percent less and keeps retrieval in milliseconds. Objects stay in Standard for 90 days, which is also the minimum storage period of that class, so no early deletion charge applies.

## 4. Sack identifier rule

The sack identifier holds no national ID and no personal data, and it encodes neither the farm nor the farmer. A lookup on the platform is the only link between code and record.

## 5. Who sees what

| Field | Buyer | Center | Carrier | Farmer |
|---|---|---|---|---|
| Origin, at department level | Yes | Yes | No | Yes |
| Process dates, state, drying variables | Yes | Yes | No | Yes |
| Trip | No | Yes | Own | No |
| Farm and lot | No | Yes | No | Own |
| Farmer identity | No | No | No | Own |

## 6. Objects that contain a person

The objects of the pilot show crops. A drone may still capture a worker or a neighbor, and such an object must not reach an inference service.

| Step | Action |
|---|---|
| 1 | Rekognition DetectLabels runs on every image before any analysis |
| 2 | If a person appears above the confidence threshold, the object moves to the restricted prefix |
| 3 | The case records that the object was withheld, and its state does not change |
| 4 | The drone operator repeats the capture |
| 5 | The withheld object is deleted after 30 days, unless an incident requires it |

Only the platform operator can reach the restricted prefix, and each access is audited.

The confidence threshold starts at a low value, because a false positive costs a repeated photo while a false negative sends a person to inference. Review with real images must set the final value.

## 7. Rights of the data subject

| Right | How it is met |
|---|---|
| Know the data held | Request through the Federation, answered from the farm or carrier record |
| Update or correct it | Application or Federation request |
| Withdraw consent or ask for deletion | Personal data is deleted or anonymized. Operational records stay, with the link removed |

Traceability survives deletion, since a sack keeps its history and loses the person behind it.

## 8. Transfer abroad

Personal data resides in the United States, since neither the chosen provider nor the alternatives have a region in Colombia.

Article 26 of Law 1581 of 2012 allows transfers to countries with an adequate level of protection, and otherwise through the exceptions of the law, a declaration of conformity from the regulator, or contracts. The regulator's External Circular 003 of 2025 adopted model clauses for transfers and transmissions.

The team could not confirm the current status of the United States on the regulator's list. Sources disagree, and the regulator is updating that list. Legal counsel must confirm it before production. The design assumes three measures that hold under either answer.

| Measure | Purpose |
|---|---|
| Data processing agreement with the provider | Frames the operation as a transmission to a processor |
| Consent in the sign-up flow, naming the destination | Supports the transfer with the authorization of the data subject |
| Model clauses, if the list does not cover the destination | Meets the regulator's instruction |

Crop images sent to inference hold no personal data, because the person filter runs first, and they stay in the same region when the model runs in region.

## 9. Cost of retention

The pilot produces about 9,000 images in a harvest month and about 1,500 in a normal month. With 3 MB per image, four harvest months and eight normal months give about 144 GB a year, so about 720 GB after five years.

| Item | Monthly cost at the end of year five, USD |
|---|---|
| 720 GB in Glacier Instant Retrieval | 2.88 |
| Readings archive, under 10 GB | Under 0.05 |

Five years of retention stays under USD 3 a month, so retention does not need trimming to save money.

## 10. Assumptions and pending confirmations

| Item | Who confirms | Effect if it fails |
|---|---|---|
| Adequacy status of the United States | Legal counsel | Model clauses apply, or personal data moves |
| The Federation acts as controller | Federation | Contracts change |
| The five years of personal data start when the relationship ends | Federation and legal counsel | Data of active farmers and carriers needs another legal basis to stay past five years |
| Images average 3 MB | Drone supplier | Storage cost scales linearly |
| The person filter confidence threshold | Review with real images | More repeated flights, or more risk |

## Sources

- Law 1581 of 2012, article 26.
- External Circular 003 of 2025, Superintendence of Industry and Commerce.
- AWS Price List API for S3 in us-east-1.
