# Databricks notebook source
# MAGIC %md
# MAGIC # Bronze Layer: Clinical Trial & LIMS Data Ingestion
# MAGIC
# MAGIC **Purpose:** Ingest raw data from Clinical Trial systems (EDC) and Laboratory Information Management Systems (LIMS)
# MAGIC
# MAGIC **Source Systems:**
# MAGIC - Medidata Rave (EDC - Electronic Data Capture)
# MAGIC - LabWare/Thermo SampleManager (LIMS)
# MAGIC - Oracle Argus (Safety Database)
# MAGIC
# MAGIC **Data Types:**
# MAGIC - Clinical trial subjects
# MAGIC - Adverse events
# MAGIC - Laboratory test results
# MAGIC - QC sample data
# MAGIC - Analytical test results
# MAGIC
# MAGIC **Extraction Method:** REST API for EDC, JDBC for LIMS
# MAGIC
# MAGIC **Compliance:** CDISC SDTM standards, 21 CFR Part 11, ALCOA+

# COMMAND ----------

import uuid
import requests
import json
from datetime import datetime
from pyspark.sql import functions as F
from pyspark.sql.types import *
from delta.tables import DeltaTable

# Configuration
catalog_name = "pharma_platform"
bronze_schema = "bronze_raw"
meta_schema = "metadata"

execution_id = str(uuid.uuid4())
pipeline_name = "bronze_clinical_lims_ingestion"

