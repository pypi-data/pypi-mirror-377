#!/usr/bin/env python3

import numpy as np
import cantera as ct
import matplotlib.pyplot as plt
import qss_py
import time


def setup_initial_conditions(
    gas, fuel_composition, oxidizer_composition, equivalence_ratio, T0, pressure
):
    """
    Setup initial conditions for any fuel/oxidizer combination using equivalence ratio.

    Parameters:
    - gas: Cantera Solution object
    - fuel_composition: dict, e.g., {'CH4': 1.0} or {'C2H6': 0.5, 'C3H8': 0.5}
    - oxidizer_composition: dict, e.g., {'O2': 1.0, 'N2': 3.76} for air
    - equivalence_ratio: float, phi (1.0 = stoichiometric)
    - T0: initial temperature [K]
    - pressure: pressure [Pa]

    Returns:
    - Y_initial: initial mass fractions array
    - major_species: list of species names with significant initial concentrations
    """
    # Set fuel composition
    gas.TPX = T0, pressure, fuel_composition

    # Calculate stoichiometric coefficients
    # This automatically handles any fuel composition
    gas.equilibrate("HP")  # Find equilibrium to get stoichiometric requirements

    # Reset to original fuel composition
    gas.TPX = T0, pressure, fuel_composition

    # Get stoichiometric air requirement
    # Use Cantera's built-in method to find stoichiometric mixture
    stoich_air_fuel_ratio = gas.stoich_air_fuel_ratio(
        fuel_composition, oxidizer_composition
    )

    # Calculate actual air-fuel ratio based on equivalence ratio
    actual_air_fuel_ratio = stoich_air_fuel_ratio / equivalence_ratio

    # Create mixture composition
    fuel_fraction = 1.0 / (1.0 + actual_air_fuel_ratio)
    air_fraction = actual_air_fuel_ratio / (1.0 + actual_air_fuel_ratio)

    # Build initial composition string
    mixture_composition = {}

    # Add fuel components
    for species, mole_frac in fuel_composition.items():
        mixture_composition[species] = mole_frac * fuel_fraction

    # Add oxidizer components
    for species, mole_frac in oxidizer_composition.items():
        mixture_composition[species] = mole_frac * air_fraction

    # Set the mixture state
    gas.TPX = T0, pressure, mixture_composition

    # Get mass fractions and find major species
    Y_initial = gas.Y.copy()
    major_species = []

    # Find species with significant initial concentrations
    for i, Y_i in enumerate(Y_initial):
        if Y_i > 1e-4:  # Threshold for "major" species
            species_name = gas.species_name(i)
            major_species.append(species_name)

    print(f"Initial mixture composition (phi = {equivalence_ratio:.2f}):")
    print(f"  T = {gas.T:.1f} K, P = {gas.P:.1f} Pa")
    print(f"  Major species:")
    for species in major_species:
        idx = gas.species_index(species)
        print(f"    {species}: Y = {gas.Y[idx]:.4f}")

    return Y_initial, major_species


def cantera_integration(
    mechanism,
    fuel_composition,
    oxidizer_composition,
    equivalence_ratio,
    T0=1400.0,
    pressure=101325.0,
    t_final=0.02,
    reactor_type="constant_pressure",
):
    """
    Standard Cantera integration for any fuel composition.
    """
    print("Running Cantera integration...")

    # Create gas object
    gas = ct.Solution(mechanism)

    # Setup initial conditions
    Y_initial, major_species = setup_initial_conditions(
        gas, fuel_composition, oxidizer_composition, equivalence_ratio, T0, pressure
    )

    # Create appropriate reactor
    if reactor_type == "constant_pressure":
        reactor = ct.IdealGasConstPressureReactor(gas)
    elif reactor_type == "constant_volume":
        reactor = ct.IdealGasReactor(gas)
    else:
        raise ValueError(
            "reactor_type must be 'constant_pressure' or 'constant_volume'"
        )

    # Create reactor network
    sim = ct.ReactorNet([reactor])

    # Set up time integration
    times = []
    temps = []
    cpu_times = []
    species_data = {name: [] for name in major_species}

    # Store initial conditions
    times.append(0.0)
    temps.append(gas.T)
    for name in major_species:
        species_data[name].append(gas.Y[gas.species_index(name)])

    # Time stepping
    n_steps = 100
    dt = t_final / n_steps
    for i in range(n_steps):
        start_time = time.time()
        sim.advance(dt * (i + 1))
        cpu_times.append(time.time() - start_time)
        times.append(sim.time)
        temps.append(reactor.T)

        for name in major_species:
            species_data[name].append(reactor.thermo.Y[gas.species_index(name)])

        # Print progress
        if (i + 1) % 20 == 0:
            fuel_name = list(fuel_composition.keys())[0]  # Primary fuel
            fuel_idx = gas.species_index(fuel_name)
            print(
                f"  t = {sim.time*1000:5.2f} ms, T = {reactor.T:6.1f} K, "
                f"{fuel_name} = {reactor.thermo.Y[fuel_idx]:.4f}"
            )

    print(f"Cantera final: T = {reactor.T:.1f} K")

    return np.array(times), np.array(temps), species_data, cpu_times


