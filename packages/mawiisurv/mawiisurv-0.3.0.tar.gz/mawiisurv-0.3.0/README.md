# mawiisurv

`mawiisurv` implements G‐estimation methods for treatment effects under endogeneity, both with and without right‐censoring, using a variety of machine‐learning and classical estimators.

---

## Features

- **Uncensor‐data** (`mawii_noncensor`)  
- **Right‐censoring** (`mawii_censor`)  
- Multiple model backends:
  - Neural networks
  - Linear regression
  - Random forests
  - XGBoost  
- Choice of Generalized Empirical Likelihood (GEL) functions:
  - Empirical Tilting (ET)
  - Empirical Likelihood (EL)
  - Continuous Updating Estimator (CUE)

---

## Installation

Install from PyPI:

```bash
pip install mawiisurv



Dependencies
Make sure you have the following installed (the minimal compatible versions shown):
numpy>=1.19
torch>=1.8
scipy>=1.5
scikit-learn>=0.24
xgboost>=1.3
numba>=0.53

If you plan to use GPU, please install a CUDA-compatible PyTorch from the official download page before installing this package.


Quick start

A runnable demo is provided below. It simulates both non-censored and right-censored data, fits the DNN + ET specification, and prints the point estimate, standard error, and the over-identification test statistic.

# demo
# pip install mawiisurv

import numpy as np
import torch
import mawiisurv

# Two main entry points:
#   mawii_noncensor(X, Z, A, Y, ...)
#   mawii_censor(X, Z, A, Y, censor_delta, ...)

# Inputs
#   X: (n, p) covariates
#   Z: (n, m) instrumental variables
#   A: (n,) treatment
#   Y: (n,) outcome
#   censor_delta: (n,) censoring indicator, 1 uncensored, 0 censored
#
# Model choices
#   model_types: ['neural_network','linear_regression','random_forest','xgboost']
#   rho_function_names: ['ET','EL','CUE']
#
# DNN hyperparameters (optional)
#   hidden_layers=[50, 50]
#   learning_rate=5e-4
#   weight_decay=1e-4
#   batch_size=256
#   dropout_rate=0
#   patience=5
#   epochs=1000
#   validation_split=0.05
#   shuffle=False
#   device='cpu' or 'cuda:0'

# ---------- simulate complete data ----------
n = 10000
m = 20
p = 1
beta_0 = 0.4
device = 'cuda:0' if torch.cuda.is_available() else 'cpu'

X = np.random.uniform(0, 1, size=(n, p))
p_Z = [0.25, 0.5, 0.25]
Z = np.random.choice([0, 1, 2], size=(n, m), p=p_Z)

gamma = np.sqrt(0.2 / (1.5*m)) * np.random.normal(0, 1, size=m)
delta = np.sqrt(0.2 / (1.5*m)) * np.random.normal(0, 1, size=m)

epsilon_A = np.random.normal(0, 0.4, size=n)
epsilon_Y = np.random.normal(0, 0.4, size=n)
U = np.random.normal(0, 0.6, size=n)

A = Z @ gamma + U + (1 + Z @ delta) * epsilon_A
Y = beta_0 * A + np.sum(X, axis=1) - U + epsilon_Y

result_noncensor = mawiisurv.mawii_noncensor(
    X, Z, A, Y,
    model_types=['neural_network'],          # options: ['neural_network','linear_regression','random_forest','xgboost']
    rho_function_names=['ET'],               # options: ['ET','EL','CUE']
    device=device
)

print(f"DNN+ET BETA: {result_noncensor['neural_network']['ET']['beta']:.3f}")
print(f"DNN+ET SE: {result_noncensor['neural_network']['ET']['se']:.3f}")
print(f"DNN+ET over-identification test: {result_noncensor['neural_network']['ET']['test']:.3f}")

# ---------- simulate right-censored data ----------
T = beta_0 * A + np.sum(X, axis=1) - U + epsilon_Y
censor_rate = 0.4
rr = 0.0

while True:
    C = np.random.uniform(0 + rr, 5 + rr, size=n)
    censor_delta = (T <= C).astype(int)
    cr = np.mean(1 - censor_delta)
    if cr >= censor_rate + 0.03:
        rr += 0.1
    elif cr <= censor_rate - 0.03:
        rr -= 0.1
    else:
        break

Y = np.minimum(T, C)

result_censor = mawiisurv.mawii_censor(
    X, Z, A, Y, censor_delta, h=1,
    model_types=['neural_network'],
    rho_function_names=['ET'],
    device=device
)

print(f"DNN+ET BETA: {result_censor['neural_network']['ET']['beta']:.3f}")
print(f"DNN+ET SE: {result_censor['neural_network']['ET']['se']:.3f}")
print(f"DNN+ET over-identification test: {result_censor['neural_network']['ET']['test']:.3f}")




API

mawii_noncensor(
    X, Z, A, Y,
    model_types=['neural_network'],
    rho_function_names=['ET'],
    hidden_layers=[50, 50],
    learning_rate=0.0005,
    weight_decay=0.0001,
    batch_size=256,
    dropout_rate=0,
    patience=5,
    epochs=100,
    validation_split=0.05,
    shuffle=False,
    device='cpu',
) -> dict
mawii_censor(
    X, Z, A, Y, censor_delta, h=1,
    model_types=['neural_network'],
    rho_function_names=['ET'],
    hidden_layers=[50, 50],
    learning_rate=0.0005,
    weight_decay=0.0001,
    batch_size=256,
    dropout_rate=0,
    patience=5,
    epochs=100,
    validation_split=0.05,
    shuffle=False,
    device='cpu',
) -> dict

Arguments

X array of shape n by p, baseline covariates

Z array of shape n by m, instrumental variables

A array of shape n, treatment

Y array of shape n, outcome

censor_delta array of shape n, 1 uncensored and 0 censored, only for mawii_censor

h scalar, window for local Kaplan–Meier in censoring adjustment

model_types list of model backends, choose from neural_network, linear_regression, random_forest, xgboost

rho_function_names list of GEL score types, choose from ET, EL, CUE

device cpu or cuda device string such as cuda:0

return values:
{
  'neural_network': {
    'ET': {
      'beta': float,    # point estimate
      'se': float,      # standard error
      'test': float     # overidentification test statistic
    },
    'EL': {...},
    'CUE': {...}
  },
  'linear_regression': {...},
  ...
}
