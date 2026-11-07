# The demonstration uses one standalone credit account that goes up and down

## Context

The code is proven on an AWS account with USD 100 in credits, extensible to USD 200. Joining an Organization moves a free account to the paid plan, and a free account closes when its credits run out. A full test environment costs about USD 0.08 an hour while up, and production about USD 0.11.

## Options

One account with environments separated by name, range, state and role, one account per environment, or an Organization with member accounts.

## Decision

One standalone account holds every environment, with one bootstrap. The team brings environments up and down through the pipeline, and the pipeline destroys every environment each night. The target design keeps its seven accounts.

## Consequences

One account is simple to create and to control, and two weeks of 8-hour sessions with both environments up cost about USD 16. The boundary between environments depends on configuration and on the trust of each role, which is weaker than an account, and the demonstration accepts that because it holds no real data. Service control policies stay in the design only, and items that exist once per account, such as the OIDC provider and the IoT registry, are shared on purpose. Azure receives nothing. Moving an environment to its own account changes its provider role and its backend, and the modules stay the same.
