# Sentient Foundation Grant Draft

## Project

OpenRights Assistant is an offline-first, source-based legal information assistant for people who cannot rely on expensive legal support or continuous connectivity. The first pilot covers U.S. labor and consumer-protection sources and is intentionally narrow enough to evaluate honestly.

## Problem

Public legal information is technically available but difficult to search on a low-cost phone. Hosted AI tools create privacy, connectivity, and recurring-cost barriers. A user should be able to ask a plain-language question and see the exact public passages behind the answer.

## MVP

The prototype downloads public sources once, cleans and chunks them, builds a local TF-IDF index, and retrieves cited passages without a server. A mobile-responsive PWA caches its interface and 1.2 MB local index for airplane-mode use. An optional llama.cpp adapter can generate a short answer from retrieved passages and cite them.

## Openness

The repository contains the ingestion pipeline, source manifest, retrieval implementation, evaluation questions, prompt, mobile interface, and limitations. Model weights are not bundled because of size and licensing; the runtime accepts compatible open GGUF weights.

## Resource target

The retrieval-only mode has no hosted dependency and is suitable for modest hardware. The first model experiment targets a 1.5B parameter instruct model in Q4 quantization, with a 256-token output cap and a 2-3 GB working-memory ceiling. The grant would fund measurement and optimization on low-cost Android hardware rather than assuming a modern flagship phone.

## Requested support

Support would be used for low-end Android testing, model/runtime optimization, source and citation evaluation, and a pilot with community users. The immediate milestone is a reproducible offline phone demo with measured install size, query latency, memory use, and citation accuracy.

## Risks and boundaries

This is not legal advice and does not claim complete legal coverage. The app shows jurisdiction, source URLs, and a verification warning. It will not collect sensitive personal data in the first pilot. Before public release, source freshness, accessibility, and user testing will be documented.
