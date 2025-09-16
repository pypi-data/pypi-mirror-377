"""
Unit tests for mask transforms.
Tests mask classes for mono audio support only.
"""
import pytest
import numpy as np
from unittest.mock import patch

from soundmentations.transforms.time.mask import BaseMask, Mask


class TestBaseMask:
    """Test cases for the BaseMask base class."""
    
    def test_init_valid_parameters(self):
        """Test initialization with valid parameters."""
        # Test default parameters
        base_mask = BaseMask()
        assert base_mask.mask_ratio == 0.2
        assert base_mask.p == 1.0
        
        # Test custom parameters
        base_mask = BaseMask(mask_ratio=0.5, p=0.7)
        assert base_mask.mask_ratio == 0.5
        assert base_mask.p == 0.7
    
    def test_init_invalid_mask_ratio_type(self):
        """Test initialization with invalid mask_ratio type."""
        with pytest.raises(TypeError):
            BaseMask(mask_ratio="0.5")
        
        with pytest.raises(TypeError):
            BaseMask(mask_ratio=None)
    
    def test_init_invalid_mask_ratio_value(self):
        """Test initialization with invalid mask_ratio value."""
        with pytest.raises(ValueError):
            BaseMask(mask_ratio=-0.1)
        
        with pytest.raises(ValueError):
            BaseMask(mask_ratio=1.1)
    
    def test_call_invalid_samples_type(self):
        """Test __call__ with invalid samples type."""
        base_mask = BaseMask()
        
        with pytest.raises(TypeError):
            base_mask([1, 2, 3], 44100)
        
        with pytest.raises(TypeError):
            base_mask("audio", 44100)
    
    def test_call_empty_samples(self):
        """Test __call__ with empty samples."""
        base_mask = BaseMask()
        
        with pytest.raises(ValueError):
            base_mask(np.array([]), 44100)
    
    def test_call_invalid_sample_rate_type(self):
        """Test __call__ with invalid sample rate type."""
        base_mask = BaseMask()
        samples = np.array([1.0, 2.0, 3.0])
        
        with pytest.raises(TypeError):
            base_mask(samples, "44100")
        
        with pytest.raises(TypeError):
            base_mask(samples, 44100.5)
    
    def test_call_invalid_sample_rate_value(self):
        """Test __call__ with invalid sample rate values."""
        base_mask = BaseMask()
        samples = np.array([1.0, 2.0, 3.0])
        
        with pytest.raises(ValueError):
            base_mask(samples, 0)
        
        with pytest.raises(ValueError):
            base_mask(samples, -44100)
    
    @patch('random.random')
    def test_probability_skip(self, mock_random):
        """Test that transformation is skipped based on probability."""
        mock_random.return_value = 0.8  # Greater than p=0.5
        
        base_mask = BaseMask(mask_ratio=0.5, p=0.5)
        samples = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        
        result = base_mask(samples, 44100)
        np.testing.assert_array_equal(result, samples)
    
    def test_not_implemented_error(self):
        """Test that _mask raises NotImplementedError."""
        base_mask = BaseMask()
        samples = np.array([1.0, 2.0, 3.0])
        
        with pytest.raises(NotImplementedError):
            base_mask._mask(samples, 44100)


