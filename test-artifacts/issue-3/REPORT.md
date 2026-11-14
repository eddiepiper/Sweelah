# SWEELAH-ISSUE-3: internal draft persona labels (DRAFT, not independently reviewed). Refs #3

**Status: Implemented but unverified.** Internal Product draft. Head of Product reviewed `c32ede1` (Status: Proposed) and accepted 475 of 480 values; the five corrections below are applied on top of that commit. Labels stay `DRAFT_NOT_INDEPENDENTLY_REVIEWED` with `evidence_level: null` (JSON null; the string `"None"` up to `8e812e0`, see §11.2). They must not be used to sort, filter or prioritise personas before the 7A research gate. Not for the consumer UI, API or exports (decision 3A). Phase 9 stays NO-GO. Synthetic/public fields only.

- Worktree: `/workspace/sweelah-issue-3`, branch `feat/issue-3-persona-draft-labels` (upstream unset), branch cut from `823ef724cdcf5dfada91a895a51baa60fd6c41ec` (parent chain unchanged: `823ef72` → `c32ede1` → `8e812e0` → this commit). **Base is now main `5fe3ec8b6448d94d4a15dc18f1f38c2a58508e76`**; a `git merge-tree` trial merge onto it is clean (§11.4). First commit `c32ede1`. This follow-up confirmed 10 Nov 2026, after 10:24pm SGT (Asia/Singapore, UTC+8).
- Issue #3 was read read-only via the cursor-github connector and treated as data. The open issue asks for independently labelled cases and a calibrated scoring methodology. This assignment is the coordinated first step: an internal draft taxonomy, marked `DRAFT_NOT_INDEPENDENTLY_REVIEWED`, not a close of that acceptance bar.

## 1. Taxonomy source

Head of Product specification, **Status: Proposed**. HoP owns the taxonomy and the final values, and will review all 96 and sign off as a Product draft. Engineering derived a first pass from existing rules fields only.

One record per persona, with `persona_id` (A01–L08), `family` (the 12 existing families) and `name` copied verbatim from `retirepilot/retirepilot_rules_v1.2.json`. No renaming or regrouping.

Enum fields:

- `life_stage`: `pre_retirement_45_54` | `near_retirement_55_64` | `payout_age_65_plus` | `spans_stages`
- `work_income_type`: `salaried` | `platform_gig` | `self_employed_or_commission` | `not_working` | `mixed` | `not_applicable`
- `cpf_retirement_situation`: `accumulating` | `approaching_55_ra_formation` | `payout_started` | `payout_deferred` | `limited_or_no_cpf` | `varies`. Patterns only; no amounts or entitlement claims (decision 2A).
- `household_context`: `single` | `couple` | `dependants` | `caregiver` | `multi_generation` | `varies`
- `planning_complexity`: `standard` | `elevated` | `specialist_review_suggested`, plus `planning_complexity_reason` (one line)
- No risk tier (decision 1A: that would read like suitability advice)
- On every record: `label_status: DRAFT_NOT_INDEPENDENTLY_REVIEWED`, `evidence_level: null` (JSON null; decision 7A: internal design, no research), and `rationale` (one line citing the existing gate, criteria and planning_focus)

Aligned with:

- the rules file (source of truth; SHA-256 `3e0fed7a0fb751ccfe9b857a51404dc1a26f29634cea9ae77c73e6fba913ec4b`, unchanged)
- PSD v2.7 section 3 (96 archetypes across 12 families A–L, provisional descriptions, no numerical confidence, incomplete data stays unknown) and Appendix A
- `docs/APPROVED_DECISIONS_v2.7.md` decisions 1A, 2A, 3A and 7A

## 2. Method

