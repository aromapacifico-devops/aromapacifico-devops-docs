# Application release note template

Copy this template into a Release note issue of the application repository for every production release of function code. Replace each text in angle brackets and keep every heading. The [change policy](README.md) explains the kinds of change, the windows, the approval and the notice. A filled example is in [examples/application-ingestion-1.1.0.md](examples/application-ingestion-1.1.0.md).

```markdown
# <Repository> <version>, <short description of the change>

| Field | Value |
|---|---|
| Kind of change | <Standard, low impact or incident> |
| Pipeline | <Ingestion or flight object> |
| Functions and versions | <Each function, its current version in production and the version this release publishes> |
| Artifact | <Path in the artifact bucket and SHA-256 of each zip> |
| Test deployment | <Link to the successful test run of this version, with the validation hook and smoke test result> |
| Written by | <Team member> |
| On duty during the window | <Team member> |

## What changes

<What the new version does differently, in terms a reader outside the team understands. List the pull requests that the version contains. Say which functions keep their current version.>

## Window

| Field | Value |
|---|---|
| Date | <Day of the week and date> |
| Start and end, Bogota time | <Start> to <end> |
| Harvest week | <Yes or no, from the harvest calendar> |
| Release pace | Canary of 10 percent for 10 minutes, then all calls |

## Impact

| Field | Value |
|---|---|
| Who notices | <Farmers, centers, carriers, buyers, the Federation, or nobody> |
| Expected interruption | <None, or how long and for whom> |
| Data written differently | <New or changed fields, records or messages, and whether the previous version can still read them> |
| Service level objectives affected | <Which objective, and how much of its error budget is left> |
| Main risk | <What goes wrong if the version is faulty, and which alarm shows it> |

## Approval

| Field | Value |
|---|---|
| Approver | <Team member> |
| Production run | <Link to the run in the protected prod environment> |
| What the approver checked | Kind of change, window and notice, the test deployment, the rollback |

## Notice to the Federation

| Field | Value |
|---|---|
| Sent to | Change contact of the Federation |
| Notice sent | <Date, 2 working days before for a standard change, 1 for low impact, at the start for an incident> |
| Summary sent | <Date and result> |

## Rollback

| Field | Value |
|---|---|
| Automatic trigger | <The alarms CodeDeploy watches during the canary> |
| Manual trigger | <What the person on duty watches after the canary, and the threshold that sends the version back> |
| Steps | Run the production release workflow with version <previous version>. It moves the `live` alias back with the same approval |
| Time to go back | Seconds during the canary, about 2 minutes by hand |
| What does not go back | <Records, messages or files the new version already wrote, and why the previous version can still read them> |

## Verification after the change

<The check that shows the version works in production, with the command or query and its expected result.>
```
