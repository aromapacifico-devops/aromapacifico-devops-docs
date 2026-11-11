# Inference Region and data leaving the country

This document states where the managed inference of the platform runs, which objects and fields leave Colombia toward it, and what happens to an image that shows a person. It completes the [personal data](personal-data-and-retention.md) rules for the four [inference functions](../architecture/inference-functions.md) and gives the controls that keep every call inside the United States.

## Contents

1. Where each service runs
2. What leaves the country
3. What reaches each service
4. Images that show a person
5. Controls
6. Statement for the privacy notice
7. Cost
8. Assumptions and pending confirmations
9. Sources

## 1. Where each service runs

| Service | Use | Region where it runs | What AWS may keep and where |
|---|---|---|---|
| S3 | Flight objects, photos, results and the restricted prefix | us-east-1 | The stored objects, under the five-year rules |
| Rekognition DetectLabels | Person filter on every image | us-east-1 | Image inputs, for service improvement, unless the account opts out (section 5) |
| Bedrock, Nova 2 Lite | Vision analysis of crop images | Called in us-east-1 through the US profile `us.amazon.nova-2-lite-v1:0`, processed in us-east-1, us-east-2 or us-west-2 | Prompts and outputs, if stored for abuse detection, in the Region that processed them |
| Lambda | The four functions | us-east-1 | Logs in us-east-1 |

Nova 2 Lite has no in-Region use in us-east-1. It answers only through a cross-Region profile, either the US profile or a global one that routes to commercial Regions on several continents. The platform uses the US profile only. Requests between Regions travel on the AWS network and never cross the public internet, and CloudTrail records every call in us-east-1.

AWS states that Bedrock inputs and outputs are not shared with model providers and are not used to train Amazon Nova or any other model.

Telemetry reconciliation calls no managed model. Its batch stays in the account and in us-east-1.

## 2. What leaves the country

Every record of the platform lives in us-east-1, because no Region of the provider is in Colombia. All the objects a drone or a node produces therefore leave the country when they are uploaded, and the [personal data](personal-data-and-retention.md) rules, in their section on transfer abroad, give the legal basis.

Inference adds two moves inside the United States and no other country.

| Object | Leaves Colombia | Moves again for inference |
|---|---|---|
| Focus confirmation photos | Yes, at upload to us-east-1 | Pixels to Rekognition in us-east-1. Pixels with no metadata to Bedrock in one of three US Regions, only if no person is found |
| Verification photos | Yes, at upload | Same as focus confirmation |
| Harvest estimation images and their tiles | Yes, at upload | Each source image goes through the person filter before stitching. Tiles of the derived map go to Bedrock |
| Flight log and flight record | Yes, at upload | No |
| Telemetry batch | Yes, at ingestion | No |
| Image that shows a person | Yes, at upload | Rekognition only, then the restricted prefix. Never Bedrock |

## 3. What reaches each service

**Rekognition** receives the exact stored version of each image, read from S3 inside us-east-1. It returns labels and confidences, and the function keeps only the person decision and its confidence.

**Bedrock** receives the image pixels and a pinned prompt, nothing else.

- The function decodes the image and encodes the pixels again before the call, so EXIF, XMP and GPS fields never reach the model. The stored source object keeps its metadata, and the flight record already holds the positions.
- The prompt carries no farm, lot, case, farmer, operator or drone identifier. The result envelope ties the answer to the source object after it returns, inside the account.
- Model invocation logging stays off, so the account keeps no copy of images or prompts in logs. The result envelope records the model and prompt versions instead.

## 4. Images that show a person

The images of the pilot show crops, and a drone may still capture a worker or a neighbor. The person filter is itself an analysis of the image, so the image with the person does reach Rekognition, in the same Region where it is stored. It never reaches Bedrock.

| Step | What happens |
|---|---|
| 1 | DetectLabels runs on the exact image version |
| 2 | A person above the confidence threshold stops the image. No Bedrock call is made |
| 3 | The function copies the image to the restricted prefix, verifies the copy and removes the source version |
| 4 | The case records that the image was withheld, and its state does not change |
| 5 | The drone operator repeats the capture if the case still needs coverage |
| 6 | A lifecycle rule deletes the restricted copy after 30 days, unless an incident holds it |