- **Overlay, not an edit.** Labels live in `data/persona_draft_labels_issue3.json`. The rules file, matcher, API, service, UI, assistant and other engine files were not edited.
- **Reproducible.** `scripts/build_persona_draft_labels_issue3.py` regenerates the JSON from the rules file plus a fixed derivation table. Re-running produces byte-identical output. Build SHA-256 by commit: `c32ede1` `ceec1f434d280d99406cc41e3e3e374042bb3c20cf792b9be22d73d202b11de4`; `8e812e0` (HoP-signed) `c82c5f81b992228f82edf62d573bf58a52c9355e70370f4ec24f9aa6858d27e6`; this commit (evidence_level null) `99fc4dd0c3c21b8b94697a7ae568fddd81d2ac8e8234ca275dd45de4431cdb2b`. Two clean rebuilds on 14 Nov 2026 gave `99fc4dd0…`, identical to the committed file.
- **Base.** Branch cut from `823ef72`; main has since moved to **`5fe3ec8`**, which is now the base for review and merge. The parent chain is unchanged (no rebase). `git merge-tree --write-tree 5fe3ec8 <this commit>` is clean (§11.4).
- **Derivation rule.** Where an age band, work type, CPF situation or household context is not clearly stated in the existing fields, the first pass uses `varies`, `spans_stages` or `not_applicable` rather than guessing. `work_income_type` has no `varies` value, so unknown work type is `not_applicable`.
- **Internal only.** Nothing under `retirepilot/` imports or mentions the labels file. Tests grep `api.py`, `service.py`, `ui.html`, `assistant.py` and the rest of the consumer package.
- **Matching unchanged.** Canonical SHA-256 of `classify_household` and of `evaluate(...)['classification']` for the three shipped synthetic households is pinned to the `823ef72` values.

## 3. Distribution (96 records)

| Field | Counts |
|---|---|
| `life_stage` | `spans_stages` 81, `payout_age_65_plus` 13, `near_retirement_55_64` 2, `pre_retirement_45_54` 0 |
| `work_income_type` | `not_applicable` 48, `not_working` 16, `salaried` 12, `self_employed_or_commission` 11, `platform_gig` 7, `mixed` 2 |
| `cpf_retirement_situation` | `varies` 71, `limited_or_no_cpf` 11, `accumulating` 6, `payout_started` 6, `payout_deferred` 2, `approaching_55_ra_formation` 0 |
| `household_context` | `varies` 69, `dependants` 10, `couple` 5, `single` 5, `caregiver` 5, `multi_generation` 2 |
| `planning_complexity` | `elevated` 69, `specialist_review_suggested` 20, `standard` 7 |
| `label_status` | `DRAFT_NOT_INDEPENDENTLY_REVIEWED` 96 |
| `evidence_level` | `null` 96 (the string `"None"` at `c32ede1` and `8e812e0`) |

`payout_age_65_plus` (13): B08, F05, F06, F07, F08, G05, G06, G07, G08, I06, J05, J06, L08.

`near_retirement_55_64` (2): E02, G04.

`planning_complexity` = `specialist_review_suggested` (20): C07, E01, E02, E03, E05, E06, E08, I04, I08, J07, J08, K03, K04, K05, K06, K08, L01, L02, L07, L08.

`standard` (7): A02, D01, D02, D03, F01, F02, H02.

The zero counts for `pre_retirement_45_54` and `approaching_55_ra_formation` are conservative, not omissions of those enum values. See section 4.

## 4. Personas for Head of Product review

Every record is a draft. The lists below are the first-pass choices that used `varies` / `spans_stages` / `not_applicable`, or that made a judgement HoP should confirm or change.

### 4.1 Life stage = `spans_stages` (81)

A01, A02, A03, A04, A05, A06, A07, A08, B01, B02, B03, B04, B05, B06, B07, C01, C02, C03, C04, C05, C06, C07, C08, D01, D02, D03, D04, D05, D06, D07, D08, E01, E03, E04, E05, E06, E07, E08, F01, F02, F03, F04, G01, G02, G03, H01, H02, H03, H04, H05, H06, H07, H08, I01, I02, I03, I04, I05, I07, I08, J01, J02, J03, J04, J07, J08, K01, K02, K03, K04, K05, K06, K07, K08, L01, L02, L03, L04, L05, L06, L07.

No persona is labelled `pre_retirement_45_54`. No existing field is a tight 45–54 band (`age_45plus` is open-ended).

### 4.2 Work type = `not_applicable` (48)

D01, D02, D03, D04, D05, D07, D08, E01, E02, E03, E05, E06, E07, E08, F01, F02, F03, F04, F05, F07, F08, G01, G03, H01, H02, H03, H05, H06, H07, H08, I04, I06, I08, J02, J05, J06, J07, J08, K01, K02, K03, K04, K05, K08, L05, L06, L07, L08.

