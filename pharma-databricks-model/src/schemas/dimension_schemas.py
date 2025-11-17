"""
PySpark Schema Definitions for Dimension Tables
"""

from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType,
    LongType, DecimalType, DateType, TimestampType, BooleanType
)


def get_batch_schema():
    """Schema for Batch dimension - supports genealogy hierarchy"""
    return StructType([
        StructField("batch_ID", StringType(), False),
        StructField("batch_status", StringType(), True),
        StructField("parent_batch_ID", StringType(), True),
        StructField("genealogy_type", StringType(), True),
        StructField("lineage_path", StringType(), True),
        StructField("generation_level", IntegerType(), True),
        StructField("source_material_ID", StringType(), True),
        StructField("batch_size", DecimalType(18, 2), True),
        StructField("batch_size_uom", StringType(), True),
        StructField("mfg_start_date", DateType(), True),
        StructField("mfg_end_date", DateType(), True),
        StructField("production_order", StringType(), True),
    ])


def get_material_schema():
    """Schema for Material dimension - supports lineage hierarchy"""
    return StructType([
        StructField("material_ID", StringType(), False),
        StructField("material_type", StringType(), True),
        StructField("material_name", StringType(), True),
        StructField("protein_sequence", StringType(), True),
        StructField("target_antigen", StringType(), True),
        StructField("protein_subtype", StringType(), True),
        StructField("molecular_weight_kda", DecimalType(10, 2), True),
        StructField("vector_name", StringType(), True),
        StructField("vector_size_bp", IntegerType(), True),
        StructField("promoter", StringType(), True),
        StructField("species_of_origin", StringType(), True),
        StructField("passage_number", IntegerType(), True),
        StructField("parent_material_ID", StringType(), True),
        StructField("lineage_path", StringType(), True),
        StructField("hierarchy_level", IntegerType(), True),
    ])


def get_sample_schema():
    """Schema for Sample dimension"""
    return StructType([
        StructField("sample_ID", StringType(), False),
        StructField("vial_number", StringType(), True),
        StructField("sample_type", StringType(), True),
        StructField("collection_date", DateType(), True),
        StructField("storage_location", StringType(), True),
    ])


def get_manufacturer_schema():
    """Schema for Manufacturer dimension"""
    return StructType([
        StructField("manufacturer_ID", StringType(), False),
        StructField("manufacturer_name", StringType(), True),
        StructField("manufacturer_type", StringType(), True),
        StructField("facility_location", StringType(), True),
        StructField("country", StringType(), True),
        StructField("regulatory_status", StringType(), True),
    ])


def get_specification_schema():
    """Schema for Specification dimension"""
    return StructType([
        StructField("specification_ID", StringType(), False),
        StructField("specification_type", StringType(), True),
        StructField("parameter_name", StringType(), True),
        StructField("target_value", DecimalType(18, 4), True),
        StructField("lower_limit", DecimalType(18, 4), True),
        StructField("upper_limit", DecimalType(18, 4), True),
        StructField("uom", StringType(), True),
    ])


def get_notification_schema():
    """Schema for Notification dimension"""
    return StructType([
        StructField("notification_ID", StringType(), False),
        StructField("notification_type", StringType(), True),
        StructField("event_type", StringType(), True),
        StructField("severity_level", StringType(), True),
        StructField("notification_status", StringType(), True),
        StructField("notification_description", StringType(), True),
        StructField("notification_date", DateType(), True),
    ])


def get_document_schema():
    """Schema for Document dimension"""
    return StructType([
        StructField("document_ID", StringType(), False),
        StructField("document_type", StringType(), True),
        StructField("document_name", StringType(), True),
        StructField("document_title", StringType(), True),
        StructField("document_url", StringType(), True),
        StructField("gel_image", StringType(), True),
        StructField("upload_date", DateType(), True),
    ])


def get_source_system_schema():
    """Schema for Source System dimension"""
    return StructType([
        StructField("source_system_ID", StringType(), False),
        StructField("source_system_name", StringType(), True),
        StructField("system_type", StringType(), True),
        StructField("vendor", StringType(), True),
        StructField("version", StringType(), True),
        StructField("is_active", BooleanType(), True),
    ])


