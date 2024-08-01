Please replace oracle_db_user with your database user.

Option 1:
Grant select any dictionary to oracle_db_user;

Option 2:
GRANT SELECT ON dba_objects TO <db_user>;
GRANT SELECT ON dba_synonyms TO <db_user>;
GRANT SELECT ON dba_source TO <db_user>;
GRANT SELECT ON dba_indexes TO <db_user>;
GRANT SELECT ON dba_users TO <db_user>;
GRANT SELECT ON dba_role_privs TO <db_user>;
GRANT SELECT ON dba_roles TO <db_user>;
GRANT SELECT ON dba_triggers TO <db_user>;
GRANT SELECT ON dba_tab_columns TO <db_user>;
GRANT SELECT ON dba_tables TO <db_user>;
GRANT SELECT ON dba_constraints TO <db_user>;
GRANT SELECT ON dba_tab_privs TO <db_user>;
GRANT SELECT ON dba_sys_privs TO <db_user>;