def qss_integration_with_cantera(
    mechanism,
    fuel_composition,
    oxidizer_composition,
    equivalence_ratio,
    T0=1400.0,
    pressure=101325.0,
    t_final=0.02,
):
    """
    QSS integration using Python+Cantera for any fuel composition.
    """
    print("\nRunning QSS integration with Cantera...")

    # class CanteraQSSODE:
    #     def __init__(self, mechanism, pressure):
    #         self.gas = ct.Solution(mechanism)
    #         self.pressure = pressure
    #         self.n_species = self.gas.n_species
    #         print(f"Using {self.n_species} species from mechanism")

    #     def __call__(self, t, y, corrector=False):
    #         """
    #         QSS ODE function: dy/dt = q(y) - d(y)
    #         where q is creation rate and d is destruction rate
    #         """
    #         # Extract state variables: T + all species
    #         T = max(y[0], 300.0)  # Prevent very low temperatures
    #         Y_species = np.array(y[1:])  # All species mass fractions

    #         # Ensure we have the right number of species
    #         if len(Y_species) != self.n_species:
    #             print(f"Error: Expected {self.n_species} species, got {len(Y_species)}")
    #             return [0.0] * (self.n_species + 1), [0.0] * (self.n_species + 1)

    #         # Ensure non-negative mass fractions
    #         Y_species = np.maximum(Y_species, 0.0)

    #         # Normalize mass fractions
    #         Y_sum = np.sum(Y_species)
    #         if Y_sum > 1e-10:
    #             Y_species /= Y_sum

    #         try:
    #             # Set Cantera state
    #             self.gas.TPY = T, self.pressure, Y_species

    #             # Debug: Print Cantera state at key times
    #             if t == 0.0 or abs(t - 0.001) < 1e-6:
    #                 print(f"\nCantera state at t={t:.6f}:")
    #                 print(f"  T = {self.gas.T:.1f} K")
    #                 print(f"  rho = {self.gas.density:.3f} kg/m³")
    #                 print(f"  cp = {self.gas.cp_mass:.1f} J/kg/K")

    #             # Get reaction rates from Cantera
    #             creation_rates = self.gas.creation_rates  # [kmol/m³/s]
    #             destruction_rates = self.gas.destruction_rates  # [kmol/m³/s]
    #             net_rates = creation_rates - destruction_rates  # [kmol/m³/s]

    #             # Thermodynamic properties
    #             rho = self.gas.density_mass
    #             cp = self.gas.cp_mass

    #             # Heat release calculation using formation enthalpies
    #             h_formation_RT = self.gas.standard_enthalpies_RT  # Dimensionless H_f/(RT)
    #             h_formation = h_formation_RT * ct.gas_constant * T  # [J/kmol]

    #             # Heat release rate - NEGATIVE sign because fuel consumption releases heat
    #             q_dot = -np.sum(net_rates * h_formation)  # [J/m³/s]

    #             if t == 0.0:
    #                 print(f"  Heat release rate: {q_dot:.6e} J/m³/s")
    #                 print(f"  dT/dt from heat: {q_dot/(rho*cp):.6e} K/s")

    #                 # Print rates for fuel species
    #                 for fuel_name in fuel_composition.keys():
    #                     try:
    #                         fuel_idx = self.gas.species_index(fuel_name)
    #                         print(f"  {fuel_name} net rate: {net_rates[fuel_idx]:.6e} kmol/m³/s")
    #                         print(f"  {fuel_name} h_formation: {h_formation[fuel_idx]:.6e} J/kmol")
    #                     except:
    #                         pass

    #             # Temperature rates - ALL heat release goes into creation term
    #             dTdt_q = q_dot / (rho * cp) if q_dot > 0 else 0.0  # Only positive heat release
    #             dTdt_d = -q_dot / (rho * cp) if q_dot < 0 else 0.0  # Heat removal if negative

    #             # Species rates - convert to mass fraction rates [1/s]
    #             mw = self.gas.molecular_weights  # [kg/kmol]

    #             # Ensure creation and destruction rates are non-negative
    #             creation_rates = np.maximum(creation_rates, 0.0)
    #             destruction_rates = np.maximum(destruction_rates, 0.0)

    #             # Convert to mass fraction rates
    #             dYdt_q = creation_rates * mw / rho  # [1/s]
    #             dYdt_d = destruction_rates * mw / rho  # [1/s]

    #         except Exception as e:
    #             print(f"Cantera error at T={T:.1f}: {e}")
    #             dTdt_q = 0.0
    #             dTdt_d = 0.0
    #             dYdt_q = np.zeros(self.n_species)
    #             dYdt_d = np.zeros(self.n_species)

    #         # Return creation and destruction rates
    #         q = np.concatenate([[dTdt_q], dYdt_q])
    #         d = np.concatenate([[dTdt_d], dYdt_d])

    #         return q.tolist(), d.tolist()
    class CanteraQSSODE:
        def __init__(self, mechanism, pressure):
            self.gas = ct.Solution(mechanism)
            self.pressure = pressure
            self.n_species = self.gas.n_species
            # caches for corrector
            self._T_cache = None
            self._rho_cache = None
            self._cp_cache = None
            self._hform_cache = None

        def __call__(self, t, y, corrector=False):
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
                rho = (
                    self._rho_cache if self._rho_cache is not None else self.gas.density
                )
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

    # Create gas object and setup initial conditions
    gas = ct.Solution(mechanism)
    Y_initial, major_species = setup_initial_conditions(
        gas, fuel_composition, oxidizer_composition, equivalence_ratio, T0, pressure
    )

    # Create QSS system
    chem = CanteraQSSODE(mechanism, pressure)
    integrator = qss_py.QssIntegrator()
    ode = qss_py.PyQssOde(chem)

    # Setup integrator
    integrator.setOde(ode)
    integrator.initialize(chem.n_species + 1)  # T + all species

    # QSS integrator settings
    integrator.epsmin = 2e-2
    integrator.epsmax = 10.0
    integrator.dtmin = 1e-16
    integrator.dtmax = 1e-6
    integrator.itermax = 2
    integrator.abstol = 1e-11
    integrator.stabilityCheck = False

    # Set minimum values for T + all species
    integrator.ymin = [200.0] + [1e-20] * chem.n_species
    integrator.enforce_ymin = [0.0] + [1.0] * chem.n_species

    # Initial state: T + all species mass fractions
    initial_state = [T0] + Y_initial.tolist()

    integrator.setState(initial_state, 0.0)

    # Integration with output control
    times = [0.0]
    states = [initial_state.copy()]

    n_outputs = 100
    dt_output = t_final / n_outputs
    cpu_times = []

    for i in range(1, n_outputs + 1):
        t_target = i * dt_output
        start_time = time.time()
        result = integrator.integrateToTime(t_target)
        cpu_times.append(time.time() - start_time)
        if result != 0:
            print(f"QSS integration failed at t = {t_target*1000:.2f} ms")
            break

        times.append(integrator.tn)
        states.append(integrator.y.copy())

        if i % 20 == 0:
            T = integrator.y[0]
            fuel_name = list(fuel_composition.keys())[0]  # Primary fuel
            try:
                fuel_idx = (
                    gas.species_index(fuel_name) + 1
                )  # +1 because T is at index 0
                Y_fuel = integrator.y[fuel_idx]
                print(
                    f"  t = {integrator.tn*1000:5.2f} ms, T = {T:6.1f} K, {fuel_name} = {Y_fuel:.6f}"
                )
            except:
                print(f"  t = {integrator.tn*1000:5.2f} ms, T = {T:6.1f} K")

    print(f"QSS final: T = {integrator.y[0]:.1f} K")
    print(f"QSS ODE evaluations: {integrator.gcount}")
    print(f"QSS failed steps: {integrator.rcount}")

    temps = [s[0] for s in states]

    # Extract species data for major species
    species_data = {}
    try:
        for species in major_species:
            species_idx = gas.species_index(species) + 1  # +1 for temperature
            species_data[species] = [s[species_idx] for s in states]
    except Exception as e:
        print(f"Warning: Could not extract species data: {e}")
        species_data = {name: [] for name in major_species}

    return np.array(times), np.array(temps), species_data, major_species, cpu_times


