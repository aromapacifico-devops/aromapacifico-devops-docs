# Port delivery stores the receiver and its receipt, and stays final

## Context

The Federation installs nothing at the port, and the person who receives a sack never signs up to the platform. The delivery ends the record of a sack, and a buyer reads that state. The design needs evidence that adds no personal data with no consent, and a rule for a mistaken delivery.

## Options

For the evidence, the organization and the receipt reference, the name of the person, or a photo of the signed receipt.

For a mistake, a final record with a confirmation step, or a correction event.

## Decision

The event stores the organization that received and the reference of its receipt, along with the location and time, and the carrier stays the responsible person. Delivery remains final. The application asks for confirmation, and a second delivery event becomes an anomaly for review.

## Consequences

The platform holds no personal data of the receiver, and a dispute leads to the document of the receiver. A confirmed mistake stays in the state, and only the review list shows it. If receivers issue no receipt, the evidence falls to the scan and the location.
