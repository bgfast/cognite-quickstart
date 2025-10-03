SELECT
CAST(`externalId` AS STRING) AS externalId,
CAST(`tag` AS STRING) AS name,
CAST(`description` AS STRING) AS description,
CASE 
  WHEN TRIM(parentExternalId) = '' OR parentExternalId IS NULL THEN NULL 
  ELSE node_reference('valhall-assets', parentExternalId)
END AS parent
FROM
  `asset_valhall_workmate`.`assets`;