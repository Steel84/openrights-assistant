# Impact Measurement Framework

## Why measure impact

Grant programs evaluate projects on real-world utility for underserved populations. This document defines how we will measure whether OpenRights Assistant actually helps people.

## Metrics

### Reach

| Metric | How measured | Target (6 months) |
| --- | --- | --- |
| Installs | APK downloads + PWA install events | 500+ |
| Active users (monthly) | PWA analytics (local-only counter) | 200+ |
| Jurisdictions covered | Number of source manifests | 3+ |
| Languages supported | Distinct source languages | 2+ |

### Quality

| Metric | How measured | Target |
| --- | --- | --- |
| Retrieval accuracy | Eval set pass rate | > 90% |
| Citation accuracy | Manual audit of generated answers | > 85% citations correct |
| Source freshness | Days since last source update check | < 90 days |
| User-reported errors | GitHub Issues labeled "wrong-answer" | < 5% of queries |

### Accessibility

| Metric | How measured | Target |
| --- | --- | --- |
| Install size | APK/PWA size | < 5 MB (retrieval only) |
| Works on budget phone | Tested on Redmi 9A or equivalent | Yes |
| Cold start time | Time to first interactive | < 3 seconds |
| Query latency | Time from submit to results | < 200 ms |
| Offline reliability | Works in airplane mode | 100% |

### Privacy

| Metric | How measured | Target |
| --- | --- | --- |
| Network requests after install | Packet capture audit | Zero |
| Personal data stored | Code audit | None |
| Permissions requested | AndroidManifest.xml | Zero |

## Data collection approach

All metrics are measured either:
- Automatically in CI (retrieval accuracy, install size, latency)
- On-device with a local counter that never leaves the phone
- Through voluntary user feedback (GitHub Issues)

No telemetry is sent to any server. Privacy is a hard constraint, not a preference.

## Reporting

We will publish a monthly impact report in the repository wiki, covering:
- Eval pass rate trend
- New sources added
- Community contributions
- Known limitations discovered
- User feedback summary (anonymized)
