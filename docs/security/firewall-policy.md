# Firewall policy, centers and cloud

Each collection center and the cloud allow only the traffic the platform needs, and deny everything else. This document is the single policy matrix of every enforcement point, with an identifier per rule, whether the rule stays for the pilot or is temporary, and which rules the infrastructure code builds.

## Contents

1. Enforcement points
2. Center perimeter firewall
3. Tunnel between a center and the cloud
4. Cloud network, security groups and network ACLs
5. Public edge
6. Temporary rules
7. Checks at installation
8. What fails and what the platform does
9. Cost
10. Assumptions and pending confirmations
11. Sources

### Terms used

| Term | Meaning in this document |
|---|---|
| Permanent rule | A rule that stays for the life of the pilot and changes only through a reviewed change |
| Temporary rule | A rule with an owner, a reason and an end date, removed when its end date arrives |
| Pending rule | A permanent rule already defined that stays unloaded until a missing fact is confirmed |
| `X` | Second octet of a center, 41 for Cauca, 42 for Huila and 43 for Tolima |
| Center source ranges | Logistics `10.X.3.0/24` and local servers `10.X.10.0/24` of every center linked to the environment |
| Security group | Stateful firewall of AWS attached to a network interface, which allows return traffic by itself |
| Network ACL | Stateless filter of AWS on a subnet, which needs a rule for return traffic |
| Web ACL | Set of AWS WAF rules in front of a public address |

---

## 1. Enforcement points

Traffic between a center and the cloud meets three independent barriers, and each one stops a wrong path by itself.

| Point | What it controls | Default | Loaded by |
|---|---|---|---|
| Center perimeter firewall | Every path between zones, toward the internet and into the tunnel | Deny | Installation template of the center, same for the three centers |
| Tunnel routes | Which center ranges enter the tunnel and which subnets of the cloud answer | No route | Firewall template on the center side, infrastructure code on the AWS side |
| Security groups of the interface endpoints | Who reaches IoT Core, S3 and the private API inside the VPC | Deny | Infrastructure code |
| Network ACLs of the VPC subnets | A second, stateless filter on each subnet | Deny | Infrastructure code |
| Web ACL of the public query | Rate and content of public requests to the sack lookup | Allow, with blocking rules | Infrastructure of the public query |

Farm nodes, drones away from a center and carriers reach AWS through the public endpoints of IoT Core, S3 and the API, protected by device certificates, Cognito tokens and TLS. No firewall of the platform sits on those paths, so identity is their control.

## 2. Center perimeter firewall

The firewall holds the gateway of every zone, the tunnel to AWS and the policy. Rules apply from the first to the last, and the last denies everything. Rules 01 to 10 restate the zone policy of the [center WLAN design](../network/center-wlan.md), which explains each zone, and rules 11 to 17 add what the firewall itself needs. Internet means every address outside `10.0.0.0/8`, `172.16.0.0/12` and `192.168.0.0/16`.

