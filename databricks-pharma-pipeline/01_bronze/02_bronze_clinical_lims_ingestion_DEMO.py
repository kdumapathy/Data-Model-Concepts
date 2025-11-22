# Databricks notebook source
# MAGIC %md
# MAGIC # Bronze Layer: Clinical & LIMS Data Ingestion (DEMO VERSION)
# MAGIC
# MAGIC **Purpose:** Demo version that generates synthetic clinical and LIMS data
# MAGIC
# MAGIC **Use this notebook to:**
# MAGIC - Test the pipeline without actual LIMS/EDC systems
# MAGIC - Validate analytical and clinical data flows
# MAGIC - Demonstrate regulatory-compliant data structures
# MAGIC
# MAGIC **For production:** Use `02_bronze_clinical_lims_ingestion.py` with real connections

# COMMAND ----------

import uuid
import random
from datetime import datetime, timedelta
from pyspark.sql import functions as F
from pyspark.sql.types import *

# Configuration
catalog_name = "pharma_platform"
bronze_schema = "bronze_raw"
meta_schema = "metadata"

execution_id = str(uuid.uuid4())
pipeline_name = "bronze_clinical_lims_ingestion_demo"

print(f"Execution ID: {execution_id}")
print(f"Pipeline: {pipeline_name}")
print("\n⚠️  DEMO MODE: Generating synthetic LIMS and clinical data")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Generate Synthetic Analytical Test Results

# COMMAND ----------

def generate_analytical_results(num_tests=200):
    """Generate synthetic LIMS analytical test results"""

    test_methods = [
        ('HPLC-001', 'HPLC Purity', 'purity', 'HPLC'),
        ('SEC-001', 'Size Exclusion Chromatography', 'purity', 'SEC'),
        ('ELISA-001', 'Potency ELISA', 'potency', 'ELISA'),
        ('ENDOTOXIN-001', 'LAL Endotoxin', 'safety', 'LAL'),
        ('pH-001', 'pH Measurement', 'identity', 'pH_meter'),
        ('OSMOLALITY-001', 'Osmolality', 'identity', 'Osmometer'),
        ('BIOBURDEN-001', 'Bioburden Testing', 'safety', 'Microbiology'),
        ('STERILITY-001', 'Sterility Test', 'safety', 'Microbiology')
    ]

    materials = [f'FP-B2025-{i:05d}' for i in range(1000, 1050)]
    batches = [f'B2025-{i:05d}' for i in range(1000, 1050)]

    results = []
    test_id = 1

    for _ in range(num_tests):
        method_code, method_name, category, technique = random.choice(test_methods)

        # Define spec limits based on test type
        if 'HPLC' in method_code:
            spec_min, spec_max, target = 95.0, 105.0, 100.0
        elif 'ELISA' in method_code:
            spec_min, spec_max, target = 80.0, 120.0, 100.0
        elif 'ENDOTOXIN' in method_code:
            spec_min, spec_max, target = 0.0, 0.5, 0.1
        elif 'pH' in method_code:
            spec_min, spec_max, target = 6.8, 7.6, 7.2
        else:
            spec_min, spec_max, target = 90.0, 110.0, 100.0

        # Generate result value (95% pass rate)
        if random.random() < 0.95:
            result_value = random.uniform(spec_min + 0.1*(spec_max-spec_min),
                                         spec_max - 0.1*(spec_max-spec_min))
            pass_fail = 'PASS'
        else:
            result_value = random.uniform(spec_max, spec_max * 1.2)
            pass_fail = 'FAIL'

        # Replicates
        rep1 = result_value + random.uniform(-0.05, 0.05) * result_value
        rep2 = result_value + random.uniform(-0.05, 0.05) * result_value
        rep3 = result_value + random.uniform(-0.05, 0.05) * result_value

        mean_val = (rep1 + rep2 + rep3) / 3
        std_dev = ((rep1-mean_val)**2 + (rep2-mean_val)**2 + (rep3-mean_val)**2)**0.5 / 2
        rsd = (std_dev / mean_val * 100) if mean_val != 0 else 0

        test_date = datetime.now() - timedelta(days=random.randint(1, 60))

        results.append({
            'test_id': f'TEST-{test_id:06d}',
            'sample_id': f'SAMP-{test_id:06d}',
            'batch_number': random.choice(batches),
            'material_code': random.choice(materials),
            'test_method_code': method_code,
            'test_method_name': method_name,
            'test_category': category,
            'analytical_technique': technique,
            'instrument_id': f'INST-{random.randint(100,999)}',
            'test_result_value': round(result_value, 3),
            'result_uom': 'Percent' if category in ['purity', 'potency'] else 'EU/mL' if 'ENDOTOXIN' in method_code else 'pH',
            'specification_min': spec_min,
            'specification_max': spec_max,
            'replicate_1': round(rep1, 3),
            'replicate_2': round(rep2, 3),
            'replicate_3': round(rep3, 3),
            'mean_value': round(mean_val, 3),
            'std_deviation': round(std_dev, 4),
            'rsd_percent': round(rsd, 2),
            'pass_fail_status': pass_fail,
            'analyst_id': f'ANALYST-{random.randint(10,99)}',
            'reviewed_by': f'REVIEWER-{random.randint(10,99)}',
            'approved_by': f'APPROVER-{random.randint(10,99)}',
            'test_date': test_date,
            'review_date': test_date + timedelta(days=1),
            'approval_date': test_date + timedelta(days=2),
            'result_timestamp': test_date,
            'lims_status': 'APPROVED',
            'comments': None if pass_fail == 'PASS' else 'Out of specification - investigation required'
        })
        test_id += 1

    return results

