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
),
instance_ids AS (
    SELECT
        instance_id,
        ROW_NUMBER() OVER (ORDER BY instance_id) AS rn
    FROM instances
),
object_counts_with_instance_ids AS (
    SELECT
        oc.OWNER,
        oc.OBJECT_TYPE,
        oc.object_count,
        ii.instance_id,
        ii.rn
    FROM object_counts oc
    JOIN instance_ids ii ON oc.instance_id = ii.instance_id
    -- WHERE oc.OBJECT_TYPE NOT IN ('TABLE PARTITION')
)
SELECT
  OWNER,
  OBJECT_TYPE,
  MAX(CASE WHEN instance_id = '<instance_1_id>' THEN object_count ELSE 0 END) AS <instance_1_id>_count,
  MAX(CASE WHEN instance_id = '<instance_2_id>'  THEN object_count ELSE 0 END) AS <instance_2_id>_count
FROM object_counts_with_instance_ids i1 <w_schema_filter>
GROUP BY OWNER, OBJECT_TYPE
ORDER BY OWNER, OBJECT_TYPE;