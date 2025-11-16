# 🔧 Pharma Data Model - Technical Quick Reference

## For Data Engineers, Database Architects, and BI Developers

---

## Model Architecture at a Glance

```
┌─────────────────────────────────────────────────────────────┐
│           KIMBALL BUS ARCHITECTURE - TWO STARS              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌────────────────────────┐    ┌────────────────────────┐  │
│  │  PROCESS STAR SCHEMA   │    │ ANALYTICAL STAR SCHEMA │  │
│  │   (Manufacturing)      │    │    (Quality/Testing)   │  │
│  │                        │    │                        │  │
│  │  FACT_MANUFACTURING_   │    │  FACT_TEST_RESULT      │  │
│  │  PROCESS_RESULT        │    │                        │  │
│  │                        │    │                        │  │
│  └────────────────────────┘    └────────────────────────┘  │
│              │                            │                 │
│              └──────────┬─────────────────┘                 │
│                         │                                   │
│             ┌───────────▼──────────────┐                    │
│             │  8 CONFORMED DIMENSIONS  │                    │
│             │  + Batch Genealogy       │                    │
│             └──────────────────────────┘                    │
└─────────────────────────────────────────────────────────────┘
```

---

## Core Tables Reference

### Fact Tables (2)

| Table | Grain | Typical Size |
|-------|-------|--------------|
| `FACT_MANUFACTURING_PROCESS_RESULT` | One row per process execution event | 10M-100M rows/year |
| `FACT_TEST_RESULT` | One row per analyte per test per sample | 50M-500M rows/year |

### Conformed Dimensions (8)

| Dimension | Business Key | SCD Type | Typical Rows |
|-----------|--------------|----------|--------------|
| `DIM_MATERIAL` | material_id | Type 2 | 10K-50K |
| `DIM_BATCH` | batch_id | Type 1 | 100K-1M |
| `DIM_SAMPLE` | sample_id | Type 1 | 500K-5M |
| `DIM_MANUFACTURER` | manufacturer_code | Type 2 | 100-500 |
| `DIM_SPECIFICATION` | specification_id | Type 2 | 1K-10K |
| `DIM_NOTIFICATION` | notification_id | Type 1 | 10K-100K |
| `DIM_DOCUMENT` | document_id | Type 1 | 50K-500K |
| `DIM_SOURCE_SYSTEM` | source_system_code | Type 2 | 10-50 |

### Process-Specific Dimensions (2)

| Dimension | Purpose | Typical Rows |
|-----------|---------|--------------|
| `DIM_PROCESS_OPERATION` | Manufacturing step taxonomy | 500-2K |
| `DIM_EQUIPMENT` | Bioreactors, columns, filters | 1K-10K |

### Analytical-Specific Dimensions (2)

| Dimension | Purpose | Typical Rows |
|-----------|---------|--------------|
| `DIM_TEST_METHOD` | Analytical procedures | 500-5K |
| `DIM_TIME` | Calendar, fiscal periods | 3.7K (10 years daily) |

### Genealogy Tables (5)

| Table | Purpose | Pattern |
|-------|---------|---------|
| `DIM_BATCH` | Parent-child via self-join | `parent_batch_key → batch_key` |
| `BRIDGE_BATCH_GENEALOGY` | Many-to-many batch relationships | Junction table |
| `DIM_MATERIAL_LOT` | Supplier lot tracking | Links to `DIM_MATERIAL` |
| `DIM_TRANSFORMATION` | Material lineage | Self-join on `DIM_MATERIAL` |
| `FACT_BATCH_MATERIAL_USAGE` | Bill of materials | Links batches to material lots |

---

## Key Design Patterns

### Pattern 1: Self-Join for Hierarchies

```sql
-- Batch genealogy: Find all children of a parent batch
SELECT 
    parent.batch_id as parent_batch,
    child.batch_id as child_batch,
    child.genealogy_type
FROM DIM_BATCH parent
LEFT JOIN DIM_BATCH child 
    ON parent.batch_key = child.parent_batch_key
WHERE parent.batch_id = 'B-2024-001';
```

### Pattern 2: Material Lineage (Vector → WCB)

```sql
-- Trace WCB back to expression vector
SELECT 
    vector.material_id as vector,
    cell_line.material_id as cell_line,
    mcb.material_id as mcb,
    wcb.material_id as wcb
FROM DIM_MATERIAL wcb
LEFT JOIN DIM_MATERIAL mcb 
    ON wcb.parent_material_key = mcb.material_key
LEFT JOIN DIM_MATERIAL cell_line 
    ON mcb.parent_material_key = cell_line.material_key
LEFT JOIN DIM_MATERIAL vector 
    ON cell_line.parent_material_key = vector.material_key
WHERE wcb.material_id = 'WCB-2024-Q1-A';
```

