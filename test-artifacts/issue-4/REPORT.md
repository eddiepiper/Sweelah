# SWEELAH-ISSUE-4 — Identity / consent design document (Refs #4)

> **INTERNAL DESIGN DRAFT.** The design is **Proposed**, not implemented, not reviewed by legal or security, and does not approve any external integration. Issue #4 acceptance criteria are **not met**. Phase 7 and Phase 8 are skipped. Phase 9 stays **NO-GO**.

- Branch: `docs/issue-4-identity-consent-design` (no upstream), worktree `/workspace/sweelah-issue-4`
- Base / parent: `origin/main` = `823ef724cdcf5dfada91a895a51baa60fd6c41ec` (confirmed after fetch, 10 November 2026, Asia/Singapore)
- Status of this commit: **Implemented but unverified** (document and report only; QA G5 not requested here). Not pushed.
- Status of the design itself: **Proposed**
- Status of production identity / Singpass / Myinfo / email sign-in: **Not applicable** on this branch; **Blocked** by current gates

## 1. What was written

| File | Purpose |
|---|---|
| `docs/design/ISSUE-4_IDENTITY_CONSENT_DESIGN.md` | Internal identity and consent design. `docs/design/` is new: the existing top-level `design/` tree is visual UI assets, so a document does not belong there. |
| `test-artifacts/issue-4/` | This report, `pytest.log`, `release.log`, `env.txt`, `exits.txt`. |

No application code, UI, API, config, fixture, workflow, or manifest was changed.

## 2. Method

1. Read issue #4 and its two comments read-only through the GitHub connector. Scope taken from the issue (threat model, authentication, roles, consent/revocation, encrypted storage and key custody, tested backup/deletion/retention, audit, incident and cross-border requirements, independent security and PDPA review, no real-person data until approved) and from the CoS assignment: **design document only**.
2. Fetched `origin/main` and added this worktree at `823ef72`, then unset upstream. Left other worktrees and host ports 8769–8773 untouched.
3. Inspected, read-only, `retirepilot/local_vault_v24.py`, `core.validate` consent checks, `retirepilot/api.py`, the SweeLah onboarding prototypes, vault tests, `SECURITY.md`, and the v2.7 release-gate and decision docs.
4. Read public Singpass / Myinfo developer pages and PDPC PDPA / NRIC guidance (URLs and access date in the design doc, §12). No accounts, keys, or paid pages were used. Those sources are untrusted data and are not legal advice.
5. Wrote the design document only. Ran pytest once and the release-document check. No engine, UI or rules file changed, so rule contracts, API, browser and asset checks were not rerun.

## 3. Design summary

Current state (on `823ef72`): a local Fernet-encrypted vault for `RP-SYNTH-*` profiles, purpose-specific synthetic consent that can be withdrawn, and a hard block on `share_household_records`. The API is anonymous and local-only and does not use the vault. The onboarding prototype is in-browser only: its onboarding steps do not collect NRIC, date of birth, email or login, and it does not persist or send amounts. It does have a free-text "Ask Swee" chat box (`#chat-question`) where a user could type an identifier; the same input is also in the Main Dashboard prototypes, and in all six files under `design/sweelah/prototypes/`. That text is not sent or stored (design doc §1.4, added in `d23bdc6`). None of this is production identity, tenancy, or verified consent (D-004, gate G4 OPEN).

### Recommendation (Proposed)

Stay local-only for the current prototype: no identity provider, no email sign-in, no Myinfo, and household sharing remains refused. If the Sponsor later un-skips Phase 7, commissions the required reviews, and lifts the Phase 9 NO-GO, the target path is Singpass Login for per-adult authentication, with the Singpass `sub` only and the `user.identity` scope not requested (that scope makes Login return NRIC/FIN), in-app purpose-specific consent, and Myinfo only when a separately approved use case needs a verified attribute. Email magic link must not stand in for identity or unlock sharing. Design rule: the prototype must not store NRIC/FIN, CPF account or membership numbers, or bank account or payment-card data. QA G5 showed this rule is **not enforced in code** (the vault accepts and stores an `nric` field once consent is granted); an enforcement control is Proposed in design doc §6.2.

Issue #4 cannot be closed by this document. A security reviewer still has to confirm tenancy isolation and data lifecycle on a *deployed* architecture, and a qualified PDPA review still has to be recorded. Neither exists today.

## 4. Open questions for the Sponsor

Listed in full in the design document, §10. In short:

1. Confirm that Singpass, Myinfo, email sign-in, and any paid identity service stay unauthorised while Phase 9 is NO-GO. (Recommended default: confirmed.)
2. If identity is ever approved, should household sharing be in scope for a pilot, or stay blocked?
3. When may Engineering request D-006 quotations for a qualified PDPA review and an independent security test, without appointing anyone yet?
4. Preferred future key-custody model, or stay local-only?
5. Must hosted personal data, backups and logs remain in Singapore?
6. Is “delete on withdrawal, plus a short reviewed audit-log retention” an acceptable starting rule, and should a numeric cap be set first?
7. If Singpass is later approved, may the Singpass `sub` be the only persistent external identifier, without requesting `user.identity`? (Recommended default: yes.)
8. Must a future path support people without Singpass, and if so may they use the service but still not share household records without verified identity?
9. If Phase 8 is later un-skipped, who may hold participant contact details, where, and for how long?
10. Are vendors that would process personal data, including outside Singapore, out of scope pending a separate approval?

