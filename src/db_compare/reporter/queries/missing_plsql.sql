WITH instances AS (
  SELECT DISTINCT PKEY AS instance_id
  FROM <dataset_name>.instances
),
all_objects AS (
  SELECT DISTINCT OWNER, NAME, TYPE
  FROM <dataset_name>.sourcecodedetailed
  WHERE PKEY IN (SELECT instance_id FROM instances)
),
instance_objects AS (
  SELECT PKEY instance_id, OWNER, NAME, TYPE
  FROM <dataset_name>.sourcecodedetailed
  WHERE PKEY IN (SELECT instance_id FROM instances)
),
instance_ids AS (
  SELECT instance_id, ROW_NUMBER() OVER (ORDER BY instance_id) AS rn
  FROM instances
)
SELECT 
  a.OWNER,
  a.NAME,
  a.TYPE,
  CASE WHEN i1.NAME IS NULL THEN 'Missing' ELSE 'Present' END AS <instance_1_id>_status,
  CASE WHEN i2.NAME IS NULL THEN 'Missing' ELSE 'Present' END AS <instance_2_id>_status
FROM all_objects a
LEFT JOIN instance_objects i1 ON a.OWNER = i1.OWNER AND a.NAME = i1.NAME AND a.TYPE = i1.TYPE AND i1.instance_id = '<instance_1_id>'
LEFT JOIN instance_objects i2 ON a.OWNER = i2.OWNER AND a.NAME = i2.NAME AND a.TYPE = i2.TYPE AND i2.instance_id = '<instance_2_id>'
WHERE (i1.NAME IS NULL OR i2.NAME IS NULL) <a_schema_filter>
ORDER BY a.TYPE, a.NAME;