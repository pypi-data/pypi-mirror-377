
# built-in modules
from configobj import ConfigObj
import re
import os
import warnings
import logging
from functools import reduce

# 3rd party modules
import numpy as np
import pandas as pd

# project modules

logger = logging.getLogger('wvlt.eddypro_compatibility')


def read_eddypro_metadata_file(filename):
    metadata = {}
    with open(filename, 'r') as file:
        section = None
        for line in file:
            line = line.strip()
            if line.startswith(';') or not line:
                continue  # Skip comments and empty lines
            if line.startswith('[') and line.endswith(']'):
                section = line[1:-1]  # Extract section name
                metadata[section] = {}
            else:
                key, value = line.split('=', 1)
                metadata[section][key.strip()] = value.strip()
    return metadata


def get_eddypro_output(site_name='', **kwargs):
    mergeorconcat = kwargs.get('mergeorconcat', 'merge')
    folder = kwargs.get('folder', 'data')

    ep_read_params = {'skiprows': [0, 2], 'na_values': [-9999, 'NAN']}

    ep_path = os.path.join(folder, site_name, 'eddypro_output')

    files = {'FLUX': [], 'FLXNT': [], 'QCQA': [], 'META': []}
    for name in os.listdir(ep_path):
        if name.endswith('.csv'):
            if re.findall('_full_output_', name):
                if name.endswith('_adv.csv'):
                    files['FLUX'] += [pd.read_csv(
                        os.path.join(ep_path, name), **ep_read_params)]
                else:
                    files['FLUX'] += [pd.read_csv(os.path.join(
                        ep_path, name), na_values=[-9999, 'NAN'])]
            elif re.findall('_fluxnet_', name):
                flxnt_last = pd.read_csv(os.path.join(
                    ep_path, name), na_values=[-9999, 'NAN'])
                flxnt_last["date"] = pd.to_datetime(
                    flxnt_last["TIMESTAMP_START"], format='%Y%m%d%H%M').dt.strftime('%Y-%m-%d')
                flxnt_last["time"] = pd.to_datetime(
                    flxnt_last["TIMESTAMP_START"], format='%Y%m%d%H%M').dt.strftime('%H:%M')
                files['FLXNT'] += [flxnt_last]
                del flxnt_last
            elif re.findall('_qc_details_', name):
                if name.endswith('_adv.csv'):
                    files['QCQA'] += [pd.read_csv(
                        os.path.join(ep_path, name), **ep_read_params)]
                else:
                    files['QCQA'] += [pd.read_csv(os.path.join(
                        ep_path, name), na_values=[-9999, 'NAN'])]
            elif re.findall('_metadata_', name):
                files['META'] += [pd.read_csv(os.path.join(ep_path, name),
                                              na_values=[-9999, 'NAN'])]

    for k in [k for k in list(files.keys()) if not files[k]]:
        del ([files[k]])

    for k in files.keys():
        if len(files[k]) == 1:
            files[k] = files[k][0]
        elif mergeorconcat == 'concat':
            files[k] = pd.concat(files[k])
        else:
            files[k] = reduce(lambda left, right: pd.merge(
                left, right, on=["date", 'time'], how="outer", suffixes=('', '_DUP')), files[k])

    data = pd.DataFrame(files.pop('FLUX', {}))
    for name, dat in files.items():
        data = pd.merge(data, dat, on=["date", 'time'],
                        how="outer", suffixes=('', f'_{name}'))

    data['TIMESTAMP'] = pd.to_datetime(
        data.date + ' ' + data.time)  # .dt.tz_localize('UTC')
    return data


