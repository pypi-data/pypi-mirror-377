"""
Implementation of the Yeh-Hummer finite-size correction for diffusion coefficients
from molecular dynamics simulations with periodic boundary conditions.

Based on: Yeh & Hummer, J. Phys. Chem. B 2004, 108, 15873-15879
"""

import numpy as np
import scipp as sc
from scipy.optimize import curve_fit
from scipy.linalg import pinvh
from emcee import EnsembleSampler
import matplotlib.pyplot as plt

from kinisi.samples import Samples


def yeh_hummer_linear(inv_L, D_0, slope):
    """
    Linear form of Yeh-Hummer equation for fitting.

    D_PBC = D_0 - slope * (1/L)

    where slope = (k_B * T * xi) / (6 * pi * eta)

    :param inv_L: Inverse box lengths (1/L)
    :param D_0: Infinite-system diffusion coefficient
    :param slope: Slope containing viscosity information
    :return: D_PBC values
    """
    return D_0 - slope * inv_L


class YehHummer:
    """
    Apply Yeh-Hummer finite-size corrections to diffusion coefficients from MD simulations
    with periodic boundary conditions.

    The Yeh-Hummer correction formula is:
    D_PBC = D_0 - (k_B * T * xi) / (6 * pi * eta * L)

    :param diffusion: sc.DataArray with diffusion coefficients and box_length coordinate
    :param temperature: Temperature (will be extracted from coords if not provided)
    :param bounds: Optional bounds for [D_0, viscosity] parameters
    """

    def __init__(self, diffusion, temperature=None, bounds=None):
        # Store diffusion data
        self.diffusion = diffusion

        # Extract box lengths from coordinates
        if "box_length" in diffusion.coords:
            self.box_lengths = diffusion.coords["box_length"]
        elif "L" in diffusion.coords:
            self.box_lengths = diffusion.coords["L"]
        else:
            raise ValueError("DataArray must have 'box_length' or 'L' coordinate")

        # Handle temperature
        if temperature is not None:
            self.temperature = (
                temperature
                if isinstance(temperature, sc.Variable)
                else sc.scalar(temperature, unit="K")
            )
        elif "temperature" in diffusion.coords:
            # If single temperature for all systems
            temps = diffusion.coords["temperature"]
            if temps.ndim == 0 or len(np.unique(temps.values)) == 1:
                self.temperature = sc.scalar(temps.values.flat[0], unit=temps.unit)
            else:
                raise ValueError("YehHummer requires single temperature for all systems")
        else:
            raise ValueError("Temperature must be provided or in coordinates")

        # Constants
        self.xi_cubic = 2.837297  # Ewald constant for cubic boxes
        self.k_B = sc.scalar(value=1.380649e-23, unit="J/K")

        # Initialize data group
        self.data_group = sc.DataGroup({"data": diffusion})

        # Set up parameters
        self.parameter_names = ("D_0", "viscosity")
        self.parameter_units = (diffusion.unit, sc.Unit("Pa*s"))

        # Set bounds
        self.bounds = bounds
        if self.bounds is None:
            # Auto-generate reasonable bounds
            D_max = np.max(self.diffusion.values)
            self.bounds = (
                (D_max * 0.8 * self.diffusion.unit, D_max * 2.0 * self.diffusion.unit),
                (1e-5 * sc.Unit("Pa*s"), 1e-1 * sc.Unit("Pa*s")),
            )

        # Convert bounds to values for optimization
        self.bounds_values = tuple(
            [
                (b[0].to(unit=u).value, b[1].to(unit=u).value)
                for b, u in zip(self.bounds, self.parameter_units)
            ]
        )

        # Fit the data
        self.max_likelihood()

    def _prepare_data_for_fit(self):
        """Prepare data in correct format for fitting."""
        # Convert box lengths to inverse values
        L_values = self.box_lengths.values
        inv_L = 1.0 / L_values

        # Get diffusion values and errors
        D_values = self.diffusion.values
        D_errors = np.sqrt(self.diffusion.variances)

        return inv_L, D_values, D_errors

    def _slope_to_viscosity(self, slope):
        """Convert slope to viscosity using Yeh-Hummer relation."""
        # slope = (k_B * T * xi) / (6 * pi * eta)
        # eta = (k_B * T * xi) / (6 * pi * slope)

        k_B_T = sc.to_unit(self.k_B * self.temperature, "J")

        # slope has units of [diffusion] / [1/length] = [diffusion] * [length]
        # diffusion is cm^2/s, box_lengths is Å, so slope * diffusion.unit / (1/box_lengths.unit)
        # This gives us (cm^2/s) / (1/Å) = cm^2/s * Å = cm^2 * Å / s
        slope_with_units = slope * self.diffusion.unit / (1 / self.box_lengths.unit)
        slope_SI = sc.to_unit(slope_with_units, "m^3/s")

        eta = (k_B_T * self.xi_cubic) / (6 * np.pi * slope_SI)
        return sc.to_unit(eta, "Pa*s")

    def _viscosity_to_slope(self, eta):
        """Convert viscosity to slope for fitting."""
        k_B_T = sc.to_unit(self.k_B * self.temperature, "J")
        eta_SI = sc.to_unit(eta, "Pa*s")

        slope_SI = (k_B_T * self.xi_cubic) / (6 * np.pi * eta_SI)

        # Convert back to data units
        target_unit = self.diffusion.unit * self.box_lengths.unit
        return sc.to_unit(slope_SI, target_unit).value

    def log_likelihood(self, parameters):
        """Calculate log likelihood for MCMC."""
        D_0, eta = parameters

        # Convert viscosity to slope
        eta_with_unit = eta * self.parameter_units[1]
        slope = self._viscosity_to_slope(eta_with_unit)

        # Get data
        inv_L, D_values, _ = self._prepare_data_for_fit()

        # Calculate model
        model = yeh_hummer_linear(inv_L, D_0, slope)

        # Calculate likelihood
        covariance_matrix = np.diag(self.diffusion.variances)

        if np.any(self.diffusion.variances > 0):
            _, logdet = np.linalg.slogdet(covariance_matrix)
            logdet += np.log(2 * np.pi) * D_values.size
            inv = pinvh(covariance_matrix)

            diff = model - D_values
            logl = -0.5 * (logdet + np.matmul(diff.T, np.matmul(inv, diff)))
        else:
            # No variance info, use simple chi-squared
            logl = -0.5 * np.sum((model - D_values) ** 2)

        return logl

    def nll(self, parameters):
        """Negative log likelihood for optimization."""
        return -self.log_likelihood(parameters)

    def max_likelihood(self):
        """Find maximum likelihood parameters."""
        # Initial guess
        inv_L, D_values, D_errors = self._prepare_data_for_fit()

        # Linear fit for initial parameters
        def linear_func(x, a, b):
            return a - b * x

        popt, _ = curve_fit(
            linear_func,
            inv_L,
            D_values,
            sigma=D_errors if np.any(D_errors > 0) else None,
            p0=[np.max(D_values), (D_values[0] - D_values[-1]) / (inv_L[0] - inv_L[-1])],
        )

        D_0_init = popt[0]
        slope_init = popt[1]

        # Convert slope to viscosity
        eta_init = self._slope_to_viscosity(slope_init).value

        # Optimize
        from scipy.optimize import minimize

        x0 = [D_0_init, eta_init]

        result = minimize(self.nll, x0, bounds=self.bounds_values, method="L-BFGS-B")

        # Store results
        self.data_group["D_0"] = result.x[0] * self.parameter_units[0]
        self.data_group["viscosity"] = result.x[1] * self.parameter_units[1]

    def mcmc(self, n_samples=1000, n_walkers=32, n_burn=500, n_thin=10):
        """Perform MCMC sampling."""
        # Get current estimates
        D_0_value = self.data_group["D_0"].value
        eta_value = self.data_group["viscosity"].value

        # Set up walkers
        ndim = 2
        pos = np.column_stack(
            [
                D_0_value + D_0_value * 0.01 * np.random.randn(n_walkers),
                eta_value + eta_value * 0.01 * np.random.randn(n_walkers),
            ]
        )

        # Ensure within bounds
        for i in range(n_walkers):
            for j in range(ndim):
                pos[i, j] = np.clip(
                    pos[i, j], self.bounds_values[j][0], self.bounds_values[j][1]
                )

        # Run MCMC
        sampler = EnsembleSampler(n_walkers, ndim, self.log_posterior)
        sampler.run_mcmc(
            pos,
            n_samples + n_burn,
            progress=True,
            progress_kwargs={"desc": "MCMC Sampling"},
        )

        # Extract samples
        flatchain = sampler.get_chain(discard=n_burn, thin=n_thin, flat=True)

        # Store as Samples
        self.data_group["D_0"] = Samples(flatchain[:, 0], unit=self.parameter_units[0])
        self.data_group["viscosity"] = Samples(
            flatchain[:, 1], unit=self.parameter_units[1]
        )

    def log_prior(self, parameters):
        """Uniform prior within bounds."""
        for i, (p, bounds) in enumerate(zip(parameters, self.bounds_values)):
            if not (bounds[0] <= p <= bounds[1]):
                return -np.inf
        return 0.0

    def log_posterior(self, parameters):
        """Log posterior for MCMC."""
        lp = self.log_prior(parameters)
        if not np.isfinite(lp):
            return -np.inf
        return lp + self.log_likelihood(parameters)

    @property
    def D_infinite(self):
        """Return infinite-system diffusion coefficient."""
        return self.data_group["D_0"]

    @property
    def shear_viscosity(self):
        """Return estimated shear viscosity."""
        return self.data_group["viscosity"]

    @property
    def distribution(self):
        """Generate distribution for plotting credible intervals."""
        if not isinstance(self.data_group["D_0"], Samples):
            raise ValueError("Run mcmc() first to generate distribution")

        inv_L, _, _ = self._prepare_data_for_fit()

        D_0_samples = self.data_group["D_0"].values
        eta_samples = self.data_group["viscosity"].values

        n_points = len(inv_L)
        n_samples = len(D_0_samples)
        predictions = np.zeros((n_points, n_samples))

        for i in range(n_samples):
            slope = self._viscosity_to_slope(eta_samples[i] * self.parameter_units[1])
            predictions[:, i] = yeh_hummer_linear(inv_L, D_0_samples[i], slope)

        return predictions

    def __repr__(self):
        """String representation."""
        return self.data_group.__repr__()

    def __str__(self):
        """String representation."""
        return self.data_group.__str__()

    def _repr_html_(self):
        """HTML representation."""
        return self.data_group._repr_html_()


