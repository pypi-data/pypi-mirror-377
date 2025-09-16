"""
Unit tests for pitch shift transforms.
Tests pitch shift classes for mono audio support only.
"""
import pytest
import numpy as np
from unittest.mock import patch

from soundmentations.transforms.frequency.pitch_shift import BasePitchShift, PitchShift, RandomPitchShift


class TestBasePitchShift:
    """Test cases for the BasePitchShift base class."""
    
    def test_init_valid_probability(self):
        """Test initialization with valid probability values."""
        # Test default probability
        base_pitch = BasePitchShift()
        assert base_pitch.p == 1.0
        
        # Test custom probabilities
        for p in [0.0, 0.5, 1.0]:
            base_pitch = BasePitchShift(p=p)
            assert base_pitch.p == p
    
    def test_call_invalid_samples_type(self):
        """Test __call__ with invalid samples type."""
        base_pitch = BasePitchShift()
        
        with pytest.raises(TypeError):
            base_pitch([1, 2, 3], 44100)
        
        with pytest.raises(TypeError):
            base_pitch("audio", 44100)
    
    def test_call_empty_samples(self):
        """Test __call__ with empty samples."""
        base_pitch = BasePitchShift()
        
        with pytest.raises(ValueError):
            base_pitch(np.array([]), 44100)
    
    def test_call_non_1d_samples(self):
        """Test __call__ with non-1D samples."""
        base_pitch = BasePitchShift()
        
        with pytest.raises(ValueError):
            base_pitch(np.array([[1, 2], [3, 4]]), 44100)
    
    def test_call_invalid_sample_rate_type(self):
        """Test __call__ with invalid sample rate type."""
        base_pitch = BasePitchShift()
        samples = np.array([1.0, 2.0, 3.0])
        
        with pytest.raises(TypeError):
            base_pitch(samples, "44100")
        
        with pytest.raises(TypeError):
            base_pitch(samples, 44100.5)
    
    def test_call_invalid_sample_rate_value(self):
        """Test __call__ with invalid sample rate values."""
        base_pitch = BasePitchShift()
        samples = np.array([1.0, 2.0, 3.0])
        
        with pytest.raises(ValueError):
            base_pitch(samples, 0)
        
        with pytest.raises(ValueError):
            base_pitch(samples, -44100)
    
    @patch('random.random')
    def test_probability_skip(self, mock_random):
        """Test that transformation is skipped based on probability."""
        mock_random.return_value = 0.8  # Greater than p=0.5
        
        base_pitch = BasePitchShift(p=0.5)
        samples = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        
        result = base_pitch(samples, 44100)
        np.testing.assert_array_equal(result, samples)
    
    def test_not_implemented_error(self):
        """Test that _pitch_shift raises NotImplementedError."""
        base_pitch = BasePitchShift()
        samples = np.array([1.0, 2.0, 3.0])
        
        with pytest.raises(NotImplementedError):
            base_pitch._pitch_shift(samples, 44100)


