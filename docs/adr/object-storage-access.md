# S3 and DynamoDB are reached through gateway endpoints

## Context

The address plan includes an object storage subnet, yet S3 does not live in a subnet. Reaching it through a NAT gateway charges by the hour and by the gigabyte.

## Options

Gateway endpoints, interface endpoints, or a NAT gateway.

## Decision

Private route tables use gateway endpoints for S3 and DynamoDB, which carry no charge. The object storage subnet stays in the plan and holds the route association. An interface endpoint for S3 serves uploads that arrive from the centers through the VPN, since gateway endpoints cannot be reached from outside the VPC.

## Consequences

No NAT gateway is needed. Three interface endpoints across two zones cost USD 43.80 a month, at USD 0.01 per hour for each zone.
