# Inference cost per 1,000 invocations in harvest

The platform analyzes crop images and archived telemetry with four event-driven functions. This document gives what that analysis costs for every 1,000 invocations in a harvest month and what it costs in the whole month, with the volume of each trigger derived from the pilot figures. One thousand images analyzed in harvest cost USD 1.89, and an average harvest month costs USD 16.26. The month in which every farm flies its harvest estimation reaches USD 45.95. The figures come from a script that reads the published rates and the volumes, so a change of either can be recomputed.

## Contents

1. Terms
2. What counts as one invocation
3. Volume of each trigger
4. Cost of one image
5. Cost per 1,000 invocations and per month
6. How the figures compare with the other cost documents
7. What moves the cost
8. Alternatives discarded
9. Assumptions and pending confirmations
10. Sources

## 1. Terms

| Term | Meaning in this document |
|---|---|
| Image invocation | One image through the person filter and, when no person is found, one call to the vision model |
| Function invocation | One completed run of an inference function on one message of its work queue, which is one published flight record or one archived telemetry object |
| Trigger | The event that starts a function. A published flight record of a given mission type, or a completed telemetry object |
| Harvest month | A month of the harvest with the monthly review campaign, the fumigations it opens and a quarter of the harvest estimation flights |
| Normal month | A month outside the harvest, with the cases that sensor alerts open and no estimation flight |
| Person filter | Rekognition DetectLabels applied before the model. An image with a person never reaches the model |
| Vision model | Amazon Nova 2 Lite on Bedrock, called through its US cross-Region profile |

## 2. What counts as one invocation

The platform reports two units, because one function run can analyze one photo or one hundred.

The **image invocation** is the headline unit. It is the unit that drives the bill, since the person filter and the model call are charged per image, and the cost of every other piece of a run is small next to them. It also stays the same whichever mission produced the image, so it compares directly with a quote or with another model.

The **function invocation** is the unit of each trigger. A focus confirmation flight of 50 photos, a verification of 20, an estimation of 100 with its orthomosaic and an archived telemetry object with no model call are four very different runs. Each trigger therefore has its own cost per 1,000 function invocations in section 5. A single figure that blended the four would be set by the telemetry objects, which are the most numerous and the cheapest, and it would say little about the vision cost.

## 3. Volume of each trigger

The volumes come from the pilot figures and from the mission and function designs. They are planning figures, and the first harvest replaces them with counted ones.

| Trigger | Harvest month | Normal month | Derivation |
|---|---:|---:|---|
| Focus confirmation flight | 60 | 15 | About 40 confirmed foci in a harvest month and 10 in a normal month, plus half again for flights that discard the alert or repeat a capture |
| Photos in each focus confirmation | 50 | 50 | Planning figure of the focus mission |
| Verification flight | 25 | 6 | One for each fumigation order, about 25 in a harvest month and 6 outside it |
| Photos in each verification | 20 | 20 | Planning figure of the verification mission |
| Harvest estimation flight | 50 | 0 | One flight for each of the 200 farms in each harvest, spread over four harvest months |
| Photos in each estimation | 100 | 100 | Planning figure of the estimation mission |
| Telemetry readings | 108,000 | 50,400 | 200 farms with 6 crop readings a day, and in harvest about 100 farms drying with 24 readings a day, over 30 days |
| Telemetry objects | Up to 5,760 | Up to 5,760 | The archive stream writes one object for each of the crop and drying streams in each 900-second window, 96 windows a day for 30 days |

The images that reach a function in a harvest month are therefore 3,000 for focus confirmation, 500 for verification and 5,000 for harvest estimation, 8,500 in all. A normal month has 750 and 120, 870 in all.

The drone operating mode counts about 9,000 drone images in a harvest month. That count includes the photos of the fumigation flights themselves, which document the application and start no inference, and it uses a single average of photos for every precision mission. The inference count keeps only the images a function analyzes, by trigger, so it is lower.

The telemetry object count is an upper bound. A window in which a stream receives no reading writes no object, so drying readings that arrive on the hour leave three of every four windows of their stream empty. The cost of an object is a fraction of a cent, so the bound changes the month by cents.

## 4. Cost of one image

Rates are the on-demand prices of the AWS Price List API for us-east-1, in USD before tax. The model runs through the US cross-Region profile of Nova 2 Lite called from us-east-1. Bedrock charges a cross-Region call at the price of the Region that makes the call and adds no routing charge, so the us-east-1 rates apply whichever of the three US Regions answers.

