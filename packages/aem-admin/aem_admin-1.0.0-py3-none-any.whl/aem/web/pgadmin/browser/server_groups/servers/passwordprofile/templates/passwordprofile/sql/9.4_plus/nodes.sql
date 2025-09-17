WITH raw as (
    SELECT
        oid, prfname,
        prffailedloginattempts,prfpasswordlocktime,prfpasswordlifetime,
        prfpasswordgracetime,prfpasswordreusetime,
        prfpasswordreusemax,prfpasswordverifyfuncdb,
        prfpasswordverifyfunc
    FROM
        ag_profile p
    {% if ppid %}
    WHERE
        p.oid = {{ ppid|qtLiteral }}::oid
    {% endif %}
    ORDER BY p.oid
),  result AS (
    SELECT
            raw.oid, raw.prfname,
            raw.prfpasswordverifyfuncdb,
            raw.prfpasswordverifyfunc,

                CASE WHEN prffailedloginattempts = -2 THEN True ELSE False END AS _prffailedloginattempts_unlimited ,
                CASE WHEN prffailedloginattempts = -1 THEN True ELSE False END AS _prffailedloginattempts_default ,
                CASE WHEN prffailedloginattempts > 0 THEN prffailedloginattempts ELSE 0 END AS prffailedloginattempts ,

                CASE WHEN prfpasswordlocktime = -2 THEN True ELSE False END AS _prfpasswordlocktime_unlimited ,
                CASE WHEN prfpasswordlocktime = -1 THEN True ELSE False END AS _prfpasswordlocktime_default ,
                CASE WHEN prfpasswordlocktime > 0 THEN date_part('days', justify_interval(prfpasswordlocktime::text::interval))::integer ELSE 0 END AS _prfpasswordlocktime_day ,
                CASE WHEN prfpasswordlocktime > 0 THEN date_part('hours', justify_interval(prfpasswordlocktime::text::interval))::integer ELSE 0 END AS _prfpasswordlocktime_hour ,
                CASE WHEN prfpasswordlocktime > 0 THEN date_part('minutes', justify_interval(prfpasswordlocktime::text::interval))::integer ELSE 0 END AS _prfpasswordlocktime_minute ,

                CASE WHEN prfpasswordlifetime = -2 THEN True ELSE False END AS _prfpasswordlifetime_unlimited ,
                CASE WHEN prfpasswordlifetime = -1 THEN True ELSE False END AS _prfpasswordlifetime_default ,
                CASE WHEN prfpasswordlifetime > 0 THEN date_part('days', justify_interval(prfpasswordlifetime::text::interval))::integer ELSE 0 END AS _prfpasswordlifetime_day ,
                CASE WHEN prfpasswordlifetime > 0 THEN date_part('hours', justify_interval(prfpasswordlifetime::text::interval))::integer ELSE 0 END AS _prfpasswordlifetime_hour ,
                CASE WHEN prfpasswordlifetime > 0 THEN date_part('minutes', justify_interval(prfpasswordlifetime::text::interval))::integer ELSE 0 END AS _prfpasswordlifetime_minute ,

                CASE WHEN prfpasswordgracetime = -2 THEN True ELSE False END AS _prfpasswordgracetime_unlimited ,
                CASE WHEN prfpasswordgracetime = -1 THEN True ELSE False END AS _prfpasswordgracetime_default ,
                CASE WHEN prfpasswordgracetime > 0 THEN date_part('days', justify_interval(prfpasswordgracetime::text::interval))::integer ELSE 0 END AS _prfpasswordgracetime_day ,
                CASE WHEN prfpasswordgracetime > 0 THEN date_part('hours', justify_interval(prfpasswordgracetime::text::interval))::integer ELSE 0 END AS _prfpasswordgracetime_hour ,
                CASE WHEN prfpasswordgracetime > 0 THEN date_part('minutes', justify_interval(prfpasswordgracetime::text::interval))::integer ELSE 0 END AS _prfpasswordgracetime_minute ,

                CASE WHEN prfpasswordreusetime = -2 THEN True ELSE False END AS _prfpasswordreusetime_unlimited ,
                CASE WHEN prfpasswordreusetime = -1 THEN True ELSE False END AS _prfpasswordreusetime_default ,
                CASE WHEN prfpasswordreusetime > 0 THEN date_part('days', justify_interval(prfpasswordreusetime::text::interval))::integer ELSE 0 END AS _prfpasswordreusetime_day ,
                CASE WHEN prfpasswordreusetime > 0 THEN date_part('hours', justify_interval(prfpasswordreusetime::text::interval))::integer ELSE 0 END AS _prfpasswordreusetime_hour ,
                CASE WHEN prfpasswordreusetime > 0 THEN date_part('minutes', justify_interval(prfpasswordreusetime::text::interval))::integer ELSE 0 END AS _prfpasswordreusetime_minute,

                CASE WHEN prfpasswordreusemax = -2 THEN True ELSE False END AS _prfpasswordreusemax_unlimited ,
                CASE WHEN prfpasswordreusemax = -1 THEN True ELSE False END AS _prfpasswordreusemax_default ,
                CASE WHEN prfpasswordreusemax > 0 THEN prfpasswordreusemax ELSE 0 END AS prfpasswordreusemax
    FROM raw
)
SELECT * FROM result;
