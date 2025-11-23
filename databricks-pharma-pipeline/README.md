# Databricks Pharmaceutical Data Platform

## Executive Summary

A comprehensive, production-ready **Databricks Delta Lake solution** implementing a **medallion architecture** (Bronze, Silver, Gold) for pharmaceutical data management. This platform supports all phases of pharmaceutical development from **early-stage discovery to commercial manufacturing**, with full **Unity Catalog** integration and **regulatory compliance** (CFR Part 11, ALCOA+, EU GMP Annex 11).

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                     SOURCE SYSTEMS                                  │
├─────────────────────────────────────────────────────────────────────┤
│  MES (Syncade)  │  LIMS (LabWare)  │  EDC (Medidata Rave)  │  ERP  │
└────────┬─────────────────┬────────────────┬────────────────┬────────┘
         │                 │                │                │
         ├─────────────────┴────────────────┴────────────────┘
         │              Data Ingestion Layer
         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    BRONZE LAYER (Raw Zone)                          │
│                Unity Catalog: pharma_platform.bronze_raw            │
├─────────────────────────────────────────────────────────────────────┤
│  • manufacturing_batch_records      • analytical_test_results       │
│  • manufacturing_process_data       • qc_sample_data                │
│  • batch_genealogy                  • clinical_subjects             │
│  • equipment_sensor_data            • clinical_adverse_events       │
├─────────────────────────────────────────────────────────────────────┤
│  Features: Immutable, Partitioned, Change Data Feed, Watermarking   │
└────────────────────────┬────────────────────────────────────────────┘
                         │  Data Quality & Validation
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│              SILVER LAYER (Kimball Star Schema)                     │
│               Unity Catalog: pharma_platform.silver_cdm             │
├─────────────────────────────────────────────────────────────────────┤
│  DIMENSIONS (Type 2 SCD)          │  FACT TABLES (Atomic Grain)     │
│  • dim_product                    │  • fact_manufacturing_process   │
│  • dim_batch                      │  • fact_analytical_testing      │
│  • dim_equipment (ISA-88)         │  • fact_batch_genealogy         │
│  • dim_material                   │  • fact_clinical_observations   │
│  • dim_site                       │  • fact_equipment_utilization   │
│  • dim_test_method                │                                 │
│  • dim_study                      │  BRIDGE TABLES                  │
│  • dim_date                       │  • bridge_batch_materials       │
├─────────────────────────────────────────────────────────────────────┤
│  Features: Surrogate Keys, SCD Type 2, Conformed Dimensions         │
└────────────────────────┬────────────────────────────────────────────┘
                         │  Business Aggregations
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                GOLD LAYER (Business Analytics)                      │
│             Unity Catalog: pharma_platform.gold_analytics           │
├─────────────────────────────────────────────────────────────────────┤
│  • gold_batch_performance_summary  - Batch KPIs (FPY, OTD, etc.)    │
│  • gold_quality_kpi_dashboard      - Quality metrics, OOS tracking  │
│  • gold_equipment_oee              - Equipment effectiveness (OEE)  │
│  • gold_material_consumption       - Material usage & forecasting   │
│  • gold_clinical_enrollment        - Clinical trial metrics         │
├─────────────────────────────────────────────────────────────────────┤
│  Features: Aggregated, Optimized for BI, Scheduled Refresh          │
└─────────────────────────┬───────────────────────────────────────────┘
                          │
                          ▼
             ┌────────────────────────────┐
             │   BI & ANALYTICS TOOLS     │
             │  Tableau | Power BI        │
             │  Looker  | Databricks SQL  │
             └────────────────────────────┘
