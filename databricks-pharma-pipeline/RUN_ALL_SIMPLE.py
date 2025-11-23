# Databricks notebook source
# MAGIC %md
# MAGIC # Run Complete Pipeline - Simple Sequential Execution
# MAGIC
# MAGIC **Purpose:** Execute the complete pharmaceutical data platform pipeline step-by-step
# MAGIC
# MAGIC **What this does:**
# MAGIC - Runs each notebook in the correct order
# MAGIC - Uses the cluster you're currently attached to (no cluster reference issues)
# MAGIC - Shows clear progress for each step
# MAGIC - Stops if any step fails
# MAGIC
# MAGIC **How to use:**
# MAGIC 1. Attach this notebook to a running cluster
# MAGIC 2. Click "Run All" or execute cells in order
# MAGIC 3. Monitor progress in the output
# MAGIC
# MAGIC **Total Runtime:** Approximately 10-15 minutes in demo mode

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration

# COMMAND ----------

import datetime

# Notebook base path - UPDATE THIS to match your workspace location
NOTEBOOK_BASE_PATH = "/Workspace/Users/kd.umapathy@gmail.com/Data-Model-Concepts/databricks-pharma-pipeline"

# Demo mode - True for synthetic data, False for real data sources
USE_DEMO_MODE = True

print("="*70)
print("  PHARMACEUTICAL DATA PLATFORM - SEQUENTIAL EXECUTION")
print("="*70)
print(f"Notebook Base Path: {NOTEBOOK_BASE_PATH}")
print(f"Mode: {'DEMO (Synthetic Data)' if USE_DEMO_MODE else 'PRODUCTION (Real Data)'}")
print(f"Started at: {datetime.datetime.now()}")
print("="*70)

# COMMAND ----------

# MAGIC %md
# MAGIC ## ⚠️ OPTIONAL: Clear All Tables (Fresh Start)
# MAGIC
# MAGIC **⚠️ WARNING: This will DELETE ALL DATA! ⚠️**
# MAGIC
# MAGIC **When to use this:**
# MAGIC - You want a completely fresh start
# MAGIC - You're troubleshooting and need to rebuild from scratch
# MAGIC - You want to test the full pipeline with clean slate
# MAGIC
# MAGIC **How to use:**
# MAGIC 1. Set `CLEAR_ALL_TABLES = True` in the cell below
# MAGIC 2. Run ONLY the cleanup cell manually (DO NOT include in "Run All")
# MAGIC 3. Set it back to `False` before running the pipeline
# MAGIC
# MAGIC **What gets deleted:**
# MAGIC - All Bronze layer tables
# MAGIC - All Silver layer tables
# MAGIC - All Gold layer tables
# MAGIC - All Metadata tables
# MAGIC - All schemas (but NOT the catalog)

# COMMAND ----------

# ⚠️ DANGEROUS: Set to True to clear all tables
# This cell is designed to be run MANUALLY ONLY
CLEAR_ALL_TABLES = False

if CLEAR_ALL_TABLES:
    print("\n" + "⚠️"*35)
    print("  WARNING: CLEARING ALL TABLES AND SCHEMAS")
    print("⚠️"*35 + "\n")

    catalog_name = "pharma_platform"
    schemas_to_drop = ["bronze_raw", "silver_cdm", "gold_analytics", "metadata"]

    for schema in schemas_to_drop:
        try:
            print(f"🗑️  Dropping schema: {catalog_name}.{schema}")
            spark.sql(f"DROP SCHEMA IF EXISTS {catalog_name}.{schema} CASCADE")
            print(f"✅ Dropped: {catalog_name}.{schema}")
        except Exception as e:
            print(f"❌ Error dropping {schema}: {str(e)}")

    print("\n" + "="*70)
    print("  ✅ ALL TABLES AND SCHEMAS CLEARED")
    print("="*70)
    print("\nNext steps:")
    print("1. Set CLEAR_ALL_TABLES = False above")
    print("2. Run the pipeline starting from Step 1 (Unity Catalog Setup)")
    print("="*70 + "\n")

