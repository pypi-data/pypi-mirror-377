"""
Unit tests for limiter transforms.
Tests limiter classes for mono audio support only.
"""
import pytest
import numpy as np
from unittest.mock import patch

from soundmentations.transforms.amplitude.limiter import BaseLimiter, Limiter


class TestBaseLimiter:
    """Test cases for the BaseLimiter base class."""
    
    def test_init_valid_probability(self):
        """Test initialization with valid probability values."""
        # Test default probability
        base_limiter = BaseLimiter()
        assert base_limiter.p == 1.0
        
        # Test custom probabilities
        for p in [0.0, 0.5, 1.0]:
            base_limiter = BaseLimiter(p=p)
            assert base_limiter.p == p
    
    def test_call_invalid_samples_type(self):
        """Test __call__ with invalid samples type."""
        base_limiter = BaseLimiter()
        
        with pytest.raises(TypeError):
            base_limiter([1, 2, 3], 44100)
        
        with pytest.raises(TypeError):
            base_limiter("audio", 44100)
    
    def test_call_empty_samples(self):
        """Test __call__ with empty samples."""
        base_limiter = BaseLimiter()
        
        with pytest.raises(ValueError):
            base_limiter(np.array([]), 44100)
    
    def test_call_non_1d_samples(self):
        """Test __call__ with non-1D samples."""
        base_limiter = BaseLimiter()
        
        with pytest.raises(ValueError):
            base_limiter(np.array([[1, 2], [3, 4]]), 44100)
    
    def test_call_invalid_sample_rate_type(self):
        """Test __call__ with invalid sample rate type."""
        base_limiter = BaseLimiter()
        samples = np.array([1.0, 2.0, 3.0])
        
        with pytest.raises(TypeError):
            base_limiter(samples, "44100")
        
        with pytest.raises(TypeError):
            base_limiter(samples, 44100.5)
    
    def test_call_invalid_sample_rate_value(self):
        """Test __call__ with invalid sample rate values."""
        base_limiter = BaseLimiter()
        samples = np.array([1.0, 2.0, 3.0])
        
        with pytest.raises(ValueError):
            base_limiter(samples, 0)
        
        with pytest.raises(ValueError):
            base_limiter(samples, -44100)
    
    @patch('random.random')
    def test_probability_skip(self, mock_random):
        """Test that transformation is skipped based on probability."""
        mock_random.return_value = 0.8  # Greater than p=0.5
        
        base_limiter = BaseLimiter(p=0.5)
        samples = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        
        result = base_limiter(samples, 44100)
        np.testing.assert_array_equal(result, samples)
    
    def test_not_implemented_error(self):
        """Test that _limit raises NotImplementedError."""
        base_limiter = BaseLimiter()
        samples = np.array([1.0, 2.0, 3.0])
        
        with pytest.raises(NotImplementedError):
            base_limiter._limit(samples, 44100)


class TestLimiter:
    """Test cases for the Limiter class."""
    
    def test_init_valid_parameters(self):
        """Test initialization with valid parameters."""
        # Test default parameters
        limiter = Limiter()
        assert limiter.threshold == -3.0
        assert limiter.p == 1.0
        
        # Test custom parameters
        limiter = Limiter(threshold=-6.0, p=0.7)
        assert limiter.threshold == -6.0
        assert limiter.p == 0.7
    
    def test_init_invalid_threshold_type(self):
        """Test initialization with invalid threshold type."""
        with pytest.raises(TypeError):
            Limiter(threshold="3.0")
        
        with pytest.raises(TypeError):
            Limiter(threshold=None)
    
    def test_basic_limiting_functionality(self):
        """Test basic limiting functionality."""
        limiter = Limiter(threshold=-6.0)  # -6dB threshold
        
        # Create samples that exceed the threshold
        samples = np.array([0.8, -0.8, 0.5, -0.5, 1.0, -1.0], dtype=np.float32)
        
        result = limiter(samples, 44100)
        
        # Result should have same length
        assert len(result) == len(samples)
        
        # Convert threshold to linear scale
        threshold_linear = 10 ** (limiter.threshold / 20)
        
        # No samples should exceed the threshold
        assert np.all(np.abs(result) <= threshold_linear * 1.01)  # Small tolerance for numerical precision
    
    def test_no_limiting_needed(self):
        """Test limiter when no limiting is needed."""
        limiter = Limiter(threshold=-6.0)
        threshold_linear = 10 ** (limiter.threshold / 20)
        
        # Create samples below threshold
        samples = np.array([0.1, -0.1, 0.2, -0.2], dtype=np.float32)
        assert np.all(np.abs(samples) < threshold_linear)
        
        result = limiter(samples, 44100)
        
        # Samples should be relatively unchanged (may have slight processing artifacts)
        np.testing.assert_array_almost_equal(result, samples, decimal=3)
    
    def test_threshold_conversion(self):
        """Test threshold conversion from dB to linear."""
        # Test various threshold values
        thresholds_db = [-1.0, -3.0, -6.0, -12.0, -20.0]
        
        for threshold_db in thresholds_db:
            limiter = Limiter(threshold=threshold_db)
            
            # Create a sample that definitely exceeds threshold
            samples = np.array([1.0, -1.0], dtype=np.float32)
            result = limiter(samples, 44100)
            
            # Check that output doesn't exceed threshold
            threshold_linear = 10 ** (threshold_db / 20)
            assert np.all(np.abs(result) <= threshold_linear * 1.01)
    
    def test_extreme_threshold_values(self):
        """Test limiter with extreme threshold values."""
        # Very low threshold
        limiter_low = Limiter(threshold=-40.0)
        samples = np.array([0.5, -0.5, 0.1, -0.1], dtype=np.float32)
        result = limiter_low(samples, 44100)
        
        threshold_linear = 10 ** (-40.0 / 20)
        assert np.all(np.abs(result) <= threshold_linear * 1.01)
        
        # Very high threshold (close to 0 dB)
        limiter_high = Limiter(threshold=-0.1)
        samples = np.array([0.8, -0.8], dtype=np.float32)
        result = limiter_high(samples, 44100)
        
        threshold_linear = 10 ** (-0.1 / 20)
        assert np.all(np.abs(result) <= threshold_linear * 1.01)
    
    def test_different_sample_rates(self):
        """Test limiter works with different sample rates."""
        limiter = Limiter(threshold=-6.0)
        samples = np.array([1.0, -1.0, 0.8, -0.8], dtype=np.float32)
        
        for sample_rate in [22050, 44100, 48000, 96000]:
            result = limiter(samples, sample_rate)
            assert len(result) == len(samples)
            
            threshold_linear = 10 ** (limiter.threshold / 20)
            assert np.all(np.abs(result) <= threshold_linear * 1.01)
    
    @patch('random.random')
    def test_probability_behavior(self, mock_random):
        """Test probability behavior."""
        mock_random.return_value = 0.3  # Less than p=0.5
        
        limiter = Limiter(threshold=-6.0, p=0.5)
        samples = np.array([1.0, -1.0], dtype=np.float32)
        
        result = limiter(samples, 44100)
        # Should apply limiting
        threshold_linear = 10 ** (limiter.threshold / 20)
        assert np.all(np.abs(result) <= threshold_linear * 1.01)
        
        mock_random.return_value = 0.7  # Greater than p=0.5
        result = limiter(samples, 44100)
        # Should not apply limiting
        np.testing.assert_array_equal(result, samples)
    
    def test_preserves_shape_and_dtype(self):
        """Test that limiter preserves array shape and dtype."""
        limiter = Limiter(threshold=-3.0)
        samples = np.random.randn(1000).astype(np.float32)
        
        result = limiter(samples, 44100)
        assert result.shape == samples.shape
        assert result.dtype == samples.dtype
    
    def test_zero_samples(self):
        """Test limiter on zero samples."""
        limiter = Limiter(threshold=-6.0)
        samples = np.zeros(10, dtype=np.float32)
        
        result = limiter(samples, 44100)
        np.testing.assert_array_equal(result, samples)
    
    def test_signs_preserved(self):
        """Test that limiting preserves the sign of samples."""
        limiter = Limiter(threshold=-6.0)
        samples = np.array([0.8, -0.8, 0.5, -0.5], dtype=np.float32)
        
        result = limiter(samples, 44100)
        
        # Signs should be preserved
        assert np.all(np.sign(result) == np.sign(samples))


