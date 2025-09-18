import pandas as pd


def import_ascii(file_handle='your_binary_file.bin', 
                 head_nlines=1,
                 header_col=0,
                 **kwargs):
    """
    Reads in a generic ASCII file.
    """
    skiprows = kwargs.pop(
        'skiprows', 
        list(set([i for i in range(0, head_nlines)]) - set([header_col]))
    )

    df = pd.read_csv(file_handle, header=0,
                     skiprows=skiprows, **kwargs)
    return df
