# SWEELAH-ISSUE-4: Identity, consent and secure household records

> **INTERNAL DESIGN DRAFT — NOT IMPLEMENTED.**
>
> This document is an engineering design only. It is **not** an implementation, **not** a security sign-off, **not** a qualified privacy or PDPA review, and **not** legal advice. No external identity or consent provider is approved. No Singpass, Myinfo, email, or other live integration is authorised by this draft. No production deploy, no paid service, and no real-person data follow from it.
>
> **Issue #4 acceptance criteria are not met by a design document.** Phase 7 (independent assurance) and Phase 8 (consumer research) are skipped. Phase 9 remains **NO-GO**. Status of this work: **Proposed**.

| Field | Value |
|---|---|
| Status | **Proposed** (design draft only) |
| Issue | [eddiepiper/Sweelah#4](https://github.com/eddiepiper/Sweelah/issues/4) — *P0 \| Implement production identity, consent and secure household records* |
| Date | 10 November 2026, Asia/Singapore (SGT); **revised 14 November 2026 (SGT)** for QA G5 conditions (see §13) |
| Base | `origin/main` `823ef724cdcf5dfada91a895a51baa60fd6c41ec` (first draft `2d03c9c`; this revision is a new commit on top of it) |
| Branch | `docs/issue-4-identity-consent-design` |
| Audience | Sponsor, Chief of Staff, Engineering, QA, Head of Product |
| Authority of this text | Engineering design input. It does not change approval boundaries, release gates, or SECURITY.md rules. |

---

## 1. Context and current state

**Status of the current system: Implemented, locally tested, not production-authorised.**

Sweelah / RetirePilot is a local, synthetic-only research prototype. `SECURITY.md`, `README.md`, `docs/RELEASE_GATES.md` (gate G4) and `docs/APPROVED_DECISIONS_v2.7.md` decision **D-004** already state that a local encrypted vault is not production identity or consent, and that household financial-record sharing stays blocked until each adult's identity and consent are independently verified.

Issue #4 records the gap: the local vault does not provide authenticated household or tenant separation, production key custody, a reviewed data lifecycle, or independent security and PDPA sign-off. Two issue comments (3 November 2026, UTC) add: an internal audit scored 4/8 production checks as fail (anonymous API, `RP-SYNTH-` prefix is not data validation, local consent lacks authenticated evidence, no production auth/TLS/tenant/rate-limit controls); product decision 4A was approved, and `share_household_records` was added as a fail-closed refusal. Synthetic consent is not verified consent. The issue remains **OPEN**. Phase 9 is **NO-GO**.

This section describes what is in `823ef72`, inspected read-only.

### 1.1 Local vault (`retirepilot/local_vault_v24.py`)

The module documents itself as an encrypted **local synthetic-only** persistence boundary, not an authenticated multi-tenant production platform, and not a remote API.

| Control | What exists today | Limit |
|---|---|---|
| Record eligibility | `put_profile` and `grant_consent` refuse any profile id that does not start with `RP-SYNTH-` | Prefix check is not proof that the payload is synthetic or that no real data was typed in |
| Encryption | Fernet (symmetric) over JSON for `profile`, `action` and `memory` blobs. Key from `RETIREPILOT_VAULT_KEY` or a constructor argument; the module refuses to open without a key and tells the caller not to store the key beside the database | Key is a local secret, not a managed production key. No rotation, HSM, or split custody. The module itself notes that the process owner can access the running process |
| File permissions | Parent directory `0700`; database file `0600`; open refused if group/other bits are set | Local POSIX only. No tenancy boundary between households beyond "one file on one machine" |
| SQLite hardening | `foreign_keys=ON`, `secure_delete=ON`, `journal_mode=DELETE` | Metadata is **not** encrypted. `secure_delete` is best-effort, not cryptographic erasure, and is untested against residual copies (backups, snapshots, swap) |
| Consent table | Plaintext rows: `profile_id`, `person_id`, `purpose`, `granted_at`, `revoked_at`. Purposes are exactly `household_planning`, `local_memory`, `action_tracking`. `grant_consent(..., explicit=True)` is required | A function call with `explicit=True` is not authenticated identity and not evidence of informed consent. There is no per-recipient sharing purpose because sharing is refused. **Revoked consent rows are not deleted:** they stay in plain text (with `revoked_at` set) until `delete_profile` removes them (QA G5, FINDINGS C11) |
| Adult consent gate | Every adult (age ≥ 18 on `as_of`, including the primary) must have unrevoked `household_planning` consent before a profile can be written or read | Age is computed from the profile's own date of birth. There is no identity proof behind that date of birth |
| Withdrawal | Revoking `household_planning` deletes the whole profile (fail-closed). Revoking `local_memory` or `action_tracking` deletes that person's memory or actions only | Deletion is a SQL `DELETE` in the local file. No tested backup, restore, or legal-hold path. Audit rows are kept. Consent rows, including revoked ones, are kept in plain text until `delete_profile` (which removes profile and consent rows but still keeps audit rows) |
| Audit | Append-only rows of time, HMAC profile digest (keyed with the Fernet signing key, truncated), and operation name | Not a production audit trail: local, unsigned as a log, no integrity chain, no operator identity, digest is not a personal identifier but is still a linkable token for anyone who has the key |
| Sharing | `share_household_records` **always** raises `VaultError`. Self-declared "identity evidence" or "consent evidence" is ignored | This is the D-004 control. It is a hard block, not a temporary flag |
| Action verification | Real `verified` is refused. `simulated_verified` requires synthetic evidence and a distinct mock verifier, and sets `verified_complete=False` | Matches the SECURITY.md rule that `simulated_verified` is not independent proof. (QA note: the refusal of `verified` currently comes from the state-transition table; the dedicated `verified` branch is unreachable.) |
| Identifier fields | **None.** There is no key allow-list or identifier check in `core.validate` or `LocalVault` | QA G5 showed the vault **accepts and round-trips** a synthetic `nric` field once consent is granted (encrypted at rest; plaintext not in the db file), and also stores identifier-named keys (`fin`, `cpf_account_number`, `bank_account`, `card_number`) and NRIC-like text in memory summaries. The §6 rule is therefore **not enforced** (§6.1) |

Covering tests live mainly in `tests/test_roadmap_v24.py` and `tests/test_approved_decisions_v27.py` (key required; all-adult consent; encryption hides a date of birth on disk; revocation deletes the profile or purpose data; wrong key cannot decrypt; real-looking profile ids rejected; sharing always blocked). `audit/demo_vault_workflow_v24.py` is an ephemeral synthetic smoke demo that deletes the profile at the end.

### 1.2 Validation-layer consent (`retirepilot/core.py`)

`core.validate` is separate from the vault. It requires `consent_for_household_planning is True` on every non-primary member aged 18 or over on `as_of` before that member's CPF balances or other referenced financial records are accepted. The check is age-based, not role-based: an adult with `role: "child"` is still checked (QA G5, FINDINGS C14); only members under 18 and the primary are skipped. The primary is not required to carry this boolean (the vault still requires the primary's `grant_consent`). This is a field on a JSON document, not an authentication event. Tests in `tests/test_phase7_independent_audit.py` pin the spouse-consent behaviour. A boolean in a fixture is still synthetic consent.

