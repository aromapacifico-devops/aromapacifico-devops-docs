# Encryption, secrets and revocation

Telemetry and drone objects never travel or rest in clear text, secrets stay out of repositories and out of Terraform state, and a lost device stops publishing. This document defines how, for each flow and each store.

## Contents

1. Threats this design answers
2. Encryption in transit
3. Encryption at rest
4. Keys
5. Secrets
6. Revocation of a node or a drone
7. Secrets in the infrastructure code
8. Cost
9. Assumptions and pending confirmations

### Terms used

| Term | Meaning in this document |
|---|---|
| Customer managed key | A KMS key the platform controls, with its own policy and rotation |
| Envelope encryption | Data is encrypted with a data key, and that key is encrypted with the KMS key |
| Pre-shared key | Secret shared by both ends of a VPN tunnel |
| Certificate revocation | Marking a certificate as invalid so that the service refuses it |

---

## 1. Threats this design answers

| Threat | Control |
|---|---|
| Someone listens on a mobile or LoRa network | TLS and LoRaWAN session encryption |
| A node is stolen from a lot | Encrypted flash, one identity per device, revocation |
| A drone is lost with its data | Encrypted storage, revocation of the ground station |
| A credential leaks from a repository | No static credentials, repository scanning |
| Someone copies a bucket or a table | Encryption at rest with restricted key policies |
| A state file exposes secrets | No secret values reach Terraform |

## 2. Encryption in transit

| Flow | Protocol | Authentication | Notes |
|---|---|---|---|
| Node to IoT Core | MQTT over TLS, port 8883 | X.509 device certificate | IoT Core supports TLS 1.3 and TLS 1.2 |
| LoRa node to gateway | LoRaWAN AES-128 session keys | Device keys | The network server cannot be bypassed |
| Gateway to cloud | TLS over LTE | Gateway certificate | Traffic stays encrypted over the backhaul |
| Carrier application to API | HTTPS with TLS 1.2 or later | Cognito token | |
| Ground station to API and S3 | HTTPS with TLS 1.2 or later | Cognito token and presigned URL | |
| Center to VPC | IPsec site-to-site VPN | Pre-shared keys | Two tunnels per connection |
| Browser to public query | HTTPS through CloudFront | None, read by code | |
| Function to AWS services | HTTPS with TLS 1.2 or later | IAM role | |
| Pipeline to AWS | HTTPS | OIDC role | |

IoT Core applies by default the policy `IoTSecurityPolicy_TLS13_1_2_2022_10`, which accepts both versions. Requiring TLS 1.3 alone would be possible, and it would exclude constrained modems with no gain, since TLS 1.2 with the current ciphers meets the need.

## 3. Encryption at rest

| Store | Key | Why |
|---|---|---|
| DynamoDB tables | Data key | Holds sacks, cases, readings and personal data |
| S3 flight objects and archive | Objects key | Separate key, so that access to objects can be cut without touching the data |
| S3 restricted prefix | Objects key, tighter policy | Objects with a person |
| Terraform state | Platform key | Readable by the pipeline only |
| Secrets | Platform key | |
| Audit logs | Key in the log archive account | A workload cannot decrypt or erase its trail |
| Node flash | Flash encryption of the microcontroller | A stolen node exposes no readings |
| Drone storage | Encrypted storage on the ground station | Depends on the chosen drone |

S3 uses bucket keys, which reduce calls to KMS and the related cost.

## 4. Keys

| Key | Encrypts | Who can use it |
|---|---|---|
| Data | Tables | Functions that write or read them |
| Objects | Buckets | Upload path and inference functions |
| Platform | Terraform state and secrets | Pipeline |
| Audit | Log archive | Trail service, read by the security role |

Yearly automatic rotation is on for every key. Rotation keeps older data readable, because KMS retains the previous key material. Deleting a key waits at least 7 days, and a service control policy limits who can schedule it.

Three customer managed keys in each workload account would be enough. Using one key for everything was discarded, because it would join what the design wants to separate. A key per table was also discarded, since at USD 1 per key per month it would add cost with no real isolation.

## 5. Secrets

| Secret | Location | Consumed by | Rotation |
|---|---|---|---|
| VPN pre-shared keys | Secrets Manager, in a secret AWS creates with the connection | Center firewall, at installation | On change of device or staff |
| Third-party API keys | Secrets Manager | Functions, read at run time | Per provider |
| Pipeline credentials | None | OIDC federation replaces them | Not applicable |
| Function credentials | None | IAM role | Not applicable |

The best secret is the one that does not exist, so the design removes as many as it can. Only two kinds of stored secrets remain.

## 6. Revocation of a node or a drone

A lost device must stop publishing. The target is one hour from the report, which is a design target to confirm with the Federation.

| Step | Who | Action |
|---|---|---|
| 1 | Farmer or operator | Reports the device by phone or in the application |
| 2 | Platform operator | Marks the certificate as `REVOKED` and detaches its policy |
| 3 | Platform | Closes the active connection, and the next attempt fails at TLS |
| 4 | Platform operator | Marks the thing as inactive, so that no silent-node alarm fires |
| 5 | Audit | Records who revoked what and when |

For LoRa nodes, the device is removed from the network server, and its session keys stop working.

For a drone, the certificate and the user session of the ground station are revoked. The drone itself holds no platform credential, so a lost airframe cannot publish.

Readings already stored stay in place. Messages from a revoked identity are rejected and appear in the failed connection metric. A replacement device receives a new certificate, and certificates are never reused.

## 7. Secrets in the infrastructure code

| Rule | How it is met |
|---|---|
| No secret in the repository | Scanner in the pull request, variables with no values |
| No secret in state | Terraform receives the name or ARN of a secret, and the value stays in Secrets Manager |
| No VPN key in state | The connection sets `preshared_key_storage = "SecretsManager"` and leaves the tunnel key arguments empty |
| State is encrypted | S3 backend with KMS and native lock file |
| Sensitive variables are marked | `sensitive = true` |
| No static credentials in the pipeline | OIDC roles |

The VPN row matters because Terraform otherwise stores the tunnel keys in the state as plain text. With that setting, AWS generates the keys, keeps them in a secret, and the state holds only the ARN and a redacted value. The installer reads the keys from Secrets Manager when configuring the center firewall.

## 8. Cost

| Item | Monthly cost, USD |
|---|---|
| Three customer managed keys | 3.00 |
| KMS requests at this load | Under 0.10 |
| Four secrets at USD 0.40 each | 1.60 |

Encryption adds under USD 5 a month, so it never competes with the budget.

## 9. Assumptions and pending confirmations

| Item | Who confirms | Effect if it fails |
|---|---|---|
| One hour is an acceptable revocation target | Federation | The on-call procedure changes |
| The chosen drone encrypts its storage | Drone supplier | Flights hold only the objects of the mission, and the mission is deleted on return |
| Nodes support flash encryption | Node supplier | The node keeps only encrypted payloads |

## Sources

- AWS IoT Core transport security documentation.
- AWS Price List API for KMS and Secrets Manager in us-east-1.
- [Terraform AWS provider, `aws_vpn_connection`](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/vpn_connection) and [AWS, pre-shared key management with Secrets Manager](https://aws.amazon.com/blogs/networking-and-content-delivery/aws-site-to-site-vpn-secure-pre-shared-key-psk-management-with-aws-secrets-manager).
