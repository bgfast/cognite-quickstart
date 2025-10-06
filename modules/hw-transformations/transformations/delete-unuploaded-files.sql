-- Delete CogniteFile instances that have isUploaded = false
-- This is an example of using transformations to clean up data model instances
-- 
-- Use case: Remove file instances that failed to upload or are in an incomplete state
-- 
-- Data Model: CogniteCore (cdf_cdm space)
-- View: CogniteFile
-- Version: v1
-- Target Space: app-packages

SELECT 
    externalId,
    name,
    space
FROM cdf_data_models("cdf_cdm", "CogniteCore", "v1", "CogniteFile")
WHERE space = 'app-packages'
  AND isUploaded = false
ORDER BY name;
