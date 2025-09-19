import numpy as np
import scipy


def vectorisation_test(f, d):
    '''
    Checks that f is vectorised as claimed.
    if is_not_vectorised, f: (d) -> float
    if not is_not_vectorised, f: (n, d) -> (n)
    '''
    fail = False

    x_1 = np.zeros(d)
    y_1 = f(x_1)
    if not (isinstance(y_1, float) or isinstance(y_1, int)):
        print('f fails test (d) -> float')
        fail = True
    
    n = 5
    x_shape = (n, d)
    x = np.ones(x_shape)
    y = f(x)
    if len(y.shape)!= 1 or len(y) != n:
        print('f fails test (n, d) -> (n)')
        fail = True
        
    if fail:
        raise Warning("logf failed Ru's vectorisation test. Either logf: (n, d) -> (n) (recommended) or logf: (d) -> float with vectorise=True. Ignore this test with ignore_test=True.")



def mode_relocate_logf(f, ics, method):
    '''Passed a function log, mode-relocates it and scales additively to 0; returns the scaled function, maximum and mode.'''
    #assert np.isfinite(f(ics)), 'logf is unbounded at initial conditions provided.'
    # ^ somehow works even if this holds

    optimise_result = scipy.optimize.minimize(lambda x: -f(x), ics, method=method)
    mode = optimise_result.x
    fmax = -optimise_result.fun

    if not optimise_result.success:
        print(f'Optimisation routine ({method}) failed maximise logf: {optimise_result.message}')

    assert np.isfinite(fmax), 'Unable to maximise of logf, either because it is unbounded, or better initial conditions are needed.'

    def f_scaled(x):
        return f(x + mode) - fmax
    
    return f_scaled, fmax, mode


def yeojohnson_x(x, lmbda):
    '''Applies an inverse Yeo-Johnson transformation to x, a d-dimensional array or (n,d) array (lmbda having length d).'''
    x_transformed = np.zeros(x.shape)
    x_pos = (x > 0)
    lmbda_b = np.broadcast_to(lmbda, x.shape)
    lmbda_zero = (lmbda_b == 0)
    lmbda_two = (lmbda_b == 2)

    mask_0 = np.logical_and(x_pos, lmbda_zero)
    mask_1 = np.logical_and(x_pos, ~lmbda_zero)
    mask_2 = np.logical_and(~x_pos, lmbda_two)
    mask_3 = np.logical_and(~x_pos, ~lmbda_two)

    x_transformed[mask_0] = np.exp(x[mask_0]) - 1
    x_transformed[mask_1] = (1 + x[mask_1]*lmbda_b[mask_1])**(1/lmbda_b[mask_1]) - 1
    x_transformed[mask_2] = 1 - np.exp(-x[mask_2])
    x_transformed[mask_3] = 1 - (1 + x[mask_3]*(lmbda_b[mask_3]-2))**(1/(2-lmbda_b[mask_3]))

    return x_transformed


def yeojohnson_logdet(x, lmbda):
    '''
    Log-magnitude-determinant of Jacobian of inverse Yeo-Johnson transformation.
    Vectorised: (n, d) -> (n) OR (d) -> float
    '''
    out = np.zeros(x.shape)
    x_pos = (x > 0)
    lmbda_b = np.broadcast_to(lmbda, x.shape)
    lmbda_zero = (lmbda_b == 0)
    lmbda_two = (lmbda_b == 2)

    mask_0 = np.logical_and(x_pos, lmbda_zero)
    mask_1 = np.logical_and(x_pos, ~lmbda_zero)
    mask_2 = np.logical_and(~x_pos, lmbda_two)
    mask_3 = np.logical_and(~x_pos, ~lmbda_two)

    out[mask_0] = x[mask_0]
    out[mask_1] = (1/lmbda_b[mask_1] - 1) * np.log(np.abs((1 + x[mask_1]*lmbda_b[mask_1])))
    out[mask_2] = -x[mask_2]
    out[mask_3] =  (1/(2 - lmbda_b[mask_3]) - 1) * np.log(np.abs(1 + x[mask_3]*(lmbda_b[mask_3]-2)))

    logdet = np.sum(out, axis=-1)
    return logdet


def yeojohnson_logf(logf, lmbda):
    '''Applies an inverse Yeo-Johnson transformation to logf, which accepts a d-length list.'''
    def f_yj(x):
        logdet = yeojohnson_logdet(x, lmbda)
        g = logf(yeojohnson_x(x, lmbda))
        return g + logdet
    return f_yj


def get_rotation_L(logf, d):
    '''Find the Hessian of -f at the origin, and find L, the lower-triangular Choleski decomposition. Return L, det(L).'''
    def f_alt(x):     # 1. vectorise so f: (d, ...) -> (...) and 2. negative (for concavity) logf
        d, *batch_shape = x.shape
        x_flat = x.reshape(d, -1)   # shape (d, N), where N = product of batch dims
        vals = np.array([-logf(x_flat[:, i]) for i in range(x_flat.shape[1])])
        return vals.reshape(batch_shape)
    origin = np.zeros(d)
    
    initial_step = 0.1
    count = 0
    hessian_succeed = False
    while count < 3 and not hessian_succeed:
        # having a smaller initial step helps when the function is undefined near to the mode, e.g. if the modal variance is close to 0
        # repeat 3 times (arbitrarily) if it turns out to not be small enough
        # (having an unnecessarily small step size seems to result in less-hermitian Hessian so I start with 0.1)
        hessian_output = scipy.differentiate.hessian(f_alt, origin, initial_step=initial_step)
        hessian = hessian_output.ddf
        if not np.any(np.isnan(hessian)):
            hessian_succeed = True
        else:
            initial_step *= 0.5
            count += 1

    # I am choosing not to filter out when H is not Hermitian
    # because this is generally due to small numerical differences and rotation will still increase Pa
    #if not np.allclose(hessian, hessian.T):
        #print('Warning: Hessian of pdf at mode may not be Hermitian (i.e. not analytic at the mode). Not rotating.')

    L = np.identity(d)
    det = 1

    if hessian_succeed:
        if not np.all(np.linalg.eigvals(hessian) > np.finfo(float).eps):
            print('Warning: Failed to find a non-inf and pos-def Hessian. Either non-concave, or mode is too close to the boundary.')
        else:
            L = np.linalg.cholesky(hessian)
            det = np.linalg.det(L)

    return L, det**(1/d)


def rotate_x(x, L_inv, scale_factor):
    y = np.matmul(x, L_inv) * scale_factor
    return y


def rotate_f(f, L_inv, scale_factor):
    def f_rotated(X):
        x = rotate_x(X, L_inv, scale_factor)
        return f(x)
    return f_rotated