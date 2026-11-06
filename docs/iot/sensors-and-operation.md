# Sensors and operation

Each farm has one autonomous node with probes for its cultivation and drying zones. The node tells the farmer what is happening and needs almost no attention.

## What the node measures

| Zone | Variable | Sensor | Cadence |
|---|---|---|---|
| Cultivation | Nitrogen, phosphorus and potassium | RS485 multiparameter soil probe | Every 4 hours, all day |
| Cultivation | Soil pH | Same probe | Every 4 hours, all day |
| Cultivation | Soil humidity and temperature | Same probe | Every 4 hours, all day |
| Cultivation | Air humidity and temperature | Climate sensor | Every 4 hours, all day |
| Drying | Grain temperature and humidity | Grain probe | Hourly, while a lot is drying |

The farmer starts and stops the drying cadence from the application. When no lot is drying, the probe stays idle and saves energy.

## Volumes

| Stream | Calculation | Readings a day |
|---|---|---|
| Cultivation | 200 farms × 6 readings | 1,200 |
| Drying in harvest | 100 farms × 24 readings | 2,400 |
| Carrier positions | 60 carriers × 12 positions × 10 hours | 7,200 |

## pH

The soil probe measures pH with the other soil variables, so the pH alert works with no task for the farmer. The farmer application accepts a manual reading when the probe fails.

## Alert ranges

The Federation configures ranges on the platform, and the node holds none. Initial values follow.

| Variable | Cultivation alert | Drying |
|---|---|---|
| pH | Outside 4.5 to 6.0, recommended 4.9 to 5.6 | Not applicable |
| Humidity | Outside 40 to 80 percent | Lot closes near 12 percent |
| Temperature | Outside 14 to 30 °C, recommended 17 to 23 °C | Grain above 40 °C |
| Nitrogen, phosphorus, potassium | Outside the range the Federation publishes | Not applicable |

## Daily operation

The node wakes on schedule, reads its probes and publishes. Without a signal it stores the reading and retries at the next cycle. The buffer retains 24 hours at most, and when a reading passes that limit the node discards it and counts the loss in its next message.

The farmer receives an alert in the application, written in plain language. The node needs no action unless the application reports it as silent for more than 24 hours.
