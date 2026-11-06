# Sack identity

Each 60 kg sack carries a random code. The code lets anyone read the buyer view of that one sack and reveals nothing about who produced it. This document defines the format, explains why it cannot be guessed, shows a record, sets who sees what, and covers sacks that reach a center with no code.

## Contents

1. Requirements
2. Options
3. Format
4. Safety of the code
5. Label
6. Registration record
7. What each actor sees
8. Code issued at the center
9. Volume and storage
10. Assumptions and pending confirmations

### Terms used

| Term | Meaning in this document |
|---|---|
| Sack code | The identifier printed on a sack |
| Buyer view | The fields a buyer may read |
| Crockford Base32 | An alphabet of 32 symbols designed to avoid confusing characters |
| Check symbol | One extra symbol that detects a mistyped code |

---

## 1. Requirements

| Requirement | Consequence |
|---|---|
| The code exposes no national ID and no full trace | It must hold no meaning |
| A buyer reads it with no account | Possession of the code is the only access |
| Staff type it when a label is damaged | It must be short and hard to misread |
| Three centers and 200 farms issue codes | Uniqueness needs no central counter |
| Some sacks arrive with no code | A center must be able to issue one |

## 2. Options

| Option | For | Against | Result |
|---|---|---|---|
| Sequential number | Short | Reveals volume and lets anyone list every sack | Discarded |
| Farm, lot and date in the code | Readable | Exposes origin and can identify the farmer | Discarded |
| UUID | Unique, standard | 36 characters are too long to type | Discarded |
| Random short code | No meaning, short, typed easily | Needs a uniqueness check | **Chosen** |

## 3. Format

The code has 12 random symbols and one check symbol, printed in groups of four.

```text
AP-7K3M-Q29X-TDHB-6
```

| Part | Meaning |
|---|---|
| `AP` | Fixed platform prefix |
| 12 symbols | 60 random bits in Crockford Base32, which leaves out I, L, O and U |
| Last symbol | Check symbol that catches a mistyped code |

The code holds no national ID, farm, lot, department or date. A lookup on the platform is the only link between a code and its record.

## 4. Safety of the code

| Question | Calculation | Result |
|---|---|---|
| How many codes exist | 2^60 | About 1.15 × 10^18 |
| Codes issued in five years, upper bound | 3 million | Far above the expected volume |
| Chance that one random guess hits a code | 3 × 10^6 / 2^60 | About 2.6 × 10^-12 |
| Chance of any collision among 3 million codes | n² / 2^61 | About 4 × 10^-6 |

A guess succeeds about 3 times in a trillion, and the firewall limits the rate of attempts. A success would expose only the buyer view of one sack, which holds no personal data.

A collision is unlikely and harmless, because the write is conditional. If a code exists, the platform draws another one.

## 5. Label

| Element | Content |
|---|---|
| QR | Query address with the code |
| Printed code | The same code, in groups of four, for manual entry |

The label must withstand handling and humidity along the route. The design system defines its appearance.

## 6. Registration record

```json
{
  "sack_code": "AP-7K3M-Q29X-TDHB-6",
  "farm_id": "f-41-0137",
  "lot_id": "l-02",
  "weight_kg": 60.0,
  "state": "in_preparation",
  "created_at": "2026-05-14T15:20:00Z",
  "created_by": "user-8f21"
}
```

Each event stores date, time and responsible person. The record links to the farm through an internal identifier, and the buyer view omits that link.

The `state` field takes one of seven values, which match the states of the pilot.

| Value | Meaning |
|---|---|
| `in_preparation` | Registered on the farm |
| `in_transit_to_center` | With the carrier, on the way to the center |
| `at_center_accepted` | Received at the center and accepted |
| `at_center_rejected` | Received at the center and rejected |
| `in_transit_to_port` | On the way to Buenaventura |
| `delivered_accepted` | Delivered at the port and accepted |
| `delivered_rejected` | Delivered at the port and rejected |

## 7. What each actor sees

| Field | Buyer | Center | Farmer |
|---|---|---|---|
| Origin, at department level | Yes | Yes | Yes |
| Process dates | Yes | Yes | Yes |
| State | Yes | Yes | Yes |
| Drying variables | Yes | Yes | Yes |
| Trip | No | Yes | No |
| Farm and lot | No | Yes | Own farms |
| Farmer identity | No | No | Own |

## 8. Code issued at the center

Some sacks reach a collection center with no code.

| Step | Action |
|---|---|
| 1 | Logistics staff register the sack with its farm and weight |
| 2 | The platform issues a new code |
| 3 | The local printer prints the code sheet |
| 4 | The event records that the code was issued at the center and by whom |

With no WAN, the application can draw a code locally from a block reserved for that center, and the platform confirms it on return.

A damaged label is reprinted with the same code. The reprint is recorded as an event, and the sack keeps its history.

## 9. Volume and storage

| Measure | Value |
|---|---|
| Sacks a day in harvest, three centers | Up to 1,200 |
| Sacks a harvest month | Up to 36,000 |
| Sacks a year, four harvest months | Up to 144,000 |
| Sacks in five years | Up to 720,000 |

The upper bound of 3 million in section 4 therefore leaves a wide margin.

## 10. Assumptions and pending confirmations

| Item | Who confirms | Effect if it fails |
|---|---|---|
| Origin at department level is enough for buyers | Federation | The buyer view gains or loses detail |
| Label material resists the route | Supplier test | Material changes |
| Offline code blocks are worth the complexity | Team | Centers wait for the WAN to issue codes |
| Transitions between states, with the event and the responsible person of each one | State model of the sack, a separate document in this folder | The `state` values gain or lose detail |