| Item | Rate | Price list entry |
|---|---:|---|
| Nova 2 Lite input tokens | USD 0.00033 per 1,000 | Bedrock, `FY8T82UUN7VZR55K` |
| Nova 2 Lite output tokens | USD 0.00275 per 1,000 | Bedrock, `DY69Q8C3F88CHA2Q` |
| Rekognition DetectLabels | USD 0.001 per image up to 1 million a month | Rekognition, `4R796AUWKTWNVC3X` |
| Lambda requests | USD 0.0000002 per request | Lambda, `GU2ZS9HVP6QTQ7KE` |
| Lambda x86 compute | USD 0.0000166667 per GB-second | Lambda, `TG3M4CAGBA3NYQBH` |
| SQS standard requests | USD 0.40 per million | SQS, `8RN6B8U4MERHRXP3` |
| EventBridge custom events | USD 1.00 per million | EventBridge, `ZA92ERYNKX457AJD` |
| DynamoDB on-demand writes | USD 0.625 per million write units | DynamoDB, `FGXVD96DKJMUASY3` |
| DynamoDB on-demand reads | USD 0.125 per million read units | DynamoDB, `4W4ZMC46EHE8XTTZ` |
| S3 GET requests | USD 0.004 per 10,000 | S3, `ZWQ6Q48CRJXX4FXE` |
| S3 PUT requests | USD 0.005 per 1,000 | S3, `E9YHNFENF4XQBZR6` |

Nova 2 bills every image at a flat 230 input tokens, whatever its resolution. Each call adds a short versioned instruction of about 50 text tokens and returns a compact result of about 240 tokens. The function spends about 5 seconds on each image at 256 MB, reads the exact object version once and writes one result item under 1 KB.

```text
Model    (230 + 50) x 0.00033 / 1,000 + 240 x 0.00275 / 1,000 = 0.0007524
Filter                                                         = 0.0010000
Function 5 s x 0.25 GB x 0.0000166667                          = 0.0000208
Read and write  0.0000004 + 0.000000625                        = 0.0000010
One image                                                      = 0.0017743
```

| Part of one image | USD |
|---|---:|
| Person filter | 0.0010000 |
| Model call | 0.0007524 |
| Function time | 0.0000208 |
| Object read and result write | 0.0000010 |
| One image | 0.0017743 |
| 1,000 images | 1.7743 |

The person filter is more than half of the cost of an image. It is also the control that keeps any person out of the model, so the design keeps it on every image and looks for savings elsewhere.

An image with a person stops after the filter and costs USD 0.001. The figures count every image as reaching the model, which is the upper bound.

## 5. Cost per 1,000 invocations and per month

Each function invocation adds the fixed pieces of one run to the cost of its images. These are one Lambda request, the queue send, receive and delete, and for a drone flight the published flight record event and the completion event. Harvest estimation also builds an orthomosaic in about 5 minutes at 4 GB and stores about 100 PNG tiles and the TIFF. A telemetry object costs one second of function time at 256 MB, a write for each reading and up to eight range lookups of half a read unit for each reading. Its storage event reaches EventBridge as an event of an AWS service, which carries no charge.

| Harvest month | Invocations | Images | USD per 1,000 invocations | USD in the month |
|---|---:|---:|---:|---:|
| Focus confirmation | 60 | 3,000 | 88.72 | 5.32 |
| Verification | 25 | 500 | 35.49 | 0.89 |
| Harvest estimation | 50 | 5,000 | 197.93 | 9.90 |
| Telemetry batch | 5,760 | 0 | 0.03 | 0.16 |
| Total | 5,895 | 8,500 | 2.76 | 16.26 |
| Vision functions per 1,000 images | | | 1.8949 | |

| Normal month | Invocations | Images | USD per 1,000 invocations | USD in the month |
|---|---:|---:|---:|---:|
| Focus confirmation | 15 | 750 | 88.72 | 1.33 |
| Verification | 6 | 120 | 35.49 | 0.21 |
| Harvest estimation | 0 | 0 | 197.93 | 0.00 |
| Telemetry batch | 5,760 | 0 | 0.02 | 0.09 |
| Total | 5,781 | 870 | 0.28 | 1.63 |
| Vision functions per 1,000 images | | | 1.7743 | |

In harvest, 1,000 images cost USD 1.89 once the orthomosaic and the run overhead are spread over them, against USD 1.77 for the image alone. Outside harvest there is no estimation flight, so the two figures match.

The harvest estimation is the largest line because it carries 5,000 of the 8,500 images and the orthomosaic. Each farm flies it once a harvest, so the month in which the flights fall decides the peak.

| Harvest month | USD in the month |
|---|---:|
| Estimation flights spread over four months, 50 in the month | 16.26 |
| All 200 estimation flights in one month | 45.95 |

A harvest of four months with the flights spread evenly costs USD 65.04 in inference. A harvest in which all estimation flights happen in the first month costs USD 45.95 in that month and USD 6.37 in each of the other three, about USD 65.05 in all. The total of the harvest hardly changes. Only the monthly budget line must hold the peak.

The figures are reproduced with this command, which also checks that every table of this document matches the computation.