print(f"Execution ID: {execution_id}")
print(f"Pipeline: {pipeline_name}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. LIMS Data Ingestion - Analytical Test Results

# COMMAND ----------

# LIMS JDBC connection (Oracle)
lims_hostname = dbutils.secrets.get(scope="pharma_platform", key="lims_jdbc_hostname")
lims_port = dbutils.secrets.get(scope="pharma_platform", key="lims_jdbc_port")
lims_service = dbutils.secrets.get(scope="pharma_platform", key="lims_service_name")
lims_username = dbutils.secrets.get(scope="pharma_platform", key="lims_username")
lims_password = dbutils.secrets.get(scope="pharma_platform", key="lims_password")

lims_jdbc_url = f"jdbc:oracle:thin:@{lims_hostname}:{lims_port}/{lims_service}"

lims_properties = {
    "user": lims_username,
    "password": lims_password,
    "driver": "oracle.jdbc.driver.OracleDriver"
}

# COMMAND ----------

# Query analytical test results
target_table_analytical = f"{catalog_name}.{bronze_schema}.analytical_test_results"

analytical_query = """
(SELECT
    test_id,
    sample_id,
    batch_number,
    material_code,
    test_method_code,
    test_method_name,
    test_category,
    analytical_technique,
    instrument_id,
    test_result_value,
    result_uom,
    specification_min,
    specification_max,
    replicate_1,
    replicate_2,
    replicate_3,
    mean_value,
    std_deviation,
    rsd_percent,
    pass_fail_status,
    analyst_id,
    reviewed_by,
    approved_by,
    test_date,
    review_date,
    approval_date,
    result_timestamp,
    lims_status,
    comments
FROM lims.analytical_results
WHERE result_timestamp >= SYSDATE - 30
) analytical_data
"""

# Read from LIMS
analytical_df = spark.read.jdbc(
    url=lims_jdbc_url,
    table=analytical_query,
    properties=lims_properties
)

# Add metadata
analytical_df_with_meta = analytical_df \
    .withColumn("ingestion_timestamp", F.current_timestamp()) \
    .withColumn("ingestion_date", F.current_date()) \
    .withColumn("source_system", F.lit("lims")) \
    .withColumn("execution_id", F.lit(execution_id))

rows_analytical = analytical_df_with_meta.count()
print(f"Analytical test results read: {rows_analytical}")

# Write to Delta
if rows_analytical > 0:
    analytical_df_with_meta.write \
        .format("delta") \
        .mode("append") \
        .option("mergeSchema", "true") \
        .partitionBy("ingestion_date") \
        .saveAsTable(target_table_analytical)

    spark.sql(f"""
        ALTER TABLE {target_table_analytical}
        SET TBLPROPERTIES (
            'delta.enableChangeDataFeed' = 'true',
            'delta.autoOptimize.optimizeWrite' = 'true'
        )
    """)

    print(f"✓ Analytical test results ingested: {rows_analytical} rows")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. LIMS Data - QC Sample Data

# COMMAND ----------

target_table_samples = f"{catalog_name}.{bronze_schema}.qc_sample_data"

sample_query = """
(SELECT
    sample_id,
    sample_number,
    sample_type,
    batch_number,
    material_code,
    sampling_point,
    sampling_datetime,
    sampled_by,
    sample_quantity,
    sample_uom,
    storage_location,
    storage_condition,
    container_type,
    sample_status,
    created_date,
    modified_date
FROM lims.samples
WHERE created_date >= SYSDATE - 30
) sample_data
"""

sample_df = spark.read.jdbc(
    url=lims_jdbc_url,
    table=sample_query,
    properties=lims_properties
) \
    .withColumn("ingestion_timestamp", F.current_timestamp()) \
    .withColumn("ingestion_date", F.current_date()) \
    .withColumn("source_system", F.lit("lims")) \
    .withColumn("execution_id", F.lit(execution_id))

rows_samples = sample_df.count()

if rows_samples > 0:
    sample_df.write \
        .format("delta") \
        .mode("append") \
        .partitionBy("ingestion_date") \
        .saveAsTable(target_table_samples)

    print(f"✓ QC samples ingested: {rows_samples} rows")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Clinical Trial Data - EDC API Integration

# COMMAND ----------

# MAGIC %md
# MAGIC ### 3.1 Define API Helper Functions

# COMMAND ----------

def fetch_clinical_data_api(endpoint, study_id, last_modified_date=None):
    """
    Fetch clinical trial data from Medidata Rave API

    Args:
        endpoint: API endpoint (subjects, adverse_events, etc.)
        study_id: Study identifier
        last_modified_date: For incremental loads

    Returns:
        JSON response data
    """
    # API configuration
    api_base_url = dbutils.secrets.get(scope="pharma_platform", key="edc_api_url")
    api_key = dbutils.secrets.get(scope="pharma_platform", key="edc_api_key")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    params = {
        "study_id": study_id
    }

    if last_modified_date:
        params["last_modified"] = last_modified_date

    url = f"{api_base_url}/{endpoint}"

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        return None

# COMMAND ----------

# MAGIC %md
# MAGIC ### 3.2 Ingest Clinical Subject Data

# COMMAND ----------

target_table_subjects = f"{catalog_name}.{bronze_schema}.clinical_subjects"

# Fetch data from API (example for study PROTO-001)
# In production, loop through active studies
study_ids = ["PROTO-001", "PROTO-002", "PROTO-003"]

all_subjects = []

for study_id in study_ids:
    subjects_data = fetch_clinical_data_api("subjects", study_id)

    if subjects_data and "data" in subjects_data:
        for subject in subjects_data["data"]:
            subject["study_id"] = study_id
            subject["ingestion_timestamp"] = datetime.now().isoformat()
            subject["ingestion_date"] = datetime.now().date().isoformat()
            subject["source_system"] = "edc_clinical"
            subject["execution_id"] = execution_id
            all_subjects.append(subject)

# Convert to Spark DataFrame
if all_subjects:
    # Define schema
    subjects_schema = StructType([
        StructField("subject_id", StringType(), False),
        StructField("study_id", StringType(), False),
        StructField("site_id", StringType(), True),
        StructField("subject_number", StringType(), True),
        StructField("screening_number", StringType(), True),
        StructField("enrollment_date", StringType(), True),
        StructField("randomization_date", StringType(), True),
        StructField("treatment_arm", StringType(), True),
        StructField("age", IntegerType(), True),
        StructField("gender", StringType(), True),
        StructField("ethnicity", StringType(), True),
        StructField("subject_status", StringType(), True),
        StructField("consent_date", StringType(), True),
        StructField("withdrawal_date", StringType(), True),
        StructField("completion_date", StringType(), True),
        StructField("updated_date", StringType(), True),
        StructField("ingestion_timestamp", StringType(), True),
        StructField("ingestion_date", StringType(), True),
        StructField("source_system", StringType(), True),
        StructField("execution_id", StringType(), True)
    ])

    subjects_df = spark.createDataFrame(all_subjects, schema=subjects_schema)

    # Convert date strings to proper types
    subjects_df = subjects_df \
        .withColumn("enrollment_date", F.to_date("enrollment_date")) \
        .withColumn("randomization_date", F.to_date("randomization_date")) \
        .withColumn("consent_date", F.to_date("consent_date")) \
        .withColumn("ingestion_timestamp", F.to_timestamp("ingestion_timestamp")) \
        .withColumn("ingestion_date", F.to_date("ingestion_date"))

    rows_subjects = subjects_df.count()

    # Write to Delta
    subjects_df.write \
        .format("delta") \
        .mode("append") \
        .partitionBy("ingestion_date", "study_id") \
        .saveAsTable(target_table_subjects)

    print(f"✓ Clinical subjects ingested: {rows_subjects} rows")
else:
    rows_subjects = 0
    print("No clinical subject data fetched")

# COMMAND ----------

# MAGIC %md
# MAGIC ### 3.3 Ingest Adverse Events

# COMMAND ----------

target_table_ae = f"{catalog_name}.{bronze_schema}.clinical_adverse_events"

all_adverse_events = []

for study_id in study_ids:
    ae_data = fetch_clinical_data_api("adverse_events", study_id)

    if ae_data and "data" in ae_data:
        for ae in ae_data["data"]:
            ae["study_id"] = study_id
            ae["ingestion_timestamp"] = datetime.now().isoformat()
            ae["ingestion_date"] = datetime.now().date().isoformat()
            ae["source_system"] = "edc_clinical"
            ae["execution_id"] = execution_id
            all_adverse_events.append(ae)

if all_adverse_events:
    ae_schema = StructType([
        StructField("ae_id", StringType(), False),
        StructField("subject_id", StringType(), False),
        StructField("study_id", StringType(), False),
        StructField("ae_term", StringType(), True),
        StructField("ae_verbatim", StringType(), True),
        StructField("meddra_code", StringType(), True),
        StructField("meddra_pt", StringType(), True),
        StructField("severity", StringType(), True),
        StructField("seriousness", StringType(), True),
        StructField("relationship_to_drug", StringType(), True),
        StructField("onset_date", StringType(), True),
        StructField("resolution_date", StringType(), True),
        StructField("outcome", StringType(), True),
        StructField("action_taken", StringType(), True),
        StructField("reported_date", StringType(), True),
        StructField("ingestion_timestamp", StringType(), True),
        StructField("ingestion_date", StringType(), True),
        StructField("source_system", StringType(), True),
        StructField("execution_id", StringType(), True)
    ])

    ae_df = spark.createDataFrame(all_adverse_events, schema=ae_schema) \
        .withColumn("onset_date", F.to_date("onset_date")) \
        .withColumn("resolution_date", F.to_date("resolution_date")) \
        .withColumn("reported_date", F.to_date("reported_date")) \
        .withColumn("ingestion_timestamp", F.to_timestamp("ingestion_timestamp")) \
        .withColumn("ingestion_date", F.to_date("ingestion_date"))

    rows_ae = ae_df.count()

    ae_df.write \
        .format("delta") \
        .mode("append") \
        .partitionBy("ingestion_date", "study_id") \
        .saveAsTable(target_table_ae)

    print(f"✓ Adverse events ingested: {rows_ae} rows")
else:
    rows_ae = 0
    print("No adverse event data fetched")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Data Quality Checks

# COMMAND ----------

# Check 1: Analytical results within specification
out_of_spec_count = spark.sql(f"""
    SELECT COUNT(*) as oos_count
    FROM {target_table_analytical}
    WHERE pass_fail_status = 'FAIL'
      AND ingestion_date = current_date()
""").collect()[0][0]

spark.sql(f"""
    INSERT INTO {catalog_name}.{meta_schema}.data_quality_metrics
    VALUES (
        '{str(uuid.uuid4())}',
        '{execution_id}',
        '{target_table_analytical}',
        'out_of_specification_check',
        'validity',
        'INFO',
        'Monitor OOS results',
        '{out_of_spec_count}',
        NULL,
        {out_of_spec_count},
        'MEDIUM',
        current_timestamp()
    )
""")

print(f"DQ Check - Out of Specification results: {out_of_spec_count}")

# Check 2: Clinical subjects with missing critical data
missing_consent = spark.sql(f"""
    SELECT COUNT(*) as missing_count
    FROM {target_table_subjects}
    WHERE consent_date IS NULL
      AND ingestion_date = current_date()
""").collect()[0][0] if rows_subjects > 0 else 0

if rows_subjects > 0:
    spark.sql(f"""
        INSERT INTO {catalog_name}.{meta_schema}.data_quality_metrics
        VALUES (
            '{str(uuid.uuid4())}',
            '{execution_id}',
            '{target_table_subjects}',
            'missing_consent_date',
            'completeness',
            '{("FAIL" if missing_consent > 0 else "PASS")}',
            '0',
            '{missing_consent}',
            NULL,
            {missing_consent},
            '{("HIGH" if missing_consent > 0 else "LOW")}',
            current_timestamp()
        )
    """)

    print(f"DQ Check - Missing consent date: {'FAIL' if missing_consent > 0 else 'PASS'}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Log Pipeline Execution

# COMMAND ----------

total_rows = rows_analytical + rows_samples + rows_subjects + rows_ae

spark.sql(f"""
    INSERT INTO {catalog_name}.{meta_schema}.pipeline_execution_log
    VALUES (
        '{execution_id}',
        '{pipeline_name}',
        'bronze',
        'lims, edc_clinical',
        '{target_table_analytical}, {target_table_samples}, {target_table_subjects}, {target_table_ae}',
        current_timestamp(),
        current_timestamp(),
        'SUCCESS',
        {total_rows},
        {total_rows},
        0,
        0,
        NULL,
        current_user(),
        '{dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get()}',
        map('execution_id', '{execution_id}'),
        current_timestamp()
    )
""")

print(f"\n{'='*60}")
print(f"Pipeline Execution Summary")
print(f"{'='*60}")
print(f"Execution ID: {execution_id}")
print(f"Status: SUCCESS")
print(f"Total Rows Ingested: {total_rows}")
print(f"  - Analytical Results: {rows_analytical}")
print(f"  - QC Samples: {rows_samples}")
print(f"  - Clinical Subjects: {rows_subjects}")
print(f"  - Adverse Events: {rows_ae}")
print(f"Completed at: {datetime.now()}")
print(f"{'='*60}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC
# MAGIC ✅ **Clinical and LIMS data ingested into Bronze layer**
# MAGIC
# MAGIC **Tables Created:**
# MAGIC - `analytical_test_results` - LIMS analytical testing results
# MAGIC - `qc_sample_data` - Sample management data
# MAGIC - `clinical_subjects` - Clinical trial subject data (CDISC compliant)
# MAGIC - `clinical_adverse_events` - Safety data (MedDRA coded)
# MAGIC
# MAGIC **Features:**
# MAGIC - Multi-source integration (JDBC for LIMS, REST API for EDC)
# MAGIC - Partitioning by ingestion_date and study_id/test_type
# MAGIC - Change Data Feed for audit trail
# MAGIC - CDISC SDTM alignment for clinical data
# MAGIC - Data quality validation with metadata logging
# MAGIC
# MAGIC **Next Steps:**
# MAGIC - Transform to Silver layer dimensional model
# MAGIC - Apply CDISC mappings for clinical data
# MAGIC - Integrate with safety database (Argus)
