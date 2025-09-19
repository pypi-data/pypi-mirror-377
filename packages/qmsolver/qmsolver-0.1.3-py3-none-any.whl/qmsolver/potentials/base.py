from abc import ABC
from abc import abstractmethod

import numpy as np


class BasePotential(ABC):
    """
    Abstract base class for quantum mechanical potentials.

    This class defines the interface for all potential classes in the qmsolver package.
    Derived classes must implement the `generate` method which returns the potential values as a numpy array.

    Attributes:
        None

    Methods:
        generate(): Abstract method that generates the potential values as a numpy array.
    """

    @abstractmethod
    def generate(self) -> np.array:
        """
        Generate the potential values as a numpy array.

        This method must be implemented by all derived classes to compute
        the potential values for the given coordinates.

        Returns:
            np.array: Array of potential values.

        Example:
            ```
            def generate(self) -> np.array:
                # Example for a harmonic oscillator potential
                x = np.linspace(-5, 5, 100)
                k = 1.0  # spring constant
                return 0.5 * k * x**2
            ```
        """
        pass
