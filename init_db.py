import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def init_db():
    # Connect to default 'postgres' database to create the 'productmaker' db if it doesn't exist
    # Note: docker-compose usually handles DB creation via POSTGRES_DB env var, 
    # but this script ensures tables are created.
    
    conn = psycopg2.connect(
        dbname="productmaker",
        user="postgres",
        password="password",
        host="localhost",
        port="5432"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    # 1. Enable pgvector extension
    print("Enabling pgvector extension...")
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # 2. Create Task Queue Table
    print("Creating task_queue table...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS task_queue (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            topic VARCHAR(50) NOT NULL,
            payload JSONB NOT NULL,
            status VARCHAR(20) DEFAULT 'PENDING',
            worker_id UUID,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
    """)

    # 3. Create Customer Segments Table
    print("Creating customer_segments table...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS customer_segments (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name TEXT NOT NULL,
            profile_data JSONB NOT NULL,
            embedding VECTOR(1536),
            benchmarks JSONB,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)

    # 4. Create Product Experiments Table
    print("Creating product_experiments table...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS product_experiments (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            segment_id UUID REFERENCES customer_segments(id),
            status VARCHAR(50) DEFAULT 'DRAFT',
            budget_cents INT,
            details JSONB NOT NULL,
            design_doc_path TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)

    # 5. Create Experiment Metrics Table
    print("Creating experiment_metrics table...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS experiment_metrics (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            experiment_id UUID REFERENCES product_experiments(id),
            metric_type VARCHAR(50),
            value NUMERIC,
            metadata JSONB,
            occurred_at TIMESTAMP DEFAULT NOW()
        );
    """)

    # 6. Create Experiment Reports Table
    print("Creating experiment_reports table...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS experiment_reports (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            experiment_id UUID REFERENCES product_experiments(id),
            report_date DATE,
            roi_percentage NUMERIC,
            opportunity_score INT,
            metrics_summary JSONB,
            agent_analysis TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)

    print("Database initialization complete.")
    cur.close()
    conn.close()

if __name__ == "__main__":
    init_db()