```bash
python3 docs/governance/tools/inference_cost.py --check
```

## 6. How the figures compare with the other cost documents

| Document | Figure it shows for inference in harvest | Why it differs |
|---|---|---|
| [Monthly cloud cost](cloud-cost.md) | USD 16.26 in an average harvest month | It takes the figure of this document |
| [Inference functions](../architecture/inference-functions.md) | USD 16.05 in an average harvest month | It prices the image without function time and counts fewer telemetry objects |
| This document | USD 16.26 in an average harvest month, USD 45.95 at the estimation peak | It counts each trigger and every billed piece of a run |

The three figures agree within USD 0.21 for an average harvest month. The monthly cloud cost and the [pilot cost](pilot-cost.md) take the figures of this one for their inference line, and the pilot cost holds the estimation peak as the monthly ceiling of that line.

## 7. What moves the cost

| Change | Effect on an average harvest month |
|---|---|
| Twice the photos in every flight | USD 15.08 more, since cost follows images almost one to one |
| 100 output tokens instead of 240 | USD 3.27 less. The result format is the lever on the model line |
| Rekognition free tier of 5,000 images a month, if the account had it | USD 5.00 less. The cost documents assume no free tier |
| Global cross-Region profile, about 10 percent cheaper on the model | About USD 0.64 less. Rejected, because a global profile may process images outside the United States |
| Function time of 15 seconds per image instead of 5 | USD 0.35 more |
| The telemetry objects at a quarter of the bound | USD 0.03 less, since the reading writes and range lookups stay |

## 8. Alternatives discarded

| Alternative | Why it was discarded |
|---|---|
| A single cost per 1,000 function invocations for all triggers | The 5,760 telemetry objects would set it near USD 2.76, a figure that hides that a focus flight costs USD 0.09 and an estimation flight USD 0.20 |
| Pricing the model by the actual image resolution | Nova 2 bills a flat 230 tokens per image, so resolution changes the result quality and leaves the cost unchanged |
| Counting all 9,000 drone images | The fumigation photos never reach a function, so they would add cost that does not exist |
| Bedrock batch inference, half the token price | It runs jobs that may take hours, while a focus confirmation must reach the reviewer the same day. It would save about USD 3.20 of model cost in an average harvest month |
| Skipping the person filter on estimation photos taken from altitude | It keeps a person out of the model on every image, and the privacy design forbids any exception |

## 9. Assumptions and pending confirmations

| Assumption | Why it is reasonable | If false | Confirms |
|---|---|---|---|
| About 50 photos cover a focus, 20 a verification and 100 an estimation | They come from the mission designs and the pilot size | Cost follows the photo count almost one to one | Brigades, on the first flights |
| 60 focus confirmation flights produce 40 confirmed foci in a harvest month | Half again covers discarded alerts and repeated captures | The focus line moves in proportion, at USD 0.09 a flight | Platform operator, after the first harvest |
| Each image takes about 5 seconds at 256 MB inside the function | One filter call, one model call and one write, with the SDK retries of the failure policy | Function time moves in proportion and stays under 2 percent of the image cost | Platform operator, from the duration in the test environment |
| Each model call uses about 50 text input tokens and 240 output tokens | A short versioned instruction and a compact result | The model line moves in proportion, while the filter stays fixed | Platform operator, from the token usage returned by the first calls |
| The estimation tiles that reach the model are about as many as the source photos | The orthomosaic covers the same area, cut into tiles the model accepts | The estimation line moves with the tile count | Platform operator, on the first estimation flight |
| No free tier applies to the account | The cost documents price at list | Rekognition and Lambda lines fall | Owner of the cost document |

## 10. Sources

- AWS Price List API for us-east-1, [Bedrock](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonBedrock/current/us-east-1/index.json), [Rekognition](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonRekognition/current/us-east-1/index.json), [Lambda](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AWSLambda/current/us-east-1/index.json), [SQS](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AWSQueueService/current/us-east-1/index.json), [EventBridge](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AWSEvents/current/us-east-1/index.json), [DynamoDB](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonDynamoDB/current/us-east-1/index.json) and [S3](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonS3/current/us-east-1/index.json).
- [Amazon Nova 2 multimodal understanding](https://docs.aws.amazon.com/nova/latest/nova2-userguide/using-multimodal-models.html), the flat 230 tokens billed for each image.
- [Bedrock cross-Region inference](https://docs.aws.amazon.com/bedrock/latest/userguide/cross-region-inference.html), price of the source Region with no routing charge, and the global profile saving.
- [Inference functions](../architecture/inference-functions.md), [inference Region and data leaving the country](../security/inference-data-egress.md), [drone operating mode](../drones/operating-mode.md), [failure policy](../architecture/failure-policy.md), [monthly cloud cost](cloud-cost.md) and [price basis](price-basis.md) of this platform.
