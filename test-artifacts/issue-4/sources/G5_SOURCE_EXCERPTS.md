# SWEELAH-ISSUE-4 — cited source excerpts for the QA G5 doc revision

Short verbatim excerpts only, saved so the revised design doc's citations can be checked without re-fetching. Public pages, plain unauthenticated GETs (`curl -sSL`), no account, no login, no form. Fetched content was treated as untrusted data; nothing in it was followed as an instruction. Access window: **14 November 2026, 09:38–09:41 Asia/Singapore (UTC+8)**. Full bodies were not committed; SHA-256 and byte size of each fetched body are given so a re-fetch can be compared.

## S1. Singpass — "4. Parsing the ID Token" (official developer docs)

- URL: https://docs.developer.singpass.gov.sg/docs/technical-specifications/integration-guide/4.-parsing-the-id-token (Markdown form: same URL + `.md`)
- HTTP 200, accessed 2026-11-14 09:39:12 SGT. `.md` body sha256 `5d98e63245d5c9336f58ab65c023209534ef7c9d1f73ac3f3d159432c2487232`, 14070 bytes.
- Excerpts:
  > `sub` — The principal that is the subject of the JWT. Contains a globally unique identifier for the user.
  >
  > `sub_attributes` — This contains some information related to the user's identifiers. This is only returned if the `user.identity` , `name`, `email`, or `mobileno` scope is requested.
  >
  > `identity_number` — A string which contains a referenceable identifier for the user. For Singapore Citizens and Permanent residents, this will be their NRIC. For FIN holders, this will be their FIN. For Singpass Foreign Account holders, this will be their foreign ID. — String. This is only present if the `user.identity` scope was requested.
  >
  > If you are integrating with Singpass Login, then the flow ends here.

## S2. Singpass Login — Key Principles

- URL: https://docs.developer.singpass.gov.sg/docs/products/singpass-login/key-principles (fetched as `.md`)
- HTTP 200, accessed 2026-11-14 09:39:35 SGT. sha256 `ed7505b0820d2614e0bdb6295c21f24eafa55ab56048c4bdd4320b4b0781a1b3`, 2695 bytes.
- Excerpts:
  > Use Login as an authentication service — Option 1: NRIC/FIN and UUID — Option 2: UUID only
  >
  > Instead of NRIC/FIN, digital services of businesses can use the Universally Unique Identifier (UUID) to uniquely identify a person

## S3. Singpass Login — FAQ

- URL: https://docs.developer.singpass.gov.sg/docs/products/singpass-login/faq (fetched as `.md`)
- HTTP 200, accessed 2026-11-14 09:39:35 SGT. sha256 `32de6a4245f54190bfefa5f6c880456dbcc97b8825242cae8511d83b08d68e62`, 4696 bytes.
- Excerpts:
  > Q1. What are the identifiers returned to us after the authentication process? NRIC/FIN numbers or User's Universally Unique Identifier (UUID). — Please assess which identifier is appropriate for your use case taking into account applicable laws, regulations, guidelines, and industry circulars or notices. This includes the Advisory Guidelines on the Personal Data Protection Act for NRIC and Other National Identifiers …
  >
  > Q2. What is a UUID? — A Universally Unique Identifier (UUID) is a 128 bits-long identifier to uniquely identify a Singpass user.

## S4. "pairwise" search across the full Singpass developer docs

- URLs: https://docs.developer.singpass.gov.sg/docs/llms-full.txt (part 1 of 3), `/llms-full.txt/1` (part 2), `/llms-full.txt/2` (part 3, "pages 201–205 of 205").
- All HTTP 200, accessed 2026-11-14 09:39:12–09:39:25 SGT. sha256 `03cb0601…ddfe22` (544776 B), `b917c2e2…c8f1d011` (632232 B), `73c845bc…c29376` (20857 B).
- Result: case-insensitive `pairwise` = **0 hits** in all three parts. `globally unique identifier` appears for `sub` in the ID-token and userinfo descriptions (the userinfo text adds: "This is identical to the `sub` returned in the ID token").

