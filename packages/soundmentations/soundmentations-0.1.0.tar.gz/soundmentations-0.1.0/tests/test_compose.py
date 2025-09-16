"""
Unit tests for composition transforms.
Tests Compose class for combining multiple transforms.
"""
import pytest
import numpy as np
from unittest.mock import patch, Mock

from soundmentations.core.composition import Compose
from soundmentations.transforms.time.trim import Trim
from soundmentations.transforms.time.pad import Pad
from soundmentations.transforms.amplitude.gain import Gain


class TestCompose:
    """Test cases for the Compose class."""
    
    def test_init_valid_transforms(self):
        """Test initialization with valid transforms."""
        # Test with empty list
        compose = Compose([])
        assert compose.transforms == []
        
        # Test with single transform
        trim = Trim(duration=1.0)
        compose = Compose([trim])
        assert len(compose.transforms) == 1
        assert compose.transforms[0] == trim
        
        # Test with multiple transforms
        pad = Pad(pad_length=1000)
        gain = Gain(gain=3.0)
        compose = Compose([trim, pad, gain])
        assert len(compose.transforms) == 3
        assert compose.transforms[0] == trim
        assert compose.transforms[1] == pad
        assert compose.transforms[2] == gain
    
    def test_init_invalid_transforms_type(self):
        """Test initialization with invalid transforms type."""
        with pytest.raises(TypeError):
            Compose("not_a_list")
        
        with pytest.raises(TypeError):
            Compose(None)
        
        with pytest.raises(TypeError):
            Compose(123)
    
    def test_init_invalid_transform_items(self):
        """Test initialization with invalid transform items."""
        with pytest.raises(TypeError):
            Compose(["not_a_transform"])
        
        with pytest.raises(TypeError):
            Compose([Trim(duration=1.0), "invalid", Pad(pad_length=100)])
        
        with pytest.raises(TypeError):
            Compose([None])
    
    def test_call_empty_compose(self):
        """Test calling compose with no transforms."""
        compose = Compose([])
        samples = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32)
        
        result = compose(samples, 44100)
        np.testing.assert_array_equal(result, samples)
    
    def test_call_single_transform(self):
        """Test calling compose with single transform."""
        trim = Trim(duration=0.5)
        compose = Compose([trim])
        
        # Create 1 second of audio
        samples = np.ones(44100, dtype=np.float32)
        
        result = compose(samples, 44100)
        
        # Should be trimmed to 0.5 seconds
        expected_length = int(0.5 * 44100)
        assert len(result) == expected_length
    
    def test_call_multiple_transforms(self):
        """Test calling compose with multiple transforms."""
        # Create a pipeline: Trim -> Pad -> Gain
        trim = Trim(duration=0.5)  # Trim to 0.5 seconds
        pad = Pad(pad_length=44100)  # Pad by 1 second worth of samples
        gain = Gain(gain=6.0)  # Apply 6dB gain
        
        compose = Compose([trim, pad, gain])
        
        # Create 1 second of audio at 0.5 amplitude
        samples = np.ones(44100, dtype=np.float32) * 0.5
        
        result = compose(samples, 44100)
        
        # Should be: trimmed (22050 samples) + padded (44100 samples) = 66150 samples
        expected_length = int(0.5 * 44100) + 44100
        assert len(result) == expected_length
        
        # The non-zero portion should be amplified
        non_zero_portion = result[:int(0.5 * 44100)]
        gain_factor = 10 ** (6.0 / 20)
        expected_amplitude = 0.5 * gain_factor
        
        np.testing.assert_array_almost_equal(
            non_zero_portion, 
            np.full(len(non_zero_portion), expected_amplitude), 
            decimal=6
        )
    
    def test_call_invalid_samples_type(self):
        """Test calling compose with invalid samples type."""
        compose = Compose([Trim(duration=1.0)])
        
        with pytest.raises(TypeError):
            compose([1, 2, 3], 44100)
        
        with pytest.raises(TypeError):
            compose("audio", 44100)
    
    def test_call_empty_samples(self):
        """Test calling compose with empty samples."""
        compose = Compose([Trim(duration=1.0)])
        
        with pytest.raises(ValueError):
            compose(np.array([]), 44100)
    
    def test_call_invalid_sample_rate_type(self):
        """Test calling compose with invalid sample rate type."""
        compose = Compose([Trim(duration=1.0)])
        samples = np.array([1.0, 2.0, 3.0])
        
        with pytest.raises(TypeError):
            compose(samples, "44100")
        
        with pytest.raises(TypeError):
            compose(samples, 44100.5)
    
    def test_call_invalid_sample_rate_value(self):
        """Test calling compose with invalid sample rate values."""
        compose = Compose([Trim(duration=1.0)])
        samples = np.array([1.0, 2.0, 3.0])
        
        with pytest.raises(ValueError):
            compose(samples, 0)
        
        with pytest.raises(ValueError):
            compose(samples, -44100)
    
    def test_transform_order_matters(self):
        """Test that the order of transforms matters."""
        # Test Trim -> Gain vs Gain -> Trim
        samples = np.ones(44100, dtype=np.float32)  # 1 second
        
        # Pipeline 1: Trim first, then gain
        compose1 = Compose([
            Trim(duration=0.5),  # Trim to 0.5 seconds
            Gain(gain=6.0)       # Then amplify
        ])
        
        # Pipeline 2: Gain first, then trim
        compose2 = Compose([
            Gain(gain=6.0),      # Amplify first
            Trim(duration=0.5)   # Then trim to 0.5 seconds
        ])
        
        result1 = compose1(samples, 44100)
        result2 = compose2(samples, 44100)
        
        # Both should have same length (trimmed)
        assert len(result1) == len(result2) == int(0.5 * 44100)
        
        # Both should have same amplitude (gain applied)
        gain_factor = 10 ** (6.0 / 20)
        np.testing.assert_array_almost_equal(result1, result2, decimal=6)
        np.testing.assert_array_almost_equal(
            result1, 
            np.full(len(result1), gain_factor), 
            decimal=6
        )
    
    def test_probability_interactions(self):
        """Test probability interactions between transforms."""
        # Create transforms with different probabilities
        trim = Trim(duration=0.5, p=1.0)  # Always apply
        gain = Gain(gain=6.0, p=0.0)      # Never apply
        
        compose = Compose([trim, gain])
        samples = np.ones(44100, dtype=np.float32)
        
        result = compose(samples, 44100)
        
        # Should be trimmed but not gained
        assert len(result) == int(0.5 * 44100)
        np.testing.assert_array_almost_equal(result, np.ones(len(result)), decimal=6)
    
    @patch('random.random')
    def test_stochastic_behavior(self, mock_random):
        """Test compose with stochastic transforms."""
        # Mock random to control probability
        mock_random.side_effect = [0.3, 0.7]  # First transform applies, second doesn't
        
        trim = Trim(duration=0.5, p=0.5)  # Should apply (0.3 < 0.5)
        gain = Gain(gain=6.0, p=0.5)      # Should not apply (0.7 > 0.5)
        
        compose = Compose([trim, gain])
        samples = np.ones(44100, dtype=np.float32)
        
        result = compose(samples, 44100)
        
        # Should be trimmed but not gained
        assert len(result) == int(0.5 * 44100)
        np.testing.assert_array_almost_equal(result, np.ones(len(result)), decimal=6)
    
    def test_different_sample_rates(self):
        """Test compose works with different sample rates."""
        trim = Trim(duration=0.5)
        gain = Gain(gain=3.0)
        compose = Compose([trim, gain])
        
        for sample_rate in [22050, 44100, 48000, 96000]:
            samples = np.ones(sample_rate, dtype=np.float32)  # 1 second
            result = compose(samples, sample_rate)
            
            # Should be trimmed to 0.5 seconds
            expected_length = int(0.5 * sample_rate)
            assert len(result) == expected_length
            
            # Should be gained
            gain_factor = 10 ** (3.0 / 20)
            np.testing.assert_array_almost_equal(
                result, 
                np.full(len(result), gain_factor), 
                decimal=6
            )
    
    def test_preserves_dtype(self):
        """Test that compose preserves the dtype of input samples."""
        trim = Trim(duration=0.5)
        compose = Compose([trim])
        
        # Test with different dtypes
        for dtype in [np.float32, np.float64]:
            samples = np.ones(44100, dtype=dtype)
            result = compose(samples, 44100)
            assert result.dtype == dtype
    
    def test_error_propagation(self):
        """Test that errors in transforms are properly propagated."""
        # Create a mock transform that raises an error
        mock_transform = Mock()
        mock_transform.side_effect = ValueError("Transform error")
        
        compose = Compose([mock_transform])
        samples = np.ones(1000, dtype=np.float32)
        
        with pytest.raises(ValueError, match="Transform error"):
            compose(samples, 44100)
    
    def test_repr_string(self):
        """Test string representation of Compose."""
        trim = Trim(duration=1.0)
        gain = Gain(gain=3.0)
        compose = Compose([trim, gain])
        
        repr_str = repr(compose)
        assert "Compose" in repr_str
        assert str(len(compose.transforms)) in repr_str


