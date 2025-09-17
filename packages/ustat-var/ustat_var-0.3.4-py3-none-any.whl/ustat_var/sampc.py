# Dependencies
import numpy as np

# Helper function for sampling covariances
def sampc(X,Y):
    r'''
    Computes the sampling covariance between rows of J-by-:math:`\operatorname{max}(T_j)` arrays X and Y.

    Parameters
    ----------
    X: array
        J-by-:math:`\operatorname{max}(T_j)` array containing residuals for outcome X
    Y: array 
        J-by-:math:`\operatorname{max}(T_j)` array containing residuals for outcome X

    Returns
    -------
    array
        J-by-1 array containing sampling covariance between each row of X and Y.
    '''
    # Check inputs
    Xcounts = np.sum(~np.isnan(X), axis=1)
    Ycounts = np.sum(~np.isnan(Y), axis=1)

    # Check at least one valid observation in each row
    if (Xcounts == 0).any() or (Ycounts == 0).any():
        raise ValueError('Each row of X and Y must have at least one non-missing value.')

    Xmeans = np.nanmean(X, axis=1)
    Ymeans = np.nanmean(Y, axis=1)
    XYcounts = np.array(np.sum(~np.isnan(X) & ~np.isnan(Y), axis=1),dtype=float)
    
    # Calculate SSE
    XYcovar = np.nansum((X-Xmeans[:,np.newaxis])*(Y-Ymeans[:,np.newaxis]),1,dtype=float)
    
    # If 1 observation, SSE set to 0 
    XYcovar[XYcounts <= 1] = 0  
    
    # If more than 1 observation, divide by d.o.f.
    XYcovar[XYcounts > 1] = XYcovar[XYcounts > 1] / (XYcounts[XYcounts > 1]-1)
    
    return XYcovar