analytical_data = generate_analytical_results(200)

analytical_schema = StructType([
    StructField("test_id", StringType(), False),
    StructField("sample_id", StringType(), True),
    StructField("batch_number", StringType(), True),
    StructField("material_code", StringType(), True),
    StructField("test_method_code", StringType(), True),
    StructField("test_method_name", StringType(), True),
    StructField("test_category", StringType(), True),
    StructField("analytical_technique", StringType(), True),
    StructField("instrument_id", StringType(), True),
    StructField("test_result_value", DoubleType(), True),
    StructField("result_uom", StringType(), True),
    StructField("specification_min", DoubleType(), True),
    StructField("specification_max", DoubleType(), True),
    StructField("replicate_1", DoubleType(), True),
    StructField("replicate_2", DoubleType(), True),
    StructField("replicate_3", DoubleType(), True),
    StructField("mean_value", DoubleType(), True),
    StructField("std_deviation", DoubleType(), True),
    StructField("rsd_percent", DoubleType(), True),
    StructField("pass_fail_status", StringType(), True),
    StructField("analyst_id", StringType(), True),
    StructField("reviewed_by", StringType(), True),
    StructField("approved_by", StringType(), True),
    StructField("test_date", TimestampType(), True),
    StructField("review_date", TimestampType(), True),
    StructField("approval_date", TimestampType(), True),
    StructField("result_timestamp", TimestampType(), True),
    StructField("lims_status", StringType(), True),
    StructField("comments", StringType(), True)
])

analytical_df = spark.createDataFrame(analytical_data, schema=analytical_schema) \
    .withColumn("ingestion_timestamp", F.current_timestamp()) \
    .withColumn("ingestion_date", F.current_date()) \
    .withColumn("source_system", F.lit("lims_demo")) \
    .withColumn("execution_id", F.lit(execution_id))

rows_analytical = analytical_df.count()
print(f"✓ Generated {rows_analytical} analytical test results")

# COMMAND ----------

target_table_analytical = f"{catalog_name}.{bronze_schema}.analytical_test_results"

analytical_df.write \
    .format("delta") \
    .mode("append") \
    .partitionBy("ingestion_date") \
    .saveAsTable(target_table_analytical)

