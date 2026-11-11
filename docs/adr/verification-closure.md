# A fumigation reaches verified only with stored photos and a persisted result, and only a person closes it

## Context

A fumigation must stay open until a photo or a short path proves the result, and a failed function on that evidence must leave the state as it was. The fumigation order already ends only through the verification, and a supervisor signs the closure. Three choices remained open. They were what moves the order to verified, who verifies a ground application, and what form a short path takes.

## Options

For the move to verified, a stored flight record alone, a stored record plus a result the function persists, or that same pair with no manual path when inference fails. For a ground application, a drone verification flight or photos from the phone of the brigade that sprayed. For a short path, a line of still photos or a short video.

## Decision

The order moves to verified when the verification flight record is published and the verification function has persisted a result marked closable for that attempt. When inference of an attempt reaches the dead letter queue, the supervisor can record the result from the photos. Every verification is a drone flight, whatever the method of the application. A short path is a line of still photos across the applied area, so both capture modes use the same person filter, model and price per image.

## Consequences

A missing photo, a failed flight, a failed invocation or a low coverage leaves the order open, and a model outage never closes an order and never keeps all of them open. The state machine gains one human move, 41 in total. The brigade that sprayed never produces the evidence that closes its work, and the flights are already counted in the drone service cost. Video would need another filter and another function, and it returns if the agronomy review finds still photos insufficient.
