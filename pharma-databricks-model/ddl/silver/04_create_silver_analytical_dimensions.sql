-- =====================================================
-- Silver Layer - Analytical-Specific Dimensions
-- Purpose: Dimensions for quality testing and stability
-- =====================================================

USE silver;

-- =====================================================
-- DIM_TEST (SCD Type 2)
-- =====================================================
CREATE TABLE IF NOT EXISTS dim_test (
    -- Surrogate Key
    test_identity BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    -- Business Key
    test_ID STRING NOT NULL,

    -- Attributes
    test_name STRING,
    test_category STRING,
    test_method_category STRING,
    test_component STRING,

    -- SCD Type 2 Columns
    effective_date DATE NOT NULL,
    expiration_date DATE,
    current_flag BOOLEAN NOT NULL DEFAULT TRUE,
    row_hash STRING,

    -- Audit Columns
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    source_system STRING
)
USING DELTA
PARTITIONED BY (effective_date)
COMMENT 'Dimension: Test with SCD Type 2 - identity, purity, potency, safety tests'
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

CREATE INDEX IF NOT EXISTS idx_test_business_key ON dim_test(test_ID, current_flag);
CREATE INDEX IF NOT EXISTS idx_test_category ON dim_test(test_category);

-- =====================================================
-- DIM_TEST_LOCATION (SCD Type 2)
-- =====================================================
CREATE TABLE IF NOT EXISTS dim_test_location (
    -- Surrogate Key
    test_location_identity BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    -- Business Key
    location_ID STRING NOT NULL,

    -- Attributes
    laboratory_name STRING,
    facility STRING,
    country STRING,
    clia_number STRING,

    -- SCD Type 2 Columns
    effective_date DATE NOT NULL,
    expiration_date DATE,
    current_flag BOOLEAN NOT NULL DEFAULT TRUE,
    row_hash STRING,

    -- Audit Columns
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    source_system STRING
)
USING DELTA
PARTITIONED BY (effective_date)
COMMENT 'Dimension: Test Location with SCD Type 2 - testing laboratories'
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

CREATE INDEX IF NOT EXISTS idx_test_location_business_key ON dim_test_location(location_ID, current_flag);

-- =====================================================
-- DIM_ANALYTICAL_METHOD (SCD Type 2)
-- =====================================================
CREATE TABLE IF NOT EXISTS dim_analytical_method (
    -- Surrogate Key
    analytical_method_identity BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    -- Business Key
    method_ID STRING NOT NULL,

    -- Attributes
    method_name STRING,
    method_type STRING,
    technique STRING,
    instrument_type STRING,
    validation_date DATE,

    -- SCD Type 2 Columns
    effective_date DATE NOT NULL,
    expiration_date DATE,
    current_flag BOOLEAN NOT NULL DEFAULT TRUE,
    row_hash STRING,

    -- Audit Columns
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    source_system STRING
)
USING DELTA
PARTITIONED BY (effective_date)
COMMENT 'Dimension: Analytical Method with SCD Type 2 - HPLC, ELISA, qPCR, Western'
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

CREATE INDEX IF NOT EXISTS idx_analytical_method_business_key ON dim_analytical_method(method_ID, current_flag);
CREATE INDEX IF NOT EXISTS idx_analytical_method_technique ON dim_analytical_method(technique);

-- =====================================================
-- DIM_CONDITION (SCD Type 2)
-- =====================================================
CREATE TABLE IF NOT EXISTS dim_condition (
    -- Surrogate Key
    condition_identity BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    -- Business Key
    condition_ID STRING NOT NULL,

    -- Attributes
    storage_condition STRING,
    temperature_celsius DECIMAL(5, 2),
    relative_humidity DECIMAL(5, 2),
    light_exposure STRING,

    -- SCD Type 2 Columns
    effective_date DATE NOT NULL,
    expiration_date DATE,
    current_flag BOOLEAN NOT NULL DEFAULT TRUE,
    row_hash STRING,

    -- Audit Columns
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    source_system STRING
)
USING DELTA
PARTITIONED BY (effective_date)
COMMENT 'Dimension: Condition with SCD Type 2 - storage conditions for stability studies'
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

CREATE INDEX IF NOT EXISTS idx_condition_business_key ON dim_condition(condition_ID, current_flag);

-- =====================================================
-- DIM_TIMEPOINT (SCD Type 2)
-- =====================================================
CREATE TABLE IF NOT EXISTS dim_timepoint (
    -- Surrogate Key
    timepoint_identity BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    -- Business Key
    timepoint_ID STRING NOT NULL,

    -- Attributes
    timepoint_value DECIMAL(10, 2),
    timepoint_uom STRING,
    timepoint_label STRING,

    -- SCD Type 2 Columns
    effective_date DATE NOT NULL,
    expiration_date DATE,
    current_flag BOOLEAN NOT NULL DEFAULT TRUE,
    row_hash STRING,

    -- Audit Columns
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    source_system STRING
)
USING DELTA
PARTITIONED BY (effective_date)
COMMENT 'Dimension: Timepoint with SCD Type 2 - T0, 1mo, 3mo, 6mo, 12mo, 24mo'
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

CREATE INDEX IF NOT EXISTS idx_timepoint_business_key ON dim_timepoint(timepoint_ID, current_flag);

-- =====================================================
-- DIM_STUDY (SCD Type 2)
-- =====================================================
CREATE TABLE IF NOT EXISTS dim_study (
    -- Surrogate Key
    study_identity BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    -- Business Key
    study_ID STRING NOT NULL,

    -- Attributes
    study_name STRING,
    study_type STRING,
    study_phase STRING,
    study_start_date DATE,
    study_end_date DATE,

    -- SCD Type 2 Columns
    effective_date DATE NOT NULL,
    expiration_date DATE,
    current_flag BOOLEAN NOT NULL DEFAULT TRUE,
    row_hash STRING,

    -- Audit Columns
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    source_system STRING
)
USING DELTA
PARTITIONED BY (effective_date)
COMMENT 'Dimension: Study with SCD Type 2 - stability, release, characterization studies'
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

CREATE INDEX IF NOT EXISTS idx_study_business_key ON dim_study(study_ID, current_flag);
CREATE INDEX IF NOT EXISTS idx_study_type ON dim_study(study_type);
