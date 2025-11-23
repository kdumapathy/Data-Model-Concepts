# Pipeline Execution Order - Quick Reference

## 🚀 Option 1: One-Click Execution (Recommended)

Run this single notebook to execute the complete pipeline:

```
/Workspace/Users/kd.umapathy@gmail.com/Data-Model-Concepts/databricks-pharma-pipeline/RUN_ALL_SIMPLE
```

**How to use:**
1. Attach the notebook to a running cluster
2. Click **"Run All"** button
3. Monitor progress (approx. 10-15 minutes)
4. All layers (Bronze → Silver → Gold) will be created automatically

---

## 📋 Option 2: Manual Step-by-Step Execution

If you prefer to run each step individually, execute these notebooks in order:

### Step 1: Setup (First-time only)
```
/Workspace/Users/kd.umapathy@gmail.com/Data-Model-Concepts/databricks-pharma-pipeline/00_setup/00_unity_catalog_setup
```
**What it does:** Creates catalog `pharma_platform`, schemas (bronze_raw, silver_cdm, gold_analytics, metadata), and metadata tables

**Runtime:** ~2 minutes

**Skip this if:** Unity Catalog already set up

---

### Step 2: Bronze Layer - Manufacturing Data
```
/Workspace/Users/kd.umapathy@gmail.com/Data-Model-Concepts/databricks-pharma-pipeline/01_bronze/01_bronze_manufacturing_ingestion_DEMO
```
**What it does:**
- Generates 50 synthetic batches
- Creates 21,600+ process data points (temperature, pH, DO, pressure, etc.)
- Generates batch genealogy for traceability

**Runtime:** ~3 minutes

**Output Tables:**
- `pharma_platform.bronze_raw.manufacturing_batch_records`
- `pharma_platform.bronze_raw.manufacturing_process_data`
- `pharma_platform.bronze_raw.batch_genealogy`

---

### Step 3: Bronze Layer - Clinical & LIMS Data
```
/Workspace/Users/kd.umapathy@gmail.com/Data-Model-Concepts/databricks-pharma-pipeline/01_bronze/02_bronze_clinical_lims_ingestion_DEMO
```
**What it does:**
- Generates 200 analytical test results (95% pass rate)
- Creates 100 QC samples
- Generates 150 clinical trial subjects (CDISC-aligned)
- Creates ~60 adverse events with MedDRA coding

**Runtime:** ~2 minutes

**Output Tables:**
- `pharma_platform.bronze_raw.analytical_test_results`
- `pharma_platform.bronze_raw.qc_sample_data`
- `pharma_platform.bronze_raw.clinical_subjects`
- `pharma_platform.bronze_raw.clinical_adverse_events`

---

### Step 4: Silver Layer - Dimensions (Type 2 SCD)
```
/Workspace/Users/kd.umapathy@gmail.com/Data-Model-Concepts/databricks-pharma-pipeline/02_silver/01_silver_dimensions_scd2
```
**What it does:**
- Creates 8 Type 2 Slowly Changing Dimensions
- Implements ISA-88 equipment hierarchy (7 levels)
- Generates surrogate keys and tracks history

**Runtime:** ~3 minutes

**Output Tables:**
- `pharma_platform.silver_cdm.dim_product`
- `pharma_platform.silver_cdm.dim_batch`
- `pharma_platform.silver_cdm.dim_equipment` (with ISA-88 hierarchy)
- `pharma_platform.silver_cdm.dim_material`
- `pharma_platform.silver_cdm.dim_site`
- `pharma_platform.silver_cdm.dim_test_method`
- `pharma_platform.silver_cdm.dim_study`
- `pharma_platform.silver_cdm.dim_date`

---

### Step 5: Silver Layer - Fact Tables
```
/Workspace/Users/kd.umapathy@gmail.com/Data-Model-Concepts/databricks-pharma-pipeline/02_silver/02_silver_fact_tables
```
**What it does:**
- Creates fact tables at atomic grain
- Links facts to dimensions via surrogate keys
- Creates bridge tables for many-to-many relationships

