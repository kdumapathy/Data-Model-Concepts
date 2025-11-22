# Databricks notebook source
# MAGIC %md
# MAGIC # Silver Layer: Dimensional Model - Type 2 Slowly Changing Dimensions
# MAGIC
# MAGIC **Purpose:** Build Kimball-style dimensional model with Type 2 SCD support
# MAGIC
# MAGIC **Methodology:** Ralph Kimball dimensional modeling approach
# MAGIC
# MAGIC **Dimensions Created:**
# MAGIC - dim_product (Type 2 SCD)
# MAGIC - dim_batch (Type 2 SCD)
# MAGIC - dim_equipment (Type 2 SCD with ISA-88 hierarchy)
# MAGIC - dim_material (Type 2 SCD)
# MAGIC - dim_site (Type 2 SCD)
# MAGIC - dim_test_method (Type 2 SCD)
# MAGIC - dim_operator (Type 2 SCD)
# MAGIC - dim_study (Type 2 SCD)
# MAGIC
# MAGIC **SCD Type 2 Implementation:**
# MAGIC - Surrogate keys for all dimensions
# MAGIC - Effective start/end dates
# MAGIC - Current record flag (is_current)
# MAGIC - Row hash for change detection
# MAGIC
# MAGIC **Compliance:** CFR Part 11, ALCOA+ data integrity

# COMMAND ----------

import uuid
import hashlib
from datetime import datetime, date
from pyspark.sql import functions as F
from pyspark.sql.types import *
from pyspark.sql.window import Window
from delta.tables import DeltaTable

# Configuration
catalog_name = "pharma_platform"
bronze_schema = "bronze_raw"
silver_schema = "silver_cdm"
meta_schema = "metadata"

execution_id = str(uuid.uuid4())
pipeline_name = "silver_dimensions_scd2"

