-- =====================================================
-- Gold Layer - GENEALOGY STAR SCHEMA
-- Fact: BATCH_MATERIAL_USAGE
-- Purpose: Track material consumption and batch traceability
-- Grain: One row per batch-material usage event
-- =====================================================

USE gold;

-- =====================================================
-- FACT_BATCH_MATERIAL_USAGE
-- Genealogy Star Schema - 4 Dimensions + Bridge
-- =====================================================
CREATE TABLE IF NOT EXISTS fact_batch_material_usage (
    -- Surrogate Key
    usage_identity BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    -- Foreign Keys - Genealogy Dimensions (3)
    batch_identity BIGINT NOT NULL,
    material_lot_identity BIGINT NOT NULL,
    transformation_identity BIGINT NOT NULL,
    production_order_identity BIGINT,

    -- Degenerate Dimensions
    bom_item_number STRING,

    -- Measures - Usage Details
    usage_type STRING,  -- Input, Output, Yield_Loss
    quantity_used DECIMAL(18, 4),
    quantity_uom STRING,

    -- Time Dimension
    usage_timestamp TIMESTAMP NOT NULL,
    usage_date DATE GENERATED ALWAYS AS (CAST(usage_timestamp AS DATE)),

    -- Audit Columns
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    source_system STRING,

    -- Foreign Key Constraints
    CONSTRAINT fk_genealogy_batch FOREIGN KEY (batch_identity)
        REFERENCES silver.dim_batch(batch_identity),
    CONSTRAINT fk_genealogy_material_lot FOREIGN KEY (material_lot_identity)
        REFERENCES silver.dim_material_lot(material_lot_identity),
    CONSTRAINT fk_genealogy_transformation FOREIGN KEY (transformation_identity)
        REFERENCES silver.dim_transformation(transformation_identity),
    CONSTRAINT fk_genealogy_production_order FOREIGN KEY (production_order_identity)
        REFERENCES silver.dim_production_order(production_order_identity)
)
USING DELTA
PARTITIONED BY (usage_date)
COMMENT 'Fact Table: Batch Material Usage - material consumption and genealogy tracking'
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- Create indexes for query optimization
CREATE INDEX IF NOT EXISTS idx_fact_genealogy_batch ON fact_batch_material_usage(batch_identity);
CREATE INDEX IF NOT EXISTS idx_fact_genealogy_material_lot ON fact_batch_material_usage(material_lot_identity);
CREATE INDEX IF NOT EXISTS idx_fact_genealogy_transformation ON fact_batch_material_usage(transformation_identity);
CREATE INDEX IF NOT EXISTS idx_fact_genealogy_timestamp ON fact_batch_material_usage(usage_timestamp);
CREATE INDEX IF NOT EXISTS idx_fact_genealogy_usage_type ON fact_batch_material_usage(usage_type);

-- Optimize table for common query patterns
OPTIMIZE fact_batch_material_usage
ZORDER BY (batch_identity, material_lot_identity, usage_date);

-- =====================================================
-- Create Business Views for Common Analysis Patterns
-- =====================================================

-- View: Complete Process Results with Current Dimensions
CREATE OR REPLACE VIEW v_process_results_current AS
SELECT
    f.process_result_identity,
    f.process_execution_id,
    -- Batch
    b.batch_ID,
    b.batch_status,
    b.batch_size,
    b.batch_size_uom,
    -- Sample
    s.sample_ID,
    s.sample_type,
    -- Material
    m.material_ID,
    m.material_name,
    m.material_type,
    -- Manufacturer
    mfr.manufacturer_name,
    mfr.manufacturer_type,
    -- Local Process
    lp.process_step_name AS local_process_step,
    lp.process_phase,
    lp.equipment_ID,
    -- Common Process
    cp.standard_process_name AS common_process_name,
    cp.process_category,
    cp.regulatory_critical,
    -- Measures
    f.yield_value,
    f.yield_uom,
    f.temperature_celsius,
    f.pH_value,
    f.viability_percent,
    f.density_cells_ml,
    f.process_timestamp,
    f.process_date
FROM fact_manufacturing_process_results f
INNER JOIN silver.v_dim_batch_current b ON f.batch_identity = b.batch_identity
LEFT JOIN silver.v_dim_sample_current s ON f.sample_identity = s.sample_identity
INNER JOIN silver.v_dim_material_current m ON f.source_material_identity = m.material_identity
INNER JOIN silver.v_dim_manufacturer_current mfr ON f.manufacturer_identity = mfr.manufacturer_identity
INNER JOIN silver.v_dim_local_process_hierarchy_current lp ON f.local_process_identity = lp.local_process_identity
INNER JOIN silver.v_dim_common_process_hierarchy_current cp ON f.common_process_identity = cp.common_process_identity;

-- View: Complete Analytical Results with Current Dimensions
CREATE OR REPLACE VIEW v_analytical_results_current AS
SELECT
    f.test_result_identity,
    f.test_execution_id,
    -- Batch
    b.batch_ID,
    b.batch_status,
    -- Material
    m.material_ID,
    m.material_name,
    m.material_type,
    -- Test
    t.test_name,
    t.test_category,
    -- Method
    am.method_name,
    am.technique,
    -- Study
    st.study_name,
    st.study_type,
    st.study_phase,
    -- Timepoint
    tp.timepoint_label,
    tp.timepoint_value,
    tp.timepoint_uom,
    -- Condition
    c.storage_condition,
    c.temperature_celsius AS storage_temperature,
    c.relative_humidity,
    -- Measures
    f.test_result,
    f.test_uom,
    f.result_status,
    f.oos_flag,
    f.percent_difference,
    f.test_timestamp,
    f.test_date
FROM fact_analytical_results f
INNER JOIN silver.v_dim_batch_current b ON f.batch_identity = b.batch_identity
INNER JOIN silver.v_dim_material_current m ON f.source_material_identity = m.material_identity
INNER JOIN silver.v_dim_test_current t ON f.test_identity = t.test_identity
INNER JOIN silver.v_dim_analytical_method_current am ON f.analytical_method_identity = am.analytical_method_identity
LEFT JOIN silver.v_dim_study_current st ON f.study_identity = st.study_identity
LEFT JOIN silver.v_dim_timepoint_current tp ON f.timepoint_identity = tp.timepoint_identity
LEFT JOIN silver.v_dim_condition_current c ON f.condition_identity = c.condition_identity;

-- View: Complete Material Usage with Current Dimensions
CREATE OR REPLACE VIEW v_batch_material_usage_current AS
SELECT
    f.usage_identity,
    f.bom_item_number,
    -- Batch
    b.batch_ID,
    b.batch_status,
    -- Material Lot
    ml.lot_number,
    ml.lot_status,
    -- Material Master
    m.material_ID,
    m.material_name,
    m.material_type,
    -- Transformation
    t.transformation_name,
    t.transformation_type,
    -- Production Order
    po.production_order_ID,
    po.order_type,
    po.order_status,
    -- Measures
    f.usage_type,
    f.quantity_used,
    f.quantity_uom,
    f.usage_timestamp,
    f.usage_date
FROM fact_batch_material_usage f
INNER JOIN silver.v_dim_batch_current b ON f.batch_identity = b.batch_identity
INNER JOIN silver.v_dim_material_lot_current ml ON f.material_lot_identity = ml.material_lot_identity
INNER JOIN silver.v_dim_material_current m ON ml.material_identity = m.material_identity
INNER JOIN silver.v_dim_transformation_current t ON f.transformation_identity = t.transformation_identity
LEFT JOIN silver.v_dim_production_order_current po ON f.production_order_identity = po.production_order_identity;
