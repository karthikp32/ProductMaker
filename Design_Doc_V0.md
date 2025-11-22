# System Overview

## Core Principle
Everything revolves around experiments tied to a target segment.
Each experiment tests a hypothesis: **“If we build X for users like Y, they’ll do Z.”**

## Primary Components

| Component | Purpose |
| :--- | :--- |
| **Orchestrator** | **(System)** The central manager that coordinates agents, enforces governance, and executes "Scale or Kill" decisions based on analytics. |
| **Multi-Agent System** | **(Brains)** Specialized agents that perform the actual work:<ul><li>**PM Agent**</li><li>**UX/UI Designer Agent**</li><li>**Backend System Design Agent**</li><li>**Frontend SWE Agent**</li><li>**Backend SWE Agent**</li><li>**Marketing Agent**</li><li>**Sales Agent**</li><li>**Analytics Agent**</li></ul> |
| **Event Bus** | **(Communication)** In-memory message broker that decouples agents and handles asynchronous events. |
| **Unified Data Store (PostgreSQL)** | **(Memory)** A single database handling all persistence:<ul><li>**Customer Segments:** Profiles & insights.</li><li>**Experiments:** Hypotheses & status.</li><li>**Metrics:** Raw events & financial data.</li><li>**Learning:** Vector embeddings for historical knowledge.</li></ul> |
| **Governance Layer** | **(Policy)** Hard-coded rules (budget caps, safety checks) that the Orchestrator enforces. |

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

## Event Bus Architecture

Since the system runs as a **Modular Monolith**, we use a lightweight **In-Memory Event Bus** to manage communication between agents. This avoids tight coupling and "spaghetti code."

### Why an Event Bus?
1.  **Decoupling:** Agents don't call each other directly. The PM Agent doesn't need to know the Designer Agent exists; it just announces "Spec Ready."
2.  **Asynchrony:** LLM operations are slow. The bus allows agents to trigger tasks without blocking the main thread.
3.  **Observability:** The bus acts as a central log for debugging the entire lifecycle of an experiment.

### Event Flow Example

1.  **PM Agent** finishes a spec → Publishes `SPEC_COMPLETED` event.
2.  **Event Bus** routes this event to all subscribers.
3.  **Designer Agent** (subscriber) wakes up, receives the spec, and starts designing.
4.  **Legal/Safety Agent** (subscriber) also wakes up to scan the spec for policy violations.

### Implementation Pattern (Python Pseudo-code)

```python
class EventBus:
    def publish(self, event_type, payload):
        # Log event
        # Notify all subscribers
        pass

    def subscribe(self, event_type, callback):
        # Register callback
        pass

# Usage
bus.publish("experiment_created", {"id": 123, "hypothesis": "..."})
```

## Data Model (PostgreSQL Schema)

We use a **Modular Monolith** approach with a single PostgreSQL database. We leverage **JSONB** for flexible document storage (profiles, ideas) and **pgvector** for semantic search (memory/learning).

### 1. Customer Segments (The "Knowledge Base")
Stores the deep understanding of each target group.
*   **Why JSONB?** Profiles vary wildly (e.g., "Tech Stack" vs "Clinical Needs").
*   **Why Vector?** Allows agents to find "similar" segments to avoid repeating work.

```sql
CREATE TABLE customer_segments (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,               -- e.g., "Indie Game Developers"
    profile_data JSONB NOT NULL,      -- { "pain_points": [...], "willingness_to_pay": "..." }
    embedding VECTOR(1536),           -- Semantic representation for similarity search
    benchmarks JSONB,                 -- { "avg_conversion": 0.02, "avg_cpc": 1.50 }
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 2. Product Hypotheses (The "Ideas")
Stores the experiments generated by the PM Agent.
*   **Hybrid Approach:** SQL columns for process tracking (`status`, `budget`), JSONB for creative content.

```sql
CREATE TABLE product_hypotheses (
    id UUID PRIMARY KEY,
    segment_id UUID REFERENCES customer_segments(id),
    status VARCHAR(50) DEFAULT 'DRAFT', -- DRAFT, RUNNING, COMPLETED, FAILED
    budget_cents INT,                 -- Stored in cents to avoid floating point errors
    details JSONB NOT NULL,           -- { "pain_point": "...", "solution": "...", "price": "..." }
    embedding VECTOR(1536),           -- To prevent duplicate ideas
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 3. Experiment Metrics (The "Raw Data")
Time-series log of every significant event.
*   **Purpose:** High-fidelity source of truth for debugging and analysis.

```sql
CREATE TABLE experiment_metrics (
    id UUID PRIMARY KEY,
    experiment_id UUID REFERENCES product_hypotheses(id),
    metric_type VARCHAR(50),          -- 'CLICK', 'SIGNUP', 'PAYMENT', 'ERROR'
    value NUMERIC,                    -- 1 (count) or 50.00 (money)
    metadata JSONB,                   -- { "source": "reddit_ad_1", "browser": "chrome" }
    occurred_at TIMESTAMP DEFAULT NOW()
);
```

### 4. Experiment Reports (The "Insights")
Derived analysis generated by the Analytics Agent.
*   **Purpose:** Agents read *this*, not the raw metrics. It contains the "Verdict".

```sql
CREATE TABLE experiment_reports (
    id UUID PRIMARY KEY,
    experiment_id UUID REFERENCES product_hypotheses(id),
    report_date DATE,
    
    -- Scores
    roi_percentage NUMERIC,
    opportunity_score INT,            -- 0-100 rating
    
    -- Calculated Metrics
    metrics_summary JSONB,            -- { "conversion_rate": "5%", "churn": "2%" }
    
    -- Qualitative Analysis
    agent_analysis TEXT,              -- "Success because the pain point was acute..."
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Orchestration & Memory

### Orchestrator
* Coordinates lifecycle of all product experiments.
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

Simple command-line interface. You talk to ProductMaker like this:

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