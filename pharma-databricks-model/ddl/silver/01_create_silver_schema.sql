-- =====================================================
-- Silver Layer Schema Creation
-- Purpose: Validated and conformed data with SCD Type 2
-- Author: Pharmaceutical Data Model Implementation
-- Date: 2025-01-17
-- =====================================================

-- Create Silver schema if not exists
CREATE SCHEMA IF NOT EXISTS silver
COMMENT 'Silver layer for validated and conformed data with SCD Type 2'
LOCATION 'dbfs:/pharma-model/silver';

-- Set current schema
USE silver;

-- Display confirmation
SELECT 'Silver schema created successfully' AS status;