spark.sql(f"""
    ALTER TABLE {target_table_analytical}
    SET TBLPROPERTIES (
        'delta.enableChangeDataFeed' = 'true',
        'delta.autoOptimize.optimizeWrite' = 'true'
    )
""")

print(f"✓ Analytical results written to {target_table_analytical}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Generate QC Sample Data

# COMMAND ----------

def generate_qc_samples(num_samples=100):
    """Generate QC sample records"""

    sample_types = ['Finished Product', 'In-Process', 'Stability', 'Reference Standard', 'Raw Material']
    batches = [f'B2025-{i:05d}' for i in range(1000, 1050)]
    materials = [f'FP-B2025-{i:05d}' for i in range(1000, 1050)]

    samples = []
    for i in range(1, num_samples+1):
        sample_date = datetime.now() - timedelta(days=random.randint(1, 60))

        samples.append({
            'sample_id': f'SAMP-{i:06d}',
            'sample_number': f'S{datetime.now().year}-{i:05d}',
            'sample_type': random.choice(sample_types),
            'batch_number': random.choice(batches),
            'material_code': random.choice(materials),
            'sampling_point': random.choice(['Final Bulk', 'Post-Filtration', 'Pre-Filling', 'Post-Fill']),
            'sampling_datetime': sample_date,
            'sampled_by': f'SAMPLER-{random.randint(10,99)}',
            'sample_quantity': round(random.uniform(10, 500), 1),
            'sample_uom': 'mL',
            'storage_location': f'FRIDGE-{random.randint(1,10)}-SHELF-{random.randint(1,5)}',
            'storage_condition': random.choice(['2-8°C', '-20°C', '-80°C', 'Room Temperature']),
            'container_type': random.choice(['Vial', 'Bottle', 'Tube']),
            'sample_status': random.choice(['Available', 'In Testing', 'Consumed', 'Discarded']),
            'created_date': sample_date,
            'modified_date': sample_date + timedelta(days=random.randint(0, 5))
        })

    return samples

sample_data = generate_qc_samples(100)

sample_schema = StructType([
    StructField("sample_id", StringType(), False),
    StructField("sample_number", StringType(), True),
    StructField("sample_type", StringType(), True),
    StructField("batch_number", StringType(), True),
    StructField("material_code", StringType(), True),
    StructField("sampling_point", StringType(), True),
    StructField("sampling_datetime", TimestampType(), True),
    StructField("sampled_by", StringType(), True),
    StructField("sample_quantity", DoubleType(), True),
    StructField("sample_uom", StringType(), True),
    StructField("storage_location", StringType(), True),
    StructField("storage_condition", StringType(), True),
    StructField("container_type", StringType(), True),
    StructField("sample_status", StringType(), True),
    StructField("created_date", TimestampType(), True),
    StructField("modified_date", TimestampType(), True)
])

sample_df = spark.createDataFrame(sample_data, schema=sample_schema) \
    .withColumn("ingestion_timestamp", F.current_timestamp()) \
    .withColumn("ingestion_date", F.current_date()) \
    .withColumn("source_system", F.lit("lims_demo")) \
    .withColumn("execution_id", F.lit(execution_id))

rows_samples = sample_df.count()

target_table_samples = f"{catalog_name}.{bronze_schema}.qc_sample_data"

sample_df.write \
    .format("delta") \
    .mode("append") \
    .partitionBy("ingestion_date") \
    .saveAsTable(target_table_samples)

print(f"✓ Generated {rows_samples} QC samples")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Generate Clinical Trial Subjects

# COMMAND ----------

def generate_clinical_subjects(num_subjects=150):
    """Generate synthetic clinical trial subjects (CDISC-aligned)"""

    studies = ['PROTO-001', 'PROTO-002', 'PROTO-003']
    sites = ['SITE-101', 'SITE-102', 'SITE-201', 'SITE-202', 'SITE-301']
    treatment_arms = ['Active_High_Dose', 'Active_Low_Dose', 'Placebo']
    statuses = ['Enrolled', 'Completed', 'Withdrawn', 'Screen Failure']
    genders = ['Male', 'Female']
    ethnicities = ['Caucasian', 'African American', 'Asian', 'Hispanic', 'Other']

    subjects = []
    base_date = datetime.now() - timedelta(days=365)

    for i in range(1, num_subjects+1):
        study = random.choice(studies)
        site = random.choice(sites)
        enroll_date = base_date + timedelta(days=random.randint(0, 300))

        subjects.append({
            'subject_id': f'{study}-{site}-{i:04d}',
            'study_id': study,
            'site_id': site,
            'subject_number': f'{i:04d}',
            'screening_number': f'SCR-{i:05d}',
            'enrollment_date': enroll_date.date(),
            'randomization_date': (enroll_date + timedelta(days=7)).date() if random.random() > 0.1 else None,
            'treatment_arm': random.choice(treatment_arms) if random.random() > 0.1 else None,
            'age': random.randint(18, 75),
            'gender': random.choice(genders),
            'ethnicity': random.choice(ethnicities),
            'subject_status': random.choice(statuses),
            'consent_date': (enroll_date - timedelta(days=2)).date(),
            'withdrawal_date': (enroll_date + timedelta(days=random.randint(30, 180))).date() if random.random() < 0.15 else None,
            'completion_date': (enroll_date + timedelta(days=180)).date() if random.random() > 0.2 else None,
            'updated_date': datetime.now().date()
        })

    return subjects

subject_data = generate_clinical_subjects(150)

subject_schema = StructType([
    StructField("subject_id", StringType(), False),
    StructField("study_id", StringType(), False),
    StructField("site_id", StringType(), True),
    StructField("subject_number", StringType(), True),
    StructField("screening_number", StringType(), True),
    StructField("enrollment_date", DateType(), True),
    StructField("randomization_date", DateType(), True),
    StructField("treatment_arm", StringType(), True),
    StructField("age", IntegerType(), True),
    StructField("gender", StringType(), True),
    StructField("ethnicity", StringType(), True),
    StructField("subject_status", StringType(), True),
    StructField("consent_date", DateType(), True),
    StructField("withdrawal_date", DateType(), True),
    StructField("completion_date", DateType(), True),
    StructField("updated_date", DateType(), True)
])

subjects_df = spark.createDataFrame(subject_data, schema=subject_schema) \
    .withColumn("ingestion_timestamp", F.current_timestamp()) \
    .withColumn("ingestion_date", F.current_date()) \
    .withColumn("source_system", F.lit("edc_clinical_demo")) \
    .withColumn("execution_id", F.lit(execution_id))

rows_subjects = subjects_df.count()

target_table_subjects = f"{catalog_name}.{bronze_schema}.clinical_subjects"

subjects_df.write \
    .format("delta") \
    .mode("append") \
    .partitionBy("ingestion_date", "study_id") \
    .saveAsTable(target_table_subjects)

print(f"✓ Generated {rows_subjects} clinical subjects")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Generate Adverse Events

# COMMAND ----------

def generate_adverse_events(subjects_df, ae_rate=0.4):
    """Generate adverse events for clinical subjects"""

    ae_terms = [
        ('Headache', 'Mild'),
        ('Nausea', 'Mild'),
        ('Fatigue', 'Mild'),
        ('Injection Site Reaction', 'Moderate'),
        ('Fever', 'Moderate'),
        ('Dizziness', 'Mild'),
        ('Rash', 'Moderate'),
        ('Hypersensitivity', 'Severe')
    ]

    relationships = ['Not Related', 'Unlikely', 'Possible', 'Probable', 'Definite']
    outcomes = ['Recovered', 'Recovering', 'Ongoing', 'Recovered with Sequelae']
    actions = ['None', 'Dose Reduced', 'Drug Withdrawn', 'Dose Not Changed']

    adverse_events = []
    ae_id = 1

    for subject_row in subjects_df.collect():
        if random.random() < ae_rate:  # 40% of subjects have AEs
            num_aes = random.randint(1, 3)

            for _ in range(num_aes):
                ae_term, severity = random.choice(ae_terms)
                onset = subject_row['enrollment_date'] + timedelta(days=random.randint(1, 150))

                adverse_events.append({
                    'ae_id': f'AE-{ae_id:06d}',
                    'subject_id': subject_row['subject_id'],
                    'study_id': subject_row['study_id'],
                    'ae_term': ae_term,
                    'ae_verbatim': f'{ae_term} reported by subject',
                    'meddra_code': f'MED-{random.randint(10000000, 99999999)}',
                    'meddra_pt': ae_term,
                    'severity': severity,
                    'seriousness': 'No' if severity != 'Severe' else random.choice(['Yes', 'No']),
                    'relationship_to_drug': random.choice(relationships),
                    'onset_date': onset,
                    'resolution_date': onset + timedelta(days=random.randint(1, 14)) if random.random() > 0.2 else None,
                    'outcome': random.choice(outcomes),
                    'action_taken': random.choice(actions),
                    'reported_date': onset + timedelta(days=random.randint(0, 2))
                })
                ae_id += 1

    return adverse_events

ae_data = generate_adverse_events(subjects_df, ae_rate=0.4)

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
    StructField("onset_date", DateType(), True),
    StructField("resolution_date", DateType(), True),
    StructField("outcome", StringType(), True),
    StructField("action_taken", StringType(), True),
    StructField("reported_date", DateType(), True)
])

