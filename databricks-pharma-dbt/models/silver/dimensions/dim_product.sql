{{
    config(
        materialized='incremental',
        unique_key='surrogate_key',
        on_schema_change='sync_all_columns',
        tags=['dimension', 'scd_type2', 'product']
    )
}}

/*
    Dimension: Product

    Type: Type 2 Slowly Changing Dimension
    Grain: One row per product version
    Business Key: product_code

    Description:
        Product master dimension including therapeutic information,
        development phase, and molecule characteristics.

    SCD Type 2 Attributes:
        - surrogate_key: Auto-incrementing surrogate key
        - effective_start_date: Start date of this version
        - effective_end_date: End date of this version
        - is_current: Flag indicating current version

    Compliance:
        - CFR Part 11: Audit trail via SCD Type 2
        - ALCOA+: Complete history maintained
*/

WITH source_data AS (
    SELECT DISTINCT
        product_id as product_code,
        'Product ' || product_id as product_name,

        -- Therapeutic classification
        CASE
            WHEN product_id LIKE 'ONCO%' THEN 'Oncology'
            WHEN product_id LIKE 'CARD%' THEN 'Cardiology'
            WHEN product_id LIKE 'NEUR%' THEN 'Neurology'
            WHEN product_id LIKE 'IMMU%' THEN 'Immunology'
            ELSE 'Other'
        END as therapeutic_area,

        -- Molecule type
        CASE
            WHEN product_id LIKE '%mAb%' THEN 'Monoclonal Antibody'
            WHEN product_id LIKE '%ADC%' THEN 'Antibody-Drug Conjugate'
            WHEN product_id LIKE '%CAR-T%' THEN 'CAR-T Cell Therapy'
            ELSE 'Small Molecule'
        END as molecule_type,

        -- Development phase
        CASE
            WHEN product_id LIKE '%DEV%' THEN 'Development'
            WHEN product_id LIKE '%CLIN%' THEN 'Clinical'
            WHEN product_id LIKE '%COMM%' THEN 'Commercial'
            ELSE 'Research'
        END as development_phase,

        -- Regulatory information
        CASE
            WHEN product_id LIKE '%FDA%' THEN 'FDA Approved'
            WHEN product_id LIKE '%IND%' THEN 'IND Submitted'
            ELSE 'Preclinical'
        END as regulatory_status,

        -- Dosage form
        CASE
            WHEN molecule_type = 'Small Molecule' THEN 'Tablet'
            WHEN molecule_type LIKE '%Antibody%' THEN 'Injectable'
            WHEN molecule_type = 'CAR-T Cell Therapy' THEN 'Cell Therapy'
            ELSE 'Other'
        END as dosage_form,

        -- API strength
        CASE
            WHEN product_id LIKE '%100%' THEN '100 mg'
            WHEN product_id LIKE '%250%' THEN '250 mg'
            WHEN product_id LIKE '%500%' THEN '500 mg'
            ELSE '50 mg'
        END as strength,

        'mg' as strength_uom,
        TRUE as active_flag,
        'GMP' as quality_standard,

        current_timestamp() as source_system_timestamp

    FROM {{ source('pharma_raw', 'manufacturing_batch_records') }}
    WHERE ingestion_timestamp >= current_date() - INTERVAL 30 DAY
      AND product_id IS NOT NULL
),

source_with_hash AS (
    SELECT
        *,
        md5(concat_ws('||',
            coalesce(cast(product_code as string), 'NULL'),
            coalesce(cast(product_name as string), 'NULL'),
            coalesce(cast(therapeutic_area as string), 'NULL'),
            coalesce(cast(molecule_type as string), 'NULL'),
            coalesce(cast(development_phase as string), 'NULL'),
            coalesce(cast(regulatory_status as string), 'NULL'),
            coalesce(cast(dosage_form as string), 'NULL'),
            coalesce(cast(strength as string), 'NULL'),
            coalesce(cast(active_flag as string), 'NULL')
        )) as row_hash
    FROM source_data
)

{% if is_incremental() %}

, target_current AS (
    SELECT *
    FROM {{ this }}
    WHERE is_current = TRUE
)

, new_records AS (
    SELECT
        source.*,
        row_number() OVER (ORDER BY product_code) +
        coalesce((SELECT max(surrogate_key) FROM {{ this }}), 0) as surrogate_key,
        current_date() as effective_start_date,
        cast('9999-12-31' as date) as effective_end_date,
        TRUE as is_current,
        current_timestamp() as created_timestamp,
        current_timestamp() as updated_timestamp
    FROM source_with_hash source
    LEFT JOIN target_current target
        ON source.product_code = target.product_code
    WHERE target.product_code IS NULL
)

, changed_records AS (
    SELECT
        source.*,
        row_number() OVER (ORDER BY product_code) +
        coalesce((SELECT max(surrogate_key) FROM {{ this }}), 0) +
        (SELECT count(*) FROM new_records) as surrogate_key,
        current_date() as effective_start_date,
        cast('9999-12-31' as date) as effective_end_date,
        TRUE as is_current,
        target.created_timestamp,
        current_timestamp() as updated_timestamp
    FROM source_with_hash source
    INNER JOIN target_current target
        ON source.product_code = target.product_code
    WHERE source.row_hash != target.row_hash
)

-- Close out old versions
, updates_to_old_records AS (
    SELECT
        target.surrogate_key,
        current_date() - INTERVAL 1 DAY as effective_end_date,
        FALSE as is_current,
        current_timestamp() as updated_timestamp
    FROM target_current target
    INNER JOIN changed_records source
        ON target.product_code = source.product_code
)

SELECT * FROM new_records
UNION ALL
SELECT * FROM changed_records
UNION ALL
SELECT
    t.surrogate_key,
    t.product_code,
    t.product_name,
    t.therapeutic_area,
    t.molecule_type,
    t.development_phase,
    t.regulatory_status,
    t.dosage_form,
    t.strength,
    t.strength_uom,
    t.active_flag,
    t.quality_standard,
    t.source_system_timestamp,
    t.row_hash,
    t.effective_start_date,
    u.effective_end_date,
    u.is_current,
    t.created_timestamp,
    u.updated_timestamp
FROM {{ this }} t
INNER JOIN updates_to_old_records u
    ON t.surrogate_key = u.surrogate_key

{% else %}

-- Initial load: all records are current
SELECT
    row_number() OVER (ORDER BY product_code) as surrogate_key,
    *,
    current_date() as effective_start_date,
    cast('9999-12-31' as date) as effective_end_date,
    TRUE as is_current,
    current_timestamp() as created_timestamp,
    current_timestamp() as updated_timestamp
FROM source_with_hash

{% endif %}
