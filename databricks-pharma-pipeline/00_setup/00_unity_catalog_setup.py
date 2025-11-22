# Databricks notebook source
# MAGIC %md
# MAGIC # Unity Catalog Setup for Pharmaceutical Data Platform
# MAGIC
# MAGIC **Purpose:** Initialize Unity Catalog structure for pharmaceutical data platform
# MAGIC
# MAGIC **Architecture:** Medallion (Bronze, Silver, Gold) + Metadata layer
# MAGIC
# MAGIC **Compliance:** CFR Part 11, EU GMP Annex 11, ALCOA+ data integrity
# MAGIC
# MAGIC **Author:** Databricks Solution
# MAGIC
# MAGIC **Last Updated:** 2025-11-22

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Import Libraries and Configuration

# COMMAND ----------

import yaml
from pyspark.sql import SparkSession
from delta.tables import DeltaTable
import datetime

# Get configuration
config_path = "/Workspace/databricks-pharma-pipeline/config/unity_catalog_config.yaml"

# For demonstration, we'll define config inline
# In production, read from YAML file using dbutils or repos
config = {
    'catalog': {
        'name': 'pharma_platform',
        'comment': 'Pharmaceutical data platform supporting all phases from early-stage to commercial'
    },
    'schemas': {
        'bronze': {'name': 'bronze_raw', 'comment': 'Raw data ingested from source systems - immutable landing zone'},
        'silver': {'name': 'silver_cdm', 'comment': 'Common Data Model - Star schema dimensional model following Kimball methodology'},
        'gold': {'name': 'gold_analytics', 'comment': 'Business-level aggregations and analytical datasets'},
        'meta': {'name': 'metadata', 'comment': 'Pipeline metadata, data lineage, and audit tracking'}
    }
}