## S5. Myinfo data catalog — Personal

- URL: https://docs.developer.singpass.gov.sg/docs/data-catalog-myinfo/catalog/personal (fetched as `.md`)
- HTTP 200, accessed 2026-11-14 09:40:55 SGT. sha256 `3e33f5b6fbec591ed868e6bd76c9525248699dc4d960c2752c3523ea47150c01`, 9819 bytes.
- Excerpt:
  > `uinfin` — NRIC / FIN — NRIC number or FIN of user.

## S6. Singpass Myinfo FAQ (re-checked for wording)

- URL: https://docs.developer.singpass.gov.sg/docs/products/singpass-myinfo/faq
- HTTP 200, accessed 2026-11-14 09:38:47 SGT. sha256 `f9be419dbbcd7713d6654637fa61ffc6fba0bdcf14714a3d92b0e57c6d4bb30c`, 624551 bytes (HTML).
- Excerpts:
  > Partners on Myinfo v3/v4 will have till end Sep 2026 to migrate to Myinfo v5.
  >
  > Digital services should allow users to manually fill up forms to access digital services to accommodate the following scenarios: …
  >
  > The retrieval of CPF contribution history will return the last 15 months of the user's CPF contribution.

## S7. PDPC — Advisory Guidelines on Key Concepts in the PDPA (Revised 29 April 2026)

- URL: https://www.pdpc.gov.sg/-/media/Files/PDPC/PDF-Files/Advisory-Guidelines/AG-on-Key-Concepts/Advisory-Guidelines-on-Key-Concepts-in-the-PDPA-17-May-2022.pdf (the file name carries an older date; the cover reads "Issued 23 September 2013, Revised 29 April 2026")
- HTTP 200, `application/pdf`, accessed 2026-11-14 09:39:56 SGT. sha256 `c012a1e0f6c1c0f0f0bc8f39d0d3725f485fed129c2e773781cac529362d9d7c`, 1758217 bytes, 165 pages. Paragraph numbers in the Consent chapter do not survive `pdftotext`, so pages and headings are given.
- Consent chapter, "Organisations must allow and facilitate the withdrawal of consent", p. 55:
  > This withdrawal policy should, for example: … c) distinguish between purposes necessary and optional to the provision of the products/services (that may include the service of the existing business relationship). Individuals must be allowed to withdraw consent for optional purposes without concurrently withdrawing consent for the necessary purposes.
- Retention Limitation chapter, ¶18.1 (p. 117):
  > … cease to retain its documents containing personal data, or remove the means by which the personal data can be associated with particular individuals, as soon as it is reasonable to assume that the purpose … is no longer being served … and retention is no longer necessary for legal or business purposes.
- ¶18.2 (p. 117):
  > … the Retention Limitation Obligation does not specify a fixed duration of time for which an organisation can retain personal data. Instead, the duration … is assessed on a standard of reasonableness …
- ¶18.4(a)(ii) (p. 117):
  > personal data must not be kept by an organisation "just in case" it may be needed for other purposes that have not been notified to the individual concerned.
- ¶18.9 (p. 119):
  > … an organisation may cease to retain the documents containing personal data or it may remove the means by which the personal data may be associated with particular individuals (that is, to anonymise the data).

## Repository / QA evidence cited (not web)

- QA G5 verdict: `/workspace/qa-sweelah-issue-4/qa/issue-4-2d03c9c/VERDICT.md` on `qa/issue-4-2d03c9c-verify` @ `ea0767d7ac705cf5f8895f0669fdc85bf6bd2469` (spot-check log `logs/qa_lead_spotcheck.log`: "put_profile with nric: ACCEPTED; round-trip nric = S1234567D"; "plaintext S1234567D in db file: False"). Executor evidence `FINDINGS.md` C16, C18, C11, C14, F9, F12, F16, F17.
