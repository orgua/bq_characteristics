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

from pathlib import Path

import pandas as pd

path_here = Path(__file__).parent
paths_import = list(path_here.glob("**/*.csv"))  # for py>=3.12: case_sensitive=False

for path in paths_import:
    if not path.exists():
        continue
    data = pd.read_csv(path, sep=",", decimal=".", skipinitialspace=True)
    data.to_pickle(path.with_suffix(".pickle"), compression="zstd")
