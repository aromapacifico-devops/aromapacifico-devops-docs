# Release notes and change policy

Every change that reaches production carries a release note. The note lets one team member approve the change with full knowledge, lets the Federation know before it happens, and tells whoever is on duty how to take it back. This document sets the rules every production change follows, and the two templates next to it give the note its shape.

## Contents

1. Kinds of change
2. When a change may run
3. Approval
4. Notice to the Federation
5. Rollback
6. Where each note lives
7. What fails and what happens then
8. Assumptions and pending confirmations

### Terms used

| Term | Meaning in this document |
|---|---|
| Production change | Any deploy, release or rollback that touches the production environment, through the platform pipeline or an application pipeline |
| Visible impact | An effect a farmer, a center, a carrier, a buyer or the Federation can notice, such as a pause, a new behavior or a change in a message |
| Harvest week | A week that the harvest calendar of the infrastructure repository lists for a department |
| Harvest freeze | No production change from 05:00 to 18:00, Bogota time, on a day inside a harvest week, except in an incident |
| Change contact | The mailbox of the Federation that receives every notice of change |
| Error budget | The bad events a service level objective allows over its window of 30 days |

| Template | Use it for | Example |
|---|---|---|
| [Application release note](application-template.md) | A new version of function code through the ingestion or flight object pipeline | [Delivery functions log the fields of the delivery objective](examples/application-ingestion-1.1.0.md) |
| [Infrastructure release note](infrastructure-template.md) | A plan applied through the platform pipeline, such as a module version, a network, firewall, ingestion or drone path change | [SMS of urgent alerts sent as transactional](examples/infrastructure-telemetry-ingestion-1.0.1.md) |

---

## 1. Kinds of change

| Kind | When it applies | Notice before | Window |
|---|---|---|---|
| Standard | The change has visible impact | 2 working days | The change window of section 2 |
| Low impact | The change has no visible impact, such as a log field, an alarm or an internal setting | 1 working day | The change window of section 2 |
| Incident | The change restores a service that is down or degraded, or closes a security exposure | At the start, and again at the close | Any time, including the harvest freeze |

The person who writes the note picks the kind, and the approver checks it. When in doubt the change is standard. Development and test take no release note, since their pipelines deploy on each merge or tag and nobody outside the team uses them.

A rollback is a production change too. A rollback of a change that went out less than a day before reuses its note and records the reason in it. Any other rollback gets its own note.

## 2. When a change may run

| Period | Window, Bogota time | Why |
|---|---|---|
| Outside a harvest week | Monday to Thursday, 08:00 to 16:00 | The team is at work for the rest of the day to watch the change and take it back. A change late on a Friday could fail with nobody there over the weekend |
| Inside a harvest week | Monday to Thursday, 18:00 to 21:00 | The harvest freeze closes 05:00 to 18:00, and the evening leaves three hours with the team still available |
| Friday, weekend and public holidays | No window | Same reason as Friday afternoon |
| Incident | Any time | A service that is down costs more than the risk of the fix |

The freeze gate enforces the harvest freeze in every production job. It reads the harvest calendar after the approval and stops the job between 05:00 and 18:00 on a harvest day unless the run carries an incident reason, which stays in the run summary next to the approval. The rest of the window is a team rule that the approver checks, since a pipeline cannot know about public holidays or who is on duty.

A service level objective with no error budget left narrows the window further. Until the indicator recovers, the only production changes to that path are fixes of the cause and security patches, as the [service level objectives](../architecture/service-levels.md) set out.

## 3. Approval

Production waits for one team member to approve it in the protected `prod` environment of GitHub. The approver reads the release note and, for the platform pipeline, the plan summary of the same run, then checks four things.

1. The kind of change matches its impact.
2. The window and the notice follow sections 1 and 2.
3. The version ran successfully in test. Application pipelines also refuse a version with no successful test deployment, and the platform pipeline deploys the same commit that test ran.
4. The rollback names a trigger, the steps and what does not go back.

The approver writes the run link into the note. The person who wrote the note may approve it, since the team is small, and the approval stays in the deployment history of the environment.

## 4. Notice to the Federation

The notice goes by e-mail to the change contact of the Federation, in Spanish, from the sections What changes, Window and Impact of the note. It names the person on duty during the window.

| Kind | Before | After |
|---|---|---|
| Standard | 2 working days before the window | A summary the same day, with the result and anything that went back |
| Low impact | 1 working day before | A summary the same day |
| Incident | When the change starts, with the cause known so far | When it closes, with the cause, the effect and what prevents it |

A working day runs Monday to Friday and leaves out Colombian public holidays. When the Federation answers a notice with an objection, the change waits until the two sides agree on a new window.

## 5. Rollback

Every note states how the change goes back, what triggers it and what stays as it is. The two pipelines go back in different ways.

| Pipeline | How it goes back | Time | What does not go back |
|---|---|---|---|
| Platform | A pull request points the environment to the previous module tag, and the same deploy runs with approval | One plan and apply, minutes for most changes | Data in tables and buckets |
| Ingestion and flight object | Automatic during the canary when an alarm fires. After the canary, the same workflow with the previous version moves the `live` alias back | Seconds during the canary, about 2 minutes by hand | Readings, alerts and flight records written by the new version |

A change that needs both pipelines follows the order of the [delivery pipelines](../architecture/delivery-pipelines.md), platform first, then code, then the removal of what the old code needed. Each step gets its own note, so each one can go back alone.

## 6. Where each note lives

Each production change opens an issue from the Release note template in the repository that changes, the infrastructure repository for the platform pipeline and the application repository for a function release. The issue body follows the template of this folder. The pull request and the production run link to the issue, and the issue closes once the summary has reached the Federation.

The issue history of each repository is therefore the change log of the pilot. The `CHANGELOG.md` of a module or an application lists what a version contains, and the release note says how that version reached production.

## 7. What fails and what happens then

| Failure | How it is noticed | What happens |
|---|---|---|
| A change starts with no note | The approver finds no issue linked from the run | The approval waits until the note exists |
| A standard change gets the notice of a low impact one | The approver checks the kind against the impact | The window moves until 2 working days have passed |
| A production job starts in the harvest freeze | Freeze gate after the approval | The job stops unless an incident reason is given |
| A change fails after its window, with the team gone | Alarms to the person on duty | The rollback of the note, which any team member can run from the same workflow |
| The change contact does not answer | No answer is needed | The change runs in its window. Only an objection stops it |

## 8. Assumptions and pending confirmations

| Assumption | If it fails | Who confirms |
|---|---|---|
| The Federation names one mailbox as its change contact | Each notice goes to a list of people, which the note template must record | Federation |
| Two working days are enough for the Federation to object to a change | The notice of a standard change grows, and fixes wait longer | Federation |
| The team can watch a change until 21:00 in a harvest week | The evening window shrinks, and changes wait for the end of the harvest | Team |
| The harvest calendar holds the weeks of each department | The freeze gate lets every hour through, and the approver checks the harvest weeks by hand | Federation |
