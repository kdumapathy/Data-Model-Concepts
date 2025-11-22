# Databricks notebook source
# MAGIC %md
# MAGIC # Pipeline Orchestration - Pharmaceutical Data Platform
# MAGIC
# MAGIC **Purpose:** Orchestrate the end-to-end data pipeline from Bronze → Silver → Gold
# MAGIC
# MAGIC **Pipeline Flow:**
# MAGIC 1. Setup: Unity Catalog initialization
# MAGIC 2. Bronze: Ingest raw data from source systems
# MAGIC 3. Silver: Transform to dimensional model (Kimball star schema)
# MAGIC 4. Gold: Create business aggregations
# MAGIC
# MAGIC **Execution:** Can be scheduled via Databricks Jobs or Workflows
# MAGIC
# MAGIC **Dependencies:** All notebooks in 00_setup, 01_bronze, 02_silver, 03_gold folders

# COMMAND ----------

import uuid
from datetime import datetime

# Configuration
catalog_name = "pharma_platform"
execution_id = str(uuid.uuid4())

# Notebook base path - UPDATE THIS based on your workspace location
# Examples:
# - If imported to Repos: "/Repos/<username>/Data-Model-Concepts/databricks-pharma-pipeline"
# - If imported to Workspace: "/Workspace/Users/<email>/Data-Model-Concepts/databricks-pharma-pipeline"
# - If imported to Shared: "/Workspace/Shared/databricks-pharma-pipeline"
NOTEBOOK_BASE_PATH = "/Workspace/Users/kd.umapathy@gmail.com/Data-Model-Concepts/databricks-pharma-pipeline"

print("="*70)
print("  PHARMACEUTICAL DATA PLATFORM - PIPELINE ORCHESTRATION")
print("="*70)
print(f"Execution ID: {execution_id}")
print(f"Notebook Base Path: {NOTEBOOK_BASE_PATH}")
print(f"Started at: {datetime.now()}")
print("="*70)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Stage 0: Unity Catalog Setup (First-time only)

# COMMAND ----------

# Run setup only if needed
setup_required = False  # Set to True for first-time setup

if setup_required:
    print("\n[STAGE 0] Running Unity Catalog Setup...")

    dbutils.notebook.run(
        f"{NOTEBOOK_BASE_PATH}/00_setup/00_unity_catalog_setup",
        timeout_seconds=600
    )

    print("✓ Unity Catalog setup complete")
