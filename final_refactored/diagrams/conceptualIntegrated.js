/**
 * Conceptual Integrated View
 * Auto-generated diagram module
 */

export const conceptualIntegrated = `graph TB
    %% Conceptual Integrated Architecture
    
    subgraph MATERIALS [Material Traceability]
        EV[Expression Vector<br/>🧬 Plasmid DNA]
        CL[Cell Lines<br/>🦠 Transfected Cells]
        MCB[Master Cell Bank<br/>🏦 Primary Stock]
        WCB[Working Cell Bank<br/>💼 Production Stock]
        RM[Raw Materials<br/>📦 Media, Buffers, Reagents]
    end
    
    subgraph PROCESS [Process Execution]
        PE[Manufacturing Steps<br/>⚙️ Execution Events]
        PP[Process Parameters<br/>📊 Critical Attributes]
        EQ[Equipment Usage<br/>🏭 Assets & Instruments]
    end
    
    subgraph GENEALOGY [Batch Genealogy]
        BG[Batch Tracking<br/>🏷️ Lot Numbers]
        SPLIT[Batch Splits<br/>📊 1 → Many]
        MERGE[Batch Pooling<br/>🔀 Many → 1]
        TRANS[Transformations<br/>⚗️ Process Changes]
        TRACE[Traceability Links<br/>🔗 Input/Output Lots]
    end
    
    subgraph QUALITY [Quality Testing]
        SAMP[Sample Collection<br/>🧪 Specimens]
        TESTS[Test Execution<br/>🔬 QC Testing]
        RESULTS[Test Results<br/>📈 Pass/Fail/OOS]
        INVEST[Investigations<br/>🔍 Root Cause]
    end
    
    subgraph GOVERNANCE [Governance & Compliance]
        SPECS[Specifications<br/>📋 Acceptance Criteria]
        DOCS[Documentation<br/>📄 Batch Records, COAs]
        EVENTS[Quality Events<br/>⚠️ Deviations, CAPA]
        SYS[Source Systems<br/>💾 LIMS, MES, ELN]
    end
    
    EV --> CL --> MCB --> WCB
    WCB --> PE
    RM --> PE
    
    PE --> BG
    BG --> SPLIT
    BG --> MERGE
    BG --> TRANS
    TRANS --> TRACE
    
    BG --> SAMP
    PE --> SAMP
    SAMP --> TESTS
    TESTS --> RESULTS
    RESULTS --> INVEST
    
    SPECS -.-> PE
    SPECS -.-> RESULTS
    
    PE --> DOCS
    RESULTS --> DOCS
    INVEST --> EVENTS
    
    PE -.-> SYS
    TESTS -.-> SYS
    DOCS -.-> SYS
    
    style MATERIALS fill:#e1f5ff
    style PROCESS fill:#fff3e0
    style GENEALOGY fill:#ffebee
    style QUALITY fill:#f3e5f5
    style GOVERNANCE fill:#f1f8e9`;

export const conceptualIntegrated_metadata = {
    title: "Conceptual Integrated View",
    id: "conceptualintegrated"
};