# Example usage
def example_usage():
    """Example showing how to use YehHummer class."""

    # TIP3P water data from Yeh & Hummer paper
    box_lengths = np.array([18.58, 23.42, 29.51, 37.19, 46.86])  # Angstroms
    D_values = np.array([4.884e-5, 5.123e-5, 5.315e-5, 5.466e-5, 5.590e-5])  # cm^2/s
    D_errors = np.array([0.032e-5, 0.027e-5, 0.014e-5, 0.011e-5, 0.013e-5])  # cm^2/s

    # Create DataArray in kinisi style
    td = sc.DataArray(
        data=sc.array(
            dims=["system"], values=D_values, variances=D_errors**2, unit="cm^2/s"
        ),
        coords={
            "box_length": sc.Variable(
                dims=["system"], values=box_lengths, unit="angstrom"
            )
        },
    )

    # Create YehHummer object
    yh = YehHummer(td, temperature=298.0)  # K

    # Run MCMC
    yh.mcmc(n_samples=500, n_walkers=16)

    print(
        f"D_infinite: {sc.mean(yh.D_infinite).value} ± {sc.std(yh.D_infinite, ddof=1).value} {yh.D_infinite.unit}"
    )
    print(
        f"Shear viscosity: {sc.mean(yh.shear_viscosity).value} ± {sc.std(yh.shear_viscosity, ddof=1).value} {yh.shear_viscosity.unit}"
    )

    credible_intervals = [[16, 84], [2.5, 97.5], [0.15, 99.85]]
    alpha = [0.6, 0.4, 0.2]

    plt.errorbar(
        1 / td.coords["box_length"].values,
        td.data.values,
        np.sqrt(td.data.variances),
        marker="o",
        ls="",
        color="k",
        zorder=10,
    )

    for i, ci in enumerate(credible_intervals):
        plt.fill_between(
            1 / td.coords["box_length"].values,
            *np.percentile(yh.distribution, ci, axis=1),
            alpha=alpha[i],
            color="#0173B2",
            lw=0,
        )
    plt.xlabel("L/Å")
    plt.ylabel("$D$/cm$^2$s$^{-1}$")
    plt.savefig("yeh_hummer_example.png", dpi=300)

    return yh

