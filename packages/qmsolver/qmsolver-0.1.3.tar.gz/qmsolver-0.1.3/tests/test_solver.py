import unittest

import numpy as np

from qmsolver.potentials.finite_square_well import FiniteSquareWellPotential
from qmsolver.tise.finite_differences import FDSolver


class TestSolver(unittest.TestCase):

    def test_finite_square_well_solver(self):
        """Test FDSolver with finite square well potential (based on finite_square_well.ipynb example)."""
        steps = 1000  # Smaller for faster testing
        x_min, x_max = -5, 5
        n_lowest = 3

        solver = FDSolver(steps, x_min, x_max, n_lowest)
        potential = FiniteSquareWellPotential(
            solver.x_grid, well_depth=25, well_width=2
        )
        solver.potential_generator = potential

        solver.solve()

        # Check that eigenvalues are computed
        self.assertIsNotNone(solver.E_lowest)
        self.assertEqual(len(solver.E_lowest), n_lowest)

        # Check wavefunctions shape
        self.assertIsNotNone(solver.Psi_lowest)
        self.assertEqual(solver.Psi_lowest.shape, (steps, n_lowest))
