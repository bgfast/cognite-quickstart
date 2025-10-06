-- Delete files from the app-packages space that are not uploaded
-- This queries the CogniteFile view in the cdf_cdm data model

-- First, let's see what files exist
SELECT 
    externalId,
    name,
    uploaded,
    uploadedTime,
    space
FROM cdf_data_models("cdf_cdm", "CogniteFile", "v1")
WHERE space = 'app-packages'
ORDER BY name;

-- To delete specific files, you would need to use the SDK or UI
-- Transformations can only SELECT, not DELETE from data models

-- However, you can identify which files to delete:
-- Files with uploaded = false or duplicate names
SELECT 
    externalId,
    name,
    uploaded,
    uploadedTime
FROM cdf_data_models("cdf_cdm", "CogniteFile", "v1")
WHERE space = 'app-packages'
  AND (uploaded = false OR name LIKE '%cognite-samples-main-mini.zip%')
ORDER BY name, uploadedTime;
