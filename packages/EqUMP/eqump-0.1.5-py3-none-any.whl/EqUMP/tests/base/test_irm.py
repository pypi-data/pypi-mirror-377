"""Tests for IRF (Item Response Model) functions in base module."""

import numpy as np
import pytest
# from EqUMP.base.irm import irf, trf


# class TestIRF:
#     """Test cases for the IRF function."""
    
#     def test_irf_1pl_model(self):
#         """Test 1PL model (only b parameter)."""
#         params = {'b': 0.0}
#         theta = 0.0
#         result = irf(theta, params)
#         expected = 0.5  # At theta = b, probability should be 0.5
#         assert abs(result - expected) < 1e-10
    
#     def test_irf_2pl_model(self):
#         """Test 2PL model (a and b parameters)."""
#         params = {'a': 1.0, 'b': 0.0}
#         theta = 0.0
#         result = irf(theta, params)
#         expected = 0.5
#         assert abs(result - expected) < 1e-10
    
#     def test_irf_3pl_model(self):
#         """Test 3PL model (a, b, and c parameters)."""
#         params = {'a': 1.0, 'b': 0.0, 'c': 0.2}
#         theta = 0.0
#         result = irf(theta, params)
#         expected = 0.2 + (1.0 - 0.2) * 0.5  # c + (1-c) * 0.5 = 0.6
#         assert abs(result - expected) < 1e-10
    
#     def test_irf_with_array_input(self):
#         """Test IRF with numpy array input."""
#         params = {'a': 1.0, 'b': 0.0}
#         theta = np.array([0.0, 1.0, -1.0])
#         result = irf(theta, params)
#         assert isinstance(result, np.ndarray)
#         assert len(result) == 3
#         assert abs(result[0] - 0.5) < 1e-10  # theta = 0
    
#     def test_irf_scaling_factor(self):
#         """Test IRF with different scaling factor D."""
#         params = {'a': 1.0, 'b': 0.0}
#         theta = 1.0
        
#         # Test with D = 1.7 (default)
#         result_default = irf(theta, params)
        
#         # Test with D = 1.0
#         result_d1 = irf(theta, params, D=1.0)
        
#         # Results should be different
#         assert result_default != result_d1
    
#     def test_irf_missing_required_parameter(self):
#         """Test that missing required parameter 'b' raises KeyError."""
#         params = {'a': 1.0}  # Missing 'b'
#         theta = 0.0
#         with pytest.raises(KeyError, match="Missing required parameter"):
#             irf(theta, params)
    
#     def test_irf_unknown_parameter(self):
#         """Test that unknown parameters raise KeyError."""
#         params = {'a': 1.0, 'b': 0.0, 'unknown': 0.5}
#         theta = 0.0
#         with pytest.raises(KeyError, match="Unknown parameter"):
#             irf(theta, params)
    
#     def test_irf_invalid_params_type(self):
#         """Test that non-dict params raise TypeError."""
#         params = [1.0, 0.0]  # List instead of dict
#         theta = 0.0
#         with pytest.raises(TypeError, match="invalid type"):
#             irf(theta, params)
    
#     def test_irf_extreme_values(self):
#         """Test IRF behavior with extreme theta values."""
#         params = {'a': 1.0, 'b': 0.0}
        
#         # Very high theta should give probability close to 1
#         result_high = irf(10.0, params)
#         assert result_high > 0.99
        
#         # Very low theta should give probability close to 0
#         result_low = irf(-10.0, params)
#         assert result_low < 0.01


# class TestTRF:
#     """Test cases for the TRF (Test Characteristic Curve) function."""
    
#     def test_trf_basic(self):
#         """Test basic TRF calculation."""
#         theta = np.array([0.0, 1.0, -1.0])
#         a_params = np.array([1.0, 1.5])
#         b_params = np.array([0.0, 0.5])
        
#         result = trf(theta, a_params, b_params)
        
#         assert isinstance(result, np.ndarray)
#         assert len(result) == len(theta)
#         assert all(result >= 0)  # TRF should be non-negative
    
#     def test_trf_single_item(self):
#         """Test TRF with single item."""
#         theta = np.array([0.0])
#         a_params = np.array([1.0])
#         b_params = np.array([0.0])
        
#         result = trf(theta, a_params, b_params)
#         expected = irf(0.0, {'a': 1.0, 'b': 0.0})
        
#         assert abs(result[0] - expected) < 1e-10
    
#     def test_trf_multiple_items(self):
#         """Test TRF with multiple items."""
#         theta = np.array([0.0])
#         a_params = np.array([1.0, 1.5, 0.8])
#         b_params = np.array([0.0, 0.5, -0.3])
        
#         result = trf(theta, a_params, b_params)
        
#         # Should be sum of individual item probabilities
#         expected = (irf(0.0, {'a': 1.0, 'b': 0.0}) + 
#                    irf(0.0, {'a': 1.5, 'b': 0.5}) + 
#                    irf(0.0, {'a': 0.8, 'b': -0.3}))
        
#         assert abs(result[0] - expected) < 1e-10
    
#     def test_trf_monotonic_property(self):
#         """Test that TRF is monotonically increasing with theta."""
#         theta = np.array([-2.0, -1.0, 0.0, 1.0, 2.0])
#         a_params = np.array([1.0, 1.2])
#         b_params = np.array([0.0, 0.3])
        
#         result = trf(theta, a_params, b_params)
        
#         # TRF should be monotonically increasing
#         for i in range(len(result) - 1):
#             assert result[i] <= result[i + 1]
    
#     def test_trf_invalid_theta_type(self):
#         """Test that non-numpy array theta raises TypeError."""
#         theta = [0.0, 1.0]  # List instead of numpy array
#         a_params = np.array([1.0])
#         b_params = np.array([0.0])
        
#         with pytest.raises(TypeError, match="invalid type"):
#             trf(theta, a_params, b_params)
    
#     def test_trf_empty_arrays(self):
#         """Test TRF with empty parameter arrays."""
#         theta = np.array([0.0])
#         a_params = np.array([])
#         b_params = np.array([])
        
#         result = trf(theta, a_params, b_params)
#         assert result[0] == 0.0  # No items means TRF = 0


# if __name__ == "__main__":
#     pytest.main([__file__])
