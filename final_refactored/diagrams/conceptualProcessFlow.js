/**
 * Conceptual Process Flow
 * Auto-generated diagram module
 */

export const conceptualProcessFlow = `graph LR
    %% Conceptual Business Process Flow
    
    CB[Cell Banking<br/>💉 Vector → Cell Line → MCB → WCB]
    CC[Cell Culture<br/>🧫 Seed Train & Production]
    HARV[Harvest<br/>⚗️ Cell Separation]
    PURIF[Purification<br/>🔬 Chromatography & Filtration]
    FORM[Formulation<br/>💊 Final Drug Product]
    
    MAT[Materials<br/>📦 Raw Materials, Reagents, Buffers]
    EQUIP[Equipment<br/>🏭 Bioreactors, Columns, Filters]
    BATCH[Batch<br/>🏷️ Production Lots & Genealogy]
    PROC_PARAMS[Process Parameters<br/>📊 Temp, pH, Flow Rate]
    
    CB --> CC
    CC --> HARV
    HARV --> PURIF
    PURIF --> FORM
    
    MAT -.-> CB
    MAT -.-> CC
    MAT -.-> PURIF
    MAT -.-> FORM
    
    EQUIP -.-> CC
    EQUIP -.-> HARV
    EQUIP -.-> PURIF
    
    BATCH -.-> CB
    BATCH -.-> CC
    BATCH -.-> HARV
    BATCH -.-> PURIF
    BATCH -.-> FORM
    
    PROC_PARAMS -.-> CC
    PROC_PARAMS -.-> PURIF
    
    style CB fill:#e1f5ff
    style CC fill:#fff3e0
    style HARV fill:#e8f5e9
    style PURIF fill:#f3e5f5
    style FORM fill:#fce4ec
    style BATCH fill:#ffebee
    style MAT fill:#f1f8e9
    style EQUIP fill:#e0f2f1
    style PROC_PARAMS fill:#fff9c4`;

export const conceptualProcessFlow_metadata = {
    title: "Conceptual Process Flow",
    id: "conceptualprocessflow"
};
