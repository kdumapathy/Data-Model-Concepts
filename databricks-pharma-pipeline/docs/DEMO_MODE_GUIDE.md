# Demo Mode - Quick Start Guide

## ✅ Issue Resolved

The manufacturing ingestion error you encountered was due to missing database connections. I've created **DEMO versions** of the Bronze layer notebooks that generate synthetic data, allowing you to test the complete pipeline without any real data sources.

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Run Unity Catalog Setup (If Not Already Done)

Open and run:
```
/Workspace/Users/kd.umapathy@gmail.com/Data-Model-Concepts/databricks-pharma-pipeline/00_setup/00_unity_catalog_setup
```

### Step 2: Run the Orchestration Notebook in Demo Mode

The orchestration notebook is **already configured** for demo mode:

Open and run:
```
/Workspace/Users/kd.umapathy@gmail.com/Data-Model-Concepts/databricks-pharma-pipeline/04_orchestration/orchestrate_pipeline
```

**Demo mode is ON by default** (`USE_DEMO_MODE = True`)

---

## 📊 What Gets Created in Demo Mode

### Bronze Layer (Synthetic Data)

#### Manufacturing Data
- **50 batches** across 5 products (BIO-001, BIO-002, VAX-001, SM-001, SM-002)
- **3 sites** (US-BOSTON, EU-DUBLIN, CN-SHANGHAI)
- **21,600+ process data points** (temperature, pH, dissolved oxygen, pressure, flow rate, etc.)
- **Batch genealogy** for material traceability

#### LIMS Data
- **200 analytical test results** (HPLC, ELISA, SEC, endotoxin, pH, etc.)
- **95% pass rate** (realistic quality metrics)
- **100 QC samples** with storage tracking

#### Clinical Trial Data
- **150 subjects** across 3 studies (PROTO-001, PROTO-002, PROTO-003)
- **~60 adverse events** with MedDRA coding
- **CDISC-aligned** data structures

### Silver Layer (Dimensional Model)
- **8 dimensions** (Type 2 SCD): product, batch, equipment, material, site, test_method, study, date
- **ISA-88 equipment hierarchy** (7 levels)
- **4+ fact tables**: manufacturing_process, analytical_testing, batch_genealogy, clinical_observations

### Gold Layer (Analytics)
- **Batch performance KPIs**: FPY, OTD, cycle time
- **Quality metrics**: pass rate, OOS tracking
- **Equipment OEE**: Overall Equipment Effectiveness
- **Material consumption**: usage trends
- **Clinical enrollment**: trial metrics

---

## ⚙️ Configuration

The orchestration notebook has a simple flag at the top:

```python
# Demo mode - Set to True to use synthetic data (no real database connections needed)
# Set to False to use production notebooks with actual JDBC/API connections
USE_DEMO_MODE = True  # ← Currently set to demo mode
```

### To Switch to Production Mode

1. Configure secrets for your data sources (see main README)
2. Change the flag:
   ```python
   USE_DEMO_MODE = False
   ```
3. Run the orchestration notebook

---

## 📁 Demo vs Production Notebooks

### Demo Notebooks (No Database Required)
- `01_bronze/01_bronze_manufacturing_ingestion_DEMO.py`
- `01_bronze/02_bronze_clinical_lims_ingestion_DEMO.py`

### Production Notebooks (Require Real Connections)
- `01_bronze/01_bronze_manufacturing_ingestion.py` (needs MES JDBC)
- `01_bronze/02_bronze_clinical_lims_ingestion.py` (needs LIMS JDBC + EDC API)

The orchestration notebook **automatically** selects the correct version based on `USE_DEMO_MODE`.

---

## 📈 Expected Output

When running in demo mode, you'll see:

```
======================================================================
  PHARMACEUTICAL DATA PLATFORM - PIPELINE ORCHESTRATION
======================================================================
Execution ID: abc-123-def-456
Notebook Base Path: /Workspace/Users/kd.umapathy@gmail.com/...
Mode: DEMO (Synthetic Data)  ← Confirms demo mode
Started at: 2025-11-22 10:30:00
======================================================================

[STAGE 0] Skipping Unity Catalog Setup (already configured)

======================================================================
[STAGE 1] BRONZE LAYER - DATA INGESTION
======================================================================

[1.1] Ingesting manufacturing data...
⚠️  DEMO MODE: Generating synthetic data (not connecting to real MES)
✓ Generated 50 synthetic batch records
✓ Generated 21,600 synthetic process data records
✓ Generated 200 genealogy records
✓ Manufacturing data ingestion complete

[1.2] Ingesting clinical and LIMS data...
⚠️  DEMO MODE: Generating synthetic LIMS and clinical data
✓ Generated 200 analytical test results
✓ Generated 100 QC samples
✓ Generated 150 clinical subjects
✓ Generated 60 adverse events
✓ Clinical and LIMS data ingestion complete

======================================================================
[STAGE 2] SILVER LAYER - DIMENSIONAL MODEL (KIMBALL)
======================================================================

[2.1] Building dimensional model with SCD Type 2...
✓ Dimensions created successfully

[2.2] Building fact tables...
✓ Fact tables created successfully

======================================================================
[STAGE 3] GOLD LAYER - BUSINESS ANALYTICS
======================================================================

[3.1] Creating gold layer analytics...
✓ Gold layer analytics created successfully

======================================================================
  PIPELINE COMPLETE
======================================================================
Final Status: SUCCESS
```

---

## 🔍 Verify the Data

After running the pipeline, you can query the tables:

