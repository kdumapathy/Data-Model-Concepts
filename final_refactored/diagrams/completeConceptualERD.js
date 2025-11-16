/**
 * Complete Conceptual ERD
 * Auto-generated diagram module
 */

export const completeConceptualERD = `erDiagram
    %% ENTERPRISE DATA MODEL - Process + Analytical + Genealogy
    
    %% === FACTS ===
    FACT_MANUFACTURING_PROCESS_RESULT["Manufacturing Process Result"]
    FACT_ANALYTICAL["Analytical Result"]
    FACT_BATCH_MATERIAL_USAGE["Batch Material Usage"]
    
    %% === CONFORMED DIMENSIONS ===
    BATCH["Batch"]
    SAMPLE["Sample"]
    MATERIAL["Material"]
    MANUFACTURER["Manufacturer"]
    SPECIFICATION["Specification"]
    NOTIFICATION["Notification"]
    DOCUMENT["Document"]
    SOURCE_SYSTEM["Source System"]
    
    %% === PROCESS-SPECIFIC DIMENSIONS ===
    LOCAL_PROCESS_HIERARCHY["Local Process Hierarchy"]
    COMMON_PROCESS_HIERARCHY["Common Process Hierarchy"]
    
    %% === ANALYTICAL-SPECIFIC DIMENSIONS ===
    TEST["Test"]
    TEST_LOCATION["Test Location"]
    ANALYTICAL_METHOD["Analytical Method"]
    CONDITION["Condition"]
    TIME_POINT["Time Point"]
    STUDY["Study"]
    
    %% === GENEALOGY DIMENSIONS ===
    MATERIAL_LOT["Material Lot"]
    TRANSFORMATION["Transformation"]
    PRODUCTION_ORDER["Production Order"]
    
    %% === BRIDGE TABLES ===
    BRIDGE_BATCH_GENEALOGY["Bridge Batch Genealogy"]
    
    %% === SELF-JOIN HIERARCHIES ===
    BATCH ||--o| BATCH : "parent of"
    MATERIAL ||--o| MATERIAL : "component of"
    LOCAL_PROCESS_HIERARCHY ||--o| LOCAL_PROCESS_HIERARCHY : "parent step of"
    COMMON_PROCESS_HIERARCHY ||--o| COMMON_PROCESS_HIERARCHY : "parent process of"
    
    %% === BRIDGE RELATIONSHIPS ===
    BATCH ||--o{ BRIDGE_BATCH_GENEALOGY : "is child in"
    BRIDGE_BATCH_GENEALOGY }o--|| BATCH : "has parent"
    
    %% === SUPPORTING RELATIONSHIPS ===
    MATERIAL ||--o{ BATCH : "used to produce"
    MATERIAL ||--o{ MATERIAL_LOT : "tracked as"
    PRODUCTION_ORDER ||--o{ BATCH : "produces"
    
    %% === PROCESS FACT RELATIONSHIPS ===
    LOCAL_PROCESS_HIERARCHY ||--o{ FACT_MANUFACTURING_PROCESS_RESULT : "defines local step for"
    COMMON_PROCESS_HIERARCHY ||--o{ FACT_MANUFACTURING_PROCESS_RESULT : "defines process for"
    
    FACT_MANUFACTURING_PROCESS_RESULT }o--|| BATCH : "performed on"
    FACT_MANUFACTURING_PROCESS_RESULT }o--|| SAMPLE : "measured from"
    FACT_MANUFACTURING_PROCESS_RESULT }o--|| MATERIAL : "consumed"
    FACT_MANUFACTURING_PROCESS_RESULT }o--|| MANUFACTURER : "manufactured by"
    FACT_MANUFACTURING_PROCESS_RESULT }o--|| SPECIFICATION : "meets specification"
    FACT_MANUFACTURING_PROCESS_RESULT }o--|| NOTIFICATION : "triggers"
    FACT_MANUFACTURING_PROCESS_RESULT }o--|| DOCUMENT : "documented in"
    FACT_MANUFACTURING_PROCESS_RESULT }o--|| SOURCE_SYSTEM : "sourced from"
    
    %% === ANALYTICAL FACT RELATIONSHIPS ===
    BATCH ||--o{ FACT_ANALYTICAL : "tested via"
    SAMPLE ||--o{ FACT_ANALYTICAL : "analyzed as"
    MATERIAL ||--o{ FACT_ANALYTICAL : "tested for"
    MANUFACTURER ||--o{ FACT_ANALYTICAL : "produced by"
    SPECIFICATION ||--o{ FACT_ANALYTICAL : "evaluated against"
    NOTIFICATION ||--o{ FACT_ANALYTICAL : "notified via"
    DOCUMENT ||--o{ FACT_ANALYTICAL : "recorded in"
    SOURCE_SYSTEM ||--o{ FACT_ANALYTICAL : "originated in"
    
    FACT_ANALYTICAL }o--|| ANALYTICAL_METHOD : "using method"
    FACT_ANALYTICAL }o--|| TEST : "performs test"
    FACT_ANALYTICAL }o--|| TEST_LOCATION : "conducted at"
    FACT_ANALYTICAL }o--|| CONDITION : "under condition"
    FACT_ANALYTICAL }o--|| TIME_POINT : "measured at"
    FACT_ANALYTICAL }o--|| STUDY : "part of study"
    
    %% === GENEALOGY FACT RELATIONSHIPS ===
    BATCH ||--o{ FACT_BATCH_MATERIAL_USAGE : "consumed in"
    MATERIAL_LOT ||--o{ FACT_BATCH_MATERIAL_USAGE : "used as"
    TRANSFORMATION ||--o{ FACT_BATCH_MATERIAL_USAGE : "transformed via"`;

export const completeConceptualERD_metadata = {
    title: "Complete Conceptual ERD",
    id: "completeconceptualerd"
};
