# Dependencies
import numpy as np
import numpy.ma as ma
import pytest
from ustat_var.makec import makec
from ustat_var.makec import makec_spec
from ustat_var.generate_test_data import generate_unique_nan_arrays

def test_makec_simple():
    '''Simple test of makec() on simple arrays with no nans'''
    X = np.array([
        [1.0, 2.0, 3.0],
        [4.0, 5.0, 6.0]
    ])
    Y = np.array([
        [1.0, 2.0, 3.0],
        [6.0, 5.0, 4.0]
    ])
    
    # Expected result based on formula in Appendix
    C_jj_expected = np.array([1/24, 1/24])
    C_jk_expected = np.array([[-1/36, -1/36], [-1/36, -1/36]])
    
    # Compute result based on makec function
    C_jj_result, C_jk_result = makec(X, Y)
    
    # Test within tolerance
    np.testing.assert_allclose(C_jj_result, C_jj_expected, rtol=1e-6)
    np.testing.assert_allclose(C_jk_result, C_jk_expected, rtol=1e-6)

def test_makec_some_nans():
    '''Simple test of makec() on simple arrays with some nans'''
    X = np.array([
        [1.0, np.nan, np.nan],
        [4.0, 5.0, np.nan]
    ])
    Y = np.array([
        [1.0, 2.0, np.nan],
        [6.0, np.nan, 4.0]
    ])
    
    # Expected result based on formula in Appendix
    C_jj_expected = np.array([1/4, 1/12])
    C_jk_expected = np.array([[-1/8, -1/8], [-1/16, -1/16]])
    
    # Compute result based on makec function
    C_jj_result, C_jk_result = makec(X, Y)
    
    # Test within tolerance
    np.testing.assert_allclose(C_jj_result, C_jj_expected, rtol=1e-6)
    np.testing.assert_allclose(C_jk_result, C_jk_expected, rtol=1e-6)

def test_makec_spec():
    '''Test of makec() on simple arrays with some nans and drop_pairs=True'''
     # Test parameters
    n_rows = 100
    n_cols = 50
    nsims = 100
    np.random.seed(8461749)

    # (Fixed) random arrays to test
    for i in range(nsims):
        X = generate_unique_nan_arrays(n_rows = n_rows, n_cols = n_cols, n_arrays = 1,
                                            min_int=1, max_int = 100, nan_prob = 0.5, balanced = False)[0]

        # Compute result based on makec function
        C_jj_expected, C_jk_expected = makec(X, X)
        C_jj_result, C_jk_result = makec_spec(X)

        # Test within tolerance
        np.testing.assert_allclose(C_jj_result, C_jj_expected, rtol=1e-6)
        np.testing.assert_allclose(C_jk_result, C_jk_expected, rtol=1e-6)
