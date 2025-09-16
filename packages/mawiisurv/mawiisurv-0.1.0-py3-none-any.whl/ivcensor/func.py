# func.py

import numpy as np
import torch
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.metrics.pairwise import pairwise_kernels
from .dnn import train_regression_model 
import numpy as np


def estimate_E_Z_given_X(X_train, Z_train, config_regression_Z, model_type='neural_network'):
    m = Z_train.shape[1]
    E_Z_given_X_train = np.zeros((X_train.shape[0], m), dtype=float)

    if model_type == 'neural_network':
        model_ZX = train_regression_model(X_train, Z_train, config_regression_Z)
        with torch.no_grad():
            X_tensor_train = torch.tensor(X_train, dtype=torch.float32).to(config_regression_Z['device'])
            E_Z_given_X_train = model_ZX(X_tensor_train).cpu().numpy()
            
    elif model_type == 'random_forest':
        # Use RandomForestRegressor with multi-output support
        model_ZX = RandomForestRegressor(n_estimators=20, max_features=0.3,
    n_jobs=-1, max_depth=10, min_samples_split=5, random_state=0)
        model_ZX.fit(X_train, Z_train)
        E_Z_given_X_train = model_ZX.predict(X_train)
        
    elif model_type == 'xgboost':
        model_ZX = MultiOutputRegressor(XGBRegressor(n_estimators=20, random_state=0, verbosity=0))
        model_ZX.fit(X_train, Z_train)
        E_Z_given_X_train = model_ZX.predict(X_train)
        
    elif model_type == 'linear_regression':
        # Use LinearRegression with multi-output support
        model_ZX = LinearRegression()
        model_ZX.fit(X_train, Z_train)
        E_Z_given_X_train = model_ZX.predict(X_train)

    else:
        raise ValueError(f"Unknown model type: {model_type}")

    return  E_Z_given_X_train

def estimate_h_functions(X_train, Z_train, A_train, Y_train, config_regression_A, model_type='neural_network'):
    # Helper function to get the appropriate model
    def get_model():
        if model_type == 'neural_network':
            return train_regression_model
        elif model_type == 'random_forest':
            return RandomForestRegressor(n_estimators=100, max_features=0.3,
    n_jobs=-1, max_depth=10, min_samples_split=5, random_state=0)
        elif model_type == 'xgboost':
            return XGBRegressor(n_estimators=20, random_state=0, verbosity=0)
        elif model_type == 'linear_regression':
            return LinearRegression()
        elif model_type == 'mean':
            return None
        else:
            raise ValueError(f"Unknown model type: {model_type}")

    # Function to estimate h1
    def estimate_h1():
        XZ_input_train = np.hstack([X_train, Z_train])
        A_output_train = A_train.reshape(-1, 1)

        if model_type == 'neural_network':
            model_AXZ = train_regression_model(XZ_input_train, A_output_train, config_regression_A)
            with torch.no_grad():
                XZ_tensor_train = torch.tensor(XZ_input_train, dtype=torch.float32).to(config_regression_A['device'])
                h1_train = model_AXZ(XZ_tensor_train).cpu().numpy().flatten()
        elif model_type in ['random_forest', 'xgboost', 'linear_regression']:
            model_AXZ = get_model()
            model_AXZ.fit(XZ_input_train, A_output_train.ravel())
            h1_train = model_AXZ.predict(XZ_input_train).flatten()
        else :            
            h1_train = np.full(X_train.shape[0], A_train.mean())
        return h1_train

    # Function to estimate h2
    def estimate_h2():
        XZ_input_train = np.hstack([X_train, Z_train])
        Y_output_train = Y_train.reshape(-1, 1)

        if model_type == 'neural_network':
            model_YXZ = train_regression_model(XZ_input_train, Y_output_train, config_regression_A)
            with torch.no_grad():
                XZ_tensor_train = torch.tensor(XZ_input_train, dtype=torch.float32).to(config_regression_A['device'])
                h2_train = model_YXZ(XZ_tensor_train).cpu().numpy().flatten()
        elif model_type in ['random_forest', 'xgboost', 'linear_regression']:
            model_YXZ = get_model()
            model_YXZ.fit(XZ_input_train, Y_output_train.ravel())
            h2_train = model_YXZ.predict(XZ_input_train).flatten()
        else :            
            h2_train = np.full(X_train.shape[0], Y_train.mean())
        return  h2_train


    h1_train = estimate_h1()
    h2_train = estimate_h2()

    RA_train = A_train - h1_train
    RY_train = Y_train - h2_train

    # Function to estimate h3
    def estimate_h3():
        RA_RY_train = RA_train * RY_train
        RA_RY_output_train = RA_RY_train.reshape(-1, 1)

        if model_type == 'neural_network':
            model_RA_RY_X = train_regression_model(X_train, RA_RY_output_train, config_regression_A)
            with torch.no_grad():
                X_tensor_train = torch.tensor(X_train, dtype=torch.float32).to(config_regression_A['device'])
                h3_train = model_RA_RY_X(X_tensor_train).cpu().numpy().flatten()
        elif model_type in ['random_forest', 'xgboost', 'linear_regression']:
            model_RA_RY_X = get_model()
            model_RA_RY_X.fit(X_train, RA_RY_output_train.ravel())
            h3_train = model_RA_RY_X.predict(X_train).flatten()
        else:
            h3_train = np.full(X_train.shape[0], RA_RY_train.mean())
            
        return h3_train

    # Function to estimate h4
    def estimate_h4():
        RA_squared_train = RA_train ** 2
        RA_squared_output_train = RA_squared_train.reshape(-1, 1)

        if model_type == 'neural_network':
            model_RA_squared_X = train_regression_model(X_train, RA_squared_output_train, config_regression_A)
            with torch.no_grad():
                X_tensor_train = torch.tensor(X_train, dtype=torch.float32).to(config_regression_A['device'])
                h4_train = model_RA_squared_X(X_tensor_train).cpu().numpy().flatten()
        elif model_type in ['random_forest', 'xgboost', 'linear_regression']:
            model_RA_squared_X = get_model()
            model_RA_squared_X.fit(X_train, RA_squared_output_train.ravel())
            h4_train = model_RA_squared_X.predict(X_train).flatten()
        else:
            h4_train = np.full(X_train.shape[0], RA_squared_train.mean())
            
        return h4_train

    h3_train = estimate_h3()
    h4_train = estimate_h4()

    return RA_train, RY_train, h3_train, h4_train
    

