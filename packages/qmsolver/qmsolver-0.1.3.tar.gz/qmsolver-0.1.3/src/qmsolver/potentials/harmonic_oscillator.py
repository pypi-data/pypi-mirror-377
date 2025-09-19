import numpy as np

from .base import BasePotential


class HarmonicOscillatorPotential(BasePotential):
    def __init__(
        self, x_grid: np.array, spring_constant: float, mass: float = 1.0
    ):
        """
        Harmonic oscillator potential: V(x) = 0.5 * k * x^2

        Parameters:
        - x_grid (np.array): Spatial grid points
        - spring_constant (float): Spring constant k (or can use frequency via k = m*ω^2)
        - mass (float): Particle mass (default 1.0 for dimensionless units)
        """
        self.x_grid = x_grid
        self.spring_constant = spring_constant
        self.mass = mass

    def generate(self) -> np.array:
        """
        Generate the harmonic oscillator potential array.

        Returns:
            np.array: Array of potential values, 0.5 * k * x^2.
        """
        return 0.5 * self.spring_constant * self.x_grid**2

    @classmethod
    def from_frequency(
        cls, x_grid: np.array, frequency: float, mass: float = 1.0
    ):
        """
        Create harmonic oscillator potential from frequency ω.
        V(x) = 0.5 * m * ω^2 * x^2

        Parameters:
        - x_grid (np.array): Spatial grid points
        - frequency (float): Angular frequency ω
        - mass (float): Particle mass (default 1.0 for dimensionless units)

        Returns:
            HarmonicOscillatorPotential: Instance with appropriate spring constant
        """
        spring_constant = mass * frequency**2
        return cls(x_grid, spring_constant, mass)
