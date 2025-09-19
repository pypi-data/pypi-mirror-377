import numpy as np
import scipy
import matplotlib.pyplot as plt
from time import time as current_time

from . import ru_libs
from . import vectorise

_sentinel = object()



class Ru:
    def __init__(
            self, logf, d=1, 
            ics=_sentinel, r=0.5, 
            optim_method='Nelder-Mead',
            X_to_x=None, X_to_x_logj=None,
            YJ_lambda=_sentinel,
            rotate=True, mode_relocate=True, rectangle=None, time=False,
            **logf_args):
        '''
        Passed a posterior distribution, apply ratio of uniforms sampling and return parameter random variates.
        f accepts x, a (m, d)-dimensional (numpy) array and returns an array of length (m).

        Parameters
        ----------
        logf: function
            log of the posterior distribution
        data: array of float
            Samples from the distribution, to calculate the posterior distribution
        d: int, optional
            Number of params
        ics: array of float, optional
            Initial parameter conditions (usually MLE)
        r: float, optional
            Tuning parameter for ratio-of-uniforms method. r=0.5 by default.
        logf_args: any
            Keyword args to be passed to f.
        '''

        if time:
            absolute_time = current_time()
            times = []

        assert r>0
        self.r = r
        self.d = d
        self.power = r/(1 + r*d)
        self.power_alt = 1/(1 + r*d)
        self.ics = self._setics(ics, d)
        self.optim_method = optim_method
        self.acceptance_rate = -1     # set when rvs is called for the first time


        # Step 0: 
        f_temp = lambda x: logf(x, **logf_args)
        f_temp_vec = vectorise.vectorise(f_temp, d)
        self.f_0 = f_temp_vec


        if time:
            times.append(current_time()-absolute_time)
            absolute_time = current_time()


        # Step 1: User defined transformation
        msg = 'If providing a user-defined transformation, you must provide both X_to_x and X_to_x_jacobian.'
        assert (X_to_x != None and X_to_x_logj != None) or (X_to_x == None and X_to_x_logj == None), msg
        self.user_defined_transformation = (X_to_x != None)

        if self.user_defined_transformation:
            X_to_x_vec = vectorise.input_matches_output(X_to_x, d)
            X_to_x_jac_vec = vectorise.vectorise(X_to_x_logj, d)
            self.X_to_x = X_to_x_vec
            self.f_1 = lambda X: self.f_0(X_to_x_vec(X)) + X_to_x_jac_vec(X)
        else:
            self.f_1 = self.f_0


        # Step 2: Yeo-Johnson
        self.YJ = not (YJ_lambda is _sentinel)
        if self.YJ:
            self.YJ_lambda = np.asarray(YJ_lambda)
            self.f_2 = ru_libs.yeojohnson_logf(self.f_1, YJ_lambda)
        else:
            self.f_2 = self.f_1

        if time:
            times.append(current_time()-absolute_time)
            absolute_time = current_time()


        # Step 3: Mode relocation
        self.mode_relocate = mode_relocate
        f_3, logfmax, self.mode = ru_libs.mode_relocate_logf(self.f_2, self.ics, optim_method)
        self.fmax = np.exp(logfmax)
        assert np.isfinite(self.fmax), f'Maximum of f exceeds computational limit (max of logf = {logfmax})'
        if mode_relocate:
            self.f_3 = f_3
            self.u_max = 1
            self.ics = np.zeros(self.d)
        else:
            self.f_3 = self.f_2
            self.u_max = self.fmax ** self.power_alt

        if time:
            times.append(current_time()-absolute_time)
            absolute_time = current_time()


        # Step 4: Axes rotation
        self.rotate = (rotate and not self.d == 1)
        if self.rotate:
            self.axes_rotate_L, self.axes_rotate_scale = ru_libs.get_rotation_L(self.f_3, self.d)
            self.axes_rotate_L_inv = np.linalg.inv(self.axes_rotate_L)
            self.f_4 = ru_libs.rotate_f(self.f_3, self.axes_rotate_L_inv, self.axes_rotate_scale)
        else:
            self.f_4 = self.f_3

        if time:
            times.append(current_time()-absolute_time)
            absolute_time = current_time()


        # logf -> f
        def f(x):
            return np.exp(self.f_4(x))
        self._f = f


        if rectangle:
            self.user_supplied_rectangle = True
            self.v_min = rectangle[0, :]
            self.v_max = rectangle[1, :]
        else:
            self.user_supplied_rectangle = False
            self._init_rectangle()

        if time:
            times.append(current_time()-absolute_time)
            absolute_time = current_time()
            total_time = np.sum(np.asarray(times))
            print(f'Setup took {total_time}s.\n\tinit/YJ/mode/rotation/rectangle: {round(times[0], 3), round(times[1], 3), round(times[2], 3), round(times[3], 3), round(times[4], 3)}')


    def _setics(self, ics, d):
        if ics is _sentinel:
            ics = np.zeros(d)
        else:
            if d==1:
                if isinstance(ics, float) or isinstance(ics, int):
                    ics = np.asarray([ics])
            else:
                ics = np.asarray(ics)
                assert len(ics)==d, 'ICs provided are of incorrect dimension (d).'
        return ics
    

    def _init_rectangle(self):
        '''
            Calculates the bounding rectangle used in ratio-of-uniforms sampling for f.
            Returns nothing (run as part of __init__)
        '''
        def f_rect_v(x, i):
            if len(x.shape)==1:
                f = x[i] * self._f(x)**self.power          # float
            else:
                f = x[:,i] * self._f(x)**self.power        # (n)
            return f
        self._f_rect_v = f_rect_v

        # index 0: refers to the parameter in f_rect_i
        # index 1: the point
        self.v_min_x = np.zeros((self.d, self.d))
        self.v_max_x = np.zeros((self.d, self.d))

        # (more important) values in the rectangle
        self.v_min = np.zeros(self.d)
        self.v_max = np.zeros(self.d)

        for i in range(0, self.d):
            optim_min = scipy.optimize.minimize(lambda x: f_rect_v(x, i), self.ics, method=self.optim_method)
            optim_max = scipy.optimize.minimize(lambda x:-f_rect_v(x, i), self.ics, method=self.optim_method)
            self.v_min_x[i, :] = optim_min.x
            self.v_max_x[i, :] = optim_max.x
            self.v_min[i] = optim_min.fun
            self.v_max[i] = -optim_max.fun

        if not (optim_min.success):
            print(f'Min of auxiliary function x_{i} f(x)**{round(self.power, 3)} fails: "{optim_min.message}"')
        elif not (optim_min.success):
            print(f'Max of auxiliary function x_{i} f(x)**{round(self.power, 3)} fails: "{optim_max.message}"')

        if np.any(np.isnan(self.v_min_x + self.v_max_x)) or np.any(np.isnan(self.v_min+self.v_max)):
            self.info()
            raise Exception('Infinite values in bounding rectangle, possibly fixable with better ICS, or the tails of f may be too fat.')

    def plot_f_1d(self, x=_sentinel):
        '''
            Plot the functions maximised for the bounding rectangle, to check if the rectangle is correct.
            x is a range.
        '''
        if self.d==1:
            if x is _sentinel:
                if not self.user_supplied_rectangle:
                    x = np.linspace(self.v_min_x[0,0]*2, self.v_max_x[0,0]*2, 100)
                else:
                    x = np.linspace(-10, 10, 0.01)
            x = np.expand_dims(x, axis=-1)   # d=1 but still need extra dimension
            y_0 = self._f(x)
            y_1 = self._f_rect_v(x, 0)

            fig, axs = plt.subplots(2)
            axs[0].plot(x, y_0)
            axs[0].plot(0, 1, 'o')
            axs[0].axhline(y=1, linestyle='--')

            axs[1].plot(x, y_1)
            axs[1].axhline(y=self.v_min, linestyle='--')
            axs[1].axhline(y=self.v_max, linestyle='--')
            if not self.user_supplied_rectangle:
                axs[1].plot(self.v_min_x, self.v_min, 'o')
                axs[1].plot(self.v_max_x, self.v_max, 'o')
            plt.show()
        else:
            print('plot_f_1d for use when d=1')

    
    def plot_f_2d(self, margin=2, contour_cutoff=-999999999, maxes=True, xlim=None, ylim=None, n_points=100, levels=50):
        """
        Plots the contours of f, f_0, and f_1 along with the points where inf/sup is found, to check if the bounding rectangle is correct.

        Parameters
        ----------
        margin : float, optional
            Length to extend the plot outside of the maxima/minima (default is 2).
        contour_cutoff: float, optional
            Minimum value of f to display, for cases when f is unbounded (default is -999999999)
        maxes : bool, optional
            If True, plot the locations of the maxima and minima used for the bounding rectangle (default is True).
        xlim : array_like or None, optional
            Limits - (3,2) array - for the x-axis for each subplot. If None, calculates based off maxima positions.
        ylim : array_like or None, optional
            Limits - (3,2) array - for the y-axis for each subplot. If None, calculates based off maxima positions.
        n_points : int, optional
            Number of points along each axis for the grid (default is 100).
        levels : int, optional
            Number of contour levels to plot (default is 50).
        

        Notes
        -----
        Only works for d=2. The function plots three subplots:
        - The normalized target density f.
        - The function maximized for the bounding rectangle in the first dimension.
        - The function maximized for the bounding rectangle in the second dimension.
        """

        def cutoff(y):
            z = np.copy(y)
            mask = np.logical_or(y < contour_cutoff, np.isnan(y))
            z[mask] = 0
            return z

        if self.d == 2:
            titles = ['f', 'f_0', 'f_1']
            funcs = [self._f, lambda arg: self._f_rect_v(arg, 0), lambda arg: self._f_rect_v(arg, 1)]
            
            if not np.any(xlim):
                xlim = np.zeros((3, 2))
                xlim[0, :] = [-5, 5]
                for j in [1, 2]:
                    xlim[j, :] = [
                        self.v_min_x[j-1, 0] - margin, 
                        self.v_max_x[j-1, 0] + margin]
            if not np.any(ylim):
                ylim = np.zeros((3, 2))
                ylim[0, :] = [-5, 5]
                for j in [1, 2]:
                    ylim[j, :] = [
                        self.v_min_x[j-1, 1] - margin, 
                        self.v_max_x[j-1, 1] + margin]

            fig, axs = plt.subplots(3)
            fig.tight_layout()
            for j in range(3):
                x = np.linspace(*xlim[j, :], n_points)
                y = np.linspace(*ylim[j, :], n_points)
                X, Y = np.meshgrid(x, y)
                XY = np.stack([X.ravel(), Y.ravel()], axis=1)
                Z = funcs[j](XY)
                Z_res = Z.reshape(X.shape)
                Z_c = cutoff(Z_res)
                axs[j].contour(X, Y, Z_c, levels=levels, cmap='viridis')
                axs[j].set_title(titles[j])

            if maxes:
                axs[0].plot(0,0,'x')
                for i in [0, 1]:
                    axs[i+1].plot(*self.v_min_x[i], 'x', color='black')
                    axs[i+1].plot(*self.v_max_x[i], 'x', color='black')

            plt.show()
        else:
            print('plot_f_2d for use when d=2')


    def plot_f(self, **kwargs):
        if self.d==1:
            self.plot_f_1d(**kwargs)
        elif self.d==2:
            self.plot_f_2d(**kwargs)

    
    def f_original(self, x):
        '''The function to sample from, without any transformations applied. No normalisation is done.'''
        f = lambda x: np.exp(self.f_0(x))
        return f(x)
    

    def bounding_box_area(self):
        temp = (self.r*self.d+1)*self.u_max
        for i in range(self.d):
            temp = temp * (self.v_max[i] - self.v_min[i])
        return temp
    

    def info(self):
        '''
            Prints out information found about bounding rectangle, fmax, mode, and rotation.
        '''
        print('------------------------------------------------------------------------')
        print('\tbounding rectangle: (scaled, i.e. matches self._f_rect_v and self.f, but not the real function)')
        print(f'\t\t[0,{self.u_max}]')
        
        for i in range(self.d):
            bound = f'[{round(self.v_min[i], 3)},{round(self.v_max[i], 3)}]'
            print(f'\t\t{bound}')
            if not self.user_supplied_rectangle:
                minloc = 'min at ['
                maxloc = 'max at ['
                for j in range(self.d):
                    minloc += str(self.v_min_x[i][j]) + '  '
                    maxloc += str(self.v_max_x[i][j]) + '  '
                minloc += ']'
                maxloc += ']'
                print(f'\t\t\t{minloc}')
                print(f'\t\t\t{maxloc}')

        fmax_current = -scipy.optimize.minimize(lambda x: -self._f(x), self.ics, method=self.optim_method).fun
        if self.YJ:
            print(f'\tYJ-transformed mode = {self.mode}')
            print(f'\tmode = {ru_libs.yeojohnson_x(self.mode, self.YJ_lambda)}')
        else:
            print(f'\tmode = {self.mode}')
        print(f'\tfmax before scaling = {self.fmax}')
        print(f'\tfmax after scaling = {fmax_current} (desired = 1)')
        print(f'\tics = {self.ics}')
        print(f'\trotate={self.rotate}')
        if self.rotate:
            for i in range(self.d):
                print(f'\t\t{self.axes_rotate_L[i,:]}')
        if self.acceptance_rate != -1:
            print(f'\tacceptance probability from previous sampling: {self.acceptance_rate}')
        print('------------------------------------------------------------------------')


    def undo_transformations(self, x):
        if self.rotate:
            x = ru_libs.rotate_x(x, self.axes_rotate_L_inv, self.axes_rotate_scale)
        if self.mode_relocate:
            x = x + self.mode
        if self.YJ:
            x = ru_libs.yeojohnson_x(x, self.YJ_lambda)
        if self.user_defined_transformation:
            x = self.X_to_x(x)
        return x
    

    def f_trans_area(self, suppress_message=False):
        '''
        Calculates the area under self._f, the function that the sampling algorithm is applied to (in order to normalise self._f).
        This uses the acceptance probability estimate, so it can only be run after self.rvs is called.
        '''
        if self.acceptance_rate != -1:
            f_area = self.acceptance_rate * self.bounding_box_area()
        else:
            f_area = 1
            if not suppress_message:
                print('Cannot call f_trans_area before rvs is called at least once.')
        return f_area


    def f(self, x):
        '''
        Returns self._f, normalised to have area 1. Should match the output if undo_transformations=False.
        (The algorithm samples from self._f because the scale factor makes no difference, but self.f is for plots.)
        '''
        a = 1.1*self.f_trans_area(suppress_message=True)
        return self._f(x)/a
    

    def hist_1d(self, xmax=np.inf, xmin=-np.inf, bins=100):
        '''
        After calling rvs, call hist_1d to plot a histogram showing the results against f.
        No normalisation is done on f (unless transformed=True).
        '''
        if self.d == 1:
            if self.acceptance_rate == -1:
                print('Cannot call hist_1d before rvs.')
            else:
                rvs = self.rvs_detail['rvs'][:, 0]
                x_lim = [min(rvs), max(rvs)]

                if np.isfinite(xmin):
                    x_lim[0] = xmin
                    rvs = rvs[rvs > xmin]

                if np.isfinite(xmax):
                    x_lim[1] = xmax
                    rvs = rvs[rvs < xmax]
                
                x_range = np.arange(*x_lim, 0.01)

                if self.undo_transformations_flag:
                    y_function = self.f_original(np.expand_dims(x_range, axis=-1))
                else:
                    y_function = self.f(np.expand_dims(x_range, axis=-1))
                
                plt.plot(x_range, y_function)
                plt.hist(rvs, bins=bins, density=True)
                plt.title(f'Acceptance probability = {self.rvs_detail['pa']}')
                plt.show()
        else:
            print('hist_1d is for d==1')


    def scatter_2d(self, levels=3, n_points=100, **scatter_args):
        '''
        After calling rvs, call scatter_2d for a scatter plot showing the results against f.
        scatter_args are passed to plt.scatter().
        '''
        if self.d == 2:
            if self.acceptance_rate == -1:
                print('Cannot call scatter_2d before rvs.')
            else:
                rvs = self.rvs_detail['rvs']
                plt.scatter(rvs[:, 0], rvs[:, 1], **scatter_args)

                if self.undo_transformations_flag:
                    f_contour = self.f_original
                else:
                    f_contour = self.f

                x_lim = (min(rvs[:, 0]), max(rvs[:, 0]))
                y_lim = (min(rvs[:, 1]), max(rvs[:, 1]))
                x = np.linspace(*x_lim, n_points)
                y = np.linspace(*y_lim, n_points)
                X, Y = np.meshgrid(x, y)
                XY = np.stack([X.ravel(), Y.ravel()], axis=1)
                Z = f_contour(XY).reshape(X.shape)
                plt.contour(X, Y, Z, levels=levels, colors='#000000')
                #plt.axis('off')
                plt.show()
        else:
            print('scatter_2d is for d==2')


    def plot(self, **kwargs):
        '''Wrapper for hist_1d and scatter_2d with default args, methods for plotting rvs after rvs is called.'''
        if self.d==1:
            self.hist_1d(**kwargs)
        if self.d==2:
            self.scatter_2d(**kwargs)
    

    def rvs(self, n=1, undo_transformations=True):
        '''
        Returns n samples from f in a (n, d) array.
        Call rvs_detail instead for rvs, acceptance probability and time elapsed.

        Parameters
        ----------
        n: int, optional
            Number of theta samples to return

        Returns
        -------
        array of array of int
            Random variates: first index 0...n-1, second index 0...d-1.
        '''
        r = self.rvs_detail(n=n, undo_transformations=undo_transformations)
        return r['rvs']
    

    def rvs_detail(self, n=1, undo_transformations=True):
        '''
        Random variates with acceptance probability and time elapsed. Call rvs for a short version.

        Parameters
        ----------
        n: int, optional
            Number of theta samples to return
        undo_transformations: bool, optional
            Whether or not to undo transformations (True by default).
    
        Returns
        -------
        dict
            'rvs': random variates
            'pa': acceptance probability
            'time': time elapsed
        '''
        assert n>0

        starttime = current_time()
        acceptance_probability_estimate = 0.75       # initial value to take for acceptance probability
        probability_margin = 0.05
        x = np.zeros((n, self.d))
        n_complete = 0
        n_chunks = 0
        total_count = 0
        self.undo_transformations_flag = undo_transformations
        warned_already = False

        while n_complete < n:
            n_chunks += 1                
            n_remaining = n-n_complete
            n_samples = round(n_remaining/(abs(acceptance_probability_estimate - probability_margin)))
            total_count += n_samples

            u = np.random.uniform(low=0, high=self.u_max, size=n_samples)
            v = np.random.uniform(low=self.v_min, high=self.v_max, size=(n_samples, self.d))
            x_maybe = v / (u[:, None] ** self.r)
            
            # determine whether to keep or discard each
            val = self._f(x_maybe)**self.power_alt

            mask = u < val
            n_accepted = np.sum(mask)
            if n_accepted > n_remaining:    # overshoot case (i.e. in the last chunk)
                accepted_indices = np.where(mask)[0][:n_remaining]
                x[n_complete:n_complete + n_remaining, :] = x_maybe[accepted_indices, :]
                n_complete += n_remaining
            else:
                x[n_complete:n_complete + n_accepted, :] = x_maybe[mask, :]
                n_complete += n_accepted

            acceptance_probability_estimate = max(0.001, n_complete/total_count)      
            # increasingly accurate estimate
            
            if acceptance_probability_estimate < 0.01 and not warned_already:
                warned_already = True
                print(f'Warning: low acceptance rate {n_complete/total_count}')

        # can opt out for debugging
        if undo_transformations:
            x_transformed = self.undo_transformations(x)
        else:
            x_transformed = x

        out = {'rvs': x_transformed,
               'pa': n/total_count,
               'time': current_time()-starttime}
        self.acceptance_rate = out['pa']
        self.rvs_detail = out

        return out