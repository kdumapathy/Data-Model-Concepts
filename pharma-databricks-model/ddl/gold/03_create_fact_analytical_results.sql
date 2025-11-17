-- =====================================================
-- Gold Layer - ANALYTICAL STAR SCHEMA
-- Fact: ANALYTICAL_RESULTS
-- Purpose: Track quality control testing and stability studies
-- Grain: One row per test result
-- =====================================================

USE gold;

-- =====================================================
-- FACT_ANALYTICAL_RESULTS
-- Analytical Star Schema - 14 Dimensions
-- =====================================================
CREATE TABLE IF NOT EXISTS fact_analytical_results (
    -- Surrogate Key
    test_result_identity BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    -- Foreign Keys - Conformed Dimensions (8)
    batch_identity BIGINT NOT NULL,
    sample_identity BIGINT,
    source_material_identity BIGINT NOT NULL,
    manufacturer_identity BIGINT NOT NULL,
    specification_identity BIGINT,
    notification_identity BIGINT,
    document_identity BIGINT,
    source_system_identity BIGINT NOT NULL,

    -- Foreign Keys - Analytical-Specific Dimensions (6)
    test_identity BIGINT NOT NULL,
    test_location_identity BIGINT NOT NULL,
    analytical_method_identity BIGINT NOT NULL,
    condition_identity BIGINT,
    timepoint_identity BIGINT,
    study_identity BIGINT,

    -- Degenerate Dimensions
    test_execution_id STRING,

    -- Measures - Test Results
    test_result DECIMAL(18, 4),
    test_uom STRING,
    cell_passage INT,
    result_status STRING,
    oos_flag BOOLEAN,
    percent_difference DECIMAL(10, 4),

    -- Time Dimension
    test_timestamp TIMESTAMP NOT NULL,
    test_date DATE GENERATED ALWAYS AS (CAST(test_timestamp AS DATE)),

    -- Audit Columns
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    source_system STRING,

    -- Foreign Key Constraints
    CONSTRAINT fk_analytical_batch FOREIGN KEY (batch_identity)
        REFERENCES silver.dim_batch(batch_identity),
    CONSTRAINT fk_analytical_sample FOREIGN KEY (sample_identity)
        REFERENCES silver.dim_sample(sample_identity),
    CONSTRAINT fk_analytical_source_material FOREIGN KEY (source_material_identity)
        REFERENCES silver.dim_material(material_identity),
    CONSTRAINT fk_analytical_manufacturer FOREIGN KEY (manufacturer_identity)
        REFERENCES silver.dim_manufacturer(manufacturer_identity),
    CONSTRAINT fk_analytical_specification FOREIGN KEY (specification_identity)
        REFERENCES silver.dim_specification(specification_identity),
    CONSTRAINT fk_analytical_notification FOREIGN KEY (notification_identity)
        REFERENCES silver.dim_notification(notification_identity),
    CONSTRAINT fk_analytical_document FOREIGN KEY (document_identity)
        REFERENCES silver.dim_document(document_identity),
    CONSTRAINT fk_analytical_source_system FOREIGN KEY (source_system_identity)
        REFERENCES silver.dim_source_system(source_system_identity),
    CONSTRAINT fk_analytical_test FOREIGN KEY (test_identity)
        REFERENCES silver.dim_test(test_identity),
    CONSTRAINT fk_analytical_test_location FOREIGN KEY (test_location_identity)
        REFERENCES silver.dim_test_location(test_location_identity),
    CONSTRAINT fk_analytical_method FOREIGN KEY (analytical_method_identity)
        REFERENCES silver.dim_analytical_method(analytical_method_identity),
    CONSTRAINT fk_analytical_condition FOREIGN KEY (condition_identity)
        REFERENCES silver.dim_condition(condition_identity),
    CONSTRAINT fk_analytical_timepoint FOREIGN KEY (timepoint_identity)
        REFERENCES silver.dim_timepoint(timepoint_identity),
    CONSTRAINT fk_analytical_study FOREIGN KEY (study_identity)
        REFERENCES silver.dim_study(study_identity)
)
USING DELTA
PARTITIONED BY (test_date)
COMMENT 'Fact Table: Analytical Results - quality testing events including stability studies'
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- Create indexes for query optimization
CREATE INDEX IF NOT EXISTS idx_fact_analytical_batch ON fact_analytical_results(batch_identity);
CREATE INDEX IF NOT EXISTS idx_fact_analytical_material ON fact_analytical_results(source_material_identity);
CREATE INDEX IF NOT EXISTS idx_fact_analytical_test ON fact_analytical_results(test_identity);
CREATE INDEX IF NOT EXISTS idx_fact_analytical_study ON fact_analytical_results(study_identity);
CREATE INDEX IF NOT EXISTS idx_fact_analytical_timestamp ON fact_analytical_results(test_timestamp);
CREATE INDEX IF NOT EXISTS idx_fact_analytical_oos ON fact_analytical_results(oos_flag);

-- Optimize table for common query patterns
OPTIMIZE fact_analytical_results
ZORDER BY (batch_identity, test_identity, study_identity, test_date);
