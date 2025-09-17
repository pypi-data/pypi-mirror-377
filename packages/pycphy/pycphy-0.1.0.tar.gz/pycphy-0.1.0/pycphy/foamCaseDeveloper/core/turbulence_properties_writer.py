# turbulence_properties_writer.py

from ..writers.turbulence_properties_writer import TurbulencePropertiesWriter as BaseTurbulencePropertiesWriter

class TurbulencePropertiesWriter(BaseTurbulencePropertiesWriter):
    """
    Extended TurbulencePropertiesWriter with additional functionality for case management.
    """
    
    def __init__(self, file_path, simulation_type, model_properties):
        """
        Initializes the TurbulencePropertiesWriter.

        Args:
            file_path (str): The full path to the output file 'turbulenceProperties'.
            simulation_type (str): The top-level simulation type (e.g., 'RAS', 'LES', 'laminar').
            model_properties (dict): A dictionary containing the properties for the chosen model.
                                     This dictionary can be nested.
        """
        super().__init__(file_path, simulation_type, model_properties)
    
    def validate_simulation_type(self):
        """
        Validates the simulation type.
        
        Returns:
            bool: True if validation passes, False otherwise.
        """
        valid_types = ['RAS', 'LES', 'laminar']
        
        if self.simulation_type not in valid_types:
            print(f"Warning: Invalid simulation type '{self.simulation_type}'. Valid types: {valid_types}")
            return False
        
        return True
    
    def validate_model_properties(self):
        """
        Validates the model properties based on simulation type.
        
        Returns:
            bool: True if validation passes, False otherwise.
        """
        if self.simulation_type == 'RAS':
            required_keys = ['RASModel', 'turbulence']
            for key in required_keys:
                if key not in self.model_properties:
                    print(f"Warning: Required RAS parameter '{key}' is missing.")
                    return False
                    
            # Validate RAS model
            valid_ras_models = ['kEpsilon', 'realizableKE', 'kOmegaSST', 'SpalartAllmaras']
            if self.model_properties.get('RASModel') not in valid_ras_models:
                print(f"Warning: Unknown RAS model '{self.model_properties.get('RASModel')}'.")
        
        elif self.simulation_type == 'LES':
            required_keys = ['LESModel', 'turbulence']
            for key in required_keys:
                if key not in self.model_properties:
                    print(f"Warning: Required LES parameter '{key}' is missing.")
                    return False
                    
            # Validate LES model
            valid_les_models = ['Smagorinsky', 'kEqn', 'WALE', 'dynamicKEqn']
            if self.model_properties.get('LESModel') not in valid_les_models:
                print(f"Warning: Unknown LES model '{self.model_properties.get('LESModel')}'.")
        
        return True
