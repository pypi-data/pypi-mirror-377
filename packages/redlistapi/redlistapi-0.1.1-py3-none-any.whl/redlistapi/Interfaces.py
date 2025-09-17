import redlistapi
import inspect
from functools import partial


class V4_Interface:
    """
    A Red List API V4 interface.

    Attributes:
        token (str): Your Red List API token.

    Methods:
        to be filled programmatically
        
    """
    def __init__(self, token):
        self.token = token
        self._add_attributes(self, redlistapi.api.v4)
    
    def _add_attributes(self, obj, module):
        for name, member in inspect.getmembers(module):
            # Skip special/magic methods and attributes
            if name.startswith("__"):
                continue
            
            elif inspect.isfunction(member):
                # Bind the token to the function and add it to the object
                setattr(obj, name, partial(member, token=self.token))
    
            else:
                # Create a sub-object to maintain the structure
                sub_obj = type(name, (), {})()
                setattr(obj, name, sub_obj)
                # Recursively add attributes to the sub-object
                self._add_attributes(sub_obj, member)