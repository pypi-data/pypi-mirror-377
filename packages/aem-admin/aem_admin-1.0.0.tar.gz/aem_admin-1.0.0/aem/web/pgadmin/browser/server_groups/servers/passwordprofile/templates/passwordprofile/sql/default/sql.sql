select
    '-- PROFILE: '	|| pg_catalog.quote_ident(prfname) || E'\n-- DROP PROFILE IF EXISTS ' ||
    pg_catalog.quote_ident(prfname) || E';\n\nCREATE PROFILE ' ||
    pg_catalog.quote_ident(prfname) || E' LIMIT\n  ' ||
    CASE
        WHEN prffailedloginattempts is not null
            THEN concat('FAILED_LOGIN_ATTEMPTS ' , p.prffailedloginattempts)
        END || E'\n  ' ||
    CASE
        WHEN prfpasswordlocktime >= 0
            THEN concat('PASSWORD_LOCK_TIME ' , (p.prfpasswordlocktime)::float4 / 24 / 60 / 60)
        WHEN prfpasswordlocktime < 0
            THEN concat('PASSWORD_LOCK_TIME ' , p.prfpasswordlocktime)
        END || E'\n  ' ||
    CASE
        WHEN prfpasswordlocktime >= 0
            THEN concat('PASSWORD_LIFE_TIME ' , (p.prfpasswordlifetime)::float4 / 24 / 60 / 60)
        WHEN prfpasswordlocktime < 0
            THEN concat('PASSWORD_LIFE_TIME ' , p.prfpasswordlifetime)
        END || E'\n  ' ||
    CASE
        WHEN prfpasswordlocktime >= 0
            THEN concat('PASSWORD_GRACE_TIME ' , (p.prfpasswordgracetime)::float4 / 24 / 60 / 60)
        WHEN prfpasswordlocktime < 0
            THEN concat('PASSWORD_GRACE_TIME ' , p.prfpasswordgracetime)
        END || E'\n  ' ||
    CASE
        WHEN prfpasswordlocktime >= 0
            THEN concat('PASSWORD_REUSE_TIME ' , (p.prfpasswordreusetime)::float4 / 24 / 60 / 60)
        WHEN prfpasswordlocktime < 0
            THEN concat('PASSWORD_REUSE_TIME ' , p.prfpasswordreusetime)
        END || E'\n  ' ||
    CASE
        WHEN prfpasswordreusemax is not null
            THEN concat('PASSWORD_REUSE_MAX ' , p.prfpasswordreusemax) END || E'\n  ' ||
    CASE
        WHEN prfpasswordverifyfunc is not null
            THEN concat('PASSWORD_VERIFY_FUNCTION ' , p.prfpasswordverifyfunc)
        WHEN prfpasswordverifyfunc is null
            THEN concat('PASSWORD_VERIFY_FUNCTION ' , 'null') END || ';'
FROM
    pg_catalog.ag_profile p
WHERE
    p.oid={{ppid}}::OID;
