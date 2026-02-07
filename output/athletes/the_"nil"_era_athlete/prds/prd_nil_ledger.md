# Product Requirements Document (PRD): NIL Ledger

**Status:** Draft / For Review
**Version:** 1.0
**Product Manager:** Senior Product Manager
**Date:** October 26, 2023

---

## 1. Overview
### 1.1 Product Purpose
**NIL Ledger** is a specialized financial management and compliance platform designed for the "Athlete-as-a-Service" era. As the NCAA landscape shifts from student-athletes to independent business entities, athletes are facing professional-grade financial complexity without professional-grade tools.

NIL Ledger serves as the "QuickBooks for Athletes," automating the backend of their business life. It solves the critical problem of **"The Tax Trap"** (unpaid taxes on non-cash/trade-in-kind deals) and the **"Compliance Burden"** (reporting mandates to universities) through a high-utility, mobile-first interface.

### 1.2 Strategic Objectives
*   **Establish the Category:** Become the default financial operating system for the emerging entrepreneurial athlete class.
*   **De-risk the NIL Ecosystem:** Protect athletes from IRS audits and NCAA eligibility violations.
*   **Capture Value:** Monetize via a high-margin SaaS model ($200/mo) targeting athletes with consistent revenue streams.

---

## 2. Success Metrics (KPIs)
| Metric | Target | Rationale |
| :--- | :--- | :--- |
| **Active Financial Tracking (AFT)** | >70% of users | Percentage of users who link at least one bank account or log one trade-in-kind deal per month. |
| **Tax Compliance Rate** | 100% | Percentage of users who have a calculated tax liability score and set-aside account. |
| **Time to Report (TTR)** | < 60 seconds | The time it takes for an athlete to export and submit a compliance report to their University/NCAA. |
| **Net Revenue Retention (NRR)** | >110% | Growth through upsells (e.g., premium tax filing services) and low churn. |

---

## 3. Personas
### 3.1 Primary Persona: The High-Volume Influencer / Performance Athlete
*   **Profile:** NCAA D1 Football/Basketball or high-reach Olympic sport athlete (Gymnastics, T&F).
*   **Key Pain Point:** Receives a mix of cash (Venmo/Direct Deposit) and "Trade-in-Kind" (free gear, supplements, car leases). They have no idea how much they actually "owe" the government and find university disclosure forms tedious.
*   **Goal:** Stay eligible to play and avoid a massive tax bill at the end of the year.

### 3.2 Secondary Persona: The Emerging High-School Recruit
*   **Profile:** Top-tier high school talent navigating early-stage local deals.
*   **Key Pain Point:** Parents and athletes are overwhelmed by the legalities and want to ensure they don't jeopardize future college eligibility.

---

## 4. User Scenarios
### Scenario A: The "Free" Gear Tax Trap
*Jordan, a D1 Wide Receiver, receives a $5,000 custom suit and a $2,000 watch in exchange for three Instagram posts. No cash changed hands. Jordan logs the deal in NIL Ledger. The app immediately notifies Jordan that he has a $1,800 tax liability based on his bracket. It prompts him to move $1,800 from his cash savings into his "Tax Set-Aside Vault" so he isn't blindsided in April.*

### Scenario B: Sunday Night Compliance
*After a weekend of signing autographs at a local fan fest, Sarah needs to report her earnings to her university’s compliance office. Instead of filling out a manual PDF, she opens NIL Ledger, selects the "Fan Fest" transactions, and hits "One-Click Submit." The app generates a compliant report and emails it directly to the Athletic Director's portal.*

---

## 5. User Stories / Features / Requirements

| Priority | Feature | User Story | Justification |
| :--- | :--- | :--- | :--- |
| **P0** | **Automated Tax Set-Aside Calculator** | As an athlete, I want to see my real-time tax liability for both cash and merchandise deals so I don't spend money I owe the IRS. | Tax ignorance is the #1 risk for NIL athletes. This provides immediate "peace of mind" value. |
| **P0** | **One-Click Compliance Reporting** | As an athlete, I want to auto-generate reports for my university so I can stay eligible without manual paperwork. | Compliance is a "must-do" chore; automating it creates high product "stickiness." |
| **P1** | **Business Profile Dashboard (Net vs. Gross)** | As a student-entrepreneur, I want to see my actual take-home pay after taxes and expenses so I can manage my budget. | Shifts mindset from "getting paid" to "running a business." |
| **P1** | **Trade-in-Kind Valuation Tool** | As an athlete, I want to easily log the Fair Market Value (FMV) of products I receive so my books are accurate. | Most NIL deals involve products, not just cash. These are often forgotten until audit time. |
| **P2** | **"The Vault" (Tax Savings Account)** | As an athlete, I want a sub-account to stash tax money so I am not tempted to spend it. | Bridges the gap between "information" (knowing you owe tax) and "action" (saving for it). |

---

## 6. Features Out (Non-Goals)
*   **NIL Marketplace:** We will NOT connect athletes with brands. We are the *back-office*, not the *agency*. We want to be a neutral partner to all marketplaces (Opendorse, etc.).
*   **Contract Legal Review:** We will not provide automated legal advice or contract redlining in V1 to avoid high-liability legal tech complexities.
*   **Social Media Scheduling:** We are a FinTech tool, not a marketing suite.

---

## 7. Open Issues / Risks
*   **Data Integration:** How many university compliance portals allow for API-based submission vs. just generating a PDF/Email? (Research required on *ARMS* and *FrontRush* integrations).
*   **Tax Jurisdiction Complexity:** Managing state-level "Jock Taxes" for athletes playing games in multiple states. V1 will focus on Federal and Home-State taxes.
*   **Bank Connectivity:** Ensuring 99% uptime for Plaid/Finicity integrations so athletes see real-time transaction data from their "influencer" bank accounts.

---

**Approval:**
*   **Product:** ____________________
*   **Engineering:** ____________________
*   **Compliance/Legal:** ____________________