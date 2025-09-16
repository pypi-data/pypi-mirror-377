
    update pg_authid
    set rolprofile = ( select ap.oid from ag_profile as ap where prfname='default'::name )
    where rolprofile = (select ap.oid from ag_profile as ap where ap.oid={{data.oid}}::oid);

{% if association_length > 0 %}

    {% for r in data.prfassociation %}
        ALTER role {{ r }} PROFILE {{ data.prfname }} ;
    {% endfor %}

{% endif %}
