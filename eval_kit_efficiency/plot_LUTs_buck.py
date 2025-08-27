from pathlib import Path

import numpy as np
import yaml
from matplotlib import pyplot as plt

path_data = Path(__file__).parent / "result_LUTs/BQ25570_LUTs_buck.yaml"

with path_data.open() as file_data:
    metadata = yaml.safe_load(file_data)
    fig = plt.figure(figsize=(9, 8), layout="tight")
    for _name, _data in metadata.items():
        if "LUT_output_efficiency" not in _data:
            continue
        data_y = np.asarray(_data["LUT_output_efficiency"])
        grid_x = np.arange(12)
        plt.plot(grid_x, data_y, label=_name)

    plt.suptitle("Efficiency LUTs_buck")
    plt.xlabel("I_Input [n]")
    plt.ylabel("Efficiency [n]")
    plt.yticks([y / 10 for y in range(11)])
    plt.ylim(bottom=0.0, top=1.0)
    plt.grid(visible=True)
    plt.legend(loc="lower right")
    plt.savefig(path_data.with_suffix(".svg"))
    plt.close(fig)
