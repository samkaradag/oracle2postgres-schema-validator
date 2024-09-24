WITH instances AS (
  SELECT DISTINCT PKEY AS instance_id
  FROM <dataset_name>.instances
),
all_roleprivs AS (
  SELECT DISTINCT GRANTEE, GRANTED_ROLE
  FROM <dataset_name>.roleprivs
  WHERE PKEY IN (SELECT instance_id FROM instances)
),

instance_roleprivs AS (
  SELECT PKEY instance_id, GRANTEE, GRANTED_ROLE
  FROM <dataset_name>.roleprivs
  WHERE PKEY IN (SELECT instance_id FROM instances)
)

SELECT 
  a.GRANTEE,
  a.GRANTED_ROLE,
  IF(i1.GRANTED_ROLE IS NULL, 'Missing', 'Present') AS <instance_1_id>_status,
  IF(i2.GRANTED_ROLE IS NULL, 'Missing', 'Present') AS <instance_2_id>_status
FROM all_roleprivs a
LEFT JOIN instance_roleprivs i1 ON a.GRANTEE = i1.GRANTEE AND a.GRANTED_ROLE = i1.GRANTED_ROLE AND i1.instance_id = '<instance_1_id>'
LEFT JOIN instance_roleprivs i2 ON a.GRANTEE = i2.GRANTEE AND a.GRANTED_ROLE = i2.GRANTED_ROLE AND i2.instance_id = '<instance_2_id>'
WHERE (i1.GRANTED_ROLE IS NULL OR i2.GRANTED_ROLE IS NULL) 
ORDER BY a.GRANTEE, a.GRANTED_ROLE;