### Bronze Layer
```sql
-- Check batch records
SELECT COUNT(*) FROM pharma_platform.bronze_raw.manufacturing_batch_records;
-- Expected: 50 batches

-- Check process data
SELECT COUNT(*) FROM pharma_platform.bronze_raw.manufacturing_process_data;
-- Expected: 21,600+ rows

-- Check analytical results
SELECT COUNT(*) FROM pharma_platform.bronze_raw.analytical_test_results;
-- Expected: 200 rows

-- Check clinical subjects
SELECT COUNT(*) FROM pharma_platform.bronze_raw.clinical_subjects;
-- Expected: 150 subjects
```

### Silver Layer
```sql
-- Check dimensions
SELECT COUNT(*) FROM pharma_platform.silver_cdm.dim_product WHERE is_current = true;
-- Expected: 5 products

SELECT COUNT(*) FROM pharma_platform.silver_cdm.dim_batch WHERE is_current = true;
-- Expected: 50 batches

-- Check facts
SELECT COUNT(*) FROM pharma_platform.silver_cdm.fact_manufacturing_process;
-- Expected: Thousands of process records

SELECT COUNT(*) FROM pharma_platform.silver_cdm.fact_analytical_testing;
-- Expected: 200 test results
```

### Gold Layer
```sql
-- Check analytics
SELECT * FROM pharma_platform.gold_analytics.gold_batch_performance_summary
LIMIT 10;

-- Quality KPIs
SELECT
  product_name,
  AVG(pass_rate_pct) as avg_pass_rate,
  SUM(oos_count) as total_oos
FROM pharma_platform.gold_analytics.gold_quality_kpi_dashboard
GROUP BY product_name;
```

---

## 💡 Use Cases for Demo Mode

### 1. Testing and Validation
- Validate the medallion architecture
- Test data transformations
- Verify Kimball dimensional model
- Validate data quality checks

### 2. Training and Demos
- Onboard new team members
- Demonstrate to stakeholders
- Training for analysts on data model

### 3. Development
- Develop BI dashboards without prod data
- Test new transformations
- Prototype Gold layer analytics

### 4. CI/CD Pipelines
- Automated testing of notebooks
- Integration tests
- Regression testing

---

## 🔄 Switching to Production

When ready to use real data:

1. **Configure Secrets** (see main README):
   ```bash
   databricks secrets create-scope --scope pharma_platform
   databricks secrets put --scope pharma_platform --key mes_jdbc_hostname
   # ... add all required secrets
   ```

2. **Update Orchestration Notebook**:
   ```python
   USE_DEMO_MODE = False
   ```

3. **Run Pipeline**:
   - Production notebooks will connect to real MES, LIMS, EDC systems
   - Incremental loads will use watermark tracking
   - Real data flows through Bronze → Silver → Gold

---

## 📊 Data Volume Comparison

| Layer | Demo Mode | Production (Typical) |
|-------|-----------|----------------------|
| **Bronze** | | |
| Batch Records | 50 | 500-5,000+ |
| Process Data | 21,600 | Millions |
| Analytical Results | 200 | Thousands |
| Clinical Subjects | 150 | 100-10,000+ per study |
| **Silver** | | |
| Dimensions | 8 tables | 8 tables (more history) |
| Fact Records | ~25,000 | Millions to billions |
| **Gold** | | |
| Aggregations | 5 tables | 5+ tables |

---

## ✅ Benefits of Demo Mode

1. **No Configuration Required**: Works immediately after Unity Catalog setup
2. **No Dependencies**: No JDBC drivers, no API credentials, no network access needed
3. **Fast**: Generates data in seconds, complete pipeline in minutes
4. **Realistic**: Synthetic data follows real pharmaceutical patterns
5. **Complete**: Tests entire medallion architecture end-to-end
6. **Safe**: No access to production systems or sensitive data
7. **Repeatable**: Generates fresh data each run for testing

---

## 🛠️ Troubleshooting

### Error: "Table already exists"
- Expected if running multiple times
- Demo notebooks use `mode="append"`
- Data accumulates - this is normal for testing
- To start fresh: `DROP SCHEMA pharma_platform.bronze_raw CASCADE`

### Error: "Notebook not found"
- Verify notebooks are imported to your workspace
- Check `NOTEBOOK_BASE_PATH` is correct
- Ensure _DEMO notebooks are present in `01_bronze/` folder

### No Data in Tables
- Check execution log: `SELECT * FROM pharma_platform.metadata.pipeline_execution_log`
- Verify execution status is SUCCESS
- Check row counts in log

---

## 📚 Next Steps

After running in demo mode:

1. **Explore the Data**: Query Bronze, Silver, Gold tables
2. **Connect BI Tools**: Point Tableau/Power BI to `gold_analytics` schema
3. **Review Data Model**: Examine dimensional model in `silver_cdm`
4. **Test Queries**: Run analytical queries on Gold layer
5. **Plan Production**: Configure secrets and source connections
6. **Switch to Production**: Set `USE_DEMO_MODE = False` when ready

---

## 📞 Support

- **Demo Mode Documentation**: This file
- **Path Configuration**: `docs/NOTEBOOK_PATH_CONFIG.md`
- **Deployment Guide**: `docs/DEPLOYMENT_GUIDE.md`
- **Main README**: `README.md`

---

**Status**: ✅ Demo Mode Active
**Last Updated**: 2025-11-22
**Commit**: `4203efd` - "Add DEMO versions of Bronze ingestion notebooks"
