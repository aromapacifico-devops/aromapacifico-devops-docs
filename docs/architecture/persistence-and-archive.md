# Persistence and archive for five years

The Federation needs the history of every sack, reading, photo and flight for five years, so the pilot can be audited. This document defines the layers where each kind of data lives, why they were chosen, how archived data is read and restored, and how each layer deletes data when the five years end. It covers the retention of operational data. The [personal data and retention](../security/personal-data-and-retention.md) document covers the rules for people, and the [custody chain](../traceability/custody-chain.md) document covers the write path of the sack events.

## Contents

1. Layers by kind of data
2. Why these layers
3. Reading archived data
4. Restoring
5. Deleting at five years
6. What fails and what happens
7. Cost
8. Assumptions and pending confirmations

### Terms used

| Term | Meaning in this document |
|---|---|
| Active layer | The store the application reads and writes during normal work |
| Archive layer | The cheaper store that holds data the application no longer reads daily |
| TTL | Time to live, the automatic expiry of a table item at a timestamp stored in the item |
| Lifecycle rule | A rule of the object store that moves or deletes objects by age |
| Glacier Instant Retrieval | An archive storage class that returns objects in milliseconds |
| Point-in-time recovery | Continuous backup of a table that restores it to any second in the last 35 days at most |
| Noncurrent version | An older version of an object in a bucket with versioning |

## 1. Layers by kind of data

| Data | Active layer | Archive layer | Deletion at five years |
|---|---|---|---|
| Farm readings | Readings table, 90 days | Parquet files in S3, five years | Lifecycle rule on the files |
| Alerts | Alerts table, five years | None | Service process |
| Versions of the alert ranges | Ranges table, five years | None | Service process |
| Carrier positions | Positions table, 90 days | Parquet files in S3, five years | Lifecycle rule on the files |
| Sack events and sacks | Both tables, five years | None | Service process, one sack at a time |
| Cases of cultivation alerts and drone missions | Case table, five years | None | Service process |
| Photos, maps and polygons | S3 Standard, 90 days | Glacier Instant Retrieval, to five years | Lifecycle rule |
| Flight logs | S3 Standard, 90 days | Glacier Instant Retrieval, to five years | Lifecycle rule |
| Audit logs | CloudWatch, 90 days | S3 in the log archive account, with object lock, five years | Lifecycle rule after the lock ends |

Objects that show a person leave the active layer sooner, since they are deleted 30 days after they are withheld, as the personal data document defines.

## 2. Why these layers

**Tables hold what the application reads, and files hold what reports read.** The application shows a farmer the recent history of a farm, so the readings and positions of the last 90 days sit in a table with automatic expiry. Older readings are read by reports, which filter a period and aggregate, and that is the work for which Parquet files and a query engine are cheap. The telemetry design explains this split with its alternatives.

**Sack history stays whole in its tables for five years.** The state of a sack comes from replaying all of its events, and a public query reads the history of any sack on demand, so a sack with part of its events elsewhere would need a second read path and a second replay. Two alternatives were compared at the volume of the pilot.

| Option | For | Against | Result |
|---|---|---|---|
| Keep sacks and events in the tables for five years | One read path, replay always complete | Table storage grows to about 16 GB, USD 4 a month | **Chosen** |
| Table class for infrequent access | USD 0.10 per GB a month instead of USD 0.25, about USD 2.40 a month less | Requests cost about 25 percent more, USD 0.78 per million writes against USD 0.625, for a saving too small to matter | Discarded |
| Export closed sacks to S3 and delete them from the tables | Smaller tables | A second read path, a replay that depends on two stores, and a restore that must rejoin them | Discarded |

The size comes from the volume of the custody chain. A harvest month brings up to 252,000 events and 36,000 sacks. If every month of the year had that load, a year would hold 3,024,000 events of about 1 KB, which is 3.0 GB, and 432,000 sacks of about 0.5 KB. Five years of that upper bound hold 15.1 GB of events and 1.1 GB of sacks. Real use is lower, since harvest lasts only part of the year.

