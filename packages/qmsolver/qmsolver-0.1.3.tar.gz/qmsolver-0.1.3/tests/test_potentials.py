import unittest

import numpy as np

from qmsolver.potentials.double_square_well import DoubleSquareWellPotential
from qmsolver.potentials.finite_square_well import FiniteSquareWellPotential
from qmsolver.potentials.harmonic_oscillator import HarmonicOscillatorPotential
from qmsolver.potentials.multiple_square_well import MultipleSquareWellPotential
from qmsolver.potentials.poschl_teller import PoschlTellerPotential


class TestPotentials(unittest.TestCase):

    def test_finite_square_well_potential(self):
        """Test generation of finite square well potential."""

        # Arrange
        x_grid = np.linspace(-5, 5, 100)
        well_depth = 10.0
        well_width = 2.0
        potential = FiniteSquareWellPotential(x_grid, well_depth, well_width)

        # Act
        V = potential.generate()

        # Assert
        # -> Check shape
        self.assertEqual(V.shape, x_grid.shape)

        # -> Check values inside well
        inside_well = np.abs(x_grid) < well_width / 2
        self.assertTrue(np.all(V[inside_well] == -well_depth))

        # -> Check values outside well
        outside_well = np.abs(x_grid) >= well_width / 2
        self.assertTrue(np.all(V[outside_well] == 0))

    def test_harmonic_oscillator_potential(self):
        """Test generation of harmonic oscillator potential."""

        # Arrange
        x_grid = np.linspace(-5, 5, 100)
        spring_constant = 1.0
        mass = 1.0
        potential = HarmonicOscillatorPotential(x_grid, spring_constant, mass)

        # Act
        V = potential.generate()

        # Assert
        # -> Check shape
        self.assertEqual(V.shape, x_grid.shape)

        # -> Check minimum at x=0
        min_idx = np.argmin(V)
        self.assertAlmostEqual(x_grid[min_idx], 0, delta=0.1)

        # -> Check symmetry
        self.assertTrue(np.allclose(V, V[::-1]))

        # -> Check expected form: 0.5 * k * x^2
        expected_V = 0.5 * spring_constant * x_grid**2
        self.assertTrue(np.allclose(V, expected_V))

    def test_double_square_well_potential(self):
        """Test generation of double square well potential."""

        # Arrange
        x_grid = np.linspace(-5, 5, 100)
        well_1_center = -2.0
        well_1_depth = 10.0
        well_1_width = 1.0
        well_2_center = 2.0
        well_2_depth = 15.0
        well_2_width = 1.5
        potential = DoubleSquareWellPotential(
            x_grid,
            well_1_center,
            well_1_depth,
            well_1_width,
            well_2_center,
            well_2_depth,
            well_2_width,
        )

        # Act
        V = potential.generate()

        # Assert
        # -> Check shape
        self.assertEqual(V.shape, x_grid.shape)

        # -> Check values in first well
        in_well_1 = np.abs(x_grid - well_1_center) < well_1_width / 2
        self.assertTrue(np.all(V[in_well_1] == -well_1_depth))

        # -> Check values in second well
        in_well_2 = np.abs(x_grid - well_2_center) < well_2_width / 2
        self.assertTrue(np.all(V[in_well_2] == -well_2_depth))

        # -> Check values outside wells
        outside = ~in_well_1 & ~in_well_2
        self.assertTrue(np.all(V[outside] == 0))

    def test_multiple_square_well_potential(self):
        """Test generation of multiple square well potential."""

        # Arrange
        x_grid = np.linspace(-10, 10, 200)
        well_depth = 20.0
        well_width = 1.0
        separation = 3.0
        num_wells = 3
        potential = MultipleSquareWellPotential(
            x_grid, well_depth, well_width, separation, num_wells
        )

        # Act
        V = potential.generate()

        # Assert
        # -> Check shape
        self.assertEqual(V.shape, x_grid.shape)

        # -> Check that there are num_wells wells
        well_count = 0
        in_well = False
        for v in V:
            if v == -well_depth and not in_well:
                well_count += 1
                in_well = True
            elif v != -well_depth:
                in_well = False

        self.assertEqual(well_count, num_wells)

        # -> Check values outside wells are 0
        outside = V != -well_depth
        self.assertTrue(np.all(V[outside] == 0))

    def test_poschl_teller_potential(self):
        """Test generation of Pöschl-Teller potential."""

        # Arrange
        x_grid = np.linspace(-5, 5, 100)
        lambda_ = 2.0
        potential = PoschlTellerPotential(x_grid, lambda_)

        # Act
        V = potential.generate()

        # Assert
        # -> Check shape
        self.assertEqual(V.shape, x_grid.shape)

        # -> Check minimum at x=0
        min_idx = np.argmin(V)
        self.assertAlmostEqual(x_grid[min_idx], 0, delta=0.1)

        # -> Check symmetry
        self.assertTrue(np.allclose(V, V[::-1]))

        # -> Check that potential is negative (well)
        self.assertTrue(np.all(V <= 0))
