
def fix_time_lag(fix, move, *args, tlag=0, **kwargs):
    return type(
        'var_', (object,),
        {"x": move.shift(time=tlag),# or move.attrs.get('nom_timelag', 0)),
         "tlag": tlag,
         "meta": {}}
        )
