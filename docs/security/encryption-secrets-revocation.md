# Encryption, secrets and revocation

Telemetry and drone objects never travel or rest in clear text.

## Encryption in transit

| Flow | Protocol | Authentication |
|---|---|---|
| Farm node to IoT Core | MQTT over TLS 1.3, port 8883 | X.509 device certificate |
| LoRa node to LoRaWAN gateway | LoRaWAN AES-128 session keys | Device keys |
| LoRaWAN gateway to cloud | TLS over cellular | Gateway certificate |
| Carrier application to API | HTTPS with TLS 1.2 or later | Cognito token |
| Drone ground station to API and S3 | HTTPS with TLS 1.2 or later | Cognito token and presigned URL |
| Collection center to VPC | IPsec site-to-site VPN | Pre-shared keys held in the secrets manager |
| Browser to public query | HTTPS through CloudFront | None, read by code |
| Function to AWS services | HTTPS with TLS 1.2 or later | IAM role |

IoT Core applies a security policy that accepts TLS 1.3 and TLS 1.2 by default. Constrained modems that only support TLS 1.2 stay compatible.

## Encryption at rest

| Store | Key |
|---|---|
| DynamoDB tables for readings, sacks and cases | Customer managed KMS key for data |
| S3 buckets for flight objects and the telemetry archive | Customer managed KMS key for objects |
| Terraform state | Customer managed KMS key for platform |
| Secrets | Customer managed KMS key for platform |
| Audit logs | Customer managed KMS key in the log archive account |

Annual key rotation is on for every key. The node's buffer uses the microcontroller's flash encryption, so a lost node exposes no readings.

## Secrets

Secrets stay out of the repositories and out of Terraform state.

| Secret | Location | Consumed by |
|---|---|---|
| VPN pre-shared keys | Secrets Manager | Center firewall, at installation |
| Third-party API keys | Secrets Manager | Functions, read at run time |
| Pipeline credentials | None, replaced by OIDC federation | Pipeline |

Terraform receives the secret's name or ARN, and functions read the value at run time. Variables that could carry sensitive values are marked sensitive, and a repository scanner blocks credentials in pull requests.

## Revocation

When a node or drone is lost, the platform revokes its identity and the device stops publishing. The target is one hour from the report.

1. The operator reports the device in the support channel, with its identifier.
2. A platform operator marks the certificate as revoked in IoT Core and detaches its policy.
3. The platform closes active connections, and the next attempt fails at the TLS handshake.
4. The operator marks the device inactive, which raises no missing-telemetry alarm for it.
5. The audit log keeps who revoked what, and when.

Readings already stored stay in place. Messages that arrive from a revoked identity are rejected and appear in the connection failure metric.

For a replacement, the installer provisions a new certificate. Certificates are never reused.