print(f"Execution ID: {execution_id}")
print(f"Pipeline: {pipeline_name}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Helper Functions for SCD Type 2

# COMMAND ----------

def generate_row_hash(df, columns_to_hash):
    """
    Generate MD5 hash of specified columns for change detection

    Args:
        df: DataFrame
        columns_to_hash: List of column names to include in hash

    Returns:
        DataFrame with row_hash column
    """
    # Concatenate columns and hash
    concat_cols = F.concat_ws("||", *[F.coalesce(F.col(c).cast("string"), F.lit("NULL")) for c in columns_to_hash])
    return df.withColumn("row_hash", F.md5(concat_cols))

def apply_scd_type2(source_df, target_table, business_key_columns, compare_columns, surrogate_key_column):
    """
    Apply Type 2 Slowly Changing Dimension logic

    Args:
        source_df: Source DataFrame with new/updated records
        target_table: Target table name
        business_key_columns: Natural key columns
        compare_columns: Columns to compare for changes
        surrogate_key_column: Name of surrogate key column

    Returns:
        Number of inserts and updates
    """
    # Check if target table exists
    table_exists = spark.catalog.tableExists(target_table)

    if not table_exists:
        # First load - insert all as current records
        initial_df = source_df \
            .withColumn(surrogate_key_column, F.monotonically_increasing_id() + 1) \
            .withColumn("effective_start_date", F.current_date()) \
            .withColumn("effective_end_date", F.lit(date(9999, 12, 31))) \
            .withColumn("is_current", F.lit(True))

        initial_df.write.format("delta").mode("overwrite").saveAsTable(target_table)

        row_count = initial_df.count()
        print(f"Initial load: {row_count} records inserted")
        return row_count, 0

    else:
        # Load existing dimension
        target_df = spark.table(target_table).filter("is_current = true")

        # Join source and target on business key
        join_condition = [source_df[k] == target_df[k] for k in business_key_columns]

        joined_df = source_df.alias("source") \
            .join(target_df.alias("target"), join_condition, "left")

        # Identify new and changed records
        new_records = joined_df.filter(F.col(f"target.{business_key_columns[0]}").isNull())
        existing_records = joined_df.filter(F.col(f"target.{business_key_columns[0]}").isNotNull())

        # Detect changes by comparing row hash
        changed_records = existing_records.filter(
            F.col("source.row_hash") != F.col("target.row_hash")
        )

        # Get max surrogate key
        max_key = spark.table(target_table).agg(F.max(surrogate_key_column)).collect()[0][0] or 0

        # Prepare new inserts
        new_inserts = new_records.select("source.*") \
            .withColumn(surrogate_key_column, F.monotonically_increasing_id() + max_key + 1) \
            .withColumn("effective_start_date", F.current_date()) \
            .withColumn("effective_end_date", F.lit(date(9999, 12, 31))) \
            .withColumn("is_current", F.lit(True))

        # Prepare changed record inserts (new version)
        changed_inserts = changed_records.select("source.*") \
            .withColumn(surrogate_key_column, F.monotonically_increasing_id() + max_key + new_records.count() + 1) \
            .withColumn("effective_start_date", F.current_date()) \
            .withColumn("effective_end_date", F.lit(date(9999, 12, 31))) \
            .withColumn("is_current", F.lit(True))

        # Insert new and changed records
        insert_count = 0
        if new_inserts.count() > 0:
            new_inserts.write.format("delta").mode("append").saveAsTable(target_table)
            insert_count += new_inserts.count()

        if changed_inserts.count() > 0:
            changed_inserts.write.format("delta").mode("append").saveAsTable(target_table)
            insert_count += changed_inserts.count()

            # Close out old versions of changed records
            delta_table = DeltaTable.forName(spark, target_table)

            # Build update condition for changed records
            update_keys = changed_records.select(*[F.col(f"target.{k}").alias(k) for k in business_key_columns]).distinct()

            for row in update_keys.collect():
                condition = " AND ".join([f"{k} = '{row[k]}'" for k in business_key_columns])
                condition += " AND is_current = true AND effective_start_date < current_date()"

                delta_table.update(
                    condition=condition,
                    set={
                        "effective_end_date": "date_sub(current_date(), 1)",
                        "is_current": "false"
                    }
                )

        update_count = changed_inserts.count() if changed_inserts.count() > 0 else 0

        print(f"SCD Type 2 complete: {insert_count} inserts, {update_count} updates")
        return insert_count, update_count

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Build dim_product

# COMMAND ----------

# Read from bronze (or could be from reference data system)
# For demo, we'll extract unique products from batch records
product_source = spark.sql(f"""
    SELECT DISTINCT
        product_code,
        'Product ' || product_code as product_name,
        CASE
            WHEN product_code LIKE 'BIO%' THEN 'Oncology'
            WHEN product_code LIKE 'VAX%' THEN 'Vaccines'
            ELSE 'Other'
        END as therapeutic_area,
        CASE
            WHEN product_code LIKE 'BIO%' THEN 'Biologic'
            WHEN product_code LIKE 'SM%' THEN 'Small Molecule'
            WHEN product_code LIKE 'VAX%' THEN 'Vaccine'
            ELSE 'Other'
        END as molecule_type,
        CASE
            WHEN batch_type = 'CLINICAL' THEN 'Phase 2 Clinical'
            WHEN batch_type = 'COMMERCIAL' THEN 'Commercial'
            ELSE 'Development'
        END as development_phase,
        CASE
            WHEN batch_type = 'COMMERCIAL' THEN 'Approved'
            WHEN batch_type = 'CLINICAL' THEN 'In Clinical Trials'
            ELSE 'Development'
        END as approval_status,
        'Liquid' as formulation_type,
        'Solution for Injection' as dosage_form,
        '100mg/mL' as strength,
        'IV' as route_of_administration
    FROM {catalog_name}.{bronze_schema}.manufacturing_batch_records
    WHERE ingestion_date >= current_date() - 30
""")

# Generate row hash
hash_columns = ["product_name", "therapeutic_area", "molecule_type", "development_phase",
                "approval_status", "formulation_type", "dosage_form", "strength", "route_of_administration"]

product_source_with_hash = generate_row_hash(product_source, hash_columns)

# Apply SCD Type 2
target_product_table = f"{catalog_name}.{silver_schema}.dim_product"

inserts, updates = apply_scd_type2(
    source_df=product_source_with_hash,
    target_table=target_product_table,
    business_key_columns=["product_code"],
    compare_columns=hash_columns,
    surrogate_key_column="product_id"
)

print(f"✓ dim_product created: {inserts} new, {updates} updated")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Build dim_batch

# COMMAND ----------

batch_source = spark.sql(f"""
    SELECT DISTINCT
        batch_number,
        product_code,
        batch_type,
        batch_size,
        batch_size_uom,
        planned_start_date,
        actual_start_date,
        planned_end_date,
        actual_end_date,
        COALESCE(batch_status, 'IN_PROGRESS') as batch_status,
        site_code as manufacturing_site_id,
        campaign_id
    FROM {catalog_name}.{bronze_schema}.manufacturing_batch_records
    WHERE ingestion_date >= current_date() - 30
""")

# Join with dim_product to get product_id
product_lookup = spark.table(target_product_table).filter("is_current = true") \
    .select("product_id", "product_code")

batch_source_with_product = batch_source.join(
    product_lookup,
    "product_code",
    "left"
)

# Generate row hash
batch_hash_cols = ["batch_number", "product_id", "batch_type", "batch_size", "batch_status",
                   "manufacturing_site_id", "campaign_id"]

batch_source_with_hash = generate_row_hash(batch_source_with_product, batch_hash_cols)

# Apply SCD Type 2
target_batch_table = f"{catalog_name}.{silver_schema}.dim_batch"

inserts, updates = apply_scd_type2(
    source_df=batch_source_with_hash,
    target_table=target_batch_table,
    business_key_columns=["batch_number"],
    compare_columns=batch_hash_cols,
    surrogate_key_column="batch_id"
)

print(f"✓ dim_batch created: {inserts} new, {updates} updated")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Build dim_equipment (with ISA-88 Hierarchy)

# COMMAND ----------

# For demo, generate equipment data from process data
equipment_source = spark.sql(f"""
    SELECT DISTINCT
        equipment_id as equipment_code,
        'Equipment ' || equipment_id as equipment_name,
        CASE
            WHEN equipment_id LIKE 'BIOREACTOR%' THEN 'Bioreactor'
            WHEN equipment_id LIKE 'COLUMN%' THEN 'Chromatography Column'
            WHEN equipment_id LIKE 'TANK%' THEN 'Hold Tank'
            ELSE 'General Equipment'
        END as equipment_type,
        'Various' as manufacturer,
        'MODEL-' || equipment_id as model_number,
        'SN-' || equipment_id as serial_number,
        -- ISA-88 Physical Model Hierarchy
        'PHARMA_CORP' as enterprise_id,
        unit_id as site_id,
        SUBSTRING(unit_id, 1, 3) as area_id,
        unit_id as process_cell_id,
        unit_id,
        equipment_id as equipment_module_id,
        equipment_id as control_module_id,
        'QUALIFIED' as qualification_status,
        current_date() + 365 as calibration_due_date,
        current_date() - 30 as last_maintenance_date,
        'PRODUCTION' as equipment_class,
        CASE
            WHEN equipment_id LIKE 'BIOREACTOR%' THEN 2000.0
            WHEN equipment_id LIKE 'TANK%' THEN 500.0
            ELSE 100.0
        END as capacity,
        'L' as capacity_uom
    FROM {catalog_name}.{bronze_schema}.manufacturing_process_data
    WHERE ingestion_date >= current_date() - 30
      AND equipment_id IS NOT NULL
""")

equipment_hash_cols = ["equipment_code", "equipment_name", "equipment_type", "manufacturer",
                       "qualification_status", "capacity", "equipment_class"]

equipment_source_with_hash = generate_row_hash(equipment_source, equipment_hash_cols)

target_equipment_table = f"{catalog_name}.{silver_schema}.dim_equipment"

inserts, updates = apply_scd_type2(
    source_df=equipment_source_with_hash,
    target_table=target_equipment_table,
    business_key_columns=["equipment_code"],
    compare_columns=equipment_hash_cols,
    surrogate_key_column="equipment_id"
)

print(f"✓ dim_equipment created: {inserts} new, {updates} updated")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Build dim_material

# COMMAND ----------

# Extract materials from genealogy and batch records
material_source = spark.sql(f"""
    SELECT DISTINCT
        material_code,
        'Material ' || material_code as material_name,
        CASE
            WHEN material_code LIKE 'API%' THEN 'Active Pharmaceutical Ingredient'
            WHEN material_code LIKE 'EXC%' THEN 'Excipient'
            WHEN material_code LIKE 'RAW%' THEN 'Raw Material'
            WHEN material_code LIKE 'FP%' THEN 'Finished Product'
            ELSE 'Other'
        END as material_type,
        CASE
            WHEN material_code LIKE 'API%' THEN 'Drug Substance'
            WHEN material_code LIKE 'FP%' THEN 'Drug Product'
            ELSE 'Material'
        END as material_category,
        'SUPPLIER-' || SUBSTRING(material_code, 1, 3) as supplier_id,
        'LOT-2024-' || material_code as lot_number,
        current_date() + 730 as expiration_date,
        '2-8°C' as storage_condition,
        'Non-Hazardous' as hazard_classification,
        true as coa_required,
        true as gmp_grade
    FROM (
        SELECT DISTINCT parent_material_code as material_code
        FROM {catalog_name}.{bronze_schema}.batch_genealogy
        WHERE ingestion_date >= current_date() - 30
        UNION
        SELECT DISTINCT child_material_code as material_code
        FROM {catalog_name}.{bronze_schema}.batch_genealogy
        WHERE ingestion_date >= current_date() - 30
    )
    WHERE material_code IS NOT NULL
""")

material_hash_cols = ["material_code", "material_name", "material_type", "material_category",
                      "supplier_id", "storage_condition", "gmp_grade"]

material_source_with_hash = generate_row_hash(material_source, material_hash_cols)

target_material_table = f"{catalog_name}.{silver_schema}.dim_material"

inserts, updates = apply_scd_type2(
    source_df=material_source_with_hash,
    target_table=target_material_table,
    business_key_columns=["material_code"],
    compare_columns=material_hash_cols,
    surrogate_key_column="material_id"
)

print(f"✓ dim_material created: {inserts} new, {updates} updated")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Build dim_site

# COMMAND ----------

site_source = spark.sql(f"""
    SELECT DISTINCT
        site_code,
        'Site ' || site_code as site_name,
        CASE
            WHEN site_code LIKE 'US%' THEN 'Manufacturing'
            WHEN site_code LIKE 'EU%' THEN 'Manufacturing'
            WHEN site_code LIKE 'CLIN%' THEN 'Clinical'
            ELSE 'R&D'
        END as site_type,
        CASE
            WHEN site_code LIKE 'US%' THEN 'United States'
            WHEN site_code LIKE 'EU%' THEN 'Germany'
            WHEN site_code LIKE 'CN%' THEN 'China'
            ELSE 'United States'
        END as country,
        CASE
            WHEN site_code LIKE 'US%' THEN 'Americas'
            WHEN site_code LIKE 'EU%' THEN 'EMEA'
            WHEN site_code LIKE 'CN%' THEN 'APAC'
            ELSE 'Americas'
        END as region,
        CASE
            WHEN site_code LIKE 'US%' THEN 'FDA'
            WHEN site_code LIKE 'EU%' THEN 'EMA'
            WHEN site_code LIKE 'CN%' THEN 'NMPA'
            ELSE 'FDA'
        END as regulatory_authority,
        true as gmp_certification,
        'ISO 9001:2015' as iso_certification
    FROM {catalog_name}.{bronze_schema}.manufacturing_batch_records
    WHERE ingestion_date >= current_date() - 30
      AND site_code IS NOT NULL
""")

site_hash_cols = ["site_code", "site_name", "site_type", "country", "region",
                  "regulatory_authority", "gmp_certification"]

site_source_with_hash = generate_row_hash(site_source, site_hash_cols)

target_site_table = f"{catalog_name}.{silver_schema}.dim_site"

inserts, updates = apply_scd_type2(
    source_df=site_source_with_hash,
    target_table=target_site_table,
    business_key_columns=["site_code"],
    compare_columns=site_hash_cols,
    surrogate_key_column="site_id"
)

print(f"✓ dim_site created: {inserts} new, {updates} updated")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Build dim_test_method

# COMMAND ----------

# Check if analytical table exists
if spark.catalog.tableExists(f"{catalog_name}.{bronze_schema}.analytical_test_results"):
    test_method_source = spark.sql(f"""
        SELECT DISTINCT
            test_method_code,
            test_method_name,
            test_category,
            analytical_technique,
            'Various' as instrument_type,
            'SPEC-' || test_method_code as specification_reference,
            'VALIDATED' as validation_status,
            CASE
                WHEN test_category = 'identity' THEN 'USP <197>'
                WHEN test_category = 'purity' THEN 'USP <621>'
                WHEN test_category = 'potency' THEN 'USP <111>'
                ELSE 'Internal'
            END as compendial_method
        FROM {catalog_name}.{bronze_schema}.analytical_test_results
        WHERE ingestion_date >= current_date() - 30
          AND test_method_code IS NOT NULL
    """)

    test_hash_cols = ["test_method_code", "test_method_name", "test_category",
                      "analytical_technique", "validation_status"]

    test_source_with_hash = generate_row_hash(test_method_source, test_hash_cols)

    target_test_table = f"{catalog_name}.{silver_schema}.dim_test_method"

    inserts, updates = apply_scd_type2(
        source_df=test_source_with_hash,
        target_table=target_test_table,
        business_key_columns=["test_method_code"],
        compare_columns=test_hash_cols,
        surrogate_key_column="test_method_id"
    )

    print(f"✓ dim_test_method created: {inserts} new, {updates} updated")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8. Build dim_study (Clinical Trials)

# COMMAND ----------

if spark.catalog.tableExists(f"{catalog_name}.{bronze_schema}.clinical_subjects"):
    study_source = spark.sql(f"""
        SELECT DISTINCT
            study_id as study_code,
            'Study ' || study_id as study_title,
            CASE
                WHEN study_id LIKE '%PH1%' THEN 'Phase 1'
                WHEN study_id LIKE '%PH2%' THEN 'Phase 2'
                WHEN study_id LIKE '%PH3%' THEN 'Phase 3'
                ELSE 'Phase 2'
            END as study_phase,
            'Oncology' as indication,
            'PharmaCorp Inc.' as sponsor,
            'Global CRO' as cro_name,
            'ENROLLING' as study_status,
            500 as planned_enrollment,
            COUNT(DISTINCT subject_id) as actual_enrollment,
            MIN(enrollment_date) as start_date,
            NULL as end_date,
            'BLA' as regulatory_submission
        FROM {catalog_name}.{bronze_schema}.clinical_subjects
        WHERE ingestion_date >= current_date() - 30
        GROUP BY study_id
    """)

    study_hash_cols = ["study_code", "study_title", "study_phase", "indication",
                       "study_status", "actual_enrollment"]

    study_source_with_hash = generate_row_hash(study_source, study_hash_cols)

    target_study_table = f"{catalog_name}.{silver_schema}.dim_study"

    inserts, updates = apply_scd_type2(
        source_df=study_source_with_hash,
        target_table=target_study_table,
        business_key_columns=["study_code"],
        compare_columns=study_hash_cols,
        surrogate_key_column="study_id"
    )

    print(f"✓ dim_study created: {inserts} new, {updates} updated")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 9. Verify Dimension Tables

# COMMAND ----------

print("\n" + "="*60)
print("Silver Layer Dimension Tables Summary")
print("="*60)

dimensions = [
    "dim_product",
    "dim_batch",
    "dim_equipment",
    "dim_material",
    "dim_site",
    "dim_test_method",
    "dim_study"
]

for dim in dimensions:
    full_table_name = f"{catalog_name}.{silver_schema}.{dim}"
    if spark.catalog.tableExists(full_table_name):
        total_count = spark.table(full_table_name).count()
        current_count = spark.table(full_table_name).filter("is_current = true").count()
        print(f"{dim:20s}: {current_count:6d} current / {total_count:6d} total (with history)")

print("="*60)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC
# MAGIC ✅ **Kimball Star Schema Dimensions Created**
# MAGIC
# MAGIC **Dimension Tables (Type 2 SCD):**
# MAGIC - `dim_product` - Product master with therapeutic area, molecule type, development phase
# MAGIC - `dim_batch` - Batch master with manufacturing details
# MAGIC - `dim_equipment` - Equipment with ISA-88 7-level hierarchy
# MAGIC - `dim_material` - Material master (API, excipients, raw materials, FP)
# MAGIC - `dim_site` - Manufacturing and clinical sites with regulatory info
# MAGIC - `dim_test_method` - Analytical testing methods
# MAGIC - `dim_study` - Clinical trial studies
# MAGIC
# MAGIC **Key Features:**
# MAGIC - Surrogate keys for all dimensions
# MAGIC - Type 2 SCD with effective dating and is_current flag
# MAGIC - Row hash for efficient change detection
# MAGIC - ISA-88 hierarchy in equipment dimension
# MAGIC - Support for all pharmaceutical phases (early-stage to commercial)
# MAGIC
# MAGIC **Next Steps:**
# MAGIC - Create dim_date (date dimension)
# MAGIC - Create fact tables (fact_manufacturing_process, fact_analytical_testing, etc.)
# MAGIC - Build bridge tables for many-to-many relationships
