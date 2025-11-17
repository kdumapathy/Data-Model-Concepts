-- =====================================================
-- Bronze Layer - Analytical-Specific Dimensions
-- Purpose: Raw tables for analytical testing dimensions
-- =====================================================

USE bronze;

-- =====================================================
-- TEST (Raw Landing)
-- =====================================================
CREATE TABLE IF NOT EXISTS bronze_test (
    -- Source Data
    test_ID STRING,
    test_name STRING,
    test_category STRING,
    test_method_category STRING,
    test_component STRING,

    -- Bronze Audit Columns
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    source_file_name STRING,
    source_system STRING
)
USING DELTA
COMMENT 'Bronze layer for Test dimension - identity, purity, potency, safety tests'
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- =====================================================
-- TEST_LOCATION (Raw Landing)
-- =====================================================
CREATE TABLE IF NOT EXISTS bronze_test_location (
    -- Source Data
    location_ID STRING,
    laboratory_name STRING,
    facility STRING,
    country STRING,
    clia_number STRING,

    -- Bronze Audit Columns
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    source_file_name STRING,
    source_system STRING
)
USING DELTA
COMMENT 'Bronze layer for Test Location dimension - testing laboratories'
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- =====================================================
-- ANALYTICAL_METHOD (Raw Landing)
-- =====================================================
CREATE TABLE IF NOT EXISTS bronze_analytical_method (
    -- Source Data
    method_ID STRING,
    method_name STRING,
    method_type STRING,
    technique STRING,
    instrument_type STRING,
    validation_date DATE,

    -- Bronze Audit Columns
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    source_file_name STRING,
    source_system STRING
)
USING DELTA
COMMENT 'Bronze layer for Analytical Method dimension - HPLC, ELISA, qPCR, Western'
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- =====================================================
-- CONDITION (Raw Landing)
-- =====================================================
CREATE TABLE IF NOT EXISTS bronze_condition (
    -- Source Data
    condition_ID STRING,
    storage_condition STRING,
    temperature_celsius DECIMAL(5, 2),
    relative_humidity DECIMAL(5, 2),
    light_exposure STRING,

    -- Bronze Audit Columns
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    source_file_name STRING,
    source_system STRING
)
USING DELTA
COMMENT 'Bronze layer for Condition dimension - storage conditions for stability'
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- =====================================================
-- TIMEPOINT (Raw Landing)
-- =====================================================
CREATE TABLE IF NOT EXISTS bronze_timepoint (
    -- Source Data
    timepoint_ID STRING,
    timepoint_value DECIMAL(10, 2),
    timepoint_uom STRING,
    timepoint_label STRING,

    -- Bronze Audit Columns
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    source_file_name STRING,
    source_system STRING
)
USING DELTA
COMMENT 'Bronze layer for Timepoint dimension - T0, 1mo, 3mo, 6mo, 12mo, 24mo'
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- =====================================================
-- STUDY (Raw Landing)
-- =====================================================
CREATE TABLE IF NOT EXISTS bronze_study (
    -- Source Data
    study_ID STRING,
    study_name STRING,
    study_type STRING,
    study_phase STRING,
    study_start_date DATE,
    study_end_date DATE,

    -- Bronze Audit Columns
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    source_file_name STRING,
    source_system STRING
)
USING DELTA
COMMENT 'Bronze layer for Study dimension - stability, release, characterization studies'
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);
