"""
Tests for the QSS integrator core functionality.
"""

import pytest
import numpy as np
from qss_integrator import QssIntegrator, PyQssOde


class SimpleTestODE(PyQssOde):
    """Simple test ODE for exponential decay."""

    def __init__(self):
        super().__init__(self._ode_function)

    def _ode_function(self, t, y, corrector=False):
        """Simple exponential decay: dy/dt = -y."""
        q = [0.0]  # No production
        d = [y[0]]  # Destruction proportional to y
        return q, d


class TestQssIntegrator:
    """Test cases for QssIntegrator."""

    def test_integrator_creation(self):
        """Test that integrator can be created."""
        integrator = QssIntegrator()
        assert integrator is not None

    def test_ode_setup(self):
        """Test setting up an ODE."""
        integrator = QssIntegrator()
        ode = SimpleTestODE()
        integrator.setOde(ode)
        integrator.initialize(1)

        # Test initial state
        y0 = [1.0]
        integrator.setState(y0, 0.0)
        assert integrator.y[0] == 1.0
        assert integrator.tn == 0.0

    def test_simple_integration(self):
        """Test simple integration."""
        integrator = QssIntegrator()
        ode = SimpleTestODE()
        integrator.setOde(ode)
        integrator.initialize(1)

        # Set reasonable parameters
        integrator.epsmin = 1e-3
        integrator.epsmax = 10.0
        integrator.dtmin = 1e-12
        integrator.dtmax = 1e-3
        integrator.itermax = 2
        integrator.abstol = 1e-10

        # Initial conditions
        y0 = [1.0]
        integrator.setState(y0, 0.0)

        # Integrate
        result = integrator.integrateToTime(1.0)

        # Should succeed
        assert result == 0

        # Final value should be approximately exp(-1) ≈ 0.368
        expected = np.exp(-1.0)
        assert abs(integrator.y[0] - expected) < 1e-3

    def test_parameter_access(self):
        """Test that parameters can be accessed and modified."""
        integrator = QssIntegrator()

        # Test default values
        assert integrator.epsmin > 0
        assert integrator.epsmax > integrator.epsmin
        assert integrator.dtmin > 0
        assert integrator.dtmax > integrator.dtmin
        assert integrator.itermax > 0
        assert integrator.abstol > 0

        # Test modification
        integrator.epsmin = 1e-4
        assert integrator.epsmin == 1e-4

        integrator.itermax = 5
        assert integrator.itermax == 5


if __name__ == "__main__":
    pytest.main([__file__])