def compute_beta_se(g_i, g_d1_i, Phin_ji, IPW, Gn_OA, xi_i, xi_d1_i, rho_derivatives, rho_name):
    
    g_bar = np.mean(g_i, axis=0)
    g_d1_bar = np.mean(g_d1_i, axis=0)
    xi_bar = np.mean(xi_i, axis=0)
    xi_d1_bar = np.mean(xi_d1_i, axis=0)
    psi_i = IPW[:,np.newaxis] * (g_i - xi_i) + xi_i
    psi_d1_i = IPW[:,np.newaxis] * (g_d1_i - xi_d1_i) + xi_d1_i
    psi_bar_i = np.mean(psi_i, axis=0)
    
    n_train, m = g_i.shape
    n_est = Phin_ji.shape[0]
    
    Omega = (1 / n_train) * (psi_i.T @ psi_i)  # m x m matrix
    Omega_inv = np.linalg.pinv(Omega+np.eye(m)*1e-3)

    Omega_d1 = (1 / n_train) * (psi_d1_i.T @ psi_i + psi_i.T @ psi_d1_i)  # m x m matrix
    Omega_d2 = (2 / n_train) * (psi_d1_i.T @ psi_d1_i)  # m x m matrix
    Omega_inv_d1 = -Omega_inv @ Omega_d1 @ Omega_inv
    Omega_inv_d2 = -2*Omega_inv_d1 @ Omega_d1 @ Omega_inv - Omega_inv @ Omega_d2 @ Omega_inv
    psi_bar = np.mean(psi_i, axis=0)
    psi_d1_bar = np.mean(psi_d1_i, axis=0)
    psi_bar_Omega_inv = -psi_bar @ Omega_inv  # m * 1
    psi_bar_Omega_inv_d1 = -psi_d1_bar @ Omega_inv - psi_bar @ Omega_inv_d1
    psi_bar_Omega_inv_d2 = -2*psi_d1_bar @ Omega_inv_d1 - psi_bar @ Omega_inv_d2
    
    psi_bar_dG = (g_bar-xi_bar)
    psi_d1_bar_dG = (g_d1_bar-xi_d1_bar)
    Omega_dG_inv = -Omega_inv@(np.outer(psi_bar_dG,psi_bar_i)+ np.outer(psi_bar_i,psi_bar_dG))@Omega_inv

    s_i = psi_i @ psi_bar_Omega_inv
    # Compute partial_s_i
    s_i_d1 = psi_d1_i @ psi_bar_Omega_inv + psi_i @ psi_bar_Omega_inv_d1  # n-dimensional vector
    s_i_d2 = 2* psi_d1_i @ psi_bar_Omega_inv_d1 + psi_i @ psi_bar_Omega_inv_d2  # n-dimensional vector
    # Get rho derivatives
    rho_prime = rho_derivatives[rho_name]['rho_prime']
    rho_double_prime = rho_derivatives[rho_name]['rho_double_prime']
    rho_prime_s_i = rho_prime(s_i)            # n-dimensional vector
    rho_double_prime_s_i = rho_double_prime(s_i)  # n-dimensional vector

    # Compute H (scalar)
    H = np.mean(rho_double_prime_s_i * (s_i_d1 ** 2) + rho_prime_s_i * s_i_d2)

    weights = rho_prime_s_i / np.sum(rho_prime_s_i)  # n-dimensional vector
    D = psi_d1_i.T @ weights  # m-dimensional vector
    # Compute variance of Gn-G
    term1 = rho_double_prime_s_i*(((xi_i-g_i)@ psi_bar_Omega_inv )* (psi_d1_i @ psi_bar_Omega_inv))*IPW/Gn_OA
    term2 = rho_prime_s_i*((xi_d1_i-g_d1_i)@ psi_bar_Omega_inv)*IPW /Gn_OA
    VarG =  (H ** -2) * np.sum((Phin_ji @ (term1+term2))** 2)/ n_train**2 * n_est  

    Varbeta = (H ** -2) * (D.T @ Omega_inv @ D)/ n_train  # Scalar 
    SE = np.sqrt(Varbeta+VarG)  # Standard Error
    VarQ = 2*np.sum((Phin_ji @ (rho_prime_s_i*((xi_i-g_i)@ psi_bar_Omega_inv)*IPW /Gn_OA))** 2)/(m*n_train) * n_est
    return SE, VarQ

