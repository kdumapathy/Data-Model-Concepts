# Pharmaceutical Data Model for Databricks

A production-ready implementation of a comprehensive pharmaceutical data model in Databricks, covering the complete drug development lifecycle from discovery through commercial manufacturing.

## 📋 Overview

This project implements a **Kimball Bus Architecture** data warehouse with three star schemas supporting:
- **Process Execution** tracking (manufacturing events and parameters)
- **Analytical Testing** (quality control, stability studies, release testing)
- **Genealogy & Traceability** (material lineage, batch genealogy, GBT compliance)

### Key Features

✅ **23 Tables** across Bronze/Silver/Gold layers
✅ **3 Star Schemas** with 8 conformed dimensions
✅ **4 Self-Join Hierarchies** (material lineage, batch genealogy, process taxonomies)
✅ **SCD Type 2** implementation on all dimension tables
✅ **100,000+ rows** of realistic sample data
✅ **Automated CI/CD** via GitHub Actions
✅ **Delta Lake** format with optimization
✅ **Medallion Architecture** (Bronze → Silver → Gold)

## 🏗️ Architecture

### Data Model Structure

```
┌─────────────────────────────────────────────────────────────┐
│                      GOLD LAYER                              │
│               (Business-Ready Star Schemas)                  │
├─────────────────────────────────────────────────────────────┤
│  Process Star          │  Analytical Star  │  Genealogy Star │
│  • Fact: Mfg Process   │  • Fact: Test     │  • Fact: Material│
│    Results             │    Results        │    Usage         │
│  • 11 Dimensions       │  • 14 Dimensions  │  • 4 Dimensions  │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌─────────────────────────────────────────────────────────────┐
│                     SILVER LAYER                             │
│           (Validated & Conformed with SCD Type 2)            │
├─────────────────────────────────────────────────────────────┤
│  • 8 Conformed Dimensions (Batch, Material, Sample, etc.)    │
│  • 2 Process Dimensions (Local & Common Hierarchies)         │
│  • 6 Analytical Dimensions (Test, Method, Study, etc.)       │
│  • 3 Genealogy Dimensions (Material Lot, Transformation, PO) │
│  • 1 Bridge Table (Batch Genealogy)                          │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌─────────────────────────────────────────────────────────────┐
│                     BRONZE LAYER                             │
│              (Raw Landing with Audit Columns)                │
└─────────────────────────────────────────────────────────────┘
```

### Conformed Dimensions (Shared Across Star Schemas)

1. **Batch** - Manufacturing batches with genealogy hierarchy
2. **Material** - Materials with lineage (Vector → Cell Line → MCB → WCB → Protein)
3. **Sample** - Sample tracking
4. **Manufacturer** - Manufacturing sites, CMOs, testing labs
5. **Specification** - Acceptance criteria and limits
6. **Notification** - Deviations, CAPAs, investigations
7. **Document** - Batch records, COAs, SOPs, protocols
8. **Source System** - LIMS, MES, ELN, ERP systems

## 🚀 Quick Start

### Prerequisites

1. **Databricks Account** (Community Edition or higher)
2. **GitHub Account** with repository access
3. **GitHub Secrets** configured:
   - `DATABRICKS_HOST` - Your Databricks workspace URL
   - `DATABRICKS_TOKEN` - Personal Access Token

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/pharma-databricks-model.git
cd pharma-databricks-model

# 2. Set up environment variables
cp .env.example .env
# Edit .env with your Databricks credentials

# 3. Install dependencies locally (optional, for development)
pip install -r requirements.txt
```

### Deployment Options

#### Option A: Automated Deployment (Recommended)

1. Configure GitHub Secrets in repository settings
2. Push to `main` branch:
   ```bash
   git push origin main
   ```
3. GitHub Actions will automatically:
   - Validate code
   - Deploy DDL scripts to DBFS
   - Upload notebooks to Databricks workspace
   - Generate deployment report

#### Option B: Manual Deployment

1. **Upload files to Databricks:**
   ```bash
   # Using Databricks CLI
   databricks fs cp -r ./ddl/ dbfs:/pharma-model/ddl/ --overwrite
   databricks fs cp -r ./src/ dbfs:/pharma-model/src/ --overwrite
   databricks workspace import-dir ./notebooks /pharma-model/notebooks --overwrite
   ```

2. **Execute DDL scripts** in Databricks SQL Editor:
   - Run scripts in order: Bronze → Silver → Gold
   - Or import and run setup notebooks

3. **Generate sample data:**
   - Open `/pharma-model/notebooks/bronze/load_bronze_data.py`
   - Run all cells to generate realistic data

## 📊 Data Model Details

### Material Lineage Hierarchy

```
Expression Vector (Level 0)
    ├── Cell Line (Level 1)
    │   ├── Master Cell Bank - MCB (Level 2)
    │   │   ├── Working Cell Bank - WCB (Level 3)
    │   │   │   └── Therapeutic Protein (Level 4)