**Photos and flight logs move to Glacier Instant Retrieval after 90 days.** A case review or a claim may need a photo at once, and this class returns an object in milliseconds. It costs USD 0.004 per GB a month against USD 0.023 for S3 Standard, and 90 days is also its minimum storage period, so the move after 90 days incurs no early deletion charge. Slower classes were discarded because a review would wait hours for a photo.

**Small objects stay in S3 Standard.** S3 does not move objects smaller than 128 KB to another class by default, since the cost of the transition request can exceed the savings. Photos average 3 MB and move. Polygon files and flight logs can be smaller than 128 KB, and they stay in S3 Standard until deletion. Their weight is a few kilobytes each, so the saving of a size filter would not repay its transition requests.

## 3. Reading archived data

| Data | Who reads | How | Time to the first byte |
|---|---|---|---|
| Readings, positions and alerts older than 90 days | Federation analysts and the pilot report | Athena queries over the Parquet files, in a workgroup with a limit on the data each query may scan | Seconds |
| Photos, maps, polygons and flight logs older than 90 days | Platform operator and the reviewer of a case | The platform checks the role and returns a link that expires, which reads the object | Milliseconds |
| Sack history, alerts, ranges and cases | Roles of the access matrix | The same API as for recent data, since the tables hold five years | Milliseconds |
| Audit logs older than 90 days | Security role | Read-only access to the log archive account | Seconds |

Reading an archived photo costs USD 0.03 per GB retrieved. Reading a full archive of readings costs little, since Athena charges USD 5 per TB scanned and the readings archive stays under 10 GB, which makes a full scan cost USD 0.05.

Reports filter by the time of measurement and scan one extra day, because a reading that waited in a buffer falls in the partition of the day it arrived.

## 4. Restoring

| What was lost | Source of the restore | How | Reach |
|---|---|---|---|
| A reading expired from the table | The Parquet archive | Query through Athena, with no restore step | Five years |
| A table damaged or emptied by mistake | Point-in-time recovery | Restore to a new table and switch the application to it | 35 days |
| Sacks and events | Point-in-time recovery of both tables, to the same second | Restore both tables together, since issued codes live only in the sacks table | 35 days |
| An object overwritten or deleted by mistake | Previous version in the bucket | Remove the delete marker or copy the previous version back | 30 days after the change |
| An archived photo | Glacier Instant Retrieval | Read the object directly, with no restore request | Five years |

Point-in-time recovery reaches back 35 days at most, and the tables expire or delete data on other schedules, so a restore never brings back what the retention rules already removed on purpose. The backup schedule that restores points older than 35 days belongs to the recovery design of the sack events.

Retrieving the whole photo archive after five years, about 720 GB, would cost 720 × USD 0.03 = USD 21.60 once, which is the figure to use when planning an audit that reads every object.

## 5. Deleting at five years

Deletion is as important as retention. Keeping personal data past its term is a fault of its own, and keeping any record longer than the pilot allows is a cost with no use.

**Readings and positions in the tables.** Each item carries an expiry timestamp in seconds, 90 days after its measurement or capture, and the table deletes it by itself. DynamoDB deletes expired items within a few days of their expiry, without using write capacity, so for a short time an expired item can still appear in a result. Every query on these tables filters out items whose timestamp has passed.

**Files in S3.** The buckets have versioning, so deleting an object only adds a delete marker and leaves the data in a noncurrent version. Each lifecycle configuration therefore holds four rules.

| Rule | Value | Effect |
|---|---|---|
| Expire the current version | 1,826 days after creation | Five years, counting a leap day |
| Expire noncurrent versions | 30 days after they become noncurrent | The data itself disappears |
| Remove expired delete markers | Always | No marker is left alone in the bucket |
| Abort incomplete uploads | 7 days | Parts of failed uploads do not stay |

S3 removes expired objects asynchronously, and the removal can come a short time after the date. The bucket does not charge for an object once it has expired. The audit bucket uses object lock, and lifecycle rules act on its objects only after the lock ends.

