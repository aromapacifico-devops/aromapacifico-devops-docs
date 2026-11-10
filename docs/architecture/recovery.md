# Recovery of the sack history

A sack event is the proof that a person held a sack at a place and a time, and it cannot be rebuilt from anything else. This document defines how the platform protects the sack history, how it restores it, and how it proves that the restore works. The objectives are a loss of at most 15 minutes of sack events and a public sack query back within 4 hours. The [custody chain](../traceability/custody-chain.md) document defines the events and their write path, and the [persistence and archive](persistence-and-archive.md) document defines how long each kind of data lives.

## Contents

1. Objectives
2. What can go wrong
3. Protection
4. Deployments that lose nothing
5. Restoring
6. Testing the restore
7. Cost
8. Options discarded
9. Assumptions and pending confirmations

### Terms used

| Term | Meaning in this document |
|---|---|
| RPO | Recovery point objective, the most data the platform may lose, measured in time |
| RTO | Recovery time objective, the time from the failure to a working service |
| Point-in-time recovery | Continuous backup of a table that restores it to any second of a window of up to 35 days |
| Restore point | The second to which the tables are restored |
| Sack tables | The two tables of the custody chain, one with the events and one with the current state of each sack |
| Replay | Computing the state of a sack again from its events |

## 1. Objectives

| Objective | Value | What it covers |
|---|---|---|
| RPO | 15 minutes | Sack events written to the platform |
| RTO | 4 hours | The public sack query |

The RTO applies to the public query only. Reception at the centers, the carrier application and the dashboards come back with the same restore, and the objective for them is the same time, with no separate commitment.

## 2. What can go wrong

| Failure | Effect | Response | Data lost |
|---|---|---|---|
| A zone of the region fails | The managed services keep running in the other zones | None | Nothing |
| A bad deployment | Requests fail or write wrong data | Rollback of the function to the previous version, and a restore if data was damaged | Nothing if only requests failed |
| The state table is damaged | Sacks show a wrong state | Replay the events, or restore both tables | Nothing, since the state comes from the events |
| A table is deleted or emptied by mistake | The query and the reception stop | Restore both tables to the same second | Events between the restore point and the failure |
| A key is disabled | Tables cannot be read | Enable the key again | Nothing |
| The region is lost | Everything stops | Rebuild from code, planned effort | Outside the objectives of the pilot |

## 3. Protection

**Point-in-time recovery on both tables.** The sack tables keep continuous backups for 35 days, the longest window. The latest restorable second is typically five minutes behind the present, so a restore to the latest point loses about 5 minutes, inside the objective of 15. A restore always creates a new table and leaves the source available while it runs. The two tables restore to the same second, since issued codes live only in the state table.

**Events cannot change.** The role of the domain function can insert events and read them, and no application role can update or delete one. Only the retention job, which acts on sacks five years old, deletes events. Damage to the history can come only from a failure of the table itself, or from a person with administrative rights, which the audit design records.

**The state is derived.** The state of a sack is the replay of its events. If only the state table is damaged, the platform recomputes it from the events and loses nothing. Only the codes issued and not yet used need the restore, since they exist nowhere else.

**The sender keeps what is not confirmed.** A carrier phone or a center application deletes a custody event only after the platform answers that it is stored. An event written in the 5 minutes before a failure was already confirmed, so the sender no longer holds it. An event that was not confirmed is sent again after the restore, and the idempotency key answers that it is stored or writes it once.

**Deletion protection.** Production tables carry deletion protection, so a mistaken change cannot remove them. When a table with point-in-time recovery is deleted anyway, DynamoDB keeps a final snapshot for 35 days at no charge.

**Alarms.** The platform alarms on failed writes to the sack tables, on throttled requests, on the state of the encryption key, and on a table that has point-in-time recovery turned off.

## 4. Deployments that lose nothing

No deployment replaces a sack table. The plan of every change to production is read before approval, and a plan that deletes or replaces one of the two tables is rejected. Deletion protection stops the change even if the check is missed.

A function deployment can interrupt a request. The sender receives an error and keeps the event, and the repeat finds the event stored or writes it once, as the idempotency design guarantees. No event depends on a response that arrived.

## 5. Restoring

A restore follows these steps.

