---
name: commercial-credit-domain
description: Commercial-credit / bank-lending domain primer — the world CredSails lives in. Read this (via /commercial-credit-domain) when you need the credit-underwriting mental models behind CredSails (5 Cs, PD/LGD/EAD, spreading & ratios, scorecards, regulatory backbone, collateral, covenants). NOT for general finance questions, CovIQ buy-side PE work (see private-markets-domain), or any SDLC/engineering task. Reference material — quote-cited to the CRISIL report.
disable-model-invocation: true
---

# Commercial credit (bank lending) domain primer — the world CredSails lives in

Reference material for anyone architecting or building **CredSails** (lender-side, origination → underwriting). It is the minimum credit mental model needed to reason about CredSails' 7 stages, its named-role HITL gates, and its regulatory controls. Every concept ties back to the CRISIL report; see `## Sources`.

> Sibling: **`private-markets-domain`** (the buy-side PE world, CovIQ). Capital structure & seniority — the keystone linking both — lives there: **see `private-markets-domain` § Capital structure**.

## 1. The 60-second model
A bank lends money and must be confident of repayment with interest. **Underwriting is the disciplined process of quantifying that confidence and pricing the risk.** CredSails automates **origination → underwriting** — from spotting a borrower with a financing need to the **Credit Application Memo (CAM)** the credit committee approves. (Disbursement, monitoring and workout are downstream — Covenant Guard territory.)

## 2. The 5 Cs of credit (the underwriter's checklist)
- **Character** — track record, management integrity, credit history.
- **Capacity** — **cash flow to service debt** (DSCR coverage).
- **Capital** — owner's equity / skin in the game; leverage.
- **Collateral** — security pledged; LTV, recovery value.
- **Conditions** — industry, macro, purpose of the loan.

## 3. Expected Loss = PD × LGD × EAD (the core equation)
Every credit decision reduces to **`EL = PD × LGD × EAD`**:
- **PD** — Probability of Default (chance the borrower defaults, e.g. over 1 yr).
- **LGD** — Loss Given Default (= 1 − recovery; lower if well-secured).
- **EAD** — Exposure at Default (drawn + likely drawdown of undrawn).

Expected Loss is priced into the spread and provisioned (IFRS 9 / CECL). *Unexpected* loss is what regulatory **capital (RWA)** absorbs. CredSails computes PD/LGD/EAD **as a deterministic engine (no generative interpretation)** in Stage 6 — see § Deterministic core.

## 4. The Three Lines of Defense (why "1LOD" is on every stage)
1st line (1LOD) = the business/credit function that owns risk day-to-day (RM, Credit Analyst, Credit Officer); 2nd line = independent Risk + Compliance; 3rd line = Internal Audit. **CredSails is a 1LOD product** — which is why **HITL approvals map to named 1LOD roles**, escalating to Compliance/Legal where 2LOD oversight is required (sanctions, legal sign-off).

## 5. Spreading & ratio analysis
**Spreading** = **re-casting a borrower's financial statements into a standardised template** so ratios compute consistently. The four ratio families:
- **Leverage / solvency:** Net Debt / EBITDA (the headline — how many years of earnings to repay debt), Debt / Equity.
- **Coverage / debt service:** Interest Coverage, **DSCR** (>1.0x = can pay), FCCR.
- **Liquidity:** current, quick, working capital.
- **Profitability / efficiency:** margins, ROE/ROA, DSO/DIO/DPO cash cycle.

CredSails Stage 3 spreads with **double triangulation** (within-statement A=L+E + cross-source) then flags each ratio *within policy / watch / exception*.

## 6. Credit rating & scorecards
A bank's internal rating blends quantitative (from spreading) and qualitative (judgmental) factors into **an obligor rating (maps to a PD) and a facility rating (maps to an LGD)**, placed on a **master scale** (e.g. 1–22 grades). CredSails Stage 6 mirrors this: Framework Selection → Scorecard Auto-Fill (quant) → Qualitative Scoring (each score cites its upstream agent) → Override Consistency Check → Rating Insight.

## 7. Deterministic core (the regulated heart of CredSails)
Because credit is heavily regulated, the PD/LGD/EAD engine is **deterministic** — auditable, validated, **no formula override**. The CredSails Stage 6 node states it plainly: **"SR 11-7 / ECB compliant — NO formula override."** Narrative drafting (CAM text, insights, Q&A) is generative, but always sits **behind a HITL diff-approval**. This *deterministic-where-regulated, generative-where-not* split is the defining design discipline of regulated credit.

