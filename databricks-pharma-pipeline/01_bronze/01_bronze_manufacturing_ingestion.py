# Databricks notebook source
# MAGIC %md
# MAGIC # Bronze Layer: Manufacturing Data Ingestion
# MAGIC
# MAGIC **Purpose:** Ingest raw manufacturing data from MES (Manufacturing Execution System) into Bronze layer
# MAGIC
# MAGIC **Source Systems:**
# MAGIC - DeltaV/PCS7 (DCS - Distributed Control System)
# MAGIC - Syncade (MES)
# MAGIC - OSIsoft PI Historian
# MAGIC
# MAGIC **Data Types:**
# MAGIC - Batch records
# MAGIC - Process data (temperature, pressure, pH, DO, etc.)
# MAGIC - Equipment sensor data
# MAGIC - Batch genealogy
# MAGIC
# MAGIC **Extraction Method:** JDBC (SQL Server) or API
# MAGIC
# MAGIC **Author:** Databricks Solution
# MAGIC **Last Updated:** 2025-11-22

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Configuration and Setup

# COMMAND ----------

import uuid
from datetime import datetime
from pyspark.sql import functions as F
from pyspark.sql.types import *
from delta.tables import DeltaTable

# Catalog and schema names
catalog_name = "pharma_platform"
bronze_schema = "bronze_raw"
meta_schema = "metadata"

# Execution tracking
execution_id = str(uuid.uuid4())
pipeline_name = "bronze_manufacturing_ingestion"

