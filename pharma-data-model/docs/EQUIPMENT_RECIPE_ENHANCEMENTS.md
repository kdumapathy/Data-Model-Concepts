# Equipment Master Data & Recipe Management Enhancements

## Overview

**Version:** 1.1 Enhancement
**Release Date:** November 16, 2025
**Enhancement Type:** Equipment and Recipe Management Integration

This document describes the major enhancements to the pharmaceutical data model, adding comprehensive **Equipment Master Data** and **Process Recipe/Control Recipe** management based on **ISA-88** and **ISA-95** standards.

---

## What Was Added

### 🏭 Equipment Master Data (ISA-88 Physical Model)

#### New Diagram: `Equipment_Master_Data_ISA88.html`

**Complete ISA-88 Physical Model Hierarchy:**
```
Enterprise
└── Site (Manufacturing location)
    └── Area (Process area: Upstream, Downstream, Fill/Finish)
        └── Process Cell (Equipment grouping: Bioreactor Farm, Chromatography Skid)
            └── Unit (Individual equipment: Bioreactor, Column, Filling Machine)
                └── Equipment Module (Subsystems: Agitation, Temperature Control, pH Control)
                    └── Control Module (Sensors/Actuators: pH Sensor, DO Probe, Pumps)
```

**New Data Entities:**

1. **EQUIPMENT_MASTER**
   - Equipment ID, name, type, class (Unit, EM, CM)
   - Self-join hierarchy (parent_equipment_identity)
   - Manufacturer, model, serial number
   - Installation date, status (Active, Maintenance, Retired)
   - Location (site, area, process cell)
   - GMP critical flag
   - Qualification status (IQ, OQ, PQ, Qualified)
   - Calibration status and schedules

2. **EQUIPMENT_CAPABILITY**
   - Equipment capabilities (volume, pressure, temperature range)
   - Min/max/nominal values
   - Unit of measure
   - Capability status (Available, Limited, Unavailable)

3. **EQUIPMENT_QUALIFICATION**
   - Qualification type (IQ, OQ, PQ)
   - Execution date, performer, status
   - Qualification documentation
   - Requalification schedule

4. **EQUIPMENT_CALIBRATION**
   - Calibration date, performer
   - Calibration standard reference
   - Accuracy measurements
   - Calibration certificate
   - Next calibration due date

5. **EQUIPMENT_MAINTENANCE**
   - Maintenance type (Preventive, Corrective, Breakdown)
   - Work order ID (CMMS integration)
   - Scheduled vs. actual dates
   - Downtime tracking
   - Maintenance documentation

6. **EQUIPMENT_USAGE**
   - Equipment used in which batch
   - Runtime tracking (start, end, duration)
   - Utilization percentage
   - Usage status (Running, Idle, Cleaning)

7. **SITE, AREA, PROCESS_CELL**
   - Hierarchical location entities
   - Site certification (GMP certified)
   - Area cleanroom classification (ISO 5, 7, 8)

**Key Features:**
- ✅ Complete ISA-88 7-level physical hierarchy
- ✅ Equipment lifecycle management (installation → retirement)
- ✅ Self-join hierarchy for equipment composition
- ✅ Qualification and calibration tracking
- ✅ CMMS integration for preventive maintenance
- ✅ Equipment utilization for OEE calculation
- ✅ GMP critical equipment flagging

---

### 📋 Process Recipe & Control Recipe (ISA-88 Procedural Model)

#### New Diagram: `Process_Recipe_Control_Recipe_ISA88.html`

**Complete ISA-88 Procedural Model Hierarchy:**
```
Procedure (Complete manufacturing process)
└── Unit Procedure (Equipment-specific process: Cell Culture, Harvest, Chromatography)
    └── Operation (Specific operation: Seed Train, Production Culture, Column Loading)
        └── Phase (Smallest procedural unit: Inoculation, Fed-Batch, Equilibration)
```

**New Data Entities:**

1. **MASTER_RECIPE**
   - Recipe ID, name, version
   - Recipe type (Procedure, Unit Procedure, Operation, Phase)
   - Product family (mAb, Vaccine, Gene Therapy)
   - Recipe status (Draft, Approved, Active, Retired)
   - Approval date and approver
   - Self-join hierarchy (parent_recipe_identity)
   - ISA-88 level designation
   - Expected duration and yield
   - GMP critical flag
   - Master batch record document

