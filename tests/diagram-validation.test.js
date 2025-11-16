const fs = require('fs');
const path = require('path');
const { glob } = require('glob');
const cheerio = require('cheerio');

describe('Diagram Validation Tests', () => {
  let diagramFiles = [];

  beforeAll(async () => {
    // Find all HTML diagram files
    diagramFiles = await glob('pharma-data-model/diagrams/**/*.html', {
      cwd: process.cwd()
    });
  });

  test('should find all diagram files', () => {
    expect(diagramFiles.length).toBeGreaterThan(0);
    console.log(`Found ${diagramFiles.length} diagram files`);
  });

  describe('HTML Structure Validation', () => {
    test.each(diagramFiles.map(f => [path.basename(f), f]))(
      'should have valid HTML structure: %s',
      (name, filePath) => {
        const content = fs.readFileSync(filePath, 'utf8');
        const $ = cheerio.load(content);

        // Check basic HTML structure
        expect($('html').length).toBe(1);
        expect($('head').length).toBe(1);
        expect($('body').length).toBe(1);
        expect($('title').length).toBeGreaterThanOrEqual(1);

        // Check for Mermaid script
        const scripts = $('script[src*="mermaid"]');
        expect(scripts.length).toBeGreaterThanOrEqual(1);
      }
    );

    test.each(diagramFiles.map(f => [path.basename(f), f]))(
      'should have zoom controls: %s',
      (name, filePath) => {
        const content = fs.readFileSync(filePath, 'utf8');
        const $ = cheerio.load(content);

        // Check for zoom control container
        expect($('.zoom-controls').length).toBeGreaterThanOrEqual(1);

        // Check for zoom buttons
        expect($('button[onclick*="zoomIn"]').length).toBeGreaterThanOrEqual(1);
        expect($('button[onclick*="zoomOut"]').length).toBeGreaterThanOrEqual(1);
        expect($('button[onclick*="resetZoom"]').length).toBeGreaterThanOrEqual(1);
      }
    );

    test.each(diagramFiles.map(f => [path.basename(f), f]))(
      'should have print button: %s',
      (name, filePath) => {
        const content = fs.readFileSync(filePath, 'utf8');
        const $ = cheerio.load(content);

        // Check for print button
        const printButton = $('button[onclick*="print"]');
        expect(printButton.length).toBeGreaterThanOrEqual(1);
      }
    );
  });

  describe('Mermaid Diagram Validation', () => {
    test.each(diagramFiles.map(f => [path.basename(f), f]))(
      'should contain valid Mermaid diagram code: %s',
      (name, filePath) => {
        const content = fs.readFileSync(filePath, 'utf8');
        const $ = cheerio.load(content);

        // Find all elements with class 'mermaid'
        const mermaidDivs = $('.mermaid');
        expect(mermaidDivs.length).toBeGreaterThanOrEqual(1);

        mermaidDivs.each((i, elem) => {
          const mermaidCode = $(elem).text().trim();
          expect(mermaidCode.length).toBeGreaterThan(0);

          // Check for valid Mermaid diagram types
          const validTypes = [
            'graph',
            'flowchart',
            'erDiagram',
            'classDiagram',
            'stateDiagram',
            'sequenceDiagram',
            'gantt',
            'pie',
            'journey'
          ];

          const hasValidType = validTypes.some(type =>
            mermaidCode.includes(type)
          );
          expect(hasValidType).toBe(true);
        });
      }
    );

    test.each(diagramFiles.map(f => [path.basename(f), f]))(
      'should not have common Mermaid syntax errors: %s',
      (name, filePath) => {
        const content = fs.readFileSync(filePath, 'utf8');
        const $ = cheerio.load(content);

        const mermaidDivs = $('.mermaid');
        mermaidDivs.each((i, elem) => {
          const mermaidCode = $(elem).text();

          // Check for common syntax errors
          // 1. Unmatched brackets
          const openBrackets = (mermaidCode.match(/\{/g) || []).length;
          const closeBrackets = (mermaidCode.match(/\}/g) || []).length;
          const openSquare = (mermaidCode.match(/\[/g) || []).length;
          const closeSquare = (mermaidCode.match(/\]/g) || []).length;
          const openParen = (mermaidCode.match(/\(/g) || []).length;
          const closeParen = (mermaidCode.match(/\)/g) || []).length;

          expect(openBrackets).toBe(closeBrackets);
          expect(openSquare).toBe(closeSquare);
          expect(openParen).toBe(closeParen);

          // 2. Check for unescaped special characters in labels
          // (This is a simplified check - actual parsing would be more complex)
          const lines = mermaidCode.split('\n');
          lines.forEach(line => {
            // Skip comment lines
            if (line.trim().startsWith('%%')) return;

            // Check for common issues in entity relationships
            if (line.includes('||--') || line.includes('}|--') ||
                line.includes('||..') || line.includes('}o--')) {
              // ER relationship line - should have proper format
              expect(line).toMatch(/\w+\s+[\|\}][o\|][-\.]{2}[\|\}][o\|]\s+\w+/);
            }
          });
        });
      }
    );
  });

  describe('CSS and JavaScript Validation', () => {
    test.each(diagramFiles.map(f => [path.basename(f), f]))(
      'should have embedded CSS styles: %s',
      (name, filePath) => {
        const content = fs.readFileSync(filePath, 'utf8');
        const $ = cheerio.load(content);

        const styles = $('style');
        expect(styles.length).toBeGreaterThanOrEqual(1);

        // Check for essential CSS classes
        const cssContent = styles.text();
        expect(cssContent).toContain('zoom-controls');
        expect(cssContent).toContain('diagram-container');
      }
    );

    test.each(diagramFiles.map(f => [path.basename(f), f]))(
      'should have zoom control JavaScript functions: %s',
      (name, filePath) => {
        const content = fs.readFileSync(filePath, 'utf8');

        // Check for zoom functions
        expect(content).toContain('function zoomIn()');
        expect(content).toContain('function zoomOut()');
        expect(content).toContain('function resetZoom()');

        // Check for Mermaid initialization
        expect(content).toContain('mermaid.initialize');
      }
    );

    test.each(diagramFiles.map(f => [path.basename(f), f]))(
      'should have correct print styles: %s',
      (name, filePath) => {
        const content = fs.readFileSync(filePath, 'utf8');
        const $ = cheerio.load(content);

        const styles = $('style');
        const cssContent = styles.text();

        // Check for print media query
        expect(cssContent).toContain('@media print');
      }
    );
  });

  describe('Accessibility Features', () => {
    test.each(diagramFiles.map(f => [path.basename(f), f]))(
      'should have proper button labels: %s',
      (name, filePath) => {
        const content = fs.readFileSync(filePath, 'utf8');
        const $ = cheerio.load(content);

        // Check buttons have text content
        $('button').each((i, elem) => {
          const text = $(elem).text().trim();
          expect(text.length).toBeGreaterThan(0);
        });
      }
    );

    test.each(diagramFiles.map(f => [path.basename(f), f]))(
      'should have meta viewport for responsive design: %s',
      (name, filePath) => {
        const content = fs.readFileSync(filePath, 'utf8');
        const $ = cheerio.load(content);

        const viewport = $('meta[name="viewport"]');
        expect(viewport.length).toBeGreaterThanOrEqual(1);
      }
    );
  });

  describe('File Organization', () => {
    test('should have data-model diagrams in correct directory', async () => {
      const dataModelFiles = await glob(
        'pharma-data-model/diagrams/data-model/*.html',
        { cwd: process.cwd() }
      );
      expect(dataModelFiles.length).toBeGreaterThan(0);
      console.log(`Found ${dataModelFiles.length} data-model diagrams`);
    });

    test('should have manufacturing-process diagrams in correct directory', async () => {
      const manufacturingFiles = await glob(
        'pharma-data-model/diagrams/manufacturing-process/*.html',
        { cwd: process.cwd() }
      );
      expect(manufacturingFiles.length).toBeGreaterThan(0);
      console.log(`Found ${manufacturingFiles.length} manufacturing-process diagrams`);
    });

    test('should have clinical-process diagrams in correct directory', async () => {
      const clinicalFiles = await glob(
        'pharma-data-model/diagrams/clinical-process/*.html',
        { cwd: process.cwd() }
      );
      expect(clinicalFiles.length).toBeGreaterThan(0);
      console.log(`Found ${clinicalFiles.length} clinical-process diagrams`);
    });
  });

  describe('Diagram Content Validation', () => {
    test('ISA-88 Equipment hierarchy should be complete', () => {
      const filePath = 'pharma-data-model/diagrams/data-model/Equipment_Master_Data_ISA88.html';
      if (fs.existsSync(filePath)) {
        const content = fs.readFileSync(filePath, 'utf8');
        const $ = cheerio.load(content);
        const mermaidCode = $('.mermaid').first().text();

        // Check for ISA-88 hierarchy levels
        const expectedLevels = [
          'Enterprise',
          'Site',
          'Area',
          'Process_Cell',
          'Unit',
          'Equipment_Module',
          'Control_Module'
        ];

        expectedLevels.forEach(level => {
          expect(mermaidCode).toContain(level);
        });
      }
    });

    test('Star Schema diagrams should have fact and dimension tables', () => {
      const starSchemaFiles = [
        'pharma-data-model/diagrams/data-model/Pharma_Data_Model_Diagram_5_Process_Star_Schema.html',
        'pharma-data-model/diagrams/data-model/Pharma_Data_Model_Diagram_6_Analytical_Star_Schema.html'
      ];

      starSchemaFiles.forEach(filePath => {
        if (fs.existsSync(filePath)) {
          const content = fs.readFileSync(filePath, 'utf8');
          const $ = cheerio.load(content);
          const mermaidCode = $('.mermaid').first().text();

          // Check for fact table indicators
          expect(mermaidCode.toLowerCase()).toMatch(/fact|dim_/i);
        }
      });
    });
  });
});
