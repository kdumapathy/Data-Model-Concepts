# Databricks notebook source
# MAGIC %md
# MAGIC # Gold Layer: Batch Performance Analytics
# MAGIC
# MAGIC **Purpose:** Create business-level aggregations for batch manufacturing analytics
# MAGIC
# MAGIC **Gold Tables:**
# MAGIC - gold_batch_performance_summary - Batch KPIs and performance metrics
# MAGIC - gold_quality_kpi_dashboard - Quality metrics and OOS tracking
# MAGIC - gold_equipment_oee - Overall Equipment Effectiveness
# MAGIC - gold_material_consumption_forecast - Material usage trends
# MAGIC - gold_clinical_enrollment_tracking - Clinical trial enrollment metrics
# MAGIC
# MAGIC **Use Cases:**
# MAGIC - Executive dashboards
# MAGIC - Regulatory submissions
# MAGIC - Manufacturing performance reports
# MAGIC - Quality trend analysis
# MAGIC - Resource planning

# COMMAND ----------

import uuid
from datetime import datetime
from pyspark.sql import functions as F
from pyspark.sql.window import Window
from delta.tables import DeltaTable

# Configuration
catalog_name = "pharma_platform"
silver_schema = "silver_cdm"
gold_schema = "gold_analytics"
meta_schema = "metadata"

execution_id = str(uuid.uuid4())
pipeline_name = "gold_batch_analytics"

