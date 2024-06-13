WITH instances AS (
  SELECT DISTINCT PKEY AS instance_id
  FROM <dataset_name>.instances
),

all_objects AS (
  SELECT DISTINCT NAME, TYPE
  FROM <dataset_name>.sourcecodedetailed
  WHERE PKEY IN (SELECT instance_id FROM instances)
),

instance_objects AS (
  SELECT PKEY instance_id, NAME, TYPE
  FROM <dataset_name>.sourcecodedetailed
  WHERE PKEY IN (SELECT instance_id FROM instances)
)

SELECT 
  a.NAME,
  a.TYPE,
  IF(i1.NAME IS NULL, 'Missing', 'Present') AS instance_1_status,
  IF(i2.NAME IS NULL, 'Missing', 'Present') AS instance_2_status
FROM all_objects a
LEFT JOIN instance_objects i1 ON a.NAME = i1.NAME AND a.TYPE = i1.TYPE AND i1.instance_id = '<instance_1_id>'
LEFT JOIN instance_objects i2 ON a.NAME = i2.NAME AND a.TYPE = i2.TYPE AND i2.instance_id = '<instance_2_id>'
WHERE i1.NAME IS NULL OR i2.NAME IS NULL
ORDER BY a.TYPE, a.NAME;