2. **RECIPE_PARAMETER**
   - Parameter name (Temperature, pH, Agitation, DO)
   - Parameter type (Process, Quality, Safety)
   - Parameter category (CPP, Non-CPP, CQA)
   - Target value (set point)
   - Min/max specification limits
   - Unit of measure
   - Control strategy (Feedback, Cascade, Manual)
   - Alarming configuration (low/high alarm thresholds)
   - Criticality level (Critical, Major, Minor)

3. **RECIPE_PHASE**
   - Phase ID and name
   - Phase sequence (execution order)
   - Phase type (Transfer, Heat, Cool, Mix, React)
   - Phase duration
   - Transition logic (Time, Parameter, Manual)
   - Transition criteria (e.g., "pH < 7.0", "Temp = 37°C")

4. **RECIPE_MATERIAL**
   - Materials required for recipe
   - Material type (Raw Material, Buffer, Media)
   - Quantity required with UOM
   - Addition type (Charge, Feed, Continuous)
   - Addition sequence
   - Material specification reference
   - Critical material flag

5. **RECIPE_EQUIPMENT**
   - Equipment class required (not specific equipment)
   - Equipment role (Primary, Secondary, Support)
   - Quantity required
   - Capability requirements (e.g., "Volume > 10000L")

6. **CONTROL_RECIPE**
   - Executable recipe instance
   - Based on master recipe
   - Assigned to specific batch
   - Assigned to specific product
   - Assigned to specific equipment (actual equipment, not class)
   - Recipe status (Scheduled, Running, Complete, Aborted)
   - Scheduled vs. actual start/end times
   - Operator assignment

7. **CONTROL_RECIPE_PARAMETER**
   - Set points for specific control recipe
   - Based on master recipe parameters
   - Actual set point, lower limit, upper limit
   - UOM

8. **RECIPE_EXECUTION**
   - Execution of specific recipe phase
   - Control recipe executed
   - Batch manufactured
   - Recipe phase executed
   - Phase start/end timestamps
   - Actual phase duration
   - Execution status (Running, Complete, Aborted, Failed)
   - Operator on duty
   - Deviation tracking

9. **EXECUTION_PARAMETER_VALUE**
   - Actual measured parameter values
   - Timestamp of measurement
   - Actual value vs. set point
   - Value status (In-Spec, Out-of-Spec, Alarm)
   - UOM

10. **PRODUCT**
    - Product master data
    - Product ID, name, type

11. **EQUIPMENT_CLASS**
    - Equipment classes (Bioreactor, Column, Filter)
    - Equipment type (Unit, Equipment Module)

**Key Features:**
- ✅ Complete ISA-88 4-level procedural hierarchy
- ✅ Master recipe (product-independent template)
- ✅ Control recipe (product-specific executable)
- ✅ Recipe versioning with SCD Type 2
- ✅ Critical Process Parameters (CPP) flagging
- ✅ Equipment class → actual equipment assignment
- ✅ Recipe execution tracking (actual vs. target)
- ✅ Electronic batch record generation
- ✅ Material bill of materials
- ✅ Phase sequencing with transition logic

**Recipe Lifecycle:**
```
Draft → Review → Approve → Schedule → Create Control Recipe → Release → Execute → Complete → Review
```

---

### 🔗 Integrated Equipment-Recipe-Batch Execution

#### New Diagram: `Integrated_Equipment_Recipe_Execution.html`

**Complete Integration Model:**

This diagram integrates ALL the concepts together:
- Equipment Master Data
- Master Recipe
- Control Recipe
- Recipe Execution
- Batch Manufacturing
- Material Usage
- Parameter Tracking

**Integration Points:**

1. **Equipment → Recipe:**
   - Recipe requires equipment class
   - Control recipe assigns actual equipment
   - Recipe execution tracks equipment used
   - Equipment usage tracks runtime per batch

2. **Recipe → Batch:**
   - Master recipe defines process template
   - Control recipe created for specific batch
   - Recipe execution captures batch manufacturing
   - Parameter values recorded for batch

