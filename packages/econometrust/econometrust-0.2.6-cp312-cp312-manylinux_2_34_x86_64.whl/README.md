# Econometrust

A Python library for econometric regression analysis, implemented in Rust for computational efficiency.

[![License](https://img.shields.io/badge/license-MIT%2FApache--2.0-blue)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![Rust](https://img.shields.io/badge/rust-stable-orange.svg)](https://www.rust-lang.org/)

## Overview

EconoMetrust provides implementations of fundamental econometric estimators with comprehensive statistical inference capabilities. The library is designed for researchers, analysts, and practitioners who need reliable econometric tools with detailed diagnostic output.

## Estimators

- **OLS (Ordinary Least Squares)**: Standard linear regression with optional robust standard errors
- **WLS (Weighted Least Squares)**: Regression with known heteroskedastic error structure
- **GLS (Generalized Least Squares)**: Regression with known error covariance matrix
- **Ridge (Ridge Regression)**: L2 regularized linear regression for multicollinearity and overfitting
- **IV (Instrumental Variables)**: Consistent estimation for exactly identified endogenous models
- **TSLS (Two-Stage Least Squares)**: Consistent estimation for overidentified endogenous models
- **FE (Fixed Effects)**: Panel data regression with entity-specific fixed effects

## Installation

```bash
pip install econometrust
```

## Basic Usage

### Ordinary Least Squares

```python
import numpy as np
from econometrust import OLS

# Prepare data
X = np.random.randn(100, 3)
y = X @ [1.5, -2.0, 0.5] + np.random.randn(100) * 0.1

# Fit model
model = OLS(fit_intercept=True, robust=False)
model.fit(X, y)

# View results
print(model.summary())
print(f"R-squared: {model.r_squared:.4f}")
```

### Weighted Least Squares

```python
from econometrust import WLS

# Data with heteroskedastic errors
X = np.random.randn(100, 2)
weights = np.exp(X[:, 0])  # Known variance structure
y = X @ [1.0, -0.5] + np.random.randn(100) / np.sqrt(weights)

# Fit weighted model
model = WLS(fit_intercept=True)
model.fit(X, y, weights)
print(model.summary())
```

### Instrumental Variables

```python
from econometrust import IV

# Generate IV data
n = 200
Z = np.random.randn(n, 2)  # Instruments
u = np.random.randn(n)     # Unobserved confounder

# Endogenous regressors
X = Z @ [0.8, 0.6] + 0.5 * u + np.random.randn(n, 2) * 0.1
y = X @ [1.0, -0.5] + u + np.random.randn(n) * 0.1

# Fit IV model (exactly identified)
model = IV(fit_intercept=True)
model.fit(Z, X, y)
print(model.summary())
```

### Two-Stage Least Squares

```python
from econometrust import TSLS

# Overidentified case (more instruments than regressors)
n = 300
Z = np.random.randn(n, 4)  # 4 instruments
u = np.random.randn(n)

# 2 endogenous regressors
X = Z @ [0.7, 0.5, 0.4, 0.3] + 0.6 * u + np.random.randn(n, 2) * 0.1
y = X @ [1.2, -0.8] + u + np.random.randn(n) * 0.1

# Fit TSLS model
model = TSLS(fit_intercept=True)
model.fit(Z, X, y)
print(model.summary())
```

### Ridge Regression

```python
from econometrust import Ridge

# Generate data with multicollinearity
np.random.seed(42)
X = np.random.randn(100, 5)
X[:, 4] = X[:, 0] + 0.1 * np.random.randn(100)  # Correlated feature
beta_true = [1.5, -2.0, 0.5, 1.0, 0.0]
y = X @ beta_true + 0.1 * np.random.randn(100)

# Fit Ridge regression with L2 regularization
model = Ridge(alpha=1.0, fit_intercept=True)
model.fit(X, y)
print(model.summary())
print(f"Regularization strength: {model.alpha}")
```

### Fixed Effects

```python
from econometrust import FE

# Generate panel data: 100 entities, 8 time periods each
N, T = 100, 8
n_obs = N * T

# Entity identifiers
entity_id = np.repeat(np.arange(N), T)

# Generate data with entity fixed effects
np.random.seed(42)
alpha = np.random.randn(N) * 2.0  # Entity fixed effects
X = np.random.randn(n_obs, 3)

# Outcome with entity effects and time-varying component
y = np.repeat(alpha, T) + X @ [1.5, -2.0, 0.8] + np.random.randn(n_obs) * 0.1

# Fit Fixed Effects model with clustered standard errors
model = FE(robust=True)
model.fit(X, y, entity_id)
print(model.summary())
```

## API Reference

### Common Methods

All estimators share the following interface:

```python
# Initialization
model = Estimator(fit_intercept=True)

# Fitting
model.fit(...)  # Parameters vary by estimator

# Prediction
predictions = model.predict(X)

# Results
print(model.summary())
model.coefficients          # Coefficient estimates
model.intercept             # Intercept term (if fitted)
model.residuals             # Residuals
model.r_squared             # R-squared
model.mse                   # Mean squared error
model.n_samples             # Number of observations
model.n_features            # Number of features
```

### Statistical Inference

```python
# Standard errors and significance tests
model.standard_errors()     # Standard errors
model.t_statistics()        # t-statistics
model.p_values()           # p-values
model.confidence_intervals(alpha=0.05)  # Confidence intervals

# Covariance matrix
model.covariance_matrix()   # Parameter covariance matrix
```

### Estimator-Specific Parameters

#### OLS
```python
OLS(fit_intercept=True, robust=False)
# robust: Use heteroskedasticity-robust (HC0) standard errors
```

#### WLS
```python
WLS(fit_intercept=True)
model.fit(X, y, weights)    # weights: positive sample weights
```

#### GLS
```python
GLS(fit_intercept=True)
model.fit(X, y, sigma)      # sigma: error covariance matrix
```

#### Ridge
```python
Ridge(alpha=1.0, fit_intercept=True)
# alpha: regularization strength (higher = more regularization)
# Handles multicollinearity and overfitting through L2 penalty
```

#### IV
```python
IV(fit_intercept=True)
model.fit(instruments, regressors, targets)
# Requires: n_instruments == n_regressors (exactly identified)
```

#### TSLS
```python
TSLS(fit_intercept=True)
model.fit(instruments, regressors, targets)
# Requires: n_instruments >= n_regressors (identified)
```

#### FE
```python
FE(robust=False)
model.fit(X, y, entity_id)
# robust: Use clustered standard errors (cluster by entity)
# entity_id: Array of entity identifiers for panel structure
```

## Output Example

The `summary()` method provides comprehensive regression output:

```
====================================
           OLS Regression Results
====================================

Dependent Variable: y              No. Observations: 100
Model: OLS                         Degrees of Freedom: 96
Method: Least Squares              R-squared: 0.830
Covariance Type: classical         Adj. R-squared: 0.825

====================================
             Coefficients
====================================
Variable    Coef      Std Err    t-stat    P>|t|    [0.025     0.975]
--------------------------------------------------------------------
const       0.0234    0.0891     0.262     0.794    -0.1536    0.2004
x1          1.4987    0.0934    16.046     0.000     1.3131    1.6843
x2         -1.9876    0.0912   -21.786     0.000    -2.1688   -1.8064
x3          0.7899    0.0888     8.896     0.000     0.6135    0.9663

Ridge regression provides similar output with regularized coefficients:

====================================
        Ridge Regression Results
====================================

Dependent Variable: y              No. Observations: 100
Model: Ridge Regression            Alpha (λ): 1.000
Method: Ridge Regression           R-squared: 0.825
Covariance Type: nonrobust         Adj. R-squared: 0.820
```

## Requirements

- Python 3.8+
- NumPy
- Rust toolchain (for building from source)

## License

This project is dual-licensed under MIT and Apache-2.0 licenses.

## Links

- [Repository](https://github.com/wdeligt/econometrust)
- [Issues](https://github.com/wdeligt/econometrust/issues)
