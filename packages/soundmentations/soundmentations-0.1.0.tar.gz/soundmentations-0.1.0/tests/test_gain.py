"""
Unit tests for gain transforms.
Tests gain classes for mono audio support only.
"""
import pytest
import numpy as np
from unittest.mock import patch

from soundmentations.transforms.amplitude.gain import BaseGain, Gain


class TestBaseGain:
    """Test cases for the BaseGain base class."""
    
    def test_init_valid_probability(self):
        """Test initialization with valid probability values."""
        # Test default probability
        base_gain = BaseGain()
        assert base_gain.p == 1.0
        
        # Test custom probabilities
        for p in [0.0, 0.5, 1.0]:
            base_gain = BaseGain(p=p)
            assert base_gain.p == p
    
    def test_init_invalid_probability_type(self):
        """Test initialization with invalid probability types."""
        with pytest.raises(TypeError, match="p must be a float or int"):
            BaseGain(p="0.5")
        
        with pytest.raises(TypeError, match="p must be a float or int"):
            BaseGain(p=None)
    
    def test_init_invalid_probability_value(self):
        """Test initialization with invalid probability values."""
        with pytest.raises(ValueError, match="p must be between 0 and 1"):
            BaseGain(p=-0.1)
        
        with pytest.raises(ValueError, match="p must be between 0 and 1"):
            BaseGain(p=1.1)
    
    def test_call_invalid_samples_type(self):
        """Test __call__ with invalid samples type."""
        base_gain = BaseGain()
        
        # BaseGain doesn't have validation, but let's test with empty samples
        with pytest.raises(ValueError, match="Input samples cannot be empty"):
            base_gain(np.array([]), 44100)
    
    def test_call_empty_samples(self):
        """Test __call__ with empty samples."""
        base_gain = BaseGain()
        
        with pytest.raises(ValueError, match="Input samples cannot be empty"):
            base_gain(np.array([]), 44100)
    
    @patch('random.random')
    def test_probability_skip(self, mock_random):
        """Test that transformation is skipped based on probability."""
        mock_random.return_value = 0.8  # Greater than p=0.5
        
        base_gain = BaseGain(p=0.5)
        samples = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        
        result = base_gain(samples, 44100)
        np.testing.assert_array_equal(result, samples)
    
    def test_not_implemented_error(self):
        """Test that _gain raises NotImplementedError."""
        base_gain = BaseGain()
        samples = np.array([1.0, 2.0, 3.0])
        
        with pytest.raises(NotImplementedError):
            base_gain._gain(samples)


class TestGain:
    """Test cases for the Gain class."""
    
    def test_init_valid_parameters(self):
        """Test initialization with valid parameters."""
        # Test default parameters
        gain = Gain()
        assert gain.gain == 1.0
        assert gain.gain_factor == 10 ** (1.0 / 20)
        assert gain.clip is True
        assert gain.p == 1.0
        
        # Test custom parameters
        gain = Gain(gain=6.0, clip=False, p=0.7)
        assert gain.gain == 6.0
        assert gain.gain_factor == 10 ** (6.0 / 20)
        assert gain.clip is False
        assert gain.p == 0.7
    
    def test_gain_calculation(self):
        """Test gain factor calculation from dB values."""
        # Test 0 dB (no change)
        gain = Gain(gain=0.0)
        assert abs(gain.gain_factor - 1.0) < 1e-6
        
        # Test 6 dB (approximately 2x)
        gain = Gain(gain=6.0)
        expected_factor = 10 ** (6.0 / 20)
        assert abs(gain.gain_factor - expected_factor) < 1e-6
        
        # Test -6 dB (approximately 0.5x)
        gain = Gain(gain=-6.0)
        expected_factor = 10 ** (-6.0 / 20)
        assert abs(gain.gain_factor - expected_factor) < 1e-6
    
    def test_gain_application_no_clipping(self):
        """Test gain application without clipping."""
        gain = Gain(gain=6.0, clip=False)  # +6dB
        samples = np.array([0.1, 0.2, -0.1, 0.3], dtype=np.float32)
        
        result = gain(samples, 44100)
        expected = samples * gain.gain_factor
        
        np.testing.assert_array_almost_equal(result, expected, decimal=6)
    
    def test_gain_application_with_clipping(self):
        """Test gain application with clipping."""
        gain = Gain(gain=20.0, clip=True)  # Very high gain
        samples = np.array([0.5, 0.8, -0.7, 0.9], dtype=np.float32)
        
        result = gain(samples, 44100)
        
        # All values should be clipped to [-1, 1]
        assert np.all(result >= -1.0)
        assert np.all(result <= 1.0)
        
        # Some values should be clipped
        expected_unclipped = samples * gain.gain_factor
        assert np.any(expected_unclipped > 1.0) or np.any(expected_unclipped < -1.0)
    
    def test_gain_zero_db(self):
        """Test that 0 dB gain leaves audio unchanged."""
        gain = Gain(gain=0.0)
        samples = np.array([0.1, 0.2, -0.1, 0.3], dtype=np.float32)
        
        result = gain(samples, 44100)
        np.testing.assert_array_almost_equal(result, samples, decimal=6)
    
    def test_gain_positive_values(self):
        """Test gain with positive dB values (amplification)."""
        gain = Gain(gain=3.0, clip=False)  # +3dB
        samples = np.array([0.1, 0.2, -0.1, 0.3], dtype=np.float32)
        
        result = gain(samples, 44100)
        
        # Result should be louder than input
        assert np.all(np.abs(result) >= np.abs(samples))
    
    def test_gain_negative_values(self):
        """Test gain with negative dB values (attenuation)."""
        gain = Gain(gain=-6.0, clip=False)  # -6dB
        samples = np.array([0.1, 0.2, -0.1, 0.3], dtype=np.float32)
        
        result = gain(samples, 44100)
        
        # Result should be quieter than input
        assert np.all(np.abs(result) <= np.abs(samples))
    
    def test_gain_extreme_values(self):
        """Test gain with extreme values."""
        # Very high gain
        gain_high = Gain(gain=60.0, clip=True)
        samples = np.array([0.001, 0.002, -0.001], dtype=np.float32)
        result = gain_high(samples, 44100)
        assert np.all(np.abs(result) <= 1.0)  # Should be clipped
        
        # Very low gain
        gain_low = Gain(gain=-60.0, clip=False)
        samples = np.array([0.5, 1.0, -0.5], dtype=np.float32)
        result = gain_low(samples, 44100)
        assert np.all(np.abs(result) < 0.01)  # Should be very quiet
    
    def test_gain_different_sample_rates(self):
        """Test gain works with different sample rates."""
        gain = Gain(gain=3.0)
        samples = np.array([0.1, 0.2, 0.3], dtype=np.float32)
        
        for sample_rate in [22050, 44100, 48000, 96000]:
            result = gain(samples, sample_rate)
            expected = samples * gain.gain_factor
            if gain.clip:
                expected = np.clip(expected, -1.0, 1.0)
            np.testing.assert_array_almost_equal(result, expected, decimal=6)
    
    @patch('random.random')
    def test_probability_behavior(self, mock_random):
        """Test probability behavior."""
        mock_random.return_value = 0.3  # Less than p=0.5
        
        gain = Gain(gain=6.0, p=0.5)
        samples = np.array([0.1, 0.2, 0.3], dtype=np.float32)
        
        result = gain(samples, 44100)
        # Should apply gain
        expected = samples * gain.gain_factor
        np.testing.assert_array_almost_equal(result, expected, decimal=6)
        
        mock_random.return_value = 0.7  # Greater than p=0.5
        result = gain(samples, 44100)
        # Should not apply gain
        np.testing.assert_array_equal(result, samples)
    
    def test_gain_preserves_shape(self):
        """Test that gain preserves array shape."""
        gain = Gain(gain=3.0)
        samples = np.random.randn(1000).astype(np.float32)
        
        result = gain(samples, 44100)
        assert result.shape == samples.shape
        assert result.dtype == samples.dtype