def get_eddypro_cospectra(site_name='', x='natural_frequency', y='f_nat*cospec(w_co2)/cov(w_co2)', folder='data', subfolder='', help=False):
    assert (x is not None and y is not None) or (help)

    ep_path = os.path.join(
        folder, site_name, 'output/eddypro_output', subfolder, 'eddypro_binned_cospectra')

    if not os.path.exists(ep_path):
        return None
    files = []
    for name in os.listdir(ep_path):
        if name.endswith('.csv'):
            if re.findall('_binned_cospectra_', name):
                binned_cosp = pd.read_csv(os.path.join(
                    ep_path, name), skiprows=11, na_values=[-9999, 'NAN'])
                if help:
                    print(binned_cosp.columns)
                    return
                if x not in binned_cosp.columns or y not in binned_cosp.columns:
                    continue
                binned_cosp.dropna(subset=[x], inplace=True)
                binned_cosp = binned_cosp[[x, y]]
                binned_cosp['TIMESTAMP'] = name.split('_')[0]
                binned_cosp = binned_cosp.pivot(
                    index='TIMESTAMP', columns=x, values=y).reset_index(drop=False)
                binned_cosp.columns = [c for c in binned_cosp.columns]
                files += [binned_cosp]

    if len(files) == 1:
        data = files[0]
    else:
        data = pd.concat(files)

    data['TIMESTAMP'] = pd.to_datetime(data['TIMESTAMP'], format='%Y%m%d-%H%M')
    return data