**Runtime:** ~4 minutes

**Output Tables:**
- `pharma_platform.silver_cdm.fact_manufacturing_process`
- `pharma_platform.silver_cdm.fact_analytical_testing`
- `pharma_platform.silver_cdm.fact_batch_genealogy`
- `pharma_platform.silver_cdm.fact_clinical_observations`
- `pharma_platform.silver_cdm.bridge_batch_materials`

**Analytical Views:**
- `v_batch_manufacturing_summary`
- `v_analytical_test_summary`

---

### Step 6: Gold Layer - Business Analytics
```
/Workspace/Users/kd.umapathy@gmail.com/Data-Model-Concepts/databricks-pharma-pipeline/03_gold/01_gold_batch_analytics
```
**What it does:**
- Creates aggregated business KPIs
- Calculates performance metrics (FPY, OTD, OEE)
- Generates analytical tables optimized for reporting

**Runtime:** ~3 minutes

**Output Tables:**
- `pharma_platform.gold_analytics.gold_batch_performance_summary`
- `pharma_platform.gold_analytics.gold_quality_kpi_dashboard`
- `pharma_platform.gold_analytics.gold_equipment_oee`
- `pharma_platform.gold_analytics.gold_material_consumption_forecast`
- `pharma_platform.gold_analytics.gold_clinical_enrollment_tracking`

**Executive View:**
- `v_executive_kpi_summary`

---

### Step 7: Add Table Constraints (PKs and FKs)
```
/Workspace/Users/kd.umapathy@gmail.com/Data-Model-Concepts/databricks-pharma-pipeline/00_setup/01_add_constraints
```
**What it does:**
- Adds PRIMARY KEY constraints to all dimensions and fact tables
- Adds FOREIGN KEY constraints to document relationships
- Creates table relationship view for ER diagrams
- Enables relationship detection in BI tools (Power BI, Tableau)

**Runtime:** ~1 minute

**Output:**
- PRIMARY KEYs on 8 dimensions, 4+ fact tables, 2 metadata tables
- FOREIGN KEYs documenting 16+ table relationships
- View: `pharma_platform.metadata.v_table_relationships`

**Benefits:**
- ✅ ER diagrams automatically generated in data modeling tools
- ✅ BI tools auto-detect relationships
- ✅ Data catalog shows relationship metadata
- ✅ Documentation of data model structure

---

## ⏱️ Total Runtime

| Execution Method | Time |
|------------------|------|
| **RUN_ALL_SIMPLE** (automated) | 12-18 minutes |
| **Manual step-by-step** | 18-25 minutes |

---

## ✅ Verification After Execution

### Quick Validation Queries

```sql
-- Check Bronze layer
SELECT COUNT(*) FROM pharma_platform.bronze_raw.manufacturing_batch_records;
-- Expected: 50 batches

SELECT COUNT(*) FROM pharma_platform.bronze_raw.manufacturing_process_data;
-- Expected: 21,600+ rows

-- Check Silver layer
SELECT COUNT(*) FROM pharma_platform.silver_cdm.dim_product WHERE is_current = true;
-- Expected: 5 products

SELECT COUNT(*) FROM pharma_platform.silver_cdm.fact_manufacturing_process;
-- Expected: Thousands of records

-- Check Gold layer
SELECT * FROM pharma_platform.gold_analytics.gold_batch_performance_summary LIMIT 10;

-- Check table relationships
SELECT * FROM pharma_platform.metadata.v_table_relationships;
-- Expected: 16+ relationship records

-- Verify constraints exist (in Unity Catalog Data Explorer)
DESCRIBE EXTENDED pharma_platform.silver_cdm.dim_batch;

-- Check execution log
SELECT * FROM pharma_platform.metadata.pipeline_execution_log
ORDER BY execution_start_timestamp DESC
LIMIT 10;
```

