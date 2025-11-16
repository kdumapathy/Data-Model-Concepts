/**
 * Conceptual Model
 * Auto-generated diagram module
 */

export const conceptualModel = `graph TB
    %% Core Manufacturing Entities
    subgraph Manufacturing["🏭 Manufacturing Process Domain"]
        ProdOrder[Production Order<br/>📋 Manufacturing Execution]
        Batch[Batch<br/>🏷️ Production Lots]
        Material[Material<br/>📦 Raw Materials & Products]
        Equipment[Equipment<br/>🏭 Bioreactors & Assets]
        ProcessOp[Process Operation<br/>⚙️ Manufacturing Steps]
        ProcessParams[Process Parameters<br/>📊 Temp, pH, Pressure]
    end
    
    %% Core Analytical Entities
    subgraph Analytical["🔬 Quality & Testing Domain"]
        Sample[Sample<br/>🧪 Test Specimens]
        Test[Test<br/>🔍 Quality Tests]
        TestResult[Test Result<br/>📈 Measurements]
        Specification[Specification<br/>📏 Quality Standards]
        Method[Test Method<br/>🔬 Analytical Procedures]
    end
    
    %% Batch Genealogy
    subgraph Genealogy["🧬 Batch Genealogy & Traceability"]
        BatchGenealogy[Batch Genealogy<br/>🔄 Parent-Child Tracking]
        MaterialLot[Material Lot<br/>📦 Supplier Lots]
        Transformation[Material Transformation<br/>🔄 Vector→Cell Line→MCB→WCB]
        BatchMaterial[Batch Material Usage<br/>📝 Bill of Materials]
    end
    
    %% Shared/Conformed Entities
    subgraph Conformed["🌐 Shared Reference Data"]
        Mfg[Manufacturer<br/>🏢 Suppliers & Partners]
        Document[Document<br/>📄 SOPs, Protocols, Reports]
        Notification[Notification<br/>🚨 Deviations & Events]
        Source[Source System<br/>💾 ERP, LIMS, MES]
    end
    
    %% Time Dimension
    Time[Time<br/>📅 Date Hierarchy]
    
    %% Relationships - Manufacturing
    ProdOrder --> Batch
    ProdOrder --> ProcessOp
    Batch --> Material
    Batch --> Equipment
    ProcessOp --> Equipment
    ProcessOp --> ProcessParams
    Batch --> Time
    
    %% Relationships - Analytical
    Sample --> Batch
    Sample --> Material
    Test --> Sample
    Test --> Method
    TestResult --> Test
    TestResult --> Specification
    TestResult --> Time
    
    %% Relationships - Genealogy
    Batch --> BatchGenealogy
    BatchGenealogy --> Batch
    Material --> MaterialLot
    Material --> Transformation
    Transformation --> Material
    Batch --> BatchMaterial
    BatchMaterial --> Material
    BatchMaterial --> MaterialLot
    
    %% Relationships - Conformed
    Material --> Mfg
    Batch --> Mfg
    Sample --> Mfg
    ProdOrder --> Document
    Test --> Document
    Batch --> Notification
    TestResult --> Notification
    ProdOrder --> Source
    Test --> Source
    
    %% Styling
    classDef processClass fill:#c8e6c9,stroke:#388e3c,stroke-width:3px
    classDef analyticalClass fill:#e1bee7,stroke:#7b1fa2,stroke-width:3px
    classDef genealogyClass fill:#ffcdd2,stroke:#c62828,stroke-width:3px
    classDef conformedClass fill:#fff9c4,stroke:#f57f17,stroke-width:3px
    classDef timeClass fill:#b3e5fc,stroke:#0277bd,stroke-width:3px
    
    class ProdOrder,Batch,Material,Equipment,ProcessOp,ProcessParams processClass
    class Sample,Test,TestResult,Specification,Method analyticalClass
    class BatchGenealogy,MaterialLot,Transformation,BatchMaterial genealogyClass
    class Mfg,Document,Notification,Source conformedClass
    class Time timeClass`;

export const conceptualModel_metadata = {
    title: "Conceptual Model",
    id: "conceptualmodel"
};
