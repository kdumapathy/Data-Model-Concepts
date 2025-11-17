# Deployment Guide - Pharmaceutical Data Model for Databricks

Complete step-by-step guide to deploy the pharmaceutical data model to Databricks.

## Prerequisites

### 1. Databricks Account

- **Community Edition** (Free): Limited to single-node clusters, no Unity Catalog
- **Standard/Premium**: Recommended for production use
- **Account Creation**: Visit [databricks.com/try-databricks](https://databricks.com/try-databricks)

### 2. Required Tools

```bash
# Python 3.10+
python --version

# Git
git --version

# Databricks CLI (optional for manual deployment)
pip install databricks-cli
```

### 3. Access Requirements

- Databricks workspace URL
- Personal Access Token (PAT) with permissions:
  - Workspace access
  - Cluster create/edit
  - SQL access
  - Jobs run

---

## Deployment Options

### Option A: Automated Deployment (Recommended)

Uses GitHub Actions to automatically deploy on code push.

### Option B: Manual Deployment

Step-by-step manual deployment using Databricks UI and CLI.

---

## Option A: Automated Deployment via GitHub Actions

### Step 1: Configure GitHub Repository

1. **Fork or Clone Repository**

```bash
git clone https://github.com/yourusername/pharma-databricks-model.git
cd pharma-databricks-model
```

2. **Configure GitHub Secrets**

Navigate to: Repository → Settings → Secrets and variables → Actions

Add two secrets:

| Secret Name | Value | Example |
|------------|-------|---------|
| `DATABRICKS_HOST` | Your Databricks workspace URL | `https://adb-1234567890123456.7.azuredatabricks.net` |
| `DATABRICKS_TOKEN` | Personal Access Token | `dapi_1234567890abcdef` |

**To generate a PAT:**
1. Log into Databricks workspace
2. Click user icon → Settings → Developer
3. Access tokens → Generate new token
4. Copy token (only shown once!)

### Step 2: Trigger Deployment

**Push to main branch:**

```bash
git add .
git commit -m "Initial deployment [generate-data]"
git push origin main
```

**Or trigger manually:**
1. Go to Actions tab in GitHub
2. Select "Databricks Pharmaceutical Data Model Deployment"
3. Click "Run workflow"
4. Select environment (dev/staging/prod)
5. Click "Run workflow"

### Step 3: Monitor Deployment

1. Navigate to Actions tab
2. Click on the running workflow
3. Monitor progress through steps:
   - ✅ Validate
   - ✅ Deploy DDL
   - ✅ Deploy Notebooks
   - ✅ Generate Data (if triggered)
   - ✅ Validate Deployment

### Step 4: Verify in Databricks

1. Log into Databricks workspace
2. Check uploaded files:
   - **DBFS**: `/pharma-model/ddl/`, `/pharma-model/src/`
   - **Workspace**: `/pharma-model/notebooks/`

---

## Option B: Manual Deployment

### Step 1: Create Databricks Cluster

1. **Navigate to Compute** in Databricks workspace
2. **Click "Create Cluster"**
3. **Configure cluster:**

```
Cluster Name: pharma-model-cluster
Cluster Mode: Single Node (Community) or Standard (Premium)
Databricks Runtime: 13.3 LTS or higher
Node Type: Standard_DS3_v2 (or available)
Terminate after: 120 minutes of inactivity
```

4. **Click "Create Cluster"**
5. **Wait for cluster to start** (green "Running" status)

### Step 2: Upload DDL Scripts

#### Via Databricks CLI:

```bash
# Configure CLI
databricks configure --token

# Inputs:
# - Host: https://your-workspace.azuredatabricks.net
# - Token: dapi_your_token_here

# Upload DDL scripts
databricks fs cp -r ./ddl/ dbfs:/pharma-model/ddl/ --overwrite

# Upload Python scripts
databricks fs cp -r ./src/ dbfs:/pharma-model/src/ --overwrite

# Verify upload
databricks fs ls dbfs:/pharma-model/
```

#### Via Databricks UI:

1. Navigate to **Data** → **DBFS**
2. Create directory: `/pharma-model/ddl/`
3. Upload files from `./ddl/bronze/`, `./ddl/silver/`, `./ddl/gold/`
4. Repeat for `/pharma-model/src/`

### Step 3: Execute DDL Scripts

#### Method 1: SQL Editor (Recommended)

1. **Navigate to SQL Editor** (SQL Persona or SQL Warehouse)

2. **Create Bronze Schema:**
```sql
-- Execute in order:
-- File: ddl/bronze/01_create_bronze_schema.sql
CREATE SCHEMA IF NOT EXISTS bronze
COMMENT 'Bronze layer for raw data landing'
LOCATION 'dbfs:/pharma-model/bronze';

-- File: ddl/bronze/02_create_bronze_conformed_dimensions.sql
-- Copy and execute entire file...

-- Continue with remaining bronze scripts...
```

3. **Create Silver Schema:**
```sql
-- Execute silver DDL scripts in order (01 through 06)
```

4. **Create Gold Schema:**
```sql
-- Execute gold DDL scripts in order (01 through 04)
```

#### Method 2: Databricks Notebook

1. **Create New Notebook** in Databricks workspace
2. **Language: SQL**
3. **Paste and run scripts** in order

```sql
%sql
-- Bronze Schema
CREATE SCHEMA IF NOT EXISTS bronze...

-- Silver Schema
CREATE SCHEMA IF NOT EXISTS silver...

-- Gold Schema
CREATE SCHEMA IF NOT EXISTS gold...
```

### Step 4: Upload and Run Data Generation Notebooks

1. **Import Notebooks:**
   - Workspace → Create → Import
   - Upload `/src/main_data_generation.py`

2. **Attach to Cluster:**
   - Click notebook name → Attach to: pharma-model-cluster

3. **Configure Environment Variables** (in notebook cell 1):
```python
import os
os.environ["SAMPLE_DATA_SEED"] = "42"
os.environ["NUM_MATERIALS"] = "200"
os.environ["NUM_BATCHES"] = "150"
os.environ["NUM_SAMPLES"] = "500"
os.environ["NUM_PROCESS_RESULTS"] = "10000"
os.environ["NUM_ANALYTICAL_RESULTS"] = "10000"
os.environ["NUM_GENEALOGY_RECORDS"] = "8000"
```

4. **Run All Cells:**
   - Click "Run All"
   - Monitor progress in output

5. **Expected Output:**
```
✓ Generated 5 source systems
✓ Generated 200 materials with lineage hierarchy
  - Vectors: 10
  - Cell Lines: 20
  - MCBs: 30
  - WCBs: 50
  - Raw Materials: 90
✓ Generated 150 batches
✓ Generated 500 samples
...
```

### Step 5: Verify Data

1. **Navigate to SQL Editor**
2. **Run verification queries:**

```sql
-- Check table counts
SELECT 'bronze_material' AS table_name, COUNT(*) AS row_count
FROM bronze.bronze_material
UNION ALL
SELECT 'dim_batch', COUNT(*) FROM silver.dim_batch
UNION ALL
SELECT 'fact_manufacturing_process_results', COUNT(*)
FROM gold.fact_manufacturing_process_results;

-- Sample data from each layer
SELECT * FROM bronze.bronze_material LIMIT 10;
SELECT * FROM silver.v_dim_material_current LIMIT 10;
SELECT * FROM gold.v_process_results_current LIMIT 10;
```

### Step 6: Run Sample Queries

1. **Open** `/docs/sample_queries.md`
2. **Copy queries** into SQL Editor
3. **Execute** to verify model functionality

Example:
```sql
-- Material Lineage
WITH RECURSIVE material_lineage AS (
    SELECT material_identity, material_ID, material_name,
           material_type, parent_material_identity, 1 AS level
    FROM silver.v_dim_material_current
    WHERE parent_material_identity IS NULL
    UNION ALL
    SELECT m.material_identity, m.material_ID, m.material_name,
           m.material_type, m.parent_material_identity, ml.level + 1
    FROM silver.v_dim_material_current m
    INNER JOIN material_lineage ml
        ON m.parent_material_identity = ml.material_identity
)
SELECT level, material_ID, material_type, material_name
FROM material_lineage
ORDER BY level, material_name;
```

---

## Data Quality Checks

After deployment, run these validation queries:

```sql
-- 1. Check for orphaned records (referential integrity)
SELECT 'Batches without source material' AS check_name, COUNT(*) AS issues
FROM silver.dim_batch b
LEFT JOIN silver.dim_material m
    ON b.source_material_identity = m.material_identity
WHERE b.source_material_identity IS NOT NULL
    AND m.material_identity IS NULL

UNION ALL

-- 2. Verify SCD Type 2 current flags
SELECT 'Materials with multiple current flags', COUNT(*)
FROM (
    SELECT material_ID, COUNT(*) AS current_count
    FROM silver.dim_material
    WHERE current_flag = TRUE
    GROUP BY material_ID
    HAVING COUNT(*) > 1
) issues

UNION ALL

-- 3. Check for null critical columns
SELECT 'Batches with null batch_ID', COUNT(*)
FROM silver.dim_batch
WHERE batch_ID IS NULL OR batch_ID = '';
```

---

## Troubleshooting

### Issue: "Table not found" error

**Solution:**
- Verify schema exists: `SHOW SCHEMAS;`
- Check table exists: `SHOW TABLES IN bronze;`
- Re-run DDL scripts if missing

### Issue: "Permission denied" error

**Solution:**
- Verify PAT has correct permissions
- Check cluster has access to DBFS location
- Ensure SQL warehouse has access to schema

### Issue: Data generation notebook fails

**Solution:**
- Verify cluster is running
- Check Python version (requires 3.10+)
- Install required libraries: `%pip install faker python-dateutil`
- Check environment variables are set

### Issue: Slow query performance

**Solution:**
```sql
-- Optimize tables
OPTIMIZE bronze.bronze_material;
OPTIMIZE silver.dim_material;
OPTIMIZE gold.fact_manufacturing_process_results ZORDER BY (batch_identity);

-- Analyze tables
ANALYZE TABLE silver.dim_material COMPUTE STATISTICS;
ANALYZE TABLE gold.fact_manufacturing_process_results COMPUTE STATISTICS;
```

---

## Post-Deployment Configuration

### 1. Create Views for Analysts

```sql
-- Simplified view for analysts
CREATE OR REPLACE VIEW gold.v_batch_summary AS
SELECT
    b.batch_ID,
    b.batch_status,
    m.material_name,
    b.batch_size || ' ' || b.batch_size_uom AS quantity,
    b.mfg_start_date,
    b.mfg_end_date,
    COUNT(DISTINCT s.sample_ID) AS num_samples,
    SUM(CASE WHEN ar.oos_flag THEN 1 ELSE 0 END) AS oos_count
FROM silver.v_dim_batch_current b
INNER JOIN silver.v_dim_material_current m
    ON b.source_material_identity = m.material_identity
LEFT JOIN silver.v_dim_sample_current s
    ON s.sample_ID LIKE CONCAT(b.batch_ID, '%')
LEFT JOIN gold.fact_analytical_results ar
    ON ar.batch_identity = b.batch_identity
GROUP BY b.batch_ID, b.batch_status, m.material_name,
         b.batch_size, b.batch_size_uom, b.mfg_start_date, b.mfg_end_date;
```

### 2. Set Up Scheduled Jobs (Optional)

1. Navigate to **Workflows** → **Jobs**
2. Create job: "Pharma Model Data Refresh"
3. Add tasks:
   - Bronze ingestion
   - Silver transformation
   - Gold aggregation
4. Schedule: Daily at 2 AM UTC

### 3. Enable Change Data Feed (CDC)

Already enabled via table properties in DDL:
```sql
'delta.enableChangeDataFeed' = 'true'
```

Query changes:
```sql
SELECT * FROM table_changes('silver.dim_batch', 0) -- version 0 onwards
WHERE _change_type IN ('insert', 'update_postimage');
```

---

## Next Steps

1. ✅ **Explore Sample Queries** - `/docs/sample_queries.md`
2. ✅ **Review Data Dictionary** - `/docs/data_dictionary.md`
3. ✅ **Create Dashboards** - Use Databricks SQL dashboards
4. ✅ **Integrate with BI Tools** - Connect Tableau, Power BI, etc.
5. ✅ **Customize Data Generation** - Modify `/src/main_data_generation.py`
6. ✅ **Add Business Logic** - Create additional views and procedures

---

## Support

For issues or questions:
- GitHub Issues: [Create an issue](https://github.com/yourusername/pharma-databricks-model/issues)
- Documentation: Review `/docs/` directory
- Sample Queries: `/docs/sample_queries.md`

---

**Deployment Complete! 🎉**

Your pharmaceutical data model is now ready for analysis and reporting.