The restricted prefix produces no thumbnail, tile or derived map, and no function reads it. Only the platform operator can read it, and every read is recorded as a CloudTrail data event in the [audit](audit.md) store. A harvest map is stitched only from images that passed the filter.

The confidence threshold starts low, since a false positive costs a repeated photo and a false negative sends a person to the model. Review with real images sets its final value.

## 5. Controls

| Control | What it ensures | Available in |
|---|---|---|
| Function role | Allows only the US profile and the foundation model in its three destination Regions | Demonstration and pilot |
| Service control policy [`deny-global-inference.json`](policies/deny-global-inference.json) | Denies any global profile, the global model ARN, and Bedrock or Rekognition calls outside the three US Regions | Pilot |
| AI services opt-out policy [`ai-opt-out.json`](policies/ai-opt-out.json) | AWS does not keep Rekognition inputs to improve its services, and content already kept is deleted | Pilot |
| Check script | The code names only the US profile and its Regions, and both policies keep their rules | Demonstration and pilot |
| Crop images only | No image of a person is used in tests | Demonstration |

Both policies are created in the management account of the organization. The demonstration runs on one standalone account, which cannot attach them, so it uses only crop images with no people, from the drone supplier's samples or public crop sets.

The Region limit of the [landing zone](../governance/landing-zone.md) allows only us-east-1. A US profile that routes to us-east-2 or us-west-2 fails under that limit, so the limit must exempt the three destinations for Bedrock calls through the US profile, which AWS supports through the `bedrock:InferenceProfileArn` condition.

`tools/check_inference_region.py` reads the Terraform files of the infrastructure and module repositories cloned next to this one. It fails when a file names a global profile, when a model identifier does not start with `us.`, when the allowed model Regions differ from the three destinations, when the service control policy stops denying the global profile or the other Regions, or when the opt-out policy stops covering every service.

```sh
python3 docs/security/tools/check_inference_region.py
```

## 6. Statement for the privacy notice

The Federation can state the following to farmers, carriers and staff.

> The platform stores its data in data centers of Amazon Web Services in the United States. Drone images of the crops are analyzed by automated services of the same provider in the United States. Before that analysis, each image is checked for people. An image that shows a person is never analyzed, is kept apart with restricted access and is deleted after 30 days. The images sent to analysis carry no location or name, and the provider does not use them to train its models.

## 7. Cost

The controls add no charge. Service control and opt-out policies are free, and encoding the pixels again happens inside an invocation the function already pays for. The cost of the person filter and of the model calls is in the [inference functions](../architecture/inference-functions.md) document, in its cost section.

## 8. Assumptions and pending confirmations

| Item | Who confirms | Effect if it fails |
|---|---|---|
| The United States meets the adequacy rule, or the model clauses cover the transfer | Legal counsel | Personal data moves, or the model clauses are signed before production |
| Processing in three US Regions counts as the same destination country | Legal counsel | The function moves to a model with in-Region use in us-east-1 |
| The demonstration uses only crop images with no people | Platform team | The demonstration needs an organization with the opt-out policy before any field image |
| The person filter threshold set low is safe | Review with real images | More repeated flights, or more risk |

## 9. Sources

| Fact | Source |
|---|---|
| US profile destinations of Nova 2 Lite, and no in-Region use in us-east-1 | [Nova 2 Lite model card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-amazon-nova-2-lite.md) and [model Region support](https://docs.aws.amazon.com/bedrock/latest/userguide/models-region-compatibility.html) |
| Data stays in the geography, AWS network, abuse detection storage, CloudTrail in the source Region, Region limits and the profile exception | [Geographic cross-Region inference](https://docs.aws.amazon.com/bedrock/latest/userguide/geographic-cross-region-inference.html) |
| Global profile routes worldwide, global model ARN | [Global cross-Region inference](https://docs.aws.amazon.com/bedrock/latest/userguide/global-cross-region-inference.html) |
| No sharing with model providers and no training on inputs or outputs | [Amazon Bedrock FAQs](https://aws.amazon.com/bedrock/faqs/), security section |
| Rekognition may use inputs to improve the service, opt-out through Organizations, deletion of kept content | [AI services opt-out policies](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_ai-opt-out.html) and [Rekognition FAQs](https://aws.amazon.com/rekognition/faqs/) |
| Model and Regions in the code | `envs/*/locals.tf` of the infrastructure repository |