| ID | Source | Destination | Protocol and port | Action | Duration |
|---|---|---|---|---|---|
| CTR-01 | Logistics `10.X.3.0/24` | Endpoint subnets of the linked environment, production `10.70.0.0/20`, `10.70.16.0/20`, `10.70.32.0/20` | TCP 443 | Allow | Permanent |
| CTR-02 | Local servers `10.X.10.0/24` | Same endpoint subnets | TCP 443 | Allow | Permanent |
| CTR-03 | Logistics `10.X.3.0/24` | Label printer, one address in `10.X.10.0/24` | One protocol and port, to confirm with the printer model | Allow | Pending |
| CTR-04 | Transport `10.X.4.0/24` | Internet | TCP 443 | Allow | Permanent |
| CTR-05 | Management `10.X.1.0/24` | Internet | TCP 443 | Allow | Permanent |
| CTR-06 | Support `10.X.2.0/24` | Internet | TCP 443 | Allow | Permanent |
| CTR-07 | Visitors `10.X.5.0/24` | Internet | TCP 80, 443 | Allow | Permanent |
| CTR-08 | Every client zone | Gateway of its own zone, `10.X.N.1` | UDP 67 for DHCP, UDP and TCP 53 for DNS | Allow | Permanent |
| CTR-09 | Visitors `10.X.5.0/24` | `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16` | Any | Deny | Permanent |
| CTR-10 | Visitors `10.X.5.0/24` | Any other address of the firewall | Any | Deny | Permanent |
| CTR-11 | Public address of the firewall | Outside addresses of tunnel 1 and tunnel 2 | UDP 500, both ways | Allow | Permanent |
| CTR-12 | Public address of the firewall | Outside addresses of tunnel 1 and tunnel 2 | UDP 4500, both ways, for NAT traversal | Allow | Permanent |
| CTR-13 | Public address of the firewall | Outside addresses of tunnel 1 and tunnel 2 | IP protocol 50, ESP, both ways | Allow | Permanent |
| CTR-14 | Resolver of the firewall | Two public DNS resolvers set at installation | UDP and TCP 53 | Allow | Permanent |
| CTR-15 | Firewall | Two NTP servers set at installation | UDP 123 | Allow | Permanent |
| CTR-16 | Administration hosts `10.X.10.11` to `10.X.10.20` | Administration address of the firewall | TCP 443 and TCP 22 | Allow | Permanent |
| CTR-17 | Administration host `10.X.10.11` | Update service of the firewall vendor | TCP 443 | Allow | Temporary, one maintenance window |
| CTR-18 | Any | Any | Any | Deny and log | Permanent |

Two choices shape this table.

**One port toward the cloud.** Devices at a center reach IoT Core, S3 and the private API on TCP 443 only. IoT Core accepts MQTT on 443 when the client presents the ALPN name `x-amzn-mqtt-ca`, so a center device needs no second port. Port 8883 stays a choice of farm nodes on the public endpoint, outside the center.

**Printing waits.** CTR-03 is written so it cannot be loaded as a placeholder range. Until the printer model fixes one address, one protocol and one port, logistics cannot reach local servers, and the cell reads as deny.

The resulting reach of each zone, which the [center WLAN design](../network/center-wlan.md) draws as a matrix, does not change. Logistics and local servers reach only the cloud, the other staff zones reach only the internet on 443, visitors reach only the internet on 80 and 443, and no zone reaches another.

## 3. Tunnel between a center and the cloud

The site-to-site VPN carries only the two center ranges that need the cloud, and the cloud answers only from the subnets that hold endpoints.

| ID | Source | Destination | Protocol and port | Action | Duration |
|---|---|---|---|---|---|
| TUN-01 | Center announces `10.X.3.0/24` and `10.X.10.0/24` | Tunnel | Route | Allow | Permanent |
| TUN-02 | Any other center range | Tunnel | Route | No route | Permanent |
| TUN-03 | Route tables of telemetry ingress, drone object ingress and application | `10.X.3.0/24` and `10.X.10.0/24` of each linked center | Route through the virtual private gateway | Allow | Permanent |
| TUN-04 | Data, object storage, administration and public query route tables | Any center range | Route | No route | Permanent |

The VPC has no internet gateway and no NAT gateway, as the [cloud addressing plan](../network/cloud-addressing.md) sets, so a center can reach nothing in AWS beyond the endpoints, and nothing in AWS can open a path into a center.

## 4. Cloud network, security groups and network ACLs

### Security groups

Each interface endpoint has its own security group, so each one keeps its own identity in a plan and a future difference touches one group. Today the three carry the same rules.

| ID | Applies to | Source | Destination | Protocol and port | Action | Duration |
|---|---|---|---|---|---|---|
| SG-01 | IoT Core data endpoint | Center source ranges | Endpoint | TCP 443 | Allow | Permanent in production, temporary elsewhere |
| SG-02 | S3 interface endpoint | Center source ranges | Endpoint | TCP 443 | Allow | Permanent in production, temporary elsewhere |
| SG-03 | Private API endpoint | Center source ranges | Endpoint | TCP 443 | Allow | Permanent in production, temporary elsewhere |
| SG-04 | The three endpoint groups | Endpoint | Any | Any | No outbound rule, so deny | Permanent |
| SG-05 | Default security group of the VPC | Any | Any | Any | No rule, so deny | Permanent |
| SG-06 | Any group | Any | Any | Any | Deny, implicit | Permanent |

