# QMSolver

**QMSolver** is a Python library for numerically solving the time-independent Schrödinger equation in one dimension. The library implements the finite difference method to compute energy eigenvalues and eigenfunctions for quantum mechanical systems with arbitrary potential energy functions.

## Installation

### PyPI Installation

```bash
pip install qmsolver
```
**Requirements:** Python >= 3.9

### Repo Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/gbatagian/qmsolver.git
   cd qmsolver
   ```

2. **Install the source code:**
   ```bash
   pip install -e .
   ```

## Usage

### Finite Differences Solver (`FDSolver`)

The `qmsolver` package provides the `tise` module, which contains the `FDSolver` class for solving the time-independent Schrödinger equation using finite differences. To use it, create an `FDSolver` instance and inject a potential class into its `potential_generator` attribute. Sample potentials are provided in the `potentials` module. For example, the finite square well solution is demonstrated below:

```python
from qmsolver.tise import FDSolver
from qmsolver.potentials import FiniteSquareWellPotential

solver = FDSolver(steps=2_000, x_min=-5, x_max=5, n_lowest=7)
potential = FiniteSquareWellPotential(
    x_grid=solver.x_grid, well_depth=25, well_width=2
)
solver.potential_generator = potential
solver.solve()
solver.output()
solver.plot()
```

```bash
****************************************

-> 7 lowest energy states:

      E(0) = -24.055438366060855
      E(1) = -21.24089736975921
      E(2) = -16.62404645487225
      E(3) = -10.37013368913339
      E(4) = -2.999982564365393
      E(5) = 0.2854054853290151
      E(6) = 0.3280462337486476

****************************************
```

> **⚠️ Attention:** The `FiniteSquareWellPotential` class requires a spatial grid as input. It is recommended to provide the `x_grid` of the solver to ensure the potential and solver use the same grid.

This will generate a plot showing the potential (black line) and the first few energy eigenstates:


![Finite Square Well Example](outputs/finite_square_well.png)

> **Note:** You can customize the physical constants by setting the `solver.h_bar` and `solver.m` attributes to your desired values before calling `solver.solve()`. By default, they are set to 1 (dimensionless units). For more information on using SI units, see the [SI Units](#si-units) section.

* After calling `solver.solve()`, the solver will have the `E_lowest` attribute containing the n-lowest eigenenergies and the `Psi_lowest` attribute containing the corresponding eigenfunctions.
    ```python
    solver.E_lowest
    ```
    ```bash
    array([-24.05543837, -21.24089737, -16.62404645, -10.37013369,
            -2.99998256,   0.28540549])
    ```

    ```python
    solver.Psi_lowest 
    ```
    ```bash
    array([[ 7.72546314e-16, -7.70210475e-15,  2.04525254e-13,
            2.68267151e-11,  7.52877452e-08,  1.30754252e-04],
        [ 1.54602276e-15, -1.54123977e-14,  4.09220681e-13,
            5.36673540e-11,  1.50586795e-07,  2.61506636e-04],
        [ 2.32136057e-15, -2.31390756e-14,  6.14256593e-13,
            8.05358477e-11,  2.25908455e-07,  3.92255285e-04],
        ...,
        [ 2.32136057e-15,  2.31390756e-14,  6.14256593e-13,
            -8.05358477e-11,  2.25908455e-07, -3.92255285e-04],
        [ 1.54602276e-15,  1.54123977e-14,  4.09220681e-13,
            -5.36673540e-11,  1.50586795e-07, -2.61506636e-04],
        [ 7.72546314e-16,  7.70210475e-15,  2.04525254e-13,
            -2.68267151e-11,  7.52877452e-08, -1.30754252e-04]],
        shape=(2000, 6))
    ```
## Method Limitations

The finite difference method is well-suited for computing **bound states** of quantum systems, but has some limitations for **unbound states** (scattering or continuum states).

The numerical implementation imposes **zero boundary conditions** at the edges of the spatial grid (**x_min** and **x_max**). This effectively encloses the system within an **infinite square well** of width (x_max - x_min), which introduces artificial quantization of the continuum energy spectrum.

For bound states, the wave functions decay exponentially to zero outside the well region. Since they naturally satisfy the zero boundary conditions at the grid edges, the computed energies and wave functions are largely unaffected by the grid size, provided the grid extends sufficiently far to capture the exponential tail.

For scattering/continuum states, the wave functions oscillate and do not decay to zero. The artificial boundary conditions at the grid edges cause **reflection** of the wave function, creating standing waves that depend on the grid length. This leads to:
  - **Quantization** of the continuum spectrum
  - **Grid-dependent** energy levels and wave functions

`FDSolver` is better-suited for bound state problems and provides reliable results within that domain - as long as the grid extends sufficiently beyond the potential region to minimize boundary effects. For scattering states, the numerical solutions behave as if the system is confined within an infinite potential well, with complete wave function reflection at the grid boundaries, leading to quantization of the continuum energy spectrum. 

## Custom Potential Implementation

While the `potentials` module provides several predefined potential classes, you can also implement custom potentials by inheriting from the `BasePotential` abstract base class. This allows you to solve the Schrödinger equation for arbitrary potential energy functions. To create a custom potential class:

1. **Inherit from `BasePotential`**: Your class must inherit from `potentials.base.BasePotential`
2. **Implement the `generate()` method**: This method should return a NumPy array containing the potential energy values evaluated on the spatial grid
3. **Accept grid as input**: The `__init__` method should accept the spatial grid (`x_grid`) as a parameter
4. **Instance attribute parameters**: Any potential parameters (depths, widths, etc.) should be stored as instance attributes

Below follows an example implementation of a sinusoidal potential well:

> **⚠️ Important:** All parameters required by the `generate()` method must be provided through the `__init__` method and stored as instance attributes (accessed through the `self` namespace). The `generate()` method should not accept additional parameters - it should only return the potential array using the stored parameters and the grid.

```python
import numpy as np

