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
),
instance_counts AS (
    SELECT
        OWNER,
        OBJECT_TYPE,
        MAX(CASE WHEN rn = 1 THEN object_count ELSE NULL END) AS instance_1_count,
        MAX(CASE WHEN rn = 2 THEN object_count ELSE NULL END) AS instance_2_count
    FROM object_counts_with_instance_ids
    GROUP BY OWNER, OBJECT_TYPE
    ORDER BY OWNER, OBJECT_TYPE
)
SELECT * FROM instance_counts i1
WHERE instance_1_count != instance_2_count <schema_filter>;