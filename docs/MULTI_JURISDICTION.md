# Multi-Jurisdiction Roadmap

OpenRights Assistant is designed to scale across jurisdictions and languages. The architecture is jurisdiction-agnostic: `data/sources.json` is the only file that ties the system to a specific country.

## Current: United States (pilot)

- Fair Labor Standards Act (wages, overtime, child labor)
- Family and Medical Leave Act (FMLA)
- Occupational Safety and Health Act (OSHA)
- Fair Debt Collection Practices Act (FDCPA)
- Civil Rights Act Title VII (employment discrimination)
- Truth in Lending Act (TILA - consumer finance)
- FTC consumer protection (phishing, advertising)

## Next: India (planned)

India is the natural second jurisdiction because:
- Massive unmet need: 400M+ workers in the informal sector with limited access to legal information.
- Key statutes are available in English and Hindi (public domain).
- India consolidated 29 old labour laws into 4 new Labour Codes, effective 21 November 2025. This is an opportunity: workers need to understand the new rules.

Target sources (current as of 2025 Labour Codes reform):
- The Code on Wages, 2019 (replaced Payment of Wages Act 1936 + Minimum Wages Act 1948 + Payment of Bonus Act 1965 + Equal Remuneration Act 1976; effective Nov 2025)
- The Occupational Safety, Health and Working Conditions Code, 2020 (replaced Factories Act 1948 and 12 other laws; effective Nov 2025)
- The Code on Social Security, 2020 (replaced 9 laws including EPF, ESI, Maternity Benefit; effective Nov 2025)
- The Industrial Relations Code, 2020 (replaced Industrial Disputes Act 1947, Trade Unions Act 1926, Standing Orders Act 1946; effective Nov 2025)
- The Consumer Protection Act, 2019 (still in force, not part of the Labour Codes consolidation)
- The Sexual Harassment of Women at Workplace Act, 2013 (still in force)

Note: India consolidated 29 labour laws into 4 codes effective 21 November 2025. Our sources target the new codes, not the repealed acts.

## Future jurisdictions

| Jurisdiction | Language | Priority sources |
| --- | --- | --- |
| Brazil | Portuguese | CLT (labour code), CDC (consumer code) |
| Nigeria | English | Labour Act, Consumer Protection Council Act |
| Philippines | English/Filipino | Labor Code, Consumer Act |
| Kenya | English | Employment Act, Consumer Protection Act |

## Technical requirements for new jurisdictions

1. Source texts must be publicly available and redistributable.
2. The tokenizer handles Latin-script languages. CJK, Devanagari, and Arabic require a tokenizer extension (planned: character n-gram fallback).
3. Each jurisdiction can have its own source manifest or share one.
4. Evaluation questions should be written by someone familiar with the jurisdiction.

## Multilingual retrieval

For the TF-IDF layer:
- Same-script languages work out of the box (Spanish, Portuguese, French).
- Different-script languages need a tokenizer swap: the `TOKEN_RE` regex in `rag.py` would be replaced with a Unicode-aware splitter.
- Cross-lingual retrieval (question in English, source in Hindi) requires either translation at ingest time or multilingual embeddings. This is a post-MVP enhancement.