```

**Example:**
```
pCDNA-CMV-Vec1
  → CHO-K1-CL1
    → MCB-2024-0015
      → WCB-2024-0045
        → mAb-Anti-PD1-TP001
```

### Batch Genealogy Scenarios

**Batch Split (1 → Many):**
```
Parent Batch: BATCH-2024-00001 (1000L)
  ├── Child A: BATCH-2024-00002 (400L) - 40%
  ├── Child B: BATCH-2024-00003 (400L) - 40%
  └── Child C: BATCH-2024-00004 (200L) - 20%
```

**Batch Merge (Many → 1):**
```
BATCH-2024-00010 (100L) ───┐
BATCH-2024-00011 (100L) ───┼──> BATCH-2024-00020 (300L)
BATCH-2024-00012 (100L) ───┘
```

### Typical Workflows Supported

#### Cell Culture Process
```
Thaw → Seed → N-1 Expansion → Production Bioreactor → Harvest
```

#### Downstream Processing
```
Centrifugation → Depth Filtration → Protein A Chromatography
→ Viral Inactivation → Polishing → UF/DF → Formulation
```

#### Stability Testing
```
Manufacturing → T0 Testing → 1mo → 3mo → 6mo → 12mo → 24mo → 36mo
Conditions: 2-8°C, 25°C/60%RH, 40°C/75%RH
```

## 📖 Sample Queries

### 1. Material Lineage Trace

```sql
-- Recursive query to trace material hierarchy
WITH RECURSIVE material_lineage AS (
    -- Base: Root materials (no parent)
    SELECT
        material_identity,
        material_ID,
        material_name,
        material_type,
        parent_material_identity,
        1 AS level
    FROM silver.v_dim_material_current
    WHERE parent_material_identity IS NULL

    UNION ALL

    -- Recursive: Children
    SELECT
        m.material_identity,
        m.material_ID,
        m.material_name,
        m.material_type,
        m.parent_material_identity,
        ml.level + 1
    FROM silver.v_dim_material_current m
    INNER JOIN material_lineage ml
        ON m.parent_material_identity = ml.material_identity
)
SELECT
    level,
    material_ID,
    material_name,
    material_type
FROM material_lineage
ORDER BY level, material_name;
```

### 2. Batch Genealogy with Contribution %

```sql
-- Trace batch genealogy including splits and merges
SELECT
    child.batch_ID AS child_batch,
    child.batch_status AS child_status,
    parent.batch_ID AS parent_batch,
    bg.contribution_percent,
    bg.relationship_type,
    child.batch_size AS child_size,
    parent.batch_size AS parent_size
FROM silver.bridge_batch_genealogy bg
INNER JOIN silver.v_dim_batch_current child
    ON bg.child_batch_identity = child.batch_identity
INNER JOIN silver.v_dim_batch_current parent
    ON bg.parent_batch_identity = parent.batch_identity
ORDER BY child.batch_ID, bg.sequence_order;
```

### 3. Process Execution Metrics by Batch

```sql
-- Aggregate process metrics for each batch
SELECT
    b.batch_ID,
    m.material_name,
    lp.process_step_name,
    COUNT(*) AS execution_count,
    AVG(f.yield_value) AS avg_yield,
    AVG(f.viability_percent) AS avg_viability,
    AVG(f.temperature_celsius) AS avg_temperature,
    AVG(f.pH_value) AS avg_pH
FROM gold.fact_manufacturing_process_results f
INNER JOIN silver.v_dim_batch_current b
    ON f.batch_identity = b.batch_identity
INNER JOIN silver.v_dim_material_current m
    ON f.source_material_identity = m.material_identity
INNER JOIN silver.v_dim_local_process_hierarchy_current lp
    ON f.local_process_identity = lp.local_process_identity
GROUP BY b.batch_ID, m.material_name, lp.process_step_name
ORDER BY b.batch_ID, lp.process_step_name;
```

### 4. Stability Study Results by Timepoint

```sql
-- Stability test results across timepoints
SELECT
    b.batch_ID,
    s.study_name,
    t.test_name,
    c.storage_condition,
    tp.timepoint_label,
    AVG(f.test_result) AS avg_result,
    COUNT(CASE WHEN f.oos_flag = true THEN 1 END) AS oos_count
FROM gold.fact_analytical_results f
INNER JOIN silver.v_dim_batch_current b
    ON f.batch_identity = b.batch_identity
INNER JOIN silver.v_dim_study_current s
    ON f.study_identity = s.study_identity
INNER JOIN silver.v_dim_test_current t
    ON f.test_identity = t.test_identity
INNER JOIN silver.v_dim_condition_current c
    ON f.condition_identity = c.condition_identity
INNER JOIN silver.v_dim_timepoint_current tp
    ON f.timepoint_identity = tp.timepoint_identity
