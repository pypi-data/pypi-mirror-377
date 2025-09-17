# QSS Integrator: Quasi-Steady State Method for Stiff ODE Systems

[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()

A high-performance Python package implementing the Quasi-Steady State (QSS) method for solving stiff ordinary differential equations, with particular focus on combustion chemistry applications. This package provides a C++ backend with Python bindings for efficient integration of chemical kinetics systems.

## What is the Quasi-Steady State (QSS) Method?

The Quasi-Steady State method is a specialized numerical technique designed for solving stiff ODE systems commonly found in chemical kinetics and combustion modeling. Unlike traditional methods that treat all species equally, QSS exploits the natural timescale separation in chemical systems.

### Key Concepts

**Stiff Systems**: In combustion chemistry, different chemical species evolve on vastly different timescales. Some species (like radicals) react very quickly, while others (like stable molecules) change slowly. This creates a "stiff" system where traditional integrators struggle.

**Timescale Separation**: The QSS method identifies fast and slow species based on their characteristic timescales:
- **Fast species**: React quickly and can be assumed to be in quasi-steady state
- **Slow species**: Evolve on the timescale of interest and are integrated explicitly

**Production-Destruction Splitting**: The method splits the ODE into production (`q`) and destruction (`d`) terms:
```
dy/dt = q(y) - d(y)
```
where `q` represents production rates and `d` represents destruction rates.

### Advantages

1. **Automatic stiffness handling**: No need for manual species classification
2. **Large timesteps**: Can take much larger steps than traditional methods
3. **Computational efficiency**: Fewer function evaluations per timestep
4. **Robustness**: Handles extreme stiffness ratios automatically

## Installation

### Prerequisites

- Python 3.8 or higher
- C++ compiler with C++17 support
- CMake (for building from source)

### Quick Install

```bash
pip install qss-integrator
```

### Development Install

```bash
git clone https://github.com/elotech47/pyQSS.git
cd qss-integrator
pip install -e .
```

### Cross-Platform Builds

This package uses `cibuildwheel` for robust cross-platform builds. The CI/CD pipeline automatically builds wheels for:

- **Linux**: x86_64 (manylinux2014)
- **macOS**: x86_64 and arm64 (universal2)
- **Windows**: x86_64 (AMD64)

Python versions supported: 3.8, 3.9, 3.10, 3.11, 3.12

#### Local Testing

To test the build process locally:

```bash
# Test basic build
python test_local_build.py

# Test with cibuildwheel (if installed)
pip install cibuildwheel
cibuildwheel --platform linux
```

### Dependencies

- **Required**: numpy, pybind11
- **Optional**: cantera (for combustion examples), matplotlib (for plotting)

## Quick Start

### Basic Usage

```python
import numpy as np
import qss_py

# Define your ODE system
class MyODE(qss_py.QssOde):
    def odefun(self, t, y, q, d, corrector=False):
        # Split your ODE into production (q) and destruction (d) terms
        q[0] = 1.0  # production rate
        d[0] = y[0]  # destruction rate (proportional to y)
        # ... define for all species

# Create integrator
integrator = qss_py.QssIntegrator()
ode = MyODE()
integrator.setOde(ode)
integrator.initialize(n_species=1)

# Set initial conditions
y0 = [1.0]  # initial state
integrator.setState(y0, t0=0.0)

# Integrate to final time
result = integrator.integrateToTime(tf=1.0)
final_state = integrator.y
```

### Combustion Example

```python
import cantera as ct
import numpy as np
from qss_utils import create_qss_solver

# Setup combustion problem
gas = ct.Solution('gri30.yaml')
gas.set_equivalence_ratio(1.0, 'CH4:1', 'O2:1, N2:3.76')
gas.TP = 1000, ct.one_atm

# Create QSS solver
config = {
    'epsmin': 1e-2,
    'epsmax': 10.0,
    'dtmin': 1e-15,
    'dtmax': 1e-6,
    'itermax': 2,
    'abstol': 1e-8,
    'stabilityCheck': True
}

solver = create_qss_solver(gas, ct.one_atm, config)

# Initial state: [T, Y1, Y2, ...]
y0 = [gas.T] + list(gas.Y)
solver.setState(y0, 0.0)

# Integrate
result = solver.integrateToTime(1e-3)  # 1 ms
print(f"Final temperature: {solver.y[0]:.1f} K")
```

## Configuration Parameters

The QSS integrator offers several parameters to control accuracy and performance:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `epsmin` | 1e-2 | Minimum accuracy parameter |
| `epsmax` | 20.0 | Maximum correction tolerance |
| `dtmin` | 1e-15 | Minimum timestep |
| `dtmax` | 1e-6 | Maximum timestep |
| `itermax` | 2 | Maximum corrector iterations |
| `abstol` | 1e-8 | Absolute tolerance for convergence |
| `stabilityCheck` | True | Enable stability checking |

## Examples

### 1. Simple Chemical Kinetics

See `examples/simple_kinetics.py` for a basic example with a simple chemical mechanism.

### 2. Combustion Modeling

See `examples/combustion.py` for methane combustion using Cantera mechanisms.

### 3. Performance Comparison

See `examples/benchmark.py` for comparing QSS performance against traditional methods.

## API Reference

### Core Classes

#### `QssIntegrator`
Main integrator class for QSS method.

**Methods:**
- `setOde(ode)`: Set the ODE system to integrate
- `initialize(n)`: Initialize for n species
- `setState(y, t)`: Set initial state
- `integrateToTime(tf)`: Integrate to final time
- `integrateOneStep(tf)`: Take one integration step

**Properties:**
- `y`: Current state vector
- `tn`: Current time
- `gcount`: Function evaluation count
- `rcount`: Timestep repeat count

#### `QssOde`
Base class for defining ODE systems.

**Methods:**
- `odefun(t, y, q, d, corrector)`: Evaluate ODE splitting

## Performance

The QSS method typically provides:
- **2-10x speedup** over traditional stiff solvers
- **Larger timesteps** without loss of accuracy
- **Better stability** for extremely stiff systems

See the benchmark results in `examples/benchmark.py` for detailed performance comparisons.

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
git clone https://github.com/elotech47/pyQSS.git
cd qss-integrator
pip install -e .[dev]
```

### Running Tests

```bash
python -m pytest tests/
```

## Citation

If you use this software in your research, please cite:

```bibtex
@software{qss_integrator,
  title={QSS Integrator: Quasi-Steady State Method for Stiff ODE Systems},
  author={Eloghosa Ikponmwoba},
  year={2024},
  url={https://github.com/elotech47/pyQSS.git}
}
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Based on the CHEMEQ2 algorithm
- Inspired by the Quasi-Steady-State method described in:
  > Mott, D., Oran, E., & van Leer, B. (2000). A Quasi-Steady-State Solver for the Stiff Ordinary Differential Equations of Reaction Kinetics. *Journal of Computational Physics*, 164(2), 407-428. https://doi.org/10.1006/jcph.2000.6605
- Built with pybind11 for Python-C++ integration

## Support

- **Issues**: [GitHub Issues](https://github.com/elotech47/pyQSS/issues)
- **Discussions**: [GitHub Discussions](https://github.com/elotech47/pyQSS/discussions)
