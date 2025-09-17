# Dependencies
import numpy as np

# Helper for C functions, general case when X != Y
def makec(X,Y, w=None):
    r"""
    Generates C-weights for U-statistic estimator.
    The function can deal with the case when there is only one product pair across the outcomes.
    But it cannot deal with the case when a row in either of the two arrays X and Y is completely empty.

    Parameters
    ----------
    X: array
        J-by-:math:`\operatorname{max}(T_j)` array containing data/residuals for outcome X
    Y: array
        J-by-:math:`\operatorname{max}(T_j)` array containing data/residuals for outcome Y.
    w: array
        J-by-1 array containing row-wise/teacher-level weights (optional).

    Returns
    -------
    list of ndarray
        First array contains C-weights for specific teachers (i.e. weight when :math:`j(i) = j(k)`), and second element contains array of cross-term C-weights (i.e. weight when :math:`j(i) \neq j(k)`)
    
    """  
    
    # Number of observations in X, Y, and intersection
    Xcounts = np.array(np.sum(~np.isnan(X), axis=1),dtype=float) # returns no. of observations across all teachers in X (e.g. event X)
    Ycounts = np.array(np.sum(~np.isnan(Y), axis=1),dtype=float) # returns no. of observations across all teachers in Y (e.g. event Y)
    XYcounts = np.array(np.sum(~np.isnan(X) & ~np.isnan(Y), axis=1),dtype=float) # returns no. of observations across all teachers in XandY (e.g. shared observations)
    nproducts = Xcounts * Ycounts - XYcounts # no. of valid observations (year product pairs)
    J = sum(nproducts > 0) # Number of rows with valid observations (more than 1 product pair)
    
    # If weights present, set weights where only 1 observation to 0
    if not(w is None):
        w[nproducts == 0] = 0
    
    # Check if weights are teacher-level and that each valid teacher has a weight.
    # Fail if not.
    if not(w is None):
        valid_w_count = np.sum(w > 0)
        if (w.ndim != 1):
            raise ValueError("Weight object has wrong dimension. You need to supply teacher-level weights only (i.e. 1 weight per teacher). Check 'w' and try again.")
        elif (valid_w_count != J):
            raise ValueError("Not enough weights supplied (i.e. some teachers didn't receive weights). Check 'w' and try again.")
    
    # If X or Y contains a row of emptys, fail and report to user.
    if (np.any(Xcounts == 0)) or (np.any(Ycounts == 0)):
            raise ValueError("One of the supplied arrays contains a completely empty row. Function does not support this. Remove those rows and try agian.")

    # Compute C coefficients
    if (w is None):
        # Unweighted (each teacher receives equal weight)
        C_jj = np.zeros(len(nproducts)) 
        C_jj[nproducts > 0] = (J-1)/J**2/(nproducts[nproducts > 0]) # Divide by nproducts when there are more than 0 (avoids divide by 0 for single observation rows)
        C_jk = -1/J**2*(1/Xcounts).reshape(-1,1).dot((1/Ycounts).reshape(1,-1))    # J-by-J, with C_jk as each element.
        
        # Set those with no observations to 0
        C_jk[Xcounts == 0,:] = 0 
        C_jk[:,Ycounts == 0] = 0
    
    else:
        # Weighted (each teacher receives weight corresponding to entries in w)
        w_norm = w / np.sum(w) # Normalised weights
        C_jj = w_norm * (1 - w_norm) 
        C_jj[nproducts == 0] = 0 # Set single observations to 0 (already 0 due to weights definition)
        C_jj[nproducts > 0] = C_jj[nproducts > 0] / nproducts[nproducts > 0] # Divide by nproducts when there are more than 0 (avoids divide by 0 for single observation rows)
        C_jk = -(w_norm * w_norm)*(1/Xcounts).reshape(-1,1).dot((1/Ycounts).reshape(1,-1))    # J-by-J, with C_jk as each element.
        
        # Set those with no observations to 0
        C_jk[Xcounts == 0,:] = 0 
        C_jk[:,Ycounts == 0] = 0
    

    return C_jj, C_jk



# C weights when X = Y
def makec_spec(X, w=None):
    r"""
    Generates C-weights for U-statistic estimator in special case when X = Y. 

    Parameters
    ----------
    X: array
        J-by-:math:`\operatorname{max}(T_j)` array containing data/residuals for outcome X
    w: array
        J-by-1 array containing row-wise/teacher-level weights (optional).

    Returns
    -------
    list of ndarray
        First array contains C-weights for specific teachers (i.e. weight when :math:`j(i) = j(k)`), and second element contains array of cross-term C-weights (i.e. weight when :math:`j(i) \neq j(k)`)
    
    """  
    
    # Number of observations in X, Y, and intersection
    Xcounts = np.array(np.sum(~np.isnan(X), axis=1),dtype=float) # returns no. of observations across all teachers in X (e.g. event X)
    nproducts = Xcounts * Xcounts - Xcounts
    J = sum(nproducts > 0) 
    
    # If weights present, set weights where only 1 observation to 0
    if not(w is None):
        w[nproducts == 0] = 0
    
    # Check if weights are teacher-level and that each valid teacher has a weight.
    # Fail if not.
    if not(w is None):
        valid_w_count = np.sum(w > 0)
        if (w.ndim != 1):
            raise ValueError("Weight object has wrong dimension. You need to supply teacher-level weights only (i.e. 1 weight per teacher). Check 'w' and try again.")
        elif (valid_w_count != J):
            raise ValueError("Not enough weights supplied (i.e. some teachers didn't receive weights). Check 'w' and try again.")
        
    # Compute C coefficients
    if (w is None):
        # Unweighted (each teacher receives equal weight
        C_jj = np.zeros(len(nproducts)) 
        C_jj[nproducts > 0] = (J-1)/J**2/(nproducts[nproducts > 0]) # Divide by nproducts when there are more than 0 (avoids divide by 0 for single observation rows)
        C_jk = -1/J**2*(1/Xcounts).reshape(-1,1).dot((1/Xcounts).reshape(1,-1))    # J-by-J, with C_jk as each element.
        
        # Set those with no observations to 0
        C_jk[Xcounts == 0,:] = 0 
        C_jk[:,Xcounts == 0] = 0
    
    else:
        # Weighted (each teacher receives weight corresponding to entries in w)
        w_norm = w / np.sum(w) # Normalised weights
        
        C_jj = w_norm * (1 - w_norm) 
        C_jj[nproducts == 0] = 0 # Set cases with no valid product pairs to 0
        C_jj[nproducts > 0] = C_jj[nproducts > 0] / nproducts[nproducts > 0] # Divide by nproducts when there are more than 0 (avoids divide by 0 for single observation rows)
        C_jk = -(w_norm * w_norm)*(1/Xcounts).reshape(-1,1).dot((1/Xcounts).reshape(1,-1))    # J-by-J, with C_jk as each element.
        
        # Set those with no observations to 0
        C_jk[Xcounts == 0,:] = 0 
        C_jk[:,Xcounts == 0] = 0
    

    return C_jj, C_jk