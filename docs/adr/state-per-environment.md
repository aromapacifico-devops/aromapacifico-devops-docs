# Each environment has one root, one state and one bucket

## Context

State must stay apart between environments, so an action in test cannot reach production. The modules of one environment also reference each other, since interface endpoints need security groups and security groups need the VPC. Environments come down every night, and a plan must still work the next day.

## Options

One root and one state per environment, or one root per domain with a state each for network, security and workload. For the buckets, one per environment, or one shared bucket with a prefix per environment.

## Decision

Each environment has one root, in its own directory, with one state in its own bucket. Separate directories let test and production pin different module versions. Separate buckets follow the AWS recommendation of distinct backends per environment, which lets each pipeline role reach one bucket and each environment use its own key.

States per domain limit what a single run can touch, and they suit a large platform whose network stays up. They were discarded here because a workload plan would fail while the network it reads through data sources is down, and because the references between network and security could not cross two states.

## Consequences

A plan of the whole environment works from nothing, and destroying an environment is one operation. A run touches every module of an environment, which stays manageable at about 100 resources. If the platform grows past that, the module boundaries already mark where to split the state.