else:
    print("\n[STAGE 0] Skipping Unity Catalog Setup (already configured)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Stage 1: Bronze Layer - Data Ingestion

# COMMAND ----------

print("\n" + "="*70)
print("[STAGE 1] BRONZE LAYER - DATA INGESTION")
print("="*70)

# Track results
bronze_results = {}

# COMMAND ----------

# MAGIC %md
# MAGIC ### 1.1 Manufacturing Data Ingestion

# COMMAND ----------

print("\n[1.1] Ingesting manufacturing data...")

try:
    result = dbutils.notebook.run(
        f"{NOTEBOOK_BASE_PATH}/01_bronze/01_bronze_manufacturing_ingestion",
        timeout_seconds=1200
    )
    bronze_results['manufacturing'] = 'SUCCESS'
    print("✓ Manufacturing data ingestion complete")
except Exception as e:
    bronze_results['manufacturing'] = f'FAILED: {str(e)}'
    print(f"✗ Manufacturing data ingestion failed: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ### 1.2 Clinical & LIMS Data Ingestion

# COMMAND ----------

print("\n[1.2] Ingesting clinical and LIMS data...")

try:
    result = dbutils.notebook.run(
        f"{NOTEBOOK_BASE_PATH}/01_bronze/02_bronze_clinical_lims_ingestion",
        timeout_seconds=1200
    )
    bronze_results['clinical_lims'] = 'SUCCESS'
    print("✓ Clinical and LIMS data ingestion complete")
except Exception as e:
    bronze_results['clinical_lims'] = f'FAILED: {str(e)}'
    print(f"✗ Clinical and LIMS data ingestion failed: {e}")

# COMMAND ----------

print("\n" + "-"*70)
print("Bronze Layer Summary:")
for source, status in bronze_results.items():
    print(f"  {source:20s}: {status}")
print("-"*70)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Stage 2: Silver Layer - Dimensional Model

# COMMAND ----------

print("\n" + "="*70)
print("[STAGE 2] SILVER LAYER - DIMENSIONAL MODEL (KIMBALL)")
print("="*70)

silver_results = {}

# COMMAND ----------

# MAGIC %md
# MAGIC ### 2.1 Build Dimensions (Type 2 SCD)

# COMMAND ----------

print("\n[2.1] Building dimensional model with SCD Type 2...")

try:
    result = dbutils.notebook.run(
        f"{NOTEBOOK_BASE_PATH}/02_silver/01_silver_dimensions_scd2",
        timeout_seconds=1800
    )
    silver_results['dimensions'] = 'SUCCESS'
    print("✓ Dimensions created successfully")
except Exception as e:
    silver_results['dimensions'] = f'FAILED: {str(e)}'
    print(f"✗ Dimension creation failed: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ### 2.2 Build Fact Tables

# COMMAND ----------

print("\n[2.2] Building fact tables...")

try:
    result = dbutils.notebook.run(
        f"{NOTEBOOK_BASE_PATH}/02_silver/02_silver_fact_tables",
        timeout_seconds=1800
    )
    silver_results['facts'] = 'SUCCESS'
    print("✓ Fact tables created successfully")
except Exception as e:
    silver_results['facts'] = f'FAILED: {str(e)}'
    print(f"✗ Fact table creation failed: {e}")

# COMMAND ----------

print("\n" + "-"*70)
print("Silver Layer Summary:")
for component, status in silver_results.items():
    print(f"  {component:20s}: {status}")
print("-"*70)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Stage 3: Gold Layer - Business Analytics

# COMMAND ----------

print("\n" + "="*70)
print("[STAGE 3] GOLD LAYER - BUSINESS ANALYTICS")
print("="*70)

gold_results = {}

# COMMAND ----------

# MAGIC %md
# MAGIC ### 3.1 Batch Performance Analytics

# COMMAND ----------

print("\n[3.1] Creating gold layer analytics...")

try:
    result = dbutils.notebook.run(
        f"{NOTEBOOK_BASE_PATH}/03_gold/01_gold_batch_analytics",
        timeout_seconds=1200
    )
    gold_results['analytics'] = 'SUCCESS'
    print("✓ Gold layer analytics created successfully")
except Exception as e:
    gold_results['analytics'] = f'FAILED: {str(e)}'
    print(f"✗ Gold layer analytics failed: {e}")

# COMMAND ----------

print("\n" + "-"*70)
print("Gold Layer Summary:")
for component, status in gold_results.items():
    print(f"  {component:20s}: {status}")
print("-"*70)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Pipeline Summary and Reporting

# COMMAND ----------

print("\n" + "="*70)
print("  PIPELINE EXECUTION SUMMARY")
print("="*70)

# Overall status
all_results = {**bronze_results, **silver_results, **gold_results}
failed_count = sum(1 for status in all_results.values() if 'FAILED' in status)
success_count = len(all_results) - failed_count

overall_status = 'SUCCESS' if failed_count == 0 else 'PARTIAL_FAILURE'

print(f"\nExecution ID: {execution_id}")
print(f"Overall Status: {overall_status}")
print(f"Successful Steps: {success_count}/{len(all_results)}")
print(f"Failed Steps: {failed_count}/{len(all_results)}")
print(f"Completed at: {datetime.now()}")

# Detailed results by layer
print("\n" + "-"*70)
print("Bronze Layer Results:")
for source, status in bronze_results.items():
    status_icon = "✓" if status == 'SUCCESS' else "✗"
    print(f"  {status_icon} {source:20s}: {status}")

print("\n" + "-"*70)
print("Silver Layer Results:")
for component, status in silver_results.items():
    status_icon = "✓" if status == 'SUCCESS' else "✗"
    print(f"  {status_icon} {component:20s}: {status}")

print("\n" + "-"*70)
print("Gold Layer Results:")
for component, status in gold_results.items():
    status_icon = "✓" if status == 'SUCCESS' else "✗"
    print(f"  {status_icon} {component:20s}: {status}")

print("="*70)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Data Quality Summary

# COMMAND ----------

# Query data quality metrics from this execution
dq_summary = spark.sql(f"""
    SELECT
        table_name,
        check_name,
        check_result,
        severity,
        actual_value,
        rows_affected
    FROM {catalog_name}.metadata.data_quality_metrics
    WHERE check_timestamp >= current_timestamp() - INTERVAL 1 HOUR
    ORDER BY severity DESC, check_timestamp DESC
""")

print("\n" + "="*70)
print("  DATA QUALITY CHECKS")
print("="*70)

if dq_summary.count() > 0:
    dq_summary.show(truncate=False)
else:
    print("No data quality checks recorded in the last hour")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Table Row Counts

# COMMAND ----------

print("\n" + "="*70)
print("  TABLE ROW COUNTS")
print("="*70)

# Bronze tables
print("\nBronze Layer:")
bronze_tables = [
    "manufacturing_batch_records",
    "manufacturing_process_data",
    "batch_genealogy",
    "analytical_test_results",
    "qc_sample_data",
    "clinical_subjects",
    "clinical_adverse_events"
]

for table in bronze_tables:
    full_table = f"{catalog_name}.bronze_raw.{table}"
    if spark.catalog.tableExists(full_table):
        count = spark.table(full_table).count()
        print(f"  {table:40s}: {count:,}")

# Silver dimensions
print("\nSilver Layer - Dimensions:")
silver_dims = [
    "dim_product",
    "dim_batch",
    "dim_equipment",
    "dim_material",
    "dim_site",
    "dim_test_method",
    "dim_study",
    "dim_date"
]

for dim in silver_dims:
    full_table = f"{catalog_name}.silver_cdm.{dim}"
    if spark.catalog.tableExists(full_table):
        count = spark.table(full_table).count()
        # Show current vs total for SCD dimensions
        if dim != "dim_date":
            current_count = spark.table(full_table).filter("is_current = true").count()
            print(f"  {dim:40s}: {current_count:,} current / {count:,} total")
        else:
            print(f"  {dim:40s}: {count:,}")

# Silver facts
print("\nSilver Layer - Facts:")
silver_facts = [
    "fact_manufacturing_process",
    "fact_analytical_testing",
    "fact_batch_genealogy",
    "fact_clinical_observations"
]

for fact in silver_facts:
    full_table = f"{catalog_name}.silver_cdm.{fact}"
    if spark.catalog.tableExists(full_table):
        count = spark.table(full_table).count()
        print(f"  {fact:40s}: {count:,}")

# Gold tables
print("\nGold Layer:")
gold_tables = [
    "gold_batch_performance_summary",
    "gold_quality_kpi_dashboard",
    "gold_equipment_oee",
    "gold_material_consumption_forecast",
    "gold_clinical_enrollment_tracking"
]

for table in gold_tables:
    full_table = f"{catalog_name}.gold_analytics.{table}"
    if spark.catalog.tableExists(full_table):
        count = spark.table(full_table).count()
        print(f"  {table:40s}: {count:,}")

print("="*70)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Optimization Recommendations

# COMMAND ----------

print("\n" + "="*70)
print("  OPTIMIZATION RECOMMENDATIONS")
print("="*70)

# Run OPTIMIZE on large fact tables
print("\n[OPTIMIZE] Running table optimization...")

fact_tables_to_optimize = [
    f"{catalog_name}.silver_cdm.fact_manufacturing_process",
    f"{catalog_name}.silver_cdm.fact_analytical_testing"
]

for table in fact_tables_to_optimize:
    if spark.catalog.tableExists(table):
        print(f"\nOptimizing {table}...")
        spark.sql(f"OPTIMIZE {table}")
        print(f"✓ {table} optimized")

# Run VACUUM (commented out for safety - requires careful consideration)
# print("\n[VACUUM] Running vacuum to remove old files...")
# spark.sql(f"VACUUM {catalog_name}.silver_cdm.fact_manufacturing_process RETAIN 168 HOURS")

print("\n✓ Optimization complete")
print("="*70)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Pipeline Completion

# COMMAND ----------

# Log final pipeline execution
spark.sql(f"""
    INSERT INTO {catalog_name}.metadata.pipeline_execution_log
    VALUES (
        '{execution_id}',
        'orchestrate_pipeline',
        'orchestration',
        'all_sources',
        'all_targets',
        current_timestamp() - INTERVAL 1 HOUR,
        current_timestamp(),
        '{overall_status}',
        NULL,
        NULL,
        NULL,
        NULL,
        '{"; ".join([f"{k}={v}" for k, v in all_results.items() if "FAILED" in v])}',
        current_user(),
        '{dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get()}',
        map('execution_id', '{execution_id}')
    )
""")

print("\n" + "="*70)
print("  PIPELINE COMPLETE")
print("="*70)
print(f"\nExecution ID: {execution_id}")
print(f"Final Status: {overall_status}")
print(f"\nAll pipeline execution details logged to:")
print(f"  {catalog_name}.metadata.pipeline_execution_log")
print(f"\nData quality metrics logged to:")
print(f"  {catalog_name}.metadata.data_quality_metrics")
print("="*70)

# Return result
dbutils.notebook.exit(overall_status)
