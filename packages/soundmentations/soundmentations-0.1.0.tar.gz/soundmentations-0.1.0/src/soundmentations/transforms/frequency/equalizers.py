import numpy as np
from soundmentations.core.transforms_interface import BaseTransform

class BaseEqualizer(BaseTransform):
    """
    Base class for equalizer transforms.

    This class provides a template for equalizer transforms that modify
    the frequency response of the input audio sample according to specified parameters.
    Subclasses must implement the _equalize method.
    """
    
    def __call__(self, sample: np.ndarray, sample_rate: int = 44100) -> np.ndarray:
        self.validate_audio(sample, sample_rate)

        if not self.should_apply():
            return sample

        return self._equalize(sample, sample_rate)
    
    def _equalize(self, sample: np.ndarray, sample_rate: int) -> np.ndarray:
        raise NotImplementedError("Subclasses must implement _equalize method")
    
class LowShelfEQ(BaseEqualizer):
    """
    Apply a low-shelf equalization to the audio sample.

    Parameters
    ----------
    gain : float
        Gain in dB for the low frequencies.
    cutoff_freq : float
        Cutoff frequency for the low-shelf filter in Hz.
    p : float, optional
        Probability of applying the transform, by default 1.0.
    """
    
    def __init__(self, gain: float, cutoff_freq: float, p: float = 1.0):
        super().__init__(p)
        self.gain = gain
        self.cutoff_freq = cutoff_freq

    def _equalize(self, sample: np.ndarray, sample_rate: int) -> np.ndarray:
        # Implement low-shelf equalization logic here
        # This is a placeholder implementation
        return sample * (1 + self.gain / 20)  # Simple gain adjustment as an example