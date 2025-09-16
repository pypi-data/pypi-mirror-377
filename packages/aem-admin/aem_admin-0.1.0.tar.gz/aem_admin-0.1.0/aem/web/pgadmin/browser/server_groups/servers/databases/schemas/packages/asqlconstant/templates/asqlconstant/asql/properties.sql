SELECT  oid,
        varname AS name,
        pg_catalog.format_type(vartype, NULL) as datatype,
        CASE
        WHEN varaccess = '+' THEN 'Public'
        WHEN varaccess = '-' THEN 'Private'
        ELSE 'Unknown' END AS visibility
FROM pg_catalog.pg_variable
WHERE varnamespace = {{pkgid}}::oid
{% if varid %}
AND oid = {{varid}}
{% endif %}
ORDER BY varname
