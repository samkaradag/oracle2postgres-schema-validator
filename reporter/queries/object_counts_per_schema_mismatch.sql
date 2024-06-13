WITH instances AS (
  SELECT DISTINCT PKEY AS instance_id
  FROM <dataset_name>.dbobjectnames
),

object_counts AS (
  SELECT
    PKEY as instance_id,
    OWNER,
    OBJECT_TYPE,
    COUNT(*) AS object_count
  FROM <dataset_name>.dbobjectnames
  WHERE PKEY IN (SELECT instance_id FROM instances)
  GROUP BY instance_id, OWNER, OBJECT_TYPE
)

SELECT * FROM (
  SELECT
    OWNER,
    OBJECT_TYPE,
    MAX(IF(instance_id = (SELECT instance_id FROM instances LIMIT 1 OFFSET 0), object_count, NULL)) AS instance_1_count,
    MAX(IF(instance_id = (SELECT instance_id FROM instances LIMIT 1 OFFSET 1), object_count, NULL)) AS instance_2_count
    -- Add more columns for additional instances as needed
  FROM object_counts
  GROUP BY OWNER, OBJECT_TYPE
  ORDER BY OWNER, OBJECT_TYPE)
WHERE instance_1_count != instance_2_count
;