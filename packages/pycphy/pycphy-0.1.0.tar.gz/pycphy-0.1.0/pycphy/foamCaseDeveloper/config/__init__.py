"""
Configuration files for OpenFOAM case setup.

This module provides configuration files for different aspects of
OpenFOAM case setup, including geometry, control, and turbulence settings.
Each config file contains detailed comments explaining all parameters.

Usage:
    from pycphy.foamCaseDeveloper.config import global_config
    from pycphy.foamCaseDeveloper.config import block_mesh_config
    from pycphy.foamCaseDeveloper.config import control_config
    from pycphy.foamCaseDeveloper.config import turbulence_config
"""

# Import all config modules
from . import global_config
from . import block_mesh_config
from . import control_config
from . import turbulence_config

__all__ = [
    "global_config",
    "block_mesh_config", 
    "control_config",
    "turbulence_config",
]
