# Databricks notebook source
# MAGIC %md
# MAGIC # Add Primary Key and Foreign Key Constraints
# MAGIC
# MAGIC **Purpose:** Add PRIMARY KEY and FOREIGN KEY constraints to all tables for:
# MAGIC - Data integrity enforcement
# MAGIC - Relationship visualization in ER diagrams
# MAGIC - Query optimization
# MAGIC - Documentation of table relationships
# MAGIC
# MAGIC **Constraints Added:**
# MAGIC - PRIMARY KEY on all dimension surrogate keys
# MAGIC - PRIMARY KEY on all fact table composite keys
# MAGIC - FOREIGN KEY relationships between facts and dimensions
# MAGIC - FOREIGN KEY relationships for bridge tables
# MAGIC
# MAGIC **Note:** Delta Lake supports constraint metadata for documentation and diagram generation.
# MAGIC Constraints are informational in Delta Lake (not enforced at write time) but are used by:
# MAGIC - BI tools (Power BI, Tableau)
# MAGIC - Data modeling tools
# MAGIC - Databricks SQL analytics
# MAGIC - Query optimizers

# COMMAND ----------

import uuid
from datetime import datetime

# Configuration
catalog_name = "pharma_platform"
bronze_schema = "bronze_raw"
silver_schema = "silver_cdm"
gold_schema = "gold_analytics"
meta_schema = "metadata"

execution_id = str(uuid.uuid4())
pipeline_name = "add_table_constraints"

