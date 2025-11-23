# Pharmaceutical Data Platform - dbt Implementation

## Overview

This is a **dbt (data build tool)** implementation of the pharmaceutical data platform, providing an alternative to the notebook-based approach. dbt enables version-controlled, tested, and documented data transformations with modern software engineering practices.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    SOURCE SYSTEMS                               │
│  MES (Manufacturing) │ LIMS (Lab) │ EDC (Clinical)             │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
          ┌─────────────┐
          │   Bronze    │  ← dbt sources + staging models
          │  (Raw Data) │
          └──────┬──────┘
                 │ dbt models
                 ▼
          ┌─────────────┐
          │   Silver    │  ← dbt dimensional models
          │ (Star Schema) │     • Type 2 SCD dimensions
          │              │     • Fact tables
          └──────┬───────┘
                 │ dbt models
                 ▼
          ┌─────────────┐
          │    Gold     │  ← dbt aggregations
          │ (Analytics) │
          └─────────────┘
```

## Key Features

### 1. Modern Data Engineering with dbt

- **Version Control**: All transformations in Git
- **Testing**: Built-in data quality tests
- **Documentation**: Auto-generated lineage and docs
- **CI/CD Ready**: Integrate with GitHub Actions, GitLab CI
- **Modularity**: Reusable macros and models

### 2. Medallion Architecture

- **Bronze Layer**: Source definitions and staging
- **Silver Layer**: Kimball star schema with Type 2 SCD
- **Gold Layer**: Business aggregations and KPIs

### 3. Databricks Integration

- **Unity Catalog**: Full catalog/schema support
- **Delta Lake**: ACID transactions and time travel
- **SQL Warehouse**: Optimized query performance
- **Databricks-dbt adapter**: Native integration

### 4. Regulatory Compliance

- **CFR Part 11**: Complete audit trail via version control + SCD Type 2
- **ALCOA+**: All data integrity principles embedded
- **GxP**: Validated data transformations
- **CDISC**: Clinical data standards

## Project Structure

```
databricks-pharma-dbt/
├── dbt_project.yml                # Project configuration
├── profiles.yml.example           # Connection profile template
├── packages.yml                   # dbt packages
├── README.md                      # This file
│
├── models/
│   ├── bronze/                    # Source definitions
│   │   ├── sources.yml           # Source table definitions
│   │   └── stg_*.sql             # Staging models (optional)
│   │
│   ├── silver/                    # Dimensional model
│   │   ├── dimensions/
│   │   │   ├── dim_product.sql   # Product dimension (SCD Type 2)
│   │   │   ├── dim_batch.sql
│   │   │   ├── dim_equipment.sql # ISA-88 hierarchy
│   │   │   ├── dim_material.sql
│   │   │   ├── dim_site.sql
│   │   │   ├── dim_test_method.sql
│   │   │   ├── dim_study.sql
│   │   │   └── dim_date.sql
│   │   │
│   │   └── facts/
│   │       ├── fact_manufacturing_process.sql
│   │       ├── fact_analytical_testing.sql
│   │       ├── fact_batch_genealogy.sql
│   │       ├── fact_clinical_observations.sql
│   │       └── bridge_batch_materials.sql
│   │
│   └── gold/                      # Analytics layer
│       ├── gold_batch_performance_summary.sql
│       ├── gold_quality_kpi_dashboard.sql
│       ├── gold_equipment_oee.sql
│       ├── gold_material_consumption_forecast.sql
│       └── gold_clinical_enrollment_tracking.sql
│
├── macros/
│   ├── generate_schema_name.sql  # Custom schema naming
│   ├── scd_type2_merge.sql       # SCD Type 2 macro
│   └── generate_row_hash.sql     # Hash generation
│
├── tests/
│   └── generic/                   # Custom generic tests
│
├── snapshots/                     # dbt snapshots (alternative to SCD Type 2)
│
└── seeds/                         # Reference data CSVs
    └── reference_*.csv
