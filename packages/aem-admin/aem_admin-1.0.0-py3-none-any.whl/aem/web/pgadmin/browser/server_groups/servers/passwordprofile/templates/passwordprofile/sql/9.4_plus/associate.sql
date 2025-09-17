{% if data.prfassociation is not none %}
    {% for r in data.prfassociation %}
        ALTER role {{ r }} PROFILE {{ data.prfname }} ;
    {% endfor %}
{% endif %}
