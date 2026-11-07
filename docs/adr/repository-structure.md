# Each module has its own repository, separate from the infrastructure repository

## Context

The code has five reusable modules and one consumer. Mixing modules and environments in one repository blocks independent versions and joins producer with consumer. HashiCorp recommends storing each module in its own repository and keeping configuration apart from module code, and AWS recommends placing each reusable module at the root of its own repository. The public Terraform Registry expects that same shape.

## Options

One repository per module, one shared modules repository with a folder per module, or everything in the infrastructure repository.

## Decision

Each module lives in its own `terraform-aws-<name>` repository, generated from a shared template. The infrastructure repository holds the roots of each environment, and the `.github` repository holds the shared workflows. Each module publishes exact `vX.Y.Z` tags.

A shared modules repository also works and costs less, since one change can touch two modules. It was discarded because each module would need a prefixed tag such as `network-v1.0.0`, or all modules would share one version and lose independent releases.

## Consequences

Each module has its own owner, tests, history and version, and a change reaches an environment through a reviewed version update. A change across modules takes more steps, since each one passes its own review and tag, so each README agrees its interface first. A template and shared workflows keep the setup of each repository small. A correction to the template does not reach repositories already generated from it, so those need their own change.
