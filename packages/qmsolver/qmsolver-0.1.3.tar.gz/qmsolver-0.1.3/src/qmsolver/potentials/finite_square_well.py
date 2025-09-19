import numpy as np

from .base import BasePotential


class FiniteSquareWellPotential(BasePotential):
    def __init__(self, x_grid: np.array, well_depth: float, well_width: float):
        """
        Finite square well potential: V(x) = -V0 for |x| < a/2, 0 otherwise

        Parameters:
        - x_grid (np.array): Spatial grid points
        - well_depth (float): Depth of the well (V0 > 0)
        - well_width (float): Width of the well (a)
        """
        self.x_grid = x_grid
        self.well_depth = well_depth
        self.well_width = well_width

    def generate(self) -> np.array:
        """
        Generate the finite square well potential array.

        Returns:
            np.array: Array of potential values, -well_depth inside the well and 0 outside.
        """
        return np.where(
            np.abs(self.x_grid) < self.well_width / 2, -self.well_depth, 0
        )