class TestIntegrationAndEdgeCases:
    """Integration tests and edge case testing for mono audio only."""
    
    def test_very_short_audio(self):
        """Test limiting on very short audio samples."""
        limiter = Limiter(threshold=-6.0)
        samples = np.array([1.0, -1.0], dtype=np.float32)
        
        result = limiter(samples, 44100)
        assert len(result) == 2
        
        threshold_linear = 10 ** (limiter.threshold / 20)
        assert np.all(np.abs(result) <= threshold_linear * 1.01)
    
    def test_single_sample_audio(self):
        """Test limiting on single sample."""
        limiter = Limiter(threshold=-6.0)
        samples = np.array([1.0], dtype=np.float32)
        
        result = limiter(samples, 44100)
        assert len(result) == 1
        
        threshold_linear = 10 ** (limiter.threshold / 20)
        assert np.abs(result[0]) <= threshold_linear * 1.01
    
    def test_large_audio(self):
        """Test limiting on large audio arrays."""
        limiter = Limiter(threshold=-6.0)
        samples = np.random.randn(1000000).astype(np.float32)
        
        result = limiter(samples, 44100)
        assert len(result) == len(samples)
        
        threshold_linear = 10 ** (limiter.threshold / 20)
        assert np.all(np.abs(result) <= threshold_linear * 1.01)
    
    def test_alternating_values(self):
        """Test limiting on alternating high/low values."""
        limiter = Limiter(threshold=-6.0)
        samples = np.array([1.0, 0.1, -1.0, 0.2, 0.9, -0.1], dtype=np.float32)
        
        result = limiter(samples, 44100)
        
        threshold_linear = 10 ** (limiter.threshold / 20)
        assert np.all(np.abs(result) <= threshold_linear * 1.01)
        
        # Small values should be relatively unchanged
        small_indices = np.abs(samples) < threshold_linear
        if np.any(small_indices):
            np.testing.assert_array_almost_equal(
                result[small_indices], 
                samples[small_indices], 
                decimal=2
            )
    
    def test_deterministic_behavior(self):
        """Test that limiting is deterministic."""
        limiter = Limiter(threshold=-6.0)
        samples = np.random.randn(100).astype(np.float32)
        
        result1 = limiter(samples, 44100)
        result2 = limiter(samples, 44100)
        
        np.testing.assert_array_equal(result1, result2)
    
    def test_limiting_effectiveness(self):
        """Test that limiting is actually effective."""
        limiter = Limiter(threshold=-3.0)
        threshold_linear = 10 ** (limiter.threshold / 20)
        
        # Create samples that definitely exceed threshold
        samples = np.array([1.0, -1.0, 0.95, -0.95], dtype=np.float32)
        assert np.all(np.abs(samples) > threshold_linear)
        
        result = limiter(samples, 44100)
        
        # All results should be at or below threshold
        assert np.all(np.abs(result) <= threshold_linear * 1.01)
        
        # But should not be zero (unless threshold is very low)
        if limiter.threshold > -20:
            assert np.all(np.abs(result) > 0.001)
