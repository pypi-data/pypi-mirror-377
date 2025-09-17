{% import 'macros/stereotype.macros' as ST %}
CREATE PROFILE
    {% if data.prfname -%}
        {{ data.prfname}}
    {% endif -%}

    {%- if not (data._prffailedloginattempts_default and
                data._prfpasswordlocktime_default and
                data._prfpasswordlifetime_default and
                data._prfpasswordgracetime_default and
                data._prfpasswordreusetime_default and
                data._prfpasswordreusemax_default) %}
    LIMIT

    {{ ST.TARGET_PROFILE_PROPERTY_VALUE_SELECTOR('FAILED_LOGIN_ATTEMPTS',   data.prffailedloginattempts, data._prffailedloginattempts_default, data._prffailedloginattempts_unlimited ) }}
    {{ ST.TARGET_PROFILE_PROPERTY_VALUE_SELECTOR('PASSWORD_LOCK_TIME',      data.prfpasswordlocktime,    data._prfpasswordlocktime_default,    data._prfpasswordlocktime_unlimited ) }}
    {{ ST.TARGET_PROFILE_PROPERTY_VALUE_SELECTOR('PASSWORD_LIFE_TIME',      data.prfpasswordlifetime,    data._prfpasswordlifetime_default,    data._prfpasswordlifetime_unlimited ) }}
    {{ ST.TARGET_PROFILE_PROPERTY_VALUE_SELECTOR('PASSWORD_GRACE_TIME',     data.prfpasswordgracetime,   data._prfpasswordgracetime_default,   data._prfpasswordgracetime_unlimited ) }}
    {{ ST.TARGET_PROFILE_PROPERTY_VALUE_SELECTOR('PASSWORD_REUSE_TIME',     data.prfpasswordreusetime,   data._prfpasswordreusetime_default,   data._prfpasswordreusetime_unlimited ) }}
    {{ ST.TARGET_PROFILE_PROPERTY_VALUE_SELECTOR('PASSWORD_REUSE_MAX',      data.prfpasswordreusemax,    data._prfpasswordreusemax_default,    data._prfpasswordreusemax_unlimited ) }}

    {% endif -%}
;
