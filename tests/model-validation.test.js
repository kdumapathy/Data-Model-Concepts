const fs = require('fs');
const path = require('path');
const cheerio = require('cheerio');

describe('Model Relationship Validation Tests', () => {
  describe('Entity Relationship Diagram Validation', () => {
    const getERDiagrams = () => {
      const diagrams = [];
      const diagramDir = 'pharma-data-model/diagrams/data-model';

      if (fs.existsSync(diagramDir)) {
        const files = fs.readdirSync(diagramDir);
        files.forEach(file => {
          if (file.endsWith('.html')) {
            const filePath = path.join(diagramDir, file);
            const content = fs.readFileSync(filePath, 'utf8');
            const $ = cheerio.load(content);
            const mermaidCode = $('.mermaid').first().text();

            if (mermaidCode.includes('erDiagram')) {
              diagrams.push({
                name: file,
                path: filePath,
                content: mermaidCode
              });
            }
          }
        });
      }

      return diagrams;
    };

    test('should find ER diagrams', () => {
      const erDiagrams = getERDiagrams();
      expect(erDiagrams.length).toBeGreaterThan(0);
      console.log(`Found ${erDiagrams.length} ER diagrams`);
    });

    test.each(getERDiagrams().map(d => [d.name, d.content]))(
      'ER diagram should have valid relationship syntax: %s',
      (name, content) => {
        // Extract relationship lines (||--||, }|--|{, etc.)
        const relationshipPattern = /(\w+)\s+([\|\}][o\|][-\.]{2}[\|\}][o\|])\s+(\w+)\s*:\s*"?([^"\n]+)"?/g;
        const relationships = [...content.matchAll(relationshipPattern)];

        // Should have at least one relationship
        expect(relationships.length).toBeGreaterThan(0);

        relationships.forEach(match => {
          const [, entity1, relType, entity2, label] = match;

          // Entities should be alphanumeric with underscores
          expect(entity1).toMatch(/^[a-zA-Z_][a-zA-Z0-9_]*$/);
          expect(entity2).toMatch(/^[a-zA-Z_][a-zA-Z0-9_]*$/);

          // Relationship type should be valid
          const validRelTypes = [
            '||--||', '||--|{', '||--o{', '||--o|',
            '}|--||', '}|--|{', '}|--o{', '}|--o|',
            '}o--||', '}o--|{', '}o--o{', '}o--o|',
            '|o--||', '|o--|{', '|o--o{', '|o--o|',
            '||..||', '||..|{', '||..o{', '||..o|',
            '}|..||', '}|..|{', '}|..o{', '}|..o|',
            '}o..||', '}o..|{', '}o..o{', '}o..o|',
            '|o..||', '|o..|{', '|o..o{', '|o..o|'
          ];

          expect(validRelTypes).toContain(relType);

          // Label should not be empty
          expect(label.trim().length).toBeGreaterThan(0);
        });
      }
    );

    test.each(getERDiagrams().map(d => [d.name, d.content]))(
      'ER diagram entities should have attributes: %s',
      (name, content) => {
        // Extract entity definitions
        const entityPattern = /(\w+)\s*\{([^}]+)\}/g;
        const entities = [...content.matchAll(entityPattern)];

        if (entities.length > 0) {
          entities.forEach(match => {
            const [, entityName, attributes] = match;

            // Entity name should be valid
            expect(entityName).toMatch(/^[a-zA-Z_][a-zA-Z0-9_]*$/);

            // Should have at least one attribute
            const attrLines = attributes
              .split('\n')
              .map(l => l.trim())
              .filter(l => l.length > 0 && !l.startsWith('%%'));

            expect(attrLines.length).toBeGreaterThan(0);

            // Each attribute should have valid format: type name
            attrLines.forEach(attr => {
              // Format: type name [optional modifiers like PK, FK, UK]
              expect(attr).toMatch(/\w+\s+\w+/);
            });
          });
        }
      }
    );

    test('Equipment Master Data should follow ISA-88 hierarchy', () => {
      const filePath = 'pharma-data-model/diagrams/data-model/Equipment_Master_Data_ISA88.html';

      if (fs.existsSync(filePath)) {
        const content = fs.readFileSync(filePath, 'utf8');
        const $ = cheerio.load(content);
        const mermaidCode = $('.mermaid').first().text();

        // ISA-88 hierarchy levels (top to bottom)
        const hierarchyLevels = [
          'Enterprise',
          'Site',
          'Area',
          'Process_Cell',
          'Unit',
          'Equipment_Module',
          'Control_Module'
        ];

        // All levels should be present
        hierarchyLevels.forEach(level => {
          expect(mermaidCode).toContain(level);
        });

        // Check for hierarchical relationships
        const hasHierarchicalRels = mermaidCode.includes('||--|{') ||
                                   mermaidCode.includes('}|--||');
        expect(hasHierarchicalRels).toBe(true);
      }
    });

    test('Batch Genealogy should have material traceability', () => {
      const filePath = 'pharma-data-model/diagrams/data-model/Pharma_Data_Model_Diagram_4_Batch_Genealogy.html';

      if (fs.existsSync(filePath)) {
        const content = fs.readFileSync(filePath, 'utf8');
        const $ = cheerio.load(content);
        const mermaidCode = $('.mermaid').first().text();

        // Should contain batch-related entities
        const batchKeywords = ['Batch', 'Material', 'Lot', 'Genealogy'];
        const hasRequiredEntities = batchKeywords.some(keyword =>
          mermaidCode.includes(keyword)
        );

        expect(hasRequiredEntities).toBe(true);
      }
    });
  });

  describe('Star Schema Validation', () => {
    test('Process Star Schema should have fact and dimension tables', () => {
      const filePath = 'pharma-data-model/diagrams/data-model/Pharma_Data_Model_Diagram_5_Process_Star_Schema.html';

      if (fs.existsSync(filePath)) {
        const content = fs.readFileSync(filePath, 'utf8');
        const $ = cheerio.load(content);
        const mermaidCode = $('.mermaid').first().text();

        // Should have entities with "Fact" or "Dim_" naming
        const hasFactTable = /Fact_?\w+/i.test(mermaidCode);
        const hasDimTable = /Dim_\w+/i.test(mermaidCode);

        expect(hasFactTable || hasDimTable).toBe(true);

        // Should have multiple entities (star schema needs center + dimensions)
        const entityPattern = /(\w+)\s*\{/g;
        const entities = [...mermaidCode.matchAll(entityPattern)];
        expect(entities.length).toBeGreaterThanOrEqual(3);
      }
    });

    test('Analytical Star Schema should have analytical entities', () => {
      const filePath = 'pharma-data-model/diagrams/data-model/Pharma_Data_Model_Diagram_6_Analytical_Star_Schema.html';

      if (fs.existsSync(filePath)) {
        const content = fs.readFileSync(filePath, 'utf8');
        const $ = cheerio.load(content);
        const mermaidCode = $('.mermaid').first().text();

        // Should have analytical-related keywords
        const analyticalKeywords = [
          'Analytical',
          'Sample',
          'Test',
          'Result',
          'Analysis'
        ];

        const hasAnalyticalContent = analyticalKeywords.some(keyword =>
          mermaidCode.toLowerCase().includes(keyword.toLowerCase())
        );

        expect(hasAnalyticalContent).toBe(true);
      }
    });
  });

  describe('Data Model Consistency', () => {
    test('Entity names should be consistently formatted', () => {
      const erDiagrams = [];
      const diagramDir = 'pharma-data-model/diagrams/data-model';

      if (fs.existsSync(diagramDir)) {
        const files = fs.readdirSync(diagramDir);
        files.forEach(file => {
          if (file.endsWith('.html')) {
            const filePath = path.join(diagramDir, file);
            const content = fs.readFileSync(filePath, 'utf8');
            const $ = cheerio.load(content);
            const mermaidCode = $('.mermaid').first().text();

            if (mermaidCode.includes('erDiagram')) {
              // Extract all entity names
              const entityPattern = /(\w+)\s*\{/g;
              const entities = [...mermaidCode.matchAll(entityPattern)];

              entities.forEach(match => {
                const entityName = match[1];

                // Entity names should use PascalCase or snake_case
                const isPascalCase = /^[A-Z][a-zA-Z0-9]*$/.test(entityName);
                const isSnakeCase = /^[A-Z][a-zA-Z0-9_]*$/.test(entityName);

                expect(isPascalCase || isSnakeCase).toBe(true);
              });
            }
          }
        });
      }
    });

    test('Common entities should appear across related diagrams', () => {
      const commonEntities = new Map();
      const diagramDir = 'pharma-data-model/diagrams/data-model';

      if (fs.existsSync(diagramDir)) {
        const files = fs.readdirSync(diagramDir);
        files.forEach(file => {
          if (file.endsWith('.html')) {
            const filePath = path.join(diagramDir, file);
            const content = fs.readFileSync(filePath, 'utf8');
            const $ = cheerio.load(content);
            const mermaidCode = $('.mermaid').first().text();

            if (mermaidCode.includes('erDiagram')) {
              const entityPattern = /(\w+)\s*\{/g;
              const entities = [...mermaidCode.matchAll(entityPattern)];

              entities.forEach(match => {
                const entityName = match[1];
                if (!commonEntities.has(entityName)) {
                  commonEntities.set(entityName, []);
                }
                commonEntities.get(entityName).push(file);
              });
            }
          }
        });

        // Find entities that appear in multiple diagrams
        const sharedEntities = Array.from(commonEntities.entries())
          .filter(([name, files]) => files.length > 1);

        // Should have some shared entities across diagrams
        expect(sharedEntities.length).toBeGreaterThan(0);
        console.log(`Found ${sharedEntities.length} entities shared across diagrams`);
      }
    });
  });

  describe('Process Flow Validation', () => {
    const getFlowDiagrams = () => {
      const diagrams = [];
      const dirs = [
        'pharma-data-model/diagrams/manufacturing-process',
        'pharma-data-model/diagrams/clinical-process'
      ];

      dirs.forEach(dir => {
        if (fs.existsSync(dir)) {
          const files = fs.readdirSync(dir);
          files.forEach(file => {
            if (file.endsWith('.html')) {
              const filePath = path.join(dir, file);
              const content = fs.readFileSync(filePath, 'utf8');
              const $ = cheerio.load(content);
              const mermaidCode = $('.mermaid').first().text();

              if (mermaidCode.includes('graph') || mermaidCode.includes('flowchart')) {
                diagrams.push({
                  name: file,
                  path: filePath,
                  content: mermaidCode
                });
              }
            }
          });
        }
      });

      return diagrams;
    };

    test('should find process flow diagrams', () => {
      const flowDiagrams = getFlowDiagrams();
      expect(flowDiagrams.length).toBeGreaterThan(0);
      console.log(`Found ${flowDiagrams.length} process flow diagrams`);
    });

    test.each(getFlowDiagrams().map(d => [d.name, d.content]))(
      'Flow diagram should have valid node connections: %s',
      (name, content) => {
        // Extract node connections (A --> B, A --- B, etc.)
        const connectionPattern = /(\w+)\s*(-->|---|\-\.\->|\-\.-)\s*(\w+)/g;
        const connections = [...content.matchAll(connectionPattern)];

        // Should have at least one connection
        expect(connections.length).toBeGreaterThan(0);

        connections.forEach(match => {
          const [, nodeA, connector, nodeB] = match;

          // Nodes should be alphanumeric
          expect(nodeA).toMatch(/^[a-zA-Z0-9_]+$/);
          expect(nodeB).toMatch(/^[a-zA-Z0-9_]+$/);

          // Connector should be valid
          const validConnectors = ['-->', '---', '-.->',  '-.-'];
          expect(validConnectors).toContain(connector);
        });
      }
    );

    test('Manufacturing process diagrams should have equipment references', () => {
      const manufacturingDir = 'pharma-data-model/diagrams/manufacturing-process';

      if (fs.existsSync(manufacturingDir)) {
        const files = fs.readdirSync(manufacturingDir);
        files.forEach(file => {
          if (file.endsWith('.html')) {
            const filePath = path.join(manufacturingDir, file);
            const content = fs.readFileSync(filePath, 'utf8');
            const $ = cheerio.load(content);
            const mermaidCode = $('.mermaid').first().text();

            // Should contain equipment-related terms
            const equipmentKeywords = [
              'Bioreactor',
              'Tank',
              'Column',
              'Filter',
              'Pump',
              'Sensor',
              'Chromatography',
              'Centrifuge',
              'PAT',
              'MES',
              'DCS',
              'SCADA'
            ];

            const hasEquipmentRef = equipmentKeywords.some(keyword =>
              mermaidCode.includes(keyword)
            );

            // At least some manufacturing files should have equipment references
            if (file.includes('cell-culture') ||
                file.includes('purification') ||
                file.includes('fill-finish')) {
              expect(hasEquipmentRef).toBe(true);
            }
          }
        });
      }
    });

    test('Clinical process diagrams should have clinical trial phases', () => {
      const filePath = 'pharma-data-model/diagrams/clinical-process/01-clinical-trial-lifecycle.html';

      if (fs.existsSync(filePath)) {
        const content = fs.readFileSync(filePath, 'utf8');
        const $ = cheerio.load(content);
        const mermaidCode = $('.mermaid').first().text();

        // Should contain clinical phase references
        const phaseKeywords = ['Phase', 'Trial', 'Clinical', 'Study'];
        const hasPhaseRef = phaseKeywords.some(keyword =>
          mermaidCode.includes(keyword)
        );

        expect(hasPhaseRef).toBe(true);
      }
    });
  });
});