def extract_info_from_eddypro_setup(eddypro=None, metadata=None):
    """
    Extracts information from EddyPro setup and metadata files and returns a dictionary.

    Parameters:
    - eddypro: Path to the EddyPro setup file.
    - metadata: Path to the metadata file.

    Returns:
    - A dictionary containing extracted information.
    """
    args = {}

    eddypro_setup = read_eddypro_metadata_file(eddypro) if eddypro else None
    eddypro_metad = read_eddypro_metadata_file(metadata) if metadata else None

    assert eddypro_setup and eddypro_metad, 'Both setup and metadata must be loaded.'
    
    separator_symb = dict(comma=',', semicolon='.', espace=' ', tab='\t')
    
    args['Files'] = dict(
        file_path=eddypro_setup['Project']['out_path'],
        in_filename=eddypro_setup['Project']['file_prototype'],
        in_firstdatarow=int(
            float(eddypro_metad['FileDescription']['header_rows']))+1,
        in_headerrow=int(
            float(eddypro_metad['FileDescription']['header_rows'])),
        in_separator=separator_symb.get(eddypro_metad['FileDescription']['separator'],
                                        eddypro_metad['FileDescription']['separator']),
        out_filename='Right click to browse(*.nc)',
        fileduration=int(
            eddypro_setup['RawProcess_Settings']['avrg_len']),
        )

    args['Global'] = dict(
        Conventions = '',
        acknowledgement = '',
        altitude = f"{eddypro_metad['Site']['altitude']}m",
        canopy_height = f"{eddypro_metad['Site']['canopy_height']}m",
        comment = '',
        contact='',
        data_link='',
        featureType='',
        fluxnet_id='',
        history='',
        institution='',
        latitude=eddypro_metad['Site']['latitude'],
        license='',
        license_name='',
        longitude=eddypro_metad['Site']['longitude'],
        metadata_link='',
        publisher_name='',
        references='',
        site_name=eddypro_setup['Project']['project_id'],
        site_pi = '',
        soil = '',
        source='',
        time_step=np.nan,#30,
        acquisition_frequency=float(eddypro_metad['Timing']['acquisition_frequency']),
        time_zone='<country>/<time_zone>',
        title='',
        tower_height = '',
        vegetation='',
        )

    args['Options'] = dict()

    args['Instruments'] = dict()
    instr_nb = set([re.findall('instr_(\d*)_', _k)[0] for _k in eddypro_metad['Instruments'].keys() if 'instr_' in _k])
    for i in instr_nb:
        model = eddypro_metad['Instruments'][f'instr_{i}_model']
        args['Instruments'][model] = dict(
            Attr={
                re.sub('^instr_\d+_', '', k): v for k, v in eddypro_metad['Instruments'].items() if k.startswith(f'instr_{i}_')
                },
                )

    instrument_aka_r = {'li7200': 'Li-7200', 'hs_50': 'HS-50'}
    args['Variables'] = dict()
    varbl_nb = set([re.findall('col_(\d*)_', _k)[0]
                   for _k in eddypro_metad['FileDescription'].keys() if 'col_' in _k])
    for i in varbl_nb:
        name = eddypro_metad['FileDescription'][f'col_{i}_variable']
        unit = eddypro_metad['FileDescription'][f'col_{i}_unit_in']
        inst_id = eddypro_metad['FileDescription'][f'col_{i}_instrument']
        inst_model = instrument_aka_r.get(inst_id.rsplit('_', 1)[0], inst_id)
        
        if eddypro_metad['FileDescription'][f'col_{i}_instrument']:
            instr_model = [_k for _k in eddypro_metad['Instruments'].keys() if eddypro_metad['FileDescription'][f'col_{i}_instrument'] == eddypro_metad['Instruments'][_k]]
            if instr_model:
                instr_nb = re.findall('instr_(.*?)_', instr_model[0])[0]
            else:
                instr_nb = 0
        else:
            instr_nb = 0
        eddypro_metad['FileDescription'][f'col_{i}_height'] = f"{eddypro_metad['Instruments'].get(f'instr_{instr_nb}_height', 0)}m"
        # mstp = eddypro_metad['FileDescription'][f'col_{i}_measuring_type']
        if name in [None, '', 'ignore', 'not_numeric']:
            continue
        unique_name = f"{name}_{unit}_{inst_id}"
        args['Variables'][unique_name] = dict(
            Attr={
                re.sub('^col_\d+_', '', k): v for k, v in eddypro_metad['FileDescription'].items() if k.startswith(f'col_{i}_')
            },
            csv={'column': i},
        )

    args['Corrections'] = dict()
    despiking_meth = {
        '0': 'vickers_et_al_1997',
        '1': 'mauder_et_al_2013',
        }
    despiking_meth_chosen = despiking_meth[eddypro_setup['RawProcess_Settings'].get(
        'despike_vm', '0')]
    args['despiking_method'] = despiking_meth_chosen
    args['Corrections']['despiking'] = dict(method=despiking_meth_chosen)
    
    axis_rotation_meth = {
        '0': None,
        '1': 'double_rotation',
        '2': 'triple_rotation',
        '3': 'planar_fit',
        '4': 'planar_fit_no_bias',
        }
    axis_rotation_meth_chosen = axis_rotation_meth[eddypro_setup['RawProcess_Settings'].get(
        'rot_meth', '0')]
    args['axis_rotation_method'] = axis_rotation_meth_chosen
    args['Corrections']['axis_rotation'] = dict(
        method=axis_rotation_meth_chosen)
    args['Corrections']['axis_rotation'].update(eddypro_setup['RawProcess_TiltCorrection_Settings'])

    time_lag_meth = {
        '0': None,
        '1': 'constant',
        '2': 'maxcov&default',
        '3': 'maxcov',
        '4': 'tlag_opt',
    }
    time_lag_meth_chosen = time_lag_meth[eddypro_setup['RawProcess_Settings'].get(
        'tlag_meth', '0')]
    args['time_lag_method'] = time_lag_meth_chosen
    args['Corrections']['time_lag'] = dict(
        method=time_lag_meth_chosen)
    args['Corrections']['time_lag'].update(eddypro_setup['RawProcess_TimelagOptimization_Settings'])

    detrending_meth = {
        '0': 'ba',
        '1': 'ld',
        '2': 'rm',
        '3': 'ew',
    }
    detrending_meth_chosen = detrending_meth[eddypro_setup['RawProcess_Settings'].get(
        'detrend_meth', '0')]
    args['detrending_method'] = detrending_meth_chosen
    args['Corrections']['detrending'] = dict(
        method=detrending_meth_chosen)

    args['Outputs'] = dict()
    
    args['Outputs'] = dict()

    footprint_meth = {
        '0': 'kl15',
        '1': '?',
    }
    footprint_meth_chosen = footprint_meth[
        eddypro_setup['RawProcess_Settings'].get('foot_meth', '0')]
    args['footprint_method'] = footprint_meth_chosen
    args['Corrections']['footprint'] = dict(
        method=footprint_meth_chosen)

    if eddypro:
        metadata = metadata or eddypro_setup['Project']['proj_file'] or str(eddypro).rsplit('.', 1)[
            0] + '.metadata'

        args['site_name'] = eddypro_setup['Project']['project_id']
        args['input_path'] = eddypro_setup['Project']['out_path'] + \
            '/eddypro_raw_datasets/level_6'
        args['output_folderpath'] = eddypro_setup['Project']['out_path'] + \
            '/wavelet_flux'
        args['datetimerange'] = (
            eddypro_setup['Project']['pr_start_date'].replace('-', '') +
            eddypro_setup['Project']['pr_start_time'].replace(':', '') + '-' +
            eddypro_setup['Project']['pr_end_date'].replace('-', '') +
            eddypro_setup['Project']['pr_end_time'].replace(':', '')
        )
        args['fileduration'] = int(
            eddypro_setup['RawProcess_Settings']['avrg_len'])
        
        try:
            gas4_col = eddypro_setup['Project']['col_n2o']
            eddypro_metad = read_eddypro_metadata_file(metadata)
            if (not gas4_col) or (str(gas4_col) != '0'):
                args['gas4_name'] = eddypro_metad['FileDescription'][f'col_{gas4_col}_variable']
        except Exception as e:
            print(f"Error extracting gas4 name: {e}")

    if metadata:
        # args['Instruments'] = {re.sub('^instr_\d','',k): v for k, v in eddypro_metad['Instruments'].items()}
        
        args['acquisition_frequency'] = int(
            float(eddypro_metad['Timing']['acquisition_frequency']))
        args['altitude'] = int(
            float(eddypro_metad['Site']['altitude']))
        args['latitude'] = int(
            float(eddypro_metad['Site']['latitude']))
        args['longitude'] = int(
            float(eddypro_metad['Site']['longitude']))
        args['zm'] = int(
            float(eddypro_metad['Instruments']['instr_1_height']))
        args['canopy_height'] = int(
            float(eddypro_metad['Site']['canopy_height']))
        args['z0'] = int(
            float(eddypro_metad['Site']['displacement_height']))
        args['zd'] = int(
            float(eddypro_metad['Site']['roughness_length']))
        args['anemometer_north_offset'] = float(eddypro_metad['Instruments'].get(
            'instr_1_north_offset', '0'))

    if eddypro:
        args['variables_available'] = ['u', 'v', 'w'] + [k for k in ['co2',
                                                                     'h2o', 'ch4'] if float(eddypro_setup['Project'][f'col_{k}']) > 0]
        
        for k in list(set(args['variables_available']) - set(['u', 'v', 'w'])):
            col_n = eddypro_setup['Project'][f'col_{k}']
            args[k] = {_k.replace(f'col_{col_n}_', ''): eddypro_metad['FileDescription'][_k] for _k in eddypro_metad['FileDescription'].keys() if _k.startswith(
                f'col_{col_n}_')}
            
            # Add instrument metadata to variables
            instr_nb = re.findall('instr_(.*)_', [_k for _k in eddypro_metad['Instruments'].keys(
            ) if eddypro_metad['FileDescription'][f'col_{col_n}_instrument'] == eddypro_metad['Instruments'][_k]][0])[0]
            args[k].update({_k.replace(f'_{instr_nb}_', '_'): eddypro_metad['Instruments'][_k] for _k in eddypro_metad['Instruments'].keys() if _k.startswith(
                f'instr_{instr_nb}_')})

    if metadata and float(eddypro_setup['Project']['col_n2o']) > 0:
        gas4 = eddypro_metad['FileDescription'][f"col_{eddypro_setup['Project']['col_n2o']}_variable"]
        if gas4:
            args['variables_available'] = args.get(
                'variables_available', []) + [gas4]

    return args


def convert_setup_to_pyfluxpro(setup, save_to=None):
    setup = ConfigObj(setup)
    setup["level"] = "L0"
    setup.filename = save_to
    if save_to:
        setup.write()
    return setup

def update_args_with_extracted_info(args, extracted_info):
    """
    Updates the args dictionary with the extracted information.

    Parameters:
    - args: The dictionary to be updated.
    - extracted_info: The dictionary containing extracted information.

    Returns:
    - The updated args dictionary.
    """
    for key, value in extracted_info.items():
        if key not in args or args[key] is None:
            args[key] = value
    return args
