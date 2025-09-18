import fluxprint
from . import kljun_et_al_2015


available_corrections = {
    'kl2015':
    type('var_', (object,), {'run': kljun_et_al_2015.retrieve_footprint,
                             'name': 'LPDM-B (Kljun et al., 2015)'}),
}


def apply_footprint(data, x1='w', x2='co2', **kwargs):
    assert all([v in data for v in [x1, x2]]
               ), 'Not all variables for time lag optimization are in data.'

    correction = available_corrections.get(
        data.attrs.get('Corrections', {}).get('footprint', {}).get('method', None), None)

    if correction:
        pass
    return