def bmim_usage():
    td = sc.DataArray(
        data=sc.array(
            dims=["system"], values=[2.06e-8, 4.09e-9], variances=[5.933668420749834e-18, 1.2697992985043594e-18], unit="cm^2/s"
        ),
        coords={
            "box_length": sc.Variable(
                dims=["system"], values=[31.73513838071529, 17.22848373713802], unit="angstrom"
            )
        },
    )

    # Create YehHummer object
    yh = YehHummer(td, temperature=298.0)  # K

    # Run MCMC
    yh.mcmc(n_samples=500, n_walkers=16)

    print(
        f"D_infinite: {sc.mean(yh.D_infinite).value} ± {sc.std(yh.D_infinite, ddof=1).value} {yh.D_infinite.unit}"
    )
    print(
        f"Shear viscosity: {sc.mean(yh.shear_viscosity).value} ± {sc.std(yh.shear_viscosity, ddof=1).value} {yh.shear_viscosity.unit}"
    )

    credible_intervals = [[16, 84], [2.5, 97.5], [0.15, 99.85]]
    alpha = [0.6, 0.4, 0.2]

    plt.errorbar(
        1 / td.coords["box_length"].values,
        td.data.values,
        np.sqrt(td.data.variances),
        marker="o",
        ls="",
        color="k",
        zorder=10,
    )

    for i, ci in enumerate(credible_intervals):
        plt.fill_between(
            1 / td.coords["box_length"].values,
            *np.percentile(yh.distribution, ci, axis=1),
            alpha=alpha[i],
            color="#0173B2",
            lw=0,
        )
    plt.xlabel("L/Å")
    plt.ylabel("$D$/cm$^2$s$^{-1}$")
    plt.savefig("yeh_hummer_example.png", dpi=300)



if __name__ == "__main__":
    bmim_usage()
