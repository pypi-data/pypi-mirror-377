{% if data.prfassociation is not none %}
    {% if data.prfname and data.%}
        ALTER PROFILE {{data.prfname}} LIMIT PASSWORD_VERIFY_FUNCTION ppf_test1;
    {% endif %}
{% endif %}

;
