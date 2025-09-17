# RQADeforestation.py

Python bindings for the Julia package [RQADeforestation.jl](https://github.com/EarthyScience/RQADeforestation.jl/).
It provides functions for fast recurrence quantification analysis (RQA), accelerated using Julia.
This library is part of the [FAIRSenDD project](https://github.com/EarthyScience/FAIRSenDD) that utilize Sentinel-1 data for FAIR deforestation detection.

## Get Started

Install:

```sh
pip install git+https://github.com/EarthyScience/RQADeforestation.py
```

Run RQA analysis on a single time series:

```python
from rqadeforestation import rqatrend
import numpy as np

x = np.arange(1, 30, step=0.01)
y = np.sin(x) + 0.1 * x
rqatrend(y, 0.5, 10, 1)
# -0.14028027430322332
```

Use in openEO:

```python
import openeo
connection = openeo.connect("https://openeo.cloud")

cube_in = connection.load_collection(
  "SENTINEL1_SIG0_20M",
  spatial_extent={"west": 16.06, "south": 48.06, "east": 16.67, "north": 48.07},
  temporal_extent=["2023-01-01", "2024-01-01"],
  bands=["VV"]
)

rqatrend = openeo.UDF(
"""
# /// script
# dependencies = [
# "xarray",
# "rqadeforestation @ git+https://github.com/EarthyScience/RQADeforestation.py",
# ]
# ///

import xarray as xr
from rqadeforestation import rqatrend

def apply_datacube(cube: xr.DataArray, context: dict) -> xr.DataArray:
    res_np = rqatrend(cube.to_numpy(), 0.5, 10, 1)
    res_xr = xr.DataArray(res_np)
    return res_xr
"""
)

cube_out = cube_in.apply(process=rqatrend)
result = cube_out.save_result("GTiff")

connection.authenticate_oidc()
job = result.create_job()
job.start_and_wait()
job.get_results().download_files("output")
```

## Motivation

Analyzing high resolution sattelite images at global scale requires to optimize the execution efficiency.
Python is required for most openEO workflows in which performance critical parts of the code are written in a compiled programming language.
Usually, this is done in C, e.g., array operations in numpy.
Julia provides an alternative to accellerate code using a more user-friendly language.

## Development

Development workflow:

1. Write Julia code at https://github.com/EarthyScience/RQADeforestation.jl
1. Compile using [`StaticCompiler`](https://github.com/EarthyScience/RQADeforestation.jl/tree/main/staticcompiler)
1. Put the binary libraries at [`rqadeforestation/lib`](rqadeforestation/lib)
1. Add python binding functions to this package
1. Install this package in openEO and use it in an [User-Defined-Function](https://open-eo.github.io/openeo-python-client/udf.html#declaration-of-udf-dependencies)

## Citation

F. Cremer, M. Urbazaev, J. Cortés, J. Truckenbrodt, C. Schmullius and C. Thiel, "Potential of Recurrence Metrics from Sentinel-1 Time Series for Deforestation Mapping," in IEEE Journal of Selected Topics in Applied Earth Observations and Remote Sensing, vol. 13, pp. 5233-5240, 2020, doi: [10.1109/JSTARS.2020.3019333](https://dx.doi.org/10.1109/JSTARS.2020.3019333).

## Funding

<img src="https://github.com/EarthyScience/FAIRSenDD/raw/main/website/docs/public/ESA_logo.svg" align="left" height="50px"/>
<img src="https://github.com/EarthyScience/FAIRSenDD/raw/main/website/docs/public/ESA_NoR_logo.svg" align="left" height="50px" style="filter: contrast(0);"/>

This project was funded by the European Space Agency in the Science Result Long-Term Availability & Reusability Demonstrator Initiative.
In addition, this project was supported by the ESA Network of Resources.
