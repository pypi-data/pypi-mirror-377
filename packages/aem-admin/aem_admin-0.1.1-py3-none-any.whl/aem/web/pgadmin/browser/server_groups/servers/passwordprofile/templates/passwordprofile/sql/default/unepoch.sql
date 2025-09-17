{% import 'macros/epoch.macros' as EP %}
{% import 'macros/default.macros' as DF %}
{% import 'macros/unlimited.macros' as UL %}
{% import 'macros/stereotype.macros' as ST %}

-- v1 : unepoch - interval to human familiar expression
-- table value to json

SELECT
    {{ ST.SELECT_PHRASE_OF_UNEPOCH('lock',data.prfpasswordlocktime) }},
    {{ ST.SELECT_PHRASE_OF_UNEPOCH('life',data.prfpasswordlifetime) }},
    {{ ST.SELECT_PHRASE_OF_UNEPOCH('grace',data.prfpasswordgracetime) }},
    {{ ST.SELECT_PHRASE_OF_UNEPOCH('reuse',data.prfpasswordreusetime) }};