class TestMask:
    """Test cases for the Mask class."""
    
    def test_init_valid_parameters(self):
        """Test initialization with valid parameters."""
        mask = Mask()
        assert mask.mask_ratio == 0.2
        assert mask.p == 1.0
        
        mask = Mask(mask_ratio=0.3, p=0.8)
        assert mask.mask_ratio == 0.3
        assert mask.p == 0.8
    
    def test_mask_basic_functionality(self):
        """Test basic masking functionality."""
        mask = Mask(mask_ratio=0.4)  # Mask 40% of audio
        samples = np.ones(100, dtype=np.float32)
        
        result = mask(samples, 44100)
        
        # Result should have same length
        assert len(result) == len(samples)
        
        # Some samples should be masked (set to 0)
        assert np.sum(result == 0) > 0
        
        # Some samples should remain unchanged
        assert np.sum(result == 1) > 0
    
    def test_mask_ratio_zero(self):
        """Test masking with ratio 0 (no masking)."""
        mask = Mask(mask_ratio=0.0)
        samples = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        
        result = mask(samples, 44100)
        np.testing.assert_array_equal(result, samples)
    
    def test_mask_ratio_one(self):
        """Test masking with ratio 1.0 (mask everything)."""
        mask = Mask(mask_ratio=1.0)
        samples = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        
        result = mask(samples, 44100)
        expected = np.zeros_like(samples)
        np.testing.assert_array_equal(result, expected)
    
    def test_mask_deterministic_behavior(self):
        """Test that masking is deterministic with same seed."""
        samples = np.random.randn(1000).astype(np.float32)
        mask = Mask(mask_ratio=0.3)
        
        # Set seed for reproducibility
        np.random.seed(42)
        result1 = mask(samples, 44100)
        
        np.random.seed(42)
        result2 = mask(samples, 44100)
        
        np.testing.assert_array_equal(result1, result2)
    
    def test_mask_different_sample_rates(self):
        """Test masking works with different sample rates."""
        mask = Mask(mask_ratio=0.2)
        samples = np.ones(100, dtype=np.float32)
        
        for sample_rate in [22050, 44100, 48000, 96000]:
            result = mask(samples, sample_rate)
            assert len(result) == len(samples)
            assert np.sum(result == 0) > 0  # Some masking should occur
    
    @patch('random.random')
    def test_probability_behavior(self, mock_random):
        """Test probability behavior."""
        mock_random.return_value = 0.3  # Less than p=0.5
        
        mask = Mask(mask_ratio=0.5, p=0.5)
        samples = np.ones(100, dtype=np.float32)
        
        result = mask(samples, 44100)
        # Should apply masking
        assert np.sum(result == 0) > 0
        
        mock_random.return_value = 0.7  # Greater than p=0.5
        result = mask(samples, 44100)
        # Should not apply masking
        np.testing.assert_array_equal(result, samples)


class TestIntegrationAndEdgeCases:
    """Integration tests and edge case testing for mono audio only."""
    
    def test_very_short_audio(self):
        """Test masking on very short audio samples."""
        mask = Mask(mask_ratio=0.5)
        samples = np.array([1.0, 2.0], dtype=np.float32)
        
        result = mask(samples, 44100)
        assert len(result) == 2
    
    def test_single_sample_audio(self):
        """Test masking on single sample."""
        mask = Mask(mask_ratio=0.5)
        samples = np.array([1.0], dtype=np.float32)
        
        result = mask(samples, 44100)
        assert len(result) == 1
    
    def test_large_audio(self):
        """Test masking on large audio arrays."""
        mask = Mask(mask_ratio=0.1)
        samples = np.random.randn(1000000).astype(np.float32)
        
        result = mask(samples, 44100)
        assert len(result) == len(samples)
        
        # Check that approximately 10% is masked
        masked_ratio = np.sum(result == 0) / len(result)
        assert 0.05 < masked_ratio < 0.15  # Allow some variance
    
    def test_different_audio_values(self):
        """Test masking preserves non-masked values correctly."""
        mask = Mask(mask_ratio=0.0)  # No masking
        samples = np.array([-1.0, -0.5, 0.0, 0.5, 1.0], dtype=np.float32)
        
        result = mask(samples, 44100)
        np.testing.assert_array_equal(result, samples)
    
    def test_float32_precision(self):
        """Test that masking maintains float32 precision."""
        mask = Mask(mask_ratio=0.0)
        samples = np.array([0.123456789], dtype=np.float32)
        
        result = mask(samples, 44100)
        assert result.dtype == np.float32
        np.testing.assert_array_equal(result, samples)
