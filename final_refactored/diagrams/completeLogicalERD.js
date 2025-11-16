/**
 * Complete Logical ERD
 * Auto-generated diagram module
 */

export const completeLogicalERD = `erDiagram
    %% COMPLETE INTEGRATED ERD - Process + Analytical + Genealogy
    
    %% === FACTS ===
    MANUFACTURING_PROCESS_RESULTS["Manufacturing Process Results"] {
        bigint process_result_identity PK
        bigint batch_identity FK
        bigint sample_identity FK
        bigint source_material_identity FK
        bigint manufacturer_identity FK
        bigint local_process_identity FK
        bigint common_process_identity FK
        bigint specification_identity FK
        bigint notification_identity FK
        bigint document_identity FK
        bigint source_system_identity FK
        decimal yield_value
        decimal temperature_celsius
        decimal pH_value
        decimal viability_percent
        timestamp process_timestamp
    }
    
    ANALYTICAL_RESULTS["Analytical Results"] {
        bigint test_result_identity PK
        bigint batch_identity FK
        bigint sample_identity FK
        bigint source_material_identity FK
        bigint manufacturer_identity FK
        bigint test_identity FK
        bigint test_location_identity FK
        bigint analytical_method_identity FK
        bigint condition_identity FK
        bigint timepoint_identity FK
        bigint specification_identity FK
        bigint study_identity FK
        bigint notification_identity FK
        bigint document_identity FK
        bigint source_system_identity FK
        decimal test_result
        varchar result_status
        boolean oos_flag
        timestamp test_timestamp
    }
    
    BATCH_MATERIAL_USAGE["Batch Material Usage"] {
        bigint usage_identity PK
        bigint batch_identity FK
        bigint material_lot_identity FK
        bigint transformation_identity FK
        varchar usage_type
        decimal quantity_used
        timestamp usage_timestamp
    }
    
    %% === CONFORMED DIMENSIONS ===
    BATCH["Batch"] {
        bigint batch_identity PK
        varchar batch_ID UK
        varchar batch_status
        bigint parent_batch_identity FK
        varchar genealogy_type
        varchar lineage_path
        int generation_level
        bigint source_material_identity FK
        decimal batch_size
        date mfg_start_date
        varchar production_order
        boolean current_flag
    }
    
    SAMPLE["Sample"] {
        bigint sample_identity PK
        varchar sample_ID UK
        varchar vial_number
        varchar sample_type
        date collection_date
        varchar storage_location
        boolean current_flag
    }
    
    MATERIAL["Material"] {
        bigint material_identity PK
        varchar material_ID UK
        varchar material_type
        varchar material_name
        text protein_sequence
        varchar target_antigen
        varchar protein_subtype
        bigint parent_material_identity FK
        varchar lineage_path
        int hierarchy_level
        boolean current_flag
    }
    
    MANUFACTURER["Manufacturer"] {
        bigint manufacturer_identity PK
        varchar manufacturer_ID UK
        varchar manufacturer_name
        varchar manufacturer_type
        varchar facility_location
        varchar country
        boolean current_flag
    }
    
    SPECIFICATION["Specification"] {
        bigint specification_identity PK
        varchar specification_ID UK
        varchar specification_type
        varchar parameter_name
        decimal target_value
        decimal lower_limit
        decimal upper_limit
        varchar uom
        boolean current_flag
    }
    
    NOTIFICATION["Notification"] {
        bigint notification_identity PK
        varchar notification_ID UK
        varchar notification_type
        varchar event_type
        varchar severity_level
        date notification_date
    }
    
    DOCUMENT["Document"] {
        bigint document_identity PK
        varchar document_ID UK
        varchar document_type
        varchar document_name
        varchar document_url
        date upload_date
    }
    
    SOURCE_SYSTEM["Source System"] {
        bigint source_system_identity PK
        varchar source_system_ID UK
        varchar source_system_name
        varchar system_type
        varchar vendor
        boolean is_active
    }
    
    %% === PROCESS-SPECIFIC DIMENSIONS ===
    LOCAL_PROCESS_HIERARCHY["Local Process Hierarchy"] {
        bigint local_process_identity PK
        varchar process_step_ID UK
        varchar process_step_name
        bigint parent_step_identity FK
        int hierarchy_level
        boolean current_flag
    }
    
    COMMON_PROCESS_HIERARCHY["Common Process Hierarchy"] {
        bigint common_process_identity PK
        varchar common_process_ID UK
        varchar standard_process_name
        bigint parent_process_identity FK
        int hierarchy_level
        boolean current_flag
    }
    
    %% === ANALYTICAL-SPECIFIC DIMENSIONS ===
    TEST["Test"] {
        bigint test_identity PK
        varchar test_ID UK
        varchar test_name
        varchar test_category
        boolean current_flag
    }
    
    TEST_LOCATION["Test Location"] {
        bigint test_location_identity PK
        varchar location_ID UK
        varchar laboratory_name
        boolean current_flag
    }
    
    ANALYTICAL_METHOD["Analytical Method"] {
        bigint analytical_method_identity PK
        varchar method_ID UK
        varchar method_name
        varchar technique
        boolean current_flag
    }
    
    CONDITION["Condition"] {
        bigint condition_identity PK
        varchar condition_ID UK
        varchar storage_condition
        decimal temperature_celsius
        boolean current_flag
    }
    
    TIMEPOINT["Timepoint"] {
        bigint timepoint_identity PK
        varchar timepoint_ID UK
        decimal timepoint_value
        varchar timepoint_label
        boolean current_flag
    }
    
    STUDY["Study"] {
        bigint study_identity PK
        varchar study_ID UK
        varchar study_name
        varchar study_type
        boolean current_flag
    }
    
    %% === GENEALOGY DIMENSIONS ===
    MATERIAL_LOT["Material Lot"] {
        bigint material_lot_identity PK
        varchar lot_number UK
        bigint material_identity FK
        varchar lot_status
        decimal quantity
        date expiry_date
        boolean current_flag
    }
    
    TRANSFORMATION["Transformation"] {
        bigint transformation_identity PK
        varchar transformation_ID UK
        varchar transformation_type
        varchar transformation_name
        boolean current_flag
    }
    
    PRODUCTION_ORDER["Production Order"] {
        bigint production_order_identity PK
        varchar production_order_ID UK
        varchar order_type
        varchar order_status
        boolean current_flag
    }
    
    %% === BRIDGE TABLES ===
    BATCH_GENEALOGY["Batch Genealogy"] {
        bigint bridge_identity PK
        bigint child_batch_identity FK
        bigint parent_batch_identity FK
        decimal contribution_percent
        int sequence_order
    }
    
    %% === SELF-JOIN HIERARCHIES ===
    BATCH ||--o| BATCH : "sourced from"
    MATERIAL ||--o| MATERIAL : "parent_material"
    LOCAL_PROCESS_HIERARCHY ||--o| LOCAL_PROCESS_HIERARCHY : "parent_step"
    COMMON_PROCESS_HIERARCHY ||--o| COMMON_PROCESS_HIERARCHY : "parent_process"
    
    %% === BRIDGE RELATIONSHIPS ===
    BATCH ||--o{ BATCH_GENEALOGY : "produces"
    BATCH_GENEALOGY }o--|| BATCH : "sourced from"
    
    %% === SUPPORTING RELATIONSHIPS ===
    MATERIAL ||--o{ BATCH : "source_material"
    MATERIAL ||--o{ MATERIAL_LOT : "material"
    PRODUCTION_ORDER ||--o{ BATCH : "production_order"
    
    %% === PROCESS FACT RELATIONSHIPS ===
    LOCAL_PROCESS_HIERARCHY ||--o{ MANUFACTURING_PROCESS_RESULTS : "local_process"
    COMMON_PROCESS_HIERARCHY ||--o{ MANUFACTURING_PROCESS_RESULTS : "common_process"
    
    MANUFACTURING_PROCESS_RESULTS }o--|| BATCH : "batch"
    MANUFACTURING_PROCESS_RESULTS }o--|| SAMPLE : "sample"
    MANUFACTURING_PROCESS_RESULTS }o--|| MATERIAL : "source_material"
    MANUFACTURING_PROCESS_RESULTS }o--|| MANUFACTURER : "manufacturer"
    MANUFACTURING_PROCESS_RESULTS }o--|| SPECIFICATION : "specification"
    MANUFACTURING_PROCESS_RESULTS }o--|| NOTIFICATION : "notification"
    MANUFACTURING_PROCESS_RESULTS }o--|| DOCUMENT : "document"
    MANUFACTURING_PROCESS_RESULTS }o--|| SOURCE_SYSTEM : "source_system"
    
    %% === ANALYTICAL FACT RELATIONSHIPS ===
    BATCH ||--o{ ANALYTICAL_RESULTS : "batch"
    SAMPLE ||--o{ ANALYTICAL_RESULTS : "sample"
    MATERIAL ||--o{ ANALYTICAL_RESULTS : "source_material"
    MANUFACTURER ||--o{ ANALYTICAL_RESULTS : "manufacturer"
    SPECIFICATION ||--o{ ANALYTICAL_RESULTS : "specification"
    NOTIFICATION ||--o{ ANALYTICAL_RESULTS : "notification"
    DOCUMENT ||--o{ ANALYTICAL_RESULTS : "document"
    SOURCE_SYSTEM ||--o{ ANALYTICAL_RESULTS : "source_system"
    
    ANALYTICAL_RESULTS }o--|| TEST : "test"
    ANALYTICAL_RESULTS }o--|| TEST_LOCATION : "test_location"
    ANALYTICAL_RESULTS }o--|| ANALYTICAL_METHOD : "analytical_method"
    ANALYTICAL_RESULTS }o--|| CONDITION : "condition"
    ANALYTICAL_RESULTS }o--|| TIMEPOINT : "timepoint"
    ANALYTICAL_RESULTS }o--|| STUDY : "study"
    
    %% === GENEALOGY FACT RELATIONSHIPS ===
    BATCH ||--o{ BATCH_MATERIAL_USAGE : "batch"
    MATERIAL_LOT ||--o{ BATCH_MATERIAL_USAGE : "material_lot"
    TRANSFORMATION ||--o{ BATCH_MATERIAL_USAGE : "transformation"`;

export const completeLogicalERD_metadata = {
    title: "Complete Logical ERD",
    id: "completelogicalerd"
};
