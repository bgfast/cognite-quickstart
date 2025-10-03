SELECT
  CAST(w.externalId AS STRING) AS externalId,
  CAST(w.title AS STRING) AS name,
  CAST(w.plannedStart AS TIMESTAMP) AS scheduledStartTime,
  CAST(FROM_UNIXTIME(CAST(w.endTime AS BIGINT) / 1000) AS TIMESTAMP) AS endTime,
  CAST(FROM_UNIXTIME(CAST(w.startTime AS BIGINT) / 1000) AS TIMESTAMP) AS startTime,
  CAST(w.description AS STRING) AS description,
  SLICE(
    COLLECT_LIST(node_reference('valhall-assets', CAST(a.targetExternalId AS STRING))),
    1, 100
  ) AS assets
FROM
  `workorder_{{default_location}}_{{source_asset}}`.`workorders` AS w
LEFT JOIN
  `workorder_{{default_location}}_{{source_asset}}`.`workorder2assets` AS a
ON
  w.externalId = a.sourceExternalId
GROUP BY
  w.externalId, w.title, w.plannedStart, w.endTime, w.startTime, w.description;
