-- =====================================================
-- Bronze Layer - Conformed Dimensions (Raw Landing)
-- Purpose: Raw tables for 8 conformed dimensions
-- These tables accept data as-is with audit columns
-- =====================================================

USE bronze;

-- =====================================================
-- BATCH (Raw Landing)
-- Self-join hierarchy for batch genealogy
-- =====================================================
CREATE TABLE IF NOT EXISTS bronze_batch (
    -- Source Data
    batch_ID STRING,
    batch_status STRING,
    parent_batch_ID STRING,
    genealogy_type STRING,
    lineage_path STRING,
    generation_level INT,
    source_material_ID STRING,
    batch_size DECIMAL(18, 2),
    batch_size_uom STRING,
    mfg_start_date DATE,
    mfg_end_date DATE,
    production_order STRING,

    -- Bronze Audit Columns
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    source_file_name STRING,
    source_system STRING
)
USING DELTA
COMMENT 'Bronze layer for Batch dimension - raw data with audit columns'
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- =====================================================
-- MATERIAL (Raw Landing)
-- Self-join hierarchy for material lineage
-- =====================================================
CREATE TABLE IF NOT EXISTS bronze_material (
    -- Source Data
    material_ID STRING,
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
    parent_material_ID STRING,
    lineage_path STRING,
    hierarchy_level INT,

    -- Bronze Audit Columns
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    source_file_name STRING,
    source_system STRING
)
USING DELTA
COMMENT 'Bronze layer for Material dimension - supports Vector->CellLine->MCB->WCB->Protein lineage'
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- =====================================================
-- SAMPLE (Raw Landing)
-- =====================================================
CREATE TABLE IF NOT EXISTS bronze_sample (
    -- Source Data
    sample_ID STRING,
    vial_number STRING,
    sample_type STRING,
    collection_date DATE,
    storage_location STRING,

    -- Bronze Audit Columns
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    source_file_name STRING,
    source_system STRING
)
USING DELTA
COMMENT 'Bronze layer for Sample dimension'
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- =====================================================
-- MANUFACTURER (Raw Landing)
-- =====================================================
CREATE TABLE IF NOT EXISTS bronze_manufacturer (
    -- Source Data
    manufacturer_ID STRING,
    manufacturer_name STRING,
    manufacturer_type STRING,
    facility_location STRING,
    country STRING,
    regulatory_status STRING,

    -- Bronze Audit Columns
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    source_file_name STRING,
    source_system STRING
)
USING DELTA
COMMENT 'Bronze layer for Manufacturer dimension - includes CMOs and testing labs'
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- =====================================================
-- SPECIFICATION (Raw Landing)
-- =====================================================
CREATE TABLE IF NOT EXISTS bronze_specification (
    -- Source Data
    specification_ID STRING,
    specification_type STRING,
    parameter_name STRING,
    target_value DECIMAL(18, 4),
    lower_limit DECIMAL(18, 4),
    upper_limit DECIMAL(18, 4),
    uom STRING,

    -- Bronze Audit Columns
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    source_file_name STRING,
    source_system STRING
)
USING DELTA
COMMENT 'Bronze layer for Specification dimension'
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- =====================================================
-- NOTIFICATION (Raw Landing)
-- =====================================================
CREATE TABLE IF NOT EXISTS bronze_notification (
    -- Source Data
    notification_ID STRING,
    notification_type STRING,
    event_type STRING,
    severity_level STRING,
    notification_status STRING,
    notification_description STRING,
    notification_date DATE,

    -- Bronze Audit Columns
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    source_file_name STRING,
    source_system STRING
)
USING DELTA
COMMENT 'Bronze layer for Notification dimension - deviations, CAPAs, change controls'
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- =====================================================
-- DOCUMENT (Raw Landing)
-- =====================================================
CREATE TABLE IF NOT EXISTS bronze_document (
    -- Source Data
    document_ID STRING,
    document_type STRING,
    document_name STRING,
    document_title STRING,
    document_url STRING,
    gel_image STRING,
    upload_date DATE,

    -- Bronze Audit Columns
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    source_file_name STRING,
    source_system STRING
)
USING DELTA
COMMENT 'Bronze layer for Document dimension - batch records, COAs, SOPs'
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- =====================================================
-- SOURCE_SYSTEM (Raw Landing)
-- =====================================================
CREATE TABLE IF NOT EXISTS bronze_source_system (
    -- Source Data
    source_system_ID STRING,
    source_system_name STRING,
    system_type STRING,
    vendor STRING,
    version STRING,
    is_active BOOLEAN,

    -- Bronze Audit Columns
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    source_file_name STRING,
    source_system STRING
)
USING DELTA
COMMENT 'Bronze layer for Source System dimension - LIMS, MES, ELN, ERP'
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);
