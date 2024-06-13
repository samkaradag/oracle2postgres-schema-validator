/*
Copyright 2022 Google LLC

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
spool &outputdir/opdb__sourcecodedetailed__&v_tag
prompt PKEY|CON_ID|OWNER|NAME|TYPE|NR_LINES|DMA_SOURCE_ID|DMA_MANUAL_ID
WITH vsrc AS (
SELECT :v_pkey AS pkey,
               &v_a_con_id AS con_id,
               owner,
               name,
               TYPE,
               MAX(line)     NR_LINES,
               COUNT(1)      count_total
        FROM   &v_tblprefix._source a
        WHERE  owner NOT IN
@&EXTRACTSDIR/exclude_schemas.sql
        GROUP  BY :v_pkey,
                  &v_a_con_id ,
                  owner,
                  name,
                  TYPE)
SELECT pkey , con_id , owner , name, type , nr_lines,
       :v_dma_source_id AS DMA_SOURCE_ID, :v_manual_unique_id AS DMA_MANUAL_ID
FROM vsrc;
spool off