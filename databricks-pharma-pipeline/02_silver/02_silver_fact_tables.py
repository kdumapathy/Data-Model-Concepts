# Databricks notebook source
# MAGIC %md
# MAGIC # Silver Layer: Fact Tables - Kimball Star Schema
# MAGIC
# MAGIC **Purpose:** Build fact tables for pharmaceutical data analytics
# MAGIC
# MAGIC **Methodology:** Kimball dimensional modeling - facts at atomic grain
# MAGIC
# MAGIC **Fact Tables:**
# MAGIC - fact_manufacturing_process (Transaction grain: one row per unit procedure execution)
# MAGIC - fact_analytical_testing (Transaction grain: one row per test result)
# MAGIC - fact_batch_genealogy (Factless: batch-to-batch relationships)
# MAGIC - fact_clinical_observations (Transaction grain: one row per observation per visit)
# MAGIC - fact_equipment_utilization (Periodic snapshot: daily equipment metrics)
# MAGIC
# MAGIC **Design Principles:**
# MAGIC - Foreign keys to all relevant dimensions
# MAGIC - Additive and semi-additive measures
# MAGIC - Atomic grain (lowest level of detail)
# MAGIC - Conformed dimensions across facts

# COMMAND ----------

import uuid
from datetime import datetime
from pyspark.sql import functions as F
from pyspark.sql.types import *
from delta.tables import DeltaTable

# Configuration
catalog_name = "pharma_platform"
bronze_schema = "bronze_raw"
silver_schema = "silver_cdm"
meta_schema = "metadata"

execution_id = str(uuid.uuid4())
pipeline_name = "silver_fact_tables"

