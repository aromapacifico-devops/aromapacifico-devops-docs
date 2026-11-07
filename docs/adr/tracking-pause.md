# Each leg is a trip, and the carrier pauses tracking outside working hours

## Context

The position of a carrier is personal data. Tracking ran through an open trip, and a trip of two days would record where a person sleeps, while the volumes of the pilot assume 10 hours a day. A trip must also end at a defined moment on each leg, and a leg to a center never has a delivery.

## Options

For tracking outside working hours, a pause by the carrier with a reminder, continuous tracking during an open trip, or an automatic time window.

## Decision

Each leg is a separate trip, which closes with data the phone already holds. The carrier pauses tracking with one action, and the application reminds the carrier after 10 hours. The pause is recorded, so a break in the route explains itself, and the sacks stay in custody.

## Consequences

The platform follows a person only while working. A carrier can forget to pause, or pause while driving, and that leaves a visible gap. If gaps turn out to be common, an automatic window could join the pause.