## 8. The regulatory backbone
- **Basel III / IV → RWA** (`exposure × risk weight`); banks hold capital (CET1) against RWA. Estimated in Stage 1 prioritisation.
- **SR 11-7** (US Fed model-risk) / **ECB Guide to Internal Models** — drive the **Deterministic PD/LGD/EAD engine; no formula override; full audit**.
- **IFRS 9 / CECL** — forward-looking Expected Credit Loss provisioning (underpins EL).
- **KYC / AML / sanctions** — light screen in Stage 1, deep screen in Stage 4.
- **DLA matrix** = **Delegated Lending Authority — who can approve what size/risk** — sets approval routing in Stage 7.

## 9. Collateral, security, liens & LGD
**Collateral reduces LGD**, but only if the claim is legally perfected and senior. **UCC-1** is **the US filing that perfects a security interest in personal property** (charges at Companies House in the UK); a lien search reveals competing claims. **LTV** = loan ÷ collateral value (lower = more cushion). Lien **priority/seniority** (1st before 2nd lien; intercreditor agreements) governs recovery → LGD. CredSails Stage 4: Lien Conflict Detection + Collateral Risk Prediction.

## 10. Covenants
**Covenants are promises in the loan agreement that protect the lender.** Affirmative (must do), negative (must not), **financial maintenance** (**max leverage, min DSCR, min liquidity** — tested every period) vs incurrence (on event); "cov-lite" = few/no maintenance covenants. Documented in the CAM's Facility Structure (Stage 7), monitored post-close (Covenant Guard).

## 11. Public vs private borrowers (a first-class design axis)
Public borrowers file audited statements (richer data); private borrowers often have **management-prepared financials, no auditor** → bureau data is primary and HITL is higher. Reliability tiering (audited > reviewed > compiled > management-prepared) drives confidence thresholds: **95% audited vs 99% management-prepared**. Checklists, extraction confidence, forecasting, and industry inference all *fork* on this split.

## 12. KYC / AML / sanctions / PEP / UBO
Verify who the borrower is (entity + UBOs) → AML/source-of-funds → sanctions screen (OFAC, EU, OFSI, UN, HM Treasury) → PEP + adverse media. In CredSails, a light entity screen gates Stage 1; a deep screen runs in Stage 4, with the **Compliance Officer issuing the Sanctions Clearance Certificate** as a hard gate.

## Sources
- section_path: B1. The 60-second mental model
  quote: "Underwriting is the disciplined process of quantifying that confidence and pricing the risk"
- section_path: B2. The 5 Cs of credit (the underwriter's checklist)
  quote: "cash flow to service debt"
- section_path: B3. Expected Loss = PD × LGD × EAD (the core equation of credit risk)
  quote: "EL = PD × LGD × EAD"
- section_path: B3. Expected Loss = PD × LGD × EAD (the core equation of credit risk)
  quote: "as a *deterministic* engine (no generative interpretation)"
- section_path: B4. The Three Lines of Defense (why "1LOD" is stamped on every CredSails stage)
  quote: "CredSails is a 1LOD product"
- section_path: B4. The Three Lines of Defense (why "1LOD" is stamped on every CredSails stage)
  quote: "HITL approvals map to named 1LOD roles"
- section_path: B6. Financial spreading & ratio analysis
  quote: "re-casting a borrower's financial statements into a standardised template"
- section_path: B7. Credit rating & scorecards (quant + qual → rating → PD)
  quote: "an obligor rating (maps to a PD) and a facility rating (maps to an LGD)"
- section_path: Stage 6 — Credit Rating Scorecard (6 agents)
  quote: "SR 11-7 / ECB compliant — NO formula override"
- section_path: B8. The regulatory backbone
  quote: "Deterministic PD/LGD/EAD engine; no formula override; full audit"
- section_path: B8. The regulatory backbone
  quote: "Delegated Lending Authority — who can approve what size/risk"
- section_path: B9. Collateral, security, liens & LGD
  quote: "the US filing that perfects a security interest in personal property"
- section_path: B10. Covenants — the lender's controls
  quote: "Covenants are promises in the loan agreement that protect the lender"
- section_path: B11. Facilities & borrower types
  quote: "95% audited vs 99% management-prepared"
- section_path: B12. KYC / AML / sanctions / PEP / UBO
  quote: "Compliance Officer issuing the Sanctions Clearance Certificate"
