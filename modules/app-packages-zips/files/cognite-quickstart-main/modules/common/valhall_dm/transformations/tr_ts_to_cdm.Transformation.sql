SELECT
  CAST(regexp_replace(t2.timeseries, '_', ':', 1) AS STRING) AS externalId,
  ARRAY(node_reference('valhall-assets', CAST(t2.asset AS STRING))) AS assets,
  CAST(t1.`type` AS STRING) AS type,
  CAST(t1.`isStep` AS BOOLEAN) AS isStep
FROM
  cdf_data_models("cdf_cdm", "CogniteCore", "v1", "CogniteTimeSeries") t1
JOIN
  `timeseries_valhall_fileshare`.`timeseries2assets` t2
ON
  t1.externalId = regexp_replace(t2.timeseries, '_', ':', 1);
