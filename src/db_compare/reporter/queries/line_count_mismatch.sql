WITH instances AS (
  SELECT DISTINCT PKEY AS instance_id
  FROM <dataset_name>.sourcecode
),

line_counts AS (
  SELECT
    PKEY as instance_id,
    OWNER,
    TYPE,
    SUM_NR_LINES 
  FROM <dataset_name>.sourcecode
  WHERE PKEY IN (SELECT instance_id FROM instances)
)

SELECT * FROM (
  SELECT
    OWNER,
    TYPE,
    MAX(IF(instance_id = (SELECT instance_id FROM instances LIMIT 1 OFFSET 0), SUM_NR_LINES, NULL)) AS <instance_1_id>_line_count,
    MAX(IF(instance_id = (SELECT instance_id FROM instances LIMIT 1 OFFSET 1), SUM_NR_LINES, NULL)) AS <instance_2_id>_line_count
    -- Add more columns for additional instances as needed
  FROM line_counts i1
  GROUP BY OWNER, TYPE
  ORDER BY OWNER, TYPE)
WHERE <instance_1_id>_line_count != <instance_2_id>_line_count <schema_filter>
;