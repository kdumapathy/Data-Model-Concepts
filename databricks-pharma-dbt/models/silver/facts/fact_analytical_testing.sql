{{
    config(
        materialized='incremental',
        unique_key='test_id',
        on_schema_change='sync_all_columns',
        incremental_strategy='merge',
        partition_by=['test_date'],
        tags=['fact', 'analytical', 'quality']
    )
}}

/*
    Fact Table: Analytical Testing

    Type: Transaction Fact Table
    Grain: One row per analytical test
    Business Key: test_id

    Description:
        Laboratory test results with dimensional context.
        Includes specifications, pass/fail status, and quality metrics.

    Fact Type: Atomic (transactional grain)
    Additive Measures: None (all semi-additive or non-additive)

    Compliance:
        - CFR Part 11: Audit trail via incremental loads
        - ALCOA+: Original data preserved
        - GxP: Quality testing fully tracked
*/

WITH analytical_tests AS (
    SELECT
        test_id,
        sample_id,
        batch_number,
        test_method_code,
        test_method_name,
        test_category,
        analytical_technique,
        test_result_value,
        test_result_unit,
        specification_lower_limit,
        specification_upper_limit,
        pass_fail_flag,
        test_date,
        test_timestamp,
        tested_by_user,
        reviewed_by_user,
        instrument_id,
        retest_flag,
        oos_flag,  -- Out of Specification
        relative_std_deviation,
        ingestion_timestamp
    FROM {{ source('pharma_raw', 'analytical_test_results') }}

    {% if is_incremental() %}
    WHERE ingestion_timestamp > (SELECT max(ingestion_timestamp) FROM {{ this }})
    {% endif %}
),

-- Join to dimensions to get surrogate keys
tests_with_dimensions AS (
    SELECT
        t.test_id,
        t.sample_id,

        -- Dimension keys
        b.batch_id as batch_key,
        p.product_id as product_key,
        tm.test_method_id as test_method_key,
        s.site_id as site_key,
        d.date_id as date_key,

        -- Test details
        t.test_category,
        t.analytical_technique,

        -- Measures (facts)
        t.test_result_value,
        t.test_result_unit,
        t.specification_lower_limit,
        t.specification_upper_limit,

        -- Calculated measures
        CASE
            WHEN t.specification_upper_limit IS NOT NULL
                AND t.specification_lower_limit IS NOT NULL
            THEN ((t.specification_upper_limit - t.specification_lower_limit) / 2.0)
            ELSE NULL
        END as specification_midpoint,

        CASE
            WHEN t.test_result_value IS NOT NULL
                AND t.specification_lower_limit IS NOT NULL
                AND t.specification_upper_limit IS NOT NULL
            THEN ((t.test_result_value - t.specification_lower_limit) /
                  (t.specification_upper_limit - t.specification_lower_limit)) * 100
            ELSE NULL
        END as specification_range_pct,

        -- Flags
        t.pass_fail_flag,
        t.retest_flag,
        t.oos_flag,

        -- Quality metrics
        t.relative_std_deviation,

        -- Timestamps
        t.test_date,
        t.test_timestamp,
        t.ingestion_timestamp,

        -- Audit fields
        t.tested_by_user,
        t.reviewed_by_user,
        t.instrument_id,

        -- Metadata
        current_timestamp() as created_timestamp

    FROM analytical_tests t

    -- Join to batch dimension
    LEFT JOIN {{ ref('dim_batch') }} b
        ON t.batch_number = b.batch_number
        AND b.is_current = TRUE

    -- Join to product dimension (through batch)
    LEFT JOIN {{ ref('dim_product') }} p
        ON b.product_code = p.product_code
        AND p.is_current = TRUE

    -- Join to test method dimension
    LEFT JOIN {{ ref('dim_test_method') }} tm
        ON t.test_method_code = tm.test_method_code
        AND tm.is_current = TRUE

    -- Join to site dimension
    LEFT JOIN {{ ref('dim_site') }} s
        ON t.site_code = s.site_code
        AND s.is_current = TRUE

    -- Join to date dimension
    LEFT JOIN {{ ref('dim_date') }} d
        ON cast(t.test_date as date) = d.date_actual
)

SELECT
    {{ dbt_utils.generate_surrogate_key(['test_id']) }} as surrogate_key,
    *
FROM tests_with_dimensions
