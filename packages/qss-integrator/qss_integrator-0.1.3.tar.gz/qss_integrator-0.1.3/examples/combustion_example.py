#!/usr/bin/env python3
"""
Combustion example using QSS integrator with Cantera.

This example demonstrates how to use the QSS integrator for combustion
chemistry problems using Cantera mechanisms.
"""

import numpy as np
import matplotlib.pyplot as plt
import cantera as ct
from qss_integrator.utils import create_qss_solver


def setup_methane_combustion():
    """Setup methane-air combustion problem."""
    # Create gas object with GRI-Mech 3.0
    gas = ct.Solution("gri30.yaml")

    # Set equivalence ratio and initial conditions
    phi = 1.0  # Stoichiometric
    fuel = "CH4:1"
    oxidizer = "O2:1, N2:3.76"

    gas.set_equivalence_ratio(phi, fuel, oxidizer)
    gas.TP = 1000.0, ct.one_atm  # 1000 K, 1 atm

    return gas


def main():
    """Run the combustion example."""
    print("QSS Integrator - Combustion Example")
    print("=" * 50)

    # Setup combustion problem
    gas = setup_methane_combustion()
    pressure = ct.one_atm

    print(f"Mechanism: {gas.name}")
    print(f"Species: {gas.n_species}")
    print(f"Reactions: {gas.n_reactions}")
    print(f"Initial T: {gas.T:.1f} K")
    print(f"Pressure: {pressure/ct.one_atm:.1f} atm")
    print(f"Equivalence ratio: 1.0 (stoichiometric)")

    # QSS solver configuration
    config = {
        "epsmin": 1e-2,
        "epsmax": 10.0,
        "dtmin": 1e-15,
        "dtmax": 1e-6,
        "itermax": 2,
        "abstol": 1e-8,
        "stabilityCheck": True,
    }

    # Create QSS solver
    solver = create_qss_solver(gas, pressure, config)

    # Initial state: [T, Y1, Y2, ...]
    y0 = [gas.T] + list(gas.Y)
    t0 = 0.0
    tf = 1e-3  # 1 ms

    print(f"\nIntegrating from t={t0} to t={tf*1000:.1f} ms")

    # Set initial state
    solver.setState(y0, t0)

    # Integrate
    result = solver.integrateToTime(tf)

    if result == 0:
        print(f"Integration successful!")
        print(f"Final temperature: {solver.y[0]:.1f} K")
        print(f"Temperature rise: {solver.y[0] - y0[0]:.1f} K")
        print(f"Function evaluations: {solver.gcount}")
        print(f"Timestep repeats: {solver.rcount}")

        # Show major species changes
        print(f"\nMajor species changes:")
        major_species = ["CH4", "O2", "CO2", "H2O", "CO", "H2"]
        for species in major_species:
            if species in gas.species_names:
                idx = gas.species_names.index(species) + 1  # +1 for temperature
                initial = y0[idx]
                final = solver.y[idx]
                change = final - initial
                print(f"  {species:4s}: {initial:.4f} -> {final:.4f} (Δ={change:+.4f})")

    else:
        print(f"Integration failed with error code: {result}")


if __name__ == "__main__":
    main()
