# block_mesh_config.py

# =============================================================================
#           *** User Input Configuration for blockMeshDict Generation ***
# =============================================================================
#
#   Modify the values in this file to define the desired geometry,
#   mesh resolution, and boundary patch names.
#

# --- 1. Geometry Definition ---

# `p0`: The minimum corner of the computational domain (x_min, y_min, z_min).
# This defines the bottom-left-front corner of the geometry.
# Example: (0.0, 0.0, 0.0) for a domain starting at the origin
p0 = (0.0, 0.0, 0.0)

# `p1`: The maximum corner of the computational domain (x_max, y_max, z_max).
# This defines the top-right-back corner of the geometry.
# Example: (0.5, 0.2, 0.1) for a channel 0.5m long, 0.2m wide, 0.1m high
p1 = (0.5, 0.2, 0.1)

# --- 2. Meshing Parameters ---

# `cells`: Number of cells in each direction (nx, ny, nz).
# This determines the mesh resolution. Higher numbers = finer mesh = longer computation time.
# Example: (50, 20, 50) means 50 cells in x-direction, 20 in y-direction, 50 in z-direction
# Total cells = nx * ny * nz = 50 * 20 * 50 = 50,000 cells
cells = (50, 20, 50)

# `scale`: Scaling factor for the mesh coordinates.
# Usually set to 1.0 for actual dimensions. Use other values to scale the entire geometry.
# Example: 1.0 for meters, 0.001 for millimeters, 1000 for kilometers
scale = 1.0

# --- 3. Boundary Patch Names ---

# `patch_names`: Dictionary mapping geometric faces to boundary patch names.
# These names will be used in boundary condition files and OpenFOAM dictionaries.
# 
# Face identifiers:
#   'minX': Face at minimum X (x = p0[0])
#   'maxX': Face at maximum X (x = p1[0])
#   'minY': Face at minimum Y (y = p0[1])
#   'maxY': Face at maximum Y (y = p1[1])
#   'minZ': Face at minimum Z (z = p0[2])
#   'maxZ': Face at maximum Z (z = p1[2])
#
# Common patch types in OpenFOAM:
#   - 'patch': General boundary patch
#   - 'wall': Solid wall boundary
#   - 'symmetryPlane': Symmetry boundary
#   - 'empty': 2D simulation (front/back faces)
#
# Example for channel flow:
patch_names = {
    'minX': 'inlet',        # Inlet face (flow enters here)
    'maxX': 'outlet',       # Outlet face (flow exits here)
    'minY': 'frontWall',    # Front wall (solid boundary)
    'maxY': 'backWall',     # Back wall (solid boundary)
    'minZ': 'floor',        # Floor (solid boundary)
    'maxZ': 'ceiling'       # Ceiling (solid boundary)
}

# --- 4. Advanced Meshing Options ---

# `grading`: Cell size grading for each direction.
# Controls how cell sizes change across the domain.
# Example: (1, 1, 1) for uniform cells, (2, 1, 0.5) for graded cells
# Note: These are used in the blockMeshDict but not currently exposed in the simple interface
grading = (1, 1, 1)

# `merge_patch_pairs`: List of patch pairs to merge (for periodic boundaries).
# Example: [('leftWall', 'rightWall')] to create a periodic boundary
# Currently not implemented in the simple interface
merge_patch_pairs = []

# --- 5. Validation Settings ---

# `min_cell_size`: Minimum allowed cell size (for validation).
# Used to prevent extremely small cells that could cause numerical issues.
min_cell_size = 1e-6

# `max_cell_size`: Maximum allowed cell size (for validation).
# Used to prevent extremely large cells that could cause accuracy issues.
max_cell_size = 1.0

# `max_total_cells`: Maximum allowed total number of cells (for validation).
# Used to prevent creating meshes that are too large for available computational resources.
max_total_cells = 1000000