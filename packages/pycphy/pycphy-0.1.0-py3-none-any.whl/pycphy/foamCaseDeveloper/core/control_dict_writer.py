# control_dict_writer.py

from ..writers.control_dict_writer import ControlDictWriter as BaseControlDictWriter

class ControlDictWriter(BaseControlDictWriter):
    """
    Extended ControlDictWriter with additional functionality for case management.
    """
    
    def __init__(self, file_path, params):
        """
        Initializes the ControlDictWriter.

        Args:
            file_path (str): The full path to the output file 'controlDict'.
            params (dict): A dictionary containing the key-value pairs for the controlDict.
                           e.g., {'application': 'icoFoam', 'deltaT': 0.001}
        """
        super().__init__(file_path, params)
    
    def validate_params(self):
        """
        Validates the control parameters for common issues.
        
        Returns:
            bool: True if validation passes, False otherwise.
        """
        required_params = ['application', 'startFrom', 'stopAt']
        
        for param in required_params:
            if param not in self.params:
                print(f"Warning: Required parameter '{param}' is missing from control parameters.")
                return False
        
        # Validate application
        valid_applications = [
            'icoFoam', 'simpleFoam', 'pimpleFoam', 'interFoam', 
            'rhoSimpleFoam', 'rhoPimpleFoam', 'buoyantFoam'
        ]
        
        if self.params.get('application') not in valid_applications:
            print(f"Warning: Application '{self.params.get('application')}' may not be a valid OpenFOAM solver.")
        
        # Validate time step
        if 'deltaT' in self.params:
            try:
                delta_t = float(self.params['deltaT'])
                if delta_t <= 0:
                    print("Warning: deltaT should be positive.")
                    return False
            except (ValueError, TypeError):
                print("Warning: deltaT should be a valid number.")
                return False
        
        return True
