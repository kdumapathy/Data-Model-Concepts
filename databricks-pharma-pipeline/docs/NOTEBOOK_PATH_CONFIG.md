# Notebook Path Configuration Guide

## Issue Fixed

The orchestration notebook was using hardcoded paths like `/databricks-pharma-pipeline/...` which don't match the actual workspace location when notebooks are imported.

## Solution Applied

Added a configurable `NOTEBOOK_BASE_PATH` variable at the top of the orchestration notebook that allows easy configuration based on your workspace structure.

## Current Configuration

The notebook is now configured for your workspace location:

```python
NOTEBOOK_BASE_PATH = "/Workspace/Users/kd.umapathy@gmail.com/Data-Model-Concepts/databricks-pharma-pipeline"
```

## How to Use

### 1. No Changes Needed (Already Configured for You)

The orchestration notebook is already set to your workspace path:
- `/Workspace/Users/kd.umapathy@gmail.com/Data-Model-Concepts/databricks-pharma-pipeline`

### 2. Run the Orchestration Notebook

Simply open and run:
```
/Workspace/Users/kd.umapathy@gmail.com/Data-Model-Concepts/databricks-pharma-pipeline/04_orchestration/orchestrate_pipeline
```

All notebook paths will now resolve correctly!

## For Other Users (Path Configuration Examples)

If sharing this solution with others or moving to a different workspace location, update the `NOTEBOOK_BASE_PATH` variable:

### Example 1: Repos (Recommended for Git Integration)
```python
NOTEBOOK_BASE_PATH = "/Repos/john.doe/Data-Model-Concepts/databricks-pharma-pipeline"
```

### Example 2: Workspace - Personal Folder
```python
NOTEBOOK_BASE_PATH = "/Workspace/Users/jane.smith@company.com/Data-Model-Concepts/databricks-pharma-pipeline"
```

### Example 3: Workspace - Shared Folder
```python
NOTEBOOK_BASE_PATH = "/Workspace/Shared/databricks-pharma-pipeline"
```

## Updated Notebook Calls

All 5 notebook.run() calls now use the configurable path:

### Setup
```python
dbutils.notebook.run(
    f"{NOTEBOOK_BASE_PATH}/00_setup/00_unity_catalog_setup",
    timeout_seconds=600
)
```

### Bronze Layer
```python
# Manufacturing
dbutils.notebook.run(
    f"{NOTEBOOK_BASE_PATH}/01_bronze/01_bronze_manufacturing_ingestion",
    timeout_seconds=1200
)

# Clinical & LIMS
dbutils.notebook.run(
    f"{NOTEBOOK_BASE_PATH}/01_bronze/02_bronze_clinical_lims_ingestion",
    timeout_seconds=1200
)
```

### Silver Layer
```python
# Dimensions
dbutils.notebook.run(
    f"{NOTEBOOK_BASE_PATH}/02_silver/01_silver_dimensions_scd2",
    timeout_seconds=1800
)

# Facts
dbutils.notebook.run(
    f"{NOTEBOOK_BASE_PATH}/02_silver/02_silver_fact_tables",
    timeout_seconds=1800
)
```

### Gold Layer
```python
# Analytics
dbutils.notebook.run(
    f"{NOTEBOOK_BASE_PATH}/03_gold/01_gold_batch_analytics",
    timeout_seconds=1200
)
```

## Verification

When you run the orchestration notebook, you'll see the configured path in the output:

```
======================================================================
  PHARMACEUTICAL DATA PLATFORM - PIPELINE ORCHESTRATION
======================================================================
Execution ID: abc-123-def-456
Notebook Base Path: /Workspace/Users/kd.umapathy@gmail.com/Data-Model-Concepts/databricks-pharma-pipeline
Started at: 2025-11-22 10:30:00
======================================================================
```

## Troubleshooting

### Error: "Notebook not found"

**Check:**
1. Verify the notebooks were imported to Databricks
2. Confirm the `NOTEBOOK_BASE_PATH` matches your actual workspace location
3. Check the notebook path in Databricks UI and update `NOTEBOOK_BASE_PATH` accordingly

**To find your actual path:**
1. Open any notebook in Databricks
2. Look at the breadcrumb or path at the top
3. Copy everything BEFORE `/databricks-pharma-pipeline`
4. Update `NOTEBOOK_BASE_PATH` to: `<copied_path>/databricks-pharma-pipeline`

### Error: "Cannot access the notebook"

**Check permissions:**
- Ensure you have READ access to all notebooks in the folder
- If using Shared folder, verify group permissions

## Testing Individual Notebooks

You can also run notebooks individually using their full paths:

### Unity Catalog Setup
```
/Workspace/Users/kd.umapathy@gmail.com/Data-Model-Concepts/databricks-pharma-pipeline/00_setup/00_unity_catalog_setup
```

### Manufacturing Ingestion
```
/Workspace/Users/kd.umapathy@gmail.com/Data-Model-Concepts/databricks-pharma-pipeline/01_bronze/01_bronze_manufacturing_ingestion
```

### Silver Dimensions
```
/Workspace/Users/kd.umapathy@gmail.com/Data-Model-Concepts/databricks-pharma-pipeline/02_silver/01_silver_dimensions_scd2
```

## Git Workflow

The corrected orchestration notebook has been committed and pushed to:
- **Branch:** `claude/databricks-delta-pipeline-016M4jhaGDLDSuZEQLaJ8tLN`
- **Commit:** `36a6d36` - "Fix notebook paths in orchestrate_pipeline to use configurable base path"

To pull the latest changes in Databricks:
1. If using Repos: Click "Pull" in the Repos UI
2. If using Workspace: Re-import the updated notebook

---

**Last Updated:** 2025-11-22
**Status:** ✅ Ready to Use
