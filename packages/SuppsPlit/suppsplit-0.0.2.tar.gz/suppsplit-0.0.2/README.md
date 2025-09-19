# Python Wrapper for R package sPlit

sPlit: Split a Dataset for training and testing based on the idea of support points

Reference: Joseph, V. R., & Vakayil, A. (2022). SPlit: An optimal method for data splitting. Technometrics, 64(2), 166-176.

## Installation

Open a command terminal.

```console
git clone https://github.com/PanyiDong/SuppsPlit.git
cd SuppsPlit
python setup.py build_ext --inplace
```

## Usage

```python
import pandas as pd
import numpy as np
from SuppsPlit import SPlit

# toy dataset
df = pd.DataFrame({
    "X": np.random.randn(100),
    "Y": np.random.randn(100)
})

indices = SPlit(df, split_ratio=0.2, n_threads=2)
print("Test indices:", indices)
```