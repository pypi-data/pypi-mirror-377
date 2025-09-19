from functools import cached_property
from functools import lru_cache

import numpy as np
import scipy as sp
from matplotlib import pyplot as plt

from ..potentials import BasePotential


class FDSolver:
    def __init__(
        self, steps: int, x_min: float, x_max: float, n_lowest: int
    ) -> None:
        """
        Solves the time-independent Schrödinger equation using finite differences.

        Parameters:
        - steps (int): Number of grid points
        - x_min, x_max (float): Spatial domain
        - n_lowest (int): Number of lowest energy states to compute
        """
        if x_min >= x_max:
            raise ValueError("x_min must be less than x_max.")

        self.steps = steps
        self.x_min = x_min
        self.x_max = x_max
        self.x_grid = np.linspace(x_min, x_max, steps)
        self.dx = abs(self.x_grid[1] - self.x_grid[0])
        self.n_lowest = n_lowest
        self._potential_generator: BasePotential | None = None
        self._potential: np.array | None = None

        # Set default values for dimensionless units
        self._h_bar = 1
        self._m = 1

        # Initialize attributes to store eigenvalues and eigenvectors of the lowest energy states
        self.E_lowest: list[float] | None = None
        self.Psi_lowest: np.array[np.array] | None = None

    @property
    def potential_generator(self) -> BasePotential:
        """
        Returns the potential energy generator class.
        """
        if self._potential_generator is None:
            raise ValueError("Potential energy function is not set.")

        return self._potential_generator

    @potential_generator.setter
    def potential_generator(self, value: BasePotential) -> None:
        """
        Sets the potential energy generator class.
        """
        self._potential_generator = value

    @property
    def potential(self) -> np.array:
        """
        Returns the potential energy array.
        """
        if self._potential is None:
            self._potential = self.potential_generator.generate()

        return self._potential

    @property
    def h_bar(self) -> float:
        """
        Returns the value of the reduced Planck constant (ℏ).
        """
        return self._h_bar

    @property
    def m(self) -> float:
        """
        Returns the value of the particle mass (m).
        """
        return self._m

    @h_bar.setter
    def h_bar(self, value: float) -> None:
        """
        Sets the value of the reduced Planck constant (ℏ).
        """
        self._h_bar = value

    @m.setter
    def m(self, value: float) -> None:
        """
        Sets the value of the particle mass (m).
        """
        self._m = value

    @property
    def k(self) -> float:
        """
        Returns the kinetic energy coefficient used in the Hamiltonian matrix.
        """
        return self.h_bar**2 / (2 * self.m * self.dx**2)

    @lru_cache
    def get_kinetic_energy_matrix_form(self) -> np.ndarray:
        """
        Returns the Hamiltonian matrix for a free particle using the finite difference method.
        The matrix form is derived based on the equation:

            - (ħ^2 / 2m) * (ψ_{j+1} - 2ψ_j + ψ_{j-1}) / Δx^2 = E * ψ_j + O(Δx^2) =

            = k * (-ψ_{j+1} + 2ψ_j - ψ_{j-1}) = E * ψ_j + O(Δx^2)

            where,
                k = ħ^2 / 2mΔx^2
                j = 1, 2, ..., N-1

        This formula is derived from the Schrödinger equation with the finite difference approximation
        used for the second derivative. This results in a tridiagonal matrix with 2*k on the diagonal
        and -k on the off-diagonals.
        """
        return (
            2 * self.k * np.diag(np.ones(self.steps))
            - self.k * np.diag(np.ones(self.steps - 1), 1)
            - self.k * np.diag(np.ones(self.steps - 1), -1)
        )

    @lru_cache
    def get_potential_energy_matrix_form(self) -> np.ndarray:
        """
        Returns the potential energy matrix for the given potential energy function.
        """
        return np.diag(self.potential)

    @cached_property
    def H_matrix(self) -> np.ndarray:
        """
        Returns the full Hamiltonian matrix, which is the sum of the kinetic and potential energy matrices.
        The form of the matrix is derived based on the equation:

            - (ħ^2 / 2m) * (ψ_{j+1} - 2ψ_j + ψ_{j-1}) / Δx^2 + V_j * ψ_j = E * ψ_j + O(Δx^2) =

            =  - k * ψ_{j+1} + (2k + V_j) ψ_j - k * ψ_{j-1} = E * ψ_j + O(Δx^2)

            where,
                k = ħ^2 / 2mΔx^2
                j = 1, 2, ..., N-1
        """
        return (
            self.get_kinetic_energy_matrix_form()
            + self.get_potential_energy_matrix_form()
        )

    @lru_cache
    def solve(self) -> None:
        """
        Solves the time-independent Schrödinger equation by computing the eigenvalues and eigenvectors
        of the Hamiltonian matrix.

        This method populates the `E_lowest` and `Psi_lowest` attributes with the `n_lowest` lowest
        energy eigenvalues and corresponding eigenvectors, sorted in ascending order.
        """
        e_all, psi_all = sp.linalg.eigh(self.H_matrix)

        # Sort eigenvalues and corresponding eigenvectors
        sort_idx = np.argsort(e_all)
        e_all = e_all[sort_idx]
        psi_all = psi_all[:, sort_idx]

        self.E_lowest = e_all[: self.n_lowest]
        self.Psi_lowest = psi_all[:, : self.n_lowest]

    def output(self):
        """
        Prints the computed lowest energy eigenvalues to the console.
        """
        if self.E_lowest is None:
            print("Run the solve method to get a valid output.")
            return

        print("*" * 40 + "\n")
        print(f"-> {self.n_lowest} lowest energy states:\n")
        for i in range(self.n_lowest):
            print(f"      E({i}) = {self.E_lowest[i]}")
        print("\n" + "*" * 40)

    def plot(
        self,
        save_path=None,
        is_dimensionless: bool = True,
        scale: float = 1.0,
        energy_units: str = "dimensionless",
    ):
        """
        Plots the eigenstates spectrum including potential energy, wavefunctions and energy levels.

        Parameters:
        - save_path (str, optional): Path to save the plot image. If None, displays the plot.
        - is_dimensionless (bool): Whether the units are dimensionless. Default is True.
        - scale (float): Scaling factor for potential and energies when not dimensionless. Default is 1.0.
        - energy_units (str): Units for energy labels. Default is "dimensionless".
        """
        if self.E_lowest is None:
            print("Run the solve method to get a valid output.")
            return

        plt.figure(figsize=(10, 6))

        potential = self.potential
        E_lowest = self.E_lowest
        if is_dimensionless is False:
            potential = self.potential * scale
            E_lowest = self.E_lowest * scale
            energy_units = f"{energy_units}$\\cdot${scale**(-1)}"

        plt.plot(self.x_grid, potential, color="black", linewidth=5)

        for i in range(self.n_lowest):
            renormalized_psi_values = (
                self.Psi_lowest[:, i] / np.max(np.abs(self.Psi_lowest[:, i]))
                + E_lowest[i]
            )
            plt.plot(self.x_grid, renormalized_psi_values)
            plt.axhline(
                y=E_lowest[i],
                color=plt.gca().lines[-1].get_color(),
                linestyle="--",
                linewidth=1,
                alpha=0.7,
            )

            x_text = (
                self.x_max - 0.05 * (self.x_max - self.x_min)
                if i % 2 == 0
                else self.x_min + 0.05 * (self.x_max - self.x_min)
            )
            y_text = E_lowest[i] + 0.02 * (plt.ylim()[1] - plt.ylim()[0])
            line_color = plt.gca().lines[-1].get_color()
            plt.text(
                x_text,
                y_text,
                f"$E_{{{i}}}$ = {round(E_lowest[i], 5)}{'' if is_dimensionless else f' {energy_units}'}",
                color=line_color,
                fontsize=8,
                ha="center",
                bbox=dict(
                    facecolor="white",
                    edgecolor="none",
                    boxstyle="round,pad=0.3",
                ),
            )

        plt.title("Eigenstates Spectrum")
        plt.xlabel(
            "Position (l.u.)" if is_dimensionless else "Position (m)",
            fontsize=14,
        )
        plt.ylabel(
            (
                r"Renormalized Wavefunction ($l.u.^{-1/2}$)"
                if is_dimensionless
                else r"Renormalized Wavefunction ($m^{-1/2}$)"
            ),
            fontsize=14,
        )
        ax = plt.gca()
        ax2 = ax.twinx()
        ax2.set_ylabel(f"Potential Energy ({energy_units})", fontsize=14)
        ax2.set_ylim(ax.get_ylim())
        ax2.get_yaxis().set_visible(True)
        ax.xaxis.set_minor_locator(plt.MultipleLocator(1))
        plt.grid(True, which="major", linestyle="--", linewidth=0.5)
        plt.tight_layout()

        if is_dimensionless:
            plt.figtext(
                0.01, 0.01, "* l.u. - length units", ha="left", fontsize=10
            )

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches="tight")
            print(f"Plot saved to {save_path}")
        else:
            plt.show()
