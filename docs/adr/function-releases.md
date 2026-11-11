# Function code ships from its own repository and goes live through a Lambda alias moved by CodeDeploy

## Context

The ingestion and flight object functions change more often than the network or the identities around them, and a bad release during harvest stops readings or flight records. The infrastructure code already creates every function with its role and triggers, and today it also packages the code. A pull request for one function therefore waits for a plan of the whole environment, and the rollback of a code change is a Terraform apply. The pilot volume is low, about 150 readings and 30 flight objects an hour in harvest.

## Options

For where code lives, one repository per application pipeline that builds a versioned zip into an artifact bucket, or the code kept in the infrastructure repository and shipped by the platform pipeline. For how a version goes live, Lambda versions behind a `live` alias moved by CodeDeploy with automatic rollback on alarms, or the alias moved by hand with a manual rollback, or a new version swapped in by Terraform.

## Decision

The ingestion and flight object code each live in their own repository, which builds one zip per function from a release tag and promotes that same file through test and production. Terraform creates each function with a first package, its role, its triggers, the `live` alias, the CodeDeploy deployment group and the alarms, and ignores later changes to code and alias target. CodeDeploy releases all at once in development and test, after a validation hook, and as a canary of 10 percent for 10 minutes in production, and it moves the alias back when the error or dead letter alarms fire.

## Consequences

A code change ships in minutes without a Terraform plan, and a failing release in production goes back without a person. The release role can change only code and aliases, so a release that needs new infrastructure fails in test and follows the platform pipeline first. At pilot volume the canary sees only a few calls, so it catches versions that fail on most calls, and the tests and the validation in test carry the rest. Two repositories, an artifact bucket and the deployment groups are added, at no material cost. If a weighted alias turns out to skip calls from SQS mappings, queue-driven functions release all at once with the same hook and alarms.
