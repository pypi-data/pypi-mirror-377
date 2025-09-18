import os
import logging
import pandas as pd
import glob
from functools import reduce
from . import import_ascii, import_binary, read_data

logger = logging.getLogger()


def import_data(setup, datetimes, file_importer, **raw_kwargs):
    setup_raw_kw = setup.get('Files', {})

    head_nlines = int(setup_raw_kw['in_firstdatarow'])-2
    header_col = int(setup_raw_kw['in_headerrow'])-1
    sep = setup_raw_kw['in_separator']
    na_values = [-9999]
    glob_files = setup_raw_kw['glob_files']

    def extract_datetime_parts(dt_input):
        # Parse if input is string
        dt = pd.to_datetime(dt_input)
        return dict(
            year=dt.strftime('%Y'),
            yr=dt.strftime('%y'),
            month=dt.strftime('%m'),
            day=dt.strftime('%d'),
            hour=dt.strftime('%H'),
            minute=dt.strftime('%M'),
        )

    def select_files_based_on_datetime(pattern, dt_input):
        datetime_parts = extract_datetime_parts(dt_input)
        return glob.glob(pattern.format(**datetime_parts))

    files = [f for dt in datetimes for f in select_files_based_on_datetime(
        glob_files, dt)]

    if not files:
        if glob.glob(os.path.dirname(glob_files)):
            logger.warning(
                f'No files found based on dates. Looked in `{os.path.dirname(glob_files)}`.')
        else:
            logger.warning(
                f'Folder `{os.path.dirname(glob_files)}` is empty.')
        
        return pd.DataFrame()

    raw_data = reduce(lambda left, right: pd.concat([left, right], ignore_index=True),
                      [file_importer(
                          f, head_nlines=head_nlines, header_col=header_col, sep=sep, na_values=na_values) for f in files])

    raw_data = read_data.format_column_names(raw_data)

    raw_data = read_data.resolve_timestamp(
        raw_data, 'timestamp')

    raw_data = raw_data.sort_values(by='timestamp')

    return raw_data