### 1.3 API and release controls (`retirepilot/api.py`)

The API is documented as a **local-only** research prototype (`127.0.0.1`, never expose to the public internet). There is no login, session, tenant, TLS termination, or rate-limit layer in the application. The JSON evaluation endpoints accept JSON, require a profile id starting with `RP-SYNTH-`, and evaluate in memory (the plain GET endpoints, such as `/`, `/api/sample`, `/api/scenarios`, `/api/release-controls` and `/sweelah`, take no profile). They do not read or write the vault. `/api/release-controls` is fail-closed and public: `identity_verification=not_integrated`, `independent_adult_consent=not_verified`, `household_sharing=blocked`, `external_consumer_pilot=NO_GO`. An anonymous caller on a bound port can submit any synthetic-looking payload. That is acceptable only while the process stays local and synthetic.

### 1.4 Onboarding (design prototype, read-only)

There is no production onboarding service in this repository. What exists is a **client-side UI concept** under `design/sweelah/prototypes/` (`SweeLah_Onboarding_Prototype.html` and related dashboard variants). README.md already states that this design does not alter production data controls or Phase 9 status.

Observed behaviour, inspected on `823ef72`:

- Six in-browser steps: life chapter, income type, household members (roles only), what matters, optional money amounts (cash, CPF total, monthly income, monthly expenses), confirmation.
- Copy states: "No Singpass, bank connections or documents needed for this demo"; "No need for your full NRIC or date of birth here"; "We are not asking for anyone else's financial records"; a partner's or other adult's details can be shared only after that person separately verifies identity and consents, and "this demo does not collect those records"; "These amounts stay in this browser view only. Nothing is sent or permanently stored."
- Onboarding inputs are numeric amounts and category choices. The onboarding steps have no email, password, login, NRIC, date of birth, postal code, or document upload field.
- **Free-text "Ask Swee" chat box.** The same prototype file has a free-text chat input in the post-onboarding dashboard (`#chat-question`, `maxlength` 150). A user can type anything there, including an NRIC/FIN, a CPF account number, or a bank or card number. On `823ef72` the text is only matched locally against a few topic keywords to pick a canned view; it is not sent, stored, or rendered back (QA G5, FINDINGS C16, exercised with synthetic identifiers). It is still a place where personal data may be typed, so it falls under the §6 rule and threat T7.
  - **Proposed fix (not implemented, not verified):** if this box is ever wired to the API (`/api/ask`) or to any storage, it must pass through issue #5's personal-data guardrails: normalise the text, then refuse NRIC/FIN, CPF account, bank and card patterns before any processing, logging or storage. That guardrail work is on branch `feat/issue-5-assistant-guardrails`; its latest fix commit (`bdc4fb3`, on top of `de9d27b`, which failed QA G5) has **not yet passed QA**. Until it does, this link is a proposal only. A client-side copy of the same check, plus copy beside the box such as "Don't type your NRIC or account numbers here", is a further Proposed option for the prototype.
- Nothing is posted to the vault or the API. Refreshing the page drops the in-memory state.

The engine's household schema (used by fixtures such as `data/mixed_income_household.json`) is richer than the onboarding demo: synthetic person ids, dates of birth, residency, optional user-reported CPF **balances** by account type (OA/SA/MA/RA), income, assets and liabilities. Those fixtures are labelled `RP-SYNTH-*`. They are not created by the onboarding prototype.

### 1.5 What is absent

