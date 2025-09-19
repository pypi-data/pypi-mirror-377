import numpy as np

from .base import BasePotential


class PoschlTellerPotential(BasePotential):
    def __init__(self, x_grid: np.array, lambda_: float):
        """
        Pöschl-Teller potential hole:

            V(x) = -λ(λ + 1)/2 * sech²(x) = -λ(λ + 1)/(2 * cosh²(x))

        Parameters:
        - x_grid (np.array): Spatial grid points
        - lambda_ (float): Dimensionless parameter controlling the well depth and number of bound states
        """
        self.x_grid = x_grid
        self.lambda_ = lambda_

    def generate(self) -> np.array:
        """
        Generate the symmetric Pöschl-Teller potential array.
        Returns:
            np.array: Array of potential values, -λ(λ + 1)/(2 * cosh²(x))
        """
        return -(self.lambda_ * (self.lambda_ + 1)) / (
            2 * np.cosh(self.x_grid) ** 2
        )
