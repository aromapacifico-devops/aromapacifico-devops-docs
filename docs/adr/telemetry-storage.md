# Telemetry lives in DynamoDB for 90 days and in S3 for five years

## Context

Readings must last five years. AWS closed Timestream for LiveAnalytics to new customers in June 2025, and DynamoDB time to live alone would delete the readings.

## Options

DynamoDB with an S3 archive, Timestream for InfluxDB, and Aurora PostgreSQL.

## Decision

Recent readings stay in DynamoDB with a 90-day time to live. Every reading also goes through Firehose to S3 for five years, and Athena serves reports over that archive. Sack events and fumigation orders stay in DynamoDB with transactional writes.

## Consequences

No instance waits idle. History older than 90 days takes longer to read, which suits reports. A need for interactive history over years would reopen this decision.