### Pattern 3: Bridge Table for Many-to-Many

```sql
-- Find all batches that contributed to a pooled batch
SELECT 
    pooled.batch_id as pooled_batch,
    source.batch_id as source_batch,
    bridge.contribution_percentage
FROM DIM_BATCH pooled
JOIN BRIDGE_BATCH_GENEALOGY bridge 
    ON pooled.batch_key = bridge.target_batch_key
JOIN DIM_BATCH source 
    ON bridge.source_batch_key = source.batch_key
WHERE pooled.batch_id = 'B-2024-POOL-001';
```

### Pattern 4: Star Schema Query (Typical BI)

```sql
-- Manufacturing KPIs by month and material type
SELECT 
    t.calendar_year_month,
    m.material_type,
    COUNT(DISTINCT b.batch_id) as batch_count,
    AVG(f.yield_value) as avg_yield,
    SUM(CASE WHEN n.severity = 'Critical' THEN 1 ELSE 0 END) as critical_deviations
FROM FACT_MANUFACTURING_PROCESS_RESULT f
JOIN DIM_BATCH b ON f.batch_key = b.batch_key
JOIN DIM_MATERIAL m ON f.source_material_key = m.material_key
JOIN DIM_TIME t ON f.process_timestamp::date = t.full_date
LEFT JOIN DIM_NOTIFICATION n ON f.notification_key = n.notification_key
WHERE t.calendar_year = 2024
GROUP BY 1, 2
ORDER BY 1, 2;
```

---

## Naming Conventions

### Tables
- Fact tables: `FACT_<domain>_<grain>` (e.g., `FACT_MANUFACTURING_PROCESS_RESULT`)
- Dimensions: `DIM_<entity>` (e.g., `DIM_BATCH`)
- Bridges: `BRIDGE_<relationship>` (e.g., `BRIDGE_BATCH_GENEALOGY`)

### Columns
- Primary key: `<table_name>_key` (e.g., `batch_key`)
- Foreign key: `<referenced_table>_key` (e.g., `batch_key` in fact table)
- Business key: `<entity>_id` (e.g., `batch_id`)
- Attributes: `<attribute_name>` (e.g., `batch_size`, `material_type`)

### Data Types (Standard)
- Surrogate keys: `BIGINT` (allows 9.2 quintillion records)
- Timestamps: `TIMESTAMP` (UTC, ISO 8601 format)
- Amounts: `DECIMAL(18,4)` (precision for calculations)
- Codes: `VARCHAR(50)` (generous for business keys)
- Descriptions: `VARCHAR(500)` or `TEXT`

---

## Performance Optimization

### Partitioning Strategy

```sql
-- Fact tables by time (monthly)
CREATE TABLE FACT_MANUFACTURING_PROCESS_RESULT (
    ...
) PARTITIONED BY (process_month INT)  -- YYYYMM format

-- Dimensions by SCD effective date (if Type 2)
CREATE TABLE DIM_MATERIAL (
    ...
) PARTITIONED BY (effective_year INT)
```

### Indexing Recommendations

```sql
-- Fact table indexes
CREATE INDEX idx_fact_mfg_batch ON FACT_MANUFACTURING_PROCESS_RESULT(batch_key);
CREATE INDEX idx_fact_mfg_material ON FACT_MANUFACTURING_PROCESS_RESULT(source_material_key);
CREATE INDEX idx_fact_mfg_time ON FACT_MANUFACTURING_PROCESS_RESULT(process_timestamp);

-- Dimension indexes
CREATE UNIQUE INDEX idx_dim_batch_id ON DIM_BATCH(batch_id);
CREATE INDEX idx_dim_batch_parent ON DIM_BATCH(parent_batch_key);
CREATE INDEX idx_dim_material_parent ON DIM_MATERIAL(parent_material_key);
```

### Databricks Optimizations

```sql
-- Delta Lake optimization
OPTIMIZE FACT_MANUFACTURING_PROCESS_RESULT
    ZORDER BY (batch_key, process_timestamp);

-- Vacuum old versions (keep 30 days for time travel)
VACUUM FACT_MANUFACTURING_PROCESS_RESULT RETAIN 720 HOURS;
```

---

## ETL Best Practices

### Load Pattern: Incremental Updates

