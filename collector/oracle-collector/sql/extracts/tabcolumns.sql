/*
Copyright 2024 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

spool &outputdir/opdb__columns__&v_tag
prompt PKEY|CON_ID|OWNER|TABLE_NAME|COLUMN_NAME|DATA_TYPE|DATA_LENGTH|DATA_PRECISION|DATA_SCALE|NULLABLE|DMA_SOURCE_ID|DMA_MANUAL_ID

SELECT /*+ USE_HASH(b a) NOPARALLEL */
    :v_pkey AS pkey,
    &v_a_con_id AS con_id,
    a.owner,
    table_name,
    column_name,
    data_type,
    data_length,
    data_precision,
    data_scale,
    nullable,
    :v_dma_source_id AS DMA_SOURCE_ID, :v_manual_unique_id AS DMA_MANUAL_ID
FROM
    &v_tblprefix._tab_columns a
WHERE
    a.owner NOT IN
@&EXTRACTSDIR/exclude_schemas.sql
;
spool off