class TestPitchShift:
    """Test cases for the PitchShift class."""
    
    def test_init_valid_parameters(self):
        """Test initialization with valid parameters."""
        # Test default parameters
        pitch_shift = PitchShift()
        assert pitch_shift.semitones == 0.0
        assert pitch_shift.p == 1.0
        
        # Test custom parameters
        pitch_shift = PitchShift(semitones=2.0, p=0.7)
        assert pitch_shift.semitones == 2.0
        assert pitch_shift.p == 0.7
        
        # Test negative semitones
        pitch_shift = PitchShift(semitones=-3.5)
        assert pitch_shift.semitones == -3.5
    
    def test_init_invalid_semitones_type(self):
        """Test initialization with invalid semitones type."""
        with pytest.raises(TypeError):
            PitchShift(semitones="2.0")
        
        with pytest.raises(TypeError):
            PitchShift(semitones=None)
        
        with pytest.raises(TypeError):
            PitchShift(semitones=[2.0])
    
    def test_no_pitch_shift(self):
        """Test pitch shift with 0 semitones (no change)."""
        pitch_shift = PitchShift(semitones=0.0)
        samples = np.array([0.1, 0.2, -0.1, 0.3], dtype=np.float32)
        
        result = pitch_shift(samples, 44100)
        
        # Should return exactly the same samples for 0 semitones
        np.testing.assert_array_almost_equal(result, samples, decimal=6)
    
    def test_positive_pitch_shift(self):
        """Test pitch shift with positive semitones (higher pitch)."""
        pitch_shift = PitchShift(semitones=2.0)  # 2 semitones up
        
        # Create a simple sine wave
        t = np.linspace(0, 1, 44100, False)
        frequency = 440  # A4
        samples = np.sin(2 * np.pi * frequency * t).astype(np.float32)
        
        result = pitch_shift(samples, 44100)
        
        # Result should have same length
        assert len(result) == len(samples)
        
        # Result should be different from input
        assert not np.allclose(result, samples, atol=1e-3)
    
    def test_negative_pitch_shift(self):
        """Test pitch shift with negative semitones (lower pitch)."""
        pitch_shift = PitchShift(semitones=-2.0)  # 2 semitones down
        
        # Create a simple sine wave
        t = np.linspace(0, 1, 44100, False)
        frequency = 440  # A4
        samples = np.sin(2 * np.pi * frequency * t).astype(np.float32)
        
        result = pitch_shift(samples, 44100)
        
        # Result should have same length
        assert len(result) == len(samples)
        
        # Result should be different from input
        assert not np.allclose(result, samples, atol=1e-3)
    
    def test_extreme_pitch_shifts(self):
        """Test pitch shift with extreme values."""
        samples = np.random.randn(1000).astype(np.float32)
        
        # Very high pitch shift
        pitch_shift_high = PitchShift(semitones=12.0)  # One octave up
        result_high = pitch_shift_high(samples, 44100)
        assert len(result_high) == len(samples)
        
        # Very low pitch shift
        pitch_shift_low = PitchShift(semitones=-12.0)  # One octave down
        result_low = pitch_shift_low(samples, 44100)
        assert len(result_low) == len(samples)
        
        # Fractional pitch shift
        pitch_shift_frac = PitchShift(semitones=0.5)  # Quarter tone up
        result_frac = pitch_shift_frac(samples, 44100)
        assert len(result_frac) == len(samples)
    
    def test_different_sample_rates(self):
        """Test pitch shift works with different sample rates."""
        pitch_shift = PitchShift(semitones=3.0)
        samples = np.random.randn(1000).astype(np.float32)
        
        for sample_rate in [22050, 44100, 48000, 96000]:
            result = pitch_shift(samples, sample_rate)
            assert len(result) == len(samples)
            assert result.dtype == samples.dtype
    
    @patch('random.random')
    def test_probability_behavior(self, mock_random):
        """Test probability behavior."""
        mock_random.return_value = 0.3  # Less than p=0.5
        
        pitch_shift = PitchShift(semitones=2.0, p=0.5)
        samples = np.random.randn(100).astype(np.float32)
        
        result = pitch_shift(samples, 44100)
        # Should apply pitch shift (will be different from input unless semitones=0)
        assert not np.allclose(result, samples, atol=1e-6)
        
        mock_random.return_value = 0.7  # Greater than p=0.5
        result = pitch_shift(samples, 44100)
        # Should not apply pitch shift
        np.testing.assert_array_equal(result, samples)
    
    def test_preserves_shape_and_dtype(self):
        """Test that pitch shift preserves array shape and dtype."""
        pitch_shift = PitchShift(semitones=1.5)
        samples = np.random.randn(1000).astype(np.float32)
        
        result = pitch_shift(samples, 44100)
        assert result.shape == samples.shape
        assert result.dtype == samples.dtype
    
    def test_zero_samples(self):
        """Test pitch shift on zero samples."""
        pitch_shift = PitchShift(semitones=5.0)
        samples = np.zeros(1000, dtype=np.float32)
        
        result = pitch_shift(samples, 44100)
        # Zero samples should remain zero
        np.testing.assert_array_almost_equal(result, samples, decimal=6)


