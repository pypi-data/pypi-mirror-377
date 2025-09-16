{% import 'macros/update.macros' as UD %}

{%- if 'prfname' in requestParam -%}
    ALTER PROFILE {{olddata.prfname}} RENAME TO {{ data.prfname }};
{%- endif -%}

{%- if 'prffailedloginattempts' in requestParam or '_prffailedloginattempts_default' in requestParam or '_prffailedloginattempts_unlimited' in requestParam or
'prfpasswordlocktime' in requestParam or '_prfpasswordlocktime_default' in requestParam or '_prfpasswordlocktime_unlimited' in requestParam or
'prfpasswordlifetime' in requestParam or '_prfpasswordlifetime_default' in requestParam or '_prfpasswordlifetime_unlimited' in requestParam or
'prfpasswordgracetime' in requestParam or '_prfpasswordgracetime_default' in requestParam or '_prfpasswordgracetime_unlimited' in requestParam or
'prfpasswordreusetime' in requestParam or '_prfpasswordreusetime_default' in requestParam or '_prfpasswordreusetime_unlimited' in requestParam or
'prfpasswordreusemax' in requestParam or '_prfpasswordreusemax_default' in requestParam or '_prfpasswordreusemax_unlimited' in requestParam -%}

{%- if 'prfname' in requestParam -%}
    ALTER PROFILE {{ data.prfname }} LIMIT
{%- else -%}
    ALTER PROFILE {{ olddata.prfname }} LIMIT
{%- endif %}

{% if requestParam.prffailedloginattempts or requestParam._prffailedloginattempts_default or requestParam._prffailedloginattempts_unlimited %}
    {{ UD.TARGET_PROFILE_PROPERTY_UPDATE_VALUE_SELECTOR('FAILED_LOGIN_ATTEMPTS', data.prffailedloginattempts,data._prffailedloginattempts_default, data._prffailedloginattempts_unlimited ) }}
{% endif %}
{% if requestParam._prfpasswordlocktime_day or requestParam._prfpasswordlocktime_hour or requestParam._prfpasswordlocktime_minute or requestParam._prfpasswordlocktime_default or requestParam._prfpasswordlocktime_unlimited %}
    {{ UD.TARGET_PROFILE_PROPERTY_UPDATE_VALUE_SELECTOR('PASSWORD_LOCK_TIME', data.prfpasswordlocktime,   requestParam._prfpasswordlocktime_default, requestParam._prfpasswordlocktime_unlimited ) }}
{% endif %}
{% if requestParam._prfpasswordlifetime_day or requestParam._prfpasswordlifetime_hour or requestParam._prfpasswordlifetime_minute or requestParam._prfpasswordlifetime_default or requestParam._prfpasswordlifetime_unlimited  %}
    {{ UD.TARGET_PROFILE_PROPERTY_UPDATE_VALUE_SELECTOR('PASSWORD_LIFE_TIME', data.prfpasswordlifetime,   requestParam._prfpasswordlifetime_default, requestParam._prfpasswordlifetime_unlimited ) }}
{% endif %}
{% if requestParam._prfpasswordgracetime_day or requestParam._prfpasswordgracetime_hour or requestParam._prfpasswordgracetime_minute or requestParam._prfpasswordgracetime_default or requestParam._prfpasswordgracetime_unlimited  %}
    {{ UD.TARGET_PROFILE_PROPERTY_UPDATE_VALUE_SELECTOR('PASSWORD_GRACE_TIME', data.prfpasswordgracetime,  requestParam._prfpasswordgracetime_default, requestParam._prfpasswordgracetime_unlimited ) }}
{% endif %}
{% if requestParam._prfpasswordreusetime_day or requestParam._prfpasswordreusetime_hour or requestParam._prfpasswordreusetime_minute or requestParam._prfpasswordgracetime_default or requestParam._prfpasswordgracetime_unlimited %}
    {{ UD.TARGET_PROFILE_PROPERTY_UPDATE_VALUE_SELECTOR('PASSWORD_REUSE_TIME', data.prfpasswordreusetime,  requestParam._prfpasswordreusetime_default, requestParam._prfpasswordreusetime_unlimited ) }}
{% endif %}
{% if requestParam.prfpasswordreusemax or requestParam._prfpasswordreusemax_default or requestParam._prfpasswordreusemax_unlimited %}
    {{ UD.TARGET_PROFILE_PROPERTY_UPDATE_VALUE_SELECTOR('PASSWORD_REUSE_MAX', data.prfpasswordreusemax,   requestParam._prfpasswordreusemax_default, requestParam._prfpasswordreusemax_unlimited ) }}
{% endif %}
;

{%- endif -%}

