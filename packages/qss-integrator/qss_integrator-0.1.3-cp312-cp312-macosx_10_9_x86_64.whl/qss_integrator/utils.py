"""
Utility functions for QSS integrator.

This module provides helper functions for setting up and using the QSS integrator
with common combustion chemistry applications.
"""

import numpy as np
import cantera as ct
from typing import Optional, Any, Dict, Tuple
import time

# Try to import the compiled extension
try:
    from qss_integrator import QssIntegrator, PyQssOde
except ImportError:
    QssIntegrator = None
    PyQssOde = None


def combustion_rhs(
    t: float, y: np.ndarray, gas: ct.Solution, pressure: float
) -> np.ndarray:
    """Right-hand side of the combustion ODE system.

    Args:
        t: Current time
        y: Current state vector [T, Y1, Y2, ...]
        gas: Cantera gas object
        pressure: Constant pressure

    Returns:
        dydt: Time derivatives [dT/dt, dY1/dt, dY2/dt, ...]
    """
    # Extract temperature and mass fractions
    T = y[0]
    Y = y[1:]

    # Update the gas state
    gas.TPY = T, pressure, Y

    # Get thermodynamic properties
    rho = gas.density_mass
    wdot = gas.net_production_rates
    cp = gas.cp_mass
    h = gas.partial_molar_enthalpies

    # Calculate temperature derivative (energy equation)
    dTdt = -(np.dot(h, wdot) / (rho * cp))

    # Calculate species derivatives (mass conservation)
    dYdt = wdot * gas.molecular_weights / rho

    # Combine into full derivative vector
    return np.hstack([dTdt, dYdt])


class CanteraQSSODE:
    """QSS ODE implementation for Cantera combustion systems."""

    def __init__(self, gas: ct.Solution, pressure: float):
        """Initialize the QSS ODE for a Cantera gas object.

        Args:
            gas: Cantera Solution object
            pressure: Constant pressure [Pa]
        """
        self.gas = gas
        self.pressure = pressure
        self.n_species = self.gas.n_species
        # caches for corrector
        self._T_cache = None
        self._rho_cache = None
        self._cp_cache = None
        self._hform_cache = None

    def __call__(self, t: float, y: list, corrector: bool = False) -> Tuple[list, list]:
        """Evaluate the ODE splitting for QSS method.

        Args:
            t: Current time
            y: Current state vector [T, Y1, Y2, ...]
            corrector: Whether this is a corrector iteration

        Returns:
            (q, d): Production and destruction rate vectors
        """
        # unpack state
        T_in = max(y[0], 300.0)
        Y = np.maximum(np.array(y[1:], dtype=float), 0.0)
        s = Y.sum()
        if s > 1e-12:
            Y /= s

        if not corrector:
            # predictor: set state and compute thermo
            self.gas.TPY = T_in, self.pressure, Y
            rho = self.gas.density
            cp = self.gas.cp_mass
            h_form = self.gas.standard_enthalpies_RT * ct.gas_constant * self.gas.T
            # cache for the corrector
            self._T_cache = self.gas.T
            self._rho_cache = rho
            self._cp_cache = cp
            self._hform_cache = h_form
        else:
            # corrector: freeze T/thermo like C++
            # (still update composition to get updated rates with the new Y)
            T_frozen = self._T_cache if self._T_cache is not None else T_in
            self.gas.TPY = T_frozen, self.pressure, Y
            rho = self._rho_cache if self._rho_cache is not None else self.gas.density
            cp = self._cp_cache if self._cp_cache is not None else self.gas.cp_mass
            h_form = (
                self._hform_cache
                if self._hform_cache is not None
                else self.gas.standard_enthalpies_RT * ct.gas_constant * T_frozen
            )

        # rates (ensure nonnegative split)
        wQ = np.maximum(self.gas.creation_rates, 0.0)  # kmol/m^3/s
        wD = np.maximum(self.gas.destruction_rates, 0.0)  # kmol/m^3/s
        net = wQ - wD
        qdot = -np.dot(
            net, h_form
        )  # J/m^3/s  (exothermic release is negative enthalpy change)

        # temperature parts: chemistry heat into q-part; put losses (if any) into d-part
        dTdt_q = qdot / (rho * cp)  # + split energy if you have it
        dTdt_d = 0.0  # add heat-loss/(rho*cp) here if modeling losses

        # species parts (mass-fraction rates)
        W = self.gas.molecular_weights  # kg/kmol
        dYdt_q = wQ * W / rho  # + split species if you have them
        dYdt_d = wD * W / rho

        q = np.concatenate(([dTdt_q], dYdt_q))
        d = np.concatenate(([dTdt_d], dYdt_d))
        return q.tolist(), d.tolist()


# Global dictionary to store references and prevent garbage collection
_qss_refs = {}


def create_qss_solver(
    gas: ct.Solution, pressure: float, config: Dict[str, Any]
) -> QssIntegrator:
    """Create a QSS solver for a Cantera combustion system.

    Args:
        gas: Cantera Solution object
        pressure: Constant pressure [Pa]
        config: Solver configuration dictionary

    Returns:
        Initialized QSS integrator
    """
    if QssIntegrator is None or PyQssOde is None:
        raise ImportError(
            "QSS C++ extension not available. Please build the package first."
        )

    chem = CanteraQSSODE(gas, pressure)
    integrator = QssIntegrator()
    ode_qss = PyQssOde(chem)

    integrator.setOde(ode_qss)
    integrator.initialize(chem.n_species + 1)

    # Set configuration parameters
    integrator.epsmin = config.get("epsmin", 1e-2)
    integrator.epsmax = config.get("epsmax", 20.0)
    integrator.dtmin = config.get("dtmin", 1e-15)
    integrator.dtmax = config.get("dtmax", 1e-6)
    integrator.itermax = config.get("itermax", 2)
    integrator.abstol = config.get("abstol", 1e-8)
    integrator.stabilityCheck = config.get("stabilityCheck", True)

    # Store references in global dictionary to prevent garbage collection
    integrator_id = id(integrator)
    _qss_refs[integrator_id] = (chem, ode_qss)

    return integrator


def integrate_single_step(
    solver_type: str,
    config: Dict[str, Any],
    gas: ct.Solution,
    state: np.ndarray,
    t0: float,
    t_end: float,
    pressure: float,
    dt: float = None,
    mxsteps: int = 1000,
) -> Tuple[np.ndarray, float, float, bool]:
    """
    Perform single-step integration with specified solver.

    Args:
        solver_type: 'qss' (only QSS supported in this module)
        config: solver configuration dict
        gas: Cantera gas object
        state: [T, Y1, Y2, ...] current state
        t0: initial time
        t_end: final time
        pressure: pressure
        dt: timestep (ignored for QSS)
        mxsteps: maximum steps (ignored for QSS)

    Returns:
        (final_state, cpu_time, solver_cpu_time, success)
    """
    y0 = np.array(state)
    try:
        start_time = time.time()

        if solver_type == "qss":
            solver = create_qss_solver(gas, pressure, config)
            solver.setState(y0.tolist(), t0)
            solver_start_time = time.time()
            result = solver.integrateToTime(t_end)
            solver_cpu_time = time.time() - solver_start_time
            cpu_time = time.time() - start_time
            if result == 0:
                final_state = np.array(solver.y)
                success = True
            else:
                final_state = y0
                success = False
        else:
            raise ValueError(f"Unknown solver type: {solver_type}")

        return final_state, cpu_time, solver_cpu_time, success

    except Exception as e:
        print(f"Integration failed with {solver_type}: {e}")
        return y0, 0.0, 0.0, False
