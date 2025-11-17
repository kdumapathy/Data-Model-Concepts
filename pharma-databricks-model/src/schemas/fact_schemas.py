"""
PySpark Schema Definitions for Fact Tables
"""

from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType,
    LongType, DecimalType, DateType, TimestampType, BooleanType
)


def get_manufacturing_process_results_schema():
    """Schema for Manufacturing Process Results fact table"""
    return StructType([
        # Foreign Key References (Business Keys)
        StructField("batch_ID", StringType(), False),
        StructField("sample_ID", StringType(), True),
        StructField("source_material_ID", StringType(), False),
        StructField("manufacturer_ID", StringType(), False),
        StructField("local_process_step_ID", StringType(), False),
        StructField("common_process_ID", StringType(), False),
        StructField("specification_ID", StringType(), True),
        StructField("notification_ID", StringType(), True),
        StructField("document_ID", StringType(), True),
        StructField("source_system_ID", StringType(), False),

        # Measures
        StructField("cell_passage", IntegerType(), True),
        StructField("yield_value", DecimalType(18, 4), True),
        StructField("yield_uom", StringType(), True),
        StructField("temperature_celsius", DecimalType(5, 2), True),
        StructField("pH_value", DecimalType(4, 2), True),
        StructField("viability_percent", DecimalType(5, 2), True),
        StructField("density_cells_ml", DecimalType(18, 2), True),
        StructField("process_timestamp", TimestampType(), False),
    ])


def get_analytical_results_schema():
    """Schema for Analytical Results fact table"""
    return StructType([
        # Foreign Key References (Business Keys)
        StructField("batch_ID", StringType(), False),
        StructField("sample_ID", StringType(), True),
        StructField("source_material_ID", StringType(), False),
        StructField("manufacturer_ID", StringType(), False),
        StructField("test_ID", StringType(), False),
        StructField("test_location_ID", StringType(), False),
        StructField("analytical_method_ID", StringType(), False),
        StructField("condition_ID", StringType(), True),
        StructField("timepoint_ID", StringType(), True),
        StructField("specification_ID", StringType(), True),
        StructField("study_ID", StringType(), True),
        StructField("notification_ID", StringType(), True),
        StructField("document_ID", StringType(), True),
        StructField("source_system_ID", StringType(), False),

        # Measures
        StructField("test_result", DecimalType(18, 4), True),
        StructField("test_uom", StringType(), True),
        StructField("cell_passage", IntegerType(), True),
        StructField("test_timestamp", TimestampType(), False),
        StructField("result_status", StringType(), True),
        StructField("oos_flag", BooleanType(), True),
        StructField("percent_difference", DecimalType(10, 4), True),
    ])


def get_batch_material_usage_schema():
    """Schema for Batch Material Usage fact table"""
    return StructType([
        # Foreign Key References (Business Keys)
        StructField("batch_ID", StringType(), False),
        StructField("material_lot_number", StringType(), False),
        StructField("transformation_ID", StringType(), False),
        StructField("production_order_ID", StringType(), True),

        # Measures
        StructField("usage_type", StringType(), True),
        StructField("quantity_used", DecimalType(18, 4), True),
        StructField("quantity_uom", StringType(), True),
        StructField("usage_timestamp", TimestampType(), False),
        StructField("bom_item_number", StringType(), True),
    ])