```

## Getting Started

### Prerequisites

1. **Python 3.8+**
2. **Databricks workspace** with Unity Catalog enabled
3. **SQL Warehouse** or cluster for dbt

### Installation

```bash
# 1. Clone the repository
cd databricks-pharma-dbt

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dbt-databricks
pip install dbt-databricks

# 4. Install dbt packages
dbt deps
```

### Configuration

#### 1. Set up profiles.yml

```bash
# Copy example profile
cp profiles.yml.example ~/.dbt/profiles.yml

# Edit with your credentials
nano ~/.dbt/profiles.yml
```

Update with your Databricks details:
```yaml
pharma_platform:
  target: dev
  outputs:
    dev:
      type: databricks
      catalog: pharma_platform
      schema: dev
      host: <your-workspace-url>
      http_path: /sql/1.0/warehouses/<warehouse-id>
      token: "{{ env_var('DBT_DATABRICKS_TOKEN') }}"
      threads: 4
```

#### 2. Set environment variable

```bash
# Set your Databricks token
export DBT_DATABRICKS_TOKEN="dapi..."
```

#### 3. Test connection

```bash
dbt debug
```

You should see:
```
All checks passed!
```

### Running dbt

#### Full pipeline execution

```bash
# Run all models (Bronze → Silver → Gold)
dbt run

# Run with tests
dbt build

# Run specific layer
dbt run --select silver.*
dbt run --select gold.*

# Run specific model and downstream dependencies
dbt run --select dim_product+
```

#### Testing

```bash
# Run all tests
dbt test

# Run tests for specific models
dbt test --select dim_product
dbt test --select silver.*

# Run specific test types
dbt test --select test_type:unique
dbt test --select test_type:not_null
```

#### Documentation

```bash
# Generate documentation
dbt docs generate

# Serve documentation locally
dbt docs serve
```

This will open a browser with:
- **Lineage graph**: Visual DAG of model dependencies
- **Model documentation**: All columns, tests, descriptions
- **Source freshness**: Data freshness checks

### Development Workflow

```bash
# 1. Create feature branch
git checkout -b feature/new-dimension

# 2. Develop models
# Edit models/silver/dimensions/dim_new.sql

# 3. Run and test locally
dbt run --select dim_new
dbt test --select dim_new

# 4. Generate docs
dbt docs generate

# 5. Commit and push
git add .
git commit -m "Add new dimension"
git push origin feature/new-dimension

# 6. Create pull request
```

## dbt vs. Notebooks Comparison

| Aspect | dbt | Notebooks |
|--------|-----|-----------|
| **Version Control** | ✅ Native Git integration | ⚠️ Requires manual export |
| **Testing** | ✅ Built-in test framework | ⚠️ Manual test notebooks |
| **Documentation** | ✅ Auto-generated lineage | ⚠️ Manual documentation |
| **Modularity** | ✅ Reusable macros, refs | ⚠️ Copy-paste code |
| **CI/CD** | ✅ Easy GitHub Actions integration | ⚠️ Complex setup |
| **Learning Curve** | ⚠️ dbt concepts to learn | ✅ Familiar notebook interface |
| **Debugging** | ⚠️ Compiled SQL only | ✅ Interactive cell execution |
| **Data Preview** | ⚠️ Separate query needed | ✅ Inline results |

**Recommendation**: Use **dbt** for production pipelines with team collaboration. Use **notebooks** for exploratory analysis and ad-hoc queries.

## Advanced Features

### 1. Incremental Models

```sql
{{ config(materialized='incremental', unique_key='id') }}

SELECT * FROM {{ source('pharma_raw', 'batch_records') }}

{% if is_incremental() %}
WHERE ingestion_timestamp > (SELECT max(ingestion_timestamp) FROM {{ this }})
{% endif %}
```

### 2. SCD Type 2 Dimensions

```sql
-- See models/silver/dimensions/dim_product.sql for full implementation
{{ config(materialized='incremental', unique_key='surrogate_key') }}