def compare_integrators(
    mechanism,
    fuel_composition,
    oxidizer_composition,
    equivalence_ratio=1.0,
    T0=1400.0,
    t_final=0.02,
    pressure=101325.0,
):
    """Compare Cantera and QSS integration for any fuel."""
    print("Comparing Cantera vs QSS Integration")
    print("=" * 60)
    print(f"Fuel: {fuel_composition}")
    print(f"Oxidizer: {oxidizer_composition}")
    print(f"Equivalence ratio: {equivalence_ratio}")
    print(f"Initial temperature: {T0} K")

    # Run both integrations
    try:
        (
            cantera_times,
            cantera_temps,
            cantera_species,
            cantera_cpu_times,
        ) = cantera_integration(
            mechanism,
            fuel_composition,
            oxidizer_composition,
            equivalence_ratio,
            T0=T0,
            t_final=t_final,
            pressure=pressure,
        )
    except Exception as e:
        print(f"Cantera integration failed: {e}")
        return

    try:
        (
            qss_times,
            qss_temps,
            qss_species,
            major_species,
            qss_cpu_times,
        ) = qss_integration_with_cantera(
            mechanism,
            fuel_composition,
            oxidizer_composition,
            equivalence_ratio,
            T0=T0,
            t_final=t_final,
            pressure=pressure,
        )
    except Exception as e:
        print(f"QSS integration failed: {e}")
        return

    # Create comparison plots for major species
    n_species = len(major_species)
    n_cols = min(3, n_species + 1)  # +1 for temperature
    n_rows = int(np.ceil((n_species + 1) / n_cols))

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(4 * n_cols, 4 * n_rows))
    if n_rows == 1:
        axes = axes.reshape(1, -1)

    # Temperature comparison
    ax = axes[0, 0]
    ax.plot(cantera_times * 1000, cantera_temps, "b-", label="Cantera", linewidth=2)
    ax.plot(qss_times * 1000, qss_temps, "r--", label="QSS", linewidth=2)
    ax.set_xlabel("Time (ms)")
    ax.set_ylabel("Temperature (K)")
    ax.set_title("Temperature Evolution")
    ax.legend()
    ax.grid(True)

    # Species comparisons
    for i, species in enumerate(major_species):
        row = (i + 1) // n_cols
        col = (i + 1) % n_cols
        ax = axes[row, col]

        ax.plot(
            cantera_times * 1000,
            cantera_species[species],
            "b-",
            label="Cantera",
            linewidth=2,
        )
        ax.plot(qss_times * 1000, qss_species[species], "r--", label="QSS", linewidth=2)
        ax.set_xlabel("Time (ms)")
        ax.set_ylabel(f"{species} Mass Fraction")
        ax.set_title(f"{species} Evolution")
        ax.legend()
        ax.grid(True)

    # Hide unused subplots
    for i in range(len(major_species) + 1, n_rows * n_cols):
        row = i // n_cols
        col = i % n_cols
        axes[row, col].set_visible(False)

    plt.tight_layout()
    fuel_name = "_".join(fuel_composition.keys())
    filename = f"cantera_vs_qss_{fuel_name}_phi{equivalence_ratio:.1f}.png"
    plt.savefig(filename, dpi=300)
    plt.show()

    print(f"Cantera CPU time: {np.sum(cantera_cpu_times):.2f} s")
    print(f"QSS CPU time: {np.sum(qss_cpu_times):.2f} s")

    fig, axes = plt.subplots(1, 2, figsize=(10, 5), dpi=300)
    axes[0].plot(cantera_cpu_times, label="Cantera")
    axes[0].plot(qss_cpu_times, label="QSS")
    axes[0].set_xlabel("Step")
    axes[0].set_ylabel("CPU Time (s)")
    axes[0].legend()
    axes[0].grid(True)
    axes[1].bar(["Cantera", "QSS"], [np.sum(cantera_cpu_times), np.sum(qss_cpu_times)])
    axes[1].set_xlabel("Step")
    axes[1].set_ylabel("CPU Time (s)")
    axes[1].legend()
    axes[1].grid(True)

    plt.tight_layout()
    plt.savefig(
        f"cantera_vs_qss_{fuel_name}_phi{equivalence_ratio:.1f}_cpu_time.png", dpi=300
    )
    plt.close()

    print(f"\nComparison saved as '{filename}'")

    # Print ignition delay comparison
    def find_ignition_delay(times, temps):
        if len(times) < 5:
            return 0.0
        dTdt = np.gradient(temps, times)
        max_idx = np.argmax(dTdt)
        return times[max_idx]

    if len(cantera_times) > 5:
        cantera_ign = find_ignition_delay(cantera_times, cantera_temps)
        print(f"Cantera ignition delay: {cantera_ign*1000:.2f} ms")

    if len(qss_times) > 5:
        qss_ign = find_ignition_delay(qss_times, qss_temps)
        print(f"QSS ignition delay: {qss_ign*1000:.2f} ms")

    # Print final temperature comparison
    print(f"\nFinal temperature comparison:")
    print(f"Cantera: {cantera_temps[-1]:.1f} K")
    print(f"QSS: {qss_temps[-1]:.1f} K")
    print(f"Difference: {abs(cantera_temps[-1] - qss_temps[-1]):.1f} K")


