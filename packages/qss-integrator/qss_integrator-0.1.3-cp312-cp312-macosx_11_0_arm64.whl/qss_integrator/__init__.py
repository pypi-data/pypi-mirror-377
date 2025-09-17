"""
QSS Integrator: Quasi-Steady State method for stiff ODE systems.

This package provides efficient numerical integration for stiff ordinary
differential equations using the Quasi-Steady State method, with particular
focus on combustion chemistry applications.
"""

__version__ = "0.1.3"
__author__ = "Eloghosa Ikponmwoba"
__email__ = "eloghosaefficiency@gmail.com"

# Import the compiled extension with better error handling
try:
    from .qss_py import QssIntegrator, QssOde, PyQssOde
    __all__ = ["QssIntegrator", "QssOde", "PyQssOde"]
    
    # Test that the extension actually works
    _test_integrator = QssIntegrator()
    del _test_integrator
    
except ImportError as e:
    # Handle case where C++ extension is not built or not found
    import warnings
    import sys
    import os
    
    # Debug information
    module_path = os.path.dirname(__file__)
    files_in_module = os.listdir(module_path) if os.path.exists(module_path) else []
    
    warnings.warn(
        f"QSS C++ extension not found. Error: {e}\n"
        f"Module path: {module_path}\n"
        f"Files in module: {files_in_module}\n"
        f"Python path: {sys.path[:3]}...\n"
        "Please ensure the package was built correctly.",
        ImportWarning
    )
    __all__ = []
except Exception as e:
    import warnings
    warnings.warn(
        f"Error initializing QSS extension: {e}. "
        "The extension was found but failed to initialize.",
        ImportWarning
    )
    __all__ = []