# Coverage

The archive has two layers, and the difference matters when reading a result.

**Plain-language answers** are written for this project: one self-contained
answer per question, in ordinary English, with the figures that decide the
question in bold. Each one names the statute it summarises and links to it.

**Statute passages** are the law verbatim, pulled from GovInfo and the FTC.
They are complete but unreadable: the top text match for "minimum wage" is
amendment history about American Samoa, technically correct and useless.

The interface leads with the plain-language answer and folds the statute
underneath as supporting evidence. When no plain-language answer covers the
question, it says so rather than presenting an excerpt as if it were an answer.

## What is covered today

50 plain-language answers across eight topics:

| Topic | Answers | Covers |
| --- | --- | --- |
| Wages and overtime | 15 | Minimum wage, overtime, exemptions, tipped work, part-time status, breaks, final paycheck, deductions, contractor misclassification, unpaid wages, records, child labor, equal pay |
| Losing a job | 5 | At-will employment, notice and severance, unlawful dismissal, retaliation, unused vacation |
| Family and medical leave | 5 | Entitlement, eligibility, qualifying reasons, job protection, health insurance |
| Workplace safety | 5 | Right to a safe workplace, refusing dangerous work, complaints, retaliation, training |
| Debt collection | 6 | Contact rules, stopping contact, harassment, false statements, required notice, disputes |
| Workplace discrimination | 5 | Protected characteristics, harassment, retaliation, accommodation, filing a charge |
| Talking about pay and organising | 4 | Pay secrecy rules, union rights, concerted activity, complaining about conditions |
| Credit reports | 5 | Reading your report, disputing errors, how long items stay, who may look, adverse action |

Statute text is indexed for all nine sources listed in `data/sources.json`,
including two with no plain-language layer yet: the Truth in Lending Act and
FTC advertising guidance.

## Known gaps

A question outside the topics above will fall through to statute text. The
largest gaps, in rough order of how often people hit them:

- Housing, tenancy, and eviction
- Consumer purchases, refunds, and warranties
- Unemployment benefits
- Wage garnishment
- Bankruptcy
- Immigration status at work
- Small claims procedure
- Family law

`python -m openrights coverage` checks both halves: that 43 questions reach the
right answer, and that 10 questions from the gap list above are **declined**
rather than answered.

The second half is the one worth having. Cosine similarity rewards sentence
shape, so "Can my landlord raise the rent?" once scored 0.63 against "Can my
employer change my schedule?" purely on "can my", with landlord and rent absent
from the answer. A confident answer to a different question is the worst thing
this tool can do, so two guards run before anything is presented as an answer:

- **A similarity floor of 0.35.** Correct matches measure 0.36 and up;
  unrelated ones sit at 0.33 and below.
- **A subject check.** The rarest substantial word in the question must appear
  in the answer. This is what catches landlord, tenant, divorce, and
  bankruptcy: the pattern matches, the subject does not.

When either guard rejects the match, the app says no plain-language answer
covers the question and shows the statute instead.

## Adding an answer

Edit a file in `data/curated/` or create one, then register it in
`PLAIN_SOURCES` in `openrights/ingest.py`.

The format is one `##` heading per question:

```markdown
## Can my employer deduct money from my paycheck?
Also asked: deductions, docked pay, taking money out of wages

Deductions are **not allowed if they push your pay below the minimum wage**
for that week.

Taxes and court-ordered garnishments are treated differently.
```

The heading is the question, indexed at four times the weight of the body,
because people search in the words of their question. The optional
`Also asked:` line holds alternative phrasings. It is indexed and never shown.
Use it when two answers share most of their wording and the search picks the
wrong sibling.

Add the question to `evals/coverage.json`, then:

```bash
python -m openrights ingest
python -m openrights coverage    # must reach the new answer
python -m openrights evaluate
python -m openrights export-web
```

## What the guards do not fix

The guards decide whether to give an *answer*. The statute passages shown
underneath when no answer exists are not filtered by score, because no score
separates them.

Measured across `evals/coverage.json`: the top statute citation for a covered
question scores between 0.05 and 0.20 (median 0.20); for an uncovered question,
between 0.10 and 0.28. The ranges overlap almost completely, so any threshold
that removed the noise would also remove real citations.

So when the archive has no answer, the passages shown are the nearest text by
similarity and may be irrelevant. The interface labels them as such rather than
filtering on a number that does not mean anything. Closing this needs a real
relevance signal, not a tuned constant: sentence embeddings are the obvious
candidate and are out of scope for the first release.

## Scaling this

Writing 50 answers took a few hours. The work is legal summarisation, not
engineering, and it is the part that decides whether the tool helps anyone.

This is deliberate for the first release: hand-written answers are auditable,
and a wrong answer about someone's wages is worse than no answer. A local model
can draft summaries from statute text later, but every draft needs review
before shipping, and the review is the expensive part.

A new jurisdiction needs its own answer set. The pipeline is jurisdiction
agnostic; the writing is not.