def get_local_process_hierarchy_schema():
    """Schema for Local Process Hierarchy dimension - supports self-join hierarchy"""
    return StructType([
        StructField("process_step_ID", StringType(), False),
        StructField("process_step_name", StringType(), True),
        StructField("process_phase", StringType(), True),
        StructField("equipment_ID", StringType(), True),
        StructField("location", StringType(), True),
        StructField("parent_step_ID", StringType(), True),
        StructField("hierarchy_level", IntegerType(), True),
        StructField("is_leaf_process", BooleanType(), True),
    ])


def get_common_process_hierarchy_schema():
    """Schema for Common Process Hierarchy dimension - supports self-join hierarchy"""
    return StructType([
        StructField("common_process_ID", StringType(), False),
        StructField("standard_process_name", StringType(), True),
        StructField("process_category", StringType(), True),
        StructField("process_subcategory", StringType(), True),
        StructField("parent_process_ID", StringType(), True),
        StructField("hierarchy_level", IntegerType(), True),
        StructField("regulatory_critical", BooleanType(), True),
    ])


def get_test_schema():
    """Schema for Test dimension"""
    return StructType([
        StructField("test_ID", StringType(), False),
        StructField("test_name", StringType(), True),
        StructField("test_category", StringType(), True),
        StructField("test_method_category", StringType(), True),
        StructField("test_component", StringType(), True),
    ])


def get_test_location_schema():
    """Schema for Test Location dimension"""
    return StructType([
        StructField("location_ID", StringType(), False),
        StructField("laboratory_name", StringType(), True),
        StructField("facility", StringType(), True),
        StructField("country", StringType(), True),
        StructField("clia_number", StringType(), True),
    ])


def get_analytical_method_schema():
    """Schema for Analytical Method dimension"""
    return StructType([
        StructField("method_ID", StringType(), False),
        StructField("method_name", StringType(), True),
        StructField("method_type", StringType(), True),
        StructField("technique", StringType(), True),
        StructField("instrument_type", StringType(), True),
        StructField("validation_date", DateType(), True),
    ])


def get_condition_schema():
    """Schema for Condition dimension"""
    return StructType([
        StructField("condition_ID", StringType(), False),
        StructField("storage_condition", StringType(), True),
        StructField("temperature_celsius", DecimalType(5, 2), True),
        StructField("relative_humidity", DecimalType(5, 2), True),
        StructField("light_exposure", StringType(), True),
    ])


def get_timepoint_schema():
    """Schema for Timepoint dimension"""
    return StructType([
        StructField("timepoint_ID", StringType(), False),
        StructField("timepoint_value", DecimalType(10, 2), True),
        StructField("timepoint_uom", StringType(), True),
        StructField("timepoint_label", StringType(), True),
    ])


def get_study_schema():
    """Schema for Study dimension"""
    return StructType([
        StructField("study_ID", StringType(), False),
        StructField("study_name", StringType(), True),
        StructField("study_type", StringType(), True),
        StructField("study_phase", StringType(), True),
        StructField("study_start_date", DateType(), True),
        StructField("study_end_date", DateType(), True),
    ])


def get_material_lot_schema():
    """Schema for Material Lot dimension"""
    return StructType([
        StructField("lot_number", StringType(), False),
        StructField("material_ID", StringType(), True),
        StructField("lot_status", StringType(), True),
        StructField("quantity", DecimalType(18, 2), True),
        StructField("quantity_uom", StringType(), True),
        StructField("manufacturing_date", DateType(), True),
        StructField("expiry_date", DateType(), True),
        StructField("supplier_lot", StringType(), True),
    ])


def get_transformation_schema():
    """Schema for Transformation dimension"""
    return StructType([
        StructField("transformation_ID", StringType(), False),
        StructField("transformation_type", StringType(), True),
        StructField("transformation_name", StringType(), True),
        StructField("equipment_ID", StringType(), True),
    ])


def get_production_order_schema():
    """Schema for Production Order dimension"""
    return StructType([
        StructField("production_order_ID", StringType(), False),
        StructField("order_type", StringType(), True),
        StructField("product_code", StringType(), True),
        StructField("planned_quantity", DecimalType(18, 2), True),
        StructField("planned_start", DateType(), True),
        StructField("planned_end", DateType(), True),
        StructField("order_status", StringType(), True),
    ])


def get_batch_genealogy_schema():
    """Schema for Batch Genealogy bridge table"""
    return StructType([
        StructField("child_batch_ID", StringType(), False),
        StructField("parent_batch_ID", StringType(), False),
        StructField("contribution_percent", DecimalType(5, 2), True),
        StructField("sequence_order", IntegerType(), True),
        StructField("relationship_type", StringType(), True),
    ])
