{% macro scd_type2_merge(
    target_table,
    source_table,
    business_key_columns,
    compare_columns,
    surrogate_key_column='surrogate_key',
    effective_start_date='effective_start_date',
    effective_end_date='effective_end_date',
    is_current='is_current',
    end_of_time='9999-12-31'
) %}

/*
  Macro to implement SCD Type 2 logic for slowly changing dimensions

  Parameters:
    - target_table: The target dimension table name
    - source_table: The source data (typically a CTE or ref)
    - business_key_columns: List of natural key columns
    - compare_columns: List of columns to compare for detecting changes
    - surrogate_key_column: Name of surrogate key (default: 'surrogate_key')
    - effective_start_date: Start date column name
    - effective_end_date: End date column name
    - is_current: Current record flag column name
    - end_of_time: Default end date for current records (default: '9999-12-31')

  Usage:
    {{ scd_type2_merge(
        target_table=this,
        source_table='source_data',
        business_key_columns=['product_code'],
        compare_columns=['product_name', 'therapeutic_area', 'development_phase']
    ) }}
*/

{%- set business_keys_join -%}
{%- for key in business_key_columns -%}
    target.{{ key }} = source.{{ key }}
    {%- if not loop.last %} AND {% endif -%}
{%- endfor -%}
{%- endset -%}

{%- set compare_columns_hash -%}
md5(concat_ws('||',
{%- for col in compare_columns -%}
    coalesce(cast({{ col }} as string), 'NULL')
    {%- if not loop.last %},{% endif -%}
{%- endfor -%}
))
{%- endset -%}

WITH source_with_hash AS (
    SELECT
        *,
        {{ compare_columns_hash }} as row_hash
    FROM {{ source_table }}
),

target_current AS (
    SELECT *
    FROM {{ target_table }}
    WHERE {{ is_current }} = TRUE
),

-- Identify new records (not in target)
new_records AS (
    SELECT
        source.*,
        ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) +
        COALESCE((SELECT MAX({{ surrogate_key_column }}) FROM {{ target_table }}), 0) as {{ surrogate_key_column }},
        current_date() as {{ effective_start_date }},
        cast('{{ end_of_time }}' as date) as {{ effective_end_date }},
        TRUE as {{ is_current }},
        current_timestamp() as created_timestamp,
        current_timestamp() as updated_timestamp
    FROM source_with_hash source
    LEFT JOIN target_current target
        ON {{ business_keys_join }}
    WHERE target.{{ business_key_columns[0] }} IS NULL
),

-- Identify changed records (different hash)
changed_records AS (
    SELECT
        source.*,
        ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) +
        COALESCE((SELECT MAX({{ surrogate_key_column }}) FROM {{ target_table }}), 0) +
        (SELECT COUNT(*) FROM new_records) as {{ surrogate_key_column }},
        current_date() as {{ effective_start_date }},
        cast('{{ end_of_time }}' as date) as {{ effective_end_date }},
        TRUE as {{ is_current }},
        target.created_timestamp,
        current_timestamp() as updated_timestamp
    FROM source_with_hash source
    INNER JOIN target_current target
        ON {{ business_keys_join }}
    WHERE source.row_hash != target.row_hash
),

-- Close out old versions of changed records
close_old_records AS (
    SELECT
        target.*,
        current_date() - INTERVAL 1 DAY as new_{{ effective_end_date }},
        FALSE as new_{{ is_current }}
    FROM target_current target
    INNER JOIN changed_records source
        ON {{ business_keys_join }}
)

-- Merge all changes
MERGE INTO {{ target_table }} as target
USING (
    -- Updated old records (closing them out)
    SELECT
        {{ surrogate_key_column }},
        new_{{ effective_end_date }} as {{ effective_end_date }},
        new_{{ is_current }} as {{ is_current }},
        current_timestamp() as updated_timestamp
    FROM close_old_records
) as updates
ON target.{{ surrogate_key_column }} = updates.{{ surrogate_key_column }}
WHEN MATCHED THEN UPDATE SET
    target.{{ effective_end_date }} = updates.{{ effective_end_date }},
    target.{{ is_current }} = updates.{{ is_current }},
    target.updated_timestamp = updates.updated_timestamp;

-- Insert new versions of changed records
INSERT INTO {{ target_table }}
SELECT * FROM changed_records;

-- Insert completely new records
INSERT INTO {{ target_table }}
SELECT * FROM new_records;

{% endmacro %}
