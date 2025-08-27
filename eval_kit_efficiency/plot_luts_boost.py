from pathlib import Path

import numpy as np
import yaml
from matplotlib import pyplot as plt

path_data = Path(__file__).parent / "result_LUTs/BQ25570_LUTs_boost.yaml"

with path_data.open() as file_data:
    metadata = yaml.safe_load(file_data)
    for _name, _data in metadata.items():
        if "LUT_input_efficiency" not in _data:
            continue
        grid_xy = np.asarray(_data["LUT_input_efficiency"])
        # plt.plot(grid_xy)
        X = np.arange(12)
        Y = np.arange(12)
        Z = grid_xy
        fig = plt.figure(figsize=(9, 8), layout="tight")
        plt.pcolormesh(X, Y, Z, vmin=0.0, vmax=1.0, cmap="RdYlGn")
        plt.colorbar()
        plt.suptitle(f"Efficiency LUT_{_name}")
        plt.xlabel("I_Input [n]")
        plt.ylabel("V_Input [n]")
        plt.axis("equal")
        path_result = path_data.with_stem(path_data.stem + "_" + _name).with_suffix(".png")
        plt.savefig(path_result)
        plt.close(fig)
