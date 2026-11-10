# The design never depends on 2G or 3G, and the modem is chosen with the operator

## Context

The farm node, the shared LoRaWAN gateway and the phones use mobile networks. The regulator says that there is no national schedule to retire 2G or 3G and that each operator decides when and where, so a network could be switched off during the pilot with the notice that the rules require. The public datasets list some 4G area in nearly every municipal seat of Cauca, Huila and Tolima for three operators, which counts seats with any reported area and measures no service. They show nothing about LTE-M or NB-IoT, nothing about signal at a farm, and nothing about the bands of a device. The [mobile network validity](../network/mobile-network-validity.md) document holds the sources, their dates and what each one proves.

## Options

The design depends on 4G only, with no fallback to 2G or 3G. The design depends on LTE-M or NB-IoT only. The decision is left open until a modem is chosen.

## Decision

The design never depends on the availability of 2G or 3G, and a modem must work on 4G networks with no fallback to them. LTE-M and NB-IoT are candidates for the farm node when the operator confirms availability, coverage, the contracted service and the compatibility of the device. A conventional LTE category can also be evaluated, and no 4G modem is approved by default. The choice weighs the bands and the category that the operator supports, the energy use and the autonomy of the solar node, the protocols and the capacity of the exchange, the antenna, the site and the behavior with no signal, and the availability and cost of the data plan. The selection of the hardware belongs to the specification of the autonomous node. The same rule applies to the cellular backhaul of the shared gateway, and the LoRa path of the farms out of coverage stays as it is.

## Consequences

The design survives the retirement of 2G and 3G. It leaves open which modem and which plan the pilot uses, and that depends on confirmations from the Federation and the operators that this decision does not replace. LTE-M and NB-IoT lower energy use if an operator provides them, and until it does, a conventional LTE modem costs more energy. A new announcement of a retirement of 4G, or an operator statement that contradicts the sources of the validity document, would reopen this decision.
