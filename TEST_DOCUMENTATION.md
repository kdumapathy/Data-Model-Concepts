# Test Documentation - Pharmaceutical Data Model

## Overview

This test suite validates the integrity, consistency, and quality of pharmaceutical data model diagrams and documentation in this repository.

## Test Categories

### 1. Diagram Validation Tests (`tests/diagram-validation.test.js`)

#### HTML Structure Validation
- ✅ Validates proper HTML5 structure (html, head, body tags)
- ✅ Checks for required meta tags and viewport settings
- ✅ Verifies Mermaid.js library is loaded from CDN
- ✅ Ensures zoom controls are present and accessible
- ✅ Confirms print button functionality

#### Mermaid Diagram Validation
- ✅ Verifies valid Mermaid diagram syntax
- ✅ Checks for supported diagram types (erDiagram, graph, flowchart, etc.)
- ✅ Validates bracket matching (curly braces, square brackets, parentheses)
- ✅ Checks entity relationship syntax (||--||, }|--|{, etc.)
- ✅ Ensures proper diagram code structure

#### CSS and JavaScript Validation
- ✅ Validates embedded CSS styles are present
- ✅ Checks for zoom control functions (zoomIn, zoomOut, resetZoom)
- ✅ Verifies Mermaid initialization code
- ✅ Ensures print media queries are defined
- ✅ Validates CSS classes for diagram containers

#### Accessibility Features
- ✅ Checks button labels for screen readers
- ✅ Validates responsive design meta tags
- ✅ Ensures proper interactive controls

#### File Organization
- ✅ Verifies diagrams are in correct directories
- ✅ Validates file naming conventions
- ✅ Confirms proper category organization

#### Diagram Content Validation
- ✅ ISA-88 equipment hierarchy completeness check
- ✅ Star schema fact and dimension table validation
- ✅ Entity relationship integrity checks

### 2. Model Relationship Validation Tests (`tests/model-validation.test.js`)

#### Entity Relationship Diagram Validation
- ✅ Validates ER diagram syntax and relationships
- ✅ Checks entity naming conventions (PascalCase, snake_case)
- ✅ Verifies attribute definitions in entities
- ✅ Validates relationship cardinality syntax

#### ISA-88 Hierarchy Validation
- ✅ Confirms all 7 levels of ISA-88 hierarchy are present:
  - Enterprise → Site → Area → Process Cell → Unit → Equipment Module → Control Module
- ✅ Validates hierarchical relationships between levels

#### Batch Genealogy Validation
- ✅ Verifies material traceability entities are present
- ✅ Checks for batch-related data structures

#### Star Schema Validation
- ✅ Process Star Schema: validates fact and dimension tables
- ✅ Analytical Star Schema: confirms analytical entities
- ✅ Checks for proper Kimball methodology implementation

#### Data Model Consistency
- ✅ Validates consistent entity naming across diagrams
- ✅ Identifies shared entities across multiple diagrams
- ✅ Ensures model coherence

#### Process Flow Validation
- ✅ Validates flowchart node connections
- ✅ Checks for valid connector syntax (-->, ---, -.->)
- ✅ Verifies manufacturing process equipment references
- ✅ Confirms clinical trial phase workflows

### 3. Documentation Validation Tests (`tests/documentation-validation.test.js`)

#### README Files Validation
- ✅ Verifies existence of root and project READMEs
- ✅ Validates markdown structure and formatting
- ✅ Checks for malformed markdown links

#### Documentation Cross-References
- ✅ Validates links to diagram files from README
- ✅ Checks equipment guide references match diagrams
- ✅ Ensures all diagrams are reachable from documentation

#### Content Quality Checks
- ✅ Verifies presence of table of contents or structure
- ✅ Confirms pharmaceutical and data modeling keywords
- ✅ Validates ISA-88 concept explanations
- ✅ Checks for data modeling standard references

#### File Naming Conventions
- ✅ Validates consistent diagram file naming
- ✅ Checks documentation file naming standards
- ✅ Ensures no spaces in filenames

#### Diagram Metadata Validation
- ✅ Verifies HTML title tags are descriptive
- ✅ Checks title-filename alignment
- ✅ Ensures no generic titles (e.g., "Untitled")

