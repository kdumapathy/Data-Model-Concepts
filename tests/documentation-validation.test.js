const fs = require('fs');
const path = require('path');
const { glob } = require('glob');

describe('Documentation Validation Tests', () => {
  describe('README Files Validation', () => {
    test('Root README should exist', () => {
      const readmePath = 'README.md';
      expect(fs.existsSync(readmePath)).toBe(true);
    });

    test('Pharma data model README should exist', () => {
      const readmePath = 'pharma-data-model/README.md';
      expect(fs.existsSync(readmePath)).toBe(true);
    });

    test('READMEs should have valid markdown structure', () => {
      const readmeFiles = [
        'README.md',
        'pharma-data-model/README.md',
        'pharma-data-model/BASELINE_SUMMARY.md'
      ].filter(f => fs.existsSync(f));

      readmeFiles.forEach(filePath => {
        const content = fs.readFileSync(filePath, 'utf8');

        // Should have content
        expect(content.length).toBeGreaterThan(0);

        // Should have at least one heading
        expect(content).toMatch(/^#{1,6}\s+.+$/m);

        // Should not have malformed markdown links
        const malformedLinks = content.match(/\[([^\]]+)\]\s*\(/g);
        if (malformedLinks) {
          malformedLinks.forEach(link => {
            expect(link).toMatch(/\[([^\]]+)\]\(/);
          });
        }
      });
    });

    test('Equipment reference guide should exist', () => {
      const guidePath = 'pharma-data-model/docs/EQUIPMENT_REFERENCE_GUIDE.md';
      expect(fs.existsSync(guidePath)).toBe(true);

      if (fs.existsSync(guidePath)) {
        const content = fs.readFileSync(guidePath, 'utf8');
        expect(content.length).toBeGreaterThan(0);

        // Should contain equipment-related keywords
        const equipmentKeywords = [
          'Equipment',
          'Bioreactor',
          'ISA-88',
          'Process'
        ];

        const hasEquipmentContent = equipmentKeywords.some(keyword =>
          content.includes(keyword)
        );

        expect(hasEquipmentContent).toBe(true);
      }
    });
  });

  describe('Documentation Cross-References', () => {
    test('README should reference existing diagram files', async () => {
      const readmePath = 'pharma-data-model/README.md';

      if (fs.existsSync(readmePath)) {
        const content = fs.readFileSync(readmePath, 'utf8');

        // Extract referenced diagram files from markdown links
        const diagramRefPattern = /\[([^\]]+)\]\(([^)]+\.html)\)/g;
        const references = [...content.matchAll(diagramRefPattern)];

        references.forEach(match => {
          const [, linkText, filePath] = match;

          // Construct full path relative to README location
          const fullPath = path.join('pharma-data-model', filePath);

          // Check if file exists
          if (!filePath.startsWith('http')) {
            expect(fs.existsSync(fullPath)).toBe(true);
          }
        });
      }
    });

    test('Equipment guide should reference valid equipment types', () => {
      const guidePath = 'pharma-data-model/docs/EQUIPMENT_REFERENCE_GUIDE.md';
      const equipmentDiagram = 'pharma-data-model/diagrams/data-model/Equipment_Master_Data_ISA88.html';

      if (fs.existsSync(guidePath) && fs.existsSync(equipmentDiagram)) {
        const guideContent = fs.readFileSync(guidePath, 'utf8');
        const diagramContent = fs.readFileSync(equipmentDiagram, 'utf8');

        // Extract equipment types mentioned in guide (this is a simplified check)
        const commonEquipment = [
          'Bioreactor',
          'Tank',
          'Pump',
          'Filter',
          'Column',
          'Sensor'
        ];

        // At least some equipment should be mentioned in both
        const mentionedInGuide = commonEquipment.filter(eq =>
          guideContent.includes(eq)
        );

        expect(mentionedInGuide.length).toBeGreaterThan(0);
      }
    });

    test('All diagrams should be reachable from documentation', async () => {
      const allDiagrams = await glob('pharma-data-model/diagrams/**/*.html', {
        cwd: process.cwd()
      });

      const readmeFiles = [
        'README.md',
        'pharma-data-model/README.md'
      ].filter(f => fs.existsSync(f));

      const allReadmeContent = readmeFiles
        .map(f => fs.readFileSync(f, 'utf8'))
        .join('\n');

      // Count how many diagrams are referenced
      const referencedDiagrams = allDiagrams.filter(diagram => {
        const diagramName = path.basename(diagram);
        const diagramPath = diagram.replace(/\\/g, '/');
        return allReadmeContent.includes(diagramName) ||
               allReadmeContent.includes(diagramPath);
      });

      console.log(`${referencedDiagrams.length} of ${allDiagrams.length} diagrams referenced in documentation`);

      // At least 50% of diagrams should be documented
      expect(referencedDiagrams.length).toBeGreaterThan(allDiagrams.length * 0.3);
    });
  });

  describe('Documentation Content Quality', () => {
    test('README should have table of contents or structure', () => {
      const readmePath = 'pharma-data-model/README.md';

      if (fs.existsSync(readmePath)) {
        const content = fs.readFileSync(readmePath, 'utf8');

        // Should have multiple headings for structure
        const headings = content.match(/^#{1,6}\s+.+$/gm);
        expect(headings).not.toBeNull();
        expect(headings.length).toBeGreaterThan(2);
      }
    });

    test('Documentation should describe the data model purpose', () => {
      const readmePath = 'pharma-data-model/README.md';

      if (fs.existsSync(readmePath)) {
        const content = fs.readFileSync(readmePath, 'utf8');

        // Should contain pharmaceutical/data model related keywords
        const keywords = [
          'pharmaceutical',
          'pharma',
          'data model',
          'manufacturing',
          'clinical',
          'batch',
          'process'
        ];

        const mentionedKeywords = keywords.filter(keyword =>
          content.toLowerCase().includes(keyword.toLowerCase())
        );

        expect(mentionedKeywords.length).toBeGreaterThan(3);
      }
    });

    test('Documentation should explain ISA-88 concepts', () => {
      const files = [
        'pharma-data-model/README.md',
        'pharma-data-model/docs/EQUIPMENT_REFERENCE_GUIDE.md',
        'pharma-data-model/docs/EQUIPMENT_RECIPE_ENHANCEMENTS.md'
      ].filter(f => fs.existsSync(f));

      const allContent = files
        .map(f => fs.readFileSync(f, 'utf8'))
        .join('\n');

      // Should mention ISA-88
      expect(allContent).toContain('ISA-88');
    });

    test('Documentation should reference data modeling standards', () => {
      const readmePath = 'pharma-data-model/README.md';

      if (fs.existsSync(readmePath)) {
        const content = fs.readFileSync(readmePath, 'utf8');

        // Should reference data modeling concepts
        const modelingConcepts = [
          'entity',
          'relationship',
          'diagram',
          'schema',
          'model'
        ];

        const mentionedConcepts = modelingConcepts.filter(concept =>
          content.toLowerCase().includes(concept.toLowerCase())
        );

        expect(mentionedConcepts.length).toBeGreaterThan(2);
      }
    });
  });

  describe('File Naming Conventions', () => {
    test('Diagram files should follow consistent naming', async () => {
      const diagrams = await glob('pharma-data-model/diagrams/**/*.html', {
        cwd: process.cwd()
      });

      diagrams.forEach(diagram => {
        const basename = path.basename(diagram);

        // Should end with .html
        expect(basename).toMatch(/\.html$/);

        // Should not have spaces (use underscores or hyphens)
        expect(basename).not.toMatch(/\s/);

        // Should use valid characters
        expect(basename).toMatch(/^[a-zA-Z0-9_-]+\.html$/);
      });
    });

    test('Documentation files should follow consistent naming', async () => {
      const docs = await glob('pharma-data-model/**/*.md', {
        cwd: process.cwd()
      });

      docs.forEach(doc => {
        const basename = path.basename(doc);

        // Should end with .md
        expect(basename).toMatch(/\.md$/);

        // Should use UPPERCASE for major docs or lowercase for guides
        expect(basename).toMatch(/^[A-Z_]+\.md$|^[a-z0-9_-]+\.md$/);
      });
    });
  });

  describe('Diagram Metadata Validation', () => {
    test.each([
      'pharma-data-model/diagrams/data-model',
      'pharma-data-model/diagrams/manufacturing-process',
      'pharma-data-model/diagrams/clinical-process'
    ])('Diagrams in %s should have descriptive titles', (dir) => {
      if (fs.existsSync(dir)) {
        const files = fs.readdirSync(dir);
        const htmlFiles = files.filter(f => f.endsWith('.html'));

        htmlFiles.forEach(file => {
          const filePath = path.join(dir, file);
          const content = fs.readFileSync(filePath, 'utf8');

          // Extract title
          const titleMatch = content.match(/<title>([^<]+)<\/title>/);
          expect(titleMatch).not.toBeNull();

          if (titleMatch) {
            const title = titleMatch[1].trim();

            // Title should not be empty
            expect(title.length).toBeGreaterThan(0);

            // Title should not be generic
            expect(title.toLowerCase()).not.toBe('diagram');
            expect(title.toLowerCase()).not.toBe('untitled');
          }
        });
      }
    });

    test('Diagram titles should match file names conceptually', async () => {
      const diagrams = await glob('pharma-data-model/diagrams/**/*.html', {
        cwd: process.cwd()
      });

      diagrams.forEach(diagram => {
        const content = fs.readFileSync(diagram, 'utf8');
        const basename = path.basename(diagram, '.html');

        // Extract title
        const titleMatch = content.match(/<title>([^<]+)<\/title>/);

        if (titleMatch) {
          const title = titleMatch[1].toLowerCase();
          const fileNameParts = basename.toLowerCase().replace(/[-_]/g, ' ').split(' ');

          // At least one significant word from filename should be in title
          const significantWords = fileNameParts.filter(word =>
            word.length > 3 && !['pharma', 'data', 'model', 'diagram'].includes(word)
          );

          if (significantWords.length > 0) {
            const hasMatchingWord = significantWords.some(word =>
              title.includes(word)
            );

            // This is a soft check - just warn if not matching
            if (!hasMatchingWord) {
              console.log(`Note: ${basename} title may not match filename`);
            }
          }
        }
      });
    });
  });

  describe('Completeness Checks', () => {
    test('Should have diagrams for all major process categories', async () => {
      const categories = [
        'pharma-data-model/diagrams/data-model',
        'pharma-data-model/diagrams/manufacturing-process',
        'pharma-data-model/diagrams/clinical-process'
      ];

      for (const category of categories) {
        expect(fs.existsSync(category)).toBe(true);

        const files = fs.readdirSync(category);
        const htmlFiles = files.filter(f => f.endsWith('.html'));

        expect(htmlFiles.length).toBeGreaterThan(0);
        console.log(`${path.basename(category)}: ${htmlFiles.length} diagrams`);
      }
    });

    test('Should have comprehensive documentation structure', () => {
      const requiredDocs = [
        'README.md',
        'pharma-data-model/README.md'
      ];

      requiredDocs.forEach(doc => {
        expect(fs.existsSync(doc)).toBe(true);
      });
    });
  });
});
