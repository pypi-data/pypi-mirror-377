# turbulence_config.py

# =============================================================================
#           *** User Input for turbulenceProperties ***
# =============================================================================
#
#   This file defines the turbulence model settings.
#   1. Set the SIMULATION_TYPE variable to 'RAS', 'LES', or 'laminar'.
#   2. Edit the corresponding properties dictionary below if needed.
#

# `SIMULATION_TYPE`: The type of turbulence simulation to perform.
# This determines which turbulence model will be used.
# Options:
#   'RAS': Reynolds-Averaged Simulation (steady or unsteady, computationally efficient)
#   'LES': Large Eddy Simulation (unsteady, more detailed but computationally expensive)
#   'laminar': Laminar flow (no turbulence model, for low Reynolds number flows)
SIMULATION_TYPE = "RAS"

# --- Reynolds-Averaged Simulation (RAS) Properties ---
# RAS models solve the Reynolds-averaged Navier-Stokes equations and model
# the effects of turbulence using statistical models. They are computationally
# less expensive and are suitable for many steady-state industrial flows.

RAS_PROPERTIES = {
    # `RASModel`: Specifies the turbulence model to use.
    # This determines how the Reynolds stresses are modeled.
    # Common Options:
    #   'kEpsilon': Standard k-epsilon model. Robust but less accurate for separated flows.
    #                Good for free shear flows, mixing layers, and jets.
    #   'realizableKE': A variation of k-epsilon with better performance for rotating flows.
    #                   Improved handling of adverse pressure gradients.
    #   'kOmegaSST': Menter's Shear Stress Transport model. Very popular, blends k-w
    #                near walls and k-e in the far-field. Excellent for aerodynamics
    #                and complex flows with separation.
    #   'SpalartAllmaras': One-equation model. Good for aerospace applications.
    #                      Particularly effective for attached flows.
    "RASModel": "kOmegaSST",

    # `turbulence`: A switch to turn the turbulence calculations on or off.
    # This allows you to run laminar simulations with RAS setup.
    # Options: 'on' (turbulence active), 'off' (laminar simulation)
    "turbulence": "on",

    # `printCoeffs`: Prints the model coefficients to the log file at the start.
    # This is useful for debugging and verifying model settings.
    # Options: 'on' (print coefficients), 'off' (don't print)
    "printCoeffs": "on",

    # Additional RAS model coefficients (advanced users only)
    # These can be used to modify the default model coefficients if needed.
    # Most users should not modify these unless they understand the model physics.
    
    # `kEpsilonCoeffs`: Coefficients for k-epsilon models (if using kEpsilon or realizableKE)
    # "kEpsilonCoeffs": {
    #     "Cmu": 0.09,          # Turbulent viscosity coefficient
    #     "C1": 1.44,           # Production coefficient
    #     "C2": 1.92,           # Destruction coefficient
    #     "C3": -0.33,          # Buoyancy coefficient
    #     "sigmap": 1.0,        # Prandtl number for pressure
    #     "sigmak": 1.0,        # Prandtl number for k
    #     "sigmaEps": 1.3       # Prandtl number for epsilon
    # },

    # `kOmegaSSTCoeffs`: Coefficients for k-omega SST model (if using kOmegaSST)
    # "kOmegaSSTCoeffs": {
    #     "beta1": 0.075,       # Beta coefficient for k equation
    #     "beta2": 0.0828,      # Beta coefficient for omega equation
    #     "betaStar": 0.09,     # Beta star coefficient
    #     "gamma1": 0.5532,     # Gamma coefficient for k equation
    #     "gamma2": 0.4403,     # Gamma coefficient for omega equation
    #     "alphaK1": 0.85,      # Alpha coefficient for k equation
    #     "alphaK2": 1.0,       # Alpha coefficient for k equation
    #     "alphaOmega1": 0.5,   # Alpha coefficient for omega equation
    #     "alphaOmega2": 0.856, # Alpha coefficient for omega equation
    #     "Prt": 0.9            # Turbulent Prandtl number
    # }
}

# --- Large Eddy Simulation (LES) Properties ---
# LES resolves the large, energy-containing eddies directly and models the
# smaller ones using sub-grid scale (SGS) models. It is more computationally
# expensive than RAS but provides more detail on transient turbulent structures.