No authenticated user. No household or tenant isolation on a server. No roles beyond profile `role` strings (`primary`, `spouse`, `child`, …). No production key management, backup, tested retention, or incident process. No cross-border processing design, because there is no hosted service. No independent security test, no qualified PDPA review, and no secret-scanning sign-off as a release gate (issue #4 work items). Gate **G4** in `docs/RELEASE_GATES.md` is **OPEN**.

---

## 2. Goals and non-goals

### 2.1 Goals of this document (**Proposed**)

1. Describe the current identity and consent posture accurately, so it is not mistaken for production security.
2. Compare realistic options for a future production path, with trade-offs, without implementing any of them.
3. Recommend what to do **now** (Phase 9 NO-GO) and what a later, gated path could look like if the Sponsor later authorises it.
4. Define a consent model that is purpose-specific, granular, withdrawable and auditable, with data minimisation and retention.
5. Classify data and state an explicit design rule that the prototype must not store NRIC/FIN, CPF account or membership numbers, or bank account or payment-card data. That rule is **not currently enforced in code** (§6.1); an enforcement control is Proposed (§6.2).
6. Record a threat model and PDPA considerations (not legal advice).
7. Tie any future work to Phase 7 / 8 / 9 and to issue #4's acceptance criteria, including the fact that those phases are skipped or NO-GO today.
8. List open questions only the Sponsor can answer.

### 2.2 Non-goals (**Not applicable** to this branch)

- No code, UI, API, config, workflow, or manifest changes.
- No Singpass, Myinfo, CorpPass, email, SMS, or other live integration; no accounts, API keys, certificates, or paid services.
- No production deploy, no internet exposure of the local API, no real-user or real-household data.
- No change to `share_household_records` (it stays refused) and no change to `/api/release-controls`.
- No attempt to close issue #4 or to move G4 or Phase 9.
- No qualified legal, PDPA, or security opinion, and no engagement of paid reviewers (D-006: quotes and approval first).
- No new profile field and no visible UI change.

---

## 3. Options compared

All three options are **Proposed** discussion only. None is implemented on this branch.

### Option A — No identity / local-only (current posture)

Keep the prototype as it is: local vault, synthetic ids, in-browser onboarding with no account, fail-closed household sharing, no external identity provider.

| | |
|---|---|
| Strengths | Matches the current Sponsor and CoS constraints (no paid services, no production deploy, no real user data, no NRIC/CPF/bank identifiers, no external emails). No new attack surface, no partner onboarding, no key or certificate to leak. The D-004 sharing block already exists. Honest about Phase 9 NO-GO. |
| Weaknesses | Cannot meet issue #4 acceptance (tenancy isolation and data lifecycle *on a deployed architecture*; qualified PDPA review). Cannot support authenticated sessions, role-based access, or per-adult verified sharing. Local key and process-owner access remain residual risks even for synthetic data. A user could still type real data into a local form or API; the `RP-SYNTH-` prefix does not prevent that. |
| Fit now | **High.** This is the only option that can be operated under the present gates. |

### Option B — Email magic link (or similar mailbox-based account)

Issue a one-time sign-in link to an email address, and treat the mailbox as the account.

| | |
|---|---|
| Strengths | Familiar UX; possible later for a single person's *session* (save-and-resume) without government onboarding. Does not require collecting an NRIC. |
| Weaknesses | Email is not a verified legal identity. It does **not** satisfy D-004 or issue #4 for sharing another adult's financial records: anyone who can open a mailbox, or who types another person's address, is not "that adult". It requires outbound email (currently disallowed without Sponsor approval), a hosted token service, and abuse controls. Mailbox compromise, link forwarding, and phishing are first-class threats. Still no tenancy, key custody, or PDPA sign-off by itself. |
| Fit now | **Poor** as a substitute for adult identity. **Possible later**, only as a *weaker* session mechanism for a single user who has already been told it is not identity verification, and only if outbound email and hosting are separately approved. It must never unlock household sharing. |

### Option C — Singpass Login, with Myinfo only if a later approved use case needs it

[Singpass Login](https://docs.developer.singpass.gov.sg/docs/products/singpass-login) is a passwordless authentication gateway: the resident authenticates in the Singpass app (biometrics, passcode, or SMS OTP). [Singpass Myinfo](https://docs.developer.singpass.gov.sg/docs/products/singpass-myinfo) is a separate product: with the person's consent, a relying party may retrieve government-sourced personal data for the scopes it was approved to request. Official developer documentation (accessed 10 November 2026, Asia/Singapore; re-checked 14 November 2026 for the items marked in §13) also states that:

- new Myinfo integrations use the current (v5) API; the FAQ gave v3/v4 partners "till end Sep 2026" to migrate (that date had already passed when this draft was written, so any new work would be v5 only), and Singpass APIs must be FAPI 2.0 compliant by 31 December 2026;
- scope requests are reviewed; relying parties must not request more data than the service needs (explicitly aligned, in the FAQ, with PDPA collection practices);
- every Myinfo retrieval must be shown to the user for verification before use; data must be freshly fetched, not reused from a cookie or stale session; digital services **should** let users who decline Myinfo, lack Singpass, or meet an outage fill in forms manually (the FAQ says "should", not "must");
- Myinfo API charges began in April 2022 (pricing is behind a Singpass login on the developer portal);
- production app registration requires a Singpass Service Agreement and an approval cycle the docs estimate at up to two weeks.

| | |
|---|---|
| Strengths | A government-run digital identity for Singapore citizens, permanent residents and FIN holders (calling it the "strongest" option, as the first draft did, was our opinion and is withdrawn). Each adult can authenticate as themselves, which is what D-004 requires before any sharing. Myinfo, if ever approved, can supply *verified attributes* under purpose-specific scopes rather than the app inventing an identity proof. Official docs already push data minimisation and user-visible confirmation. Singpass Login returns a subject identifier (`sub`), which the official ID-token documentation describes as "a globally unique identifier for the user" (a UUID in the samples). Login can be used with the UUID only, instead of NRIC/FIN (Login Key Principles, "Option 2: UUID only"). So `sub` can identify a returning user **without storing an NRIC, but only if the `user.identity` scope is not requested** (see Weaknesses). The first draft called `sub` "pairwise"; no official Singpass source found says that, so the word is withdrawn. Because the official text says *globally* unique, we assume `sub` may be the same across relying parties and is therefore a linkable personal identifier that must be protected (INTERNAL ASSUMPTION: the docs do not state whether it is per-client). |
| Weaknesses | Not authorised now. Partner onboarding, legal agreement, and (for Myinfo) **paid usage** would need explicit Sponsor approval, which this draft does not give. Implementation would be a production-shaped integration (FAPI, keys, redirect URIs, incident response) on a prototype that is not allowed to deploy or to hold real-person data. **Singpass Login itself can return the NRIC/FIN, not only Myinfo:** if the `user.identity` scope is requested, the ID token's `sub_attributes.identity_number` carries the NRIC (citizens and PRs) or FIN (FIN holders). Myinfo can also return national identifiers (`uinfin`) and, for some scopes, CPF-related data such as up to 15 months of CPF contribution history. Persisting any of those would break the rule in §6 and conflict with PDPC NRIC guidance (§8); because that rule is not yet enforced in code (§6.1), requesting `user.identity` would put an NRIC straight into a path that nothing stops from being stored. People without Singpass need a fallback. This option still cannot close issue #4 without Phase 7 reviews and a Phase 9 decision. |
| Fit now | **Blocked.** Appropriate only as a *target* architecture if and when Phases 7 and 8 are un-skipped, paid/legal onboarding is approved, and Phase 9 is no longer NO-GO. |

### Comparison (summary)

| Criterion | A. Local-only | B. Email magic link | C. Singpass ± Myinfo |
|---|---|---|---|
| Meets D-004 (per-adult verified identity before sharing) | No; sharing stays blocked | No | Yes, in principle, after onboarding and reviews |
| Meets issue #4 acceptance by itself | No | No | No (reviews and a deployed architecture still required) |
| Allowed under current Phase 9 NO-GO and CoS constraints | Yes | Not without email and hosting approval | No |
| Paid service / partner agreement | None | Email vendor likely | Myinfo is charged; Singpass Service Agreement required |
| Risk of holding NRIC/CPF/bank identifiers | Low if §6 rule is kept | Low if not collected | High unless scopes and retention are tightly constrained |
| Residual prototype risks (local key, process owner) | Remain | Remain unless a hosted design replaces the vault | Remain until a reviewed hosted design replaces the vault |

---

## 4. Recommended approach

**Status: Proposed. Not implemented. Not approved for integration.**

**Now (internal prototype, Phase 9 NO-GO):** stay on Option A. Do not add an identity provider, an email sign-in, or Myinfo. Keep household sharing fail-closed. Keep synthetic-only vault and API guards. Treat in-browser onboarding as a non-persistent demo. Keep the §6 rule against storing NRIC/FIN, CPF account or membership numbers, and bank account or payment-card data. Today that rule is a design rule only, **not enforced in code** (§6.1); the enforcement control in §6.2 is Proposed and needs its own assignment with failing tests first.

**Later, only if the Sponsor un-skips Phase 7, commissions the reviews in §9, and eventually lifts the Phase 9 NO-GO:** the target architecture is Option C in a *minimised* form — Singpass Login so each adult authenticates as themselves; do **not** request the `user.identity` scope, and persist only the Singpass `sub` (a globally unique UUID, protected as personal data) plus in-app, purpose-specific consent records; use Myinfo only if a separately approved use case needs a verified attribute, and then only for that scope, shown to the user, and not used as a pretext to store NRIC, CPF account numbers, or bank data. Option B must not be used to unlock sharing or to stand in for identity verification.

Until those gates pass, issue #4 stays open and G4 stays OPEN. This recommendation is a design position, not a release decision.

---

## 5. Consent model

**Status: Proposed** for any future implementation. The local vault already sketches parts of this for synthetic data; that sketch is **not** verified consent.

### 5.1 Principles

1. **Purpose-specific.** Consent is granted for a named purpose, not as a blanket "I agree". Current vault purposes (`household_planning`, `local_memory`, `action_tracking`) are the starting set. A future sharing purpose, if ever approved, would be separate, per recipient, and would remain refuse-by-default until D-004 is actually met.
2. **Granular.** An adult can grant one purpose and refuse another. Withdrawal of an optional purpose must not be bundled with withdrawal of a purpose that is strictly necessary to hold the profile. Source: PDPC *Advisory Guidelines on Key Concepts in the PDPA* (revised 29 April 2026), Consent chapter, "Organisations must allow and facilitate the withdrawal of consent", p. 55: "Individuals must be allowed to withdraw consent for optional purposes without concurrently withdrawing consent for the necessary purposes." Which of our purposes counts as "optional" (we treat `local_memory` and `action_tracking` as optional, and `household_planning` as necessary to hold a plan) is **our own reading (INTERNAL ASSUMPTION)**, not PDPC's. If `household_planning` is withdrawn, the financial profile is deleted (already the vault's fail-closed behaviour).
3. **Independent per adult.** Decision D-004: each adult's identity and consent are verified separately before that adult's financial records are shared. One household member cannot consent for another adult. A self-declared checkbox, username, or "I have permission" statement is not enough.
4. **Withdrawable.** Withdrawal is always available, with a clear statement of the consequence (for example, "your household plan on this device will be deleted"). After withdrawal, collection, use and disclosure for that purpose cease, and associated data is deleted or irreversibly disassociated, subject only to a later-approved audit-retention rule.
5. **Auditable.** Grant, refusal, withdrawal, and deletion events are recorded with time, purpose, and an operator or subject reference that is not an NRIC. A production log would need tamper evidence, controlled access, and retention limits. Today's local audit table is a prototype aid only.
6. **Data minimisation.** Collect only what the stated purpose requires. Official Myinfo FAQ guidance is the same: do not request more data items than the service needs; each scope request is reviewed.
7. **Retention limitation.** Keep personal data only while the purpose is live or a documented legal or business need remains, then delete or anonymise it. Do not keep data "just in case". Source: PDPC *Advisory Guidelines on Key Concepts in the PDPA* (revised 29 April 2026), ¶18.1, ¶18.4(a)(ii) and ¶18.9 (see §8.2).
8. **Informed and unbundled.** Notify the purpose *before* collection. Do not condition the core educational planning service on consent to unrelated uses (for example marketing, or sharing with another adult).
9. **Minors.** A child in the household model does not grant in-app consent. The app must not collect a child's NRIC or other national identifier. Dependency relationships and a child's year of birth or age band, if ever needed, are a later product decision and still synthetic in the prototype.
10. **No disguised verification.** `simulated_verified` and synthetic consent booleans stay labelled as simulation. They never become "verified" by renaming.

### 5.2 Proposed purpose catalogue (future, not implemented)

| Purpose | What it permits | Withdrawal effect (proposed) |
|---|---|---|
| `household_planning` | Hold and compute on that adult's financial records in the household plan | Delete the stored plan (current vault behaviour) |
| `local_memory` | Store short user-reviewed memory summaries | Delete that person's memories |
| `action_tracking` | Store suggested or approved in-app actions | Delete that person's actions |
| `identity_binding` (future only) | Bind a Singpass `sub` (UUID; requested without `user.identity`) to a local person id | Unbind; do not keep national identifiers |
| `household_sharing_with:{person}` (future only, currently **Blocked**) | Disclose that adult's financial records to one named, authenticated adult | Revoke that disclosure path; do not imply other purposes are withdrawn |

Experimental model use (`explicit_model_consent` on the disabled LLM path) is a separate, already-fail-closed control and is not a household-consent purpose.

### 5.3 Roles (proposed)

| Role | Prototype today | Future production (if approved) |
|---|---|---|
| Primary planner | Unauthenticated local user of a synthetic profile; `core.validate` does not require the consent boolean, but the vault still requires the primary's `household_planning` consent | Authenticated adult; cannot see another adult's financial records without that adult's verified consent |
| Other adult member | Present in fixtures; sharing blocked | Must authenticate and consent independently |
| Child / dependent | Role and date of birth in fixtures; `core.validate` requires no consent boolean for members **under 18** (the check is age-based, so an adult with `role: "child"` is still checked) | No in-app consent; no national identifier stored |
| Process owner / operator | Anyone who can run the local process and read the key | Named, logged, least-privilege admin; no standing access to plaintext household records |
| Security / privacy reviewer | None signed | External; required in Phase 7 before any real data |

---

## 6. Data classification

**Status: Proposed as a standing engineering rule for the prototype; consistent with SECURITY.md. The rule is NOT currently enforced in code (§6.1).**

### Explicit rule (design rule, not yet enforced)

**Design rule: the prototype must not store NRIC or FIN numbers, CPF account or membership numbers, or bank account or payment-card data.** This is a rule people and future code must follow, not a description of what the code prevents today. It must not log them, commit them, put them in fixtures, or send them to a service. This includes copies or partials used as passwords, usernames, or file names. The rule also covers other national identification numbers treated like NRIC in PDPC guidance (including birth-certificate, work-permit and passport numbers). It is not limited to a particular field name.

### 6.1 Enforcement status: not enforced (QA G5 evidence)

QA's G5 review of `2d03c9c` (verdict on `qa/issue-4-2d03c9c-verify` @ `ea0767d`, `qa/issue-4-2d03c9c/VERDICT.md`, spot-check `logs/qa_lead_spotcheck.log`; executor evidence `FINDINGS.md` C18) showed:

- After explicit `household_planning` consent was granted, `LocalVault.put_profile` **accepted** a synthetic profile carrying an `nric` field, and `get_profile` round-tripped it unchanged.
- `core.validate` has no key allow-list. A profile with `nric`, `fin`, `cpf_account_number`, `bank_account` and `card_number` keys was accepted, and the vault stored it. `save_memory` also stored a summary containing an NRIC-like value and a bank number.
- What does hold: the values were **encrypted at rest** (plaintext not found in the db file, before or after revocation). The API and browser UI accepted the same keys but did not echo, log or persist them. The uvicorn access log holds only method, path and status.

So nothing in the prototype *prevents* an identifier from being stored in the vault. Today the rule depends on synthetic-only fixtures, the `RP-SYNTH-` convention, SECURITY.md and review discipline.

### 6.2 Proposed enforcement control (Proposed, not implemented)

**Status: Proposed. No code is changed by this document.** A future assignment, with failing tests written first and G5 to follow, could add:

1. **Shared detector.** Reuse issue #5's normalised identifier detector (`retirepilot/assistant.py` on `feat/issue-5-assistant-guardrails`: `normalise_question` and `find_sensitive_identifier`), moved into a small shared module so the assistant and the vault use the same code. It strips zero-width characters, normalises NBSP, full-width characters and separators, then matches NRIC/FIN with or without separators, CPF account wording, bank and card numbers and compact IBANs. That detector is itself **unverified**: its latest fix (`bdc4fb3`) has not passed QA yet.
2. **Key denylist and allowlist at the vault boundary.** `LocalVault.put_profile` (and `core.validate`, so the API path fails the same way) rejects, with a `VaultError` or `ValidationError` that does not echo the value, any key whose normalised name matches an identifier pattern (for example `nric`, `fin`, `uin`, `uinfin`, `identity_number`, `passport`, `work_permit`, `cpf_account`, `bank_account`, `account_number`, `card_number`, `iban`), at any nesting depth. Longer term, the preferred form is an allowlist: only schema-known keys are accepted.
3. **Value scan.** Every string value in the profile, and every `save_memory` summary and `create_action` title or reason, is run through the shared detector before encryption. A match is refused, not silently redacted, so the caller sees a clear error.
4. **Tests (red first).** Each of these is refused and leaves no row written: an `nric` key; a nested `identity_number` key; NRIC-shaped values with spaces, dots, dashes, zero-width characters or full-width digits under a harmless key; a 16-digit card number in a memory summary. Ordinary amounts, ages, dates of birth and `RP-SYNTH-*` ids are still accepted. Mutation checks, such as removing the key rule or skipping normalisation, must make a test fail.
5. **Out of scope for the control:** it reduces accidental storage; it does not make real-person data allowed, and it is not a substitute for Phase 7 secret scanning or a qualified review.

User-reported **CPF balances** in synthetic fixtures (OA/SA/MA/RA amounts under an `RP-SYNTH-*` id) are not account numbers. They remain allowed only as synthetic research data. Real CPF balances, real official statements, and any CPF identifier are out of scope until a later Sponsor decision allows real-person data, which is **not** allowed now.

### Classification table

| Class | Examples | Prototype rule | Future production (if ever approved) |
|---|---|---|---|
| **Forbidden identifiers** | NRIC/FIN, passport or work-permit numbers, CPF account or membership numbers, bank account or card numbers, Singpass login credentials | **Must not store, log, or transmit** (design rule; not enforced in code today — the vault will store them, encrypted, if given; §6.1. Enforcement Proposed in §6.2) | Still do not persist these. If Singpass Login is used, do not request `user.identity` and keep only the `sub`. If Myinfo ever returns `uinfin` or account numbers, use them in memory for a one-time, user-visible check if a qualified review requires it, then discard |
| **Secrets** | Vault keys, tokens, certificates, `.env` files | Never commit; vault key is supplied at run time, not stored beside the database | Managed production custody, rotation, and access logs, reviewed in Phase 7 |
| **Personal financial data** | Date of birth, residency, income, assets, liabilities, user-reported CPF balances, goals | Synthetic `RP-SYNTH-*` records only. No real-person data | Only after identity and purpose-specific consent; minimised; encrypted at rest; tenancy isolated |
| **Consent and audit metadata** | Purpose, timestamps, profile digest, operation name | Local SQLite; plaintext metadata today | Encrypted or tightly access-controlled; retention cap; no NRIC in the log |
| **In-browser demo state** | Optional amounts in the onboarding prototype | Not sent, not persisted | If onboarding is later wired, it must inherit these classes and the forbidden-identifier rule |
| **Public or non-personal** | Statutory tables, product library, this design document | Allowed | Allowed |

SECURITY.md's "never commit" list (real personal, CPF, health, identity, account, employment, banking or family financial data; credentials; generated vault files; interview recordings) remains in force. This classification does not narrow it.

---

## 7. Threat model

**Status: Proposed.** This is an engineering threat model of the current prototype and of the options in §3. It is **not** an independent security assessment and does not satisfy issue #4's security-review acceptance criterion.

Assumptions: an attacker may be a remote caller if the API is ever bound beyond localhost; a local user or process owner on the same machine; a household member with physical access; a future cloud operator or vendor; or a mistaken commit of real data. The asset of concern is household financial and identity data, plus any secrets that protect it. The prototype should currently hold **only** synthetic data, but the model treats accidental real data as a realistic failure mode.

| ID | Threat | Relevance | Current mitigation | Residual / proposed treatment |
|---|---|---|---|---|
| T1 | Local API or UI exposed on a network and used without authentication | High if someone binds past `127.0.0.1` | Documented local-only; synthetic id prefix; no vault behind the API | Keep local-only while Phase 9 is NO-GO. Do not treat the prefix as tenancy. Any future host needs auth, TLS, tenancy, and rate limits |
| T2 | Vault key leakage (env, shell history, process list, committed `.env`) | High for any data at rest | Key required; gitignore for `.env` and keys; key not stored beside the DB | Production would need managed custody and rotation. Prototype: continue to refuse a missing key and never commit one |
| T3 | Process owner or host administrator reads memory, the key, or the DB | Inherent on a single machine | Documented in the vault module | Acceptable only for synthetic local use. A deployed architecture needs a different trust boundary |
| T4 | Unencrypted SQLite metadata (profile ids, consent rows) leaks or is copied | Medium | File mode `0600` | Do not put real identifiers in metadata. Future design should encrypt or avoid plaintext ids |
| T5 | Synthetic consent or `simulated_verified` treated as real verification | High (already observed as a product risk) | Naming; fail-closed sharing; tests; issue comments | Keep the block. Training and review language must stay explicit |
| T6 | One adult views or exports another adult's records without consent | High in a household product | `share_household_records` always refuses; validate() needs a consent boolean for some cases | Do not weaken the refusal. A future share path requires Option C plus per-recipient consent |
| T7 | Real NRIC, bank, or CPF account data typed in or committed | High impact | Prefix guard, gitignore, SECURITY.md, onboarding copy avoids NRIC. **No technical control:** the vault accepts and stores identifier fields and NRIC-like text (QA G5, §6.1). The prototype's free-text "Ask Swee" box (§1.4) accepts typed identifiers but does not send or store them | Proposed: the §6.2 vault control and issue #5's guardrails on any wired free-text input (both unverified); review discipline; secret scanning is a Phase 7 item, not done here |
| T8 | Weak audit (no chain, no actor identity, local only) hides misuse | Medium | Event names and digests exist | Sufficient for a local demo only. Production needs a reviewed audit design |
| T9 | Deletion or "secure_delete" leaves residual copies (backups, images, logs) | Medium | SQL delete + `secure_delete=ON`; demo deletes the profile | Issue #4 asked for *tested* backup and deletion. That test programme belongs in Phase 7, on a defined architecture, not in this draft |
| T10 | Dependency or supply-chain compromise; secrets in the repo | Medium | CI and gitignore; no production secrets should exist | Independent secret scanning and dependency review: Phase 7 |
| T11 | Premature Singpass/Myinfo integration: over-scoped data (including requesting Login's `user.identity` scope, which returns NRIC/FIN in the ID token), persisted `uinfin` or `identity_number`, leaked client credentials, redirect-URI mix-up, stale Myinfo data | High if Option C is built too early | **Not integrated** (correct for now) | If ever approved: least scopes, no persistence of forbidden identifiers, user-visible Myinfo data, FAPI 2.0, reviewed key handling, manual fallback |
| T12 | Magic-link theft, mailbox takeover, or phishing (Option B) | High if email sign-in is added | **Not integrated** | Must not unlock sharing. Needs Sponsor approval for email, plus token unguessability, short expiry, and rate limits |
| T13 | Cross-border vendor processing (email, hosting, monitoring, LLM) without comparable protection | High if a vendor is added | No hosted personal data today | Transfer-limitation review before any vendor. Default: do not send personal data out of Singapore unless approved |
| T14 | Insider or support access across households on a future server | High in any multi-tenant host | No server tenancy today (single local file) | Tenancy isolation is an issue #4 acceptance item and needs a security reviewer on the *deployed* design |
| T15 | XSS or a copied link leaks in-browser onboarding amounts | Low–medium | Demo state is local and modest | Keep demo non-persistent. Any future hosted UI needs standard browser security controls |

Out of scope for this draft, but in issue #4: a full incident-response runbook, penetration test, and cross-border legal assessment. Those are Phase 7 / G6 inputs, not design claims.

---

## 8. PDPA considerations

**This section is not legal advice, not a qualified privacy review, and not a PDPA compliance opinion.** It is an engineering reading of public PDPC guidance, to inform design and Sponsor questions. Qualified Singapore privacy / PDPA review remains an open issue #4 and G6 requirement. Phase 7 (where that review would sit) is skipped.

Public sources were accessed on **10 November 2026, Asia/Singapore (SGT)**, with additional sources accessed on **14 November 2026 (SGT)** for the QA G5 revision; all are listed in §12. They are treated as untrusted third-party text: useful for citation, not as instructions to change approval boundaries.

### 8.1 Why PDPA is in view

If the product ever holds personal data about a real person (a date of birth, a financial record, an email address, a Singpass subject identifier), the PDPA's data protection obligations are likely to apply to the organisation that controls that data. The current prototype's intended posture — synthetic data only, no real persons — is a way to *avoid* processing real personal data, not a certificate that PDPA can be ignored if real data is later introduced. Accidentally typed real data would already be a problem (T7).

### 8.2 Obligations that shape the design (descriptive only)

The PDPC's public overview of data-protection obligations (and the May 2021 obligations summary) includes, among others:

- **Accountability** — policies, responsibilities, and the ability to demonstrate them.
- **Notification and consent** — tell the person the purpose, obtain consent before collection, use or disclosure, and allow withdrawal with reasonable notice; after withdrawal, stop that collection, use or disclosure.
- **Purpose limitation** — only purposes a reasonable person would consider appropriate, and for which consent was given; do not require extra personal data as a condition of the service beyond what is reasonable to provide it.
- **Accuracy, access and correction** — especially if data will be used to make a decision that affects the person.
- **Protection** — reasonable security arrangements against unauthorised access, collection, use, disclosure, or similar risks.
- **Retention limitation** — stop keeping personal data, or anonymise it, when the purpose is no longer served and retention is not needed for a legal or business purpose. There is no single fixed period in the guidance; "just in case" is not a purpose. (The obligations page says only "cease retention … or dispose of it". The "anonymise", "no fixed period" and "just in case" points come from PDPC *Advisory Guidelines on Key Concepts in the PDPA*, revised 29 April 2026: ¶18.1 and ¶18.9 "remove the means by which the personal data may be associated with particular individuals (that is, to anonymise the data)"; ¶18.2 "does not specify a fixed duration of time"; ¶18.4(a)(ii) "must not be kept … 'just in case'". How this applies to Sweelah is our own reading, not legal advice.)
- **Transfer limitation** — do not transfer personal data outside Singapore except as the PDPA prescribes, with a comparable standard of protection.
- **Data breach notification** — notify PDPC and affected individuals where the statutory threshold is met.
- **Data portability** — noted in PDPC public material as coming into effect when the relevant regulations are issued; not designed here.

The consent model in §5 and the classification in §6 are intended to be *compatible with* those themes (purpose-specific, withdrawable, minimised, deletable, not transferred abroad by default). Compatibility of a sketch with published guidance is **not** compliance.

### 8.3 NRIC and national identifiers

PDPC *Advisory Guidelines on the PDPA for NRIC and other National Identification Numbers* (issued 31 August 2018; the published PDF states that they remain valid while an update is prepared following an MDDI statement of 13 December 2024) say that organisations are **generally not allowed** to collect, use or disclose NRIC numbers (or copies of NRIC), except where required by law (or a PDPA exception applies) or where it is necessary to accurately establish or verify identity to a **high degree of fidelity**. The same treatment extends to FIN, birth-certificate and work-permit numbers. A notice on the same document advises against using NRIC numbers as passwords, or using them to authenticate a person or to set default passwords (PDPC statement of 14 December 2024).

**Design consequence (Proposed, not legal advice):** the prototype is designed not to collect or store NRIC/FIN (a design rule; nothing in the code enforces it today, §6.1), and a future Singpass path should authenticate via the official channel, not request the `user.identity` scope, and persist only the `sub`, not a national ID. (Singpass Login's own FAQ asks integrators to assess which identifier is appropriate, citing these PDPC guidelines.) Even if a later reviewer argued that financial-record sharing needs a high degree of fidelity, that would not, on this reading, justify *keeping* NRIC numbers in our database, using them as usernames, or logging them.

### 8.4 Myinfo and minimisation

If Myinfo were ever approved, official FAQ rules already require least scopes, fresh retrieval, user-visible data, and a manual fallback. Those rules support §4's "Myinfo only if needed, never to stockpile identifiers" position. They do not authorise integration.

### 8.5 What this document does not do

It does not determine whether Sweelah would be a data intermediary or an organisation, whether any exemption applies, what a breach-notification threshold would be, or whether a particular consent wording is valid. Those questions are for qualified counsel, under D-006, if the Sponsor authorises an engagement.

---

## 9. Phased rollout gates

**Status today: Phase 7 skipped, Phase 8 skipped, Phase 9 NO-GO.** No identity implementation is scheduled against these phases until the Sponsor changes that.

This mapping uses the phase list in `docs/PROGRESS_v2.5.md` and the v2.7 release gates in `docs/RELEASE_GATES.md`. Issue #4 is the substance of **G4** (household privacy and security) and part of **G6** (qualified privacy / legal and independent security assessment).

| Phase / gate | Current status | What identity and consent work would require | Allowed now? |
|---|---|---|---|
| Prototype (local, synthetic) | In use | This design; keep Option A; enforce §6; leave sharing blocked | **Yes** (this document only) |
| Phase 7 — Assurance (independent reviewer sign-offs) | **Skipped** | Independent security testing of the *intended deployed architecture*; qualified PDPA / privacy review; secret scanning; tested backup, deletion and retention; incident and cross-border requirements. This is where issue #4's acceptance criteria would be *examined* | **No implementation.** Reviews would also need D-006 (quotes, qualifications, approval) before any paid engagement |
| Phase 8 — Consumer research (48 observed, consented sessions) | **Skipped** (0/48) | Consent UX, withdrawal, and comprehension can be researched only with a reviewed protocol. Research contact data is still personal data. Simulated interviews do not count (D-007) | **No** real participants and no real financial records under this assignment |
| Phase 9 — External pilot / G8 | **NO-GO**, blocked by G2–G7 (G4 and G6 still OPEN) | A named GO, residual-risk acceptance, operations and rollback, and production auth/consent actually in place | **No.** This design does not seek a GO |
| After a future GO (hypothetical) | Not authorised | Only then could Option C be built, in a separate assignment, on its own branch, with failing tests first for each control, and with G5 / G5X as required | **Blocked** now |

**Sequencing if the gates are later opened (Proposed, not a plan to execute):** (1) Sponsor un-skips Phase 7 and authorises reviewer quotes under D-006; (2) security and PDPA reviewers comment on this design and on a concrete architecture; (3) only after those reviews, a separate engineering assignment implements controls on a non-production environment, still without real-person data if the reviewers so require; (4) Phase 8 consent research, if un-skipped, uses a reviewed protocol; (5) Phase 9 GO or continued NO-GO is a Sponsor decision, not an engineering one.

There is no "soft launch" of Singpass, Myinfo, or email sign-in inside the current prototype to get ahead of these gates.

---

## 10. Open questions for the Sponsor

These are decisions Engineering cannot make. Recommended default, where one is given, is the conservative option.

1. **Confirm the hold:** while Phase 9 is NO-GO, is Singpass, Myinfo, email sign-in, or any paid identity service **not** authorised? *Recommended default: confirmed, not authorised.*
2. **Sharing scope:** if a future identity path exists, should household financial-record sharing ever be in scope for a pilot, or should it stay blocked even then?
3. **Phase 7 reviews:** when (if ever) may Engineering request written quotations for a qualified PDPA / privacy review and an independent security test, under D-006, without yet appointing anyone?
4. **Key custody:** if a hosted vault is ever in scope, does the Sponsor prefer organisation-managed keys (HSM or equivalent), user-held keys, or a split model? Staying local-only is still an option.
5. **Data residency:** must any future hosted personal data, backups, and logs remain in Singapore?
6. **Retention:** is "delete on withdrawal, plus a short, reviewed audit-log retention" an acceptable starting rule, and should a numeric cap be set before any implementation?
7. **Provider identifier:** if Singpass Login is later approved, may the Singpass `sub` (a globally unique UUID per the official docs) be the only persistent external identifier, with the `user.identity` scope **not** requested so that no NRIC/FIN is returned? *Recommended default: yes.*
8. **People without Singpass:** must a future production path support a manual fallback (as Myinfo FAQ guidance already expects for form-filling), and if so what weaker identity standard, if any, is acceptable? *Recommended default: fallback for use of the service, but no household sharing without a verified adult identity.*
9. **Phase 8 contact data:** if Phase 8 is later un-skipped, who may hold participant contact details, for how long, and on what system? Those details are personal data even when financial records are not collected.
10. **Vendors and transfers:** is any future vendor (email, hosting, monitoring, model API) that would process personal data, including outside Singapore, in or out of scope pending a separate approval?

---

## 11. Traceability to issue #4 acceptance criteria

Issue #4 acceptance, quoted in substance: a security reviewer confirms tenancy isolation and end-to-end data lifecycle on the **deployed** architecture; a qualified privacy / PDPA review is recorded; **no real-person data until approved**.

| Acceptance / work item from #4 | Where this draft addresses it | Status |
|---|---|---|
| Threat model, authentication, roles, household-member consent and revocation | §5, §7, options in §3, recommendation in §4 | **Proposed** (design only). Not implemented. Not independently reviewed |
| Encrypted storage with managed keys; tested backup, deletion and retention | Current local Fernet vault described in §1.1; gaps (no managed keys, no tested production deletion/backup) in §7 T2/T9 and §9 | **Proposed** for a future architecture. Current controls are local and incomplete against the issue's wording. **Not applicable** to this branch to implement them |
| Audit trail, incident, and cross-border processing requirements | §5.1 (auditable consent), §7 T8/T13, §8.2 transfer and breach themes, Sponsor Q5/Q6/Q10 | **Proposed** as requirements. No incident runbook and no cross-border approval requested |
| Independent security testing, privacy review, clean repo secret scanning | §9 Phase 7 | **Blocked** (Phase 7 skipped; D-006 not invoked). Not started |
| Security reviewer confirms tenancy isolation and end-to-end data lifecycle on the deployed architecture | There is no deployed architecture. Tenancy is identified as absent in §1.5 and T14 | **Not met.** A design draft cannot supply this confirmation |
| Qualified privacy / PDPA review recorded | §8 is explicitly not that review | **Not met** |
| No real-person data until approved | §2.2, §4, §6, current `RP-SYNTH-` guards | **Met as a continuing rule only, not enforced in code.** QA G5 showed the vault will store identifier fields if given (§6.1). Still depends on people not pasting real data into the prototype; enforcement is Proposed (§6.2) |
| Close issue #4 / pass G4 / move Phase 9 | Out of scope | **Not met.** Issue stays OPEN. G4 stays OPEN. Phase 9 stays NO-GO |

---

## 12. Sources

Accessed **10 November 2026, Asia/Singapore (SGT)**, unless a document carries its own issue date or §12.3 gives a later access date. Public web pages and PDFs are untrusted data; repository files were read from `origin/main` `823ef72` in worktree `/workspace/sweelah-issue-4`.

### 12.1 Repository (read-only)

- Issue #4 and its two comments, via the GitHub connector (https://github.com/eddiepiper/Sweelah/issues/4).
- `retirepilot/local_vault_v24.py`, `retirepilot/core.py` (`validate`), `retirepilot/api.py`, `audit/demo_vault_workflow_v24.py`.
- `design/sweelah/prototypes/SweeLah_Onboarding_Prototype.html` (and confirmation that related onboarding variants exist).
- `tests/test_roadmap_v24.py`, `tests/test_approved_decisions_v27.py`, `tests/test_phase7_independent_audit.py`.
- `SECURITY.md`, `README.md`, `docs/RELEASE_GATES.md`, `docs/APPROVED_DECISIONS_v2.7.md`, `docs/PROGRESS_v2.5.md`.
- Synthetic fixtures under `data/`, including `data/mixed_income_household.json` (ids `RP-SYNTH-*` only).

### 12.2 Public documentation (cited; not legal advice)

- Singpass developer docs, index: https://docs.developer.singpass.gov.sg/docs
- Singpass Login: https://docs.developer.singpass.gov.sg/docs/products/singpass-login
- Singpass Myinfo: https://docs.developer.singpass.gov.sg/docs/products/singpass-myinfo
- Singpass Myinfo FAQ (scopes, fresh retrieval, user-visible data, manual fallback, charges from April 2022, FAPI 2.0 deadline 31 December 2026, v3/v4 migration by end of September 2026): https://docs.developer.singpass.gov.sg/docs/products/singpass-myinfo/faq
- Singpass production-app note (Service Agreement; approval may take up to two weeks; Login scopes): https://docs.developer.singpass.gov.sg/docs/singpass-developer-portal-sdp/app-management/create-production-app
- PDPC, PDPA overview: https://www.pdpc.gov.sg/overview-of-pdpa/the-legislation/personal-data-protection-act
- PDPC, Data Protection Obligations: https://www.pdpc.gov.sg/overview-of-pdpa/the-legislation/personal-data-protection-act/data-protection-obligations
- PDPC, *Data Protection Obligations under the PDPA* (summary PDF, "Information correct as of May 2021"): https://www.pdpc.gov.sg/-/media/Files/PDPC/PDF-Files/Resource-for-Organisation/Data-Protection-Obligations-under-the-PDPA.pdf
- PDPC, *Advisory Guidelines on the Personal Data Protection Act for NRIC and other National Identification Numbers*, issued 31 August 2018, with the document's 14 December 2024 validity notice: landing page https://www.pdpc.gov.sg/organisations/regulations-decisions/regulatory-guidance/advisory-guidelines-on-the-personal-data-protection-act-for-nric-and-other-national-identification-numbers and published PDF https://www.pdpc.gov.sg/assets/cc9c647a-465f-4fbb-8bc2-5efa0bbe7ed2

### 12.3 Sources added for the QA G5 revision (accessed 14 November 2026, 09:38–09:41 SGT)

Plain unauthenticated GETs, all HTTP 200. Verbatim excerpts, byte sizes and SHA-256 hashes are saved in `test-artifacts/issue-4/sources/G5_SOURCE_EXCERPTS.md`.

- Singpass, *4. Parsing the ID Token* (`sub` "globally unique identifier"; `user.identity` returns `identity_number` = NRIC/FIN): https://docs.developer.singpass.gov.sg/docs/technical-specifications/integration-guide/4.-parsing-the-id-token
- Singpass Login, Key Principles ("Option 2: UUID only"): https://docs.developer.singpass.gov.sg/docs/products/singpass-login/key-principles
- Singpass Login, FAQ (Q1 identifier choice and PDPC NRIC guidelines; Q2 UUID): https://docs.developer.singpass.gov.sg/docs/products/singpass-login/faq
- Singpass developer docs, full-text export, all three parts, searched for "pairwise" (0 hits): https://docs.developer.singpass.gov.sg/docs/llms-full.txt , `/llms-full.txt/1` and `/llms-full.txt/2`
- Myinfo data catalog, Personal (`uinfin` = NRIC/FIN): https://docs.developer.singpass.gov.sg/docs/data-catalog-myinfo/catalog/personal
- Singpass Myinfo FAQ, re-checked for "till end Sep 2026", "should allow users to manually fill up forms" and the 15-month CPF contribution history: https://docs.developer.singpass.gov.sg/docs/products/singpass-myinfo/faq
- PDPC, *Advisory Guidelines on Key Concepts in the PDPA* (issued 23 September 2013, revised 29 April 2026; Consent chapter p. 55 on withdrawal of optional purposes; ¶18.1, ¶18.2, ¶18.4(a)(ii), ¶18.9 on retention): https://www.pdpc.gov.sg/-/media/Files/PDPC/PDF-Files/Advisory-Guidelines/AG-on-Key-Concepts/Advisory-Guidelines-on-Key-Concepts-in-the-PDPA-17-May-2022.pdf
- QA G5 evidence (repository-internal, not web): `qa/issue-4-2d03c9c/VERDICT.md`, `FINDINGS.md` and `logs/qa_lead_spotcheck.log` on `qa/issue-4-2d03c9c-verify` @ `ea0767d7ac705cf5f8895f0669fdc85bf6bd2469`.

No Singpass, PDPC, or other account was created. No paid material behind a login (for example the Myinfo price table) was accessed.

---

## 13. Changelog

### Revision 2 — 14 November 2026 (SGT): QA G5 conditions on `2d03c9c`

QA G5 verdict: **PASS with conditions** (`qa/issue-4-2d03c9c-verify` @ `ea0767d`). Doc wording only; no code, test, UI, API, config or manifest change.

| QA item | What changed |
|---|---|
| **Condition 1** — "never stores NRIC" (§1 #5, §6, §7) | §2.1 #5 and §6 now state a **design rule that is not currently enforced**. New §6.1 cites QA's evidence: the vault accepted and round-tripped a synthetic `nric` field after consent, with no key allow-list, though values were encrypted at rest and nothing was echoed or logged. New §6.2 proposes a control (**Proposed, not implemented**): reuse issue #5's normalised detector, a key denylist (and later an allowlist) plus value scan at `put_profile` / `core.validate` / `save_memory` / `create_action`, and red-first tests with mutation checks. Also updated: §1.1 new "Identifier fields" row, §4, the §6 classification table, §7 T7, §8.3, and §11. |
| **Condition 2** — Singpass `sub` "pairwise" (§3C, §4, §5.2, §10 Q7) | "Pairwise" removed everywhere; no official source supports it, and a full-text search of the Singpass docs (§12.3) found 0 hits. `sub` is now quoted as "a globally unique identifier for the user" from the official ID-token page (accessed 14 Nov 2026). Added: requesting `user.identity` makes **Singpass Login itself** return the NRIC/FIN in `sub_attributes.identity_number`, so "without storing an NRIC" holds only if that scope is not requested; this is tied to the unenforced rule in §6.1. §4 and §10 Q7 now recommend not requesting `user.identity`. Added an INTERNAL ASSUMPTION that a globally unique `sub` may be linkable across services. |
| **Condition 3** — unsourced glosses | "Optional purposes withdrawable on their own" (§5.1 #2) is now cited to PDPC Key Concepts p. 55; how our purposes map to optional or necessary is marked **INTERNAL ASSUMPTION**. The "anonymise", "no fixed period" and "just in case" retention glosses (§5.1 #7, §8.2) are now cited to PDPC Key Concepts ¶18.1, ¶18.2, ¶18.4(a)(ii) and ¶18.9. |
| **Condition 4** — onboarding "Ask Swee" box | §1.4 now describes the free-text `#chat-question` box as a place where users may type personal data (not sent or stored today). It links to issue #5's guardrails as a **proposed fix, not yet verified** (`bdc4fb3` awaiting QA). §7 T7 updated. |
| Nit: manual fallback "must" vs "should" | §3C now says "should", matching the Myinfo FAQ. |
| Nit: v3/v4 deadline already passed | §3C now says the FAQ gave v3/v4 partners until end September 2026 and that this had passed before the draft date. |
| Nit: "strongest digital identity" is opinion | Withdrawn and replaced with a neutral description. |
| Nit: consent rows stay plain text after revocation | Now stated in the §1.1 Consent table and Withdrawal rows. |
| Nit: §5.3 and §1.2 understate the consent check | §1.2 and §5.3 now say the `core.validate` check is age-based (≥ 18 on `as_of`), so an adult with `role: "child"` is still checked; the §5.3 primary row notes the vault still needs the primary's consent. |
| Nit: REPORT line counts 85/499 vs actual 88/502 | Recorded here: the first commit's actual figures are **88 lines** for `test-artifacts/issue-4/REPORT.md` and **502 insertions** in total (QA FINDINGS §6). `REPORT.md` itself is not edited in this docs-only revision, by the brief's staging scope. |
| Nit: env.txt shows `HEAD=823ef72` | Recorded here: the first draft's test logs were produced on the uncommitted tree at base `823ef72`, before commit `2d03c9c`. QA's rerun at `2d03c9c` matched (821 passed, rules 498/498, release errors 0). `env.txt` is a historical log of that run and is not rewritten. |
| Extra accuracy fixes from QA FINDINGS | §1.3 now limits the `RP-SYNTH-` claim to the JSON evaluation endpoints (GET endpoints take no profile). §1.1 Action verification notes that the `verified` refusal comes from the transition table. |

Still not verified, and unchanged by this revision: the issue #4 GitHub comments (QA did not access them), the Myinfo price table (needs a Singpass login), and per-scope catalog detail beyond the Personal page.

### Revision 1 — 10 November 2026 (SGT): first draft (`2d03c9c`)

---

*End of internal design draft. Not for external circulation as a security or legal position.*
