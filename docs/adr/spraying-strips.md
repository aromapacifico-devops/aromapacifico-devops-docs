# Drone spraying keeps the aerial safety strips, with ground application as the fallback

## Context

Houses, the processing facility, roads and water sources are places where the drone does not fly, and they must be on the platform before the first flight. Colombia has no safety strip written for drones. The aviation regulation sends drone spraying to the rules of agricultural aviation and to Decree 1843 of 1991, whose article 87 keeps aerial application 100 m and ground application 10 m away from water, trunk roads and human and animal population. Decree 1076 of 2015 protects 100 m around springs. RAC 100 keeps drones 30 m from people outside the operation. A strip of 100 m around a single house covers about 3.1 ha.

## Options

The legal values as versioned parameters with a ground fallback, operating ranges narrower than the rules where no rule was found, or 100 m for everything with no fallback.

## Decision

The four places are always no-fly zones. No-spray strips use the legal values, stored as versioned parameters for each type of place. When a focus falls inside the drone strip and outside the ground strip of 10 m, the order becomes a ground application by the brigade with the same authorization. Inside the ground strip no product is applied. Minor roads and narrower water strips have no value until a legal review confirms one.

## Consequences

Every distance in the design rests on a rule, and a legal answer changes a parameter and nothing else. Foci near houses and water stay treatable. The brigade carries ground spraying equipment, and the fumigation order records whether it is applied by drone or on foot. The 100 m strip may prove stricter than the authority requires.
