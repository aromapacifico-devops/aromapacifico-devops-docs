# Each pull request passes automatic checks, with tools pinned by version

## Context

The team standards ask for format, validation, tests and security analysis before any plan. Repositories are public and the pipeline reaches AWS through OIDC, so the workflows are themselves part of what must be protected. In 2026 attackers rewrote the version tags of a widely used security scanning action, which exposed every pipeline that referenced it by tag.

## Options

The minimum of format, validation and one scanner, or that minimum plus checks of the project rules, the workflows, the secrets and the cost.

## Decision

Each pull request runs format, validation, `terraform test` with a mocked provider, TFLint, a check of the project rules, Checkov, gitleaks, zizmor and actionlint, and a check of the title against Conventional Commits. Roots also run Infracost for the resources it can price, and test receives a smoke test after each apply. GitHub push protection and Dependabot complete the set.

Third-party actions are pinned to a full commit SHA, and tools install by exact version with a verified checksum. Trivy was left out because it repeats Checkov. Terratest was left out because it creates real resources and spends credits.

## Consequences

Most failures appear before a plan, and the tests cost nothing since they use a mocked provider. An accepted finding needs a row in the exceptions file, with its reason and its end condition. Infracost prices resources with a fixed rate well, and it says little about services billed per message, such as IoT Core, so the cost documents remain the reference for those.
