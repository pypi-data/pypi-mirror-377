import numpy as np
from scipy.optimize import minimize
from sklearn.metrics.pairwise import pairwise_kernels
from numba import njit, prange
from .func import estimate_E_Z_given_X, estimate_h_functions, compute_beta_se, compute_beta_se_noncensor

def mawii_censor(
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
):
    config_nn = {
        'hidden_layers': hidden_layers,
        'learning_rate': learning_rate,
        'weight_decay': weight_decay,
        'batch_size': batch_size,
        'dropout_rate': dropout_rate,
        'patience': patience,
        'epochs': epochs,
        'validation_split': validation_split,
        'shuffle': shuffle,
        'device': device
    }

    A = np.ravel(A)
    Y = np.ravel(Y)
    censor_delta = np.ravel(censor_delta)
    n = Z.shape[0]
    m = Z.shape[1]
    X_train, Z_train, A_train, Y_train, censor_train = X, Z, A, Y, censor_delta
    
    # Kernel & weight matrix
    OA_i = np.hstack((A_train[:,None], X_train, Z_train))
    K = pairwise_kernels(OA_i, OA_i, metric='rbf', gamma=2/h**2,n_jobs=-1)
    B = K/np.sum(K,axis=0)
    mask_y       = (Y_train[:,None] <= Y_train[None,:])
    mask_y_delta = mask_y & (censor_train[:,None] == 0)
    H = mask_y.astype(np.int8).dot(B)
    H = np.maximum(H, 0.01)
    
    @njit(parallel=True)
    def compute_Gn_fast(B, H, mask_y_delta):
        n = B.shape[0]
        Gn = np.ones(n, dtype=np.float64)
        for i in prange(n):
            g = 1.0
            for j in range(n):
                if mask_y_delta[j, i]:
                    g *= 1.0 - B[j, i] / H[j, i]
            Gn[i] = g if g >= 0.01 else 0.01
        return Gn
    
    Gn = compute_Gn_fast(B, H, mask_y_delta)
    IPW = censor_train/Gn  
    
    @njit(parallel=True)
    def compute_Phi_fast(Bji, Gn, Y_train, censor_train):
        m, n = Bji.shape
    
        Hji = np.empty((m, n), dtype=np.float64)
        for i in prange(m):
            yi = Y_train[i]
            for j in range(n):
                acc = 0.0
                for l in range(m):
                    if yi <= Y_train[l]:
                        acc += Bji[l, j]
                Hji[i, j] = acc if acc >= 0.1 else 0.1
    
        Phi = np.zeros((m, n), dtype=np.float64)
        for i in prange(m):
            yi = Y_train[i]
            ci = censor_train[i]
            dm_i = 1.0 if ci == 0 else 0.0
    
            for j in range(n):
                mj = 1.0 if (yi <= Y_train[j] and dm_i == 1.0) else 0.0
                mj_over = mj / Hji[i, j]
    
                t1 = 0.0
                if dm_i == 1.0:
                    for k in range(m):
                        if Y_train[k] <= yi and Y_train[k] <= Y_train[j]:
                            hkj = Hji[k, j]
                            t1 += Bji[k, j] / (hkj * hkj)
    
                Phi[i, j] = Bji[i, j] * Gn[j] * (mj_over - t1)
    
        return Phi
    
    
    Phi = compute_Phi_fast(B, Gn, Y_train, censor_train)

    rho_funcs = {
        'ET': lambda v: -np.exp(v)+1,
        'EL': lambda v: np.log(1-v),
        'CUE': lambda v: -v - v**2/2
    }
    rho_derivatives = {
         'ET': {
             'rho': lambda v: np.sum(-np.exp(v) + 1),
             'rho_prime': lambda v: -np.exp(v),
             'rho_double_prime': lambda v: -np.exp(v),
         },
         'EL': {
             'rho': lambda v: np.sum(np.log(1 - v)),
             'rho_prime': lambda v: -1 / (1 - v),
             'rho_double_prime': lambda v: -1 / (1 - v) ** 2,
         },
         'CUE': {
             'rho': lambda v: np.sum(-v - v ** 2 / 2),
             'rho_prime': lambda v: -1 - v,
             'rho_double_prime': lambda v: -np.ones_like(v),
         },
     }
    
    results = {}
    
    for model in model_types:
        EZ = estimate_E_Z_given_X(X_train,Z_train,config_nn,model)
        RA,RY,h3,h4 = estimate_h_functions(X_train,Z_train,A_train,Y_train,config_nn,model)
        def compute_g(beta):
            b=beta[0]
            Delta=(RA*RY - b*RA**2)-(h3-b*h4)
            g=(Z_train - EZ)*Delta[:,None]
            g_d1=-(Z_train-EZ)*(RA**2-h4)[:,None]
            return g,g_d1
        results[model] = {}
        for rho_name in rho_function_names:
            def Q(beta):
                g,g_d1 = compute_g(beta)
                xi = B.T.dot(IPW[:,None]*g)
                psi = IPW[:,None]*(g-xi)+xi
                Sigma = psi.T.dot(psi)/psi.shape[0]
                Sigma_inv = np.linalg.pinv(Sigma+np.eye(Sigma.shape[0])*1e-3)
                lam = -psi.mean(0).dot(Sigma_inv)
                lam_psi=psi.dot(lam)
                if rho_name=='EL': lam_psi = np.minimum(0.9, lam_psi)
                Q_value = rho_funcs[rho_name](lam_psi).mean()
                return Q_value
    
            res = minimize(Q, np.random.rand(1), method='Powell', bounds=[(-10,10)])
            beta_hat=res.x[0]
            ghat,g_d1=compute_g(res.x)
            xi= B.T.dot(IPW[:,None]*ghat)
            xi_d1=B.T.dot(IPW[:,None]*g_d1)
            SE,VarQ= compute_beta_se(ghat,g_d1,Phi,IPW,Gn,xi,xi_d1,rho_derivatives,rho_name)
            tempQ = 2*n*Q(res.x)
            test=(tempQ - (m-1))/np.sqrt(2*(m-1)*(1+VarQ))
            results[model][rho_name]={'beta':beta_hat,'se':SE,'test':test}
    
    return results


