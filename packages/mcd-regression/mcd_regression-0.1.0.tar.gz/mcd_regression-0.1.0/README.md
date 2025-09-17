# mcd_regression

Python implementation of robust linear regression in the multiple regression and multivariate regression cases using the minimum covariance determinant (MCD).

Usage ([docs/examples/example.ipynb](https://github.com/stevenstetzler/mcd_regression/tree/main/docs/examples/example.ipynb)):
```python
>>> from mcd_regression import MCDRegression
>>> mcdr = MCDRegression()
>>> x = data[:, 0, None] # n x d_x, must be 2D
>>> y = data[:, 1:] # n x d_y, must be 2D
>>> mcdr.fit(x, y)
>>> residuals = y - mcdr.predict(x)
>>> slope = mcdr.beta
>>> intercept = mcdr.alpha
```

Installation:
- Available via PyPI as `mcd-regression`
```bash
$ python -m pip install mcd-regression
```

- Development
```bash
$ git clone https://github.com/stevenstetzler/mcd_regression.git
$ python -m pip install -e mcd_regression
```

References:
- Peter J Rousseeuw, Stefan Van Aelst, Katrien Van Driessen & Jose A Gulló (2004) Robust Multivariate Regression, Technometrics, 46:3, 293-305, DOI: [10.1198/004017004000000329](https://doi.org/10.1198/004017004000000329)
