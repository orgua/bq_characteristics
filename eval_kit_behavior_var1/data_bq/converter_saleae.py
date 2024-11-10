"""Convert saleae-measurements to pandas DataFrame
- direct import seems not to exist
- manual steps:
    - open .sal file,
    - choose 'file', 'export raw data',
    - select desired channels, export to csv, WITHOUT ISO timestamps (to get relative timing)
    - this produces an analog.csv & digital.csv
    - rename these to something like 'measurment abc.analog.csv'
- to compress the data it will be imported as dataFrame and pickled
"""

from pathlib import Path

import pandas as pd

path_here = Path(__file__).parent

paths_import = [
    path_here / "OC, LED 400mA.analog.csv",
    path_here / "OC, LED 400mA.digital.csv",
    path_here / "R1k, LED 400mA.analog.csv",
    path_here / "R1k, LED 400mA.digital.csv",
    path_here / "R1k, LED 700mA.analog.csv",
    path_here / "R1k, LED 700mA.digital.csv",
    path_here / "R1k, LED 900mA.analog.csv",
    path_here / "R1k, LED 900mA.digital.csv",
    path_here / "R1k, LED 1100mA.analog.csv",
    path_here / "R1k, LED 1100mA.digital.csv",
    path_here / "R100, LED 400mA.analog.csv",
    path_here / "R100, LED 400mA.digital.csv",
]

for path in paths_import:
    data = pd.read_csv(path, sep=",", decimal=".", skipinitialspace=True)
    data.to_pickle(path.with_suffix(".pickle"), compression="zstd")
