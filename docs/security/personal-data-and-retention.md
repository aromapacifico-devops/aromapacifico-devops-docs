# Personal data and retention

The platform collects the personal data it needs to operate the pilot and keeps operational records for five years.

## Classification

| Data | Subject | Class | Where it lives |
|---|---|---|---|
| Name, national ID, phone and address | Farmer | Personal | User pool and farm table |
| Name, national ID, phone and vehicle plate | Carrier | Personal | User pool and carrier table |
| Farm location and lot polygon | Farmer | Personal when tied to the farmer | Farm table and object storage |
| Carrier position in transit | Carrier | Personal | Position table and archive |
| Farm readings | Farm | Operational | Readings table and archive |
| Sack identifier and states | Sack | Operational | Sack table |
| Drone photos and flight logs | Farm | Operational, personal if a person appears | Object storage |
| Operator accounts | Staff | Personal | User pool and audit logs |

National ID is stored encrypted and never leaves the personal data tables.

## Retention

| Data | Active storage | Archive | Deletion |
|---|---|---|---|
| Readings | DynamoDB, 90 days | S3, to five years | Lifecycle rule at five years |
| Photos, maps and polygons | S3, 90 days | Glacier Instant Retrieval, to five years | Lifecycle rule at five years |
| Flight logs | S3, 90 days | Glacier Instant Retrieval, to five years | Lifecycle rule at five years |
| Sack history | DynamoDB, five years | None | Scheduled deletion at five years |
| Carrier positions | DynamoDB, 90 days | S3, to five years | Lifecycle rule at five years |
| Personal data | Active while the relationship lasts | Up to five years after it ends | Deletion or anonymization by request or at term |
| Audit logs | CloudWatch, 90 days | S3 in the log archive account, five years | Lifecycle rule at five years |

## Sack identifier rule

The sack identifier contains no national ID and no personal data, and it encodes neither the farm nor the farmer. Its format is described in the sack identity document.

## Objects that contain a person

The objects of the pilot show crops. When the person filter detects a person, the platform follows these steps.

1. The object moves to a restricted prefix and never reaches the inference service.
2. The case records that the object was withheld, and its state does not change.
3. The drone operator repeats the capture.
4. The withheld object is deleted after 30 days unless an incident requires it, and only the platform operator can read it.

## Transfer abroad

Personal data resides in the United States, since no region of the chosen provider exists in Colombia. Law 1581 of 2012 allows transfers to countries with an adequate level of protection, and otherwise through its exceptions, a declaration of conformity or the contract clauses of the regulator. The team could not confirm the current status of the United States on the regulator's list, so legal counsel must confirm it before production. The design assumes a data processing agreement with the provider, consent in the application's sign-up flow, and the model clauses of the regulator's External Circular 003 of 2025 if the list does not cover the destination.

Crop images sent to inference stay in the same region and hold no personal data, because the person filter runs first.