from qmsolver.potentials import BasePotential
from qmsolver.tise.finite_differences import FDSolver


class SinusoidalWellPotential(BasePotential):
    """
    A sinusoidal potential well: V(x) = -A * |sin(x)| for |x| ≤ π, 0 otherwise
    """

    def __init__(self, x_grid: np.array, amplitude: float) -> None:
        """
        Parameters:
        - x_grid: Spatial grid points
        - amplitude: Amplitude of the sinusoidal modulation (A > 0)
        """
        self.x_grid = x_grid
        self.amplitude = amplitude

    def generate(self) -> np.array:
        """
        Generate the potential energy array.

        Returns:
            np.array: Potential energy values on the grid
        """
        return np.where(
            np.abs(self.x_grid) <= np.pi,
            -self.amplitude * np.abs(np.sin(self.x_grid)),
            0.0,
        )


solver = FDSolver(steps=2000, x_min=-10, x_max=10, n_lowest=5)
potential = SinusoidalWellPotential(x_grid=solver.x_grid, amplitude=5.0)
solver.potential_generator = potential
solver.solve()
solver.output()
solver.plot()
```

```bash
****************************************

-> 5 lowest energy states:

      E(0) = -3.9325130490544944
      E(1) = -3.9007355756749442
      E(2) = -1.9743485404975893
      E(3) = -1.709360959487448
      E(4) = -0.2899193058335374

****************************************
```

![Sinusoidal Well Example](outputs/sinusoidal_well.png)

# SI Units

By default, `FDSolver` solves the Schrödinger equation in dimensionless units. However, it is also possible to perform the calculations in **SI units**. To use SI units:

1. Express the potential energy in Joules and the spatial grid in meters.
2. Set the `h_bar` and `m` attributes of the solver to their SI values (e.g. using `scipy.constants`).

Below follows an example for an electron in a finite square well:

```python
import numpy as np
from scipy import constants
from qmsolver.tise import FDSolver
from qmsolver.potentials import FiniteSquareWellPotential

well_depth_ev = 1.0     # Well depth in electron volts
well_width_nm = 1.0     # Well width in nanometers

# Convert to SI units
well_depth_joules = well_depth_ev * constants.e     # Convert eV to Joules
well_width_meters = well_width_nm * 1e-9            # Convert nm to meters

# Spatial domain in meters
x_min_m = -3e-9
x_max_m = 3e-9

solver = FDSolver(steps=2_000, x_min=x_min_m, x_max=x_max_m, n_lowest=3)

# Set physical constants in SI units
solver.h_bar = constants.hbar  # Reduced Planck's constant in J⋅s
solver.m = constants.m_e       # Electron mass in kg

potential = FiniteSquareWellPotential(
    x_grid=solver.x_grid,
    well_depth=well_depth_joules,
    well_width=well_width_meters,
)
solver.potential_generator = potential

solver.solve()
solver.output()
solver.plot(is_dimensionless=False, scale=1e19, energy_units="J")
```

```bash
****************************************

-> 3 lowest energy states:

      E(0) = -1.297613251785845e-19
      E(1) = -4.7950999500587644e-20
      E(2) = 7.54877077796044e-21

****************************************
```

![SI Units Example](outputs/finite_square_well_SI_units.png)

# Convert to eV

After solving in SI units, simply divide the eigenenergies by the electron charge to get values in eV:

```python
E_lowest_ev = np.array(solver.E_lowest) / constants.e
print("\nEnergies in electron volts:")
for i, energy in enumerate(E_lowest_ev):
    print(f"E({i}) = {energy:.8f} eV")
```
```bash
Energies in electron volts:
E(0) = -0.80990649 eV
E(1) = -0.29928660 eV
E(2) = 0.04711572 eV
```

# Development

## Build and Test

1. Build the package: `make build`
2. Install in development mode: `make install-dev`
3. Run the test suite: `make test`

## Virtual Environment Setup

1. **Python >= 3.9** should be installed
2. **Pipenv** should be installed (if not: `pip install pipenv`)
3. Create the virtual environment: `make venv`
4. Run the test suite: `make test`

> **⚠️ Important:** For development, it is recommended to build and test from within the virtual environment.

## Additional Development Commands

- **Format code**: `make reformat` (runs black and isort)
- **Run tests with coverage**: `make coverage`
- **Create the virtual environment**: `make venv`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Important Notes:**
- This is a personal project developed in my free time
- No warranty is provided
- For serious scientific work, please verify results independently and consult domain experts

## References

1. Computational Quantum Mechanics  
   Joshua Izaac, Jingbo Wang  
   Springer, Chapter 9.6: The Direct Matrix Method

2. Solving the time-dependent Schrödinger equation using finite difference methods  
   R. Becerril, F.S. Guzmán, A. Rendón-Romero, S. Valdez-Alvarado  
   *Revista Mexicana de Física E*, Vol. 54, No. 2, pp. 120-132, 2008

3. [A Python Program for Solving Schrödinger's Equation in Undergraduate Physical Chemistry](https://pubs.acs.org/doi/10.1021/acs.jchemed.7b00003)  
   Matthew N. Srnec, Shiv Upadhyay, Jeffry D. Madura  
   *Journal of Chemical Education*, Vol 94/Issue 6, 2017