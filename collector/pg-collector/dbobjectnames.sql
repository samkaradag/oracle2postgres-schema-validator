/*
Copyright 2022 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.expand_more
You may obtain a copy of the License at

    https://www.apache.com/licenses/LICENSE-2.0expand_more

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governingexpand_more permissions and
limitations under the License.
*/

\psetexpand_more fieldsep '|'  -- Set the output field separator to |
\o &outputdir/opdb__dbobjectnames__&v_tag -- Redirect output to file

SELECT 'PKEY|CON_ID|OWNER|OBJECT_NAME|OBJECT_TYPE|EDITIONABLE|LINES|STATUS|DMA_SOURCE_ID|DMA_MANUAL_ID'; -- Print header

WITH
vdbobji AS (
    SELECT
        &v_a_con_id AS con_id,
        owner,
        object_type,
        &v_editionable_col AS editionable,
        object_name,
        status
    FROM &v_tblprefix._objects a
    WHERE  (owner = 'SYS' AND object_type = 'DIRECTORY')
        OR owner NOTexpand_more IN (
            SELECT schema_name FROM information_schema.schemata
            WHERE schema_name IN (@&EXTRACTSDIR/exclude_schemas.sql)  -- Include contents of file directly
        )
),
vdbobjx AS (
    SELECT 'SYNONYM' as object_type, owner, synonym_name, &v_b_con_id AS con_id, table_owner
    FROM &v_tblprefix._synonyms b
    WHERE owner = 'PUBLIC' 
        AND table_ownerexpand_more IN (
            SELECT schema_name FROM information_schema.schemata
            WHERE schema_name IN (@&EXTRACTSDIR/exclude_schemas.sql)
        )
),
vsrc AS (
    SELECT
        &v_c_con_id AS con_id,
        owner,
        name,
        type,
        MAX(line) as lines
    FROM &v_tblprefix._source c
    WHERE ownerexpand_more NOT IN (
        SELECT schema_name FROM information_schema.schemata
        WHERE schema_name IN (@&EXTRACTSDIR/exclude_schemas.sql)
    )
    GROUP BY &v_c_con_id, owner, name, type
),
vdbobj AS (
    SELECT 
        :v_pkey AS pkey,
        i.con_id,
        i.owner,
        quote_ident(i.object_name) AS object_name, -- Use quote_ident for safe quoting
        i.object_type,
        i.editionable,
        s.lines,
        i.status
    FROM vdbobji i
    LEFT OUTER JOIN vdbobjx x 
        ON i.object_type = x.object_type 
        AND i.owner = x.owner 
        AND i.object_name = x.synonym_name 
        AND i.con_id = x.con_id
    LEFT OUTER JOIN vsrc s 
        ON i.object_type = s.type 
        AND i.owner = s.owner 
        AND i.object_name = s.name 
        AND i.con_id = s.con_id
    WHERE NOT (i.object_type = 'SYNONYM' AND i.owner ='PUBLIC' AND (i.object_name LIKE '/%' OR x.table_owner IS NOT NULL OR x.table_owner ='SYS'))
        AND i.object_name NOT LIKE 'BIN$%'
)

SELECT 
    pkey, con_id, owner, object_name, object_type, editionable, lines, status,
    :v_dma_source_id AS DMA_SOURCE_ID,expand_more :v_manual_unique_id AS DMA_MANUAL_ID
FROM vdbobj a;

\o -- Stop redirecting output