A security group allows the return of traffic it accepted, so SG-04 blocks only connections that an endpoint would open by itself, which none needs. Development and test turn their endpoints on only for a session that needs them, so their groups exist only while the endpoints do.

### Network ACLs

Two network ACLs replace the default one, which allows everything.

| ID | Applies to | Direction | Source or destination | Protocol and port | Action | Duration |
|---|---|---|---|---|---|---|
| NACL-01 | Telemetry ingress, drone object ingress, application | In | From center source ranges | TCP 443 | Allow | Permanent |
| NACL-02 | Same subnets | Out | To center source ranges | TCP 1024 to 65535, return traffic | Allow | Permanent |
| NACL-03 | Same subnets | In and out | Any | Any | Deny | Permanent |
| NACL-04 | Data, object storage, administration, public query | In and out | Any | Any | Deny | Permanent |

A network ACL keeps no state, so NACL-02 lets responses of the endpoints return to the ephemeral ports that the center client chose. The reserved subnets hold nothing that receives traffic, since S3 and DynamoDB are reached through gateway endpoints, functions run outside the VPC, and CloudFront and API Gateway run outside it. A security group written wrong therefore still meets a subnet that admits only TCP 443 from the centers.

## 5. Public edge

The public sack lookup is the only service anyone can reach without an account, and the [sack identity design](../traceability/sack-identity.md) relies on limiting the rate of code guesses. A web ACL of AWS WAF sits in front of its CloudFront distribution. Its default action is allow, since the lookup must answer any browser, and the rules block what does not belong.

| ID | Rule | Match | Action | Duration |
|---|---|---|---|---|
| WAF-01 | Rate per source IP | More than 300 requests in 300 seconds on the sack lookup path | Block, in count mode for the first two weeks of the first harvest | Permanent |
| WAF-02 | Managed core rule set, `AWSManagedRulesCommonRuleSet` | Common web attacks, such as cross-site scripting and size violations | Block | Permanent |
| WAF-03 | Managed known bad inputs, `AWSManagedRulesKnownBadInputsRuleSet` | Request patterns of known exploits | Block | Permanent |
| WAF-04 | Default action | Any other request | Allow | Permanent |

The whole pilot peaks at 30 sack reads a minute in harvest. A limit of 300 requests in 5 minutes per address leaves room for many buyers behind one carrier address, while a script trying codes meets the limit within minutes. With about 3 million valid codes in a space of 2^60, a client held to 300 tries in 5 minutes needs far longer than the life of the pilot to hit one. Count mode in the first weeks shows real traffic before the rule blocks anyone, and the limit can move to 100 if the counts allow.

Center stations call a separate API, an API Gateway REST API of the private type, because that is the only type that an interface endpoint reaches and that accepts a resource policy. Its resource policy accepts requests only through the interface endpoint of the VPC, so a center call never travels the public internet. Phones and the public lookup use the public HTTP API, which has neither feature.

## 6. Temporary rules

A temporary rule exists only with an owner, a reason and an end date written in the change that adds it. It enters through the change process, and it leaves at its end date or at the monthly review, whichever comes first. A rule found past its end date is removed before any other change.

| ID | Owner | Reason | End |
|---|---|---|---|
| CTR-17 | Network lead of the center | Firmware and license updates of the firewall | End of the maintenance window, at most one day |
| SG-01 to SG-03 in development and test | Platform lead | A session that tests the center path | When the session ends and the endpoints are turned off |

No change enters production between 05:00 and 18:00 in a harvest week except for an incident, and that applies to adding or removing a rule.

## 7. Checks at installation

