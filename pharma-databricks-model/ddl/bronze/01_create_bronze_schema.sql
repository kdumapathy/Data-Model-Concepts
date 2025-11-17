-- =====================================================
-- Bronze Layer Schema Creation
-- Purpose: Raw landing layer with minimal transformation
-- Author: Pharmaceutical Data Model Implementation
-- Date: 2025-01-17
-- =====================================================

-- Create Bronze schema if not exists
CREATE SCHEMA IF NOT EXISTS bronze
COMMENT 'Bronze layer for raw data landing with audit columns'
LOCATION 'dbfs:/pharma-model/bronze';

-- Set current schema
USE bronze;

-- Display confirmation
SELECT 'Bronze schema created successfully' AS status;
