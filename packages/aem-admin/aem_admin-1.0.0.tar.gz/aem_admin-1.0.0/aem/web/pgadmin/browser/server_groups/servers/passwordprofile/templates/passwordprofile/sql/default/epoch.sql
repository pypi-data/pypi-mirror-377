{% import 'macros/epoch.macros' as EP %}
{% import 'macros/default.macros' as DF %}
{% import 'macros/unlimited.macros' as UL %}
{% import 'macros/stereotype.macros' as ST %}

-- v1 : epoch - human familiar time expression to interval
-- json to table value

SELECT
        {{ST.SELECT_PHRASE_OF_EPOCH('lock', data._prfpasswordlocktime_default, data._prfpasswordlocktime_unlimited)}} ,
        {{ST.SELECT_PHRASE_OF_EPOCH('life', data._prfpasswordlifetime_default, data._prfpasswordlifetime_unlimited)}} ,
        {{ST.SELECT_PHRASE_OF_EPOCH('grace', data._prfpasswordgracetime_default, data._prfpasswordgracetime_unlimited)}} ,
        {{ST.SELECT_PHRASE_OF_EPOCH('reuse', data._prfpasswordreusetime_default, data._prfpasswordreusetime_unlimited)}}
FROM
        {{ST.FROM_PHRASE_OF_EPOCH_DAYS('lock', data._prfpasswordlocktime_day)}} ,
        {{ST.FROM_PHRASE_OF_EPOCH_HOURS('lock', data._prfpasswordlocktime_hour)}} ,
        {{ST.FROM_PHRASE_OF_EPOCH_MINUTES('lock', data._prfpasswordlocktime_minute)}} ,

        {{ST.FROM_PHRASE_OF_EPOCH_DAYS('life', data._prfpasswordlifetime_day)}} ,
        {{ST.FROM_PHRASE_OF_EPOCH_HOURS('life', data._prfpasswordlifetime_hour)}} ,
        {{ST.FROM_PHRASE_OF_EPOCH_MINUTES('life', data._prfpasswordlifetime_minute)}} ,

        {{ST.FROM_PHRASE_OF_EPOCH_DAYS('grace', data._prfpasswordgracetime_day)}} ,
        {{ST.FROM_PHRASE_OF_EPOCH_HOURS('grace', data._prfpasswordgracetime_hour)}} ,
        {{ST.FROM_PHRASE_OF_EPOCH_MINUTES('grace', data._prfpasswordgracetime_minute)}} ,

        {{ST.FROM_PHRASE_OF_EPOCH_DAYS('reuse', data._prfpasswordreusetime_day)}} ,
        {{ST.FROM_PHRASE_OF_EPOCH_HOURS('reuse', data._prfpasswordreusetime_hour)}} ,
        {{ST.FROM_PHRASE_OF_EPOCH_MINUTES('reuse', data._prfpasswordreusetime_minute)}}
;
