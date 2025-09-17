SELECT  oid,
        varname AS name
FROM pg_catalog.pg_variable
WHERE varnamespace = {{pkgid}}::oid
{% if varid %}
AND oid = {{ varid|qtLiteral(conn) }}
{% endif %}
ORDER BY varname
