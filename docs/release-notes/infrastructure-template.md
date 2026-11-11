# Infrastructure release note template

Copy this template into a Release note issue of the infrastructure repository for every production deploy of the platform pipeline. Replace each text in angle brackets and keep every heading. The [change policy](README.md) explains the kinds of change, the windows, the approval and the notice. A filled example is in [examples/infrastructure-telemetry-ingestion-1.0.1.md](examples/infrastructure-telemetry-ingestion-1.0.1.md).

```markdown
# <Area> <module version or short name>, <short description of the change>

| Field | Value |
|---|---|
| Kind of change | <Standard, low impact or incident> |
| Area | <Network, center links, firewall, ingestion, drone path, security, or another root or module> |
| Pull request | <Link to the merged pull request of the infrastructure repository> |
| Module versions | <Each module whose tag changes, from the current tag to the new one> |
| Test deployment | <Link to the deploy of test from the same commit, with the smoke test result> |
| Written by | <Team member> |
| On duty during the window | <Team member> |

## What changes

<What the platform does differently after the apply, in terms a reader outside the team understands. Say why the change is needed.>

| Plan of production | Value |
|---|---|
| Summary | <N to add, N to change, N to destroy> |
| Resources changed in place | <Each resource address and the attribute that changes> |
| Resources replaced or destroyed | <Each one, or none> |

## Window

| Field | Value |
|---|---|
| Date | <Day of the week and date> |
| Start and end, Bogota time | <Start> to <end> |
| Harvest week | <Yes or no, from the harvest calendar> |

## Impact

| Field | Value |
|---|---|
| Who notices | <Farmers, centers, carriers, buyers, the Federation, or nobody> |
| Expected interruption | <None, or which service stops, for how long and for whom> |
| Data | <Whether any table, bucket or stream is replaced, emptied or moved> |
| Service level objectives affected | <Which objective, and how much of its error budget is left> |
| Main risk | <What goes wrong if the apply fails halfway, and how it shows> |

## Approval

| Field | Value |
|---|---|
| Approver | <Team member> |
| Production run | <Link to the deploy run in the protected prod environment> |
| What the approver checked | The plan summary of the same run, kind of change, window and notice, the test deployment, the rollback |

## Notice to the Federation

| Field | Value |
|---|---|
| Sent to | Change contact of the Federation |
| Notice sent | <Date, 2 working days before for a standard change, 1 for low impact, at the start for an incident> |
| Summary sent | <Date and result> |

## Rollback

| Field | Value |
|---|---|
| Trigger | <What the person on duty watches after the apply, and the threshold that sends the change back> |
| Steps | A pull request points the environment to <previous module tag or previous value>, then the deploy runs for production with approval |
| Time to go back | <One plan and apply, with the measured duration of the apply in test> |
| What does not go back | <Data written while the change was live, or a resource that a replacement already deleted> |

## Verification after the change

<The check that shows the change works in production, with the command and its expected result, and the next drift run that must report no difference.>
```
