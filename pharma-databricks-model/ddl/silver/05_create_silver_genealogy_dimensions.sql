-- =====================================================
-- Silver Layer - Genealogy-Specific Dimensions
-- Purpose: Dimensions for material traceability
-- =====================================================

USE silver;

-- =====================================================
-- DIM_MATERIAL_LOT (SCD Type 2)
-- =====================================================
CREATE TABLE IF NOT EXISTS dim_material_lot (
    -- Surrogate Key
    material_lot_identity BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    -- Business Key
    lot_number STRING NOT NULL,

    -- Foreign Keys
    material_identity BIGINT,  -- FK to dim_material

    -- Attributes
    lot_status STRING,
    quantity DECIMAL(18, 2),
    quantity_uom STRING,
    manufacturing_date DATE,
    expiry_date DATE,
    supplier_lot STRING,

    -- SCD Type 2 Columns
    effective_date DATE NOT NULL,
    expiration_date DATE,
    current_flag BOOLEAN NOT NULL DEFAULT TRUE,
    row_hash STRING,

    -- Audit Columns
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    source_system STRING

    -- Note: Foreign key constraints will be added after all tables are created
)
USING DELTA
PARTITIONED BY (effective_date)
COMMENT 'Dimension: Material Lot with SCD Type 2 - specific lot instances'
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

CREATE INDEX IF NOT EXISTS idx_material_lot_business_key ON dim_material_lot(lot_number, current_flag);
CREATE INDEX IF NOT EXISTS idx_material_lot_material ON dim_material_lot(material_identity);

-- =====================================================
-- DIM_TRANSFORMATION (SCD Type 2)
-- =====================================================
CREATE TABLE IF NOT EXISTS dim_transformation (
    -- Surrogate Key
    transformation_identity BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    -- Business Key
    transformation_ID STRING NOT NULL,

    -- Attributes
    transformation_type STRING,
    transformation_name STRING,
    equipment_ID STRING,

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
COMMENT 'Dimension: Transformation with SCD Type 2 - process steps that transform materials'
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

CREATE INDEX IF NOT EXISTS idx_transformation_business_key ON dim_transformation(transformation_ID, current_flag);
CREATE INDEX IF NOT EXISTS idx_transformation_type ON dim_transformation(transformation_type);

-- =====================================================
-- DIM_PRODUCTION_ORDER (SCD Type 2)
-- =====================================================
CREATE TABLE IF NOT EXISTS dim_production_order (
    -- Surrogate Key
    production_order_identity BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    -- Business Key
    production_order_ID STRING NOT NULL,

    -- Attributes
    order_type STRING,
    product_code STRING,
    planned_quantity DECIMAL(18, 2),
    planned_start DATE,
    planned_end DATE,
    order_status STRING,

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
COMMENT 'Dimension: Production Order with SCD Type 2 - manufacturing work orders'
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

CREATE INDEX IF NOT EXISTS idx_production_order_business_key ON dim_production_order(production_order_ID, current_flag);
CREATE INDEX IF NOT EXISTS idx_production_order_status ON dim_production_order(order_status);
