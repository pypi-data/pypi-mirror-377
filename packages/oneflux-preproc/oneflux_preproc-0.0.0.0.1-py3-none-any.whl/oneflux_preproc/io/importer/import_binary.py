import numpy as np
import pandas as pd
import struct


def import_binary(head_nlines=1,
                  header_col=0,
                  dtypes_col=3,
                  file_handle='your_binary_file.bin',
                  separator=',',
                  nbytes=2,
                  ):
    """
    Reads in a generic binary file.
    """
    with open(file_handle, 'rb') as f:
        header_cols = [f.readline().decode('utf-8').strip().replace('"', '').replace('\r\n', '').split(separator)
                       for _ in range(head_nlines)]
        header = header_cols[header_col]
        dtypes = header_cols[dtypes_col]

        binary_data = f.read()

    # Calculate number of records
    num_records = len(binary_data) // sum(4 if dtype ==
                                          'ULONG' else 2 for dtype in dtypes)

    # Prepare lists to hold unpacked data for each column
    columns_data = [[] for _ in range(len(dtypes))]

    # Unpack binary data column by column
    offset = 0
    for i, dtype in enumerate(dtypes):
        if dtype == 'ULONG':
            fmt = f'{num_records}L'  # 'L' for unsigned long (4 bytes)
            size = 4
        elif dtype == 'FP2':
            fmt = f'{num_records}e'  # 'e' for 2-byte float (FP2)
            size = 2
        else:
            raise ValueError(f"Unsupported data type: {dtype}")

        # Extract the bytes for this column
        col_bytes = binary_data[offset: offset + num_records * size]
        # Unpack and append to the list
        columns_data[i] = list(struct.unpack(fmt, col_bytes))
        offset += num_records * size

    # Convert to numpy arrays
    data_arrays = []
    for i, dtype in enumerate(dtypes):
        if dtype == 'ULONG':
            data_arrays.append(np.array(columns_data[i], dtype=np.uint32))
        elif dtype == 'FP2':
            data_arrays.append(np.array(columns_data[i], dtype=np.float32))

    # Combine into a 2D array
    data_array = np.column_stack(data_arrays)

    # Convert to DataFrame and filter columns
    df = pd.DataFrame(data_array)
    df.columns = header
    return df