LES_PROPERTIES = {
    # `LESModel`: Specifies the sub-grid scale (SGS) model for LES.
    # This determines how the unresolved small-scale turbulence is modeled.
    # Common Options:
    #   'Smagorinsky': The classic SGS model. Simple and robust but can be
    #                  overly dissipative near walls.
    #   'kEqn': One-equation eddy-viscosity model. Solves an equation for
    #           sub-grid scale kinetic energy. More accurate than Smagorinsky.
    #   'WALE': Wall-Adapting Local Eddy-viscosity model. Better near-wall
    #           behavior than Smagorinsky.
    #   'dynamicKEqn': Dynamic version of kEqn model. Coefficients are
    #                  computed dynamically, more accurate but computationally expensive.
    "LESModel": "kEqn",
    
    # `turbulence`: A switch to turn the turbulence calculations on or off.
    # Options: 'on' (LES active), 'off' (laminar simulation)
    "turbulence": "on",

    # `printCoeffs`: Prints the model coefficients to the log file at the start.
    # Options: 'on' (print coefficients), 'off' (don't print)
    "printCoeffs": "on",

    # `delta`: The model for the LES filter width.
    # This determines how the characteristic length scale is calculated.
    # Common Options:
    #   'cubeRootVol': Based on the cell volume. (Most common and recommended)
    #   'vanDriest': Wall-damping model. Reduces filter width near walls.
    #   'smooth': Smoothing for the delta field. Helps with mesh sensitivity.
    "delta": "smooth",

    # Each delta model and some LES models have their own coefficient sub-dictionaries.
    # The structure below is an example for the kEqn model with smooth delta.

    # `cubeRootVolCoeffs`: Coefficients for cubeRootVol delta model
    "cubeRootVolCoeffs": {
        # `deltaCoeff`: Coefficient for the filter width calculation.
        # Typical range: 0.5 to 2.0. Higher values = larger filter width.
        "deltaCoeff": 1
    },
    
    # `smoothCoeffs`: Coefficients for smooth delta model
    "smoothCoeffs": {
        # `delta`: The base delta model to use for smoothing.
        "delta": "cubeRootVol",
        
        # `cubeRootVolCoeffs`: Coefficients for the base delta model
        "cubeRootVolCoeffs": {
            "deltaCoeff": 1
        },
        
        # `maxDeltaRatio`: Maximum ratio between adjacent delta values.
        # This prevents large jumps in filter width between cells.
        # Typical range: 1.1 to 1.5
        "maxDeltaRatio": 1.1
    },

    # Additional LES model coefficients (advanced users only)
    # `kEqnCoeffs`: Coefficients for kEqn LES model (if using kEqn)
    # "kEqnCoeffs": {
    #     "Ck": 0.094,          # Model coefficient
    #     "Ce": 1.048           # Dissipation coefficient
    # },

    # `SmagorinskyCoeffs`: Coefficients for Smagorinsky model (if using Smagorinsky)
    # "SmagorinskyCoeffs": {
    #     "Ck": 0.094           # Smagorinsky constant
    # },

    # `WALECoeffs`: Coefficients for WALE model (if using WALE)
    # "WALECoeffs": {
    #     "Cw": 0.325           # WALE constant
    # }

    # Add other coefficient dictionaries like 'vanDriestCoeffs' if your model needs them.
}

# --- Laminar Simulation Properties ---
# For flows at low Reynolds numbers where turbulence is not present.
# The dictionary is typically empty as no turbulence modeling is required.

LAMINAR_PROPERTIES = {
    # For laminar flows, no turbulence model coefficients are needed.
    # This dictionary is kept for consistency but should remain empty.
    # If you need to add any laminar-specific parameters in the future,
    # they would go here.
}

# --- Additional Turbulence Settings ---

# `turbulenceOn`: Global switch for turbulence calculations.
# This can be used to quickly disable turbulence for testing.
# Options: True (turbulence active), False (laminar simulation)
turbulenceOn = True

# `turbulenceCorrected`: Enable turbulence corrections for better accuracy.
# This is useful for complex geometries and flow conditions.
# Options: True (enable corrections), False (disable corrections)
turbulenceCorrected = True

# `turbulenceDebug`: Enable debug output for turbulence calculations.
# This provides detailed information about turbulence model behavior.
# Options: True (debug on), False (debug off)
turbulenceDebug = False