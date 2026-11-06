# Bedrock analyzes images and Rekognition only filters people

## Context

No model is trained for the pilot. Rekognition standard labels find plants and leaves, and AWS documents that telling healthy plants from infected ones needs Custom Labels, which trains a model.

## Options

A Bedrock multimodal model with a Rekognition person filter, or Rekognition Custom Labels.

## Decision

A Bedrock multimodal model analyzes confirmation, verification and estimation objects. Rekognition DetectLabels runs first and stops any object that contains a person.

## Consequences

Nothing is trained, and the model can change with no platform change. Analysis quality depends on the prompt and needs review with agronomists.

Cost favors this option as well. Custom Labels bills USD 4 per hour while a model is running, about USD 2,920 a month if it stays on. With Nova 2 Lite, which bills 230 tokens per image, an image costs about USD 0.0007 in Bedrock and USD 0.001 in Rekognition, about USD 1.75 per 1,000 images counting the function. A harvest month of 9,000 images costs about USD 16.