-- Automatically tracks history with effective dates
```

### 3. Custom Tests

```yaml
# models/silver/dimensions/schema.yml
models:
  - name: dim_product
    tests:
      - dbt_expectations.expect_table_row_count_to_be_between:
          min_value: 1
          max_value: 10000
    columns:
      - name: product_code
        tests:
          - unique
          - not_null
          - dbt_expectations.expect_column_values_to_match_regex:
              regex: "^[A-Z]{4}[0-9]{3}$"
```

### 4. Macros for Reusability

```sql
-- macros/scd_type2_merge.sql
{% macro scd_type2_merge(target, source, business_keys) %}
-- Reusable SCD Type 2 logic
{% endmacro %}

-- Use in models:
{{ scd_type2_merge(this, 'source_data', ['product_code']) }}
```

## CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/dbt_ci.yml
name: dbt CI

on:
  pull_request:
    branches: [main]

jobs:
  dbt-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Install dbt
        run: pip install dbt-databricks

      - name: Run dbt tests
        env:
          DBT_DATABRICKS_TOKEN: ${{ secrets.DBT_DATABRICKS_TOKEN }}
        run: |
          dbt deps
          dbt run --target dev
          dbt test --target dev
```

## Best Practices

### 1. Model Naming

- **Staging**: `stg_<source>_<table>`
- **Dimensions**: `dim_<entity>`
- **Facts**: `fact_<process>`
- **Gold**: `gold_<subject>_<metric>`

### 2. Materialization Strategy

- **Sources**: Not materialized (references only)
- **Staging**: Views (lightweight transformations)
- **Dimensions**: Tables (SCD Type 2 requires persistence)
- **Facts**: Incremental (large volume data)
- **Gold**: Tables (pre-aggregated for performance)

### 3. Testing Strategy

- **Sources**: Freshness tests
- **Dimensions**: Unique, not_null on business keys
- **Facts**: Relationship tests to dimensions
- **Gold**: Accepted values, range checks

### 4. Documentation

- Add descriptions to all models in `schema.yml`
- Document business logic in model SQL comments
- Use `dbt docs generate` before each release

## Troubleshooting

### Connection Issues

```bash
# Test connection
dbt debug

# Check profiles.yml location
dbt debug --config-dir

# Verify token
echo $DBT_DATABRICKS_TOKEN
```

### Model Errors

```bash
# Show compiled SQL
dbt compile --select model_name

# View compiled file
cat target/compiled/pharma_platform_dbt/models/...

# Run with verbose logging
dbt run --select model_name --debug
```

### Performance Optimization

```sql
-- Add partition and optimize
{{ config(
    partition_by=['test_date'],
    post_hook='OPTIMIZE {{ this }} ZORDER BY (batch_number)'
) }}
```

## Migration from Notebooks

To migrate from the notebook-based implementation:

1. **Bronze layer**: Define sources in `models/bronze/sources.yml`
2. **Silver layer**: Convert notebooks to dbt models, implement SCD Type 2
3. **Gold layer**: Convert aggregation notebooks to dbt models
4. **Tests**: Add data quality tests
5. **Run**: Execute `dbt run` to rebuild
6. **Validate**: Compare results with notebook output

## Resources

- **dbt Documentation**: https://docs.getdbt.com
- **dbt-databricks**: https://github.com/databricks/dbt-databricks
- **Discourse Community**: https://discourse.getdbt.com
- **dbt Slack**: https://www.getdbt.com/community/join-the-community

## Support

For issues or questions:
1. Check dbt logs: `logs/dbt.log`
2. Review compiled SQL: `target/compiled/`
3. Consult dbt docs: `dbt docs serve`
4. Open GitHub issue

---

**Version**: 1.0.0
**Last Updated**: 2025-11-23
**dbt Version**: >= 1.6.0
**Databricks Runtime**: >= 13.0
