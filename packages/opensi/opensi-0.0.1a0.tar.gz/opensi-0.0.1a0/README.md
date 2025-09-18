# OpenSI: Open-source Selective Inference

[![PyPI version](https://badge.fury.io/py/OpenSI.svg)](https://badge.fury.io/py/OpenSI)
[![License](https://anaconda.org/conda-forge/pot/badges/license.svg)](https://github.com/OpenSI/OpenSI/blob/master/LICENSE)

This open source Python library provides APIs for selective inference for problems in machine learning such as feature selection, anomaly detection and domain adaptation.

Website and documentation: [https://OpenSI.github.io/](https://OpenSI.github.io/)

Source code (MIT): [https://github.com/OpenSI/OpenSI](https://github.com/OpenSI/OpenSI)

## Implemented Features

OpenSI have provide selective inference support for methods:

* Feature Selection:
    * Lasso Feature Selection
    * Sequential Feature Selection
* Domain Adaptation:
    * Optimal Transport-based Domain Adaptation

## Installation

The library has only been tested on Windows with Python 3.10. It requires some of the following modules:
- numpy (=2.2.6)
- mpmath (=1.3.0)
- POT (==0.9.5)
- scikit-learn (==1.7.1)
- scipy (==1.15.3)

Note: Other versions of Python and dependencies shall be tested in the future.

### Pip Installation

You can install the toolbox through PyPI with:

```console
pip install OpenSI
```

### Post installation check
After a correct installation, you should be able to import the module without errors:

```python
import opensi
```

## Examples and Notebooks

The examples folder contain several examples and use case for the library. The full documentation with examples and output is available on [https://OpenSI.github.io/](https://OpenSI.github.io/).