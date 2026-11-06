# The drone service combines area and precision work

## Context

The five services are lot delimitation, alert confirmation, fumigation, verification and harvest estimation. None can replace another.

## Options

Precision only, area only, or a combination.

## Decision

The service uses a combination. Area work delimits the lot and estimates the harvest. Precision work confirms the focus, fumigates it and verifies that same lot.

A lot polygon published on the platform is the event that passes a lot from area to precision work. Without it, no precision mission can be issued for that lot.

## Consequences

Drones fly to foci marked by a sensor and skip blanket sweeps, which reduces flight hours. A farm with no polygon cannot receive a fumigation order, so delimitation flights come first in each department.
