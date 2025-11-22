# Deployment Guide - Databricks Pharmaceutical Data Platform

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Environment Setup](#environment-setup)
3. [Step-by-Step Deployment](#step-by-step-deployment)
4. [Post-Deployment Validation](#post-deployment-validation)
5. [Production Configuration](#production-configuration)
6. [Disaster Recovery](#disaster-recovery)
7. [Troubleshooting](#troubleshooting)

---

## Pre-Deployment Checklist

### Infrastructure Requirements

- [ ] **Databricks Workspace** provisioned (AWS, Azure, or GCP)
- [ ] **Unity Catalog** enabled on workspace
- [ ] **Cluster** created with:
  - DBR 13.3 LTS or higher
  - Minimum: 2 workers (8 cores, 32GB RAM each)
  - Recommended: Autoscaling 2-8 workers
  - Node type: Standard_DS3_v2 (Azure) or m5.2xlarge (AWS)
- [ ] **Storage** configured:
  - S3 bucket (AWS) or ADLS Gen2 (Azure)
  - Bucket policy for Databricks access
  - Lifecycle policies for cost optimization

### Access and Permissions

- [ ] **Databricks Admin** access for initial setup
- [ ] **Unity Catalog** admin privileges
- [ ] **Service Principal** or **User** with:
  - CREATE CATALOG permission
  - CREATE SCHEMA permission
  - CREATE TABLE permission
- [ ] **Source System** credentials:
  - MES database (JDBC: SQL Server)
  - LIMS database (JDBC: Oracle)
  - EDC API credentials (REST API)

### Network and Connectivity

- [ ] **JDBC drivers** installed on cluster:
  - Microsoft SQL Server JDBC driver
  - Oracle JDBC driver (ojdbc8.jar)
- [ ] **Network access** configured:
  - Firewall rules for database access
  - VPN or PrivateLink for secure connectivity
  - Outbound internet for API calls (if needed)

### Source Data Requirements

- [ ] **Manufacturing System (MES)**:
  - Tables: batch_records, process_data, batch_genealogy
  - Read-only access
  - Watermark columns identified (timestamp, modified_date)

- [ ] **LIMS**:
  - Tables: analytical_results, samples
  - Read-only access
  - Result timestamp for incremental loads

- [ ] **Clinical EDC**:
  - API endpoints documented
  - Authentication method (API key, OAuth)
  - Rate limits understood

---

## Environment Setup

### 1. Install Databricks CLI

```bash
# Install Databricks CLI
pip install databricks-cli

# Configure authentication
databricks configure --token

# Provide:
# - Databricks Host: https://your-workspace.cloud.databricks.com
# - Token: (generate from User Settings → Access Tokens)
```

### 2. Create Secret Scope

```bash
# Create scope for storing credentials
databricks secrets create-scope --scope pharma_platform

# Add database credentials
databricks secrets put --scope pharma_platform --key mes_jdbc_hostname --string-value "mes-db.yourcompany.com"
databricks secrets put --scope pharma_platform --key mes_jdbc_port --string-value "1433"
databricks secrets put --scope pharma_platform --key mes_jdbc_database --string-value "MES_PROD"
databricks secrets put --scope pharma_platform --key mes_jdbc_username --string-value "databricks_reader"
databricks secrets put --scope pharma_platform --key mes_jdbc_password  # Interactive prompt

# Add LIMS credentials
databricks secrets put --scope pharma_platform --key lims_jdbc_hostname --string-value "lims-db.yourcompany.com"
databricks secrets put --scope pharma_platform --key lims_jdbc_port --string-value "1521"
databricks secrets put --scope pharma_platform --key lims_service_name --string-value "LIMS_PROD"
databricks secrets put --scope pharma_platform --key lims_username --string-value "databricks_reader"
databricks secrets put --scope pharma_platform --key lims_password  # Interactive prompt

# Add EDC API credentials
databricks secrets put --scope pharma_platform --key edc_api_url --string-value "https://api.mdsol.com/v1"
databricks secrets put --scope pharma_platform --key edc_api_key  # Interactive prompt

# Verify secrets
databricks secrets list --scope pharma_platform
```

### 3. Configure Cluster Libraries

Add JDBC drivers to cluster:

**Using Cluster UI:**
1. Navigate to Cluster → Libraries → Install New
2. Library Source: Maven
3. Coordinates:
   - SQL Server: `com.microsoft.sqlserver:mssql-jdbc:11.2.3.jre11`
   - Oracle: Upload `ojdbc8.jar` or use Maven coordinates

**Using Cluster API:**
```bash
# Create cluster with libraries
cat > cluster_config.json <<EOF
{
  "cluster_name": "pharma-platform-cluster",
  "spark_version": "13.3.x-scala2.12",
  "node_type_id": "Standard_DS3_v2",
  "autoscale": {
    "min_workers": 2,
    "max_workers": 8
  },
  "libraries": [
    {
      "maven": {
        "coordinates": "com.microsoft.sqlserver:mssql-jdbc:11.2.3.jre11"
      }
    }
  ],
  "spark_conf": {
    "spark.databricks.delta.preview.enabled": "true",
    "spark.databricks.delta.properties.defaults.enableChangeDataFeed": "true"
  }
}
EOF

databricks clusters create --json-file cluster_config.json
```

### 4. Upload Notebooks

```bash
# Navigate to project directory
cd databricks-pharma-pipeline

# Import all notebooks
databricks workspace import_dir \
  . \
  /Workspace/databricks-pharma-pipeline \
  --overwrite

# Verify upload
databricks workspace ls /Workspace/databricks-pharma-pipeline
```

---

## Step-by-Step Deployment

### Phase 1: Unity Catalog Initialization (15 minutes)

**Objective**: Create catalog, schemas, and metadata tables

```python
# 1. Open notebook in Databricks UI:
/Workspace/databricks-pharma-pipeline/00_setup/00_unity_catalog_setup

# 2. Attach to cluster

# 3. Run all cells

# 4. Verify output:
# ✓ Catalog 'pharma_platform' created/verified
# ✓ Schema 'bronze_raw' created
# ✓ Schema 'silver_cdm' created
# ✓ Schema 'gold_analytics' created
# ✓ Schema 'metadata' created
# ✓ Table 'pipeline_execution_log' created
# ✓ Table 'data_quality_metrics' created
# ✓ Table 'data_lineage' created
# ✓ Table 'watermark_tracking' created
```

**Validation**:
```sql
-- Check catalog and schemas
SHOW SCHEMAS IN pharma_platform;

-- Check metadata tables
SHOW TABLES IN pharma_platform.metadata;

-- Verify reference data
SELECT * FROM pharma_platform.silver_cdm.ref_development_phase;
```

### Phase 2: Bronze Layer Deployment (30 minutes)

**Objective**: Ingest raw data from source systems

#### 2.1 Manufacturing Data Ingestion

```python
# Open notebook:
/Workspace/databricks-pharma-pipeline/01_bronze/01_bronze_manufacturing_ingestion

# Configure source query if needed (edit notebook cells)
# Run all cells

# Expected output:
# Rows read from source: 1,234
# ✓ Batch records ingested: 1,234 rows
# ✓ Process data ingested: 45,678 rows
# ✓ Batch genealogy records ingested: 890 rows
```

**Validation**:
```sql
-- Check Bronze tables
SELECT COUNT(*) FROM pharma_platform.bronze_raw.manufacturing_batch_records;
SELECT COUNT(*) FROM pharma_platform.bronze_raw.manufacturing_process_data;

-- Check watermark tracking
SELECT * FROM pharma_platform.metadata.watermark_tracking;

-- Sample data
SELECT * FROM pharma_platform.bronze_raw.manufacturing_batch_records LIMIT 10;
```

#### 2.2 Clinical and LIMS Data Ingestion

```python
# Open notebook:
/Workspace/databricks-pharma-pipeline/01_bronze/02_bronze_clinical_lims_ingestion

# Run all cells

# Expected output:
# ✓ Analytical test results ingested: 5,432 rows
# ✓ QC samples ingested: 1,234 rows
# ✓ Clinical subjects ingested: 789 rows
# ✓ Adverse events ingested: 123 rows
```

### Phase 3: Silver Layer Deployment (45 minutes)

**Objective**: Build Kimball star schema dimensional model

#### 3.1 Create Dimensions (Type 2 SCD)

```python
# Open notebook:
/Workspace/databricks-pharma-pipeline/02_silver/01_silver_dimensions_scd2

# Run all cells

# Expected output:
# ✓ dim_product created: 15 new, 0 updated
# ✓ dim_batch created: 234 new, 0 updated
# ✓ dim_equipment created: 45 new, 0 updated
# ✓ dim_material created: 89 new, 0 updated
# ✓ dim_site created: 5 new, 0 updated
# ✓ dim_test_method created: 25 new, 0 updated
# ✓ dim_study created: 3 new, 0 updated
```

**Validation**:
```sql
-- Check dimension row counts
SELECT COUNT(*) as total, SUM(CASE WHEN is_current THEN 1 ELSE 0 END) as current
FROM pharma_platform.silver_cdm.dim_product;

-- Verify surrogate keys
SELECT product_id, product_code, product_name, is_current
FROM pharma_platform.silver_cdm.dim_product;

-- Check ISA-88 hierarchy in equipment
SELECT equipment_code, equipment_name, site_id, area_id, unit_id
FROM pharma_platform.silver_cdm.dim_equipment
WHERE is_current = true
LIMIT 10;
```

#### 3.2 Create Fact Tables

```python
# Open notebook:
/Workspace/databricks-pharma-pipeline/02_silver/02_silver_fact_tables

# Run all cells

# Expected output:
# ✓ dim_date created: 4,018 dates
# ✓ fact_manufacturing_process created: 45,678 rows
# ✓ fact_analytical_testing created: 5,432 rows
# ✓ fact_batch_genealogy created: 890 rows
# ✓ bridge_batch_materials created: 456 rows
```

**Validation**:
```sql
-- Check fact table row counts
SELECT COUNT(*) FROM pharma_platform.silver_cdm.fact_manufacturing_process;

-- Verify foreign key relationships
SELECT
  COUNT(*) as total_facts,
  COUNT(DISTINCT batch_key) as unique_batches,
  COUNT(DISTINCT equipment_key) as unique_equipment
FROM pharma_platform.silver_cdm.fact_manufacturing_process;

-- Test analytical view
SELECT * FROM pharma_platform.silver_cdm.v_batch_manufacturing_summary LIMIT 10;
```

### Phase 4: Gold Layer Deployment (30 minutes)

**Objective**: Create business-level aggregations

```python
# Open notebook:
/Workspace/databricks-pharma-pipeline/03_gold/01_gold_batch_analytics

# Run all cells

# Expected output:
# ✓ gold_batch_performance_summary: 234 batches
# ✓ gold_quality_kpi_dashboard: 156 aggregated records
# ✓ gold_equipment_oee: 540 equipment-month records
# ✓ gold_material_consumption_forecast: 267 material-month records
```

**Validation**:
```sql
-- Check Gold tables
SELECT COUNT(*) FROM pharma_platform.gold_analytics.gold_batch_performance_summary;

-- Sample KPIs
SELECT
  product_name,
  AVG(first_pass_yield_pct) as avg_fpy,
  AVG(cycle_time_days) as avg_cycle_time,
  COUNT(*) as batch_count
FROM pharma_platform.gold_analytics.gold_batch_performance_summary
GROUP BY product_name;

-- OEE summary
SELECT
  equipment_type,
  AVG(oee_pct) as avg_oee,
  AVG(availability_pct) as avg_availability
FROM pharma_platform.gold_analytics.gold_equipment_oee
GROUP BY equipment_type;
```

### Phase 5: Orchestration Setup (15 minutes)

**Objective**: Set up end-to-end pipeline orchestration

#### 5.1 Test Orchestration Notebook

```python
# Open notebook:
/Workspace/databricks-pharma-pipeline/04_orchestration/orchestrate_pipeline

# Set setup_required = False (since already run)

# Run all cells

# Expected output:
# ========================================
#   PIPELINE COMPLETE
# ========================================
# Final Status: SUCCESS
```

#### 5.2 Create Databricks Job

**Using UI:**
1. Navigate to **Workflows** → **Jobs** → **Create Job**
2. **Job Name**: Pharma Platform Daily Pipeline
3. **Task Configuration**:
   - **Task name**: Run Pipeline
   - **Type**: Notebook
   - **Source**: Workspace
   - **Path**: `/Workspace/databricks-pharma-pipeline/04_orchestration/orchestrate_pipeline`
   - **Cluster**: Select existing cluster or create new
4. **Schedule**:
   - **Trigger**: Scheduled
   - **Schedule**: `0 2 * * *` (Daily at 2:00 AM)
   - **Time zone**: Your timezone
5. **Alerts**:
   - **On Failure**: Email to data engineering team
   - **On Success**: (Optional) Email summary
6. **Save** and **Run Now** to test

**Using Jobs API:**
```bash
cat > job_config.json <<EOF
{
  "name": "Pharma Platform Daily Pipeline",
  "tasks": [{
    "task_key": "run_pipeline",
    "notebook_task": {
      "notebook_path": "/Workspace/databricks-pharma-pipeline/04_orchestration/orchestrate_pipeline"
    },
    "existing_cluster_id": "your-cluster-id"
  }],
  "schedule": {
    "quartz_cron_expression": "0 0 2 * * ?",
    "timezone_id": "America/New_York"
  },
  "email_notifications": {
    "on_failure": ["data-engineering@yourcompany.com"]
  }
}
EOF

databricks jobs create --json-file job_config.json
```

---

## Post-Deployment Validation

### 1. Data Quality Validation

```sql
-- Check DQ metrics
SELECT
  table_name,
  check_name,
  check_result,
  severity,
  check_timestamp
FROM pharma_platform.metadata.data_quality_metrics
ORDER BY check_timestamp DESC
LIMIT 20;

-- Verify no critical failures
SELECT COUNT(*) as critical_failures
FROM pharma_platform.metadata.data_quality_metrics
WHERE check_result = 'FAIL'
  AND severity = 'CRITICAL';
```

### 2. Pipeline Execution Log

```sql
-- Review recent pipeline runs
SELECT
  pipeline_name,
  layer,
  execution_status,
  rows_written,
  execution_start_timestamp,
  execution_end_timestamp
FROM pharma_platform.metadata.pipeline_execution_log
ORDER BY execution_start_timestamp DESC;
```

### 3. Data Lineage Verification

```sql
-- Check lineage for a specific table
SELECT *
FROM pharma_platform.metadata.data_lineage
WHERE target_table = 'fact_manufacturing_process';
```

### 4. Performance Benchmarking

```sql
-- Query performance test
SELECT COUNT(*) FROM pharma_platform.silver_cdm.fact_manufacturing_process;
-- Should complete in < 5 seconds for millions of rows

-- Join performance test
SELECT
  db.batch_number,
  dp.product_name,
  COUNT(*) as process_records
FROM pharma_platform.silver_cdm.fact_manufacturing_process fmp
INNER JOIN pharma_platform.silver_cdm.dim_batch db ON fmp.batch_key = db.batch_id
INNER JOIN pharma_platform.silver_cdm.dim_product dp ON db.product_id = dp.product_id
WHERE db.is_current = true
GROUP BY db.batch_number, dp.product_name
LIMIT 100;
-- Should complete in < 10 seconds
```

---

## Production Configuration

### 1. Enable Table Optimization

```sql
-- Optimize all fact tables
OPTIMIZE pharma_platform.silver_cdm.fact_manufacturing_process;
OPTIMIZE pharma_platform.silver_cdm.fact_analytical_testing;

-- Z-order frequently filtered columns
OPTIMIZE pharma_platform.silver_cdm.fact_manufacturing_process
ZORDER BY (batch_key, date_key);
```

### 2. Configure Auto-Compaction

```sql
-- Enable auto-optimize on all tables
ALTER TABLE pharma_platform.bronze_raw.manufacturing_batch_records
SET TBLPROPERTIES (
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true'
);
```

### 3. Set Up Vacuum Schedule

**Important**: Only run VACUUM after verifying time travel requirements

```sql
-- Vacuum old files (retain 7 days of history)
VACUUM pharma_platform.bronze_raw.manufacturing_batch_records RETAIN 168 HOURS;

-- For production, schedule as separate job to run weekly
```

### 4. Configure Alerts

Set up monitoring alerts for:
- Pipeline failures
- Data quality check failures
- Data freshness violations (data not updated in expected timeframe)
- Disk space thresholds

Use Databricks alerts or integrate with:
- PagerDuty
- Slack
- Email
- Microsoft Teams

---

## Disaster Recovery

### Backup Strategy

1. **Unity Catalog Metadata**: Backed up automatically by Databricks
2. **Delta Lake Data**: Backed up to S3/ADLS with versioning enabled
3. **Notebooks**: Version controlled in Git (recommended)

### Recovery Procedures

#### Scenario 1: Accidental Table Drop

```sql
-- Use Delta Lake time travel to restore
CREATE TABLE pharma_platform.silver_cdm.dim_batch_restored AS
SELECT * FROM pharma_platform.silver_cdm.dim_batch VERSION AS OF 123;

-- Rename back
ALTER TABLE pharma_platform.silver_cdm.dim_batch_restored
RENAME TO pharma_platform.silver_cdm.dim_batch;
```

#### Scenario 2: Corrupted Data Load

```sql
-- Rollback to previous version
RESTORE TABLE pharma_platform.bronze_raw.manufacturing_batch_records
TO VERSION AS OF 100;

-- Or restore to timestamp
RESTORE TABLE pharma_platform.bronze_raw.manufacturing_batch_records
TO TIMESTAMP AS OF '2025-01-01 02:00:00';
```

#### Scenario 3: Complete Environment Rebuild

```bash
# 1. Recreate workspace and cluster
# 2. Re-import notebooks from Git
databricks workspace import_dir ./databricks-pharma-pipeline /Workspace/databricks-pharma-pipeline

# 3. Re-create secret scope and secrets
databricks secrets create-scope --scope pharma_platform
# ... add all secrets

# 4. Run setup notebook
# 5. Data will be restored from S3/ADLS if using external storage location
```

---

## Troubleshooting

### Issue 1: JDBC Connection Failure

**Error**: `java.sql.SQLException: Login failed for user`

**Solution**:
1. Verify credentials in secrets:
   ```bash
   databricks secrets list --scope pharma_platform
   ```
2. Test connectivity from cluster:
   ```python
   import socket
   socket.getaddrinfo("mes-db.yourcompany.com", 1433)
   ```
3. Check firewall rules and VPN connection

### Issue 2: Slow Ingestion Performance

**Symptom**: Bronze ingestion taking > 1 hour for small datasets

**Solutions**:
1. Increase cluster size
2. Adjust JDBC fetch size:
   ```python
   df = spark.read.jdbc(url, table, properties={
       "fetchsize": "10000"  # Increase from default 1000
   })
   ```
3. Use parallel partitioning:
   ```python
   df = spark.read.jdbc(
       url=jdbc_url,
       table=source_query,
       column="batch_id",
       lowerBound=1,
       upperBound=10000,
       numPartitions=10,
       properties=connection_properties
   )
   ```

### Issue 3: Out of Memory Errors

**Error**: `java.lang.OutOfMemoryError: GC overhead limit exceeded`

**Solutions**:
1. Increase driver/executor memory in cluster configuration
2. Reduce partition size:
   ```python
   spark.conf.set("spark.sql.files.maxPartitionBytes", "67108864")  # 64MB
   ```
3. Enable adaptive query execution:
   ```python
   spark.conf.set("spark.sql.adaptive.enabled", "true")
   ```

### Issue 4: Type 2 SCD Not Updating

**Symptom**: Changed records not creating new versions

**Solution**:
1. Verify row hash calculation includes all comparison columns
2. Check business key join conditions
3. Manually test SCD logic:
   ```sql
   -- Check for changes
   SELECT source.*, target.*
   FROM source_df source
   LEFT JOIN target_table target ON source.business_key = target.business_key
   WHERE target.is_current = true
     AND source.row_hash <> target.row_hash;
   ```

---

## Production Checklist

Before going live:

- [ ] All notebooks tested end-to-end
- [ ] Job schedule configured and tested
- [ ] Alerts configured for failures
- [ ] Access controls applied (grants reviewed)
- [ ] Secrets properly configured
- [ ] Cluster auto-scaling configured
- [ ] Table optimization scheduled
- [ ] Backup and recovery tested
- [ ] Documentation updated for operations team
- [ ] Runbook created for common issues
- [ ] Stakeholders trained on accessing Gold layer
- [ ] BI tools connected and tested
- [ ] Performance benchmarks documented
- [ ] Compliance review completed (if required)

---

## Support

For deployment issues:
- Check Databricks workspace event logs
- Review cluster logs
- Query `pipeline_execution_log` for error details
- Check `data_quality_metrics` for validation failures

---

**Document Version**: 1.0
**Last Updated**: 2025-11-22
