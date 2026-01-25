# Product Requirements Document: AthleteCorp OS

**Status:** Draft / Initial Version  
**Author:** Senior Product Manager  
**Date:** October 26, 2023  
**Target Release:** Q1 2024

---

## 1. Overview
### 1.1 Product Vision
**AthleteCorp OS** is the definitive "Business-in-a-Box" for the modern athlete. We are transitioning the athlete from a "laborer" dependent on a scholarship or team salary into an independent "Corporate Entity." By providing the legal, financial, and mental infrastructure required to manage Name, Image, and Likeness (NIL) revenue, we enable athletes to focus on their performance while their business scales in the background.

### 1.2 The "Why"
The structural shift in the NCAA and professional sports has turned student-athletes into entrepreneurs overnight. However, they lack the back-office infrastructure to manage this. Most are currently operating as sole proprietorships, exposing them to massive tax liabilities, legal risks, and mental burnout. AthleteCorp OS bridges this gap with a high-utility mobile interface that professionalizes their brand.

---

## 2. Success Metrics (KPIs)
| Metric | Definition | Goal (Year 1) |
| :--- | :--- | :--- |
| **Total Entities Formed** | Number of LLCs/EINs registered via the platform. | 5,000 |
| **AUM (Assets Under Management)** | Total capital flowing through the "Wealth Vault." | $50M |
| **Monthly Churn** | Percentage of athletes cancelling the $200/mo subscription. | < 5% |
| **Mental Health Concierge Utilization** | % of users engaging with a specialist at least once/quarter. | 25% |
| **NIL Compliance Accuracy** | % of deals reported to universities with zero regulatory errors. | 100% |

---

## 3. Personas

### 3.1 Primary Persona: The "High-Cap" Collegiate Entrepreneur
*   **Profile:** NCAA D1 Football or Basketball player.
*   **Context:** Earning $50k–$500k/year in NIL deals.
*   **Pain Points:** Overwhelmed by tax 1099s, family members asking for money, and no time to research "what an LLC is."
*   **Goal:** Protect their earnings and build a long-term legacy beyond the jersey.

### 3.2 Secondary Persona: The "Micro-Influencer" Athlete
*   **Profile:** D1/D2 Olympic Sports (Gymnastics, Volleyball, Track).
*   **Context:** Large social following; high volume of smaller deals ($500–$2,000).
*   **Pain Points:** Tracking 20+ different contracts and managing content deadlines.

---

## 4. User Scenarios

### Scenario A: The Professionalization Kickoff
*Jordan, a sophomore QB, just signed a $100k deal with a local dealership.* Instead of depositing the check into a personal checking account (and losing 30% to future taxes), he opens AthleteCorp OS. In 5 minutes, he applies for "Jordan King Enterprises LLC." The app handles the state filing and EIN. Within 48 hours, he has a business banking account integrated into the app where his NIL check is deposited.

### Scenario B: The Identity Crisis
*Sarah, a star gymnast, is facing immense pressure after a poor performance.* Her social media mentions are toxic. She opens the app and hits the "Concierge" button. Within 15 minutes, she is on a private, encrypted video call with a sports psychologist who specializes in NIL-related burnout and identity management.

---

## 5. User Stories / Features / Requirements

### 5.1 Pillar 1: Legal & Corporate Infrastructure (The Foundation)
| ID | Feature | User Story | Priority |
| :--- | :--- | :--- | :--- |
| **F1.1** | **One-Tap LLC Formation** | As an athlete, I want to form a legal entity without hiring a lawyer so I can limit my personal liability. | P0 |
| **F1.2** | **NIL Disclosure Engine** | As an athlete, I want my contracts automatically sent to my university's compliance office to ensure I remain eligible. | P0 |
| **F1.3** | **Contract Repository** | As an athlete, I want a centralized place to store all my NIL agreements for easy retrieval during audits. | P1 |

### 5.2 Pillar 2: Wealth-Building Vault (The FinTech)
| ID | Feature | User Story | Priority |
| :--- | :--- | :--- | :--- |
| **F2.1** | **Tax Reserve Automation** | As an athlete, I want 30% of every incoming payment moved to a "Tax Vault" so I am not surprised in April. | P0 |
| **F2.2** | **Automated SEP-IRA** | As a high-earner, I want to auto-contribute to a SEP-IRA to maximize my retirement savings and lower my taxable income. | P1 |
| **F2.3** | **Integrated Business Debit** | As an entrepreneur, I want a physical/virtual card for business expenses (travel, gear) to keep personal and business separate. | P1 |

### 5.3 Pillar 3: Specialized Support (The Concierge)
| ID | Feature | User Story | Priority |
| :--- | :--- | :--- | :--- |
| **F3.1** | **On-Demand Sports Psych** | As a high-pressure athlete, I want instant access to a therapist who understands athletic identity. | P0 |
| **F3.2** | **Crisis Management Alert** | As a public figure, I want a "red button" for PR support if a social media scandal or legal issue arises. | P2 |

---

## 6. Features Out (Non-Goals)
*   **NIL Marketplace:** We are **not** an agency. We do not find deals for athletes. We manage the revenue *after* the deal is signed.
*   **General Consumer Banking:** We are not a replacement for their personal Venmo or daily checking; we are strictly for their "Athlete Corp" business.
*   **Agent Services:** We do not negotiate contracts. We provide the tools to professionalize the execution of those contracts.

---

## 7. Open Issues & Risks
*   **Regulatory Variance:** NIL laws vary by state (e.g., California vs. Texas). *Action: Hire a dedicated Policy Lead to map state-specific legal requirements into the automation engine.*
*   **Under-18 Users:** High school athletes in certain states can now sign NIL deals. *Action: Legal review of "Minor-owned LLCs" and custodial banking requirements.*
*   **Bank Partnership:** Requires a robust BaaS (Banking-as-a-Service) provider that supports high-net-worth individuals and entity accounts. *Action: Shortlist Unit, Treasury, or Stripe Treasury.*

---

**End of PRD**