```

## Key Features

### 1. Medallion Architecture (Bronze → Silver → Gold)

- **Bronze Layer**: Raw, immutable data landing zone with full audit trail
- **Silver Layer**: Curated dimensional model following Kimball methodology
- **Gold Layer**: Business-level aggregations optimized for reporting

### 2. Kimball Star Schema (Silver Layer)

#### Dimensions (Type 2 SCD)
- **dim_product**: Product master with therapeutic area, molecule type, development phase
- **dim_batch**: Batch master linked to products and sites
- **dim_equipment**: Equipment with full ISA-88 7-level hierarchy
- **dim_material**: Material master (API, excipients, raw materials, finished products)
- **dim_site**: Manufacturing and clinical sites with regulatory information
- **dim_test_method**: Analytical testing methods with validation status
- **dim_study**: Clinical trial studies with enrollment tracking
- **dim_date**: Date dimension with fiscal calendar

#### Fact Tables (Atomic Grain)
- **fact_manufacturing_process**: Process parameters (temperature, pressure, pH, DO, etc.)
- **fact_analytical_testing**: Test results with specifications and pass/fail status
- **fact_batch_genealogy**: Material traceability and batch-to-batch relationships
- **fact_clinical_observations**: Clinical trial data (vitals, labs, assessments)
- **fact_equipment_utilization**: Daily equipment metrics for OEE calculation

### 3. Unity Catalog Integration

- **Catalog**: `pharma_platform`
- **Schemas**: `bronze_raw`, `silver_cdm`, `gold_analytics`, `metadata`
- **Features**:
  - Centralized governance and access control
  - Data lineage tracking
  - Audit logging
  - Row-level and column-level security support
  - Tag-based classification (PII, PHI, GxP)

### 4. Regulatory Compliance

- **21 CFR Part 11**: Electronic records and signatures
  - Change Data Feed enabled on all tables
  - Complete audit trail
  - User identification and timestamping

- **ALCOA+ Data Integrity**:
  - **A**ttributable: User tracking in all pipelines
  - **L**egible: Structured Delta tables
  - **C**ontemporaneous: Real-time ingestion timestamps
  - **O**riginal: Bronze layer immutability
  - **A**ccurate: Data quality validation
  - **Complete**: Full data lineage
  - **Consistent**: Standardized data models
  - **Enduring**: Long-term retention (25 years)
  - **Available**: Query-optimized Delta tables

- **EU GMP Annex 11**: Computerized systems validation
- **CDISC Standards**: Clinical data (SDTM/ADaM alignment)
- **ISA-88/ISA-95**: Manufacturing systems standards

### 5. ISA-88 Equipment Hierarchy

Full 7-level physical model implemented in `dim_equipment`:

```
Enterprise (Pharma Corporation)
  └── Site (Boston Manufacturing Plant)
      └── Area (Upstream Processing)
          └── Process Cell (Cell Culture Suite)
              └── Unit (Bioreactor Room 101)
                  └── Equipment Module (2KL Bioreactor)
                      └── Control Module (pH Controller)
```

### 6. Pharmaceutical Phase Coverage

The data model supports all development and commercial phases:

| Phase | Description | Data Captured |
|-------|-------------|---------------|
| Discovery | Target identification | Research data, assays |
| Preclinical | Animal studies | Safety studies, PK/PD |
| Phase 1 | First-in-human | Safety, PK, dose escalation |
| Phase 2 | Proof of concept | Efficacy, dose ranging |
| Phase 3 | Pivotal trials | Large-scale efficacy, safety |
| Commercial | Post-approval | Manufacturing, lot release, PMS |

### 7. Data Quality Framework

- **Metadata Schema**: `pharma_platform.metadata`
  - `pipeline_execution_log`: Audit trail for all pipeline runs
  - `data_quality_metrics`: DQ validation results
  - `data_lineage`: End-to-end lineage tracking
  - `watermark_tracking`: Incremental load state management

- **DQ Dimensions**:
  - **Completeness**: Null checks, mandatory field validation
  - **Accuracy**: Value range checks, specification limits
  - **Consistency**: Cross-table referential integrity
  - **Timeliness**: Data freshness monitoring
  - **Validity**: Format and data type validation

### 8. Table Constraints & ER Diagrams

- **PRIMARY KEY Constraints**: Added to all dimension and fact tables
  - 8 dimension tables (surrogate keys)
  - 4+ fact tables (atomic grain identifiers)
  - 2+ metadata tables

- **FOREIGN KEY Constraints**: Document all table relationships
  - 16+ fact-to-dimension relationships
  - Enables automatic ER diagram generation
  - BI tools (Power BI, Tableau) auto-detect relationships

- **Relationship Documentation**:
  - View: `pharma_platform.metadata.v_table_relationships`
  - Displays all FK relationships for data modeling tools
  - Supports Unity Catalog Data Explorer diagram visualization

- **Benefits**:
  - ✅ **Automatic ER diagrams** in data modeling tools (DbSchema, DataGrip, ER/Studio)
  - ✅ **BI tool integration** - relationships auto-detected for drag-and-drop analytics
  - ✅ **Data catalog metadata** - Unity Catalog shows relationship graph
  - ✅ **Documentation** - Self-documenting data model structure
  - ✅ **Query optimization** - Query planner uses constraint metadata

**Example Query:**
```sql
-- View all table relationships
SELECT * FROM pharma_platform.metadata.v_table_relationships
ORDER BY fact_table, foreign_key_column;