print(f"Execution ID: {execution_id}")
print(f"Pipeline: {pipeline_name}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Add Primary Keys to Dimension Tables

# COMMAND ----------

# Silver Layer Dimensions
dimensions_pk = [
    ("dim_product", "product_id"),
    ("dim_batch", "batch_id"),
    ("dim_equipment", "equipment_id"),
    ("dim_material", "material_id"),
    ("dim_site", "site_id"),
    ("dim_test_method", "test_method_id"),
    ("dim_study", "study_id"),
    ("dim_date", "date_id")
]

print("Adding PRIMARY KEY constraints to dimensions...")
for table_name, pk_column in dimensions_pk:
    full_table = f"{catalog_name}.{silver_schema}.{table_name}"

    try:
        # Add primary key constraint
        spark.sql(f"""
            ALTER TABLE {full_table}
            ADD CONSTRAINT pk_{table_name}
            PRIMARY KEY({pk_column}) NOT ENFORCED
        """)
        print(f"✓ {table_name}: PRIMARY KEY({pk_column})")
    except Exception as e:
        if "already exists" in str(e).lower():
            print(f"  {table_name}: PRIMARY KEY already exists")
        else:
            print(f"✗ {table_name}: {str(e)}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Add Primary Keys to Fact Tables

# COMMAND ----------

# Fact tables with composite primary keys
facts_pk = [
    ("fact_manufacturing_process", ["process_data_id"]),
    ("fact_analytical_testing", ["test_id"]),
    ("fact_batch_genealogy", ["genealogy_id"]),
    ("fact_clinical_observations", ["observation_id"])
]

print("\nAdding PRIMARY KEY constraints to fact tables...")
for table_name, pk_columns in facts_pk:
    full_table = f"{catalog_name}.{silver_schema}.{table_name}"
    pk_cols_str = ", ".join(pk_columns)

    try:
        spark.sql(f"""
            ALTER TABLE {full_table}
            ADD CONSTRAINT pk_{table_name}
            PRIMARY KEY({pk_cols_str}) NOT ENFORCED
        """)
        print(f"✓ {table_name}: PRIMARY KEY({pk_cols_str})")
    except Exception as e:
        if "already exists" in str(e).lower():
            print(f"  {table_name}: PRIMARY KEY already exists")
        else:
            print(f"✗ {table_name}: {str(e)}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Add Foreign Keys from Facts to Dimensions

# COMMAND ----------

# Foreign key relationships: (fact_table, fk_column, referenced_table, referenced_column)
foreign_keys = [
    # fact_manufacturing_process relationships
    ("fact_manufacturing_process", "batch_key", "dim_batch", "batch_id"),
    ("fact_manufacturing_process", "product_key", "dim_product", "product_id"),
    ("fact_manufacturing_process", "equipment_key", "dim_equipment", "equipment_id"),
    ("fact_manufacturing_process", "site_key", "dim_site", "site_id"),
    ("fact_manufacturing_process", "date_key", "dim_date", "date_id"),

    # fact_analytical_testing relationships
    ("fact_analytical_testing", "batch_key", "dim_batch", "batch_id"),
    ("fact_analytical_testing", "product_key", "dim_product", "product_id"),
    ("fact_analytical_testing", "test_method_key", "dim_test_method", "test_method_id"),
    ("fact_analytical_testing", "site_key", "dim_site", "site_id"),
    ("fact_analytical_testing", "date_key", "dim_date", "date_id"),

    # fact_batch_genealogy relationships
    ("fact_batch_genealogy", "child_batch_key", "dim_batch", "batch_id"),
    ("fact_batch_genealogy", "parent_batch_key", "dim_batch", "batch_id"),

    # fact_clinical_observations relationships
    ("fact_clinical_observations", "study_key", "dim_study", "study_id"),
    ("fact_clinical_observations", "site_key", "dim_site", "site_id"),
    ("fact_clinical_observations", "date_key", "dim_date", "date_id"),

    # bridge_batch_materials relationships
    ("bridge_batch_materials", "batch_key", "dim_batch", "batch_id"),
    ("bridge_batch_materials", "material_key", "dim_material", "material_id")
]

print("\nAdding FOREIGN KEY constraints...")
for fact_table, fk_column, ref_table, ref_column in foreign_keys:
    full_fact_table = f"{catalog_name}.{silver_schema}.{fact_table}"
    full_ref_table = f"{catalog_name}.{silver_schema}.{ref_table}"
    constraint_name = f"fk_{fact_table}_{fk_column}"

    try:
        # Check if fact table exists
        if not spark.catalog.tableExists(full_fact_table):
            print(f"  {fact_table}: table does not exist, skipping")
            continue

        spark.sql(f"""
            ALTER TABLE {full_fact_table}
            ADD CONSTRAINT {constraint_name}
            FOREIGN KEY({fk_column}) REFERENCES {full_ref_table}({ref_column}) NOT ENFORCED
        """)
        print(f"✓ {fact_table}.{fk_column} → {ref_table}.{ref_column}")
    except Exception as e:
        if "already exists" in str(e).lower():
            print(f"  {constraint_name}: already exists")
        else:
            print(f"✗ {constraint_name}: {str(e)}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Add Primary Keys to Metadata Tables

# COMMAND ----------

metadata_pk = [
    ("pipeline_execution_log", "execution_id"),
    ("data_quality_log", "quality_check_id")
]

print("\nAdding PRIMARY KEY constraints to metadata tables...")
for table_name, pk_column in metadata_pk:
    full_table = f"{catalog_name}.{meta_schema}.{table_name}"

    try:
        if not spark.catalog.tableExists(full_table):
            print(f"  {table_name}: table does not exist, skipping")
            continue

        spark.sql(f"""
            ALTER TABLE {full_table}
            ADD CONSTRAINT pk_{table_name}
            PRIMARY KEY({pk_column}) NOT ENFORCED
        """)
        print(f"✓ {table_name}: PRIMARY KEY({pk_column})")
    except Exception as e:
        if "already exists" in str(e).lower():
            print(f"  {table_name}: PRIMARY KEY already exists")
        else:
            print(f"✗ {table_name}: {str(e)}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Display All Constraints

# COMMAND ----------

print(f"\n{'='*80}")
print("Table Constraints Summary")
print(f"{'='*80}\n")

# Get all tables in silver schema
silver_tables = spark.sql(f"SHOW TABLES IN {catalog_name}.{silver_schema}").collect()

for table_row in silver_tables:
    table_name = table_row['tableName']
    full_table = f"{catalog_name}.{silver_schema}.{table_name}"

    try:
        # Get table properties to see constraints
        desc_output = spark.sql(f"DESCRIBE DETAIL {full_table}").collect()

        # Get extended table info
        desc_extended = spark.sql(f"DESCRIBE EXTENDED {full_table}").collect()

        # Look for constraint information in table properties
        constraints_found = False
        for row in desc_extended:
            if row['col_name'] and 'constraint' in str(row['col_name']).lower():
                if not constraints_found:
                    print(f"\n{table_name}:")
                    constraints_found = True
                print(f"  {row['col_name']}: {row['data_type']}")

        if not constraints_found:
            # Try to get constraint info using information_schema if available
            try:
                constraints_query = f"""
                    SELECT constraint_name, constraint_type
                    FROM system.information_schema.table_constraints
                    WHERE table_catalog = '{catalog_name}'
                      AND table_schema = '{silver_schema}'
                      AND table_name = '{table_name}'
                """
                constraints_df = spark.sql(constraints_query)
                if constraints_df.count() > 0:
                    if not constraints_found:
                        print(f"\n{table_name}:")
                    constraints_df.show(truncate=False)
            except:
                pass

    except Exception as e:
        pass

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Create ER Diagram Documentation Query

# COMMAND ----------

# Create a view that shows all table relationships
spark.sql(f"""
    CREATE OR REPLACE VIEW {catalog_name}.{meta_schema}.v_table_relationships AS
    SELECT
        'fact_manufacturing_process' as fact_table,
        'batch_key' as foreign_key_column,
        'dim_batch' as dimension_table,
        'batch_id' as primary_key_column,
        'Batch Details' as relationship_description

    UNION ALL SELECT 'fact_manufacturing_process', 'product_key', 'dim_product', 'product_id', 'Product Details'
    UNION ALL SELECT 'fact_manufacturing_process', 'equipment_key', 'dim_equipment', 'equipment_id', 'Equipment Details'
    UNION ALL SELECT 'fact_manufacturing_process', 'site_key', 'dim_site', 'site_id', 'Site Details'
    UNION ALL SELECT 'fact_manufacturing_process', 'date_key', 'dim_date', 'date_id', 'Date Dimension'

    UNION ALL SELECT 'fact_analytical_testing', 'batch_key', 'dim_batch', 'batch_id', 'Batch Tested'
    UNION ALL SELECT 'fact_analytical_testing', 'product_key', 'dim_product', 'product_id', 'Product Tested'
    UNION ALL SELECT 'fact_analytical_testing', 'test_method_key', 'dim_test_method', 'test_method_id', 'Test Method'
    UNION ALL SELECT 'fact_analytical_testing', 'site_key', 'dim_site', 'site_id', 'Testing Site'
    UNION ALL SELECT 'fact_analytical_testing', 'date_key', 'dim_date', 'date_id', 'Test Date'

    UNION ALL SELECT 'fact_batch_genealogy', 'child_batch_key', 'dim_batch', 'batch_id', 'Child Batch'
    UNION ALL SELECT 'fact_batch_genealogy', 'parent_batch_key', 'dim_batch', 'batch_id', 'Parent Batch'

    UNION ALL SELECT 'fact_clinical_observations', 'study_key', 'dim_study', 'study_id', 'Clinical Study'
    UNION ALL SELECT 'fact_clinical_observations', 'site_key', 'dim_site', 'site_id', 'Clinical Site'
    UNION ALL SELECT 'fact_clinical_observations', 'date_key', 'dim_date', 'date_id', 'Observation Date'

    UNION ALL SELECT 'bridge_batch_materials', 'batch_key', 'dim_batch', 'batch_id', 'Batch'
    UNION ALL SELECT 'bridge_batch_materials', 'material_key', 'dim_material', 'material_id', 'Material Used'
""")

print("✓ View v_table_relationships created for ER diagram documentation")

# Display the relationships
print("\nTable Relationships for ER Diagrams:")
spark.sql(f"SELECT * FROM {catalog_name}.{meta_schema}.v_table_relationships ORDER BY fact_table, foreign_key_column").show(100, truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Log Execution

# COMMAND ----------

spark.sql(f"""
    INSERT INTO {catalog_name}.{meta_schema}.pipeline_execution_log
    VALUES (
        '{execution_id}',
        '{pipeline_name}',
        'setup',
        'all_tables',
        'constraints_added',
        current_timestamp(),
        current_timestamp(),
        'SUCCESS',
        0,
        0,
        0,
        0,
        NULL,
        current_user(),
        '{dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get()}',
        map('execution_id', '{execution_id}', 'dimensions', '{len(dimensions_pk)}', 'facts', '{len(facts_pk)}', 'foreign_keys', '{len(foreign_keys)}'),
        current_timestamp()
    )
""")

print(f"\n{'='*80}")
print(f"Constraints Added Successfully")
print(f"{'='*80}")
print(f"Execution ID: {execution_id}")
print(f"Status: SUCCESS")
print(f"Summary:")
print(f"  - Dimension PRIMARY KEYs: {len(dimensions_pk)}")
print(f"  - Fact Table PRIMARY KEYs: {len(facts_pk)}")
print(f"  - FOREIGN KEY relationships: {len(foreign_keys)}")
print(f"  - Metadata table PRIMARY KEYs: {len(metadata_pk)}")
print(f"{'='*80}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC
# MAGIC ✅ **Primary and Foreign Key Constraints Added**
# MAGIC
# MAGIC **Benefits:**
# MAGIC 1. **Relationship Visualization** - ER diagrams can now be generated showing FK relationships
# MAGIC 2. **Data Catalog** - Unity Catalog displays relationship metadata
# MAGIC 3. **BI Tool Integration** - Power BI, Tableau can auto-detect relationships
# MAGIC 4. **Documentation** - Table relationships are explicitly documented
# MAGIC 5. **Query Optimization** - Query optimizer can use FK metadata for better plans
# MAGIC
# MAGIC **Note:** Constraints in Delta Lake are informational (NOT ENFORCED at write time).
# MAGIC They serve as metadata for documentation, visualization, and optimization.
# MAGIC
# MAGIC **To View Relationships:**
# MAGIC ```sql
# MAGIC -- View all table relationships
# MAGIC SELECT * FROM pharma_platform.metadata.v_table_relationships;
# MAGIC
# MAGIC -- Describe table constraints
# MAGIC DESCRIBE EXTENDED pharma_platform.silver_cdm.dim_batch;
# MAGIC ```
# MAGIC
# MAGIC **ER Diagram Tools:**
# MAGIC - Databricks Unity Catalog UI (Data Explorer)
# MAGIC - Power BI relationship view
# MAGIC - Tableau data source relationships
# MAGIC - Third-party ER diagram tools (DbSchema, DataGrip, etc.)