print(f"Execution ID: {execution_id}")
print(f"Pipeline: {pipeline_name}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Gold: Batch Performance Summary

# COMMAND ----------

# Aggregate batch performance metrics
gold_batch_performance = spark.sql(f"""
    SELECT
        -- Dimensions
        db.batch_number,
        db.batch_id,
        dp.product_code,
        dp.product_name,
        dp.therapeutic_area,
        dp.development_phase,
        db.batch_type,
        ds.site_name,
        ds.country,
        ds.region,

        -- Date attributes
        YEAR(db.actual_start_date) as batch_year,
        QUARTER(db.actual_start_date) as batch_quarter,
        MONTH(db.actual_start_date) as batch_month,

        -- Batch metrics
        db.batch_size,
        db.batch_size_uom,
        db.batch_status,
        db.actual_start_date,
        db.actual_end_date,

        -- Calculated KPIs
        DATEDIFF(db.actual_end_date, db.actual_start_date) as cycle_time_days,
        DATEDIFF(db.actual_start_date, db.planned_start_date) as start_date_variance_days,
        DATEDIFF(db.actual_end_date, db.planned_end_date) as end_date_variance_days,

        -- On-time metrics
        CASE
            WHEN db.actual_start_date <= db.planned_start_date THEN 1
            ELSE 0
        END as on_time_start_flag,

        CASE
            WHEN db.actual_end_date <= db.planned_end_date THEN 1
            ELSE 0
        END as on_time_completion_flag,

        -- Process deviations count
        COUNT(DISTINCT CASE WHEN fmp.deviation_flag = true THEN fmp.process_data_id END) as deviation_count,

        -- Process alarms count
        COUNT(DISTINCT CASE WHEN fmp.alarm_flag = true THEN fmp.process_data_id END) as alarm_count,

        -- Analytical testing metrics
        COUNT(DISTINCT fat.test_id) as total_tests,
        SUM(fat.pass_fail_flag) as tests_passed,
        COUNT(DISTINCT fat.test_id) - SUM(fat.pass_fail_flag) as tests_failed,

        -- First pass yield
        CASE
            WHEN COUNT(DISTINCT fat.test_id) > 0 THEN
                ROUND(SUM(fat.pass_fail_flag) * 100.0 / COUNT(DISTINCT fat.test_id), 2)
            ELSE NULL
        END as first_pass_yield_pct,

        -- Material count
        COUNT(DISTINCT bbm.material_key) as material_count,

        -- Timestamps
        current_timestamp() as created_timestamp,
        current_timestamp() as updated_timestamp

    FROM {catalog_name}.{silver_schema}.dim_batch db

    INNER JOIN {catalog_name}.{silver_schema}.dim_product dp
        ON db.product_id = dp.product_id

    INNER JOIN {catalog_name}.{silver_schema}.dim_site ds
        ON db.manufacturing_site_id = ds.site_code

    LEFT JOIN {catalog_name}.{silver_schema}.fact_manufacturing_process fmp
        ON db.batch_id = fmp.batch_key

    LEFT JOIN {catalog_name}.{silver_schema}.fact_analytical_testing fat
        ON db.batch_id = fat.batch_key

    LEFT JOIN {catalog_name}.{silver_schema}.bridge_batch_materials bbm
        ON db.batch_id = bbm.batch_key

    WHERE db.is_current = true
      AND db.batch_status IN ('COMPLETED', 'IN_PROGRESS')

    GROUP BY
        db.batch_number, db.batch_id, dp.product_code, dp.product_name,
        dp.therapeutic_area, dp.development_phase, db.batch_type,
        ds.site_name, ds.country, ds.region,
        db.batch_size, db.batch_size_uom, db.batch_status,
        db.actual_start_date, db.actual_end_date,
        db.planned_start_date, db.planned_end_date
""")

# Write to Gold table
target_gold_batch = f"{catalog_name}.{gold_schema}.gold_batch_performance_summary"

gold_batch_performance.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(target_gold_batch)

batch_perf_count = gold_batch_performance.count()
print(f"✓ gold_batch_performance_summary: {batch_perf_count} batches")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Gold: Quality KPI Dashboard

# COMMAND ----------

if spark.catalog.tableExists(f"{catalog_name}.{silver_schema}.fact_analytical_testing"):
    gold_quality_kpi = spark.sql(f"""
        SELECT
            -- Time dimensions
            dd.year,
            dd.quarter,
            dd.month_number,
            dd.month_name,

            -- Product dimensions
            dp.product_name,
            dp.therapeutic_area,
            dp.development_phase,

            -- Site dimensions
            ds.site_name,
            ds.country,
            ds.region,

            -- Test dimensions
            dtm.test_category,
            dtm.analytical_technique,

            -- Quality metrics
            COUNT(DISTINCT fat.test_id) as total_tests,
            SUM(fat.pass_fail_flag) as tests_passed,
            COUNT(DISTINCT fat.test_id) - SUM(fat.pass_fail_flag) as tests_failed,

            -- Pass rate
            ROUND(SUM(fat.pass_fail_flag) * 100.0 / COUNT(DISTINCT fat.test_id), 2) as pass_rate_pct,

            -- Out of specification count
            COUNT(DISTINCT CASE WHEN fat.pass_fail_flag = 0 THEN fat.test_id END) as oos_count,

            -- Average test results by category
            AVG(fat.test_result_value) as avg_test_result,
            STDDEV(fat.test_result_value) as stddev_test_result,
            MIN(fat.test_result_value) as min_test_result,
            MAX(fat.test_result_value) as max_test_result,

            -- Precision metrics (RSD)
            AVG(fat.relative_std_deviation) as avg_rsd_pct,

            -- Number of batches tested
            COUNT(DISTINCT fat.batch_key) as batches_tested,

            -- Timestamps
            current_timestamp() as created_timestamp

        FROM {catalog_name}.{silver_schema}.fact_analytical_testing fat

        INNER JOIN {catalog_name}.{silver_schema}.dim_date dd
            ON fat.date_key = dd.date_id

        INNER JOIN {catalog_name}.{silver_schema}.dim_batch db
            ON fat.batch_key = db.batch_id

        INNER JOIN {catalog_name}.{silver_schema}.dim_product dp
            ON db.product_id = dp.product_id

        INNER JOIN {catalog_name}.{silver_schema}.dim_site ds
            ON fat.site_key = ds.site_id

        INNER JOIN {catalog_name}.{silver_schema}.dim_test_method dtm
            ON fat.test_method_key = dtm.test_method_id

        WHERE dd.year >= YEAR(current_date()) - 2  -- Last 2 years

        GROUP BY
            dd.year, dd.quarter, dd.month_number, dd.month_name,
            dp.product_name, dp.therapeutic_area, dp.development_phase,
            ds.site_name, ds.country, ds.region,
            dtm.test_category, dtm.analytical_technique
    """)

    target_gold_quality = f"{catalog_name}.{gold_schema}.gold_quality_kpi_dashboard"

    gold_quality_kpi.write \
        .format("delta") \
        .mode("overwrite") \
        .saveAsTable(target_gold_quality)

    quality_kpi_count = gold_quality_kpi.count()
    print(f"✓ gold_quality_kpi_dashboard: {quality_kpi_count} aggregated records")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Gold: Equipment OEE (Overall Equipment Effectiveness)

# COMMAND ----------

# Calculate OEE from manufacturing process data
gold_equipment_oee = spark.sql(f"""
    WITH equipment_utilization AS (
        SELECT
            de.equipment_code,
            de.equipment_name,
            de.equipment_type,
            ds.site_name,
            dd.year,
            dd.month_number,
            dd.month_name,

            -- Count of batches processed
            COUNT(DISTINCT fmp.batch_key) as batches_processed,

            -- Total processing time (sum of phase durations)
            -- For demo, using record count as proxy for runtime hours
            COUNT(*) / 60.0 as total_runtime_hours,

            -- Ideal cycle time (assuming 24/7 operation)
            COUNT(DISTINCT dd.date_id) * 24.0 as available_hours,

            -- Calculate availability (runtime / available time)
            ROUND((COUNT(*) / 60.0) / (COUNT(DISTINCT dd.date_id) * 24.0) * 100, 2) as availability_pct,

            -- Performance (actual vs. target rates) - simplified
            100.0 as performance_pct,  -- Would need target rates from recipes

            -- Quality (good units / total units)
            ROUND(
                COUNT(DISTINCT CASE WHEN fmp.deviation_flag = false THEN fmp.process_data_id END) * 100.0 /
                NULLIF(COUNT(DISTINCT fmp.process_data_id), 0),
                2
            ) as quality_pct

        FROM {catalog_name}.{silver_schema}.fact_manufacturing_process fmp

        INNER JOIN {catalog_name}.{silver_schema}.dim_equipment de
            ON fmp.equipment_key = de.equipment_id

        INNER JOIN {catalog_name}.{silver_schema}.dim_site ds
            ON fmp.site_key = ds.site_id

        INNER JOIN {catalog_name}.{silver_schema}.dim_date dd
            ON fmp.date_key = dd.date_id

        WHERE dd.year >= YEAR(current_date()) - 1  -- Last year

        GROUP BY
            de.equipment_code, de.equipment_name, de.equipment_type,
            ds.site_name, dd.year, dd.month_number, dd.month_name
    )

    SELECT
        *,
        -- OEE = Availability * Performance * Quality
        ROUND(availability_pct * performance_pct * quality_pct / 10000, 2) as oee_pct,

        -- Categorize OEE performance
        CASE
            WHEN (availability_pct * performance_pct * quality_pct / 10000) >= 85 THEN 'World Class'
            WHEN (availability_pct * performance_pct * quality_pct / 10000) >= 65 THEN 'Good'
            WHEN (availability_pct * performance_pct * quality_pct / 10000) >= 40 THEN 'Fair'
            ELSE 'Poor'
        END as oee_category,

        current_timestamp() as created_timestamp

    FROM equipment_utilization
""")

target_gold_oee = f"{catalog_name}.{gold_schema}.gold_equipment_oee"

gold_equipment_oee.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable(target_gold_oee)

oee_count = gold_equipment_oee.count()
print(f"✓ gold_equipment_oee: {oee_count} equipment-month records")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Gold: Material Consumption Trends and Forecast

# COMMAND ----------

gold_material_consumption = spark.sql(f"""
    SELECT
        -- Time dimensions
        dd.year,
        dd.quarter,
        dd.month_number,
        dd.month_name,

        -- Material dimensions
        dm.material_code,
        dm.material_name,
        dm.material_type,
        dm.material_category,

        -- Product dimensions
        dp.product_name,
        dp.therapeutic_area,

        -- Site dimensions
        ds.site_name,

        -- Consumption metrics
        COUNT(DISTINCT bbm.batch_key) as batches_consuming_material,
        SUM(bbm.quantity) as total_quantity_consumed,
        bbm.quantity_uom,
        AVG(bbm.quantity) as avg_quantity_per_batch,
        MIN(bbm.quantity) as min_quantity,
        MAX(bbm.quantity) as max_quantity,
        STDDEV(bbm.quantity) as stddev_quantity,

        -- Cost proxy (in production, join with material cost table)
        SUM(bbm.quantity) * 100 as estimated_cost_usd,

        current_timestamp() as created_timestamp

    FROM {catalog_name}.{silver_schema}.bridge_batch_materials bbm

    INNER JOIN {catalog_name}.{silver_schema}.dim_material dm
        ON bbm.material_key = dm.material_id

    INNER JOIN {catalog_name}.{silver_schema}.dim_batch db
        ON bbm.batch_key = db.batch_id

    INNER JOIN {catalog_name}.{silver_schema}.dim_product dp
        ON db.product_id = dp.product_id

    INNER JOIN {catalog_name}.{silver_schema}.dim_site ds
        ON db.manufacturing_site_id = ds.site_code

    INNER JOIN {catalog_name}.{silver_schema}.dim_date dd
        ON DATE_FORMAT(db.actual_start_date, 'yyyyMMdd') = CAST(dd.date_id AS STRING)

    WHERE dm.is_current = true
      AND dd.year >= YEAR(current_date()) - 2

    GROUP BY
        dd.year, dd.quarter, dd.month_number, dd.month_name,
        dm.material_code, dm.material_name, dm.material_type, dm.material_category,
        dp.product_name, dp.therapeutic_area,
        ds.site_name, bbm.quantity_uom
""")

target_gold_material = f"{catalog_name}.{gold_schema}.gold_material_consumption_forecast"

gold_material_consumption.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable(target_gold_material)

material_count = gold_material_consumption.count()
print(f"✓ gold_material_consumption_forecast: {material_count} material-month records")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Gold: Clinical Trial Enrollment Tracking

# COMMAND ----------

if spark.catalog.tableExists(f"{catalog_name}.{silver_schema}.dim_study"):
    gold_clinical_enrollment = spark.sql(f"""
        SELECT
            -- Study dimensions
            dst.study_code,
            dst.study_title,
            dst.study_phase,
            dst.indication,
            dst.sponsor,

            -- Enrollment metrics
            dst.planned_enrollment,
            dst.actual_enrollment,
            dst.planned_enrollment - dst.actual_enrollment as enrollment_gap,
            ROUND(dst.actual_enrollment * 100.0 / NULLIF(dst.planned_enrollment, 0), 2) as enrollment_pct,

            -- Timeline
            dst.start_date,
            dst.end_date,
            DATEDIFF(COALESCE(dst.end_date, current_date()), dst.start_date) as study_duration_days,

            -- Enrollment velocity (subjects per month)
            ROUND(
                dst.actual_enrollment /
                NULLIF(DATEDIFF(COALESCE(dst.end_date, current_date()), dst.start_date) / 30.0, 0),
                2
            ) as enrollment_velocity_per_month,

            -- Site count
            COUNT(DISTINCT dsi.site_id) as sites_active,

            -- Subject status breakdown (would come from subject-level data in production)
            dst.actual_enrollment as total_subjects,

            -- Regulatory status
            dst.study_status,
            dst.regulatory_submission,

            current_timestamp() as created_timestamp

        FROM {catalog_name}.{silver_schema}.dim_study dst

        LEFT JOIN {catalog_name}.{silver_schema}.fact_clinical_observations fco
            ON dst.study_id = fco.study_key

        LEFT JOIN {catalog_name}.{silver_schema}.dim_site dsi
            ON fco.site_key = dsi.site_id

        WHERE dst.is_current = true

        GROUP BY
            dst.study_code, dst.study_title, dst.study_phase, dst.indication,
            dst.sponsor, dst.planned_enrollment, dst.actual_enrollment,
            dst.start_date, dst.end_date, dst.study_status, dst.regulatory_submission
    """)

    target_gold_clinical = f"{catalog_name}.{gold_schema}.gold_clinical_enrollment_tracking"

    gold_clinical_enrollment.write \
        .format("delta") \
        .mode("overwrite") \
        .saveAsTable(target_gold_clinical)

    clinical_count = gold_clinical_enrollment.count()
    print(f"✓ gold_clinical_enrollment_tracking: {clinical_count} studies")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Create Executive Summary Views

# COMMAND ----------

# Executive KPI summary
spark.sql(f"""
    CREATE OR REPLACE VIEW {catalog_name}.{gold_schema}.v_executive_kpi_summary AS

    SELECT
        'Manufacturing Performance' as kpi_category,
        COUNT(DISTINCT batch_id) as total_count,
        ROUND(AVG(first_pass_yield_pct), 2) as avg_pct,
        SUM(deviation_count) as total_deviations,
        SUM(CASE WHEN on_time_completion_flag = 1 THEN 1 ELSE 0 END) as on_time_count,
        ROUND(SUM(CASE WHEN on_time_completion_flag = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as on_time_pct
    FROM {catalog_name}.{gold_schema}.gold_batch_performance_summary

    UNION ALL

    SELECT
        'Quality Performance' as kpi_category,
        SUM(total_tests) as total_count,
        ROUND(AVG(pass_rate_pct), 2) as avg_pct,
        SUM(oos_count) as total_deviations,
        NULL as on_time_count,
        NULL as on_time_pct
    FROM {catalog_name}.{gold_schema}.gold_quality_kpi_dashboard

    UNION ALL

    SELECT
        'Equipment Effectiveness' as kpi_category,
        COUNT(DISTINCT equipment_code) as total_count,
        ROUND(AVG(oee_pct), 2) as avg_pct,
        NULL as total_deviations,
        SUM(CASE WHEN oee_category IN ('World Class', 'Good') THEN 1 ELSE 0 END) as on_time_count,
        NULL as on_time_pct
    FROM {catalog_name}.{gold_schema}.gold_equipment_oee
""")

print("✓ View v_executive_kpi_summary created")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Log Pipeline Execution

# COMMAND ----------

spark.sql(f"""
    INSERT INTO {catalog_name}.{meta_schema}.pipeline_execution_log
    VALUES (
        '{execution_id}',
        '{pipeline_name}',
        'gold',
        'silver layer tables',
        'gold analytical tables',
        current_timestamp(),
        current_timestamp(),
        'SUCCESS',
        {batch_perf_count + oee_count + material_count},
        {batch_perf_count + oee_count + material_count},
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
print(f"Gold Layer Analytics Summary")
print(f"{'='*60}")
print(f"Execution ID: {execution_id}")
print(f"Status: SUCCESS")
print(f"Gold Tables Created:")
print(f"  - gold_batch_performance_summary: {batch_perf_count} batches")
if spark.catalog.tableExists(target_gold_quality):
    print(f"  - gold_quality_kpi_dashboard: {quality_kpi_count} records")
print(f"  - gold_equipment_oee: {oee_count} equipment-months")
print(f"  - gold_material_consumption_forecast: {material_count} material-months")
if spark.catalog.tableExists(target_gold_clinical):
    print(f"  - gold_clinical_enrollment_tracking: {clinical_count} studies")
print(f"{'='*60}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC
# MAGIC ✅ **Gold Layer Business Analytics Created**
# MAGIC
# MAGIC **Analytical Tables:**
# MAGIC - `gold_batch_performance_summary` - Batch KPIs including cycle time, on-time delivery, FPY
# MAGIC - `gold_quality_kpi_dashboard` - Quality metrics, pass rates, OOS tracking
# MAGIC - `gold_equipment_oee` - Overall Equipment Effectiveness by equipment and month
# MAGIC - `gold_material_consumption_forecast` - Material usage trends and forecasting
# MAGIC - `gold_clinical_enrollment_tracking` - Clinical trial enrollment metrics
# MAGIC
# MAGIC **Executive Views:**
# MAGIC - `v_executive_kpi_summary` - High-level KPIs across all areas
# MAGIC
# MAGIC **Key Metrics:**
# MAGIC - First Pass Yield (FPY)
# MAGIC - On-Time Delivery (OTD)
# MAGIC - Overall Equipment Effectiveness (OEE)
# MAGIC - Quality Pass Rate
# MAGIC - Out of Specification (OOS) Count
# MAGIC - Cycle Time
# MAGIC - Material Consumption
# MAGIC - Clinical Enrollment Velocity
# MAGIC
# MAGIC **Use Cases:**
# MAGIC - Executive dashboards (Tableau, Power BI)
# MAGIC - Regulatory submissions
# MAGIC - Manufacturing performance reviews
# MAGIC - Resource planning and forecasting
# MAGIC - Quality trend analysis
# MAGIC - Clinical trial monitoring
# MAGIC
# MAGIC **Ready for:**
# MAGIC - BI tool connectivity
# MAGIC - Scheduled reporting
# MAGIC - Alerting and monitoring
# MAGIC - Predictive analytics
