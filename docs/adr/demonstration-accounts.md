# The demonstration uses standalone credit accounts that go up and down

## Context

The code is proven on AWS accounts with USD 100 in credits, extensible to USD 200. Joining an Organization moves a free account to the paid plan, and a free account closes when its credits run out. A full test environment costs about USD 0.08 an hour while up.

## Options

One account per environment, one account with name prefixes, or an Organization with member accounts.

## Decision

Test and production use separate standalone accounts, each with its bootstrap. The pipeline deploys and destroys on demand, and it destroys each night outside production. The target design keeps its seven accounts.

## Consequences

Credits last, since two weeks of 8-hour sessions cost under USD 7. Service control policies stay in the design only. Azure receives nothing.
