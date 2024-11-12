SELECT 
COALESCE(i1.object_type, i2.object_type) AS object_type,
CASE WHEN i1.pkey = '<instance_1_id>' THEN i1.object_count ELSE 0  END <instance_1_id>_count,
CASE WHEN i2.pkey = '<instance_2_id>' THEN i2.object_count ELSE 0  END <instance_2_id>_count
FROM  
(SELECT pkey, object_type,count(*) object_count FROM schema_compare.dbobjectnames WHERE  pkey ='<instance_2_id>' AND OWNER = '<instance_2_owner>' group by pkey, object_type) i2
FULL OUTER JOIN
(SELECT pkey, object_type,count(*) object_count  FROM  schema_compare.dbobjectnames WHERE  pkey ='<instance_1_id>' AND OWNER = '<instance_1_owner>'  group by pkey, object_type) i1 
ON i1.OBJECT_TYPE=i2.OBJECT_TYPE;