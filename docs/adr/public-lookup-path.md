# The public lookup runs on a function URL behind CloudFront, with a ceiling of five reserved copies

## Context

The sack lookup is the only service anyone can reach without an account. Its web firewall sits on the CloudFront distribution and limits each address to 300 requests in 5 minutes. An origin with its own public address could be called directly and skip that limit, and API Gateway HTTP APIs keep such an address and accept no web firewall and no resource policy. The per-address limit also leaves requests spread over many addresses with no bound on rate or cost.

## Options

To close the direct path, a Lambda function URL with IAM authorization behind the distribution with origin access control, an HTTP API with a secret header checked by the function, or a regional REST API with the firewall attached to it. To bound the total rate, five reserved copies of the lookup function, a firewall rule that counts every request together, or no bound and an alarm only.

## Decision

The lookup function has a function URL that admits only requests signed by the distribution, so IAM enforces the path with no secret to rotate, and the route costs USD 1.00 less per million lookups. Five reserved copies cap the lookup at about 25 a second, about 50 times the harvest peak, while a buyer meets a refusal about once in ten million lookups. A rule that counts every request together would be filled by about 10 addresses. Phones and the reports web keep the HTTP API.

## Consequences

Every lookup passes the firewall, and the cost of abuse stays bounded until the operator blocks the addresses or switches the lookup off. About 25 addresses at the per-address limit can fill the ceiling and deny buyers for that time. The route has no API Gateway logs, and the audit events and firewall logs take their place. If a warm lookup proves much slower than 200 ms, the number of reserved copies is recomputed.
