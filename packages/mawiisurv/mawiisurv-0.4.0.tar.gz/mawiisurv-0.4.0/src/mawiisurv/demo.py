# demo

#  pip install mawiisurv
import numpy as np
import mawiisurv
import torch
import copy
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

# complete data simulation
n = 10000
m = 20
p = 1
beta_0 = 0.4
device = 'cuda:0' if torch.cuda.is_available() else 'cpu'


def generate_data(n=10000, m=10, p=5, beta_0=0.4, h_2=0.2,eta_A=1,censor_rate=0.3, case='case1'):
    random_coefs = np.random.normal(loc=0, scale=1, size=1000)
    
    X = np.random.uniform(-2,2,size=(n,p))
    Z = np.random.uniform(-2,2,size=(n,m))

    gamma = np.sqrt(h_2 / (1.5*m)) * random_coefs[0 : m] 
    delta = np.sqrt(h_2 / (1.5*m)) * random_coefs[m : 2*m]

    epsilon_A = np.random.normal(0, 0.4*(1-h_2), size=n)
    epsilon_Y = np.random.normal(0, 0.4*(1-h_2), size=n)
    

    alpha_case1 = np.zeros(m)
    alpha_case2 = np.sqrt(h_2 / (1.5*m)) * (random_coefs[2*m : 3*m])/2
    alpha_case3 = gamma / 2
    Z_new = copy.deepcopy(Z)
    Z_new = np.cos(Z*2)

    
    if case == "case1":
        tmp = np.random.multinomial(1, [1, 0, 0], size=m)
    elif case == "case2":
        tmp = np.random.multinomial(1, [0.6, 0.2, 0.2], size=m)
    elif case == "case3":
        tmp = np.random.multinomial(1, [0.1, 0.9, 0], size=m)
    elif case == "case4":
        tmp = np.random.multinomial(1, [0.1, 0, 0.9], size=m)
    else:
        raise ValueError("Unknown case provided.")
    alpha = tmp[:, 0] * alpha_case1 + tmp[:, 1] * alpha_case2 + tmp[:, 2] * alpha_case3

    U = np.random.normal(0, 0.6*(1-h_2), size=n)
    A = Z_new @ gamma + U + (1 + Z @ delta)*epsilon_A
    T = beta_0*A  + Z_new @ alpha -U  + epsilon_Y 

    rr = 0
    
    while True:
        C = np.random.uniform( -1+rr,5+rr, size=n)
        censor_delta = np.where(T <= C, 1, 0) 
        if np.mean(1-censor_delta) >=censor_rate+0.03:
            rr = rr + 0.1
        elif np.mean(1-censor_delta)<=censor_rate-0.03:
            rr = rr - 0.1
        else:
             break
            
    Y = np.minimum(T,C)
 
    return X, Z, A, Y, T, censor_delta

X, Z, A, Y, T, censor_delta= generate_data(n=10000, m=20, p=1, beta_0=0.4, h_2=0.2, eta_A=1, censor_rate=0.4, case='case1')


# uncensored data simulation

result_noncensor = mawiisurv.mawii_noncensor(X, Z, A, T, 
                          model_types=['neural_network','linear_regression','random_forest','xgboost'],
                          rho_function_names=['ET','EL','CUE'],
                          device = device)

print(f"DNN+ET BETA: {result_noncensor['neural_network']['ET']['beta']:.3f}")
print(f"DNN+ET SE: {result_noncensor['neural_network']['ET']['se']:.3f}")
print(f"DNN+ET over-identification test: {result_noncensor['neural_network']['ET']['test']:.3f}")


# right-censor data simulation

result_censor = mawiisurv.mawii_censor(X, Z, A, Y, censor_delta, h = 4,
                                          model_types=['neural_network'],
                                          rho_function_names=['ET'],
                                          device = device)

print(f"DNN+ET BETA: {result_censor['neural_network']['ET']['beta']:.3f}")
print(f"DNN+ET SE: {result_censor['neural_network']['ET']['se']:.3f}")
print(f"DNN+ET over-identification test: {result_censor['neural_network']['ET']['test']:.3f}")
    

