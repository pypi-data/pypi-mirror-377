# lhcb-ftcalib
[![pipeline status](https://gitlab.cern.ch/lhcb-ft/lhcb_ftcalib/badges/master/pipeline.svg)](https://gitlab.cern.ch/lhcb-ft/lhcb_ftcalib/-/commits/master)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.12156329.svg)](https://doi.org/10.5281/zenodo.12156328)
### A software package for the calibration of flavour-tagged LHCb data

At high-energy proton-proton collider experiments, the production flavour of neutral B mesons can not be inferred from the reconstructed signal itself.
Instead, it is determined from the charge of reconstructed particles in the associated event by exploiting different mechanism in the hadronisation process of the signal.
Two classes of processes are exploited at the LHCb experiment: the fragmentation of the b quark bound in the signal at the so called same side (SS) and the decay of partner b quark produced in the same b-bbar quark pair at the opposite side (OS).
The determination of the production flavour based on these different processes is performed by different algorithms.
Each algorithm provides the predicted production flavour, the tag decision d, and an estimated mistag (probability) judging the quality of the prediction, by estimating the fraction/probability of wrongly tagged candidates.
This mistag estimate is usually based on ML techniques like (recurrent) neural networks or boosted decision trees.
To maintain the probabilistic character of this estimate, a calibration is needed based on the true initial flavour or by constraining the oscillation of neutral B mesons.

This calibration tool optimizes a generalized linear model (GLM) to map the estimated mistag to the true mistag probability.
In the case of flavour-specific decays of neutral B mesons, the decay-time dependent oscillation probability is taken into account for this calibration. In addition, this package provides helper functions to measure the performance and correlations of these algorithms and allows for the combination of multiple predictions.

**Documentation:** [Read the Docs](https://lhcb-ftcalib.readthedocs.io/en/latest/)

## Installation
```
pip install lhcb_ftcalib
```

## Command Line Interface Examples
Run `ftcalib --help` for a list of all options or [read the docs](https://lhcb-ftcalib.readthedocs.io/en/latest/)

**1. Calibrating opposite side taggers in a sample and saving result**
```
ftcalib file:tree -OS VtxCh Charm OSElectronLatest OSMuonLatest OSKaonLatest \
        -mode Bd -tau B_tau -id B_ID -op calibrate -out output
```
**2. Calibrating both tagging sides, combining them inidividually, and calibrating+saving the results**
```
ftcalib file:tree -OS VtxCh Charm OSElectronLatest OSMuonLatest OSKaonLatest \
        -SS SSPion SSProton \
        -mode Bd -tau B_tau -id B_ID -op calibrate combine calibrate -out output
```
**Note:** The command line interface is by design not feature complete. Use the API to fine tune the calibration settings.

## Requirements
* `numpy>1.21`
* `pandas>2.2.1`
* `scipy`
* `pathlib`
* `iminuit>2.3.0`
* `matplotlib>=3.3.0`
* `numba`
* `uproot>=5.3`
* `sweights==0.0.5`

## Python version support
* 3.7: Install failure (Python end of life)
* 3.8: Install failure (Use ftcalib 1.4.1 instead)
* 3.9: Supported
* 3.10: Supported
* 3.11: Supported
* 3.12: Supported
* 3.13: not tested

## Cite as
```
@misc{lhcb_ftcalib:2024,
    author    = {Führing, Q. and Jevti\'c, V.},
    title     = {{lhcb-ftcalib}: {A software package for the calibration of flavour-tagged LHCb data}},
    url       = {https://gitlab.cern.ch/lhcb-ft/lhcb_ftcalib},
    doi       = {10.5281/zenodo.12156328},
    publisher = {Zenodo},
    year      = {2024}
}
```

## Credits
lhcb-ftcalib is designed to produce results compatible with the [EspressoPerformanceMonitor](https://gitlab.cern.ch/lhcb-ft/EspressoPerformanceMonitor) and is meant to supersede it. It contains all EPM features as well as several more and performs better.

The EPM was originally developed by J. Wimberley and has been used in several measurements

### For developers
#### Testing multiple python versions via tox
<details>
<summary>Click to expand</summary>

To test lhcb_ftcalib in different python environments, interpreters for each
version need to be installed. Multiple python versions can be installed with `pyenv`:
```bash
CC=clang pyenv install 3.6.15
pyenv install 3.7.13
pyenv install 3.8.13
pyenv install 3.9.13
pyenv install 3.10.5
pyenv install 3.11.8
pyenv install 3.12.2
```
Whereby only missing versions need to be installed! Note that python 3.6 has
issues with pip throwing segfaults if not built with clang. To make the newly
installed versions globally available run
```bash
pyenv global 3.6.15 3.7.13 3.8.13 3.9.13 3.10.5 3.11.8 3.12.2
```
and add `$HOME/.pyenv/shims` to your `PATH`.
To run the basic tests, execute
```bash
tox
```
in the lhcb_ftcalib directory
</details>
