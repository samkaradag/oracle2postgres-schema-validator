WITH instances AS (
  SELECT DISTINCT PKEY AS instance_id
  FROM <dataset_name>.dbobjectnames
),
all_objects AS (
  SELECT DISTINCT OWNER, OBJECT_NAME, OBJECT_TYPE
  FROM <dataset_name>.dbobjectnames
  WHERE PKEY IN (SELECT instance_id FROM instances)
),
instance_objects AS (
  SELECT PKEY instance_id, OWNER, OBJECT_NAME, OBJECT_TYPE
  FROM <dataset_name>.dbobjectnames
  WHERE PKEY IN (SELECT instance_id FROM instances)
),
instance_ids AS (
  SELECT instance_id, ROW_NUMBER() OVER (ORDER BY instance_id) AS rn
  FROM instances
)
SELECT 
  a.OWNER,
  a.OBJECT_NAME,
  a.OBJECT_TYPE,
  CASE WHEN i1.OBJECT_NAME IS NULL THEN 'Missing' ELSE 'Present' END AS <instance_1_id>_status,
  CASE WHEN i2.OBJECT_NAME IS NULL THEN 'Missing' ELSE 'Present' END AS <instance_2_id>_status
FROM all_objects a
LEFT JOIN instance_objects i1 ON a.OBJECT_NAME = i1.OBJECT_NAME AND a.OBJECT_TYPE = i1.OBJECT_TYPE AND i1.instance_id = 'instance_1_id'
LEFT JOIN instance_objects i2 ON a.OBJECT_NAME = i2.OBJECT_NAME AND a.OBJECT_TYPE = i2.OBJECT_TYPE  AND i2.instance_id = '<instance_2_id>'
WHERE (i1.OBJECT_NAME IS NULL OR i2.OBJECT_NAME IS NULL) 
AND a.OWNER IN ('<instance_1_owner>','<instance_2_owner>') AND coalesce(i1.OWNER,'<instance_1_owner>') = '<instance_1_owner>' AND coalesce(i2.OWNER,'<instance_2_owner>') = '<instance_2_owner>'
ORDER BY a.OBJECT_TYPE, a.OBJECT_NAME;