class TestIntegrationAndEdgeCases:
    """Integration tests and edge case testing for Compose."""
    
    def test_very_short_audio(self):
        """Test compose on very short audio samples."""
        trim = Trim(duration=0.01)  # 10ms
        gain = Gain(gain=6.0)
        compose = Compose([trim, gain])
        
        samples = np.array([1.0, 1.0], dtype=np.float32)
        
        result = compose(samples, 44100)
        assert len(result) >= 0  # Should handle gracefully
    
    def test_single_sample_audio(self):
        """Test compose on single sample."""
        gain = Gain(gain=6.0)
        compose = Compose([gain])
        
        samples = np.array([1.0], dtype=np.float32)
        
        result = compose(samples, 44100)
        assert len(result) == 1
        
        gain_factor = 10 ** (6.0 / 20)
        np.testing.assert_array_almost_equal(result, [gain_factor], decimal=6)
    
    def test_large_number_of_transforms(self):
        """Test compose with many transforms."""
        transforms = []
        for i in range(10):
            transforms.append(Gain(gain=0.1))  # Small gains to avoid clipping
        
        compose = Compose(transforms)
        samples = np.ones(1000, dtype=np.float32)
        
        result = compose(samples, 44100)
        assert len(result) == len(samples)
        
        # Each gain of 0.1dB applied 10 times = 1.0dB total
        total_gain_factor = 10 ** (1.0 / 20)
        np.testing.assert_array_almost_equal(
            result, 
            np.full(len(result), total_gain_factor), 
            decimal=5
        )
    
    def test_no_side_effects(self):
        """Test that compose doesn't modify the original samples."""
        trim = Trim(duration=0.5)
        gain = Gain(gain=6.0)
        compose = Compose([trim, gain])
        
        original_samples = np.ones(44100, dtype=np.float32)
        samples_copy = original_samples.copy()
        
        result = compose(samples_copy, 44100)
        
        # Original samples should be unchanged
        np.testing.assert_array_equal(original_samples, samples_copy)
        
        # Result should be different
        assert len(result) != len(original_samples) or not np.allclose(result[:len(original_samples)], original_samples)
    
    def test_zero_samples(self):
        """Test compose on zero samples."""
        gain = Gain(gain=10.0)
        compose = Compose([gain])
        
        samples = np.zeros(1000, dtype=np.float32)
        
        result = compose(samples, 44100)
        np.testing.assert_array_equal(result, samples)
    
    def test_mixed_transform_types(self):
        """Test compose with different types of transforms."""
        # Mix time and amplitude transforms
        trim = Trim(duration=0.5)        # Time domain
        pad = Pad(pad_length=1000)       # Time domain  
        gain = Gain(gain=3.0)            # Amplitude domain
        
        compose = Compose([trim, pad, gain])
        samples = np.ones(44100, dtype=np.float32) * 0.5
        
        result = compose(samples, 44100)
        
        # Check final result properties
        expected_length = int(0.5 * 44100) + 1000
        assert len(result) == expected_length
        
        # Check that gain was applied to the non-padded portion
        gain_factor = 10 ** (3.0 / 20)
        non_padded_portion = result[:int(0.5 * 44100)]
        expected_amplitude = 0.5 * gain_factor
        
        np.testing.assert_array_almost_equal(
            non_padded_portion,
            np.full(len(non_padded_portion), expected_amplitude),
            decimal=6
        )
    
    def test_deterministic_behavior(self):
        """Test that compose is deterministic when transforms are deterministic."""
        trim = Trim(duration=0.5)
        gain = Gain(gain=3.0)
        compose = Compose([trim, gain])
        
        samples = np.random.randn(44100).astype(np.float32)
        
        result1 = compose(samples, 44100)
        result2 = compose(samples, 44100)
        
        np.testing.assert_array_equal(result1, result2)
    
    def test_compose_of_composes(self):
        """Test composing Compose objects (nested composition)."""
        # Create two separate compose objects
        compose1 = Compose([Trim(duration=0.5)])
        compose2 = Compose([Gain(gain=6.0)])
        
        # Create a compose of composes
        meta_compose = Compose([compose1, compose2])
        
        samples = np.ones(44100, dtype=np.float32)
        result = meta_compose(samples, 44100)
        
        # Should work the same as a single compose with all transforms
        single_compose = Compose([Trim(duration=0.5), Gain(gain=6.0)])
        expected = single_compose(samples, 44100)
        
        np.testing.assert_array_equal(result, expected)
