# Dependencies:
import numpy as np
from scipy import sparse
from ustat_var.varcovar import varcovar
from ustat_var.generate_test_data import generate_unique_nan_arrays
from ustat_var.generate_test_data import generate_data


def test_varcovar_weights_simple():
    '''A simple test of the varcovar() function's weighting options for small, balanced arrays '''
    
    # Arrays to test
    A = np.array([
        [1.0, 2.0, 3.0],
        [4.0, 5.0, 6.0],
        [3.0, 2.0, 1.0]
    ])
    B = np.array([
        [1.0, 2.0, 3.0],
        [6.0, 5.0, 4.0],
        [64.0, 8.0, 3.0]
    ])
    
    # Weights to test
    w_row = np.array([5, 5, 5])
    
    # Results to test
    unweighted = varcovar(origX = A, origY = B)
    teacher_weighted = varcovar(origX=A, origY=B, w=w_row)

    
    # Test equality
    np.testing.assert_allclose(unweighted, teacher_weighted, rtol=1e-6)
    

def test_varcovar_weights_unbalanced():
    '''A simple test of the varcovar() function's weighting options. Note, tests for imbalance within- and between-teachers. '''
    
    # Arrays to test
    n_teachers, n_time = 50, 10
    A, B = generate_unique_nan_arrays(n_rows=n_teachers, n_cols=n_time, n_arrays=2,
                                      min_int=1, max_int=9, nan_prob=0.25, balanced = False)
    
    # Weights to test
    w_row = np.array(np.repeat(5, n_teachers))
    
    # Results to test
    unweighted = varcovar(A, B)
    teacher_weighted = varcovar(origX=A, origY=B, w=w_row)
    
    ### Expected results when WEIGHTS ARE EQUAL ###
    # C_unweighted = C_teacherWeighted
    np.testing.assert_allclose(unweighted, teacher_weighted, rtol=1e-6)
    


def test_varcovar_simple_corr():
    '''If A = B, then corr(A,B) = cov(A,B)/(sqrt(var(A))sqrt(var(B))) = 1'''
    
    # Arrays to test
    n_teachers, n_time = 100, 50
    
    np.random.seed(81830)
    
    # Test 100 times
    for i in range(100):
        
        # Random mean and sd
        mu = np.random.normal(scale = 1, size = (n_teachers, 1))
        A = np.random.normal(mu, 1, size = (n_teachers, n_time))
        B = A
        
        # Calculate unweighted covariance and variance
        covAB = varcovar(A, B)
        varA = varcovar(A, A)
        varB = varcovar(B, B)
        corrAB = covAB / (np.sqrt(varA * varB))
        
        # Test only when variances greater than 0 (debiasing can lead to negative variances)
        if (varA > 0) and (varB > 0):
            np.testing.assert_allclose(corrAB, 1, rtol=1e-6)


def test_varcovar_scale_var():
    ''' B = k*A, then var(B)=k^2*var(A) '''
    
    # Array parameters
    n_teachers, n_time = 100, 50
    
    # Set seed
    np.random.seed(81830)
    
    # Test 100 times
    for i in range(100):
        
        A = generate_unique_nan_arrays(n_rows=n_teachers, n_cols=n_time, n_arrays=1,
                                      min_int=1, max_int=9, nan_prob=0.25, balanced = False)[0]
        k = np.random.randint(1, 100)
        B = k * A
        
        # Calculate var(A) and var(B)
        varA = varcovar(A, A)
        varB = varcovar(B, B)
        
        np.testing.assert_allclose(varB / varA, k**2, rtol=1e-6)
    
    