WHERE s.study_type = 'Stability'
GROUP BY
    b.batch_ID, s.study_name, t.test_name,
    c.storage_condition, tp.timepoint_label, tp.timepoint_value
ORDER BY
    b.batch_ID, t.test_name, tp.timepoint_value;
```

### 5. Out-of-Specification (OOS) Investigations

```sql
-- All OOS results with investigation details
SELECT
    b.batch_ID,
    m.material_name,
    t.test_name,
    f.test_result,
    f.test_uom,
    sp.lower_limit,
    sp.upper_limit,
    n.notification_ID,
    n.notification_type,
    n.severity_level,
    n.notification_status,
    d.document_title
FROM gold.fact_analytical_results f
INNER JOIN silver.v_dim_batch_current b
    ON f.batch_identity = b.batch_identity
INNER JOIN silver.v_dim_material_current m
    ON f.source_material_identity = m.material_identity
INNER JOIN silver.v_dim_test_current t
    ON f.test_identity = t.test_identity
LEFT JOIN silver.v_dim_specification_current sp
    ON f.specification_identity = sp.specification_identity
LEFT JOIN silver.dim_notification n
    ON f.notification_identity = n.notification_identity
LEFT JOIN silver.dim_document d
    ON f.document_identity = d.document_identity
WHERE f.oos_flag = true
ORDER BY f.test_timestamp DESC;
```

More queries available in `/docs/sample_queries.md`

## 📁 Project Structure

```
pharma-databricks-model/
├── .github/
│   └── workflows/
│       └── databricks-deploy.yml      # CI/CD pipeline
├── ddl/
│   ├── bronze/                        # 6 SQL scripts
│   ├── silver/                        # 6 SQL scripts
│   └── gold/                          # 4 SQL scripts
├── src/
│   ├── data_generators/               # Data generation framework
│   ├── schemas/                       # PySpark schemas
│   ├── transformations/               # Bronze→Silver→Gold
│   └── main_data_generation.py        # Orchestrator
├── notebooks/
│   ├── setup/                         # Environment setup
│   ├── bronze/                        # Bronze layer notebooks
│   ├── silver/                        # Silver layer notebooks
│   ├── gold/                          # Gold layer notebooks
│   └── analysis/                      # Sample queries
├── scripts/
│   ├── manage_cluster.py              # Cluster automation
│   ├── execute_ddl.py                 # DDL execution
│   └── data_quality_checks.py         # Validation
├── config/
│   ├── databricks_config.json         # Project config
│   └── cluster_config.json            # Cluster specs
├── docs/
│   ├── data_dictionary.md             # Complete data dictionary
│   ├── deployment_guide.md            # Step-by-step deployment
│   └── sample_queries.md              # Additional queries
├── tests/
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment template
└── README.md                          # This file
```

## 🔧 Configuration

### Environment Variables

Create `.env` file from template:

```bash
# Databricks Connection
DATABRICKS_HOST=https://adb-xxxxxxxxxxxx.azuredatabricks.net
DATABRICKS_TOKEN=dapi_your_token_here

# Data Generation
SAMPLE_DATA_SEED=42
NUM_MATERIALS=200
NUM_BATCHES=150
NUM_SAMPLES=500
NUM_PROCESS_RESULTS=10000
NUM_ANALYTICAL_RESULTS=10000
NUM_GENEALOGY_RECORDS=8000
```

### GitHub Secrets

Configure in repository settings → Secrets and variables → Actions:

- `DATABRICKS_HOST` - Your Databricks workspace URL
- `DATABRICKS_TOKEN` - Personal Access Token (Scope: workspace, clusters, SQL, jobs)

## 📚 Documentation

- [Data Dictionary](docs/data_dictionary.md) - Complete entity and attribute definitions
- [Deployment Guide](docs/deployment_guide.md) - Step-by-step deployment instructions
- [Sample Queries](docs/sample_queries.md) - 15+ analytical queries with explanations
- [Architecture Overview](docs/architecture.md) - Detailed architecture documentation

## 🧪 Testing

```bash
# Run unit tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Lint code
pylint src/
black src/ --check
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- Based on pharmaceutical industry best practices
- Implements Kimball dimensional modeling methodology
- Supports FDA 21 CFR Part 11 and GMP requirements
- Designed for batch genealogy traceability (GBT) compliance

## 📞 Support

For issues or questions:
- Open an issue on GitHub
- Check documentation in `/docs/`
- Review sample queries in `/docs/sample_queries.md`

## 🎯 Roadmap

- [ ] Add equipment master data (ISA-88)
- [ ] Implement recipe/formula management
- [ ] Add real-time monitoring dashboard
- [ ] Integrate with external LIMS/MES systems
- [ ] Add ML models for process optimization
- [ ] Implement data versioning with Delta Lake time travel

---

**Built with ❤️ for the Pharmaceutical Data Science Community**