```python
# Databricks/PySpark example
from pyspark.sql.functions import current_timestamp

# Incremental load with watermark
max_timestamp = spark.sql("""
    SELECT MAX(load_timestamp) 
    FROM FACT_MANUFACTURING_PROCESS_RESULT
""").collect()[0][0]

new_data = (
    spark.read
    .format("delta")
    .load("s3://raw-zone/mes_data/")
    .filter(f"source_timestamp > '{max_timestamp}'")
    .withColumn("load_timestamp", current_timestamp())
)

new_data.write.format("delta").mode("append").save("s3://curated-zone/FACT_MANUFACTURING_PROCESS_RESULT/")
```

### SCD Type 2 Pattern

```sql
-- Update dimension with SCD Type 2
MERGE INTO DIM_MATERIAL target
USING (
    SELECT * FROM staging.material_updates
) source
ON target.material_id = source.material_id 
   AND target.is_current = TRUE
WHEN MATCHED AND target.material_description <> source.material_description THEN
    UPDATE SET 
        is_current = FALSE,
        end_date = CURRENT_DATE
WHEN NOT MATCHED THEN
    INSERT (material_key, material_id, material_description, 
            is_current, start_date, end_date)
    VALUES (nextval('material_key_seq'), 
            source.material_id, 
            source.material_description,
            TRUE, CURRENT_DATE, '9999-12-31');
```

---

## Data Quality Checks

### Critical Validations

```sql
-- 1. Referential Integrity
SELECT COUNT(*) as orphan_records
FROM FACT_MANUFACTURING_PROCESS_RESULT f
LEFT JOIN DIM_BATCH b ON f.batch_key = b.batch_key
WHERE b.batch_key IS NULL;

-- 2. Completeness (critical fields)
SELECT 
    COUNT(*) as total_rows,
    COUNT(batch_key) as batch_key_count,
    COUNT(process_timestamp) as timestamp_count,
    (COUNT(*) - COUNT(batch_key)) as missing_batch_key
FROM FACT_MANUFACTURING_PROCESS_RESULT
WHERE process_timestamp >= CURRENT_DATE - 1;

-- 3. Duplicate Detection
SELECT batch_id, COUNT(*) as duplicate_count
FROM DIM_BATCH
GROUP BY batch_id
HAVING COUNT(*) > 1;

-- 4. Business Rule: Yield must be 0-100%
SELECT COUNT(*) as invalid_yield_records
FROM FACT_MANUFACTURING_PROCESS_RESULT
WHERE yield_value < 0 OR yield_value > 100;
```

---

## Platform-Specific Notes

### Databricks Delta Lake

```python
# Time travel queries
df = spark.read.format("delta").option("versionAsOf", 5).load("/delta/fact_table")

# Audit history
spark.sql("DESCRIBE HISTORY delta.`/delta/fact_table`").show()

# Ensure ACID compliance
spark.conf.set("spark.databricks.delta.properties.defaults.enableChangeDataFeed", "true")
```

### Trino Federated Queries

```sql
-- Query across multiple catalogs
SELECT 
    mes.batch_id,
    lims.test_result,
    erp.material_cost
FROM mes.manufacturing.batches mes
JOIN lims.quality.test_results lims 
    ON mes.batch_id = lims.batch_id
JOIN erp.finance.material_costs erp 
    ON mes.material_id = erp.material_id;
```

### AWS Redshift

```sql
-- Distribution keys for star schema
CREATE TABLE FACT_MANUFACTURING_PROCESS_RESULT (
    ...
) DISTKEY(batch_key)
SORTKEY(process_timestamp);

CREATE TABLE DIM_BATCH (
    ...
) DISTSTYLE ALL;  -- Broadcast small dimensions
```

---

## Common Query Patterns

### 1. Batch Traceability (Forward)
```sql
-- All downstream batches from a parent
WITH RECURSIVE batch_tree AS (
    SELECT batch_key, batch_id, parent_batch_key, 1 as level
    FROM DIM_BATCH
    WHERE batch_id = 'B-2024-PARENT'
    
    UNION ALL
    
    SELECT b.batch_key, b.batch_id, b.parent_batch_key, bt.level + 1
    FROM DIM_BATCH b
    JOIN batch_tree bt ON b.parent_batch_key = bt.batch_key
)
SELECT * FROM batch_tree;
```

