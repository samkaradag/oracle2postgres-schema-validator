WITH instances AS (
  SELECT DISTINCT PKEY AS instance_id
  FROM <dataset_name>.sourcecodedetailed
),

line_counts AS (
  SELECT
    PKEY as instance_id,
    OWNER,
    NAME,
    TYPE,
    NR_LINES 
  FROM <dataset_name>.sourcecodedetailed
  WHERE PKEY IN (SELECT instance_id FROM instances)
)

SELECT * FROM (
  SELECT
    OWNER,
    NAME,
    TYPE,
    MAX(IF(instance_id = (SELECT instance_id FROM instances LIMIT 1 OFFSET 0), NR_LINES, NULL)) AS <instance_1_id>_line_count,
    MAX(IF(instance_id = (SELECT instance_id FROM instances LIMIT 1 OFFSET 1), NR_LINES, NULL)) AS <instance_2_id>_line_count
    -- Add more columns for additional instances as needed
  FROM line_counts i1
  GROUP BY OWNER, TYPE, NAME
  ORDER BY OWNER, TYPE, NAME)
WHERE <instance_1_id>_line_count != <instance_2_id>_line_count <schema_filter>
;