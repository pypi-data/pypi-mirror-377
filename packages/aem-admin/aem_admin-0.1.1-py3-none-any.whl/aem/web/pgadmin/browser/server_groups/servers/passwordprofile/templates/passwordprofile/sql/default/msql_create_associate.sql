{% for r in data %}
    ALTER role {{ r }} PROFILE "{{ prfname }}" ;
{% endfor %}
