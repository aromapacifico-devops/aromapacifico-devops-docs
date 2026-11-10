# Alert ranges are versions judged by the time of the reading

## Context

The Federation changes alert ranges from the platform, and every change must be audited. A reading can reach the platform up to 24 hours after it was measured. The pilot names crop humidity and temperature without saying soil or air, and the node measures both. Cenicafé gives the coffee zone a mean air relative humidity of 70 to 85 percent and a mean air temperature of 18 to 22.5 °C.

## Options

Ranges for the whole Federation kept as versions in one table, or configurations for each farm and lot. For the bindings, humidity on the soil and temperature on the air, or no alert until the Federation decides.

## Decision

The ranges table keeps every version of each range, and a reading is judged by the version in force at its measured time. A change is a new version published through the platform API and audited, and a rollback is a new version too. Ranges apply to the whole Federation in the pilot. Crop humidity applies to the soil and crop temperature to the air.

## Consequences

A late reading gets the result it would have had on time, and no change rewrites history. Ranges for one farm or lot would add a scope to the table after the pilot. An upper limit of 80 percent on air humidity would have alerted on ordinary days, which the binding to the soil avoids.
