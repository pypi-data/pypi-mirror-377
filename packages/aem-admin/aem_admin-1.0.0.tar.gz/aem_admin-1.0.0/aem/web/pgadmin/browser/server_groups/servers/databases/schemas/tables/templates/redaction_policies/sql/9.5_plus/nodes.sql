-- 오리지날 노드 조회 sql.

-- SELECT
--     pl.oid AS oid,
--     pl.polname AS name
-- FROM
--     pg_catalog.pg_policy pl
-- WHERE
-- {% if tid %}
--     pl.polrelid	 = {{ tid }}
-- {% elif plid %}
--     pl.oid = {{ plid }}
-- {% endif %}
-- ORDER BY
--     pl.polname;

SELECT
    rp.oid AS oid,
    rp.rdname AS name
FROM
    pg_catalog.ag_redaction_policy rp
WHERE
{% if tid %}
    rp.rdrelid	 = {{ tid }}
{% elif rpid %}
    rp.oid = {{ rpid }}
{% endif %}
ORDER BY
    rp.rdname;
