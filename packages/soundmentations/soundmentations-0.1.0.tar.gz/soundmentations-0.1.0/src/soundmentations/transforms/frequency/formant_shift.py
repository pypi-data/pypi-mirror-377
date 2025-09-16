import numpy as np
from soundmentations.core.transforms_interface import BaseTransform

class BaseFormantShift(BaseTransform):
    """
    Base class for formant shifting audio data.

    This class provides a template for formant shifting transforms that modify
    the formants of the input audio sample according to a specified ratio.
    Subclasses must implement the `_shift` method.

    Parameters
    ----------
    shift_ratio : float, optional
        The ratio of formant shift (0.0 to 1.0, inclusive), by default 0.2.
    p : float, optional
        Probability of applying the transform, by default 1.0.
    """
    def __init__(self, shift_ratio: float = 0.2, p: float = 1.0):
        if not 0.0 <= shift_ratio <= 1.0:
            raise ValueError("shift_ratio must be between 0.0 and 1.0 (inclusive).")
        super().__init__(p)
        self.shift_ratio = shift_ratio

    def __call__(self, sample: np.ndarray, sample_rate: int = 44100) -> np.ndarray:
        self.validate_audio(sample, sample_rate)

        if not self.should_apply():
            return sample

        return self._shift(sample, sample_rate)
    
    def _shift(self, sample: np.ndarray, sample_rate: int) -> np.ndarray:
        """
        Shift the formants of the audio sample.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method.")
    
class FormantShift(BaseFormantShift):
    """
    Shift the formants of the audio sample by a fixed ratio.

    Parameters
    ----------
    shift_ratio : float, optional
        The ratio of formant shift (0.0 to 1.0, inclusive), by default 0.2.
    p : float, optional
        Probability of applying the transform, by default 1.0.
    """
    
    def _shift(self, sample: np.ndarray, sample_rate: int) -> np.ndarray:
        # Implement the formant shifting logic here
        # This is a placeholder implementation
        return sample * (1 + self.shift_ratio)