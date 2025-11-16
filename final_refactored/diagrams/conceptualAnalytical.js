/**
 * Conceptual Analytical
 * Auto-generated diagram module
 */

export const conceptualAnalytical = `graph TB
    %% Conceptual Analytical Data Model
    
    SAMPLE[Samples<br/>🧪 Test Specimens]
    TEST_CAT[Test Categories<br/>📋 Identity, Purity, Potency, Safety]
    MEAS[Measurements<br/>📊 Test Results & Values]
    METHODS[Analytical Methods<br/>🔬 HPLC, ELISA, PCR, Western Blot]
    
    SPECS[Quality Specifications<br/>✅ Acceptance Criteria & Limits]
    LABS[Testing Laboratories<br/>🏥 Internal & Contract Labs]
    STUDIES[Studies<br/>📚 Stability, Release, Characterization]
    
    CONDITIONS[Storage Conditions<br/>🌡️ Temperature, Humidity, Light]
    TIMEPOINTS[Study Timepoints<br/>⏱️ T0, 3mo, 6mo, 12mo, 24mo]
    
    EVENTS[Quality Events<br/>⚠️ Deviations, OOS, Investigations]
    DOCS[Documentation<br/>📄 COAs, Reports, Protocols]
    
    SAMPLE --> MEAS
    TEST_CAT --> MEAS
    METHODS --> MEAS
    
    SPECS -.-> MEAS
    LABS -.-> MEAS
    STUDIES -.-> MEAS
    
    CONDITIONS -.-> STUDIES
    TIMEPOINTS -.-> STUDIES
    
    MEAS -.-> EVENTS
    MEAS -.-> DOCS
    
    style SAMPLE fill:#e3f2fd
    style MEAS fill:#fff3e0
    style TEST_CAT fill:#f3e5f5
    style METHODS fill:#e8f5e9
    style SPECS fill:#fce4ec
    style LABS fill:#f1f8e9
    style STUDIES fill:#e0f2f1
    style CONDITIONS fill:#fff9c4
    style TIMEPOINTS fill:#ffebee
    style EVENTS fill:#ffccbc
    style DOCS fill:#f0f4c3`;

export const conceptualAnalytical_metadata = {
    title: "Conceptual Analytical",
    id: "conceptualanalytical"
};
