# Bedrock analyzes images and Rekognition only filters people

## Context

No model is trained for the pilot. Rekognition standard labels find plants and leaves, and AWS documents that telling healthy plants from infected ones needs Custom Labels, which trains a model.

## Options

A Bedrock multimodal model with a Rekognition person filter, or Rekognition Custom Labels.

## Decision

A Bedrock multimodal model analyzes confirmation, verification and estimation objects. Rekognition DetectLabels runs first and stops any object that contains a person.

## Consequences

Nothing is trained, and the model can change with no platform change. Analysis quality depends on the prompt and needs review with agronomists. Bedrock token prices must be confirmed in the cost document.
