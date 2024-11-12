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
LEFT JOIN instance_objects i1 ON a.NAME = i1.NAME AND a.TYPE = i1.TYPE AND i1.instance_id = 'instance_1_id'
LEFT JOIN instance_objects i2 ON a.NAME = i2.NAME AND a.TYPE = i2.TYPE AND i2.instance_id = '<instance_2_id>'
WHERE (i1.NAME IS NULL OR i2.NAME IS NULL) 
AND a.OWNER IN ('<instance_1_owner>','<instance_2_owner>') AND coalesce(i1.OWNER,'<instance_1_owner>') = '<instance_1_owner>' AND coalesce(i2.OWNER,'<instance_2_owner>') = '<instance_2_owner>'
ORDER BY a.TYPE, a.NAME;