ae_df = spark.createDataFrame(ae_data, schema=ae_schema) \
    .withColumn("ingestion_timestamp", F.current_timestamp()) \
    .withColumn("ingestion_date", F.current_date()) \
    .withColumn("source_system", F.lit("edc_clinical_demo")) \
    .withColumn("execution_id", F.lit(execution_id))

rows_ae = ae_df.count()

target_table_ae = f"{catalog_name}.{bronze_schema}.clinical_adverse_events"

ae_df.write \
    .format("delta") \
    .mode("append") \
    .partitionBy("ingestion_date", "study_id") \
    .saveAsTable(target_table_ae)

print(f"✓ Generated {rows_ae} adverse events")

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
        'synthetic_demo_data',
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
        'demo_clinical_lims_ingestion',
        map('execution_id', '{execution_id}', 'mode', 'demo')
    )
""")

print(f"\n{'='*60}")
print(f"Pipeline Execution Summary (DEMO MODE)")
print(f"{'='*60}")
print(f"Execution ID: {execution_id}")
print(f"Status: SUCCESS")
print(f"Total Rows Generated: {total_rows}")
print(f"  - Analytical Results: {rows_analytical}")
print(f"  - QC Samples: {rows_samples}")
print(f"  - Clinical Subjects: {rows_subjects}")
print(f"  - Adverse Events: {rows_ae}")
print(f"Completed at: {datetime.now()}")
print(f"{'='*60}")
print(f"\n✅ Demo LIMS and clinical data successfully loaded!")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC
# MAGIC ✅ **Demo Clinical and LIMS Data Generated**
# MAGIC
# MAGIC **LIMS Tables:**
# MAGIC - `analytical_test_results` - 200 tests with specifications, replicates, pass/fail status
# MAGIC - `qc_sample_data` - 100 samples with storage conditions and tracking
# MAGIC
# MAGIC **Clinical Tables:**
# MAGIC - `clinical_subjects` - 150 subjects across 3 studies (CDISC-aligned)
# MAGIC - `clinical_adverse_events` - Adverse events with MedDRA coding
# MAGIC
# MAGIC **Data Quality:**
# MAGIC - 95% pass rate for analytical tests
# MAGIC - 40% of subjects have adverse events
# MAGIC - Realistic temporal relationships
# MAGIC - Regulatory-compliant data structures
# MAGIC
# MAGIC **Next Steps:**
# MAGIC - Proceed to Silver layer transformations
# MAGIC - Build dimensional model
# MAGIC - Create Gold layer analytics
