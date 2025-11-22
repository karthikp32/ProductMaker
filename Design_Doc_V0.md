# System Overview

## Core Principle
Everything revolves around experiments tied to a target segment.
Each experiment tests a hypothesis: **“If we build X for users like Y, they’ll do Z.”**

## Primary Components

| Component | Purpose |
| :--- | :--- |
| **Customer Segment Data Store** | **(Tool)** A database storing market data, persona profiles, and segment insights for agents to query. |
| **Experiment Data Store** | **(Tool)** A database tracking the state, configuration, and results of all product experiments. |
| **Multi-Agent System** | Orchestrates the entire product lifecycle with specialized agents:<ul>
<li>**PM Agent:** Defines strategy, roadmap, and user stories.</li>
<li>**UX/UI Designer Agent:** Focuses on UX/UI, wireframes, and prototypes.</li>
<li>**Backend System Design Agent:** Designs the system architecture and data models.</li>
<li>**Frontend SWE Agent:** Implements user-facing features and UI logic.</li>
<li>**Backend SWE Agent:** Implements server-side logic, APIs, and database interactions.</li>
<li>**Marketing Agent:** Develops messaging, campaigns, and drives user acquisition.</li>
<li>**Sales Agent:** Handles lead generation, conversions, and customer relationships.</li>
<li>**Analytics Agent:** Tracks technical, product, and business KPIs for each experiment.</li>
</ul> |
| **Revenue Engine** | Connects experiments to real monetization (e.g., Stripe sandbox, leads, ad conversions). |
| **Analytics Engine** | Tracks technical, product, and business KPIs for each experiment. |
| **Memory & Learning** | Builds historical knowledge about what worked for which segments. |
| **Governance Layer** | Budgeting, safety, compliance, and human approval checkpoints. |

## Core Concept: “Customer Segment → Experiments → Winners”

Each Customer Segment Run goes through this lifecycle:

### Step 1 — Define Customer Segment
**PM Agent identifies and writes to Customer Segment Data Store:**
* Persona profiles
* Typical workflows
* Pain points
* Willingness to pay
* Communication channels (Reddit, X, Slack groups)

### Step 2 — Generate Hypotheses
**PM Agent proposes 3–10 candidate product ideas based on segment data.**
Each includes:
* Pain point
* Solution concept
* Expected outcome
* Price hypothesis

### Step 3 — Design & Build
**Designer + SWE Agents:**
* Produce clickable prototype or live MVP.
* Deploy to staging or limited live environment.
* Integrate basic telemetry & payment hooks.

### Step 4 — Launch & Market
**Marketing + Sales Agents:**
* Push experiment campaigns to relevant channels.
* Run cold outreach or ad tests.
* Measure click-through, signups, demos booked, or payments.

### Step 5 — Measure & Learn
**Analytics + PM Agents:**
* Collect adoption, conversion, churn, and engagement data.
* Compute ROI and opportunity score.
* Compare against segment benchmarks.

### Step 6 — Scale or Kill
* Experiments that hit KPI thresholds get scaled up.
* Others are stopped, and their learnings feed back to the Segment Knowledge Base.

## Customer Segment Data Store

A database that holds the deep knowledge about users.

### Inputs
* Public data (Reddit, ProductHunt, LinkedIn groups)
* Market research reports
* Prior ProductMaker experiments

### Outputs
**Customer Segment Card** (example below):

```json
{
  "segment": "indie_game_developers",
  "size_estimate": "200k globally",
  "top_pain_points": [
    "marketing and visibility",
    "time wasted on backend/infrastructure",
    "lack of analytics"
  ],
  "pricing_bands": ["$10-50/month", "$100-200 one-time"],
  "preferred_channels": ["Reddit r/gamedev", "Discord servers"],
  "examples": ["solo developers on itch.io", "2-person Unity teams"]
}
```

### How it works
* Runs a discovery loop (web scraping, embeddings, sentiment analysis).
* Builds persona embeddings for fast similarity matching.
* Supports multi-segment targeting (e.g., “SaaS founders and indie devs”).

## Experiment Data Store

**Goal:** Persist the state and history of all experiments.
The PM Agent writes to this store, and the Orchestrator reads from it to execute.

### Experiment Schema

```json
{
  "experiment_id": "exp-20251113-001",
  "segment": "indie_game_developers",
  "hypothesis": "A plug-and-play backend will reduce setup time by 80%",
  "solution_type": "SaaS MVP",
  "budget_usd": 200,
  "success_criteria": {
    "signup_rate": ">5%",
    "willingness_to_pay": ">=3 paying users"
  },
  "duration_days": 10
}
```

### Execution Model
* Experiments run in sandboxes.
* Each has its own mini-team of agents.
* The Orchestrator ensures resource isolation and budget caps.
* After completion → archived with full results and lessons learned.

## Agent System (Simplified Roles)

| Agent | Role |
| :--- | :--- |
| **PM Agent** | Researches, defines segment, writes ExperimentSpecs, measures success. |
| **Designer Agent** | Designs mockups & copy for MVPs and campaigns. |
| **SWE Agent** | Builds MVP backend/frontend with CI/CD automation. |
| **QA Agent** | Tests functionality, accessibility, and basic performance. |
| **Marketing Agent** | Runs Reddit/Twitter ads, writes posts, tracks engagement. |
| **Sales Agent** | Conducts cold outreach and logs responses. |
| **Analytics Agent** | Tracks metrics, runs A/B tests, and ranks experiments. |

Each agent communicates via event bus, with explicit task contracts (so you can swap in improved versions later).

## Orchestration & Memory

### Orchestrator
* Coordinates lifecycle of all segment experiments.
* Enforces global policies (budget, safety).
* Tracks state transitions (idea → design → build → test → release → eval).

### Memory / Learning Layer
* Stores all experiment metadata, results, and qualitative feedback.
* Embedding index for “What’s worked before for similar segments?”
* Enables meta-learning so future experiments improve over time.

## Metrics Hierarchy

| Category | Metrics |
| :--- | :--- |
| **User Behavior** | DAU, retention, conversion, engagement |
| **Technical** | uptime, latency, error rates |
| **Monetization** | free-to-paid conversion, ARPU, gross revenue |
| **Experiment Efficiency** | time-to-launch, cost-per-experiment, success rate |
| **Learning Loop** | improvement in idea quality per segment over time |

## Revenue Engine

To prove self-sustainability, ProductMaker should:
* Plug into Stripe sandbox for initial “mock revenue”.
* Progress to real Stripe/PayPal for real customers.
* Log unit economics per experiment.
* Rank experiments by revenue-per-dollar-spent.
* Later: auto-scale profitable ones, kill the rest.

## Interface (How you use ProductMaker)

Simple command interface. You talk to ProductMaker like this:

**You:**
> “ProductMaker, focus on indie game developers. Try to find a $30/month painkiller tool.”

**ProductMaker:**
> “✅ Created segment profile: indie_game_developers
> 🚀 Launching 5 experiments targeting their top pain points.
> 🔍 First MVP: Auto-build analytics dashboards for Unity games. Estimated completion: 4 days.”

## Safety, Controls, and Ethics

* Hard limits on campaign spend, outreach volume, and compute cost.
* No real user data without opt-in or anonymization.
* Human approval required before any public campaign or payment.
* Experiments must tag all data and actions with origin for traceability.