3. **Equipment → Batch:**
   - Equipment usage links equipment to batch
   - Batch material usage tracks materials consumed
   - Equipment qualification ensures batch quality
   - Equipment calibration ensures measurement accuracy

4. **Material → Recipe → Batch:**
   - Recipe material defines BOM
   - Batch material usage tracks actual consumption
   - Material lot provides traceability
   - Recipe execution links materials to phases

**Key Query Patterns Enabled:**

```sql
-- 1. Equipment Usage History
-- Which batches were manufactured on equipment BR-10KL-001?

-- 2. Recipe Version Tracking
-- Which recipe version was used for each batch?

-- 3. Out-of-Specification (OOS) Detection
-- Find all OOS parameter values for a batch

-- 4. Material Lot Genealogy
-- Which material lots were used in a batch?

-- 5. Equipment Utilization (OEE)
-- Calculate equipment utilization for Q4 2025

-- 6. Recipe Execution Time Analysis
-- Compare actual vs. planned phase durations
```

**Benefits:**
- ✅ Complete traceability (Equipment → Recipe → Batch → Material → Parameters)
- ✅ Electronic Batch Record (21 CFR Part 11 compliant)
- ✅ Equipment lifecycle management
- ✅ Recipe versioning and change control
- ✅ CPP monitoring and alarming
- ✅ Material genealogy with lot-level traceability
- ✅ OEE calculation and utilization tracking
- ✅ Deviation management (OOS/OOT detection)
- ✅ Regulatory inspection readiness
- ✅ Process optimization analytics

---

## ISA-88 & ISA-95 Compliance

### ISA-88 (Batch Control)

**Physical Model:**
- Enterprise → Site → Area → Process Cell → Unit → Equipment Module → Control Module

**Procedural Model:**
- Procedure → Unit Procedure → Operation → Phase

**Recipe Management:**
- General Recipe → Site Recipe → Master Recipe → Control Recipe

**Batch Management:**
- Batch definition, scheduling, execution, history

### ISA-95 (Enterprise-Control Integration)

**Equipment Hierarchy:**
- Level 4: Enterprise (ERP)
- Level 3: Manufacturing Operations (MES)
- Level 2: Supervisory Control (SCADA)
- Level 1: Process Control (DCS)
- Level 0: Field Devices (Sensors, Actuators)

**Integration:**
- Equipment master data bridges Level 3 (MES) and Level 4 (ERP)
- Recipe management integrates Level 3 (execution) with Level 4 (planning)
- Batch execution data flows from Level 1/2 (control) to Level 3 (MES) to Level 4 (analytics)

---

## Use Cases

### 1. Equipment Qualification Management
**Objective:** Track all equipment qualification activities
**Data:** Equipment qualification records, calibration certificates
**Query:** Which equipment is due for requalification?
**Outcome:** Proactive qualification management, compliance assurance

### 2. Recipe Version Control
**Objective:** Track which recipe version produced which batches
**Data:** Master recipe versions, control recipes, batches
**Query:** Show batch performance by recipe version
**Outcome:** Identify optimal recipe version, support change control

### 3. Electronic Batch Record
**Objective:** Generate complete electronic batch record
**Data:** Recipe execution, parameter values, material usage, equipment usage
**Query:** Retrieve complete batch history for Batch B-12345
**Outcome:** 21 CFR Part 11 compliant documentation, inspection readiness

### 4. Equipment Utilization (OEE)
**Objective:** Calculate Overall Equipment Effectiveness
**Data:** Equipment usage (runtime, idle, downtime)
**Query:** OEE calculation for BR-10KL-001 in Q4 2025
**Outcome:** Identify bottlenecks, optimize scheduling

### 5. Critical Process Parameter Monitoring
**Objective:** Monitor CPPs in real-time
**Data:** Execution parameter values, alarm thresholds
**Query:** Find all CPP excursions for Product XYZ
**Outcome:** Early deviation detection, quality assurance

### 6. Material Lot Genealogy
**Objective:** Complete material traceability for recalls
**Data:** Batch material usage, material lots
**Query:** Which batches used Material Lot L-12345?
**Outcome:** Rapid recall response (<1 hour)

