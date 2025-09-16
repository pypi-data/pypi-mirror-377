"""
Unit tests for fade transforms.
Tests fade classes for mono audio support only.
"""
import pytest
import numpy as np
from unittest.mock import patch

from soundmentations.transforms.amplitude.fade import BaseFade, FadeIn, FadeOut


class TestBaseFade:
    """Test cases for the BaseFade base class."""
    
    def test_init_valid_probability(self):
        """Test initialization with valid probability values."""
        # Test default probability
        base_fade = BaseFade()
        assert base_fade.p == 1.0
        
        # Test custom probabilities
        for p in [0.0, 0.5, 1.0]:
            base_fade = BaseFade(p=p)
            assert base_fade.p == p
    
    def test_validate_duration_param_valid(self):
        """Test duration parameter validation with valid values."""
        base_fade = BaseFade()
        
        # Should not raise for valid durations
        base_fade.validate_duration_param(1.0)
        base_fade.validate_duration_param(0.5)
        base_fade.validate_duration_param(5)
        base_fade.validate_duration_param(0.001)
    
    def test_validate_duration_param_invalid_type(self):
        """Test duration parameter validation with invalid types."""
        base_fade = BaseFade()
        
        with pytest.raises(TypeError, match="duration must be a float or an integer"):
            base_fade.validate_duration_param("1.0")
        
        with pytest.raises(TypeError, match="duration must be a float or an integer"):
            base_fade.validate_duration_param(None)
        
        with pytest.raises(TypeError, match="duration must be a float or an integer"):
            base_fade.validate_duration_param([1.0])
    
    def test_validate_duration_param_invalid_value(self):
        """Test duration parameter validation with invalid values."""
        base_fade = BaseFade()
        
        with pytest.raises(ValueError, match="duration must be positive"):
            base_fade.validate_duration_param(0.0)
        
        with pytest.raises(ValueError, match="duration must be positive"):
            base_fade.validate_duration_param(-1.0)
        
        with pytest.raises(ValueError, match="duration must be positive"):
            base_fade.validate_duration_param(-0.001)
    
    def test_call_invalid_samples_type(self):
        """Test __call__ with invalid samples type."""
        base_fade = BaseFade()
        
        with pytest.raises(TypeError):
            base_fade([1, 2, 3], 44100)
        
        with pytest.raises(TypeError):
            base_fade("audio", 44100)
    
    def test_call_empty_samples(self):
        """Test __call__ with empty samples."""
        base_fade = BaseFade()
        
        with pytest.raises(ValueError):
            base_fade(np.array([]), 44100)
    
    def test_call_non_1d_samples(self):
        """Test __call__ with non-1D samples."""
        base_fade = BaseFade()
        
        with pytest.raises(ValueError):
            base_fade(np.array([[1, 2], [3, 4]]), 44100)
    
    def test_call_invalid_sample_rate_type(self):
        """Test __call__ with invalid sample rate type."""
        base_fade = BaseFade()
        samples = np.array([1.0, 2.0, 3.0])
        
        with pytest.raises(TypeError):
            base_fade(samples, "44100")
        
        with pytest.raises(TypeError):
            base_fade(samples, 44100.5)
    
    def test_call_invalid_sample_rate_value(self):
        """Test __call__ with invalid sample rate values."""
        base_fade = BaseFade()
        samples = np.array([1.0, 2.0, 3.0])
        
        with pytest.raises(ValueError):
            base_fade(samples, 0)
        
        with pytest.raises(ValueError):
            base_fade(samples, -44100)
    
    @patch('random.random')
    def test_probability_skip(self, mock_random):
        """Test that transformation is skipped based on probability."""
        mock_random.return_value = 0.8  # Greater than p=0.5
        
        base_fade = BaseFade(p=0.5)
        samples = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        
        result = base_fade(samples, 44100)
        np.testing.assert_array_equal(result, samples)
    
    def test_not_implemented_error(self):
        """Test that _fade raises NotImplementedError."""
        base_fade = BaseFade()
        samples = np.array([1.0, 2.0, 3.0])
        
        with pytest.raises(NotImplementedError):
            base_fade._fade(samples, 44100)


