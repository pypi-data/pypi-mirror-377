# Dependencies
import numpy as np
import numpy.ma as ma
import pytest
from ustat_var.generate_test_data import generate_unique_nan_arrays
from ustat_var.generate_test_data import generate_data
from ustat_var.sampc import sampc


def test_sampc_simple():
    '''Test the sampc helper function on a simple case'''
    
    # Test arrays
    X = np.array([
        [1.0, 2.0, 3.0],
        [4.0, 5.0, 6.0]
    ])
    Y = np.array([
        [1.0, 2.0, 3.0],
        [6.0, 5.0, 4.0]
    ])
    
    # Sampc() should return rowwise sampling covariance between X and Y
    expected = [np.cov(X[row,:], Y[row,:])[0,1] for row in range(X.shape[0])]
    result = sampc(X,Y)
    
    # Test within tolerance
    np.testing.assert_allclose(result, expected, rtol=1e-6)


def test_sampc_some_nans():
    '''Test the sampc helper function on a simple case with some NaNs'''
    
    # Test arrays
    X = np.array([
        [1.0, np.nan, 3.0],
        [4.0, 5.0, np.nan]
    ])
    Y = np.array([
        [2.0, np.nan, 6.0],
        [6.0, 5.0, np.nan]
    ])
    
    # Sampc() should return rowwise sampling covariance between X and Y
    expected = [ma.cov(ma.masked_invalid(X[row,:]), ma.masked_invalid(Y[row,:]))[0,1] for row in range(X.shape[0])]
    result = sampc(X,Y)
    
    # Test within tolerance
    np.testing.assert_allclose(result, expected, rtol=1e-6)
    

def test_sampc_no_valid_pairs():
    '''Test the sampc helper function when there are no valid pairs. Should return 0s.'''
    
    # Test arrays
    X = np.array([
        [1.0, np.nan, 3.0, np.nan],
        [np.nan, 3.0, np.nan, 1.0]
    ])
    Y = np.array([
        [np.nan, 4.0, np.nan, 8.0],
        [8.0, np.nan, 4.0, np.nan]
    ])
    
    # Expect to return all 0s when no valid pairs.
    expected = [0,0]
    result = sampc(X,Y)
    
    # Test within tolerance
    np.testing.assert_allclose(result, expected, rtol=1e-6)


def test_sampc_very_few_valid_pairs():
    '''Test the sampc helper function when some rows have no valid pairs. 
    Should return 0s for those rows, and should equal the sample covariance for other rows invalid rows are removed'''
    
    # Array parameters
    n_teachers, n_time = 100, 50

    # Set seed
    np.random.seed(131)
    
    # Generate arrays
    for i in range(1000):  # Test multiple times 

        # Generate arrays (high probability of single product pair)
        nanA, nanB = generate_unique_nan_arrays(n_rows=n_teachers, n_cols=n_time, n_arrays=2,
                                        min_int=1, max_int=2, nan_prob=0.6, balanced = True)
        A, B = generate_data(n_teachers=n_teachers, n_time=n_time, n_arrays=2, cov_factor=1)
        A = nanA * A
        B = nanB * B

        Acounts = np.count_nonzero(~np.isnan(A),1)  # No. of valid obs in A
        Bcounts = np.count_nonzero(~np.isnan(B),1)  # No. of valid obs in B
        ABcounts = np.count_nonzero(~np.isnan(A * B),1)   # No. of valid obs in both A and B
        nproducts = (Acounts*Bcounts - ABcounts) # No. of valid product pairs
        check = np.any(nproducts == 0)  
        if not check:
            continue  # Try again if all rows have valid pairs

        # Expect to return all 0s when no valid pairs.
        expected = sampc(A[ABcounts>1],B[Bcounts>1])  # Should handle internally
        result = sampc(A,B)
        result = result[ABcounts>1]  # Only compare valid rows

        # Test within tolerance
        np.testing.assert_allclose(result, expected, rtol=1e-6)