-- Verify constraints on a table
DESCRIBE EXTENDED pharma_platform.silver_cdm.dim_batch;
```

## Project Structure

```
databricks-pharma-pipeline/
├── RUN_ALL_SIMPLE.py                        # ⭐ ONE-CLICK EXECUTION - Run this!
├── 00_setup/
│   ├── 00_unity_catalog_setup.py           # Unity Catalog initialization
│   └── 01_add_constraints.py               # Add PKs and FKs for ER diagrams
├── 01_bronze/
│   ├── 01_bronze_manufacturing_ingestion_DEMO.py  # Demo: Synthetic manufacturing data
│   ├── 01_bronze_manufacturing_ingestion.py       # Prod: Real MES/DCS data
│   ├── 02_bronze_clinical_lims_ingestion_DEMO.py  # Demo: Synthetic clinical/LIMS data
│   └── 02_bronze_clinical_lims_ingestion.py       # Prod: Real EDC/LIMS data
├── 02_silver/
│   ├── 01_silver_dimensions_scd2.py         # Type 2 SCD dimensions
│   └── 02_silver_fact_tables.py             # Fact tables and date dimension
├── 03_gold/
│   └── 01_gold_batch_analytics.py           # Business aggregations
├── 04_orchestration/
│   └── orchestrate_pipeline.py              # Automated pipeline orchestration
├── config/
│   ├── unity_catalog_config.yaml            # Unity Catalog configuration
│   └── table_definitions.yaml               # Table schemas and metadata
└── docs/
    ├── EXECUTION_ORDER.md                   # Quick reference execution guide
    ├── DEMO_MODE_GUIDE.md                   # Using synthetic data
    ├── DEPLOYMENT_GUIDE.md                  # Production deployment
    └── NOTEBOOK_PATH_CONFIG.md              # Path configuration
```

## Getting Started

### ⚡ Quick Start (5 Minutes)

**Want to try it immediately?** Use demo mode with synthetic data:

1. **Import notebooks** to your Databricks workspace
2. **Open**: `RUN_ALL_SIMPLE.py`
3. **Attach** to a running cluster
4. **Click** "Run All"
5. ✅ Complete pipeline runs in 10-15 minutes!

**See**: [`docs/EXECUTION_ORDER.md`](docs/EXECUTION_ORDER.md) for detailed instructions

---

### Prerequisites

1. **Databricks Workspace**
   - Unity Catalog enabled
   - Cluster with Delta Lake support
   - DBR 13.3 LTS or higher recommended

2. **Access and Permissions**
   - Catalog CREATE permission
   - Schema CREATE permission
   - Table CREATE/MODIFY permissions

3. **For Production (optional for demo)**
   - JDBC drivers for SQL Server, Oracle
   - API credentials for EDC systems
   - S3/ADLS bucket for data lake storage

### Installation Steps

#### Step 1: Upload Notebooks to Databricks Workspace

```bash
# Using Databricks CLI
databricks workspace import_dir \
  ./databricks-pharma-pipeline \
  /Workspace/databricks-pharma-pipeline \
  --overwrite
```

Or use the Databricks UI: Workspace → Import → Folder

#### Step 2: Configure Secrets

Create a secret scope for connection credentials:

```python
# Using Databricks CLI
databricks secrets create-scope --scope pharma_platform

