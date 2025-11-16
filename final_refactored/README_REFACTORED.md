# Pharma Data Model - Refactored Package

## Overview
This package contains the refactored Pharma Data Model with business-friendly naming conventions and improved architecture.

## Key Changes

### 1. Business-Friendly Entity Names
All technical entity names have been converted to business-friendly format:

| Technical Name | Business Name |
|---|---|
| DIM_BATCH | Batch |
| DIM_MATERIAL | Material |
| FACT_ANALYTICAL | Analytical Results |
| FACT_MANUFACTURING_PROCESS_RESULT | Manufacturing Process Results |
| BRIDGE_BATCH_GENEALOGY | Batch Genealogy |
| DIM_MANUFACTURER | Manufacturer |

### 2. Meaningful Relationship Labels
Relationships now use business terminology instead of technical field names:

| Technical Label | Business Label |
|---|---|
| batch_key | performed on |
| parent_batch (self-join) | derived from |
| manufacturer_key | manufactured by |
| test_key | evaluated against |
| method_key | tested via |

### 3. Identity Instead of Key
All surrogate keys now use "identity" suffix instead of "key":

| Before | After |
|---|---|
| batch_key PK | batch identity PK |
| material_key FK | material identity FK |
| test_key FK | test identity FK |

### 4. Consistent Naming Across All Artifacts
- Mermaid diagrams use business names
- Entity catalog uses business names
- Documentation uses business names
- All descriptions and tooltips updated

### 5. Dynamic Diagram Architecture
The main lifecycle HTML file can optionally load diagrams from separate JavaScript modules in the `diagrams/` directory:

```
diagrams/
├── index.js (central export)
├── batchGenealogy.js
├── conceptualProcessFlow.js
├── conceptualAnalytical.js
├── conceptualIntegrated.js
├── processStarSchema.js
├── analyticalStarSchema.js
├── completeConceptualERD.js
└── completeLogicalERD.js
```

**Benefits:**
- Single source of truth - no diagram duplication
- Edit one file, changes reflect everywhere
- Better maintainability
- Cleaner HTML files

## Files Included

1. **Pharma_Data_Model_Complete_Lifecycle.html** - Main comprehensive view with all diagrams
2. **Pharma_Data_Model_Diagram_1_Conceptual_Process_Flow.html** - Process flow conceptual model
3. **Pharma_Data_Model_Diagram_2_Conceptual_Analytical.html** - Analytical conceptual model
4. **Pharma_Data_Model_Diagram_3_Conceptual_Integrated.html** - Integrated conceptual view
5. **Pharma_Data_Model_Diagram_4_Batch_Genealogy.html** - SAP GBT batch genealogy
6. **Pharma_Data_Model_Diagram_5_Process_Star_Schema.html** - Manufacturing star schema
7. **Pharma_Data_Model_Diagram_6_Analytical_Star_Schema.html** - Analytical star schema
8. **Pharma_Data_Model_Diagram_7_Complete_Conceptual_ERD.html** - Complete conceptual ERD
9. **Pharma_Data_Model_Diagram_8_Complete_Logical_ERD.html** - Complete logical ERD
10. **Pharma_Data_Model_Diagram_9_Conceptual_Model.html** - High-level conceptual model

## Usage

### Viewing the Models
Simply open any HTML file in a web browser. The diagrams will render automatically using Mermaid.js.

### Updating Diagrams
For the modular approach:
1. Edit the corresponding `.js` file in the `diagrams/` directory
2. Refresh the main HTML file to see changes
3. No need to edit multiple files

For individual diagrams:
1. Each standalone HTML file contains its own diagram
2. Edit the mermaid code directly in the HTML
3. Refresh to see changes

## Entity Catalog Summary

### Facts (Measurement Tables)
- **Analytical Results**: Quality control test results and specifications
- **Manufacturing Process Results**: Process execution metrics and parameters
- **Batch Material Usage**: Material consumption and production tracking

### Conformed Dimensions (Shared Across Domains)
- **Material**: Raw materials, cell lines, MCB/WCB, therapeutic proteins
- **Batch**: Production batches with genealogy tracking
- **Sample**: Test specimens and retention samples
- **Manufacturer**: Manufacturing sites, CMOs, laboratories
- **Specification**: Acceptance criteria and limits
- **Notification**: Deviations, CAPA, quality events
- **Document**: Batch records, protocols, COAs, SOPs
- **Source System**: Data lineage (LIMS, MES, ERP, ELN)

### Process-Specific Dimensions
- **Local Process Hierarchy**: Site-specific process decomposition
- **Common Process Hierarchy**: Industry standard process taxonomy
- **Process Operation**: Manufacturing process steps
- **Transformation**: Material transformation processes
- **Production Order**: SAP production orders and work orders

### Analytical-Specific Dimensions
- **Test**: Test catalog and methods
- **Test Location**: Laboratory locations
- **Method**: Analytical procedures and protocols
- **Instrument**: Laboratory instruments and equipment

### Bridge Tables (Many-to-Many Relationships)
- **Batch Genealogy**: Multi-parent batch relationships (pooling, merging)
- **Material Transformation**: Material lineage tracking

## Technology Stack
- **Visualization**: Mermaid.js for ERD diagrams
- **Format**: HTML5 with embedded CSS
- **Modularity**: ES6 JavaScript modules (optional)
- **Compatibility**: Works in all modern browsers

## Best Practices

1. **Naming Convention**: Always use business-friendly names in new entities
2. **Relationships**: Use descriptive business terms for relationships
3. **Documentation**: Keep entity descriptions clear and business-focused
4. **Consistency**: Maintain naming consistency across all artifacts
5. **Modularity**: Consider using diagram modules for large projects

## Support & Maintenance

For questions or updates:
- Review the entity catalog in the main HTML file
- Check individual diagram files for specific details
- Refer to this README for naming conventions
- Follow the established patterns for new entities

---

**Version**: 2.0 (Refactored)  
**Last Updated**: November 2025  
**Status**: Production Ready