---

## 🔄 Re-running the Pipeline

### Multiple Runs
- **Bronze layer**: Data appends (new records added each run)
- **Silver layer**: Type 2 SCD tracks changes (creates new versions)
- **Gold layer**: Overwrites with latest aggregations

### Fresh Start
To start completely fresh:
```sql
-- Drop all schemas (WARNING: Deletes all data)
DROP SCHEMA IF EXISTS pharma_platform.bronze_raw CASCADE;
DROP SCHEMA IF EXISTS pharma_platform.silver_cdm CASCADE;
DROP SCHEMA IF EXISTS pharma_platform.gold_analytics CASCADE;
DROP SCHEMA IF EXISTS pharma_platform.metadata CASCADE;

-- Then re-run from Step 1 (Unity Catalog Setup)
```

---

## 🎯 When to Use Each Option

### Use RUN_ALL_SIMPLE When:
- ✅ First-time setup and testing
- ✅ You want one-click execution
- ✅ Demonstrating to stakeholders
- ✅ Running in CI/CD pipelines
- ✅ You don't need to inspect intermediate results

### Use Manual Step-by-Step When:
- ✅ Learning the data model
- ✅ Debugging issues
- ✅ Inspecting data at each layer
- ✅ Making modifications to specific steps
- ✅ Teaching or training sessions

---

## 🔧 Troubleshooting

### Issue: "Table already exists"
**Solution:** This is normal when running multiple times. Data appends to Bronze, creates new versions in Silver (Type 2 SCD), and overwrites Gold.

### Issue: "Cluster not found"
**Solution:**
1. Ensure the notebook is attached to a running cluster
2. Wait for cluster to be in "Running" state (green indicator)
3. Re-run the cell

### Issue: Slow Performance
**Solution:**
1. Check cluster size (recommend 2+ workers)
2. Increase timeout in `dbutils.notebook.run()` calls
3. Monitor cluster utilization

### Issue: Need to Modify Notebooks
**Solution:**
1. Make changes to individual notebooks
2. Run them manually in order (Option 2)
3. Once verified, use RUN_ALL_SIMPLE for automated runs

---

## 📊 What Gets Created

### Total Tables: 28+

| Layer | Tables | Description |
|-------|--------|-------------|
| **Bronze** | 7 | Raw data landing zone |
| **Silver** | 13 | Dimensional model (8 dims + 4 facts + 1 bridge) |
| **Gold** | 5 | Business analytics |
| **Metadata** | 4+ | Pipeline tracking + relationship documentation |

### Total Constraints:
- **PRIMARY KEYs**: 14+ (all dimensions and fact tables)
- **FOREIGN KEYs**: 16+ (fact-to-dimension relationships)

### Total Rows (Demo Mode):
- **Bronze**: ~22,000 rows
- **Silver**: ~25,000+ rows (with dimensional lookups)
- **Gold**: ~500 aggregated rows

---

## 🎓 Learning Path

### For Beginners
1. Start with **RUN_ALL_SIMPLE**
2. Review the output and verify data
3. Explore Gold layer tables first (business view)
4. Then examine Silver layer (dimensional model)
5. Finally look at Bronze layer (raw data)

### For Advanced Users
1. Run **manual steps** to understand each transformation
2. Examine the SQL transformations in each notebook
3. Review Type 2 SCD logic in Silver layer
4. Analyze Kimball methodology implementation
5. Customize for your specific use cases

---

## 📚 Related Documentation

- **Main README**: `../README.md` - Complete architecture and features
- **Deployment Guide**: `DEPLOYMENT_GUIDE.md` - Production setup
- **Demo Mode Guide**: `DEMO_MODE_GUIDE.md` - Using synthetic data
- **Path Configuration**: `NOTEBOOK_PATH_CONFIG.md` - Notebook locations

---

**Last Updated**: 2025-11-22
**Version**: 1.0
