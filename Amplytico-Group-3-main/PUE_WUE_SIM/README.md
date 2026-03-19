# PUE_WUE_SIM (Simulator Core)

This directory contains the simulator core used by `01_weather_api_and_pue_wue_simulation/county_pipeline.py`.

## Files
- `simulation_funs_DC.py`
  - Implements the physics/model functions used to compute PUE/WUE for AE and WEC configurations.
  - Loads COP regression model pickles from the same folder at runtime.

- `COP_2.pkl`, `COP_DX.pkl`, `COP_AC.pkl`
  - Model pickles used by `simulation_funs_DC.py` to estimate chiller performance (COP).

## Notes
- `simulation_funs_DC.py` expects the pickle files to be available in the current working directory.
  `county_pipeline.py` handles this by temporarily `chdir`’ing into `PUE_WUE_SIM/` before importing the simulator.