class TestIntegrationAndEdgeCases:
    """Integration tests and edge case testing for mono audio only."""
    
    def test_very_small_values(self):
        """Test gain on very small audio values."""
        gain = Gain(gain=20.0, clip=False)  # High gain
        samples = np.array([1e-6, -1e-6, 1e-7], dtype=np.float32)
        
        result = gain(samples, 44100)
        assert np.all(np.abs(result) > np.abs(samples))
    
    def test_very_large_values(self):
        """Test gain on values at clipping threshold."""
        gain = Gain(gain=6.0, clip=True)
        samples = np.array([0.99, -0.99, 1.0, -1.0], dtype=np.float32)
        
        result = gain(samples, 44100)
        assert np.all(result >= -1.0)
        assert np.all(result <= 1.0)
    
    def test_zero_samples(self):
        """Test gain on zero samples."""
        gain = Gain(gain=20.0)
        samples = np.zeros(10, dtype=np.float32)
        
        result = gain(samples, 44100)
        np.testing.assert_array_equal(result, samples)
    
    def test_mixed_positive_negative(self):
        """Test gain on mixed positive and negative values."""
        gain = Gain(gain=3.0, clip=False)
        samples = np.array([0.1, -0.2, 0.3, -0.4, 0.0], dtype=np.float32)
        
        result = gain(samples, 44100)
        expected = samples * gain.gain_factor
        
        np.testing.assert_array_almost_equal(result, expected, decimal=6)
        
        # Check signs are preserved
        assert np.all(np.sign(result) == np.sign(samples))
    
    def test_single_sample(self):
        """Test gain on single sample."""
        gain = Gain(gain=6.0, clip=False)
        samples = np.array([0.5], dtype=np.float32)
        
        result = gain(samples, 44100)
        expected = samples * gain.gain_factor
        
        np.testing.assert_array_almost_equal(result, expected, decimal=6)
    
    def test_large_audio_array(self):
        """Test gain on large audio arrays."""
        gain = Gain(gain=3.0, clip=True)
        samples = np.random.randn(1000000).astype(np.float32) * 0.5
        
        result = gain(samples, 44100)
        
        assert len(result) == len(samples)
        assert result.dtype == np.float32
        assert np.all(result >= -1.0)
        assert np.all(result <= 1.0)
    
    def test_deterministic_behavior(self):
        """Test that gain application is deterministic."""
        gain = Gain(gain=6.0, clip=True)
        samples = np.random.randn(100).astype(np.float32)
        
        result1 = gain(samples, 44100)
        result2 = gain(samples, 44100)
        
        np.testing.assert_array_equal(result1, result2)
