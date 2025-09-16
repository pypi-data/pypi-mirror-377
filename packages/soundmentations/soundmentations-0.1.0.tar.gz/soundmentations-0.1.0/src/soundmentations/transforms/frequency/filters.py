import numpy as np
from soundmentations.core.transforms_interface import BaseTransform

class BaseFilter(BaseTransform):
    """
    Base class for frequency filter transforms.

    This class provides a template for frequency filter transforms that modify
    the frequency response of the input audio sample according to specified parameters.
    Subclasses must implement the _filter method.
    """
    
    def __call__(self, sample: np.ndarray, sample_rate: int = 44100) -> np.ndarray:
        self.validate_audio(sample, sample_rate)

        if not self.should_apply():
            return sample

        return self._filter(sample, sample_rate)
    
    def _filter(self, sample: np.ndarray, sample_rate: int) -> np.ndarray:
        raise NotImplementedError("Subclasses must implement _filter method")
    
class LowPassFilter(BaseFilter):
    """
    Apply a low-pass filter to the audio sample.

    Parameters
    ----------
    cutoff_freq : float
        Cutoff frequency for the low-pass filter in Hz.
    p : float, optional
        Probability of applying the transform, by default 1.0.
    """
    
    def __init__(self, cutoff_freq: float, p: float = 1.0):
        super().__init__(p)
        self.cutoff_freq = cutoff_freq

    def _filter(self, sample: np.ndarray, sample_rate: int) -> np.ndarray:
        # Implement low-pass filtering logic here
        # This is a placeholder implementation
        return sample * (1 - self.cutoff_freq / (sample_rate / 2))  # Simple gain adjustment as an example