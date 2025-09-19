-- Initialize trading bot database
-- This script is run when the PostgreSQL container starts

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create additional schemas if needed
CREATE SCHEMA IF NOT EXISTS trading;
CREATE SCHEMA IF NOT EXISTS monitoring;

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA trading TO tradingbot;
GRANT ALL PRIVILEGES ON SCHEMA monitoring TO tradingbot;

-- Create monitoring tables
CREATE TABLE IF NOT EXISTS monitoring.health_checks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    component VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    details JSONB,
    response_time_ms NUMERIC(10,2)
);

CREATE TABLE IF NOT EXISTS monitoring.system_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    cpu_percent NUMERIC(5,2),
    memory_percent NUMERIC(5,2),
    disk_percent NUMERIC(5,2),
    network_io JSONB,
    process_metrics JSONB
);

-- Create indexes for monitoring tables
CREATE INDEX IF NOT EXISTS idx_health_checks_timestamp ON monitoring.health_checks(timestamp);
CREATE INDEX IF NOT EXISTS idx_health_checks_component ON monitoring.health_checks(component);
CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp ON monitoring.system_metrics(timestamp);

-- Grant permissions on monitoring tables
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA monitoring TO tradingbot;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA monitoring TO tradingbot;