### 7. Process Optimization
**Objective:** Analyze actual vs. target across batches
**Data:** Execution parameter values, recipe parameters
**Query:** Compare temperature control across 100 batches
**Outcome:** Process improvements, reduced variability

---

## Technical Implementation

### Database Schema Additions

**New Tables:** 21 new entities
- Equipment: 7 tables
- Recipe: 11 tables
- Integration: 3 tables

**New Relationships:** 30+ new foreign keys

**SCD Type 2 Implementation:**
- All entities support historical tracking
- current_flag, effective_from, effective_to

### Integration Points

**Equipment Master → ERP/EAM:**
- Equipment ID synchronization
- CMMS integration (work orders)
- Spare parts inventory

**Recipe Management → MES:**
- Recipe download to control system
- Recipe execution monitoring
- Batch record upload

**Parameter Tracking → Historian:**
- Real-time data collection
- Parameter value storage
- Alarm management

**Material Usage → Inventory:**
- Material lot consumption
- Inventory depletion
- Reorder triggers

---

## File Additions

### New HTML Diagrams (3)
1. `Equipment_Master_Data_ISA88.html` (15 KB)
2. `Process_Recipe_Control_Recipe_ISA88.html` (20 KB)
3. `Integrated_Equipment_Recipe_Execution.html` (25 KB)

### Updated Documentation
- `README.md` - Added equipment & recipe sections
- `EQUIPMENT_RECIPE_ENHANCEMENTS.md` (this file)

**Total New Content:** ~60 KB of diagrams + documentation

---

## Migration from Previous Version

### For Existing Implementations

**Phase 1: Add Equipment Tables**
- Deploy EQUIPMENT_MASTER and hierarchy tables
- Populate with existing equipment data
- Link to existing BATCH and MANUFACTURING_PROCESS_RESULTS

**Phase 2: Add Recipe Tables**
- Deploy MASTER_RECIPE and related tables
- Document existing processes as recipes
- Version recipes (start with v1.0)

**Phase 3: Link Executions**
- Deploy RECIPE_EXECUTION and parameter tracking
- Start capturing execution data for new batches
- Backfill historical data if needed

**Phase 4: Full Integration**
- Link equipment usage to batches
- Link material usage to recipe executions
- Enable full query patterns

---

## Regulatory Compliance

### 21 CFR Part 11
- ✅ Electronic batch records with complete audit trail
- ✅ Electronic signatures for recipe approval
- ✅ Change control with versioning

### EU GMP Annex 11
- ✅ Computerized system validation (equipment qualification)
- ✅ Data integrity (ALCOA+)
- ✅ Audit trail for all data changes

### ISA-88 / ISA-95
- ✅ Physical model hierarchy (7 levels)
- ✅ Procedural model hierarchy (4 levels)
- ✅ Recipe management (master, control, execution)
- ✅ Batch management (definition, scheduling, execution)

### ICH Q10
- ✅ Knowledge management (recipe capture)
- ✅ Process performance monitoring (parameter tracking)
- ✅ Continuous improvement (process optimization)

---

## Next Steps

### Recommended Actions

1. **Review New Diagrams:**
   - Open and review all 3 new HTML diagrams
   - Understand equipment hierarchy
   - Understand recipe procedural model
   - Review integration points

2. **Map to Your Environment:**
   - Identify your equipment hierarchy
   - Document your master recipes
   - Define critical process parameters
   - Establish qualification schedules

3. **Plan Implementation:**
   - Start with equipment master data
   - Add recipe management
   - Implement execution tracking
   - Full integration

4. **Validate:**
   - IQ/OQ/PQ for new system components
   - User acceptance testing
   - Regulatory inspection readiness

---

## Support

For questions about equipment and recipe enhancements:
1. Review the 3 new HTML diagrams
2. Check integration diagram for relationships
3. Review query patterns in integration document
4. Contact data architecture team

---

**Version:** 1.1 Enhancement
**Status:** Production Ready
**Compliance:** ISA-88, ISA-95, 21 CFR Part 11, EU GMP, ICH Q10

🏭 **Equipment + Recipe + Batch = Complete Manufacturing Traceability** 🏭