else:
    print("ℹ️  Cleanup skipped (CLEAR_ALL_TABLES = False)")
    print("   To clear all tables, set CLEAR_ALL_TABLES = True and run this cell manually")

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC
# MAGIC # Pipeline Execution Steps
# MAGIC
# MAGIC **Start here for normal execution** (after optional cleanup above)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1: Unity Catalog Setup
# MAGIC
# MAGIC Creates catalog, schemas, and metadata tables.
# MAGIC
# MAGIC **Skip this step if already run** - Set `skip_setup = True` below

# COMMAND ----------

# Set to True to skip Unity Catalog setup (if already done)
skip_setup = False

if skip_setup:
    print("⏭️  Skipping Unity Catalog Setup (already configured)")
else:
    print("🔧 [STEP 1/7] Running Unity Catalog Setup...")
    print("-" * 70)

    dbutils.notebook.run(
        f"{NOTEBOOK_BASE_PATH}/00_setup/00_unity_catalog_setup",
        timeout_seconds=600
    )

    print("✅ Unity Catalog setup complete")
    print("")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2: Bronze Layer - Manufacturing Data
# MAGIC
# MAGIC Ingests manufacturing data (batches, process data, genealogy).
# MAGIC
# MAGIC **Demo Mode:** Generates 50 batches + 21,600 process data points

# COMMAND ----------

print("📥 [STEP 2/7] Ingesting Manufacturing Data...")
print("-" * 70)

# Select demo or production notebook
mfg_notebook = "01_bronze_manufacturing_ingestion_DEMO" if USE_DEMO_MODE else "01_bronze_manufacturing_ingestion"

dbutils.notebook.run(
    f"{NOTEBOOK_BASE_PATH}/01_bronze/{mfg_notebook}",
    timeout_seconds=1200
)

print("✅ Manufacturing data ingestion complete")
print("")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3: Bronze Layer - Clinical & LIMS Data
# MAGIC
# MAGIC Ingests clinical trial and laboratory data.
# MAGIC
# MAGIC **Demo Mode:** Generates 200 analytical tests + 150 clinical subjects

# COMMAND ----------

print("📥 [STEP 3/7] Ingesting Clinical & LIMS Data...")
print("-" * 70)

# Select demo or production notebook
clinical_notebook = "02_bronze_clinical_lims_ingestion_DEMO" if USE_DEMO_MODE else "02_bronze_clinical_lims_ingestion"

dbutils.notebook.run(
    f"{NOTEBOOK_BASE_PATH}/01_bronze/{clinical_notebook}",
    timeout_seconds=1200
)

print("✅ Clinical & LIMS data ingestion complete")
print("")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4: Silver Layer - Dimensional Model (Dimensions)
# MAGIC
# MAGIC Creates Kimball star schema dimensions with Type 2 SCD.
# MAGIC
# MAGIC **Creates:** 8 dimensions (product, batch, equipment, material, site, test_method, study, date)

# COMMAND ----------

print("🔄 [STEP 4/7] Building Dimensional Model (Dimensions)...")
print("-" * 70)

dbutils.notebook.run(
    f"{NOTEBOOK_BASE_PATH}/02_silver/01_silver_dimensions_scd2",
    timeout_seconds=1800
)

print("✅ Dimensions created successfully")
print("")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5: Silver Layer - Dimensional Model (Facts)
# MAGIC
# MAGIC Creates fact tables at atomic grain.
# MAGIC
# MAGIC **Creates:** 4+ fact tables (manufacturing_process, analytical_testing, batch_genealogy, clinical_observations)

# COMMAND ----------

print("🔄 [STEP 5/7] Building Fact Tables...")
print("-" * 70)

dbutils.notebook.run(
    f"{NOTEBOOK_BASE_PATH}/02_silver/02_silver_fact_tables",
    timeout_seconds=1800
)

print("✅ Fact tables created successfully")
print("")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 6: Gold Layer - Business Analytics
# MAGIC
# MAGIC Creates aggregated analytics tables.
# MAGIC
# MAGIC **Creates:** 5 gold tables (batch performance, quality KPIs, equipment OEE, material consumption, clinical enrollment)

# COMMAND ----------

print("📊 [STEP 6/7] Creating Gold Layer Analytics...")
print("-" * 70)