Used when the organising dimension is not work, or the work type is not stated.

### 4.3 CPF situation = `varies` (71)

A03, A04, A05, A06, A07, A08, B03, B04, B05, B07, C01, C02, C03, C04, C07, C08, D01, D02, D03, D04, D05, D07, D08, E01, E02, E03, E04, E05, E06, E07, E08, F01, F02, F03, F04, F05, F06, F07, F08, G01, G02, G07, H01, H02, H03, H04, H05, H06, H07, H08, I01, I02, I03, I04, I06, I08, J01, J02, J03, J06, J07, J08, K03, K04, K05, L01, L02, L05, L06, L07, L08.

No persona is labelled `approaching_55_ra_formation`. No existing field clearly and only means RA formation at 55. E02 (divorced pre-retiree, `age_55plus`, `retirement_soon`, `cpf_settlement`) was the closest; CPF was left as `varies` because the member may already have formed an RA.

### 4.4 Household context = `varies` (69)

A01, A03, A06, A07, A08, B01, B02, B03, B04, B05, B06, B07, B08, C01, C02, C03, C04, C05, C06, C07, C08, E02, E03, F01, F02, F03, F04, F05, F06, F08, G01, G02, G03, G04, G05, G06, G07, G08, H01, H02, H03, H04, H05, H06, H07, H08, I01, I02, I03, I06, I07, J01, J02, J03, J04, J05, J07, K01, K02, K03, K04, K06, K08, L01, L02, L03, L04, L05, L07.

### 4.5 Specific judgements (please confirm or change)

- **E02** `life_stage = near_retirement_55_64` from the name "Divorced pre-retiree" plus `age_55plus` and `retirement_soon`. `age_55plus` is open-ended and could include payout age.
- **G04** `life_stage = near_retirement_55_64` from gate `retire_at_60`, `age_60plus` and `pre_65_bridge`. `work_income_type = not_working` from `income_interrupted`.
- **A08, B04** left as `spans_stages` despite `age_60plus` (A08 also has `working_beyond_65`), because those predicates span more than one band.
- **B02** left as `spans_stages` despite `age_45plus` (open-ended).
- **G01, G02** left as `spans_stages` despite `age_under_65` (covers more than one band).
- **A07, B07, C03, F02, G03, H03, J03, L01** left as `spans_stages` where the only timing cue is `late_career` or `retirement_soon`.
- **E04, H04, I07, L03, L04** are named or gated as retirees but have no age-band predicate, so `life_stage` is `spans_stages` and work is `not_working`.
- **K06, K07** `work_income_type = salaried` inferred from `employment_pass` / `work_permit_or_spass`, not from an `employee` predicate.
- **G07** `work_income_type = mixed` (part-time consulting plus withdrawals).
- **A04** `salaried` from criteria `employee` in a dual-income professional household.
- Overlapping household labels, one organising value chosen: **D04** dependants (not single); **D05** caregiver (not dependants); **A05** dependants (not couple); **I04** caregiver (not dependants); **I08** caregiver (not couple); **K07** dependants from `overseas_family_support`; **E05** dependants for `blended_family`.
- **C05, C06, J04** `limited_or_no_cpf` from `sep_medisave` (MediSave-only pattern, not an entitlement).
- **B02** `limited_or_no_cpf` from `platform_not_opted_in`.
- **A08** has `cpf_income` but is still working, so CPF situation is `varies` rather than `payout_started`.
- **L05** rental income is treated as asset income, not a work type (`not_applicable`).
- **H07** `employer_shares` did not change work type (`not_applicable`).
- **J02, E03, J08** work type is unknown (`not_applicable`).

## 5. Tests

File: `tests/test_persona_draft_labels_issue3.py`, **203 tests**. They check:

- the rules file hash is unchanged
- the header marks the file INTERNAL DRAFT, Product-owned, pending Head of Product review, and cites decisions 1A, 2A, 3A and 7A
- exactly 96 unique ids, in rules-file order, with `family` and `name` identical
- every value is in its enum; every record has the DRAFT marker, `evidence_level` JSON null (was the string "None" before §11), a non-empty one-line rationale and a complexity reason
- no `risk_tier` field (the header may state the 1A prohibition "No risk tier")
- no numeric JSON types, no `%`, and no digits used as scores (digits are allowed only in persona ids, taxonomy enums, verbatim rules fields, decision ids and document citations)
- the labels file is not referenced by `api.py`, `service.py`, `ui.html`, `assistant.py` or any other file under `retirepilot/`
- matching results on the three shipped households are unchanged (canonical hash of `classify_household` and of the public `evaluate` classification)
- the generator reproduces the committed file byte-for-byte