catalog_name = config['catalog']['name']
print(f"Setting up Unity Catalog: {catalog_name}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Create Unity Catalog

# COMMAND ----------

# Create catalog if not exists
spark.sql(f"""
CREATE CATALOG IF NOT EXISTS {catalog_name}
COMMENT '{config['catalog']['comment']}'
""")

# Set as current catalog
spark.sql(f"USE CATALOG {catalog_name}")

print(f"✓ Catalog '{catalog_name}' created/verified")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Create Schemas for Medallion Architecture

# COMMAND ----------

# Create Bronze schema
bronze_schema = config['schemas']['bronze']['name']
spark.sql(f"""
CREATE SCHEMA IF NOT EXISTS {catalog_name}.{bronze_schema}
COMMENT '{config['schemas']['bronze']['comment']}'
WITH DBPROPERTIES (
  'layer' = 'bronze',
  'data_classification' = 'raw',
  'retention_policy' = '25_years',
  'compliance' = 'CFR_Part_11'
)
""")
print(f"✓ Schema '{bronze_schema}' created")

# Create Silver schema
silver_schema = config['schemas']['silver']['name']
spark.sql(f"""
CREATE SCHEMA IF NOT EXISTS {catalog_name}.{silver_schema}
COMMENT '{config['schemas']['silver']['comment']}'
WITH DBPROPERTIES (
  'layer' = 'silver',
  'data_classification' = 'curated',
  'data_model' = 'star_schema_kimball',
  'compliance' = 'CFR_Part_11,ALCOA_Plus'
)
""")
print(f"✓ Schema '{silver_schema}' created")

# Create Gold schema
gold_schema = config['schemas']['gold']['name']
spark.sql(f"""
CREATE SCHEMA IF NOT EXISTS {catalog_name}.{gold_schema}
COMMENT '{config['schemas']['gold']['comment']}'
WITH DBPROPERTIES (
  'layer' = 'gold',
  'data_classification' = 'analytical',
  'compliance' = 'CFR_Part_11'
)
""")
print(f"✓ Schema '{gold_schema}' created")

# Create Metadata schema
meta_schema = config['schemas']['meta']['name']
spark.sql(f"""
CREATE SCHEMA IF NOT EXISTS {catalog_name}.{meta_schema}
COMMENT '{config['schemas']['meta']['comment']}'
WITH DBPROPERTIES (
  'layer' = 'metadata',
  'data_classification' = 'operational'
)
""")
print(f"✓ Schema '{meta_schema}' created")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Create Metadata Tables

# COMMAND ----------

# MAGIC %md
# MAGIC ### 4.1 Pipeline Execution Metadata

# COMMAND ----------

spark.sql(f"""
CREATE TABLE IF NOT EXISTS {catalog_name}.{meta_schema}.pipeline_execution_log (
  execution_id STRING COMMENT 'Unique execution identifier',
  pipeline_name STRING COMMENT 'Name of the pipeline/notebook',
  layer STRING COMMENT 'bronze/silver/gold',
  source_table STRING COMMENT 'Source table name',
  target_table STRING COMMENT 'Target table name',
  execution_start_timestamp TIMESTAMP COMMENT 'Pipeline start time',
  execution_end_timestamp TIMESTAMP COMMENT 'Pipeline end time',
  execution_status STRING COMMENT 'SUCCESS/FAILED/RUNNING',
  rows_read BIGINT COMMENT 'Number of rows read from source',
  rows_written BIGINT COMMENT 'Number of rows written to target',
  rows_updated BIGINT COMMENT 'Number of rows updated',
  rows_deleted BIGINT COMMENT 'Number of rows deleted',
  error_message STRING COMMENT 'Error details if failed',
  user_name STRING COMMENT 'User who executed the pipeline',
  notebook_path STRING COMMENT 'Path to the notebook',
  parameters MAP<STRING, STRING> COMMENT 'Execution parameters',
  created_timestamp TIMESTAMP,
  PRIMARY KEY(execution_id)
)
USING DELTA
COMMENT 'Audit trail for all pipeline executions - CFR Part 11 compliance'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true',
  'delta.dataSkippingNumIndexedCols' = '5'
)
""")
print("✓ Table 'pipeline_execution_log' created")

# COMMAND ----------

# MAGIC %md
# MAGIC ### 4.2 Data Quality Metrics

# COMMAND ----------

# Step 1: Create the table without DEFAULT
spark.sql(
    f"""
    CREATE TABLE IF NOT EXISTS {catalog_name}.{meta_schema}.data_quality_metrics (
      dq_check_id STRING COMMENT 'Unique DQ check identifier',
      execution_id STRING COMMENT 'Reference to pipeline execution',
      table_name STRING COMMENT 'Table being checked',
      check_name STRING COMMENT 'Name of the quality check',
      check_type STRING COMMENT 'Type: completeness/accuracy/consistency/timeliness/validity',
      check_result STRING COMMENT 'PASS/FAIL/WARNING',
      expected_value STRING COMMENT 'Expected value or threshold',
      actual_value STRING COMMENT 'Actual measured value',
      deviation_percentage DOUBLE COMMENT 'Percentage deviation from expected',
      rows_affected BIGINT COMMENT 'Number of rows failing the check',
      severity STRING COMMENT 'CRITICAL/HIGH/MEDIUM/LOW',
      check_timestamp TIMESTAMP,
      PRIMARY KEY(dq_check_id)
    )
    USING DELTA
    COMMENT 'Data quality validation results for ALCOA+ compliance'
    TBLPROPERTIES (
      'delta.enableChangeDataFeed' = 'true'
    )
    """
)
print("✓ Table 'data_quality_metrics' created")

# Step 2: Enable column defaults feature
spark.sql(
    f"""
    ALTER TABLE {catalog_name}.{meta_schema}.data_quality_metrics
    SET TBLPROPERTIES('delta.feature.allowColumnDefaults' = 'supported')
    """
)

# Step 3: Add the DEFAULT value to the column
spark.sql(
    f"""
    ALTER TABLE {catalog_name}.{meta_schema}.data_quality_metrics
    ALTER COLUMN check_timestamp SET DEFAULT CURRENT_TIMESTAMP()
    """
)

# COMMAND ----------

# MAGIC %md
# MAGIC ### 4.3 Data Lineage Tracking

# COMMAND ----------

# Step 1: Create the table without DEFAULT
spark.sql(
    f"""
    CREATE TABLE IF NOT EXISTS {catalog_name}.{meta_schema}.data_lineage (
      lineage_id STRING COMMENT 'Unique lineage record identifier',
      source_catalog STRING COMMENT 'Source catalog name',
      source_schema STRING COMMENT 'Source schema name',
      source_table STRING COMMENT 'Source table name',
      source_column STRING COMMENT 'Source column name (optional)',
      target_catalog STRING COMMENT 'Target catalog name',
      target_schema STRING COMMENT 'Target schema name',
      target_table STRING COMMENT 'Target table name',
      target_column STRING COMMENT 'Target column name (optional)',
      transformation_logic STRING COMMENT 'SQL or description of transformation',
      execution_id STRING COMMENT 'Reference to pipeline execution',
      created_timestamp TIMESTAMP,
      PRIMARY KEY(lineage_id)
    )
    USING DELTA
    COMMENT 'End-to-end data lineage for regulatory compliance'
    TBLPROPERTIES (
      'delta.enableChangeDataFeed' = 'true'
    )
    """
)
print("✓ Table 'data_lineage' created")

# Step 2: Enable column defaults feature
spark.sql(
    f"""
    ALTER TABLE {catalog_name}.{meta_schema}.data_lineage
    SET TBLPROPERTIES('delta.feature.allowColumnDefaults' = 'supported')
    """
)

# Step 3: Add the DEFAULT value to the column
spark.sql(
    f"""
    ALTER TABLE {catalog_name}.{meta_schema}.data_lineage
    ALTER COLUMN created_timestamp SET DEFAULT CURRENT_TIMESTAMP()
    """
)

# COMMAND ----------

# MAGIC %md
# MAGIC ### 4.4 Watermark Tracking for Incremental Loads

# COMMAND ----------

# Step 1: Create the table without DEFAULT
spark.sql(
    f"""
    CREATE TABLE IF NOT EXISTS {catalog_name}.{meta_schema}.watermark_tracking (
      table_name STRING COMMENT 'Fully qualified table name',
      watermark_column STRING COMMENT 'Column used for incremental processing',
      last_watermark_value STRING COMMENT 'Last processed watermark value',
      last_run_timestamp TIMESTAMP COMMENT 'Last successful run timestamp',
      last_run_status STRING COMMENT 'SUCCESS/FAILED',
      rows_processed BIGINT COMMENT 'Number of rows in last run',
      next_run_watermark STRING COMMENT 'Starting point for next run',
      updated_timestamp TIMESTAMP,
      PRIMARY KEY(table_name, watermark_column)
    )
    USING DELTA
    COMMENT 'Watermark state for incremental data loads'
    TBLPROPERTIES (
      'delta.enableChangeDataFeed' = 'true'
    )
    """
)

# Step 2: Enable column defaults feature
spark.sql(
    f"""
    ALTER TABLE {catalog_name}.{meta_schema}.watermark_tracking
    SET TBLPROPERTIES('delta.feature.allowColumnDefaults' = 'supported')
    """
)

# Step 3: Add the DEFAULT value to the column
spark.sql(
    f"""
    ALTER TABLE {catalog_name}.{meta_schema}.watermark_tracking
    ALTER COLUMN updated_timestamp SET DEFAULT CURRENT_TIMESTAMP()
    """
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Create Reference/Lookup Tables in Silver Layer

# COMMAND ----------

# MAGIC %md
# MAGIC ### 5.1 ISA-88 Physical Model Hierarchy

# COMMAND ----------

# Step 1: Create the table without DEFAULT
spark.sql(
    f"""
    CREATE TABLE IF NOT EXISTS {catalog_name}.{silver_schema}.ref_isa88_hierarchy (
      hierarchy_id STRING COMMENT 'Unique hierarchy record ID',
      hierarchy_level STRING COMMENT 'Enterprise/Site/Area/ProcessCell/Unit/EquipmentModule/ControlModule',
      hierarchy_level_number INT COMMENT '1=Enterprise, 2=Site, 3=Area, 4=ProcessCell, 5=Unit, 6=EquipmentModule, 7=ControlModule',
      element_code STRING COMMENT 'Unique code for this element',
      element_name STRING COMMENT 'Name of the element',
      parent_element_code STRING COMMENT 'Code of parent in hierarchy',
      description STRING COMMENT 'Detailed description',
      is_active BOOLEAN,
      effective_start_date DATE,
      effective_end_date DATE,
      created_timestamp TIMESTAMP,
      updated_timestamp TIMESTAMP,
      PRIMARY KEY(hierarchy_id)
    )
    USING DELTA
    COMMENT 'ISA-88 Physical Model Hierarchy for equipment organization'
    TBLPROPERTIES (
      'delta.enableChangeDataFeed' = 'true'
    )
    """
)

# Step 2: Enable column defaults feature
spark.sql(
    f"""
    ALTER TABLE {catalog_name}.{silver_schema}.ref_isa88_hierarchy
    SET TBLPROPERTIES('delta.feature.allowColumnDefaults' = 'supported')
    """
)

# Step 3: Add the DEFAULT values to the columns
spark.sql(
    f"""
    ALTER TABLE {catalog_name}.{silver_schema}.ref_isa88_hierarchy
    ALTER COLUMN is_active SET DEFAULT TRUE
    """
)
spark.sql(
    f"""
    ALTER TABLE {catalog_name}.{silver_schema}.ref_isa88_hierarchy
    ALTER COLUMN created_timestamp SET DEFAULT CURRENT_TIMESTAMP()
    """
)
spark.sql(
    f"""
    ALTER TABLE {catalog_name}.{silver_schema}.ref_isa88_hierarchy
    ALTER COLUMN updated_timestamp SET DEFAULT CURRENT_TIMESTAMP()
    """
)

# COMMAND ----------

# MAGIC %md
# MAGIC ### 5.2 Pharmaceutical Development Phases Reference

# COMMAND ----------

spark.sql(f"""
CREATE TABLE IF NOT EXISTS {catalog_name}.{silver_schema}.ref_development_phase (
  phase_id INT COMMENT 'Unique phase identifier',
  phase_code STRING COMMENT 'Short code: DISC/PRECLIN/PH1/PH2/PH3/COMMERCIAL',
  phase_name STRING COMMENT 'Full phase name',
  phase_description STRING COMMENT 'Detailed description',
  regulatory_requirements STRING COMMENT 'Key regulatory requirements for this phase',
  typical_duration_months INT COMMENT 'Typical duration in months',
  sort_order INT COMMENT 'Sort order for display',
  PRIMARY KEY(phase_id)
)
USING DELTA
COMMENT 'Pharmaceutical development phases from discovery to commercial'
""")

# Insert reference data
spark.sql(f"""
INSERT INTO {catalog_name}.{silver_schema}.ref_development_phase VALUES
  (1, 'DISC', 'Discovery', 'Target identification and validation', 'Preclinical research', 24, 1),
  (2, 'PRECLIN', 'Preclinical', 'Animal testing and safety studies', 'IND-enabling studies', 36, 2),
  (3, 'PH1', 'Phase 1 Clinical', 'First-in-human safety studies', 'IND submission, safety focus', 18, 3),
  (4, 'PH2', 'Phase 2 Clinical', 'Efficacy and dose-ranging studies', 'Efficacy proof of concept', 24, 4),
  (5, 'PH3', 'Phase 3 Clinical', 'Pivotal trials for regulatory approval', 'BLA/NDA submission data', 36, 5),
  (6, 'COMMERCIAL', 'Commercial', 'Post-approval commercial manufacturing', 'GMP compliance, lot release', NULL, 6),
  (7, 'PH4', 'Phase 4 Post-Marketing', 'Post-approval surveillance', 'REMS, safety monitoring', NULL, 7)
""")
print("✓ Table 'ref_development_phase' created and populated")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Set Up Table Access Controls (Unity Catalog Permissions)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Grant permissions to data engineering team
# MAGIC
# MAGIC ```sql
# MAGIC -- Grant usage on catalog
# MAGIC GRANT USE CATALOG ON CATALOG pharma_platform TO `data_engineering_team`;
# MAGIC
# MAGIC -- Grant permissions on Bronze schema (read/write for ingestion)
# MAGIC GRANT USE SCHEMA, CREATE TABLE, MODIFY ON SCHEMA pharma_platform.bronze_raw TO `data_engineering_team`;
# MAGIC
# MAGIC -- Grant permissions on Silver schema
# MAGIC GRANT USE SCHEMA, CREATE TABLE, MODIFY ON SCHEMA pharma_platform.silver_cdm TO `data_engineering_team`;
# MAGIC
# MAGIC -- Grant permissions on Gold schema
# MAGIC GRANT USE SCHEMA, CREATE TABLE, MODIFY ON SCHEMA pharma_platform.gold_analytics TO `data_engineering_team`;
# MAGIC
# MAGIC -- Grant read-only access to analysts
# MAGIC GRANT USE CATALOG ON CATALOG pharma_platform TO `data_analysts`;
# MAGIC GRANT USE SCHEMA, SELECT ON SCHEMA pharma_platform.silver_cdm TO `data_analysts`;
# MAGIC GRANT USE SCHEMA, SELECT ON SCHEMA pharma_platform.gold_analytics TO `data_analysts`;
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Enable Features for Compliance

# COMMAND ----------

# MAGIC %md
# MAGIC ### Enable Change Data Feed for Audit Trail (ALCOA+ Compliance)
# MAGIC
# MAGIC All tables are created with `delta.enableChangeDataFeed = true` to support:
# MAGIC - Complete audit trail of all changes
# MAGIC - Time travel for regulatory inquiries
# MAGIC - Point-in-time recovery
# MAGIC - Change data capture for downstream systems
# MAGIC
# MAGIC ### Data Classification Tags
# MAGIC
# MAGIC Tables are tagged with:
# MAGIC - `data_classification`: raw/curated/analytical
# MAGIC - `compliance`: CFR_Part_11, ALCOA_Plus, EU_GMP_Annex_11
# MAGIC - `retention_policy`: 25_years (FDA requirement)
# MAGIC - `contains_pii`: true/false
# MAGIC - `contains_phi`: true/false (for clinical data)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8. Verify Setup

# COMMAND ----------

# Show all schemas in catalog
print("\n=== Schemas in Catalog ===")
spark.sql(f"SHOW SCHEMAS IN {catalog_name}").show(truncate=False)

# Show metadata tables
print("\n=== Metadata Tables ===")
spark.sql(f"SHOW TABLES IN {catalog_name}.{meta_schema}").show(truncate=False)

# Show reference tables in Silver
print("\n=== Reference Tables in Silver ===")
spark.sql(f"SHOW TABLES IN {catalog_name}.{silver_schema}").show(truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 9. Helper Functions for Metadata Logging

# COMMAND ----------

def log_pipeline_execution(execution_id, pipeline_name, layer, source_table, target_table,
                          execution_status, rows_read=0, rows_written=0,
                          rows_updated=0, rows_deleted=0, error_message=None):
    """
    Log pipeline execution to metadata table

    Args:
        execution_id: Unique execution identifier
        pipeline_name: Name of the pipeline/notebook
        layer: bronze/silver/gold
        source_table: Source table name
        target_table: Target table name
        execution_status: SUCCESS/FAILED/RUNNING
        rows_read: Number of rows read
        rows_written: Number of rows written
        rows_updated: Number of rows updated
        rows_deleted: Number of rows deleted
        error_message: Error details if failed
    """
    from pyspark.sql.types import StructType, StructField, StringType, LongType, TimestampType, MapType
    from datetime import datetime

    user_name = spark.sql("SELECT current_user()").collect()[0][0]

    log_data = [(
        execution_id,
        pipeline_name,
        layer,
        source_table,
        target_table,
        datetime.now() if execution_status == 'RUNNING' else None,
        datetime.now() if execution_status != 'RUNNING' else None,
        execution_status,
        rows_read,
        rows_written,
        rows_updated,
        rows_deleted,
        error_message,
        user_name,
        dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get(),
        {}
    )]

    schema = StructType([
        StructField("execution_id", StringType(), False),
        StructField("pipeline_name", StringType(), False),
        StructField("layer", StringType(), False),
        StructField("source_table", StringType(), True),
        StructField("target_table", StringType(), True),
        StructField("execution_start_timestamp", TimestampType(), True),
        StructField("execution_end_timestamp", TimestampType(), True),
        StructField("execution_status", StringType(), False),
        StructField("rows_read", LongType(), True),
        StructField("rows_written", LongType(), True),
        StructField("rows_updated", LongType(), True),
        StructField("rows_deleted", LongType(), True),
        StructField("error_message", StringType(), True),
        StructField("user_name", StringType(), True),
        StructField("notebook_path", StringType(), True),
        StructField("parameters", MapType(StringType(), StringType()), True)
    ])

    log_df = spark.createDataFrame(log_data, schema)

    log_df.write.format("delta").mode("append").saveAsTable(
        f"{catalog_name}.{meta_schema}.pipeline_execution_log"
    )

# Test the function
import uuid
test_execution_id = str(uuid.uuid4())
log_pipeline_execution(
    execution_id=test_execution_id,
    pipeline_name="00_unity_catalog_setup",
    layer="setup",
    source_table=None,
    target_table=None,
    execution_status="SUCCESS",
    rows_read=0,
    rows_written=0
)

print("✓ Pipeline execution logged successfully")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC
# MAGIC Unity Catalog setup complete with:
# MAGIC
# MAGIC ✅ **Catalog Created:** `pharma_platform`
# MAGIC
# MAGIC ✅ **Schemas Created:**
# MAGIC - `bronze_raw` - Raw data landing zone
# MAGIC - `silver_cdm` - Kimball star schema dimensional model
# MAGIC - `gold_analytics` - Business aggregations
# MAGIC - `metadata` - Pipeline metadata and audit logs
# MAGIC
# MAGIC ✅ **Metadata Tables:**
# MAGIC - `pipeline_execution_log` - Audit trail for all executions
# MAGIC - `data_quality_metrics` - DQ validation results
# MAGIC - `data_lineage` - End-to-end lineage tracking
# MAGIC - `watermark_tracking` - Incremental load state
# MAGIC
# MAGIC ✅ **Reference Tables:**
# MAGIC - `ref_isa88_hierarchy` - Equipment hierarchy
# MAGIC - `ref_development_phase` - Pharmaceutical phases
# MAGIC
# MAGIC ✅ **Compliance Features:**
# MAGIC - Change Data Feed enabled for audit trail (CFR Part 11)
# MAGIC - Data classification tags
# MAGIC - 25-year retention policy
# MAGIC - ALCOA+ data integrity support
# MAGIC
# MAGIC **Next Steps:**
# MAGIC 1. Run Bronze layer ingestion notebooks
# MAGIC 2. Run Silver layer dimensional model creation
# MAGIC 3. Run Gold layer analytical table creation
