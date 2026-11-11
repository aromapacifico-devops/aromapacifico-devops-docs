# Ingestion, telemetry ingestion 1.0.1, SMS of urgent alerts sent as transactional

This example fills the [infrastructure template](../infrastructure-template.md) with a real change of the platform, the move of production from telemetry ingestion 1.0.0 to 1.0.1. The window, the names and the dates are an example.

| Field | Value |
|---|---|
| Kind of change | Low impact |
| Area | Ingestion, alert delivery |
| Pull request | [aromapacifico-devops-infra#27](https://github.com/aromapacifico-devops/aromapacifico-devops-infra/pull/27) |
| Module versions | `terraform-aws-telemetry-ingestion` from `v1.0.0` to `v1.0.1` |
| Test deployment | Deploy of test from the merge commit of the pull request, with the smoke test reading found in the readings table |
| Written by | Platform team member |
| On duty during the window | Platform team member |

## What changes

Urgent drying alerts that reach a farmer by SMS must travel as transactional messages, the class that carriers deliver first and that marketing filters leave alone. Version 1.0.0 set that class once, on the SMS configuration set. The weekly drift check of test found that the provider leaves the class empty when it creates the set, so the setting never reached AWS and each new deploy showed the same difference.

Version 1.0.1 moves the class to each message. The delivery check function reads `SMS_MESSAGE_TYPE` with the value `TRANSACTIONAL` and passes it on every send, so the class no longer depends on the configuration set. The same version encrypts the records that wait in the archive stream with a key owned by AWS. Every archived object already landed in S3 under the objects key, and the change covers the at most 15 minutes a record waits in the stream.

| Plan of production | Value |
|---|---|
| Summary | 0 to add, 2 to change, 0 to destroy |
| Resources changed in place | `module.telemetry_ingestion.aws_lambda_function.functions["delivery_check"]`, a new environment variable. `module.telemetry_ingestion.aws_kinesis_firehose_delivery_stream.archive`, server-side encryption turned on |
| Resources replaced or destroyed | None |

## Window

| Field | Value |
|---|---|
| Date | Tuesday, outside a harvest week |
| Start and end, Bogota time | 09:00 to 10:00 |
| Harvest week | No |

## Impact

| Field | Value |
|---|---|
| Who notices | Nobody. A farmer receives the same SMS, now sent with the transactional class |
| Expected interruption | None. Lambda keeps serving the current configuration until the update finishes, and the archive stream stays active while encryption turns on |
| Data | No table, bucket or stream is replaced. Records in the stream during the switch keep flowing to the archive |
| Service level objectives affected | Crop alert delivery. Push delivery does not change, and SMS reaches only urgent alerts with no receipt after 5 minutes, which the objective does not count |
| Main risk | A delivery check function that fails on the new variable would stop the SMS of urgent alerts. The SMS not delivered alarm and the dead letter queue alarm of the delivery check queue show it |

## Approval

| Field | Value |
|---|---|
| Approver | Platform team member |
| Production run | Deploy run of production in the protected `prod` environment |
| What the approver checked | The plan summary of the same run shows 2 changes in place and nothing replaced, the change is low impact and the notice went out one working day before, test ran the same commit, and the rollback below |

## Notice to the Federation

| Field | Value |
|---|---|
| Sent to | Change contact of the Federation |
| Notice sent | Monday, one working day before |
| Summary sent | Tuesday after the window, with the result of the verification |

## Rollback

| Field | Value |
|---|---|
| Trigger | An SMS not delivered alarm or a message in the dead letter queue of the delivery check queue within a day of the change |
| Steps | A pull request points the three roots back to `?ref=v1.0.0`, then the deploy runs for production with approval |
| Time to go back | One plan and apply of the production root, a few minutes |
| What does not go back | SMS already sent as transactional stay sent. Going back reopens the drift difference on the configuration set, which version 1.0.0 cannot close |

## Verification after the change

The next manual drift run of production reports no difference on the SMS configuration set. The configuration of the delivery check function shows the new variable.

```bash
aws lambda get-function-configuration --function-name <delivery check function> \
  --query 'Environment.Variables.SMS_MESSAGE_TYPE'
```

The expected answer is `"TRANSACTIONAL"`. The next urgent alert that goes to SMS shows the message type in the SMS status log.