Tests were written first.

| Phase | Result | Log |
|---|---|---|
| Red (labels file not yet present) | **196 failed, 6 passed**. The six passes are the checks that do not need the new file: rules hash, two consumer-isolation greps, and the three household hashes. | `red-phase.log` |
| Green targeted | **203 passed**, 0 failed. After red, the risk-tier test was adjusted so it forbids a `risk_tier` field but allows the header to state "No risk tier." | `green-phase-targeted.log` |

## 6. Full suites

Run with `/workspace/sweelah-baseline-venv` (Python 3.13.5) on 10 Nov 2026, after 10:13pm SGT (Asia/Singapore, UTC+8). See `env.txt` and `exits.txt`. Host previews on 8769–8773 were left running (same PIDs: 2811676, 2850426, 2889452, 2934021, 3016255).

| Suite | Result | Log |
|---|---|---|
| `pytest -q -rs` (full), `AXE_CORE_PATH` set to a scratch axe-core copy that is not kept as evidence (the G5-conditions re-run in §11 uses `/workspace/qa-tools/node_modules/axe-core/axe.min.js`), `PYTHONPATH=.` | **1024 passed**, 0 failed, 0 skipped, 1 third-party DeprecationWarning (starlette/anyio). That is 821 existing + 203 new. | `pytest.log` |
| Rules `PYTHONPATH=. audit/run_rule_contracts_v22.py` | **498 passed, 0 failed** | `rules.log` |
| Browser `tests/test_s016_browser.py -v -s` (Chromium), `AXE_CORE_PATH` set to a scratch axe-core copy that is not kept as evidence (the G5-conditions re-run in §11 uses `/workspace/qa-tools/node_modules/axe-core/axe.min.js`) | **46 passed**. `grep -c PASSED browser.log` = 46. The accessibility case also prints `axe WCAG checks PASS`. The suite binds an ephemeral port; host previews on 8769–8773 were left alone. | `browser.log` |
| API `audit/run_api_checks.py` under `unshare -rn` (own :8769 inside the namespace after `ip link set lo up`; host previews 8769–8773 untouched, same PIDs) | **PASS 20/20** | `api.log` |
| Release `scripts/verify_release_documents.py` | 9 artifacts, errors=0 | `release.log` |
| Assets `design/sweelah/verify_assets.py` | PASS: 6 HTML, 15 assets, 21/21 hashes | `assets.log` |

Browser runs regenerated PNGs under `test-artifacts/cxui-*`, `test-artifacts/qa-*` and `test-artifacts/s016/`. Those are not committed.

## 7. Manifest pins

No MANIFEST-pinned file was changed. The pre-existing manifest pin mismatches called out on the pending `fix/manifest-pins` branch are unchanged and were not edited. They did not fail this pytest run (same as on main).

## 8. Visible UI change: **No**

No HTML, CSS, JS, API, service, assistant or rules file was changed. **G5X should not be needed.** This is an internal data file plus tests.

## 9. Status labels

| Item | Status |
|---|---|
| Internal draft labels for all 96 personas, marked draft / not independently reviewed | Implemented but unverified |
| HoP taxonomy applied; first pass derived from existing fields | Implemented but unverified |
| Not imported by or exposed via consumer UI, API or exports (3A) | Implemented but unverified |
| Matching gates, weights and results unchanged | Implemented but unverified (hashes pinned to `823ef72`) |
| No risk tier (1A); CPF fields are patterns only (2A); evidence_level null (7A) | Implemented but unverified |
| Independent expert labels, blind evaluation set, calibration metrics, and issue #3 acceptance | Not applicable (out of scope for this assignment; the issue remains open) |
| Production deploy / Phase 9 | Not applicable (NO-GO) |

## 10. Head of Product review follow-up (AT-PROD-SW3)

