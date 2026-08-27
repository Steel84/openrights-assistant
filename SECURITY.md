# Security Policy

## Scope

OpenRights Assistant processes only publicly available legal texts. It does not collect, store, or transmit personal data. There is no authentication, no server component, and no network communication after installation.

## Reporting a vulnerability

If you find a security issue (for example, a way the app could be made to leak device data or execute unintended code), please report it by opening a GitHub Issue with the label "security" or by emailing the maintainer directly.

We will acknowledge the report within 72 hours and aim to release a fix within 7 days for confirmed issues.

## Threat model

The primary threats we consider:

1. **Malicious source injection**: A compromised upstream source could inject misleading legal text. Mitigation: sources are pinned to specific official government URLs; ingestion includes HTML sanitization.
2. **Prompt injection and cloud disclosure via generation**: If the optional PWA AI Summary is enabled, adversarial text in source passages could manipulate the model output, and the user's question plus up to five matched legal passages are sent to external Gemini/Mistral servers. The PWA feature is disabled by default. The CLI `--model` path uses llama.cpp locally and does not send the question or passages to an external provider. In both modes, output is shown alongside raw source passages for verification.
3. **Supply chain**: The project has zero runtime dependencies beyond the Python standard library. The optional LLM layer depends only on an external `llama-cli` binary.

## Supported versions

Only the latest release on the `main` branch is supported.
