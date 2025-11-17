-- =====================================================
-- Bronze Layer - Fact Tables (Raw Landing)
-- Purpose: Raw fact data for 3 star schemas
-- =====================================================

USE bronze;

-- =====================================================
-- MANUFACTURING_PROCESS_RESULTS (Raw Landing)
-- Process Star Schema Fact Table
-- =====================================================
CREATE TABLE IF NOT EXISTS bronze_manufacturing_process_results (
    -- Foreign Key References (Business Keys)
    batch_ID STRING,
    sample_ID STRING,
    source_material_ID STRING,
    manufacturer_ID STRING,
    local_process_step_ID STRING,
    common_process_ID STRING,
    specification_ID STRING,
    notification_ID STRING,
    document_ID STRING,
    source_system_ID STRING,

    -- Measures
    cell_passage INT,
    yield_value DECIMAL(18, 4),
    yield_uom STRING,
    temperature_celsius DECIMAL(5, 2),
    pH_value DECIMAL(4, 2),
    viability_percent DECIMAL(5, 2),
    density_cells_ml DECIMAL(18, 2),
    process_timestamp TIMESTAMP,

    -- Bronze Audit Columns
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    source_file_name STRING,
    source_system STRING
)
USING DELTA
COMMENT 'Bronze layer for Manufacturing Process Results - process execution events'
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- =====================================================
-- ANALYTICAL_RESULTS (Raw Landing)
-- Analytical Star Schema Fact Table
-- =====================================================
CREATE TABLE IF NOT EXISTS bronze_analytical_results (
    -- Foreign Key References (Business Keys)
    batch_ID STRING,
    sample_ID STRING,
    source_material_ID STRING,
    manufacturer_ID STRING,
    test_ID STRING,
    test_location_ID STRING,
    analytical_method_ID STRING,
    condition_ID STRING,
    timepoint_ID STRING,
    specification_ID STRING,
    study_ID STRING,
    notification_ID STRING,
    document_ID STRING,
    source_system_ID STRING,

    -- Measures
    test_result DECIMAL(18, 4),
    test_uom STRING,
    cell_passage INT,
    test_timestamp TIMESTAMP,
    result_status STRING,
    oos_flag BOOLEAN,
    percent_difference DECIMAL(10, 4),

    -- Bronze Audit Columns
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    source_file_name STRING,
    source_system STRING
)
USING DELTA
COMMENT 'Bronze layer for Analytical Results - quality testing events'
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- =====================================================
-- BATCH_MATERIAL_USAGE (Raw Landing)
-- Genealogy Star Schema Fact Table
-- =====================================================
CREATE TABLE IF NOT EXISTS bronze_batch_material_usage (
    -- Foreign Key References (Business Keys)
    batch_ID STRING,
    material_lot_number STRING,
    transformation_ID STRING,
    production_order_ID STRING,

    -- Measures
    usage_type STRING,
    quantity_used DECIMAL(18, 4),
    quantity_uom STRING,
    usage_timestamp TIMESTAMP,
    bom_item_number STRING,

    -- Bronze Audit Columns
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    source_file_name STRING,
    source_system STRING
)
USING DELTA
COMMENT 'Bronze layer for Batch Material Usage - material consumption and traceability'
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);
