# Dynamic Diagram Loading - Implementation Guide

## Overview

This guide explains how to implement dynamic diagram loading in the main Pharma Data Model HTML file. This eliminates diagram duplication and creates a single source of truth.

---

## Current Architecture

### Inline Approach (Current Default)
- Each diagram is embedded directly in the HTML file
- Complete diagram code duplicated in main lifecycle file
- **Pros**: Works immediately, self-contained
- **Cons**: Diagram duplication, harder to maintain

### Modular Approach (Available)
- Diagrams stored as ES6 modules in `diagrams/` directory
- Main file dynamically imports and renders diagrams
- **Pros**: Single source of truth, easier maintenance
- **Cons**: Requires ES6 module support (all modern browsers)

---

## Diagram Modules Structure

```
diagrams/
├── index.js                    # Central export for all diagrams
├── batchGenealogy.js          # SAP GBT Batch Genealogy
├── conceptualProcessFlow.js   # Conceptual Process Flow
├── conceptualAnalytical.js    # Conceptual Analytical
├── conceptualIntegrated.js    # Conceptual Integrated View
├── processStarSchema.js       # Process Star Schema
├── analyticalStarSchema.js    # Analytical Star Schema
├── completeConceptualERD.js   # Complete Conceptual ERD
├── completeLogicalERD.js      # Complete Logical ERD
└── conceptualModel.js         # High-level Conceptual Model
```

Each module exports:
1. **Diagram content** - The mermaid ERD code
2. **Metadata** - Title and ID information

---

## Implementation Steps

### Step 1: Prepare HTML Containers

Replace inline mermaid diagrams with placeholder containers:

**Before (Inline):**
```html
<div class="diagram-container">
    <div class="mermaid">
erDiagram
    Batch {
        bigint batch identity PK
        ...
    }
    </div>
</div>
```

**After (Dynamic):**
```html
<div class="diagram-container">
    <div id="diagram-batch-genealogy" class="diagram-placeholder">
        <!-- Diagram will be loaded here dynamically -->
    </div>
</div>
```

### Step 2: Add Loading Script

Add this script before the closing `</body>` tag:

```html
<script type="module">
    // Import all diagram modules
    import * as diagrams from './diagrams/index.js';
    
    // Diagram configuration mapping
    const diagramConfig = [
        { containerId: 'diagram-batch-genealogy', module: 'batchGenealogy' },
        { containerId: 'diagram-conceptual-process', module: 'conceptualProcessFlow' },
        { containerId: 'diagram-conceptual-analytical', module: 'conceptualAnalytical' },
        { containerId: 'diagram-conceptual-integrated', module: 'conceptualIntegrated' },
        { containerId: 'diagram-process-star', module: 'processStarSchema' },
        { containerId: 'diagram-analytical-star', module: 'analyticalStarSchema' },
        { containerId: 'diagram-complete-conceptual', module: 'completeConceptualERD' },
        { containerId: 'diagram-complete-logical', module: 'completeLogicalERD' },
        { containerId: 'diagram-conceptual-model', module: 'conceptualModel' }
    ];
    
    // Function to load diagram into container
    function loadDiagram(containerId, moduleName) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.warn(`Container not found: ${containerId}`);
            return;
        }
        
        const diagramContent = diagrams[moduleName];
        if (!diagramContent) {
            console.warn(`Diagram module not found: ${moduleName}`);
            return;
        }
        
        // Create mermaid div
        const mermaidDiv = document.createElement('div');
        mermaidDiv.className = 'mermaid';
        mermaidDiv.textContent = diagramContent;
        
        // Clear container and add diagram
        container.innerHTML = '';
        container.appendChild(mermaidDiv);
    }
    
    // Load all diagrams on DOM ready
    document.addEventListener('DOMContentLoaded', () => {
        diagramConfig.forEach(config => {
            loadDiagram(config.containerId, config.module);
        });
        
        // Re-initialize mermaid
        if (typeof mermaid !== 'undefined') {
            mermaid.init(undefined, document.querySelectorAll('.mermaid'));
        }
    });
</script>
```

### Step 3: Update Individual Diagram Sections

For each diagram section in the main HTML file:

1. Add a unique container ID
2. Remove the inline mermaid code
3. Keep the descriptive text

**Example:**

```html
<h2 id="batch-genealogy">🧬 SAP GBT Batch Genealogy</h2>

<div class="description">
    Complete traceability model supporting batch splits, merges, and transformations.
</div>

<div class="diagram-container">
    <div id="diagram-batch-genealogy" class="diagram-placeholder">
        <!-- Batch Genealogy diagram loaded from diagrams/batchGenealogy.js -->
    </div>
</div>
```

---

## Diagram Module Format

Each diagram module follows this format:

```javascript
/**
 * Batch Genealogy Diagram
 * Auto-generated diagram module
 */

export const batchGenealogy = `
erDiagram
    Batch {
        bigint batch identity PK "Surrogate key"
        varchar batch ID UK "Business batch number"
        ...
    }
    
    Batch Genealogy {
        ...
    }
    
    Batch ||--o| Batch : "derived from"
