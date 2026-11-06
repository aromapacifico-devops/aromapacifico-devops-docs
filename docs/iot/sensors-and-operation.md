# Sensors and operation

This document defines what the farm node measures, how often, how pH is handled, and how the node operates on solar power in a single-visit installation. It answers what the farmer needs to understand about the alerts, and it gives the volumes the ingestion design takes as input.

## Contents

1. What the node measures
2. Volumes
3. pH
4. Alert ranges
5. Hourly cycle
6. Energy
7. Buffer
8. Installation in one visit
9. Environment
10. What the farmer sees
11. Assumptions and pending confirmations

### Terms used

| Term | Meaning in this document |
|---|---|
| Node | The enclosure with controller, modem, buffer and battery |
| Probe | The part in contact with soil, air or grain |
| Cycle | One wake-up to read and publish |
| Peak sun hours | Hours a day at full solar output, a way to measure usable sun |

---

## 1. What the node measures

| Zone | Variable | Sensor | Cadence |
|---|---|---|---|
| Cultivation | Nitrogen, phosphorus, potassium | RS485 multiparameter soil probe | Every 4 hours, all day |
| Cultivation | Soil pH | Same probe | Every 4 hours, all day |
| Cultivation | Soil humidity and temperature | Same probe | Every 4 hours, all day |
| Cultivation | Air humidity and temperature | Climate sensor | Every 4 hours, all day |
| Drying | Grain temperature and humidity | Grain probe | Hourly, while a lot is drying |

One multiparameter probe was chosen over separate sensors, because each extra sensor adds cost, wiring and failure points to a site that is hard to reach.

The farmer starts and stops the drying cadence from the application, and the node picks up the change at its next hourly connection. Outside drying, the probe stays idle, which saves energy and avoids readings with no use.

## 2. Volumes

| Stream | Calculation | Readings a day | Readings a month |
|---|---|---|---|
| Cultivation | 200 farms × 6 readings | 1,200 | 36,000 |
| Drying in harvest | 100 farms × 24 readings | 2,400 | 72,000 |
| Drying in a normal month | About 20 farms × 24 readings | 480 | 14,400 |
| Carrier positions, for reference | 60 carriers × 12 positions × 10 hours | 7,200 | 216,000 |

A reading fits in about 0.5 KB, so the payload of a farm stays under 15 KB on the busiest day. Each connection also costs TLS and MQTT overhead, which brings the total to about 5.5 MB a month. The data plan can stay very small, which suits a moderate fee. [Farm connectivity](../network/farm-connectivity.md) shows the calculation.

## 3. pH

The alert ranges include pH, while the list of crop variables leaves it out, so the design had to choose a source.

| Option | For | Against |
|---|---|---|
| Measured by the probe | Automatic, same cadence, no task for the farmer | Depends on calibration |
| Manual reading in the application | No extra hardware | A task for the farmer, and alerts depend on it |

The probe measures pH, and the application accepts a manual reading as a fallback when the probe fails.

## 4. Alert ranges

The Federation configures ranges on the platform and the node holds none. A change reaches the next evaluation with no visit and no firmware update.

| Variable | Cultivation alert | Drying |
|---|---|---|
| pH | Outside 4.5 to 6.0, recommended 4.9 to 5.6 | Not applicable |
| Humidity | Outside 40 to 80 percent | Lot closes near 12 percent |
| Temperature | Outside 14 to 30 °C, recommended 17 to 23 °C | Grain above 40 °C |
| Nitrogen, phosphorus, potassium | Outside the range the Federation publishes | Not applicable |

## 5. Hourly cycle

| Step | Action |
|---|---|
| 1 | The controller wakes each hour, at a minute fixed for the node |
| 2 | If a reading is due, it powers the probes, waits for them to stabilize and reads them |
| 3 | It writes the reading to the buffer with its time and sequence number, and deletes records of age 24 hours or more |
| 4 | It powers the modem and connects, within 120 seconds |
| 5 | It publishes everything in the buffer, oldest first, with delivery confirmation |
| 6 | It deletes what was confirmed, reads its configuration and sleeps |

The node reads first and publishes after. A failed connection then loses nothing, and the reading waits for the next hour.

Time comes from the network at each connection, with NTP as a fallback, and a real-time clock on backup power keeps it during sleep. A reading stored in the buffer keeps its measured time.

## 6. Energy

There is no reliable power at the lot, so the node must live on its solar kit.

| Item | Value |
|---|---|
| Battery | 12.8 V, 12 Ah, 153.6 Wh |
| Target autonomy with no sun | 5 days |
| Average power that autonomy allows | 1.28 W |
| Daily energy that autonomy allows | 30.7 Wh |
| Panel | 20 W |
| Panel output with 3 peak sun hours | 60 Wh a day |

The panel covers about twice the daily budget with 3 peak sun hours, which leaves margin to recharge after cloudy days. Since the controller sleeps most of the time, real consumption should sit under this budget. The hourly connection takes about 0.45 Wh a day, and 1.2 Wh with every attempt failing, at an assumed 1.5 W on the modem. Field measurement must confirm that with the chosen modem.

## 7. Buffer

The buffer retains 24 hours at most. Storage is not the limit, since 64 MB of flash far exceeds the 15 KB of a busy day. The limit is a rule of the pilot, because an older reading no longer supports a timely decision.

| Situation | Behavior |
|---|---|
| Signal returns within 23 hours | Everything publishes, oldest first |
| Reading reaches 24 hours | The node deletes it before connecting and adds it to `dropped_total` |
| Next successful message | Reports the running total of lost readings |

The platform therefore knows what is missing and when. A silent node for more than 24 hours raises an alarm.

## 8. Installation in one visit

| Step | Action | Time |
|---|---|---|
| 1 | Fix the mast and panel | 30 min |
| 2 | Bury the soil probe and fix the climate sensor | 20 min |
| 3 | Place the grain probe in the drying zone | 10 min |
| 4 | Power on, check the signal, the port the carrier allows and the first reading on the platform | 15 min |
| 5 | Link the node to the farm and show the application to the farmer | 25 min |

Times are estimates to validate in the first installations. The kit arrives assembled, and the installer needs no special tools.

## 9. Environment

| Condition | Response |
|---|---|
| High humidity and rain | IP67 enclosure |
| High temperature | Controller and LiFePO4 battery rated for the range |
| Animals and tools | Buried cable and mast height |

## 10. What the farmer sees

The farmer distrusts leaving the notebook, so the application stays simple. It shows the state of the farm, the alerts in plain language and the history. Numbers appear on request.

| Example alert | Meaning |
|---|---|
| "Grain temperature is above 40 °C in your drying lot" | Act now |
| "Soil humidity in your crop is below the range" | Check at your next visit |

## 11. Assumptions and pending confirmations

| Item | Who confirms | Effect if it fails |
|---|---|---|
| One node reaches both zones with wired probes | Site survey | A second small node per farm |
| 3 peak sun hours or more on an average day in these departments | Field data | A larger panel or battery |
| About 20 farms dry lots in a normal month | Federation | Monthly volume changes, cost barely moves |
| The probe's pH holds calibration for a harvest | Probe supplier | Calibration visits or more manual readings |
