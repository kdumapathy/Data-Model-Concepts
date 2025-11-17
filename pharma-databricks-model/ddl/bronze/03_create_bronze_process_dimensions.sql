-- =====================================================
-- Bronze Layer - Process-Specific Dimensions
-- Purpose: Raw tables for process hierarchy dimensions
-- =====================================================

USE bronze;

-- =====================================================
-- LOCAL_PROCESS_HIERARCHY (Raw Landing)
-- Self-join hierarchy for site-specific process steps
-- =====================================================
CREATE TABLE IF NOT EXISTS bronze_local_process_hierarchy (
    -- Source Data
    process_step_ID STRING,
    process_step_name STRING,
    process_phase STRING,
    equipment_ID STRING,
    location STRING,
    parent_step_ID STRING,
    hierarchy_level INT,
    is_leaf_process BOOLEAN,

    -- Bronze Audit Columns
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    source_file_name STRING,
    source_system STRING
)
USING DELTA
COMMENT 'Bronze layer for Local Process Hierarchy - site-specific process decomposition'
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- =====================================================
-- COMMON_PROCESS_HIERARCHY (Raw Landing)
-- Self-join hierarchy for standard process taxonomy
-- =====================================================
CREATE TABLE IF NOT EXISTS bronze_common_process_hierarchy (
    -- Source Data
    common_process_ID STRING,
    standard_process_name STRING,
    process_category STRING,
    process_subcategory STRING,
    parent_process_ID STRING,
    hierarchy_level INT,
    regulatory_critical BOOLEAN,

    -- Bronze Audit Columns
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    source_file_name STRING,
    source_system STRING
)
USING DELTA
COMMENT 'Bronze layer for Common Process Hierarchy - industry standard process taxonomy'
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);
