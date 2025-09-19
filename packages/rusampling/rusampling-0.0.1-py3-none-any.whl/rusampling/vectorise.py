import numpy as np

def vectorise_1d(f):
    '''
    Passed f, which deals with a one-dimensional number, establishes the expected input and output and returns a function that accepts a (n, 1) array and returns a (n) array.
    '''

    def f_1(x):
        return np.asarray([f(x_i) for x_i in x[:, 0]])
    def f_2(x):
        return f(x[:,0])
    def f_3(x):
        return f(x)[:,0]
    def f_5(x):
        return np.asarray([f(np.asarray([x_i]))[0] for x_i in x[:, 0]])
    def f_6(x):
        return np.asarray([f(np.asarray([x_i])) for x_i in x[:, 0]])

    fs = [f_1, f_2, f_3, f, f_5, f_6]
    n = 5
    try:
        test_0 = f(np.ones((n, 1)))
        if test_0.shape == (n, 1):
            case = 3
        elif test_0.shape == (n,):
            case = 4
        else:
            case = -1
    except Exception:
        try:
            test_1 = f(np.ones(n))
            if len(test_1) == n:
                case = 2
            else:
                case = -1
        except Exception:
            try:
                test_3 = f(np.ones(1))
                if isinstance(test_3, int) or isinstance(test_3, float):
                    case = 6
                elif len(test_3) == 1:
                    case = 5
                else:
                    case = -1
            except Exception:
                test_4 = f(1)
                if isinstance(test_4, int) or isinstance(test_4, float):
                    case = 1
                else:
                    case = -1

    if case == -1:
        raise Exception('Check that f is vectorised correctly, e.g. takes an nD array and returns an nD array.')
    else:
        return fs[case - 1]
    



def vectorise_dd(f, d):
    '''
    Passed f, which deals with a d-dimensional number, establishes the expected input and output and returns a function that accepts a (n, d) array and returns a (n) array.
    '''
    def f_1(x):
        return f(x)[:, 0]
    def f_2(x):
        y = np.zeros(x.shape[0])
        for i in range(x.shape[0]):
            y[i] = f(x[i, :])[0]
        return y
    def f_3(x):
        y = np.zeros(x.shape[0])
        for i in range(x.shape[0]):
            y[i] = f(x[i, :])
        return y
    fs = [f, f_1, f_2, f_3]

    n = d*2
    try:
        test_0 = f(np.ones((n, d)))
        if len(test_0) == n:
            case = 0
        elif test_0.shape == (n, 1):
            case = 1
        else:
            case = -1
    except Exception:
        try:
            test_1 = f(np.ones(d))
            if isinstance(test_1, int) or isinstance(test_1, float):
                case = 3
            elif len(test_1) == 1:
                case = 2
            else:
                case = -1
        except Exception:
            case = -2

    if case == -2:
        raise Exception('Check that f is vectorised correctly, e.g. takes an (n, d) array and returns an (n) array (not the parameters individually).')
    elif case == -1:
        raise Exception('Check that f is vectorised correctly, e.g. takes an (n, d) array and returns an (n) array.')
    else:
        return fs[case]


def vectorise_2(f):
    '''
    Passed f: (n,d) -> (n) (including when d=1), adds the functionality (d) -> float.
    '''
    # In some, perhaps most, cases this is unnecessary, but I do not think it will slow down the code that much comparatively to the optimisation part.  
    def f_new(x):                                    
        if len(x.shape)==1:
            return f(np.expand_dims(x, axis=0))[0]
        else:
            return f(x)
    return f_new


def vectorise(f, d):
    # Combines vectorise_2 with either vectorise_1d or vectorise_dd
    if d == 1:
        f_temp = vectorise_1d(f)
    else:
        f_temp = vectorise_dd(f, d)
    f_temp_2 = vectorise_2(f_temp)
    return f_temp_2



def input_matches_output(g, d):
    n = d*3
    
    if d==1:
        try:
            y = g(np.ones((n, 1)))
            if y.shape == (n, 1):
                case = 0
            else:
                case = -1
        except Exception:
            y = g(1)
            if isinstance(y, int) or isinstance(y, float):
                case = 1
            else:
                case = -1

    else:
        try:
            y = g(np.ones((n, d)))
            if y.shape == (n, d):
                case = 0
            else:
                case = -1
        except Exception:
            y = g(np.ones(d))
            if len(y) == d:
                case = 1
            else:
                case = -1

    if case == -1:
        raise Exception('Output of X_to_x must be of the same type as the input, be this array or scalar.')
    if case == 0:
        g_temp = g
    if case == 1:
        def g_temp(x):
            y = np.zeros(x.shape[0])
            for i in range(x.shape[0]):
                y[i] = g(x[i, :])
            return y
    
    return vectorise_2(g_temp)