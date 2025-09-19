import numpy as np

from .base import BasePotential


class MultipleSquareWellPotential(BasePotential):
    def __init__(
        self,
        x_grid: np.array,
        well_depth: float,
        well_width: float,
        separation: float,
        num_wells: int,
    ):
        """
        Multiple square well potential (superlattice): Periodic array of finite square wells.

        Parameters:
        - x_grid (np.array): Spatial grid points
        - well_depth (float): Depth of each well (V0 > 0, so potential is -V0 inside wells)
        - well_width (float): Width of each well
        - separation (float): Distance between centers of adjacent wells
        - num_wells (int): Number of wells to create
        """
        self.x_grid = x_grid
        self.well_depth = well_depth
        self.well_width = well_width
        self.separation = separation
        self.num_wells = num_wells

    def generate(self) -> np.array:
        """
        Generate the multiple well potential array.

        Returns:
            np.array: Array of potential values with periodic wells.
        """
        potential = np.zeros_like(self.x_grid)

        # Calculate the starting position to center the potential
        total_width = self.num_wells * self.well_width + (
            self.num_wells - 1
        ) * (self.separation - 2 * self.well_width / 2)

        center = -total_width / 2

        for _ in range(self.num_wells):
            well_mask = np.abs(self.x_grid - center) < self.well_width / 2
            potential[well_mask] = -self.well_depth
            center += self.separation

        return potential
