# Harvest estimation by area flight

A collection center receives up to 400 sacks a day in harvest and prepares people, space and transport for them. This document defines how one area flight per farm and per harvest, combined with a field sample of the trees, gives the center an estimate of how many 60 kg sacks each farm will bring, with a range, a date and the objects it came from. The estimate informs the center and never creates a packing order, a sack or a spraying action.

## Contents

1. Terms
2. Context and volumes
3. Method
4. Flow of one estimate
5. Result contract
6. What the center sees
7. Integrity, privacy and limits
8. What fails and what the platform does
9. Cost
10. Assumptions and pending confirmations
11. Sources

## 1. Terms

| Term | Meaning in this document |
|---|---|
| Cherry | The ripe coffee fruit as picked |
| Dry parchment | Coffee after pulping, washing and drying at the farm, still in its parchment layer |
| Sack | A 60 kg sack of dry parchment, as it leaves the farm processing facility |
| Orthomosaic | One map image of a lot stitched from the photos of an area flight |
| Productive tree | A coffee tree old enough to bear fruit in this harvest |
| Load per tree | Kilograms of cherry a tree is expected to give in this harvest |
| Conversion factor | Kilograms of dry parchment obtained from one kilogram of cherry |
| Range | The lowest and highest number of sacks the estimate supports |

## 2. Context and volumes

The drone service flies in area mode to delimit lots and to estimate the harvest, and in precision mode for confirmation, fumigation and verification, as the [drone operating mode](operating-mode.md) explains. Estimation uses one area flight a year for each harvest, with no product on board.

| Figure | Value | Origin |
|---|---|---|
| Farms | 200 | Pilot definition |
| Estimation missions | 200 per harvest, one per farm, covering all its published lots | Design choice |
| Harvest months | Four a year | Team estimate in the operating mode |
| Missions in a harvest month | About 50 when spread over the four months | 200 divided by 4 |
| Sacks received by one center on a peak day | Up to 400 | Pilot definition |
| Inference rate | About USD 1.75 per 1,000 images, with the person filter | Managed inference cost of the platform |

One mission per farm answers the question the center asks, how many sacks come from each farm, and the result keeps the detail of each lot so a later review can see where a difference came from.

## 3. Method

An aerial image shows trees and canopy. It cannot see most of the fruit, which grows under the leaves along the branches. The estimate therefore joins what the drone measures well with what a field sample measures well, and converts the result with the published factor of Cenicafé.

| Step | What is measured | Who or what measures it |
|---|---|---|
| Productive trees per lot | Count of trees inside the published polygon, minus no-fly zones, with a low and high count | Inference function on the orthomosaic, reviewed by the supervisor on a sample of tiles |
| Load per tree | Kilograms of cherry per tree, with mean and spread | Field sample of trees by the brigade during the same visit, counting fruit on sampled branches, or the farm's own history once one harvest exists |
| Dry parchment | Cherry multiplied by the conversion factor | Platform, with the factor of Cenicafé |
| Sacks | Dry parchment divided by 60 kg | Platform |

Cenicafé measured between 4.89 and 4.94 kg of cherry for each kilogram of dry parchment, with an older reference of 4.50. The platform uses 0.20 kg of dry parchment per kilogram of cherry, the factor of that table, as the central value, and 0.20 to 0.222 for the range, where 0.222 follows from the older 4.50.

A worked example, with invented values that are not field data, shows the arithmetic. A lot with 5,000 productive trees and a sample of 2.0 kg of cherry per tree gives 10,000 kg of cherry, 2,000 kg of dry parchment and about 33 sacks. With a tree count between 4,800 and 5,200, a load between 1.7 and 2.3 kg, and the factor interval, the range runs from about 27 to 44 sacks.

The farm history becomes a second source after the first harvest. The platform already records each sack a farm delivers, so the sacks of the last harvest divided by the trees counted then give a load per tree that the next estimate can compare with the field sample.

## 4. Flow of one estimate

