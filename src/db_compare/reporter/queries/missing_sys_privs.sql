WITH instances AS (
  SELECT DISTINCT PKEY AS instance_id
  FROM <dataset_name>.instances
),
all_sysprivs AS (
  SELECT DISTINCT GRANTEE, PRIVILEGE
  FROM <dataset_name>.sysprivs
  WHERE PKEY IN (SELECT instance_id FROM instances)
),

instance_sysprivs AS (
  SELECT PKEY instance_id, GRANTEE, PRIVILEGE
  FROM <dataset_name>.sysprivs
  WHERE PKEY IN (SELECT instance_id FROM instances)
)

SELECT 
  a.GRANTEE,
  a.PRIVILEGE,
  IF(i1.PRIVILEGE IS NULL, 'Missing', 'Present') AS <instance_1_id>_status,
  IF(i2.PRIVILEGE IS NULL, 'Missing', 'Present') AS <instance_2_id>_status
FROM all_sysprivs a
LEFT JOIN instance_sysprivs i1 ON a.GRANTEE = i1.GRANTEE AND a.PRIVILEGE = i1.PRIVILEGE AND i1.instance_id = '<instance_1_id>'
LEFT JOIN instance_sysprivs i2 ON a.GRANTEE = i2.GRANTEE AND a.PRIVILEGE = i2.PRIVILEGE AND i2.instance_id = '<instance_2_id>'
WHERE (i1.PRIVILEGE IS NULL OR i2.PRIVILEGE IS NULL) 
ORDER BY a.GRANTEE, a.PRIVILEGE;