| Step | Action | Time budget |
|---|---|---|
| 1 | The alarm fires and a person confirms the failure | 15 minutes |
| 2 | The platform operator and a reviewer agree on the restore point and approve the restore | 30 minutes |
| 3 | Both tables restore to the same second, under new names | 90 minutes |
| 4 | Point-in-time recovery, alarms, tags and permissions are set again on the new tables through the infrastructure code | 30 minutes |
| 5 | Counts of events and sacks are compared with the damaged tables, and a sample of sacks is replayed | 30 minutes |
| 6 | The function reads the new table names, and the public query is checked | 15 minutes |
| | Total | 3 hours 30 minutes |

The budget leaves 30 minutes of margin. The time of step 3 is the one that AWS does not promise. It depends on the amount of data and the number of secondary indexes, and the restore can leave out secondary indexes, which makes it faster. The restore test measures it.

A restore does not carry over time to live, point-in-time recovery, alarms, tags, permissions or stream settings, which is why step 4 exists. The infrastructure code takes the table names as inputs, so a restored table is brought under the code by changing the name, importing the table and applying the plan.

The restore point is the second before the damage. When the table is lost, it is the latest restorable second. In both cases the events between the restore point and the failure that their senders had already seen confirmed are not in the restored tables.

## 6. Testing the restore

The restore is tested in the test environment before the pilot and then every quarter, with the following procedure.

| Step | Check | Passes when |
|---|---|---|
| 1 | Write a known set of events through the API | Every event is stored once |
| 2 | Restore both tables to a second after the writes | The restore ends and both tables are active |
| 3 | Compare counts of events and sacks | They equal the source at that second |
| 4 | Replay every sack and compare states | Every state equals the stored one |
| 5 | Repeat the writes of step 1 | Every answer is "repeated" and nothing is written |
| 6 | Measure the time of each step | The total stays under 4 hours |

The result, with the measured times, is stored as evidence in the pull request that closes each test. The first test waits for the environment that holds the sack tables, so this document states the procedure and the budget, and the measurements replace the budget once they exist.

## 7. Cost

Rates come from the AWS Price List API for us-east-1. Continuous backup costs USD 0.20 per GB a month, and a restore costs USD 0.15 per GB restored.

| Item | Calculation | Cost, USD |
|---|---|---|
| Continuous backup, first harvest month | About 0.3 GB × 0.20 | 0.06 a month |
| Continuous backup, end of year five, upper bound | 16.2 GB × 0.20 | 3.24 a month |
| One restore of both tables at that size | 16.2 GB × 0.15 | 2.43 each time |

A quarterly test costs under USD 3 each time, and a real restore costs the same.

## 8. Options discarded

| Option | For | Against | Result |
|---|---|---|---|
| Point-in-time recovery only | Covers the objectives at a few dollars a month | No restore point older than 35 days | **Chosen** |
| Monthly backups kept for 12 months | Restore to a month long gone | Up to about USD 19 a month at the end of year five, since each copy is the size of the tables, and replay already repairs the state | Discarded |
| Copy of the backups to another Region | Survives the loss of the region | The region loss is outside the objectives of the pilot, and the cost doubles storage | Discarded |
| Export of every event to S3 | A second copy of the history | A second path to keep in step, for a risk that immutability and point-in-time recovery already cover | Discarded |

If the Federation extends the objectives to the loss of a region, the second option and the copy to another Region become the path to follow.

## 9. Assumptions and pending confirmations

| Item | Who confirms | Effect if it fails |
|---|---|---|
| A restore of both tables ends within 90 minutes | First restore test | The budget of step 3 grows, and the margin shrinks or disappears |
| A restore point older than 35 days is not needed | Federation | Monthly backups are added at the cost shown above |
| The loss of a region stays outside the objectives | Federation | A copy to another Region is added |
| A person with administrative rights is the only way to damage the history | Team, with the audit design | A second copy of the events is added |
| The infrastructure code takes the table names as inputs | Team, when the module is written | The switch of step 6 needs another mechanism |

## Sources

- Amazon DynamoDB documentation on point-in-time recovery, on restoring a table and on deleting a table with recovery enabled.
- AWS Price List API for DynamoDB in us-east-1.
