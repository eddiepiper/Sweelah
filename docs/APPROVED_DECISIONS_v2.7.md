# RetirePilot Approved Product Decisions v2.7

**Approval date:** 2026-11-04  
**Authority:** Product owner, confirmed in conversation  
**Status:** Approved product choices, not independent certification  
**Release:** Phase 9 NO-GO

| ID | Choice | Binding decision | Engineering/control consequence |
|---|---|---|---|
| D-001 | **1A** | Personalised retirement projections, scenario comparisons and educational explanations only | No regulated product recommendations or transactions. Legal review remains mandatory |
| D-002 | **2A** | CPF LIFE amount comes from the member's official estimate; CPF Board published examples are illustrations | User-transcribed source declaration required. No inference from RA balance or public tables |
| D-003 | **3A** | Retain all 96 personas, show provisional descriptions without numerical confidence claims | Consumer assessment omits 0-100 matches and raw weights; internal matching audits retain them |
| D-004 | **4A** | Verify each adult's identity and separate consent before sharing financial records | No authenticated provider exists, so sharing remains blocked; synthetic consent is not identity verification |
| D-005 | **5A** | Validate five high-value scenarios before implementing the remaining catalogue | S020 downsizing; S030 payout timing; S004 part-time; S016 parent care; S012 divorce/family transition |
| D-006 | **6A** | Obtain reviewer qualifications, written proposals and quotations before appointments | Non-binding enquiries only; no fees or engagement approved |
| D-007 | **7A** | Assume favourable consumer testing only for development planning | 48 real consented sessions remain required before an external pilot |

## Decision-dependent gates

- **D-001:** Block product recommendations and execution; qualified Singapore legal scope review of actual behaviour pending.
- **D-002:** Personal CPF LIFE payout requires a member-transcribed official estimate. The claim of origin remains user-reported, not CPF-system verified. Public illustrations cannot be personal inputs.
- **D-003:** UI and consumer API must hide match percentages, evidence coverage, thresholds and other numerical confidence claims. Internal scorer remains uncalibrated.
- **D-004:** No household financial-record sharing before separately authenticated identity and consent for each adult. Existing local consent check is a synthetic simulation only.
- **D-005:** All five priority events have contracts; four bounded financial previews exist, while S012 divorce remains blocked. None of these is a complete validated life-event engine.
- **D-006:** Review qualifications, independence, scope and quote; no appointment or spending without specific approval.
- **D-007:** 0/48 real interviews conducted. Counterfactual consumer PASS does not authorise a pilot.

## Engineering evidence, local only

- **609/609** local Python automated tests passed after v2.7 changes.
- **498/498** classifier rule contracts and **13/13** local API checks passed.
- Terminal partial-month forecast denominator fixed and calendar-day reference tests added.
- Consumer-facing persona score display and public score payload removed.
- CPF LIFE source guard and household sharing fail-closed method added.
- Five priority scenario preview contracts implemented or blocked as appropriate.

**Source-control caveat:** Full v2.7 application code and this test suite have not yet been pushed to the repository, and no GitHub Actions CI is claimed. Issues #1 and #9 remain open pending remote commit and verified CI.

## Evidence standards

Internal synthetic tests are not independent financial validation. A source-based legal assessment is not a qualified legal opinion. A local encrypted vault does not establish production identity or consent. A simulated consumer session is not an observed interview. Phase 9 remains NO-GO.