def mawii_noncensor(X, Z, A, Y,
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
        ):
    
    config_nn = {
        'hidden_layers': hidden_layers,
        'learning_rate': learning_rate,
        'weight_decay': weight_decay,
        'batch_size': batch_size,
        'dropout_rate': dropout_rate,
        'patience': patience,
        'epochs': epochs,
        'validation_split': validation_split,
        'shuffle': shuffle,
        'device': device
    }
    A = np.ravel(A)
    Y = np.ravel(Y)
    n = Z.shape[0]
    m = Z.shape[1]
    X_train, Z_train, A_train, Y_train = X, Z, A, Y
    
    rho_funcs = {
        'ET': lambda v: -np.exp(v)+1,
        'EL': lambda v: np.log(1-v),
        'CUE': lambda v: -v - v**2/2
    }
    rho_derivatives = {
         'ET': {
             'rho': lambda v: np.sum(-np.exp(v) + 1),
             'rho_prime': lambda v: -np.exp(v),
             'rho_double_prime': lambda v: -np.exp(v),
         },
         'EL': {
             'rho': lambda v: np.sum(np.log(1 - v)),
             'rho_prime': lambda v: -1 / (1 - v),
             'rho_double_prime': lambda v: -1 / (1 - v) ** 2,
         },
         'CUE': {
             'rho': lambda v: np.sum(-v - v ** 2 / 2),
             'rho_prime': lambda v: -1 - v,
             'rho_double_prime': lambda v: -np.ones_like(v),
         },
     }
    
    results = {}
    
    
    for model in model_types:
        EZ = estimate_E_Z_given_X(X_train,Z_train,config_nn,model)
        RA,RY,h3,h4 = estimate_h_functions(X_train,Z_train,A_train,Y_train,config_nn,model)
        def compute_g(beta):
            b=beta[0]
            Delta=(RA*RY - b*RA**2)-(h3-b*h4)
            g=(Z_train - EZ)*Delta[:,None]
            g_d1=-(Z_train-EZ)*(RA**2-h4)[:,None]
            return g,g_d1
        results[model] = {}
        for rho_name in rho_function_names:
            def Q(b):
                g,g_d1 = compute_g(b)
                Omega = g.T.dot(g)/g.shape[0]
                inv = np.linalg.pinv(Omega+np.eye(Omega.shape[0])*1e-3)
                lam = -g.mean(0).dot(inv)
                lam_psi=g.dot(lam)
                if rho_name=='EL': lam_psi = np.minimum(0.99, lam_psi)
                return rho_funcs[rho_name](lam_psi).mean()
    
            res = minimize(Q, np.random.rand(1), method='Powell', bounds=[(-10,10)])
            beta_hat=res.x[0]
            ghat,g_d1=compute_g(res.x)
            SE= compute_beta_se_noncensor(ghat, g_d1, rho_derivatives, rho_name)
            tempQ = 2*n*Q(res.x)
            test=(tempQ - (m-1))/np.sqrt(2*(m-1))
            results[model][rho_name]={'beta':beta_hat,'se':SE,'test':test}
    
    return results

