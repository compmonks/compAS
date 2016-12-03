"""brg.numerical.solvers.differential_evolution : Differential evolution."""

from numpy import array
from numpy import argmin
from numpy import min
from numpy import newaxis
from numpy import tile
from numpy import where
from numpy import zeros
from numpy.random import rand

from random import sample
from functools import partial

import matplotlib.pyplot as plt
import multiprocessing


__author__     = ['Andrew Liew <liew@arch.ethz.ch>', ]
__copyright__  = 'Copyright 2016, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__version__    = '0.10'
__date__       = '10.10.2016'


def de_solver(fn, bounds, population, iterations, results=None, threads=0,
              args=()):
    """ Call the differential evolution solver.

    Note:
        fn returns vectorised output for input (k, population) if threads=0.

    Parameters:
        fn (obj): The function to evaluate and minimise.
        bounds (list): List of tuples defining bounds for each DoF.
        population (int): Number of agents in the population.
        iterations (int): Number of cross-over cycles or steps to perform.
        results (boolean): Store results or not.
        threads (int): Number of threads/processes for multiprocessing.
        arg (seq): Sequence of optional arguments to pass to fn.

    Returns:
        float: Optimal value of objective function.
        array: Values that give optimum (minimised) function.
        array: Data for plotting.

    Examples:
        >>> def fn(u, *args):
        >>>     # Booth's function, fopt=0, xopt=(1, 3)
        >>>     x = u[0, :]
        >>>     y = u[1, :]
        >>>     z = (x + 2*y - 7)**2 + (2*x + y - 5)**2
        >>>     return z
        >>> bounds = [(-10, 10) for i in range(2)]
        >>> fopt, xopt = solver(fn, bounds, population=100, iterations=150)
        Iteration: 0 fopt: 9.29475634582
        Iteration: 1 fopt: 0.714845258545
        Iteration: 2 fopt: 0.714845258545
        ...
        Iteration: 148 fopt: 4.22441611201e-22
        Iteration: 149 fopt: 4.22441611201e-22
        Iteration: 150 fopt: 5.18467217924e-23
        >>> print(xopt)
        array([ 1.,  3.])
    """
    F = 0.8
    CR = 0.9
    k = len(bounds)
    b_ran = array([bound[1] - bound[0] for bound in bounds])[:, newaxis]
    b_min = array([bound[0] for bound in bounds])[:, newaxis]
    agents = (rand(k, population) * tile(b_ran, (1, population)) +
              tile(b_min, (1, population)))
    candidates = [list(range(population)) for i in range(population)]
    for i in range(population):
        del candidates[i][i]
    candidates = array(candidates)
    ts = 0
    if threads > 1:
        t = range(population)
        pool = multiprocessing.Pool(processes=threads)
        func = partial(funct, agents, args)
        fun = array(pool.map(func, t))
        pool.close()
        pool.join()
    elif threads == 1:
        fun = zeros(population)
        for i in range(population):
            fun[i] = fn(agents[:, i], args)
    else:
        fun = fn(agents, args)
    fopt = min(fun)
    print('Iteration: ' + str(ts) + ' fopt: ' + str(fopt))
    ac = zeros((k, population))
    bc = zeros((k, population))
    cc = zeros((k, population))
    data = zeros((iterations, population))
    while ts < iterations:
        if results:
            data[ts, :] = fun
        ind = rand(k, population) < CR
        for i in range(population):
            inds = candidates[i, sample(range(population - 1), 3)]
            ac[:, i] = agents[:, inds[0]]
            bc[:, i] = agents[:, inds[1]]
            cc[:, i] = agents[:, inds[2]]
        agents_ = ind * (ac + F * (bc - cc)) + ~ind * agents
        if threads > 1:
            t = range(population)
            pool = multiprocessing.Pool(processes=threads)
            func = partial(funct, agents_, args)
            fun_ = array(pool.map(func, t))
            pool.close()
            pool.join()
        elif threads == 1:
            fun_ = zeros(population)
            for i in range(population):
                fun_[i] = fn(agents_[:, i], args)
        else:
            fun_ = fn(agents_, args)
        log = where((fun - fun_) > 0)[0]
        agents[:, log] = agents_[:, log]
        fun[log] = fun_[log]
        fopt = min(fun)
        xopt = agents[:, argmin(fun)]
        ts += 1
        ac *= 0
        bc *= 0
        cc *= 0
        print('Iteration: ' + str(ts) + ' fopt: ' + str(fopt))
    if results:
        return fopt, xopt, data
    else:
        return fopt, xopt


def de_plot(data, ms, path):
    """ Plot the differential evolution results.

    Parameters:
        data (array): Data array (iterations x population).
        ms (float): Markersize of points.
        path (str): Path to save figure.

    Returns:
        None
    """
    n = data.shape[0]
    m = data.shape[1]
    nt = tile(array(list(range(1, n + 1)))[:, newaxis], (1, m))
    plt.plot(nt.ravel(), data.ravel(), 'o', markersize=ms)
    plt.grid(True)
    plt.xlabel('Evolution')
    plt.ylabel('Function')
    plt.savefig(path + 'data.png')


# ==============================================================================
# Debugging
# ==============================================================================

# ------------------------------------------------------------------------------
# USE THIS SPACE FOR MULTIPROCESSING FUNCTIONS
# ------------------------------------------------------------------------------


def funct(agents, args, t):
    return fn(agents[:, t], args)


# ------------------------------------------------------------------------------
# USE THIS SPACE FOR MULTIPROCESSING FUNCTIONS
# ------------------------------------------------------------------------------

if __name__ == "__main__":

    def fn(u, *args):
        # Booth's function, fopt=0, xopt=(1, 3)
        x = u[0]
        y = u[1]
        z = (x + 2*y - 7)**2 + (2*x + y - 5)**2
        return z

    bounds = [(-10, 10) for i in range(2)]
    fopt, xopt, data = de_solver(fn, bounds, population=100, iterations=20,
                              results=True, threads=1)
    de_plot(data, 5, '/home/al/Temp/')



    # Optimisation
    # tic = time()
    # png_path = '/home/al/Temp/'
    # args = (C, Ct, X, l0, ks, P, Pn, V, BC, M, ind, tol, steps)
    # print('Optimisation started...')
    # fopt, uopt, data = de_solver(fn, bounds, population=settings['pop_factor'],
    #             iterations=trials, results=True, threads=threads, args=args)
    # plot(data, 5, png_path)