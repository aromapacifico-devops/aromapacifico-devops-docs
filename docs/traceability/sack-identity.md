# Sack identity

Each 60 kg sack carries a random code. The code lets anyone read the buyer view of that one sack and reveals nothing about who produced it.

## Format

The code has 12 random symbols and one check symbol, printed in groups of four.

```text
AP-7K3M-Q29X-TDHB-6
```

| Part | Meaning |
|---|---|
| `AP` | Fixed platform prefix |
| 12 symbols | 60 random bits in Crockford Base32, which leaves out I, L, O and U to avoid reading errors |
| Last symbol | Check symbol that catches a mistyped code |

The code holds no national ID, farm, lot, department or date. A database lookup is the only link between a code and its record, and that link stays on the platform.

The QR on the label encodes the query address and the code. A person can also type the code.

## Guessing

The pilot produces at most 1,200 sacks a day in harvest. Even with several million codes issued, the share of valid codes among 60 random bits is negligible, and the firewall limits request rates. A guess does not expose personal data in any case, because the buyer view holds none.

## Registration record

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

A conditional write rejects a repeated code, so uniqueness holds across the three centers and the farms.

The record links to the farm, and the buyer view omits that link.

| Field | Buyer | Center | Farmer |
|---|---|---|---|
| Origin, at department level | Yes | Yes | Yes |
| Process dates | Yes | Yes | Yes |
| State | Yes | Yes | Yes |
| Drying variables | Yes | Yes | Yes |
| Trip | No | Yes | No |
| Farm and lot | No | Yes | Own farms |
| Farmer identity | No | No | Own |

## Code issued at the center

Some sacks reach a collection center with no code. Logistics staff register the sack with its farm and weight, and the platform issues a code that the local printer places on a sheet. The event records that the code was issued at the center and by whom.

A damaged label is reprinted with the same code. The reprint is recorded as an event, and the sack keeps its history.