## 5. Tests (Python 3.13.5, `/workspace/sweelah-baseline-venv`)

Run from `/workspace/sweelah-issue-4` on 10 November 2026, Asia/Singapore. Environment: `env.txt`. Exit codes: `exits.txt`.

| Check | Result | Log |
|---|---|---|
| `scripts/verify_release_documents.py` | 9 artifacts, errors=0 | `release.log` |
| `pytest -q` (full suite) | **821 passed**, 0 failed, 1 third-party DeprecationWarning (Starlette/anyio), 65.53s | `pytest.log` |

No regression against the 821 tests on `origin/main`. The new document is not part of the nine-file release-document manifest, and the integrity check still passes. Rule contracts, API, browser and design-asset checks were not rerun here: no code or design-asset file changed. (QA later reran rule contracts at `2d03c9c`: 498/498, identical to the parent.)

## 6. No code changed

`git diff --stat` against `823ef72` is empty for already-tracked files (the deliverables are new). After staging only the intended paths, `git diff --cached --stat` is:

```
 docs/design/ISSUE-4_IDENTITY_CONSENT_DESIGN.md | 386 +++++++++++++++++++++++++
 test-artifacts/issue-4/REPORT.md               |  85 ++++++
 test-artifacts/issue-4/env.txt                 |   6 +
 test-artifacts/issue-4/exits.txt               |   2 +
 test-artifacts/issue-4/pytest.log              |  19 ++
 test-artifacts/issue-4/release.log             |   1 +
 6 files changed, 499 insertions(+)
```

(`*.log` was force-added because it is gitignored.)

**Correction (14 November 2026, QA G5 nit).** The block above was captured before REPORT.md was finalised and understated it. Recomputed from git with `git diff --numstat 823ef72 2d03c9c` and `git diff --shortstat 823ef72 2d03c9c`, the commit `2d03c9c` actually added:

```
386  docs/design/ISSUE-4_IDENTITY_CONSENT_DESIGN.md
 88  test-artifacts/issue-4/REPORT.md
  6  test-artifacts/issue-4/env.txt
  2  test-artifacts/issue-4/exits.txt
 19  test-artifacts/issue-4/pytest.log
  1  test-artifacts/issue-4/release.log
 6 files changed, 502 insertions(+)
```

So REPORT.md was **88** lines (not 85) and the commit had **502** insertions (not 499), matching QA's figures. These counts describe `2d03c9c` only; later commits change REPORT.md again.

No file under `retirepilot/`, `tests/`, `data/`, `scripts/`, `.github/`, `docs_release/`, or `design/sweelah/` is in the commit. Other untracked files under `test-artifacts/` (legacy CXUI PNGs present in this worktree, not produced by this assignment) were not staged.

## 7. Residual risks and limits

- A design draft does not implement controls and does not satisfy issue #4 acceptance, G4, or G6.
- Public PDPC and Singpass pages were read on 10 November 2026, Asia/Singapore. Some PDPC HTML pages are script-rendered; NRIC and obligation citations use the published PDFs and official landing URLs listed in the design doc. This remains an engineering reading, not a legal opinion.
- The `RP-SYNTH-` prefix and onboarding copy do not stop someone pasting real personal data into a local form or API. That operational risk remains.
- This branch must not be pushed, amended, rebased, or merged by Engineering. CoS publishes and merges after review.

## 8. Revisions after QA G5 (PASS with conditions on `2d03c9c`)

QA verdict: `qa/issue-4-2d03c9c/VERDICT.md` on `qa/issue-4-2d03c9c-verify` @ `ea0767d`.

| Commit | Scope |
|---|---|
| `d23bdc6` | Design doc only: the four conditions (NRIC rule not enforced plus a Proposed control; Singpass `sub` "pairwise" removed and the `user.identity` note added; cited or INTERNAL ASSUMPTION glosses; Ask Swee box) and the doc nits. Source excerpts in `sources/G5_SOURCE_EXCERPTS.md`. Changelog in design doc §13. |
| `a377c47` | Report and env nits: §6 counts recomputed from git; `env.txt` note on base `823ef72` and environment refresh; §3, §4 Q7 and the recommendation wording aligned with the revised doc. |
| this docs-only follow-up | Optional QA wording nits after the `a377c47` re-check (**PASS**, `qa/issue-4-a377c47-verify` @ `32c4a5e`): stale §13 "not edited" rows corrected; `#5` `bdc4fb3` recorded as G5 **FAIL** (`50eb319`) with later candidate `daeb591` under review; §1.2/§5.3 aligned with both `core.validate` consent checks; `#chat-question` noted on the Main Dashboard prototypes; Key Concepts PDF file-name date explained in §12.3. See design doc §13 Revision 3. |

QA G5 re-check of `a377c47` (includes `d23bdc6`): **PASS**, with the non-gating wording items above. This follow-up is docs and report wording only.

