{% import 'macros/stereotype.macros' as ST %}

WITH prf_association AS (
    select ARRAY(
        SELECT a.rolname AS prfassociation
        FROM pg_authid AS a, ag_profile AS p
        WHERE a.rolprofile=p.oid
    {% if ppid %}
        and p.oid = {{ ppid|qtLiteral }}::oid
    {% else %}

    {% endif %}
     	) prfassociation
    FROM
    	pg_catalog.ag_profile a
) , raw as (
    SELECT
        p.oid, prfname,
        prffailedloginattempts,prfpasswordlocktime,prfpasswordlifetime,
        prfpasswordgracetime,prfpasswordreusetime,
        prfpasswordreusemax,prfpasswordverifyfuncdb,
        prfpasswordverifyfunc,n.oid as prfpasswordverifyfuncschema,prf_association.prfassociation
    FROM
        ag_profile p, prf_association, pg_namespace as n, pg_proc as proc
    {% if ppid %}

        WHERE
            p.oid = {{ ppid|qtLiteral }}::oid and proc.pronamespace = n.oid
                {% if funcoid %}
                    and proc.oid = p.prfpasswordverifyfunc
                {% endif %}
    {% endif %}
    Group BY p.oid, prfname,
                     prffailedloginattempts,prfpasswordlocktime,prfpasswordlifetime,
                     prfpasswordgracetime,prfpasswordreusetime,
                     prfpasswordreusemax,prfpasswordverifyfuncdb,
                     prfpasswordverifyfunc,n.oid ,prf_association.prfassociation
),  result AS (
    SELECT
            raw.oid, raw.prfname,
            raw.prfpasswordverifyfuncdb,
            raw.prfpasswordverifyfunc,
            raw.prfpasswordverifyfuncschema,
            prf_association.prfassociation::text,
            {{ ST.CASE_DATE_PART_SELECTOR('lock') }} ,
            {{ ST.CASE_DATE_PART_SELECTOR('life') }},
            {{ ST.CASE_DATE_PART_SELECTOR('grace') }},
            {{ ST.CASE_DATE_PART_SELECTOR('reuse') }},
            {{ ST.CASE_INTEGER_SELECTOR('prfpasswordreusemax') }},
            {{ ST.CASE_INTEGER_SELECTOR('prffailedloginattempts') }}

    FROM raw,prf_association
    Group BY 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32
)
SELECT distinct(oid), prfname, prfpasswordverifyfuncdb, prfpasswordverifyfunc,
       CASE WHEN prfpasswordverifyfunc is null THEN null ELSE prfpasswordverifyfuncschema END as prfpasswordverifyfuncschema,
       prfassociation, _prfpasswordlocktime_unlimited, _prfpasswordlocktime_default, _prfpasswordlocktime_day, _prfpasswordlocktime_hour, _prfpasswordlocktime_minute, _prfpasswordlifetime_unlimited, _prfpasswordlifetime_default, _prfpasswordlifetime_day, _prfpasswordlifetime_hour, _prfpasswordlifetime_minute, _prfpasswordgracetime_unlimited, _prfpasswordgracetime_default, _prfpasswordgracetime_day, _prfpasswordgracetime_hour, _prfpasswordgracetime_minute, _prfpasswordreusetime_unlimited, _prfpasswordreusetime_default, _prfpasswordreusetime_day, _prfpasswordreusetime_hour, _prfpasswordreusetime_minute, _prfpasswordreusemax_unlimited, _prfpasswordreusemax_default, prfpasswordreusemax, _prffailedloginattempts_unlimited, _prffailedloginattempts_default, prffailedloginattempts
FROM result;
