WITH instances AS (
  SELECT DISTINCT PKEY AS instance_id
  FROM <dataset_name>.dbobjectnames
),

all_objects AS (
  SELECT DISTINCT OBJECT_NAME, OBJECT_TYPE
  FROM <dataset_name>.dbobjectnames
  WHERE PKEY IN (SELECT instance_id FROM instances)
),

instance_objects AS (
  SELECT PKEY instance_id, OBJECT_NAME, OBJECT_TYPE
  FROM <dataset_name>.dbobjectnames
  WHERE PKEY IN (SELECT instance_id FROM instances)
)

SELECT 
  a.OBJECT_NAME,
  a.OBJECT_TYPE,
  IF(i1.OBJECT_NAME IS NULL, 'Missing', 'Present') AS instance_1_status,
  IF(i2.OBJECT_NAME IS NULL, 'Missing', 'Present') AS instance_2_status
FROM all_objects a
LEFT JOIN instance_objects i1 ON a.OBJECT_NAME = i1.OBJECT_NAME AND a.OBJECT_TYPE = i1.OBJECT_TYPE AND i1.instance_id = '<instance_1_id>'
LEFT JOIN instance_objects i2 ON a.OBJECT_NAME = i2.OBJECT_NAME AND a.OBJECT_TYPE = i2.OBJECT_TYPE AND i2.instance_id = '<instance_2_id>'
WHERE i1.OBJECT_NAME IS NULL OR i2.OBJECT_NAME IS NULL
ORDER BY a.OBJECT_TYPE, a.OBJECT_NAME;