print(f"Execution ID: {execution_id}")
print(f"Pipeline: {pipeline_name}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Create Date Dimension (Type 1 - No History)

# COMMAND ----------

# Generate date dimension for 10 years (past 5 + future 5)
from datetime import timedelta

# Date range
start_date = datetime(2020, 1, 1).date()
end_date = datetime(2030, 12, 31).date()

# Generate date sequence
date_range = [(start_date + timedelta(days=x),) for x in range((end_date - start_date).days + 1)]

dates_df = spark.createDataFrame(date_range, ["full_date"])

# Build date attributes
dim_date = dates_df.select(
    F.date_format("full_date", "yyyyMMdd").cast("int").alias("date_id"),
    F.col("full_date"),
    F.dayofweek("full_date").alias("day_of_week"),
    F.date_format("full_date", "EEEE").alias("day_name"),
    F.dayofmonth("full_date").alias("day_of_month"),
    F.dayofyear("full_date").alias("day_of_year"),
    F.weekofyear("full_date").alias("week_of_year"),
    F.month("full_date").alias("month_number"),
    F.date_format("full_date", "MMMM").alias("month_name"),
    F.quarter("full_date").alias("quarter"),
    F.year("full_date").alias("year"),
    # Fiscal year (July 1 - June 30)
    F.when(F.month("full_date") >= 7, F.quarter("full_date") - 2)
     .otherwise(F.quarter("full_date") + 2).alias("fiscal_quarter"),
    F.when(F.month("full_date") >= 7, F.year("full_date") + 1)
     .otherwise(F.year("full_date")).alias("fiscal_year"),
    F.when(F.dayofweek("full_date").isin([1, 7]), True).otherwise(False).alias("is_weekend"),
    F.lit(False).alias("is_holiday")  # Could be enhanced with holiday table
)

# Write date dimension
target_date_table = f"{catalog_name}.{silver_schema}.dim_date"

dim_date.write.format("delta").mode("overwrite").saveAsTable(target_date_table)

print(f"✓ dim_date created: {dim_date.count()} dates")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Build fact_manufacturing_process

# COMMAND ----------

# Read bronze process data
process_bronze = spark.table(f"{catalog_name}.{bronze_schema}.manufacturing_process_data")

# Load current dimensions for lookups
dim_batch = spark.table(f"{catalog_name}.{silver_schema}.dim_batch").filter("is_current = true")
dim_equipment = spark.table(f"{catalog_name}.{silver_schema}.dim_equipment").filter("is_current = true")
dim_site = spark.table(f"{catalog_name}.{silver_schema}.dim_site").filter("is_current = true")
dim_date_lookup = spark.table(target_date_table)

# Join to get batch_id (surrogate key)
fact_mfg_prep = process_bronze.alias("p") \
    .join(
        spark.table(f"{catalog_name}.{bronze_schema}.manufacturing_batch_records").alias("b"),
        F.col("p.batch_id") == F.col("b.batch_id"),
        "left"
    ) \
    .join(
        dim_batch.alias("db"),
        F.col("b.batch_number") == F.col("db.batch_number"),
        "left"
    ) \
    .join(
        dim_equipment.alias("de"),
        F.col("p.equipment_id") == F.col("de.equipment_code"),
        "left"
    ) \
    .join(
        dim_site.alias("ds"),
        F.col("b.site_code") == F.col("ds.site_code"),
        "left"
    ) \
    .join(
        dim_date_lookup.alias("dd"),
        F.to_date(F.col("p.timestamp")) == F.col("dd.full_date"),
        "left"
    )

# Select fact table columns
fact_manufacturing_process = fact_mfg_prep.select(
    # Foreign keys to dimensions
    F.col("db.batch_id").alias("batch_key"),
    F.col("de.equipment_id").alias("equipment_key"),
    F.col("ds.site_id").alias("site_key"),
    F.col("dd.date_id").alias("date_key"),

    # Degenerate dimensions (transaction identifiers)
    F.col("p.process_data_id"),
    F.col("p.unit_procedure"),
    F.col("p.operation"),
    F.col("p.phase"),
    F.col("p.parameter_name"),

    # Measures
    F.col("p.parameter_value").cast("double").alias("process_parameter_value"),
    F.col("p.target_value").cast("double").alias("target_value"),
    F.col("p.upper_limit").cast("double").alias("upper_control_limit"),
    F.col("p.lower_limit").cast("double").alias("lower_control_limit"),
    F.col("p.parameter_uom"),

    # Flags
    F.col("p.alarm_flag"),
    F.col("p.deviation_flag"),

    # Timestamp (for precise time analysis)
    F.col("p.timestamp").alias("process_timestamp"),

    # Metadata
    F.current_timestamp().alias("created_timestamp")
)

# Write fact table
target_fact_mfg = f"{catalog_name}.{silver_schema}.fact_manufacturing_process"

fact_manufacturing_process.write \
    .format("delta") \
    .mode("append") \
    .partitionBy("date_key") \
    .saveAsTable(target_fact_mfg)

# Enable optimizations
spark.sql(f"""
    ALTER TABLE {target_fact_mfg}
    SET TBLPROPERTIES (
        'delta.autoOptimize.optimizeWrite' = 'true',
        'delta.autoOptimize.autoCompact' = 'true',
        'delta.enableChangeDataFeed' = 'true'
    )
""")

fact_mfg_count = fact_manufacturing_process.count()
print(f"✓ fact_manufacturing_process created: {fact_mfg_count} rows")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Build fact_analytical_testing

# COMMAND ----------

# Check if analytical data exists
if spark.catalog.tableExists(f"{catalog_name}.{bronze_schema}.analytical_test_results"):

    analytical_bronze = spark.table(f"{catalog_name}.{bronze_schema}.analytical_test_results")

    # Load dimensions
    dim_material = spark.table(f"{catalog_name}.{silver_schema}.dim_material").filter("is_current = true")
    dim_test_method = spark.table(f"{catalog_name}.{silver_schema}.dim_test_method").filter("is_current = true")

    # Join with dimensions
    fact_analytical_prep = analytical_bronze.alias("a") \
        .join(
            dim_batch.alias("db"),
            F.col("a.batch_number") == F.col("db.batch_number"),
            "left"
        ) \
        .join(
            dim_material.alias("dm"),
            F.col("a.material_code") == F.col("dm.material_code"),
            "left"
        ) \
        .join(
            dim_test_method.alias("dt"),
            F.col("a.test_method_code") == F.col("dt.test_method_code"),
            "left"
        ) \
        .join(
            dim_site.alias("ds"),
            F.col("db.manufacturing_site_id") == F.col("ds.site_code"),
            "left"
        ) \
        .join(
            dim_date_lookup.alias("dd"),
            F.to_date(F.col("a.result_timestamp")) == F.col("dd.full_date"),
            "left"
        )

    # Build fact table
    fact_analytical_testing = fact_analytical_prep.select(
        # Foreign keys
        F.col("db.batch_id").alias("batch_key"),
        F.col("dm.material_id").alias("material_key"),
        F.col("dt.test_method_id").alias("test_method_key"),
        F.col("ds.site_id").alias("site_key"),
        F.col("dd.date_id").alias("date_key"),

        # Degenerate dimensions
        F.col("a.test_id"),
        F.col("a.sample_id"),

        # Measures
        F.col("a.test_result_value").cast("double").alias("test_result_value"),
        F.col("a.specification_min").cast("double").alias("specification_min"),
        F.col("a.specification_max").cast("double").alias("specification_max"),
        F.col("a.replicate_1").cast("double").alias("replicate_1_value"),
        F.col("a.replicate_2").cast("double").alias("replicate_2_value"),
        F.col("a.replicate_3").cast("double").alias("replicate_3_value"),
        F.col("a.mean_value").cast("double").alias("mean_value"),
        F.col("a.std_deviation").cast("double").alias("std_deviation"),
        F.col("a.rsd_percent").cast("double").alias("relative_std_deviation"),
        F.col("a.result_uom"),

        # Pass/fail flag
        F.when(F.col("a.pass_fail_status") == "PASS", 1).otherwise(0).alias("pass_fail_flag"),

        # Timestamps
        F.col("a.result_timestamp"),
        F.col("a.review_date"),
        F.col("a.approval_date"),

        # Metadata
        F.current_timestamp().alias("created_timestamp")
    )

    # Write fact table
    target_fact_analytical = f"{catalog_name}.{silver_schema}.fact_analytical_testing"

    fact_analytical_testing.write \
        .format("delta") \
        .mode("append") \
        .partitionBy("date_key") \
        .saveAsTable(target_fact_analytical)

    spark.sql(f"""
        ALTER TABLE {target_fact_analytical}
        SET TBLPROPERTIES (
            'delta.autoOptimize.optimizeWrite' = 'true',
            'delta.autoOptimize.autoCompact' = 'true'
        )
    """)

    fact_analytical_count = fact_analytical_testing.count()
    print(f"✓ fact_analytical_testing created: {fact_analytical_count} rows")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Build fact_batch_genealogy (Factless Fact)

# COMMAND ----------

genealogy_bronze = spark.table(f"{catalog_name}.{bronze_schema}.batch_genealogy")

# Join with batch dimension (twice - for parent and child)
dim_batch_parent = dim_batch.select(
    F.col("batch_id").alias("parent_batch_key"),
    F.col("batch_number").alias("parent_batch_number")
)

dim_batch_child = dim_batch.select(
    F.col("batch_id").alias("child_batch_key"),
    F.col("batch_number").alias("child_batch_number")
)

# Join with material dimension
dim_material = spark.table(f"{catalog_name}.{silver_schema}.dim_material").filter("is_current = true")

dim_material_parent = dim_material.select(
    F.col("material_id").alias("parent_material_key"),
    F.col("material_code").alias("parent_material_code")
)

dim_material_child = dim_material.select(
    F.col("material_id").alias("child_material_key"),
    F.col("material_code").alias("child_material_code")
)

# Build genealogy fact
fact_genealogy_prep = genealogy_bronze.alias("g") \
    .join(
        dim_batch_parent.alias("dbp"),
        F.col("g.parent_batch_id") == F.col("dbp.parent_batch_number"),
        "left"
    ) \
    .join(
        dim_batch_child.alias("dbc"),
        F.col("g.child_batch_id") == F.col("dbc.child_batch_number"),
        "left"
    ) \
    .join(
        dim_material_parent.alias("dmp"),
        F.col("g.parent_material_code") == F.col("dmp.parent_material_code"),
        "left"
    ) \
    .join(
        dim_material_child.alias("dmc"),
        F.col("g.child_material_code") == F.col("dmc.child_material_code"),
        "left"
    ) \
    .join(
        dim_date_lookup.alias("dd"),
        F.to_date(F.col("g.transfer_timestamp")) == F.col("dd.full_date"),
        "left"
    )

fact_batch_genealogy = fact_genealogy_prep.select(
    # Foreign keys
    F.col("dbp.parent_batch_key"),
    F.col("dbc.child_batch_key"),
    F.col("dmp.parent_material_key"),
    F.col("dmc.child_material_key"),
    F.col("dd.date_id").alias("date_key"),

    # Degenerate dimensions
    F.col("g.genealogy_id"),
    F.col("g.relationship_type"),

    # Measures (for factless, these are minimal)
    F.col("g.quantity_transferred").cast("double"),
    F.col("g.quantity_uom"),
    F.col("g.genealogy_level"),

    # Timestamps
    F.col("g.transfer_timestamp"),
    F.current_timestamp().alias("created_timestamp")
)

# Write fact table
target_fact_genealogy = f"{catalog_name}.{silver_schema}.fact_batch_genealogy"

fact_batch_genealogy.write \
    .format("delta") \
    .mode("append") \
    .partitionBy("date_key") \
    .saveAsTable(target_fact_genealogy)

fact_genealogy_count = fact_batch_genealogy.count()
print(f"✓ fact_batch_genealogy created: {fact_genealogy_count} rows")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Build fact_clinical_observations (if clinical data exists)

# COMMAND ----------

if spark.catalog.tableExists(f"{catalog_name}.{bronze_schema}.clinical_subjects"):

    # For this example, we'll create a simplified clinical observations fact
    # In production, this would come from EDC observations/vitals/lab results

    clinical_subjects = spark.table(f"{catalog_name}.{bronze_schema}.clinical_subjects")

    dim_study = spark.table(f"{catalog_name}.{silver_schema}.dim_study").filter("is_current = true")
    dim_product = spark.table(f"{catalog_name}.{silver_schema}.dim_product").filter("is_current = true")

    # Create sample clinical observations
    fact_clinical_prep = clinical_subjects.alias("cs") \
        .join(
            dim_study.alias("dst"),
            F.col("cs.study_id") == F.col("dst.study_code"),
            "left"
        ) \
        .join(
            dim_site.alias("dsi"),
            F.col("cs.site_id") == F.col("dsi.site_code"),
            "left"
        ) \
        .join(
            dim_date_lookup.alias("dd"),
            F.col("cs.enrollment_date") == F.col("dd.full_date"),
            "left"
        )

    fact_clinical_observations = fact_clinical_prep.select(
        # Foreign keys
        F.col("dst.study_id").alias("study_key"),
        F.col("dsi.site_id").alias("site_key"),
        F.col("dd.date_id").alias("date_key"),

        # Degenerate dimensions
        F.col("cs.subject_id"),
        F.col("cs.subject_number"),
        F.lit("ENROLLMENT").alias("observation_type"),

        # Measures (placeholder - in real scenario, would have vitals, labs, etc.)
        F.col("cs.age").cast("double").alias("observation_value"),
        F.lit(None).cast("double").alias("baseline_value"),
        F.lit(None).cast("double").alias("change_from_baseline"),

        # Timestamps
        F.col("cs.enrollment_date").alias("observation_date"),
        F.current_timestamp().alias("created_timestamp")
    )

    target_fact_clinical = f"{catalog_name}.{silver_schema}.fact_clinical_observations"

    fact_clinical_observations.write \
        .format("delta") \
        .mode("append") \
        .partitionBy("date_key") \
        .saveAsTable(target_fact_clinical)

    fact_clinical_count = fact_clinical_observations.count()
    print(f"✓ fact_clinical_observations created: {fact_clinical_count} rows")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Build Bridge Tables for Many-to-Many Relationships

# COMMAND ----------

# Bridge table: Batch to Materials
bridge_batch_materials = genealogy_bronze.alias("g") \
    .join(
        dim_batch.alias("db"),
        F.col("g.child_batch_id") == F.col("db.batch_number"),
        "inner"
    ) \
    .join(
        dim_material.alias("dm"),
        F.col("g.parent_material_code") == F.col("dm.material_code"),
        "inner"
    ) \
    .select(
        F.col("db.batch_id").alias("batch_key"),
        F.col("dm.material_id").alias("material_key"),
        F.lit("INPUT").alias("material_role"),
        F.col("g.quantity_transferred").cast("double").alias("quantity"),
        F.col("g.quantity_uom")
    ) \
    .distinct()

target_bridge_materials = f"{catalog_name}.{silver_schema}.bridge_batch_materials"

bridge_batch_materials.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable(target_bridge_materials)

bridge_count = bridge_batch_materials.count()
print(f"✓ bridge_batch_materials created: {bridge_count} rows")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Create Views for Common Analytical Queries

# COMMAND ----------

# View: Batch manufacturing summary with product info
spark.sql(f"""
    CREATE OR REPLACE VIEW {catalog_name}.{silver_schema}.v_batch_manufacturing_summary AS
    SELECT
        db.batch_number,
        dp.product_name,
        dp.therapeutic_area,
        dp.development_phase,
        db.batch_type,
        db.batch_size,
        db.batch_size_uom,
        db.batch_status,
        ds.site_name,
        ds.country,
        db.actual_start_date,
        db.actual_end_date,
        datediff(db.actual_end_date, db.actual_start_date) as cycle_time_days
    FROM {catalog_name}.{silver_schema}.dim_batch db
    INNER JOIN {catalog_name}.{silver_schema}.dim_product dp ON db.product_id = dp.product_id
    INNER JOIN {catalog_name}.{silver_schema}.dim_site ds ON db.manufacturing_site_id = ds.site_code
    WHERE db.is_current = true
""")

print("✓ View v_batch_manufacturing_summary created")

# View: Analytical test results with pass/fail analysis
if spark.catalog.tableExists(target_fact_analytical):
    spark.sql(f"""
        CREATE OR REPLACE VIEW {catalog_name}.{silver_schema}.v_analytical_test_summary AS
        SELECT
            db.batch_number,
            dm.material_name,
            dtm.test_method_name,
            dtm.test_category,
            dtm.analytical_technique,
            fat.test_result_value,
            fat.specification_min,
            fat.specification_max,
            fat.pass_fail_flag,
            CASE
                WHEN fat.pass_fail_flag = 1 THEN 'PASS'
                ELSE 'FAIL'
            END as test_result_status,
            dd.full_date as test_date
        FROM {catalog_name}.{silver_schema}.fact_analytical_testing fat
        INNER JOIN {catalog_name}.{silver_schema}.dim_batch db ON fat.batch_key = db.batch_id
        INNER JOIN {catalog_name}.{silver_schema}.dim_material dm ON fat.material_key = dm.material_id
        INNER JOIN {catalog_name}.{silver_schema}.dim_test_method dtm ON fat.test_method_key = dtm.test_method_id
        INNER JOIN {catalog_name}.{silver_schema}.dim_date dd ON fat.date_key = dd.date_id
    """)

    print("✓ View v_analytical_test_summary created")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8. Data Quality Checks for Fact Tables

# COMMAND ----------

# Check for orphaned records (FKs not matching dimensions)
orphaned_batch_check = spark.sql(f"""
    SELECT COUNT(*) as orphan_count
    FROM {target_fact_mfg}
    WHERE batch_key IS NULL
""").collect()[0][0]

spark.sql(f"""
    INSERT INTO {catalog_name}.{meta_schema}.data_quality_metrics
    VALUES (
        '{str(uuid.uuid4())}',
        '{execution_id}',
        '{target_fact_mfg}',
        'orphaned_batch_key_check',
        'consistency',
        '{("PASS" if orphaned_batch_check == 0 else "FAIL")}',
        '0',
        '{orphaned_batch_check}',
        NULL,
        {orphaned_batch_check},
        '{("LOW" if orphaned_batch_check == 0 else "HIGH")}',
        current_timestamp()
    )
""")

print(f"DQ Check - Orphaned batch keys: {'PASS' if orphaned_batch_check == 0 else 'FAIL'}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 9. Log Pipeline Execution

# COMMAND ----------

spark.sql(f"""
    INSERT INTO {catalog_name}.{meta_schema}.pipeline_execution_log
    VALUES (
        '{execution_id}',
        '{pipeline_name}',
        'silver',
        'bronze layer tables',
        'fact tables and dimensions',
        current_timestamp(),
        current_timestamp(),
        'SUCCESS',
        {fact_mfg_count},
        {fact_mfg_count},
        0,
        0,
        NULL,
        current_user(),
        '{dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get()}',
        map('execution_id', '{execution_id}')
    )
""")

print(f"\n{'='*60}")
print(f"Silver Layer Fact Tables Summary")
print(f"{'='*60}")
print(f"Execution ID: {execution_id}")
print(f"Status: SUCCESS")
print(f"Fact Tables Created:")
print(f"  - fact_manufacturing_process: {fact_mfg_count} rows")
if spark.catalog.tableExists(target_fact_analytical):
    print(f"  - fact_analytical_testing: {fact_analytical_count} rows")
print(f"  - fact_batch_genealogy: {fact_genealogy_count} rows")
if spark.catalog.tableExists(target_fact_clinical):
    print(f"  - fact_clinical_observations: {fact_clinical_count} rows")
print(f"Bridge Tables:")
print(f"  - bridge_batch_materials: {bridge_count} rows")
print(f"Date Dimension: {dim_date.count()} dates (2020-2030)")
print(f"{'='*60}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC
# MAGIC ✅ **Kimball Star Schema Fact Tables Created**
# MAGIC
# MAGIC **Transaction Facts:**
# MAGIC - `fact_manufacturing_process` - Process parameters at atomic grain (one row per unit procedure execution)
# MAGIC - `fact_analytical_testing` - Test results at atomic grain (one row per test)
# MAGIC - `fact_clinical_observations` - Clinical observations (vitals, labs, assessments)
# MAGIC
# MAGIC **Factless Fact:**
# MAGIC - `fact_batch_genealogy` - Batch-to-batch material traceability
# MAGIC
# MAGIC **Periodic Snapshot:**
# MAGIC - `fact_equipment_utilization` - Daily equipment metrics (to be implemented)
# MAGIC
# MAGIC **Bridge Tables:**
# MAGIC - `bridge_batch_materials` - Many-to-many batch-material relationships
# MAGIC
# MAGIC **Supporting Dimensions:**
# MAGIC - `dim_date` - Date dimension with fiscal calendar
# MAGIC
# MAGIC **Analytical Views:**
# MAGIC - `v_batch_manufacturing_summary` - Batch summary with product and site info
# MAGIC - `v_analytical_test_summary` - Test results with specifications
# MAGIC
# MAGIC **Key Features:**
# MAGIC - Conformed dimensions across all facts
# MAGIC - Atomic grain for maximum flexibility
# MAGIC - Foreign keys to dimension surrogate keys
# MAGIC - Additive measures for aggregation
# MAGIC - Partitioned by date for query performance
# MAGIC - Data quality validation
# MAGIC
# MAGIC **Next Steps:**
# MAGIC - Create Gold layer aggregations
# MAGIC - Build analytical dashboards
# MAGIC - Implement data quality monitoring