print(f"Execution ID: {execution_id}")
print(f"Pipeline: {pipeline_name}")
print(f"Started at: {datetime.now()}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Source Connection Configuration

# COMMAND ----------

# Database connection parameters (use Databricks secrets in production)
jdbc_hostname = dbutils.secrets.get(scope="pharma_platform", key="mes_jdbc_hostname")
jdbc_port = dbutils.secrets.get(scope="pharma_platform", key="mes_jdbc_port")
jdbc_database = dbutils.secrets.get(scope="pharma_platform", key="mes_jdbc_database")
jdbc_username = dbutils.secrets.get(scope="pharma_platform", key="mes_jdbc_username")
jdbc_password = dbutils.secrets.get(scope="pharma_platform", key="mes_jdbc_password")

jdbc_url = f"jdbc:sqlserver://{jdbc_hostname}:{jdbc_port};database={jdbc_database};encrypt=true;trustServerCertificate=false;hostNameInCertificate=*.database.windows.net;loginTimeout=30;"

connection_properties = {
    "user": jdbc_username,
    "password": jdbc_password,
    "driver": "com.microsoft.sqlserver.jdbc.SQLServerDriver"
}

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Get Last Watermark for Incremental Load

# COMMAND ----------

def get_last_watermark(table_name, watermark_column):
    """
    Retrieve the last watermark value for incremental processing

    Args:
        table_name: Fully qualified table name
        watermark_column: Column name used for watermarking

    Returns:
        Last watermark value as string, or None for full load
    """
    try:
        watermark_df = spark.sql(f"""
            SELECT last_watermark_value
            FROM {catalog_name}.{meta_schema}.watermark_tracking
            WHERE table_name = '{table_name}'
              AND watermark_column = '{watermark_column}'
              AND last_run_status = 'SUCCESS'
        """)

        if watermark_df.count() > 0:
            return watermark_df.collect()[0][0]
        else:
            return None
    except Exception as e:
        print(f"No previous watermark found for {table_name}. Starting full load.")
        return None

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Ingest Batch Records

# COMMAND ----------

# Define target table
target_table_batch = f"{catalog_name}.{bronze_schema}.manufacturing_batch_records"

# Get last watermark
last_watermark = get_last_watermark(target_table_batch, "recorded_timestamp")

# Build incremental query
if last_watermark:
    source_query = f"""
    (SELECT
        batch_id,
        batch_number,
        product_code,
        batch_size,
        batch_size_uom,
        batch_status,
        site_code,
        unit_id,
        recipe_id,
        recipe_version,
        planned_start_date,
        actual_start_date,
        planned_end_date,
        actual_end_date,
        operator_id,
        supervisor_id,
        campaign_id,
        batch_type,
        recorded_timestamp,
        modified_timestamp
    FROM dbo.batch_records
    WHERE recorded_timestamp > '{last_watermark}'
    ) as batch_data
    """
    print(f"Incremental load from watermark: {last_watermark}")
else:
    source_query = """
    (SELECT
        batch_id,
        batch_number,
        product_code,
        batch_size,
        batch_size_uom,
        batch_status,
        site_code,
        unit_id,
        recipe_id,
        recipe_version,
        planned_start_date,
        actual_start_date,
        planned_end_date,
        actual_end_date,
        operator_id,
        supervisor_id,
        campaign_id,
        batch_type,
        recorded_timestamp,
        modified_timestamp
    FROM dbo.batch_records
    ) as batch_data
    """
    print("Full load - no previous watermark found")

# Read from source
batch_df = spark.read.jdbc(
    url=jdbc_url,
    table=source_query,
    properties=connection_properties
)

# Add metadata columns
batch_df_with_meta = batch_df \
    .withColumn("ingestion_timestamp", F.current_timestamp()) \
    .withColumn("ingestion_date", F.current_date()) \
    .withColumn("source_system", F.lit("manufacturing_mes")) \
    .withColumn("execution_id", F.lit(execution_id))

rows_read = batch_df_with_meta.count()
print(f"Rows read from source: {rows_read}")

# COMMAND ----------

# Create table if not exists and write data
if rows_read > 0:
    # Write to Delta table
    batch_df_with_meta.write \
        .format("delta") \
        .mode("append") \
        .option("mergeSchema", "true") \
        .partitionBy("ingestion_date", "site_code") \
        .saveAsTable(target_table_batch)

    # Enable Change Data Feed for audit trail
    spark.sql(f"""
        ALTER TABLE {target_table_batch}
        SET TBLPROPERTIES (
            'delta.enableChangeDataFeed' = 'true',
            'delta.dataSkippingNumIndexedCols' = '5',
            'delta.autoOptimize.optimizeWrite' = 'true',
            'delta.autoOptimize.autoCompact' = 'true'
        )
    """)

    # Update watermark
    max_watermark = batch_df_with_meta.agg(F.max("recorded_timestamp")).collect()[0][0]

    spark.sql(f"""
        MERGE INTO {catalog_name}.{meta_schema}.watermark_tracking AS target
        USING (
            SELECT
                '{target_table_batch}' as table_name,
                'recorded_timestamp' as watermark_column,
                '{max_watermark}' as last_watermark_value,
                current_timestamp() as last_run_timestamp,
                'SUCCESS' as last_run_status,
                {rows_read} as rows_processed,
                '{max_watermark}' as next_run_watermark
        ) AS source
        ON target.table_name = source.table_name
           AND target.watermark_column = source.watermark_column
        WHEN MATCHED THEN UPDATE SET *
        WHEN NOT MATCHED THEN INSERT *
    """)

    print(f"✓ Batch records ingested: {rows_read} rows")
    print(f"✓ New watermark: {max_watermark}")
else:
    print("No new records to ingest")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Ingest Process Data (Time-Series Sensor Data)

# COMMAND ----------

target_table_process = f"{catalog_name}.{bronze_schema}.manufacturing_process_data"

# Get last watermark
last_watermark_process = get_last_watermark(target_table_process, "timestamp")

# Build incremental query for process data
if last_watermark_process:
    process_query = f"""
    (SELECT
        process_data_id,
        batch_id,
        unit_id,
        equipment_id,
        unit_procedure,
        operation,
        phase,
        parameter_name,
        parameter_value,
        parameter_uom,
        target_value,
        upper_limit,
        lower_limit,
        alarm_flag,
        deviation_flag,
        timestamp,
        data_source
    FROM dbo.process_data
    WHERE timestamp > '{last_watermark_process}'
    ) as process_data
    """
else:
    # For initial load, limit to last 30 days to avoid massive data volume
    process_query = """
    (SELECT
        process_data_id,
        batch_id,
        unit_id,
        equipment_id,
        unit_procedure,
        operation,
        phase,
        parameter_name,
        parameter_value,
        parameter_uom,
        target_value,
        upper_limit,
        lower_limit,
        alarm_flag,
        deviation_flag,
        timestamp,
        data_source
    FROM dbo.process_data
    WHERE timestamp >= DATEADD(day, -30, GETDATE())
    ) as process_data
    """

# Read from source
process_df = spark.read.jdbc(
    url=jdbc_url,
    table=process_query,
    properties=connection_properties
)

# Add metadata columns
process_df_with_meta = process_df \
    .withColumn("ingestion_timestamp", F.current_timestamp()) \
    .withColumn("ingestion_date", F.current_date()) \
    .withColumn("source_system", F.lit("manufacturing_mes")) \
    .withColumn("execution_id", F.lit(execution_id))

rows_read_process = process_df_with_meta.count()
print(f"Process data rows read: {rows_read_process}")

# COMMAND ----------

# Write process data
if rows_read_process > 0:
    process_df_with_meta.write \
        .format("delta") \
        .mode("append") \
        .option("mergeSchema", "true") \
        .partitionBy("ingestion_date", "unit_id") \
        .saveAsTable(target_table_process)

    # Enable optimizations
    spark.sql(f"""
        ALTER TABLE {target_table_process}
        SET TBLPROPERTIES (
            'delta.enableChangeDataFeed' = 'true',
            'delta.autoOptimize.optimizeWrite' = 'true',
            'delta.autoOptimize.autoCompact' = 'true'
        )
    """)

    # Update watermark
    max_watermark_process = process_df_with_meta.agg(F.max("timestamp")).collect()[0][0]

    spark.sql(f"""
        MERGE INTO {catalog_name}.{meta_schema}.watermark_tracking AS target
        USING (
            SELECT
                '{target_table_process}' as table_name,
                'timestamp' as watermark_column,
                '{max_watermark_process}' as last_watermark_value,
                current_timestamp() as last_run_timestamp,
                'SUCCESS' as last_run_status,
                {rows_read_process} as rows_processed,
                '{max_watermark_process}' as next_run_watermark
        ) AS source
        ON target.table_name = source.table_name
           AND target.watermark_column = source.watermark_column
        WHEN MATCHED THEN UPDATE SET *
        WHEN NOT MATCHED THEN INSERT *
    """)

    print(f"✓ Process data ingested: {rows_read_process} rows")
    print(f"✓ New watermark: {max_watermark_process}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Ingest Batch Genealogy (Material Traceability)

# COMMAND ----------

target_table_genealogy = f"{catalog_name}.{bronze_schema}.batch_genealogy"

genealogy_query = """
(SELECT
    genealogy_id,
    parent_batch_id,
    child_batch_id,
    parent_material_code,
    child_material_code,
    relationship_type,
    quantity_transferred,
    quantity_uom,
    transfer_timestamp,
    created_timestamp,
    genealogy_level
FROM dbo.batch_genealogy
) as genealogy_data
"""

# Read genealogy data
genealogy_df = spark.read.jdbc(
    url=jdbc_url,
    table=genealogy_query,
    properties=connection_properties
)

# Add metadata
genealogy_df_with_meta = genealogy_df \
    .withColumn("ingestion_timestamp", F.current_timestamp()) \
    .withColumn("ingestion_date", F.current_date()) \
    .withColumn("source_system", F.lit("manufacturing_mes")) \
    .withColumn("execution_id", F.lit(execution_id))

rows_genealogy = genealogy_df_with_meta.count()

# Write using MERGE to avoid duplicates
if rows_genealogy > 0:
    genealogy_df_with_meta.createOrReplaceTempView("genealogy_source")

    spark.sql(f"""
        CREATE TABLE IF NOT EXISTS {target_table_genealogy} (
            genealogy_id STRING,
            parent_batch_id STRING,
            child_batch_id STRING,
            parent_material_code STRING,
            child_material_code STRING,
            relationship_type STRING,
            quantity_transferred DECIMAL(18,4),
            quantity_uom STRING,
            transfer_timestamp TIMESTAMP,
            created_timestamp TIMESTAMP,
            genealogy_level INT,
            ingestion_timestamp TIMESTAMP,
            ingestion_date DATE,
            source_system STRING,
            execution_id STRING
        )
        USING DELTA
        PARTITIONED BY (ingestion_date)
        TBLPROPERTIES (
            'delta.enableChangeDataFeed' = 'true'
        )
    """)

    spark.sql(f"""
        MERGE INTO {target_table_genealogy} AS target
        USING genealogy_source AS source
        ON target.genealogy_id = source.genealogy_id
        WHEN MATCHED THEN UPDATE SET *
        WHEN NOT MATCHED THEN INSERT *
    """)

    print(f"✓ Batch genealogy records ingested: {rows_genealogy} rows")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Data Quality Checks

# COMMAND ----------

# Check for null batch_id in batch records
null_batch_check = spark.sql(f"""
    SELECT COUNT(*) as null_count
    FROM {target_table_batch}
    WHERE batch_id IS NULL
      AND ingestion_date = current_date()
""").collect()[0][0]

# Log DQ check
spark.sql(f"""
    INSERT INTO {catalog_name}.{meta_schema}.data_quality_metrics
    VALUES (
        '{str(uuid.uuid4())}',
        '{execution_id}',
        '{target_table_batch}',
        'null_batch_id_check',
        'completeness',
        '{("PASS" if null_batch_check == 0 else "FAIL")}',
        '0',
        '{null_batch_check}',
        NULL,
        {null_batch_check},
        '{("LOW" if null_batch_check == 0 else "CRITICAL")}',
        current_timestamp()
    )
""")

print(f"DQ Check - Null batch_id: {'PASS' if null_batch_check == 0 else 'FAIL'} ({null_batch_check} nulls found)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8. Log Pipeline Execution

# COMMAND ----------

# Calculate total rows ingested
total_rows_ingested = rows_read + rows_read_process + rows_genealogy

# Log execution
spark.sql(f"""
    INSERT INTO {catalog_name}.{meta_schema}.pipeline_execution_log
    VALUES (
        '{execution_id}',
        '{pipeline_name}',
        'bronze',
        'manufacturing_mes',
        '{target_table_batch}, {target_table_process}, {target_table_genealogy}',
        current_timestamp(),
        current_timestamp(),
        'SUCCESS',
        {total_rows_ingested},
        {total_rows_ingested},
        0,
        0,
        NULL,
        current_user(),
        '{dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get()}',
        map('execution_id', '{execution_id}')
    )
""")

print(f"\n{'='*60}")
print(f"Pipeline Execution Summary")
print(f"{'='*60}")
print(f"Execution ID: {execution_id}")
print(f"Status: SUCCESS")
print(f"Total Rows Ingested: {total_rows_ingested}")
print(f"  - Batch Records: {rows_read}")
print(f"  - Process Data: {rows_read_process}")
print(f"  - Genealogy: {rows_genealogy}")
print(f"Completed at: {datetime.now()}")
print(f"{'='*60}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC
# MAGIC ✅ **Manufacturing data ingested into Bronze layer**
# MAGIC
# MAGIC **Tables Created:**
# MAGIC - `manufacturing_batch_records` - Batch header records
# MAGIC - `manufacturing_process_data` - Time-series process parameters
# MAGIC - `batch_genealogy` - Material traceability and genealogy
# MAGIC
# MAGIC **Features:**
# MAGIC - Incremental loading using watermark tracking
# MAGIC - Partition by ingestion_date and site_code/unit_id for query optimization
# MAGIC - Change Data Feed enabled for audit trail
# MAGIC - Auto-optimize for write and compaction
# MAGIC - Data quality checks with metadata logging
# MAGIC - Pipeline execution tracking
# MAGIC
# MAGIC **Next Steps:**
# MAGIC - Run Silver layer transformation to create dimensional model
# MAGIC - Set up data quality validation rules
# MAGIC - Configure alerting for failed DQ checks
