{% if data.prfassociation is not none %}
    {% for r in data.prfassociation %}
        ALTER role {{r['role']}} PROFILE {{data.prfname}} ;
    {% endfor %}
{% endif %}
;