1. The campaign plan issues one estimation mission for each farm before its harvest peak. The mission needs a published polygon for every lot it covers. A lot whose polygon is missing or suspended stays out of the mission and is reported.
2. The ground station loads the mission at the municipal seat or the collection center, and the drone flies with the sprayer off. During the visit the brigade records the field sample of each lot.
3. On return, the station uploads the photos, the flight log and the sample record, as the [drone mission link](../network/drone-mission-link.md) defines. No estimate starts until the platform publishes the flight record.
4. The publication event starts the estimation function. It screens every image for people first. An image with a person goes to the restricted prefix and never reaches inference, and the brigade repeats that capture if the lot loses coverage.
5. The function builds the orthomosaic of each lot, counts productive trees through the managed inference service, reads the field sample, applies the conversion, and writes the result with a conditional write. A repeated event finds the same key and changes nothing.
6. The supervisor reviews the count on a sample of tiles and the field sample, then validates the estimate. Only a validated estimate reaches the center.

When the function fails, it retries three times, then sends the event to the dead letter queue and raises an alarm. The source objects stay, and no estimate changes.

## 5. Result contract

The example uses invented values and identifiers.

```json
{
  "estimate_id": "est-demo-001",
  "farm_id": "farm-demo",
  "harvest_id": "harvest-demo-main",
  "mission_id": "mission-demo-77",
  "method_version": "trees-sample-cenicafe-1",
  "lots": [
    {
      "lot_id": "lot-demo-a",
      "geometry_version": 3,
      "productive_trees": 5000,
      "productive_trees_low": 4800,
      "productive_trees_high": 5200,
      "cherry_kg_per_tree": 2.0,
      "cherry_kg_per_tree_low": 1.7,
      "cherry_kg_per_tree_high": 2.3,
      "sample_trees": 30,
      "sample_ref": "sample-demo-a-1",
      "orthomosaic": {"key": "estimation/farm-demo/lot-demo-a/ortho.tif", "version_id": "v-demo", "sha256": "4f8e2c9b7d1a0e63c5b2f7d8a9e1c3b5d7f9a1c3e5b7d9f1a3c5e7b9d1f3a5c7"}
    }
  ],
  "conversion": {"parchment_per_cherry": 0.20, "range": [0.20, 0.222], "source": "Cenicafe, Avance Tecnico 370"},
  "estimated_sacks": 33,
  "sacks_low": 27,
  "sacks_high": 44,
  "relative_range": 0.26,
  "captured_at": "2026-04-02T15:10:00Z",
  "estimated_at": "2026-04-03T09:00:00Z",
  "status": "VALIDATED",
  "validated_by": "supervisor-demo-02"
}
```

| Field | Rule |
|---|---|
| Farm, harvest and mission | Exactly one planned estimation mission per farm and harvest. A corrective flight links to the original and does not count as another |
| Lots | Each lot with its exact published polygon version, tree count with its range, load per tree with its range and the sample behind it |
| Source objects | S3 key, version and SHA-256 of each orthomosaic, plus the field sample record |
| Conversion | The factor, its range and its source, stored with the result so a later change of factor never rewrites past estimates |
| Result | Estimated sacks of 60 kg of dry parchment, with the low and high values |
| Confidence | `relative_range`, the half width of the range divided by the estimate, together with the range itself |
| Dates | Capture, upload and estimation times in UTC, each kept apart |
| Status | `PENDING`, `REVIEW_REQUIRED`, `VALIDATED` or `FAILED`, with validation by a named supervisor |

A correction creates a new version of the result, linked to the one it replaces. The idempotency key is the mission, the lot and the version of the source object, so a repeated or late event never counts a lot twice.

## 6. What the center sees

The center reads the latest validated estimate of each farm that delivers to it, with the range, the estimation date and the label estimated. It sees totals per farm and per day of expected delivery when the farm reports its picking plan. It does not see photos, inference details or the field samples. The estimate never creates a packing order, a sack, a custody event or any change in the sack history.

## 7. Integrity, privacy and limits

- Photos, orthomosaics, logs and samples stay in the encrypted, versioned bucket for five years.
- An image with a person never reaches inference, and if screening fails or is unavailable, the image waits for review.
- The inference function reads only the estimation prefix and writes only results. Center operators read validated results. Buyers and carriers have no access.
- An estimate is a forecast. Before the second harvest, the team compares each estimate with the sacks actually delivered and adjusts the method, the sample size and the tree count review.
- A lot whose load per tree has no sample and no history gets `REVIEW_REQUIRED` and no number.