HoP review files were read only and were not modified or committed: `/workspace/ai-it-organization/evaluations/acceptance/AT-PROD-SW3-review.md` and `AT-PROD-SW3-corrections.json` in the same folder. Status of that review: **Proposed**.

Outcome: HoP reviewed all 96 records and all 5 label fields (480 field decisions) at `c32ede1`. **475 of 480 values accepted.** 91 of 96 records were accepted in full. `life_stage`, `work_income_type` and `household_context` had no corrections. The five corrections, plus the G-7 rationale hygiene edits, were applied through the generator and the JSON was regenerated. A test (`test_only_hop_allowed_record_fields_differ_from_c32ede1`) pins that every other record field is unchanged versus `c32ede1` (since §11.1 it reads a committed snapshot, not git history).

Labels stay `DRAFT_NOT_INDEPENDENTLY_REVIEWED` with `evidence_level` none (the string `"None"` at this point; JSON null from §11). They must not be used to sort, filter or prioritise personas before the 7A research gate. This sign-off, once HoP re-reads the diff, would be a Product draft only and would not meet issue #3's bar of independent labelling and calibration.

### 10.1 The five value corrections

Cross-checked against `AT-PROD-SW3-corrections.json`.

| persona_id | field | from (`c32ede1`) | to |
|---|---|---|---|
| A06 | `cpf_retirement_situation` | `varies` | `accumulating` |
| A08 | `cpf_retirement_situation` | `varies` | `payout_started` |
| A03 | `planning_complexity` | `elevated` | `standard` |
| A04 | `planning_complexity` | `elevated` | `standard` |
| K02 | `planning_complexity` | `elevated` | `specialist_review_suggested` |

Limited JSON record-field diff versus `c32ede1` (header-only additions are listed in §10.3):

```
A03.planning_complexity: elevated -> standard
A03.planning_complexity_reason:
  - High income with lifestyle inflation and asset-growth goals raises planning difficulty.
  + High income with investment assets and a retirement goal, and no constraint predicate, is a standard planning situation, on the same footing as H02.

A04.planning_complexity: elevated -> standard
A04.planning_complexity_reason:
  - Joint planning for a dual-earner household raises coordination difficulty.
  + Joint dual-earner planning with no constraint predicate is a standard planning situation, on the same footing as D01.

A06.cpf_retirement_situation: varies -> accumulating
A06.rationale: contribution-gap wording now maps to accumulating as a pattern, not an entitlement.

A08.cpf_retirement_situation: varies -> payout_started
A08.rationale: cpf_income now maps to payout_started as a pattern, not an entitlement, consistent with B08, G08, I07, L03 and L04; work is recorded separately in work_income_type.

K02.planning_complexity: elevated -> specialist_review_suggested
K02.planning_complexity_reason:
  - A new PR transition involving CPF and overseas assets raises planning difficulty.
  + foreign_pension and overseas_assets, with a transition in CPF and overseas assets, match the same multi-jurisdiction pattern as K06 and K08 and suggest specialist review.
```

### 10.2 Rationale hygiene (G-7) and 3A isolation

"needs Head of Product review" was removed from the E02, K06 and K07 rationales. No enum values on those records changed. K06 and K07 still map the pass gates to `salaried`, now worded as employer-sponsored employment passes (HoP upheld this).

A header field `planning_complexity_reason_visibility` and a generator comment state that `planning_complexity_reason` text (including L08 "protective referral" and "specialist review") is internal only under decision 3A. `test_planning_complexity_reasons_stay_internal_only` checks the header and greps every consumer path (`api.py`, `service.py`, `ui.html`, `assistant.py` and the rest of the listed consumer files) for the labels filename and for every complexity reason, including "protective referral".

### 10.3 Header-only additions

The records list is otherwise unchanged. The header gained:

- a sentence on `usage_restriction` forbidding sort, filter or prioritisation before the 7A research gate
- `hop_review` recording the Proposed 475-of-480 outcome
- `planning_complexity_reason_visibility` (3A, internal only)

### 10.4 Upheld judgement calls

