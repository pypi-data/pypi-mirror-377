{% import 'macros/stereotype.macros' as ST %}
SELECT
{{ ST.DEFAULT_OR_UNLIMITED_TRANSFORMER('FAILED_LOGIN_ATTEMPTS','prffailedloginattempts', data.prffailedloginattempts) }},
{{ ST.DEFAULT_OR_UNLIMITED_TRANSFORMER('PASSWORD_LOCK_TIME','prfpasswordlocktime', data.prfpasswordlocktime) }},
{{ ST.DEFAULT_OR_UNLIMITED_TRANSFORMER('PASSWORD_LIFE_TIME','prfpasswordlifetime', data.prfpasswordlifetime) }},
{{ ST.DEFAULT_OR_UNLIMITED_TRANSFORMER('PASSWORD_GRACE_TIME','prfpasswordgracetime', data.prfpasswordgracetime) }},
{{ ST.DEFAULT_OR_UNLIMITED_TRANSFORMER('PASSWORD_REUSE_TIME','prfpasswordreusetime', data.prfpasswordreusetime) }},
{{ ST.DEFAULT_OR_UNLIMITED_TRANSFORMER('PASSWORD_REUSE_MAX','prfpasswordreusemax', data.prfpasswordreusemax) }}
