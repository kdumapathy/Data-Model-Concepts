{{
    config(
        materialized='table',
        tags=['gold', 'analytics', 'kpi', 'manufacturing']
    )
}}

/*
    Gold Table: Batch Performance Summary

    Type: Aggregated Analytics Table
    Grain: One row per batch

    Description:
        Executive-level batch performance KPIs including:
        - First Pass Yield (FPY)
        - On-Time Delivery (OTD)
        - Cycle Time
        - Quality Metrics
        - Deviation Tracking

    Use Cases:
        - Executive dashboards
        - Manufacturing performance reviews
        - Regulatory submissions
        - Continuous improvement initiatives
*/

WITH batch_manufacturing AS (
    SELECT
        b.batch_number,
        b.batch_id,
        p.product_code,
        p.product_name,
        p.therapeutic_area,
        p.development_phase,
        b.batch_type,
        s.site_name,
        s.country,
        s.region,

        -- Date attributes
        year(b.actual_start_date) as batch_year,
        quarter(b.actual_start_date) as batch_quarter,
        month(b.actual_start_date) as batch_month,

        -- Batch metrics
        b.batch_size,
        b.batch_size_uom,
        b.batch_status,
        b.actual_start_date,
        b.actual_end_date,
        b.planned_start_date,
        b.planned_end_date

    FROM {{ ref('dim_batch') }} b

    INNER JOIN {{ ref('dim_product') }} p
        ON b.product_id = p.surrogate_key
        AND p.is_current = TRUE

    INNER JOIN {{ ref('dim_site') }} s
        ON b.manufacturing_site_id = s.surrogate_key
        AND s.is_current = TRUE

    WHERE b.is_current = TRUE
      AND b.batch_status IN ('COMPLETED', 'RELEASED')
),

batch_process_metrics AS (
    SELECT
        batch_key,
        count(distinct case when deviation_flag = TRUE then process_data_id end) as deviation_count,
        count(distinct case when alarm_flag = TRUE then process_data_id end) as alarm_count,
        count(*) as total_process_points
    FROM {{ ref('fact_manufacturing_process') }}
    GROUP BY batch_key
),

batch_quality_metrics AS (
    SELECT
        batch_key,
        count(distinct test_id) as total_tests,
        sum(pass_fail_flag) as tests_passed,
        count(distinct test_id) - sum(pass_fail_flag) as tests_failed,
        count(distinct case when oos_flag = TRUE then test_id end) as oos_count
    FROM {{ ref('fact_analytical_testing') }}
    GROUP BY batch_key
),

batch_material_count AS (
    SELECT
        batch_key,
        count(distinct material_key) as material_count
    FROM {{ ref('bridge_batch_materials') }}
    GROUP BY batch_key
)

SELECT
    -- Dimensions
    bm.batch_number,
    bm.batch_id,
    bm.product_code,
    bm.product_name,
    bm.therapeutic_area,
    bm.development_phase,
    bm.batch_type,
    bm.site_name,
    bm.country,
    bm.region,

    -- Date attributes
    bm.batch_year,
    bm.batch_quarter,
    bm.batch_month,

    -- Batch metrics
    bm.batch_size,
    bm.batch_size_uom,
    bm.batch_status,
    bm.actual_start_date,
    bm.actual_end_date,

    -- Calculated KPIs
    datediff(bm.actual_end_date, bm.actual_start_date) as cycle_time_days,
    datediff(bm.actual_start_date, bm.planned_start_date) as start_date_variance_days,
    datediff(bm.actual_end_date, bm.planned_end_date) as end_date_variance_days,

    -- On-time metrics
    case
        when bm.actual_start_date <= bm.planned_start_date then 1
        else 0
    end as on_time_start_flag,

    case
        when bm.actual_end_date <= bm.planned_end_date then 1
        else 0
    end as on_time_completion_flag,

    -- Process metrics
    coalesce(pm.deviation_count, 0) as deviation_count,
    coalesce(pm.alarm_count, 0) as alarm_count,
    coalesce(pm.total_process_points, 0) as total_process_points,

    -- Quality metrics
    coalesce(qm.total_tests, 0) as total_tests,
    coalesce(qm.tests_passed, 0) as tests_passed,
    coalesce(qm.tests_failed, 0) as tests_failed,
    coalesce(qm.oos_count, 0) as oos_count,

    -- First pass yield
    case
        when coalesce(qm.total_tests, 0) > 0
        then round(coalesce(qm.tests_passed, 0) * 100.0 / qm.total_tests, 2)
        else null
    end as first_pass_yield_pct,

    -- Material complexity
    coalesce(mc.material_count, 0) as material_count,

    -- Quality score (weighted composite)
    case
        when coalesce(qm.total_tests, 0) > 0
        then round(
            (coalesce(qm.tests_passed, 0) * 100.0 / qm.total_tests) * 0.5 +  -- FPY: 50%
            (case when bm.actual_end_date <= bm.planned_end_date then 100 else 0 end) * 0.3 +  -- OTD: 30%
            (case when coalesce(pm.deviation_count, 0) = 0 then 100 else 0 end) * 0.2,  -- Zero deviations: 20%
            2
        )
        else null
    end as quality_score,

    -- Timestamps
    current_timestamp() as created_timestamp,
    current_timestamp() as updated_timestamp

FROM batch_manufacturing bm

LEFT JOIN batch_process_metrics pm
    ON bm.batch_id = pm.batch_key

LEFT JOIN batch_quality_metrics qm
    ON bm.batch_id = qm.batch_key

LEFT JOIN batch_material_count mc
    ON bm.batch_id = mc.batch_key
