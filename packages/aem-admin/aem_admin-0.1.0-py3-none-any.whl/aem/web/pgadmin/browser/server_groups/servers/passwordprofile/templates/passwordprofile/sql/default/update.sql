{% import 'macros/stereotype.macros' as ST %}

{% if data.prfname %}
    ALTER PROFILE {{olddata.prfname}} RENAME TO {{ data.prfname }};
{% endif %}

{% if 'prfpasswordlocktime' in data or
'prfpasswordlifetime' in data or
'prfpasswordgracetime' in data or
'prfpasswordreusetime' in data or
'prffailedloginattempts' in data or
'prfpasswordlocktime' in data or
'prffailedloginattempts' in data or
'_prffailedloginattempts_default' in data or
'_prffailedloginattempts_unlimited' in data or
'_prfpasswordgracetime_default' in data or
'_prfpasswordgracetime_unlimited' in data or
'_prfpasswordlocktime_default' in data or
'_prfpasswordlocktime_unlimited' in data or
'_prfpasswordreusemax_default' in data or
'_prfpasswordreusemax_unlimited' in data or
'_prfpasswordreusetime_default' in data or
'_prfpasswordreusetime_unlimited' in data %}

ALTER PROFILE
{% if data.prfname %}
    {{ data.prfname }}
{% elif olddata.prfname %}
    {{ olddata.prfname }}
{% endif %}
LIMIT
{% if requestParam.prffailedloginattempts or requestParam._prffailedloginattempts_default or requestParam._prffailedloginattempts_unlimited %}
    {{ ST.TARGET_PROFILE_PROPERTY_UPDATE_VALUE_SELECTOR('FAILED_LOGIN_ATTEMPTS', data.prffailedloginattempts,data._prffailedloginattempts_default, data._prffailedloginattempts_unlimited ) }}
{% endif %}
{% if requestParam._prfpasswordlocktime_day or requestParam._prfpasswordlocktime_hour or requestParam._prfpasswordlocktime_minute or requestParam._prfpasswordlocktime_default or requestParam._prfpasswordlocktime_unlimited %}
    {{ ST.TARGET_PROFILE_PROPERTY_UPDATE_VALUE_SELECTOR('PASSWORD_LOCK_TIME', data.prfpasswordlocktime,   requestParam._prfpasswordlocktime_default, requestParam._prfpasswordlocktime_unlimited ) }}
{% endif %}
{% if requestParam._prfpasswordlifetime_day or requestParam._prfpasswordlifetime_hour or requestParam._prfpasswordlifetime_minute or requestParam._prfpasswordlifetime_default or requestParam._prfpasswordlifetime_unlimited  %}    
    {{ ST.TARGET_PROFILE_PROPERTY_UPDATE_VALUE_SELECTOR('PASSWORD_LIFE_TIME', data.prfpasswordlifetime,   requestParam._prfpasswordlifetime_default, requestParam._prfpasswordlifetime_unlimited ) }}
{% endif %}
{% if requestParam._prfpasswordgracetime_day or requestParam._prfpasswordgracetime_hour or requestParam._prfpasswordgracetime_minute or requestParam._prfpasswordgracetime_default or requestParam._prfpasswordgracetime_unlimited  %}    
    {{ ST.TARGET_PROFILE_PROPERTY_UPDATE_VALUE_SELECTOR('PASSWORD_GRACE_TIME', data.prfpasswordgracetime,  requestParam._prfpasswordgracetime_default, requestParam._prfpasswordgracetime_unlimited ) }}
{% endif %}
{% if requestParam._prfpasswordreusetime_day or requestParam._prfpasswordreusetime_hour or requestParam._prfpasswordreusetime_minute or requestParam._prfpasswordgracetime_default or requestParam._prfpasswordgracetime_unlimited %}    
    {{ ST.TARGET_PROFILE_PROPERTY_UPDATE_VALUE_SELECTOR('PASSWORD_REUSE_TIME', data.prfpasswordreusetime,  requestParam._prfpasswordreusetime_default, requestParam._prfpasswordreusetime_unlimited ) }}
{% endif %}
{% if requestParam.prfpasswordreusemax or requestParam._prfpasswordreusemax_default or requestParam._prfpasswordreusemax_unlimited %}
    {{ ST.TARGET_PROFILE_PROPERTY_UPDATE_VALUE_SELECTOR('PASSWORD_REUSE_MAX', data.prfpasswordreusemax,   requestParam._prfpasswordreusemax_default, requestParam._prfpasswordreusemax_unlimited ) }}
{% endif %}
;
{% endif %}
