import numpy as np

from .base import BasePotential


class DoubleSquareWellPotential(BasePotential):
    def __init__(
        self,
        x_grid: np.array,
        well_1_center: float,
        well_1_depth: float,
        well_1_width: float,
        well_2_center: float,
        well_2_depth: float,
        well_2_width: float,
    ):
        """
        Double well potential: Two finite square wells with customizable depths, centers, and widths.

        Parameters:
        - x_grid (np.array): Spatial grid points
        - well_1_depth (float): Depth of the first well (V0 > 0, so potential is -V0 inside well)
        - well_1_center (float): Center position of the first well
        - well_1_width (float): Width of the first well
        - well_2_depth (float): Depth of the second well (V0 > 0, so potential is -V0 inside well)
        - well_2_center (float): Center position of the second well
        - well_2_width (float): Width of the second well
        """
        self.x_grid = x_grid
        self.well_1_center = well_1_center
        self.well_1_depth = well_1_depth
        self.well_1_width = well_1_width
        self.well_2_center = well_2_center
        self.well_2_depth = well_2_depth
        self.well_2_width = well_2_width

    def generate(self) -> np.array:
        """
        Generate the double well potential array.

        Returns:
            np.array: Array of potential values with two wells and a barrier.
        """
        well_1 = np.where(
            np.abs(self.x_grid - self.well_1_center) < self.well_1_width / 2,
            -self.well_1_depth,
            0,
        )
        well_2 = np.where(
            np.abs(self.x_grid - self.well_2_center) < self.well_2_width / 2,
            -self.well_2_depth,
            0,
        )

        return well_1 + well_2