#### Completeness Checks
- ✅ Confirms diagrams exist for all major categories
- ✅ Validates comprehensive documentation structure

## Running Tests

### Prerequisites

```bash
# Install Node.js 18.x or 20.x
node --version  # Should be v18.x or v20.x

# Install dependencies
npm install
```

### Run All Tests

```bash
# Run tests with verbose output
npm test

# Run tests with coverage report
npm run test:ci
```

### Run Specific Test Suites

```bash
# Run only diagram validation tests
npx jest tests/diagram-validation.test.js

# Run only model validation tests
npx jest tests/model-validation.test.js

# Run only documentation validation tests
npx jest tests/documentation-validation.test.js
```

### Run Tests in Watch Mode (for development)

```bash
npx jest --watch
```

## GitHub Actions Integration

This repository uses GitHub Actions to automatically run tests on:
- Every push to main/master branches
- Every push to branches starting with 'claude/'
- Every pull request
- Manual workflow dispatch

### Workflow Jobs

1. **validate-diagrams**: Runs full test suite on Node.js 18.x and 20.x
2. **diagram-analysis**: Generates statistics and diagram inventory
3. **security-scan**: Runs npm audit for dependency vulnerabilities

### Viewing Results

GitHub Actions results are available in:
- **Actions Tab**: Full test logs and results
- **Pull Request Comments**: Automated test summary for PRs
- **Job Summary**: Quick overview of test results and statistics

## Test Statistics

### Current Coverage

- **Total Diagrams**: 21 HTML files
  - Data Model: 16 diagrams
  - Manufacturing Process: 3 diagrams
  - Clinical Process: 2 diagrams

- **Total Tests**: 50+ test cases across 3 test suites
  - Diagram Validation: ~25 tests
  - Model Validation: ~15 tests
  - Documentation Validation: ~15 tests

### Test Execution Time

- Average test run: ~5-10 seconds
- Full CI pipeline: ~2-3 minutes

## Interpreting Test Results

### Success Indicators

```
PASS  tests/diagram-validation.test.js
PASS  tests/model-validation.test.js
PASS  tests/documentation-validation.test.js

Test Suites: 3 passed, 3 total
Tests:       50 passed, 50 total
```

### Common Failure Scenarios

1. **Missing Mermaid diagram**: Check that `<div class="mermaid">` exists
2. **Bracket mismatch**: Verify matching braces, brackets, parentheses
3. **Invalid relationship syntax**: Ensure ER relationships use valid cardinality notation
4. **Broken documentation links**: Verify referenced files exist
5. **Missing zoom controls**: Confirm zoom buttons are outside diagram containers

## Extending the Tests

### Adding New Test Cases

1. Navigate to appropriate test file:
   - Diagram structure → `tests/diagram-validation.test.js`
   - Data model logic → `tests/model-validation.test.js`
   - Documentation → `tests/documentation-validation.test.js`

2. Add new test within relevant `describe` block:

```javascript
test('should validate new requirement', () => {
  // Your test logic here
  expect(actual).toBe(expected);
});
```

3. Run tests to verify:

```bash
npm test
```

### Adding New Test Suites

1. Create new test file in `tests/` directory:

```bash
touch tests/new-validation.test.js
```

2. Import required dependencies:

```javascript
const fs = require('fs');
const path = require('path');
const cheerio = require('cheerio');
```

3. Create test structure:

```javascript
describe('New Validation Tests', () => {
  test('should validate something', () => {
    // Test logic
  });
});
```

## Continuous Improvement

This test suite is designed to evolve with the repository. As new diagrams are added or requirements change, tests should be updated accordingly.

### Maintenance Checklist

- [ ] Update tests when adding new diagram categories
- [ ] Review test coverage monthly
- [ ] Update documentation when adding new test types
- [ ] Monitor GitHub Actions for failures
- [ ] Keep dependencies updated (npm audit)

## Support

For issues or questions about the test suite:
1. Check existing test output for error messages
2. Review this documentation
3. Check GitHub Actions logs for detailed failure information
4. Review individual test files for test logic

## Version History

- **v1.0.0** (2025-11-16): Initial test suite creation
  - Diagram validation tests
  - Model relationship tests
  - Documentation validation tests
  - GitHub Actions integration