### 2. Material Genealogy (Backward)
```sql
-- Trace material back to origin
WITH RECURSIVE material_lineage AS (
    SELECT material_key, material_id, parent_material_key, 0 as hierarchy_level
    FROM DIM_MATERIAL
    WHERE material_id = 'WCB-2024-001'
    
    UNION ALL
    
    SELECT m.material_key, m.material_id, m.parent_material_key, ml.hierarchy_level + 1
    FROM DIM_MATERIAL m
    JOIN material_lineage ml ON m.material_key = ml.parent_material_key
)
SELECT * FROM material_lineage ORDER BY hierarchy_level DESC;
```

### 3. Quality Trending
```sql
-- Statistical process control
SELECT 
    t.calendar_year_week,
    m.material_id,
    AVG(tr.numeric_result) as mean_value,
    STDDEV(tr.numeric_result) as std_dev,
    AVG(tr.numeric_result) - 3 * STDDEV(tr.numeric_result) as lcl,
    AVG(tr.numeric_result) + 3 * STDDEV(tr.numeric_result) as ucl
FROM FACT_TEST_RESULT tr
JOIN DIM_TIME t ON tr.test_date = t.full_date
JOIN DIM_BATCH b ON tr.batch_key = b.batch_key
JOIN DIM_MATERIAL m ON b.material_key = m.material_key
WHERE tr.analyte_name = 'Potency'
  AND t.calendar_year = 2024
GROUP BY 1, 2
ORDER BY 1;
```

---

## Monitoring & Alerting

### Key Metrics to Track

```sql
-- ETL job monitoring
SELECT 
    table_name,
    load_date,
    rows_inserted,
    rows_updated,
    rows_failed,
    load_duration_seconds
FROM ETL_JOB_LOG
WHERE load_date >= CURRENT_DATE - 7
ORDER BY load_date DESC;

-- Data freshness
SELECT 
    'FACT_MANUFACTURING' as table_name,
    MAX(process_timestamp) as latest_data,
    DATEDIFF('hour', MAX(process_timestamp), CURRENT_TIMESTAMP) as hours_old
FROM FACT_MANUFACTURING_PROCESS_RESULT
UNION ALL
SELECT 
    'FACT_TEST_RESULT',
    MAX(test_timestamp),
    DATEDIFF('hour', MAX(test_timestamp), CURRENT_TIMESTAMP)
FROM FACT_TEST_RESULT;
```

---

## Security & Compliance

### Row-Level Security Example

```sql
-- Databricks Unity Catalog
CREATE ROW ACCESS POLICY site_access_policy
AS (site_code STRING)
RETURNS BOOLEAN
RETURN 
    CASE 
        WHEN IS_MEMBER('site_admin') THEN TRUE
        WHEN CURRENT_USER() = 'site_user@company.com' 
            AND site_code = 'SITE-001' THEN TRUE
        ELSE FALSE
    END;

ALTER TABLE FACT_MANUFACTURING_PROCESS_RESULT
SET ROW FILTER site_access_policy ON (manufacturer_code);
```

### Audit Trail

```sql
-- Track all changes with 21 CFR Part 11 compliance
CREATE TABLE AUDIT_LOG (
    audit_key BIGINT PRIMARY KEY,
    table_name VARCHAR(100),
    record_key BIGINT,
    action_type VARCHAR(20),  -- INSERT, UPDATE, DELETE
    changed_by VARCHAR(100),
    changed_at TIMESTAMP,
    old_values TEXT,  -- JSON
    new_values TEXT,  -- JSON
    reason_for_change VARCHAR(500)
);
```

---

## Testing Checklist

- [ ] Unit tests for all ETL transformations
- [ ] Data quality rules automated
- [ ] Referential integrity validated
- [ ] Performance benchmarks met (<5 sec for 95% queries)
- [ ] SCD Type 2 logic tested
- [ ] Genealogy queries validated
- [ ] BI reports tested with production-like volumes
- [ ] Security policies enforced
- [ ] Disaster recovery tested
- [ ] Documentation updated

---

## Troubleshooting

### Slow Queries
1. Check EXPLAIN plan
2. Verify partition pruning
3. Add missing indexes
4. Update table statistics
5. Consider materialized views

### Data Quality Issues
1. Check source system data
2. Review ETL error logs
3. Validate business rules
4. Check for schema drift
5. Review recent changes

### Missing Data
1. Verify source system availability
2. Check ETL job status
3. Review incremental load logic
4. Validate date/time filters
5. Check for deletions in source

---

**Quick Links:**
- Full Documentation: `Pharma_Data_Model_Complete_Lifecycle.html`
- Diagram Files: `Pharma_Data_Model_Diagram_1-9.html`
- README: `README_Pharma_Data_Model.md`

**Version:** 1.0 Baseline | **Last Updated:** November 16, 2025