# Example usage functions for different fuels
def test_methane(pressure=101325.0):
    """Test with methane/air combustion"""
    mechanism = (
        "/Users/elotech/Downloads/research_code/large_mechanism/ch4_53species.yaml"
    )
    fuel_composition = {"CH4": 1.0}
    oxidizer_composition = {"O2": 1.0, "N2": 3.76}  # Air composition
    compare_integrators(
        mechanism,
        fuel_composition,
        oxidizer_composition,
        equivalence_ratio=1.0,
        T0=1200.0,
        t_final=0.08,
        pressure=pressure,
    )


def test_hydrogen(pressure=101325.0):
    """Test with hydrogen/air combustion"""
    mechanism = "h2o2.yaml"  # Cantera's built-in H2/O2 mechanism
    fuel_composition = {"H2": 1.0}
    oxidizer_composition = {"O2": 1.0, "N2": 3.76}
    compare_integrators(
        mechanism,
        fuel_composition,
        oxidizer_composition,
        equivalence_ratio=1.0,
        T0=1000.0,
        t_final=0.01,
        pressure=pressure,
    )


def test_propane(pressure=101325.0):
    """Test with propane/air combustion"""
    mechanism = "gri30.yaml"  # GRI-Mech 3.0
    fuel_composition = {"C3H8": 1.0}
    oxidizer_composition = {"O2": 1.0, "N2": 3.76}
    compare_integrators(
        mechanism,
        fuel_composition,
        oxidizer_composition,
        equivalence_ratio=1.0,
        T0=1300.0,
        t_final=0.05,
        pressure=pressure,
    )


def test_fuel_blend(pressure=101325.0):
    """Test with fuel blend"""
    mechanism = "gri30.yaml"
    fuel_composition = {"CH4": 0.7, "C2H6": 0.3}  # Natural gas blend
    oxidizer_composition = {"O2": 1.0, "N2": 3.76}
    compare_integrators(
        mechanism,
        fuel_composition,
        oxidizer_composition,
        equivalence_ratio=0.8,
        T0=1400.0,
        t_final=0.05,
        pressure=pressure,
    )


if __name__ == "__main__":
    # Test different fuels
    print("Testing Methane...")
    test_methane(1 * ct.one_atm)

    # Uncomment to test other fuels:
    # print("\nTesting Hydrogen...")
    # test_hydrogen(pressure=101325.0*60)

    # print("\nTesting Propane...")
    # test_propane()

    # print("\nTesting Fuel Blend...")
    # test_fuel_blend()