def compute_beta_se_noncensor(g_i, G_i, rho_derivatives, rho_name):
    n_est, m = g_i.shape

    # Compute Omega_hat
    Omega = (1 / n_est) * (g_i.T @ g_i)  # m x m matrix
    Omega_inv = np.linalg.pinv(Omega)

    # Compute Omega_hat_1 and Omega_hat_2
    Omega_d1 = (1 / n_est) * (G_i.T @ g_i + g_i.T @ G_i)  # m x m matrix
    Omega_d2 = (2 / n_est) * (G_i.T @ G_i)  # m x m matrix
    Omega_inv_d1 = -Omega_inv @ Omega_d1 @ Omega_inv
    Omega_inv_d2 = -2*Omega_inv_d1 @ Omega_d1 @ Omega_inv - Omega_inv @ Omega_d2 @ Omega_inv
    g_bar = np.mean(g_i, axis=0)
    G_bar = np.mean(G_i, axis=0)
    g_bar_Omega_inv = -g_bar @ Omega_inv  # m * 1
    g_bar_Omega_inv_d1 = -G_bar @ Omega_inv - g_bar @ Omega_inv_d1
    g_bar_Omega_inv_d2 = -2*G_bar @ Omega_inv_d1 - g_bar @ Omega_inv_d2
    

    s_i = g_i @ g_bar_Omega_inv
    # Compute partial_s_i
    s_i_d1 = G_i @ g_bar_Omega_inv + g_i @ g_bar_Omega_inv_d1  # n-dimensional vector
    s_i_d2 = 2* G_i @ g_bar_Omega_inv_d1 + g_i @ g_bar_Omega_inv_d2  # n-dimensional vector
    # Get rho derivatives
    rho_prime = rho_derivatives[rho_name]['rho_prime']
    rho_double_prime = rho_derivatives[rho_name]['rho_double_prime']

    # Compute rho'(s_i) and rho''(s_i)
    rho_prime_s_i = rho_prime(s_i)            # n-dimensional vector
    rho_double_prime_s_i = rho_double_prime(s_i)  # n-dimensional vector

    # Compute H (scalar)
    H = np.mean(rho_double_prime_s_i * (s_i_d1 ** 2) + rho_prime_s_i * s_i_d2)

    # Compute weights w_i
    weights = rho_prime_s_i / np.sum(rho_prime_s_i)  # n-dimensional vector

    # Compute D_0 (m-dimensional vector)
    D = G_i.T @ weights  # m-dimensional vector

    # Compute V/n (scalar)
    V = (H ** -2) * D.T @ Omega_inv @ D  # Scalar
    SE = np.sqrt(V / n_est)  # Standard Error
    

    return SE