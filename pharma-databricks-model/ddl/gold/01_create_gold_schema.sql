-- =====================================================
-- Gold Layer Schema Creation
-- Purpose: Business-ready star schemas
-- Author: Pharmaceutical Data Model Implementation
-- Date: 2025-01-17
-- =====================================================

-- Create Gold schema if not exists
CREATE SCHEMA IF NOT EXISTS gold
COMMENT 'Gold layer for business-ready star schemas'
LOCATION 'dbfs:/pharma-model/gold';

-- Set current schema
USE gold;

-- Display confirmation
SELECT 'Gold schema created successfully' AS status;
