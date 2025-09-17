# control_dict_writer.py

from .foam_writer import FoamWriter

class ControlDictWriter(FoamWriter):
    """
    A class to write an OpenFOAM controlDict file.

    It takes a dictionary of control parameters and formats them
    into a valid controlDict file.
    """

    def __init__(self, file_path, params):
        """
        Initializes the ControlDictWriter.

        Args:
            file_path (str): The full path to the output file 'controlDict'.
            params (dict): A dictionary containing the key-value pairs for the controlDict.
                           e.g., {'application': 'icoFoam', 'deltaT': 0.001}
        """
        super().__init__(file_path, foam_class="dictionary", foam_object="controlDict")
        self.params = params

    def _write_parameters(self):
        """Writes the control parameters from the dictionary."""
        # Find the longest key for alignment purposes to make the file pretty
        max_key_len = max(len(key) for key in self.params.keys()) if self.params else 0
        padding = max_key_len + 4 # Add some extra space

        for key, value in self.params.items():
            # The format string left-aligns the key in a padded field
            line = f"{key:<{padding}} {value};\n"
            self.file_handle.write(line)
        self.file_handle.write("\n")


    def write(self):
        """
        Writes the complete controlDict file.
        """
        print(f"Writing controlDict to: {self.file_path}")
        with open(self.file_path, 'w') as f:
            self.file_handle = f
            self._write_header()
            self._write_foamfile_dict()
            self._write_separator()
            
            # Write controlDict specific content
            self._write_parameters()

            self._write_footer()
        self.file_handle = None
        print("...Done")
