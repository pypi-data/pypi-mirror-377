# -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 15:18:26 2019

@author: couledhousseine
"""

import time
import numpy as np
import numpy.linalg as LA
import scipy
from tqdm import tqdm
from Snoopy import logger
from Snoopy.Math.numerical_jacobian import approx_jacobian_n

# -----------------------------------------------------------------------------

# function to minimize (for scipy tests) --------------------------------------
def f(x):
    return LA.norm(x)**2

# gradient
def df(x):
    return 2*x
# -----------------------------------------------------------------------------

def MHLGA(x0, func, beta_tol, func_tol, itmax = 50, ls_itmax = 50,  dx = 1e-3, nproc = 1):
    """MHLGA algorithm for FORM.

    Parameters
    ----------
    x0 : np.ndarray
        starting solution
    func : TYPE
        DESCRIPTION.
    beta_tol : float
        beta tolerance (absolute error).
    func_tol : float
        limit state function tolerance (absolute error).
    itmax : int
        maximum number of iterations.
    ls_itmax : int
        maximum number of iterations for line search ("sub-iteration").
    dx : float, optional
        Step for gradient evaluation. The default is 1e-3.
    nproc : int, optional
        Number of core to use for gradient evaluation. The default is 1.

    Returns
    -------
    OptimisationResults
        Results of optimization.  OptimizeResult.x being the value minimizing beta.
    """

    if(beta_tol<0):
        raise ValueError('Tolerance on beta should be positive')
    if(func_tol<0):
        raise ValueError('Tolerance on the limit state function should be positive')

    funCall = 0
    gradCall = 0

    # parameters
    A     = 10.
    B     = 100.
    alpha = 1.
    m1    = 0.1
    m2    = 0.9

    r1    = 0.5
    r2    = 1.5

    start = time.time()

    xk    = x0
    xk1   = x0
    Gk    = func(x0)

    beta0 = 0.
    
    for k in tqdm( range(itmax), total = 0 , desc = "MHLGA" ):
        beta = LA.norm(xk)

        if (abs(beta-beta0) < beta_tol) and (abs(Gk) < func_tol):
            logger.debug( f"Iteration finished : d_beta = {abs(beta-beta0):.3f} < beta_tol = {beta_tol}" )
            logger.debug( f"Iteration finished : abs(func(xk)) = {abs(Gk):.6f} < func_tol = {func_tol:.6f}" )
            break
        else:
            if((abs(beta-beta0) > beta_tol)and (abs(Gk) > func_tol)):
                logger.debug( f"   Iteration {k:} : d_beta = {abs(beta-beta0):.3f} > beta_tol = {beta_tol}" )
                logger.debug( f"   Iteration {k:} : abs(func(xk)) = {abs(Gk):.6f} > func_tol = {func_tol:.6f}" )
            elif(abs(Gk) > func_tol):
                logger.debug( f"   Iteration {k:} : abs(func(xk)) = {abs(Gk):.6f} > func_tol = {func_tol:.6f}" )
            else:
                logger.debug( f"   Iteration {k:} : d_beta = {abs(beta-beta0):.3f} > beta_tol = {beta_tol}" )


            beta0 = beta


        logger.debug( f"Iteration {k:} - Calculate function" )
        Gk  = func(xk)
        funCall += 1

        # gradient
        logger.debug( f"Iteration {k:} - Calculate gradient" )
        dGk = approx_jacobian_n(func=func,x=xk,fx=Gk,epsilon=dx,nproc=nproc)[0]
        gradCall += 1

        # direction
        Nk  = LA.norm(dGk)**2
        ak  = np.dot(xk,dGk)/Nk
        dk  = (ak-Gk/Nk)*dGk-xk

        #if(LA.norm(dk) < beta_tol):
        #    break

        if(abs(Gk) < func_tol):
            ck = B
        else:
            ck = A * abs(ak / Gk)

        # line search to minimize merit function
        alphak = alpha
        mk     = 0.5*(LA.norm(xk)**2+ck*Gk**2)
        dmk    = xk + ck*Gk*dGk
        pk     = np.dot(dmk,dk)

        for i in range(ls_itmax):
            logger.debug( f"    Iteration {k:} - Calculate function (line search {i:}) - {LA.norm( alphak * dk ):.2e}" )
            xk1  = xk + alphak * dk

            Gk1  = func(xk1)
            funCall += 1
            mk1  = 0.5*(LA.norm(xk1)**2+ck*Gk1**2)

            #Do not reduce step more than necessary (usefull when close to the solution)
            if LA.norm( alphak * dk ) < 0.1 * beta_tol :
                break

            #Adjust step
            if (mk1 - mk > alphak * m1 * pk):
                alphak = r1 * alphak
            elif (mk1 - mk < alphak * m2 * pk):
                alphak = r2 * alphak
            else:
                break

        else:
            logger.warning("MHGLA, max number of iteration during line search is reached")

        xk  = xk1
        Gk  = Gk1
    else :
        logger.warning("MHGLA has not converged in {itmax:} iteration")

    clock_time = time.time() - start

    success = not (k == itmax - 1)

    res_str = f"""-------------------------------------------
********* FORM - MHLGA algorithm **********
-------------------------------------------
Inputs
    > beta tolerance (absolute error): {beta_tol:}
    > Limit state function tolerance (absolute error): {func_tol:}
Outputs'
    > Nbr of iterations exceeded: {not success:}
    > Iterations: {k:}
    > beta: {beta:}
    > Limit state function: {Gk:}
    > cpu time: {clock_time:}
    > function call: {funCall:}
    > gradient call: {gradCall:}
    > total function call: {funCall + len(x0) * gradCall:}
"""
    logger.debug(res_str)

    return scipy.optimize.OptimizeResult( x = xk, success=success, fun=beta,
                                          nit=k , constraint = Gk ,
                                          nfev = funCall ,
                                          njev = gradCall,
                                          nfev_tot = funCall + len(x0) * gradCall,
                                          total_clock_time = clock_time )
