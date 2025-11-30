-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- 1. Customer Segments
CREATE TABLE customer_segments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    profile_data JSONB NOT NULL,
    embedding VECTOR(1536),
    benchmarks JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 2. Product Hypotheses
CREATE TABLE product_experiments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    segment_id UUID REFERENCES customer_segments(id),
    status VARCHAR(50) DEFAULT 'DRAFT',
    budget_cents INT,
    details JSONB NOT NULL,
    embedding VECTOR(1536),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 3. Experiment Metrics
CREATE TABLE experiment_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experiment_id UUID REFERENCES product_experiments(id),
    metric_type VARCHAR(50),
    value NUMERIC,
    metadata JSONB,
    occurred_at TIMESTAMP DEFAULT NOW()
);

-- 4. Experiment Reports
CREATE TABLE experiment_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experiment_id UUID REFERENCES product_experiments(id),
    report_date DATE,
    roi_percentage NUMERIC,
    opportunity_score INT,
    metrics_summary JSONB,
    agent_analysis TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
