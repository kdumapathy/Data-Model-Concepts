-- =====================================================
-- Bronze Layer - Genealogy-Specific Dimensions
-- Purpose: Raw tables for genealogy and traceability
-- =====================================================

USE bronze;

-- =====================================================
-- MATERIAL_LOT (Raw Landing)
-- =====================================================
CREATE TABLE IF NOT EXISTS bronze_material_lot (
    -- Source Data
    lot_number STRING,
    material_ID STRING,
    lot_status STRING,
    quantity DECIMAL(18, 2),
    quantity_uom STRING,
    manufacturing_date DATE,
    expiry_date DATE,
    supplier_lot STRING,

    -- Bronze Audit Columns
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    source_file_name STRING,
    source_system STRING
)
USING DELTA
COMMENT 'Bronze layer for Material Lot dimension - specific lot instances'
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- =====================================================
-- TRANSFORMATION (Raw Landing)
-- =====================================================
CREATE TABLE IF NOT EXISTS bronze_transformation (
    -- Source Data
    transformation_ID STRING,
    transformation_type STRING,
    transformation_name STRING,
    equipment_ID STRING,

    -- Bronze Audit Columns
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    source_file_name STRING,
    source_system STRING
)
USING DELTA
COMMENT 'Bronze layer for Transformation dimension - process steps that transform materials'
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- =====================================================
-- PRODUCTION_ORDER (Raw Landing)
-- =====================================================
CREATE TABLE IF NOT EXISTS bronze_production_order (
    -- Source Data
    production_order_ID STRING,
    order_type STRING,
    product_code STRING,
    planned_quantity DECIMAL(18, 2),
    planned_start DATE,
    planned_end DATE,
    order_status STRING,

    -- Bronze Audit Columns
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    source_file_name STRING,
    source_system STRING
)
USING DELTA
COMMENT 'Bronze layer for Production Order dimension - manufacturing work orders'
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- =====================================================
-- BATCH_GENEALOGY (Raw Landing - Bridge Table)
-- Many-to-many batch relationships
-- =====================================================
CREATE TABLE IF NOT EXISTS bronze_batch_genealogy (
    -- Source Data
    child_batch_ID STRING,
    parent_batch_ID STRING,
    contribution_percent DECIMAL(5, 2),
    sequence_order INT,
    relationship_type STRING,

    -- Bronze Audit Columns
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    source_file_name STRING,
    source_system STRING
)
USING DELTA
COMMENT 'Bronze layer for Batch Genealogy bridge table - batch splits, merges, pooling'
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);
