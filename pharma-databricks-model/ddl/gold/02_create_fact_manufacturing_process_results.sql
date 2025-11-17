-- =====================================================
-- Gold Layer - PROCESS STAR SCHEMA
-- Fact: MANUFACTURING_PROCESS_RESULTS
-- Purpose: Track manufacturing execution events
-- Grain: One row per process execution event
-- =====================================================

USE gold;

-- =====================================================
-- FACT_MANUFACTURING_PROCESS_RESULTS
-- Process Star Schema - 11 Dimensions
-- =====================================================
CREATE TABLE IF NOT EXISTS fact_manufacturing_process_results (
    -- Surrogate Key
    process_result_identity BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    -- Foreign Keys - Conformed Dimensions (8)
    batch_identity BIGINT NOT NULL,
    sample_identity BIGINT,
    source_material_identity BIGINT NOT NULL,
    manufacturer_identity BIGINT NOT NULL,
    specification_identity BIGINT,
    notification_identity BIGINT,
    document_identity BIGINT,
    source_system_identity BIGINT NOT NULL,

    -- Foreign Keys - Process-Specific Dimensions (2)
    local_process_identity BIGINT NOT NULL,
    common_process_identity BIGINT NOT NULL,

    -- Degenerate Dimensions
    process_execution_id STRING,

    -- Measures - Process Parameters
    cell_passage INT,
    yield_value DECIMAL(18, 4),
    yield_uom STRING,
    temperature_celsius DECIMAL(5, 2),
    pH_value DECIMAL(4, 2),
    viability_percent DECIMAL(5, 2),
    density_cells_ml DECIMAL(18, 2),

    -- Time Dimension
    process_timestamp TIMESTAMP NOT NULL,
    process_date DATE GENERATED ALWAYS AS (CAST(process_timestamp AS DATE)),

    -- Audit Columns
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    source_system STRING,

    -- Foreign Key Constraints (will be added after table creation)
    CONSTRAINT fk_process_batch FOREIGN KEY (batch_identity)
        REFERENCES silver.dim_batch(batch_identity),
    CONSTRAINT fk_process_sample FOREIGN KEY (sample_identity)
        REFERENCES silver.dim_sample(sample_identity),
    CONSTRAINT fk_process_source_material FOREIGN KEY (source_material_identity)
        REFERENCES silver.dim_material(material_identity),
    CONSTRAINT fk_process_manufacturer FOREIGN KEY (manufacturer_identity)
        REFERENCES silver.dim_manufacturer(manufacturer_identity),
    CONSTRAINT fk_process_specification FOREIGN KEY (specification_identity)
        REFERENCES silver.dim_specification(specification_identity),
    CONSTRAINT fk_process_notification FOREIGN KEY (notification_identity)
        REFERENCES silver.dim_notification(notification_identity),
    CONSTRAINT fk_process_document FOREIGN KEY (document_identity)
        REFERENCES silver.dim_document(document_identity),
    CONSTRAINT fk_process_source_system FOREIGN KEY (source_system_identity)
        REFERENCES silver.dim_source_system(source_system_identity),
    CONSTRAINT fk_process_local_process FOREIGN KEY (local_process_identity)
        REFERENCES silver.dim_local_process_hierarchy(local_process_identity),
    CONSTRAINT fk_process_common_process FOREIGN KEY (common_process_identity)
        REFERENCES silver.dim_common_process_hierarchy(common_process_identity)
)
USING DELTA
PARTITIONED BY (process_date)
COMMENT 'Fact Table: Manufacturing Process Results - process execution events with parameters'
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- Create indexes for query optimization
CREATE INDEX IF NOT EXISTS idx_fact_process_batch ON fact_manufacturing_process_results(batch_identity);
CREATE INDEX IF NOT EXISTS idx_fact_process_material ON fact_manufacturing_process_results(source_material_identity);
CREATE INDEX IF NOT EXISTS idx_fact_process_local ON fact_manufacturing_process_results(local_process_identity);
CREATE INDEX IF NOT EXISTS idx_fact_process_common ON fact_manufacturing_process_results(common_process_identity);
CREATE INDEX IF NOT EXISTS idx_fact_process_timestamp ON fact_manufacturing_process_results(process_timestamp);

-- Optimize table for common query patterns
OPTIMIZE fact_manufacturing_process_results
ZORDER BY (batch_identity, source_material_identity, process_date);
