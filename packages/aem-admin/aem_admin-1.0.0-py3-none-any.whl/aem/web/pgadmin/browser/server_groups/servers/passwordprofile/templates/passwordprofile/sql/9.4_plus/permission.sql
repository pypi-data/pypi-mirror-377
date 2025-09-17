-- SELECT
--     rolname, rolcanlogin, rolsuper AS rolcatupdate, rolsuper
-- FROM
--     pg_catalog.pg_roles
-- WHERE oid = {{ rid }}::OID


SELECT
    r.rolname, r.rolcanlogin, r.rolsuper AS rolcatupdate, r.rolsuper, a.prfname
FROM
    pg_catalog.pg_roles as r, public.ag_profile as a
WHERE r.oid = 3373::OID
  -- AND a.oid = 3373::OID --replace_me