# Add secrets
databricks secrets put --scope pharma_platform --key mes_jdbc_hostname
databricks secrets put --scope pharma_platform --key mes_jdbc_username
databricks secrets put --scope pharma_platform --key mes_jdbc_password
databricks secrets put --scope pharma_platform --key lims_jdbc_hostname
databricks secrets put --scope pharma_platform --key edc_api_key
```

#### Step 3: Initialize Unity Catalog

Run the setup notebook:

```python
# Navigate to notebook and run
/databricks-pharma-pipeline/00_setup/00_unity_catalog_setup
```

This creates:
- Catalog: `pharma_platform`
- Schemas: `bronze_raw`, `silver_cdm`, `gold_analytics`, `metadata`
- Metadata tables for pipeline tracking

#### Step 4: Run Bronze Layer Ingestion

Execute bronze notebooks to ingest raw data:

```python
# Manufacturing data
/databricks-pharma-pipeline/01_bronze/01_bronze_manufacturing_ingestion

# Clinical and LIMS data
/databricks-pharma-pipeline/01_bronze/02_bronze_clinical_lims_ingestion
```

#### Step 5: Build Silver Layer (Dimensional Model)

```python
# Create dimensions (Type 2 SCD)
/databricks-pharma-pipeline/02_silver/01_silver_dimensions_scd2

# Create fact tables
/databricks-pharma-pipeline/02_silver/02_silver_fact_tables
```

#### Step 6: Create Gold Layer (Analytics)

```python
# Business aggregations
/databricks-pharma-pipeline/03_gold/01_gold_batch_analytics
```

#### Step 7: Orchestrate End-to-End Pipeline

```python
# Run complete pipeline
/databricks-pharma-pipeline/04_orchestration/orchestrate_pipeline
```

### Scheduling with Databricks Jobs

Create a Databricks Job to schedule the orchestration notebook:

1. **Jobs** → **Create Job**
2. **Task Name**: Pharma Platform Pipeline
3. **Type**: Notebook
4. **Path**: `/databricks-pharma-pipeline/04_orchestration/orchestrate_pipeline`
5. **Cluster**: Select or create cluster
6. **Schedule**: Daily at 2:00 AM (or as needed)
7. **Alerts**: Configure email/Slack notifications

## Key Metrics and KPIs

### Manufacturing Performance
- **First Pass Yield (FPY)**: Percentage of batches passing all quality tests on first attempt
- **On-Time Delivery (OTD)**: Percentage of batches completed on schedule
- **Cycle Time**: Duration from batch start to completion
- **Deviation Rate**: Number of deviations per batch

### Quality Metrics
- **Pass Rate**: Percentage of analytical tests passing specifications
- **Out of Specification (OOS)**: Count and rate of failed tests
- **Right First Time (RFT)**: Quality metric for manufacturing excellence

### Equipment Effectiveness
- **OEE (Overall Equipment Effectiveness)**: Availability × Performance × Quality
  - **World Class**: ≥85%
  - **Good**: 65-84%
  - **Fair**: 40-64%
  - **Poor**: <40%

### Clinical Trials
- **Enrollment Velocity**: Subjects enrolled per month
- **Enrollment %**: Actual vs. planned enrollment
- **Study Duration**: Days from start to completion

## Data Lineage Example

```
Source: MES Database (manufacturing_mes.dbo.batch_records)
   ↓
Bronze: pharma_platform.bronze_raw.manufacturing_batch_records
   ↓ [Join with product reference data]
Silver: pharma_platform.silver_cdm.dim_batch (Type 2 SCD)
   ↓ [Join with dim_product, dim_site, fact_manufacturing_process]
Gold: pharma_platform.gold_analytics.gold_batch_performance_summary
   ↓
BI Tool: Tableau Dashboard "Manufacturing KPI Overview"
```

All lineage tracked in `pharma_platform.metadata.data_lineage`

## Security and Governance

### Access Control Patterns

```sql
-- Grant read access to analysts
GRANT USE CATALOG ON CATALOG pharma_platform TO `data_analysts`;
GRANT USE SCHEMA, SELECT ON SCHEMA pharma_platform.silver_cdm TO `data_analysts`;
GRANT USE SCHEMA, SELECT ON SCHEMA pharma_platform.gold_analytics TO `data_analysts`;

-- Grant write access to data engineering
GRANT USE CATALOG, CREATE SCHEMA ON CATALOG pharma_platform TO `data_engineering`;
GRANT ALL PRIVILEGES ON SCHEMA pharma_platform.bronze_raw TO `data_engineering`;

