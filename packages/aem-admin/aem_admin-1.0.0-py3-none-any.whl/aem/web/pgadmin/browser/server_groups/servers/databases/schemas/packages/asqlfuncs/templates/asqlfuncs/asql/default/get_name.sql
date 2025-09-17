SELECT  proname AS name
FROM pg_catalog.pg_proc
WHERE oid = {{asqlfnid}}::oid
