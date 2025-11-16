# Pharmaceutical Equipment & Instruments Reference Guide

## Overview

This guide provides a comprehensive reference of equipment, instruments, and systems used throughout pharmaceutical manufacturing and clinical development. Each entry includes technical specifications, applications, and regulatory considerations.

---

## Table of Contents

1. [Upstream Manufacturing Equipment](#upstream-manufacturing-equipment)
2. [Downstream Purification Equipment](#downstream-purification-equipment)
3. [Fill/Finish Equipment](#fillfinish-equipment)
4. [Analytical Instrumentation](#analytical-instrumentation)
5. [Clinical Trial Systems](#clinical-trial-systems)
6. [Quality Control Laboratory](#quality-control-laboratory)
7. [Facility Support Systems](#facility-support-systems)

---

## Upstream Manufacturing Equipment

### Bioreactor Systems

#### Production Bioreactor (Stirred Tank Reactor - STR)
- **Manufacturers:** Thermo Fisher (HyPerforma), Sartorius (BIOSTAT), Eppendorf (BioFlo)
- **Capacity Range:** 2,000L - 20,000L working volume
- **Material:** 316L stainless steel, electropolished surface
- **Design Features:**
  - Top-driven impeller (pitched blade or marine type)
  - Jacketed vessel for temperature control
  - Micro-sparger for gas delivery
  - Multiple ports for sensors, sampling, feeding
- **Control Systems:** DCS (DeltaV, PCS7), pH/DO/Temperature control
- **Applications:** Production-scale mammalian cell culture
- **Validation:** IQ/OQ/PQ, SIP validation, CIP validation
- **Cost:** $500K - $2M (vessel + automation)

#### WAVE Bioreactor (Rocking Platform)
- **Manufacturer:** Cytiva (formerly GE Healthcare)
- **Models:** WAVE 25, WAVE 50, ReadyToProcess WAVE 25
- **Capacity:** 25L - 500L
- **Technology:** Single-use rocking platform with inflatable bag
- **Advantages:** No cleaning validation, rapid setup, reduced contamination risk
- **Applications:** Seed train expansion, process development
- **Cost:** $50K - $150K (system), $500-$2K per bag

#### Seed Bioreactor
- **Models:** Sartorius BIOSTAT 200-500L
- **Purpose:** Scale-up from WAVE to production bioreactor
- **Features:** Similar to production STR but smaller scale
- **Automation:** Integrated with MES for recipe execution

### Online Sensors & Process Analytical Technology (PAT)

#### pH Sensors
- **Model:** Mettler Toledo InPro 4260i/SG
- **Technology:** Glass electrode with temperature compensation
- **Range:** pH 0-14
- **Accuracy:** ±0.02 pH units
- **Sterilization:** SIP compatible (121°C steam)
- **Calibration:** 2-point (pH 4.0, 7.0)
- **Lifespan:** 6-12 months in bioreactor

#### Dissolved Oxygen (DO) Sensors
- **Model:** Mettler Toledo InPro 6860i (optical)
- **Technology:** Luminescence-based (no membrane, no drift)
- **Range:** 0-200% saturation
- **Accuracy:** ±1% of reading
- **Advantages:** Long-term stability, no calibration drift
- **Applications:** Bioreactor oxygen monitoring, cascade control

#### Biomass Sensors
- **Model:** ABER Futura Neotec
- **Technology:** Capacitance probe (dielectric spectroscopy)
- **Measurement:** Viable cell density (VCD) estimation
- **Range:** 0.5 - 50 × 10⁶ cells/mL
- **Advantages:** Real-time, non-invasive, no sampling
- **Calibration:** Correlation with offline cell counting

#### Metabolite Analyzers
- **Model:** YSI 2900 Biochemistry Analyzer
- **Analytes:** Glucose, lactate, glutamine, glutamate, ammonia
- **Technology:** Enzyme-based electrochemical detection
- **Sample Volume:** 25 μL
- **Time:** 60 seconds per sample
- **Applications:** At-line monitoring, feed control

### Control & Automation Systems

#### Distributed Control Systems (DCS)
- **Emerson DeltaV:**
  - Industry standard for biotech
  - 21 CFR Part 11 compliant
  - Integrated batch management
  - Cost: $500K - $2M per suite

- **Siemens PCS 7:**
  - Robust automation platform
  - TIA Portal integration
  - Scalable architecture

#### Manufacturing Execution Systems (MES)
- **Emerson Syncade:**
  - Electronic batch records (EBR)
  - Workflow orchestration
  - Material tracking and genealogy

- **Dassault Systèmes BIOVIA:**
  - Lab execution system (LES)
  - Quality management integration

#### Historians & Data Analytics
- **OSIsoft PI System:**
  - Real-time data historian
  - Process analytics
  - Integration with BI tools

- **Aspen IP.21:**
  - Manufacturing intelligence platform
  - Advanced analytics

---

## Downstream Purification Equipment

### Clarification Systems

#### Disk-Stack Centrifuge
- **Models:** Alfa Laval BTPX 205, Carr Powerfuge P12
- **Speed:** 8,000 - 10,000 RPM
- **Flow Rate:** 200-400 L/hr
- **Function:** Remove cells and debris (>5 μm)
- **Output Turbidity:** <50 NTU
- **CIP/SIP:** Automated sequences
- **Cost:** $200K - $500K

#### Depth Filtration
- **Systems:** Pall SUPRAcap, Merck Millistak+
- **Configuration:** Dual-stage (0.6μm → 0.2μm)
- **Technology:** Single-use capsule filters
- **Capacity:** 200-400 kg cell mass/m²
- **Advantages:** No equipment cleaning, scalable

### Chromatography Systems

#### Protein A Affinity Chromatography
- **Resin:** GE MabSelect SuRe, Poros MabCapture A
- **Binding Capacity:** 30-50 g mAb/L resin
- **Column Size:** 60 cm diameter × 30 cm bed height (300L)
- **System:** GE AKTA Ready, Cytiva BioProcess
- **Automation:** UNICORN software
- **Resin Lifetime:** 100-200 cycles
- **Cost:** $20K - $50K per liter of resin

#### Cation Exchange (CEX)
- **Resin:** Poros 50 XS, GE Capto S ImpRes
- **Mode:** Bind-elute (salt gradient)
- **Function:** Remove aggregates, HCP, leached Protein A
- **Output:** >99% monomer purity

#### Anion Exchange (AEX)
- **Resin:** Poros 50 HQ, GE Q Sepharose FF
- **Mode:** Flow-through (product in flow-through)
- **Function:** Remove DNA, viruses, endotoxin
- **Impurity Removal:** DNA <100 pg/dose, HCP <100 ppm

### Viral Clearance

#### Viral Inactivation (Low pH)
- **Method:** Citrate buffer, pH 3.5, 60 min, 18-25°C
- **Equipment:** Jacketed hold tank (500-1,000L)
- **Log Reduction:** >4 logs (enveloped viruses)
- **Monitoring:** pH probe, timer, temperature

#### Nanofiltration
- **Filter:** Asahi Planova 20N (20 nm pores)
- **Mechanism:** Size exclusion
- **Log Reduction:** >4-6 logs (MuLV, MMV, PPV)
- **Capacity:** 200-500 L/m²
- **Integrity Test:** Bubble point before and after use

### Concentration & Formulation

#### Ultrafiltration/Diafiltration (UF/DF)
- **Systems:** Merck Pellicon 3, Sartorius Sartocon Eco
- **Membrane:** 30 kDa MWCO (polyethersulfone)
- **Technology:** Tangential flow filtration (TFF)
- **Function:** 10-30X concentration + buffer exchange
- **Final Concentration:** 50-150 mg/mL

#### Sterile Filtration
- **Filters:** Sartorius Sartopore 2, Pall Supor
- **Pore Size:** 0.2 μm (dual redundant)
- **Integrity Test:** Bubble point, diffusion test
- **Application:** Terminal bioburden reduction

---

## Fill/Finish Equipment

### Aseptic Filling

#### Filling Machines
- **Manufacturers:** Optima (Inova), Groninger, Bausch+Ströbel
- **Technology:** Rotary piston or peristaltic pump
- **Speed:** 200-600 vials/min
- **Fill Volume:** 0.5 mL - 50 mL (programmable)
- **Accuracy:** ±2% (for volumes >1 mL)
- **Environment:** Isolator (Grade A) or RABS
- **Cost:** $2M - $10M (complete line)

#### Isolator/RABS Systems
- **Technology:** Barrier isolation technology
- **Classification:** ISO 5 (Grade A)
- **HEPA Filtration:** >99.995% efficiency at 0.3 μm
- **Sterilization:** VHP (vaporized hydrogen peroxide)
- **Pressure:** Positive 50-100 Pa
- **Monitoring:** Particle counting, viable air sampling

### Container Preparation

#### Depyrogenation Tunnel
- **Function:** Dry heat sterilization + depyrogenation
- **Temperature:** 250-350°C for 20-60 minutes
- **Capacity:** 10,000 - 50,000 vials/hour
- **Zones:** Pre-heat → Sterilization → Cooling
- **Validation:** Endotoxin challenge (3-log reduction)

#### Stopper Washing & Sterilization
- **Process:** WFI washing + steam sterilization
- **Equipment:** Automated washer/sterilizer
- **Material:** Elastomeric closures (butyl rubber)

### Lyophilization

#### Freeze Dryers
- **Manufacturers:** IMA Life, SP Scientific, Telstar
- **Capacity:** 10,000 - 100,000 vials/batch
- **Shelves:** 10-30 shelves with hydraulic control
- **Temperature Range:** -55°C to +60°C
- **Vacuum:** <100 mTorr (0.13 mbar)
- **Cycle Time:** 48-120 hours
- **Cost:** $1M - $5M

### Inspection Systems

#### Automated Visual Inspection (AVI)
- **Manufacturers:** Eisai, Stevanato, Brevetti CEA
- **Technology:** High-resolution cameras (360° view)
- **Speed:** 300-600 vials/min
- **Detection:** Particles, cracks, fill level, color
- **AI/ML:** Defect classification algorithms
- **Cost:** $500K - $2M

#### Manual Visual Inspection
- **Light Boxes:** White and black background
- **Speed:** 30-60 units/min per inspector
- **Training:** Operator qualification program

### Labeling & Serialization

#### Track & Trace Systems
- **Vendors:** Antares Vision, Optel, Laetus
- **Technology:** 2D DataMatrix barcode
- **Compliance:** FDA DSCSA, EU FMD
- **Aggregation:** Vial → Carton → Case → Pallet
- **Verification:** 100% barcode read verification

---

## Analytical Instrumentation

### Chromatography Systems

#### HPLC/UPLC
- **Agilent 1260/1290 Infinity:**
  - Binary pump, autosampler, TCC, DAD
  - 21 CFR Part 11 compliant
  - Cost: $50K - $100K

- **Waters ACQUITY UPLC:**
  - Ultra-high pressure (15,000 psi)
  - Faster analysis, higher resolution
  - Cost: $80K - $150K

#### Size Exclusion Chromatography (SEC)
- **Column:** TSKgel G3000SWXL (7.8 × 300 mm)
- **Mobile Phase:** 200 mM phosphate, pH 6.8
- **Detection:** UV 280 nm
- **Application:** Aggregates, monomer, fragments

#### Capillary Electrophoresis
- **Sciex PA800 Plus:**
  - CE-SDS (purity)
  - cIEF (charge variants)
  - Imaged CE (automated)
  - Cost: $100K - $150K

### Mass Spectrometry

#### LC-MS Systems
- **Thermo Orbitrap Exploris 480:**
  - High-resolution (>500,000)
  - Intact mass, peptide mapping
  - Cost: $400K - $600K

- **AB Sciex TripleTOF 6600:**
  - Hybrid quadrupole-TOF
  - High sensitivity
  - Cost: $400K - $500K

#### MALDI-TOF
- **Bruker Autoflex Speed:**
  - Intact mass, glycan profiling
  - Rapid screening (<5 min/sample)
  - Cost: $250K - $350K

### Protein Characterization

#### Spectrophotometers
- **Thermo Nanodrop:**
  - Micro-volume (1-2 μL)
  - Protein concentration (A280)
  - Cost: $10K - $15K

- **Agilent Cary 60:**
  - UV-Vis scanning
  - Cost: $20K - $30K

#### Differential Scanning Calorimetry (DSC)
- **Malvern MicroCal VP-Capillary DSC:**
  - Thermal stability (Tm)
  - Formulation screening
  - Cost: $100K - $150K

#### Dynamic Light Scattering (DLS)
- **Malvern Zetasizer Nano ZS:**
  - Particle size (0.3 nm - 10 μm)
  - Aggregation monitoring
  - Cost: $50K - $80K

### Bioassays

#### Plate Readers
- **BMG CLARIOstar Plus:**
  - Luminescence, fluorescence, absorbance
  - Cell-based assays
  - Cost: $80K - $120K

- **Molecular Devices SpectraMax i3x:**
  - Multi-mode detection
  - ELISA, cell viability
  - Cost: $40K - $60K

#### Flow Cytometers
- **BD FACSCanto II:**
  - 3-laser, 8-color
  - Cell surface binding assays
  - Cost: $150K - $200K

#### Surface Plasmon Resonance (SPR)
- **Cytiva Biacore 8K:**
  - Real-time binding kinetics
  - 8 parallel channels
  - Cost: $400K - $500K

### Microbiological Testing

#### Endotoxin Testing
- **Charles River Endosafe nexgen-PTS:**
  - LAL cartridge-based
  - 15-minute results
  - Cost: $30K - $50K

#### Sterility Testing
- **BACTEC FX:**
  - Rapid microbial detection
  - Automated monitoring
  - Cost: $50K - $80K

---

## Clinical Trial Systems

### Electronic Data Capture (EDC)
- **Medidata Rave:**
  - Cloud-based EDC
  - GCP/21 CFR Part 11 compliant
  - Cost: $100K - $500K per trial

### Clinical Trial Management System (CTMS)
- **Veeva Vault CTMS:**
  - Trial planning, site management
  - Budget tracking, milestones
  - Cost: $200K - $1M annually

### Interactive Response Technology (IRT)
- **Almac IWRS:**
  - Randomization, blinding
  - Drug supply management
  - Cost: $50K - $200K per trial

### Safety Database
- **Oracle Argus:**
  - Pharmacovigilance
  - AE reporting, MedDRA coding
  - Cost: $500K - $2M

---

## Quality Control Laboratory

### LIMS Platforms
- **LabWare LIMS:**
  - Industry standard
  - Highly configurable
  - Cost: $500K - $2M (implementation)

- **Thermo SampleManager:**
  - Strong instrument integration
  - Scientific data management

### Validation & Compliance
- **IQ/OQ/PQ Documentation**
- **21 CFR Part 11 Compliance**
- **Audit Trail Requirements**
- **Method Validation (ICH Q2)**

---

## Facility Support Systems

### Water for Injection (WFI)
- **Technology:** Distillation or RO + EDI
- **Distribution:** 80°C hot loop
- **Monitoring:** Conductivity, TOC, bioburden, endotoxin

### Clean Steam
- **Generation:** Pure steam generator
- **Application:** SIP (steam-in-place)
- **Quality:** 121°C, pyrogen-free

### HVAC & Cleanrooms
- **Classification:** ISO 5 (Grade A) to ISO 8 (Grade C)
- **HEPA Filters:** 99.995% efficiency
- **Monitoring:** Particle counting, differential pressure

### Gas Systems
- **Compressed Air:** Oil-free, HEPA filtered
- **Nitrogen:** USP grade, blanketing
- **CO2:** USP grade, pH control

---

## Equipment Qualification & Validation

### Qualification Phases
1. **User Requirements Specification (URS):** Define functional requirements
2. **Design Qualification (DQ):** Verify design meets URS
3. **Installation Qualification (IQ):** Verify correct installation
4. **Operational Qualification (OQ):** Verify operates per specifications
5. **Performance Qualification (PQ):** Verify performance in production

### Ongoing Compliance
- **Calibration:** Annual for critical instruments
- **Preventive Maintenance:** Per manufacturer schedule
- **Change Control:** Manage equipment modifications
- **Deviation Management:** Track and investigate failures

---

## Cost Summary (Approximate)

| **Equipment Category** | **Cost Range** |
|------------------------|----------------|
| Production Bioreactor (10KL) | $500K - $2M |
| Chromatography Skid | $300K - $1M |
| Protein A Resin (300L) | $6M - $15M |
| Fill/Finish Line | $5M - $20M |
| Lyophilizer | $1M - $5M |
| LC-MS System | $300K - $600K |
| HPLC System | $50K - $150K |
| LIMS Implementation | $500K - $2M |
| DCS/MES Suite | $1M - $5M |

---

## Regulatory Considerations

### FDA Guidance
- **Process Validation (2011):** Lifecycle approach (Stage 1/2/3)
- **PAT Guidance (2004):** Real-time quality monitoring
- **Data Integrity (2018):** ALCOA+ principles

### EU GMP
- **Annex 1:** Sterile manufacturing
- **Annex 11:** Computerized systems
- **Annex 15:** Qualification and validation

### ICH Guidelines
- **Q7:** API manufacturing GMP
- **Q8:** Pharmaceutical development
- **Q9:** Quality risk management
- **Q10:** Pharmaceutical quality system

---

## References

1. FDA Guidance for Industry - Process Validation (2011)
2. ICH Q7 - Good Manufacturing Practice for APIs
3. EU GMP Annex 1 - Manufacture of Sterile Medicinal Products
4. USP <1229> - Sterilization of Compendial Articles
5. ASTM E2500 - Bioprocessing Equipment Standard

---

**Document Version:** 1.0
**Last Updated:** November 16, 2025
**Maintained By:** Data Architecture Team