-- Row-level security example (for clinical data)
CREATE FUNCTION pharma_platform.silver_cdm.mask_subject_id(subject_id STRING)
  RETURN CASE
    WHEN is_member('clinical_investigators') THEN subject_id
    ELSE 'MASKED'
  END;
```

### Data Classification Tags

Tables are tagged with:
- `data_classification`: raw/curated/analytical
- `contains_pii`: true/false
- `contains_phi`: true/false (for clinical data)
- `compliance_framework`: CFR_Part_11, ALCOA_Plus, EU_GMP_Annex_11
- `retention_policy`: 25_years

## Performance Optimization

### Partitioning Strategy

| Layer | Table | Partition Columns |
|-------|-------|-------------------|
| Bronze | manufacturing_batch_records | ingestion_date, site_code |
| Bronze | manufacturing_process_data | ingestion_date, unit_id |
| Bronze | analytical_test_results | ingestion_date |
| Silver | fact_manufacturing_process | date_key |
| Silver | fact_analytical_testing | date_key |

### Auto-Optimization

All tables configured with:
```sql
ALTER TABLE pharma_platform.silver_cdm.fact_manufacturing_process
SET TBLPROPERTIES (
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true'
);
```

### Z-Ordering

For frequently filtered columns:
```sql
OPTIMIZE pharma_platform.silver_cdm.fact_manufacturing_process
ZORDER BY (batch_key, equipment_key);
```

## Monitoring and Alerting

### Pipeline Monitoring

Query execution logs:
```sql
SELECT
  execution_id,
  pipeline_name,
  layer,
  execution_status,
  rows_written,
  execution_start_timestamp,
  execution_end_timestamp,
  TIMESTAMPDIFF(MINUTE, execution_start_timestamp, execution_end_timestamp) as duration_minutes
FROM pharma_platform.metadata.pipeline_execution_log
WHERE execution_start_timestamp >= current_date()
ORDER BY execution_start_timestamp DESC;
```

### Data Quality Alerts

Set up alerts for:
- Failed DQ checks (severity = CRITICAL)
- OOS results exceeding threshold
- Pipeline execution failures
- Data freshness violations

## BI Tool Integration

### Connecting Tableau

1. **Connector**: Databricks
2. **Server**: `<workspace-url>`
3. **HTTP Path**: From cluster configuration
4. **Authentication**: Personal Access Token
5. **Catalog**: `pharma_platform`
6. **Schema**: `gold_analytics` or `silver_cdm`

### Sample Dashboards

1. **Manufacturing Operations Dashboard**
   - Batch completion trends
   - Cycle time analysis
   - Deviation tracking
   - Equipment utilization

2. **Quality KPI Dashboard**
   - Pass rate trends
   - OOS analysis
   - Test method performance
   - Material quality trends

3. **Executive Dashboard**
   - Overall KPIs
   - Study enrollment status
   - Manufacturing throughput
   - Quality metrics summary

## Troubleshooting

### Common Issues

#### Issue: Table not found
```
Error: Table pharma_platform.silver_cdm.dim_product not found
```
**Solution**: Run Silver layer notebooks to create dimensional model

#### Issue: Missing foreign keys (orphaned records)
```
DQ Check - Orphaned batch keys: FAIL
```
**Solution**: Ensure Bronze layer data is complete before running Silver layer

#### Issue: Slow query performance
**Solution**:
1. Run OPTIMIZE on large tables
2. Check partitioning strategy
3. Review query execution plan
4. Consider Z-ordering on frequently filtered columns

## Support and Contact

For issues or questions:
- **Documentation**: See `docs/` folder
- **Architecture Diagrams**: Review data model HTML files in parent repository
- **GitHub Issues**: Create issue in repository

## License

This solution is provided as-is for pharmaceutical data platform implementation.

## Acknowledgments

- **Data Modeling**: Based on Kimball dimensional modeling methodology
- **Industry Standards**: ISA-88, ISA-95, CDISC, FDA guidelines
- **Technology**: Databricks, Delta Lake, Unity Catalog

---

**Version**: 1.0
**Last Updated**: 2025-11-22
**Author**: Databricks Solution Architecture Team
