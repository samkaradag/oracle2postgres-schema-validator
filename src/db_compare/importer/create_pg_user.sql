CREATE SCHEMA IF NOT EXISTS schema_compare;

CREATE TABLE schema_compare.instances
(
  pkey VARCHAR(1000),
  con_id INT
);

CREATE TABLE schema_compare.dbobjectnames
(
  pkey VARCHAR(1000),
  con_id INT,
  owner VARCHAR(1000),
  object_name VARCHAR(1000),
  object_type VARCHAR(1000),
  dma_source_id VARCHAR(1000),
  dma_manual_id VARCHAR(1000)
);

CREATE TABLE schema_compare.sourcecodedetailed
(
  pkey VARCHAR(1000),
  con_id INT,
  owner VARCHAR(1000),
  name VARCHAR(1000),
  type VARCHAR(1000),
  nr_lines INT,
  dma_source_id VARCHAR(1000),
  dma_manual_id VARCHAR(1000)
);

CREATE TABLE schema_compare.views
(
  pkey VARCHAR(1000),
  con_id INT,
  owner VARCHAR(1000),
  view_name VARCHAR(1000),
  dma_source_id VARCHAR(1000),
  dma_manual_id VARCHAR(1000)
);

CREATE TABLE schema_compare.triggers
(
  pkey VARCHAR(1000),
  con_id INT,
  owner VARCHAR(1000),
  trigger_name VARCHAR(1000),
  base_table VARCHAR(1000),
  base_object_type VARCHAR(1000),
  status VARCHAR(1000),
  dma_source_id VARCHAR(1000),
  dma_manual_id VARCHAR(1000)
);

CREATE TABLE schema_compare.indexes
(
  pkey VARCHAR(1000),
  con_id INT,
  owner VARCHAR(1000),
  index_name VARCHAR(1000),
  index_type VARCHAR(1000),
  table_owner VARCHAR(1000),
  table_name VARCHAR(1000),
  uniqueness VARCHAR(1000),
  status VARCHAR(1000),
  num_rows INT,
  dma_source_id VARCHAR(1000),
  dma_manual_id VARCHAR(1000)
);

CREATE TABLE schema_compare.eoj
(
  pkey VARCHAR(1000)
);

CREATE TABLE schema_compare.defines
(
  pkey VARCHAR(1000)
);

CREATE TABLE schema_compare.tableconstraints
(
  pkey VARCHAR(1000),
  con_id INT,
  owner VARCHAR(1000),
  table_name VARCHAR(1000),
  constraint_type VARCHAR(1000),
  constraint_name VARCHAR(1000),
  status VARCHAR(1000)
);

CREATE TABLE schema_compare.columns
(
  pkey VARCHAR(1000),
  con_id INT,
  owner VARCHAR(1000),
  table_name VARCHAR(1000),
  column_name VARCHAR(1000),
  data_type VARCHAR(1000),
  data_length INT,
  data_precision INT,
  data_scale INT,
  nullable BOOL,
  dma_source_id VARCHAR(1000),
  dma_manual_id VARCHAR(1000)
);

