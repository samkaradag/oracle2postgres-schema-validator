WITH instances AS (
  SELECT DISTINCT PKEY AS instance_id
  FROM <dataset_name>.instances
),
all_indexes AS (
  SELECT DISTINCT OWNER, TABLE_NAME, INDEX_NAME, INDEX_TYPE
  FROM <dataset_name>.indexes
  WHERE PKEY IN (SELECT instance_id FROM instances)
),

instance_indexes AS (
  SELECT PKEY instance_id, OWNER, TABLE_NAME, INDEX_NAME
  FROM <dataset_name>.indexes
  WHERE PKEY IN (SELECT instance_id FROM instances)
)

SELECT 
  a.OWNER,
  a.TABLE_NAME,
  a.INDEX_NAME,
  IF(i1.INDEX_NAME IS NULL, 'Missing', 'Present') AS <instance_1_id>_status,
  IF(i2.INDEX_NAME IS NULL, 'Missing', 'Present') AS <instance_2_id>_status
FROM all_indexes a
LEFT JOIN instance_indexes i1 ON a.OWNER = i1.OWNER AND a.TABLE_NAME = i1.TABLE_NAME AND a.INDEX_NAME = i1.INDEX_NAME  AND i1.instance_id = '<instance_1_id>'
LEFT JOIN instance_indexes i2 ON a.OWNER = i2.OWNER AND a.TABLE_NAME = i2.TABLE_NAME AND a.INDEX_NAME = i2.INDEX_NAME  AND i2.instance_id = '<instance_2_id>'
WHERE (i1.INDEX_NAME IS NULL OR i2.INDEX_NAME IS NULL) AND INDEX_TYPE != 'LOB' <a_schema_filter>
ORDER BY a.OWNER, a.TABLE_NAME, a.INDEX_NAME;