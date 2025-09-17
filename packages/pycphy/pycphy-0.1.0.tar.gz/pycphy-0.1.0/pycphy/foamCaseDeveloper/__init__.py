"""
foamCaseDeveloper - OpenFOAM Case Development Tools

This module provides tools for creating and managing OpenFOAM simulation cases,
including mesh generation, control dictionary setup, and turbulence properties
configuration.

Author: Sanjeev Bashyal
"""

from .core import (
    BlockMeshDeveloper,
    ControlDictWriter,
    TurbulencePropertiesWriter,
    FoamCaseManager
)
from .writers import (
    BlockMeshWriter,
    FoamWriter
)
from .config import (
    global_config,
    block_mesh_config,
    control_config,
    turbulence_config
)

__version__ = "0.1.0"

__all__ = [
    "BlockMeshDeveloper",
    "ControlDictWriter", 
    "TurbulencePropertiesWriter",
    "FoamCaseManager",
    "BlockMeshWriter",
    "FoamWriter",
    "global_config",
    "block_mesh_config",
    "control_config", 
    "turbulence_config",
]
