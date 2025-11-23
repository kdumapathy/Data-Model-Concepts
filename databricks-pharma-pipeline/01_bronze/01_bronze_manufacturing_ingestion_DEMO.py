# Databricks notebook source
# MAGIC %md
# MAGIC # Bronze Layer: Manufacturing Data Ingestion (DEMO VERSION)
# MAGIC
# MAGIC **Purpose:** Demo version that generates synthetic data instead of connecting to real MES systems
# MAGIC
# MAGIC **Use this notebook to:**
# MAGIC - Test the pipeline without actual source systems
# MAGIC - Validate the medallion architecture
# MAGIC - Demonstrate the data model with sample data
# MAGIC
# MAGIC **For production:** Use `01_bronze_manufacturing_ingestion.py` with real JDBC connections

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Configuration and Setup

# COMMAND ----------

import uuid
from datetime import datetime, timedelta
from pyspark.sql import functions as F
from pyspark.sql.types import *
from delta.tables import DeltaTable
import random

# Catalog and schema names
catalog_name = "pharma_platform"
bronze_schema = "bronze_raw"
meta_schema = "metadata"

# Execution tracking
execution_id = str(uuid.uuid4())
pipeline_name = "bronze_manufacturing_ingestion_demo"

print(f"Execution ID: {execution_id}")
print(f"Pipeline: {pipeline_name}")
print(f"Started at: {datetime.now()}")
print("\n⚠️  DEMO MODE: Generating synthetic data (not connecting to real MES)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Generate Synthetic Batch Records

# COMMAND ----------

# Generate sample batch data
def generate_batch_records(num_batches=50):
    """Generate synthetic batch records"""

    products = ['BIO-001', 'BIO-002', 'VAX-001', 'SM-001', 'SM-002']
    sites = ['US-BOSTON', 'EU-DUBLIN', 'CN-SHANGHAI']
    batch_types = ['COMMERCIAL', 'CLINICAL', 'DEVELOPMENT', 'VALIDATION']
    statuses = ['COMPLETED', 'IN_PROGRESS', 'RELEASED']

    batches = []
    base_date = datetime.now() - timedelta(days=90)

    for i in range(num_batches):
        batch_num = f"B{datetime.now().year}-{str(i+1000).zfill(5)}"
        product = random.choice(products)
        site = random.choice(sites)
        batch_type = random.choice(batch_types)

        planned_start = base_date + timedelta(days=i*2)
        actual_start = planned_start + timedelta(hours=random.randint(-4, 4))
        planned_end = planned_start + timedelta(days=14)
        actual_end = planned_end + timedelta(hours=random.randint(-12, 24))

        batches.append({
            'batch_id': batch_num,
            'batch_number': batch_num,
            'product_code': product,
            'batch_size': round(random.uniform(100, 2000), 2),
            'batch_size_uom': 'L',
            'batch_status': random.choice(statuses),
            'site_code': site,
            'unit_id': f"{site}-UNIT-{random.randint(1,5)}",
            'recipe_id': f"RCP-{product}-V{random.randint(1,3)}",
            'recipe_version': f"V{random.randint(1,3)}.{random.randint(0,5)}",
            'planned_start_date': planned_start,
            'actual_start_date': actual_start,
            'planned_end_date': planned_end,
            'actual_end_date': actual_end if random.random() > 0.3 else None,
            'operator_id': f"OPR-{random.randint(100,999)}",
            'supervisor_id': f"SUP-{random.randint(10,99)}",
            'campaign_id': f"CAMP-{datetime.now().year}-Q{((i//10)%4)+1}",
            'batch_type': batch_type,
            'recorded_timestamp': actual_start,
            'modified_timestamp': datetime.now() - timedelta(hours=random.randint(1,48))
        })

    return batches

# Generate data
batch_data = generate_batch_records(50)

# Create DataFrame
batch_schema = StructType([
    StructField("batch_id", StringType(), False),
    StructField("batch_number", StringType(), False),
    StructField("product_code", StringType(), True),
    StructField("batch_size", DoubleType(), True),
    StructField("batch_size_uom", StringType(), True),
    StructField("batch_status", StringType(), True),
    StructField("site_code", StringType(), True),
    StructField("unit_id", StringType(), True),
    StructField("recipe_id", StringType(), True),
    StructField("recipe_version", StringType(), True),
    StructField("planned_start_date", TimestampType(), True),
    StructField("actual_start_date", TimestampType(), True),
    StructField("planned_end_date", TimestampType(), True),
    StructField("actual_end_date", TimestampType(), True),
    StructField("operator_id", StringType(), True),
    StructField("supervisor_id", StringType(), True),
    StructField("campaign_id", StringType(), True),
    StructField("batch_type", StringType(), True),
    StructField("recorded_timestamp", TimestampType(), True),
    StructField("modified_timestamp", TimestampType(), True)
])

batch_df = spark.createDataFrame(batch_data, schema=batch_schema)

# Add metadata columns
batch_df_with_meta = batch_df \
    .withColumn("ingestion_timestamp", F.current_timestamp()) \
    .withColumn("ingestion_date", F.current_date()) \
    .withColumn("source_system", F.lit("manufacturing_mes_demo")) \
    .withColumn("execution_id", F.lit(execution_id))

rows_read = batch_df_with_meta.count()
print(f"✓ Generated {rows_read} synthetic batch records")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Write Batch Records to Bronze

# COMMAND ----------

target_table_batch = f"{catalog_name}.{bronze_schema}.manufacturing_batch_records"

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

print(f"✓ Batch records written to {target_table_batch}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Generate Synthetic Process Data

# COMMAND ----------

def generate_process_data(batch_df, records_per_batch=100):
    """Generate synthetic time-series process data"""

    parameters = [
        ('Temperature', 'C', 37.0, 35.0, 39.0),
        ('pH', '', 7.2, 6.8, 7.6),
        ('Dissolved_Oxygen', '%', 40.0, 30.0, 60.0),
        ('Pressure', 'psi', 15.0, 10.0, 20.0),
        ('Flow_Rate', 'L/min', 50.0, 40.0, 80.0),
        ('Agitation', 'RPM', 100.0, 80.0, 150.0),
        ('Glucose', 'g/L', 5.0, 2.0, 10.0),
        ('Lactate', 'g/L', 2.0, 0.5, 4.0),
        ('Cell_Density', 'cells/mL', 5000000.0, 1000000.0, 10000000.0)
    ]

    process_records = []
    process_id = 1

    for batch_row in batch_df.collect():
        batch_id = batch_row['batch_number']
        unit_id = batch_row['unit_id']
        equipment_id = f"EQUIP-{random.randint(1000,9999)}"
        start_time = batch_row['actual_start_date']

        # Generate time series data
        for hour in range(0, records_per_batch):
            timestamp = start_time + timedelta(hours=hour)

            for param_name, uom, target, lower, upper in parameters:
                # Add some variation
                value = target + random.uniform(-0.1, 0.1) * (upper - lower)
                alarm = value < lower or value > upper
                deviation = abs(value - target) > 0.15 * (upper - lower)

                process_records.append({
                    'process_data_id': f"PD-{process_id}",
                    'batch_id': batch_id,
                    'unit_id': unit_id,
                    'equipment_id': equipment_id,
                    'unit_procedure': 'Fermentation',
                    'operation': 'Cell_Culture',
                    'phase': f'Phase_{(hour//24)+1}',
                    'parameter_name': param_name,
                    'parameter_value': round(value, 2),
                    'parameter_uom': uom,
                    'target_value': target,
                    'upper_limit': upper,
                    'lower_limit': lower,
                    'alarm_flag': alarm,
                    'deviation_flag': deviation,
                    'timestamp': timestamp,
                    'data_source': 'DCS'
                })
                process_id += 1

    return process_records

# Generate process data (limit to first 10 batches for demo)
sample_batches = batch_df.limit(10)
process_data = generate_process_data(sample_batches, records_per_batch=24)  # 24 hours per batch

process_schema = StructType([
    StructField("process_data_id", StringType(), False),
    StructField("batch_id", StringType(), True),
    StructField("unit_id", StringType(), True),
    StructField("equipment_id", StringType(), True),
    StructField("unit_procedure", StringType(), True),
    StructField("operation", StringType(), True),
    StructField("phase", StringType(), True),
    StructField("parameter_name", StringType(), True),
    StructField("parameter_value", DoubleType(), True),
    StructField("parameter_uom", StringType(), True),
    StructField("target_value", DoubleType(), True),
    StructField("upper_limit", DoubleType(), True),
    StructField("lower_limit", DoubleType(), True),
    StructField("alarm_flag", BooleanType(), True),
    StructField("deviation_flag", BooleanType(), True),
    StructField("timestamp", TimestampType(), True),
    StructField("data_source", StringType(), True)
])

process_df = spark.createDataFrame(process_data, schema=process_schema)

# Add metadata
process_df_with_meta = process_df \
    .withColumn("ingestion_timestamp", F.current_timestamp()) \
    .withColumn("ingestion_date", F.current_date()) \
    .withColumn("source_system", F.lit("manufacturing_mes_demo")) \
    .withColumn("execution_id", F.lit(execution_id))

rows_read_process = process_df_with_meta.count()
print(f"✓ Generated {rows_read_process:,} synthetic process data records")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Write Process Data to Bronze

# COMMAND ----------

target_table_process = f"{catalog_name}.{bronze_schema}.manufacturing_process_data"

process_df_with_meta.write \
    .format("delta") \
    .mode("append") \
    .option("mergeSchema", "true") \
    .partitionBy("ingestion_date", "unit_id") \
    .saveAsTable(target_table_process)

spark.sql(f"""
    ALTER TABLE {target_table_process}
    SET TBLPROPERTIES (
        'delta.enableChangeDataFeed' = 'true',
        'delta.autoOptimize.optimizeWrite' = 'true',
        'delta.autoOptimize.autoCompact' = 'true'
    )
""")

print(f"✓ Process data written to {target_table_process}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Generate Batch Genealogy Data

# COMMAND ----------

def generate_genealogy(batch_df, num_materials=20):
    """Generate synthetic batch genealogy"""

    materials = [f"MAT-{i:04d}" for i in range(1, num_materials+1)]
    relationship_types = ['INPUT', 'OUTPUT', 'INTERMEDIATE']

    genealogy_records = []
    gen_id = 1

    batches = batch_df.select('batch_number').collect()

    for i, batch_row in enumerate(batches):
        batch_num = batch_row['batch_number']

        # Input materials
        for _ in range(random.randint(3, 6)):
            genealogy_records.append({
                'genealogy_id': f"GEN-{gen_id}",
                'parent_batch_id': batches[max(0, i-1)]['batch_number'] if i > 0 else None,
                'child_batch_id': batch_num,
                'parent_material_code': random.choice(materials),
                'child_material_code': f"FP-{batch_num}",
                'relationship_type': 'INPUT',
                'quantity_transferred': round(random.uniform(10, 500), 2),
                'quantity_uom': 'kg',
                'transfer_timestamp': datetime.now() - timedelta(days=random.randint(1, 90)),
                'created_timestamp': datetime.now() - timedelta(days=random.randint(1, 90)),
                'genealogy_level': 1
            })
            gen_id += 1

    return genealogy_records

genealogy_data = generate_genealogy(batch_df, num_materials=30)

genealogy_schema = StructType([
    StructField("genealogy_id", StringType(), False),
    StructField("parent_batch_id", StringType(), True),
    StructField("child_batch_id", StringType(), True),
    StructField("parent_material_code", StringType(), True),
    StructField("child_material_code", StringType(), True),
    StructField("relationship_type", StringType(), True),
    StructField("quantity_transferred", DoubleType(), True),
    StructField("quantity_uom", StringType(), True),
    StructField("transfer_timestamp", TimestampType(), True),
    StructField("created_timestamp", TimestampType(), True),
    StructField("genealogy_level", IntegerType(), True)
])

genealogy_df = spark.createDataFrame(genealogy_data, schema=genealogy_schema) \
    .withColumn("ingestion_timestamp", F.current_timestamp()) \
    .withColumn("ingestion_date", F.current_date()) \
    .withColumn("source_system", F.lit("manufacturing_mes_demo")) \
    .withColumn("execution_id", F.lit(execution_id))

rows_genealogy = genealogy_df.count()
print(f"✓ Generated {rows_genealogy} genealogy records")

# COMMAND ----------

target_table_genealogy = f"{catalog_name}.{bronze_schema}.batch_genealogy"

genealogy_df.write \
    .format("delta") \
    .mode("append") \
    .partitionBy("ingestion_date") \
    .saveAsTable(target_table_genealogy)

spark.sql(f"""
    ALTER TABLE {target_table_genealogy}
    SET TBLPROPERTIES (
        'delta.enableChangeDataFeed' = 'true'
    )
""")

print(f"✓ Genealogy data written to {target_table_genealogy}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Log Pipeline Execution

# COMMAND ----------

total_rows_ingested = rows_read + rows_read_process + rows_genealogy

spark.sql(f"""
    INSERT INTO {catalog_name}.{meta_schema}.pipeline_execution_log
    VALUES (
        '{execution_id}',
        '{pipeline_name}',
        'bronze',
        'synthetic_demo_data',
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
        'demo_manufacturing_ingestion',
        map('execution_id', '{execution_id}', 'mode', 'demo'),
        current_timestamp()
    )
""")

print(f"\n{'='*60}")
print(f"Pipeline Execution Summary (DEMO MODE)")
print(f"{'='*60}")
print(f"Execution ID: {execution_id}")
print(f"Status: SUCCESS")
print(f"Total Rows Generated: {total_rows_ingested:,}")
print(f"  - Batch Records: {rows_read}")
print(f"  - Process Data: {rows_read_process:,}")
print(f"  - Genealogy: {rows_genealogy}")
print(f"Completed at: {datetime.now()}")
print(f"{'='*60}")
print(f"\n✅ Demo data successfully loaded to Bronze layer!")
print(f"   You can now proceed to Silver layer transformations.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC
# MAGIC ✅ **Demo Manufacturing Data Generated and Loaded**
# MAGIC
# MAGIC **Tables Populated:**
# MAGIC - `manufacturing_batch_records` - 50 synthetic batches
# MAGIC - `manufacturing_process_data` - Time-series sensor data (temperature, pH, DO, etc.)
# MAGIC - `batch_genealogy` - Material traceability records
# MAGIC
# MAGIC **Data Characteristics:**
# MAGIC - Multiple products (BIO, VAX, SM series)
# MAGIC - Multiple sites (US, EU, CN)
# MAGIC - Realistic batch types (Commercial, Clinical, Development)
# MAGIC - Time-series process parameters with controlled variation
# MAGIC - Material genealogy with parent-child relationships
# MAGIC
# MAGIC **Next Steps:**
# MAGIC - Run Silver layer: `02_silver/01_silver_dimensions_scd2`
# MAGIC - Transform to Kimball star schema
# MAGIC - Create Gold layer analytics
# MAGIC
# MAGIC **To Use Real Data:**
# MAGIC - Configure secrets for MES, LIMS connections
# MAGIC - Use `01_bronze_manufacturing_ingestion.py` (production version)
