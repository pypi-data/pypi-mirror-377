# Prototype hwo_disra

This repository contains prototypes and working designs for
a framework to generate Design Reference Mission (DRM) analysis
products for the Habitable Worlds Observatory (HWO) project.

## Repository Structure

This repository is organized to support both **published Python package** distribution and **private research notebooks**:

### Published Package (`hwo_disra/`)
The core package contains the public API and framework components that are published to PyPI:
- `hwo_disra/` - Main package directory
  - `api/` - Notebook evaluation and API interfaces
  - `yields/` - Science case yieldinator implementations
    - `BDYieldinator.py` - Brown dwarf detection yields
    - `KBOYieldinator.py` - Kuiper Belt Object detection yields  
    - `QSOYieldinator.py` - Quasar detection yields
    - `StellarEvolution.py` - Stellar evolution case yields
  - `DRMinator.py` - Main DRM analysis orchestrator
  - `Yieldinator.py` - Supports 'Panel 1' analysis of yields over independant variables.
  - `Timeinator.py` - Supports 'Panel 2' analysis of cost on an observatory.
  - `Plotinator.py` - Plotting utilities
  - `tests/` - Unit tests and package validation

### Private Research Content (`hwo_disra/disra_notebooks/`)
**⚠️ Not published to PyPI** - This directory contains complete research notebooks and supporting code:
- Complete science case notebooks with full analysis workflows
- Supporting analysis code specific to individual science cases  
- Research data and intermediate results
- Experimental implementations and prototypes

The `MANIFEST.in` configuration ensures that `hwo_disra/disra_notebooks/` is excluded from package builds and PyPI publication.

### Test Resources (`hwo_disra/tests/resources/`)
Contains minimal test notebooks that **are included** in the published package to validate the notebook evaluation API.

## Development Setup

- Create a python environment.  I use `venv`, `python -m venv hwo_disra-venv`
  (`hwo_disra-venv` can be anything, it's the path of the folder the `venv` is in.)
- Source the activation script.  This requires a POSIX shell. `source hwo_disra-venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`
- Install the dev version of syotools:
  - `git clone https://github.com/spacetelescope/syotools.git`
  - `pip install /path/to/syotools`
- Install `pytest`: `pip install pytest`
- Run `pytest` from the root of the hwo_disra repository.  `pytest`

### Environment

It can be useful to add this to the activate script in your venv

```
export PYSYN_CDBS=$(python -c "import sys; print([p for p in sys.path if 'site-packages' in p][0])")/syotools/reference_data/pysynphot_data/
```

## Project Structure

The core of this project are the [Yieldinator](src/hwo_disra/Yieldinator.py)
and [Timeinator](src/hwo_disra/Timeinator.py) classes, which define the API
for what a science case must provide to us to support analysis.
The Timeinator is generally expected to wrap a Yieldinator and provide
extended analysis on top of yield.

The Yieldinator supports "Panel 1" analysis and the "Timeinator" supports
"Panel 2" analysis.

![](images/science-case-trade-spacee-panels.png)

This class relies on the [EAC](src/hwo_disra/EAC.py) class which we
will create from the syotools telescope models and pass to the
various Yieldinators we receive. **We should discuss what we need
from the Telescope API**

The [DRMinator](src/hwo_disra/DRMinator.py) drives the higher level analysis,
generating sampling points and calling into the Yieldinators to
generate a table of data for analysis.

The [KBOYieldinator](src/hwo_disra/yields/KBOYieldinator.py) is a mostly
complete and working implementation of the KBO science notebook
within this framework.

## TODO

- Implement more Yieldinators for other science cases.
- Move the plotting functionality in `test_kbo_yieldinator` into
  a class and flesh it out a bit.
- Look at some sort of caching mechanism so a Yieldinator does
  not have to recreate the exposure structure every time it is called
  because it's repeatedly called with the same EAC model when sampling
  range spaces.
- Configure pytest to run on Gitlab and write some actual tests.
- Extensively document the Yieldinator class for publication to other
  collaborators.

## CI Build Image

Currently the CI build image is built manually and pushed
to the container repository as needed.

```
docker build -t registry.stsci.edu/hwoe/amyers-scratchpad/hwo_disra:ci-image .
docker push registry.stsci.edu/hwoe/amyers-scratchpad/hwo_disra:ci-image
```
