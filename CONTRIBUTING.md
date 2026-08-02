# Contributing to OpenRights Assistant

Thank you for considering a contribution. This project exists to make public legal information accessible offline, and we welcome help from anyone who shares that goal.

## How to contribute

### Report a problem

Open a GitHub Issue describing what you expected and what happened instead. Include the command you ran if applicable.

### Add a legal source

1. Find an official, public-domain legal or consumer-protection source.
2. Add an entry to `data/sources.json` with a unique `id`, a human-readable `title`, and the canonical `url`.
3. Run `python -m openrights ingest` and confirm the new source is chunked correctly.
4. Add at least two evaluation questions to `evals/questions.json` that test retrieval from the new source.
5. Run `python -m openrights evaluate` and confirm all tests pass.
6. Open a pull request with the source entry and the new evaluation questions.

### Add a new jurisdiction

The architecture supports multiple jurisdictions. To add one:

1. Create a new source manifest or extend `data/sources.json`.
2. Ensure the source text is in the public domain or under an open license.
3. If the source is in a language other than English, note this in the PR description.
4. Add evaluation questions in the source language.

### Improve the mobile interface

The app in `app/` is a dependency-free PWA. Changes should:

- Work without a build step (no bundler, no framework).
- Remain functional at 360px viewport width.
- Not add any external network requests.
- Keep the total shipped archive under 2 MB.

### Fix or improve code

1. Fork the repository and create a branch.
2. Make your change and run `python -m openrights evaluate && python -m unittest discover -s tests`.
3. Open a pull request. Describe what you changed and why.

## Code style

- Python: type hints, docstrings on public functions, no external dependencies in the core.
- JavaScript: no framework, no build step, vanilla ES6.
- Commits: imperative mood, short first line, optional body after a blank line.

## Code of conduct

Be respectful and constructive. Discrimination, harassment, and personal attacks are not tolerated.

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.
