-- =====================================================
-- Silver Layer - Process-Specific Dimensions
-- Purpose: Process hierarchy dimensions with SCD Type 2
-- =====================================================

USE silver;

-- =====================================================
-- DIM_LOCAL_PROCESS_HIERARCHY (SCD Type 2)
-- Self-join hierarchy for site-specific process steps
-- Example: Cell Culture → Seed Train → Vial Thaw / T-Flask / Shake Flask
-- =====================================================
CREATE TABLE IF NOT EXISTS dim_local_process_hierarchy (
    -- Surrogate Key
    local_process_identity BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    -- Business Key
    process_step_ID STRING NOT NULL,

    -- Attributes
    process_step_name STRING,
    process_phase STRING,
    equipment_ID STRING,
    location STRING,
    parent_step_identity BIGINT,  -- Self-join FK
    hierarchy_level INT,
    is_leaf_process BOOLEAN,

    -- SCD Type 2 Columns
    effective_date DATE NOT NULL,
    expiration_date DATE,
    current_flag BOOLEAN NOT NULL DEFAULT TRUE,
    row_hash STRING,

    -- Audit Columns
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    source_system STRING

    -- Note: Foreign key constraint for self-join will be added after table creation
)
USING DELTA
PARTITIONED BY (effective_date)
COMMENT 'Dimension: Local Process Hierarchy with SCD Type 2 and self-join decomposition'
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

CREATE INDEX IF NOT EXISTS idx_local_process_business_key ON dim_local_process_hierarchy(process_step_ID, current_flag);
CREATE INDEX IF NOT EXISTS idx_local_process_parent ON dim_local_process_hierarchy(parent_step_identity);
CREATE INDEX IF NOT EXISTS idx_local_process_phase ON dim_local_process_hierarchy(process_phase);

-- =====================================================
-- DIM_COMMON_PROCESS_HIERARCHY (SCD Type 2)
-- Self-join hierarchy for standard process taxonomy
-- Example: Category → Phase → Step
-- =====================================================
CREATE TABLE IF NOT EXISTS dim_common_process_hierarchy (
    -- Surrogate Key
    common_process_identity BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    -- Business Key
    common_process_ID STRING NOT NULL,

    -- Attributes
    standard_process_name STRING,
    process_category STRING,
    process_subcategory STRING,
    parent_process_identity BIGINT,  -- Self-join FK
    hierarchy_level INT,
    regulatory_critical BOOLEAN,

    -- SCD Type 2 Columns
    effective_date DATE NOT NULL,
    expiration_date DATE,
    current_flag BOOLEAN NOT NULL DEFAULT TRUE,
    row_hash STRING,

    -- Audit Columns
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    source_system STRING

    -- Note: Foreign key constraint for self-join will be added after table creation
)
USING DELTA
PARTITIONED BY (effective_date)
COMMENT 'Dimension: Common Process Hierarchy with SCD Type 2 - industry standard process taxonomy'
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

CREATE INDEX IF NOT EXISTS idx_common_process_business_key ON dim_common_process_hierarchy(common_process_ID, current_flag);
CREATE INDEX IF NOT EXISTS idx_common_process_parent ON dim_common_process_hierarchy(parent_process_identity);
CREATE INDEX IF NOT EXISTS idx_common_process_category ON dim_common_process_hierarchy(process_category);
