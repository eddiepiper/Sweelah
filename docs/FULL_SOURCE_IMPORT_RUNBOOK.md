# RetirePilot v2.5: Full Source Import Handover

**Status: SOURCE PUSH PENDING.** This document is not evidence that the Python source has already reached GitHub.

The curated, executable migration kit has been built and verified in the working environment. The GitHub connector can write repository text, but cannot consume the local ZIP/file tree directly, and this environment cannot connect to github.com by Git. The final source push requires running the provided migration script from a GitHub-authenticated machine.

## Import package

- File name: `RetirePilot_Full_Source_Migration_v2.5.zip`
- SHA-256: `bf96f1196497981ba72ad95a7c7dc019ab4879765780c7c338f9d3d2e1d52cb6`
- Contains **55 files**: 51 curated active v2.5 source/test/fixture/audit files, GitHub Actions CI, local migration script, import manifest and runbook.
- No real customer financial records, vault databases, secrets or generated test caches included.
- Existing repository README, release gates, security policy and issues are preserved.

## How to finish the migration

1. Download `RetirePilot_Full_Source_Migration_v2.5.zip` from the ChatGPT conversation where the kit was prepared.
2. On your Mac or another authenticated development machine, extract the ZIP to an empty directory.
3. Open Terminal in the extracted directory and run:

```bash
shasum -a 256 ../RetirePilot_Full_Source_Migration_v2.5.zip
bash MIGRATE_TO_GITHUB.sh
```

4. The script clones `https://github.com/eddiepiper/RetirePilot.git`, copies the curated sources, installs Python requirements in a virtual environment, runs the tests, commits and pushes to the repository's `main` branch. It does **not** force-push.
5. Review the resulting GitHub Actions run and close issue #1 only after the remote CI test results and file hashes are confirmed.

## Local checks already completed

- `python -m pytest -q`: **477 passed** on the curated set.
- `PYTHONPATH=. python audit/run_rule_contracts_v22.py`: **498 checks passed**.
- Local API script: **13 cases passed** with localhost uvicorn serving the API.
- Targeted credentials/private-key/email scan of the curated text package: **0 detected matches**. This is not a third-party secret or security certification.
- Phase 9: **NO-GO**.

## Critical restrictions

The code still has uncalibrated persona scoring, incomplete full CPF/CPF LIFE/statutory reconciliation, no independent QA/legal/security sign-offs and 0 of 48 actual user interviews. Do not infer production readiness from code migration or a green synthetic CI run.

## Current tracking

- Issue #1: Source import and CI, **OPEN** until GitHub contains the files and runs CI.
- Issues #2–#8: Outstanding financial, classification, security, AI, assurance, user research and scenario scope.