def test_varcovar_sum():
    ''' var(A+B) = var(A) + var(B) + 2*cov(A,B) '''
    
    # Array parameters
    n_teachers, n_time = 100, 50
    
    # Set seed
    np.random.seed(81830)
    
    # Test 100 times
    for i in range(100):
        
        # Generate arrays
        nanA, nanB = generate_unique_nan_arrays(n_rows=n_teachers, n_cols=n_time, n_arrays=2,
                                       min_int=1, max_int=2, nan_prob=0.25, balanced = True)
        
        A, B = generate_data(n_teachers=n_teachers, n_time=n_time, n_arrays=2, cov_factor=1)
        A = nanA * A
        B = nanB * B
        C = A + B
  
        
        # Calculate required variances/covariances
        varA = varcovar(A, A)
        varB = varcovar(B, B)
        covAB = varcovar(A, B)
        varC = varcovar(C, C)
        
        # Test identity (which only work when variance exceeds 0)
        if (varA > 0) and (varB > 0) and (varC > 0):
            np.testing.assert_allclose(varC, varA + varB + 2*covAB, rtol=1e-6)
    
    
def test_varcovar_balanced_works():
    '''test whether the varcovar function works for simple known arrays'''
    
    # Arrays to test
    A = np.array([
        [1.0, 2.0, 3.0],
        [4.0, 5.0, 6.0],
        [3.0, 2.0, 1.0]
    ])
    
    B = np.array([
        [1.0, 2.0, 3.0],
        [6.0, 5.0, 4.0],
        [64.0, 8.0, 3.0]
    ])
    
    C = np.array([
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ])
    
    # Expected results (from manual calculation)
    covAB = 826/54 - 209/9
    varC  = 52/9
    
    # Function results
    covAB_result = varcovar(A, B)
    varC_result  = varcovar(C, C)
    
    # Test equality
    np.testing.assert_allclose(covAB, covAB_result, rtol=1e-6)
    np.testing.assert_allclose(varC, varC_result, rtol=1e-6)
    
    
def test_prod_pair_drops():
    '''test that function drops single observations properly'''
    
    # Array parameters
    n_teachers, n_time = 500, 50
    
    # Set seed
    np.random.seed(131)
    
    # Test 100 times
    for i in range(100):
        
        # Generate arrays (high probability of single product pair)
        nanA, nanB = generate_unique_nan_arrays(n_rows=n_teachers, n_cols=n_time, n_arrays=2,
                                       min_int=1, max_int=2, nan_prob=0.80, balanced = False)
        
        # Check if nan arrays generated single product pairs
        countsX = np.count_nonzero(~np.isnan(nanA),1)  # No. of obs in X
        countsY = np.count_nonzero(~np.isnan(nanB),1)  # No. of obs in Y
        nsquares = np.count_nonzero(~np.isnan(nanA * nanB),1)   # No. of obs in both X and Y
        nproducts = (countsX*countsY - nsquares) # No. of valid product pairs        
        check = np.any(nproducts == 0)
        
        # If some rows have no products pairs, generate data
        if (check):
            A, B = generate_data(n_teachers=n_teachers, n_time=n_time, n_arrays=2, cov_factor=1)
            A = nanA * A
            B = nanB * B
            
            # A and B with single product pair rows removed
            A_filt = A[nproducts>0,:].copy()
            B_filt = B[nproducts>0,:].copy()

            # Generate weights
            w_rand = np.random.exponential(scale = 1, size = n_teachers)
            w_ones = np.ones(n_teachers)
            
            # Calc variance-covariance objects
            covAB_equal_weights = varcovar(A,B,w=w_ones)
            covAB_unweighted = varcovar(A,B)
            covAB_exp_weights = varcovar(A,B,w_rand)
            covAB_filt_exp_weights = varcovar(A_filt, B_filt, w_rand[nproducts>0])
            
            # Test equality
            np.testing.assert_allclose(covAB_unweighted, covAB_equal_weights, rtol=1e-6)
            np.testing.assert_allclose(covAB_exp_weights, covAB_filt_exp_weights, rtol=1e-6)

        # If the random arrays didn't generate single product pair rows, then skip this iteration.
        else:
            continue
        
        
        
        
        
    