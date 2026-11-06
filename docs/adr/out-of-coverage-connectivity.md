# Out-of-coverage farms use a shared gateway for readings and a data mule for objects

## Context

Some pilot farms have no cellular signal. Their readings and objects must arrive with no new base station and no weekly visit, and the local buffer retains 24 hours at most.

## Options

A shared LoRaWAN gateway, a satellite modem on each farm, and a data mule alone.

## Decision

Farm nodes send readings over LoRa to a LoRaWAN gateway shared by the vereda, placed at a high point with cellular signal. Objects, which are too large for LoRa, travel by data mule along existing daily routes and enter at the municipal seat or the collection center.

## Consequences

One gateway serves several farms, which keeps the cost per farm low. Each gateway needs a site survey and its own power. A vereda with no line of sight to any point with signal needs another link, and the design treats that as an exception to be quoted.