dbutils.notebook.run(
    f"{NOTEBOOK_BASE_PATH}/03_gold/01_gold_batch_analytics",
    timeout_seconds=1200
)

print("✅ Gold layer analytics created successfully")
print("")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 7: Add Table Constraints (PKs and FKs)
# MAGIC
# MAGIC Adds PRIMARY KEY and FOREIGN KEY constraints for:
# MAGIC - Data integrity documentation
# MAGIC - ER diagram generation
# MAGIC - BI tool relationship detection
# MAGIC
# MAGIC **Creates:** Primary keys on all dimensions/facts, Foreign keys for all relationships

# COMMAND ----------

print("🔗 [STEP 7/7] Adding Primary and Foreign Key Constraints...")
print("-" * 70)

dbutils.notebook.run(
    f"{NOTEBOOK_BASE_PATH}/00_setup/01_add_constraints",
    timeout_seconds=600
)

print("✅ Table constraints added successfully")
print("")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Pipeline Complete! 🎉

# COMMAND ----------

print("\n" + "="*70)
print("  ✅ PIPELINE EXECUTION COMPLETE!")
print("="*70)
print(f"Completed at: {datetime.datetime.now()}")
print("")
print("📊 Data Platform Status:")
print("  ✅ Bronze Layer - Raw data ingested")
print("  ✅ Silver Layer - Dimensional model created (Kimball star schema)")
print("  ✅ Gold Layer - Business analytics ready")
print("  ✅ Table Constraints - PKs and FKs added for ER diagrams")
print("")
print("🔍 Next Steps:")
print("  1. Query the data: SELECT * FROM pharma_platform.gold_analytics.gold_batch_performance_summary")
print("  2. View relationships: SELECT * FROM pharma_platform.metadata.v_table_relationships")
print("  3. Connect BI tools: Point to pharma_platform.gold_analytics schema (relationships auto-detected)")
print("  4. Explore dimensions: SELECT * FROM pharma_platform.silver_cdm.dim_product WHERE is_current=true")
print("="*70)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verification Queries
# MAGIC
# MAGIC Run these to verify the data was created successfully:

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check Bronze layer row counts
# MAGIC SELECT
# MAGIC   'Bronze - Batch Records' as layer_table,
# MAGIC   COUNT(*) as row_count
# MAGIC FROM pharma_platform.bronze_raw.manufacturing_batch_records
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT
# MAGIC   'Bronze - Process Data' as layer_table,
# MAGIC   COUNT(*) as row_count
# MAGIC FROM pharma_platform.bronze_raw.manufacturing_process_data
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT
# MAGIC   'Bronze - Analytical Results' as layer_table,
# MAGIC   COUNT(*) as row_count
# MAGIC FROM pharma_platform.bronze_raw.analytical_test_results
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT
# MAGIC   'Bronze - Clinical Subjects' as layer_table,
# MAGIC   COUNT(*) as row_count
# MAGIC FROM pharma_platform.bronze_raw.clinical_subjects
# MAGIC
# MAGIC ORDER BY layer_table

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check Silver layer dimensions
# MAGIC SELECT
# MAGIC   'Silver - Products' as dimension,
# MAGIC   COUNT(*) as current_records
# MAGIC FROM pharma_platform.silver_cdm.dim_product
# MAGIC WHERE is_current = true
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT
# MAGIC   'Silver - Batches' as dimension,
# MAGIC   COUNT(*) as current_records
# MAGIC FROM pharma_platform.silver_cdm.dim_batch
# MAGIC WHERE is_current = true
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT
# MAGIC   'Silver - Equipment' as dimension,
# MAGIC   COUNT(*) as current_records
# MAGIC FROM pharma_platform.silver_cdm.dim_equipment
# MAGIC WHERE is_current = true
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT
# MAGIC   'Silver - Materials' as dimension,
# MAGIC   COUNT(*) as current_records
# MAGIC FROM pharma_platform.silver_cdm.dim_material
# MAGIC WHERE is_current = true
# MAGIC
# MAGIC ORDER BY dimension

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check Gold layer analytics
# MAGIC SELECT
# MAGIC   product_name,
# MAGIC   COUNT(*) as batch_count,
# MAGIC   ROUND(AVG(first_pass_yield_pct), 2) as avg_first_pass_yield,
# MAGIC   ROUND(AVG(cycle_time_days), 1) as avg_cycle_time_days,
# MAGIC   SUM(deviation_count) as total_deviations
# MAGIC FROM pharma_platform.gold_analytics.gold_batch_performance_summary
# MAGIC GROUP BY product_name
# MAGIC ORDER BY batch_count DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ## Troubleshooting
# MAGIC
# MAGIC **If any step fails:**
# MAGIC
# MAGIC 1. **Check the error message** in the cell output
# MAGIC 2. **Review logs:** Check `pharma_platform.metadata.pipeline_execution_log`
# MAGIC 3. **Data quality:** Check `pharma_platform.metadata.data_quality_metrics`
# MAGIC 4. **Re-run failed step:** You can re-run individual cells
# MAGIC
# MAGIC **Common Issues:**
# MAGIC
# MAGIC - **"Table already exists"**: Normal if running multiple times (data appends)
# MAGIC - **"Cluster not found"**: Make sure this notebook is attached to a running cluster
# MAGIC - **"Timeout"**: Increase timeout_seconds in dbutils.notebook.run() calls
# MAGIC
# MAGIC **For Production Mode:**
# MAGIC
# MAGIC Set `USE_DEMO_MODE = False` and configure secrets:
# MAGIC ```bash
# MAGIC databricks secrets create-scope --scope pharma_platform
# MAGIC databricks secrets put --scope pharma_platform --key mes_jdbc_hostname
# MAGIC # ... add all required secrets
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC
# MAGIC **What Was Created:**
# MAGIC
# MAGIC ### Bronze Layer (Raw Data)
# MAGIC - manufacturing_batch_records
# MAGIC - manufacturing_process_data
# MAGIC - batch_genealogy
# MAGIC - analytical_test_results
# MAGIC - qc_sample_data
# MAGIC - clinical_subjects
# MAGIC - clinical_adverse_events
# MAGIC
# MAGIC ### Silver Layer (Dimensional Model - Kimball Star Schema)
# MAGIC **Dimensions (Type 2 SCD):**
# MAGIC - dim_product
# MAGIC - dim_batch
# MAGIC - dim_equipment (ISA-88 hierarchy)
# MAGIC - dim_material
# MAGIC - dim_site
# MAGIC - dim_test_method
# MAGIC - dim_study
# MAGIC - dim_date
# MAGIC
# MAGIC **Fact Tables:**
# MAGIC - fact_manufacturing_process
# MAGIC - fact_analytical_testing
# MAGIC - fact_batch_genealogy
# MAGIC - fact_clinical_observations
# MAGIC
# MAGIC **Bridge Tables:**
# MAGIC - bridge_batch_materials
# MAGIC
# MAGIC ### Gold Layer (Business Analytics)
# MAGIC - gold_batch_performance_summary (FPY, OTD, cycle time)
# MAGIC - gold_quality_kpi_dashboard (pass rate, OOS tracking)
# MAGIC - gold_equipment_oee (Overall Equipment Effectiveness)
# MAGIC - gold_material_consumption_forecast (usage trends)
# MAGIC - gold_clinical_enrollment_tracking (trial metrics)
# MAGIC
# MAGIC ### Metadata Layer
# MAGIC - pipeline_execution_log (audit trail)
# MAGIC - data_quality_metrics (DQ validation)
# MAGIC - data_lineage (end-to-end tracking)
# MAGIC - watermark_tracking (incremental loads)
# MAGIC
# MAGIC **Compliance Features:**
# MAGIC - ✅ CFR Part 11 (electronic records)
# MAGIC - ✅ ALCOA+ data integrity
# MAGIC - ✅ EU GMP Annex 11
# MAGIC - ✅ CDISC standards (clinical data)
# MAGIC - ✅ ISA-88/ISA-95 (manufacturing)
# MAGIC
# MAGIC **Ready for:**
# MAGIC - BI tool connectivity (Tableau, Power BI)
# MAGIC - SQL queries and analytics
# MAGIC - Regulatory submissions
# MAGIC - Production scaling