`;

export const batchGenealogy_metadata = {
    title: "SAP GBT Batch Genealogy",
    id: "batchgenealogy"
};
```

---

## Updating Diagrams

### To Update a Diagram:

1. **Edit the module file** in `diagrams/` directory
   ```bash
   # Edit the diagram
   vi diagrams/batchGenealogy.js
   ```

2. **Save changes** - Updates automatically reflect in main file

3. **No need to edit** the main HTML file or other references

### Example Update:

**Before:**
```javascript
export const batchGenealogy = `
erDiagram
    Batch {
        bigint batch identity PK
    }
`;
```

**After:**
```javascript
export const batchGenealogy = `
erDiagram
    Batch {
        bigint batch identity PK
        varchar batch status "Active, Expired"  -- New field added
    }
`;
```

**Result:** Main HTML file automatically shows updated diagram on next load!

---

## Benefits in Practice

### Scenario 1: Add New Entity Field
- ✅ Edit one diagram module
- ✅ Changes reflect everywhere
- ❌ No hunting through HTML files
- ❌ No copy-paste errors

### Scenario 2: Fix Relationship Label
- ✅ Update one diagram module
- ✅ Consistent across all views
- ❌ No missing updates

### Scenario 3: Version Control
- ✅ Clear git diff on diagram changes
- ✅ Easy to review changes
- ✅ Better change tracking

---

## Compatibility

### Browser Support
- ✅ Chrome 61+
- ✅ Firefox 60+
- ✅ Edge 16+
- ✅ Safari 10.1+
- ❌ IE 11 (does not support ES6 modules)

### Server Requirements
- Needs HTTP server (ES6 modules don't work with `file://` protocol)
- Any web server works (Apache, Nginx, Node.js, Python SimpleHTTPServer)

### Quick Server Setup

**Python:**
```bash
cd /path/to/pharma-model
python3 -m http.server 8000
# Visit http://localhost:8000
```

**Node.js:**
```bash
npx http-server .
# Visit http://localhost:8080
```

---

## Troubleshooting

### Issue: Diagrams Not Loading

**Check:**
1. Are you using a web server (not `file://`)?
2. Is the `diagrams/` directory in the same location as HTML?
3. Are there console errors? (Open browser DevTools)

**Solution:**
```bash
# Verify file structure
ls diagrams/index.js
# Should show: diagrams/index.js

# Verify module exports
cat diagrams/index.js
# Should show: export { ... } statements
```

### Issue: Module Not Found Error

**Check:**
1. Module name in `diagramConfig` matches file name
2. Module is exported from `diagrams/index.js`

**Solution:**
```javascript
// In diagrams/index.js, verify:
export { batchGenealogy } from './batchGenealogy.js';
```

### Issue: Mermaid Not Rendering

**Check:**
1. Mermaid.js library is loaded
2. `mermaid.init()` is called after diagram insertion

**Solution:**
```html
<!-- Verify in HTML head -->
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
```

---

## Migration Checklist

When converting from inline to modular:

- [ ] Backup original HTML file
- [ ] Verify `diagrams/` directory exists and has all modules
- [ ] Add container IDs to each diagram section
- [ ] Remove inline mermaid code
- [ ] Add loading script
- [ ] Test in web server environment
- [ ] Verify all diagrams load correctly
- [ ] Check navigation links still work
- [ ] Validate in multiple browsers

---

## Best Practices

### 1. Consistent Naming
```javascript
// Module file: batchGenealogy.js
// Export name: batchGenealogy
// Container ID: diagram-batch-genealogy
```

### 2. Clear Comments
```html
<!-- Batch Genealogy diagram loaded from diagrams/batchGenealogy.js -->
<div id="diagram-batch-genealogy"></div>
```

### 3. Version Control
```bash
# Separate commits for diagram changes
git add diagrams/batchGenealogy.js
git commit -m "Update Batch entity with new status field"
```

### 4. Documentation
Keep a changelog for diagram module updates:
```markdown
## diagrams/batchGenealogy.js
- 2025-11-15: Added batch_status field
- 2025-11-14: Updated relationship labels
```

---

## Optional: Fallback for Non-Module Browsers

```html
<script nomodule>
    // Fallback for older browsers
    alert('Your browser does not support ES6 modules. Please use a modern browser.');
</script>
```

---

## Summary

### Inline Approach (Default)
- ✅ Works immediately
- ✅ No server required
- ❌ Diagram duplication
- **Use when:** Quick sharing, simple deployment

### Modular Approach (Available)
- ✅ Single source of truth
- ✅ Easy maintenance
- ❌ Requires web server
- **Use when:** Active development, frequent updates

**Both approaches produce identical visual results!**

---

## Quick Start with Modular Approach

```bash
# 1. Start web server
cd /path/to/final_refactored
python3 -m http.server 8000

# 2. Open browser
open http://localhost:8000/Pharma_Data_Model_Complete_Lifecycle.html

# 3. Edit diagram
vi diagrams/batchGenealogy.js

# 4. Refresh browser to see changes
```

---

For questions or support with dynamic diagram loading, refer to the main README or contact the development team.

**Version**: 1.0
**Last Updated**: November 16, 2025