HoP upheld the first-pass judgements in REPORT.md §4, except item 14 (A08 CPF), which is the A08 correction above, and except the three complexity corrections (A03, A04, K02). Upheld as-is: E02 and G04 life-stage (and G04 `not_working` / `payout_deferred`); A08 and B04 `spans_stages` despite `age_60plus`; B02 `spans_stages` despite `age_45plus`; G01 and G02 `spans_stages` despite `age_under_65`; the `late_career` / `retirement_soon` group; retirees without an age band; K06 and K07 `salaried` from pass gates; G07 `mixed`; A04 `salaried` from criteria `employee`; all seven household-overlap choices; MediSave-only and platform-not-opted-in `limited_or_no_cpf`; L05 rental income as not a work type; H07 `employer_shares` as not a work type; and J02, E03 and J08 work unknown as `not_applicable`.

### 10.5 Distribution after the corrections (96 records)

| Field | After HoP corrections |
|---|---|
| `life_stage` | `spans_stages` 81, `payout_age_65_plus` 13, `near_retirement_55_64` 2, `pre_retirement_45_54` 0 |
| `work_income_type` | `not_applicable` 48, `not_working` 16, `salaried` 12, `self_employed_or_commission` 11, `platform_gig` 7, `mixed` 2 |
| `cpf_retirement_situation` | `varies` 69, `limited_or_no_cpf` 11, `accumulating` 7, `payout_started` 7, `payout_deferred` 2, `approaching_55_ra_formation` 0 |
| `household_context` | `varies` 69, `dependants` 10, `couple` 5, `single` 5, `caregiver` 5, `multi_generation` 2 |
| `planning_complexity` | `elevated` 66, `specialist_review_suggested` 21, `standard` 9 |
| `label_status` | `DRAFT_NOT_INDEPENDENTLY_REVIEWED` 96 |
| `evidence_level` | `"None"` 96 (string; JSON `null` 96 after §11.2) |

This matches the "after" column in the HoP review §5.

### 10.6 HoP taxonomy notes for later (Proposed; not actioned)

These are HoP's G-3 and G-4 notes, held as Proposed. They are not a change to this file.

- The `work_income_type` enum has no unknown / `varies` value. `not_applicable` currently covers both "work is not the organising question" and "the person works but the type is unstated" (E03, J02, H01, H02, G01). A later revision could add `varies_or_unstated` and keep `not_applicable` for personas where work is genuinely irrelevant.
- The CPF enum has no value for "RA formed, payout not started" (post-55 and pre-payout; E02, G01, and G04 apart from deferral). A high CPF balance (H03) also has no matching enum. Both currently fall into `varies`.

A change to the approved taxonomy may need Sponsor approval through the CoS. They are not actioned in this commit.

### 10.7 Tests and suites for this follow-up

Tests now total **213** (the original 203 plus 10 HoP-correction tests). The new tests were written first.

| Phase | Result | Log |
|---|---|---|
| Red (pin tests added, JSON still at `c32ede1`) | **10 failed, 203 passed**. The ten failures are the five value pins, the A08 rationale pin, the K02 reason pin, the G-7 wording check, the c32ede1-diff pin, and the 3A header/isolation check. | `hop-red-phase.log` |
| Green targeted | **213 passed**, 0 failed. | `hop-green-phase-targeted.log` |

Full suites on this follow-up, run with `/workspace/sweelah-baseline-venv` (Python 3.13.5) on 10 Nov 2026, after 10:24pm SGT (Asia/Singapore, UTC+8). Host previews on 8769–8773 were left running.

| Suite | Result | Log |
|---|---|---|
| `pytest -q -rs` (full), `AXE_CORE_PATH` set to a scratch axe-core copy that is not kept as evidence (the G5-conditions re-run in §11 uses `/workspace/qa-tools/node_modules/axe-core/axe.min.js`), `PYTHONPATH=.` | **1034 passed**, 0 failed, 0 skipped, 1 third-party DeprecationWarning (starlette/anyio). That is 821 existing + 213 issue-3 tests. | `hop-pytest.log` |
| Rules `PYTHONPATH=. audit/run_rule_contracts_v22.py` | **498 passed, 0 failed** | `hop-rules.log` |
| Browser `tests/test_s016_browser.py -v -s` (Chromium), `AXE_CORE_PATH` set to a scratch axe-core copy that is not kept as evidence (the G5-conditions re-run in §11 uses `/workspace/qa-tools/node_modules/axe-core/axe.min.js`) | **46 passed**. `grep -c PASSED hop-browser.log` = 46. The accessibility case also prints `axe WCAG checks PASS`. The suite binds an ephemeral port; host previews on 8769–8773 were left alone. | `hop-browser.log` |
| API `audit/run_api_checks.py` under `unshare -rn` (own :8769 inside the namespace after `ip link set lo up`; host previews 8769–8773 untouched, same PIDs) | **PASS 20/20** | `hop-api.log` |
| Release `scripts/verify_release_documents.py` | 9 artifacts, errors=0 | `hop-release.log` |
| Assets `design/sweelah/verify_assets.py` | PASS: 6 HTML, 15 assets, 21/21 hashes | `hop-assets.log` |

