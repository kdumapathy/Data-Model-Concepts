-- =====================================================
-- Silver Layer - Conformed Dimensions with SCD Type 2
-- Purpose: 8 conformed dimensions shared across star schemas
-- Implements: Surrogate keys, SCD Type 2, self-join hierarchies
-- =====================================================

USE silver;

-- =====================================================
-- DIM_BATCH (SCD Type 2)
-- Self-join hierarchy for batch genealogy
-- =====================================================
CREATE TABLE IF NOT EXISTS dim_batch (
    -- Surrogate Key
    batch_identity BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    -- Business Key
    batch_ID STRING NOT NULL,

    -- Attributes
    batch_status STRING,
    parent_batch_identity BIGINT,  -- Self-join FK
    genealogy_type STRING,
    lineage_path STRING,
    generation_level INT,
    source_material_identity BIGINT,  -- FK to dim_material
    batch_size DECIMAL(18, 2),
    batch_size_uom STRING,
    mfg_start_date DATE,
    mfg_end_date DATE,
    production_order STRING,

    -- SCD Type 2 Columns
    effective_date DATE NOT NULL,
    expiration_date DATE,
    current_flag BOOLEAN NOT NULL DEFAULT TRUE,
    row_hash STRING,

    -- Audit Columns
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    source_system STRING

    -- Note: Foreign key constraints for self-joins will be added after table creation
)
USING DELTA
PARTITIONED BY (effective_date)
COMMENT 'Dimension: Batch with SCD Type 2 and self-join genealogy hierarchy'
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_batch_business_key ON dim_batch(batch_ID, current_flag);
CREATE INDEX IF NOT EXISTS idx_batch_parent ON dim_batch(parent_batch_identity);
CREATE INDEX IF NOT EXISTS idx_batch_source_material ON dim_batch(source_material_identity);

-- =====================================================
-- DIM_MATERIAL (SCD Type 2)
-- Self-join hierarchy for material lineage
-- Vector → Cell Line → MCB → WCB → Therapeutic Protein
-- =====================================================
CREATE TABLE IF NOT EXISTS dim_material (
    -- Surrogate Key
    material_identity BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    -- Business Key
    material_ID STRING NOT NULL,

    -- Attributes
    material_type STRING,
    material_name STRING,
    protein_sequence STRING,
    target_antigen STRING,
    protein_subtype STRING,
    molecular_weight_kda DECIMAL(10, 2),
    vector_name STRING,
    vector_size_bp INT,
    promoter STRING,
    species_of_origin STRING,
    passage_number INT,
    parent_material_identity BIGINT,  -- Self-join FK
    lineage_path STRING,
    hierarchy_level INT,

    -- SCD Type 2 Columns
    effective_date DATE NOT NULL,
    expiration_date DATE,
    current_flag BOOLEAN NOT NULL DEFAULT TRUE,
    row_hash STRING,

    -- Audit Columns
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    source_system STRING

    -- Note: Foreign key constraints for self-joins will be added after table creation
)
USING DELTA
PARTITIONED BY (effective_date)
COMMENT 'Dimension: Material with SCD Type 2 and self-join lineage hierarchy'
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_material_business_key ON dim_material(material_ID, current_flag);
CREATE INDEX IF NOT EXISTS idx_material_parent ON dim_material(parent_material_identity);
CREATE INDEX IF NOT EXISTS idx_material_type ON dim_material(material_type);

-- =====================================================
-- DIM_SAMPLE (SCD Type 2)
-- =====================================================
CREATE TABLE IF NOT EXISTS dim_sample (
    -- Surrogate Key
    sample_identity BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    -- Business Key
    sample_ID STRING NOT NULL,

    -- Attributes
    vial_number STRING,
    sample_type STRING,
    collection_date DATE,
    storage_location STRING,

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
COMMENT 'Dimension: Sample with SCD Type 2'
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

CREATE INDEX IF NOT EXISTS idx_sample_business_key ON dim_sample(sample_ID, current_flag);

-- =====================================================
-- DIM_MANUFACTURER (SCD Type 2)
-- =====================================================
CREATE TABLE IF NOT EXISTS dim_manufacturer (
    -- Surrogate Key
    manufacturer_identity BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    -- Business Key
    manufacturer_ID STRING NOT NULL,

    -- Attributes
    manufacturer_name STRING,
    manufacturer_type STRING,
    facility_location STRING,
    country STRING,
    regulatory_status STRING,

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
COMMENT 'Dimension: Manufacturer with SCD Type 2 - includes CMOs and testing labs'
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

CREATE INDEX IF NOT EXISTS idx_manufacturer_business_key ON dim_manufacturer(manufacturer_ID, current_flag);

-- =====================================================
-- DIM_SPECIFICATION (SCD Type 2)
-- =====================================================
CREATE TABLE IF NOT EXISTS dim_specification (
    -- Surrogate Key
    specification_identity BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    -- Business Key
    specification_ID STRING NOT NULL,

    -- Attributes
    specification_type STRING,
    parameter_name STRING,
    target_value DECIMAL(18, 4),
    lower_limit DECIMAL(18, 4),
    upper_limit DECIMAL(18, 4),
    uom STRING,

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
COMMENT 'Dimension: Specification with SCD Type 2'
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

CREATE INDEX IF NOT EXISTS idx_specification_business_key ON dim_specification(specification_ID, current_flag);

-- =====================================================
-- DIM_NOTIFICATION
-- No SCD Type 2 - events are immutable
-- =====================================================
CREATE TABLE IF NOT EXISTS dim_notification (
    -- Surrogate Key
    notification_identity BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    -- Business Key
    notification_ID STRING NOT NULL UNIQUE,

    -- Attributes
    notification_type STRING,
    event_type STRING,
    severity_level STRING,
    notification_status STRING,
    notification_description STRING,
    notification_date DATE,

    -- Audit Columns
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    source_system STRING
)
USING DELTA
COMMENT 'Dimension: Notification - deviations, CAPAs, change controls (immutable events)'
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

CREATE INDEX IF NOT EXISTS idx_notification_business_key ON dim_notification(notification_ID);

-- =====================================================
-- DIM_DOCUMENT
-- No SCD Type 2 - documents are immutable
-- =====================================================
CREATE TABLE IF NOT EXISTS dim_document (
    -- Surrogate Key
    document_identity BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    -- Business Key
    document_ID STRING NOT NULL UNIQUE,

    -- Attributes
    document_type STRING,
    document_name STRING,
    document_title STRING,
    document_url STRING,
    gel_image STRING,
    upload_date DATE,

    -- Audit Columns
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    source_system STRING
)
USING DELTA
COMMENT 'Dimension: Document - batch records, COAs, SOPs (immutable)'
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

CREATE INDEX IF NOT EXISTS idx_document_business_key ON dim_document(document_ID);

-- =====================================================
-- DIM_SOURCE_SYSTEM
-- No SCD Type 2 - reference data
-- =====================================================
CREATE TABLE IF NOT EXISTS dim_source_system (
    -- Surrogate Key
    source_system_identity BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    -- Business Key
    source_system_ID STRING NOT NULL UNIQUE,

    -- Attributes
    source_system_name STRING,
    system_type STRING,
    vendor STRING,
    version STRING,
    is_active BOOLEAN,

    -- Audit Columns
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
USING DELTA
COMMENT 'Dimension: Source System - LIMS, MES, ELN, ERP'
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

CREATE INDEX IF NOT EXISTS idx_source_system_business_key ON dim_source_system(source_system_ID);