| Check | Expected |
|---|---|
| From a logistics device, open the private API through the tunnel | It answers on 443 |
| From a logistics device, connect to the IoT endpoint on 8883 | It fails |
| From a visitor phone, reach any address in `10.0.0.0/8` | It fails |
| From a management desktop, reach the private API | It fails, since management has no route into the tunnel |
| From the center, reach an address in the data subnet of the cloud | It fails, with no route |
| In AWS, list the rules of each endpoint security group | Only TCP 443 from the center source ranges, and no outbound rule |
| Send 400 requests in one minute to the sack lookup from one address | WAF counts them in count mode, and blocks them after the switch |

## 8. What fails and what the platform does

| Failure | What the platform does | What is lost |
|---|---|---|
| A center rule allows too much | The tunnel carries only two ranges, and the endpoint groups and the network ACLs admit only those ranges on 443 | Nothing reaches the cloud beyond what the cloud rules allow |
| A security group gains a wrong rule | The network ACL of the subnet still admits only 443 from the centers | Nothing |
| The tunnel drops | The second tunnel of the connection takes over, and reception continues locally if both drop | Nothing, the center synchronizes on return |
| The rate rule blocks a legitimate buyer | The buyer retries after 5 minutes. The count mode period sizes the limit before it blocks | A delayed lookup |
| A temporary rule outlives its end date | The monthly review removes it before any other change | Nothing |

## 9. Cost

Calculated from the AWS price list for us-east-1.

| Item | Rate | Monthly cost |
|---|---|---|
| Web ACL | USD 5 per month | USD 5.00 |
| Three rules, two of them managed rule groups | USD 1 per rule per month | USD 3.00 |
| Requests to the public lookup | USD 0.60 per million | USD 0.32 for an upper bound of 540,000 requests in a harvest month |
| Security groups and network ACLs | No charge | USD 0.00 |
| **Total** | | **About USD 8.32 in a harvest month** |

The center firewalls are equipment of each center, and the VPN connections and interface endpoints are costed with the network.

## 10. Assumptions and pending confirmations

| Assumption | Why it is reasonable | If false | Confirms |
|---|---|---|---|
| Center devices that use IoT Core support MQTT on 443 with ALPN | The device SDKs of AWS IoT support it, and farm nodes already need it | SG-01 and CTR-01 add TCP 8883 | Network lead |
| Each center firewall has a static public address and supports IKEv2 with NAT traversal | The center LAN design requires both | CTR-11 to CTR-13 change, or the center needs another device | Network lead |

| Pending confirmation | How it is settled |
|---|---|
| Printer address, protocol and port for CTR-03 | Printer model selection |
| Center devices resolve the endpoint-specific DNS names of the interface endpoints through public DNS, so no resolver path into the VPC is needed | First center device on the test environment |
| The rate limit of WAF-01 | Counts of the first two weeks of harvest |

## 11. Sources

| Fact | Source |
|---|---|
| Customer gateway rules, UDP 500 and IP protocol 50 to both tunnel addresses, UDP 4500 with NAT traversal | https://docs.aws.amazon.com/vpn/latest/s2svpn/FirewallRules.html |
| Network ACLs are stateless, need rules for return traffic, and 1024 to 65535 covers client ephemeral ports | https://docs.aws.amazon.com/vpc/latest/userguide/custom-network-acl.html |
| Rate-based rules, windows of 60, 120, 300 or 600 seconds and a lowest limit of 10 | https://docs.aws.amazon.com/waf/latest/developerguide/waf-rule-statement-type-rate-based-high-level-settings.html |
| Core rule set and known bad inputs managed rule groups | https://docs.aws.amazon.com/waf/latest/developerguide/aws-managed-rule-groups-baseline.html |
| Only REST APIs offer the private endpoint type, resource policies and AWS WAF, and HTTP APIs offer none of them | https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-vs-rest.html |
| MQTT on 443 with ALPN `x-amzn-mqtt-ca` | [Farm connectivity](../network/farm-connectivity.md) |
| Zones, VLANs and the zone policy of a center | [Center WLAN](../network/center-wlan.md) |
| Subnets, routes and the absence of internet and NAT gateways | [Cloud addressing](../network/cloud-addressing.md) |
| AWS WAF prices | AWS Price List API, `pricing.us-east-1.amazonaws.com/offers/v1.0/aws/awswaf/current/us-east-1/index.json` |
