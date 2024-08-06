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

set termout on pause on
SET DEFINE "&"
DEFINE SQLDIR=&2
DEFINE v_tag=&3
DEFINE outputdir=&4
DEFINE v_manualUniqueId=&5

DEFINE EXTRACTSDIR=&SQLDIR/extracts
DEFINE TERMOUTOFF=OFF
prompt
prompt ***********************************************************************************
prompt
prompt !!! ATTENTION !!!
prompt
prompt
prompt
prompt ***********************************************************************************
prompt

prompt Initializing Database Schema Validation Collector...
prompt
set termout &TERMOUTOFF
@@op_collect_init.sql
set termout on
prompt
prompt Initialization completed.
prompt
prompt Collecting Database Schema Validation data...
prompt

set termout &TERMOUTOFF
-- @&EXTRACTSDIR/dbobjects.sql
@&EXTRACTSDIR/dbobjectnames.sql
-- @&EXTRACTSDIR/sourcecode.sql
@&EXTRACTSDIR/sourcecode_detailed.sql
@&EXTRACTSDIR/tableconstraints.sql
@&EXTRACTSDIR/triggers.sql
@&EXTRACTSDIR/indexes.sql
@&EXTRACTSDIR/instances.sql
-- @&EXTRACTSDIR/roleprivs.sql
-- @&EXTRACTSDIR/roles.sql
-- @&EXTRACTSDIR/sysprivs.sql
@&EXTRACTSDIR/tabcolumns.sql
-- @&EXTRACTSDIR/tabprivs.sql
-- @&EXTRACTSDIR/users.sql
@&EXTRACTSDIR/eoj.sql

set termout on
prompt Step completed.
prompt
prompt Database Schema Validation data successfully extracted.
prompt
exit