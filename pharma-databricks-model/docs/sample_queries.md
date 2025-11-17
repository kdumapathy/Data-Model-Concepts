## Sample Analytical Queries for Pharmaceutical Data Model

This document provides comprehensive SQL queries for common analytical use cases in pharmaceutical manufacturing and quality control.

## Table of Contents

1. [Material Lineage & Genealogy](#material-lineage--genealogy)
2. [Batch Traceability](#batch-traceability)
3. [Process Execution Analysis](#process-execution-analysis)
4. [Quality Control & Testing](#quality-control--testing)
5. [Stability Studies](#stability-studies)
6. [Deviations & Investigations](#deviations--investigations)
7. [Performance Metrics](#performance-metrics)

---

## Material Lineage & Genealogy

### Q1: Complete Material Lineage (Vector to Protein)

Trace the complete genealogy of a material from expression vector to therapeutic protein.

```sql
WITH RECURSIVE material_lineage AS (
    -- Anchor: Root materials (Expression Vectors)
    SELECT
        material_identity,
        material_ID,
        material_name,
        material_type,
        parent_material_identity,
        lineage_path,
        1 AS level,
        CAST(material_name AS STRING) AS full_lineage_name
    FROM silver.v_dim_material_current
    WHERE parent_material_identity IS NULL
        AND material_type = 'Expression Vector'

    UNION ALL

    -- Recursive: Child materials
    SELECT
        m.material_identity,
        m.material_ID,
        m.material_name,
        m.material_type,
        m.parent_material_identity,
        m.lineage_path,
        ml.level + 1,
        CONCAT(ml.full_lineage_name, ' → ', m.material_name)
    FROM silver.v_dim_material_current m
    INNER JOIN material_lineage ml
        ON m.parent_material_identity = ml.material_identity
)
SELECT
    level AS hierarchy_level,
    material_ID,
    material_type,
    material_name,
    full_lineage_name AS complete_lineage
FROM material_lineage
WHERE material_type IN ('Expression Vector', 'Cell Line', 'Master Cell Bank (MCB)',
                        'Working Cell Bank (WCB)', 'Therapeutic Protein')
ORDER BY level, material_name;
```

### Q2: Find All Descendants of a Specific Material

```sql
WITH RECURSIVE descendants AS (
    -- Anchor: Specific material (e.g., a cell line)
    SELECT
        material_identity,
        material_ID,
        material_name,
        material_type,
        0 AS generation
    FROM silver.v_dim_material_current
    WHERE material_ID = 'CL-2024-0001'  -- Replace with your material ID

    UNION ALL

    -- Recursive: All descendants
    SELECT
        m.material_identity,
        m.material_ID,
        m.material_name,
        m.material_type,
        d.generation + 1
    FROM silver.v_dim_material_current m
    INNER JOIN descendants d
        ON m.parent_material_identity = d.material_identity
)
SELECT
    generation,
    material_ID,
    material_type,
    material_name,
    REPEAT('  ', generation) || material_name AS indented_name
FROM descendants
ORDER BY generation, material_name;
```

---

## Batch Traceability

### Q3: Batch Genealogy with Splits and Merges

Show complete batch genealogy including split and merge relationships.

```sql
SELECT
    child.batch_ID AS child_batch,
    child.batch_status AS child_status,
    child.genealogy_type,
    parent.batch_ID AS parent_batch,
    parent.batch_status AS parent_status,
    bg.contribution_percent,
    bg.relationship_type,
    child.batch_size || ' ' || child.batch_size_uom AS child_quantity,
    parent.batch_size || ' ' || parent.batch_size_uom AS parent_quantity,
    child.mfg_start_date AS child_mfg_date
FROM silver.bridge_batch_genealogy bg
INNER JOIN silver.v_dim_batch_current child
    ON bg.child_batch_identity = child.batch_identity
INNER JOIN silver.v_dim_batch_current parent
    ON bg.parent_batch_identity = parent.batch_identity
WHERE child.batch_ID LIKE 'BATCH-2024-%'
ORDER BY child.mfg_start_date DESC, bg.sequence_order;
```

### Q4: Identify Batch Splits (One Parent → Multiple Children)

```sql
SELECT
    parent.batch_ID AS parent_batch,
    parent.batch_size || ' ' || parent.batch_size_uom AS parent_size,
    COUNT(DISTINCT child.batch_ID) AS num_children,
    STRING_AGG(
        child.batch_ID || ' (' || bg.contribution_percent || '%)',
        ', '
    ) AS child_batches,
    SUM(bg.contribution_percent) AS total_contribution_pct
FROM silver.bridge_batch_genealogy bg
INNER JOIN silver.v_dim_batch_current parent
    ON bg.parent_batch_identity = parent.batch_identity
INNER JOIN silver.v_dim_batch_current child
    ON bg.child_batch_identity = child.batch_identity
GROUP BY parent.batch_ID, parent.batch_size, parent.batch_size_uom
HAVING COUNT(DISTINCT child.batch_ID) > 1
ORDER BY num_children DESC, parent.batch_ID;
```

### Q5: Identify Batch Merges (Multiple Parents → One Child)

```sql
SELECT
    child.batch_ID AS merged_batch,
    child.batch_size || ' ' || child.batch_size_uom AS final_size,
    COUNT(DISTINCT parent.batch_ID) AS num_source_batches,
    STRING_AGG(
        parent.batch_ID || ' (' || bg.contribution_percent || '%)',
        ', '
    ) AS source_batches,
    child.mfg_start_date AS merge_date
FROM silver.bridge_batch_genealogy bg
INNER JOIN silver.v_dim_batch_current parent
    ON bg.parent_batch_identity = parent.batch_identity
INNER JOIN silver.v_dim_batch_current child
    ON bg.child_batch_identity = child.batch_identity
WHERE bg.relationship_type IN ('Input', 'Merge')
GROUP BY child.batch_ID, child.batch_size, child.batch_size_uom, child.mfg_start_date
HAVING COUNT(DISTINCT parent.batch_ID) > 1
ORDER BY child.mfg_start_date DESC;
```

---

## Process Execution Analysis

### Q6: Process Execution Timeline for a Batch

Show chronological process execution for a specific batch.

```sql
SELECT
    f.process_timestamp,
    lp.process_phase,
    lp.process_step_name AS process_step,
    m.material_name AS material_used,
    f.yield_value || ' ' || f.yield_uom AS yield,
    f.viability_percent AS viability_pct,
    f.temperature_celsius AS temp_c,
    f.pH_value,
    f.density_cells_ml AS cell_density,
    CASE
        WHEN n.notification_ID IS NOT NULL THEN '⚠️ ' || n.notification_type
        ELSE 'Normal'
    END AS status
FROM gold.fact_manufacturing_process_results f
INNER JOIN silver.v_dim_batch_current b
    ON f.batch_identity = b.batch_identity
INNER JOIN silver.v_dim_local_process_hierarchy_current lp
    ON f.local_process_identity = lp.local_process_identity
INNER JOIN silver.v_dim_material_current m
    ON f.source_material_identity = m.material_identity
LEFT JOIN silver.dim_notification n
    ON f.notification_identity = n.notification_identity
WHERE b.batch_ID = 'BATCH-2024-00001'  -- Replace with your batch ID
ORDER BY f.process_timestamp;
```

### Q7: Average Process Parameters by Process Step

```sql
SELECT
    lp.process_phase,
    lp.process_step_name,
    COUNT(*) AS execution_count,
    ROUND(AVG(f.yield_value), 2) AS avg_yield,
    ROUND(STDDEV(f.yield_value), 2) AS stddev_yield,
    ROUND(AVG(f.viability_percent), 2) AS avg_viability,
    ROUND(AVG(f.temperature_celsius), 2) AS avg_temperature,
    ROUND(AVG(f.pH_value), 2) AS avg_pH,
    ROUND(AVG(f.density_cells_ml), 0) AS avg_cell_density
FROM gold.fact_manufacturing_process_results f
INNER JOIN silver.v_dim_local_process_hierarchy_current lp
    ON f.local_process_identity = lp.local_process_identity
WHERE f.process_timestamp >= CURRENT_DATE - INTERVAL 90 DAYS
GROUP BY lp.process_phase, lp.process_step_name
ORDER BY lp.process_phase, lp.process_step_name;
```

### Q8: Process Step Duration Analysis

```sql
WITH process_steps AS (
    SELECT
        b.batch_ID,
        lp.process_step_name,
        MIN(f.process_timestamp) AS step_start,
        MAX(f.process_timestamp) AS step_end,
        COUNT(*) AS num_executions
    FROM gold.fact_manufacturing_process_results f
    INNER JOIN silver.v_dim_batch_current b
        ON f.batch_identity = b.batch_identity
    INNER JOIN silver.v_dim_local_process_hierarchy_current lp
        ON f.local_process_identity = lp.local_process_identity
    GROUP BY b.batch_ID, lp.process_step_name
)
SELECT
    process_step_name,
    AVG(TIMESTAMPDIFF(HOUR, step_start, step_end)) AS avg_duration_hours,
    MIN(TIMESTAMPDIFF(HOUR, step_start, step_end)) AS min_duration_hours,
    MAX(TIMESTAMPDIFF(HOUR, step_start, step_end)) AS max_duration_hours,
    COUNT(*) AS num_batches
FROM process_steps
GROUP BY process_step_name
ORDER BY avg_duration_hours DESC;
```

---

## Quality Control & Testing

### Q9: All Test Results for a Batch

```sql
SELECT
    t.test_category,
    t.test_name,
    am.technique AS test_method,
    f.test_result || ' ' || f.test_uom AS result,
    sp.lower_limit || ' - ' || sp.upper_limit || ' ' || sp.uom AS specification,
    f.result_status,
    CASE WHEN f.oos_flag THEN '🔴 OOS' ELSE '✅ Pass' END AS oos_status,
    f.test_timestamp,
    tl.laboratory_name AS tested_by
FROM gold.fact_analytical_results f
INNER JOIN silver.v_dim_batch_current b
    ON f.batch_identity = b.batch_identity
INNER JOIN silver.v_dim_test_current t
    ON f.test_identity = t.test_identity
INNER JOIN silver.v_dim_analytical_method_current am
    ON f.analytical_method_identity = am.analytical_method_identity
INNER JOIN silver.v_dim_test_location_current tl
    ON f.test_location_identity = tl.test_location_identity
LEFT JOIN silver.v_dim_specification_current sp
    ON f.specification_identity = sp.specification_identity
WHERE b.batch_ID = 'BATCH-2024-00001'
ORDER BY f.test_timestamp DESC, t.test_category, t.test_name;
```

### Q10: Test Pass Rates by Category

```sql
SELECT
    t.test_category,
    COUNT(*) AS total_tests,
    SUM(CASE WHEN f.result_status = 'Pass' THEN 1 ELSE 0 END) AS passed,
    SUM(CASE WHEN f.oos_flag THEN 1 ELSE 0 END) AS oos_count,
    ROUND(100.0 * SUM(CASE WHEN f.result_status = 'Pass' THEN 1 ELSE 0 END) / COUNT(*), 2) AS pass_rate_pct,
    ROUND(100.0 * SUM(CASE WHEN f.oos_flag THEN 1 ELSE 0 END) / COUNT(*), 2) AS oos_rate_pct
FROM gold.fact_analytical_results f
INNER JOIN silver.v_dim_test_current t
    ON f.test_identity = t.test_identity
WHERE f.test_timestamp >= CURRENT_DATE - INTERVAL 180 DAYS
GROUP BY t.test_category
ORDER BY total_tests DESC;
```

---

## Stability Studies

### Q11: Stability Test Results Across Timepoints

```sql
SELECT
    b.batch_ID,
    s.study_name,
    c.storage_condition,
    t.test_name,
    tp.timepoint_label,
    tp.timepoint_value || ' ' || tp.timepoint_uom AS timepoint,
    AVG(f.test_result) AS avg_result,
    f.test_uom,
    sp.lower_limit || ' - ' || sp.upper_limit AS spec_range,
    COUNT(CASE WHEN f.oos_flag THEN 1 END) AS oos_count
FROM gold.fact_analytical_results f
INNER JOIN silver.v_dim_batch_current b
    ON f.batch_identity = b.batch_identity
INNER JOIN silver.v_dim_study_current s
    ON f.study_identity = s.study_identity
INNER JOIN silver.v_dim_test_current t
    ON f.test_identity = t.test_identity
INNER JOIN silver.v_dim_timepoint_current tp
    ON f.timepoint_identity = tp.timepoint_identity
INNER JOIN silver.v_dim_condition_current c
    ON f.condition_identity = c.condition_identity
LEFT JOIN silver.v_dim_specification_current sp
    ON f.specification_identity = sp.specification_identity
WHERE s.study_type = 'Stability'
GROUP BY
    b.batch_ID, s.study_name, c.storage_condition,
    t.test_name, tp.timepoint_label, tp.timepoint_value,
    tp.timepoint_uom, f.test_uom, sp.lower_limit, sp.upper_limit
ORDER BY
    b.batch_ID, t.test_name, c.storage_condition, tp.timepoint_value;
```

### Q12: Stability Trending Analysis

Identify degradation trends across timepoints.

```sql
WITH stability_data AS (
    SELECT
        b.batch_ID,
        t.test_name,
        c.storage_condition,
        tp.timepoint_value AS timepoint_months,
        AVG(f.test_result) AS avg_result
    FROM gold.fact_analytical_results f
    INNER JOIN silver.v_dim_batch_current b ON f.batch_identity = b.batch_identity
    INNER JOIN silver.v_dim_test_current t ON f.test_identity = t.test_identity
    INNER JOIN silver.v_dim_timepoint_current tp ON f.timepoint_identity = tp.timepoint_identity
    INNER JOIN silver.v_dim_condition_current c ON f.condition_identity = c.condition_identity
    INNER JOIN silver.v_dim_study_current s ON f.study_identity = s.study_identity
    WHERE s.study_type = 'Stability'
        AND tp.timepoint_uom = 'months'
    GROUP BY b.batch_ID, t.test_name, c.storage_condition, tp.timepoint_value
)
SELECT
    batch_ID,
    test_name,
    storage_condition,
    MAX(CASE WHEN timepoint_months = 0 THEN avg_result END) AS T0,
    MAX(CASE WHEN timepoint_months = 1 THEN avg_result END) AS M1,
    MAX(CASE WHEN timepoint_months = 3 THEN avg_result END) AS M3,
    MAX(CASE WHEN timepoint_months = 6 THEN avg_result END) AS M6,
    MAX(CASE WHEN timepoint_months = 12 THEN avg_result END) AS M12,
    MAX(CASE WHEN timepoint_months = 24 THEN avg_result END) AS M24,
    ROUND((MAX(CASE WHEN timepoint_months = 24 THEN avg_result END) -
           MAX(CASE WHEN timepoint_months = 0 THEN avg_result END)) /
           MAX(CASE WHEN timepoint_months = 0 THEN avg_result END) * 100, 2) AS pct_change_24mo
FROM stability_data
GROUP BY batch_ID, test_name, storage_condition
ORDER BY batch_ID, test_name, storage_condition;
```

---

## Deviations & Investigations

### Q13: All Out-of-Specification (OOS) Results with Investigations

```sql
SELECT
    f.test_timestamp,
    b.batch_ID,
    m.material_name,
    t.test_category,
    t.test_name,
    f.test_result,
    f.test_uom,
    sp.lower_limit,
    sp.upper_limit,
    ABS(f.percent_difference) AS pct_deviation,
    n.notification_ID,
    n.notification_type,
    n.severity_level,
    n.notification_status,
    n.notification_description,
    d.document_title AS investigation_doc
FROM gold.fact_analytical_results f
INNER JOIN silver.v_dim_batch_current b
    ON f.batch_identity = b.batch_identity
INNER JOIN silver.v_dim_material_current m
    ON f.source_material_identity = m.material_identity
INNER JOIN silver.v_dim_test_current t
    ON f.test_identity = t.test_identity
LEFT JOIN silver.v_dim_specification_current sp
    ON f.specification_identity = sp.specification_identity
LEFT JOIN silver.dim_notification n
    ON f.notification_identity = n.notification_identity
LEFT JOIN silver.dim_document d
    ON f.document_identity = d.document_identity
WHERE f.oos_flag = TRUE
ORDER BY f.test_timestamp DESC, n.severity_level;
```

### Q14: Deviation Summary by Type and Severity

```sql
SELECT
    n.notification_type,
    n.event_type,
    n.severity_level,
    n.notification_status,
    COUNT(*) AS total_count,
    COUNT(CASE WHEN n.notification_status = 'Closed' THEN 1 END) AS closed_count,
    COUNT(CASE WHEN n.notification_status = 'Open' THEN 1 END) AS open_count,
    ROUND(AVG(DATEDIFF(CURRENT_DATE, n.notification_date)), 1) AS avg_age_days
FROM silver.dim_notification n
WHERE n.notification_date >= CURRENT_DATE - INTERVAL 365 DAYS
GROUP BY n.notification_type, n.event_type, n.severity_level, n.notification_status
ORDER BY n.severity_level, n.notification_type, n.event_type;
```

---

## Performance Metrics

### Q15: Material Consumption by Batch

```sql
SELECT
    b.batch_ID,
    b.batch_size || ' ' || b.batch_size_uom AS output_quantity,
    m.material_name,
    m.material_type,
    f.usage_type,
    SUM(f.quantity_used) AS total_quantity,
    f.quantity_uom,
    COUNT(*) AS usage_events
FROM gold.fact_batch_material_usage f
INNER JOIN silver.v_dim_batch_current b
    ON f.batch_identity = b.batch_identity
INNER JOIN silver.v_dim_material_lot_current ml
    ON f.material_lot_identity = ml.material_lot_identity
INNER JOIN silver.v_dim_material_current m
    ON ml.material_identity = m.material_identity
WHERE b.batch_ID LIKE 'BATCH-2024-%'
GROUP BY b.batch_ID, b.batch_size, b.batch_size_uom,
         m.material_name, m.material_type, f.usage_type, f.quantity_uom
ORDER BY b.batch_ID, m.material_type, f.usage_type;
```

These queries demonstrate the power and flexibility of the pharmaceutical data model for real-world analytical use cases.