## 8. What fails and what the platform does

| Situation | What the platform does |
|---|---|
| A lot of the farm has no published polygon or is suspended | The lot stays out of the mission, and the estimate marks it as not estimated |
| The drone has no signal at the farm | Photos wait on the drone and the station, and no estimate exists yet |
| The flight record is not published | Nothing is estimated |
| The upload arrives days later | The result keeps capture, upload and estimation times apart |
| Events arrive twice or out of order | One result per lot and source version, with no double count |
| An image shows a person | The image goes to the restricted prefix and skips inference. The brigade repeats the capture when coverage matters |
| The function, inference or the write fails | Three retries, then the dead letter queue and an alarm, with no change of state |
| A lot has no field sample and no history | `REVIEW_REQUIRED`, with no number shown to the center |
| The supervisor rejects the tree count | `REVIEW_REQUIRED`, and the count is redone on the orthomosaic or by a repeat flight |
| A validated estimate exists | The center sees sacks, range, date and origin |
| Any business workflow reads the estimate | No packing order, sack event or fumigation is created |
| A new harvest or a corrected source arrives | A new version, with the earlier one kept and nothing counted twice |

## 9. Cost

Rates come from the AWS Price List API for us-east-1, and the inference rate from the managed inference cost of the platform.

| Item | Rate | Volume per harvest | USD per harvest |
|---|---|---|---|
| Person filter and inference | About 1.75 per 1,000 images | 200 farms, at 100 images per farm in this example | About 35 |
| Storage of photos | 0.023 per GB-month | 20,000 images of 3 MB, about 58.6 GB | About 1.35 a month while kept |
| Uploads | 0.005 per 1,000 PUT requests | 20,000 | 0.10 |
| Estimation function | 0.20 per million requests and 0.0000166667 per GB-second | 200 runs of about 5 minutes at 4 GB to build orthomosaics, 240,000 GB-seconds | About 4.00 |
| Result writes | 0.625 per million write request units | A few thousand | Below 0.01 |

The number of images per farm flight is not known before the first flights. At 100 images a farm, the 200 missions add about 5,000 images to each harvest month, inside the 9,000 images a month the operating mode assumes for all drone work. The flights, brigades and field sampling belong to the drone service cost in the operating mode document.

## 10. Assumptions and pending confirmations

| Item | Who confirms | Effect if it fails |
|---|---|---|
| The 60 kg sack holds dry parchment, as it leaves the processing facility | Federation | For green coffee the estimate is multiplied by the Cenicafé factor of 0.80 from parchment to green |
| The brigade can sample trees per lot during the estimation visit | Federation and the certified operator | Estimates wait for the farm history after the first harvest |
| Managed inference counts productive trees on an orthomosaic with a useful error | Agronomy review on the first flights | Tree counts come from the field, and the flight provides only the area |
| The conversion range of Cenicafé holds for the pilot farms | Cenicafé or agronomy review | The factor parameter and its range change |
| A farm flight produces about 100 images | Brigades, on the first flights | Inference and storage cost scale with the real count |
| The acceptable error of an estimate | Federation and the collection centers | The sample size and the review effort change |

## 11. Sources

- Cenicafé, [Physical properties and conversion factors of coffee in processing, Avance Técnico 370](https://biblioteca.cenicafe.org/bitstream/10778/358/1/avt0370.pdf), table 6.
- AWS Price List API, [S3](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonS3/current/us-east-1/index.json), [DynamoDB](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonDynamoDB/current/us-east-1/index.json) and [Lambda](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AWSLambda/current/us-east-1/index.json), us-east-1.
- [Drone operating mode](operating-mode.md), [lot boundaries and exclusion zones](lot-boundaries-and-exclusions.md), [drone mission link](../network/drone-mission-link.md), [managed inference decision](../adr/managed-inference.md) and [personal data and retention](../security/personal-data-and-retention.md) of this platform.