**Sacks, events, alerts, ranges and cases.** The sack events table accepts inserts only, so no function of the platform may delete from it, and a time-to-live attribute does not fit either. An event cannot be changed after it is written, so its expiry cannot move when later events arrive, and deleting the oldest events of a sack while later ones remain would break the replay that gives its state. Deleting the whole sack at one moment is the only way to keep every sack either complete or absent.

A scheduled job does this work under its own role, which no API function can assume.

| Step | Action |
|---|---|
| 1 | Once a day, the job reads the sacks whose deletion date has passed, up to a limit for each run |
| 2 | For each sack it reads the events, and checks that the version and the deletion date are those it read |
| 3 | It deletes the events in groups, then the sack, with a condition on the version, so a sack that received a late event is skipped |
| 4 | It records the run in the audit log, with the number of sacks deleted and the range of their dates, and without sack codes |

The deletion date of a sack is the arrival of its latest event plus five years, and the write path sets it in the same transaction that stores the event. A code issued and never used counts from the day it was issued. If the job stops in the middle of a sack, the sack still has a past deletion date, so the next run finishes it. Alerts, ranges and cases follow the same job with the date of their latest change.

A limit on the sacks of each run keeps a faulty date from deleting much in one day. Reaching that limit raises an alarm. Point-in-time recovery restores a mistaken deletion within 35 days.

**Personal data.** Deletion of people follows the term and the requests that the personal data document defines. The job above does not touch the records of farmers and carriers, which keep their own process.

## 6. What fails and what happens

| Failure | Effect | Response |
|---|---|---|
| The deletion job fails | Records stay beyond five years for a day | The next run picks them up, and an alarm warns after two failed runs |
| The job deletes too much | Sacks removed before their term | The limit per run caps the damage, and a restore within 35 days brings them back |
| A lifecycle rule is missing or misconfigured | Objects stay beyond five years, with cost | A check in the deployment pipeline reads the rules, and the storage metrics show the age of the oldest object |
| Expired items still appear after their time | An old reading shows in a result | Queries filter on the expiry timestamp |
| A late event reaches a sack already deleted | The platform refuses the code as unknown | Nothing, since five years passed with no event |
| An archived photo is needed in bulk | Retrieval cost and time | Read it by object, at USD 0.03 per GB |

## 7. Cost

Calculated from the AWS price list for us-east-1, at the end of year five and with the upper bound of the sack history.

| Item | Calculation | Monthly cost, USD |
|---|---|---|
| Sacks and events in DynamoDB | 16.2 GB × USD 0.25 | 4.05 |
| Photos and flight logs in Glacier Instant Retrieval | 720 GB × USD 0.004 | 2.88 |
| Readings and positions archive in S3 | Under 10 GB | Under 0.05 |
| **Total** | | **About 7** |

Five years of retention costs about USD 7 a month at its peak, so no part of it needs trimming for savings. The storage of the first 25 GB of a DynamoDB account carries no charge, and the table above leaves that allowance out to show the cost without it.

## 8. Assumptions and pending confirmations

| Item | Who confirms | Effect if it fails |
|---|---|---|
| A sack and its events are deleted together, five years after the latest event | Federation and legal counsel | A deletion by the date of each event would need a second storage design for the history of a sack |
| An event averages 1 KB in the table, and a sack 0.5 KB | First events written in the test environment | Table storage and its cost change in proportion |
| Photos average 3 MB, and 144 GB are added each year | Drone supplier | Archive storage and the cost of a full retrieval change in proportion |
| A recovery within 30 days is enough for objects changed by mistake | Team | The noncurrent window changes, and storage grows with it |
| The scheduled job and its role are built in the first plan of the infrastructure code | Team | The deletion stays manual until they exist |

## Sources

- AWS Price List API for DynamoDB, S3 and Athena in us-east-1.
- Amazon DynamoDB documentation on time to live and point-in-time recovery.
- Amazon S3 documentation on lifecycle transitions, expiration and versioning.