class TestFadeIn:
    """Test cases for the FadeIn class."""
    
    def test_init_valid_parameters(self):
        """Test initialization with valid parameters."""
        # Test default parameters
        fade_in = FadeIn()
        assert fade_in.duration == 0.1
        assert fade_in.p == 1.0
        
        # Test custom parameters
        fade_in = FadeIn(duration=0.5, p=0.7)
        assert fade_in.duration == 0.5
        assert fade_in.p == 0.7
    
    def test_init_invalid_duration_type(self):
        """Test initialization with invalid duration type."""
        with pytest.raises(TypeError, match="duration must be a float or an integer"):
            FadeIn(duration="0.5")
        
        with pytest.raises(TypeError, match="duration must be a float or an integer"):
            FadeIn(duration=None)
    
    def test_init_invalid_duration_value(self):
        """Test initialization with invalid duration value."""
        with pytest.raises(ValueError, match="duration must be positive"):
            FadeIn(duration=0.0)
        
        with pytest.raises(ValueError, match="duration must be positive"):
            FadeIn(duration=-0.5)
    
    def test_fade_in_basic_functionality(self):
        """Test basic fade-in functionality."""
        fade_in = FadeIn(duration=0.1)  # 0.1 second fade
        sample_rate = 44100
        samples = np.ones(sample_rate, dtype=np.float32)  # 1 second of audio
        
        result = fade_in(samples, sample_rate)
        
        # Result should have same length
        assert len(result) == len(samples)
        
        # First sample should be 0 (start of fade)
        assert abs(result[0]) < 1e-6
        
        # Fade duration in samples
        fade_samples = int(0.1 * sample_rate)
        
        # Samples after fade should be unchanged
        np.testing.assert_array_almost_equal(result[fade_samples:], samples[fade_samples:], decimal=6)
        
        # Samples during fade should be increasing
        fade_region = result[:fade_samples]
        assert np.all(fade_region[1:] >= fade_region[:-1])  # Non-decreasing
    
    def test_fade_in_short_duration(self):
        """Test fade-in with very short duration."""
        fade_in = FadeIn(duration=0.01)  # 10ms fade
        sample_rate = 44100
        samples = np.ones(1000, dtype=np.float32)
        
        result = fade_in(samples, sample_rate)
        
        # Should start at 0
        assert abs(result[0]) < 1e-6
        
        # Should reach full amplitude quickly
        fade_samples = int(0.01 * sample_rate)
        assert fade_samples < len(samples)
        
        # Check fade region is smooth
        fade_region = result[:fade_samples + 1]
        assert np.all(fade_region[1:] >= fade_region[:-1])
    
    def test_fade_in_long_duration(self):
        """Test fade-in with duration covering entire audio."""
        fade_in = FadeIn(duration=1.0)  # 1 second fade
        sample_rate = 44100
        samples = np.ones(sample_rate, dtype=np.float32)  # Exactly 1 second
        
        result = fade_in(samples, sample_rate)
        
        # Should start at 0
        assert abs(result[0]) < 1e-6
        
        # Should end at original amplitude
        assert abs(result[-1] - samples[-1]) < 1e-6
        
        # Should be monotonically increasing
        assert np.all(result[1:] >= result[:-1])
    
    def test_fade_in_exceeds_audio_length(self):
        """Test fade-in when duration exceeds audio length."""
        fade_in = FadeIn(duration=2.0)  # 2 second fade
        sample_rate = 44100
        samples = np.ones(sample_rate // 2, dtype=np.float32)  # 0.5 seconds
        
        result = fade_in(samples, sample_rate)
        
        # Should still work, fading over entire audio length
        assert abs(result[0]) < 1e-6
        assert np.all(result[1:] >= result[:-1])
    
    def test_fade_in_different_amplitudes(self):
        """Test fade-in on different amplitude levels."""
        fade_in = FadeIn(duration=0.1)
        sample_rate = 44100
        
        for amplitude in [0.1, 0.5, 1.0, 2.0]:
            samples = np.full(sample_rate, amplitude, dtype=np.float32)
            result = fade_in(samples, sample_rate)
            
            # Should start at 0
            assert abs(result[0]) < 1e-6
            
            # Should end at original amplitude
            fade_samples = int(0.1 * sample_rate)
            if fade_samples < len(samples):
                assert abs(result[fade_samples:].mean() - amplitude) < 1e-3
    
    def test_fade_in_different_sample_rates(self):
        """Test fade-in works with different sample rates."""
        fade_in = FadeIn(duration=0.1)
        
        for sample_rate in [22050, 44100, 48000, 96000]:
            samples = np.ones(sample_rate, dtype=np.float32)
            result = fade_in(samples, sample_rate)
            
            assert len(result) == len(samples)
            assert abs(result[0]) < 1e-6
            
            fade_samples = int(0.1 * sample_rate)
            if fade_samples < len(samples):
                np.testing.assert_array_almost_equal(
                    result[fade_samples:], 
                    samples[fade_samples:], 
                    decimal=6
                )
    
    @patch('random.random')
    def test_probability_behavior(self, mock_random):
        """Test probability behavior."""
        mock_random.return_value = 0.3  # Less than p=0.5
        
        fade_in = FadeIn(duration=0.1, p=0.5)
        samples = np.ones(1000, dtype=np.float32)
        
        result = fade_in(samples, 44100)
        # Should apply fade-in
        assert abs(result[0]) < 1e-6
        
        mock_random.return_value = 0.7  # Greater than p=0.5
        result = fade_in(samples, 44100)
        # Should not apply fade-in
        np.testing.assert_array_equal(result, samples)


class TestFadeOut:
    """Test cases for the FadeOut class."""
    
    def test_init_valid_parameters(self):
        """Test initialization with valid parameters."""
        # Test default parameters
        fade_out = FadeOut()
        assert fade_out.duration == 0.1
        assert fade_out.p == 1.0
        
        # Test custom parameters
        fade_out = FadeOut(duration=0.5, p=0.7)
        assert fade_out.duration == 0.5
        assert fade_out.p == 0.7
    
    def test_init_invalid_duration_type(self):
        """Test initialization with invalid duration type."""
        with pytest.raises(TypeError, match="duration must be a float or an integer"):
            FadeOut(duration="0.5")
        
        with pytest.raises(TypeError, match="duration must be a float or an integer"):
            FadeOut(duration=None)
    
    def test_init_invalid_duration_value(self):
        """Test initialization with invalid duration value."""
        with pytest.raises(ValueError, match="duration must be positive"):
            FadeOut(duration=0.0)
        
        with pytest.raises(ValueError, match="duration must be positive"):
            FadeOut(duration=-0.5)
    
    def test_fade_out_basic_functionality(self):
        """Test basic fade-out functionality."""
        fade_out = FadeOut(duration=0.1)  # 0.1 second fade
        sample_rate = 44100
        samples = np.ones(sample_rate, dtype=np.float32)  # 1 second of audio
        
        result = fade_out(samples, sample_rate)
        
        # Result should have same length
        assert len(result) == len(samples)
        
        # Last sample should be 0 (end of fade)
        assert abs(result[-1]) < 1e-6
        
        # Fade duration in samples
        fade_samples = int(0.1 * sample_rate)
        
        # Samples before fade should be unchanged
        np.testing.assert_array_almost_equal(result[:-fade_samples], samples[:-fade_samples], decimal=6)
        
        # Samples during fade should be decreasing
        fade_region = result[-fade_samples:]
        assert np.all(fade_region[1:] <= fade_region[:-1])  # Non-increasing
    
    def test_fade_out_short_duration(self):
        """Test fade-out with very short duration."""
        fade_out = FadeOut(duration=0.01)  # 10ms fade
        sample_rate = 44100
        samples = np.ones(1000, dtype=np.float32)
        
        result = fade_out(samples, sample_rate)
        
        # Should end at 0
        assert abs(result[-1]) < 1e-6
        
        # Should maintain amplitude before fade
        fade_samples = int(0.01 * sample_rate)
        if fade_samples < len(samples):
            assert abs(result[:-fade_samples].mean() - 1.0) < 1e-3
    
    def test_fade_out_long_duration(self):
        """Test fade-out with duration covering entire audio."""
        fade_out = FadeOut(duration=1.0)  # 1 second fade
        sample_rate = 44100
        samples = np.ones(sample_rate, dtype=np.float32)  # Exactly 1 second
        
        result = fade_out(samples, sample_rate)
        
        # Should start at original amplitude
        assert abs(result[0] - samples[0]) < 1e-6
        
        # Should end at 0
        assert abs(result[-1]) < 1e-6
        
        # Should be monotonically decreasing
        assert np.all(result[1:] <= result[:-1])
    
    def test_fade_out_exceeds_audio_length(self):
        """Test fade-out when duration exceeds audio length."""
        fade_out = FadeOut(duration=2.0)  # 2 second fade
        sample_rate = 44100
        samples = np.ones(sample_rate // 2, dtype=np.float32)  # 0.5 seconds
        
        result = fade_out(samples, sample_rate)
        
        # Should still work, fading over entire audio length
        assert abs(result[-1]) < 1e-6
        assert np.all(result[1:] <= result[:-1])
    
    def test_fade_out_different_amplitudes(self):
        """Test fade-out on different amplitude levels."""
        fade_out = FadeOut(duration=0.1)
        sample_rate = 44100
        
        for amplitude in [0.1, 0.5, 1.0, 2.0]:
            samples = np.full(sample_rate, amplitude, dtype=np.float32)
            result = fade_out(samples, sample_rate)
            
            # Should end at 0
            assert abs(result[-1]) < 1e-6
            
            # Should start at original amplitude
            fade_samples = int(0.1 * sample_rate)
            if fade_samples < len(samples):
                assert abs(result[:-fade_samples].mean() - amplitude) < 1e-3
    
    def test_fade_out_different_sample_rates(self):
        """Test fade-out works with different sample rates."""
        fade_out = FadeOut(duration=0.1)
        
        for sample_rate in [22050, 44100, 48000, 96000]:
            samples = np.ones(sample_rate, dtype=np.float32)
            result = fade_out(samples, sample_rate)
            
            assert len(result) == len(samples)
            assert abs(result[-1]) < 1e-6
            
            fade_samples = int(0.1 * sample_rate)
            if fade_samples < len(samples):
                np.testing.assert_array_almost_equal(
                    result[:-fade_samples], 
                    samples[:-fade_samples], 
                    decimal=6
                )
    
    @patch('random.random')
    def test_probability_behavior(self, mock_random):
        """Test probability behavior."""
        mock_random.return_value = 0.3  # Less than p=0.5
        
        fade_out = FadeOut(duration=0.1, p=0.5)
        samples = np.ones(1000, dtype=np.float32)
        
        result = fade_out(samples, 44100)
        # Should apply fade-out
        assert abs(result[-1]) < 1e-6
        
        mock_random.return_value = 0.7  # Greater than p=0.5
        result = fade_out(samples, 44100)
        # Should not apply fade-out
        np.testing.assert_array_equal(result, samples)


class TestIntegrationAndEdgeCases:
    """Integration tests and edge case testing for mono audio only."""
    
    def test_very_short_audio(self):
        """Test fades on very short audio samples."""
        fade_in = FadeIn(duration=0.1)
        fade_out = FadeOut(duration=0.1)
        
        samples = np.array([1.0, 1.0], dtype=np.float32)
        
        result_in = fade_in(samples, 44100)
        result_out = fade_out(samples, 44100)
        
        assert len(result_in) == len(samples)
        assert len(result_out) == len(samples)
    
    def test_single_sample_audio(self):
        """Test fades on single sample."""
        fade_in = FadeIn(duration=0.1)
        fade_out = FadeOut(duration=0.1)
        
        samples = np.array([1.0], dtype=np.float32)
        
        result_in = fade_in(samples, 44100)
        result_out = fade_out(samples, 44100)
        
        assert len(result_in) == 1
        assert len(result_out) == 1
        
        # Both should result in 0 for single sample
        assert abs(result_in[0]) < 1e-6
        assert abs(result_out[0]) < 1e-6
    
    def test_zero_samples(self):
        """Test fades on zero samples."""
        fade_in = FadeIn(duration=0.1)
        fade_out = FadeOut(duration=0.1)
        
        samples = np.zeros(1000, dtype=np.float32)
        
        result_in = fade_in(samples, 44100)
        result_out = fade_out(samples, 44100)
        
        np.testing.assert_array_equal(result_in, samples)
        np.testing.assert_array_equal(result_out, samples)
    
    def test_combined_fade_in_out(self):
        """Test combining fade-in and fade-out."""
        fade_in = FadeIn(duration=0.1)
        fade_out = FadeOut(duration=0.1)
        
        samples = np.ones(44100, dtype=np.float32)  # 1 second
        
        # Apply both fades
        result = fade_in(samples, 44100)
        result = fade_out(result, 44100)
        
        # Should start and end at 0
        assert abs(result[0]) < 1e-6
        assert abs(result[-1]) < 1e-6
        
        # Should have some middle region at full amplitude
        middle = result[len(result)//4:3*len(result)//4]
        assert np.any(middle > 0.9)
    
    def test_preserves_shape_and_dtype(self):
        """Test that fades preserve array shape and dtype."""
        fade_in = FadeIn(duration=0.1)
        fade_out = FadeOut(duration=0.1)
        
        samples = np.random.randn(1000).astype(np.float32)
        
        result_in = fade_in(samples, 44100)
        result_out = fade_out(samples, 44100)
        
        assert result_in.shape == samples.shape
        assert result_out.shape == samples.shape
        assert result_in.dtype == samples.dtype
        assert result_out.dtype == samples.dtype
    
    def test_deterministic_behavior(self):
        """Test that fading is deterministic."""
        fade_in = FadeIn(duration=0.1)
        fade_out = FadeOut(duration=0.1)
        
        samples = np.random.randn(1000).astype(np.float32)
        
        result_in1 = fade_in(samples, 44100)
        result_in2 = fade_in(samples, 44100)
        result_out1 = fade_out(samples, 44100)
        result_out2 = fade_out(samples, 44100)
        
        np.testing.assert_array_equal(result_in1, result_in2)
        np.testing.assert_array_equal(result_out1, result_out2)
