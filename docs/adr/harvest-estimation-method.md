# Harvest estimates come from a tree count, a field sample and the Cenicafé factor

## Context

A collection center needs to know how many 60 kg sacks each farm will bring. An aerial image shows canopy and hides most of the fruit, so an image alone cannot give a defensible number of sacks. Cenicafé publishes the conversion from cherry to dry parchment, about 0.20 kg of dry parchment for each kilogram of cherry.

## Options

A direct estimate of sacks by managed inference on the images, validated by a person, or a tree count from the images joined with a field sample of the load per tree. For the scope, one mission per farm or one mission per lot.

## Decision

Inference counts productive trees on the orthomosaic of each lot. The brigade samples the load per tree during the same visit, and the farm history replaces or checks the sample after the first harvest. The platform applies the Cenicafé factor with its range and divides by 60 kg. One mission per farm and per harvest covers all its published lots and keeps the detail of each lot.

## Consequences

Each step can be measured and compared with the sacks the platform records at delivery. The center receives one figure per farm with a range. The brigade spends time sampling trees on each estimation visit. The estimate assumes the sack holds dry parchment, and a green coffee sack would need the factor of 0.80.