class TestRandomPitchShift:
    """Test cases for the RandomPitchShift class."""
    
    def test_init_valid_parameters(self):
        """Test initialization with valid parameters."""
        # Test default parameters
        random_pitch = RandomPitchShift()
        assert random_pitch.min_semitones == -2.0
        assert random_pitch.max_semitones == 2.0
        assert random_pitch.p == 1.0
        
        # Test custom parameters
        random_pitch = RandomPitchShift(
            min_semitones=-1.0, 
            max_semitones=3.0, 
            p=0.7
        )
        assert random_pitch.min_semitones == -1.0
        assert random_pitch.max_semitones == 3.0
        assert random_pitch.p == 0.7
    
    def test_init_invalid_semitones_type(self):
        """Test initialization with invalid semitones types."""
        with pytest.raises(TypeError):
            RandomPitchShift(min_semitones="1.0", max_semitones=2.0)
        
        with pytest.raises(TypeError):
            RandomPitchShift(min_semitones=1.0, max_semitones="2.0")
        
        with pytest.raises(TypeError):
            RandomPitchShift(min_semitones=None, max_semitones=2.0)
    
    def test_init_invalid_semitones_range(self):
        """Test initialization with invalid semitones range."""
        with pytest.raises(ValueError):
            RandomPitchShift(min_semitones=3.0, max_semitones=1.0)  # min > max
        
        with pytest.raises(ValueError):
            RandomPitchShift(min_semitones=2.0, max_semitones=2.0)  # min == max (should use PitchShift instead)
    
    @patch('random.uniform')
    def test_random_pitch_shift_selection(self, mock_uniform):
        """Test that random pitch shift values are selected correctly."""
        mock_uniform.return_value = 1.0  # Should select 1.0 semitone
        
        random_pitch = RandomPitchShift(min_semitones=-1.0, max_semitones=3.0)
        samples = np.random.randn(100).astype(np.float32)
        
        result = random_pitch(samples, 44100)
        
        # Should have called random.uniform with correct range
        mock_uniform.assert_called_with(-1.0, 3.0)
        assert len(result) == len(samples)
    
    @patch('random.uniform')
    def test_different_random_values(self, mock_uniform):
        """Test with different random values."""
        random_pitch = RandomPitchShift(min_semitones=-2.0, max_semitones=2.0)
        samples = np.random.randn(100).astype(np.float32)
        
        # Test with minimum value
        mock_uniform.return_value = -2.0
        result_min = random_pitch(samples, 44100)
        assert len(result_min) == len(samples)
        
        # Test with maximum value
        mock_uniform.return_value = 2.0
        result_max = random_pitch(samples, 44100)
        assert len(result_max) == len(samples)
        
        # Test with middle value
        mock_uniform.return_value = 0.0
        result_mid = random_pitch(samples, 44100)
        # With 0 semitones, should be close to original
        np.testing.assert_array_almost_equal(result_mid, samples, decimal=6)
    
    def test_random_pitch_shift_variability(self):
        """Test that random pitch shift produces varied results."""
        random_pitch = RandomPitchShift(min_semitones=-2.0, max_semitones=2.0)
        samples = np.random.randn(100).astype(np.float32)
        
        results = []
        for _ in range(10):
            result = random_pitch(samples, 44100)
            results.append(result)
        
        # Not all results should be exactly the same
        all_same = True
        for i in range(1, len(results)):
            if not np.allclose(results[0], results[i], atol=1e-6):
                all_same = False
                break
        
        # With random selection, results should vary
        assert not all_same, "Random pitch shift should produce varied results"
    
    def test_single_semitone_range(self):
        """Test with very narrow semitone range."""
        random_pitch = RandomPitchShift(min_semitones=0.9, max_semitones=1.1)
        samples = np.random.randn(100).astype(np.float32)
        
        result = random_pitch(samples, 44100)
        assert len(result) == len(samples)
        # Should apply some pitch shift
        assert not np.allclose(result, samples, atol=1e-3)
    
    def test_different_sample_rates(self):
        """Test random pitch shift works with different sample rates."""
        random_pitch = RandomPitchShift(min_semitones=-1.0, max_semitones=1.0)
        samples = np.random.randn(100).astype(np.float32)
        
        for sample_rate in [22050, 44100, 48000, 96000]:
            result = random_pitch(samples, sample_rate)
            assert len(result) == len(samples)
            assert result.dtype == samples.dtype
    
    @patch('random.random')
    def test_probability_behavior(self, mock_random):
        """Test probability behavior."""
        mock_random.return_value = 0.3  # Less than p=0.5
        
        random_pitch = RandomPitchShift(
            min_semitones=-2.0, 
            max_semitones=2.0, 
            p=0.5
        )
        samples = np.random.randn(100).astype(np.float32)
        
        # Should apply pitch shift (result should potentially be different)
        result = random_pitch(samples, 44100)
        assert len(result) == len(samples)
        
        mock_random.return_value = 0.7  # Greater than p=0.5
        result = random_pitch(samples, 44100)
        # Should not apply pitch shift
        np.testing.assert_array_equal(result, samples)
    
    def test_preserves_shape_and_dtype(self):
        """Test that random pitch shift preserves array shape and dtype."""
        random_pitch = RandomPitchShift(min_semitones=-1.0, max_semitones=1.0)
        samples = np.random.randn(1000).astype(np.float32)
        
        result = random_pitch(samples, 44100)
        assert result.shape == samples.shape
        assert result.dtype == samples.dtype


