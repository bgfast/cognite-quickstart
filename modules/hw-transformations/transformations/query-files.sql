-- Query CogniteFile instances in the app-packages space
-- This is an example of reading data from data models using transformations
-- 
-- Use case: List all files in a specific space with their metadata
-- 
-- Data Model: CogniteCore (cdf_cdm space)
-- View: CogniteFile
-- Version: v1

SELECT 
    externalId,
    name,
    uploaded,
    uploadedTime,
    mimeType,
    space
FROM cdf_data_models("cdf_cdm", "CogniteCore", "v1", "CogniteFile")
WHERE space = 'app-packages'
ORDER BY name;
