# pH is measured by the soil probe

## Context

Alert ranges include pH, while the list of measured crop variables leaves it out. The alert needs a source.

## Options

Field measurement by the probe, or a manual reading entered in the farmer application.

## Decision

The multiparameter RS485 soil probe measures pH with nitrogen, phosphorus, potassium, humidity and temperature, every four hours. The farmer application accepts a manual reading as a fallback when the probe fails.

## Consequences

The alert works with no extra task for the farmer. Probe accuracy for pH depends on calibration, which the installation visit covers.