class TestIntegrationAndEdgeCases:
    """Integration tests and edge case testing for mono audio only."""
    
    def test_very_short_audio(self):
        """Test pitch shift on very short audio samples."""
        pitch_shift = PitchShift(semitones=2.0)
        random_pitch = RandomPitchShift(min_semitones=-1.0, max_semitones=1.0)
        
        samples = np.array([1.0, -1.0], dtype=np.float32)
        
        result1 = pitch_shift(samples, 44100)
        result2 = random_pitch(samples, 44100)
        
        assert len(result1) == len(samples)
        assert len(result2) == len(samples)
    
    def test_single_sample_audio(self):
        """Test pitch shift on single sample."""
        pitch_shift = PitchShift(semitones=3.0)
        random_pitch = RandomPitchShift(min_semitones=-2.0, max_semitones=2.0)
        
        samples = np.array([1.0], dtype=np.float32)
        
        result1 = pitch_shift(samples, 44100)
        result2 = random_pitch(samples, 44100)
        
        assert len(result1) == 1
        assert len(result2) == 1
    
    def test_large_audio(self):
        """Test pitch shift on large audio arrays."""
        pitch_shift = PitchShift(semitones=1.0)
        random_pitch = RandomPitchShift(min_semitones=-0.5, max_semitones=0.5)
        
        samples = np.random.randn(1000000).astype(np.float32)
        
        result1 = pitch_shift(samples, 44100)
        result2 = random_pitch(samples, 44100)
        
        assert len(result1) == len(samples)
        assert len(result2) == len(samples)
        assert result1.dtype == np.float32
        assert result2.dtype == np.float32
    
    def test_deterministic_behavior_pitch_shift(self):
        """Test that PitchShift is deterministic."""
        pitch_shift = PitchShift(semitones=2.0)
        samples = np.random.randn(1000).astype(np.float32)
        
        result1 = pitch_shift(samples, 44100)
        result2 = pitch_shift(samples, 44100)
        
        np.testing.assert_array_equal(result1, result2)
    
    def test_frequency_content_change(self):
        """Test that pitch shift actually changes frequency content."""
        # Create a pure tone
        t = np.linspace(0, 0.1, 4410, False)  # 0.1 seconds
        frequency = 440  # A4
        samples = np.sin(2 * np.pi * frequency * t).astype(np.float32)
        
        # Pitch shift up by one octave (12 semitones)
        pitch_shift = PitchShift(semitones=12.0)
        result = pitch_shift(samples, 44100)
        
        # Result should be different and roughly twice the frequency
        assert not np.allclose(result, samples, atol=1e-3)
        assert len(result) == len(samples)
    
    def test_zero_crossing_preservation(self):
        """Test behavior around zero crossings."""
        # Create signal with zero crossings
        samples = np.array([0.5, 0.0, -0.5, 0.0, 0.3], dtype=np.float32)
        
        pitch_shift = PitchShift(semitones=1.0)
        result = pitch_shift(samples, 44100)
        
        assert len(result) == len(samples)
        assert result.dtype == np.float32
    
    def test_edge_case_semitone_values(self):
        """Test with edge case semitone values."""
        samples = np.random.randn(100).astype(np.float32)
        
        # Very small pitch shift
        pitch_shift_tiny = PitchShift(semitones=0.01)
        result_tiny = pitch_shift_tiny(samples, 44100)
        assert len(result_tiny) == len(samples)
        
        # Very large pitch shift
        pitch_shift_large = PitchShift(semitones=24.0)  # Two octaves
        result_large = pitch_shift_large(samples, 44100)
        assert len(result_large) == len(samples)
        
        # Negative large pitch shift
        pitch_shift_neg_large = PitchShift(semitones=-24.0)
        result_neg_large = pitch_shift_neg_large(samples, 44100)
        assert len(result_neg_large) == len(samples)
