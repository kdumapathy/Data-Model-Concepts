-- =====================================================
-- Silver Layer - Bridge Tables
-- Purpose: Many-to-many relationships
-- =====================================================

USE silver;

-- =====================================================
-- BRIDGE_BATCH_GENEALOGY
-- Many-to-many batch relationships
-- Handles batch splits (1 → many) and merges (many → 1)
-- =====================================================
CREATE TABLE IF NOT EXISTS bridge_batch_genealogy (
    -- Surrogate Key
    bridge_identity BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    -- Foreign Keys
    child_batch_identity BIGINT NOT NULL,
    parent_batch_identity BIGINT NOT NULL,

    -- Attributes
    contribution_percent DECIMAL(5, 2),
    sequence_order INT,
    relationship_type STRING,

    -- Audit Columns
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    source_system STRING,

    -- Composite unique constraint
    CONSTRAINT uk_batch_genealogy UNIQUE (child_batch_identity, parent_batch_identity)

    -- Note: Foreign key constraints will be added after all tables are created
)
USING DELTA
COMMENT 'Bridge Table: Batch Genealogy - many-to-many batch relationships for splits, merges, pooling'
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

CREATE INDEX IF NOT EXISTS idx_bridge_child_batch ON bridge_batch_genealogy(child_batch_identity);
CREATE INDEX IF NOT EXISTS idx_bridge_parent_batch ON bridge_batch_genealogy(parent_batch_identity);
CREATE INDEX IF NOT EXISTS idx_bridge_relationship_type ON bridge_batch_genealogy(relationship_type);

-- =====================================================
-- Create views for current versions of SCD Type 2 tables
-- These views simplify querying by filtering to current_flag = true
-- =====================================================

-- Current Batch View
CREATE OR REPLACE VIEW v_dim_batch_current AS
SELECT * FROM dim_batch WHERE current_flag = TRUE;

-- Current Material View
CREATE OR REPLACE VIEW v_dim_material_current AS
SELECT * FROM dim_material WHERE current_flag = TRUE;

-- Current Sample View
CREATE OR REPLACE VIEW v_dim_sample_current AS
SELECT * FROM dim_sample WHERE current_flag = TRUE;

-- Current Manufacturer View
CREATE OR REPLACE VIEW v_dim_manufacturer_current AS
SELECT * FROM dim_manufacturer WHERE current_flag = TRUE;

-- Current Specification View
CREATE OR REPLACE VIEW v_dim_specification_current AS
SELECT * FROM dim_specification WHERE current_flag = TRUE;

-- Current Local Process Hierarchy View
CREATE OR REPLACE VIEW v_dim_local_process_hierarchy_current AS
SELECT * FROM dim_local_process_hierarchy WHERE current_flag = TRUE;

-- Current Common Process Hierarchy View
CREATE OR REPLACE VIEW v_dim_common_process_hierarchy_current AS
SELECT * FROM dim_common_process_hierarchy WHERE current_flag = TRUE;

-- Current Test View
CREATE OR REPLACE VIEW v_dim_test_current AS
SELECT * FROM dim_test WHERE current_flag = TRUE;

-- Current Test Location View
CREATE OR REPLACE VIEW v_dim_test_location_current AS
SELECT * FROM dim_test_location WHERE current_flag = TRUE;

-- Current Analytical Method View
CREATE OR REPLACE VIEW v_dim_analytical_method_current AS
SELECT * FROM dim_analytical_method WHERE current_flag = TRUE;

-- Current Condition View
CREATE OR REPLACE VIEW v_dim_condition_current AS
SELECT * FROM dim_condition WHERE current_flag = TRUE;

-- Current Timepoint View
CREATE OR REPLACE VIEW v_dim_timepoint_current AS
SELECT * FROM dim_timepoint WHERE current_flag = TRUE;

-- Current Study View
CREATE OR REPLACE VIEW v_dim_study_current AS
SELECT * FROM dim_study WHERE current_flag = TRUE;

-- Current Material Lot View
CREATE OR REPLACE VIEW v_dim_material_lot_current AS
SELECT * FROM dim_material_lot WHERE current_flag = TRUE;

-- Current Transformation View
CREATE OR REPLACE VIEW v_dim_transformation_current AS
SELECT * FROM dim_transformation WHERE current_flag = TRUE;

-- Current Production Order View
CREATE OR REPLACE VIEW v_dim_production_order_current AS
SELECT * FROM dim_production_order WHERE current_flag = TRUE;
