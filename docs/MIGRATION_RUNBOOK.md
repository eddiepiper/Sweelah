# RetirePilot v2.5 Source Control Migration

This kit contains the complete runnable v2.5 Python application, synthetic fixtures,
tests, supporting audit source and current technical addenda. It does not contain
real customer records or production credentials. The private GitHub repository
already contains a README, release gates and issues; those files must be preserved.

## Import safely (macOS/Linux)

1. Download this kit and extract it into a temporary folder, outside your existing repository.
2. Ensure GitHub authentication works for `https://github.com/eddiepiper/RetirePilot`.
3. Run from the kit folder:

```bash
bash MIGRATE_TO_GITHUB.sh
```

The script clones the private repository, copies the files, runs the three verification
routes, creates a source import commit and pushes to `main` **only if tests pass**.
It never force-pushes. It leaves production deployment disabled. Use a branch/PR
instead if repository policy requires review.

## Verification

- Self-run local Python tests: 477 passed (2026-11-04).
- Classifier rule-contract checks: 498 passed (2026-11-04).
- API smoke cases: 13 passed with localhost server running.
- GitHub CI must be run on the committed source before claiming remote reproducibility.
- Financial/regulatory/consumer gates remain NO-GO irrespective of CI.

## Scope and exclusions

The import kit includes all 51 curated active text source files, tests, synthetic JSON
fixtures, executable audit scripts, policies and v2.5 addenda. It excludes old binary
reports, historical Excel workbooks, generated execution outputs, local vaults and caches.
The retained 96-archetype machine-readable rule file is `retirepilot/retirepilot_rules_v1.2.json`.
For source import traceability, see `docs/SOURCE_IMPORT_MANIFEST.json`.
