"""Convert saleae-measurements to pandas DataFrame
- direct import seems not to exist
- manual steps:
    - open .sal file,
    - choose 'file', 'export raw data',
    - select desired channels, export to csv, WITHOUT ISO timestamps (to get relative timing)
    - this produces an analog.csv & digital.csv
    - rename these to something like 'measurement abc.analog.csv'
- to compress the data it will be imported as dataFrame and pickled
"""

import os
from pathlib import Path

import pandas as pd

path_here = Path(__file__).parent


def path_to_flist(data_path: Path, suffix: str) -> list[Path]:
    """Every path gets transformed to a list of paths.

    Transformations:
    - if directory: list of files inside
    - if existing file: list with 1 element
    - or else: empty list
    """
    data_path = Path(data_path).resolve()
    h5files = []
    if data_path.is_file() and data_path.suffix.lower() == suffix:
        h5files.append(data_path)
    elif data_path.is_dir():
        flist = os.listdir(data_path)
        for file in flist:
            fpath = data_path / str(file)
            if not fpath.is_file() or fpath.suffix.lower() != suffix:
                continue
            h5files.append(fpath)
    return h5files


paths_import = path_to_flist(path_here, ".csv")

for path in paths_import:
    if not path.exists():
        continue
    data = pd.read_csv(path, sep=",", decimal=".", skipinitialspace=True)
    data.to_pickle(path.with_suffix(".pickle"), compression="zstd")
