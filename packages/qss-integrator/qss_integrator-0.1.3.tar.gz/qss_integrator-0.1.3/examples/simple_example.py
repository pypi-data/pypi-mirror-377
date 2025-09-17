#!/usr/bin/env python3
"""
Simple example demonstrating basic QSS integrator usage.

This example shows how to set up and use the QSS integrator for a simple
chemical kinetics problem.
"""

import numpy as np
import matplotlib.pyplot as plt
from qss_integrator import QssIntegrator, PyQssOde


class SimpleKineticsODE(PyQssOde):
    """Simple chemical kinetics ODE for demonstration."""

    def __init__(self, k1=1.0, k2=0.1):
        """Initialize with rate constants.

        Args:
            k1: Forward rate constant
            k2: Reverse rate constant
        """
        super().__init__(self._ode_function)
        self.k1 = k1
        self.k2 = k2

    def _ode_function(self, t, y, corrector=False):
        """ODE function: A <-> B with first-order kinetics.

        Args:
            t: Time
            y: State vector [A, B]
            corrector: Whether this is a corrector iteration

        Returns:
            (q, d): Production and destruction rates
        """
        A, B = y[0], y[1]

        # Production rates (q)
        q = [self.k2 * B, self.k1 * A]

        # Destruction rates (d) - proportional to species concentration
        d = [self.k1 * A, self.k2 * B]

        return q, d


def main():
    """Run the simple kinetics example."""
    print("QSS Integrator - Simple Kinetics Example")
    print("=" * 50)

    # Create ODE system
    ode = SimpleKineticsODE(k1=10.0, k2=1.0)

    # Create integrator
    integrator = QssIntegrator()
    integrator.setOde(ode)
    integrator.initialize(2)  # 2 species: A and B

    # Set integrator parameters
    integrator.epsmin = 1e-3
    integrator.epsmax = 10.0
    integrator.dtmin = 1e-12
    integrator.dtmax = 1e-3
    integrator.itermax = 2
    integrator.abstol = 1e-10
    integrator.stabilityCheck = True

    # Initial conditions: A=1.0, B=0.0
    y0 = [1.0, 0.0]
    t0 = 0.0
    tf = 2.0

    print(f"Initial conditions: A={y0[0]:.3f}, B={y0[1]:.3f}")
    print(f"Integrating from t={t0} to t={tf}")

    # Set initial state
    integrator.setState(y0, t0)

    # Integrate
    result = integrator.integrateToTime(tf)

    if result == 0:
        print(f"Integration successful!")
        print(f"Final state: A={integrator.y[0]:.6f}, B={integrator.y[1]:.6f}")
        print(f"Function evaluations: {integrator.gcount}")
        print(f"Timestep repeats: {integrator.rcount}")

        # Analytical solution for comparison
        k1, k2 = 10.0, 1.0
        k_total = k1 + k2
        A_analytical = (y0[0] * k2 + y0[1] * k1) / k_total + (
            y0[0] * k1 - y0[1] * k2
        ) / k_total * np.exp(-k_total * tf)
        B_analytical = (y0[0] + y0[1]) - A_analytical

        print(f"Analytical solution: A={A_analytical:.6f}, B={B_analytical:.6f}")
        print(
            f"Error: A={abs(integrator.y[0] - A_analytical):.2e}, B={abs(integrator.y[1] - B_analytical):.2e}"
        )

    else:
        print(f"Integration failed with error code: {result}")


if __name__ == "__main__":
    main()
