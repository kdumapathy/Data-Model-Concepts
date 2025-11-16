/**
 * SAP GBT Batch Genealogy
 * Auto-generated diagram module
 */

export const batchGenealogy = `erDiagram
    %% SAP GBT Genealogy Model with Tooltips
    
    BATCH["Batch"] {
        bigint batch_identity PK "Surrogate key"
        varchar batch_ID UK "Business batch number"
        varchar batch_status "Released, Quarantine, Rejected"
        bigint parent_batch_identity FK "Self-join for genealogy"
        varchar genealogy_type "Split, Merge, Rework, Original"
        varchar lineage_path "Materialized path for queries"
        int generation_level "0=original, 1=child, 2=grandchild"
        bigint source_material_identity FK "Material used (WCB, MCB)"
        decimal batch_size "Quantity produced"
        varchar batch_size_uom "L, kg, vials"
        date mfg_start_date "Manufacturing start"
        date mfg_end_date "Manufacturing completion"
        varchar production_order "SAP order number"
        boolean current_flag "SCD Type 2"
    }
    
    BATCH_GENEALOGY["Batch Genealogy"] {
        bigint bridge_identity PK "Surrogate key"
        bigint child_batch_identity FK "Resulting batch"
        bigint parent_batch_identity FK "Source batch"
        decimal contribution_percent "% from parent"
        int sequence_order "Order of pooling"
        varchar relationship_type "Input, Output, Rework"
        timestamp created_ts "Audit timestamp"
    }
    
    MATERIAL_LOT["Material Lot"] {
        bigint material_lot_identity PK "Surrogate key"
        varchar lot_number UK "Material lot ID"
        bigint material_identity FK "Material master"
        varchar lot_status "Available, Consumed, Quarantine"
        decimal quantity "Amount available"
        varchar quantity_uom "Unit of measure"
        date manufacturing_date "Lot production date"
        date expiry_date "Expiration date"
        varchar supplier_lot "Vendor lot number"
        boolean current_flag "SCD Type 2"
    }
    
    BATCH_MATERIAL_USAGE["Batch Material Usage"] {
        bigint usage_identity PK "Surrogate key"
        bigint batch_identity FK "Consuming batch"
        bigint material_lot_identity FK "Material lot used"
        bigint transformation_identity FK "Process step"
        varchar usage_type "Input, Output, Yield_Loss"
        decimal quantity_used "Amount consumed/produced"
        varchar quantity_uom "Unit of measure"
        timestamp usage_timestamp "When used"
        varchar bom_item_number "Bill of material line"
    }
    
    TRANSFORMATION["Transformation"] {
        bigint transformation_identity PK "Surrogate key"
        varchar transformation_ID UK "Process step ID"
        varchar transformation_type "Culture, Harvest, Purify, Fill"
        varchar transformation_name "Business process name"
        varchar equipment_ID "Equipment used"
        boolean current_flag "SCD Type 2"
    }
    
    PRODUCTION_ORDER["Production Order"] {
        bigint production_order_identity PK "Surrogate key"
        varchar production_order_ID UK "SAP order number"
        varchar order_type "Production, Rework, Validation"
        varchar product_code "SKU or product ID"
        decimal planned_quantity "Target amount"
        date planned_start "Scheduled start"
        date planned_end "Scheduled completion"
        varchar order_status "Released, Complete, Cancelled"
        boolean current_flag "SCD Type 2"
    }
    
    %% Relationships
    BATCH ||--o| BATCH : "derived from"
    BATCH ||--o{ BATCH_GENEALOGY : "produces"
    BATCH_GENEALOGY }o--|| BATCH : "sourced from"
    
    BATCH ||--o{ BATCH_MATERIAL_USAGE : "performed on"
    MATERIAL_LOT ||--o{ BATCH_MATERIAL_USAGE : "consumes"
    TRANSFORMATION ||--o{ BATCH_MATERIAL_USAGE : "transformed by"
    
    PRODUCTION_ORDER ||--o{ BATCH : "ordered via"`;

export const batchGenealogy_metadata = {
    title: "SAP GBT Batch Genealogy",
    id: "batchgenealogy"
};
