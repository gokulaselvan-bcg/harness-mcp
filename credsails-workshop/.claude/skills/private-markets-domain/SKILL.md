---
name: private-markets-domain
description: Private-equity / private-markets domain primer — the world CovIQ lives in. Read this (via /private-markets-domain) when you need the PE mental models behind CovIQ (fund economics, deal archetypes, CIM/EBITDA, LBO value creation, the IC). NOT for general finance questions, CredSails credit work (see commercial-credit-domain), or any SDLC/engineering task. Reference material — quote-cited to the CRISIL report.
disable-model-invocation: true
---

# Private markets (PE) domain primer — the world CovIQ lives in

Reference material for anyone architecting or building **CovIQ** (buy-side, pre-deal PE intelligence). It is the minimum PE mental model needed to reason about CovIQ's agents and HITL gates. Every concept ties back to the CRISIL report; see `## Sources` for the exact passages.

> Sibling: **`commercial-credit-domain`** (the lender world, CredSails). The two meet in **§ Capital structure** below.

## 1. The 60-second model
A PE fund raises money from large investors, **buys companies, improves them over a few years, and sells them for more**, returning the profit. **CovIQ automates the front half** — source → screen → analyse → diligence → Investment Committee (IC) decision. Value creation and exit are post-deal (out of CovIQ's scope).

## 2. Fund structure & economics
- **LPs** (pension funds, endowments, SWFs, insurers) provide capital; the **GP** (the PE firm / deal team) manages it and decides. The fund is closed-end (~10-yr life), tied to a **vintage** year.
- **Management fee** ~2% of committed capital funds the GP; **carried interest ("carry")** ~20% is the GP's profit share, earned only **above a hurdle** (~8%). **GP commitment** (~1–5%) = skin in the game. **Dry powder** = committed-but-uninvested capital.
- **Returns vocabulary:** **IRR** (annualised, time-sensitive — the headline), **MOIC** (multiple on invested capital, ignores time), and fund-level **TVPI / DPI / RVPI** (total / distributed / residual value to paid-in).
- **The J-curve:** early in a fund's life, fees + early write-downs make net returns *negative*; returns turn sharply positive as companies are improved and exited.

*Why it matters for CovIQ:* every screen, primer and IC memo is implicitly underwriting a fund-level return (IRR/MOIC) under these economics.

## 3. Deal archetypes — these are CovIQ's screeners
Different strategies hunt different signals; **CovIQ ships a dedicated screener per archetype**:

| Archetype | Looking for | CovIQ screener |
|---|---|---|
| Buyout / LBO | mature, cash-generative targets to lever and improve | Buyout Opportunity Screener |
| Growth equity | fast-growing, often founder-led, little/no debt | Growth Equity Signal Screener |
| Distressed / special situations | troubled companies, buy debt/equity cheap ("loan-to-own") | Distressed Opportunity Screener |
| Carve-out | a division a parent wants to divest | Carve-out Opportunity Screener |
| Secondary buyout | buying from another PE sponsor | Sponsor Portfolio Scanner |
| Co-investment | investing alongside another GP | Sponsor Universe Builder (co-invest) |
| Add-on / bolt-on | small targets to merge into a platform | Adjacent Target Screener |

## 4. The deal documents (the paper trail CovIQ ingests)
**Teaser** (1–2 pp, anonymised) → **NDA** → **CIM** (Confidential Information Memorandum — the seller/banker's full marketing book, 50–100+ pp) → **IOI / LOI** (indicative price + terms) → **IC memo** (internal recommendation) → **SPA** (binding, at signing). CovIQ's Teaser KPI Extractor, CIM Extractor & Validator, and IC Pack Assembler handle these.

## 5. EBITDA, add-backs, normalization & QoE — the number everything hinges on
**EBITDA** (Earnings Before Interest, Taxes, Depreciation & Amortization) is the base for valuation (price = a *multiple* of EBITDA). Sellers present **Adjusted EBITDA** by adding back "one-time" costs; buyers decide which add-backs are defensible. A **Quality of Earnings (QoE)** study verifies this, producing the **normalized EBITDA** the buyer underwrites.

*CovIQ implements exactly this:* the CIM Extractor builds the seller-stated → firm-normalized bridge and **flags add-backs over 25% of EBITDA as aggressive**; the Narrative Tracker re-rates claims against QoE findings in diligence.

## 6. Valuation toolkit
- **Market:** comparable companies (EV/EBITDA, EV/Revenue) and precedent transactions.
- **Intrinsic:** DCF (discounted free cash flow, WACC, terminal value).
- **Returns-based:** the LBO model — solve for IRR/MOIC given entry/exit multiple, leverage, hold, growth.

The key bridge is **`EV = Equity Value + Net Debt`** (multiples are quoted on EV, e.g. "9.0x EV/EBITDA").

## 7. The LBO value-creation engine — how PE makes money
In a leveraged buyout **the fund buys a company using a mix of equity (its own) + debt (borrowed)**. Over the hold, three engines grow the equity: **(1) EBITDA growth** (organic + add-ons), **(2) multiple expansion** (exit > entry multiple), **(3) debt paydown** (free cash flow reduces debt → equity grows). Leverage amplifies returns — which is why CovIQ's analysis stage builds a full 3-statement LBO with debt schedule and IRR/MOIC sensitivities.

## 8. The Investment Committee (IC)
The IC (senior partners) is the decision body. The IC memo must answer: **what are we buying, why now, at what price, with what leverage**, what's the return (base + downside), key risks/mitigants, and the value-creation plan. CovIQ's IC Pack Assembler drafts these sections and even simulates anticipated IC Q&A.

## Capital structure — where CovIQ and CredSails meet (canonical)
> This is the keystone shared with **`commercial-credit-domain`**; it lives here and is cross-referenced there.

A leveraged buyout is funded by **both** worlds: **equity from the PE sponsor (CovIQ's user) plus debt from lenders** (CredSails' user) — counterparties on the *same deal*, often the same CIM. The **capital stack** (paid first → last in a default):

1. **Senior secured debt** (revolver, Term Loan A/B) — *lenders / CredSails*
2. Second-lien debt
3. Mezzanine / subordinated debt
4. Preferred equity
5. **Common equity** — *PE sponsor / CovIQ* (first losses, all the upside)

**The defining tension:** the **sponsor (CovIQ side) wants maximum leverage** (less equity in → higher IRR); the lender (CredSails side) wants a thick equity cushion below it and tight covenants. A target in CovIQ and a borrower in CredSails can be the *same entity* — the basis of the products' "horizontal agent link (CLS)".

## Sources
- section_path: A1. The 60-second mental model
  quote: "buys companies, improves them over a few years, and sells them for more"
- section_path: A2. Fund structure & economics — GP, LP, carry, the J-curve
  quote: "Limited Partners (LPs) provide the capital; the General Partner (GP)"
- section_path: A2. Fund structure & economics — GP, LP, carry, the J-curve
  quote: "GP's share of profits, ~20%, earned only above a hurdle/preferred return"
- section_path: A3. Deal archetypes — these are CovIQ's screeners
  quote: "CovIQ ships a dedicated screener per archetype"
- section_path: A5. The deal documents (the paper trail CovIQ ingests)
  quote: "Confidential Information Memorandum"
- section_path: A6. EBITDA, add-backs, normalization & QoE — the number everything hinges on
  quote: "flags add-backs over 25% of EBITDA as aggressive"
- section_path: A7. Valuation toolkit
  quote: "EV = Equity Value + Net Debt"
- section_path: A8. The LBO value-creation engine — how PE actually makes money
  quote: "the fund buys a company using a mix of equity (its own) + debt (borrowed)"
- section_path: A10. The Investment Committee (IC)
  quote: "What are we buying, why now, at what price, with what leverage"
- section_path: Part C — Where the two worlds meet: the capital structure
  quote: "equity from the PE sponsor (CovIQ's user) plus debt from lenders"
- section_path: Part C — Where the two worlds meet: the capital structure
  quote: "sponsor (CovIQ side) wants maximum leverage"
