# demo

#  pip install mawiisurv
import numpy as np
import mawiisurv
import torch

# function input
'''
Main input variables:
    X: (n,p) array, covariates
    Z: (n,m) array, instrumental variables
    A: (n,) array, treatment
    Y: (n,) array, outcome
    censor_delta: (n,) array, censor indicator, 1 for uncensor and 0 for censor
    h: window for local KM estimation, and default setting is 1
    model_types: ['neural_network','linear_regression','random_forest','xgboost'], 4 choices of comparsion models, and default setting is ['neural_network']
    rho_function_names: ['ET','EL','CUE'], GEL functions, and default setting is ['EL']

Other DNN setting: 
    hidden_layers=[50, 50],
    learning_rate=0.0005,
    weight_decay=0.0001,
    batch_size=256,
    dropout_rate=0,
    patience=5,
    epochs=1000,
    validation_split=0.05,
    shuffle=False,
    device='cpu'
'''

# two main functions:
'''
'mawii_noncensor' for complete data
'mawii_censor' for right censor data
'''

# function output
'''
function will return a list of result, including 
    'beta' : estimation of treatment effect
    'se' : estimated standard error
    'test' : overidentification test statistics
'''

# complete data
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

A = Z @ gamma + U + (1 + Z @ delta)*epsilon_A
Y = beta_0*A + np.sum(X,axis=1) - U  + epsilon_Y

result_noncensor = mawiisurv.mawii_noncensor(X, Z, A, Y, 
                          model_types= ['neural_network'], # more options: ['neural_network','linear_regression','random_forest','xgboost'],
                          rho_function_names=['ET'], # more options: ['ET','EL','CUE'],
                          device = device)

print(f"DNN+ET BETA: {result_noncensor['neural_network']['ET']['beta']:.3f}")
print(f"DNN+ET SE: {result_noncensor['neural_network']['ET']['se']:.3f}")
print(f"DNN+ET over-identification test: {result_noncensor['neural_network']['ET']['test']:.3f}")


# right-censor data simulation
T = beta_0*A + np.sum(X,axis=1) - U  + epsilon_Y
censor_rate = 0.4
rr = 0

while True:
    C = np.random.uniform(0+rr,5+rr, size=n)
    censor_delta = np.where(T <= C, 1, 0) 
    if np.mean(1-censor_delta) >=censor_rate+0.03:
        rr = rr + 0.1
    elif np.mean(1-censor_delta)<=censor_rate-0.03:
        rr = rr - 0.1
    else:
         break
        
Y = np.minimum(T,C)

result_censor = mawiisurv.mawii_censor(X, Z, A, Y, censor_delta, h = 1,
                                       model_types= ['neural_network'], # more options: ['neural_network','linear_regression','random_forest','xgboost'],
                                       rho_function_names=['ET'], # more options: ['ET','EL','CUE'],
                                       device = device)

print(f"DNN+ET BETA: {result_censor['neural_network']['ET']['beta']:.3f}")
print(f"DNN+ET SE: {result_censor['neural_network']['ET']['se']:.3f}")
print(f"DNN+ET over-identification test: {result_censor['neural_network']['ET']['test']:.3f}")