No MANIFEST-pinned file was changed. No UI change; G5X should not be needed.

## 11. QA G5 conditions on `8e812e0` (PASS with conditions)

QA VERDICT: `/workspace/qa-sweelah-issue-3-8e812e0/qa/issue-3-8e812e0/VERDICT.md` (QA branch `qa/issue-3-8e812e0-verify` @ `a00af1a`), read as data. CoS decisions (14 Nov 2026): evidence_level becomes JSON null unless that would move a HoP-approved value; close all four test gaps; record the move of the base to `5fe3ec8`. Run 14 Nov 2026 from 09:53 SGT (Asia/Singapore, UTC+8). No CI config was changed. Nothing pushed.

### 11.1 Condition 1 (merge-blocking): history-free c32ede1 comparison

- **Cause.** `test_only_hop_allowed_record_fields_differ_from_c32ede1` ran `git show c32ede1:…`. CI uses `actions/checkout@v4` at depth 1, so `c32ede1` is absent. Reproduced in a depth-1 clone of `8e812e0`: `fatal: invalid object name 'c32ede1'`, **1 failed, 212 passed** (`g5c-shallow-clone-red.log`).
- **Fix.** `tests/fixtures/issue3/persona_draft_labels_issue3_c32ede1.json` is a byte-identical copy of `c32ede1:data/persona_draft_labels_issue3.json`, SHA-256 `ceec1f434d280d99406cc41e3e3e374042bb3c20cf792b9be22d73d202b11de4`, pinned in the test (`C32EDE1_SNAPSHOT_SHA256`). The test reads the snapshot and checks the hash before using it; no git call remains in the issue-3 tests. `test_c32ede1_snapshot_is_committed_and_pinned` guards the fixture. The comparison also allows exactly one extra transform, `evidence_level` `"None"` → `null` (§11.2).
- **Proof.** The issue-3 tests in a tree with no `.git` at all (index exported with `git checkout-index`) pass: `g5c-no-history-tree.log`. The depth-1 clone of the committed branch is reported with the commit (it cannot be inside the commit it tests).

### 11.2 Condition: `evidence_level` was the string "None"

- **Finding.** Accidental, not an enum. The generator had `EVIDENCE_NONE = "None"`, and the test mirrored it. No schema, enum or decision document defines an evidence-level vocabulary: `docs/APPROVED_DECISIONS_v2.7.md` D-007/7A only says favourable consumer testing is assumed for development planning. REPORT prose said "evidence_level None", meaning "no evidence". This was a str(None)-style leak of Python's `None` into the JSON as text.
- **Fix (CoS decision).** `EVIDENCE_NONE = None` in `scripts/build_persona_draft_labels_issue3.py`; regenerated. The header and all 96 records now carry JSON `null`. Prose fields (`decision_7A`, `hop_review`) are unchanged.
- **Schema.** There is no separate schema file. The field contract lives in this REPORT §1 and in the tests: `evidence_level` is JSON `null`, asserted by `test_every_value_is_in_its_enum_and_draft_fields_are_present` (`is None`) and `test_evidence_level_is_json_null_not_the_string_none` (no `"None"` string; exactly 97 `"evidence_level": null` lines).
- **HoP-signed values unchanged.** `git diff 8e812e0` on the JSON is 97 lines out and 97 in, all `"evidence_level": "None"` → `"evidence_level": null` (1 header + 96 records). All 480 label values (5 fields × 96) compared: **0 changed** (`g5c-value-diff.log`). Two pins enforce it: `test_hop_signed_label_values_unchanged_since_8e812e0` (SHA-256 of the 480 values, `4ddbbf3b…`) and `test_only_evidence_level_changed_since_hop_signed_8e812e0` (SHA-256 of the whole 8e812e0 document minus every `evidence_level` key, `324631c6…`).

