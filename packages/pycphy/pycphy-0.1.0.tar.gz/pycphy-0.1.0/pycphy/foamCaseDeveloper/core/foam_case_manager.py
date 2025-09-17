# foam_case_manager.py

import os
from .block_mesh_developer import BlockMeshDeveloper
from .control_dict_writer import ControlDictWriter
from .turbulence_properties_writer import TurbulencePropertiesWriter

class FoamCaseManager:
    """
    A comprehensive manager for creating and setting up OpenFOAM cases.
    
    This class provides a high-level interface for creating complete OpenFOAM
    case directories with all necessary configuration files.
    """
    
    def __init__(self, case_name):
        """
        Initialize the FoamCaseManager.
        
        Args:
            case_name (str): The name of the OpenFOAM case directory.
        """
        self.case_name = case_name
        self.system_dir = os.path.join(case_name, "system")
        self.constant_dir = os.path.join(case_name, "constant")
        
        # Ensure directories exist
        os.makedirs(self.system_dir, exist_ok=True)
        os.makedirs(self.constant_dir, exist_ok=True)
    
    def setup_geometry(self, p0, p1, cells, patch_names, scale=1.0):
        """
        Set up the geometry and mesh configuration.
        
        Args:
            p0 (tuple): The minimum corner of the cube (x0, y0, z0).
            p1 (tuple): The maximum corner of the cube (x1, y1, z1).
            cells (tuple): Number of cells in each direction (nx, ny, nz).
            patch_names (dict): A dictionary mapping face identifiers to custom names.
            scale (float): The scaling factor for the mesh.
        """
        self.geometry_config = {
            'p0': p0,
            'p1': p1,
            'cells': cells,
            'patch_names': patch_names,
            'scale': scale
        }
    
    def setup_control(self, control_params):
        """
        Set up the control dictionary parameters.
        
        Args:
            control_params (dict): Dictionary containing control parameters.
        """
        self.control_config = control_params
    
    def setup_turbulence(self, simulation_type, model_properties):
        """
        Set up the turbulence model configuration.
        
        Args:
            simulation_type (str): The simulation type ('RAS', 'LES', 'laminar').
            model_properties (dict): Properties for the turbulence model.
        """
        self.turbulence_config = {
            'simulation_type': simulation_type,
            'model_properties': model_properties
        }
    
    def create_blockmesh_dict(self):
        """
        Create the blockMeshDict file.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        if not hasattr(self, 'geometry_config'):
            print("Error: Geometry configuration not set. Call setup_geometry() first.")
            return False
        
        try:
            developer = BlockMeshDeveloper(
                p0=self.geometry_config['p0'],
                p1=self.geometry_config['p1'],
                cells=self.geometry_config['cells'],
                patch_names=self.geometry_config['patch_names'],
                scale=self.geometry_config.get('scale', 1.0)
            )
            
            bmd_path = os.path.join(self.system_dir, "blockMeshDict")
            developer.create_blockmesh_dict(file_path=bmd_path)
            return True
            
        except Exception as e:
            print(f"Error creating blockMeshDict: {e}")
            return False
    
    def create_control_dict(self):
        """
        Create the controlDict file.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        if not hasattr(self, 'control_config'):
            print("Error: Control configuration not set. Call setup_control() first.")
            return False
        
        try:
            cd_path = os.path.join(self.system_dir, "controlDict")
            control_dict = ControlDictWriter(file_path=cd_path, params=self.control_config)
            
            # Validate parameters before writing
            if not control_dict.validate_params():
                print("Warning: Control parameters validation failed, but proceeding anyway.")
            
            control_dict.write()
            return True
            
        except Exception as e:
            print(f"Error creating controlDict: {e}")
            return False
    
    def create_turbulence_properties(self):
        """
        Create the turbulenceProperties file.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        if not hasattr(self, 'turbulence_config'):
            print("Error: Turbulence configuration not set. Call setup_turbulence() first.")
            return False
        
        try:
            tp_path = os.path.join(self.constant_dir, "turbulenceProperties")
            turbulence_writer = TurbulencePropertiesWriter(
                file_path=tp_path,
                simulation_type=self.turbulence_config['simulation_type'],
                model_properties=self.turbulence_config['model_properties']
            )
            
            # Validate configuration before writing
            if not turbulence_writer.validate_simulation_type():
                print("Warning: Simulation type validation failed, but proceeding anyway.")
            
            if not turbulence_writer.validate_model_properties():
                print("Warning: Model properties validation failed, but proceeding anyway.")
            
            turbulence_writer.write()
            return True
            
        except Exception as e:
            print(f"Error creating turbulenceProperties: {e}")
            return False
    
    def create_full_case(self):
        """
        Create a complete OpenFOAM case with all configuration files.
        
        Returns:
            bool: True if all files created successfully, False otherwise.
        """
        print(f"--- Starting full OpenFOAM case setup for '{self.case_name}' ---")
        
        success = True
        
        # Create blockMeshDict
        print("\n[Step 1/3] Creating blockMeshDict...")
        if not self.create_blockmesh_dict():
            success = False
        
        # Create controlDict
        print("\n[Step 2/3] Creating controlDict...")
        if not self.create_control_dict():
            success = False
        
        # Create turbulenceProperties
        print("\n[Step 3/3] Creating turbulenceProperties...")
        if not self.create_turbulence_properties():
            success = False
        
        if success:
            print(f"\n--- Case setup complete! ---")
            print(f"Files written in '{self.case_name}'")
            print(f"  - {os.path.join(self.case_name, 'system', 'blockMeshDict')}")
            print(f"  - {os.path.join(self.case_name, 'system', 'controlDict')}")
            print(f"  - {os.path.join(self.case_name, 'constant', 'turbulenceProperties')}")
        else:
            print(f"\n--- Case setup failed! ---")
            print("Some files could not be created. Check error messages above.")
        
        return success
