SELECT 
  i1.OWNER,
  i1.TABLE_NAME,
  i1.COLUMN_NAME,
  i1.DATA_TYPE <instance_1_id>_data_type,
  i2.DATA_TYPE <instance_2_id>_data_type,
  i1.DATA_LENGTH <instance_1_id>_data_length,
  i2.DATA_LENGTH <instance_2_id>_data_length,
  i1.DATA_PRECISION <instance_1_id>_data_precision,
  i2.DATA_PRECISION <instance_2_id>_data_precision,
  i1.NULLABLE <instance_1_id>_nullable,
  i2.NULLABLE <instance_2_id>_nullable
FROM <dataset_name>.columns i1
JOIN <dataset_name>.columns i2 ON i1.OWNER = i2.OWNER AND i1.TABLE_NAME = i2.TABLE_NAME AND i1.COLUMN_NAME = i2.COLUMN_NAME AND (i1.DATA_TYPE != i2.DATA_TYPE or i1.DATA_LENGTH != i2.DATA_LENGTH or i1.DATA_PRECISION != i2.DATA_PRECISION or i1.DATA_SCALE != i2.DATA_SCALE  or i1.NULLABLE != i2.NULLABLE )  AND i2.PKEY = '<instance_2_id>'
WHERE i1.PKEY = '<instance_1_id>' <schema_filter>
ORDER BY i1.OWNER, i1.TABLE_NAME, i1.COLUMN_NAME;