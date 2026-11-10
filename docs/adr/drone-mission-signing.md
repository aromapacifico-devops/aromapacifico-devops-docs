# Drone mission packages and flight results are signed

## Context

A mission package is downloaded at a municipal seat or a collection center and then sits on a ground station with no connection until the flight. TLS protects the download and stops protecting the package once it is stored. On return, the platform must know which station delivered a flight result before it publishes the flight record. Each ground station already holds an X.509 certificate of its own for IoT Core.

## Options

For the package, a signature made with an asymmetric KMS key, or a list of hashes delivered over TLS. For the station, a signature on each result manifest made with its device key, or mutual TLS on the mission API.

## Decision

The platform signs each package with one elliptic curve KMS key, and the station and the drone adapter verify it offline with the public key. The station signs each result manifest with the private key of its device certificate, and the platform checks that signature against the certificate in the IoT registry. The operator still signs in with Cognito and a second factor.

## Consequences

A package altered on the station fails its check before takeoff. Revoking a station certificate stops its IoT access and its ability to publish flights in one step. The signing key costs USD 1 a month. Mutual TLS was discarded because the API would need a private certificate authority, at USD 400 a month plus USD 0.75 per certificate, next to the issuer IoT Core already provides. The ground application must hold the device key and sign with it, and a rotation of the signing key must reach every station before the first package signed with the new key.