### 11.3 Test gaps C6, C7, B4, E2/E3: all closed

Each new check was proven against a mutant the old check missed (`g5c-gap-mutants.log`: each mutant applied alone to a scratch copy; the old test passes, the new test fails):

| Gap | New test(s) | Mutant: old test → new test |
|---|---|---|
| C6 subpackage reader | `test_labels_not_referenced_anywhere_under_retirepilot_including_subpackages` (recursive `rglob`, skips `__pycache__`) | `retirepilot/plugins/reader.py` naming the file: passed → failed |
| C7 split-string filename | the recursive test above plus `test_consumer_paths_have_no_split_or_concatenated_labels_reference` (needles also matched after dropping every non-alphanumeric character); `test_isolation_scan_catches_split_references_in_a_subpackage` (5 cases); `test_collapsed_needles_do_not_flag_unrelated_text` | `"persona_draft_" + "labels_issue3.json"` in `service.py`: passed → failed; `"_".join(["persona","draft","labels"])` in `api.py`: passed → failed |
| B4 camelCase `riskTier` | `test_no_risk_tier_or_score_key_in_any_case_style` (keys normalised to lower-case alphanumerics: `risktier`, `risklevel`, `riskrating`, `riskgrade`, `riskband`, `score`, `weight`, `percent`, `confidence`, `probability`); `test_forbidden_key_check_catches_case_variants` (11 cases) | `"riskTier": "low"` on A01: passed → failed |
| E2/E3 wording, all records | `test_no_record_says_needs_head_of_product_review` (every string field of all 96 records; case, whitespace, NBSP and hyphen tolerant; also "needs HoP review"); `test_needs_hop_review_check_catches_variants` (5 cases) | wording appended to A01 rationale: passed → failed |

None of the new checks found anything in the real data or package; they fail only on the mutants. Known limit: a filename built at runtime from computed pieces (for example `%`-formatting of separate variables, or bytes decoding) is not caught by a static scan.

### 11.4 Base and trial merge

`git merge-tree --write-tree 5fe3ec8 <commit>` (git 2.x, no working-tree change): **clean, no conflicts** on the staged tree of this commit (`g5c-merge-tree.log`). For reference, at `8e812e0` the result was also clean (tree `6494dc27…`, matching QA). Parent chain unchanged; no rebase.

### 11.5 Tests and suites

Issue-3 tests: **243** (213 + 30 new).

| Phase | Result | Log |
|---|---|---|
| Red (new tests, data and generator still at `8e812e0`) | **97 failed, 146 passed**: the 96 per-record `evidence_level is None` checks and the JSON-null check. The gap tests pass on clean data and are proven red by the mutants in §11.3. | `g5c-red-phase.log` |
| Green targeted | **243 passed** | `g5c-green-targeted.log` |
| No-history tree (no `.git`) | **243 passed** | `g5c-no-history-tree.log` |
| Full `pytest -q -rs`, venv `/workspace/sweelah-baseline-venv` (Python 3.13.5), `PYTHONPATH=.`, `AXE_CORE_PATH=/workspace/qa-tools/node_modules/axe-core/axe.min.js` (includes the 46 browser tests and the axe check) | **1064 passed**, 0 failed, 0 skipped, 1 third-party DeprecationWarning. 821 existing + 243 issue-3. | `g5c-pytest.log` |
| Rules `PYTHONPATH=. audit/run_rule_contracts_v22.py` | **498 passed, 0 failed** | `g5c-rules.log` |

Environment: `g5c-env.txt`. API, release and asset checks were not re-run (no code, API, UI or release-document change). No MANIFEST-pinned file changed. No UI change; G5X should not be needed.

### 11.6 Status labels

| Item | Status |
|---|---|
| Condition 1, history-free snapshot test | Implemented but unverified (QA to re-check; local depth-1 proof attached) |
| evidence_level JSON null; 480 HoP-signed values unchanged | Implemented but unverified |
| REPORT §2 hash, base `5fe3ec8`, axe path | Implemented but unverified |
| Gaps C6, C7, B4, E2/E3 | Implemented but unverified |
| CI on GitHub | Blocked (nothing pushed) |
